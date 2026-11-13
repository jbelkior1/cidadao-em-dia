"""Testes da conta básica (usuário e senha). Sem rede: repositório em memória e um Supabase falso."""
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import contas  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.contas_supabase import RepositorioSupabaseContas  # noqa: E402
from sistema.mobilidade import rede  # noqa: E402

AGORA = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)


def estacao(nome: str) -> str:
    return next(e["id"] for e in rede.estacoes_para_escolha() if e["nome"] == nome)


class Base(unittest.TestCase):
    def setUp(self):
        self.original = contas.repo
        contas.usar_repositorio(contas.RepositorioMemoria())

    def tearDown(self):
        contas.usar_repositorio(self.original)


class Regras(Base):
    def test_cadastro_e_login(self):
        conta, token = contas.cadastrar("Maria.SP", "senha-forte-1", agora=AGORA)
        self.assertEqual(conta.usuario, "maria.sp")                   # minúsculas
        self.assertNotIn("senha-forte-1", conta.senha_hash)           # só o hash
        self.assertTrue(conta.senha_hash.startswith("scrypt$"))
        self.assertEqual(contas.conta_do_token(token, agora=AGORA).id, conta.id)
        _, token2 = contas.entrar("maria.sp", "senha-forte-1", agora=AGORA)
        self.assertNotEqual(token, token2)

    def test_usuario_repetido_e_invalido(self):
        contas.cadastrar("joao", "12345678", agora=AGORA)
        with self.assertRaises(contas.ErroConta) as e:
            contas.cadastrar("JOAO", "12345678", agora=AGORA)
        self.assertEqual(e.exception.status, 409)
        for ruim in ("ab", "joão", "tem espaço", "x" * 31):
            with self.assertRaises(contas.ErroConta, msg=ruim):
                contas.cadastrar(ruim, "12345678", agora=AGORA)

    def test_usuario_com_cara_de_cpf_ou_telefone_e_recusado(self):
        for ruim in ("12345678909", "11912345678"):
            with self.assertRaises(contas.ErroConta, msg=ruim) as e:
                contas.cadastrar(ruim, "12345678", agora=AGORA)
            self.assertIn("dado pessoal", e.exception.mensagem)

    def test_senha_curta(self):
        with self.assertRaises(contas.ErroConta):
            contas.cadastrar("ana", "1234567", agora=AGORA)

    def test_senha_errada_nao_diz_se_o_usuario_existe(self):
        contas.cadastrar("ana", "12345678", agora=AGORA)
        for usuario in ("ana", "ninguem"):
            with self.assertRaises(contas.ErroConta) as e:
                contas.entrar(usuario, "errada!!", agora=AGORA)
            self.assertEqual((e.exception.status, e.exception.mensagem), (401, "Usuário ou senha incorretos."))

    def test_cinco_erros_bloqueiam_por_15_minutos(self):
        contas.cadastrar("ana", "12345678", agora=AGORA)
        for _ in range(contas.FALHAS_ATE_BLOQUEIO):
            with self.assertRaises(contas.ErroConta):
                contas.entrar("ana", "errada!!", agora=AGORA)
        with self.assertRaises(contas.ErroConta) as e:
            contas.entrar("ana", "12345678", agora=AGORA + timedelta(minutes=5))   # bloqueada, mesmo com a senha certa
        self.assertEqual(e.exception.status, 401)        # mesma resposta de senha errada: não revela que a conta existe
        contas.entrar("ana", "12345678", agora=AGORA + timedelta(minutes=16))      # passou o bloqueio

    def test_tentativas_em_paralelo_nao_furam_o_bloqueio(self):
        from concurrent.futures import ThreadPoolExecutor
        contas.cadastrar("ana", "12345678", agora=AGORA)

        def tentar(_):
            try:
                contas.entrar("ana", "errada!!", agora=AGORA)
            except contas.ErroConta:
                pass
        with ThreadPoolExecutor(max_workers=8) as ex:
            list(ex.map(tentar, range(8)))
        self.assertIsNotNone(contas.repo.conta_por_usuario("ana").bloqueado_ate)

    def test_sessao_expira_e_token_falso(self):
        _, token = contas.cadastrar("ana", "12345678", agora=AGORA)
        with self.assertRaises(contas.ErroConta):
            contas.conta_do_token(token, agora=AGORA + timedelta(days=contas.SESSAO_DIAS + 1))
        with self.assertRaises(contas.ErroConta):
            contas.conta_do_token("token-inventado", agora=AGORA)

    def test_preferencias_filtram_linha_e_estacao(self):
        conta, _ = contas.cadastrar("ana", "12345678", agora=AGORA)
        p = contas.salvar_preferencias(conta, ["4", "1", "99", "1"], estacao("Sé"))
        self.assertEqual(p.linhas, ["1", "4"])                 # sem a linha 99 e sem repetição
        with self.assertRaises(contas.ErroConta):
            contas.salvar_preferencias(conta, [], "estacao-que-nao-existe")

    def test_rotinas(self):
        conta, _ = contas.cadastrar("ana", "12345678", agora=AGORA)
        r = contas.criar_rotina(conta, "Casa → Trabalho", estacao("Sé"), estacao("Paulista"), "08:30", "51234")
        self.assertEqual((r.dias, r.horario.strftime("%H:%M")), ("12345", "08:30"))
        with self.assertRaises(contas.ErroConta):
            contas.criar_rotina(conta, "Igual", estacao("Sé"), estacao("Sé"), "08:30", "1")
        with self.assertRaises(contas.ErroConta):
            contas.criar_rotina(conta, "Hora ruim", estacao("Sé"), estacao("Paulista"), "25:99", "1")
        with self.assertRaises(contas.ErroConta):
            contas.criar_rotina(conta, "meu cpf 123.456.789-09", estacao("Sé"), estacao("Paulista"), "08:30", "1")
        outra, _ = contas.cadastrar("bia", "12345678", agora=AGORA)
        self.assertFalse(contas.repo.apagar_rotina(outra.id, r.id))   # uma conta não apaga a rota da outra
        self.assertTrue(contas.repo.apagar_rotina(conta.id, r.id))


class Api(Base):
    def setUp(self):
        super().setUp()
        self.c = TestClient(app)

    def test_fluxo_completo(self):
        r = self.c.post("/api/conta/cadastro", json={"usuario": "passageiro1", "senha": "12345678"})
        self.assertEqual(r.status_code, 201)
        token = r.json()["token"]
        cab = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.c.get("/api/conta/eu", headers=cab).json()["usuario"], "passageiro1")
        p = self.c.put("/api/conta/preferencias", headers=cab, json={"linhas": ["1", "4"], "casa": estacao("Sé")}).json()
        self.assertEqual((p["linhas"], p["casa"]), (["1", "4"], estacao("Sé")))
        p = self.c.post("/api/conta/rotinas", headers=cab, json={
            "nome": "Trabalho", "origem": estacao("Sé"), "destino": estacao("Paulista"), "horario": "08:30", "dias": "12345"}).json()
        rotina = p["rotinas"][0]
        self.assertEqual((rotina["origem_nome"], rotina["destino_nome"]), ("Sé", "Paulista"))
        self.assertEqual(self.c.delete(f"/api/conta/rotinas/{rotina['id']}", headers=cab).json()["rotinas"], [])
        self.assertEqual(self.c.delete("/api/conta/rotinas/nao-e-uuid", headers=cab).status_code, 404)
        self.c.post("/api/conta/sair", headers=cab)
        self.assertEqual(self.c.get("/api/conta/eu", headers=cab).status_code, 401)

    def test_uma_conta_nao_ve_nem_apaga_rota_da_outra(self):
        cab_a = {"Authorization": "Bearer " + self.c.post("/api/conta/cadastro", json={"usuario": "conta.a", "senha": "12345678"}).json()["token"]}
        cab_b = {"Authorization": "Bearer " + self.c.post("/api/conta/cadastro", json={"usuario": "conta.b", "senha": "12345678"}).json()["token"]}
        rota = self.c.post("/api/conta/rotinas", headers=cab_a, json={
            "nome": "A", "origem": estacao("Sé"), "destino": estacao("Paulista"), "horario": "07:00", "dias": "1"}).json()["rotinas"][0]
        self.assertEqual(self.c.get("/api/conta/eu", headers=cab_b).json()["rotinas"], [])
        self.assertEqual(self.c.delete(f"/api/conta/rotinas/{rota['id']}", headers=cab_b).status_code, 404)
        self.assertEqual(len(self.c.get("/api/conta/eu", headers=cab_a).json()["rotinas"]), 1)
        self.assertEqual(self.c.get("/api/conta/eu", headers={"Authorization": "token-sem-bearer"}).status_code, 401)
        self.assertEqual(self.c.post("/api/conta/entrar", json={"usuario": "conta.a", "senha": "x" * 5000}).status_code, 422)

    def test_sem_token_e_apagar_conta(self):
        self.assertEqual(self.c.get("/api/conta/eu").status_code, 401)
        token = self.c.post("/api/conta/cadastro", json={"usuario": "tchau", "senha": "12345678"}).json()["token"]
        cab = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.c.request("DELETE", "/api/conta", headers=cab, json={"senha": "errada!!"}).status_code, 401)
        self.assertEqual(self.c.request("DELETE", "/api/conta", headers=cab, json={"senha": "12345678"}).status_code, 200)
        self.assertEqual(self.c.post("/api/conta/entrar", json={"usuario": "tchau", "senha": "12345678"}).status_code, 401)


class SupabaseFalso(unittest.TestCase):
    """O repositório do Supabase monta as chamadas certas e trata o usuário repetido (409)."""

    def test_usuario_repetido_vira_false_e_filtro_da_sessao(self):
        pedidos = []

        def responder(req: httpx.Request) -> httpx.Response:
            pedidos.append(req)
            if req.method == "POST" and req.url.path.endswith("/contas"):
                return httpx.Response(409, json={"code": "23505"})
            return httpx.Response(200, json=[{"conta_id": "c1"}])

        cli = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(responder))
        repo = RepositorioSupabaseContas("https://x.supabase.co", "chave", cliente=cli)
        conta = contas.Conta(id="c1", usuario="ana", senha_hash=contas.gerar_hash("12345678"), criado_em=AGORA)
        self.assertFalse(repo.inserir_conta(conta))
        self.assertEqual(repo.conta_da_sessao("a" * 64, AGORA), "c1")
        q = pedidos[-1].url.params
        self.assertEqual(q["token_hash"], "eq." + "a" * 64)
        self.assertTrue(q["expira_em"].startswith("gt."))
        self.assertNotIn("12345678", json.dumps([str(p.content) for p in pedidos]))


if __name__ == "__main__":
    unittest.main()
