# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# Questão 02 - Probabilidade com distribuição normal
# Variável escolhida: total (ocorrências registradas a até 300 m de cada estação)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("ocorrencias_estacoes_2026.csv")
x = df["total"]

media = x.mean()
mediana = x.median()
desvio = x.std(ddof=0)  # desvio populacional (usamos as 139 estações)

print("QUESTÃO 02")
print("n =", len(x))
print("Média:", round(media, 2))
print("Mediana:", round(mediana, 2))
print("Desvio padrão populacional:", round(desvio, 2))


def classificar(p):
    if p == 0:
        return "evento impossível"
    if p == 1:
        return "evento certo"
    if p < 0.5:
        return "evento pouco provável (menos de 50%)"
    if p > 0.5:
        return "evento provável (mais de 50%)"
    return "evento equiprovável (exatamente 50%)"


# a) P(X < média)
z_a = (media - media) / desvio
p_a = stats.norm.cdf(media, loc=media, scale=desvio)
print("\na) P(X < média)")
print("z =", round(z_a, 4))
print("P(X <", round(media, 2), ") =", round(p_a, 4))
print("Classificação:", classificar(p_a))

# comparando com o dado real
abaixo_real = (x < media).mean()
negativos = stats.norm.cdf(0, loc=media, scale=desvio)
print("No dado real,", round(abaixo_real * 100, 1), "% das estações ficam abaixo da média")
print("A normal coloca", round(negativos * 100, 1), "% da probabilidade abaixo de zero")

# b) P(X > mediana)
z_b = (mediana - media) / desvio
p_b = stats.norm.sf(mediana, loc=media, scale=desvio)
print("\nb) P(X > mediana)")
print("z =", round(z_b, 4))
print("P(X >", round(mediana, 2), ") =", round(p_b, 4))
print("Classificação:", classificar(p_b))

print("\nInterpretação: a média fica acima da mediana porque poucas estações têm muitos registros.")
print("Por isso a normal não descreve bem essa variável (no dado real, P(X > mediana) seria 0,5).")

# gráfico: dado real x normal e as áreas das letras a e b
grade = np.linspace(max(0, media - 4 * desvio), media + 4 * desvio, 400)
curva = stats.norm.pdf(grade, loc=media, scale=desvio)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
ax1.hist(x, bins=20, density=True, color="#9ecae1", edgecolor="white", label="Distribuição real")
ax1.plot(grade, curva, color="#c2410c", lw=2, label="Normal assumida")
ax1.axvline(media, color="black", ls="--", label="Média = " + str(round(media)))
ax1.axvline(mediana, color="green", ls=":", lw=2, label="Mediana = " + str(round(mediana)))
ax1.set_title("Ocorrências por estação: dado real e modelo normal")
ax1.set_xlabel("Ocorrências no entorno da estação (jan-set/2026)")
ax1.set_ylabel("Densidade")
ax1.legend(fontsize=8)

ax2.plot(grade, curva, color="black")
ax2.fill_between(grade, curva, where=grade < media, color="#93c5fd", label="a) P(X < média) = " + str(round(p_a, 4)))
ax2.fill_between(grade, curva, where=grade > mediana, color="#c2410c", alpha=0.45, label="b) P(X > mediana) = " + str(round(p_b, 4)))
ax2.set_title("Áreas das letras a) e b)")
ax2.set_xlabel("Ocorrências no entorno da estação (jan-set/2026)")
ax2.set_ylabel("Densidade")
ax2.legend(fontsize=8)

plt.tight_layout()
plt.savefig("q02_probabilidade.png", dpi=150)
plt.show()
