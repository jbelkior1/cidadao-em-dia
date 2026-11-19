# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# Questão 04 - Análise bivariada entre duas variáveis quantitativas
# X = dist_marco_zero_km (distância até o Marco Zero) e Y = total (ocorrências no entorno da estação)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan

df = pd.read_csv("ocorrencias_estacoes_2026.csv")
x = df["dist_marco_zero_km"]
y = df["total"]

print("QUESTÃO 04")
print("n =", len(df), "estações")

# a) gráfico de dispersão (a reta de regressão da letra d entra no mesmo gráfico)
modelo = sm.OLS(y, sm.add_constant(x)).fit()
a = modelo.params.iloc[0]
b = modelo.params.iloc[1]

perto = y[x <= 5]
longe = y[x > 20]
print("\na) Gráfico de dispersão: arquivo q04a_dispersao.png")
print("Entre 0 e 5 km os valores vão de", perto.min(), "a", perto.max())
print("Acima de 20 km,", int((longe < 300).sum()), "das", len(longe), "estações ficam abaixo de 300 (a maior chega a", longe.max(), ")")
print("Interpretação: quanto mais longe do centro, menos ocorrências, mas a relação é frouxa e abre em leque perto do centro.")

fig, ax = plt.subplots(figsize=(8, 5.2))
ax.scatter(x, y, color="#2563eb", alpha=0.65, label="Estação")
grade = np.linspace(x.min(), x.max(), 100)
ax.plot(grade, a + b * grade, color="#c2410c", lw=2.5,
        label="Regressão: y = " + str(round(a, 1)) + " - " + str(round(abs(b), 1)) + "x   (R² = " + str(round(modelo.rsquared, 3)) + ")")
for _, linha in df.nlargest(3, "total").iterrows():
    ax.annotate(linha["estacao"], (linha["dist_marco_zero_km"], linha["total"]), fontsize=8, xytext=(6, 2), textcoords="offset points")
ax.set_title("Ocorrências no entorno da estação × distância até o Marco Zero")
ax.set_xlabel("Distância até o Marco Zero (km)")
ax.set_ylabel("Ocorrências no entorno da estação (jan–set/2026)")
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig("q04a_dispersao.png", dpi=150)
plt.show()

# b) covariância e correlação de Pearson
cov = np.cov(x, y, ddof=1)[0, 1]
r, p_r = stats.pearsonr(x, y)
print("\nb) Covariância e correlação")
print("Covariância amostral:", round(cov, 2))
print("Correlação de Pearson r:", round(r, 4))
print("p-valor da correlação:", p_r)
print("r² =", round(r ** 2, 4))
print("Interpretação: covariância negativa mostra só o sentido; r de", round(r, 3), "indica relação negativa moderada.")

# c) gráfico da correlação (mapa de calor do par)
matriz = np.array([[1.0, r], [r, 1.0]])
fig, ax = plt.subplots(figsize=(4.6, 4))
imagem = ax.imshow(matriz, cmap="coolwarm", vmin=-1, vmax=1)
nomes = ["Distância (km)", "Ocorrências"]
ax.set_xticks([0, 1])
ax.set_xticklabels(nomes)
ax.set_yticks([0, 1])
ax.set_yticklabels(nomes)
for i in range(2):
    for j in range(2):
        ax.text(j, i, format(matriz[i, j], ".2f").replace(".", ","), ha="center", va="center", fontsize=13, fontweight="bold")
ax.set_title("Correlação de Pearson")
ax.set_xlabel("Variável")
ax.set_ylabel("Variável")
fig.colorbar(imagem, ax=ax, shrink=0.8)
plt.tight_layout()
plt.savefig("q04c_correlacao.png", dpi=150)
plt.show()
print("\nc) Mapa de calor: arquivo q04c_correlacao.png (diagonal 1,00 e", round(r, 2), "fora dela)")
print("Interpretação: a cor fora da diagonal fica do lado negativo da escala (r =", round(r, 3), "),")
print("ou seja, relação negativa moderada: mais longe do centro, menos registros. A diagonal é 1 (a variável com ela mesma).")

# d) reta da regressão e equação
print("\nd) Regressão linear simples")
print("Equação: total =", round(a, 2), "-", round(abs(b), 2), "x distância_km")
print("Intercepto a =", round(a, 4), "| erro padrão =", round(modelo.bse.iloc[0], 4), "| p-valor =", modelo.pvalues.iloc[0])
print("Inclinação b =", round(b, 4), "| erro padrão =", round(modelo.bse.iloc[1], 4), "| p-valor =", modelo.pvalues.iloc[1])
print("Distância mínima da base:", round(x.min(), 2), "km")
print("Interpretação: cada km a mais do Marco Zero reduz em média", round(abs(b), 1), "ocorrência no entorno.")

# e) R² e Teste F
print("\ne) Adequação do modelo")
print("R² =", round(modelo.rsquared, 4), "| R² ajustado =", round(modelo.rsquared_adj, 4))
print("Teste F: F(" + str(int(modelo.df_model)) + ",", str(int(modelo.df_resid)) + ") =", round(modelo.fvalue, 3),
      "| p-valor =", modelo.f_pvalue)
print("A distância explica", round(modelo.rsquared * 100, 1), "% da variação; sobram", round((1 - modelo.rsquared) * 100, 1), "%")

# pressupostos: Breusch-Pagan e erro padrão robusto (HC3)
_, bp_p, _, _ = het_breuschpagan(modelo.resid, modelo.model.exog)
assimetria = stats.skew(modelo.resid)
robusto = modelo.get_robustcov_results(cov_type="HC3")
print("Breusch-Pagan p-valor =", round(bp_p, 4), "| assimetria dos resíduos =", round(assimetria, 2))
print("p-valores com erro padrão robusto (HC3): const =", robusto.pvalues[0], "| distância =", robusto.pvalues[1])
print("Interpretação: o modelo é significativo (F), mas o R² é baixo; Breusch-Pagan confirma o leque, então os p-valores são aproximados.")

# f) previsão para uma estação a 5 km
novo = sm.add_constant(np.array([[5.0]]), has_constant="add")
pred = modelo.get_prediction(novo)
previsao = pred.predicted_mean[0]
ic = pred.conf_int(alpha=0.05)[0]
faixa = df[(x >= 4) & (x <= 6)]
print("\nf) Previsão para 5 km do Marco Zero")
print("total previsto =", round(a, 2), "-", round(abs(b), 2), "x 5 =", round(previsao, 2), "ocorrências")
print("Intervalo de 95% para a média prevista: [", round(ic[0], 1), ";", round(ic[1], 1), "]")
print("As", len(faixa), "estações entre 4 e 6 km têm média real de", round(faixa["total"].mean(), 1),
      "(de", faixa["total"].min(), "a", faixa["total"].max(), ")")
print("Interpretação: o modelo acerta a ordem de grandeza, mas não serve para prever uma estação isolada.")
