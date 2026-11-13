# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Peças comuns às questões 02 a 06: leitura da base, variáveis escolhidas e saída dos resultados.

Base: uma linha por estação de trem ou metrô de São Paulo, com a contagem de ocorrências
registradas pela SSP-SP num raio de 300 m entre janeiro e setembro de 2026 (ver dados/LEIA-ME.md).

Escolha das variáveis (vale para todas as questões):

- Variável de estudo (resposta): `total`, o número de ocorrências registradas no entorno da estação.
- Variáveis explicativas: `dist_marco_zero_km`, `qtd_linhas` e `lat`. São características da
  estação, conhecidas antes de qualquer ocorrência.
- O que NÃO entra como explicativa: `roubo`, `furto`, `outros`, `madrugada`, `manha`, `tarde`,
  `noite` e `sem_faixa`. Cada um desses dois grupos soma exatamente `total` (conferido no código
  abaixo), então usá-los seria prever a variável com ela mesma.
- `celular` está vazia de propósito: a planilha da SSP-SP não permite identificar o aparelho
  (ver LEIA-ME). A coluna fica no arquivo para deixar essa limitação registrada.
"""
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
BASE = PASTA / "dados" / "ocorrencias_estacoes_2026.csv"
SAIDAS = PASTA / "saidas"

# O enunciado pede nome completo e RM de todos os integrantes em todos os arquivos.
# Preencha aqui uma vez: o relatório PDF (questão 07) lê esta lista.
INTEGRANTES = [
    ("João Vitor Belchior Domingos Leite", "572478"),
    ("João Pedro Pereira Teixeira", "569937"),
    ("Thiago de Oliveira Coelho Souza", "568783"),
]

RESPOSTA = "total"
EXPLICATIVAS = ["dist_marco_zero_km", "qtd_linhas", "lat"]

NOMES = {
    "total": "Ocorrências no entorno da estação (jan–set/2026)",
    "dist_marco_zero_km": "Distância até o Marco Zero (km)",
    "qtd_linhas": "Linhas que passam na estação",
    "lat": "Latitude da estação (sul → norte)",
    "noite": "Ocorrências à noite",
    "roubo": "Roubos",
    "furto": "Furtos",
}

PARTES = ["roubo", "furto", "outros"]
FAIXAS = ["madrugada", "manha", "tarde", "noite", "sem_faixa"]


def carregar() -> pd.DataFrame:
    """Lê a base e confere o que o resto das análises assume sobre ela."""
    df = pd.read_csv(BASE)
    assert len(df) == 139, f"esperava 139 estações, vieram {len(df)}"
    assert not df[[RESPOSTA, *EXPLICATIVAS]].isna().any().any(), "há vazio nas variáveis usadas"
    assert (df[PARTES].sum(axis=1) == df[RESPOSTA]).all(), "roubo+furto+outros deveria dar total"
    assert (df[FAIXAS].sum(axis=1) == df[RESPOSTA]).all(), "as faixas de horário deveriam somar total"
    return df


def nome(coluna: str) -> str:
    return NOMES.get(coluna, coluna)


def salvar_figura(fig, arquivo: str) -> Path:
    SAIDAS.mkdir(exist_ok=True)
    caminho = SAIDAS / arquivo
    fig.savefig(caminho, dpi=150, bbox_inches="tight")
    return caminho


def titulo(texto: str) -> None:
    print(f"\n{'=' * 78}\n{texto}\n{'=' * 78}")


def item(letra: str, texto: str) -> None:
    print(f"\n--- {letra}) {texto}")


def interpretacao(texto: str) -> None:
    """Escreve a leitura do resultado em uma ou mais linhas, com margem."""
    print("\nInterpretação:")
    for linha in texto.strip().splitlines():
        print(f"  {linha.strip()}")


def checar_pressupostos(modelo) -> dict:
    """Checagem dos pressupostos da regressão linear (OLS) usada nas questões 04 e 05.

    Breusch-Pagan testa se a variância dos resíduos muda com as explicativas (heterocedasticidade);
    p-valor baixo quer dizer que muda, e aí o Teste F e os p-valores da OLS ficam aproximados.
    Os p-valores com erro padrão robusto (HC3) servem de conferência: valem mesmo com o leque.
    """
    from scipy import stats
    from statsmodels.stats.diagnostic import het_breuschpagan

    _, bp_p, _, _ = het_breuschpagan(modelo.resid, modelo.model.exog)
    robusto = modelo.get_robustcov_results(cov_type="HC3")
    nomes = list(modelo.params.index)
    print(f"Pressupostos: Breusch-Pagan p-valor = {bp_p:.4f} | assimetria dos resíduos = {stats.skew(modelo.resid):.2f}")
    print("p-valores com erro padrão robusto (HC3): "
          + " | ".join(f"{n} = {p:.3e}" for n, p in zip(nomes, robusto.pvalues)))
    return {"breusch_pagan_p": float(bp_p), "assimetria_residuos": float(stats.skew(modelo.resid)),
            "p_robusto": {n: float(p) for n, p in zip(nomes, robusto.pvalues)}}


def classificar_probabilidade(p: float) -> str:
    """Classificação do evento pelo resultado probabilístico."""
    if p == 0:
        return "evento impossível"
    if p == 1:
        return "evento certo"
    if p < 0.5:
        return "evento pouco provável (menos de 50%)"
    if p > 0.5:
        return "evento provável (mais de 50%)"
    return "evento equiprovável (exatamente 50%)"
