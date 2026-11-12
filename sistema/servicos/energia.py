"""Minha conta de luz: quanto do consumo entra no desconto da Tarifa Social.

Regra usada (Aneel, lida em 12/11/2026; ver pesquisa/dados_tarifa_social.json):
desconto de 100% no consumo de até 80 kWh por mês, nas contas emitidas a
partir de 5 de julho de 2025; o que passa de 80 kWh não tem desconto.

O valor em reais é uma ESTIMATIVA feita com o preço médio da própria conta da
pessoa (valor da conta dividido pelo consumo). Impostos e iluminação pública
continuam cobrados, então o desconto real é menor.

Esta é a parte que a entrega da SERS vai ampliar: dados de consumo com origem
e a comparação de duas alternativas, uma delas renovável.
"""

EM_CONFERENCIA = True
FAIXA_KWH = 80
FONTE = "https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social"
CONSULTADO_EM = "2026-11-12"


def reais(valor: float, casas: int = 2) -> str:
    return "R$ " + f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def por_kwh(valor: float) -> str:
    """Preço por kWh com 3 casas, para a conta do desconto fechar na tela."""
    return reais(valor, 3) + " por kWh"


def calcular(kwh: float, valor_da_conta: float | None = None) -> dict:
    com_desconto = min(kwh, FAIXA_KWH)
    resultado = {"kwh": kwh, "kwh_com_desconto": com_desconto, "kwh_cobrados": max(kwh - FAIXA_KWH, 0),
                 "preco_medio": None, "desconto_mes": None, "desconto_ano": None}
    if valor_da_conta and kwh > 0:
        preco = valor_da_conta / kwh
        resultado["preco_medio"] = round(preco, 4)
        resultado["desconto_mes"] = round(com_desconto * preco, 2)
        resultado["desconto_ano"] = round(com_desconto * preco * 12, 2)
    return resultado
