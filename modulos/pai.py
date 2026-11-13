"""PAI · o agente (EXEMPLO DO ESQUELETO, SEM IA).

Aqui só há uma busca por palavra nas fichas fictícias de exemplo.
O agente de verdade (framework, LLM, fichas de Aurora e o juiz nas 26 mensagens)
é a entrega da PAI. Quando estiver pronto, `responder` passa a chamar o agente.
As fichas de Aurora são fictícias: nunca misturar com a base real do PCP.
"""
import json
from pathlib import Path

import streamlit as st

from modulos.pcp import contem

MATERIA = "PAI"
FICHAS = json.loads((Path(__file__).parent.parent / "data" / "fichas_exemplo.json").read_text(encoding="utf-8"))


def responder(pergunta: str):
    """Devolve (texto, ficha) ou (None, None) quando não encontra."""
    melhor, n = None, 0
    for f in FICHAS:
        k = sum(1 for w in f["palavras_chave"] if contem(pergunta, w))
        if k > n:
            melhor, n = f, k
    if not melhor:
        return None, None
    return melhor["texto"], melhor


def testar():
    st.markdown("Nesta versão ainda não há IA: o agente só procura nas fichas fictícias de exemplo.")
    q = st.text_input("Pergunta sobre documentos", placeholder="Exemplo: perdi meu RG, o que faço?", key="pai_q")
    if q:
        texto, ficha = responder(q)
        if ficha:
            st.success(texto)
            st.caption(f"Ficha {ficha['id']} · {ficha['data']} · fictícia")
        else:
            st.info("Não encontrei nas fichas. O agente responde que não sabe e indica o atendimento presencial.")
    st.markdown("**Juiz (LLM)** · nota nas 26 mensagens antes e depois da melhoria")
    st.dataframe([{"rodada": "antes", "acerto": "-", "cita a ficha": "-", "recusa dado pessoal": "-"},
                  {"rodada": "depois", "acerto": "-", "cita a ficha": "-", "recusa dado pessoal": "-"}],
                 hide_index=True, width="stretch")
