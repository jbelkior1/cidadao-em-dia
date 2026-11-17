"""Ponte entre o sistema e a entrega de DSA.

O catálogo de serviços e prazos mora na lista encadeada da entrega
(entregas/dsa). Aqui só se chama o que ela oferece; nenhuma regra é reescrita.
"""
import sys
from datetime import date

from sistema import config
from sistema import hora

PASTA = config.RAIZ / "entregas" / "dsa"
_catalogo = None
_erro = ""


def _carregar():
    """Carrega o catálogo uma vez. Se a entrega não estiver lá, o sistema segue sem prazo."""
    global _catalogo, _erro
    if _catalogo is None and not _erro:
        try:
            if str(PASTA) not in sys.path:
                sys.path.insert(0, str(PASTA))
            import integracao
            _catalogo = integracao.carregar_catalogo()
        except Exception as e:  # entrega ausente ou com erro não derruba o chat
            _erro = f"{type(e).__name__}: {e}"
    return _catalogo


def situacao() -> dict:
    catalogo = _carregar()
    return {"ok": catalogo is not None, "registros": catalogo.lista.tamanho() if catalogo else 0, "erro": _erro}


def _faltam(dias: int) -> str:
    if dias > 1:
        return f"faltam {dias} dias"
    if dias == 1:
        return "falta 1 dia"
    if dias == 0:
        return "vence hoje"
    return "prazo vencido"


def servico_de(titulo: str) -> dict | None:
    """Registro do catálogo cujo título combina com o texto: para quem é, canal e prazo (se houver data)."""
    catalogo = _carregar()
    if catalogo is None:
        return None
    from algoritmos import contem_trecho
    for servico in catalogo.lista.percorrer():
        if contem_trecho(servico.titulo, titulo) or contem_trecho(titulo, servico.titulo):
            achado = {"id": servico.id, "titulo": servico.titulo, "publico_alvo": servico.publico_alvo,
                      "canal": servico.canal, "prazo": None}
            if servico.prazo:
                try:
                    dia = date.fromisoformat(servico.prazo)
                    achado["prazo"] = {"data": servico.prazo, "texto": "até " + dia.strftime("%d/%m/%Y"),
                                       "faltam": _faltam((dia - hora.hoje()).days)}
                except ValueError:
                    pass
            return achado
    return None


def servico_por_id(servico_id: str) -> dict | None:
    """Percorre a lista encadeada do primeiro nó ao último até achar o id (busca linear)."""
    catalogo = _carregar()
    if catalogo is None:
        return None
    for servico in catalogo.lista.percorrer():
        if servico.id == servico_id:
            return {"id": servico.id, "titulo": servico.titulo, "publico_alvo": servico.publico_alvo, "canal": servico.canal, "prazo": None}
    return None


def proximos() -> list[dict]:
    """Serviços com prazo, do que vence primeiro para o último (ordenados pelo merge sort da entrega)."""
    catalogo = _carregar()
    if catalogo is None:
        return []
    catalogo.ordenar("prazo")
    saida = []
    for servico in catalogo.lista.percorrer():
        if servico.prazo:
            saida.append({"titulo": servico.titulo, "categoria": servico.categoria, "data": servico.prazo})
    return saida
