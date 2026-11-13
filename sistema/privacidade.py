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
    "meu whatsapp e ", "meu email e ", "meu e-mail e ", "minha senha e ",
)
#: "meu celular é ..." anuncia o número; "perdi meu rg e meu cpf" ou "roubaram meu celular e a carteira"
#: falam do objeto. Por isso, depois de "e", a palavra seguinte não pode ser um artigo ou possessivo.
OBJETO_OU_DADO = re.compile(
    r"\bmeu (cpf|rg|celular|telefone) (e|eh)\b(?! (meu|minha|meus|minhas|o|a|os|as|um|uma|outro|outra)\b)")
#: e-mail escrito por extenso ("fulano arroba gmail ponto com"); "ponto com" sozinho é comum ("ponto com alagamento")
EMAIL_POR_EXTENSO = re.compile(r"\barroba\b|\bponto com( br)?$|\bponto com ponto br\b")
#: Separadores que alguém põe entre os dígitos de um CPF ou telefone. A barra fica de fora de
#: propósito: "12/11/2026" é data, não dado pessoal, e é comum em pergunta de declaração de atraso.
SEPARADORES_ENTRE_DIGITOS = re.compile(r"(?<=\d)[\s.,_()\-–—]+(?=\d)")

AVISO = ("Para a sua segurança, não escreva CPF, telefone, e-mail, endereço, nome ou senha. "
         "Eu não preciso desses dados para ajudar. Pode perguntar de novo sem eles.")


def normal(texto: str) -> str:
    """Minúsculas e sem acento."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def motivo(texto: str) -> str | None:
    """Devolve por que o texto foi barrado, ou None se pode seguir.

    É uma barreira por regra, não por sentido: pega número longo (com ou sem separador), @, e-mail
    escrito por extenso e as frases que anunciam um dado. Nome solto ("sou a Maria") não é pego; por
    isso o modelo também recebe a instrução de nunca pedir nem repetir dado pessoal.
    """
    junto = SEPARADORES_ENTRE_DIGITOS.sub("", texto)   # 123.456.789-09 ou 123,456,789_09 viram 12345678909
    if re.search(r"\d{8,}", junto):
        return "número longo, que pode ser CPF, telefone ou CEP"
    if "@" in texto:
        return "endereço de e-mail"
    n = normal(texto) + " "
    for frase in FRASES:
        if frase in n:
            return "frase que anuncia um dado pessoal"
    limpo = " ".join(re.sub(r"[^\w\s]", " ", n).split())
    if OBJETO_OU_DADO.search(limpo):
        return "frase que anuncia um dado pessoal"
    if EMAIL_POR_EXTENSO.search(limpo):
        return "e-mail escrito por extenso"
    return None


def mascarar(texto: str) -> str:
    """Esconde números longos e e-mails. Usado para mostrar de volta uma mensagem colada."""
    texto = re.sub(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", "[e-mail oculto]", texto)
    return re.sub(r"\d[\d.,_\-–—\s()]{6,}\d", "[número oculto]", texto)
