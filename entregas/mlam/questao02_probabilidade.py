"""Questão 02 (1,0) — Probabilidade com distribuição normal.

Variável escolhida: `total`, as ocorrências registradas no entorno de cada estação.

    a) P(X < média dos registros), classificando o evento;
    b) P(X > mediana dos registros), classificando o evento.

Rodar:  python questao02_probabilidade.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import comum


def resolver(df=None) -> dict:
    df = comum.carregar() if df is None else df
    x = df[comum.RESPOSTA]
    media, mediana = x.mean(), x.median()
    desvio = x.std(ddof=0)                      # desvio padrão populacional: a base é a população das 139 estações
    normal = stats.norm(loc=media, scale=desvio)

    comum.titulo("QUESTÃO 02 — Probabilidade assumindo distribuição normal")
    print(f"Variável: {comum.nome(comum.RESPOSTA)}")
    print(f"n = {len(x)} estações | média = {media:.2f} | mediana = {mediana:.2f} | "
          f"desvio padrão populacional = {desvio:.2f}")
    print(f"Modelo assumido: X ~ Normal(μ = {media:.2f}, σ = {desvio:.2f})")

    # ---- a) P(X < média)
    z_media = (media - media) / desvio
    p_a = float(normal.cdf(media))
    comum.item("a", f"P(X < média) = P(X < {media:.2f})")
    print(f"z = ({media:.2f} − {media:.2f}) / {desvio:.2f} = {z_media:.4f}")
    print(f"P(X < {media:.2f}) = Φ({z_media:.4f}) = {p_a:.4f}  ({p_a * 100:.2f}%)")
    print(f"Classificação: {comum.classificar_probabilidade(p_a)}")
    real_abaixo = float((x < media).mean())
    massa_negativa = float(normal.cdf(0))
    comum.interpretacao(f"""
        O resultado é exatamente 0,5 por construção: a normal é simétrica em torno da média, então
        metade da massa fica de cada lado. Assumindo normalidade, uma estação sorteada teria 50% de
        chance de ter menos de {media:.0f} ocorrências no entorno.
        O dado real não é simétrico: {real_abaixo * 100:.1f}% das 139 estações ficam abaixo da média,
        não 50%. E a normal com σ = {desvio:.0f} coloca {massa_negativa * 100:.1f}% da probabilidade em
        valores negativos, que são impossíveis para uma contagem de ocorrências. As duas coisas mostram
        que a normalidade pedida pelo enunciado é uma aproximação grosseira para esta variável.
    """)

    # ---- b) P(X > mediana)
    z_mediana = (mediana - media) / desvio
    p_b = float(normal.sf(mediana))
    comum.item("b", f"P(X > mediana) = P(X > {mediana:.2f})")
    print(f"z = ({mediana:.2f} − {media:.2f}) / {desvio:.2f} = {z_mediana:.4f}")
    print(f"P(X > {mediana:.2f}) = 1 − Φ({z_mediana:.4f}) = {p_b:.4f}  ({p_b * 100:.2f}%)")
    print(f"Classificação: {comum.classificar_probabilidade(p_b)}")
    comum.interpretacao(f"""
        Como a mediana ({mediana:.0f}) é bem menor que a média ({media:.2f}), o modelo normal coloca
        {p_b * 100:.1f}% da probabilidade acima dela: é um evento provável.
        A distância entre média e mediana mostra a assimetria à direita da distribuição real: poucas
        estações muito movimentadas (República tem 2.100 registros) puxam a média para cima, enquanto
        metade das estações fica abaixo de {mediana:.0f}.
        Na distribuição real, P(X > mediana) é 0,5 por definição de mediana; o modelo normal devolve
        {p_b:.4f}. A diferença de {abs(p_b - 0.5) * 100:.1f} pontos percentuais é o preço de assumir
        normalidade numa variável assimétrica, como o enunciado pede. É a principal limitação desta questão.
    """)

    _grafico(x, media, mediana, desvio, normal)
    return {"n": int(len(x)), "media": float(media), "mediana": float(mediana), "desvio_populacional": float(desvio),
            "proporcao_real_abaixo_da_media": real_abaixo, "massa_normal_negativa": massa_negativa,
            "a_P_menor_que_media": p_a, "a_classificacao": comum.classificar_probabilidade(p_a),
            "b_P_maior_que_mediana": p_b, "b_classificacao": comum.classificar_probabilidade(p_b),
            "b_z": float(z_mediana)}


def _grafico(x, media, mediana, desvio, normal) -> None:
    """Histograma real contra a normal assumida, com as duas áreas das letras a e b."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    grade = np.linspace(max(0, media - 4 * desvio), media + 4 * desvio, 400)

    ax1.hist(x, bins=20, density=True, color="#9ecae1", edgecolor="white", label="Distribuição real")
    ax1.plot(grade, normal.pdf(grade), color="#c2410c", lw=2, label="Normal assumida")
    ax1.axvline(media, color="#1f2937", ls="--", lw=1.5, label=f"Média = {media:.0f}")
    ax1.axvline(mediana, color="#16a34a", ls=":", lw=2, label=f"Mediana = {mediana:.0f}")
    ax1.set_title("Ocorrências por estação: dado real e modelo normal")
    ax1.set_xlabel(comum.nome(comum.RESPOSTA))
    ax1.set_ylabel("Densidade")
    ax1.legend(fontsize=8)

    ax2.plot(grade, normal.pdf(grade), color="#1f2937", lw=1.5)
    ax2.fill_between(grade, normal.pdf(grade), where=grade < media, color="#93c5fd", alpha=0.8,
                     label=f"a) P(X < média) = {normal.cdf(media):.4f}")
    ax2.fill_between(grade, normal.pdf(grade), where=grade > mediana, color="#c2410c", alpha=0.45,
                     label=f"b) P(X > mediana) = {normal.sf(mediana):.4f}")
    ax2.set_title("Áreas das letras a) e b)")
    ax2.set_xlabel(comum.nome(comum.RESPOSTA))
    ax2.set_ylabel("Densidade")
    ax2.legend(fontsize=8)

    fig.tight_layout()
    print(f"\nGráfico salvo em: {comum.salvar_figura(fig, 'q02_probabilidade.png')}")
    plt.close(fig)


if __name__ == "__main__":
    resolver()
