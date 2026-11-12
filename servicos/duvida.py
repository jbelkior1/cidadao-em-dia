import streamlit as st

from nucleo import orquestrador, ui



def mostrar():
    st.title("Tirar uma dúvida")
    st.markdown("Pergunte com suas palavras. Não escreva CPF, telefone ou e-mail.")
    ui.veio_do_atendimento("Tirar uma dúvida")
    ui.guia("Responde dúvidas sobre documentos e serviços, sempre dizendo de onde veio a informação.",
            ["Escreva a pergunta ou toque numa pergunta pronta.", "Leia a resposta, onde ir e a fonte.",
             "Se o sistema não souber, ele diz e indica onde procurar."],
            ["PCP", "PAI"], "Faça uma pergunta da base (perdi meu RG), uma que só o agente responde e uma com telefone, para mostrar a recusa.")

    if "conversa" not in st.session_state:
        st.session_state.conversa = []

    SUGESTOES = ["Perdi meu RG, o que faço?", "Como atualizo o Cadastro Único?", "Tenho dinheiro esquecido em banco?"]
    cols = st.columns(len(SUGESTOES))
    clicada = None
    for c, s in zip(cols, SUGESTOES):
        if c.button(s, width="stretch"):
            clicada = s


    def html_resposta(r) -> str:
        if r.tipo == "recusa":
            return f"Não envie CPF, telefone ou e-mail. Consigo ajudar sem eles. A pergunta não foi guardada.{ui.tags('PCP')}"
        if r.tipo == "nao_sei":
            return (f"Não sei responder isso com segurança. Procure o CRAS ou o site oficial do serviço."
                    f"{ui.tags('PCP', 'PAI')}")
        selo = ui.tags("PCP") if r.tipo == "orientacao" else ui.tags("PAI")
        onde = f"<br><b>Onde:</b> {r.onde}" if r.onde else ""
        origem = "Fonte" if r.tipo == "orientacao" else "Resposta do agente, pela"
        motivo = f'<br><span class="fonte">Por que esta resposta: {r.motivo}.</span>' if r.motivo else ""
        return (f"<b>{r.titulo}</b>{selo}<br>{r.texto}{onde}"
                f'<br><span class="fonte">{origem}: {r.fonte} (conferido: {r.conferido})</span>{motivo}')


    for msg in st.session_state.conversa:
        with st.chat_message(msg["papel"]):
            st.markdown(msg["html"], unsafe_allow_html=True)

    pergunta = st.chat_input("Escreva sua pergunta") or clicada or st.session_state.pop("duvida_pendente", None)
    if pergunta:
        r = orquestrador.tirar_duvida(pergunta)
        ui.registrar(f"Pergunta: {pergunta if r.tipo != 'recusa' else '(recusada por ter dado pessoal)'}", r.etapas)
        texto_usuario = pergunta if r.tipo != "recusa" else "(mensagem com dado pessoal, não guardada)"
        st.session_state.conversa += [{"papel": "user", "html": texto_usuario}, {"papel": "assistant", "html": html_resposta(r)}]
        st.rerun()

    if st.session_state.conversa:
        rastro = ui.ultimo_rastro()
        if rastro:
            ui.como_chegamos(rastro["etapas"])
        if st.button("Limpar conversa"):
            st.session_state.conversa = []
            st.rerun()

    ui.rodape()
