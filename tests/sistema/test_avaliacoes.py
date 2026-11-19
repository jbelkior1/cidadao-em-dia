"""Testes da avaliação de quem usou o sistema. Sem rede: repositório em memória e um Supabase falso."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import avaliacoes  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.avaliacoes_supabase import RepositorioSupabaseAvaliacoes  # noqa: E402

AGORA = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)
APARELHO = "0123456789abcdef0123456789abcdef"
COMPLETA = {"perfil": "faculdade", "tempos": [40, 25, None], "acertos": [True, True, None],
            "energia": ["sim", "em parte", "sim", None], "nota_energia": 4, "facilidade": [5, 4, 4, 5, 5],
            "comentario": "Gostei muito de relatar na hora.", "sugestao": "Ter dados de ônibus."}


class Base(unittest.TestCase):
    def setUp(self):
        self.original = avaliacoes.repo
        avaliacoes.usar_repositorio(avaliacoes.RepositorioMemoria())

    def tearDown(self):
        avaliacoes.usar_repositorio(self.original)

    def registrar(self, **mudancas):
        d = COMPLETA | mudancas
        return avaliacoes.registrar(APARELHO, d["perfil"], d["tempos"], d["acertos"], d["energia"], d["nota_energia"],
                                    d["facilidade"], d["comentario"], d["sugestao"], agora=d.get("agora", AGORA))


class Regras(Base):
    def test_registra_e_resume(self):
        self.registrar()
        self.registrar(tempos=[60, 35, 90], acertos=[False, True, True], facilidade=[3, 4, 4, 3, 4], comentario=None, sugestao=None)
        r = avaliacoes.resumo()
        self.assertEqual(r["pessoas"], 2)
        self.assertEqual(r["tarefas"][0]["tempo_medio_s"], 50.0)
        self.assertEqual(r["tarefas"][0]["acerto_percentual"], 50)
        self.assertEqual(r["tarefas"][2]["acharam"], 1)                 # um não achou a tarefa 3
        self.assertEqual(r["facilidade"][0]["media"], 4.0)
        self.assertEqual(r["energia"][1]["em parte"], 2)                  # as duas responderam "em parte" na situação 2
        self.assertEqual(len(r["comentarios"]), 1)                      # só quem escreveu algo
        self.assertEqual(r["perfis"], {"Faculdade": 2})

    def test_recusa_dado_pessoal_no_comentario(self):
        with self.assertRaises(avaliacoes.ErroAvaliacao) as e:
            self.registrar(comentario="me liga no 11987654321")
        self.assertEqual(e.exception.status, 422)
        self.assertEqual(avaliacoes.resumo()["pessoas"], 0)

    def test_recusa_link(self):
        for texto in ("veja www.promo.com", "https://x.io/oferta", "acesse loja.com.br"):
            with self.subTest(texto=texto), self.assertRaises(avaliacoes.ErroAvaliacao):
                self.registrar(sugestao=texto)

    def test_valida_faixas(self):
        for mudanca in ({"facilidade": [6, 4, 4, 4, 4]}, {"tempos": [400, 1, 1]}, {"energia": ["talvez", None, None, None]},
                        {"nota_energia": 0}, {"perfil": "vizinho"}, {"facilidade": [4, 4]}):
            with self.subTest(mudanca=mudanca), self.assertRaises(avaliacoes.ErroAvaliacao):
                self.registrar(**mudanca)

    def test_limite_por_aparelho(self):
        for i in range(avaliacoes.LIMITE_POR_HORA):
            self.registrar(agora=AGORA + timedelta(minutes=i))
        with self.assertRaises(avaliacoes.ErroAvaliacao) as e:
            self.registrar(agora=AGORA + timedelta(minutes=20))
        self.assertEqual(e.exception.status, 429)
        self.registrar(agora=AGORA + timedelta(hours=2))               # depois de uma hora, volta a aceitar

    def test_nao_guarda_id_do_aparelho(self):
        a = self.registrar()
        self.assertNotEqual(a.autor_hash, APARELHO)
        self.assertNotIn("autor_hash", avaliacoes.como_json(a))


class Rotas(Base):
    def test_enviar_e_ler(self):
        cliente = TestClient(app)
        r = cliente.post("/api/avaliacoes", json=COMPLETA, headers={"X-Device-Id": APARELHO})
        self.assertEqual(r.status_code, 201, r.text)
        resumo = cliente.get("/api/avaliacoes").json()
        self.assertEqual(resumo["pessoas"], 1)
        self.assertEqual(len(resumo["perguntas"]), 5)

    def test_sem_aparelho_e_com_dado_pessoal(self):
        cliente = TestClient(app)
        self.assertEqual(cliente.post("/api/avaliacoes", json=COMPLETA).status_code, 400)
        r = cliente.post("/api/avaliacoes", json=COMPLETA | {"sugestao": "meu email é ana@x.com"}, headers={"X-Device-Id": APARELHO})
        self.assertEqual(r.status_code, 422)


class Supabase(unittest.TestCase):
    def test_grava_e_le_pelas_colunas(self):
        linhas = []

        def tratar(pedido: httpx.Request) -> httpx.Response:
            if pedido.method == "POST":
                linhas.append(json.loads(pedido.content))
                return httpx.Response(201)
            return httpx.Response(200, json=linhas)

        cliente = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(tratar))
        repo = RepositorioSupabaseAvaliacoes("https://x.supabase.co", "chave", cliente=cliente)
        original = avaliacoes.repo
        avaliacoes.usar_repositorio(repo)
        try:
            avaliacoes.registrar(APARELHO, "familia", [10, 20, 30], [True, False, True], ["sim", "sim", "nao", "em parte"], 5,
                                 [5, 5, 4, 4, 5], "Muito útil", None, agora=AGORA)
            self.assertEqual(linhas[0]["t2_segundos"], 20)
            self.assertEqual(linhas[0]["e4"], "em parte")
            self.assertEqual(linhas[0]["f5"], 5)
            lidas = repo.todas()
            self.assertEqual(lidas[0].acertos, [True, False, True])
            self.assertEqual(lidas[0].facilidade, [5, 5, 4, 4, 5])
        finally:
            avaliacoes.usar_repositorio(original)


if __name__ == "__main__":
    unittest.main()


class FormularioSimples(Base):
    def test_so_comentario(self):
        a = avaliacoes.registrar(APARELHO, "trabalho", comentario="Achei muito útil para o dia a dia.", agora=AGORA)
        self.assertEqual(a.facilidade, [None] * 5)
        r = avaliacoes.resumo()
        self.assertEqual(r["pessoas"], 1)
        self.assertEqual(r["testes_completos"], 0)
        self.assertEqual(r["grupos"][0]["grupo"], "Trabalho")
        self.assertIsNone(r["facilidade_media"])

    def test_vazio_ou_notas_pela_metade(self):
        with self.assertRaises(avaliacoes.ErroAvaliacao):
            avaliacoes.registrar(APARELHO, None, comentario="   ", agora=AGORA)
        with self.assertRaises(avaliacoes.ErroAvaliacao):
            avaliacoes.registrar(APARELHO, None, facilidade=[5, None, None, None, None], comentario="ok", agora=AGORA)

    def test_rota_so_comentario(self):
        cliente = TestClient(app)
        r = cliente.post("/api/avaliacoes", json={"perfil": "familia", "comentario": "Gostei do relatar."}, headers={"X-Device-Id": APARELHO})
        self.assertEqual(r.status_code, 201, r.text)
        self.assertEqual(cliente.get("/api/avaliacoes").json()["grupos"][0]["comentarios"][0]["comentario"], "Gostei do relatar.")
