"""Carrega as 7 fichas FC-01 a FC-07 da Central do Cidadão de Aurora.

As fichas são a ÚNICA fonte de verdade do assistente. Elas ficam em `entregas/pai/fichas/`,
exatamente como vieram do enunciado (versão de 01/10/2026): nada foi reescrito aqui, para o
agente não responder por um texto que o professor não mandou.

Cada arquivo `.md` tem o mesmo formato: um título `# FC-0X — Assunto` e blocos
`**Campo:** valor`, alguns com lista numerada ou com travessão. Este módulo transforma isso em
registros com os campos que o enunciado manda preservar: id, assunto, palavras-chave, custo,
prazo, documentos, passo a passo, onde, agendamento, fonte e a data de verificação.

Nada aqui chama modelo de linguagem: é leitura de arquivo e pode ser testado sozinho.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "fichas"
VERSAO = "01/10/2026"

#: Campos cujo nome muda de ficha para ficha mas significam a mesma coisa.
SINONIMOS = {
    "documentos necessários": "documentos",
    "documentos necessários para a segunda via": "documentos",
    "passo a passo": "passo_a_passo",
    "passo a passo (pelo portal)": "passo_a_passo",
    "palavras-chave": "palavras_chave",
    "custo e prazo (cada certidão)": "custo",
    "quem pode pedir": "quem_pode_pedir",
    "quem deve ter": "quem_pode_pedir",
    "horário de atendimento presencial": "atendimento",
    "atendimento por terceiros": "terceiros",
    "atendimento prioritário": "prioritario",
    "validade da cnh renovada": "validade",
    "quando renovar": "quando_renovar",
    "perda, roubo ou furto de documento": "perda_roubo",
}


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


@dataclass
class Ficha:
    id: str                     # FC-01 … FC-07
    assunto: str
    arquivo: str
    texto: str                  # a ficha inteira, como está no arquivo
    campos: dict[str, str] = field(default_factory=dict)
    palavras_chave: list[str] = field(default_factory=list)

    @property
    def fonte(self) -> str:
        return self.campos.get("fonte", f"Central do Cidadão de Aurora, ficha {self.id}, versão de {VERSAO}")

    def termos_do_texto(self) -> set[str]:
        """Palavras longas da própria ficha, usadas só como rede de segurança na busca.

        A FC-07 (regras gerais) não traz "Palavras-chave" no enunciado, então sem isto ela nunca
        seria encontrada — e o golden pergunta por ela ("Vocês atendem aos sábados?"). Indexar o
        texto da ficha não inventa conteúdo: é só achar o que já está escrito nela.
        """
        return {p for p in re.findall(r"\w{6,}", sem_acento(self.texto))}

    def pontuar(self, pergunta: str) -> int:
        """Quantos termos da ficha aparecem na pergunta. Palavra-chave vale 3; assunto e texto valem 1.

        Mesma ideia da busca por pontos da PCP, para o agente achar a ficha certa sem depender do modelo.
        """
        alvo = sem_acento(pergunta)
        pontos = sum(3 for p in self.palavras_chave if p and sem_acento(p) in alvo)
        pontos += sum(1 for p in re.findall(r"\w{4,}", sem_acento(self.assunto)) if p in alvo)
        if not self.palavras_chave:                       # só para quem não tem palavras-chave (FC-07)
            pontos += sum(1 for p in self.termos_do_texto() if p in alvo)
        return pontos

    def resumo(self) -> dict:
        return {"ficha": self.id, "assunto": self.assunto, "fonte": self.fonte,
                **{k: v for k, v in self.campos.items() if k != "fonte"}}


def _partir_campos(corpo: str) -> dict[str, str]:
    """Quebra o corpo da ficha nos blocos `**Campo:** valor`, juntando as listas que vêm abaixo."""
    campos: dict[str, str] = {}
    partes = re.split(r"\*\*(.+?):\*\*", corpo)
    for i in range(1, len(partes) - 1, 2):
        nome = partes[i].strip().lower()
        chave = SINONIMOS.get(nome, sem_acento(nome).replace(" ", "_").replace("-", "_"))
        valor = re.sub(r"\n+", " ", partes[i + 1]).strip()
        valor = re.sub(r"\s{2,}", " ", valor)
        if valor:
            campos[chave] = valor
    return campos


def _ler(arquivo: Path) -> Ficha | None:
    texto = arquivo.read_text(encoding="utf-8").strip()
    cabecalho = re.match(r"#\s*(FC-\d{2})\s*[—–-]\s*(.+)", texto)
    if not cabecalho:
        return None
    campos = _partir_campos(texto)
    chaves = [p.strip() for p in campos.get("palavras_chave", "").split(",") if p.strip()]
    return Ficha(id=cabecalho.group(1), assunto=cabecalho.group(2).strip(), arquivo=arquivo.name,
                 texto=texto, campos=campos, palavras_chave=chaves)


@lru_cache(maxsize=1)
def carregar() -> list[Ficha]:
    """As 7 fichas, em ordem de id. Levanta erro se faltar alguma: sem base não há assistente."""
    fichas = [f for f in (_ler(a) for a in sorted(PASTA.glob("FC-*.md"))) if f]
    esperados = {f"FC-{n:02d}" for n in range(1, 8)}
    faltando = esperados - {f.id for f in fichas}
    if faltando:
        raise FileNotFoundError(f"faltam fichas em {PASTA}: {', '.join(sorted(faltando))}")
    return fichas


def por_id(ficha_id: str) -> Ficha | None:
    alvo = (ficha_id or "").strip().upper()
    return next((f for f in carregar() if f.id == alvo), None)


def buscar(pergunta: str, limite: int = 3) -> list[Ficha]:
    """As fichas mais prováveis para a pergunta, da maior pontuação para a menor. Zero pontos não entra."""
    com_nota = [(f.pontuar(pergunta), f) for f in carregar()]
    return [f for nota, f in sorted(com_nota, key=lambda x: (-x[0], x[1].id)) if nota > 0][:limite]


def catalogo() -> list[dict]:
    """O menu por categorias: uma entrada por ficha."""
    return [{"ficha": f.id, "assunto": f.assunto, "palavras_chave": f.palavras_chave} for f in carregar()]
