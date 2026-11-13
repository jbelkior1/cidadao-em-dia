"""Contas no Supabase (esquema "datempo"), pela API REST (PostgREST), com a chave secreta do servidor.

Mesmo contrato do `RepositorioMemoria` de contas.py. Tabelas em banco/migracoes/0002_datempo_contas.sql.
Erro do banco vira `BancoIndisponivel` (a API responde 503), como nos relatos.
"""
from datetime import datetime, time

import httpx

from sistema.contas import Conta, Preferencias, Rotina
from sistema.relatos_supabase import BancoIndisponivel, _cabecalhos


def _data(texto: str | None) -> datetime | None:
    return datetime.fromisoformat(texto.replace("Z", "+00:00")) if texto else None


def _conta(x: dict) -> Conta:
    return Conta(id=x["id"], usuario=x["usuario"], senha_hash=x["senha_hash"], criado_em=_data(x["criado_em"]),
                 tentativas_falhas=x.get("tentativas_falhas", 0), bloqueado_ate=_data(x.get("bloqueado_ate")))


def _rotina(x: dict) -> Rotina:
    return Rotina(id=x["id"], conta_id=x["conta_id"], nome=x["nome"], origem=x["origem"], destino=x["destino"],
                  horario=time.fromisoformat(x["horario"]), dias=x["dias"])


class RepositorioSupabaseContas:
    def __init__(self, url: str, chave: str, cliente: httpx.Client | None = None) -> None:
        self._http = cliente or httpx.Client(base_url=f"{url}/rest/v1", headers=_cabecalhos(chave), timeout=10)

    def _ok(self, r: httpx.Response) -> httpx.Response:
        if r.status_code >= 400:
            raise BancoIndisponivel(f"Supabase respondeu {r.status_code}: {r.text[:200]}")
        return r

    # --- contas
    def inserir_conta(self, conta: Conta) -> bool:
        r = self._http.post("/contas", headers={"Prefer": "return=minimal"}, json={
            "id": conta.id, "usuario": conta.usuario, "senha_hash": conta.senha_hash, "criado_em": conta.criado_em.isoformat()})
        if r.status_code == 409:          # usuário repetido (unique)
            return False
        self._ok(r)
        return True

    def _uma_conta(self, **filtro: str) -> Conta | None:
        r = self._ok(self._http.get("/contas", params={"select": "*", **{k: f"eq.{v}" for k, v in filtro.items()}}))
        linhas = r.json()
        return _conta(linhas[0]) if linhas else None

    def conta_por_usuario(self, usuario: str) -> Conta | None:
        return self._uma_conta(usuario=usuario)

    def conta_por_id(self, conta_id: str) -> Conta | None:
        return self._uma_conta(id=conta_id)

    def atualizar_tentativas(self, conta_id: str, falhas: int, bloqueado_ate: datetime | None) -> None:
        self._ok(self._http.patch("/contas", params={"id": f"eq.{conta_id}"}, headers={"Prefer": "return=minimal"},
                                  json={"tentativas_falhas": falhas,
                                        "bloqueado_ate": bloqueado_ate.isoformat() if bloqueado_ate else None}))

    def apagar_conta(self, conta_id: str) -> None:       # sessões, preferências e rotinas saem em cascata
        self._ok(self._http.delete("/contas", params={"id": f"eq.{conta_id}"}))

    # --- sessões
    def criar_sessao(self, token_hash: str, conta_id: str, expira_em: datetime) -> None:
        self._ok(self._http.post("/sessoes", headers={"Prefer": "return=minimal"},
                                 json={"token_hash": token_hash, "conta_id": conta_id, "expira_em": expira_em.isoformat()}))

    def conta_da_sessao(self, token_hash: str, agora: datetime) -> str | None:
        r = self._ok(self._http.get("/sessoes", params={"select": "conta_id", "token_hash": f"eq.{token_hash}",
                                                        "expira_em": f"gt.{agora.isoformat()}"}))
        linhas = r.json()
        return linhas[0]["conta_id"] if linhas else None

    def apagar_sessao(self, token_hash: str) -> None:
        self._ok(self._http.delete("/sessoes", params={"token_hash": f"eq.{token_hash}"}))

    def remover_sessoes_vencidas(self, agora: datetime) -> None:
        self._ok(self._http.delete("/sessoes", params={"expira_em": f"lte.{agora.isoformat()}"}))

    # --- preferências
    def preferencias(self, conta_id: str) -> Preferencias:
        r = self._ok(self._http.get("/preferencias", params={"select": "linhas,casa", "conta_id": f"eq.{conta_id}"}))
        linhas = r.json()
        return Preferencias(list(linhas[0]["linhas"] or []), linhas[0]["casa"]) if linhas else Preferencias()

    def salvar_preferencias(self, conta_id: str, prefs: Preferencias) -> None:
        self._ok(self._http.post("/preferencias", params={"on_conflict": "conta_id"},
                                 headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
                                 json={"conta_id": conta_id, "linhas": prefs.linhas, "casa": prefs.casa,
                                       "atualizado_em": datetime.now().astimezone().isoformat()}))

    # --- rotinas
    def rotinas(self, conta_id: str) -> list[Rotina]:
        r = self._ok(self._http.get("/rotinas", params={"select": "*", "conta_id": f"eq.{conta_id}", "order": "horario.asc"}))
        return [_rotina(x) for x in r.json()]

    def inserir_rotina(self, rotina: Rotina) -> None:
        self._ok(self._http.post("/rotinas", headers={"Prefer": "return=minimal"}, json={
            "id": rotina.id, "conta_id": rotina.conta_id, "nome": rotina.nome, "origem": rotina.origem,
            "destino": rotina.destino, "horario": rotina.horario.strftime("%H:%M"), "dias": rotina.dias}))

    def apagar_rotina(self, conta_id: str, rotina_id: str) -> bool:
        r = self._ok(self._http.delete("/rotinas", params={"id": f"eq.{rotina_id}", "conta_id": f"eq.{conta_id}"},
                                       headers={"Prefer": "return=representation"}))
        return bool(r.json())
