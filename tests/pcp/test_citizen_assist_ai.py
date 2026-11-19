"""Testes do Citizen Assist AI (PCP). Rodar da raiz do repositório:

    python -m unittest discover -s tests/pcp -v

Os testes usam uma base de teste criada em pasta temporária; não dependem
do conteúdo de entregas/pcp/citizen-assist-ai/data/base_conhecimento.json.
"""

import contextlib
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA_ENTREGA = os.path.join(RAIZ, "entregas", "pcp", "citizen-assist-ai")
sys.path.insert(0, PASTA_ENTREGA)

from assistente import Assistente  # noqa: E402
from base_conhecimento import BaseConhecimento, normalizar  # noqa: E402
from orientacao import Orientacao  # noqa: E402
import main as programa  # noqa: E402

BASE_TESTE = [
    {"id": 3, "categoria": "Saúde",
     "titulo": "Fazer o Cartão Nacional de Saúde (Cartão SUS)",
     "palavras_chave": ["cartao sus", "cartao do sus", "sus", "cns"],
     "resposta": "Pode ser feito em uma UBS ou no app Meu SUS Digital.",
     "documentos": ["Documento com foto", "CPF"],
     "onde": "Qualquer UBS ou aplicativo Meu SUS Digital",
     "fonte": "https://www.gov.br/saude", "verificado_em": "2026-11-05"},
    {"id": 4, "categoria": "Saúde",
     "titulo": "Agendar vacina na unidade de saúde",
     "palavras_chave": ["vacina", "vacinacao", "caderneta"],
     "resposta": "Teste: procure a unidade de saúde.",
     "documentos": ["Documento com foto"], "onde": "UBS",
     "fonte": "https://www.gov.br/saude", "verificado_em": "2026-11-05"},
    {"id": 5, "categoria": "Documentos",
     "titulo": "Segunda via do RG",
     "palavras_chave": ["rg", "identidade", "segunda via"],
     "resposta": "Teste: pedir no órgão de identificação.",
     "documentos": [], "onde": "Órgão do estado",
     "fonte": "https://www.gov.br/", "verificado_em": "2026-11-05"},
    {"id": 6, "categoria": "Trabalho",
     "titulo": "Carteira de trabalho digital",
     "palavras_chave": ["carteira de trabalho", "ctps", "primeiro emprego"],
     "resposta": "Teste: baixe o aplicativo.",
     "documentos": ["CPF"], "onde": "Aplicativo",
     "fonte": "https://www.gov.br/trabalho-e-emprego", "verificado_em": "2026-11-05"},
]


def digitar(*linhas):
    """Simula a pessoa digitando: devolve o patch de input().

    Quando as linhas acabam, input() levanta EOFError sempre (como no fim de um arquivo).
    """
    restantes = list(linhas)

    def proxima_linha(mensagem=""):
        if restantes:
            return restantes.pop(0)
        raise EOFError

    return mock.patch("builtins.input", side_effect=proxima_linha)


class TesteComPasta(unittest.TestCase):
    """Cria uma pasta temporária com a base de teste e um assistente."""

    def setUp(self):
        self.temporaria = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporaria.cleanup)
        self.pasta = self.temporaria.name
        self.caminho_base = os.path.join(self.pasta, "base.json")
        with open(self.caminho_base, "w", encoding="utf-8") as arquivo:
            json.dump(BASE_TESTE, arquivo, ensure_ascii=False)
        self.base = BaseConhecimento(self.caminho_base)
        self.base.carregar()
        self.assistente = self.novo_assistente()

    def novo_assistente(self):
        return Assistente("Teste", self.base,
                          caminho_historico=os.path.join(self.pasta, "historico.json"),
                          caminho_csv=os.path.join(self.pasta, "atendimentos.csv"))

    def executar(self, funcao, *linhas):
        """Roda uma tela com entradas simuladas e devolve o que foi impresso."""
        saida = io.StringIO()
        with digitar(*linhas), contextlib.redirect_stdout(saida):
            funcao()
        return saida.getvalue()


class TesteNormalizacao(unittest.TestCase):
    def test_remove_acentos_pontuacao_e_maiusculas(self):
        self.assertEqual(normalizar("  Como faço o Cartão do SUS?! "), " como faco o cartao do sus ")

    def test_texto_vazio(self):
        self.assertEqual(normalizar("   ").strip(), "")


class TesteBase(TesteComPasta):
    def test_carrega_objetos_orientacao(self):
        self.assertEqual(len(self.base.orientacoes), 4)
        self.assertIsInstance(self.base.orientacoes[0], Orientacao)
        self.assertEqual(self.base.erro, "")

    def test_categorias_sem_repeticao(self):
        self.assertEqual(self.base.categorias(), ["Saúde", "Documentos", "Trabalho"])

    def test_por_categoria(self):
        titulos = [o.id for o in self.base.por_categoria("Saúde")]
        self.assertEqual(titulos, [3, 4])

    def test_exemplo_numerico_do_enunciado(self):
        """'Como faço o cartão do SUS?' = +3 'cartao do sus', +3 'sus', +1 'cartao' = 7."""
        orientacao = self.base.orientacoes[0]
        pergunta = "Como faço o cartão do SUS?"
        self.assertEqual(self.base.pontuar(pergunta, orientacao), 7)
        detalhe = self.base.detalhar_pontuacao(pergunta, orientacao)
        self.assertEqual(detalhe["palavras_chave"], ["cartao do sus", "sus"])
        self.assertEqual(detalhe["palavras_titulo"], ["cartao"])
        self.assertEqual(detalhe["pontos"], 7)
        resposta = self.assistente.responder(pergunta)
        self.assertEqual(resposta["confianca"], "ALTA")
        self.assertEqual(resposta["pontos"], 7)
        self.assertEqual(resposta["orientacao"].id, 3)

    def test_palavra_inteira_nao_casa_pedaco(self):
        """'rg' não pode casar dentro de 'energia'."""
        orientacao = self.base.orientacoes[2]
        self.assertEqual(self.base.pontuar("conta de energia", orientacao), 0)

    def test_palavra_do_titulo_conta_uma_vez(self):
        orientacao = self.base.orientacoes[0]
        # 'cartao' aparece duas vezes na pergunta e duas no título: só +1
        self.assertEqual(self.base.pontuar("cartao cartao", orientacao), 1)

    def test_palavra_curta_do_titulo_nao_pontua(self):
        orientacao = self.base.orientacoes[0]   # título tem 'o' e 'de'
        self.assertEqual(self.base.pontuar("o de", orientacao), 0)

    def test_buscar_devolve_tuplas_ordenadas(self):
        resultados = self.base.buscar("cartao do sus e vacina")
        self.assertTrue(all(isinstance(t, tuple) and len(t) == 2 for t in resultados))
        pontos = [t[0] for t in resultados]
        self.assertEqual(pontos, sorted(pontos, reverse=True))
        self.assertEqual(resultados[0][1].id, 3)
        self.assertIsInstance(resultados[0][1], Orientacao)

    def test_faixas_de_confianca(self):
        self.assertEqual(BaseConhecimento.nivel_confianca(6), "ALTA")
        self.assertEqual(BaseConhecimento.nivel_confianca(5), "MÉDIA")
        self.assertEqual(BaseConhecimento.nivel_confianca(3), "MÉDIA")
        self.assertEqual(BaseConhecimento.nivel_confianca(2), "NENHUMA")

    def test_confianca_media(self):
        resposta = self.assistente.responder("preciso da vacina")
        self.assertEqual(resposta["pontos"], 4)   # +3 vacina, +1 palavra do título
        self.assertEqual(resposta["confianca"], "MÉDIA")

    def test_nao_encontrei_com_so_1_ponto(self):
        # 'saude' (5 letras) está no título de duas orientações, mas vale só 1 ponto
        resposta = self.assistente.responder("quero saude")
        self.assertFalse(resposta["encontrou"])
        self.assertEqual(resposta["confianca"], "NENHUMA")
        self.assertIn("Saúde", resposta["categorias"])

    def test_nao_encontrei_sem_pontos(self):
        resposta = self.assistente.responder("banana voadora")
        self.assertFalse(resposta["encontrou"])
        self.assertIsNone(resposta["orientacao"])

    def test_melhor_e_ate_duas_alternativas(self):
        pergunta = "cartao sus vacina rg identidade carteira de trabalho ctps"
        resposta = self.assistente.responder(pergunta)
        self.assertTrue(resposta["encontrou"])
        self.assertEqual(len(resposta["alternativas"]), 2)
        pontos = [resposta["pontos"]] + [a["pontos"] for a in resposta["alternativas"]]
        self.assertEqual(pontos, sorted(pontos, reverse=True))

    def test_responder_dict_pronto_para_json(self):
        resposta = self.assistente.responder_dict("cartao do sus")
        json.dumps(resposta, ensure_ascii=False)   # não pode levantar erro
        self.assertEqual(resposta["orientacao"]["id"], 3)


class TesteArquivosDaBase(unittest.TestCase):
    def test_arquivo_ausente_nao_derruba(self):
        base = BaseConhecimento(os.path.join(tempfile.gettempdir(), "nao_existe_xyz.json"))
        self.assertEqual(base.carregar(), 0)
        self.assertTrue(base.erro)
        self.assertEqual(base.categorias(), [])
        self.assertEqual(base.buscar("sus"), [])

    def test_arquivo_corrompido_nao_derruba(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "ruim.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write("{ isto não é json [")
            base = BaseConhecimento(caminho)
            self.assertEqual(base.carregar(), 0)
            self.assertIn("corrompido", base.erro)

    def test_registro_invalido_e_ignorado(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "mista.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump([BASE_TESTE[0], {"id": 9, "titulo": "incompleto"}, "texto solto"], arquivo)
            base = BaseConhecimento(caminho)
            self.assertEqual(base.carregar(), 1)
            self.assertEqual(base.ignoradas, 2)

    def test_json_que_nao_e_lista(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = os.path.join(pasta, "dict.json")
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump({"a": 1}, arquivo)
            base = BaseConhecimento(caminho)
            self.assertEqual(base.carregar(), 0)
            self.assertTrue(base.erro)

    def test_assistente_com_base_vazia_nao_trava(self):
        base = BaseConhecimento("nao_existe.json")
        base.carregar()
        with tempfile.TemporaryDirectory() as pasta:
            assistente = Assistente("T", base, os.path.join(pasta, "h.json"),
                                    os.path.join(pasta, "a.csv"))
            saida = io.StringIO()
            with digitar("1", "2", "0", "0"), contextlib.redirect_stdout(saida):
                # perguntar, navegar e sair (nota 0 = voltar; depois a entrada acaba e encerra)
                assistente.menu()
            self.assertIn("vazia", saida.getvalue())


class TesteOrientacao(unittest.TestCase):
    def test_ida_e_volta_do_dicionario(self):
        orientacao = Orientacao.de_dict(BASE_TESTE[0])
        self.assertEqual(orientacao.para_dict(), BASE_TESTE[0])

    def test_exibir_mostra_campos_e_aviso(self):
        orientacao = Orientacao.de_dict(BASE_TESTE[0])
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            orientacao.exibir()
        texto = saida.getvalue()
        for trecho in ("Fazer o Cartão Nacional de Saúde (Cartão SUS)  [Saúde]",
                       "Documentos necessários:", "  - CPF",
                       "Onde: Qualquer UBS", "Fonte: https://www.gov.br/saude (verificado em 2026-11-05)",
                       "NÃO é um canal oficial"):
            self.assertIn(trecho, texto)


class TesteDadosPessoais(TesteComPasta):
    def test_bloqueia_cpf_telefone_email(self):
        for texto in ("meu cpf é 123.456.789-00", "12345678", "liga 11 98888-7777",
                      "1 2 3 4 5 6 7 8", "joao@exemplo.com", "@"):
            self.assertTrue(Assistente.tem_dado_pessoal(texto), texto)

    def test_nao_bloqueia_texto_normal(self):
        for texto in ("como faço o cartão do sus", "tenho 65 anos", "1234567", "cep 12 34 56"):
            self.assertFalse(Assistente.tem_dado_pessoal(texto), texto)

    def test_responder_bloqueia(self):
        resposta = self.assistente.responder("meu cpf é 123.456.789-00 cartao sus")
        self.assertTrue(resposta["bloqueada"])
        self.assertFalse(resposta["encontrou"])

    def test_registrar_recusa_dado_pessoal(self):
        self.assertIsNone(self.assistente.registrar("pergunta", "cpf 12345678900", None,
                                                    False, False, 1, 1.0))
        self.assertEqual(self.assistente.historico, [])
        self.assertFalse(os.path.exists(os.path.join(self.pasta, "historico.json")))

    def test_tela_recusa_e_nao_grava(self):
        saida = self.executar(self.assistente.perguntar,
                              "meu cpf é 123.456.789-00", "escreva a@b.com", "0")
        self.assertEqual(saida.count("Atenção: não digite CPF, telefone ou e-mail. Reescreva."), 2)
        self.assertEqual(self.assistente.historico, [])
        self.assertFalse(os.path.exists(os.path.join(self.pasta, "historico.json")))


class TesteHistoricoIndicadoresCsv(TesteComPasta):
    def test_registrar_grava_campos_do_enunciado(self):
        self.assistente.registrar("pergunta", "cartao sus", 3, True, True, 1, 2.5)
        with open(os.path.join(self.pasta, "historico.json"), encoding="utf-8") as arquivo:
            salvo = json.load(arquivo)
        self.assertEqual(len(salvo), 1)
        self.assertEqual(set(salvo[0]), {"data", "origem", "pergunta", "orientacao_id",
                                         "encontrou", "ajudou", "tentativas", "tempo_segundos"})
        self.assertEqual(salvo[0]["origem"], "pergunta")
        self.assertEqual(salvo[0]["tempo_segundos"], 2.5)

    def test_historico_e_recarregado(self):
        self.assistente.registrar("pergunta", "cartao sus", 3, True, True, 1, 2.5)
        novo = self.novo_assistente()
        self.assertEqual(len(novo.historico), 1)

    def test_historico_corrompido_nao_derruba(self):
        with open(os.path.join(self.pasta, "historico.json"), "w", encoding="utf-8") as arquivo:
            arquivo.write("{{{ quebrado")
        self.assertEqual(self.novo_assistente().historico, [])

    def test_indicadores(self):
        a = self.assistente
        a.registrar("pergunta", "p1", 3, True, True, 1, 4.0)
        a.registrar("pergunta", "p2", 4, True, True, 3, 8.0)
        a.registrar("pergunta", "p3 sem resposta", None, False, False, 2, 6.0)
        a.registrar("categoria", "p4 nao ajudou", 5, True, False, 1, 2.0)
        a.registrar_nota(4)
        a.registrar_nota(5)
        ind = a.indicadores()
        self.assertEqual(ind["total"], 4)
        self.assertEqual(ind["resposta_encontrada_pct"], 75.0)
        self.assertEqual(ind["taxa_acerto_pct"], 50.0)
        self.assertEqual(ind["tempo_medio"], 6.0)
        self.assertEqual(ind["tentativas_media"], 1.8)
        self.assertEqual(ind["facilidade_media"], 4.5)
        self.assertEqual(ind["duvidas_sem_solucao"], ["p3 sem resposta", "p4 nao ajudou"])

    def test_indicadores_sem_atendimentos(self):
        ind = self.assistente.indicadores()
        self.assertEqual(ind["total"], 0)
        self.assertEqual(ind["taxa_acerto_pct"], 0.0)
        self.assertIsNone(ind["facilidade_media"])
        self.assertEqual(ind["duvidas_sem_solucao"], [])

    def test_exportar_csv_com_dictwriter(self):
        self.assistente.registrar("pergunta", "cartao do sus, por favor", 3, True, True, 1, 2.5)
        self.assistente.registrar("categoria", "Navegação: Segunda via do RG", 5, True, False, 1, 1.0)
        linhas = self.assistente.exportar_csv()
        self.assertEqual(linhas, 2)
        with open(os.path.join(self.pasta, "atendimentos.csv"), newline="",
                  encoding="utf-8-sig") as arquivo:
            lidas = list(csv.DictReader(arquivo))
        self.assertEqual(len(lidas), 2)
        self.assertEqual(lidas[0]["pergunta"], "cartao do sus, por favor")
        self.assertEqual(lidas[0]["orientacao_id"], "3")
        self.assertEqual(list(lidas[0]), ["data", "origem", "pergunta", "orientacao_id",
                                          "encontrou", "ajudou", "tentativas", "tempo_segundos"])

    def test_exportar_csv_em_pasta_impossivel_nao_derruba(self):
        arquivo_no_lugar_da_pasta = os.path.join(self.pasta, "arquivo.txt")
        with open(arquivo_no_lugar_da_pasta, "w", encoding="utf-8") as arquivo:
            arquivo.write("x")
        self.assertIsNone(self.assistente.exportar_csv(
            os.path.join(arquivo_no_lugar_da_pasta, "sub", "a.csv")))


class TesteTelas(TesteComPasta):
    def test_pergunta_encontrada_e_ajudou(self):
        saida = self.executar(self.assistente.perguntar, "Como faço o cartão do SUS?", "s", "0")
        self.assertIn("Confiança da resposta: ALTA (7 pontos)", saida)
        self.assertIn(">> Fazer o Cartão Nacional de Saúde (Cartão SUS)  [Saúde]", saida)
        self.assertIn("Documentos necessários:", saida)
        self.assertIn("Fonte: https://www.gov.br/saude (verificado em 2026-11-05)", saida)
        self.assertIn("NÃO é um canal oficial", saida)
        self.assertEqual(len(self.assistente.historico), 1)
        registro = self.assistente.historico[0]
        self.assertTrue(registro["encontrou"] and registro["ajudou"])
        self.assertEqual(registro["orientacao_id"], 3)
        self.assertEqual(registro["tentativas"], 1)

    def test_nao_encontrei_depois_encontrou_conta_tentativas(self):
        saida = self.executar(self.assistente.perguntar, "banana", "cartao sus", "s", "0")
        self.assertIn("Não encontrei", saida)
        registro = self.assistente.historico[0]
        self.assertEqual(registro["tentativas"], 2)
        self.assertTrue(registro["ajudou"])

    def test_encontrou_nao_ajudou_e_depois_nao_encontrou_registra_ultima_tentativa(self):
        # a base de teste: "cartao sus" acha a orientação 3; "banana azul" não acha nada
        self.executar(self.assistente.perguntar, "cartao sus", "n", "banana azul", "0")
        self.assertEqual(len(self.assistente.historico), 1)
        registro = self.assistente.historico[0]
        self.assertEqual(registro["pergunta"], "banana azul")
        self.assertIsNone(registro["orientacao_id"])
        self.assertFalse(registro["encontrou"])
        self.assertFalse(registro["ajudou"])
        self.assertEqual(registro["tentativas"], 2)

    def test_desistir_registra_sem_solucao(self):
        self.executar(self.assistente.perguntar, "banana", "0")
        registro = self.assistente.historico[0]
        self.assertFalse(registro["encontrou"])
        self.assertFalse(registro["ajudou"])
        self.assertEqual(registro["pergunta"], "banana")

    def test_voltar_sem_perguntar_nao_registra(self):
        self.executar(self.assistente.perguntar, "0")
        self.assertEqual(self.assistente.historico, [])

    def test_entradas_invalidas_na_pergunta_nao_encerram(self):
        saida = self.executar(self.assistente.perguntar, "", "   ", "cartao sus",
                              "talvez", "", "s", "0")
        self.assertIn("Resposta inválida", saida)
        self.assertEqual(len(self.assistente.historico), 1)

    def test_texto_sem_letras_nem_numeros_nao_conta_como_duvida(self):
        # melhoria do teste com usuários: "-" virava um atendimento sem solução
        saida = self.executar(self.assistente.perguntar, "-", "?!", "0")
        self.assertIn("Escreva sua dúvida com palavras", saida)
        self.assertEqual(self.assistente.historico, [])

    def test_texto_sem_letras_depois_pergunta_valida(self):
        self.executar(self.assistente.perguntar, "...", "cartao sus", "s", "0")
        self.assertEqual(len(self.assistente.historico), 1)
        self.assertEqual(self.assistente.historico[0]["tentativas"], 1)

    def test_nao_ajudou_e_tenta_de_novo(self):
        self.executar(self.assistente.perguntar, "cartao sus", "n", "vacina", "s", "0")
        self.assertEqual(len(self.assistente.historico), 1)
        self.assertEqual(self.assistente.historico[0]["tentativas"], 2)

    def test_zero_na_pergunta_s_n_volta(self):
        self.executar(self.assistente.perguntar, "cartao sus", "0")
        self.assertFalse(self.assistente.historico[0]["ajudou"])

    def test_entrada_encerrada_nao_trava(self):
        self.executar(self.assistente.perguntar, "banana")   # acaba a entrada (EOFError)
        self.assertEqual(len(self.assistente.historico), 1)

    def test_navegar_por_categoria(self):
        saida = self.executar(self.assistente.navegar,
                              "x", "9", "-1", "", "1", "2", "s", "0", "0")
        self.assertIn("1. Saúde", saida)
        self.assertIn("0. Voltar", saida)
        self.assertIn("Opção inválida", saida)
        self.assertIn("Agendar vacina na unidade de saúde", saida)
        registro = self.assistente.historico[0]
        self.assertEqual(registro["origem"], "categoria")
        self.assertEqual(registro["orientacao_id"], 4)
        self.assertTrue(registro["ajudou"])

    def test_navegar_voltar_direto(self):
        self.executar(self.assistente.navegar, "0")
        self.assertEqual(self.assistente.historico, [])

    def test_menu_completo(self):
        saida = self.executar(self.assistente.menu,
                              "abc", "7", "3", "1", "cartao sus", "s", "0",
                              "4", "0", "6", "5")
        self.assertIn("Opção inválida", saida)
        self.assertIn("=== Indicadores ===", saida)
        self.assertIn("Exportados 1 atendimentos", saida)
        self.assertIn("Nota inválida", saida)
        self.assertEqual(self.assistente.notas, [5])
        self.assertTrue(os.path.exists(os.path.join(self.pasta, "atendimentos.csv")))

    def test_sair_pede_nota_de_1_a_5(self):
        saida = self.executar(self.assistente.menu, "0", "9", "x", "", "3")
        self.assertEqual(saida.count("Nota inválida"), 3)
        self.assertEqual(self.assistente.notas, [3])


class TesteEstruturaDaEntrega(unittest.TestCase):
    def test_exatamente_quatro_arquivos_py_na_entrega(self):
        achados = []
        for pasta, _, arquivos in os.walk(PASTA_ENTREGA):
            if "__pycache__" in pasta:
                continue
            achados += [a for a in arquivos if a.endswith(".py")]
        self.assertEqual(sorted(achados),
                         ["assistente.py", "base_conhecimento.py", "main.py", "orientacao.py"])

    def test_base_entregue_carrega(self):
        base = BaseConhecimento(os.path.join(PASTA_ENTREGA, "data", "base_conhecimento.json"))
        self.assertGreater(base.carregar(), 0)
        self.assertEqual(base.ignoradas, 0)

    def test_main_usa_pasta_da_entrega(self):
        self.assertEqual(os.path.normcase(programa.PASTA), os.path.normcase(PASTA_ENTREGA))


if __name__ == "__main__":
    unittest.main()
