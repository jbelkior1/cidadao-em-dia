"""Molde das páginas de matéria: Entenda, Teste e Checklist da entrega."""
import streamlit as st

from modulos import coa, dsa, mlam, pai, pcp, sers
from nucleo import diagrama, entregaveis, nav, ui
from nucleo.materias import REGISTRO

MODULOS = {"PCP": pcp, "PAI": pai, "DSA": dsa, "COA": coa, "SERS": sers, "MLAM": mlam}


def mostrar(cod: str):
    m = REGISTRO[cod]
    st.markdown(f'<div class="cab-materia" style="border-color:{m["cor"]}"><h1 style="margin:0">{m["curto"]}</h1>'
                f'<p class="curto">{m["nome"]} ({cod})</p></div>', unsafe_allow_html=True)

    # rótulos fixos: se o texto do rótulo muda, o Streamlit recria o seletor e volta para a primeira parte
    parte = st.segmented_control("Parte da página", ["Entenda", "Teste", "Checklist da entrega"], default="Entenda",
                                 key=f"parte_{cod}", label_visibility="collapsed") or "Entenda"

    if parte == "Entenda":
        st.markdown(f"### O que faz no sistema\n{m['papel']}")
        st.markdown(f"### Como ajuda o cidadão\n{m['ajuda']}")
        st.markdown("### Quando entra em ação\n" + "\n".join(f"- {q}" for q in m["quando"]))
        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.markdown("**Recebe**")
            st.markdown(m["entrada"])
        with c2.container(border=True):
            st.markdown("**Devolve**")
            st.markdown(m["saida"])
        st.markdown("### A parte dela no fluxograma")
        st.caption(f"Em destaque, {m['curto'].lower()} e as ligações com as telas e as outras matérias. O resto fica em cinza.")
        st.graphviz_chart(diagrama.fluxograma(cod), width="stretch")
        st.markdown(f"### Nesta versão\n{m['nesta_versao']}")
        if m["aparece_em"]:
            st.markdown("**Ver funcionando**")
            cols = st.columns(len(m["aparece_em"]))
            for i, (col, p) in enumerate(zip(cols, m["aparece_em"])):
                if p in ui.SERVICOS:
                    if col.button(p, icon=":material/arrow_outward:", key=f"ver_{cod}_{i}", width="stretch"):
                        ui.trocar_servico(p)
                        st.switch_page(nav.CIDADAO["Resolva aqui"])
                else:
                    col.page_link(nav.CIDADAO[p], label=p, icon=":material/arrow_outward:")

    elif parte == "Teste":
        st.info(m["como_testar"], icon=":material/science:")
        MODULOS[cod].testar()

    else:
        pct = entregaveis.percentual(cod)
        st.markdown("Tudo o que o enunciado da matéria pede, onde está no projeto, como foi feito e o status. "
                    "Edite na tabela e clique em salvar.")
        st.progress(pct / 100, text=f"{pct}% (feito conta 1, no esqueleto conta meio)")
        entregaveis.editor(cod, detalhes=st.toggle("Mostrar detalhe do enunciado, peso e fonte", key=f"det_{cod}"))
