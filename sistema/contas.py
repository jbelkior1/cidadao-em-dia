"""Conta básica do Dá Tempo?: usuário e senha, e o que a conta guarda.

A conta é opcional. Sem ela, o app funciona como antes (linhas e estação de casa só no aparelho).
Com ela, minhas linhas, estação de casa e as rotas salvas voltam em qualquer aparelho.

Decisões (pedido do grupo em 13/11: "login e senha básico mesmo", numa tabela nossa):
- Usuário escolhido pela pessoa, sem e-mail e sem nome real: o mínimo de dado pessoal. Usuário que
  pareça CPF ou telefone (8 dígitos ou mais) é recusado pela mesma barreira da conversa.
- Senha só como hash scrypt com sal (biblioteca padrão do Python); comparação em tempo constante.
- Sessão: token aleatório entregue uma vez ao aparelho; o banco guarda só o SHA-256 dele. Vale 30 dias.
- 5 senhas erradas seguidas bloqueiam a conta por 15 minutos (contra tentativa e erro).
- Tabelas no esquema "datempo" (banco/migracoes/0002_datempo_contas.sql), acessadas só pelo servidor.
"""
import hashlib
import hmac
import re
import secrets
import threading
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, time, timedelta, timezone
from typing import Protocol

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from sistema import privacidade
from sistema.mobilidade import rede

router = APIRouter(prefix="/api/conta", tags=["conta"])

USUARIO_VALIDO = re.compile(r"^[a-z0-9_.]{3,30}$")
SENHA_MIN, SENHA_MAX = 8, 128
SESSAO_DIAS = 30
FALHAS_ATE_BLOQUEIO, BLOQUEIO_MIN = 5, 15
MAX_ROTINAS = 10
SCRYPT = {"n": 2 ** 14, "r": 8, "p": 1}


# ------------------------------------------------------------------ modelo

@dataclass
class Conta:
    id: str
    usuario: str
    senha_hash: str
    criado_em: datetime
    tentativas_falhas: int = 0
    bloqueado_ate: datetime | None = None


@dataclass
class Rotina:
    id: str
    conta_id: str
    nome: str
    origem: str
    destino: str
    horario: time
    dias: str = "12345"


@dataclass
class Preferencias:
    linhas: list[str] = field(default_factory=list)
    casa: str | None = None


class ErroConta(Exception):
    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status, self.mensagem = status, mensagem


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------ senha e token

def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(16)
    chave = hashlib.scrypt(senha.encode("utf-8"), salt=sal, dklen=32, **SCRYPT)
    return f"scrypt${SCRYPT['n']}${SCRYPT['r']}${SCRYPT['p']}${sal.hex()}${chave.hex()}"


def conferir_senha(senha: str, guardado: str) -> bool:
    try:
        _, n, r, p, sal, chave = guardado.split("$")
        calculada = hashlib.scrypt(senha.encode("utf-8"), salt=bytes.fromhex(sal), dklen=len(chave) // 2,
                                   n=int(n), r=int(r), p=int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculada.hex(), chave)


_HASH_FALSO = gerar_hash(secrets.token_urlsafe(16))


def hash_do_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ repositório (memória nos testes, Supabase com .env)

class Repositorio(Protocol):
    def inserir_conta(self, conta: Conta) -> bool: ...
    def conta_por_usuario(self, usuario: str) -> Conta | None: ...
    def conta_por_id(self, conta_id: str) -> Conta | None: ...
    def atualizar_tentativas(self, conta_id: str, falhas: int, bloqueado_ate: datetime | None) -> None: ...
    def apagar_conta(self, conta_id: str) -> None: ...
    def criar_sessao(self, token_hash: str, conta_id: str, expira_em: datetime) -> None: ...
    def conta_da_sessao(self, token_hash: str, agora: datetime) -> str | None: ...
    def apagar_sessao(self, token_hash: str) -> None: ...
    def remover_sessoes_vencidas(self, agora: datetime) -> None: ...
    def preferencias(self, conta_id: str) -> Preferencias: ...
    def salvar_preferencias(self, conta_id: str, prefs: Preferencias) -> None: ...
    def rotinas(self, conta_id: str) -> list[Rotina]: ...
    def inserir_rotina(self, rotina: Rotina) -> None: ...
    def apagar_rotina(self, conta_id: str, rotina_id: str) -> bool: ...


class RepositorioMemoria:
    def __init__(self) -> None:
        self._contas: dict[str, Conta] = {}
        self._sessoes: dict[str, tuple[str, datetime]] = {}
        self._prefs: dict[str, Preferencias] = {}
        self._rotinas: dict[str, Rotina] = {}
        self._trava = threading.Lock()

    def inserir_conta(self, conta: Conta) -> bool:
        with self._trava:
            if any(c.usuario == conta.usuario for c in self._contas.values()):
                return False
            self._contas[conta.id] = replace(conta)
            return True

    def conta_por_usuario(self, usuario: str) -> Conta | None:
        return next((replace(c) for c in self._contas.values() if c.usuario == usuario), None)

    def conta_por_id(self, conta_id: str) -> Conta | None:
        c = self._contas.get(conta_id)
        return replace(c) if c else None

    def atualizar_tentativas(self, conta_id: str, falhas: int, bloqueado_ate: datetime | None) -> None:
        if conta_id in self._contas:
            self._contas[conta_id] = replace(self._contas[conta_id], tentativas_falhas=falhas, bloqueado_ate=bloqueado_ate)

    def apagar_conta(self, conta_id: str) -> None:
        with self._trava:
            self._contas.pop(conta_id, None)
            self._prefs.pop(conta_id, None)
            self._sessoes = {k: v for k, v in self._sessoes.items() if v[0] != conta_id}
            self._rotinas = {k: v for k, v in self._rotinas.items() if v.conta_id != conta_id}

    def criar_sessao(self, token_hash: str, conta_id: str, expira_em: datetime) -> None:
        self._sessoes[token_hash] = (conta_id, expira_em)

    def conta_da_sessao(self, token_hash: str, agora: datetime) -> str | None:
        s = self._sessoes.get(token_hash)
        return s[0] if s and s[1] > agora else None

    def apagar_sessao(self, token_hash: str) -> None:
        self._sessoes.pop(token_hash, None)

    def remover_sessoes_vencidas(self, agora: datetime) -> None:
        self._sessoes = {k: v for k, v in self._sessoes.items() if v[1] > agora}

    def preferencias(self, conta_id: str) -> Preferencias:
        p = self._prefs.get(conta_id)
        return Preferencias(list(p.linhas), p.casa) if p else Preferencias()

    def salvar_preferencias(self, conta_id: str, prefs: Preferencias) -> None:
        self._prefs[conta_id] = Preferencias(list(prefs.linhas), prefs.casa)

    def rotinas(self, conta_id: str) -> list[Rotina]:
        return [replace(r) for r in self._rotinas.values() if r.conta_id == conta_id]

    def inserir_rotina(self, rotina: Rotina) -> None:
        self._rotinas[rotina.id] = replace(rotina)

    def apagar_rotina(self, conta_id: str, rotina_id: str) -> bool:
        r = self._rotinas.get(rotina_id)
        if not r or r.conta_id != conta_id:
            return False
        del self._rotinas[rotina_id]
        return True


repo: Repositorio = RepositorioMemoria()


def usar_repositorio(novo: Repositorio) -> None:
    global repo
    repo = novo


# ------------------------------------------------------------------ regras

def _validar_usuario(bruto: str) -> str:
    usuario = (bruto or "").strip().lower()
    if not USUARIO_VALIDO.match(usuario):
        raise ErroConta(422, "Use de 3 a 30 caracteres: letras sem acento, números, ponto ou sublinhado.")
    if privacidade.motivo(usuario):
        raise ErroConta(422, "Não use CPF, telefone ou outro dado pessoal no nome de usuário.")
    return usuario


def _validar_senha(senha: str) -> str:
    if not (SENHA_MIN <= len(senha or "") <= SENHA_MAX):
        raise ErroConta(422, f"A senha precisa ter de {SENHA_MIN} a {SENHA_MAX} caracteres.")
    return senha


def _abrir_sessao(conta_id: str, agora: datetime) -> str:
    repo.remover_sessoes_vencidas(agora)          # a cada login, some com as sessões que já venceram
    token = secrets.token_urlsafe(32)
    repo.criar_sessao(hash_do_token(token), conta_id, agora + timedelta(days=SESSAO_DIAS))
    return token


def cadastrar(usuario: str, senha: str, *, agora: datetime | None = None) -> tuple[Conta, str]:
    agora = agora or agora_utc()
    conta = Conta(id=str(uuid.uuid4()), usuario=_validar_usuario(usuario), senha_hash=gerar_hash(_validar_senha(senha)),
                  criado_em=agora)
    if not repo.inserir_conta(conta):
        raise ErroConta(409, "Esse nome de usuário já existe. Escolha outro.")
    return conta, _abrir_sessao(conta.id, agora)


# Ler, conferir e gravar as falhas numa trava só: sem ela, 40 tentativas em paralelo leriam todas
# "0 falhas" e o bloqueio de 5 erros não valeria. Basta com um processo (a mesma premissa dos relatos).
_TRAVA_LOGIN = threading.Lock()


def entrar(usuario: str, senha: str, *, agora: datetime | None = None) -> tuple[Conta, str]:
    agora = agora or agora_utc()
    mensagem_generica = "Usuário ou senha incorretos."
    usuario = (usuario or "").strip().lower()
    senha = (senha or "")[:SENHA_MAX]
    with _TRAVA_LOGIN:
        conta = repo.conta_por_usuario(usuario) if USUARIO_VALIDO.match(usuario) else None
        if not conta:
            conferir_senha(senha, _HASH_FALSO)      # mesmo custo com ou sem conta: não revela quem existe
            raise ErroConta(401, mensagem_generica)
        if conta.bloqueado_ate and conta.bloqueado_ate > agora:
            conferir_senha(senha, _HASH_FALSO)      # mesmo custo e mesma resposta: o bloqueio não denuncia a conta
            raise ErroConta(401, f"{mensagem_generica} Depois de {FALHAS_ATE_BLOQUEIO} erros, espere {BLOQUEIO_MIN} minutos.")
        if not conferir_senha(senha, conta.senha_hash):
            falhas = conta.tentativas_falhas + 1
            bloqueio = agora + timedelta(minutes=BLOQUEIO_MIN) if falhas >= FALHAS_ATE_BLOQUEIO else None
            repo.atualizar_tentativas(conta.id, 0 if bloqueio else falhas, bloqueio)
            raise ErroConta(401, mensagem_generica)
        if conta.tentativas_falhas or conta.bloqueado_ate:
            repo.atualizar_tentativas(conta.id, 0, None)
    return conta, _abrir_sessao(conta.id, agora)


def conta_do_token(token: str | None, *, agora: datetime | None = None) -> Conta:
    if not token:
        raise ErroConta(401, "Entre na sua conta para continuar.")
    conta_id = repo.conta_da_sessao(hash_do_token(token), agora or agora_utc())
    conta = repo.conta_por_id(conta_id) if conta_id else None
    if not conta:
        raise ErroConta(401, "Sua sessão terminou. Entre de novo.")
    return conta


def _estacao_valida(estacao_id: str | None) -> str | None:
    if estacao_id is None or estacao_id == "":
        return None
    if estacao_id not in rede.carregar()["por_id"]:
        raise ErroConta(422, "Estação desconhecida.")
    return estacao_id


def salvar_preferencias(conta: Conta, linhas: list[str], casa: str | None) -> Preferencias:
    conhecidas = set(rede.carregar()["linhas"])
    limpas = sorted({str(n) for n in linhas if str(n) in conhecidas}, key=lambda n: int(n))[:20]
    prefs = Preferencias(limpas, _estacao_valida(casa))
    repo.salvar_preferencias(conta.id, prefs)
    return prefs


def criar_rotina(conta: Conta, nome: str, origem: str, destino: str, horario: str, dias: str) -> Rotina:
    nome = (nome or "").strip()
    if not 1 <= len(nome) <= 40 or privacidade.motivo(nome):
        raise ErroConta(422, "Dê um nome curto para a rota, sem dado pessoal (ex.: Casa → Trabalho).")
    origem, destino = _estacao_valida(origem), _estacao_valida(destino)
    if not origem or not destino or origem == destino:
        raise ErroConta(422, "Escolha estações de saída e de chegada diferentes.")
    try:
        hora = time.fromisoformat(horario)
    except (TypeError, ValueError):
        raise ErroConta(422, "Horário inválido. Use HH:MM.") from None
    dias = "".join(sorted(set(dias or "")))
    if not re.fullmatch(r"[1-7]{1,7}", dias):
        raise ErroConta(422, "Escolha ao menos um dia da semana.")
    if len(repo.rotinas(conta.id)) >= MAX_ROTINAS:
        raise ErroConta(422, f"Limite de {MAX_ROTINAS} rotas salvas.")
    rotina = Rotina(id=str(uuid.uuid4()), conta_id=conta.id, nome=nome, origem=origem, destino=destino,
                    horario=hora.replace(second=0, microsecond=0), dias=dias)
    repo.inserir_rotina(rotina)
    return rotina


# ------------------------------------------------------------------ API

class Credenciais(BaseModel):
    usuario: str = Field(max_length=60)
    senha: str = Field(max_length=SENHA_MAX)


class NovasPreferencias(BaseModel):
    linhas: list[str] = []
    casa: str | None = None


class NovaRotina(BaseModel):
    nome: str
    origem: str
    destino: str
    horario: str
    dias: str = "12345"


class ConfirmarSenha(BaseModel):
    senha: str = Field(max_length=SENHA_MAX)


def _token(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip() or None
    return None


def _http(e: ErroConta) -> HTTPException:
    return HTTPException(e.status, e.mensagem)


def rotina_json(r: Rotina) -> dict:
    por_id = rede.carregar()["por_id"]
    return {"id": r.id, "nome": r.nome, "origem": r.origem, "destino": r.destino,
            "origem_nome": por_id.get(r.origem, {}).get("nome", r.origem),
            "destino_nome": por_id.get(r.destino, {}).get("nome", r.destino),
            "horario": r.horario.strftime("%H:%M"), "dias": r.dias}


def perfil_json(conta: Conta) -> dict:
    p = repo.preferencias(conta.id)
    return {"usuario": conta.usuario, "linhas": p.linhas, "casa": p.casa,
            "rotinas": [rotina_json(r) for r in sorted(repo.rotinas(conta.id), key=lambda r: r.horario)]}


@router.post("/cadastro", status_code=201)
def rota_cadastro(c: Credenciais) -> dict:
    try:
        conta, token = cadastrar(c.usuario, c.senha)
    except ErroConta as e:
        raise _http(e)
    return {"token": token, "perfil": perfil_json(conta)}


@router.post("/entrar")
def rota_entrar(c: Credenciais) -> dict:
    try:
        conta, token = entrar(c.usuario, c.senha)
    except ErroConta as e:
        raise _http(e)
    return {"token": token, "perfil": perfil_json(conta)}


@router.post("/sair")
def rota_sair(authorization: str | None = Header(None)) -> dict:
    token = _token(authorization)
    if token:
        repo.apagar_sessao(hash_do_token(token))
    return {"ok": True}


@router.get("/eu")
def rota_eu(authorization: str | None = Header(None)) -> dict:
    try:
        return perfil_json(conta_do_token(_token(authorization)))
    except ErroConta as e:
        raise _http(e)


@router.put("/preferencias")
def rota_preferencias(p: NovasPreferencias, authorization: str | None = Header(None)) -> dict:
    try:
        conta = conta_do_token(_token(authorization))
        salvar_preferencias(conta, p.linhas, p.casa)
        return perfil_json(conta)
    except ErroConta as e:
        raise _http(e)


@router.post("/rotinas", status_code=201)
def rota_nova_rotina(r: NovaRotina, authorization: str | None = Header(None)) -> dict:
    try:
        conta = conta_do_token(_token(authorization))
        criar_rotina(conta, r.nome, r.origem, r.destino, r.horario, r.dias)
        return perfil_json(conta)
    except ErroConta as e:
        raise _http(e)


@router.delete("/rotinas/{rotina_id}")
def rota_apagar_rotina(rotina_id: str, authorization: str | None = Header(None)) -> dict:
    try:
        conta = conta_do_token(_token(authorization))
        try:
            rotina_id = str(uuid.UUID(rotina_id))      # forma canônica antes de ir para o filtro do banco
        except ValueError:
            raise ErroConta(404, "Rota não encontrada.") from None
        if not repo.apagar_rotina(conta.id, rotina_id):
            raise ErroConta(404, "Rota não encontrada.")
        return perfil_json(conta)
    except ErroConta as e:
        raise _http(e)


@router.delete("")
def rota_apagar_conta(c: ConfirmarSenha, authorization: str | None = Header(None)) -> dict:
    try:
        conta = conta_do_token(_token(authorization))
        if not conferir_senha(c.senha, conta.senha_hash):
            raise ErroConta(401, "Senha incorreta.")
        repo.apagar_conta(conta.id)
        return {"ok": True}
    except ErroConta as e:
        raise _http(e)
