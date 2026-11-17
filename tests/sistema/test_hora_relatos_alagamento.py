"""Hora de São Paulo, relatos guardados no banco e aviso de alagamento só com chuva.

Rodar da raiz do repositório:
    uv run python -m unittest discover -s tests/sistema -v
"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from sistema import hora  # noqa: E402
from sistema.mobilidade import fontes, plano  # noqa: E402
from test_relatos_supabase import AGORA, repositorio  # noqa: E402
from test_sistema import COM_CHUVA, SemInternet, estacao  # noqa: E402


class HoraDeSaoPaulo(unittest.TestCase):
    def test_agora_e_a_hora_de_sao_paulo_mesmo_com_servidor_em_utc(self):
        utc = datetime.now(timezone.utc).replace(tzinfo=None)
        diferenca = utc - hora.agora()
        self.assertLess(abs(diferenca - timedelta(hours=3)), timedelta(minutes=2))

    def test_agora_sem_fuso_para_comparar_com_horarios_do_dia(self):
        self.assertIsNone(hora.agora().tzinfo)
        self.assertEqual(hora.hoje(), hora.agora().date())


class RelatosFicamNoBanco(unittest.TestCase):
    def test_vencidos_saem_do_feed_mas_nao_sao_apagados_do_banco(self):
        repo, api = repositorio({})
        self.assertEqual(repo.remover_expirados(AGORA), 0)
        self.assertFalse([p for p in api.pedidos if p.method == "DELETE"])

    def test_feed_le_do_banco_so_os_que_nao_venceram(self):
        repo, api = repositorio({})
        repo.listar()
        self.assertTrue(api.pedidos[0].url.params["expira_em"].startswith("gt."))


class AlagamentoSoComChuva(SemInternet):
    def _avisos(self, p):
        return [m["texto"] for m in p["motivos"] if m["tipo"] == "alagamento"]

    def test_sem_chuva_nao_avisa_ponto_historico(self):
        p = plano.antes_de_sair(estacao("Pinheiros"), estacao("Vila Olímpia"), agora=datetime(2026, 11, 12, 11, 0))
        self.assertEqual(self._avisos(p), [])

    def test_com_chuva_avisa_como_historico(self):
        with mock.patch.object(fontes, "avisos_tempo", return_value=COM_CHUVA):
            p = plano.antes_de_sair(estacao("Pinheiros"), estacao("Vila Olímpia"), agora=datetime(2026, 11, 12, 11, 0))
        avisos = self._avisos(p)
        self.assertTrue(avisos)
        self.assertIn("histórico", avisos[0])
        self.assertNotIn("alagad", avisos[0].split(":")[1].split("histórico")[0])


if __name__ == "__main__":
    unittest.main()
