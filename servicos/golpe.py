import streamlit as st

from modulos import pcp
from nucleo import orquestrador, ui



def mostrar():
    st.title("Isso é golpe?")
    st.markdown("Recebeu uma mensagem ou um link sobre benefício, documento ou conta? Cole aqui antes de clicar.")
    ui.veio_do_atendimento("Isso é golpe?")
    ui.guia("Confere uma mensagem antes de você clicar ou pagar, explicando cada sinal de golpe.",
            ["Cole a mensagem ou o link que você recebeu.", "Toque em Conferir a mensagem.", "Veja o que passou e o que acendeu alerta, e o que fazer."],
            ["PCP"], "Use o exemplo de golpe e depois o oficial, e mostre a lista do que foi conferido em cada um.")

    EXEMPLOS = {
        "Exemplo de golpe": "URGENTE: sua CNH será suspensa. Regularize agora pagando a taxa por Pix em detran-regulariza.com",
        "Exemplo oficial": "Consulte se você tem valores a receber em https://valoresareceber.bcb.gov.br",
    }
    c1, c2 = st.columns(2)
    for col, (rotulo, texto) in zip((c1, c2), EXEMPLOS.items()):
        if col.button(rotulo, width="stretch"):
            st.session_state.golpe_texto = texto

    texto = st.text_area("Mensagem ou link recebido", key="golpe_texto", height=110)
    auto = st.session_state.pop("golpe_auto", False)
    if (st.button("Conferir a mensagem", type="primary") or auto) and texto.strip():
        st.session_state.golpe_res = orquestrador.checar_golpe(texto)
        ui.registrar("Conferência em Isso é golpe?", st.session_state.golpe_res.etapas)

    res = st.session_state.get("golpe_res")
    if res:
        if res.nivel == "atencao":
            motivos = "".join(f"<li>{m}</li>" for m in res.motivos)
            st.markdown(f'<div class="comprovante"><div class="status" style="border-left:6px solid #B42318; color:#B42318">'
                        f'Cuidado: esta mensagem tem sinais de golpe{ui.tags("PCP")}</div>'
                        f'<h4>O que encontramos</h4><ol>{motivos}</ol>'
                        f'<h4>O que fazer</h4><ol><li>Não clique no link e não pague nada.</li>'
                        f'<li>Digite você mesmo o endereço do site oficial, que termina em .gov.br.</li>'
                        f'<li>Na dúvida, procure o atendimento presencial.</li></ol></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="comprovante"><div class="status" style="border-left:6px solid #2E7D4F; color:#2E7D4F">'
                        f'Não encontramos sinais claros de golpe{ui.tags("PCP")}</div>'
                        f'<p class="sub">Mesmo assim, nunca informe senha ou código recebido por mensagem.</p></div>', unsafe_allow_html=True)
        st.markdown("**O que conferimos**")
        for pergunta, passou, detalhe in pcp.checagens(st.session_state.get("golpe_texto", "")):
            st.markdown(f"{':green[:material/check_circle:]' if passou else ':red[:material/error:]'} {pergunta} <span class='fonte'>({detalhe})</span>",
                        unsafe_allow_html=True)
        ui.como_chegamos(res.etapas)

    ui.rodape()
