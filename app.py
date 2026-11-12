"""Cidadão em Dia · GS 2026.2.

Rodar:  uv run streamlit run app.py
"""
import streamlit as st

from nucleo import nav, ui
from nucleo.materias import NOME_DO_SISTEMA, ORDEM, REGISTRO
from paginas import materia

st.set_page_config(page_title=NOME_DO_SISTEMA, page_icon=":material/how_to_reg:")
ui.aplicar_estilo()
st.session_state.setdefault("modo_banca", True)   # modo banca ligado por padrão


def pagina_da_materia(cod: str):
    def mostrar():
        materia.mostrar(cod)
    mostrar.__name__ = f"materia_{cod.lower()}"
    return mostrar


comece = [st.Page("paginas/comece_aqui.py", title="Como o sistema funciona", icon=":material/info:", default=True)]
cidadao = [
    st.Page("paginas/atendimento.py", title="1. Conte o que precisa", icon=":material/support_agent:"),
    st.Page("paginas/resolver.py", title="2. Resolva aqui", icon=":material/task_alt:"),
]
laboratorio = [st.Page("paginas/simulacao.py", title="Simulação da sociedade", icon=":material/groups:")]
materias = [st.Page("paginas/painel.py", title="Painel da equipe", icon=":material/monitoring:")] + [
    st.Page(pagina_da_materia(c), title=f"{REGISTRO[c]['curto']} ({c})", icon=REGISTRO[c]["icone"], url_path=f"materia-{c.lower()}")
    for c in ORDEM]
nav.MATERIAS = dict(zip(ORDEM, materias[1:]))

pagina = st.navigation({"Comece aqui": comece, "Para o cidadão": cidadao, "Laboratório": laboratorio, "Matérias": materias},
                       expanded=True)

with st.sidebar:
    st.divider()
    st.toggle("Modo banca", key="modo_banca", help="Mostra, em cada resposta, qual matéria fez cada parte.")
    st.caption("Ligado, cada parte da resposta mostra o selo da matéria que a produziu.")

pagina.run()
