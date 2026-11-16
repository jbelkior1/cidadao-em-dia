"""Vaga da SERS: a mesma viagem de carro, de ônibus a diesel e de trem ou metrô elétrico.

Os números vêm de pesquisa/energia_modos.json (levantados em fontes oficiais em
12/11/2026), lidos pela chave. Nada fica escrito à mão aqui: se a equipe corrigir
um valor na pesquisa, a tela muda junto.

Contas (por pessoa, para a distância do trajeto):
- trilho: km × kWh por passageiro-km do Metrô; CO2 = kWh × fator do SIN;
- carro: litros = km ÷ km/L; CO2 entre a fração fóssil (gasolina com 22% de etanol)
  e o litro inteiro; energia = litros × 32,2 MJ/L; custo = só combustível;
- ônibus: CO2 pelo indicador de 79 g por passageiro-km publicado pelo Metrô,
  porque a lotação média do ônibus não tem fonte oficial.

É estimativa a partir de médias oficiais, não medição da viagem de ninguém.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parents[2] / "pesquisa" / "energia_modos.json"
MJ_POR_LITRO_GASOLINA = 32.2          # 0,770 tep/m³ × 41,87 GJ/tep (BEN), conta da pesquisa
FRACAO_FOSSIL_GASOLINA_C = 0.78       # ensaio do INMETRO com 22% de etanol; teor atual do posto a confirmar
ROTULO = "Estimativa a partir de médias oficiais, não medição da sua viagem."


@lru_cache(maxsize=1)
def _pesquisa() -> dict:
    dados = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    return {"consultado_em": dados.get("consultado_em", ""), "itens": {i["chave"]: i for i in dados["itens"]}}


def _v(chave: str) -> float:
    valor = _pesquisa()["itens"][chave]["valor"]
    if valor is None:
        raise ValueError(f"{chave} não tem valor na pesquisa")
    return float(valor)


def _fonte(chave: str) -> str:
    return _pesquisa()["itens"][chave]["fonte"]


# nome curto de cada fonte, para mostrar ao lado do link (o link vem do JSON)
NOMES_DAS_FONTES = {
    "fator_emissao_sin": "MCTI, fator de emissão da eletricidade (SIN)",
    "renovaveis_matriz_eletrica": "EPE, Balanço Energético Nacional 2026",
    "metro_sp_energia_por_passageiro_km": "Metrô de São Paulo, Relatório Integrado 2025",
    "comparativo_metro_onibus_sp_gco2e_pkm": "Metrô de São Paulo, Relatório Integrado 2025",
    "carro_consumo_hb20_sense_gasolina": "INMETRO, PBE Veicular 2026",
    "fator_emissao_gasolina_automotiva": "Ministério dos Transportes, inventário de emissões",
    "preco_gasolina_sp_capital": "ANP, preços semanais de combustíveis",
    "tarifa_metro_trem": "Agência SP, tarifa de trem e metrô",
    "tarifa_onibus_sptrans": "SPTrans, tarifas",
}
TIPOS = {"oficial": "dado oficial", "calculado": "calculado pela equipe", "estimativa": "estimativa"}


def _ano(chave: str) -> str:
    texto = str(_pesquisa()["itens"][chave].get("ano_referencia", ""))
    faixa = re.search(r"\d{4}\s*-\s*(\d{4})", texto)         # "2004-2024": vale o último ano da série
    achado = faixa or re.search(r"\d{4}", texto)
    return achado.group(1 if faixa else 0) if achado else ""


def _tipo(chave: str) -> str:
    """Dado oficial (confiança alta no JSON), calculado pela equipe (a unidade diz) ou estimativa (o resto)."""
    item = _pesquisa()["itens"][chave]
    if "calculado" in str(item.get("unidade", "")).lower():
        return "calculado"
    return "oficial" if item.get("confianca") == "alta" else "estimativa"


def _premissa(chave: str, texto: str, no_cartao: bool = False) -> dict:
    tipo, ano = _tipo(chave), _ano(chave)
    return {"chave": chave, "texto": texto, "tipo": tipo, "ano": ano, "no_cartao": no_cartao,
            "rotulo": f"{TIPOS[tipo]}{', ' + ano if ano else ''}"}


def _br(numero: float) -> str:
    return f"{numero:g}".replace(".", ",")


def mensal(km: float, viagens: int) -> list[dict]:
    """As três alternativas no mesmo período (um mês de trabalho, ida e volta).

    Multiplica os valores exatos da viagem e só arredonda no fim: somar viagens já arredondadas
    deixava o mês com até 0,4% de diferença para quem refaz a conta à mão (1,08 kWh x 44 = 47,52,
    quando 15 km x 0,0717 kWh x 44 = 47,32).
    """
    km = round(float(km), 1)
    trilho_kwh = km * _v("metro_sp_energia_por_passageiro_km")
    litros = km / _v("carro_consumo_hb20_sense_gasolina")
    fator_gasolina = _v("fator_emissao_gasolina_automotiva")
    return [
        {"modo": "Trem ou metrô", "renovavel": True, "energia_kwh": round(trilho_kwh * viagens, 1),
         "co2_kg": round(trilho_kwh * _v("fator_emissao_sin") * viagens, 1), "co2_kg_max": None,
         "custo_rs": round(_v("tarifa_metro_trem") * viagens, 2), "custo_tipo": "tarifa"},
        {"modo": "Ônibus a diesel", "renovavel": False, "energia_kwh": None,
         "co2_kg": round(km * _v("comparativo_metro_onibus_sp_gco2e_pkm") / 1000 * viagens, 1), "co2_kg_max": None,
         "custo_rs": round(_v("tarifa_onibus_sptrans") * viagens, 2), "custo_tipo": "tarifa"},
        {"modo": "Carro, sozinho", "renovavel": False, "energia_kwh": round(litros * MJ_POR_LITRO_GASOLINA / 3.6 * viagens, 1),
         "co2_kg": round(litros * fator_gasolina * FRACAO_FOSSIL_GASOLINA_C * viagens, 1),
         "co2_kg_max": round(litros * fator_gasolina * viagens, 1),
         "custo_rs": round(litros * _v("preco_gasolina_sp_capital") * viagens, 2), "custo_tipo": "combustível"},
    ]


def comparar(km: float) -> dict:
    km = round(float(km), 1)
    fator_sin = _v("fator_emissao_sin")                       # tCO2/MWh = kg/kWh
    kwh_pkm = _v("metro_sp_energia_por_passageiro_km")
    consumo_carro = _v("carro_consumo_hb20_sense_gasolina")   # km/L, cidade
    fator_gasolina = _v("fator_emissao_gasolina_automotiva")
    preco_gasolina = _v("preco_gasolina_sp_capital")
    onibus_gpkm = _v("comparativo_metro_onibus_sp_gco2e_pkm")

    renovaveis = _v("renovaveis_matriz_eletrica")
    trilho_kwh = km * kwh_pkm
    litros = km / consumo_carro
    trilho_co2 = trilho_kwh * fator_sin                                    # sem arredondar, para a razão
    carro_co2 = litros * fator_gasolina * FRACAO_FOSSIL_GASOLINA_C
    modos = [
        {"modo": "Trem ou metrô", "energia_kwh": round(trilho_kwh, 2), "co2_kg": round(trilho_kwh * fator_sin, 3), "co2_kg_max": None,
         "custo_rs": _v("tarifa_metro_trem"), "custo_tipo": "tarifa", "renovavel": True,
         "nota": f"Elétrico; {_br(_v('renovaveis_matriz_eletrica'))}% da eletricidade do país veio de fonte renovável em 2025."},
        {"modo": "Ônibus a diesel", "energia_kwh": None, "co2_kg": round(km * onibus_gpkm / 1000, 2), "co2_kg_max": None,
         "custo_rs": _v("tarifa_onibus_sptrans"), "custo_tipo": "tarifa", "renovavel": False,
         "nota": "CO₂ pelo indicador publicado pelo Metrô; a lotação do ônibus não tem fonte oficial."},
        {"modo": "Carro, sozinho", "energia_kwh": round(litros * MJ_POR_LITRO_GASOLINA / 3.6, 1),
         "co2_kg": round(litros * fator_gasolina * FRACAO_FOSSIL_GASOLINA_C, 2), "co2_kg_max": round(litros * fator_gasolina, 2),
         "custo_rs": round(litros * preco_gasolina, 2), "custo_tipo": "combustível", "renovavel": False,
         "nota": f"Carro popular a gasolina, {_br(consumo_carro)} km/L na cidade (INMETRO); custo só do combustível."},
    ]
    premissas = [
        _premissa("fator_emissao_sin", f"fator da eletricidade de {_br(round(fator_sin * 1000, 1))} g de CO₂ por kWh (média do país, MCTI)", True),
        _premissa("renovaveis_matriz_eletrica", f"{_br(renovaveis)}% da eletricidade do país vem de fonte renovável (EPE), o que sustenta o trilho como alternativa renovável"),
        _premissa("metro_sp_energia_por_passageiro_km", f"metrô gasta {_br(kwh_pkm)} kWh por passageiro por km (Relatório Integrado do Metrô); trem usa o mesmo valor, pois a CPTM não publicou o dela"),
        _premissa("carro_consumo_hb20_sense_gasolina", f"carro com uma pessoa, {_br(consumo_carro)} km/L na cidade, gasolina a R$ {preco_gasolina:.2f}".replace(".", ",") + " (preço da ANP)", True),
        _premissa("comparativo_metro_onibus_sp_gco2e_pkm", f"ônibus com {onibus_gpkm:g} g de CO₂ por passageiro por km (dado publicado pelo Metrô, lotação média sem fonte oficial)", True),
        _premissa("fator_emissao_gasolina_automotiva", f"gasolina com {_br(fator_gasolina)} kg de CO₂ por litro; faixa do carro entre a parte fóssil ({round(FRACAO_FOSSIL_GASOLINA_C * 100)}%, com 22% de etanol) e o litro inteiro"),
        {"chave": "poder_calorifico_gasolina", "texto": f"energia da gasolina de {_br(MJ_POR_LITRO_GASOLINA)} MJ por litro (0,770 tep/m³ × 41,87 GJ/tep, BEN da EPE)",
         "tipo": "calculado", "ano": "", "no_cartao": False, "rotulo": f"{TIPOS['calculado']}, a partir do BEN da EPE"},
    ]
    chaves_das_fontes = ("fator_emissao_sin", "renovaveis_matriz_eletrica", "metro_sp_energia_por_passageiro_km",
                         "comparativo_metro_onibus_sp_gco2e_pkm", "carro_consumo_hb20_sense_gasolina", "fator_emissao_gasolina_automotiva",
                         "preco_gasolina_sp_capital", "tarifa_metro_trem", "tarifa_onibus_sptrans")
    fontes, vistas = [], set()
    for c in chaves_das_fontes:                  # o poder calorífico usa o mesmo BEN (EPE) da fonte renovável
        if _fonte(c) not in vistas:
            vistas.add(_fonte(c))
            fontes.append({"nome": NOMES_DAS_FONTES[c], "url": _fonte(c)})
    return {
        "km": km,
        "modos": modos,
        # razão calculada com os valores cheios: dividir números já arredondados distorcia o percentual
        "trilho_vs_carro": round(100 * trilho_co2 / carro_co2, 1) if carro_co2 else None,
        "premissas": [f"{p['texto']} [{p['rotulo']}]" for p in premissas],
        "premissas_detalhe": premissas,
        "rotulo": ROTULO,
        "fontes": sorted({f["url"] for f in fontes}),
        "fontes_nomeadas": fontes,
        "renovavel": {"percentual": renovaveis, "ano": _ano("renovaveis_matriz_eletrica"),
                      "texto": f"O trilho é a alternativa renovável: usa a rede elétrica, que em {_ano('renovaveis_matriz_eletrica')} teve "
                               f"{_br(renovaveis)}% de fonte renovável (EPE). É a média do país, não um contrato do Metrô."},
        "consultado_em": _pesquisa()["consultado_em"],
    }
