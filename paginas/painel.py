from datetime import date

import streamlit as st

from nucleo import entregaveis as E
from nucleo import nav, ui
from nucleo.materias import A_PARTE, ORDEM, PRAZO_GS, REGISTRO, TODAS

st.title("Painel da equipe")
st.markdown("O andamento de cada matéria. O checklist completo de cada uma fica na página dela, na parte Checklist da entrega.")

dados = E.carregar()
todos = [i for c in TODAS for i in dados["materias"].get(c, {}).get("itens", [])]
cont = E.contagem(todos)
dias = (date.fromisoformat(PRAZO_GS) - date.today()).days
c1, c2, c3, c4 = st.columns(4)
c1.metric("Dias até a entrega", dias, help="19/11 às 23h55. Enviem até as 18h.")
c2.metric("Itens feitos", f"{cont['Feito']} de {len(todos)}")
c3.metric("No esqueleto", cont["No esqueleto"], help=E.LEGENDA["No esqueleto"])
c4.metric("A fazer", cont["A fazer"])

st.subheader("Matérias dentro do sistema")
for c in ORDEM:
    k = E.contagem(dados["materias"].get(c, {}).get("itens", []))
    col1, col2 = st.columns([3, 2])
    col1.markdown(f"{ui.tag(c)} **{REGISTRO[c]['curto']}**<br><span class='fonte'>{k['Feito']} feitos, "
                  f"{k['No esqueleto']} no esqueleto, {k['A fazer']} a fazer</span>", unsafe_allow_html=True)
    col1.page_link(nav.MATERIAS[c], label="Abrir a matéria e o checklist", icon=":material/arrow_outward:")
    col2.progress(E.percentual(c) / 100, text=f"{E.percentual(c)}%")

st.subheader("Entregues à parte")
st.caption("Não entram no sistema. O checklist delas fica aqui.")
for c in A_PARTE:
    m = dados["materias"].get(c)
    if not m:
        continue
    k = E.contagem(m["itens"])
    with st.expander(f"{REGISTRO[c]['nome']} ({c}): {k['Feito']} de {len(m['itens'])} itens feitos"):
        E.editor(c, detalhes=st.toggle("Mostrar detalhe do enunciado, peso e fonte", key=f"det_{c}"))

if dados.get("geral"):
    with st.expander(f"Regras gerais da GS ({len(dados['geral'])})"):
        for g in dados["geral"]:
            st.markdown(f"- **{g['requisito']}** {g.get('detalhe', '')}  \n  <span class='fonte'>{g.get('fonte', '')}</span>",
                        unsafe_allow_html=True)
if dados.get("alertas") or dados.get("divergencias"):
    with st.expander("Alertas e divergências entre os documentos"):
        for a in dados.get("alertas", []) + dados.get("divergencias", []):
            st.markdown(f"- {a}")
st.caption("Progresso: item feito conta 1, item no esqueleto conta meio. Itens com fonte 'resumo' vieram do resumo do portal.")
