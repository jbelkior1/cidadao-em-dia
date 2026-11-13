"""Testes da aba Mapa: camadas com as fontes ao vivo trocadas por valores fixos.

Rodar da raiz: uv run python -m unittest discover -s tests/sistema -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import mapa  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.mobilidade import fontes, rede  # noqa: E402

LINHAS = {n: {"numero": n, "status": "Operação Normal", "descricao": "", "nivel": "normal", "operadora": "Teste", "atualizado": ""}
          for n in ("1", "2", "3", "4", "5", "8", "9", "10", "11", "12", "13", "15", "17")}
LINHAS["8"] = dict(LINHAS["8"], status="Velocidade reduzida", nivel="atencao")
SITUACAO = {"ok": True, "lido_em": "2026-11-12T10:00:00", "linhas": LINHAS, "aviso": "", "fonte": "teste"}
CGE = {"ok": True, "lido_em": "2026-11-12T10:00:00", "estado": {"titulo": "Estado de atenção para alagamentos", "quando": "12/11 09:00"},
       "ativos": 1, "avisos": [], "pontos_hoje": [], "fonte": "teste",
       "ativos_lista": [{"zona": "Sul", "bairro": "Santo Amaro", "ativo": True, "transitavel": False, "via": "Av. Teste"}]}


class Camadas(unittest.TestCase):
    def setUp(self):
        mock.patch.object(fontes, "situacao_linhas", return_value=SITUACAO).start()
        mock.patch.object(fontes, "alertas_cge", return_value=CGE).start()
        self.cliente = TestClient(app)

    def tearDown(self):
        mock.patch.stopall()

    def test_estrutura_da_resposta(self):
        r = self.cliente.get("/api/mapa/camadas")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(set(d), {"lido_em", "linhas", "estacoes", "alagamentos", "seguranca", "cge"})
        self.assertEqual(d["lido_em"], "2026-11-12T10:00:00")
        self.assertEqual(len(d["linhas"]), len(rede.carregar()["linhas"]))
        linha9 = next(l for l in d["linhas"] if l["numero"] == "9")
        self.assertEqual(set(linha9), {"numero", "nome", "cor", "nivel", "status", "simulado", "trechos"})
        self.assertEqual(linha9["nivel"], "normal")
        self.assertFalse(linha9["simulado"])
        self.assertTrue(linha9["trechos"])
        (a, b) = linha9["trechos"][0]
        self.assertEqual((len(a), len(b)), (2, 2))
        self.assertEqual(next(l for l in d["linhas"] if l["numero"] == "8")["nivel"], "atencao")
        self.assertEqual(set(d["estacoes"][0]), {"id", "nome", "lat", "lon", "linhas"})
        self.assertTrue(d["seguranca"])
        self.assertEqual(set(d["seguranca"][0]), {"estacao", "lat", "lon", "total", "faixa"})
        for p in d["alagamentos"][:5]:
            self.assertEqual(len(p), 2)

    def test_cge_sem_coordenadas(self):
        cge = self.cliente.get("/api/mapa/camadas").json()["cge"]
        self.assertTrue(cge["ok"])
        self.assertEqual(cge["estado"], {"titulo": "Estado de atenção para alagamentos", "quando": "12/11 09:00"})
        self.assertEqual(cge["ativos"], 1)
        self.assertEqual(cge["pontos"], [{"bairro": "Santo Amaro", "via": "Av. Teste", "transitavel": False}])

    def test_cge_fora_do_ar(self):
        fora = {"ok": False, "lido_em": "", "estado": None, "ativos": None, "avisos": [], "pontos_hoje": [], "ativos_lista": []}
        with mock.patch.object(fontes, "alertas_cge", return_value=fora):
            cge = self.cliente.get("/api/mapa/camadas").json()["cge"]
        self.assertEqual(cge, {"ok": False, "estado": None, "ativos": None, "pontos": []})

    def test_simulacao_de_falha(self):
        d = self.cliente.get("/api/mapa/camadas", params={"simular": "9"}).json()
        l9 = next(l for l in d["linhas"] if l["numero"] == "9")
        self.assertEqual(l9["nivel"], "parada")
        self.assertTrue(l9["simulado"])
        outras = [l for l in d["linhas"] if l["numero"] != "9"]
        self.assertFalse(any(l["simulado"] for l in outras))

    def test_linha_sem_dado(self):
        sem9 = {k: v for k, v in LINHAS.items() if k != "9"}
        with mock.patch.object(fontes, "situacao_linhas", return_value=dict(SITUACAO, linhas=sem9)):
            d = self.cliente.get("/api/mapa/camadas").json()
        self.assertEqual(next(l for l in d["linhas"] if l["numero"] == "9")["nivel"], "sem_dado")

    def test_arquivo_de_alagamentos_ausente(self):
        with tempfile.TemporaryDirectory() as pasta:
            with mock.patch.object(mapa, "ALAGAMENTOS", Path(pasta) / "nao_existe.json"):
                r = self.cliente.get("/api/mapa/camadas")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["alagamentos"], [])

    def test_arquivo_de_alagamentos_lido(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "alagamentos.json"
            arquivo.write_text(json.dumps({"fonte": "t", "baixado_em": "2026-11-12", "pontos": [[-23.5, -46.6], [-23.6, -46.7]]}), encoding="utf-8")
            with mock.patch.object(mapa, "ALAGAMENTOS", arquivo):
                d = self.cliente.get("/api/mapa/camadas").json()
        self.assertEqual(d["alagamentos"], [[-23.5, -46.6], [-23.6, -46.7]])

    def test_arquivo_de_alagamentos_gerado_so_tem_coordenadas(self):
        dados = json.loads((mapa.DADOS / "alagamentos_geosampa.json").read_text(encoding="utf-8")) if (mapa.DADOS / "alagamentos_geosampa.json").exists() else None
        if dados is None:
            self.skipTest("arquivo ainda não baixado")
        self.assertEqual(set(dados), {"fonte", "baixado_em", "pontos"})
        self.assertTrue(all(len(p) == 2 for p in dados["pontos"]))


if __name__ == "__main__":
    unittest.main()
