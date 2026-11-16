"""A Lia fala de energia, CO2 e custo da viagem inteira, nunca "por km" (o modelo já errou isso uma vez)."""
import unittest
from datetime import datetime

from sistema import assistente
from sistema.mobilidade import energia


class EnergiaNaConversa(unittest.TestCase):
    def test_instrucao_proibe_dizer_por_km(self):
        texto = assistente._instrucoes({}, None, datetime(2026, 11, 16, 9, 0))
        self.assertIn("viagem inteira", texto)
        self.assertIn("Nunca diga que são por km", texto)

    def test_mensal_usa_o_valor_exato_e_nao_o_da_viagem_arredondado(self):
        # 15 km x 0,0717 kWh x 44 viagens = 47,3 (e não 1,08 x 44 = 47,5)
        trilho = energia.mensal(15, 44)[0]
        self.assertEqual(trilho["energia_kwh"], 47.3)
        carro = energia.mensal(15, 44)[2]
        self.assertAlmostEqual(carro["custo_rs"], 315.11, places=2)

    def test_mensal_mantem_a_ordem_dos_modos_da_viagem(self):
        viagem = [m["modo"] for m in energia.comparar(15)["modos"]]
        self.assertEqual([m["modo"] for m in energia.mensal(15, 44)], viagem)


if __name__ == "__main__":
    unittest.main()
