import streamlit as st

from nucleo import diagrama, nav, ui
from nucleo.materias import A_PARTE, FRASE_DO_SISTEMA, NOME_DO_SISTEMA, ORDEM, REGISTRO

st.title(NOME_DO_SISTEMA)
st.markdown(f"<p style='font-size:1.25rem; max-width:660px; margin-top:-6px'>{FRASE_DO_SISTEMA}</p>", unsafe_allow_html=True)
st.page_link(nav.CIDADAO["Conte o que precisa"], label="Começar o atendimento", icon=":material/play_arrow:")

st.subheader("O problema")
st.markdown("Quem mais precisa de um serviço público é quem menos consegue acompanhar as regras. "
            "Os canais oficiais respondem quando você pergunta, mas ninguém avisa que você tem um direito, "
            "que ele vence num prazo ou que aquela mensagem é golpe.")
numeros = [("17 de 24,9 milhões", "de famílias aptas recebem a tarifa social de energia"),
           ("3,5 milhões", "de famílias podem perder o desconto em 2026"),
           ("3,7 milhões", "de famílias chamadas na revisão do Bolsa Família")]
for col, (valor, texto) in zip(st.columns(3), numeros):
    col.markdown(f"<p style='font-size:1.45rem; font-weight:700; margin:0; color:#17363A'>{valor}</p>"
                 f"<p class='fonte' style='margin-top:2px'>{texto}</p>", unsafe_allow_html=True)
st.markdown('<span class="nota-exemplo">Números de reportagens e apresentações oficiais: conferir antes de citar.</span>', unsafe_allow_html=True)

st.subheader("Como o cidadão usa")
st.markdown(
    "1. **Conte o que precisa.** A pessoa escreve do jeito dela. O sistema entende o assunto, mostra o que entendeu e por quê.\n"
    "2. **Resolva aqui.** O caso chega já com o que a pessoa contou e cai na parte certa: tirar uma dúvida sobre documentos, "
    "descobrir os direitos, entender a conta de luz ou conferir se uma mensagem é golpe.")
st.graphviz_chart(diagrama.fluxograma(), width="stretch")

st.subheader("As matérias por trás")
st.markdown("Cada parte do sistema é feita por uma matéria. Na página de cada uma estão o que ela faz, a parte dela no fluxograma, "
            "um teste e o checklist do que o enunciado pede.")
for c in ORDEM:
    m = REGISTRO[c]
    col1, col2 = st.columns([3, 2])
    col1.markdown(f"{ui.tag(c)} **{m['curto']}**<br><span class='fonte'>{m['ajuda']}</span>", unsafe_allow_html=True)
    col2.page_link(nav.MATERIAS[c], label=f"Entender {m['curto'].lower()}", icon=":material/arrow_outward:")
st.caption("Entregues à parte, fora do sistema: " + ", ".join(f"{REGISTRO[c]['nome']} ({c})" for c in A_PARTE)
           + ". O andamento de todas está no Painel da equipe.")

st.subheader("O Laboratório")
st.markdown("Antes de levar o produto às ruas, a **Simulação da sociedade** testa a ideia com pessoas simuladas: uma idosa da zona rural, "
            "uma mãe da periferia, um entregador, uma agente do CRAS e outras. Cada uma tem a sua internet, a sua familiaridade com o celular "
            "e a sua confiança no governo, e diz se usaria o produto e por quê. Dá para testar cada parte e cada canal (app, totem no CRAS, "
            "WhatsApp) e ver quem fica de fora. As personas e os números são fictícios até a MLAM trazer os dados reais.")
st.page_link(nav.CIDADAO["Simulação da sociedade"], label="Abrir a simulação", icon=":material/groups:")

st.subheader("Combinados")
st.markdown("Não é canal oficial, não pede dados pessoais, mostra a fonte e a data de cada orientação e diz quando não sabe. "
            "Com o **modo banca** ligado, cada parte das respostas mostra o selo da matéria que a produziu.")
ui.rodape()
