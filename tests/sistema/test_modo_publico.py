"""Servidor público (MODO_PUBLICO=1): ninguém troca a IA nem edita o checklist pela tela,
e a configuração de IA pode vir das variáveis de ambiente (deploy em Docker)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import config  # noqa: E402
from sistema.api import app  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.arquivo_real = config.ARQUIVO
        config.ARQUIVO = Path(self.pasta.name) / "config.local.json"   # nunca toca a configuração verdadeira
        self.c = TestClient(app)

    def tearDown(self):
        config.ARQUIVO = self.arquivo_real
        self.pasta.cleanup()


class ModoPublico(Base):
    def test_rotas_que_gravam_respondem_403(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": "1"}):
            self.assertEqual(self.c.put("/api/config/ia", json={"provedor": "groq"}).status_code, 403)
            self.assertEqual(self.c.post("/api/config/ia/testar").status_code, 403)
            self.assertEqual(self.c.patch("/api/checklist/PCP/PCP-01", json={"status": "Feito"}).status_code, 403)
            self.assertFalse(config.ARQUIVO.exists())                     # nada foi gravado

    def test_telas_sabem_que_e_so_leitura(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": "1"}):
            self.assertTrue(self.c.get("/api/config/ia").json()["modo_publico"])
            self.assertFalse(self.c.get("/api/materias/pcp").json()["editavel"])

    def test_no_computador_continua_editavel(self):
        with mock.patch.dict(os.environ, {"MODO_PUBLICO": ""}):
            self.assertFalse(self.c.get("/api/config/ia").json()["modo_publico"])
            self.assertTrue(self.c.get("/api/materias/pcp").json()["editavel"])
            self.assertEqual(self.c.put("/api/config/ia", json={"limite_diario": 50}).status_code, 200)


class ConfigPeloAmbiente(Base):
    def test_ambiente_vale_mais_que_o_arquivo_e_completa_o_padrao(self):
        config.ARQUIVO.write_text('{"provedor": "ollama", "modelo": "llama3.2", "limite_diario": 100}', encoding="utf-8")
        with mock.patch.dict(os.environ, {"IA_PROVEDOR": "groq", "IA_CHAVE": "chave-de-teste-1234", "IA_LIMITE_DIARIO": "400",
                                          "IA_MODELO": "", "IA_BASE_URL": ""}):
            cfg = config.ler()
        self.assertEqual(cfg["provedor"], "groq")
        self.assertEqual(cfg["limite_diario"], 400)
        self.assertEqual(cfg["chave"], "chave-de-teste-1234")
        self.assertEqual(cfg["base_url"], config.PROVEDORES["groq"]["base_url"])
        self.assertEqual(cfg["modelo"], "llama3.2")          # o modelo do arquivo continua valendo quando o ambiente não define

    def test_tela_nunca_recebe_a_chave(self):
        with mock.patch.dict(os.environ, {"IA_PROVEDOR": "groq", "IA_CHAVE": "chave-de-teste-1234"}):
            publico = config.publico()
            resposta = self.c.get("/api/config/ia").text
        self.assertNotIn("chave", publico)
        self.assertEqual(publico["final_da_chave"], "1234")
        self.assertNotIn("chave-de-teste-1234", resposta)


if __name__ == "__main__":
    unittest.main()
