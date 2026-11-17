"""Foto como evidência do relato: valida, limpa e recomprime antes de guardar.

O arquivo que a pessoa manda nunca é guardado como veio. O servidor abre a imagem, confere que é
mesmo JPEG, PNG ou WebP, gira conforme a orientação do celular, reduz para no máximo 1280 px e grava
um JPEG novo. Esse JPEG novo não carrega os metadados do original, onde ficam a localização exata
(GPS), o modelo do aparelho e a data. Aviso: o servidor não reconhece rosto nem placa na imagem;
quem relata vê o aviso na tela e quem vê o relato pode sinalizar.
"""
import base64
import binascii
import io
import threading

from PIL import Image, ImageOps, UnidentifiedImageError

from sistema.relatos import ErroRelato

LADO_MAXIMO = 1280                  # px do lado maior depois de recomprimir
TAMANHO_MAXIMO = 3_000_000          # bytes do arquivo enviado (o app já manda reduzido, perto de 300 KB)
PIXELS_MAXIMOS = 12_000_000         # antes de abrir a imagem inteira (evita "bomba" de descompressão); o app manda no máximo 1280 px
QUALIDADE = 80
FORMATOS = ("JPEG", "PNG", "WEBP")

_vagas = threading.BoundedSemaphore(2)    # no máximo 2 fotos sendo decodificadas ao mesmo tempo (memória)

_MENSAGEM = "Não consegui ler essa foto. Use uma imagem JPEG, PNG ou WebP."


def decodificar(texto: str) -> bytes:
    """Base64 puro ou 'data:image/...;base64,...' (como o navegador gera) para bytes."""
    if texto.startswith("data:"):
        _, _, texto = texto.partition(",")
    try:
        return base64.b64decode(texto, validate=True)
    except (binascii.Error, ValueError):
        raise ErroRelato(422, "A foto veio com defeito. Tire ou escolha de novo.")


def processar(dados: bytes) -> bytes:
    """Devolve o JPEG limpo. 422 se não for uma imagem aceita ou se for grande demais."""
    if not dados:
        raise ErroRelato(422, _MENSAGEM)
    if len(dados) > TAMANHO_MAXIMO:
        raise ErroRelato(422, f"A foto é grande demais (limite de {TAMANHO_MAXIMO // 1_000_000} MB).")
    try:
        imagem = Image.open(io.BytesIO(dados))
        if imagem.format not in FORMATOS:
            raise ErroRelato(422, _MENSAGEM)
        if imagem.width * imagem.height > PIXELS_MAXIMOS:
            raise ErroRelato(422, "A foto tem resolução alta demais. Tire de novo em tamanho normal.")
        with _vagas:
            imagem = ImageOps.exif_transpose(imagem).convert("RGB")      # orientação aplicada, sem transparência
            imagem.thumbnail((LADO_MAXIMO, LADO_MAXIMO))
            saida = io.BytesIO()
            imagem.save(saida, "JPEG", quality=QUALIDADE, optimize=True)  # sem exif=: nada dos metadados passa
            return saida.getvalue()
    except ErroRelato:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise ErroRelato(422, _MENSAGEM)
