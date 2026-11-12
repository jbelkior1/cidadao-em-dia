import streamlit as st

from modulos import coa, dsa, sers
from nucleo import nav, orquestrador, ui



def mostrar():
    PERGUNTAS = [
        ("cad", "Sua família está no Cadastro Único?", "É o cadastro do governo para programas sociais, feito no CRAS."),
        ("atu", "O cadastro foi atualizado nos últimos 2 anos?", "Se você não lembra, responda não."),
        ("tit", "A conta de luz está no nome de alguém da família?", "Olhe o nome que aparece no topo da conta."),
    ]
    CORES = {"ok": "#2E7D4F", "risco": "#B7791F", "comecar": "#1F6F6B"}

    s = st.session_state
    s.setdefault("dir_passo", 0)
    s.setdefault("dir_resp", {})


    def responder(chave, valor):
        s.dir_resp[chave] = valor
        s.dir_passo += 1
        if chave == "cad" and not valor:      # sem cadastro, a pergunta da atualização não faz sentido
            s.dir_resp["atu"] = False
            s.dir_passo += 1


    def recomecar():
        s.dir_passo, s.dir_resp = 0, {}
        s.pop("dir_resultado", None)


    st.title("Meus direitos")
    ui.veio_do_atendimento("Meus direitos")
    ui.guia("Descobre se você pode ter o desconto na conta de luz, se ele está em risco e o que fazer.",
            ["Responda as perguntas de sim ou não.", "Informe o consumo de luz, use o medidor ou pule.",
             "Leia o comprovante e abra Entenda cada parte do resultado para ver as contas."],
            ["PCP", "DSA", "COA", "SERS", "PAI"], "Responda Sim, Não, Sim e use o medidor: o comprovante mostra o selo de cada matéria e a conta do desconto.")

    if s.dir_passo < 3:
        chave, pergunta, ajuda = PERGUNTAS[s.dir_passo]
        st.progress(s.dir_passo / 4, text=f"Pergunta {s.dir_passo + 1} de 4")
        st.markdown(f"### {pergunta}")
        st.caption(ajuda)
        c1, c2 = st.columns(2)
        c1.button("Sim", on_click=responder, args=(chave, True), width="stretch", type="primary")
        c2.button("Não", on_click=responder, args=(chave, False), width="stretch")
        st.caption("Nenhum dado pessoal é pedido.")

    elif s.dir_passo == 3:
        st.progress(3 / 4, text="Pergunta 4 de 4")
        st.markdown("### Quanto de energia sua casa gasta por mês?")
        st.caption("Aparece na conta de luz, em kWh. Se não souber, tudo bem.")
        modo = st.radio("Como você quer informar", ["Eu sei o valor", "Usar o medidor da casa", "Não sei"], horizontal=True, label_visibility="collapsed")
        kwh, do_medidor = None, False
        if modo == "Eu sei o valor":
            kwh = float(st.number_input("Consumo em kWh por mês", 0, 1000, 90, step=5))
        elif modo == "Usar o medidor da casa":
            kwh, do_medidor = coa.ler_consumo(), True
            st.info(f"O medidor marcou {kwh} kWh neste mês (simulação).")
        c1, c2 = st.columns(2)
        if c1.button("Ver o resultado", type="primary", width="stretch"):
            r = s.dir_resp
            s.dir_resultado = orquestrador.checar_direitos(r["cad"], r["atu"], r["tit"], kwh, do_medidor)
            ui.registrar("Checagem em Meus direitos", s.dir_resultado.etapas)
            s.dir_passo = 4
            st.rerun()
        c2.button("Voltar ao começo", on_click=recomecar, width="stretch")

    else:
        r = s.dir_resultado
        cor = CORES[r.nivel]
        partes = [f'<div class="status" style="border-left:6px solid {cor}; color:{cor}">{r.situacao}{ui.tags("PCP")}</div>',
                  f'<p class="sub">{r.explicacao}</p>',
                  "<h4>O que fazer</h4><ol>" + "".join(f"<li>{p}</li>" for p in r.passos) + "</ol>"]
        if r.prazo and r.dias is not None:
            partes.append(f'<h4>Prazo</h4><p><span class="marca">até {dsa.data_br(r.prazo["prazo"])}</span> faltam {r.dias} dias'
                          f'{ui.tags("DSA")}<br><span class="fonte">{r.prazo["acao"]} ({r.prazo["situacao_do_dado"]})</span></p>')
        if r.economia is not None:
            partes.append(f'<h4>Quanto vale o desconto</h4><p class="valor">{sers.brl(r.economia)} por ano{ui.tags("SERS")}</p>'
                          '<p class="fonte">Estimativa com tarifa e faixa de exemplo.</p>')
        if r.documentos:
            partes.append(f"<h4>O que levar</h4><p>{r.documentos}{ui.tags('PAI')}</p>")
        if r.fonte:
            partes.append(f'<p class="fonte">Fonte: {r.fonte["fonte"]} (conferido: {r.fonte["verificado_em"]}){ui.tags("PCP")}</p>')
        st.markdown(f'<div class="comprovante">{"".join(partes)}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.button("Refazer as perguntas", on_click=recomecar, width="stretch")
        c2.button("Entender minha conta de luz", icon=":material/bolt:", on_click=ui.trocar_servico, args=("Minha conta de luz",), width="stretch")
        with st.expander("Entenda cada parte do resultado", icon=":material/lightbulb:"):
            resp = s.dir_resp
            sim_nao = lambda v: "sim" if v else "não"
            st.markdown(f"**Situação {ui.tags('PCP')}** · O sistema usa três regras: sem Cadastro Único, o primeiro passo é fazer o cadastro; "
                        f"cadastro sem atualização há mais de 2 anos coloca o desconto em risco; conta de luz fora do nome da família também. "
                        f"Suas respostas: Cadastro Único {sim_nao(resp.get('cad'))}, atualizado {sim_nao(resp.get('atu'))}, "
                        f"conta no nome da família {sim_nao(resp.get('tit'))}. Por isso: {r.situacao.lower()}.", unsafe_allow_html=True)
            if r.prazo:
                st.markdown(f"**Prazo {ui.tags('DSA')}** · Vem do catálogo de prazos: {r.prazo['acao'].lower()} até {dsa.data_br(r.prazo['prazo'])}. "
                            f"Contando de hoje, faltam {r.dias} dias. Dado {r.prazo['situacao_do_dado']}.", unsafe_allow_html=True)
            if r.economia is not None and r.kwh is not None:
                kwh_desc = min(r.kwh, sers.FAIXA_EXEMPLO)
                st.markdown(f"**Quanto vale {ui.tags('SERS')}** · O desconto vale para até {sers.FAIXA_EXEMPLO} kWh por mês. "
                            f"Seu consumo: {r.kwh:g} kWh, então entram {kwh_desc:g} kWh. "
                            f"{kwh_desc:g} kWh × {sers.brl(sers.TARIFA_EXEMPLO)} = {sers.brl(kwh_desc * sers.TARIFA_EXEMPLO)} por mês, "
                            f"× 12 meses = {sers.brl(r.economia)} por ano. Tarifa e faixa de exemplo.", unsafe_allow_html=True)
            if r.ficha:
                st.markdown(f"**O que levar {ui.tags('PAI')}** · Vem da ficha {r.ficha['id']} do agente, de {r.ficha['data']}. Ficha fictícia nesta versão.",
                            unsafe_allow_html=True)
            if r.fonte:
                st.markdown(f"**Fonte {ui.tags('PCP')}** · Toda orientação guarda a fonte oficial e a data em que foi conferida: {r.fonte['fonte']}.",
                            unsafe_allow_html=True)
        ui.como_chegamos(r.etapas)

    ui.rodape()
