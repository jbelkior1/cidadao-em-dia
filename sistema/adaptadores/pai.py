"""Ponte entre o sistema e a entrega da PAI (entregas/pai/pai_agente).

O agente da PAI é um LangGraph de três nós (guardrails → busca nas fichas → resposta) que só responde
pelas 7 fichas de transporte (FT-01 a FT-07) e cita a ficha de origem. Na conversa, a Lia chama esse
agente como ferramenta (`perguntar_fichas`) quando a dúvida é de regra ou procedimento: declaração de
atraso, gratuidade, reclamação, achados e perdidos, tarifa, assédio, acessibilidade, chuva.

Aqui só se chama o que a entrega oferece e se converte o resultado para o formato do chat. O código do
agente, as fichas, o golden dataset e o juiz continuam na pasta da entrega, que roda sozinha.
"""
import re
import sys

from sistema import config

PASTA = config.RAIZ / "entregas" / "pai"
LIDO_EM = "2026-11-12"          # data em que as páginas oficiais das fichas foram lidas

_erro = ""


def _modulos():
    """Importa o agente da entrega. Se ela estiver ausente, o chat segue sem esta ferramenta.

    Uma falha não fica guardada para sempre: na próxima chamada tenta de novo (o import que deu certo
    fica em cache no próprio Python). A pasta entra no fim do sys.path, para não sombrear módulos do sistema.
    """
    global _erro
    try:
        if str(PASTA) not in sys.path:
            sys.path.append(str(PASTA))
        from pai_agente import agente, fichas, guardrails
        _erro = ""
        return agente, fichas, guardrails
    except Exception as e:                      # entrega ausente ou dependência faltando
        _erro = f"{type(e).__name__}: {e}"
        return None


def disponivel() -> bool:
    return _modulos() is not None


def _primeira_url(texto: str) -> str:
    achada = re.search(r"https?://[^\s)]+", texto or "")
    return achada.group(0) if achada else ""


def perguntar(pergunta: str) -> dict:
    """Pergunta ao agente das fichas. Devolve a resposta citada e as fichas, ou o motivo da recusa."""
    mods = _modulos()
    if not mods:
        return {"ok": False, "erro": f"agente da PAI indisponível ({_erro})"}
    agente, fichas, _ = mods
    try:
        r = agente.responder(pergunta)
    except Exception as e:                      # cota, rede, chave: a Lia avisa e segue
        return {"ok": False, "erro": f"o agente das fichas não respondeu agora ({type(e).__name__})"}
    usadas = [f for f in (fichas.por_id(i) for i in r["fichas"]) if f]
    resposta = r["resposta"].replace(agente.AVISO, "").strip()
    return {"ok": True, "encontrou": bool(usadas) and r["usou_modelo"], "resposta": resposta, "motivo": r["motivo"],
            "fichas": [f.id for f in usadas], "assuntos": [f.assunto for f in usadas],
            "fonte": _primeira_url(usadas[0].fonte) if usadas else "", "usou_modelo": r["usou_modelo"],
            "aviso": agente.AVISO}


def testar(pergunta: str) -> dict:
    """Para a aba Teste da PAI: mostra cada etapa do grafo, não só a resposta final."""
    mods = _modulos()
    if not mods:
        return {"ok": False, "erro": f"agente da PAI indisponível ({_erro})"}
    agente, fichas, guardrails = mods
    v = guardrails.avaliar(pergunta)
    # como no grafo: mensagem barrada no guardrail não chega à busca
    pontos = [] if not v.limpo else sorted(
        ({"ficha": f.id, "assunto": f.assunto, "pontos": f.pontuar(v.texto_seguro)} for f in fichas.carregar()),
        key=lambda x: (-x["pontos"], x["ficha"]))
    etapa = {"dado_pessoal": v.tipos_mascarados, "injecao": v.tipos_injecao, "entrada_invalida": v.entrada_invalida,
             "texto_que_segue": v.texto_seguro}
    return {"ok": True, "guardrails": etapa, "busca": pontos, **perguntar(pergunta)}


def catalogo() -> list[dict]:
    mods = _modulos()
    return mods[1].catalogo() if mods else []
