"""Testes da entrega de DSA. Rodar da raiz do repositório:
python -m unittest discover -s tests/dsa -v
"""

import json
import os
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA_DSA = os.path.join(RAIZ, "entregas", "dsa")
sys.path.insert(0, PASTA_DSA)

import algoritmos  # noqa: E402
from catalogo import Catalogo  # noqa: E402
from lista_encadeada import ListaEncadeada  # noqa: E402
from servico import Servico  # noqa: E402


def servico(id, titulo="T", categoria="C", prazo=""):
    return Servico(id, titulo, categoria, "desc", "todos", "CRAS", prazo)


def ids(lista):
    resultado = []
    for s in lista.percorrer():
        resultado.append(s.id)
    return resultado


def lista_com(*identificadores):
    lista = ListaEncadeada()
    for i in identificadores:
        lista.inserir_fim(servico(i))
    return lista


def catalogo_com_tres():
    c = Catalogo()
    c.cadastrar("B2", "Segunda via do RG", "Documentos", "d", "todos", "Órgão estadual", "2027-01-10")
    c.cadastrar("A1", "Tarifa social", "Energia", "d", "famílias", "CRAS", "2026-12-31")
    c.cadastrar("C3", "Atendimento de saúde", "Saúde", "d", "todos", "UBS")
    return c


class TesteListaEncadeada(unittest.TestCase):
    def test_lista_vazia(self):
        lista = ListaEncadeada()
        self.assertTrue(lista.esta_vazia())
        self.assertEqual(lista.tamanho(), 0)
        self.assertEqual(ids(lista), [])
        self.assertIsNone(lista.buscar_por_id("X"))
        self.assertFalse(lista.remover("X"))

    def test_inserir_fim_e_inicio(self):
        lista = lista_com("1", "2")
        lista.inserir_inicio(servico("0"))
        lista.inserir_fim(servico("3"))
        self.assertEqual(ids(lista), ["0", "1", "2", "3"])
        self.assertEqual(lista.tamanho(), 4)
        self.assertEqual(lista.cauda.dado.id, "3")

    def test_buscar_por_id(self):
        lista = lista_com("a", "b", "c")
        self.assertEqual(lista.buscar_por_id("B").id, "b")
        self.assertIsNone(lista.buscar_por_id("z"))

    def test_atualizar(self):
        lista = lista_com("a", "b")
        self.assertTrue(lista.atualizar("b", titulo="Novo"))
        self.assertEqual(lista.buscar_por_id("b").titulo, "Novo")
        self.assertFalse(lista.atualizar("z", titulo="x"))

    def test_remover_cabeca(self):
        lista = lista_com("a", "b", "c")
        self.assertTrue(lista.remover("a"))
        self.assertEqual(ids(lista), ["b", "c"])
        self.assertEqual(lista.cabeca.dado.id, "b")
        self.assertEqual(lista.tamanho(), 2)

    def test_remover_meio(self):
        lista = lista_com("a", "b", "c")
        self.assertTrue(lista.remover("b"))
        self.assertEqual(ids(lista), ["a", "c"])
        self.assertEqual(lista.tamanho(), 2)

    def test_remover_fim_ajusta_cauda(self):
        lista = lista_com("a", "b", "c")
        self.assertTrue(lista.remover("c"))
        self.assertEqual(ids(lista), ["a", "b"])
        self.assertEqual(lista.cauda.dado.id, "b")
        lista.inserir_fim(servico("d"))
        self.assertEqual(ids(lista), ["a", "b", "d"])

    def test_remover_unico(self):
        lista = lista_com("a")
        self.assertTrue(lista.remover("a"))
        self.assertTrue(lista.esta_vazia())
        self.assertIsNone(lista.cauda)
        self.assertEqual(lista.tamanho(), 0)
        lista.inserir_fim(servico("b"))  # continua funcionando depois de esvaziar
        self.assertEqual(ids(lista), ["b"])

    def test_remover_inexistente(self):
        lista = lista_com("a", "b")
        self.assertFalse(lista.remover("z"))
        self.assertEqual(lista.tamanho(), 2)


class TesteAlgoritmos(unittest.TestCase):
    def test_comparar_texto(self):
        self.assertEqual(algoritmos.comparar_texto("abc", "abd"), -1)
        self.assertEqual(algoritmos.comparar_texto("b", "a"), 1)
        self.assertEqual(algoritmos.comparar_texto("Água", "agua"), 0)
        self.assertEqual(algoritmos.comparar_texto("ab", "abc"), -1)

    def test_contem_trecho(self):
        self.assertTrue(algoritmos.contem_trecho("Tarifa social de energia", "SOCIAL"))
        self.assertTrue(algoritmos.contem_trecho("Educação", "educacao"))
        self.assertFalse(algoritmos.contem_trecho("Saúde", "energia"))
        self.assertFalse(algoritmos.contem_trecho("ab", "abc"))

    def test_ordenar_por_titulo(self):
        c = catalogo_com_tres()
        ok, _, _ = c.ordenar("titulo")
        self.assertTrue(ok)
        # Atendimento de saúde (C3), Segunda via do RG (B2), Tarifa social (A1)
        self.assertEqual(ids(c.lista), ["C3", "B2", "A1"])

    def test_ordenar_por_id(self):
        c = catalogo_com_tres()
        c.ordenar("id")
        self.assertEqual(ids(c.lista), ["A1", "B2", "C3"])
        self.assertEqual(c.lista.cauda.dado.id, "C3")

    def test_ordenar_por_prazo_sem_prazo_no_fim(self):
        c = catalogo_com_tres()
        c.ordenar("prazo")
        self.assertEqual(ids(c.lista), ["A1", "B2", "C3"])

    def test_ordenar_muitos_e_estavel(self):
        lista = ListaEncadeada()
        for id_, titulo in (("1", "d"), ("2", "b"), ("3", "a"), ("4", "b"), ("5", "c"), ("6", "a"), ("7", "e")):
            lista.inserir_fim(Servico(id_, titulo, "c", "d", "p", "x"))
        algoritmos.ordenar(lista, "titulo")
        self.assertEqual(ids(lista), ["3", "6", "2", "4", "5", "1", "7"])
        self.assertEqual(lista.tamanho(), 7)

    def test_ordenar_vazia_e_um_elemento(self):
        lista = ListaEncadeada()
        algoritmos.ordenar(lista, "id")
        self.assertTrue(lista.esta_vazia())
        lista.inserir_fim(servico("a"))
        algoritmos.ordenar(lista, "id")
        self.assertEqual(ids(lista), ["a"])

    def test_buscar_por_titulo_e_categoria(self):
        c = catalogo_com_tres()
        _, _, achados = c.pesquisar("titulo", "via")
        self.assertEqual([s.id for s in achados], ["B2"])
        _, _, achados = c.pesquisar("categoria", "ener")
        self.assertEqual([s.id for s in achados], ["A1"])
        ok, msg, achados = c.pesquisar("titulo", "inexistente")
        self.assertFalse(ok)
        self.assertIsNone(achados)


class TesteCatalogo(unittest.TestCase):
    def test_cadastrar_ok(self):
        c = Catalogo()
        ok, _, s = c.cadastrar(" X1 ", "Título", "Cat", "desc", "todos", "CRAS")
        self.assertTrue(ok)
        self.assertEqual(s.id, "X1")
        self.assertEqual(c.lista.tamanho(), 1)

    def test_id_duplicado(self):
        c = Catalogo()
        c.cadastrar("X1", "A", "c", "d", "p", "x")
        ok, msg, _ = c.cadastrar("x1", "B", "c", "d", "p", "x")
        self.assertFalse(ok)
        self.assertIn("Já existe", msg)
        self.assertEqual(c.lista.tamanho(), 1)

    def test_campo_vazio(self):
        c = Catalogo()
        ok, msg, _ = c.cadastrar("X1", "   ", "c", "d", "p", "x")
        self.assertFalse(ok)
        self.assertIn("obrigatório", msg)
        self.assertTrue(c.lista.esta_vazia())

    def test_prazo_invalido_e_valor_incompativel(self):
        c = Catalogo()
        ok, _, _ = c.cadastrar("X1", "A", "c", "d", "p", "x", "31/12/2026")
        self.assertFalse(ok)
        ok, _, _ = c.cadastrar("X1", "A", "c", "d", "p", "x", "2026-02-30")
        self.assertFalse(ok)
        ok, _, _ = c.cadastrar("X1", 123, "c", "d", "p", "x")
        self.assertFalse(ok)

    def test_operacoes_em_lista_vazia(self):
        c = Catalogo()
        for resultado in (c.listar(), c.consultar("A"), c.excluir("A"), c.ordenar("id"),
                          c.pesquisar("titulo", "a"), c.atualizar("A", "titulo", "x")):
            self.assertFalse(resultado[0])
            self.assertIn("vazia", resultado[1])

    def test_consultar_e_nao_encontrado(self):
        c = catalogo_com_tres()
        ok, _, s = c.consultar("a1")
        self.assertTrue(ok)
        self.assertEqual(s.titulo, "Tarifa social")
        ok, msg, _ = c.consultar("ZZ")
        self.assertFalse(ok)
        self.assertIn("não encontrado", msg)

    def test_atualizar_regras(self):
        c = catalogo_com_tres()
        ok, _, _ = c.atualizar("A1", "titulo", "Tarifa social nova")
        self.assertTrue(ok)
        self.assertEqual(c.consultar("A1")[2].titulo, "Tarifa social nova")
        self.assertFalse(c.atualizar("A1", "titulo", "  ")[0])
        self.assertFalse(c.atualizar("A1", "id", "Z9")[0])
        self.assertFalse(c.atualizar("A1", "prazo", "ontem")[0])
        self.assertFalse(c.atualizar("ZZ", "titulo", "x")[0])
        self.assertTrue(c.atualizar("A1", "prazo", "")[0])  # opcional pode ser limpo

    def test_excluir(self):
        c = catalogo_com_tres()
        self.assertTrue(c.excluir("A1")[0])
        self.assertEqual(c.lista.tamanho(), 2)
        self.assertFalse(c.excluir("A1")[0])

    def test_carga_inicial(self):
        c = Catalogo()
        caminho = os.path.join(PASTA_DSA, "dados", "servicos.json")
        with open(caminho, encoding="utf-8") as arquivo:
            esperado = len(json.load(arquivo))
        ok, _, qtd = c.carregar_json(caminho)
        self.assertTrue(ok)
        self.assertEqual(qtd, esperado)
        self.assertEqual(c.lista.tamanho(), esperado)
        ok, _, _ = c.carregar_json(os.path.join(PASTA_DSA, "dados", "nao_existe.json"))
        self.assertFalse(ok)


class TestePureza(unittest.TestCase):
    def test_sem_funcoes_prontas_de_ordenacao_e_busca(self):
        for nome in ("algoritmos.py", "lista_encadeada.py"):
            with open(os.path.join(PASTA_DSA, nome), encoding="utf-8") as arquivo:
                texto = arquivo.read()
            for proibido in ("sorted(", ".sort(", ".index(", ".find("):
                self.assertNotIn(proibido, texto, nome + " usa " + proibido)

    def test_sem_colecoes_nativas_na_lista(self):
        with open(os.path.join(PASTA_DSA, "lista_encadeada.py"), encoding="utf-8") as arquivo:
            texto = arquivo.read()
        for proibido in ("[]", "{}", "list(", "dict(", "set("):
            self.assertNotIn(proibido, texto, "lista_encadeada.py usa " + proibido)


if __name__ == "__main__":
    unittest.main()
