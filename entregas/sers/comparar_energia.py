# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""SERS: comparação de energia, custo e CO₂ da mesma viagem em três modos.

Roda a comparação que está no app "Dá Tempo?" e mostra cada conta passo a passo, com a origem
de cada número. É este arquivo que o professor roda para ver a parte da SERS funcionando.

    python comparar_energia.py            # viagem de 15 km (casa-trabalho média)
    python comparar_energia.py 8.5        # outra distância

O cálculo não é reescrito aqui: ele vem de `sistema/mobilidade/energia.py`, o mesmo módulo que o
app usa. Assim não existe uma versão da matéria e outra do produto, que poderiam divergir.
Os fatores vêm de `pesquisa/energia_modos.json`, com fonte, unidade, ano e premissa em cada um.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from sistema.mobilidade import energia  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")   # o "₂" de CO₂ quebra no Windows quando a saída é redirecionada

PADRAO_KM = 15.0
DIAS_UTEIS = 22         # período de referência: um mês de trabalho, ida e volta


def real(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def br(numero: float, casas: int = 2) -> str:
    """Número no formato do Brasil, sem zero à toa no fim."""
    return (f"{numero:.{casas}f}".rstrip("0").rstrip(".") or "0").replace(".", ",")


def main(km: float) -> int:
    r = energia.comparar(km)
    print(f"\n{'=' * 76}")
    print(f"SERS: a energia da viagem · {br(r['km'], 1)} km, por pessoa, só a ida")
    print(f"{'=' * 76}")
    print(f"Necessidade energética: deslocamento casa-trabalho de quem usa trem e metrô em São Paulo.")
    print(f"Alternativas comparadas para a MESMA necessidade e o MESMO período (uma viagem):\n")

    print(f"{'Modo':<18}{'Energia':>12}{'CO₂':>18}{'Custo':>12}   Renovável")
    print("-" * 76)
    for m in r["modos"]:
        kwh = f"{br(m['energia_kwh'])} kWh" if m["energia_kwh"] is not None else "sem fonte"
        co2 = (f"{br(m['co2_kg'])} a {br(m['co2_kg_max'])} kg" if m["co2_kg_max"] else f"{br(m['co2_kg'])} kg")
        print(f"{m['modo']:<18}{kwh:>12}{co2:>18}{real(m['custo_rs']):>12}   {'sim' if m['renovavel'] else 'não'}")
    print("-" * 76)

    print("\nNotas de cada modo:")
    for m in r["modos"]:
        print(f"  {m['modo']}: {m['nota']}")

    if r["trilho_vs_carro"] is not None:
        print(f"\nResultado: o trilho emite {br(r['trilho_vs_carro'], 1)}% do CO₂ do carro nesta distância "
              f"(uma redução de {br(100 - r['trilho_vs_carro'], 1)}%).")

    # ---- período de referência comum: um mês de ida e volta ao trabalho
    viagens = DIAS_UTEIS * 2
    print(f"\nPeríodo de referência: um mês de trabalho ({DIAS_UTEIS} dias úteis, ida e volta = {viagens} viagens de {br(r['km'], 1)} km)")
    print(f"{'Modo':<18}{'Energia/mês':>14}{'CO₂/mês':>18}{'Custo/mês':>14}")
    print("-" * 76)
    mes = energia.mensal(r["km"], viagens)
    for m in mes:
        kwh = f"{br(m['energia_kwh'], 1)} kWh" if m["energia_kwh"] is not None else "sem fonte"
        co2 = (f"{br(m['co2_kg'], 1)} a {br(m['co2_kg_max'], 1)} kg" if m["co2_kg_max"] else f"{br(m['co2_kg'], 1)} kg")
        print(f"{m['modo']:<18}{kwh:>14}{co2:>18}{real(m['custo_rs']):>14}")
    print("-" * 76)
    trilho_mes, carro_mes = mes[0], mes[2]
    evita_min = carro_mes["co2_kg"] - trilho_mes["co2_kg"]
    evita_max = carro_mes["co2_kg_max"] - trilho_mes["co2_kg"]
    # em distâncias curtas (abaixo de ~11 km) a tarifa do trilho passa o gasto de gasolina: a frase muda para "a mais"
    diferenca = carro_mes["custo_rs"] - trilho_mes["custo_rs"]
    custo_frase = f"{real(abs(diferenca))} a {'menos' if diferenca >= 0 else 'mais'}"
    print(f"Trocar o carro pelo trilho nesse mês evita cerca de {br(evita_min, 0)} a {br(evita_max, 0)} kg de CO₂ "
          f"(faixa do teor de etanol) e custa cerca de {custo_frase}")
    print("(tarifa do trilho contra só a gasolina do carro, sem estacionamento, manutenção nem depreciação).")
    print("O custo do trilho e do ônibus é tarifa cheia; com a integração do Bilhete Único ou vale-transporte o valor muda.")

    print("\nComo ler a energia: o kWh do trilho é eletricidade usada na tração; o kWh do carro é a energia")
    print("contida na gasolina queimada. São formas diferentes de energia, então a coluna mostra a ordem de")
    print("grandeza, e a comparação justa entre os modos é a do CO₂ e a do custo.")

    print("\nPremissas (toda estimativa depende delas):")
    for p in r["premissas"]:
        print(f"  - {p}")

    print("\nFontes consultadas:")
    for f in r["fontes_nomeadas"]:
        print(f"  - {f['nome']}: {f['url']}")
    print()
    print(r["renovavel"]["texto"])

    print(f"\nDados levantados em {r['consultado_em']}. {r['rotulo']}")
    print("Limitações: a lotação média do ônibus não tem fonte oficial, por isso o CO₂ dele vem do")
    print("indicador por passageiro-km publicado pelo Metrô; o carro é considerado com uma pessoa e")
    print("o custo é só o combustível, sem estacionamento, manutenção nem depreciação.\n")
    return 0


if __name__ == "__main__":
    try:
        distancia = float(sys.argv[1].replace(",", ".")) if len(sys.argv) > 1 else PADRAO_KM
    except ValueError:
        print(f"Distância inválida: {sys.argv[1]!r}. Use um número, por exemplo 15 ou 8,5.")
        raise SystemExit(2)
    if distancia <= 0:
        print("A distância precisa ser maior que zero.")
        raise SystemExit(2)
    raise SystemExit(main(distancia))
