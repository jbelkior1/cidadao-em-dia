"""Avaliação de quem usou o sistema (página "Avaliação usuários" e formulário "Avaliar o Dá Tempo?").

Uma avaliação é o teste guiado de uma pessoa: as 3 tarefas da PAI (tempo até achar e se a resposta escolhida
estava certa), as 4 situações de energia da SERS (entendeu: sim, em parte, não) com uma nota de 1 a 5, as
5 perguntas de facilidade (1 a 5), um comentário e uma sugestão. Os números alimentam os relatórios de
teste com usuários da PAI, da SERS e da PCP.

Sem dado pessoal: ninguém se identifica, o comentário e a sugestão passam pela mesma barreira da Lia
(privacidade.motivo) e o servidor guarda só o hash do id aleatório do aparelho, para limitar envios
(o mesmo celular pode passar de mão em mão num teste, por isso o limite é de 10 por hora, não 1).

Repositório em memória nos testes e no computador local; no Supabase (esquema datempo) quando o .env tem as
chaves. Tabela em banco/migracoes/0005_datempo_avaliacoes.sql.
"""
import re
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Literal, Protocol

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from sistema import privacidade
from sistema.relatos import _aparelho_obrigatorio, autor_hash

router = APIRouter(prefix="/api/avaliacoes", tags=["avaliacoes"])

PERFIS = ("familia", "faculdade", "trabalho", "conhecido", "outro")
ROTULO_PERFIL = {"familia": "Família", "faculdade": "Faculdade", "trabalho": "Trabalho", "conhecido": "Conhecido", "outro": "Outro"}
ENTENDEU = ("sim", "em parte", "nao")
LIMITE_POR_HORA = 10
TEMPO_MAXIMO_S = 300
CACHE_RESUMO_S = 30                   # a página pública não lê o banco a cada visita
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(com|br|net|org|io|ly|me)\b", re.IGNORECASE)
_cache: dict = {"quando": 0.0, "dados": None}

# As 3 tarefas da PAI (entregas/pai/TESTES_USUARIOS.md) e as 4 situações de energia da SERS
# (entregas/sers/TESTES_USUARIOS.md), com o mesmo texto que a pessoa lê no formulário.
TAREFAS = [
    "Descobrir como pedir a declaração de atraso de uma viagem de metrô feita hoje",
    "Descobrir se uma pessoa de 67 anos paga o metrô e o que ela precisa mostrar",
    "Descobrir onde procurar uma mochila esquecida no trem da CPTM",
]
SITUACOES = [
    "Pedir à Lia uma viagem e abrir \"Segurança nas estações e energia\": quanto CO₂ e quanto custa de trilho e de carro",
    "Saber qual modo emite menos na viagem",
    "Entender por que o trilho é a alternativa renovável",
    "Entender que a conta é uma estimativa por média, não a medição da viagem",
]
PERGUNTAS = [
    "Foi fácil fazer a pergunta.",
    "A resposta foi clara.",
    "Eu confiaria na resposta para agir (sabendo que devo confirmar no canal oficial).",
    "Ficou claro de onde veio a informação.",
    "Eu usaria o Dá Tempo? de novo.",
]


@dataclass
class Avaliacao:
    id: str
    criada_em: datetime
    autor_hash: str
    perfil: str | None
    tempos: list[int | None]          # 3 tarefas; None = não achou em 5 minutos
    acertos: list[bool | None]        # 3 tarefas; None = não respondeu
    energia: list[str | None]         # 4 situações: "sim", "em parte", "nao" ou None (pulou)
    nota_energia: int | None
    facilidade: list[int]             # 5 notas de 1 a 5
    comentario: str | None = None
    sugestao: str | None = None
    extra: dict = field(default_factory=dict)


class ErroAvaliacao(Exception):
    def __init__(self, status: int, mensagem: str) -> None:
        super().__init__(mensagem)
        self.status = status
        self.mensagem = mensagem


# ------------------------------------------------------------------ repositório

class Repositorio(Protocol):
    def inserir(self, a: Avaliacao) -> None: ...
    def todas(self) -> list[Avaliacao]: ...
    def contar_do_autor(self, autor: str, desde: datetime) -> int: ...


class RepositorioMemoria:
    def __init__(self) -> None:
        self._dados: list[Avaliacao] = []
        self._trava = threading.Lock()

    def inserir(self, a: Avaliacao) -> None:
        with self._trava:
            self._dados.append(a)

    def todas(self) -> list[Avaliacao]:
        return sorted(self._dados, key=lambda a: a.criada_em, reverse=True)

    def contar_do_autor(self, autor: str, desde: datetime) -> int:
        return sum(1 for a in self._dados if a.autor_hash == autor and a.criada_em >= desde)


repo: Repositorio = RepositorioMemoria()


def usar_repositorio(novo: Repositorio) -> None:
    global repo
    repo = novo
    _cache["dados"] = None


# ------------------------------------------------------------------ regras

def _texto(valor: str | None, maximo: int, campo: str) -> str | None:
    texto = " ".join((valor or "").split())
    if not texto:
        return None
    if len(texto) > maximo:
        raise ErroAvaliacao(422, f"O {campo} pode ter até {maximo} caracteres.")
    if privacidade.motivo(texto):
        raise ErroAvaliacao(422, f"O {campo} parece ter dado pessoal. {privacidade.AVISO}")
    if LINK.search(texto):
        raise ErroAvaliacao(422, f"O {campo} não pode ter link.")
    return texto


def registrar(id_aparelho: str, perfil: str | None, tempos: list[int | None], acertos: list[bool | None],
              energia: list[str | None], nota_energia: int | None, facilidade: list[int],
              comentario: str | None = None, sugestao: str | None = None, agora: datetime | None = None) -> Avaliacao:
    agora = agora or datetime.now(timezone.utc)
    if perfil is not None and perfil not in PERFIS:
        raise ErroAvaliacao(422, "Perfil desconhecido.")
    if len(tempos) != 3 or len(acertos) != 3 or len(energia) != 4 or len(facilidade) != 5:
        raise ErroAvaliacao(422, "A avaliação está incompleta.")
    if any(t is not None and not 0 <= t <= TEMPO_MAXIMO_S for t in tempos):
        raise ErroAvaliacao(422, "Tempo de tarefa fora do esperado.")
    if any(e is not None and e not in ENTENDEU for e in energia):
        raise ErroAvaliacao(422, "Resposta de energia desconhecida.")
    if nota_energia is not None and not 1 <= nota_energia <= 5:
        raise ErroAvaliacao(422, "A nota de energia vai de 1 a 5.")
    if any(not 1 <= f <= 5 for f in facilidade):
        raise ErroAvaliacao(422, "As notas de facilidade vão de 1 a 5.")
    comentario = _texto(comentario, 500, "comentário")
    sugestao = _texto(sugestao, 300, "sugestão")
    autor = autor_hash(id_aparelho)
    if repo.contar_do_autor(autor, agora - timedelta(hours=1)) >= LIMITE_POR_HORA:
        raise ErroAvaliacao(429, "Muitas avaliações seguidas deste aparelho. Espere um pouco e tente de novo.")
    a = Avaliacao(id=str(uuid.uuid4()), criada_em=agora, autor_hash=autor, perfil=perfil, tempos=list(tempos),
                  acertos=list(acertos), energia=list(energia), nota_energia=nota_energia, facilidade=list(facilidade),
                  comentario=comentario, sugestao=sugestao)
    repo.inserir(a)
    _cache["dados"] = None                # a nova avaliação aparece na hora para quem acabou de enviar
    return a


def _media(valores: list[float]) -> float | None:
    return round(sum(valores) / len(valores), 1) if valores else None


def resumo() -> dict:
    agora = time.monotonic()
    if _cache["dados"] is None or agora - _cache["quando"] > CACHE_RESUMO_S:
        _cache["dados"], _cache["quando"] = _calcular_resumo(), agora
    return _cache["dados"]


def _calcular_resumo() -> dict:
    """Os números da página: quantas pessoas, tempo médio e acerto por tarefa, facilidade por pergunta, energia
    e a lista de comentários e sugestões (sem nada que identifique a pessoa)."""
    lista = repo.todas()
    tarefas = []
    for i, texto in enumerate(TAREFAS):
        tempos = [a.tempos[i] for a in lista if a.tempos[i] is not None]
        respondidas = [a.acertos[i] for a in lista if a.acertos[i] is not None]
        tarefas.append({"tarefa": texto, "tempo_medio_s": _media(tempos), "acharam": len(tempos), "pessoas": len(lista),
                        "acerto_percentual": round(100 * sum(respondidas) / len(respondidas)) if respondidas else None})
    facilidade = [{"pergunta": p, "media": _media([a.facilidade[i] for a in lista])} for i, p in enumerate(PERGUNTAS)]
    energia = []
    for i, texto in enumerate(SITUACOES):
        respostas = [a.energia[i] for a in lista if a.energia[i] is not None]
        energia.append({"situacao": texto, "respostas": len(respostas),
                        **{e: sum(1 for r in respostas if r == e) for e in ENTENDEU}})
    perfis = {ROTULO_PERFIL[p]: sum(1 for a in lista if a.perfil == p) for p in PERFIS}
    comentarios = [{"pessoa": f"Pessoa {len(lista) - k}", "quando": a.criada_em.date().isoformat(), "perfil": ROTULO_PERFIL.get(a.perfil or ""),
                    "media": _media(a.facilidade), "comentario": a.comentario, "sugestao": a.sugestao}
                   for k, a in enumerate(lista) if a.comentario or a.sugestao]
    todas_notas = [f for a in lista for f in a.facilidade]
    return {"pessoas": len(lista), "facilidade_media": _media(todas_notas), "tarefas": tarefas, "facilidade": facilidade,
            "energia": energia, "nota_energia_media": _media([a.nota_energia for a in lista if a.nota_energia]),
            "perfis": {k: v for k, v in perfis.items() if v}, "comentarios": comentarios}


def como_json(a: Avaliacao) -> dict:
    d = asdict(a)
    d["criada_em"] = a.criada_em.isoformat()
    d.pop("autor_hash")
    d.pop("extra")
    return d


# ------------------------------------------------------------------ rotas

class NovaAvaliacao(BaseModel):
    perfil: Literal["familia", "faculdade", "trabalho", "conhecido", "outro"] | None = None
    tempos: list[int | None] = Field(min_length=3, max_length=3)
    acertos: list[bool | None] = Field(min_length=3, max_length=3)
    energia: list[Literal["sim", "em parte", "nao"] | None] = Field(min_length=4, max_length=4)
    nota_energia: int | None = Field(default=None, ge=1, le=5)
    facilidade: list[int] = Field(min_length=5, max_length=5)
    comentario: str | None = Field(default=None, max_length=2000)
    sugestao: str | None = Field(default=None, max_length=2000)


@router.get("")
def rota_resumo() -> dict:
    return resumo() | {"perguntas": PERGUNTAS, "tarefas_texto": TAREFAS, "situacoes": SITUACOES}


@router.post("", status_code=201)
def rota_registrar(corpo: NovaAvaliacao, x_device_id: str | None = Header(None)) -> dict:
    aparelho = _aparelho_obrigatorio(x_device_id)
    try:
        a = registrar(aparelho, corpo.perfil, corpo.tempos, corpo.acertos, corpo.energia, corpo.nota_energia,
                      corpo.facilidade, corpo.comentario, corpo.sugestao)
    except ErroAvaliacao as e:
        raise HTTPException(e.status, e.mensagem)
    return {"ok": True, "avaliacao": como_json(a)}
