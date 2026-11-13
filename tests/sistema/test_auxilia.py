"""Testes da Lia (a agente), da leitura do CGE e da sociedade usando o sistema.

O modelo de IA é trocado por respostas fixas: os testes não gastam chamada nem dependem
da internet. Rodar da raiz: uv run python -m unittest discover -s tests/sistema -v
"""
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import assistente, ia, laboratorio, relatos  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.mobilidade import fontes  # noqa: E402

LINHAS = {n: {"numero": n, "status": "Operação Normal", "descricao": "", "nivel": "normal", "operadora": "Teste", "atualizado": ""}
          for n in ("1", "2", "3", "4", "5", "8", "9", "10", "11", "12", "13", "15", "17")}
SITUACAO = {"ok": True, "lido_em": "2026-11-12T10:00:00", "linhas": LINHAS, "aviso": "", "fonte": "teste"}
SEM_CHUVA = {"ok": True, "lido_em": "2026-11-12T10:00:00", "avisos": [], "fonte": "teste"}
CGE = {"ok": True, "lido_em": "2026-11-12T10:00:00", "estado": None, "ativos": 0, "avisos": [], "pontos_hoje": [], "ativos_lista": [], "fonte": "teste"}
AGORA = datetime(2026, 11, 12, 11, 0)       # quinta-feira, fora do pico


def chamada(nome: str, argumentos: dict, ident: str = "c1") -> dict:
    return {"role": "assistant", "content": None,
            "tool_calls": [{"id": ident, "type": "function", "function": {"name": nome, "arguments": json.dumps(argumentos)}}]}


def final(texto: str) -> dict:
    return {"role": "assistant", "content": texto}


class SemInternet(unittest.TestCase):
    def setUp(self):
        for nome, valor in (("situacao_linhas", SITUACAO), ("avisos_tempo", SEM_CHUVA), ("alertas_cge", CGE),
                            ("duracao_tipica", {"suficiente": False, "episodios": 0, "coletando_desde": None})):
            mock.patch.object(fontes, nome, return_value=valor).start()

    def tearDown(self):
        mock.patch.stopall()


class Estacoes(unittest.TestCase):
    def test_nomes_do_jeito_que_a_pessoa_escreve(self):
        for escrito, nome in (("se", "Sé"), ("barra funda", "Palmeiras - Barra Funda"), ("estação paulista", "Paulista"), ("grajau", "Grajaú")):
            self.assertEqual(assistente.resolver_estacao(escrito)["nome"], nome, escrito)
        self.assertIsNone(assistente.resolver_estacao("xyzw"))


class Conversa(SemInternet):
    def test_alertas_do_canto(self):
        r = assistente.alertas_agora()
        self.assertEqual(r["total"], 0)                      # tudo normal nos dados fixos
        self.assertEqual([i["nivel"] for i in r["itens"]], ["ok"])   # só o CGE conferido, sem alerta
        simulado = assistente.alertas_agora("9")
        self.assertEqual(simulado["total"], 1)
        self.assertTrue(simulado["parada"])
        self.assertIn("Linha 9", simulado["itens"][0]["titulo"])
        self.assertIn("simulação", simulado["itens"][0]["texto"])

    def test_dado_pessoal_nao_chega_ao_modelo(self):
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=AssertionError("não devia chamar")):
            r = assistente.responder("meu cpf é 123.456.789-09", agora=AGORA)
        self.assertTrue(r["recusa"])

    def test_viagem_com_ferramenta(self):
        respostas = [chamada("ver_trajeto", {"origem": "grajaú", "destino": "paulista"}), final("Pode ir, chega às 11:53.")]
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=respostas) as falso:
            r = assistente.responder("vou do grajaú pra paulista", agora=AGORA)
        self.assertEqual(r["texto"], "Pode ir, chega às 11:53.")
        plano = r["cartoes"][0]
        self.assertEqual(plano["tipo"], "plano")
        self.assertEqual(plano["chegada"], "11:53")
        self.assertNotIn("CS", [p["materia"] for p in r["rastro"]])      # a CS é entregue à parte
        self.assertEqual(plano["situacao"]["9"]["nivel"], "normal")
        self.assertIn("PAI", [p["materia"] for p in r["rastro"]])
        self.assertIsNotNone(r["ultima_viagem"])
        # a segunda rodada leva o resultado da ferramenta como mensagem "tool"
        segunda = falso.call_args_list[1].args[0]
        self.assertEqual(segunda[-1]["role"], "tool")

    def test_mensagem_de_atraso_usa_a_viagem_ja_conferida(self):
        g, p = assistente.resolver_estacao("grajaú")["id"], assistente.resolver_estacao("paulista")["id"]
        respostas = [chamada("mensagem_de_atraso", {"para_quem": "trabalho"}), final("Pronto, está aí embaixo.")]
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=respostas):
            r = assistente.responder("avisa o trabalho que vou atrasar", contexto={"ultima_viagem": {"origem": g, "destino": p}},
                                     simular="9", agora=AGORA)
        mensagem = [c for c in r["cartoes"] if c["tipo"] == "mensagem"][0]
        self.assertIn("atrasado", mensagem["texto"])
        self.assertIn("Linha 9", mensagem["texto"])
        self.assertNotIn("plano", [c["tipo"] for c in r["cartoes"]])     # não repete o cartão da viagem

    def test_lembra_a_estacao_de_casa(self):
        respostas = [chamada("lembrar_casa", {"estacao": "grajaú"}), final("Anotado.")]
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=respostas):
            r = assistente.responder("moro perto do grajaú", agora=AGORA)
        self.assertEqual(r["memoria"]["casa"], assistente.resolver_estacao("grajaú")["id"])

    def test_sem_ia_responde_por_regras(self):
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=ia.IAIndisponivel("sem cota")):
            oi = assistente.responder("oi", agora=AGORA)
            viagem = assistente.responder("vou do grajaú para a paulista", agora=AGORA)
            saindo = assistente.responder("estou saindo de casa", agora=AGORA)
        self.assertIn("Lia", oi["texto"])
        self.assertEqual(oi["ia"]["aviso"], "sem cota")
        self.assertEqual(viagem["cartoes"][0]["tipo"], "plano")
        self.assertIn("Para onde", saindo["texto"])

    def test_ferramenta_desconhecida_nao_quebra(self):
        respostas = [chamada("apagar_tudo", {}), final("Não consigo fazer isso.")]
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=respostas):
            r = assistente.responder("faça algo estranho", agora=AGORA)
        self.assertEqual(r["texto"], "Não consigo fazer isso.")


class LeituraDoCGE(unittest.TestCase):
    INICIAL = '''<div class="noticia"><a href="x"><h1>T&eacute;rmino do Estado de aten&ccedil;&atilde;o para alagamentos na Zona Leste, &agrave;s 17h35</h1>
        <h2>12/11/2026 17:39 - Quinta-feira</h2></a></div>
        <div class="noticia"><a href="y"><h1>Estado de aten&ccedil;&atilde;o para alagamentos na Zona Leste, &agrave;s 16h23</h1><h2>12/11/2026 16:24</h2></a></div>
        <span class="num-ativos">3</span>'''
    ALAGAMENTOS = '''<h1 class="tit-bairros">Zona Sudeste</h1><table><tr><td class="bairro arial-bairros-alag linha-pontilhada">Vila Mariana <hr/></td></tr>
        <tr><td><div class="ponto-de-alagamento"><ul><li class="ativo-intransitavel" title="x"></li><li class="espaco"></li>
        <li class="arial-descr-alag col-local">De 09:28 a 09:30<br/>AV DR RICARDO JAFET</li><li class="ln-vert"></li>
        <li class="arial-descr-alag">Sentido: SANTOS/S PAULO<br/>Refer&ecirc;ncia: R VERGUEIRO</li></ul></div></td></tr></table>'''

    def test_termino_desliga_o_estado(self):
        r = fontes.ler_cge_pagina_inicial(self.INICIAL)
        self.assertIsNone(r["estado"])
        self.assertEqual(r["ativos"], 3)
        self.assertEqual(len(r["avisos"]), 2)

    def test_estado_ativo(self):
        r = fontes.ler_cge_pagina_inicial(self.INICIAL.split("</div>", 1)[1])
        self.assertIn("Estado de atenção", r["estado"]["titulo"])

    def test_pontos(self):
        p = fontes.ler_cge_alagamentos(self.ALAGAMENTOS)[0]
        self.assertEqual((p["zona"], p["bairro"], p["via"], p["inicio"], p["fim"]), ("Zona Sudeste", "Vila Mariana", "AV DR RICARDO JAFET", "09:28", "09:30"))
        self.assertTrue(p["ativo"])
        self.assertFalse(p["transitavel"])
        self.assertEqual(p["referencia"], "R VERGUEIRO")


class Sociedade(SemInternet):
    def test_cada_situacao_gera_conversa_com_o_sistema(self):
        for situacao in laboratorio.SITUACOES:
            for p in laboratorio.PERSONAS:
                c = laboratorio.conversa_da_persona(p, situacao, hoje=AGORA)
                self.assertIsNotNone(c, f"{p['nome']} em {situacao}")
                self.assertTrue(c["pessoa"] and c["auxilia"])

    def test_linha_parada_pede_plano_b(self):
        joana = next(p for p in laboratorio.PERSONAS if p["id"] == "joana")
        c = laboratorio.conversa_da_persona(joana, "Linha parada na hora do pico", hoje=AGORA)
        self.assertEqual(c["decisao"], "plano_b")
        self.assertIn("Linha 9", c["pessoa"])

    def test_dia_normal_ignora_a_chuva_de_hoje(self):
        with mock.patch.object(fontes, "avisos_tempo", return_value={**SEM_CHUVA, "avisos": [{"quando": "hoje", "tipo": "Tempestade", "severidade": "Perigo",
                                                                                              "inicio": "", "fim": "2026-11-12 23:59", "riscos": "", "instrucoes": ""}]}):
            marcos = next(p for p in laboratorio.PERSONAS if p["id"] == "marcos")
            c = laboratorio.conversa_da_persona(marcos, "Dia normal", hoje=AGORA)
        self.assertEqual(c["decisao"], "pode_ir")


class RelatosNaLia(SemInternet):
    """A Lia lê os relatos dos passageiros: só campos prontos, e sem relato não diz que está tudo certo."""

    def setUp(self):
        super().setUp()
        self.repo = relatos.RepositorioMemoria()
        relatos.usar_repositorio(self.repo)

    def tearDown(self):
        relatos.usar_repositorio(relatos.RepositorioMemoria())
        super().tearDown()

    def test_toda_ferramenta_tem_rastro(self):
        nomes = {f["function"]["name"] for f in assistente.FERRAMENTAS}
        self.assertEqual(nomes - set(assistente.MATERIA_DA_FERRAMENTA), set())

    def test_dois_aparelhos_viram_alerta_com_o_aviso_de_estimativa(self):
        relatos.semear_demo(repositorio=self.repo)
        r = assistente.Sessao(None, AGORA).relatos_dos_passageiros("3")
        self.assertEqual(r["total_de_relatos"], 2)
        self.assertEqual(r["estimativa_por_linha"][0]["nivel"], "alerta")
        self.assertIn("não dado oficial", r["aviso"])

    def test_sem_relato_nao_diz_que_esta_tudo_certo(self):
        r = assistente.Sessao(None, AGORA).relatos_dos_passageiros("9")
        self.assertEqual(r["total_de_relatos"], 0)
        self.assertIn("ninguém relatou", r["observacao"])

    def test_nada_de_texto_de_terceiros_vai_ao_modelo(self):
        relatos.semear_demo(repositorio=self.repo)
        texto = json.dumps(assistente.Sessao(None, AGORA).relatos_dos_passageiros(), ensure_ascii=False)
        for proibido in ("apelido", "Passageiro ", "autor", "device"):
            self.assertNotIn(proibido, texto)

    def test_o_modelo_chama_a_ferramenta(self):
        relatos.semear_demo(repositorio=self.repo)
        respostas = [chamada("relatos_dos_passageiros", {"linha": "3"}), final("Passageiros relataram a Linha 3 lotada.")]
        with mock.patch.object(ia, "chamar_com_ferramentas", side_effect=respostas):
            r = assistente.responder("a linha 3 está lotada?", agora=AGORA)
        self.assertIn("Leu os relatos dos passageiros", [p["titulo"] for p in r["rastro"]])


class Api(SemInternet):
    def test_inicio_e_resposta(self):
        cliente = TestClient(app)
        alertas = cliente.get("/api/assistente/alertas", params={"simular": "4"}).json()
        self.assertEqual(alertas["total"], 1)
        with mock.patch.object(ia, "chamar_com_ferramentas", return_value=final("Oi! Para onde você vai?")):
            r = cliente.post("/api/assistente", json={"texto": "oi", "historico": [{"papel": "plano", "texto": "Oi! Como posso te auxiliar?"}]}).json()
        self.assertEqual(r["texto"], "Oi! Para onde você vai?")


if __name__ == "__main__":
    unittest.main()
