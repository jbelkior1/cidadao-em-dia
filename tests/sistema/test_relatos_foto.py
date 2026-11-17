"""Foto como evidência no relato: validação, recompressão sem metadados, banco, API e o que a Lia enxerga.

Rodar da raiz do repositório:
    uv run python -m unittest discover -s tests/sistema -v
"""
import base64
import io
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from sistema import assistente, fotos, relatos  # noqa: E402
from sistema.api import app  # noqa: E402
from sistema.relatos import ErroRelato, RepositorioMemoria  # noqa: E402
from sistema.relatos_supabase import BUCKET, RepositorioSupabase  # noqa: E402
from test_relatos_supabase import linha_banco  # noqa: E402

AGORA = datetime(2026, 11, 12, 18, 0, tzinfo=timezone.utc)
A, B = "aparelho-aaaaaaaa", "aparelho-bbbbbbbb"


def imagem(formato="JPEG", tamanho=(800, 600), exif=False, cor=(200, 30, 30)) -> bytes:
    img = Image.new("RGB", tamanho, cor)
    saida = io.BytesIO()
    extra = {}
    if exif:
        e = Image.Exif()
        e[0x010F] = "Fabricante Secreto"                  # Make
        e[0x8825] = {1: "S", 2: (23.0, 33.0, 0.0), 3: "W", 4: (46.0, 38.0, 0.0)}   # GPS
        extra["exif"] = e
    img.save(saida, formato, **extra)
    return saida.getvalue()


def como_base64(dados: bytes, prefixo=False) -> str:
    texto = base64.b64encode(dados).decode()
    return ("data:image/jpeg;base64," + texto) if prefixo else texto


class Processamento(unittest.TestCase):
    def test_aceita_jpeg_png_e_webp_e_devolve_jpeg(self):
        for formato in ("JPEG", "PNG", "WEBP"):
            with self.subTest(formato=formato):
                saida = fotos.processar(imagem(formato))
                self.assertEqual(Image.open(io.BytesIO(saida)).format, "JPEG")

    def test_apaga_metadados_inclusive_localizacao(self):
        original = imagem(exif=True)
        self.assertTrue(Image.open(io.BytesIO(original)).getexif())
        saida = fotos.processar(original)
        self.assertEqual(dict(Image.open(io.BytesIO(saida)).getexif()), {})
        self.assertNotIn(b"Fabricante Secreto", saida)
        self.assertNotIn(b"Exif", saida)

    def test_reduz_foto_grande_para_no_maximo_1280(self):
        saida = Image.open(io.BytesIO(fotos.processar(imagem(tamanho=(4000, 3000)))))
        self.assertEqual(max(saida.size), fotos.LADO_MAXIMO)

    def test_mantem_foto_pequena_sem_aumentar(self):
        saida = Image.open(io.BytesIO(fotos.processar(imagem(tamanho=(320, 200)))))
        self.assertEqual(saida.size, (320, 200))

    def test_recusa_o_que_nao_e_imagem(self):
        for lixo in (b"", b"isto nao e uma imagem", b"%PDF-1.4 ...", b"<svg xmlns='http://www.w3.org/2000/svg'/>", b"GIF89a" + b"0" * 30):
            with self.subTest(lixo=lixo[:12]):
                with self.assertRaises(ErroRelato) as e:
                    fotos.processar(lixo)
                self.assertEqual(e.exception.status, 422)

    def test_recusa_arquivo_grande_demais(self):
        with self.assertRaises(ErroRelato) as e:
            fotos.processar(b"\xff\xd8\xff" + b"0" * (fotos.TAMANHO_MAXIMO + 1))
        self.assertEqual(e.exception.status, 422)

    def test_recusa_imagem_com_pixels_demais(self):
        enorme = imagem("PNG", tamanho=(6000, 6000), cor=(1, 1, 1))
        with self.assertRaises(ErroRelato):
            fotos.processar(enorme)

    def test_decodifica_base64_com_ou_sem_prefixo(self):
        dados = imagem()
        self.assertEqual(fotos.decodificar(como_base64(dados)), dados)
        self.assertEqual(fotos.decodificar(como_base64(dados, prefixo=True)), dados)

    def test_base64_invalido_da_422(self):
        with self.assertRaises(ErroRelato) as e:
            fotos.decodificar("isto não é base64 !!!")
        self.assertEqual(e.exception.status, 422)


class Dominio(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioMemoria()

    def relatar(self, foto, aparelho=A, linha="3"):
        return relatos.criar_relato(aparelho, linha, "alagado", None, foto=foto, agora=AGORA, repositorio=self.repo)

    def test_relato_com_foto_guarda_so_o_jpeg_limpo(self):
        r = self.relatar(imagem(exif=True))
        self.assertTrue(r.tem_foto)
        guardada = self.repo.obter_foto(r.id)
        self.assertEqual(dict(Image.open(io.BytesIO(guardada)).getexif()), {})

    def test_sem_foto_continua_valendo(self):
        r = self.relatar(None)
        self.assertFalse(r.tem_foto)
        self.assertIsNone(self.repo.obter_foto(r.id))

    def test_foto_invalida_nao_cria_relato(self):
        with self.assertRaises(ErroRelato):
            self.relatar(b"nao e imagem")
        self.assertEqual(self.repo.listar(), [])

    def test_intervalo_por_linha_barra_antes_de_gravar_a_foto(self):
        self.relatar(imagem())
        with self.assertRaises(ErroRelato) as e:
            self.relatar(imagem())
        self.assertEqual(e.exception.status, 429)
        self.assertEqual(len(self.repo.listar()), 1)
        self.assertEqual(len(self.repo._fotos), 1)

    def test_json_traz_o_endereco_da_foto_so_quando_tem(self):
        com = relatos.para_json(self.relatar(imagem()), AGORA)
        sem = relatos.para_json(self.relatar(None, aparelho=B, linha="4"), AGORA)
        self.assertTrue(com["tem_foto"])
        self.assertEqual(com["foto_url"], f"/api/relatos/{com['id']}/foto")
        self.assertFalse(sem["tem_foto"])
        self.assertIsNone(sem["foto_url"])

    def test_foto_some_junto_com_o_relato_vencido(self):
        r = self.relatar(imagem())
        self.repo.remover_expirados(AGORA + relatos.VALIDADE + timedelta(minutes=1))
        self.assertIsNone(self.repo.obter_foto(r.id))


class Api(unittest.TestCase):
    def setUp(self):
        self.http = TestClient(app)
        self.repo = RepositorioMemoria()
        patch = mock.patch.object(relatos, "repo", self.repo)
        patch.start()
        self.addCleanup(patch.stop)

    def post(self, aparelho=A, **corpo):
        return self.http.post("/api/relatos", json={"linha": "3", "tipo": "alagado", **corpo}, headers={"X-Device-Id": aparelho})

    def test_envia_e_baixa_a_foto(self):
        r = self.post(foto=como_base64(imagem(), prefixo=True))
        self.assertEqual(r.status_code, 201)
        dados = r.json()
        self.assertTrue(dados["tem_foto"])
        baixada = self.http.get(dados["foto_url"])
        self.assertEqual(baixada.status_code, 200)
        self.assertEqual(baixada.headers["content-type"], "image/jpeg")
        self.assertEqual(baixada.headers["x-content-type-options"], "nosniff")
        self.assertEqual(Image.open(io.BytesIO(baixada.content)).format, "JPEG")

    def test_foto_invalida_da_422_e_nao_cria_relato(self):
        r = self.post(foto=como_base64(b"isto nao e imagem"))
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.http.get("/api/relatos").json()["total"], 0)

    def test_foto_de_relato_inexistente_ou_sem_foto_da_404(self):
        self.assertEqual(self.http.get("/api/relatos/abcdef123456/foto").status_code, 404)
        sem = self.post().json()
        self.assertEqual(self.http.get(f"/api/relatos/{sem['id']}/foto").status_code, 404)

    def test_foto_deixa_de_ser_entregue_depois_de_tres_sinalizacoes(self):
        criado = self.post(foto=como_base64(imagem())).json()
        for n in range(relatos.LIMITE_SINALIZACOES):
            self.http.post(f"/api/relatos/{criado['id']}/sinalizar", headers={"X-Device-Id": f"sinalizador-{n:08d}"})
        self.assertEqual(self.http.get(criado["foto_url"]).status_code, 404)

    def test_foto_deixa_de_ser_entregue_quando_o_relato_vence(self):
        criado = self.post(foto=como_base64(imagem())).json()
        depois = relatos.agora_utc() + relatos.VALIDADE + timedelta(minutes=1)
        with mock.patch.object(relatos, "agora_utc", return_value=depois):
            self.assertEqual(self.http.get(criado["foto_url"]).status_code, 404)

    def test_texto_enorme_no_campo_foto_e_barrado_antes_de_decodificar(self):
        r = self.post(foto="A" * 3_000_000)
        self.assertEqual(r.status_code, 422)


class ApiDoStorage:
    """Faz de conta do Storage do Supabase: guarda objetos num dicionário."""

    def __init__(self, bucket_existe=True):
        self.objetos: dict[str, bytes] = {}
        self.bucket_existe = bucket_existe
        self.pedidos: list[httpx.Request] = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append(pedido)
        caminho, metodo = pedido.url.path, pedido.method
        if caminho.endswith("/storage/v1/bucket") and metodo == "POST":
            self.bucket_existe = True
            return httpx.Response(200, json={"name": BUCKET})
        if f"/object/{BUCKET}/" in caminho:
            nome = caminho.split(f"/object/{BUCKET}/")[1]
            if not self.bucket_existe:
                # resposta real medida no Supabase: HTTP 400 (não 404), com o 404 só dentro do corpo
                return httpx.Response(400, json={"statusCode": "404", "error": "Bucket not found",
                                                 "message": "Bucket not found", "code": "NoSuchBucket"})
            if metodo == "POST":
                self.objetos[nome] = pedido.content
                return httpx.Response(200, json={"Key": f"{BUCKET}/{nome}"})
            if metodo == "GET":
                return httpx.Response(200, content=self.objetos[nome]) if nome in self.objetos else httpx.Response(404, json={"error": "not_found"})
            if metodo == "DELETE":
                self.objetos.pop(nome, None)
                return httpx.Response(200, json={"message": "Successfully deleted"})
        return httpx.Response(500, json={"erro": "caminho inesperado " + caminho})


class ApiDoBanco:
    def __init__(self, linhas=None):
        self.linhas = linhas if linhas is not None else []
        self.pedidos: list[httpx.Request] = []

    def __call__(self, pedido: httpx.Request) -> httpx.Response:
        self.pedidos.append(pedido)
        if pedido.method == "GET":
            return httpx.Response(200, json=self.linhas)
        return httpx.Response(204)


def repositorio_com_storage(linhas=None, bucket_existe=True):
    banco, storage = ApiDoBanco(linhas), ApiDoStorage(bucket_existe)
    rest = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(banco), headers={"apikey": "sb_secret_t"})
    arm = httpx.Client(base_url="https://x.supabase.co/storage/v1", transport=httpx.MockTransport(storage), headers={"apikey": "sb_secret_t"})
    return RepositorioSupabase("https://x.supabase.co", "sb_secret_t", cliente=rest, armazenamento=arm), banco, storage


class NoSupabase(unittest.TestCase):
    JPEG = imagem()

    def test_guarda_le_e_apaga_o_arquivo(self):
        repo, _, storage = repositorio_com_storage()
        repo.guardar_foto("a1b2c3d4e5f6", self.JPEG)
        self.assertEqual(list(storage.objetos), ["a1b2c3d4e5f6.jpg"])
        self.assertEqual(repo.obter_foto("a1b2c3d4e5f6"), self.JPEG)
        repo.apagar_foto("a1b2c3d4e5f6")
        self.assertIsNone(repo.obter_foto("a1b2c3d4e5f6"))

    def test_cria_o_bucket_privado_se_ainda_nao_existir(self):
        repo, _, storage = repositorio_com_storage(bucket_existe=False)
        repo.guardar_foto("a1b2c3d4e5f6", self.JPEG)
        criacao = [p for p in storage.pedidos if p.url.path.endswith("/storage/v1/bucket")][0]
        corpo = json.loads(criacao.content)
        self.assertEqual((corpo["name"], corpo["public"]), (BUCKET, False))
        self.assertEqual(corpo["allowed_mime_types"], ["image/jpeg"])
        self.assertIn("a1b2c3d4e5f6.jpg", storage.objetos)

    def test_relato_grava_e_le_tem_foto(self):
        repo, banco, _ = repositorio_com_storage([linha_banco(tem_foto=True)])
        self.assertTrue(repo.listar()[0].tem_foto)
        r = relatos.Relato(id="a1b2c3d4e5f6", linha="3", estacao_id=None, tipo="alagado", criado_em=AGORA,
                           expira_em=AGORA + timedelta(hours=2), autor_hash="0123456789ab", tem_foto=True)
        repo.inserir(r)
        enviado = [p for p in banco.pedidos if p.method == "POST"][0]
        self.assertTrue(json.loads(enviado.content)["tem_foto"])

    def test_linha_antiga_sem_o_campo_vira_sem_foto(self):
        repo, _, _ = repositorio_com_storage([linha_banco()])
        self.assertFalse(repo.listar()[0].tem_foto)

    def test_limpeza_apaga_arquivo_de_relato_vencido_ou_sinalizado_e_marca_no_banco(self):
        repo, banco, storage = repositorio_com_storage([{"id": "a1b2c3d4e5f6"}, {"id": "0a0a0a0a0a0a"}])
        storage.objetos.update({"a1b2c3d4e5f6.jpg": b"x", "0a0a0a0a0a0a.jpg": b"y"})
        self.assertEqual(repo.remover_expirados(AGORA), 2)
        self.assertEqual(storage.objetos, {})
        consulta = [p for p in banco.pedidos if p.method == "GET"][0].url.params
        self.assertEqual(consulta["tem_foto"], "eq.true")
        self.assertIn("expira_em.lte.", consulta["or"])
        self.assertIn("sinalizacoes.gte.3", consulta["or"])
        marcas = [p for p in banco.pedidos if p.method == "PATCH"]
        self.assertEqual(len(marcas), 2)
        self.assertEqual(json.loads(marcas[0].content), {"tem_foto": False})
        self.assertFalse([p for p in banco.pedidos if p.method == "DELETE"])     # nunca apaga o relato

    def test_limpeza_nao_roda_mais_de_uma_vez_por_minuto(self):
        repo, banco, _ = repositorio_com_storage([])
        repo.remover_expirados(AGORA)
        repo.remover_expirados(AGORA)
        self.assertEqual(len([p for p in banco.pedidos if p.method == "GET"]), 1)


class LiaNaoVe(unittest.TestCase):
    def test_ferramenta_da_lia_nao_leva_foto_nem_endereco_dela(self):
        repo = RepositorioMemoria()
        relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        with mock.patch.object(relatos, "repo", repo), mock.patch.object(relatos, "agora_utc", return_value=AGORA):
            saida = assistente.Sessao(None, datetime(2026, 11, 12, 15, 0)).relatos_dos_passageiros("3")
        texto = json.dumps(saida, ensure_ascii=False)
        self.assertEqual(saida["total_de_relatos"], 1)
        for proibido in ("foto", "jpg", "jpeg", "base64"):
            self.assertNotIn(proibido, texto.lower())


class LimpezaNaoDerrubaNada(unittest.TestCase):
    """A faxina das fotos é best-effort: Storage ou banco com defeito não podem quebrar feed nem criação."""

    def test_falha_do_banco_na_limpeza_so_vai_para_o_log(self):
        rest = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(lambda p: httpx.Response(500, json={})))
        repo = RepositorioSupabase("https://x.supabase.co", "sb_secret_t", cliente=rest)
        with self.assertLogs("sistema.relatos_supabase", level="WARNING"):
            self.assertEqual(repo.remover_expirados(AGORA), 0)

    def test_falha_de_uma_foto_nao_impede_as_outras_e_ela_fica_marcada(self):
        repo, banco, storage = repositorio_com_storage([{"id": "a1b2c3d4e5f6"}, {"id": "0a0a0a0a0a0a"}])
        storage.objetos.update({"a1b2c3d4e5f6.jpg": b"x", "0a0a0a0a0a0a.jpg": b"y"})
        original = storage.__call__

        def com_defeito(pedido):
            if pedido.method == "DELETE" and "a1b2c3d4e5f6" in pedido.url.path:
                return httpx.Response(500, json={"error": "falhou"})
            return original(pedido)

        repo._arm = httpx.Client(base_url="https://x.supabase.co/storage/v1", transport=httpx.MockTransport(com_defeito))
        with self.assertLogs("sistema.relatos_supabase", level="WARNING"):
            self.assertEqual(repo.remover_expirados(AGORA), 1)
        marcados = [p.url.params["id"] for p in banco.pedidos if p.method == "PATCH"]
        self.assertEqual(marcados, ["eq.0a0a0a0a0a0a"])             # a que falhou continua com tem_foto = true

    def test_limpeza_pega_um_lote_por_vez_dos_mais_antigos(self):
        repo, banco, _ = repositorio_com_storage([])
        repo.remover_expirados(AGORA)
        consulta = [p for p in banco.pedidos if p.method == "GET"][0].url.params
        self.assertEqual(consulta["limit"], "20")
        self.assertEqual(consulta["order"], "expira_em.asc")

    def test_objeto_inexistente_no_storage_vira_none_mas_erro_de_verdade_aparece(self):
        repo, _, _ = repositorio_com_storage()
        repo._arm = httpx.Client(base_url="https://x.supabase.co/storage/v1", transport=httpx.MockTransport(
            lambda p: httpx.Response(400, json={"statusCode": "404", "error": "not_found"})))
        self.assertIsNone(repo.obter_foto("a1b2c3d4e5f6"))
        repo._arm = httpx.Client(base_url="https://x.supabase.co/storage/v1", transport=httpx.MockTransport(
            lambda p: httpx.Response(400, json={"error": "Invalid JWT"})))
        with self.assertRaises(RuntimeError):
            repo.obter_foto("a1b2c3d4e5f6")


class FalhaAoGravarNaoDeixaArquivoSolto(unittest.TestCase):
    class RepoQueFalha(RepositorioMemoria):
        def __init__(self, gravou_mesmo_assim=False):
            super().__init__()
            self.gravou_mesmo_assim = gravou_mesmo_assim

        def inserir(self, relato):
            if self.gravou_mesmo_assim:
                super().inserir(relato)           # gravou, mas a resposta se perdeu
            raise RuntimeError("banco caiu")

    def test_apaga_a_foto_quando_o_relato_nao_foi_gravado(self):
        repo = self.RepoQueFalha()
        with self.assertRaises(RuntimeError):
            relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        self.assertEqual(repo._fotos, {})

    def test_mantem_a_foto_quando_o_relato_chegou_ao_banco(self):
        repo = self.RepoQueFalha(gravou_mesmo_assim=True)
        with self.assertRaises(RuntimeError):
            relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        self.assertEqual(len(repo._fotos), 1)

    def test_erro_ao_apagar_nao_esconde_o_erro_original(self):
        repo = self.RepoQueFalha()
        repo.apagar_foto = mock.Mock(side_effect=OSError("storage fora"))
        with self.assertLogs("sistema.relatos", level="WARNING"):
            with self.assertRaises(RuntimeError) as e:
                relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        self.assertEqual(str(e.exception), "banco caiu")


class LimitesDoEnvio(unittest.TestCase):
    def setUp(self):
        self.http = TestClient(app)
        patch = mock.patch.object(relatos, "repo", RepositorioMemoria())
        patch.start()
        self.addCleanup(patch.stop)

    def test_corpo_acima_de_5_mb_e_recusado_com_413_antes_de_ler(self):
        r = self.http.post("/api/relatos", content=b"{}", headers={"X-Device-Id": A, "Content-Type": "application/json",
                                                                   "Content-Length": "5000001"})
        self.assertEqual(r.status_code, 413)

    def test_cooldown_e_conferido_antes_de_processar_a_foto(self):
        repo = RepositorioMemoria()
        relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        with mock.patch.object(fotos, "processar", side_effect=AssertionError("não devia processar")):
            with self.assertRaises(ErroRelato) as e:
                relatos.criar_relato(A, "3", "alagado", None, foto=imagem(), agora=AGORA, repositorio=repo)
        self.assertEqual(e.exception.status, 429)

    def test_limite_de_pixels_foi_reduzido_para_12_milhoes(self):
        self.assertEqual(fotos.PIXELS_MAXIMOS, 12_000_000)

    def test_no_servidor_publico_o_mesmo_ip_tem_limite_de_relatos_por_janela(self):
        from sistema import api, config
        api._relatos_por_ip.clear()
        with mock.patch.object(config, "modo_publico", return_value=True):
            codigos = [self.http.post("/api/relatos", json={"linha": "3", "tipo": "lotado"},
                                      headers={"X-Device-Id": f"aparelho-{n:08d}"}).status_code
                       for n in range(api.MAXIMO_RELATOS_POR_IP + 2)]
        api._relatos_por_ip.clear()
        self.assertEqual(codigos[:api.MAXIMO_RELATOS_POR_IP], [201] * api.MAXIMO_RELATOS_POR_IP)
        self.assertEqual(codigos[api.MAXIMO_RELATOS_POR_IP:], [429, 429])


if __name__ == "__main__":
    unittest.main()
