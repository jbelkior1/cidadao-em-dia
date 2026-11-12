import streamlit as st

from modulos import dsa, pcp
from nucleo import nav, ui
from nucleo.contrato import Etapa

s = st.session_state
ASSUNTOS = [   # (intenção, rótulo do botão, exemplo em linguagem simples)
    ("duvida", "Documentos e serviços", "Perdi meu RG. Como tiro o CPF?"),
    ("direitos", "Direitos e benefícios", "Tenho direito a desconto? Meu cadastro está em dia?"),
    ("conta_luz", "Conta de luz", "Minha conta veio alta. Quanto eu gasto?"),
    ("golpe", "Mensagem suspeita", "Recebi um link ou uma cobrança estranha."),
]


def encaminhar(intencao: str, texto: str):
    """Passa o caso para a tela certa, levando o que a pessoa contou."""
    info = pcp.INTENCOES[intencao]
    s.handoff = {"pagina": info["pagina"], "texto": texto}
    if intencao == "duvida" and texto:
        s.duvida_pendente = texto                      # a pergunta chega feita
    elif intencao == "golpe" and texto:
        s.golpe_texto, s.golpe_auto = texto, True      # a mensagem chega colada e conferida
    elif intencao == "direitos":
        s.dir_passo, s.dir_resp = 0, {}                # começa as perguntas do zero
        s.pop("dir_resultado", None)
    st.switch_page(nav.CIDADAO["Resolva aqui"])


st.title("Como posso ajudar?")
st.markdown("Conte com as suas palavras o que você precisa. Eu entendo e levo você para o lugar certo. "
            "Não escreva CPF, telefone ou e-mail.")
ui.guia("É a porta de entrada: em vez de procurar a tela certa, você conta o que precisa e o sistema encaminha.",
        ["Escreva o que precisa, do seu jeito, ou toque num dos assuntos.", "Veja o que o sistema entendeu e por quê.",
         "Confirme para seguir ou toque em 'Não é isso' para escolher outro caminho."],
        ["PCP", "DSA"], "Escreva uma frase como 'quero desconto na conta de luz' e mostre como o sistema explica o que entendeu antes de encaminhar.")

with st.form("atendimento", clear_on_submit=False, border=False):
    texto = st.text_area("O que você precisa?", placeholder="Exemplo: minha conta de luz veio alta e não sei se tenho direito a desconto",
                         height=90, key="at_texto")
    enviar = st.form_submit_button("Continuar", type="primary", width="stretch")

if enviar and texto.strip():
    s.pop("at_corrigir", None)
    if pcp.tem_dado_pessoal(texto):
        s.at_resultado = {"tipo": "dado_pessoal"}
    else:
        intencao, confianca, palavras = pcp.entender_necessidade(texto)
        s.at_resultado = {"tipo": "entendi" if intencao else "nao_entendi", "intencao": intencao, "confianca": confianca,
                          "palavras": palavras, "texto": texto}
        ui.registrar(f"Atendimento: {texto}", [Etapa("PCP", "Entendeu a necessidade" if intencao else "Não entendeu e perguntou", "",
                                                     f"palavras: {', '.join(palavras)}; confiança {confianca}" if intencao else "nenhuma palavra conhecida")])

r = s.get("at_resultado")
if r and r["tipo"] == "dado_pessoal":
    st.warning("Seu texto parece ter CPF, telefone ou e-mail. Apague esses dados e escreva de novo: consigo ajudar sem eles. Nada foi guardado.")
elif r and r["tipo"] == "entendi" and not s.get("at_corrigir"):
    info = pcp.INTENCOES[r["intencao"]]
    palavras = ", ".join(f"“{p}”" for p in r["palavras"])
    st.markdown(f'<div class="comprovante"><div class="status" style="border-left:6px solid #1F6F6B; color:#1F6F6B">'
                f'Entendi: você quer {info["resumo"]}.{ui.tags("PCP")}</div>'
                f'<p class="sub">Por quê: encontrei {palavras} no que você escreveu (confiança {r["confianca"]}).</p>'
                f'<h4>O que vai acontecer</h4><p>{info["proximo"]}</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button(f"Ir para {info['pagina']}", type="primary", width="stretch"):
        encaminhar(r["intencao"], r["texto"])
    if c2.button("Não é isso", width="stretch"):
        s.at_corrigir = True
        st.rerun()
elif r and r["tipo"] == "nao_entendi":
    st.info("Não consegui entender o assunto. Qual destes se parece mais com o que você precisa?", icon=":material/help:")

mostrar_assuntos = (not r) or r["tipo"] == "nao_entendi" or s.get("at_corrigir")
if mostrar_assuntos:
    st.subheader("Ou escolha um assunto")
    cols = st.columns(2)
    for i, (intencao, rotulo, exemplo) in enumerate(ASSUNTOS):
        with cols[i % 2].container(border=True):
            st.markdown(f"**{rotulo}**")
            st.caption(exemplo)
            if st.button(f"Escolher {rotulo.lower()}", key=f"assunto_{intencao}", width="stretch"):
                s.pop("at_corrigir", None)
                encaminhar(intencao, (r or {}).get("texto", "") if r and r.get("tipo") != "dado_pessoal" else "")

st.subheader("Prazos que vencem primeiro")
linhas = []
for item in dsa.por_prazo():
    dias = dsa.dias_ate(item["prazo"])
    quando = (f'<span class="marca">até {dsa.data_br(item["prazo"])}</span> faltam {dias} dias' if dias is not None
              else f'<span class="fonte">{item["prazo"]}</span>')
    linhas.append(f"<li><b>{item['direito']}</b>{ui.tags('DSA')}<br>{item['acao']}<br>{quando}</li>")
st.markdown(f'<ul class="etapas">{"".join(linhas)}</ul>', unsafe_allow_html=True)
st.markdown('<span class="nota-exemplo">Prazos de exemplo: conferir nas fontes oficiais.</span>', unsafe_allow_html=True)
ui.rodape()
