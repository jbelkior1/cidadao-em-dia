"""Barreira de dado pessoal.

Roda antes de qualquer registro e antes de qualquer chamada ao modelo de IA.
A regra do enunciado do PCP (8 dígitos ou mais, ou @) continua valendo dentro
do assistente do PCP. Aqui a barreira é um pouco mais larga, porque o chat
também precisa barrar quem escreve "meu endereço é...", sem número nenhum.
"""
import re
import unicodedata

FRASES = (
    "meu nome e ", "me chamo ", "meu endereco e ", "moro na rua ", "moro na avenida ", "moro na travessa ",
    "meu telefone e ", "meu celular e ", "meu whatsapp e ", "meu email e ", "meu e-mail e ", "minha senha e ",
)

AVISO = ("Para a sua segurança, não escreva CPF, telefone, e-mail, endereço, nome ou senha. "
         "Eu não preciso desses dados para ajudar. Pode perguntar de novo sem eles.")


def normal(texto: str) -> str:
    """Minúsculas e sem acento."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def motivo(texto: str) -> str | None:
    """Devolve por que o texto foi barrado, ou None se pode seguir."""
    junto = re.sub(r"[.\-\s()]", "", texto)          # 123.456.789-09 vira 12345678909
    if re.search(r"\d{8,}", junto):
        return "número longo, que pode ser CPF, telefone ou CEP"
    if "@" in texto:
        return "endereço de e-mail"
    n = normal(texto) + " "
    for frase in FRASES:
        if frase in n:
            return "frase que anuncia um dado pessoal"
    return None


def mascarar(texto: str) -> str:
    """Esconde números longos e e-mails. Usado para mostrar de volta uma mensagem colada."""
    texto = re.sub(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", "[e-mail oculto]", texto)
    return re.sub(r"\d[\d.\-\s()]{6,}\d", "[número oculto]", texto)
