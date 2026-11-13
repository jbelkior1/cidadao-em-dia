"""Testes do feed de relatos dos passageiros.

O relógio entra por parâmetro (`agora`) e cada teste usa um RepositorioMemoria novo: nada depende
de internet, de horário real nem de teste anterior. Rodar da raiz:
    uv run python -m unittest discover -s tests/sistema -v
"""
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi.testclient import TestClient  # noqa: E402

from sistema import relatos  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.mobilidade import rede  # noqa: E402
from sistema.relatos import ErroRelato, RepositorioMemoria  # noqa: E402

AGORA = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)
MIN = timedelta(minutes=1)
A, B, C, D = "aparelho-aaaaaaaa", "aparelho-bbbbbbbb", "aparelho-cccccccc", "aparelho-dddddddd"


def um_id_de_estacao() -> str:
    return rede.carregar()["estacoes"][0]["id"]


class Dominio(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioMemoria()

    def relatar(self, aparelho=A, linha="3", tipo="lotado", estacao_id=None, quando=AGORA):
        return relatos.criar_relato(aparelho, linha, tipo, estacao_id, agora=quando, repositorio=self.repo)

    def ativos(self, quando=AGORA, **filtro):
        return relatos.listar_ativos(agora=quando, repositorio=self.repo, **filtro)

    # ---- campos
    def test_cria_relato_valido(self):
        r = self.relatar(estacao_id=um_id_de_estacao())
        self.assertEqual((r.linha, r.tipo), ("3", "lotado"))
        self.assertEqual(r.expira_em - r.criado_em, timedelta(hours=2))
        self.assertEqual((r.confirmacoes, r.contestacoes, r.sinalizacoes, r.demo), (0, 0, 0, False))

    def test_valida_linha_tipo_e_estacao(self):
        for linha, tipo, estacao in (("99", "lotado", None), (None, "lotado", None), ("3", "briga", None),
                                     ("3", None, None), ("3", "lotado", "nao-existe")):
            with self.subTest(linha=linha, tipo=tipo, estacao=estacao):
                with self.assertRaises(ErroRelato) as e:
                    self.relatar(linha=linha, tipo=tipo, estacao_id=estacao)
                self.assertEqual(e.exception.status, 422)
        self.assertEqual(self.ativos(), [])

    def test_estacao_e_opcional(self):
        self.assertIsNone(self.relatar(estacao_id=None).estacao_id)
        self.assertIsNone(self.relatar(aparelho=B, estacao_id="").estacao_id)

    def test_todos_os_tipos_previstos_existem(self):
        self.assertEqual(set(relatos.TIPOS), {"lotado", "parado", "quebrou", "chuva", "alagado", "seguranca", "normal"})
        self.assertEqual(relatos.TIPOS["normal"].rotulo, "Tudo certo")

    # ---- limite por linha
    def test_um_relato_por_autor_e_linha_a_cada_10_minutos(self):
        self.relatar()
        with self.assertRaises(ErroRelato) as e:
            self.relatar(quando=AGORA + 4 * MIN)
        self.assertEqual(e.exception.status, 429)
        self.assertIn("6 min", e.exception.mensagem)
        self.assertIn("Linha 3", e.exception.mensagem)
        self.relatar(quando=AGORA + 10 * MIN)                      # passou o intervalo
        self.assertEqual(len(self.ativos(AGORA + 10 * MIN)), 2)

    def test_limite_e_por_linha_e_por_autor(self):
        self.relatar(linha="3")
        self.relatar(linha="9")                                    # outra linha, mesmo autor: pode
        self.relatar(aparelho=B, linha="3")                        # mesma linha, outro autor: pode
        self.assertEqual(len(self.ativos()), 3)

    # ---- expiração
    def test_relato_expira_em_2_horas(self):
        self.relatar()
        self.assertEqual(len(self.ativos(AGORA + timedelta(hours=1, minutes=59))), 1)
        self.assertEqual(self.ativos(AGORA + timedelta(hours=2)), [])
        self.assertEqual(self.repo.listar(), [])                   # e é apagado do repositório

    def test_nao_vota_em_relato_expirado(self):
        r = self.relatar()
        with self.assertRaises(ErroRelato) as e:
            relatos.votar(r.id, B, "ainda", agora=AGORA + timedelta(hours=3), repositorio=self.repo)
        self.assertEqual(e.exception.status, 404)

    def test_lista_filtra_por_linha_e_ordena_do_mais_novo(self):
        self.relatar(aparelho=A, linha="3", quando=AGORA - 20 * MIN)
        self.relatar(aparelho=B, linha="3", quando=AGORA - 5 * MIN)
        self.relatar(aparelho=C, linha="9", quando=AGORA - 1 * MIN)
        tres = self.ativos(linha="3")
        self.assertEqual([x.autor_hash for x in tres], [relatos.autor_hash(B), relatos.autor_hash(A)])
        self.assertEqual(len(self.ativos()), 3)

    # ---- votos
    def test_voto_unico_por_autor(self):
        r = self.relatar()
        relatos.votar(r.id, B, "ainda", agora=AGORA, repositorio=self.repo)
        with self.assertRaises(ErroRelato) as e:
            relatos.votar(r.id, B, "acabou", agora=AGORA, repositorio=self.repo)
        self.assertEqual(e.exception.status, 409)
        atual = self.repo.obter(r.id)
        self.assertEqual((atual.confirmacoes, atual.contestacoes), (1, 0))

    def test_votos_de_autores_diferentes_somam(self):
        r = self.relatar()
        relatos.votar(r.id, B, "ainda", agora=AGORA, repositorio=self.repo)
        relatos.votar(r.id, C, "ainda", agora=AGORA, repositorio=self.repo)
        relatos.votar(r.id, D, "acabou", agora=AGORA, repositorio=self.repo)
        atual = self.repo.obter(r.id)
        self.assertEqual((atual.confirmacoes, atual.contestacoes), (2, 1))

    def test_autor_nao_vota_no_proprio_relato(self):
        r = self.relatar()
        with self.assertRaises(ErroRelato) as e:
            relatos.votar(r.id, A, "ainda", agora=AGORA, repositorio=self.repo)
        self.assertEqual(e.exception.status, 403)
        self.assertEqual(self.repo.obter(r.id).confirmacoes, 0)

    def test_voto_invalido(self):
        r = self.relatar()
        with self.assertRaises(ErroRelato) as e:
            relatos.votar(r.id, B, "talvez", agora=AGORA, repositorio=self.repo)
        self.assertEqual(e.exception.status, 422)

    # ---- sinalização
    def test_tres_sinalizacoes_tiram_o_relato_da_lista(self):
        r = self.relatar()
        for aparelho in (B, C):
            self.assertIsNotNone(relatos.sinalizar(r.id, aparelho, agora=AGORA, repositorio=self.repo))
            self.assertEqual(len(self.ativos()), 1)
        self.assertIsNone(relatos.sinalizar(r.id, D, agora=AGORA, repositorio=self.repo))
        self.assertEqual(self.ativos(), [])

    def test_mesmo_autor_nao_sinaliza_duas_vezes(self):
        r = self.relatar()
        relatos.sinalizar(r.id, B, agora=AGORA, repositorio=self.repo)
        with self.assertRaises(ErroRelato) as e:
            relatos.sinalizar(r.id, B, agora=AGORA, repositorio=self.repo)
        self.assertEqual(e.exception.status, 409)
        self.assertEqual(self.repo.obter(r.id).sinalizacoes, 1)

    def test_relato_sinalizado_nao_entra_na_estimativa(self):
        r1 = self.relatar(aparelho=A)
        self.relatar(aparelho=B)
        for aparelho in (B, C, D):
            relatos.sinalizar(r1.id, aparelho, agora=AGORA, repositorio=self.repo)
        est = relatos.estimativa_por_linha(self.repo.listar(), AGORA)
        self.assertEqual(est[0]["nivel"], "relato")                # sobrou um autor só

    # ---- autor
    def test_hash_do_autor_nao_contem_o_id(self):
        h = relatos.autor_hash(A)
        self.assertEqual(len(h), 12)
        self.assertNotIn(A, h)
        self.assertEqual(h, relatos.autor_hash(A))                 # estável
        self.assertNotEqual(h, relatos.autor_hash(B))
        r = self.relatar()
        self.assertNotIn(A, json.dumps(relatos.para_json(r, AGORA, A)))
        self.assertNotIn(r.autor_hash, json.dumps(relatos.para_json(r, AGORA, A)))   # nem o hash vai para a tela
        self.assertNotIn(A, repr(self.repo.listar()))

    def test_sal_muda_o_hash(self):
        with mock.patch.dict(os.environ, {"RELATOS_SAL": "outro-sal"}):
            outro = relatos.autor_hash(A)
        self.assertNotEqual(outro, relatos.autor_hash(A))

    def test_apelido_vem_do_hash(self):
        h = relatos.autor_hash(A)
        self.assertEqual(relatos.apelido(h), f"Passageiro {h[:4].upper()}")

    # ---- estimativa
    def est(self, quando=AGORA):
        return {e["linha"]: e for e in relatos.estimativa_por_linha(self.repo.listar(), quando)}

    def test_dois_autores_no_mesmo_tipo_viram_alerta(self):
        self.relatar(aparelho=A, tipo="parado")
        self.relatar(aparelho=B, tipo="parado")
        e = self.est()["3"]
        self.assertEqual((e["nivel"], e["tipo_principal"], e["n_autores"], e["n_relatos"]), ("alerta", "parado", 2, 2))
        self.assertEqual(e["ultimo_em"], AGORA.isoformat(timespec="seconds"))

    def test_um_autor_so_nao_vira_alerta(self):
        self.relatar(aparelho=A, tipo="parado")
        e = self.est()["3"]
        self.assertEqual((e["nivel"], e["n_autores"]), ("relato", 1))

    def test_dois_autores_em_tipos_diferentes_nao_viram_alerta(self):
        self.relatar(aparelho=A, tipo="parado")
        self.relatar(aparelho=B, tipo="lotado")
        self.assertEqual(self.est()["3"]["nivel"], "relato")

    def test_normal_nao_conta_para_gravidade(self):
        self.relatar(aparelho=A, tipo="normal")
        self.relatar(aparelho=B, tipo="normal")
        e = self.est()["3"]
        self.assertEqual((e["nivel"], e["tipo_principal"], e["n_calmos"]), ("normal", "normal", 2))
        self.relatar(aparelho=C, tipo="lotado")
        e = self.est()["3"]
        self.assertEqual((e["nivel"], e["tipo_principal"]), ("relato", "lotado"))   # o problema prevalece
        self.assertEqual(e["n_calmos"], 2)

    def test_linha_sem_relato_nao_aparece(self):
        self.relatar(linha="9", tipo="chuva")
        self.assertEqual(set(self.est()), {"9"})

    def test_peso_decai_pela_metade_a_cada_30_minutos(self):
        r = self.relatar()
        self.assertAlmostEqual(relatos.peso_do_relato(r, AGORA), 1.0)
        self.assertAlmostEqual(relatos.peso_do_relato(r, AGORA + 30 * MIN), 0.5)
        self.assertAlmostEqual(relatos.peso_do_relato(r, AGORA + 60 * MIN), 0.25)

    def test_o_mais_recente_vence_o_antigo(self):
        # parado: 2 autores há 90 min; lotado: 2 autores agora. Os dois são alerta, o recente pesa mais.
        self.relatar(aparelho=A, tipo="parado", quando=AGORA - 90 * MIN)
        self.relatar(aparelho=B, tipo="parado", quando=AGORA - 90 * MIN)
        self.relatar(aparelho=C, tipo="lotado")
        self.relatar(aparelho=D, tipo="lotado")
        e = self.est()["3"]
        self.assertEqual((e["nivel"], e["tipo_principal"]), ("alerta", "lotado"))
        self.assertGreater(e["peso"], 1.9)
        antigo = self.est(AGORA + 60 * MIN)["3"]                    # uma hora depois, o peso caiu
        self.assertLess(antigo["peso"], e["peso"] / 3)

    def test_confirmacoes_pesam(self):
        # lotado (2 autores) contra parado (2 autores) com o mesmo horário: as confirmações desempatam.
        a = self.relatar(aparelho=A, tipo="lotado")
        self.relatar(aparelho=B, tipo="lotado")
        self.relatar(aparelho=C, tipo="parado")
        self.relatar(aparelho=D, tipo="parado")
        self.assertEqual(self.est()["3"]["tipo_principal"], "parado")     # empate de peso: o mais grave
        for votante in ("aparelho-eeeeeeee", "aparelho-ffffffff"):
            relatos.votar(a.id, votante, "ainda", agora=AGORA, repositorio=self.repo)
        e = self.est()["3"]
        self.assertEqual(e["tipo_principal"], "lotado")
        self.assertAlmostEqual(e["peso"], (1 + 0.5 * 2) + 1.0)

    def test_contestacoes_reduzem_o_peso_com_piso(self):
        r = self.relatar(aparelho=A)
        for i in range(6):
            relatos.votar(r.id, f"votante-{i:08d}", "acabou", agora=AGORA, repositorio=self.repo)
        self.assertAlmostEqual(relatos.peso_do_relato(self.repo.obter(r.id), AGORA), 0.2)   # nunca abaixo de 0,2

    def test_estimativa_ordena_alertas_primeiro(self):
        self.relatar(aparelho=A, linha="9", tipo="chuva")
        self.relatar(aparelho=A, linha="3", tipo="parado")
        self.relatar(aparelho=B, linha="3", tipo="parado")
        self.assertEqual([e["linha"] for e in relatos.estimativa_por_linha(self.repo.listar(), AGORA)], ["3", "9"])

    def test_estimativa_ignora_expirados(self):
        self.relatar(aparelho=A, tipo="parado")
        self.relatar(aparelho=B, tipo="parado")
        self.assertEqual(relatos.estimativa_por_linha(self.repo.listar(), AGORA + timedelta(hours=2, minutes=1)), [])

    # ---- demonstração
    def test_semeia_3_relatos_de_demonstracao_sem_duplicar(self):
        criados = relatos.semear_demo(agora=AGORA, repositorio=self.repo)
        self.assertEqual(len(criados), 3)
        self.assertTrue(all(r.demo for r in criados))
        self.assertEqual(len(relatos.semear_demo(agora=AGORA, repositorio=self.repo)), 3)
        self.assertEqual(len(self.repo.listar()), 3)
        self.assertEqual(self.est()["3"]["nivel"], "alerta")


class Endpoints(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioMemoria()
        self.relogio = {"agora": AGORA}
        mock.patch.object(relatos, "repo", self.repo).start()
        mock.patch.object(relatos, "_agora", lambda: self.relogio["agora"]).start()
        mock.patch.dict(os.environ, {"DEMO_RELATOS": ""}).start()
        self.http = TestClient(app)

    def tearDown(self):
        mock.patch.stopall()

    def com(self, aparelho):
        return {"X-Device-Id": aparelho}

    def relatar(self, aparelho=A, **corpo):
        corpo = {"linha": "3", "tipo": "lotado", **corpo}
        return self.http.post("/api/relatos", json=corpo, headers=self.com(aparelho))

    def test_sem_cabecalho_da_400_nos_posts(self):
        self.assertEqual(self.http.post("/api/relatos", json={"linha": "3", "tipo": "lotado"}).status_code, 400)
        self.assertEqual(self.http.post("/api/relatos/abc/confirmar", json={"valor": "ainda"}).status_code, 400)
        self.assertEqual(self.http.post("/api/relatos/abc/sinalizar").status_code, 400)
        r = self.http.post("/api/relatos", json={"linha": "3", "tipo": "lotado"}, headers={"X-Device-Id": "curto"})
        self.assertEqual(r.status_code, 400)

    def test_criar_e_listar(self):
        r = self.relatar(estacao_id=um_id_de_estacao())
        self.assertEqual(r.status_code, 201)
        criado = r.json()
        self.assertTrue(criado["meu"])
        self.assertEqual(criado["estacao_nome"], rede.carregar()["por_id"][um_id_de_estacao()]["nome"])
        self.assertTrue(criado["apelido"].startswith("Passageiro "))
        lista = self.http.get("/api/relatos", headers=self.com(A)).json()
        self.assertEqual(lista["total"], 1)
        self.assertEqual(lista["aviso"], relatos.AVISO)
        item = lista["relatos"][0]
        self.assertEqual((item["linha"], item["tipo"], item["meu"], item["demo"], item["ha_min"]), ("3", "lotado", True, False, 0))
        self.assertEqual((item["confirmacoes"], item["contestacoes"]), (0, 0))
        outro = self.http.get("/api/relatos", headers=self.com(B)).json()["relatos"][0]
        self.assertFalse(outro["meu"])
        anonimo = self.http.get("/api/relatos").json()["relatos"][0]       # a leitura não exige cabeçalho
        self.assertFalse(anonimo["meu"])
        self.assertNotIn(A, json.dumps(lista))

    def test_filtro_por_linha_e_validacao(self):
        self.relatar(linha="3")
        self.relatar(linha="9")
        self.assertEqual(self.http.get("/api/relatos?linha=9").json()["total"], 1)
        self.assertEqual(self.http.get("/api/relatos?linha=77").status_code, 422)

    def test_campos_invalidos_da_422_com_mensagem_em_texto(self):
        for corpo in ({"linha": "77", "tipo": "lotado"}, {"linha": "3", "tipo": "briga"}, {"linha": "3"}, {"tipo": "lotado"},
                      {"linha": "3", "tipo": "lotado", "estacao_id": "nada"}):
            r = self.http.post("/api/relatos", json=corpo, headers=self.com(A))
            self.assertEqual(r.status_code, 422, corpo)
            self.assertIsInstance(r.json()["detail"], str)

    def test_limite_de_10_minutos_da_429_com_mensagem(self):
        self.assertEqual(self.relatar().status_code, 201)
        r = self.relatar()
        self.assertEqual(r.status_code, 429)
        self.assertIn("Linha 3", r.json()["detail"])
        self.assertIn("Retry-After", r.headers)
        self.relogio["agora"] = AGORA + 11 * MIN
        self.assertEqual(self.relatar().status_code, 201)

    def test_confirmar_contestar_e_regras(self):
        id_ = self.relatar(aparelho=A).json()["id"]
        proprio = self.http.post(f"/api/relatos/{id_}/confirmar", json={"valor": "ainda"}, headers=self.com(A))
        self.assertEqual(proprio.status_code, 403)
        ok = self.http.post(f"/api/relatos/{id_}/confirmar", json={"valor": "ainda"}, headers=self.com(B))
        self.assertEqual(ok.status_code, 200)
        self.assertEqual((ok.json()["confirmacoes"], ok.json()["meu_voto"]), (1, "ainda"))
        repetido = self.http.post(f"/api/relatos/{id_}/confirmar", json={"valor": "acabou"}, headers=self.com(B))
        self.assertEqual(repetido.status_code, 409)
        self.http.post(f"/api/relatos/{id_}/confirmar", json={"valor": "acabou"}, headers=self.com(C))
        item = self.http.get("/api/relatos", headers=self.com(A)).json()["relatos"][0]
        self.assertEqual((item["confirmacoes"], item["contestacoes"]), (1, 1))
        self.assertEqual(self.http.post(f"/api/relatos/{id_}/confirmar", json={"valor": "x"}, headers=self.com(D)).status_code, 422)
        self.assertEqual(self.http.post("/api/relatos/naoexiste/confirmar", json={"valor": "ainda"}, headers=self.com(D)).status_code, 404)

    def test_sinalizar_tres_vezes_remove_do_feed(self):
        id_ = self.relatar(aparelho=A).json()["id"]
        respostas = [self.http.post(f"/api/relatos/{id_}/sinalizar", headers=self.com(x)).json() for x in (B, C, D)]
        self.assertEqual([r["removido"] for r in respostas], [False, False, True])
        self.assertEqual(self.http.get("/api/relatos").json()["total"], 0)
        self.assertEqual(self.http.post(f"/api/relatos/{id_}/sinalizar", headers=self.com("aparelho-eeeeeeee")).status_code, 404)

    def test_estimativa_traz_o_aviso_fixo(self):
        vazio = self.http.get("/api/relatos/estimativa").json()
        self.assertEqual(vazio["linhas"], [])
        self.assertEqual(vazio["aviso"], "Estimativa por relatos de passageiros, não dado oficial.")
        self.relatar(aparelho=A, tipo="parado")
        self.assertEqual(self.http.get("/api/relatos/estimativa").json()["linhas"][0]["nivel"], "relato")
        self.relatar(aparelho=B, tipo="parado")
        r = self.http.get("/api/relatos/estimativa").json()
        self.assertEqual(r["aviso"], relatos.AVISO)
        self.assertEqual(r["linhas"][0]["nivel"], "alerta")
        self.assertEqual(r["linhas"][0]["n_autores"], 2)

    def test_demo_sem_a_variavel_da_403(self):
        r = self.http.post("/api/relatos/demo")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.repo.listar(), [])

    def test_demo_com_a_variavel_semeia_3_relatos_marcados(self):
        with mock.patch.dict(os.environ, {"DEMO_RELATOS": "1"}):
            r = self.http.post("/api/relatos/demo")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(len(r.json()["relatos"]), 3)
            self.assertEqual(len(self.http.post("/api/relatos/demo").json()["relatos"]), 3)    # sem duplicar
        lista = self.http.get("/api/relatos").json()["relatos"]
        self.assertEqual(len(lista), 3)
        self.assertTrue(all(x["demo"] for x in lista))
        self.assertEqual(self.http.get("/api/relatos/estimativa").json()["linhas"][0]["linha"], "3")

    def test_repositorio_pode_ser_trocado(self):
        outro = RepositorioMemoria()
        relatos.usar_repositorio(outro)                      # mock.patch.object devolve o original no tearDown
        self.relatar()
        self.assertEqual(len(outro.listar()), 1)
        self.assertEqual(self.repo.listar(), [])


if __name__ == "__main__":
    unittest.main()
