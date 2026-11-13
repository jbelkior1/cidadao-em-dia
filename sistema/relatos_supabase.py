"""Repositório dos relatos no Supabase (esquema "datempo"), pela API REST (PostgREST).

Mesmo contrato do `RepositorioMemoria` em relatos.py. Cada método é uma chamada só:
voto e sinalização usam funções do banco (registrar_voto, registrar_sinalizacao) para gravar
e somar o contador na mesma transação. Tabelas em banco/migracoes/0001_datempo_relatos.sql.
"""
from datetime import datetime

import httpx

from sistema import banco
from sistema.relatos import Relato

CAMPOS = "id,linha,estacao_id,tipo,criado_em,expira_em,autor_hash,confirmacoes,contestacoes,sinalizacoes,demo"


def _cabecalhos(chave: str) -> dict:
    c = {"apikey": chave, "Accept-Profile": banco.ESQUEMA, "Content-Profile": banco.ESQUEMA}
    if chave.startswith("eyJ"):          # chave antiga (JWT): vai também no Authorization
        c["Authorization"] = f"Bearer {chave}"
    return c


def _data(texto: str) -> datetime:
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def _relato(linha: dict) -> Relato:
    return Relato(
        id=linha["id"], linha=linha["linha"], estacao_id=linha.get("estacao_id"), tipo=linha["tipo"],
        criado_em=_data(linha["criado_em"]), expira_em=_data(linha["expira_em"]), autor_hash=linha["autor_hash"],
        confirmacoes=linha.get("confirmacoes", 0), contestacoes=linha.get("contestacoes", 0),
        sinalizacoes=linha.get("sinalizacoes", 0), demo=linha.get("demo", False),
        votos={v["autor_hash"]: v["valor"] for v in linha.get("votos") or []},
        sinalizadores={s["autor_hash"] for s in linha.get("sinalizacoes_lista") or []},
    )


class BancoIndisponivel(RuntimeError):
    """O Supabase respondeu com erro. A API transforma em 503, e a Lia segue sem os relatos."""


class RepositorioSupabase:
    def __init__(self, url: str, chave: str, cliente: httpx.Client | None = None) -> None:
        self._http = cliente or httpx.Client(base_url=f"{url}/rest/v1", headers=_cabecalhos(chave), timeout=10)

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
            "autor_hash": relato.autor_hash, "demo": relato.demo,
            "confirmacoes": relato.confirmacoes, "contestacoes": relato.contestacoes, "sinalizacoes": relato.sinalizacoes,
        }))

    def obter(self, relato_id: str) -> Relato | None:
        r = self._ok(self._http.get("/relatos", params={"select": self._selecao(), "id": f"eq.{relato_id}"}))
        linhas = r.json()
        return _relato(linhas[0]) if linhas else None

    def listar(self) -> list[Relato]:
        r = self._ok(self._http.get("/relatos", params={"select": self._selecao(), "order": "criado_em.desc", "limit": "500"}))
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
        r = self._ok(self._http.delete("/relatos", params={"expira_em": f"lte.{agora.isoformat()}"},
                                       headers={"Prefer": "return=representation"}))
        return len(r.json())
