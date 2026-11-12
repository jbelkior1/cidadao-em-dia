"""DSA · catálogo de direitos e prazos (EXEMPLO DO ESQUELETO).

Aqui o catálogo usa a lista pronta do Python só para o esqueleto funcionar.
Na entrega da DSA a lista nativa NÃO vale: troque pelo catálogo com a lista
encadeada da equipe e mantenha as funções abaixo para o sistema seguir funcionando.
"""
import json
from datetime import date
from pathlib import Path

import streamlit as st

MATERIA = "DSA"
CATALOGO = json.loads((Path(__file__).parent.parent / "data" / "prazos_exemplo.json").read_text(encoding="utf-8"))


def dias_ate(prazo: str):
    try:
        return (date.fromisoformat(prazo) - date.today()).days
    except ValueError:
        return None


def prazo_de(direito: str):
    for item in CATALOGO:
        if direito.lower() in item["direito"].lower():
            return item
    return None


def por_prazo():
    """Direitos com data primeiro (do mais próximo ao mais distante), depois os sem data."""
    return sorted(CATALOGO, key=lambda i: (dias_ate(i["prazo"]) is None, dias_ate(i["prazo"]) or 0))


def data_br(prazo: str) -> str:
    try:
        return date.fromisoformat(prazo).strftime("%d/%m/%Y")
    except ValueError:
        return prazo


def testar():
    st.markdown("Cadastre um direito e veja o catálogo ordenado pelo prazo mais próximo.")
    with st.form("dsa_novo", clear_on_submit=True):
        c1, c2, c3 = st.columns([2, 3, 2])
        d = c1.text_input("Direito")
        a = c2.text_input("O que fazer")
        p = c3.text_input("Prazo (AAAA-MM-DD)")
        if st.form_submit_button("Cadastrar") and d.strip():
            CATALOGO.append({"direito": d, "acao": a, "prazo": p or "sem prazo", "situacao_do_dado": "cadastrado no teste"})
    st.dataframe([{"direito": i["direito"], "o que fazer": i["acao"], "prazo": data_br(i["prazo"])} for i in por_prazo()],
                 hide_index=True, width="stretch")
    st.caption("Big-O de inserir, buscar, excluir e ordenar: preencher com a análise da equipe.")
