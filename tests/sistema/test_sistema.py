"""Testes do sistema: barreira de dado pessoal, triagem, conversa e API.

Rodar da raiz do repositório:
    uv run python -m unittest discover -s tests/sistema -v
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import config, conversa, privacidade, triagem  # noqa: E402
from sistema.adaptadores import dsa, pcp  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.servicos import direitos, energia, golpe  # noqa: E402


def tipos(resposta):
    return [b["tipo"] for b in resposta["blocos"]]


class Privacidade(unittest.TestCase):
    def test_barra_cpf_telefone_email_e_frases(self):
        for texto in ("meu cpf é 123.456.789-09", "liga pra mim (11) 91234-5678", "fulano@exemplo.com",
                      "meu nome é Maria", "moro na rua das Flores", "CEP 01310-100"):
            self.assertIsNotNone(privacidade.motivo(texto), texto)

    def test_deixa_passar_pergunta_comum(self):
        for texto in ("meu CPF está suspenso, o que eu faço?", "minha conta veio 280 reais em 10/11/2026",
                      "gastei 310 kWh", "como atualizo o cadastro único?"):
            self.assertIsNone(privacidade.motivo(texto), texto)

    def test_mascara_numero_e_email(self):
        mascarado = privacidade.mascarar("ligue 0800 123 4567 ou escreva para golpe@site.com")
        self.assertNotIn("4567", mascarado)
        self.assertNotIn("@", mascarado)


class Triagem(unittest.TestCase):
    def test_assuntos(self):
        casos = {
            "minha conta de luz veio 280 reais. tenho direito a algum desconto?": "direitos",
            "recebi uma mensagem pedindo pix para liberar o benefício": "golpe",
            "quanto gasta o chuveiro na conta de luz?": "luz",
            "perdi meu rg, como faço a segunda via?": "duvida",
        }
        for texto, esperado in casos.items():
            self.assertEqual(triagem.entender(texto)[0], esperado, texto)

    def test_sem_assunto(self):
        self.assertEqual(triagem.entender("bom dia")[0], None)

    def test_palavra_inteira(self):
        self.assertFalse(triagem.contem("energia", "rg"))


class EntregasLigadas(unittest.TestCase):
    def test_pcp_carregou_a_base(self):
        s = pcp.situacao()
        self.assertTrue(s["ok"], s)
        self.assertGreaterEqual(s["orientacoes"], 10)
        self.assertGreaterEqual(s["categorias"], 3)

    def test_dsa_carregou_o_catalogo(self):
        s = dsa.situacao()
        self.assertTrue(s["ok"], s)
        self.assertGreater(s["registros"], 0)

    def test_busca_oficial_explica_os_pontos(self):
        r = pcp.responder("como atualizo meu cadastro único?")
        self.assertTrue(r["encontrou"])
        self.assertEqual(r["orientacao"]["titulo"], "Atualizar o Cadastro Único")
        self.assertEqual(r["confianca"], "ALTA")
        self.assertEqual(sum(d["pontos"] for d in r["detalhe"]), r["pontos"])

    def test_pergunta_sobre_desconto_na_luz_acha_a_tarifa_social(self):
        r = pcp.responder("tenho direito a desconto na conta de luz?")
        self.assertTrue(r["encontrou"])
        self.assertIn("Tarifa Social", r["orientacao"]["titulo"])

    def test_desconto_que_nao_apareceu(self):
        r = pcp.responder("o desconto não apareceu na minha conta de luz")
        self.assertIn("não apareceu", r["orientacao"]["titulo"])

    def test_catalogo_da_dsa_traz_para_quem(self):
        s = dsa.servico_de("tarifa social")
        self.assertIsNotNone(s)
        self.assertTrue(s["publico_alvo"])


class Conversa(unittest.TestCase):
    def test_boas_vindas(self):
        r = conversa.boas_vindas()
        self.assertEqual(tipos(r), ["texto", "opcoes"])

    def test_dado_pessoal_e_recusado_e_o_estado_nao_muda(self):
        estado = {"etapa": "duvida"}
        r = conversa.processar("meu cpf é 123.456.789-09", None, estado)
        self.assertEqual(tipos(r), ["recusa"])
        self.assertEqual(r["estado"], estado)
        self.assertNotIn("123", json.dumps(r, ensure_ascii=False))

    def test_triagem_pede_confirmacao_e_explica(self):
        r = conversa.processar("minha conta de luz veio 280 reais. tenho direito a algum desconto?", None, {})
        self.assertEqual(tipos(r), ["entendi"])
        self.assertIn("desconto", r["blocos"][0]["porque"])
        self.assertEqual(r["estado"]["assunto"], "direitos")

    def test_pergunta_que_a_base_responde_vira_duvida(self):
        r = conversa.processar("como atualizo meu cadastro único?", None, {})
        self.assertEqual(tipos(r), ["entendi"])
        self.assertIn("Atualizar o Cadastro Único", r["blocos"][0]["resumo"])
        self.assertEqual(r["estado"]["assunto"], "duvida")
        r = conversa.processar(None, "confirmar", r["estado"])
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")
        self.assertEqual(r["blocos"][0]["titulo"], "Atualizar o Cadastro Único")

    def test_mensagem_de_golpe_continua_indo_para_a_conferencia(self):
        r = conversa.processar("recebi uma mensagem com link pedindo pix, é golpe?", None, {})
        self.assertEqual(r["estado"]["assunto"], "golpe")

    def test_orientacao_de_conta_de_luz_oferece_o_caso_da_pessoa(self):
        r = conversa.processar("tenho direito a desconto na conta de luz?", None, {})
        r = conversa.processar(None, "confirmar", r["estado"])
        self.assertEqual(tipos(r), ["orientacao", "opcoes"])

    def test_direitos_tudo_sim(self):
        r = conversa.processar(None, "assunto:direitos", {})
        for _ in direitos.PERGUNTAS:
            self.assertEqual(r["blocos"][-1]["tipo"], "opcoes")
            r = conversa.processar(None, "resp:Sim", r["estado"])
        ficha = r["blocos"][0]
        self.assertEqual(ficha["tipo"], "ficha")
        self.assertEqual(ficha["tom"], "ok")
        self.assertTrue(ficha["fonte"].startswith("https://www.gov.br/"))
        self.assertIn("DSA", [s["materia"] for s in ficha["selos"]])

    def test_direitos_sem_cadastro_para_na_primeira_pergunta(self):
        r = conversa.processar(None, "assunto:direitos", {})
        r = conversa.processar(None, "resp:Não", r["estado"])
        self.assertEqual(r["blocos"][0]["tipo"], "ficha")
        self.assertEqual(r["blocos"][0]["situacao"], "Comece pelo Cadastro Único")

    def test_duvida_encontra_e_mostra_a_pontuacao(self):
        r = conversa.processar(None, "assunto:duvida", {})
        r = conversa.processar("como atualizo meu cadastro único?", None, r["estado"])
        bloco = r["blocos"][0]
        self.assertEqual(bloco["tipo"], "orientacao")
        self.assertEqual(bloco["confianca"], "ALTA")
        self.assertTrue(bloco["fonte"])
        self.assertTrue(bloco["verificado_em"])
        self.assertEqual([p["materia"] for p in r["rastro"]], ["PCP", "DSA"])

    def test_duvida_nao_encontrada_diz_que_nao_sabe(self):
        r = conversa.processar(None, "assunto:duvida", {})
        r = conversa.processar("quero um unicórnio", None, r["estado"])
        self.assertEqual(tipos(r), ["texto", "opcoes"])
        self.assertIn("Não encontrei", r["blocos"][0]["texto"])

    def test_navegacao_por_categoria(self):
        r = conversa.processar(None, "categorias", {})
        categoria = r["blocos"][0]["opcoes"][0]["acao"]
        r = conversa.processar(None, categoria, r["estado"])
        r = conversa.processar(None, r["blocos"][0]["opcoes"][0]["acao"], r["estado"])
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")

    def test_conta_de_luz_com_valor(self):
        r = conversa.processar(None, "assunto:luz", {})
        self.assertEqual(r["blocos"][0]["tipo"], "numero")
        r = conversa.processar("310 kWh", None, r["estado"])
        self.assertEqual(r["estado"]["etapa"], "luz_valor")
        r = conversa.processar("280", None, r["estado"])
        ficha = r["blocos"][0]
        self.assertEqual(ficha["tipo"], "ficha")
        texto = json.dumps(ficha, ensure_ascii=False)
        self.assertIn("80 kWh", texto)
        self.assertIn("230 kWh", texto)
        self.assertIn("R$ 72,26", texto)          # 80 kWh x (280 / 310)

    def test_conta_de_luz_pulando_o_valor(self):
        r = conversa.processar(None, "assunto:luz", {})
        r = conversa.processar("60", None, r["estado"])
        r = conversa.processar(None, "pular", r["estado"])
        texto = json.dumps(r["blocos"][0], ensure_ascii=False)
        self.assertIn("60 kWh, sem cobrança", texto)
        self.assertNotIn("Desconto estimado", texto)

    def test_conta_de_luz_recusa_texto_sem_numero(self):
        r = conversa.processar(None, "assunto:luz", {})
        r2 = conversa.processar("não sei", None, r["estado"])
        self.assertEqual(tipos(r2), ["texto"])
        self.assertEqual(r2["estado"], r["estado"])

    def test_golpe_analisa_mensagem_com_telefone_sem_recusar(self):
        r = conversa.processar(None, "assunto:golpe", {})
        mensagem = "URGENTE: seu benefício foi bloqueado. Pague a taxa por Pix em www.beneficio-gov.com ou ligue 0800 123 4567"
        r = conversa.processar(mensagem, None, r["estado"])
        bloco = r["blocos"][0]
        self.assertEqual(bloco["tipo"], "sinais")
        self.assertEqual(bloco["nivel"], "atencao")
        self.assertNotIn("4567", json.dumps(r, ensure_ascii=False))

    def test_golpe_mensagem_limpa(self):
        r = golpe.conferir("Lembrete: a reunião do bairro é na quinta, na escola.")
        self.assertEqual(r["nivel"], "ok")


class Energia(unittest.TestCase):
    def test_faixa_de_80_kwh(self):
        self.assertEqual(energia.calcular(100)["kwh_cobrados"], 20)     # exemplo oficial: de 100 kWh, paga 20
        self.assertEqual(energia.calcular(60)["kwh_cobrados"], 0)
        self.assertIsNone(energia.calcular(60)["desconto_mes"])


class Laboratorio(unittest.TestCase):
    def test_mais_canais_aumentam_a_adesao(self):
        from sistema import laboratorio
        so_app = laboratorio.simular("Tenho algum direito?", ["App e site"], n=1000)
        todos = laboratorio.simular("Tenho algum direito?", list(laboratorio.CANAIS), n=1000)
        self.assertGreater(todos["adesao"], so_app["adesao"])
        self.assertEqual(so_app["total_personas"], len(laboratorio.PERSONAS))

    def test_mesma_semente_mesmo_resultado(self):
        from sistema import laboratorio
        a = laboratorio.simular("Minha conta de luz", ["App e site"], n=500, semente=3)
        b = laboratorio.simular("Minha conta de luz", ["App e site"], n=500, semente=3)
        self.assertEqual(a["adesao"], b["adesao"])

    def test_sem_canal_usa_app(self):
        from sistema import laboratorio
        self.assertEqual(laboratorio.simular("Isso é golpe?", [], n=200)["canais"], ["App e site"])


class Checklist(unittest.TestCase):
    def test_estrutura(self):
        from sistema import checklist, materias
        dados = checklist.ler()
        for m in materias.NO_SISTEMA + materias.A_PARTE:
            itens = dados["materias"][m["cod"]]["itens"]
            self.assertTrue(itens, m["cod"])
            ids = [i["id"] for i in itens]
            self.assertEqual(len(ids), len(set(ids)), m["cod"])
            for i in itens:
                self.assertIn(i["status"], checklist.STATUS)
                self.assertIn(i["quem"], ("código", "grupo"))

    def test_percentual(self):
        from sistema import checklist
        r = checklist.contar([{"status": "Feito"}, {"status": "Falta conferir"}, {"status": "A fazer"}, {"status": "A fazer"}])
        self.assertEqual(r["percentual"], 38)   # (1 + 0,5) / 4


class Api(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo_real = config.ARQUIVO
        config.ARQUIVO = Path(self.pasta.name) / "config.local.json"   # nunca toca a configuração verdadeira
        self.cliente = TestClient(app)

    def tearDown(self):
        config.ARQUIVO = self.arquivo_real
        self.pasta.cleanup()

    def test_saude(self):
        r = self.cliente.get("/api/saude").json()
        self.assertTrue(r["ok"] and r["pcp"]["ok"] and r["dsa"]["ok"])

    def test_chat(self):
        r = self.cliente.post("/api/chat", json={"texto": "perdi meu rg, como faço a segunda via?"}).json()
        self.assertEqual(r["blocos"][0]["tipo"], "entendi")
        r = self.cliente.post("/api/chat", json={"acao": "confirmar", "estado": r["estado"]}).json()
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")

    def test_chave_nunca_volta_para_a_tela(self):
        segredo = "chave-de-teste-ABCD1234"
        r = self.cliente.put("/api/config/ia", json={"provedor": "groq", "modelo": "modelo-x", "chave": segredo})
        self.assertEqual(r.status_code, 200)
        corpo = r.text + self.cliente.get("/api/config/ia").text
        self.assertNotIn(segredo, corpo)
        dados = self.cliente.get("/api/config/ia").json()
        self.assertTrue(dados["config"]["tem_chave"])
        self.assertEqual(dados["config"]["final_da_chave"], "1234")
        self.assertEqual(dados["config"]["base_url"], "https://api.groq.com/openai/v1")
        self.assertTrue(dados["ligada"])

    def test_salvar_sem_chave_mantem_a_que_existe(self):
        self.cliente.put("/api/config/ia", json={"provedor": "groq", "modelo": "m", "chave": "abcdefgh9999"})
        self.cliente.put("/api/config/ia", json={"modelo": "outro-modelo"})
        self.assertEqual(config.ler()["chave"], "abcdefgh9999")
        self.cliente.put("/api/config/ia", json={"apagar_chave": True})
        self.assertEqual(config.ler()["chave"], "")

    def test_sem_ia_o_sistema_responde_e_explicar_avisa(self):
        self.assertFalse(self.cliente.get("/api/config/ia").json()["ligada"])
        r = self.cliente.post("/api/explicar", json={"orientacao_id": 1})
        self.assertEqual(r.status_code, 503)

    def test_provedor_desconhecido(self):
        self.assertEqual(self.cliente.put("/api/config/ia", json={"provedor": "xyz"}).status_code, 400)

    def test_paginas_das_materias(self):
        for cod in ("pcp", "dsa", "sers", "pai", "mlam", "coa", "cs", "mmc"):
            r = self.cliente.get(f"/api/materias/{cod}")
            self.assertEqual(r.status_code, 200, cod)
            self.assertIsNotNone(r.json()["checklist"], cod)
        self.assertEqual(self.cliente.get("/api/materias/xyz").status_code, 404)
        self.assertGreater(self.cliente.get("/api/painel").json()["geral"]["total"], 100)

    def test_teste_do_pcp_devolve_as_tuplas_em_ordem(self):
        r = self.cliente.post("/api/teste/pcp", json={"pergunta": "como atualizo meu cadastro único?"}).json()
        pontos = [x["pontos"] for x in r["resultados"]]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertTrue(self.cliente.post("/api/teste/pcp", json={"pergunta": "meu cpf 12345678900"}).json()["bloqueada"])

    def test_teste_da_dsa_na_memoria(self):
        self.cliente.post("/api/teste/dsa", json={"operacao": "reiniciar"})
        r = self.cliente.post("/api/teste/dsa", json={"operacao": "ordenar", "dados": {"criterio": "id"}}).json()
        ids = [n["id"] for n in r["nos"]]
        self.assertEqual(ids, sorted(ids))
        novo = {"id": "T-1", "titulo": "Teste", "categoria": "X", "descricao": "d", "publico_alvo": "p", "canal": "c"}
        r = self.cliente.post("/api/teste/dsa", json={"operacao": "cadastrar", "dados": novo}).json()
        self.assertTrue(r["ok"])
        self.assertEqual(r["cauda"], "T-1")
        self.assertFalse(self.cliente.post("/api/teste/dsa", json={"operacao": "cadastrar", "dados": novo}).json()["ok"])
        self.assertEqual(self.cliente.post("/api/teste/dsa", json={"operacao": "reiniciar"}).json()["tamanho"], len(ids))

    def test_teste_da_sers(self):
        r = self.cliente.post("/api/teste/sers", json={"kwh": 310, "valor": 280}).json()
        self.assertIn("R$ 72,26", r["passos"][-1])
        self.assertEqual(self.cliente.post("/api/teste/sers", json={"kwh": 0}).status_code, 400)

    def test_laboratorio(self):
        r = self.cliente.post("/api/laboratorio/simular", json={"parte": "Tenho algum direito?", "canais": ["App e site"], "n": 500}).json()
        self.assertEqual(len(r["opinioes"]), 10)
        self.assertEqual(self.cliente.post("/api/laboratorio/simular", json={"parte": "xyz"}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
