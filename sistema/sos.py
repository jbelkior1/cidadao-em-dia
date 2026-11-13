"""SOS: o canal certo para pedir ajuda ou denunciar, conforme a linha em que a pessoa está.

O app NÃO denuncia sozinho (o Metrô e as concessionárias não têm API para isso). O que ele faz é
abrir o canal já preenchido, e quem envia é a pessoa:
- Metrô (linhas 1, 2, 3, 15 e 17): SMS Segurança, com linha e estação já escritas no texto;
- CPTM (linhas 10, 11 e 12): canal de denúncia e central de atendimento;
- ViaQuatro e ViaMobilidade (linhas 4, 5, 8 e 9): central de atendimento da linha;
- sem canal próprio no catálogo (linhas 6, 7 e 13): Ouvidoria da Artesp, que fiscaliza as concessões.

Os canais vêm do catálogo da DSA (a lista encadeada da entrega), com o id do serviço, para a
equipe conferir a fonte. Os números de discagem ficam aqui e o teste confere se aparecem no texto
do catálogo. Não é canal de emergência: em perigo, 190, 192 ou 193.
"""
from sistema.adaptadores import dsa
from sistema.mobilidade import rede

EMERGENCIA = [
    {"rotulo": "Polícia", "numero": "190"},
    {"rotulo": "SAMU", "numero": "192"},
    {"rotulo": "Bombeiros", "numero": "193"},
]
AVISO = "O Dá Tempo? não é canal de emergência nem canal oficial. Em perigo, ligue 190, 192 ou 193."
SMS_METRO = "+5511973332252"
OPERADORA = {"1": "metro", "2": "metro", "3": "metro", "15": "metro", "17": "metro",
             "10": "cptm", "11": "cptm", "12": "cptm",
             "4": "via4", "5": "via", "8": "via", "9": "via"}
NOME = {"metro": "Metrô", "cptm": "CPTM", "via4": "ViaQuatro", "via": "ViaMobilidade"}


def _servico(servico_id: str) -> dict:
    return dsa.servico_por_id(servico_id) or {"id": servico_id, "titulo": "", "canal": ""}


def _canal(servico_id: str, rotulo: str, acao: dict, detalhe: str) -> dict:
    s = _servico(servico_id)
    return {"servico": servico_id, "rotulo": rotulo, "detalhe": detalhe, "acao": acao, "catalogo": s["canal"]}


def texto_do_sms(linha: str | None, estacao: str | None) -> str:
    """Texto que já vai escrito no SMS; a pessoa completa a ocorrência antes de enviar."""
    partes = []
    if linha:
        info = rede.linha(linha)
        partes.append(f"Linha {linha}-{info['nome']}" if info.get("nome") else f"Linha {linha}")
    if estacao:
        partes.append(f"estação {estacao}")
    return (", ".join(partes) + ". " if partes else "") + "Ocorrência: "


def canais(linha: str | None = None, estacao: str | None = None) -> dict:
    linha = (linha or "").strip() or None
    operadora = OPERADORA.get(linha or "")
    lista: list[dict] = []
    if operadora == "metro":
        corpo = texto_do_sms(linha, estacao)
        lista.append(_canal("SRV-004", "Denunciar por SMS ao Metrô",
                            {"tipo": "sms", "numero": "(11) 97333-2252", "texto": corpo,
                             "href": f"sms:{SMS_METRO}?&body={_codificar(corpo)}"},
                            "O texto já vai com a linha e a estação. Complete a ocorrência e envie: o formato é sugerido, confira no site do Metrô."))
    elif operadora == "cptm":
        lista.append(_canal("SRV-009", "Canal de denúncia da CPTM",
                            {"tipo": "tel", "numero": "(11) 3117-7459", "href": "tel:+551131177459"},
                            "Importunação, assédio, discriminação e fraude; a CPTM informa que o anonimato é garantido."))
        lista.append(_canal("SRV-007", "Central da CPTM",
                            {"tipo": "tel", "numero": "0800 055 0121", "href": "tel:08000550121"},
                            "Atendimento ao passageiro, das 5h às 23h."))
    elif operadora in ("via4", "via"):
        numero, href = ("0800 770 7100", "tel:08007707100") if operadora == "via4" else ("0800 770 7106", "tel:08007707106")
        lista.append(_canal("SRV-011", f"Central da {NOME[operadora]}",
                            {"tipo": "tel", "numero": numero, "href": href},
                            "Atendimento da linha; confira o horário no site da concessionária."))
    else:
        lista.append(_canal("SRV-012", "Ouvidoria da Artesp",
                            {"tipo": "tel", "numero": "0800 727 83 77", "href": "tel:08007278377"},
                            "A Artesp fiscaliza as concessões. Para esta linha não há canal próprio no catálogo."))
    return {"linha": linha, "operadora": NOME.get(operadora or "", None), "canais": lista, "emergencia": EMERGENCIA, "aviso": AVISO}


def _codificar(texto: str) -> str:
    from urllib.parse import quote
    return quote(texto, safe="")
