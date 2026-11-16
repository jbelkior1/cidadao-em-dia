"""Checklist das entregas: o que cada enunciado pede, agrupado pelos critérios da rubrica, e o status.

Fica em sistema/dados/checklist.json, que vai para o git. Cada matéria tem o formato de entrega
no portal, o prazo, a rubrica e as seções; cada item diz se é do sistema (código ou documento no
repositório) ou de fora dele (vídeo, testes com pessoas, envio no portal), onde está e como foi feito.

No computador da equipe a tela muda status, onde e como. No servidor público (MODO_PUBLICO=1)
o checklist é só leitura.
"""
import json
import re
from datetime import date
from pathlib import Path

from sistema import config, materias

ARQUIVO = Path(__file__).parent / "dados" / "checklist.json"
STATUS = ["Feito", "Conferir", "A fazer"]
VALOR = {"Feito": 1.0, "Conferir": 0.5, "A fazer": 0.0}


def ler() -> dict:
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"materias": {}, "geral": []}


def _gravar(dados: dict) -> None:
    dados["atualizado_em"] = date.today().isoformat()
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def itens_da(m: dict) -> list[dict]:
    """Todos os itens de uma matéria, na ordem das seções."""
    return [item for secao in m.get("secoes", []) for item in secao.get("itens", [])]


def _andamento(itens: list[dict]) -> dict:
    prontos = sum(1 for i in itens if i.get("status") == "Feito")
    return {"total": len(itens), "prontos": prontos, "faltam": len(itens) - prontos,
            "percentual": round(100 * prontos / len(itens)) if itens else 0}


def contar(itens: list[dict]) -> dict:
    """Quantos itens em cada status e o andamento separado entre sistema e equipe.

    Separar importa: uma matéria com o código inteiro pronto não pode aparecer pela metade só
    porque o vídeo e o teste com pessoas ainda não foram feitos.
    """
    por_status = {s: sum(1 for i in itens if i.get("status") == s) for s in STATUS}
    pontos = sum(VALOR.get(i.get("status", "A fazer"), 0) for i in itens)
    return {"total": len(itens), "por_status": por_status, "percentual": round(100 * pontos / len(itens)) if itens else 0,
            "por_quem": {"sistema": _andamento([i for i in itens if i.get("quem") == "sistema"]),
                         "equipe": _andamento([i for i in itens if i.get("quem") == "equipe"])}}


def _com_links(item: dict) -> dict:
    """Quando "onde" começa com um caminho do repositório, a tela ganha o link do GitHub.

    O caminho é o primeiro trecho, sem número de linha ("main.py:28-41") nem pontuação. Só vira link se
    existir no repositório: caminho velho ou errado não vira link quebrado.
    """
    achado = re.match(r"`?([\w./-]+)", item.get("onde") or "")
    caminho = achado.group(1).rstrip(".:;,") if achado else ""
    existe = "/" in caminho and (config.RAIZ / caminho).exists()
    return item | {"onde_url": materias.link(caminho) if existe else ""}


def da_materia(cod: str) -> dict | None:
    m = ler()["materias"].get(cod)
    if m is None:
        return None
    secoes = [s | {"itens": [_com_links(i) for i in s.get("itens", [])]} for s in m.get("secoes", [])]
    return m | {"secoes": secoes, "resumo": contar(itens_da(m))}


def atualizar(cod: str, item_id: str, mudancas: dict) -> dict | None:
    """Muda status, onde ou como de um item. Devolve o item atualizado ou None se não existir."""
    dados = ler()
    for item in itens_da(dados["materias"].get(cod, {})):
        if item["id"] == item_id:
            if mudancas.get("status") in STATUS:
                item["status"] = mudancas["status"]
            for campo in ("onde", "como"):
                if isinstance(mudancas.get(campo), str):
                    item[campo] = mudancas[campo].strip()
            _gravar(dados)
            return _com_links(item)
    return None
