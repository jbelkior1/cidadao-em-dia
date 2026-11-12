"""Triagem: entende sobre qual assunto a pessoa está falando.

É uma regra do sistema, não a busca por pontos do PCP. Ela só escolhe o
caminho. Quem responde a dúvida é a busca oficial do PCP.

Cada assunto tem palavras com peso. Palavra forte vale 2. A ordem do
dicionário desempata.
"""
import re

from sistema.privacidade import normal

ASSUNTOS = {
    "golpe": {
        "rotulo": "Isso é golpe?",
        "resumo": "conferir se uma mensagem é golpe",
        "palavras": [("golpe", 2), ("link", 1), ("mensagem", 1), ("pix", 1), ("taxa", 1), ("clique", 1), ("suspensa", 1),
                     ("bloqueada", 1), ("sms", 1), ("recebi", 1), ("cobranca", 1), ("boleto", 1)],
    },
    "direitos": {
        "rotulo": "Tenho algum direito?",
        "resumo": "saber se tem direito a desconto ou benefício",
        "palavras": [("direito", 2), ("direitos", 2), ("desconto", 2), ("tarifa social", 2), ("beneficio", 2), ("bolsa familia", 1),
                     ("cadunico", 1), ("cadastro unico", 1), ("auxilio", 1), ("bpc", 1)],
    },
    "luz": {
        "rotulo": "Minha conta de luz",
        "resumo": "entender a sua conta de luz",
        "palavras": [("conta de luz", 1), ("energia", 1), ("kwh", 1), ("consumo", 1), ("medidor", 1), ("chuveiro", 1),
                     ("gasto", 1), ("gastando", 1), ("veio alta", 1), ("muito cara", 1)],
    },
    "duvida": {
        "rotulo": "Tirar uma dúvida",
        "resumo": "tirar uma dúvida sobre documentos e serviços",
        "palavras": [("rg", 2), ("cpf", 2), ("documento", 2), ("documentos", 2), ("segunda via", 2), ("identidade", 1), ("certidao", 1),
                     ("titulo", 1), ("carteira", 1), ("perdi", 1), ("como faco", 1)],
    },
}

TEM_ENDERECO = r"https?://|www[.]|[.](com|net|org|info|xyz)([^a-z]|$)"


def contem(texto: str, termo: str) -> bool:
    """Procura o termo como palavra inteira: 'rg' não casa dentro de 'energia'."""
    return re.search(r"\b" + re.escape(normal(termo)) + r"\b", normal(texto)) is not None


def entender(texto: str) -> tuple[str | None, str, list[str]]:
    """Devolve (assunto ou None, confiança 'alta'/'média'/'baixa', palavras que indicaram)."""
    pontos, achadas = {}, {}
    for chave, info in ASSUNTOS.items():
        lista = [(p, w) for p, w in info["palavras"] if contem(texto, p)]
        if chave == "golpe" and re.search(TEM_ENDERECO, texto.lower()):
            lista.append(("um endereço de site", 2))
        pontos[chave] = sum(w for _, w in lista)
        achadas[chave] = [p for p, _ in lista]
    melhor = max(ASSUNTOS, key=lambda k: pontos[k])
    if pontos[melhor] == 0:
        return None, "baixa", []
    return melhor, ("alta" if pontos[melhor] >= 2 else "média"), achadas[melhor]
