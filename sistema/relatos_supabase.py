"""Repositório dos relatos no Supabase (esquema "datempo"), pela API REST (PostgREST).

Mesmo contrato do `RepositorioMemoria` em relatos.py. Cada método é uma chamada só:
voto e sinalização usam funções do banco (registrar_voto, registrar_sinalizacao) para gravar
e somar o contador na mesma transação. Tabelas em banco/migracoes/0001_datempo_relatos.sql.

As fotos ficam no Storage do mesmo projeto, num bucket privado só nosso, com o nome "<id do relato>.jpg".
O relato guarda apenas a marca tem_foto. O arquivo é apagado quando o relato vence ou é sinalizado
3 vezes (remover_expirados); o relato em si continua no banco como histórico.
"""
import logging
import time
from datetime import datetime, timezone

import httpx

from sistema import banco
from sistema.relatos import Relato

CAMPOS = "id,linha,estacao_id,tipo,criado_em,expira_em,autor_hash,confirmacoes,contestacoes,sinalizacoes,demo,descricao,tem_foto"
log = logging.getLogger(__name__)
BUCKET = "datempo-relatos"
LOTE_DE_LIMPEZA = 20                  # fotos apagadas por rodada; o resto fica para a rodada seguinte
LIMITE_FOTO_BUCKET = 2_097_152        # 2 MB por arquivo (o app grava JPEG de 1280 px, bem menor)
INTERVALO_LIMPEZA_S = 60              # a limpeza das fotos vencidas roda no máximo uma vez por minuto


def _cabecalhos(chave: str) -> dict:
    c = {"apikey": chave, "Accept-Profile": banco.ESQUEMA, "Content-Profile": banco.ESQUEMA}
    if chave.startswith("eyJ"):          # chave antiga (JWT): vai também no Authorization
        c["Authorization"] = f"Bearer {chave}"
    return c


def _cabecalhos_storage(chave: str) -> dict:
    c = {"apikey": chave}
    if chave.startswith("eyJ"):
        c["Authorization"] = f"Bearer {chave}"
    return c


def _bucket_ausente(r: httpx.Response) -> bool:
    """O Storage do Supabase responde HTTP 400 (não 404) com "Bucket not found" no corpo; aceita os dois."""
    texto = r.text.lower()
    return r.status_code in (400, 404) and ("bucket not found" in texto or "nosuchbucket" in texto)


def _nao_existe(r: httpx.Response) -> bool:
    """Objeto ou bucket inexistente: o Storage usa 404, ou 400 com "not_found"/"Bucket not found" no corpo."""
    texto = r.text.lower()
    return r.status_code == 404 or (r.status_code == 400 and ("not_found" in texto or "bucket not found" in texto or "nosuchbucket" in texto))


def _data(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def _relato(linha: dict) -> Relato:
    return Relato(
        id=linha["id"], linha=linha["linha"], estacao_id=linha.get("estacao_id"), tipo=linha["tipo"],
        criado_em=_data(linha["criado_em"]), expira_em=_data(linha["expira_em"]), autor_hash=linha["autor_hash"],
        confirmacoes=linha.get("confirmacoes", 0), contestacoes=linha.get("contestacoes", 0),
        sinalizacoes=linha.get("sinalizacoes", 0), demo=linha.get("demo", False), descricao=linha.get("descricao") or "",
        tem_foto=bool(linha.get("tem_foto", False)),
        votos={v["autor_hash"]: v["valor"] for v in linha.get("votos") or []},
        sinalizadores={s["autor_hash"] for s in linha.get("sinalizacoes_lista") or []},
    )


class BancoIndisponivel(RuntimeError):
    """O Supabase respondeu com erro. A API transforma em 503, e a Lia segue sem os relatos."""


class RepositorioSupabase:
    def __init__(self, url: str, chave: str, cliente: httpx.Client | None = None,
                 armazenamento: httpx.Client | None = None) -> None:
        self._http = cliente or httpx.Client(base_url=f"{url}/rest/v1", headers=_cabecalhos(chave), timeout=10)
        self._arm = armazenamento or httpx.Client(base_url=f"{url}/storage/v1", headers=_cabecalhos_storage(chave), timeout=20)
        self._ultima_limpeza = float("-inf")

    def _ok(self, r: httpx.Response) -> httpx.Response:
        if r.status_code >= 400:
            raise BancoIndisponivel(f"Supabase respondeu {r.status_code}: {r.text[:200]}")
        return r

    def _selecao(self) -> str:
        return f"{CAMPOS},votos(autor_hash,valor),sinalizacoes_lista:sinalizacoes(autor_hash)"

    def inserir(self, relato: Relato) -> None:
        self._ok(self._http.post("/relatos", headers={"Prefer": "return=minimal"}, json={
            "id": relato.id, "linha": relato.linha, "estacao_id": relato.estacao_id, "tipo": relato.tipo,
            "criado_em": relato.criado_em.isoformat(), "expira_em": relato.expira_em.isoformat(),
            "autor_hash": relato.autor_hash, "demo": relato.demo, "descricao": relato.descricao,
            "tem_foto": relato.tem_foto,
            "confirmacoes": relato.confirmacoes, "contestacoes": relato.contestacoes, "sinalizacoes": relato.sinalizacoes,
        }))

    def obter(self, relato_id: str) -> Relato | None:
        r = self._ok(self._http.get("/relatos", params={"select": self._selecao(), "id": f"eq.{relato_id}"}))
        linhas = r.json()
        return _relato(linhas[0]) if linhas else None

    def listar(self) -> list[Relato]:
        """Só os que ainda não venceram: o histórico fica no banco, mas não precisa vir a cada leitura do feed."""
        agora = datetime.now(timezone.utc).isoformat()
        r = self._ok(self._http.get("/relatos", params={"select": self._selecao(), "expira_em": f"gt.{agora}", "sinalizacoes": "lt.3",
                                                        "order": "criado_em.desc", "limit": "500"}))
        return [_relato(x) for x in r.json()]

    def ultimo_do_autor(self, autor: str, linha: str) -> Relato | None:
        r = self._ok(self._http.get("/relatos", params={
            "select": self._selecao(), "autor_hash": f"eq.{autor}", "linha": f"eq.{linha}", "demo": "eq.false",
            "order": "criado_em.desc", "limit": "1",
        }))
        linhas = r.json()
        return _relato(linhas[0]) if linhas else None

    def registrar_voto(self, relato_id: str, autor: str, valor: str) -> bool:
        r = self._ok(self._http.post("/rpc/registrar_voto", json={"p_relato": relato_id, "p_autor": autor, "p_valor": valor}))
        return r.json() is True

    def registrar_sinalizacao(self, relato_id: str, autor: str) -> bool:
        r = self._ok(self._http.post("/rpc/registrar_sinalizacao", json={"p_relato": relato_id, "p_autor": autor}))
        return r.json() is True

    def remover_expirados(self, agora: datetime) -> int:
        """No banco o relato vencido fica como histórico: só sai do feed (listar filtra por expira_em).
        Já a FOTO é apagada do Storage quando o relato vence ou chega a 3 sinalizações, e o relato passa
        a tem_foto = false. Devolve quantas fotos foram apagadas.

        É uma faxina, não uma etapa obrigatória: roda no máximo uma vez por minuto, apaga até
        LOTE_DE_LIMPEZA por rodada e, se o banco ou o Storage falharem, só registra no log e segue
        (o feed e a criação de relatos não podem cair por causa dela). A foto que falhou fica
        marcada e entra na próxima rodada."""
        if time.monotonic() - self._ultima_limpeza < INTERVALO_LIMPEZA_S:
            return 0
        self._ultima_limpeza = time.monotonic()
        try:
            r = self._ok(self._http.get("/relatos", params={
                "select": "id", "tem_foto": "eq.true", "or": f"(expira_em.lte.{agora.isoformat()},sinalizacoes.gte.3)",
                "order": "expira_em.asc", "limit": str(LOTE_DE_LIMPEZA),
            }))
            pendentes = [linha["id"] for linha in r.json()]
        except (BancoIndisponivel, httpx.HTTPError):
            log.warning("limpeza de fotos: não consegui listar os relatos com foto vencida", exc_info=True)
            return 0
        apagadas = 0
        for relato_id in pendentes:
            try:
                self.apagar_foto(relato_id)
                self._ok(self._http.patch("/relatos", params={"id": f"eq.{relato_id}"}, json={"tem_foto": False}))
                apagadas += 1
            except (BancoIndisponivel, httpx.HTTPError):
                log.warning("limpeza de fotos: falhou no relato %s, tento de novo na próxima rodada", relato_id, exc_info=True)
        return apagadas

    # ---- fotos (Storage)

    def _criar_bucket(self) -> None:
        r = self._arm.post("/bucket", json={"id": BUCKET, "name": BUCKET, "public": False,
                                            "file_size_limit": LIMITE_FOTO_BUCKET, "allowed_mime_types": ["image/jpeg"]})
        if r.status_code >= 400 and "already exists" not in r.text.lower():
            raise BancoIndisponivel(f"Storage não criou o bucket: {r.status_code}: {r.text[:200]}")

    def guardar_foto(self, relato_id: str, jpeg: bytes) -> None:
        for tentativa in (1, 2):
            r = self._arm.post(f"/object/{BUCKET}/{relato_id}.jpg", content=jpeg, headers={"Content-Type": "image/jpeg"})
            if _bucket_ausente(r) and tentativa == 1:            # o bucket ainda não existe: cria uma vez e tenta de novo
                self._criar_bucket()
                continue
            if r.status_code >= 400:
                raise BancoIndisponivel(f"Storage respondeu {r.status_code}: {r.text[:200]}")
            return

    def obter_foto(self, relato_id: str) -> bytes | None:
        r = self._arm.get(f"/object/{BUCKET}/{relato_id}.jpg")
        if _nao_existe(r):
            return None            # objeto (ou bucket) que não existe: sem foto, não é erro
        if r.status_code >= 400:
            raise BancoIndisponivel(f"Storage respondeu {r.status_code}: {r.text[:200]}")
        return r.content

    def apagar_foto(self, relato_id: str) -> None:
        r = self._arm.delete(f"/object/{BUCKET}/{relato_id}.jpg")
        if r.status_code >= 400 and not _nao_existe(r):
            raise BancoIndisponivel(f"Storage respondeu {r.status_code}: {r.text[:200]}")
