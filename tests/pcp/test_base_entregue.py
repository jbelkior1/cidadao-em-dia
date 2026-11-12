"""Confere se a base entregue cumpre os mínimos do enunciado do PCP.

Mínimos: 10 orientações, 3 categorias e 3 palavras-chave por orientação, com
todos os campos obrigatórios, fonte e data de conferência.
"""
import json
import os
import re
import unittest

PASTA_ENTREGA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "entregas", "pcp", "citizen-assist-ai")
CAMPOS = ("id", "categoria", "titulo", "palavras_chave", "resposta", "documentos", "onde", "fonte", "verificado_em")


class BaseEntregue(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PASTA_ENTREGA, "data", "base_conhecimento.json"), encoding="utf-8") as arquivo:
            cls.base = json.load(arquivo)

    def test_minimos_do_enunciado(self):
        self.assertGreaterEqual(len(self.base), 10)
        self.assertGreaterEqual(len({o["categoria"] for o in self.base}), 3)
        for o in self.base:
            self.assertGreaterEqual(len(o["palavras_chave"]), 3, o["titulo"])

    def test_campos_obrigatorios_preenchidos(self):
        for o in self.base:
            for campo in CAMPOS:
                self.assertIn(campo, o, f"{o.get('titulo')}: falta {campo}")
            self.assertTrue(o["resposta"].strip() and o["onde"].strip(), o["titulo"])

    def test_ids_unicos(self):
        ids = [o["id"] for o in self.base]
        self.assertEqual(len(ids), len(set(ids)))

    def test_fonte_oficial_e_data(self):
        for o in self.base:
            self.assertRegex(o["fonte"], r"^https://[^/]*(\.gov\.br|\.jus\.br)/", o["titulo"])
            self.assertTrue(re.fullmatch(r"\d{4}-\d{2}-\d{2}", o["verificado_em"]), o["titulo"])

    def test_nada_de_texto_provisorio(self):
        texto = json.dumps(self.base, ensure_ascii=False).lower()
        for marca in ("exemplo:", "provisório", "a conferir"):
            self.assertNotIn(marca, texto)


if __name__ == "__main__":
    unittest.main()
