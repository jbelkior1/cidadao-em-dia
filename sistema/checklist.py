"""Checklist das entregas: o que cada matéria pede, onde está, como foi feito e o status.

Fica em sistema/dados/checklist.json, que vai para o git: é o andamento da equipe.
A tela pode mudar só status, onde e como.
"""
import json
from datetime import date
from pathlib import Path

from sistema import materias

ARQUIVO = Path(__file__).parent / "dados" / "checklist.json"
STATUS = ["Feito", "Falta conferir", "A fazer"]
VALOR = {"Feito": 1.0, "Falta conferir": 0.5, "A fazer": 0.0}


def ler() -> dict:
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"materias": {}, "geral": [], "alertas": [], "divergencias": []}


def _gravar(dados: dict) -> None:
    dados["atualizado_em"] = date.today().isoformat()
    ARQUIVO.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def contar(itens: list[dict]) -> dict:
    """Quantos itens em cada status e o percentual (Feito vale 1, Falta conferir vale meio)."""
    contagem = {s: 0 for s in STATUS}
    for item in itens:
        contagem[item.get("status", "A fazer")] = contagem.get(item.get("status", "A fazer"), 0) + 1
    total = len(itens)
    pontos = sum(VALOR.get(i.get("status", "A fazer"), 0) for i in itens)
    return {"total": total, "por_status": contagem, "percentual": round(100 * pontos / total) if total else 0,
            "do_grupo": sum(1 for i in itens if i.get("quem") == "grupo" and i.get("status") != "Feito")}


def da_materia(cod: str) -> dict | None:
    m = ler()["materias"].get(cod)
    if m is None:
        return None
    return m | {"resumo": contar(m.get("itens", []))}


def atualizar(cod: str, item_id: str, mudancas: dict) -> dict | None:
    """Muda status, onde ou como de um item. Devolve o item atualizado ou None se não existir."""
    dados = ler()
    for item in dados["materias"].get(cod, {}).get("itens", []):
        if item["id"] == item_id:
            if mudancas.get("status") in STATUS:
                item["status"] = mudancas["status"]
            for campo in ("onde", "como"):
                if isinstance(mudancas.get(campo), str):
                    item[campo] = mudancas[campo].strip()
            _gravar(dados)
            return item
    return None


def painel() -> dict:
    dados = ler()
    todos, linhas = [], []
    for m in materias.NO_SISTEMA + materias.A_PARTE:
        itens = dados["materias"].get(m["cod"], {}).get("itens", [])
        todos += itens
        linhas.append({"cod": m["cod"], "nome": m["nome"], "cor": m["cor"], "no_sistema": m in materias.NO_SISTEMA, **contar(itens)})
    return {
        "dias": (date.fromisoformat(materias.PRAZO_GS) - date.today()).days,
        "prazo": materias.PRAZO_GS, "geral": contar(todos), "materias": linhas,
        "regras": dados.get("geral", []), "alertas": dados.get("alertas", []), "divergencias": dados.get("divergencias", []),
        "atualizado_em": dados.get("atualizado_em", ""),
    }
