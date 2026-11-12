import streamlit as st

from modulos import coa, sers
from nucleo import nav, orquestrador, ui



def mostrar():
    st.title("Minha conta de luz")
    st.markdown("Veja quanto sua casa gasta, quanto isso custa e quanto vale o desconto da tarifa social.")
    ui.veio_do_atendimento("Minha conta de luz")
    ui.guia("Mostra quanto a casa gasta de energia, quanto fica a conta e quanto vale o desconto.",
            ["Leia o medidor da casa ou ajuste quantas horas usa cada aparelho.", "Veja o consumo, a conta e o desconto.",
             "Abra Como calculamos para ver a conta de cada aparelho."],
            ["COA", "SERS"], "Leia o medidor algumas vezes para a luz mudar de cor e depois mexa no chuveiro para ver a conta subir.")

    st.subheader("Medidor da casa")
    st.caption("O medidor conta o consumo do mês e acende uma luz quando a faixa com desconto está acabando.")
    if st.button("Ler o medidor", type="primary"):
        st.session_state.luz_medidor = coa.ler_consumo()
    k_med = st.session_state.get("luz_medidor")
    if k_med is not None:
        cor, frase = coa.estado(k_med)
        st.markdown(f"**{k_med} kWh** neste mês{ui.tags('COA')}", unsafe_allow_html=True)
        st.progress(min(k_med / coa.FAIXA_KWH, 1.0), text=f"Luz {cor}: {frase} ({coa.FAIXA_KWH} kWh de exemplo)")

    st.subheader("Quanto cada aparelho gasta")
    usar_medidor = k_med is not None and st.toggle("Usar a leitura do medidor no cálculo", value=False)
    if usar_medidor:
        kwh = k_med
    else:
        with st.expander("Ajustar o uso dos aparelhos", expanded=True):
            kwh = sers.calculadora("luz")

    res = orquestrador.conta_de_luz(kwh, usar_medidor)
    ui.registrar("Cálculo em Minha conta de luz", res["etapas"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Consumo do mês", f"{res['kwh']} kWh")
    c2.metric("Conta estimada", sers.brl(res["conta"]))
    c3.metric("Desconto vale até", f"{sers.brl(res['economia'])}/ano")
    st.markdown(f'<p class="fonte">Valores estimados com tarifa e faixa de exemplo.{ui.tags("SERS")}</p>', unsafe_allow_html=True)

    with st.expander("Como calculamos", icon=":material/calculate:"):
        if usar_medidor:
            st.markdown(f"O consumo veio do medidor da casa: {res['kwh']} kWh no mês.")
        else:
            st.markdown("Cada aparelho gasta potência × horas por dia × 30 dias ÷ 1000 = kWh por mês.")
            st.dataframe(sers.detalhe("luz"), hide_index=True, width="stretch")
        kwh_desc = min(res["kwh"], sers.FAIXA_EXEMPLO)
        st.markdown(f"Conta: {res['kwh']} kWh × {sers.brl(sers.TARIFA_EXEMPLO)} = {sers.brl(res['conta'])}.  \n"
                    f"Desconto: vale para até {sers.FAIXA_EXEMPLO} kWh, então {kwh_desc:g} kWh × {sers.brl(sers.TARIFA_EXEMPLO)} × 12 meses = {sers.brl(res['economia'])} por ano.  \n"
                    "Tarifa, faixa e potências são exemplos.")
    st.button("Ver se você tem direito ao desconto", icon=":material/fact_check:", on_click=ui.trocar_servico, args=("Meus direitos",))
    ui.como_chegamos(res["etapas"])
    ui.rodape()
