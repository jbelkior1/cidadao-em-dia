"""Testes do SOS: o canal certo por linha e os números conferidos contra o catálogo da DSA."""
import re
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import sos  # noqa: E402
from sistema.api import app  # noqa: E402


def digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


class Sos(unittest.TestCase):
    def test_metro_manda_sms_com_linha_e_estacao(self):
        r = sos.canais("3", "Sé")
        c = r["canais"][0]
        self.assertEqual(r["operadora"], "Metrô")
        self.assertEqual(c["acao"]["tipo"], "sms")
        self.assertIn("Linha 3-Vermelha, estação Sé. Ocorrência: ", c["acao"]["texto"])
        self.assertTrue(c["acao"]["href"].startswith("sms:+5511973332252?&body="))
        self.assertIn("Ocorr%C3%AAncia", c["acao"]["href"])      # texto codificado para o link

    def test_cada_operadora_tem_o_seu_canal(self):
        self.assertEqual(sos.canais("11")["canais"][0]["servico"], "SRV-009")
        self.assertEqual(sos.canais("4")["canais"][0]["acao"]["numero"], "0800 770 7100")
        self.assertEqual(sos.canais("9")["canais"][0]["acao"]["numero"], "0800 770 7106")

    def test_linha_sem_canal_proprio_cai_na_artesp(self):
        for linha in ("6", "7", "13", None, ""):
            self.assertEqual(sos.canais(linha)["canais"][0]["servico"], "SRV-012", linha)

    def test_numeros_batem_com_o_catalogo(self):
        """Todo número de discagem que o app oferece precisa aparecer no texto do serviço da DSA."""
        for linha in ("3", "11", "4", "9", "6"):
            for c in sos.canais(linha)["canais"]:
                numero = c["acao"]["numero"]
                self.assertIn(digitos(numero), digitos(c["catalogo"]), f"linha {linha}: {numero} não está em {c['servico']}")

    def test_emergencia_e_aviso_sempre_presentes(self):
        r = sos.canais("1")
        self.assertEqual([e["numero"] for e in r["emergencia"]], ["190", "192", "193"])
        self.assertIn("não é canal de emergência", r["aviso"])

    def test_api(self):
        r = TestClient(app).get("/api/sos", params={"linha": "3", "estacao": "Sé"}).json()
        self.assertEqual(r["canais"][0]["servico"], "SRV-004")


if __name__ == "__main__":
    unittest.main()
