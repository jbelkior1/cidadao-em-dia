# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Operações do sistema sobre a lista encadeada (sem input/print).

Cada operação devolve uma tupla (sucesso, mensagem, dado):
- sucesso: True/False
- mensagem: texto claro para mostrar ao usuário
- dado: o que foi pedido (um Servico, uma list para exibição...) ou None
"""

import json

from algoritmos import buscar_por_atributo, ordenar
from lista_encadeada import ListaEncadeada
from servico import CAMPOS_OBRIGATORIOS, CAMPOS_OPCIONAIS, ROTULOS, Servico, data_valida

CAMPOS_EDITAVEIS = ("titulo", "categoria", "descricao", "publico_alvo", "canal",
                    "prazo", "fonte", "verificado_em")  # o id nunca muda
CRITERIOS_ORDEM = ("titulo", "id", "prazo")
ATRIBUTOS_BUSCA = ("titulo", "categoria")
NOMES = {"titulo": "título", "categoria": "categoria", "id": "id", "prazo": "prazo"}


def _validar_campo(campo, valor):
    """Devolve uma mensagem de erro, ou None se o valor é aceitável."""
    if valor == "" and campo in CAMPOS_OBRIGATORIOS:
        return "O campo '" + ROTULOS[campo] + "' é obrigatório e não pode ficar vazio."
    if campo == "prazo" and valor != "" and not data_valida(valor):
        return "Prazo inválido: use uma data real no formato AAAA-MM-DD (ex.: 2026-12-31)."
    return None


class Catalogo:
    """Guarda os serviços numa ListaEncadeada e oferece as operações do sistema."""

    def __init__(self):
        self.lista = ListaEncadeada()

    # ---------- cadastrar ----------
    def cadastrar(self, id, titulo, categoria, descricao, publico_alvo, canal,
                  prazo="", fonte="", verificado_em=""):
        valores = (id, titulo, categoria, descricao, publico_alvo, canal, prazo, fonte, verificado_em)
        campos = CAMPOS_OBRIGATORIOS + CAMPOS_OPCIONAIS
        limpos = []
        for campo, valor in zip(campos, valores):
            if not isinstance(valor, str):
                return False, "Valor incompatível no campo '" + ROTULOS[campo] + "': esperado texto.", None
            valor = valor.strip()
            erro = _validar_campo(campo, valor)
            if erro is not None:
                return False, erro, None
            limpos.append(valor)
        if self.lista.buscar_por_id(limpos[0]) is not None:
            return False, "Já existe um registro com o id '" + limpos[0] + "'.", None
        servico = Servico(*limpos)
        self.lista.inserir_fim(servico)
        return True, "Registro '" + servico.id + "' cadastrado.", servico

    # ---------- consultar / listar ----------
    def consultar(self, id):
        id = id.strip()
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nenhum registro cadastrado.", None
        if id == "":
            return False, "Informe um identificador.", None
        servico = self.lista.buscar_por_id(id)
        if servico is None:
            return False, "Registro '" + id + "' não encontrado.", None
        return True, "Registro encontrado.", servico

    def listar(self):
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nenhum registro cadastrado.", None
        registros = []  # list comum só para exibição
        for servico in self.lista.percorrer():
            registros.append(servico)
        return True, str(self.lista.tamanho()) + " registro(s) na lista.", registros

    # ---------- atualizar ----------
    def atualizar(self, id, campo, valor):
        id = id.strip()
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nenhum registro para atualizar.", None
        if campo == "id":
            return False, "O identificador não pode ser alterado.", None
        if campo not in CAMPOS_EDITAVEIS:
            return False, "Campo '" + campo + "' não existe.", None
        valor = valor.strip()
        servico = self.lista.buscar_por_id(id)
        if servico is None:
            return False, "Registro '" + id + "' não encontrado.", None
        erro = _validar_campo(campo, valor)
        if erro is not None:
            return False, erro, None
        self.lista.atualizar(id, **{campo: valor})
        return True, "Registro '" + servico.id + "' atualizado.", servico

    # ---------- excluir ----------
    def excluir(self, id):
        id = id.strip()
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nenhum registro para excluir.", None
        if id == "":
            return False, "Informe um identificador.", None
        if self.lista.remover(id):
            return True, "Registro '" + id + "' excluído.", None
        return False, "Registro '" + id + "' não encontrado.", None

    # ---------- pesquisar ----------
    def pesquisar(self, atributo, trecho):
        trecho = trecho.strip()
        if atributo not in ATRIBUTOS_BUSCA:
            return False, "Só é possível pesquisar por título ou categoria.", None
        if trecho == "":
            return False, "Digite um texto para pesquisar.", None
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nada para pesquisar.", None
        achados = buscar_por_atributo(self.lista, atributo, trecho)
        if len(achados) == 0:
            return False, "Nenhum registro com '" + trecho + "' em " + NOMES[atributo] + ".", None
        return True, str(len(achados)) + " registro(s) encontrado(s).", achados

    # ---------- ordenar ----------
    def ordenar(self, criterio):
        if criterio not in CRITERIOS_ORDEM:
            return False, "Critério inválido: use título, id ou prazo.", None
        if self.lista.esta_vazia():
            return False, "A lista está vazia: nada para ordenar.", None
        ordenar(self.lista, criterio)
        return True, "Lista ordenada por " + NOMES[criterio] + " (crescente).", None

    # ---------- carga inicial ----------
    def carregar_json(self, caminho):
        """Lê o JSON e insere os registros na lista, um nó por vez.
        (O json.load devolve uma list temporária só para a leitura; ela não guarda nada.)"""
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                itens = json.load(arquivo)
        except FileNotFoundError:
            return False, "Arquivo de dados não encontrado: " + caminho, 0
        except (ValueError, OSError):
            return False, "Não foi possível ler o arquivo de dados: " + caminho, 0
        if not isinstance(itens, list):
            return False, "Formato inesperado no arquivo de dados.", 0
        carregados = 0
        ignorados = 0
        for item in itens:
            if not isinstance(item, dict):
                ignorados += 1
                continue
            args = []
            for campo in CAMPOS_OBRIGATORIOS + CAMPOS_OPCIONAIS:
                args.append(item.get(campo, ""))
            ok, _, _ = self.cadastrar(*args)
            if ok:
                carregados += 1
            else:
                ignorados += 1
        mensagem = str(carregados) + " registro(s) carregado(s)"
        if ignorados > 0:
            mensagem = mensagem + ", " + str(ignorados) + " ignorado(s) por erro"
        return True, mensagem + ".", carregados
