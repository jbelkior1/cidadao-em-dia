"""COA · medidor de energia da casa (SIMULAÇÃO NO ESQUELETO).

O valor abaixo é simulado. Na versão final, o Pico W no Wokwi publica a leitura
por MQTT (rede Wokwi-GUEST, broker público) e `ler_consumo` passa a ler o último
valor recebido. Coloque o link do projeto em WOKWI_URL para ele aparecer na página.
"""
import time

import streamlit as st
import streamlit.components.v1 as components

MATERIA = "COA"
WOKWI_URL = ""   # exemplo: "https://wokwi.com/projects/SEU_ID"
FAIXA_KWH = 80   # faixa usada no aviso (valor de exemplo: conferir a regra com a SERS)


def ler_consumo() -> float:
    """Leitura simulada que muda com o tempo, entre 40 e 95 kWh."""
    return round(40 + (time.time() / 7) % 55, 1)


def estado(kwh: float):
    """Devolve (cor do LED, frase)."""
    if kwh < FAIXA_KWH * 0.85:
        return "verde", "dentro da faixa com desconto"
    if kwh <= FAIXA_KWH:
        return "amarelo", "perto do fim da faixa com desconto"
    return "vermelho", "passou da faixa com desconto"


def testar():
    st.markdown(f"Leitura simulada até o Pico W publicar de verdade. Faixa de exemplo: {FAIXA_KWH} kWh por mês.")
    if st.button("Ler o medidor", key="coa_ler"):
        st.session_state["coa_leitura"] = ler_consumo()
    k = st.session_state.get("coa_leitura")
    if k is not None:
        cor, frase = estado(k)
        st.metric("Consumo no mês", f"{k} kWh", help="simulação")
        st.progress(min(k / FAIXA_KWH, 1.0), text=f"LED {cor}: {frase}")
    if WOKWI_URL:
        components.iframe(f"{WOKWI_URL}?embed=1", height=520)
    else:
        st.caption("Coloque o link do projeto em WOKWI_URL (modulos/coa.py) para o simulador aparecer aqui.")
