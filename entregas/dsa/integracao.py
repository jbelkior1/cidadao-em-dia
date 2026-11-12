"""EXTRA (não faz parte do enunciado de DSA): funções para o sistema web reutilizar o catálogo.

Ficam separadas da entrega para deixar claro que a entrega de DSA é main.py + catalogo.py +
lista_encadeada.py + algoritmos.py. Aqui, listas nativas só aparecem para exibição.
"""

import os
import sys
from datetime import date

_PASTA = os.path.dirname(os.path.abspath(__file__))
if _PASTA not in sys.path:
    sys.path.insert(0, _PASTA)

from algoritmos import contem_trecho  # noqa: E402
from catalogo import Catalogo  # noqa: E402


def carregar_catalogo(caminho=None):
    """Cria um Catalogo já preenchido com os dados iniciais (ou com o JSON indicado)."""
    catalogo = Catalogo()
    catalogo.carregar_json(caminho or os.path.join(_PASTA, "dados", "servicos.json"))
    return catalogo


def prazo_de(titulo, catalogo=None):
    """Prazo (texto) do primeiro serviço cujo título contém 'titulo'. '' se não houver."""
    catalogo = catalogo or carregar_catalogo()
    for servico in catalogo.lista.percorrer():
        if contem_trecho(servico.titulo, titulo):
            return servico.prazo
    return ""


def por_prazo(catalogo=None):
    """Lista comum (só para exibição) dos serviços, já ordenados pelo nosso merge sort."""
    catalogo = catalogo or carregar_catalogo()
    catalogo.ordenar("prazo")
    resultado = []
    for servico in catalogo.lista.percorrer():
        resultado.append(servico)
    return resultado


def dias_ate(data_iso):
    """Dias de hoje até a data AAAA-MM-DD (negativo se já passou). None se a data for inválida."""
    try:
        return (date.fromisoformat(data_iso) - date.today()).days
    except (ValueError, TypeError):
        return None
