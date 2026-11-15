# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Questão 04 (2,0): Análise bivariada entre duas variáveis quantitativas.

Par escolhido: distância da estação até o Marco Zero (km) × ocorrências no entorno.
A pergunta do produto é direta: a posição da estação na cidade ajuda a explicar quantas
ocorrências são registradas em volta dela?

    a) gráfico de dispersão, interpretado;
    b) covariância e correlação linear de Pearson, interpretadas;
    c) gráfico da correlação linear de Pearson, interpretado;
    d) reta da regressão linear simples no gráfico de dispersão e a equação;
    e) adequação do modelo (R² e Teste F), interpretada;
    f) uma previsão.

Rodar:  python questao04_bivariada.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy import stats

import comum

X = "dist_marco_zero_km"
Y = comum.RESPOSTA
PREVER_KM = 5.0


def resolver(df=None) -> dict:
    df = comum.carregar() if df is None else df
    x, y = df[X], df[Y]

    comum.titulo("QUESTÃO 04: Análise bivariada (2 variáveis quantitativas)")
    print(f"X = {comum.nome(X)}\nY = {comum.nome(Y)}\nn = {len(df)} estações")

    # ---- b) covariância e correlação (calculadas antes para entrarem no gráfico da letra a)
    covariancia = float(np.cov(x, y, ddof=1)[0, 1])
    r, p_r = stats.pearsonr(x, y)
    r, p_r = float(r), float(p_r)

    # ---- regressão (letras d e e)
    modelo = sm.OLS(y, sm.add_constant(x)).fit()
    a, b = float(modelo.params.iloc[0]), float(modelo.params.iloc[1])
    equacao = f"total = {a:.2f} {'+' if b >= 0 else '−'} {abs(b):.2f} × distância_km"

    comum.item("a", "Gráfico de dispersão")
    print("Cada ponto é uma estação. Ver o arquivo q04a_dispersao.png.")
    perto_c = y[x <= 5]
    longe_c = y[x > 20]
    comum.interpretacao(f"""
        A nuvem desce da esquerda para a direita: quanto mais longe do centro, menos ocorrências
        registradas no entorno. A relação existe, mas é frouxa: há estações distantes com muitos
        registros e estações centrais com poucos.
        A dispersão abre em leque perto do centro (heterocedasticidade): entre 0 e 5 km os valores vão
        de {perto_c.min()} a {perto_c.max()}, enquanto acima de 20 km {int((longe_c < 300).sum())} das
        {len(longe_c)} estações ficam abaixo de 300 (a maior chega a {longe_c.max()}).
        Os pontos no alto à esquerda são as estações de maior circulação; o gráfico rotula as três maiores.
    """)

    comum.item("b", "Covariância e correlação linear de Pearson")
    print(f"Covariância amostral = {covariancia:.2f} (km × ocorrências)")
    print(f"Correlação de Pearson r = {r:.4f}  |  p-valor = {p_r:.3e}  |  r² = {r ** 2:.4f}")
    comum.interpretacao(f"""
        A covariância é negativa, o que só diz o sentido da relação: as duas variáveis andam em
        direções opostas. O valor em si não é comparável com nada, porque depende das unidades
        (quilômetros vezes ocorrências).
        A correlação resolve isso: r = {r:.3f} é adimensional e fica entre −1 e 1. Em módulo, {abs(r):.3f}
        indica relação negativa moderada. O p-valor de {p_r:.1e} é bem menor que 1%. Esse p-valor supõe
        estações independentes, e os raios de 300 m de estações vizinhas se sobrepõem; mesmo assim, com um
        p-valor tão pequeno, a direção da relação é clara nesta base.
        Correlação não é causa: a distância não causa ocorrência. Ela está de intermediária para
        circulação de pessoas, comércio e concentração de serviços, que a base não mede.
    """)

    comum.item("c", "Gráfico da correlação linear de Pearson")
    print("Mapa de calor do par, no arquivo q04c_correlacao.png.")
    comum.interpretacao(f"""
        O mapa mostra a diagonal em 1,00 (cada variável com ela mesma) e {r:.2f} fora da diagonal.
        A cor fria confirma o sinal negativo; a intensidade média confirma a força moderada.
        Num par só o mapa é redundante, mas ele é a mesma leitura que a questão 05 faz com quatro
        variáveis, e serve de ponte entre as duas.
    """)

    comum.item("d", "Reta da regressão linear simples e a equação")
    print(f"Equação estimada:  {equacao}")
    print(f"Intercepto a = {a:.4f}   (erro padrão {modelo.bse.iloc[0]:.4f}, p-valor {modelo.pvalues.iloc[0]:.3e})")
    print(f"Inclinação  b = {b:.4f}   (erro padrão {modelo.bse.iloc[1]:.4f}, p-valor {modelo.pvalues.iloc[1]:.3e})")
    comum.interpretacao(f"""
        Cada quilômetro a mais de distância do Marco Zero corresponde, em média, a {abs(b):.1f} ocorrência
        a menos no entorno da estação.
        O intercepto {a:.0f} seria o valor previsto para uma estação no próprio Marco Zero. É extrapolação
        de borda: a estação mais central da base está a {x.min():.2f} km, então o número serve ao modelo,
        não como previsão para um ponto que não existe na rede.
        A inclinação é significativa (p-valor {modelo.pvalues.iloc[1]:.1e}).
    """)

    comum.item("e", "Adequação do modelo: R² e Teste F")
    print(f"R² = {modelo.rsquared:.4f}   |   R² ajustado = {modelo.rsquared_adj:.4f}")
    print(f"Teste F: F({int(modelo.df_model)}, {int(modelo.df_resid)}) = {modelo.fvalue:.3f}  |  "
          f"p-valor = {modelo.f_pvalue:.3e}")
    bp = comum.checar_pressupostos(modelo)
    comum.interpretacao(f"""
        O Teste F pergunta se o modelo inteiro explica mais que a média simples de Y. Com p-valor
        {modelo.f_pvalue:.1e}, bem abaixo de 1%, a resposta é sim: o modelo é significativo.
        Significativo não é o mesmo que bom. O R² de {modelo.rsquared:.4f} diz que a distância explica
        {modelo.rsquared * 100:.1f}% da variação do número de ocorrências; os outros
        {(1 - modelo.rsquared) * 100:.1f}% vêm do que a base não tem: fluxo de passageiros, comércio no
        entorno, policiamento, hora do dia.
        Em R² simples: um modelo pode ser estatisticamente certo e, ainda assim, prever mal uma estação
        específica. É por isso que a questão 05 acrescenta variáveis.
        Pressupostos: o teste de Breusch-Pagan confirma o leque visto na letra a (p-valor
        {bp['breusch_pagan_p']:.4f}), e os resíduos são assimétricos (assimetria {bp['assimetria_residuos']:.2f}).
        Por isso o Teste F e os p-valores acima são aproximados. Refazendo o p-valor da inclinação com erro
        padrão robusto (HC3), ele fica em {bp['p_robusto'][X]:.1e}: a conclusão sobre o sinal não muda.
    """)

    # ---- f) previsão
    previsao = float(modelo.get_prediction(sm.add_constant(np.array([[PREVER_KM]]), has_constant="add")).predicted_mean[0])
    intervalo = modelo.get_prediction(sm.add_constant(np.array([[PREVER_KM]]), has_constant="add")).conf_int(alpha=0.05)[0]
    comum.item("f", f"Previsão para uma estação a {PREVER_KM:.0f} km do Marco Zero")
    print(f"total previsto = {a:.2f} {'+' if b >= 0 else '−'} {abs(b):.2f} × {PREVER_KM:.0f} = {previsao:.2f} ocorrências")
    print(f"Intervalo de 95% para a média prevista: [{intervalo[0]:.1f} ; {intervalo[1]:.1f}]")
    reais = df[(df[X] >= PREVER_KM - 1) & (df[X] <= PREVER_KM + 1)]
    print(f"Conferência: as {len(reais)} estações entre {PREVER_KM - 1:.0f} e {PREVER_KM + 1:.0f} km têm média real de "
          f"{reais[Y].mean():.1f} (de {reais[Y].min()} a {reais[Y].max()})")
    comum.interpretacao(f"""
        O modelo prevê {previsao:.0f} ocorrências para uma estação a {PREVER_KM:.0f} km do centro, e a média
        real das estações nessa faixa é {reais[Y].mean():.0f}: o modelo acerta a ordem de grandeza.
        O intervalo de confiança é da MÉDIA das estações nessa distância, não de uma estação isolada.
        Com R² de {modelo.rsquared:.2f}, o erro para uma estação específica é grande: na faixa, os valores
        reais vão de {reais[Y].min()} a {reais[Y].max()}. Use a previsão para comparar regiões, nunca para
        afirmar algo sobre uma estação.
    """)

    _graficos(df, x, y, a, b, r, modelo)
    return {"x": X, "y": Y, "covariancia": covariancia, "pearson_r": r, "pearson_p": p_r,
            "intercepto": a, "inclinacao": b, "equacao": equacao,
            "r2": float(modelo.rsquared), "r2_ajustado": float(modelo.rsquared_adj),
            "F": float(modelo.fvalue), "F_p_valor": float(modelo.f_pvalue), "pressupostos": bp,
            "previsao_km": PREVER_KM, "previsao": previsao,
            "previsao_ic95": [float(intervalo[0]), float(intervalo[1])],
            "media_real_na_faixa": float(reais[Y].mean())}


def _graficos(df, x, y, a, b, r, modelo) -> None:
    # a) e d): dispersão com a reta
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.scatter(x, y, s=38, color="#2563eb", alpha=0.65, edgecolor="white", linewidth=0.6, label="Estação")
    grade = np.linspace(x.min(), x.max(), 100)
    ax.plot(grade, a + b * grade, color="#c2410c", lw=2.5,
            label=f"Regressão: y = {comum.dec(a, 1)} {'+' if b >= 0 else '−'} {comum.dec(abs(b), 1)}x   (R² = {comum.dec(modelo.rsquared, 3)})")
    for _, linha in df.nlargest(3, y.name).iterrows():
        ax.annotate(linha["estacao"], (linha[X], linha[Y]), fontsize=8, xytext=(6, 2), textcoords="offset points")
    ax.set_title("Ocorrências no entorno da estação × distância até o Marco Zero")
    ax.set_xlabel(comum.nome(X))
    ax.set_ylabel(comum.nome(y.name))
    ax.legend(fontsize=9)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    print(f"\nGráfico salvo em: {comum.salvar_figura(fig, 'q04a_dispersao.png')}")
    plt.close(fig)

    # c) mapa de calor do par
    fig, ax = plt.subplots(figsize=(4.6, 4))
    matriz = np.array([[1.0, r], [r, 1.0]])
    imagem = ax.imshow(matriz, cmap="coolwarm", vmin=-1, vmax=1)
    rotulos = ["Distância (km)", "Ocorrências"]
    ax.set_xticks([0, 1], rotulos, fontsize=9)
    ax.set_yticks([0, 1], rotulos, fontsize=9)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, comum.dec(matriz[i, j]), ha="center", va="center", fontsize=13, fontweight="bold")
    ax.set_title("Correlação de Pearson", fontsize=11)
    fig.colorbar(imagem, ax=ax, shrink=0.8)
    fig.tight_layout()
    print(f"Gráfico salvo em: {comum.salvar_figura(fig, 'q04c_correlacao.png')}")
    plt.close(fig)


if __name__ == "__main__":
    resolver()
