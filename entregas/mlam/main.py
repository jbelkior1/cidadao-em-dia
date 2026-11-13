"""Roda as questões 02 a 06 na ordem, grava a saída em texto e os números em JSON.

    python main.py

Deixa em saidas/:
  - relatorio.txt       toda a saída das questões, com as interpretações
  - resultados.json     os números de cada questão, para montar o relatório da questão 07
  - q0*.png             os gráficos pedidos
"""
import io
import json
import sys
from contextlib import redirect_stdout
from datetime import datetime

import comum
import questao02_probabilidade as q02
import questao03_testes_hipotese as q03
import questao04_bivariada as q04
import questao05_multivariada as q05
import questao06_logistica as q06

QUESTOES = (("questao_02", q02), ("questao_03", q03), ("questao_04", q04),
            ("questao_05", q05), ("questao_06", q06))


def main() -> int:
    df = comum.carregar()
    resultados, saida = {}, io.StringIO()
    with redirect_stdout(saida):
        print(f"MLAM — Global Solution 2026.2 — análises rodadas em "
              f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"Base: {comum.BASE.name} ({len(df)} estações, SSP-SP, jan–set/2026)")
        for chave, modulo in QUESTOES:
            resultados[chave] = modulo.resolver(df)

    texto = saida.getvalue()
    print(texto)

    comum.SAIDAS.mkdir(exist_ok=True)
    (comum.SAIDAS / "relatorio.txt").write_text(texto, encoding="utf-8")
    (comum.SAIDAS / "resultados.json").write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"\nSaídas em {comum.SAIDAS}:")
    for arquivo in sorted(comum.SAIDAS.iterdir()):
        print(f"  {arquivo.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
