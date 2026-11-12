import streamlit as st

from nucleo import nav, ui
from servicos import conta_luz, direitos, duvida, golpe

MODULOS = {"Tirar uma dúvida": duvida, "Meus direitos": direitos, "Minha conta de luz": conta_luz, "Isso é golpe?": golpe}
ICONES = {"Tirar uma dúvida": ":material/chat:", "Meus direitos": ":material/fact_check:",
          "Minha conta de luz": ":material/bolt:", "Isso é golpe?": ":material/gpp_maybe:"}

h = st.session_state.get("handoff")

if not h or h.get("pagina") not in MODULOS:
    st.title("Resolva aqui")
    st.markdown("Aqui o seu caso é resolvido. Comece contando o que você precisa, para o sistema trazer você para a parte certa.")
    st.page_link(nav.CIDADAO["Conte o que precisa"], label="Contar o que eu preciso", icon=":material/support_agent:")
    st.markdown("**Ou vá direto para um assunto**")
    cols = st.columns(2)
    for i, nome in enumerate(ui.SERVICOS):
        cols[i % 2].button(nome, icon=ICONES[nome], on_click=ui.trocar_servico, args=(nome,), width="stretch", key=f"ir_{i}")
    ui.rodape()
    st.stop()

atual = h["pagina"]
c1, c2 = st.columns([3, 1])
c1.caption(f"Assunto: {atual}")
with c2.popover("Mudar de assunto", icon=":material/swap_horiz:", width="stretch"):
    for i, nome in enumerate(ui.SERVICOS):
        if nome != atual:
            st.button(nome, icon=ICONES[nome], on_click=ui.trocar_servico, args=(nome,), width="stretch", key=f"troca_{i}")
    st.page_link(nav.CIDADAO["Conte o que precisa"], label="Contar de novo", icon=":material/support_agent:")

MODULOS[atual].mostrar()
