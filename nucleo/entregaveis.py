"""Lista de entregáveis: o que cada matéria pede, onde está no projeto, como foi feito e o status.

Fonte única: data/entregaveis.json (o grupo edita pelo app ou direto no arquivo).
"""
import json
from pathlib import Path

import streamlit as st

ARQ = Path(__file__).parent.parent / "data" / "entregaveis.json"
STATUS = ["Feito", "No esqueleto", "A fazer"]
LEGENDA = {"Feito": "pronto e conferido", "No esqueleto": "existe uma versão de exemplo que precisa ser trocada",
           "A fazer": "ainda não começou"}


def carregar() -> dict:
    if ARQ.exists():
        return json.loads(ARQ.read_text(encoding="utf-8"))
    return {"materias": {}, "geral": []}


def salvar(dados: dict):
    ARQ.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def contagem(itens: list[dict]) -> dict:
    c = {s: 0 for s in STATUS}
    for i in itens:
        c[i.get("status", "A fazer")] = c.get(i.get("status", "A fazer"), 0) + 1
    return c


def percentual(cod: str) -> int:
    itens = carregar()["materias"].get(cod, {}).get("itens", [])
    if not itens:
        return 0
    c = contagem(itens)
    return round(100 * (c["Feito"] + 0.5 * c["No esqueleto"]) / len(itens))


def editor(cod: str, detalhes: bool = False):
    """Tabela editável dos itens de uma matéria; salva no JSON."""
    dados = carregar()
    m = dados["materias"].get(cod)
    if not m:
        st.info("A lista desta matéria ainda não foi gerada.")
        return
    itens = m["itens"]
    c = contagem(itens)
    st.markdown(f"**Formato da entrega.** {m.get('formato_entrega', '')}")
    st.caption(" | ".join(f"{s}: {c[s]}" for s in STATUS))
    colunas = ["status", "id", "requisito", "onde", "como"] + (["detalhe", "peso", "fonte"] if detalhes else [])
    linhas = [{k: i.get(k, "") for k in colunas} for i in itens]
    editado = st.data_editor(
        linhas, key=f"ed_{cod}", hide_index=True, width="stretch",
        disabled=[k for k in colunas if k not in ("status", "onde", "como")],
        column_config={
            "status": st.column_config.SelectboxColumn("Status", options=STATUS, width="medium", required=True),
            "id": st.column_config.TextColumn("Item", width="small"),
            "requisito": st.column_config.TextColumn("O que é pedido", width="large"),
            "onde": st.column_config.TextColumn("Onde está", width="medium"),
            "como": st.column_config.TextColumn("Como foi feito", width="large"),
            "detalhe": st.column_config.TextColumn("Detalhe do enunciado", width="large"),
            "peso": st.column_config.TextColumn("Peso", width="small"),
            "fonte": st.column_config.TextColumn("Fonte", width="medium"),
        })
    if st.button("Salvar alterações", key=f"salvar_{cod}"):
        por_id = {e["id"]: e for e in editado}
        for i in itens:
            e = por_id.get(i["id"])
            if e:
                i["status"], i["onde"], i["como"] = e["status"], e["onde"], e["como"]
        salvar(dados)
        st.success("Salvo em data/entregaveis.json.")
