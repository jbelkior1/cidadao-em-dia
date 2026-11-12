"""Isso é golpe? Confere uma mensagem colada, item por item.

A análise é feita na memória. O texto não é gravado nem enviado a modelo de IA.
"""
import re

from sistema.privacidade import normal

PAGAMENTO = {"pix": "Pix", "pague": "pagamento", "pagamento": "pagamento", "taxa": "taxa", "boleto": "boleto", "deposito": "depósito"}
PRESSAO = {"urgente": "urgência", "bloquead": "bloqueio", "suspens": "suspensão", "cancelad": "cancelamento",
           "ultimo dia": "último dia", "imediat": "pressa"}
ACESSO = {"senha": "senha", "clique": "clicar em link", "codigo": "código de confirmação", "token": "token"}

DOMINIO = r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})(?:/\S*)?"


def conferir(texto: str) -> dict:
    """Devolve o nível ('atencao' ou 'ok') e a lista do que foi conferido."""
    dominios = re.findall(DOMINIO, texto.lower())
    fora_do_governo = [d for d in dominios if not d.endswith(".gov.br")]
    n = normal(texto)
    pagamento = sorted({nome for chave, nome in PAGAMENTO.items() if chave in n})
    pressao = sorted({nome for chave, nome in PRESSAO.items() if chave in n})
    acesso = sorted({nome for chave, nome in ACESSO.items() if chave in n})

    if fora_do_governo:
        detalhe_site = f"o endereço {fora_do_governo[0]} não termina em .gov.br"
    elif dominios:
        detalhe_site = "os endereços terminam em .gov.br"
    else:
        detalhe_site = "a mensagem não traz endereço de site"

    itens = [
        {"pergunta": "O endereço é de um site do governo?", "ok": not fora_do_governo, "detalhe": detalhe_site},
        {"pergunta": "A mensagem pede dinheiro?", "ok": not pagamento,
         "detalhe": "fala em " + ", ".join(pagamento) if pagamento else "não pede"},
        {"pergunta": "A mensagem pressiona ou ameaça?", "ok": not pressao,
         "detalhe": "fala em " + ", ".join(pressao) if pressao else "não pressiona"},
        {"pergunta": "A mensagem pede senha, código ou clique?", "ok": not acesso,
         "detalhe": "pede " + ", ".join(acesso) if acesso else "não pede"},
    ]
    sinais = sum(1 for i in itens if not i["ok"])
    if sinais:
        titulo = "Cuidado: esta mensagem tem sinais de golpe"
        orientacao = ("Não clique, não pague e não informe senha ou código. "
                      "Se quiser confirmar, procure o órgão pelo site oficial ou pelo telefone que está na sua conta ou cartão, "
                      "nunca pelo contato que veio na mensagem.")
    else:
        titulo = "Não encontrei os sinais mais comuns de golpe"
        orientacao = ("Isso não garante que a mensagem é verdadeira. "
                      "Na dúvida, confirme pelo site oficial do órgão ou pessoalmente no CRAS.")
    return {"nivel": "atencao" if sinais else "ok", "titulo": titulo, "itens": itens, "orientacao": orientacao, "sinais": sinais}
