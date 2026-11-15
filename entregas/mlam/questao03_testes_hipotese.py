# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Questão 03 (1,0): Teste de hipótese para a média, com desvio padrão de referência conhecido.

    a) média amostral MENOR que a de referência; significância 6%; n = 20;
    b) média amostral MAIOR que a de referência; significância 9%; n = 25.

Em ambos, o desvio padrão de referência é o desvio padrão populacional da base, como pede o enunciado,
então o teste é o z para a média (e não o t).

As amostras não são sorteadas: cada uma responde a uma pergunta do problema-tema.
  a) as 20 estações MAIS DISTANTES do Marco Zero: a periferia da rede registra menos ocorrências?
  b) as 25 estações MAIS PRÓXIMAS do Marco Zero: o centro registra mais?
Amostra dirigida é escolha de recorte, não sorteio: as conclusões valem para esses grupos de estações,
não para uma estação qualquer. Isso está dito nas interpretações e nas limitações do relatório.

Rodar:  python questao03_testes_hipotese.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import comum

SEMENTE = 42        # para a checagem com amostra sorteada: com a mesma semente, o resultado se repete


def _teste_z(amostra, mu0: float, sigma: float, alfa: float, lado: str) -> dict:
    n = len(amostra)
    media_amostral = float(np.mean(amostra))
    erro_padrao = sigma / np.sqrt(n)
    z = (media_amostral - mu0) / erro_padrao
    if lado == "menor":
        critico, p_valor = float(stats.norm.ppf(alfa)), float(stats.norm.cdf(z))
        rejeita = z < critico
    else:
        critico, p_valor = float(stats.norm.ppf(1 - alfa)), float(stats.norm.sf(z))
        rejeita = z > critico
    return {"n": n, "media_amostral": media_amostral, "mu0": mu0, "sigma": sigma, "erro_padrao": float(erro_padrao),
            "z": float(z), "z_critico": critico, "alfa": alfa, "p_valor": p_valor, "rejeita_h0": bool(rejeita),
            "lado": lado}


def _mostrar(r: dict, h1_texto: str) -> None:
    sinal = "<" if r["lado"] == "menor" else ">"
    print(f"H0: μ = {r['mu0']:.2f}   (a média do grupo é igual à de referência)")
    print(f"H1: μ {sinal} {r['mu0']:.2f}   ({h1_texto})")
    print(f"n = {r['n']} | média amostral = {r['media_amostral']:.2f} | σ de referência = {r['sigma']:.2f} | "
          f"erro padrão = {r['erro_padrao']:.2f}")
    print(f"z = ({r['media_amostral']:.2f} − {r['mu0']:.2f}) / {r['erro_padrao']:.2f} = {r['z']:.4f}")
    print(f"α = {r['alfa'] * 100:.0f}%  →  z crítico = {r['z_critico']:.4f}  |  p-valor = {r['p_valor']:.4f}")
    decisao = "REJEITA H0" if r["rejeita_h0"] else "NÃO REJEITA H0"
    print(f"Decisão: {decisao} (p-valor {'<' if r['p_valor'] < r['alfa'] else '≥'} α)")


def resolver(df=None) -> dict:
    df = comum.carregar() if df is None else df
    x = df[comum.RESPOSTA]
    mu0 = float(x.mean())
    sigma = float(x.std(ddof=0))

    comum.titulo("QUESTÃO 03: Teste de hipótese para a média (teste z)")
    print(f"Variável: {comum.nome(comum.RESPOSTA)}")
    print(f"Média populacional de referência μ0 = {mu0:.2f} (as 139 estações)")
    print(f"Desvio padrão de referência σ = {sigma:.2f} (desvio padrão populacional, como pede o enunciado)")

    # ---- a) n = 20, α = 6%, unilateral à esquerda
    longe = df.nlargest(20, "dist_marco_zero_km")
    comum.item("a", "Média amostral MENOR que a de referência: α = 6%, n = 20")
    print(f"Amostra: as 20 estações mais distantes do Marco Zero "
          f"(de {longe.dist_marco_zero_km.min():.1f} km a {longe.dist_marco_zero_km.max():.1f} km)")
    r_a = _teste_z(longe[comum.RESPOSTA], mu0, sigma, 0.06, "menor")
    _mostrar(r_a, "a periferia da rede registra menos ocorrências")
    comum.interpretacao(f"""
        A média das 20 estações mais distantes é {r_a['media_amostral']:.1f}, contra {mu0:.1f} da rede inteira.
        Com z = {r_a['z']:.3f} abaixo do crítico {r_a['z_critico']:.3f} e p-valor {r_a['p_valor']:.4f}, o
        procedimento rejeita H0 a 6%, mas por pouco: o p-valor ({r_a['p_valor']:.4f}) está só um pouco abaixo
        do nível de 6%. A 5% a decisão seria a mesma (o z crítico a 5% é {stats.norm.ppf(0.05):.3f} e o z
        observado, {r_a['z']:.3f}, continua além dele); o resultado só deixaria de rejeitar H0 se o nível
        fosse menor que o próprio p-valor, ou seja, abaixo de {r_a['p_valor'] * 100:.1f}%.
        Cuidado com a leitura: este grupo não foi sorteado, foi escolhido pelos extremos de distância e faz
        parte da própria população de referência. Nesse caso o p-valor não mede "acaso de amostragem"; o
        teste descreve que esse grupo de ponta de linha tem média de registros abaixo da rede, não prova
        nada sobre uma estação qualquer. A checagem com amostra sorteada, logo abaixo, mostra a diferença.
        Atenção ao que o dado é: contagem de registros de BO, não risco por passageiro. Essas estações também
        movimentam menos gente, e a base não traz o fluxo de passageiros para dividir uma coisa pela outra.
    """)

    # ---- b) n = 25, α = 9%, unilateral à direita
    perto = df.nsmallest(25, "dist_marco_zero_km")
    comum.item("b", "Média amostral MAIOR que a de referência: α = 9%, n = 25")
    print(f"Amostra: as 25 estações mais próximas do Marco Zero "
          f"(de {perto.dist_marco_zero_km.min():.1f} km a {perto.dist_marco_zero_km.max():.1f} km)")
    r_b = _teste_z(perto[comum.RESPOSTA], mu0, sigma, 0.09, "maior")
    _mostrar(r_b, "o centro expandido registra mais ocorrências")
    comum.interpretacao(f"""
        A média das 25 estações mais centrais é {r_b['media_amostral']:.1f}, mais que o dobro da referência
        ({mu0:.1f}). Com z = {r_b['z']:.3f}, muito acima do crítico {r_b['z_critico']:.3f}, o procedimento
        rejeita H0 a 9% com folga.
        Vale o mesmo cuidado da letra a: o grupo foi escolhido pela distância, não sorteado, então o
        resultado descreve o centro expandido e não é inferência para a rede. Os dois testes mostram a mesma
        tendência por lados opostos, o que motiva olhar a distância nas questões 04 e 05, onde a relação é
        medida com a base inteira, sem recorte.
    """)

    # ---- checagem: as mesmas contas com amostras SORTEADAS, para separar recorte de acaso
    comum.item("checagem", "As mesmas contas com amostras sorteadas (semente fixa, para dar para repetir)")
    sorteio_a = df.sample(20, random_state=SEMENTE)[comum.RESPOSTA]
    sorteio_b = df.sample(25, random_state=SEMENTE + 1)[comum.RESPOSTA]
    s_a = _teste_z(sorteio_a, mu0, sigma, 0.06, "menor")
    s_b = _teste_z(sorteio_b, mu0, sigma, 0.09, "maior")
    for rotulo, r in (("a) n = 20, α = 6%, H1: μ < μ0", s_a), ("b) n = 25, α = 9%, H1: μ > μ0", s_b)):
        print(f"{rotulo}: média sorteada = {r['media_amostral']:.1f} | z = {r['z']:.3f} | crítico = {r['z_critico']:.3f} | "
              f"p-valor = {r['p_valor']:.4f} | {'REJEITA H0' if r['rejeita_h0'] else 'NÃO REJEITA H0'}")
    comum.interpretacao(f"""
        Com amostras sorteadas (sementes {SEMENTE} e {SEMENTE + 1}), que é o que o teste z pressupõe, as médias
        ficam perto da referência e o resultado muda: {'rejeita' if s_a['rejeita_h0'] else 'não rejeita'} H0
        na letra a e {'rejeita' if s_b['rejeita_h0'] else 'não rejeita'} na letra b. É isso que se espera de
        uma amostra aleatória da própria população: a média dela flutua em torno de μ0.
        A comparação deixa claro o que cada leitura significa. Os recortes por distância mostram uma
        diferença real ENTRE grupos de estações; o sorteio mostra que, sem escolher o grupo, não há motivo para
        a média de uma amostra fugir da referência.
    """)

    _grafico(r_a, r_b)
    return {"referencia": {"mu0": mu0, "sigma": sigma}, "a": r_a, "b": r_b,
            "checagem_sorteada": {"semente": SEMENTE, "a": s_a, "b": s_b}}


def _grafico(r_a: dict, r_b: dict) -> None:
    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, r, titulo_ in zip(eixos, (r_a, r_b), ("a) 20 mais distantes · α = 6%", "b) 25 mais próximas · α = 9%")):
        grade = np.linspace(-6.5, 6.5, 500)
        ax.plot(grade, stats.norm.pdf(grade), color="#1f2937", lw=1.5)
        if r["lado"] == "menor":
            ax.fill_between(grade, stats.norm.pdf(grade), where=grade < r["z_critico"], color="#c2410c", alpha=0.45,
                            label=f"região de rejeição (α = {r['alfa'] * 100:.0f}%)")
        else:
            ax.fill_between(grade, stats.norm.pdf(grade), where=grade > r["z_critico"], color="#c2410c", alpha=0.45,
                            label=f"região de rejeição (α = {r['alfa'] * 100:.0f}%)")
        ax.axvline(r["z"], color="#16a34a", lw=2, label=f"z observado = {comum.dec(r['z'])}")
        ax.axvline(r["z_critico"], color="#1f2937", ls="--", lw=1.2, label=f"z crítico = {comum.dec(r['z_critico'])}")
        ax.set_title(titulo_)
        ax.set_xlabel("z")
        ax.set_ylabel("Densidade")
        ax.legend(fontsize=8)
    fig.tight_layout()
    print(f"\nGráfico salvo em: {comum.salvar_figura(fig, 'q03_testes_hipotese.png')}")
    plt.close(fig)


if __name__ == "__main__":
    resolver()
