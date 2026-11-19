# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# Questão 03 - Teste de hipótese para a média (teste z, desvio padrão de referência conhecido)
# a) média menor que a de referência, alfa = 6%, n = 20 | b) média maior, alfa = 9%, n = 25

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

df = pd.read_csv("ocorrencias_estacoes_2026.csv")
x = df["total"]

mu0 = x.mean()
sigma = x.std(ddof=0)  # desvio padrão populacional, como pede o enunciado

print("QUESTÃO 03")
print("Média de referência (mu0):", round(mu0, 2))
print("Desvio padrão de referência (sigma):", round(sigma, 2))


def teste_z(amostra, alfa, lado):
    n = len(amostra)
    media_amostral = amostra.mean()
    erro_padrao = sigma / np.sqrt(n)
    z = (media_amostral - mu0) / erro_padrao
    if lado == "menor":
        critico = stats.norm.ppf(alfa)
        p_valor = stats.norm.cdf(z)
        rejeita = z < critico
    else:
        critico = stats.norm.ppf(1 - alfa)
        p_valor = stats.norm.sf(z)
        rejeita = z > critico
    return n, media_amostral, erro_padrao, z, critico, p_valor, rejeita


def mostrar(n, media_amostral, erro_padrao, z, critico, p_valor, rejeita, alfa):
    print("n =", n)
    print("Média amostral:", round(media_amostral, 2))
    print("Erro padrão:", round(erro_padrao, 2))
    print("z =", round(z, 4))
    print("alfa =", alfa, "| z crítico =", round(critico, 4))
    print("p-valor =", round(p_valor, 4), "(", p_valor, ")")
    print("Decisão:", "REJEITA H0" if rejeita else "NÃO REJEITA H0")


# a) H0: mu = mu0 contra H1: mu < mu0 (20 estações mais distantes do Marco Zero)
longe = df.nlargest(20, "dist_marco_zero_km")
print("\na) alfa = 6%, n = 20, H1: mu <", round(mu0, 2))
print("Amostra: as 20 estações mais distantes (de", round(longe["dist_marco_zero_km"].min(), 1),
      "km a", round(longe["dist_marco_zero_km"].max(), 1), "km)")
res_a = teste_z(longe["total"], 0.06, "menor")
mostrar(*res_a, 0.06)
print("z crítico a 5% =", round(stats.norm.ppf(0.05), 3))
print("Só deixaria de rejeitar H0 com nível abaixo de", round(res_a[5] * 100, 1), "%")
print("Interpretação: a média das 20 estações mais distantes (", round(res_a[1], 1), ") é menor que a da rede (",
      round(mu0, 1), ") e H0 é rejeitada, mas por pouco.")
print("Esse grupo foi escolhido pela distância, não sorteado, então a conclusão vale só para ele.")

# b) H0: mu = mu0 contra H1: mu > mu0 (25 estações mais próximas do Marco Zero)
perto = df.nsmallest(25, "dist_marco_zero_km")
print("\nb) alfa = 9%, n = 25, H1: mu >", round(mu0, 2))
print("Amostra: as 25 estações mais próximas (de", round(perto["dist_marco_zero_km"].min(), 1),
      "km a", round(perto["dist_marco_zero_km"].max(), 1), "km)")
res_b = teste_z(perto["total"], 0.09, "maior")
mostrar(*res_b, 0.09)
print("Interpretação: a média das 25 estações mais centrais (", round(res_b[1], 1),
      ") é mais que o dobro da referência e H0 é rejeitada com folga.")

# checagem com amostras sorteadas (semente fixa)
print("\nChecagem com amostras sorteadas (sementes 42 e 43)")
sorteio_a = df.sample(20, random_state=42)["total"]
sorteio_b = df.sample(25, random_state=43)["total"]
s_a = teste_z(sorteio_a, 0.06, "menor")
s_b = teste_z(sorteio_b, 0.09, "maior")
for nome, s in (("a) n = 20, alfa = 6%", s_a), ("b) n = 25, alfa = 9%", s_b)):
    print(nome, "| média sorteada =", round(s[1], 1), "| z =", round(s[3], 3), "| crítico =", round(s[4], 3),
          "| p-valor =", round(s[5], 4), "|", "REJEITA H0" if s[6] else "NÃO REJEITA H0")
print("Interpretação: com amostras sorteadas a média fica perto da referência e nenhuma das duas rejeita H0.")

# gráfico: curva normal padrão com a região de rejeição, z observado e z crítico
fig, eixos = plt.subplots(1, 2, figsize=(12, 4.2))
grade = np.linspace(-6.5, 6.5, 500)
dados = [(res_a, 0.06, "menor", "a) 20 mais distantes · α = 6%"), (res_b, 0.09, "maior", "b) 25 mais próximas · α = 9%")]
for ax, (res, alfa, lado, titulo) in zip(eixos, dados):
    z, critico = res[3], res[4]
    ax.plot(grade, stats.norm.pdf(grade), color="black")
    if lado == "menor":
        ax.fill_between(grade, stats.norm.pdf(grade), where=grade < critico, color="#c2410c", alpha=0.45,
                        label="região de rejeição (α = " + str(round(alfa * 100)) + "%)")
    else:
        ax.fill_between(grade, stats.norm.pdf(grade), where=grade > critico, color="#c2410c", alpha=0.45,
                        label="região de rejeição (α = " + str(round(alfa * 100)) + "%)")
    ax.axvline(z, color="green", lw=2, label="z observado = " + str(round(z, 2)))
    ax.axvline(critico, color="black", ls="--", label="z crítico = " + str(round(critico, 2)))
    ax.set_title(titulo)
    ax.set_xlabel("z")
    ax.set_ylabel("Densidade")
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("q03_testes_hipotese.png", dpi=150)
plt.show()
