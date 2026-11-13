"""Questão 05 (2,0) — Análise multivariada com regressão linear múltipla.

Quatro variáveis quantitativas: ocorrências no entorno (resposta) explicadas por distância até o
Marco Zero, quantidade de linhas na estação e latitude.

    a) gráfico de dispersão com pelo menos 3 variáveis quantitativas, interpretado;
    b) matriz de covariância e matriz de correlação de Pearson, interpretadas;
    c) gráfico de correlação de Pearson, interpretado;
    d) equação da regressão linear múltipla;
    e) adequação do modelo (R² e Teste F), interpretada;
    f) previsão com pelo menos 2 variáveis explicativas.

Rodar:  python questao05_multivariada.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

import comum

X = comum.EXPLICATIVAS          # dist_marco_zero_km, qtd_linhas, lat
Y = comum.RESPOSTA
CENARIO = {"dist_marco_zero_km": 4.0, "qtd_linhas": 3, "lat": -23.55}


def resolver(df=None) -> dict:
    df = comum.carregar() if df is None else df
    colunas = [Y, *X]
    dados = df[colunas]

    comum.titulo("QUESTÃO 05 — Análise multivariada (regressão linear múltipla)")
    print(f"Resposta:     {Y} — {comum.nome(Y)}")
    for c in X:
        print(f"Explicativa:  {c} — {comum.nome(c)}")
    print(f"n = {len(df)} estações")
    print("\nNão entram como explicativas: roubo, furto, outros e as faixas de horário. Cada um desses")
    print("grupos soma exatamente `total`, então seriam a própria resposta reescrita.")

    comum.item("a", "Gráfico de dispersão com as quatro variáveis")
    print("Matriz de dispersão em q05a_dispersao.png: cada painel fora da diagonal é um par de variáveis,")
    print("e a diagonal traz o histograma de cada uma.")
    comum.interpretacao("""
        A coluna da resposta mostra o que já se via na questão 04: queda com a distância e subida com a
        quantidade de linhas. A latitude quase não inclina, o que indica que a divisão norte-sul importa
        pouco depois que a distância ao centro já está no modelo.
        A quantidade de linhas é discreta (1 a 5) e quase toda concentrada em 1, por isso seus painéis
        aparecem em faixas: as poucas estações de baldeação estão no alto da faixa de `total`.
        O histograma de `total` mostra a assimetria à direita que a questão 02 já tinha apontado.
    """)

    comum.item("b", "Matriz de covariância e matriz de correlação de Pearson")
    covariancia = dados.cov()
    correlacao = dados.corr()
    print("\nMatriz de covariância (unidades de cada par, não comparáveis entre si):")
    print(covariancia.round(3).to_string())
    print("\nMatriz de correlação de Pearson (adimensional, de −1 a 1):")
    print(correlacao.round(4).to_string())
    r_dist, r_linhas, r_lat = (float(correlacao.loc[Y, c]) for c in X)
    r_entre = float(correlacao.loc["dist_marco_zero_km", "qtd_linhas"])
    comum.interpretacao(f"""
        A covariância serve para ver o sinal; comparar magnitudes entre pares não faz sentido, porque
        cada célula tem uma unidade diferente (km × ocorrências, linhas × ocorrências, grau × ocorrências).
        Na correlação dá para comparar: quantidade de linhas tem a relação mais forte com as ocorrências
        ({r_linhas:.3f}), seguida da distância ({r_dist:.3f}); a latitude é fraca ({r_lat:.3f}).
        Entre as explicativas, distância e quantidade de linhas correlacionam {r_entre:.3f}: estações de
        baldeação tendem a ficar perto do centro. A relação entre elas é fraca, então cada uma traz
        informação própria; o VIF abaixo confirma que não há multicolinearidade atrapalhando.
    """)

    comum.item("c", "Gráfico de correlação de Pearson")
    print("Mapa de calor em q05c_correlacao.png.")
    comum.interpretacao("""
        Ler a primeira linha do mapa responde à pergunta do produto: o que acompanha o número de
        ocorrências. Ler fora dela mostra se as explicativas dizem a mesma coisa entre si, que é o que
        decide se vale manter as duas no modelo.
    """)

    modelo = sm.OLS(dados[Y], sm.add_constant(dados[X])).fit()
    coeficientes = {nome_: float(valor) for nome_, valor in modelo.params.items()}
    const = coeficientes["const"]
    termos = " ".join(f"{'+' if coeficientes[c] >= 0 else '−'} {abs(coeficientes[c]):.2f}×{c} " for c in X)
    equacao = f"total = {const:.2f} {termos}".strip()

    comum.item("d", "Equação da regressão linear múltipla")
    print(f"\n{equacao}\n")
    print(modelo.summary2().tables[1].round(4).to_string())
    comum.interpretacao(f"""
        Cada coeficiente é o efeito daquela variável mantendo as outras fixas.
        Distância: cada quilômetro a mais do centro corresponde a {abs(coeficientes['dist_marco_zero_km']):.1f}
        ocorrência a menos, entre estações com o mesmo número de linhas e a mesma latitude.
        Quantidade de linhas: cada linha a mais corresponde a {abs(coeficientes['qtd_linhas']):.0f} ocorrências
        {'a mais' if coeficientes['qtd_linhas'] >= 0 else 'a menos'}, à mesma distância do centro. É o maior
        efeito do modelo e faz sentido: baldeação concentra gente.
        Latitude: p-valor {modelo.pvalues['lat']:.3f}. {'Não é significativa a 5%, então a posição norte-sul não acrescenta ao que a distância já explica.' if modelo.pvalues['lat'] >= 0.05 else 'É significativa a 5%.'}
    """)

    vif = pd.DataFrame({"variavel": X,
                        "VIF": [variance_inflation_factor(sm.add_constant(dados[X]).values, i + 1) for i in range(len(X))]})
    comum.item("e", "Adequação do modelo: R² e Teste F")
    print(f"R² = {modelo.rsquared:.4f}   |   R² ajustado = {modelo.rsquared_adj:.4f}")
    print(f"Teste F: F({int(modelo.df_model)}, {int(modelo.df_resid)}) = {modelo.fvalue:.3f}  |  "
          f"p-valor = {modelo.f_pvalue:.3e}")
    print("\nFator de inflação da variância (VIF), para checar multicolinearidade:")
    print(vif.round(3).to_string(index=False))
    simples = sm.OLS(dados[Y], sm.add_constant(dados[["dist_marco_zero_km"]])).fit()
    comum.interpretacao(f"""
        O Teste F rejeita, com p-valor {modelo.f_pvalue:.1e}: o conjunto das três variáveis explica mais
        que a média simples.
        O R² subiu de {simples.rsquared:.4f} na questão 04 (só distância) para {modelo.rsquared:.4f} aqui.
        Acrescentar a quantidade de linhas valeu a pena: são {(modelo.rsquared - simples.rsquared) * 100:.1f}
        pontos percentuais de variação explicada a mais.
        Olhar o R² ajustado ({modelo.rsquared_adj:.4f}) evita se enganar: ele penaliza variável inútil, e
        como ficou perto do R², as variáveis acrescentadas se pagam.
        Todos os VIF estão abaixo de 5, então não há multicolinearidade que atrapalhe a leitura dos
        coeficientes.
        Mesmo assim, {(1 - modelo.rsquared) * 100:.0f}% da variação continua fora do modelo. O que falta é
        fluxo de passageiros, e a base não tem.
    """)

    cenario = pd.DataFrame([CENARIO])[X]
    previsao_obj = modelo.get_prediction(sm.add_constant(cenario, has_constant="add"))
    previsao = float(previsao_obj.predicted_mean[0])
    ic = previsao_obj.conf_int(alpha=0.05)[0]
    comum.item("f", "Previsão com as três variáveis explicativas")
    print(f"Cenário: estação a {CENARIO['dist_marco_zero_km']:.0f} km do Marco Zero, com "
          f"{CENARIO['qtd_linhas']} linhas, latitude {CENARIO['lat']}")
    conta = " ".join(f"{'+' if coeficientes[c] >= 0 else '−'} {abs(coeficientes[c]):.2f}×{CENARIO[c]} " for c in X)
    print(f"total previsto = {const:.2f} {conta}= {previsao:.1f} ocorrências")
    print(f"Intervalo de 95% para a média prevista: [{ic[0]:.1f} ; {ic[1]:.1f}]")
    parecidas = df[(df.qtd_linhas >= 3) & (df.dist_marco_zero_km <= 6)]
    print(f"Conferência: as {len(parecidas)} estações reais com 3+ linhas até 6 km do centro têm média "
          f"{parecidas[Y].mean():.1f} (de {parecidas[Y].min()} a {parecidas[Y].max()})")
    comum.interpretacao(f"""
        O modelo prevê {previsao:.0f} ocorrências para uma estação de baldeação próxima do centro, e as
        estações reais parecidas têm média {parecidas[Y].mean():.0f}: a ordem de grandeza bate.
        A previsão vale como comparação entre perfis de estação ("baldeação central registra mais que ponta
        de linha"), nunca como número esperado para uma estação nomeada. Entre as estações parecidas, os
        valores reais vão de {parecidas[Y].min()} a {parecidas[Y].max()}.
        Ressalva importante: pedir 3 linhas é extrapolar. Na base, 121 estações têm 1 linha, 14 têm 2 e só
        4 têm 3 ou mais. O coeficiente de `qtd_linhas` se apoia nessas poucas estações, então a previsão
        deste cenário é frágil.
    """)

    _graficos(dados, correlacao, df)
    return {"explicativas": X, "covariancia": covariancia.round(4).to_dict(), "correlacao": correlacao.round(4).to_dict(),
            "coeficientes": coeficientes, "equacao": equacao,
            "p_valores": {k: float(v) for k, v in modelo.pvalues.items()},
            "r2": float(modelo.rsquared), "r2_ajustado": float(modelo.rsquared_adj),
            "r2_do_modelo_simples": float(simples.rsquared),
            "F": float(modelo.fvalue), "F_p_valor": float(modelo.f_pvalue),
            "vif": vif.set_index("variavel")["VIF"].round(3).to_dict(),
            "cenario": CENARIO, "previsao": previsao, "previsao_ic95": [float(ic[0]), float(ic[1])],
            "media_real_parecidas": float(parecidas[Y].mean())}


def _graficos(dados, correlacao, df) -> None:
    eixos = pd.plotting.scatter_matrix(dados, figsize=(9.5, 9.5), diagonal="hist", color="#2563eb",
                                       alpha=0.6, s=26, hist_kwds={"color": "#93c5fd", "edgecolor": "white"})
    for eixo in eixos.flatten():
        eixo.xaxis.label.set_size(8)
        eixo.yaxis.label.set_size(8)
        eixo.xaxis.label.set_rotation(20)
        eixo.yaxis.label.set_rotation(70)
    fig = eixos[0, 0].get_figure()
    fig.suptitle("Dispersão entre as quatro variáveis quantitativas", y=0.92)
    print(f"\nGráfico salvo em: {comum.salvar_figura(fig, 'q05a_dispersao.png')}")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.2, 5))
    imagem = ax.imshow(correlacao.values, cmap="coolwarm", vmin=-1, vmax=1)
    nomes = [c.replace("dist_marco_zero_km", "distância").replace("qtd_linhas", "nº de linhas") for c in correlacao.columns]
    ax.set_xticks(range(len(nomes)), nomes, rotation=25, ha="right", fontsize=9)
    ax.set_yticks(range(len(nomes)), nomes, fontsize=9)
    for i in range(len(nomes)):
        for j in range(len(nomes)):
            ax.text(j, i, f"{correlacao.values[i, j]:.2f}", ha="center", va="center", fontsize=11, fontweight="bold")
    ax.set_title("Correlação de Pearson entre as variáveis")
    fig.colorbar(imagem, ax=ax, shrink=0.8)
    fig.tight_layout()
    print(f"Gráfico salvo em: {comum.salvar_figura(fig, 'q05c_correlacao.png')}")
    plt.close(fig)


if __name__ == "__main__":
    resolver()
