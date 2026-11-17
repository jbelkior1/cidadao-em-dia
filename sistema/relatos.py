"""Relatos dos passageiros: o feed "Agora nas linhas" do Dá Tempo?

Quem está na linha toca em campos prontos (linha, o que vê, estação opcional). Não há texto
livre nem foto: assim não entra ofensa, dado pessoal nem instrução escondida para a IA, que
vai ler estes relatos. Ninguém precisa de conta: o aparelho manda um id aleatório no cabeçalho
X-Device-Id e o servidor guarda só um hash dele.

O que sai daqui é uma ESTIMATIVA POR RELATOS DE PASSAGEIROS, não dado oficial. A lotação do
vagão não existe como dado público.

O armazenamento fica atrás do Protocol `Repositorio`: `RepositorioMemoria` (testes e uso local) ou
`RepositorioSupabase` (servidor, com SUPABASE_URL e SUPABASE_SECRET_KEY). No Supabase o relato vencido
continua guardado como histórico; ele só sai do feed.
Todas as funções de domínio recebem `agora` para os testes
controlarem o relógio.
"""
import hashlib
import math
import os
import re
import secrets
import threading
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from typing import Protocol

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from sistema.mobilidade import rede

router = APIRouter(prefix="/api/relatos", tags=["relatos"])

AVISO = "Estimativa por relatos de passageiros, não dado oficial."

VALIDADE = timedelta(hours=2)                 # o relato some do feed depois disso
INTERVALO_POR_LINHA = timedelta(minutes=10)   # um relato por (autor, linha) a cada 10 min
LIMITE_SINALIZACOES = 3                       # com 3 denúncias o relato some da lista
MEIA_VIDA_MIN = 30.0                          # o peso do relato cai pela metade a cada 30 min
PESO_MINIMO = 0.2                             # piso do peso depois dos votos
AUTORES_PARA_ALERTA = 2                       # pessoas diferentes relatando o mesmo tipo


@dataclass(frozen=True)
class Tipo:
    codigo: str
    rotulo: str
    gravidade: int      # 0 = tudo certo, 1 = incômodo, 2 = atrapalha, 3 = grave


TIPOS: dict[str, Tipo] = {t.codigo: t for t in (
    Tipo("lotado", "Lotado", 2),
    Tipo("parado", "Parado", 3),
    Tipo("quebrou", "Quebrou", 3),
    Tipo("chuva", "Chuva", 1),
    Tipo("alagado", "Alagamento", 3),
    Tipo("seguranca", "Segurança", 3),
    Tipo("normal", "Tudo certo", 0),
)}

VOTOS = ("ainda", "acabou")                   # "ainda está assim" e "já acabou"
_ID_APARELHO = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


class ErroRelato(Exception):
    """Erro de regra de negócio, já com o código HTTP e a mensagem para a pessoa."""

    def __init__(self, status: int, mensagem: str, espera_s: int | None = None):
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem
        self.espera_s = espera_s


# ------------------------------------------------------------------ modelo

@dataclass
class Relato:
    id: str
    linha: str
    estacao_id: str | None
    tipo: str
    criado_em: datetime
    expira_em: datetime
    autor_hash: str
    confirmacoes: int = 0       # "ainda está assim"
    contestacoes: int = 0       # "já acabou"
    sinalizacoes: int = 0
    demo: bool = False
    votos: dict[str, str] = field(default_factory=dict)          # autor_hash -> "ainda" | "acabou"
    sinalizadores: set[str] = field(default_factory=set)

    def copia(self) -> "Relato":
        return replace(self, votos=dict(self.votos), sinalizadores=set(self.sinalizadores))


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def autor_hash(id_aparelho: str) -> str:
    """O servidor nunca guarda o id do aparelho: só estes 12 caracteres do hash com sal."""
    sal = os.environ.get("RELATOS_SAL", "da-tempo-relatos-v1")
    return hashlib.sha256((sal + id_aparelho).encode("utf-8")).hexdigest()[:12]


def apelido(hash_autor: str) -> str:
    return f"Passageiro {hash_autor[:4].upper()}"


def esta_ativo(r: Relato, agora: datetime) -> bool:
    return agora < r.expira_em and r.sinalizacoes < LIMITE_SINALIZACOES


# ------------------------------------------------------------------ repositório

class Repositorio(Protocol):
    """O mínimo que o domínio precisa. Cada método deve ser atômico (no Supabase, uma
    instrução ou RPC; aqui, um lock). O que volta é sempre uma cópia."""

    def inserir(self, relato: Relato) -> None: ...
    def obter(self, relato_id: str) -> Relato | None: ...
    def listar(self) -> list[Relato]: ...
    def ultimo_do_autor(self, autor: str, linha: str) -> Relato | None: ...
    def registrar_voto(self, relato_id: str, autor: str, valor: str) -> bool: ...
    def registrar_sinalizacao(self, relato_id: str, autor: str) -> bool: ...
    def remover_expirados(self, agora: datetime) -> int: ...


class RepositorioMemoria:
    def __init__(self) -> None:
        self._dados: dict[str, Relato] = {}
        self._trava = threading.Lock()

    def inserir(self, relato: Relato) -> None:
        with self._trava:
            self._dados[relato.id] = relato.copia()

    def obter(self, relato_id: str) -> Relato | None:
        with self._trava:
            r = self._dados.get(relato_id)
            return r.copia() if r else None

    def listar(self) -> list[Relato]:
        with self._trava:
            return [r.copia() for r in self._dados.values()]

    def ultimo_do_autor(self, autor: str, linha: str) -> Relato | None:
        with self._trava:
            dele = [r for r in self._dados.values() if r.autor_hash == autor and r.linha == linha and not r.demo]
            return max(dele, key=lambda r: r.criado_em).copia() if dele else None

    def registrar_voto(self, relato_id: str, autor: str, valor: str) -> bool:
        """False se este autor já votou neste relato (ou se o relato não existe mais)."""
        with self._trava:
            r = self._dados.get(relato_id)
            if r is None or autor in r.votos:
                return False
            r.votos[autor] = valor
            if valor == "ainda":
                r.confirmacoes += 1
            else:
                r.contestacoes += 1
            return True

    def registrar_sinalizacao(self, relato_id: str, autor: str) -> bool:
        with self._trava:
            r = self._dados.get(relato_id)
            if r is None or autor in r.sinalizadores:
                return False
            r.sinalizadores.add(autor)
            r.sinalizacoes += 1
            return True

    def remover_expirados(self, agora: datetime) -> int:
        with self._trava:
            velhos = [i for i, r in self._dados.items() if agora >= r.expira_em]
            for i in velhos:
                del self._dados[i]
            return len(velhos)


repo: Repositorio = RepositorioMemoria()        # o Supabase troca este objeto


def usar_repositorio(novo: Repositorio) -> None:
    global repo
    repo = novo


def _repo(r: Repositorio | None) -> Repositorio:
    return r if r is not None else repo


_trava_criacao = threading.Lock()       # confere o intervalo e grava sem corrida (um processo só)


# ------------------------------------------------------------------ regras

def _validar_linha(linha: str | None) -> str:
    linhas = rede.carregar()["linhas"]
    if not isinstance(linha, str) or linha not in linhas:
        raise ErroRelato(422, "Escolha uma linha da lista.")
    return linha


def _validar_estacao(estacao_id: str | None) -> str | None:
    if estacao_id in (None, ""):
        return None
    if not isinstance(estacao_id, str) or estacao_id not in rede.carregar()["por_id"]:
        raise ErroRelato(422, "Estação desconhecida.")
    return estacao_id


def criar_relato(id_aparelho: str, linha: str | None, tipo: str | None, estacao_id: str | None = None, *,
                 agora: datetime | None = None, repositorio: Repositorio | None = None) -> Relato:
    agora = agora or agora_utc()
    r = _repo(repositorio)
    linha = _validar_linha(linha)
    if tipo not in TIPOS:
        raise ErroRelato(422, "Escolha o que você está vendo na lista.")
    estacao_id = _validar_estacao(estacao_id)
    autor = autor_hash(id_aparelho)
    with _trava_criacao:
        r.remover_expirados(agora)
        anterior = r.ultimo_do_autor(autor, linha)
        if anterior is not None and agora - anterior.criado_em < INTERVALO_POR_LINHA:
            falta = INTERVALO_POR_LINHA - (agora - anterior.criado_em)
            minutos = max(1, math.ceil(falta.total_seconds() / 60))
            raise ErroRelato(429, f"Você já relatou na Linha {linha} há pouco. "
                                  f"Dá para relatar de novo nesta linha em {minutos} min.", espera_s=math.ceil(falta.total_seconds()))
        novo = Relato(id=secrets.token_hex(6), linha=linha, estacao_id=estacao_id, tipo=tipo, criado_em=agora,
                      expira_em=agora + VALIDADE, autor_hash=autor)
        r.inserir(novo)
    return novo


def _relato_ativo(relato_id: str, agora: datetime, repositorio: Repositorio | None) -> Relato:
    relato = _repo(repositorio).obter(relato_id)
    if relato is None or not esta_ativo(relato, agora):
        raise ErroRelato(404, "Este relato não está mais no feed.")
    return relato


def votar(relato_id: str, id_aparelho: str, valor: str | None, *, agora: datetime | None = None,
          repositorio: Repositorio | None = None) -> Relato:
    agora = agora or agora_utc()
    if valor not in VOTOS:
        raise ErroRelato(422, "Voto inválido: use \"ainda\" ou \"acabou\".")
    relato = _relato_ativo(relato_id, agora, repositorio)
    autor = autor_hash(id_aparelho)
    if relato.autor_hash == autor:
        raise ErroRelato(403, "Você não pode votar no seu próprio relato.")
    if not _repo(repositorio).registrar_voto(relato_id, autor, valor):
        raise ErroRelato(409, "Você já votou neste relato.")
    return _relato_ativo(relato_id, agora, repositorio)


def sinalizar(relato_id: str, id_aparelho: str, *, agora: datetime | None = None,
              repositorio: Repositorio | None = None) -> Relato | None:
    """Denuncia o relato. Devolve o relato atualizado, ou None se esta denúncia o tirou da lista."""
    agora = agora or agora_utc()
    _relato_ativo(relato_id, agora, repositorio)
    if not _repo(repositorio).registrar_sinalizacao(relato_id, autor_hash(id_aparelho)):
        raise ErroRelato(409, "Você já sinalizou este relato.")
    atual = _repo(repositorio).obter(relato_id)
    return atual if atual is not None and esta_ativo(atual, agora) else None


def listar_ativos(*, linha: str | None = None, agora: datetime | None = None,
                  repositorio: Repositorio | None = None) -> list[Relato]:
    """Ativos (não expirados, com menos de 3 sinalizações), os mais novos primeiro."""
    agora = agora or agora_utc()
    r = _repo(repositorio)
    r.remover_expirados(agora)
    ativos = [x for x in r.listar() if esta_ativo(x, agora) and (linha is None or x.linha == linha)]
    return sorted(ativos, key=lambda x: x.criado_em, reverse=True)


# ------------------------------------------------------------------ estimativa

def peso_do_relato(r: Relato, agora: datetime) -> float:
    """Decaimento exponencial (meia-vida de 30 min) vezes o efeito dos votos (mínimo 0,2)."""
    idade_min = max(0.0, (agora - r.criado_em).total_seconds() / 60)
    decaimento = 0.5 ** (idade_min / MEIA_VIDA_MIN)
    votos = max(PESO_MINIMO, 1 + 0.5 * r.confirmacoes - 0.5 * r.contestacoes)
    return decaimento * votos


def estimativa_por_linha(relatos: list[Relato], agora: datetime) -> list[dict]:
    """Uma entrada por linha que tem relato ativo. Linha sem relato não aparece (sem dado não é "normal").

    - "normal" não conta para a gravidade; só vira nível "normal" quando é tudo o que a linha tem.
    - "alerta" exige pelo menos 2 autores diferentes relatando o MESMO tipo.
    - tipo_principal: entre os tipos em alerta (se houver) ou entre todos os de problema, o de maior peso
      (empate: o mais grave). n_relatos, n_autores e ultimo_em dizem respeito a esse tipo.
    """
    por_linha: dict[str, list[Relato]] = {}
    for r in relatos:
        if esta_ativo(r, agora):
            por_linha.setdefault(r.linha, []).append(r)

    saida = []
    for linha, da_linha in por_linha.items():
        problemas = [r for r in da_linha if r.tipo != "normal"]
        calmos = [r for r in da_linha if r.tipo == "normal"]
        grupos: dict[str, list[Relato]] = {}
        for r in (problemas or calmos):
            grupos.setdefault(r.tipo, []).append(r)
        pesos = {t: sum(peso_do_relato(r, agora) for r in rs) for t, rs in grupos.items()}

        em_alerta = [t for t, rs in grupos.items() if t != "normal" and len({r.autor_hash for r in rs}) >= AUTORES_PARA_ALERTA]
        candidatos = em_alerta or list(grupos)
        principal = max(candidatos, key=lambda t: (round(pesos[t], 9), TIPOS[t].gravidade))
        do_tipo = grupos[principal]
        saida.append({
            "linha": linha,
            "nivel": "alerta" if em_alerta else ("relato" if problemas else "normal"),
            "tipo_principal": principal,
            "tipo_rotulo": TIPOS[principal].rotulo,
            "n_relatos": len(do_tipo),
            "n_autores": len({r.autor_hash for r in do_tipo}),
            "n_calmos": len({r.autor_hash for r in calmos}),
            "peso": round(pesos[principal], 3),
            "ultimo_em": max(r.criado_em for r in do_tipo).isoformat(timespec="seconds"),
        })
    ordem = {"alerta": 0, "relato": 1, "normal": 2}
    return sorted(saida, key=lambda e: (ordem[e["nivel"]], -e["peso"], e["linha"]))


# ------------------------------------------------------------------ saída em JSON

def para_json(r: Relato, agora: datetime, id_aparelho: str | None = None) -> dict:
    eu = autor_hash(id_aparelho) if id_aparelho else None
    estacao = rede.carregar()["por_id"].get(r.estacao_id) if r.estacao_id else None
    saida = {
        "id": r.id,
        "linha": r.linha,
        "tipo": r.tipo,
        "tipo_rotulo": TIPOS[r.tipo].rotulo,
        "estacao_id": r.estacao_id,
        "criado_em": r.criado_em.isoformat(timespec="seconds"),
        "expira_em": r.expira_em.isoformat(timespec="seconds"),
        "ha_min": max(0, int((agora - r.criado_em).total_seconds() // 60)),
        "apelido": apelido(r.autor_hash),
        "meu": eu is not None and r.autor_hash == eu,
        "meu_voto": r.votos.get(eu) if eu else None,
        "confirmacoes": r.confirmacoes,
        "contestacoes": r.contestacoes,
        "sinalizacoes": r.sinalizacoes,
        "demo": r.demo,
    }
    if estacao:
        saida["estacao_nome"] = estacao["nome"]
    return saida


# ------------------------------------------------------------------ demonstração

#: Uma manhã de pico com chuva na zona leste, para o sistema não aparecer vazio em demonstração.
#: (aparelho fictício, linha, tipo, estação, minutos atrás, votos de outros aparelhos)
#: As estações são reais (ids do rede.json), para os relatos aparecerem também no mapa.
DEMO_RELATOS: tuple[tuple[str, str, str, str | None, int, tuple[tuple[str, str], ...]], ...] = (
    # Linha 3-Vermelha: três pessoas, vira alerta de lotação
    ("demo-ana", "3", "lotado", "18869", 6, (("demo-caio", "ainda"), ("demo-bia", "ainda"))),      # Sé
    ("demo-bia", "3", "lotado", "1010054", 13, (("demo-ana", "ainda"),)),                          # Brás
    ("demo-caio", "3", "lotado", "6714561", 27, ()),                                               # República
    # Linha 11-Coral: duas pessoas, trem parado
    ("demo-duda", "11", "parado", "18895", 9, (("demo-eli", "ainda"), ("demo-ana", "ainda"))),     # Guaianases
    ("demo-eli", "11", "parado", "18940", 21, ()),                                                 # Luz
    # Linha 9-Esmeralda: alagamento perto da estação
    ("demo-fabio", "9", "alagado", "18906", 16, (("demo-gi", "ainda"),)),                           # Santo Amaro
    ("demo-gi", "9", "alagado", "18966", 34, ()),                                                   # Pinheiros
    # Linha 10-Turquesa: porta quebrada
    ("demo-hugo", "10", "quebrou", "18927", 24, (("demo-ivo", "ainda"),)),                          # Tamanduateí
    ("demo-ivo", "10", "quebrou", "1010053", 41, ()),                                               # Brás
    # Linhas com um relato só: aparecem no feed, mas não viram alerta
    ("demo-joana", "8", "lotado", "18960", 11, ()),                                                 # Osasco
    ("demo-kaue", "1", "seguranca", "18882", 38, ()),                                               # Tucuruvi
    ("demo-lia", "12", "chuva", "18987", 19, (("demo-joana", "ainda"),)),                           # Brás
    ("demo-nina", "2", "lotado", "18861", 62, (("demo-kaue", "acabou"), ("demo-hugo", "acabou"))),  # Paraíso, já passou
    # Linha 4-Amarela: quem passou por lá diz que está tudo certo
    ("demo-ot", "4", "normal", "2600672", 8, ()),                                                   # Paulista
    ("demo-paulo", "4", "normal", "6311287", 29, ()),                                               # Pinheiros
)


def relatos_de_demo(agora: datetime, repositorio: Repositorio | None = None) -> list[Relato]:
    return [x for x in _repo(repositorio).listar() if x.demo and esta_ativo(x, agora)]


def limpar_demo(*, repositorio: Repositorio | None = None) -> int:
    """Tira do feed os relatos de demonstração (sinaliza até sumirem). Devolve quantos saíram."""
    r = _repo(repositorio)
    fora = 0
    for x in r.listar():
        if not x.demo:
            continue
        for n in range(LIMITE_SINALIZACOES):
            r.registrar_sinalizacao(x.id, f"ffffffffff{n:02d}")      # autor de limpeza (12 hex, como os outros)
        fora += 1
    return fora


def semear_demo(*, agora: datetime | None = None, repositorio: Repositorio | None = None) -> list[Relato]:
    """Enche o feed com a cena de demonstração. Não duplica enquanto os relatos de demo estão ativos."""
    agora = agora or agora_utc()
    r = _repo(repositorio)
    r.remover_expirados(agora)
    existentes = relatos_de_demo(agora, repositorio)
    if existentes:
        return existentes
    criados = []
    for aparelho, linha, tipo, estacao, atras, votos in DEMO_RELATOS:
        criado = agora - timedelta(minutes=atras)
        novo = Relato(id=secrets.token_hex(6), linha=linha, estacao_id=estacao, tipo=tipo, criado_em=criado,
                      expira_em=criado + VALIDADE, autor_hash=autor_hash(aparelho), demo=True)
        r.inserir(novo)
        for votante, valor in votos:
            r.registrar_voto(novo.id, autor_hash(votante), valor)
        criados.append(r.obter(novo.id) or novo)
    return criados


# ------------------------------------------------------------------ endpoints

class NovoRelato(BaseModel):
    linha: str | None = None
    tipo: str | None = None
    estacao_id: str | None = None


class Voto(BaseModel):
    valor: str | None = None


def _agora() -> datetime:
    return agora_utc()


def _aparelho_obrigatorio(x_device_id: str | None) -> str:
    valor = (x_device_id or "").strip()
    if not valor:
        raise HTTPException(400, "Falta o cabeçalho X-Device-Id (o id do aparelho).")
    if not _ID_APARELHO.match(valor):
        raise HTTPException(400, "O cabeçalho X-Device-Id é inválido.")
    return valor


def _aparelho_opcional(x_device_id: str | None) -> str | None:
    valor = (x_device_id or "").strip()
    return valor if _ID_APARELHO.match(valor) else None


def _como_http(e: ErroRelato) -> HTTPException:
    cabecalhos = {"Retry-After": str(e.espera_s)} if e.espera_s else None
    return HTTPException(e.status, e.mensagem, headers=cabecalhos)


@router.get("")
def listar(linha: str | None = Query(None), x_device_id: str | None = Header(None)) -> dict:
    if linha is not None and linha not in rede.carregar()["linhas"]:
        raise HTTPException(422, "Linha desconhecida.")
    agora = _agora()
    aparelho = _aparelho_opcional(x_device_id)
    relatos = [para_json(r, agora, aparelho) for r in listar_ativos(linha=linha, agora=agora)]
    return {"relatos": relatos, "total": len(relatos), "aviso": AVISO}


@router.post("", status_code=201)
def criar(corpo: NovoRelato, x_device_id: str | None = Header(None)) -> dict:
    aparelho = _aparelho_obrigatorio(x_device_id)
    agora = _agora()
    try:
        r = criar_relato(aparelho, corpo.linha, corpo.tipo, corpo.estacao_id, agora=agora)
    except ErroRelato as e:
        raise _como_http(e)
    return para_json(r, agora, aparelho)


@router.get("/estimativa")
def estimativa() -> dict:
    agora = _agora()
    repo.remover_expirados(agora)
    return {"linhas": estimativa_por_linha(repo.listar(), agora), "gerado_em": agora.isoformat(timespec="seconds"), "aviso": AVISO}


def _demo_ligada() -> None:
    if os.environ.get("DEMO_RELATOS") != "1":
        raise HTTPException(403, "Os relatos de demonstração estão desligados neste servidor.")


@router.post("/demo")
def demo() -> dict:
    _demo_ligada()
    agora = _agora()
    relatos = semear_demo(agora=agora)
    return {"relatos": [para_json(r, agora) for r in relatos], "aviso": AVISO}


@router.delete("/demo")
def apagar_demo() -> dict:
    _demo_ligada()
    return {"removidos": limpar_demo()}


@router.post("/{relato_id}/confirmar")
def confirmar(relato_id: str, corpo: Voto, x_device_id: str | None = Header(None)) -> dict:
    aparelho = _aparelho_obrigatorio(x_device_id)
    agora = _agora()
    try:
        r = votar(relato_id, aparelho, corpo.valor, agora=agora)
    except ErroRelato as e:
        raise _como_http(e)
    return para_json(r, agora, aparelho)


@router.post("/{relato_id}/sinalizar")
def sinalizar_relato(relato_id: str, x_device_id: str | None = Header(None)) -> dict:
    aparelho = _aparelho_obrigatorio(x_device_id)
    agora = _agora()
    try:
        r = sinalizar(relato_id, aparelho, agora=agora)
    except ErroRelato as e:
        raise _como_http(e)
    return {"ok": True, "removido": r is None}
