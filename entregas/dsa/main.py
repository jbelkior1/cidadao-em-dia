"""Menu interativo de terminal do Citizen Assist AI (DSA).

Execute com:  python main.py   (de dentro da pasta entregas/dsa)
Este arquivo só conversa com o usuário (input/print); a lógica fica em catalogo.py.
"""

import os
import sys

from catalogo import Catalogo
from servico import CAMPOS_OBRIGATORIOS, CAMPOS_OPCIONAIS, ROTULOS

CAMINHO_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "servicos.json")

MENU = """
===== Citizen Assist AI - Serviços e orientações =====
1 - Cadastrar serviço
2 - Consultar por identificador
3 - Listar todos
4 - Atualizar registro
5 - Excluir registro
6 - Pesquisar (título ou categoria)
7 - Ordenar (título, id ou prazo)
0 - Sair"""


def mostrar(resultado):
    """Imprime a mensagem de uma operação e devolve o dado."""
    _, mensagem, dado = resultado
    print(mensagem)
    return dado


def mostrar_lista(registros):
    for servico in registros:
        print(servico.resumo())


def opcao_cadastrar(catalogo):
    print("Preencha os campos (os marcados com * são obrigatórios).")
    respostas = []
    for campo in CAMPOS_OBRIGATORIOS + CAMPOS_OPCIONAIS:
        marca = "*" if campo in CAMPOS_OBRIGATORIOS else " "
        respostas.append(input(marca + ROTULOS[campo] + ": "))
    mostrar(catalogo.cadastrar(*respostas))


def opcao_consultar(catalogo):
    servico = mostrar(catalogo.consultar(input("Identificador: ")))
    if servico is not None:
        print(servico.como_texto())


def opcao_listar(catalogo):
    registros = mostrar(catalogo.listar())
    if registros is not None:
        mostrar_lista(registros)


def opcao_atualizar(catalogo):
    id = input("Identificador do registro a atualizar: ")
    servico = mostrar(catalogo.consultar(id))
    if servico is None:
        return
    print(servico.como_texto())
    editaveis = CAMPOS_OBRIGATORIOS[1:] + CAMPOS_OPCIONAIS  # tudo, menos o id
    print("Qual campo deseja alterar?")
    numero = 1
    for campo in editaveis:
        print(str(numero) + " - " + ROTULOS[campo])
        numero += 1
    escolha = input("Número do campo: ").strip()
    if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(editaveis):
        print("Opção inválida: digite um número da lista.")
        return
    campo = editaveis[int(escolha) - 1]
    valor = input("Novo valor para '" + ROTULOS[campo] + "': ")
    mostrar(catalogo.atualizar(id, campo, valor))


def opcao_excluir(catalogo):
    mostrar(catalogo.excluir(input("Identificador do registro a excluir: ")))


def opcao_pesquisar(catalogo):
    print("Pesquisar por: 1 - Título   2 - Categoria")
    escolha = input("Opção: ").strip()
    if escolha == "1":
        atributo = "titulo"
    elif escolha == "2":
        atributo = "categoria"
    else:
        print("Opção inválida: digite 1 ou 2.")
        return
    registros = mostrar(catalogo.pesquisar(atributo, input("Trecho a procurar: ")))
    if registros is not None:
        mostrar_lista(registros)


def opcao_ordenar(catalogo):
    print("Ordenar por: 1 - Título   2 - Identificador   3 - Prazo")
    escolha = input("Opção: ").strip()
    if escolha == "1":
        criterio = "titulo"
    elif escolha == "2":
        criterio = "id"
    elif escolha == "3":
        criterio = "prazo"
    else:
        print("Opção inválida: digite 1, 2 ou 3.")
        return
    resultado = catalogo.ordenar(criterio)
    mostrar(resultado)
    if resultado[0]:
        mostrar_lista(catalogo.listar()[2])


ACOES = {
    "1": opcao_cadastrar,
    "2": opcao_consultar,
    "3": opcao_listar,
    "4": opcao_atualizar,
    "5": opcao_excluir,
    "6": opcao_pesquisar,
    "7": opcao_ordenar,
}


def main():
    # Garante acentos corretos no terminal do Windows.
    for fluxo in (sys.stdout, sys.stdin):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    catalogo = Catalogo()
    mostrar(catalogo.carregar_json(CAMINHO_DADOS))
    try:
        while True:
            print(MENU)
            escolha = input("Escolha uma opção: ").strip()
            if escolha == "0":
                print("Até logo!")
                break
            acao = ACOES.get(escolha)
            if acao is None:
                print("Opção inexistente: digite um número de 0 a 7.")
            else:
                acao(catalogo)
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada encerrada. Até logo!")


if __name__ == "__main__":
    main()
