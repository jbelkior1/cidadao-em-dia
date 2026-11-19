"""Proteções do servidor público apontadas na revisão de 15/11: limite por aparelho nas rotas com IA,
limite diário também no agente da PAI, entradas estranhas que não derrubam rotas e o teto do catálogo
de teste da DSA. Nada aqui chama modelo de verdade."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import api, config, ia, testes  # noqa: E402
from sistema.adaptadores import pai as ponte_pai  # noqa: E402

c = TestClient(app := api.app)


class LimitePorAparelho(unittest.TestCase):
    def setUp(self):
        api._pedidos_por_ip.clear()

    def tearDown(self):
        api._pedidos_por_ip.clear()

    def _perguntar(self):
        # "asdfgh ??? 123" para no guardrail do agente: responde sem modelo e sem rede
        return c.post("/api/teste/pai", json={"pergunta": "asdfgh ??? 123"})

    def test_servidor_publico_barra_o_excesso_com_429(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": "1"}), mock.patch.object(api, "MAXIMO_POR_IP", 3):
            codigos = [self._perguntar().status_code for _ in range(4)]
        self.assertEqual(codigos, [200, 200, 200, 429])

    def test_no_computador_nao_ha_limite_por_aparelho(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": ""}), mock.patch.object(api, "MAXIMO_POR_IP", 1):
            codigos = [self._perguntar().status_code for _ in range(3)]
        self.assertEqual(codigos, [200, 200, 200])


class LimiteDiarioNoAgenteDaPai(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.config_real, self.uso_real = config.ARQUIVO, ia.ARQUIVO_USO
        config.ARQUIVO = Path(self.pasta.name) / "config.local.json"
        ia.ARQUIVO_USO = Path(self.pasta.name) / "uso_ia.local.json"
        config.ARQUIVO.write_text(json.dumps({"provedor": "groq", "modelo": "teste", "chave": "chave-de-teste-1234",
                                              "limite_diario": 2}), encoding="utf-8")

    def tearDown(self):
        config.ARQUIVO, ia.ARQUIVO_USO = self.config_real, self.uso_real
        self.pasta.cleanup()

    def test_chamada_do_agente_conta_no_limite_e_o_limite_barra(self):
        class Falso:
            def invoke(self, _mensagens):
                return mock.Mock(content="O crédito comum custa R$ 5,40 no metrô e no trem.")

        with mock.patch.dict(os.environ, {"IA_CHAVE": "", "IA_PROVEDOR": "", "IA_LIMITE_DIARIO": ""}), \
                mock.patch("pai_agente.modelo.criar", return_value=Falso()):
            primeira = ponte_pai.perguntar("Quanto custa a passagem do metrô?")
            segunda = ponte_pai.perguntar("Quanto custa a passagem do metrô?")
            terceira = ponte_pai.perguntar("Quanto custa a passagem do metrô?")
            recusa = ponte_pai.perguntar("asdfgh ??? 123")          # sem modelo: continua respondendo
        self.assertTrue(primeira["ok"] and segunda["ok"])
        self.assertFalse(terceira["ok"])
        self.assertIn("limite", terceira["erro"])
        self.assertEqual(ia.uso_de_hoje()["chamadas"], 2)
        self.assertTrue(recusa["ok"])


class EntradasEstranhas(unittest.TestCase):
    def test_dsa_aceita_numero_no_lugar_de_texto_sem_cair(self):
        for operacao, dados in (("consultar", {"id": 5}), ("excluir", {"id": 5}), ("pesquisar", {"campo": "titulo", "trecho": 5}),
                                ("atualizar", {"id": 5, "campo": "titulo", "valor": 7})):
            r = c.post("/api/teste/dsa", json={"operacao": operacao, "dados": dados})
            self.assertEqual(r.status_code, 200, operacao)
        c.post("/api/teste/dsa", json={"operacao": "reiniciar"})

    def test_catalogo_de_teste_da_dsa_tem_teto(self):
        c.post("/api/teste/dsa", json={"operacao": "reiniciar"})
        tamanho = c.get("/api/teste/dsa").json()["tamanho"]
        novo = {"id": "SRV-900", "titulo": "Teste", "categoria": "Teste", "descricao": "x", "publico_alvo": "todos", "canal": "site"}
        with mock.patch.object(testes, "DSA_MAXIMO_DE_NOS", tamanho):
            r = c.post("/api/teste/dsa", json={"operacao": "cadastrar", "dados": novo}).json()
        self.assertFalse(r["ok"])
        self.assertIn("vai até", r["mensagem"])
        self.assertEqual(r["tamanho"], tamanho)
        c.post("/api/teste/dsa", json={"operacao": "reiniciar"})


class Segredos(unittest.TestCase):
    def test_servidor_publico_nao_mostra_nem_o_final_da_chave(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": "1", "IA_PROVEDOR": "groq", "IA_CHAVE": "chave-de-teste-1234"}):
            self.assertEqual(config.publico()["final_da_chave"], "")
            self.assertTrue(config.publico()["tem_chave"])


class DatasDaPai(unittest.TestCase):
    def test_data_das_fontes_e_a_mesma_no_agente_e_no_app(self):
        agente, _, _ = ponte_pai._modulos()
        self.assertEqual(datetime.strptime(agente.DATA_FONTES, "%d/%m/%Y").date().isoformat(), ponte_pai.LIDO_EM)


if __name__ == "__main__":
    unittest.main()
