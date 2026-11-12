"""SERS · calculadora de energia (VALORES DE EXEMPLO).

A tarifa e a faixa do desconto abaixo são exemplos para o esqueleto funcionar.
A entrega da SERS precisa usar dados com origem, unidade, período e premissas,
e comparar pelo menos duas alternativas, uma renovável.
"""
import streamlit as st

MATERIA = "SERS"
TARIFA_EXEMPLO = 0.80   # R$/kWh, valor de exemplo: trocar pela tarifa real com fonte
FAIXA_EXEMPLO = 80      # kWh com desconto, exemplo: conferir a regra na Aneel
APARELHOS = {            # potência em W e uso padrão por dia (premissas de exemplo)
    "Chuveiro elétrico": (5500, 0.67),
    "Geladeira": (150 * 0.35, 24),      # 0,35 = tempo em que o motor fica ligado
    "Televisão": (100, 4),
    "Lâmpadas (5)": (5 * 9, 5),
    "Ferro de passar": (1000, 0.3),
}


def brl(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def kwh_mes(potencia_w: float, horas_dia: float, dias: int = 30) -> float:
    return potencia_w * horas_dia * dias / 1000


def conta_mes(kwh: float) -> float:
    return round(kwh * TARIFA_EXEMPLO, 2)


def economia_ano(kwh: float) -> float:
    """Quanto a família deixa de pagar por ano com o desconto da faixa (exemplo)."""
    return round(min(kwh, FAIXA_EXEMPLO) * TARIFA_EXEMPLO * 12, 2)


def calculadora(prefixo: str) -> float:
    """Sliders de uso por aparelho; devolve o consumo do mês em kWh."""
    total = 0.0
    for nome, (w, h) in APARELHOS.items():
        horas = st.slider(f"{nome} · horas por dia", 0.0, 24.0, float(h), 0.25 if h < 2 else 1.0, key=f"{prefixo}_{nome}")
        total += kwh_mes(w, horas)
    return round(total, 1)


def detalhe(prefixo: str) -> list[dict]:
    """Conta por aparelho com os valores escolhidos nos controles (para explicar o cálculo)."""
    linhas = []
    for nome, (w, h) in APARELHOS.items():
        horas = float(st.session_state.get(f"{prefixo}_{nome}", h))
        linhas.append({"aparelho": nome, "potência (W)": round(w), "horas por dia": horas,
                       "kWh por mês": round(kwh_mes(w, horas), 1)})
    return linhas


def testar():
    st.markdown(f"Tarifa de exemplo {brl(TARIFA_EXEMPLO)} por kWh e faixa de exemplo de {FAIXA_EXEMPLO} kWh.")
    k = calculadora("sers")
    c1, c2, c3 = st.columns(3)
    c1.metric("Consumo", f"{k} kWh/mês")
    c2.metric("Conta estimada", brl(conta_mes(k)))
    c3.metric("Economia com desconto", f"{brl(economia_ano(k))}/ano")
    st.caption("Comparação de alternativas (rede elétrica e solar, custo, viabilidade e impacto): espaço para a análise da equipe.")
