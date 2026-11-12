"""MLAM · os dados do problema (DADOS FICTÍCIOS NO ESQUELETO).

Os números abaixo são inventados só para o gráfico aparecer. A MLAM exige base
REAL: troque `DADOS` pela leitura da base escolhida (Aneel, MDS, IBGE) e use os
mesmos gráficos do relatório.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

MATERIA = "MLAM"
DADOS = {"Estado A": 38, "Estado B": 29, "Estado C": 21, "Estado D": 12}   # FICTÍCIO


def grafico():
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    nomes, valores = list(DADOS)[::-1], list(DADOS.values())[::-1]
    ax.barh(nomes, valores, color="#d04f87", height=0.5)
    for i, v in enumerate(valores):
        ax.text(v + 0.6, i, f"{v}%", va="center", fontsize=9, color="#17363A")
    ax.set_xlabel("famílias aptas que não recebem (%) · dados fictícios")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


def testar():
    st.markdown("Gráfico com dados fictícios até a base real entrar.")
    st.pyplot(grafico())
    st.caption("Resultados das regressões (simples, múltipla e logística com matriz de confusão): espaço para a análise da equipe.")
