"""O pacote que a plataforma entrega para baixar: um .zip por matéria com o LEIA-ME e a entrega do portal."""
import io
import unittest
import zipfile

from fastapi.testclient import TestClient

from sistema import materias, pacotes
from sistema.api import app

COD = sorted(materias.POR_CODIGO)
URL = "https://datempo.exemplo.com.br"


class Pacotes(unittest.TestCase):
    def test_cada_materia_tem_zip_com_leia_me_e_entrega(self):
        for cod in COD:
            with self.subTest(cod=cod):
                z = zipfile.ZipFile(io.BytesIO(pacotes.pacote(cod, URL)))
                nomes = z.namelist()
                self.assertIn(f"LEIA-ME_{cod}.txt", nomes)
                self.assertTrue(any(n.startswith("entrega_para_o_portal/") for n in nomes))
                texto = z.read(f"LEIA-ME_{cod}.txt").decode("utf-8")
                for trecho in ("INTEGRANTES", "O SISTEMA", f"O QUE {cod} FAZ NO SISTEMA", "LINKS"):
                    self.assertIn(trecho, texto)
                self.assertIn(f"{URL}/materias/{cod.lower()}", texto)

    def test_sem_segredo_nem_lixo_no_zip(self):
        for cod in COD:
            nomes = zipfile.ZipFile(io.BytesIO(pacotes.pacote(cod, URL))).namelist()
            for n in nomes:
                self.assertNotIn("__pycache__", n)
                self.assertFalse(n.endswith((".pyc", ".env")) or "config.local" in n or "uso_ia" in n, n)

    def test_links_do_github_so_para_o_que_existe_no_repositorio(self):
        texto = zipfile.ZipFile(io.BytesIO(pacotes.pacote("PCP", URL))).read("LEIA-ME_PCP.txt").decode("utf-8")
        self.assertIn("https://github.com/jbelkior1/cidadao-em-dia/tree/main/entregas/pcp/citizen-assist-ai", texto)

    def test_sem_endereco_o_zip_nao_leva_link_quebrado(self):
        texto = zipfile.ZipFile(io.BytesIO(pacotes.pacote("DSA"))).read("LEIA-ME_DSA.txt").decode("utf-8")
        self.assertNotIn("/materias/", texto)
        self.assertNotIn("{URL_SISTEMA}", texto)

    def test_materia_desconhecida(self):
        with self.assertRaises(KeyError):
            pacotes.pacote("XYZ")

    def test_leia_me_curto(self):
        for cod in COD:
            self.assertLessEqual(len(pacotes.explicacao(cod, URL).splitlines()), 30, cod)

    def test_texto_sem_travessao(self):
        for cod in COD:
            self.assertNotIn("—", pacotes.explicacao(cod, URL))


class RotaDoPacote(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(app)

    def test_baixa_o_zip_com_o_endereco_do_navegador(self):
        r = self.c.get("/api/materias/pcp/pacote", headers={"host": "datempo.exemplo.com.br", "x-forwarded-proto": "https"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["content-type"], "application/zip")
        self.assertIn('filename="DaTempo_PCP.zip"', r.headers["content-disposition"])
        texto = zipfile.ZipFile(io.BytesIO(r.content)).read("LEIA-ME_PCP.txt").decode("utf-8")
        self.assertIn(f"{URL}/materias/pcp", texto)

    def test_host_estranho_nao_entra_no_texto(self):
        r = self.c.get("/api/materias/pcp/pacote", headers={"host": "x.com/<script>"})
        texto = zipfile.ZipFile(io.BytesIO(r.content)).read("LEIA-ME_PCP.txt").decode("utf-8")
        self.assertNotIn("<script>", texto)

    def test_matéria_inexistente_é_404(self):
        self.assertEqual(self.c.get("/api/materias/xyz/pacote").status_code, 404)

    def test_a_pagina_da_materia_traz_texto_fluxo_e_rotas(self):
        m = self.c.get("/api/materias/pcp").json()["materia"]
        self.assertTrue(m["explicacao"] and m["fluxo"]["passos"] and m["rotas"])


if __name__ == "__main__":
    unittest.main()
