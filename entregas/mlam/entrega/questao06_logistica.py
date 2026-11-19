# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# Questão 06 - Regressão logística binária
# Resposta: 1 se a estação tem total acima da mediana (alta ocorrência), 0 caso contrário

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score

df = pd.read_csv("ocorrencias_estacoes_2026.csv")
X = ["dist_marco_zero_km", "qtd_linhas", "lat"]

corte = df["total"].median()
y = (df["total"] > corte).astype(int)

print("QUESTÃO 06")
print("Corte (mediana do total) =", round(corte))
print("Classes: alta =", int(y.sum()), "| normal =", int((1 - y).sum()), "| n =", len(y))

# a) modelo e equação
Xc = sm.add_constant(df[X])
modelo = sm.Logit(y, Xc).fit(disp=False)
b = modelo.params
print("\na) Equação logística")
eq = "logito(p) = " + str(round(b["const"], 4))
for v in X:
    sinal = " + " if b[v] >= 0 else " - "
    eq += sinal + str(round(abs(b[v]), 4)) + " × " + v
print(eq)
print("p = 1 / (1 + e^(-logito))")
print("Coeficientes:")
print(b.round(4))
print("p-valores:")
for nome in modelo.pvalues.index:
    print(" ", nome, "=", round(modelo.pvalues[nome], 4))
razoes = np.exp(b)
print("Razões de chance:")
for c in X:
    print(" ", c, "=", round(razoes[c], 4))
print("Pseudo R² (McFadden) =", round(modelo.prsquared, 4))
print("LLR p-valor =", format(modelo.llr_pvalue, ".3e"))
print("Interpretação: cada km a mais do centro reduz a chance de alta ocorrência (razão", round(razoes["dist_marco_zero_km"], 3), ").")
print("Só a distância é significativa; linhas e latitude têm p-valor acima de 5%.")

# b) matriz de confusão
prob = modelo.predict(Xc)
previsto = (prob >= 0.5).astype(int)
mc = confusion_matrix(y, previsto)
vn, fp, fn, vp = mc[0, 0], mc[0, 1], mc[1, 0], mc[1, 1]
acuracia = accuracy_score(y, previsto)
piso = max(vn + fp, fn + vp) / len(y)
print("\nb) Matriz de confusão")
print(pd.DataFrame(mc, index=["Real: normal (0)", "Real: alta (1)"],
                   columns=["Previsto: normal (0)", "Previsto: alta (1)"]))
print("Acurácia =", round(acuracia, 4))
print("Piso (sempre a classe maior) =", round(piso, 4))
print("Precisão =", round(vp / (vp + fp), 4))
print("Revocação =", round(vp / (vp + fn), 4))
print("AUC =", round(roc_auc_score(y, prob), 4))
print("Interpretação: o modelo acerta mais que o piso da classe majoritária; o número é medido na própria base, então é otimista.")

# gráfico: matriz de confusão e probabilidade por distância
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))
im = ax1.imshow(mc, cmap="Blues")
ax1.set_xticks([0, 1], ["Previsto: normal", "Previsto: alta"])
ax1.set_yticks([0, 1], ["Real: normal", "Real: alta"])
for i in range(2):
    for j in range(2):
        ax1.text(j, i, mc[i, j], ha="center", va="center", fontsize=18, fontweight="bold",
                 color="white" if mc[i, j] > mc.max() / 2 else "black")
ax1.set_title("Matriz de confusão (corte: total > " + str(round(corte)) + ")")
fig.colorbar(im, ax=ax1, shrink=0.75)

ax2.scatter(df["dist_marco_zero_km"][y == 0], prob[y == 0], color="#3b4cc0", alpha=0.75, label="classe real: ocorrência normal")
ax2.scatter(df["dist_marco_zero_km"][y == 1], prob[y == 1], color="#b40426", alpha=0.75, label="classe real: alta ocorrência")
ax2.axhline(0.5, color="black", ls="--", label="corte de classificação (0,5)")
ax2.set_title("Probabilidade prevista por estação\n(cor = classe real, ver legenda)")
ax2.set_xlabel("Distância até o Marco Zero (km)")
ax2.set_ylabel("Probabilidade prevista de alta ocorrência")
ax2.legend(fontsize=8)
plt.tight_layout()
plt.savefig("q06_logistica.png", dpi=150)
plt.show()

# c) classificação de dois perfis
cenarios = [("Baldeação central (3 linhas, 2 km)", 2.0, 3, -23.54),
            ("Ponta de linha (1 linha, 22 km)", 22.0, 1, -23.48)]


def prever(dist, linhas, lat):
    logito = b["const"] + b["dist_marco_zero_km"] * dist + b["qtd_linhas"] * linhas + b["lat"] * lat
    return logito, 1 / (1 + np.exp(-logito))


print("\nc) Classificações de exemplo")
for nome, dist, linhas, lat in cenarios:
    logito, p = prever(dist, linhas, lat)
    classe = "ALTA ocorrência" if p >= 0.5 else "ocorrência normal"
    print(nome, "-> logito =", round(logito, 4), "| p =", round(p, 4), "|", classe)

p1 = prever(2.0, 1, -23.54)[1]
p2 = prever(22.0, 3, -23.54)[1]
print("Decomposição do cenário central: com 1 linha a 2 km, p =", round(p1, 4),
      "| com 3 linhas a 22 km, p =", round(p2, 4))
print("Interpretação: os dois perfis ficam em lados opostos; trocando só as linhas ou só a distância a probabilidade cai.")
print("O peso das linhas é o menos confiável, pois poucas estações têm 3 linhas ou mais.")
