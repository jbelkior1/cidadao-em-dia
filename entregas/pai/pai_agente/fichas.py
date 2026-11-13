"""Carrega as 7 fichas de transporte (FT-01 a FT-07), a única fonte de verdade do assistente da PAI.

O enunciado da PAI trazia 7 fichas fictícias de documentos pessoais (Central do Cidadão de Aurora).
Em 13/11/2026 o professor autorizou trocar o tema pelo do nosso protótipo, mantendo as mesmas regras
de construção. As fichas novas seguem a mesma estrutura das de Aurora, mas com informação real:
cada fato saiu de página oficial (Metrô, CPTM, concessionárias, SPTrans, Artesp, Defesa Civil), e a
URL está no campo **Fonte** de cada ficha. As fichas de Aurora ficaram em `historico/aurora/`.

Cada arquivo `.md` tem um título `# FT-0X — Assunto` e blocos `**Campo:** valor`, alguns com lista
numerada. Este módulo transforma isso em registros com o que o enunciado manda preservar: id,
assunto, palavras-chave, os campos de conteúdo, passo a passo, onde e a fonte com a data.

Nada aqui chama modelo de linguagem: é leitura de arquivo e pode ser testado sozinho.
"""
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "fichas"
PREFIXO = "FT"
QUANTIDADE = 7
VERSAO = "13/11/2026"

#: Campos cujo nome muda de ficha para ficha mas significam a mesma coisa.
SINONIMOS = {
    "documentos necessários": "documentos",
    "passo a passo": "passo_a_passo",
    "passo a passo (bilhete único especial)": "passo_a_passo",
    "palavras-chave": "palavras_chave",
    "não consta nesta ficha": "nao_consta",
}


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower()) if unicodedata.category(c) != "Mn")


@dataclass
class Ficha:
    id: str                     # FT-01 … FT-07
    assunto: str
    arquivo: str
    texto: str                  # a ficha inteira, como está no arquivo
    campos: dict[str, str] = field(default_factory=dict)
    palavras_chave: list[str] = field(default_factory=list)

    @property
    def fonte(self) -> str:
        return self.campos.get("fonte", f"Fichas de transporte do Dá Tempo?, ficha {self.id}, versão de {VERSAO}")

    def termos_do_texto(self) -> set[str]:
        """Palavras longas da própria ficha, usadas só como rede de segurança na busca.

        Só entra para ficha sem "Palavras-chave" (foi o caso da FC-07 de Aurora, que o golden
        perguntava e a busca nunca achava). Indexar o texto não inventa conteúdo: só acha o que
        já está escrito na ficha.
        """
        return {p for p in re.findall(r"\w{6,}", sem_acento(self.texto))}

    def pontuar(self, pergunta: str) -> int:
        """Quantos termos da ficha aparecem na pergunta. Palavra-chave vale 3; assunto e texto valem 1.

        Mesma ideia da busca por pontos da PCP, para o agente achar a ficha certa sem depender do modelo.
        Na palavra-chave, `#` vale qualquer dígito: "## anos" casa com "67 anos" (melhoria da rodada
        "depois": a pergunta "Tenho 67 anos. Pago metrô?" não achava a FT-04, que só tinha "60 anos" e
        "65 anos").
        """
        alvo = sem_acento(pergunta)
        pontos = sum(3 for p in self.palavras_chave if p and _casa(p, alvo))
        pontos += sum(1 for p in re.findall(r"\w{4,}", sem_acento(self.assunto)) if p in alvo)
        if not self.palavras_chave:
            pontos += sum(1 for p in self.termos_do_texto() if p in alvo)
        return pontos

    def resumo(self) -> dict:
        return {"ficha": self.id, "assunto": self.assunto, "fonte": self.fonte,
                **{k: v for k, v in self.campos.items() if k != "fonte"}}


def _casa(palavra_chave: str, alvo_sem_acento: str) -> bool:
    """A palavra-chave aparece na pergunta? `#` na palavra-chave vale um dígito qualquer."""
    termo = sem_acento(palavra_chave)
    if "#" not in termo:
        return termo in alvo_sem_acento
    return re.search(re.escape(termo).replace("\\#", r"\d").replace("#", r"\d"), alvo_sem_acento) is not None


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


def _ler(arquivo: Path, prefixo: str) -> Ficha | None:
    texto = arquivo.read_text(encoding="utf-8").strip()
    cabecalho = re.match(rf"#\s*({prefixo}-\d{{2}})\s*[—–-]\s*(.+)", texto)
    if not cabecalho:
        return None
    campos = _partir_campos(texto)
    chaves = [p.strip() for p in campos.get("palavras_chave", "").split(",") if p.strip()]
    return Ficha(id=cabecalho.group(1), assunto=cabecalho.group(2).strip(), arquivo=arquivo.name,
                 texto=texto, campos=campos, palavras_chave=chaves)


@lru_cache(maxsize=4)
def carregar(pasta: Path = PASTA, prefixo: str = PREFIXO) -> list[Ficha]:
    """As 7 fichas, em ordem de id. Levanta erro se faltar alguma: sem base não há assistente."""
    fichas = [f for f in (_ler(a, prefixo) for a in sorted(Path(pasta).glob(f"{prefixo}-*.md"))) if f]
    esperados = {f"{prefixo}-{n:02d}" for n in range(1, QUANTIDADE + 1)}
    faltando = esperados - {f.id for f in fichas}
    if faltando:
        raise FileNotFoundError(f"faltam fichas em {pasta}: {', '.join(sorted(faltando))}")
    return fichas


def por_id(ficha_id: str) -> Ficha | None:
    alvo = (ficha_id or "").strip().upper()
    return next((f for f in carregar() if f.id == alvo), None)


def buscar(pergunta: str, limite: int = 3) -> list[Ficha]:
    """As fichas mais prováveis para a pergunta, da maior pontuação para a menor. Zero pontos não entra."""
    com_nota = [(f.pontuar(pergunta), f) for f in carregar()]
    return [f for nota, f in sorted(com_nota, key=lambda x: (-x[0], x[1].id)) if nota > 0][:limite]


def catalogo() -> list[dict]:
    """O menu por assunto: uma entrada por ficha."""
    return [{"ficha": f.id, "assunto": f.assunto, "palavras_chave": f.palavras_chave} for f in carregar()]
