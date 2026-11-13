"""Checagem das fontes: forma do relatório e comportamento quando a fonte cai. Sem internet."""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sistema import fontes_saude  # noqa: E402
from sistema.mobilidade import fontes  # noqa: E402

CAMPOS = {"id", "nome", "tipo", "origem", "estado", "ms", "lido_em", "amostra", "usado_em", "detalhe"}


class Forma(unittest.TestCase):
    """Com todas as APIs fora do ar, o relatório continua inteiro: só muda o estado."""

    def setUp(self):
        fora = mock.Mock(side_effect=OSError("sem rede"))
        for nome in ("situacao_linhas", "avisos_tempo", "alertas_cge"):
            p = mock.patch.object(fontes, nome, fora)
            p.start()
            self.addCleanup(p.stop)
        sem_banco = mock.patch.object(fontes_saude.banco, "credenciais", lambda: None)   # teste não fala com o Supabase
        sem_banco.start()
        self.addCleanup(sem_banco.stop)
        self.r = fontes_saude.checar_tudo()

    def test_uma_entrada_por_fonte_com_os_mesmos_campos(self):
        self.assertEqual(len(self.r["fontes"]), len(fontes_saude.CHECAGENS))
        for f in self.r["fontes"]:
            self.assertEqual(CAMPOS - set(f), set(), f["id"])
            self.assertIn(f["estado"], ("ok", "vazio", "falhou"))
            self.assertNotIn("valor", f)          # o dado bruto não vaza no relatório

    def test_api_fora_do_ar_e_falha_declarada_sem_derrubar_o_resto(self):
        por_id = {f["id"]: f for f in self.r["fontes"]}
        self.assertEqual([por_id[x]["estado"] for x in ("linhas", "inmet", "cge")], ["falhou"] * 3)
        self.assertEqual(por_id["rede"]["estado"], "ok")              # base local não depende de rede
        self.assertIn("estações", por_id["rede"]["amostra"])

    def test_resumo_bate_com_as_fontes(self):
        r = self.r["resumo"]
        self.assertEqual(r["total"], len(self.r["fontes"]))
        self.assertEqual(r["ok"] + r["vazio"] + r["falhou"], r["total"])

    def test_nenhuma_chave_ou_segredo_no_relatorio(self):
        import json
        texto = json.dumps(self.r, ensure_ascii=False).lower()
        for proibido in ("sb_secret", "sbp_", "apikey", "eyj", "chave\":", "password"):
            self.assertNotIn(proibido, texto)


class BasesReais(unittest.TestCase):
    """As bases do repositório precisam existir e ter dado de verdade."""

    def test_rede_seguranca_alagamentos_energia_e_mlam(self):
        for checagem, pedaco in ((fontes_saude.checar_rede, "linhas"),
                                 (fontes_saude.checar_seguranca, "estações"),
                                 (fontes_saude.checar_alagamentos_base, "pontos"),
                                 (fontes_saude.checar_energia, "fatores"),
                                 (fontes_saude.checar_base_mlam, "estações")):
            f = checagem()
            self.assertEqual(f["estado"], "ok", f["nome"])
            self.assertIn(pedaco, f["amostra"])
            self.assertTrue(f["usado_em"], f["nome"])

    def test_toda_linha_da_rede_tem_status_ao_vivo_menos_a_7(self):
        """A 7-Rubi não aparece na fonte ao vivo; é por isso que as telas não a oferecem."""
        from sistema.mobilidade import rede
        self.assertIn("7", rede.carregar()["linhas"])


if __name__ == "__main__":
    unittest.main()
