import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from modulos import sociedade
from nucleo import ui
from nucleo.contrato import Etapa

COR_VEREDITO = {"usaria": "green", "em dúvida": "orange", "não usaria": "red"}
NOME_BARREIRA = {"internet": "internet", "letramento": "uso do celular", "confianca": "confiança",
                 "utilidade": "não atende", "nenhuma": "nenhuma"}

st.title("Simulação da sociedade")
st.markdown("Antes de levar o produto às ruas, um grupo de pessoas simuladas avalia a ideia, cada uma com a sua realidade: "
            "internet, familiaridade com o celular, confiança no governo e o que ela precisa.")
st.markdown(f'Modelo de adesão {ui.tag("MLAM")} · falas com IA {ui.tag("PAI", False)} (em breve)', unsafe_allow_html=True)

with st.expander("Como a simulação funciona"):
    st.markdown(
        "1. **Personas.** Dez pessoas fictícias, descritas em `data/personas.json`, com idade, onde moram, internet, "
        "familiaridade com o celular, confiança no governo, o que precisam, o canal que preferem e um medo.\n"
        "2. **Avaliação.** Para a parte do produto e os canais escolhidos, um modelo logístico calcula a chance de cada pessoa usar: "
        "quanto o produto atende a necessidade dela, menos as barreiras de internet, de uso do celular e de confiança. "
        "Cada pessoa usa o canal que funciona melhor para ela.\n"
        "3. **Fala.** A opinião de cada pessoa é montada a partir dos motivos que mais pesaram.\n"
        "4. **População.** Milhares de pessoas parecidas com as personas, com variação aleatória, estimam a adesão por perfil.\n\n"
        "A ideia vem de projetos como o [TinyTroupe](https://github.com/microsoft/TinyTroupe) da Microsoft, que simula grupos focais "
        "com personas, e de plataformas maiores como [OASIS](https://github.com/camel-ai/oasis) e "
        "[AgentSociety](https://github.com/tsinghua-fib-lab/AgentSociety). Nesta versão não há IA: as falas seguem regras, "
        "e as personas e proporções são fictícias até a MLAM trazer os dados reais.")

c1, c2 = st.columns([3, 2])
parte = c1.selectbox("O que vamos testar", list(sociedade.PARTES), index=1)
n = c2.select_slider("Tamanho da população", [500, 1000, 3000, 5000], value=3000)
canais = st.pills("Por onde o produto chega", list(sociedade.CANAIS), selection_mode="multi", default=["App e site"])
c3, c4 = st.columns([1, 1])
rodar = c3.button("Rodar a simulação", type="primary", width="stretch")
if c4.button("Rodar com outra amostra", width="stretch"):
    st.session_state.sim_semente = st.session_state.get("sim_semente", 7) + 1
    rodar = True

if rodar:
    canais = canais or ["App e site"]
    semente = st.session_state.get("sim_semente", 7)
    st.session_state.sim = {"parte": parte, "canais": canais, "opinioes": sociedade.ouvir_personas(parte, canais),
                            "pop": sociedade.simular_populacao(parte, canais, n, semente), "n": n}
    ui.registrar(f"Simulação: {parte} por {', '.join(canais)}",
                 [Etapa("MLAM", "Calculou a chance de cada pessoa usar", "", "modelo logístico com dados fictícios"),
                  Etapa("MLAM", "Simulou a população", "", f"{n} pessoas sintéticas"),
                  Etapa("PAI", "Falas com IA", "", "em breve: hoje as falas seguem regras", pronto=False)])

sim = st.session_state.get("sim")
if sim:
    ops = sim["opinioes"]
    adesao, por_perfil, barreiras = sim["pop"]
    usariam = sum(o.veredito == "usaria" for o in ops)
    principal = max(barreiras, key=barreiras.get) if barreiras else "nenhuma"

    st.subheader("Resumo")
    m1, m2, m3 = st.columns(3)
    m1.metric("Personas que usariam", f"{usariam} de {len(ops)}")
    m2.metric("Adesão estimada", f"{adesao}%", help=f"em {sim['n']} pessoas sintéticas")
    m3.metric("Principal barreira", NOME_BARREIRA[principal])
    st.caption(f"Testando: {sim['parte']}. Canais: {', '.join(sim['canais'])}. Dados fictícios.")

    st.subheader("O que as pessoas disseram")
    cols = st.columns(2)
    for i, o in enumerate(sorted(ops, key=lambda x: -x.chance)):
        p = o.persona
        with cols[i % 2].container(border=True):
            st.markdown(f"**{p['nome']}**, {p['idade']} anos")
            st.caption(f"{p['quem']}, {p['onde']}. Internet: {p['internet']}.")
            st.badge(f"{o.veredito} · nota {o.nota} de 5", color=COR_VEREDITO[o.veredito])
            st.markdown(f"*“{o.fala}”*")
            st.caption(f"Canal que funciona melhor para {'ela' if p['genero'] == 'f' else 'ele'}: {o.canal}. Sugestão: {o.sugestao}.")

    st.subheader("Adesão por perfil")
    fig, ax = plt.subplots(figsize=(6.4, 0.42 * len(por_perfil) + 0.6))
    nomes, valores = list(por_perfil)[::-1], list(por_perfil.values())[::-1]
    ax.barh(nomes, valores, color="#1F6F6B", height=0.55)
    for j, v in enumerate(valores):
        ax.text(v + 1, j, f"{v}%", va="center", fontsize=9, color="#17363A")
    ax.set_xlim(0, 105)
    ax.tick_params(axis="y", labelsize=9, colors="#17363A")
    ax.tick_params(axis="x", labelsize=8, colors="#5b6b66")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("pessoas que usariam (%)", fontsize=8, color="#5b6b66")
    fig.tight_layout()
    st.pyplot(fig)

    st.subheader("Sugestões mais citadas")
    contagem = {}
    for o in ops:
        if o.veredito != "usaria" or o.barreira != "nenhuma":
            contagem[o.sugestao] = contagem.get(o.sugestao, 0) + 1
    for sug, k in sorted(contagem.items(), key=lambda x: -x[1]):
        st.markdown(f"- {sug} ({k} {'pessoa' if k == 1 else 'pessoas'})")
    ui.como_chegamos(ui.ultimo_rastro()["etapas"] if ui.ultimo_rastro() else [])
