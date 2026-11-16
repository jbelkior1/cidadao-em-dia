"""Ponte entre o sistema e a entrega do PCP.

A busca por pontos, a confiança e a barreira de dado pessoal são as das
classes da entrega (entregas/pcp/citizen-assist-ai). Aqui só se chama o que
elas oferecem e se converte o resultado para o formato do chat.

O sistema nunca grava no histórico do PCP: o histórico pertence aos
atendimentos feitos no terminal.
"""
import json
import sys

from sistema import config

PASTA = config.RAIZ / "entregas" / "pcp" / "citizen-assist-ai"
ARQUIVO_BASE = PASTA / "data" / "base_conhecimento.json"

_assistente = None
_erro = ""
_em_conferencia: set[int] = set()   # ids ainda não conferidos na fonte


def _carregar():
    """Cria o Assistente uma vez. Se a entrega estiver ausente, o chat segue e avisa."""
    global _assistente, _erro
    if _assistente is None and not _erro:
        try:
            if str(PASTA) not in sys.path:
                sys.path.insert(0, str(PASTA))
            from assistente import Assistente
            from base_conhecimento import BaseConhecimento
            base = BaseConhecimento(str(ARQUIVO_BASE))
            base.carregar()
            if base.erro:
                _erro = base.erro
                return None
            _assistente = Assistente("Cidadão em Dia", base, caminho_historico=str(PASTA / "data" / "historico.json"))
            for registro in json.loads(ARQUIVO_BASE.read_text(encoding="utf-8")):
                if registro.get("conferido_pela_equipe") is False:
                    _em_conferencia.add(registro["id"])
        except Exception as e:  # entrega ausente ou com erro não derruba o chat
            _erro = f"{type(e).__name__}: {e}"
    return _assistente


def situacao() -> dict:
    a = _carregar()
    if a is None:
        return {"ok": False, "orientacoes": 0, "categorias": 0, "em_conferencia": 0, "erro": _erro}
    return {"ok": True, "orientacoes": len(a.base.orientacoes), "categorias": len(a.base.categorias()),
            "em_conferencia": len(_em_conferencia), "erro": ""}


def _para_tela(orientacao: dict) -> dict:
    orientacao = dict(orientacao)
    orientacao["em_conferencia"] = orientacao["id"] in _em_conferencia
    return orientacao


def responder(pergunta: str) -> dict:
    """Faz a busca oficial do PCP e devolve o resultado pronto para o chat."""
    vazio = {"encontrou": False, "bloqueada": False, "confianca": None, "pontos": 0, "orientacao": None, "detalhe": [], "alternativas": []}
    a = _carregar()
    if a is None:
        return vazio
    r = a.responder_dict(pergunta)
    if r["bloqueada"]:
        return vazio | {"bloqueada": True}
    if not r["encontrou"]:
        return vazio
    detalhe = [{"termo": t, "pontos": 3, "origem": "palavra-chave"} for t in r["detalhe"]["palavras_chave"]]
    detalhe += [{"termo": t, "pontos": 1, "origem": "palavra do título"} for t in r["detalhe"]["palavras_titulo"]]
    alternativas = [{"id": alt["orientacao"]["id"], "titulo": alt["orientacao"]["titulo"], "pontos": alt["pontos"]}
                    for alt in r["alternativas"]]
    return {"encontrou": True, "bloqueada": False, "confianca": r["confianca"], "pontos": r["pontos"],
            "orientacao": _para_tela(r["orientacao"]), "detalhe": detalhe, "alternativas": alternativas}


def categorias() -> list[str]:
    a = _carregar()
    return a.base.categorias() if a else []


def por_categoria(categoria: str) -> list[dict]:
    a = _carregar()
    return [_para_tela(o.para_dict()) for o in a.base.por_categoria(categoria)] if a else []


def orientacao(identificador: int) -> dict | None:
    a = _carregar()
    if a is None:
        return None
    for o in a.base.orientacoes:
        if o.id == identificador:
            return _para_tela(o.para_dict())
    return None


def pontuar_todas(pergunta: str) -> dict:
    """Para a página Teste do PCP: a lista de tuplas de buscar(), com o detalhe de cada pontuação."""
    a = _carregar()
    if a is None:
        return {"ok": False, "erro": _erro, "bloqueada": False, "resultados": []}
    if a.tem_dado_pessoal(pergunta):
        return {"ok": True, "erro": "", "bloqueada": True, "resultados": []}
    resultados = []
    for pontos, o in a.base.buscar(pergunta):
        d = a.base.detalhar_pontuacao(pergunta, o)
        resultados.append({"pontos": pontos, "confianca": a.base.nivel_confianca(pontos), "id": o.id, "titulo": o.titulo,
                           "categoria": o.categoria, "palavras_chave": d["palavras_chave"], "palavras_titulo": d["palavras_titulo"]})
    return {"ok": True, "erro": "", "bloqueada": False, "resultados": resultados}


def base_resumida() -> list[dict]:
    a = _carregar()
    if a is None:
        return []
    return [{"id": o.id, "titulo": o.titulo, "categoria": o.categoria, "palavras_chave": o.palavras_chave,
             "em_conferencia": o.id in _em_conferencia} for o in a.base.orientacoes]
