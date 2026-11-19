# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# Questão 05 - Análise multivariada (regressão linear múltipla)
# Resposta: total; explicativas: dist_marco_zero_km, qtd_linhas e lat

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan

df = pd.read_csv("ocorrencias_estacoes_2026.csv")
y = "total"
X = ["dist_marco_zero_km", "qtd_linhas", "lat"]
dados = df[[y] + X]

print("QUESTÃO 05")
print("n =", len(df), "estações")

# a) gráfico de dispersão com as 4 variáveis
nomes = {"total": "Ocorrências\nno entorno",
         "dist_marco_zero_km": "Distância até o\nMarco Zero (km)",
         "qtd_linhas": "Linhas que passam\nna estação",
         "lat": "Latitude\n(sul → norte)"}
dados_graf = dados.rename(columns=nomes)
eixos = pd.plotting.scatter_matrix(dados_graf, figsize=(10, 10), diagonal="hist", alpha=0.6,
                                   color="#2563eb", hist_kwds={"color": "#93c5fd", "edgecolor": "white"})
for eixo in eixos.flatten():
    eixo.xaxis.label.set_size(8)
    eixo.yaxis.label.set_size(8)
    eixo.xaxis.label.set_rotation(0)
    eixo.yaxis.label.set_rotation(90)
    eixo.yaxis.set_label_coords(-0.42, 0.5)
plt.suptitle("Dispersão entre as quatro variáveis quantitativas", y=0.92)
plt.savefig("q05a_dispersao.png", dpi=150, bbox_inches="tight")
plt.show()
print("\na) Gráfico salvo em q05a_dispersao.png")
print("Interpretação: o total cai com a distância e sobe com a quantidade de linhas; a latitude quase não inclina.")

# b) covariância e correlação
cov = dados.cov()
corr = dados.corr()
print("\nb) Matriz de covariância")
print(cov.round(4))
print("\nMatriz de correlação de Pearson")
print(corr.round(4))
print("Interpretação: linhas tem a correlação mais forte com o total e a latitude a mais fraca.")

# c) mapa de calor da correlação
rotulos = ["total", "distância", "nº de linhas", "latitude"]
plt.figure(figsize=(6.5, 5))
plt.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar()
plt.xticks(range(4), rotulos, rotation=25, ha="right")
plt.yticks(range(4), rotulos)
for i in range(4):
    for j in range(4):
        plt.text(j, i, format(corr.values[i, j], ".2f"), ha="center", va="center", fontweight="bold")
plt.title("Correlação de Pearson entre as variáveis")
plt.tight_layout()
plt.savefig("q05c_correlacao.png", dpi=150)
plt.show()
print("\nc) Gráfico salvo em q05c_correlacao.png")
print("Interpretação: a primeira linha do mapa mostra o que acompanha o total de ocorrências.")

# d) regressão linear múltipla
Xc = sm.add_constant(dados[X])
modelo = sm.OLS(dados[y], Xc).fit()
b = modelo.params
print("\nd) Equação da regressão")
print("total =", round(b["const"], 2), "+", round(b["dist_marco_zero_km"], 2), "× dist_marco_zero_km +",
      round(b["qtd_linhas"], 2), "× qtd_linhas +", round(b["lat"], 2), "× lat")
print("Coeficientes:")
print(b.round(4))
print("p-valores:")
for nome in modelo.pvalues.index:
    print(" ", nome, "=", format(modelo.pvalues[nome], ".3e"))
print("Interpretação: cada km a mais do centro reduz o total em cerca de", round(abs(b["dist_marco_zero_km"]), 1),
      "e cada linha a mais soma cerca de", round(b["qtd_linhas"]), "ocorrências; a latitude não é significativa.")

# e) adequação: R², Teste F, VIF e pressupostos
print("\ne) Adequação do modelo")
print("R² =", round(modelo.rsquared, 4))
print("R² ajustado =", round(modelo.rsquared_adj, 4))
print("Teste F: F(", int(modelo.df_model), ",", int(modelo.df_resid), ") =", round(modelo.fvalue, 3),
      "| p-valor =", format(modelo.f_pvalue, ".3e"))
print("VIF:")
for i in range(len(X)):
    print(" ", X[i], "=", round(variance_inflation_factor(Xc.values, i + 1), 3))

simples = sm.OLS(dados[y], sm.add_constant(dados[["dist_marco_zero_km"]])).fit()
sem_lat = sm.OLS(dados[y], sm.add_constant(dados[["dist_marco_zero_km", "qtd_linhas"]])).fit()
print("R² do modelo simples (só distância) =", round(simples.rsquared, 4))
print("R² ajustado só com distância =", round(simples.rsquared_adj, 4))
print("R² ajustado sem a latitude =", round(sem_lat.rsquared_adj, 4))

_, p_bp, _, _ = het_breuschpagan(modelo.resid, modelo.model.exog)
print("Breusch-Pagan p-valor =", round(p_bp, 4))
print("Assimetria dos resíduos =", round(stats.skew(modelo.resid), 2))
robusto = modelo.get_robustcov_results(cov_type="HC3")
print("p-valores robustos (HC3):")
for nome, p in zip(modelo.params.index, robusto.pvalues):
    print(" ", nome, "=", format(p, ".3e"))
print("Interpretação: o Teste F rejeita e o R² subiu com as três variáveis, mas a latitude não ajuda (R² ajustado cai).")
print("A variância dos resíduos não é constante, então usamos o erro robusto como conferência.")

# f) previsão
cenario = pd.DataFrame([{"dist_marco_zero_km": 4.0, "qtd_linhas": 3, "lat": -23.55}])
pred = modelo.get_prediction(sm.add_constant(cenario, has_constant="add"))
valor = pred.predicted_mean[0]
ic = pred.conf_int(alpha=0.05)[0]
print("\nf) Previsão: estação a 4 km do Marco Zero, 3 linhas, latitude -23.55")
print("Total previsto =", round(valor, 1))
print("IC 95% da média prevista: [", round(ic[0], 1), ";", round(ic[1], 1), "]")
parecidas = df[(df["qtd_linhas"] >= 3) & (df["dist_marco_zero_km"] <= 6)]
print("Estações parecidas (3+ linhas, até 6 km):", len(parecidas))
print("Média real delas =", round(parecidas[y].mean(), 1), "(de", parecidas[y].min(), "a", parecidas[y].max(), ")")
print("Interpretação: a média real fica acima do intervalo, então o modelo subestima esse grupo;")
print("além disso só poucas estações têm 3 linhas ou mais, então a previsão é frágil.")
