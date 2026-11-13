"""Repositório do Supabase contra uma API falsa (httpx.MockTransport): sem rede, sem banco."""
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import httpx  # noqa: E402

from sistema import banco, relatos  # noqa: E402
from sistema.relatos_supabase import RepositorioSupabase  # noqa: E402

AGORA = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)


def linha_banco(**extra):
    base = {"id": "a1b2c3d4e5f6", "linha": "3", "estacao_id": None, "tipo": "lotado",
            "criado_em": "2026-11-13T11:55:00+00:00", "expira_em": "2026-11-13T13:55:00+00:00",
            "autor_hash": "0123456789ab", "confirmacoes": 1, "contestacoes": 0, "sinalizacoes": 0, "demo": False,
            "votos": [{"autor_hash": "ffffffffffff", "valor": "ainda"}], "sinalizacoes_lista": []}
    base.update(extra)
    return base


class ApiFalsa:
    def __init__(self, respostas):
        self.respostas = respostas      # (método, caminho) -> corpo JSON
        self.pedidos: list[httpx.Request] = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append(pedido)
        corpo = self.respostas.get((pedido.method, pedido.url.path), [])
        return httpx.Response(200 if corpo is not None else 204, json=corpo)


def repositorio(respostas, chave="sb_secret_teste"):
    api = ApiFalsa(respostas)
    cliente = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(api),
                           headers=__import__("sistema.relatos_supabase", fromlist=["_cabecalhos"])._cabecalhos(chave))
    return RepositorioSupabase("https://x.supabase.co", chave, cliente=cliente), api


class Cabecalhos(unittest.TestCase):
    def test_esquema_proprio_e_chave_secreta_so_no_apikey(self):
        repo, api = repositorio({("GET", "/rest/v1/relatos"): []})
        repo.listar()
        p = api.pedidos[0]
        self.assertEqual(p.headers["accept-profile"], "datempo")
        self.assertEqual(p.headers["apikey"], "sb_secret_teste")
        self.assertNotIn("authorization", p.headers)

    def test_chave_antiga_vai_tambem_no_authorization(self):
        repo, api = repositorio({("GET", "/rest/v1/relatos"): []}, chave="eyJabc")
        repo.listar()
        self.assertEqual(api.pedidos[0].headers["authorization"], "Bearer eyJabc")


class Leitura(unittest.TestCase):
    def test_lista_com_votos_e_datas(self):
        repo, _ = repositorio({("GET", "/rest/v1/relatos"): [linha_banco()]})
        [r] = repo.listar()
        self.assertEqual(r.votos, {"ffffffffffff": "ainda"})
        self.assertEqual(r.criado_em, datetime(2026, 11, 13, 11, 55, tzinfo=timezone.utc))
        self.assertTrue(relatos.esta_ativo(r, AGORA))

    def test_ultimo_do_autor_filtra_autor_linha_e_tira_demo(self):
        repo, api = repositorio({("GET", "/rest/v1/relatos"): [linha_banco()]})
        repo.ultimo_do_autor("0123456789ab", "3")
        q = api.pedidos[0].url.params
        self.assertEqual((q["autor_hash"], q["linha"], q["demo"], q["limit"]), ("eq.0123456789ab", "eq.3", "eq.false", "1"))

    def test_obter_sem_resultado(self):
        repo, _ = repositorio({("GET", "/rest/v1/relatos"): []})
        self.assertIsNone(repo.obter("000000000000"))


class Escrita(unittest.TestCase):
    def test_inserir_manda_so_campos_do_banco(self):
        repo, api = repositorio({("POST", "/rest/v1/relatos"): None})
        r = relatos.Relato(id="a1b2c3d4e5f6", linha="3", estacao_id=None, tipo="lotado", criado_em=AGORA,
                           expira_em=AGORA + timedelta(hours=2), autor_hash="0123456789ab")
        repo.inserir(r)
        corpo = json.loads(api.pedidos[0].content)
        self.assertNotIn("votos", corpo)
        self.assertEqual(corpo["autor_hash"], "0123456789ab")

    def test_voto_e_sinalizacao_pelas_funcoes_do_banco(self):
        repo, api = repositorio({("POST", "/rest/v1/rpc/registrar_voto"): True, ("POST", "/rest/v1/rpc/registrar_sinalizacao"): False})
        self.assertTrue(repo.registrar_voto("a1b2c3d4e5f6", "0123456789ab", "ainda"))
        self.assertFalse(repo.registrar_sinalizacao("a1b2c3d4e5f6", "0123456789ab"))
        self.assertEqual(json.loads(api.pedidos[0].content)["p_valor"], "ainda")

    def test_remover_expirados_conta_o_que_saiu(self):
        repo, api = repositorio({("DELETE", "/rest/v1/relatos"): [linha_banco(), linha_banco(id="000000000001")]})
        self.assertEqual(repo.remover_expirados(AGORA), 2)
        self.assertTrue(api.pedidos[0].url.params["expira_em"].startswith("lte.2026-11-13T12:00:00"))

    def test_erro_do_banco_vira_excecao(self):
        api = lambda p: httpx.Response(401, json={"message": "no"})  # noqa: E731
        cliente = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(api))
        with self.assertRaises(RuntimeError):
            RepositorioSupabase("https://x.supabase.co", "k", cliente=cliente).listar()


class Env(unittest.TestCase):
    def test_env_nao_sobrescreve_o_ambiente(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / ".env"
            arq.write_text("DT_TESTE_A=1\n# comentario\nDT_TESTE_B='dois'\n", encoding="utf-8")
            os.environ["DT_TESTE_A"] = "ja"
            banco.carregar_env(arq)
            self.assertEqual((os.environ["DT_TESTE_A"], os.environ["DT_TESTE_B"]), ("ja", "dois"))
            del os.environ["DT_TESTE_A"], os.environ["DT_TESTE_B"]


if __name__ == "__main__":
    unittest.main()
