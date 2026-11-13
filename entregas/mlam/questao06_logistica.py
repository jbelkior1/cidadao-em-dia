"""Questão 06 (2,0) — Regressão logística binária com três variáveis quantitativas.

A resposta vira sim ou não: a estação está entre as de MAIOR número de ocorrências registradas
no entorno? "Maior" é acima da mediana das 139 estações, o que parte a base ao meio e deixa as
duas classes equilibradas.

    a) equação da regressão logística binária;
    b) matriz de confusão e acurácia, interpretadas;
    c) uma classificação com pelo menos 2 variáveis explicativas.

Rodar:  python questao06_logistica.py
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score

import comum

X = comum.EXPLICATIVAS
CENARIOS = [
    {"nome": "Baldeação central (3 linhas, 2 km)", "dist_marco_zero_km": 2.0, "qtd_linhas": 3, "lat": -23.54},
    {"nome": "Ponta de linha (1 linha, 22 km)", "dist_marco_zero_km": 22.0, "qtd_linhas": 1, "lat": -23.48},
]


def resolver(df=None) -> dict:
    df = comum.carregar() if df is None else df
    corte = float(df[comum.RESPOSTA].median())
    y = (df[comum.RESPOSTA] > corte).astype(int)

    comum.titulo("QUESTÃO 06 — Regressão logística binária")
    print(f"Variável resposta criada: alta_ocorrencia = 1 se total > {corte:.0f} (mediana), senão 0")
    print(f"Classes: {int(y.sum())} estações com 1 e {int((1 - y).sum())} com 0, de {len(y)}")
    print(f"Explicativas: {', '.join(X)}")

    modelo = sm.Logit(y, sm.add_constant(df[X])).fit(disp=False)
    coef = {k: float(v) for k, v in modelo.params.items()}
    const = coef["const"]

    comum.item("a", "Equação da regressão logística binária")
    termos = " ".join(f"{'+' if coef[c] >= 0 else '−'} {abs(coef[c]):.4f}×{c} " for c in X)
    print(f"\nlogito(p) = ln(p / (1 − p)) = {const:.4f} {termos}".strip())
    print(f"\np = 1 / (1 + e^(−logito))\n")
    print(modelo.summary2().tables[1].round(4).to_string())
    razoes = np.exp(modelo.params)
    print("\nRazões de chance (odds ratio = e^coeficiente):")
    for c in X:
        print(f"  {c}: {razoes[c]:.4f}")
    print(f"\nPseudo R² (McFadden) = {modelo.prsquared:.4f}  |  LLR p-valor = {modelo.llr_pvalue:.3e}")
    comum.interpretacao(f"""
        Os coeficientes estão na escala do logito, por isso a razão de chance é a leitura prática.
        Distância: razão {razoes['dist_marco_zero_km']:.3f}. Cada quilômetro a mais do centro
        {'reduz' if razoes['dist_marco_zero_km'] < 1 else 'aumenta'} em
        {abs(1 - razoes['dist_marco_zero_km']) * 100:.1f}% a chance de a estação ser de alta ocorrência.
        Quantidade de linhas: razão {razoes['qtd_linhas']:.3f}, mas com p-valor
        {modelo.pvalues['qtd_linhas']:.4f}, acima de 5%, e intervalo de confiança que cruza o 1
        ([{np.exp(modelo.conf_int().loc['qtd_linhas', 0]):.2f} ; {np.exp(modelo.conf_int().loc['qtd_linhas', 1]):.2f}]).
        O efeito aparenta ser grande, mas NÃO é estatisticamente significativo a 5%: não dá para afirmar
        que ele existe na população. A razão é a base: só 4 das 139 estações têm 3 linhas ou mais
        (1 com 3, 2 com 4 e 1 com 5), e 121 têm uma linha só. Com tão poucos casos no alto da escala,
        o coeficiente é instável.
        Só a distância é significativa aqui (p-valor {modelo.pvalues['dist_marco_zero_km']:.4f}).
        A latitude não é significativa (p-valor {modelo.pvalues['lat']:.3f}), como na questão 05: depois da
        distância ao centro, a posição norte-sul não acrescenta. Ficou no modelo porque o enunciado pede
        pelo menos três variáveis quantitativas, e sua presença está registrada aqui como limitação.
        O LLR testa o modelo inteiro contra um modelo só com o intercepto, e rejeita (p-valor
        {modelo.llr_pvalue:.1e}). O pseudo R² de McFadden não se lê como o R² da regressão linear: a
        referência usual é que 0,2 a 0,4 já indica bom ajuste, e aqui ele é {modelo.prsquared:.3f}, abaixo
        dessa faixa. O modelo acerta bem mais que o acaso, mas com três variáveis estruturais só.
    """)

    probabilidade = modelo.predict(sm.add_constant(df[X]))
    previsto = (probabilidade >= 0.5).astype(int)
    mc = confusion_matrix(y, previsto)
    (vn, fp), (fn, vp) = mc
    acuracia = float(accuracy_score(y, previsto))
    maior_classe = max(vn + fp, fn + vp) / len(y)          # piso honesto: acertar sempre a classe maior
    precisao = vp / (vp + fp) if (vp + fp) else 0.0
    revocacao = vp / (vp + fn) if (vp + fn) else 0.0
    auc = float(roc_auc_score(y, probabilidade))

    comum.item("b", "Matriz de confusão e acurácia")
    print(pd.DataFrame(mc, index=["Real: normal (0)", "Real: alta (1)"],
                       columns=["Previsto: normal (0)", "Previsto: alta (1)"]).to_string())
    print(f"\nAcurácia = ({vn} + {vp}) / {len(y)} = {acuracia:.4f}  ({acuracia * 100:.1f}%)")
    print(f"Precisão (dos previstos como alta, quantos eram) = {precisao:.4f}")
    print(f"Revocação (das estações de alta, quantas o modelo pegou) = {revocacao:.4f}")
    print(f"AUC = {auc:.4f}")
    comum.interpretacao(f"""
        O modelo acerta {acuracia * 100:.1f}% das 139 estações. O piso de comparação é a classe
        majoritária: responder sempre "normal" acertaria {maior_classe * 100:.1f}% (as {int(max(vn + fp, fn + vp))}
        estações da classe maior). O modelo ganha {(acuracia - maior_classe) * 100:.1f} pontos percentuais
        sobre esse piso.
        Os erros: {fp} estações previstas como alta que não são (falso positivo) e {fn} estações de alta que
        passaram como normais (falso negativo).
        Para um app que avisa o passageiro, o falso negativo é o erro caro: dizer que está tranquilo onde
        não está. São {fn} casos, {fn / max(1, (fn + vp)) * 100:.0f}% das estações de alta ocorrência.
        O AUC de {auc:.3f} mede a separação das classes sem depender do corte de 0,5.
        Medido na mesma base em que foi ajustado, este número é otimista. Com 139 linhas e 3 variáveis o
        sobreajuste é pequeno, mas a leitura honesta é "o modelo descreve bem esta base", não "vai acertar
        assim numa cidade nova".
    """)

    comum.item("c", "Classificação com as variáveis explicativas")
    classificacoes = []
    for cenario in CENARIOS:
        entrada = pd.DataFrame([{c: cenario[c] for c in X}])
        p = float(modelo.predict(sm.add_constant(entrada, has_constant="add")).iloc[0])
        classe = "ALTA ocorrência" if p >= 0.5 else "ocorrência normal"
        print(f"\n{cenario['nome']}")
        print(f"  entrada: " + ", ".join(f"{c} = {cenario[c]}" for c in X))
        logito = const + sum(coef[c] * cenario[c] for c in X)
        print(f"  logito = {logito:.4f}  →  p = 1 / (1 + e^({-logito:+.4f})) = {p:.4f}")
        print(f"  classificação (corte 0,5): {classe}")
        classificacoes.append({**{c: cenario[c] for c in X}, "nome": cenario["nome"],
                               "probabilidade": p, "classe": classe})
    # quanto do cenário central vem das linhas e quanto da distância: troca uma coisa de cada vez
    base_central = {c: CENARIOS[0][c] for c in X}
    p_1linha = float(modelo.predict(sm.add_constant(pd.DataFrame([{**base_central, "qtd_linhas": 1}]),
                                                    has_constant="add")).iloc[0])
    p_longe = float(modelo.predict(sm.add_constant(pd.DataFrame([{**base_central, "dist_marco_zero_km": 22.0}]),
                                                   has_constant="add")).iloc[0])
    print(f"\nDecomposição do cenário central: com 1 linha a 2 km, p = {p_1linha:.4f}; "
          f"com 3 linhas a 22 km, p = {p_longe:.4f}")
    comum.interpretacao(f"""
        Os dois perfis extremos saem em lados opostos, com probabilidades de
        {classificacoes[0]['probabilidade']:.2f} e {classificacoes[1]['probabilidade']:.2f}: o modelo separa
        bem o que já se esperava.
        Trocando uma variável de cada vez dá para ver de onde vem o {classificacoes[0]['probabilidade']:.2f}:
        com 1 linha só, a 2 km, a probabilidade cai para {p_1linha:.2f}; com 3 linhas, mas a 22 km, cai para
        {p_longe:.2f}. As duas variáveis pesam de forma parecida nesse cenário.
        Ressalva: o peso das linhas é o menos confiável. Só 4 estações da base têm 3 linhas ou mais, e o
        coeficiente de `qtd_linhas` não é significativo a 5%. A parte sólida da conclusão é a da distância.
        No app, isso vira um aviso de atenção no entorno da estação, nunca um rótulo de "estação perigosa".
        O que o modelo prevê é a chance de haver MUITO REGISTRO DE BO num raio de 300 m, e registro
        acompanha movimento de gente. Sem o fluxo de passageiros na base, não dá para transformar isso em
        risco por pessoa.
    """)

    _graficos(df, y, probabilidade, mc, corte)
    return {"corte_mediana": corte, "classes": {"alta": int(y.sum()), "normal": int((1 - y).sum())},
            "coeficientes": coef, "razoes_de_chance": {c: float(razoes[c]) for c in X},
            "p_valores": {k: float(v) for k, v in modelo.pvalues.items()},
            "pseudo_r2_mcfadden": float(modelo.prsquared), "llr_p_valor": float(modelo.llr_pvalue),
            "matriz_confusao": {"vn": int(vn), "fp": int(fp), "fn": int(fn), "vp": int(vp)},
            "acuracia": acuracia, "piso_classe_majoritaria": float(maior_classe), "precisao": float(precisao), "revocacao": float(revocacao), "auc": auc,
            "classificacoes": classificacoes,
            "decomposicao_central": {"p_1_linha_2km": p_1linha, "p_3_linhas_22km": p_longe}}


def _graficos(df, y, probabilidade, mc, corte) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))

    imagem = ax1.imshow(mc, cmap="Blues")
    ax1.set_xticks([0, 1], ["Previsto: normal", "Previsto: alta"])
    ax1.set_yticks([0, 1], ["Real: normal", "Real: alta"])
    for i in range(2):
        for j in range(2):
            ax1.text(j, i, mc[i, j], ha="center", va="center", fontsize=18, fontweight="bold",
                     color="white" if mc[i, j] > mc.max() / 2 else "#1f2937")
    ax1.set_title(f"Matriz de confusão (corte: total > {corte:.0f})")
    fig.colorbar(imagem, ax=ax1, shrink=0.75)

    ax2.scatter(df["dist_marco_zero_km"], probabilidade, c=y, cmap="coolwarm", s=42, alpha=0.75,
                edgecolor="white", linewidth=0.6)
    ax2.axhline(0.5, color="#1f2937", ls="--", lw=1.2, label="corte de classificação (0,5)")
    ax2.set_xlabel(comum.nome("dist_marco_zero_km"))
    ax2.set_ylabel("Probabilidade prevista de alta ocorrência")
    ax2.set_title("Probabilidade prevista por estação\n(cor = classe real)")
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.2)

    fig.tight_layout()
    print(f"\nGráfico salvo em: {comum.salvar_figura(fig, 'q06_logistica.png')}")
    plt.close(fig)


if __name__ == "__main__":
    resolver()
