"""Avaliações no Supabase (esquema "datempo"), pela API REST (PostgREST), com a chave secreta do servidor.

Mesmo contrato do `RepositorioMemoria` de avaliacoes.py. Tabelas em banco/migracoes/0005_datempo_avaliacoes.sql e 0006 (comentário sem notas).
Erro do banco vira `BancoIndisponivel` (a API responde 503), como nos relatos e nas contas.
"""
from datetime import datetime

import httpx

from sistema.avaliacoes import Avaliacao
from sistema.relatos_supabase import BancoIndisponivel, _cabecalhos

LIMITE_LEITURA = 500


def _linha(a: Avaliacao) -> dict:
    return {"id": a.id, "criada_em": a.criada_em.isoformat(), "autor_hash": a.autor_hash, "perfil": a.perfil,
            "t1_segundos": a.tempos[0], "t2_segundos": a.tempos[1], "t3_segundos": a.tempos[2],
            "t1_acertou": a.acertos[0], "t2_acertou": a.acertos[1], "t3_acertou": a.acertos[2],
            "e1": a.energia[0], "e2": a.energia[1], "e3": a.energia[2], "e4": a.energia[3], "nota_energia": a.nota_energia,
            "f1": a.facilidade[0], "f2": a.facilidade[1], "f3": a.facilidade[2], "f4": a.facilidade[3], "f5": a.facilidade[4],
            "comentario": a.comentario, "sugestao": a.sugestao}


def _avaliacao(x: dict) -> Avaliacao:
    return Avaliacao(id=x["id"], criada_em=datetime.fromisoformat(x["criada_em"].replace("Z", "+00:00")), autor_hash=x["autor_hash"],
                     perfil=x.get("perfil"), tempos=[x.get("t1_segundos"), x.get("t2_segundos"), x.get("t3_segundos")],
                     acertos=[x.get("t1_acertou"), x.get("t2_acertou"), x.get("t3_acertou")],
                     energia=[x.get("e1"), x.get("e2"), x.get("e3"), x.get("e4")], nota_energia=x.get("nota_energia"),
                     facilidade=[x.get("f1"), x.get("f2"), x.get("f3"), x.get("f4"), x.get("f5")], comentario=x.get("comentario"), sugestao=x.get("sugestao"))


class RepositorioSupabaseAvaliacoes:
    def __init__(self, url: str, chave: str, cliente: httpx.Client | None = None) -> None:
        self._http = cliente or httpx.Client(base_url=f"{url}/rest/v1", headers=_cabecalhos(chave), timeout=10)

    def _ok(self, r: httpx.Response) -> httpx.Response:
        if r.status_code >= 400:
            raise BancoIndisponivel(f"Supabase respondeu {r.status_code}: {r.text[:200]}")
        return r

    def inserir(self, a: Avaliacao) -> None:
        self._ok(self._http.post("/avaliacoes", headers={"Prefer": "return=minimal"}, json=_linha(a)))

    def todas(self) -> list[Avaliacao]:
        r = self._ok(self._http.get("/avaliacoes", params={"select": "*", "order": "criada_em.desc", "limit": str(LIMITE_LEITURA)}))
        return [_avaliacao(x) for x in r.json()]

    def contar_do_autor(self, autor: str, desde: datetime) -> int:
        r = self._ok(self._http.get("/avaliacoes", params={"select": "id", "autor_hash": f"eq.{autor}",
                                                           "criada_em": f"gte.{desde.isoformat()}"}))
        return len(r.json())
