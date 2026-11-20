# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
# SERS - comparação de energia, custo e CO2 da mesma viagem de trem/metrô, ônibus e carro
# Uso: python comparar_energia.py        (viagem de 15 km)
#      python comparar_energia.py 8.5    (outra distância)
# As contas ficam em sistema/mobilidade/energia.py, o mesmo arquivo que o app usa,
# e os fatores (com fonte e ano) em pesquisa/energia_modos.json.

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sistema.mobilidade import energia  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

DIAS_UTEIS = 22  # período de referência: um mês de trabalho, ida e volta


def br(numero, casas=2):
    # número no formato brasileiro, sem zero sobrando no fim
    texto = f"{numero:.{casas}f}".rstrip("0").rstrip(".")
    return (texto or "0").replace(".", ",")


def real(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def co2_texto(m, casas=2):
    if m["co2_kg_max"]:
        return br(m["co2_kg"], casas) + " a " + br(m["co2_kg_max"], casas) + " kg"
    return br(m["co2_kg"], casas) + " kg"


def energia_texto(m, casas=2):
    if m["energia_kwh"] is None:
        return "sem fonte"
    return br(m["energia_kwh"], casas) + " kWh"


# distância digitada (ou 15 km)
km = 15.0
if len(sys.argv) > 1:
    try:
        km = float(sys.argv[1].replace(",", "."))
    except ValueError:
        print(f"Distância inválida: {sys.argv[1]!r}. Use um número, por exemplo 15 ou 8,5.")
        sys.exit(2)
    if km <= 0:
        print("A distância precisa ser maior que zero.")
        sys.exit(2)

r = energia.comparar(km)
linha = "-" * 76

print()
print("=" * 76)
print(f"SERS: a energia da viagem · {br(r['km'], 1)} km, por pessoa, só a ida")
print("=" * 76)
print("Necessidade energética: deslocamento casa-trabalho de quem usa trem e metrô em São Paulo.")
print("Alternativas comparadas para a MESMA necessidade e o MESMO período (uma viagem):\n")

# uma viagem
print(f"{'Modo':<18}{'Energia':>12}{'CO₂':>18}{'Custo':>12}   Renovável")
print(linha)
for m in r["modos"]:
    renovavel = "sim" if m["renovavel"] else "não"
    print(f"{m['modo']:<18}{energia_texto(m):>12}{co2_texto(m):>18}{real(m['custo_rs']):>12}   {renovavel}")
print(linha)

print("\nNotas de cada modo:")
for m in r["modos"]:
    print(f"  {m['modo']}: {m['nota']}")

if r["trilho_vs_carro"] is not None:
    print(f"\nResultado: o trilho emite {br(r['trilho_vs_carro'], 1)}% do CO₂ do carro nesta distância "
          f"(uma redução de {br(100 - r['trilho_vs_carro'], 1)}%).")

# período de referência: um mês de ida e volta ao trabalho
viagens = DIAS_UTEIS * 2
print(f"\nPeríodo de referência: um mês de trabalho ({DIAS_UTEIS} dias úteis, ida e volta = {viagens} viagens de {br(r['km'], 1)} km)")
print(f"{'Modo':<18}{'Energia/mês':>14}{'CO₂/mês':>18}{'Custo/mês':>14}")
print(linha)
mes = energia.mensal(r["km"], viagens)
for m in mes:
    print(f"{m['modo']:<18}{energia_texto(m, 1):>14}{co2_texto(m, 1):>18}{real(m['custo_rs']):>14}")
print(linha)

trilho, carro = mes[0], mes[2]
evita_min = carro["co2_kg"] - trilho["co2_kg"]
evita_max = carro["co2_kg_max"] - trilho["co2_kg"]
diferenca = carro["custo_rs"] - trilho["custo_rs"]  # em viagens curtas a tarifa do trilho passa a gasolina
custo = real(abs(diferenca)) + (" a menos" if diferenca >= 0 else " a mais")
print(f"Trocar o carro pelo trilho nesse mês evita cerca de {br(evita_min, 0)} a {br(evita_max, 0)} kg de CO₂ "
      f"(faixa do teor de etanol) e custa cerca de {custo}")
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
