"""Testes do sistema Dá Tempo?: rede, rota, desvio, decisão, Pergunte, privacidade e API.

Rodar da raiz do repositório:
    uv run python -m unittest discover -s tests/sistema -v

Os testes não dependem da internet: a situação das linhas e os avisos de tempo
são substituídos por valores fixos.
"""
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import config, conversa, privacidade, testes  # noqa: E402
from sistema.adaptadores import dsa, pcp  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.mobilidade import decisao, energia, fontes, plano, rede  # noqa: E402

LINHAS_NORMAIS = {n: {"numero": n, "status": "Operação Normal", "descricao": "", "nivel": "normal", "operadora": "Teste", "atualizado": ""}
                  for n in ("1", "2", "3", "4", "5", "8", "9", "10", "11", "12", "13", "15")}
SITUACAO = {"ok": True, "lido_em": "2026-11-12T10:00:00", "linhas": LINHAS_NORMAIS, "aviso": "", "fonte": "teste"}
SEM_CHUVA = {"ok": True, "lido_em": "2026-11-12T10:00:00", "avisos": [], "fonte": "teste"}
COM_CHUVA = {"ok": True, "lido_em": "2026-11-12T10:00:00", "fonte": "teste",
             "avisos": [{"quando": "hoje", "tipo": "Tempestade", "severidade": "Perigo Potencial", "inicio": "", "fim": "2026-11-12 23:59",
                         "riscos": "", "instrucoes": ""}]}


def estacao(nome: str) -> str:
    for e in rede.estacoes_para_escolha():
        if rede.sem_acento(e["nome"]) == rede.sem_acento(nome):
            return e["id"]
    raise KeyError(nome)


class SemInternet(unittest.TestCase):
    """Substitui as fontes ao vivo por valores fixos."""

    def setUp(self):
        self.p1 = mock.patch.object(fontes, "situacao_linhas", return_value=SITUACAO)
        self.p2 = mock.patch.object(fontes, "avisos_tempo", return_value=SEM_CHUVA)
        self.p3 = mock.patch.object(fontes, "duracao_tipica", return_value={"suficiente": False, "episodios": 0, "coletando_desde": None})
        self.p1.start(), self.p2.start(), self.p3.start()

    def tearDown(self):
        mock.patch.stopall()


class Rede(unittest.TestCase):
    def test_rede_carrega(self):
        r = rede.carregar()
        self.assertGreaterEqual(len(r["linhas"]), 13)
        self.assertGreater(len(r["estacoes"]), 150)
        self.assertGreater(len(r["baldeacoes"]), 20)

    def test_rota_com_baldeacao(self):
        r = rede.rota(estacao("Grajaú"), estacao("Paulista"))
        self.assertEqual(r["linhas"], ["9", "4"])
        self.assertEqual(r["baldeacoes"], 1)
        self.assertGreater(r["km"], 10)

    def test_rota_numa_linha_so(self):
        r = rede.rota(estacao("Jabaquara"), estacao("Tucuruvi"))
        self.assertEqual(r["linhas"], ["1"])

    def test_rota_evitando_linha(self):
        r = rede.rota(estacao("Osasco"), estacao("Luz"), evitar={"9"})
        self.assertNotIn("9", r["linhas"])

    def test_sem_alternativa(self):
        self.assertIsNone(rede.rota(estacao("Jabaquara"), estacao("Tucuruvi"), evitar={"1"}))

    def test_desvio_ate_a_proxima_baldeacao(self):
        r = rede.rota_saindo_cedo(estacao("Grajaú"), estacao("Paulista"), {"9"})
        self.assertEqual(r["etapas"][0]["via"], "9")
        self.assertEqual(r["etapas"][0]["ate"], "Santo Amaro")      # primeira troca a partir do Grajaú
        self.assertNotIn("9", r["linhas"][1:])


class Decisao(unittest.TestCase):
    def test_regra_provisoria(self):
        self.assertEqual(decisao.decidir(True, False, False, False), decisao.PLANO_B)
        self.assertEqual(decisao.decidir(False, True, True, False), decisao.MAIS_CEDO)
        self.assertEqual(decisao.decidir(False, False, False, True), decisao.PODE_IR)

    def test_pico(self):
        self.assertTrue(decisao.horario_de_pico(datetime(2026, 11, 12, 7, 30)))     # quinta-feira
        self.assertFalse(decisao.horario_de_pico(datetime(2026, 11, 12, 11, 0)))
        self.assertFalse(decisao.horario_de_pico(datetime(2026, 11, 15, 7, 30)))    # domingo


class Plano(SemInternet):
    def test_tudo_normal_pode_ir(self):
        p = plano.antes_de_sair(estacao("Jabaquara"), estacao("Tucuruvi"), agora=datetime(2026, 11, 12, 11, 0))
        self.assertEqual(p["veredito"]["codigo"], decisao.PODE_IR)
        self.assertIsNone(p["plano_b"])

    def test_falha_simulada_gera_desvio(self):
        p = plano.antes_de_sair(estacao("Osasco"), estacao("Luz"), simular_falha="9", agora=datetime(2026, 11, 12, 11, 0))
        self.assertEqual(p["veredito"]["codigo"], decisao.PLANO_B)
        self.assertEqual(p["plano_b"]["recomendacao"], "desviar")
        self.assertNotIn("9", p["plano_b"]["alternativa"]["linhas"])
        self.assertEqual(p["simulacao"], "9")

    def test_falha_sem_caminho_manda_esperar(self):
        p = plano.antes_de_sair(estacao("Jabaquara"), estacao("Tucuruvi"), simular_falha="1", agora=datetime(2026, 11, 12, 11, 0))
        self.assertEqual(p["plano_b"]["recomendacao"], "esperar")
        self.assertIn("PAESE", p["plano_b"]["texto"])

    def test_chuva_no_pico_saia_mais_cedo(self):
        with mock.patch.object(fontes, "avisos_tempo", return_value=COM_CHUVA):
            p = plano.antes_de_sair(estacao("Jabaquara"), estacao("Tucuruvi"), agora=datetime(2026, 11, 12, 7, 30))
        self.assertEqual(p["veredito"]["codigo"], decisao.MAIS_CEDO)
        self.assertTrue(any(m["tipo"] == "chuva" for m in p["motivos"]))


class Fontes(unittest.TestCase):
    def test_nivel(self):
        self.assertEqual(fontes.nivel("Operação Normal"), "normal")
        self.assertEqual(fontes.nivel("Velocidade Reduzida"), "atencao")
        self.assertEqual(fontes.nivel("Operação Parcial"), "atencao")
        self.assertEqual(fontes.nivel("Paralisada"), "parada")
        self.assertEqual(fontes.nivel("Operação Encerrada"), "encerrada")
        self.assertEqual(fontes.nivel(""), "sem_dado")

    def test_duracao_tipica_pelo_historico(self):
        linhas = []
        for minuto, nivel in [(0, "normal"), (2, "parada"), (32, "normal"), (40, "atencao"), (60, "normal"), (70, "parada"), (110, "normal")]:
            t = datetime(2026, 11, 12, 8, 0).replace(minute=0) .isoformat()
            hora = 8 + minuto // 60
            linhas.append(json.dumps({"t": f"2026-11-12T{hora:02d}:{minuto % 60:02d}:00", "l": {"9": nivel}}))
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "h.jsonl"
            arquivo.write_text("\n".join(linhas), encoding="utf-8")
            with mock.patch.object(fontes, "HISTORICO", arquivo):
                d = fontes.duracao_tipica("9")
        self.assertTrue(d["suficiente"])
        self.assertEqual(d["episodios"], 3)
        self.assertEqual(d["mediana_min"], 30)


class Energia(unittest.TestCase):
    def test_trilho_emite_menos_que_onibus_e_carro(self):
        r = energia.comparar(15)
        trilho, onibus, carro = r["modos"]
        self.assertTrue(trilho["renovavel"])
        self.assertLess(trilho["co2_kg"], onibus["co2_kg"])
        self.assertLess(onibus["co2_kg"], carro["co2_kg"])
        self.assertLess(carro["co2_kg"], carro["co2_kg_max"])

    def test_contas_batem_com_a_pesquisa(self):
        r = energia.comparar(15)
        trilho, _, carro = r["modos"]
        self.assertAlmostEqual(trilho["energia_kwh"], 15 * 0.0717, places=2)
        self.assertAlmostEqual(carro["custo_rs"], 15 / 13.3 * 6.35, places=2)
        self.assertTrue(all(f.startswith("https://") for f in r["fontes"]))

    def test_teste_da_sers_mostra_os_passos(self):
        r = testes.sers_testar(10)
        self.assertEqual(len(r["passos"]), 4)
        self.assertIn("km", r["passos"][0])


class Seguranca(unittest.TestCase):
    def test_estacao_da_capital_tem_dado(self):
        s = plano.seguranca_da_estacao(estacao("República"))
        self.assertEqual(s["estacao"], "República")
        self.assertGreater(s["total"], 0)
        self.assertIsNone(s["celular"])               # a planilha da SSP não informa o objeto

    def test_casa_pela_proximidade_quando_o_nome_difere(self):
        self.assertIsNotNone(plano.seguranca_da_estacao(estacao("Pinheiros")))

    def test_estacao_fora_da_capital_fica_sem_dado(self):
        self.assertIsNone(plano.seguranca_da_estacao(estacao("Osasco")))

    def test_resumo_da_mlam(self):
        r = testes.mlam_resumo()
        self.assertTrue(r["ok"])
        self.assertEqual(r["estacoes"], 139)
        self.assertEqual(r["ranking"][0]["total"], max(x["total"] for x in r["ranking"]))
        self.assertNotIn("logradouro", json.dumps(r, ensure_ascii=False).lower())


class Privacidade(unittest.TestCase):
    def test_barra_cpf_telefone_email_e_frases(self):
        for texto in ("meu cpf é 123.456.789-09", "liga pra mim (11) 91234-5678", "fulano@exemplo.com",
                      "meu nome é Maria", "moro na rua das Flores"):
            self.assertIsNotNone(privacidade.motivo(texto), texto)

    def test_deixa_passar_pergunta_comum(self):
        for texto in ("a linha 9 parou, e agora?", "roubaram meu celular no trem", "quanto custa a passagem"):
            self.assertIsNone(privacidade.motivo(texto), texto)


class Pergunte(unittest.TestCase):
    def test_boas_vindas(self):
        r = conversa.boas_vindas()
        self.assertEqual([b["tipo"] for b in r["blocos"]], ["texto", "opcoes", "opcoes"])

    def test_pergunta_encontra_orientacao(self):
        r = conversa.processar("a linha 9 parou, e agora?", None, {})
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")
        self.assertIn("PAESE", r["blocos"][0]["titulo"])
        self.assertTrue(r["blocos"][0]["fonte"].startswith("https://"))

    def test_orientacao_traz_o_canal_do_catalogo(self):
        bloco = conversa.processar("perdi minha mochila no metrô", None, {})["blocos"][0]
        self.assertIn("0800", bloco["canal"])
        self.assertEqual([s["materia"] for s in bloco["selos"]], ["PCP", "DSA"])

    def test_todo_servico_ligado_existe_no_catalogo(self):
        for orientacao, servico in conversa.SERVICO_DA_ORIENTACAO.items():
            self.assertIsNotNone(dsa.servico_por_id(servico), f"orientação {orientacao} -> {servico}")

    def test_dado_pessoal_recusado(self):
        r = conversa.processar("meu cpf é 123.456.789-09", None, {})
        self.assertEqual(r["blocos"][0]["tipo"], "recusa")
        self.assertNotIn("123", json.dumps(r, ensure_ascii=False))

    def test_nao_encontrou(self):
        r = conversa.processar("quero um unicórnio", None, {})
        self.assertIn("Não encontrei", r["blocos"][0]["texto"])

    def test_navegacao_por_categoria(self):
        r = conversa.processar(None, "categoria:Segurança", {})
        r = conversa.processar(None, r["blocos"][0]["opcoes"][0]["acao"], {})
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")

    def test_exemplo(self):
        r = conversa.processar(None, "exemplo:Roubaram meu celular no trem", {})
        self.assertIn("Celular", r["blocos"][0]["titulo"])


class EntregasLigadas(unittest.TestCase):
    def test_pcp_carregou_a_base(self):
        s = pcp.situacao()
        self.assertTrue(s["ok"], s)
        self.assertGreaterEqual(s["orientacoes"], 10)

    def test_dsa_carregou_o_catalogo(self):
        s = dsa.situacao()
        self.assertTrue(s["ok"], s)
        self.assertGreater(s["registros"], 10)


class Api(SemInternet):
    def setUp(self):
        super().setUp()
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo_real = config.ARQUIVO
        config.ARQUIVO = Path(self.pasta.name) / "config.local.json"   # nunca toca a configuração verdadeira
        self.cliente = TestClient(app)

    def tearDown(self):
        config.ARQUIVO = self.arquivo_real
        self.pasta.cleanup()
        super().tearDown()

    def test_estacoes_e_linhas(self):
        e = self.cliente.get("/api/mobilidade/estacoes").json()
        self.assertGreater(len(e["estacoes"]), 150)
        l = self.cliente.get("/api/mobilidade/linhas").json()
        self.assertEqual(len(l["linhas"]), len(e["linhas"]))

    def test_plano(self):
        r = self.cliente.get("/api/mobilidade/plano", params={"origem": estacao("Grajaú"), "destino": estacao("Paulista"), "simular": "9"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["veredito"]["codigo"], "plano_b")

    def test_plano_mesma_estacao(self):
        self.assertEqual(self.cliente.get("/api/mobilidade/plano", params={"origem": estacao("Sé"), "destino": estacao("Sé")}).status_code, 400)

    def test_teste_cs(self):
        r = self.cliente.post("/api/teste/cs", json={"falha": False, "chuva": True, "alagamento": True, "pico": False}).json()
        self.assertEqual(r["codigo"], "mais_cedo")

    def test_chat(self):
        r = self.cliente.post("/api/chat", json={"texto": "perdi minha mochila no metrô"}).json()
        self.assertEqual(r["blocos"][0]["tipo"], "orientacao")

    def test_chave_nunca_volta_para_a_tela(self):
        segredo = "chave-de-teste-ABCD1234"
        self.cliente.put("/api/config/ia", json={"provedor": "groq", "modelo": "modelo-x", "chave": segredo})
        corpo = self.cliente.get("/api/config/ia").text
        self.assertNotIn(segredo, corpo)
        self.assertEqual(self.cliente.get("/api/config/ia").json()["config"]["final_da_chave"], "1234")

    def test_paginas_das_materias(self):
        for cod in ("pcp", "cs", "dsa", "sers", "mlam", "pai", "mmc", "coa"):
            self.assertEqual(self.cliente.get(f"/api/materias/{cod}").status_code, 200, cod)

    def test_laboratorio(self):
        r = self.cliente.post("/api/laboratorio/simular", json={"parte": "Linha parada na hora do pico", "canais": ["App e site"], "n": 300}).json()
        self.assertEqual(len(r["opinioes"]), 10)


if __name__ == "__main__":
    unittest.main()
