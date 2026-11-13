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


def _br(numero: float) -> str:
    return f"{numero:g}".replace(".", ",")


def comparar(km: float) -> dict:
    km = round(float(km), 1)
    fator_sin = _v("fator_emissao_sin")                       # tCO2/MWh = kg/kWh
    kwh_pkm = _v("metro_sp_energia_por_passageiro_km")
    consumo_carro = _v("carro_consumo_hb20_sense_gasolina")   # km/L, cidade
    fator_gasolina = _v("fator_emissao_gasolina_automotiva")
    preco_gasolina = _v("preco_gasolina_sp_capital")
    onibus_gpkm = _v("comparativo_metro_onibus_sp_gco2e_pkm")

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
    return {
        "km": km,
        "modos": modos,
        # razão calculada com os valores cheios: dividir números já arredondados distorcia o percentual
        "trilho_vs_carro": round(100 * trilho_co2 / carro_co2, 1) if carro_co2 else None,
        "premissas": [
            f"fator da eletricidade de {_br(round(fator_sin * 1000, 1))} g de CO₂ por kWh (média do país em 2025, MCTI)",
            f"metrô gasta {_br(kwh_pkm)} kWh por passageiro por km (Relatório Integrado 2025); trem usa o mesmo valor, pois a CPTM não publicou o dela",
            f"carro com uma pessoa, {_br(consumo_carro)} km/L, gasolina a R$ {preco_gasolina:.2f}".replace(".", ","),
            f"ônibus com {onibus_gpkm:g} g de CO₂ por passageiro por km (dado publicado pelo Metrô)",
        ],
        "rotulo": ROTULO,
        "fontes": sorted({_fonte(c) for c in ("fator_emissao_sin", "metro_sp_energia_por_passageiro_km", "carro_consumo_hb20_sense_gasolina",
                                              "fator_emissao_gasolina_automotiva", "preco_gasolina_sp_capital", "tarifa_metro_trem",
                                              "tarifa_onibus_sptrans")}),
        "consultado_em": _pesquisa()["consultado_em"],
    }
