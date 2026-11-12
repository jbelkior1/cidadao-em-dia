"""Estilo, selos de matéria e o registro do "como chegamos".

Os selos só aparecem com o modo banca ligado na barra lateral.
"""
from html import escape

import streamlit as st

from nucleo.contrato import Etapa
from nucleo.materias import REGISTRO

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap');
html, body, p, li, label, input, textarea, h1, h2, h3, h4, .stMarkdown, .stButton button, [data-testid="stPageLink"] a {
  font-family: 'Atkinson Hyperlegible', system-ui, sans-serif !important;
}
html {font-size: 17px}
h1 {font-size: 2.3rem !important; letter-spacing: -0.01em; color: #17363A}
h2, h3 {color: #17363A}
.bloco-principal {max-width: 760px}
.tag {display:inline-block; padding:1px 8px; margin-left:6px; border-radius:9px; color:#fff;
      font-size:.72rem; font-weight:700; vertical-align:middle; line-height:1.5}
.tag.off {background:#9aa8a4 !important}
.marca {background: linear-gradient(transparent 52%, #F6D860 52%); padding: 0 3px; font-weight:700}
.comprovante {border:1px solid #cfdad6; border-top:2px dashed #9db3ac; border-radius:4px 4px 16px 16px;
              padding:22px 26px 18px; background:#fff; margin: 6px 0 14px}
.comprovante .status {font-size:1.55rem; font-weight:700; line-height:1.25; padding-left:14px; margin-bottom:6px}
.comprovante .sub {color:#4d5f5a; margin:0 0 14px 20px}
.comprovante h4 {margin:16px 0 4px; font-size:1.02rem; color:#17363A}
.comprovante ol {margin:4px 0 0 22px; padding:0}
.comprovante ol li {margin:6px 0; font-size:1.05rem}
.comprovante .valor {font-size:1.6rem; font-weight:700; color:#17363A}
.fonte {font-size:.82rem; color:#5b6b66}
.nota-exemplo {font-size:.8rem; color:#7a6a2a; background:#fbf3d0; padding:2px 8px; border-radius:6px}
.etapas {list-style:none; margin:0; padding:0}
.etapas li {padding:10px 0; border-bottom:1px solid #e3ebe8}
.etapas li:last-child {border-bottom:none}
.trilha {display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin: 8px 0 4px}
.trilha .no {padding:6px 12px; border-radius:10px; background:#eef3f1; color:#17363A; font-weight:700; font-size:.9rem; border:2px solid transparent}
.trilha .no.ativo {color:#fff}
.trilha .seta {color:#9aa8a4}
.cab-materia {border-left:6px solid; padding:2px 0 2px 16px; margin-bottom:10px}
.cab-materia .curto {color:#4d5f5a; font-size:1.05rem; margin:0}
.aviso {font-size:.78rem; color:#5b6b66}
[data-testid="stPageLink"] a {border:1px solid #cfdad6; border-radius:12px; padding:14px 16px !important; background:#fff;
                              display:flex !important; width:100% !important; box-sizing:border-box}
[data-testid="stPageLink"] a:hover {border-color:#1F6F6B; background:#f5f9f8}
[data-testid="stPageLink"] p {font-size:1.12rem !important}
.stButton button {min-height:2.9rem; font-size:1.05rem}
</style>
"""

AVISO = ("Projeto educacional da Global Solution FIAP. Não é canal oficial do governo. "
         "Textos, prazos e valores desta versão são exemplos e precisam ser conferidos nas fontes oficiais.")


def aplicar_estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def banca() -> bool:
    return st.session_state.get("modo_banca", False)


def tag(cod: str, ativo: bool = True) -> str:
    cor = REGISTRO[cod]["cor"]
    classe = "tag" if ativo else "tag off"
    return f'<span class="{classe}" style="background:{cor}" title="{escape(REGISTRO[cod]["nome"])}">{cod}</span>'


def tags(*cods: str) -> str:
    """Selos para colocar ao lado de um texto; vazio se o modo banca estiver desligado."""
    return "".join(tag(c) for c in cods) if banca() else ""


def registrar(acao: str, etapas: list[Etapa]):
    st.session_state["rastro"] = {"acao": acao, "etapas": etapas}


def ultimo_rastro():
    return st.session_state.get("rastro")


def lista_etapas(etapas: list[Etapa]) -> str:
    itens = []
    for e in etapas:
        estado = "" if e.pronto else " (em construção)"
        detalhe = f'<br><span class="fonte">{escape(e.explicacao)}</span>' if e.explicacao else ""
        itens.append(f"<li>{tag(e.materia, e.pronto)} <b>{escape(e.titulo)}</b>{estado}{detalhe}</li>")
    return f'<ul class="etapas">{"".join(itens)}</ul>'


def como_chegamos(etapas: list[Etapa]):
    """Mostra o caminho entre as matérias, só no modo banca."""
    if banca() and etapas:
        with st.expander("Como o sistema chegou nesta resposta", expanded=False):
            st.markdown(lista_etapas(etapas), unsafe_allow_html=True)


def rodape():
    st.markdown(f'<p class="aviso">{AVISO}</p>', unsafe_allow_html=True)


def guia(para_que: str, passos: list[str], materias: list[str] = (), para_banca: str | None = None):
    """Quadro 'Como usar esta tela': para que serve, passos e quem trabalha aqui."""
    with st.expander("Como usar esta tela", expanded=False, icon=":material/school:"):
        st.markdown(f"**Para que serve.** {para_que}")
        st.markdown("**Como usar**\n" + "\n".join(f"{i}. {p}" for i, p in enumerate(passos, 1)))
        if materias and banca():
            st.markdown("**Matérias que trabalham aqui** " + "".join(tag(c) for c in materias), unsafe_allow_html=True)
        if para_banca and banca():
            st.markdown(f"**Para mostrar à banca.** {para_banca}")


def veio_do_atendimento(pagina: str):
    """Mostra o que a pessoa contou no Atendimento, quando ela foi encaminhada para esta tela."""
    h = st.session_state.get("handoff")
    if h and h.get("pagina") == pagina and h.get("texto"):
        st.info(f"Você contou: “{h['texto']}”. Por isso o Atendimento trouxe você para cá.", icon=":material/support_agent:")


SERVICOS = ["Tirar uma dúvida", "Meus direitos", "Minha conta de luz", "Isso é golpe?"]


def trocar_servico(nome: str, texto: str = ""):
    """Muda o assunto da aba Resolva aqui (usado como on_click; o Streamlit recarrega sozinho)."""
    st.session_state["handoff"] = {"pagina": nome, "texto": texto}
    if nome == "Meus direitos":
        st.session_state["dir_passo"], st.session_state["dir_resp"] = 0, {}
        st.session_state.pop("dir_resultado", None)
