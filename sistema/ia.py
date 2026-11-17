"""Camada de IA: um cliente só para qualquer serviço no formato OpenAI.

Groq, Ollama e Gemini aceitam o mesmo formato de chamada. O que muda é o
endereço (base_url), o modelo e a chave, que vêm da configuração local.

Regras:
- sem configuração, o sistema inteiro funciona por regras e esta camada não é chamada;
- há um limite de chamadas por dia e um contador do que foi usado;
- a chave nunca aparece em mensagem de erro nem em log.
"""
import json
import time

import httpx

from sistema import config
from sistema import hora

ARQUIVO_USO = config.PASTA_LOCAL / "uso_ia.local.json"
TEMPO_LIMITE = 40  # segundos


class IAIndisponivel(Exception):
    """Erro com mensagem pronta para mostrar na tela."""


def ligada(cfg: dict | None = None) -> bool:
    cfg = cfg or config.ler()
    if cfg["provedor"] == "nenhum" or not cfg["base_url"] or not cfg["modelo"]:
        return False
    precisa = config.PROVEDORES.get(cfg["provedor"], {}).get("precisa_chave", True)
    return bool(cfg["chave"]) or not precisa


def uso_de_hoje() -> dict:
    hoje = hora.hoje().isoformat()
    try:
        uso = json.loads(ARQUIVO_USO.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        uso = {}
    if uso.get("dia") != hoje:
        uso = {"dia": hoje, "chamadas": 0, "tokens_entrada": 0, "tokens_saida": 0}
    return uso


def _somar_uso(entrada: int, saida: int) -> None:
    uso = uso_de_hoje()
    uso["chamadas"] += 1
    uso["tokens_entrada"] += entrada
    uso["tokens_saida"] += saida
    ARQUIVO_USO.write_text(json.dumps(uso), encoding="utf-8")


def limite_atingido(cfg: dict | None = None) -> bool:
    """O limite de chamadas do dia vale para tudo que usa a mesma chave, inclusive o agente da PAI."""
    cfg = cfg or config.ler()
    return bool(cfg["limite_diario"]) and uso_de_hoje()["chamadas"] >= cfg["limite_diario"]


def contar_chamada_externa() -> None:
    """Soma uma chamada feita fora deste módulo (o agente da PAI chama o modelo pelo langchain)."""
    _somar_uso(0, 0)


def _cabecalhos(cfg: dict) -> dict:
    return {"Authorization": f"Bearer {cfg['chave']}"} if cfg.get("chave") else {}


def _explicar_erro(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        codigo = e.response.status_code
        if codigo in (401, 403):
            return "O serviço recusou a chave. Confira se ela está certa e ativa."
        if codigo == 404:
            return "Endereço ou modelo não encontrado. Confira o endereço da API e o nome do modelo."
        if codigo == 429:
            texto = e.response.text.lower()
            if "per day" in texto or "perday" in texto or "requests per day" in texto:
                return "A cota de uso de hoje do serviço de IA acabou. Ela volta amanhã."
            return "O serviço de IA atingiu o limite de uso por minuto. Tente de novo daqui a pouco."
        return f"O serviço respondeu com erro {codigo}."
    if isinstance(e, httpx.ConnectError):
        return "Não consegui conectar. Se for o Ollama, confira se ele está aberto no computador."
    if isinstance(e, httpx.TimeoutException):
        return "O serviço demorou demais para responder."
    return "Não foi possível falar com o serviço de IA."


ESPERA_MAXIMA_S = 12      # se o provedor pedir para esperar até isso (limite por minuto), espera e tenta de novo


def _postar(cfg: dict, corpo: dict) -> httpx.Response:
    """POST no provedor. Com 429 e um "tente em N segundos" curto, espera e tenta mais uma vez.

    O Groq gratuito tem 8.000 tokens por minuto, e uma mensagem da Lia gasta 2 ou 3 chamadas: sem isso,
    a segunda pergunta seguida já caía para as regras. Cota do dia esgotada pede horas, e aí não espera.
    """
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    r = httpx.post(url, json=corpo, headers=_cabecalhos(cfg), timeout=TEMPO_LIMITE)
    if r.status_code == 429:
        try:
            espera = float(r.headers.get("retry-after", "") or "nan")
        except ValueError:
            espera = float("nan")
        if 0 < espera <= ESPERA_MAXIMA_S:
            time.sleep(espera + 0.5)
            r = httpx.post(url, json=corpo, headers=_cabecalhos(cfg), timeout=TEMPO_LIMITE)
    r.raise_for_status()
    return r


def listar_modelos(cfg: dict | None = None) -> list[str]:
    cfg = cfg or config.ler()
    r = httpx.get(cfg["base_url"].rstrip("/") + "/models", headers=_cabecalhos(cfg), timeout=TEMPO_LIMITE)
    r.raise_for_status()
    nomes = [m.get("id", "") for m in r.json().get("data", [])]
    return sorted(n.removeprefix("models/") for n in nomes if n)


def conversar(mensagens: list[dict], max_tokens: int = 350, temperatura: float = 0.2, cfg: dict | None = None) -> str:
    """Manda as mensagens ao modelo e devolve o texto da resposta."""
    cfg = cfg or config.ler()
    if not ligada(cfg):
        raise IAIndisponivel("A IA não está configurada. O sistema segue funcionando por regras.")
    uso = uso_de_hoje()
    if cfg["limite_diario"] and uso["chamadas"] >= cfg["limite_diario"]:
        raise IAIndisponivel(f"O limite de {cfg['limite_diario']} chamadas de IA por dia foi atingido.")
    corpo = {"model": cfg["modelo"], "messages": mensagens, "max_tokens": max_tokens, "temperature": temperatura}
    try:
        dados = _postar(cfg, corpo).json()
        texto = dados["choices"][0]["message"].get("content") or ""
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
        raise IAIndisponivel(_explicar_erro(e)) from None
    consumo = dados.get("usage") or {}
    _somar_uso(int(consumo.get("prompt_tokens", 0)), int(consumo.get("completion_tokens", 0)))
    return texto.strip()


def chamar_com_ferramentas(mensagens: list[dict], ferramentas: list[dict], max_tokens: int = 600, temperatura: float = 0.3,
                           cfg: dict | None = None) -> dict:
    """Uma rodada com ferramentas (function calling no formato OpenAI). Devolve a mensagem do modelo como veio.

    A mensagem volta inteira para o histórico na rodada seguinte: os modelos novos do Gemini anexam
    uma assinatura às chamadas de ferramenta e recusam a continuação sem ela.
    """
    cfg = cfg or config.ler()
    if not ligada(cfg):
        raise IAIndisponivel("A IA não está configurada.")
    uso = uso_de_hoje()
    if cfg["limite_diario"] and uso["chamadas"] >= cfg["limite_diario"]:
        raise IAIndisponivel(f"O limite de {cfg['limite_diario']} chamadas de IA por dia foi atingido.")
    corpo = {"model": cfg["modelo"], "messages": mensagens, "tools": ferramentas, "tool_choice": "auto",
             "max_tokens": max_tokens, "temperature": temperatura}
    try:
        dados = _postar(cfg, corpo).json()
        mensagem = dados["choices"][0]["message"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
        raise IAIndisponivel(_explicar_erro(e)) from None
    consumo = dados.get("usage") or {}
    _somar_uso(int(consumo.get("prompt_tokens", 0)), int(consumo.get("completion_tokens", 0)))
    return mensagem


def testar(cfg: dict | None = None) -> dict:
    """Confere a conexão: lista os modelos e faz uma chamada mínima."""
    cfg = cfg or config.ler()
    if not ligada(cfg):
        return {"ok": False, "erro": "Escolha o provedor, o modelo e informe a chave (o Ollama não precisa de chave).", "modelos": []}
    try:
        modelos = listar_modelos(cfg)
    except httpx.HTTPError as e:
        return {"ok": False, "erro": _explicar_erro(e), "modelos": []}
    inicio = time.time()
    try:
        resposta = conversar([{"role": "user", "content": "Responda apenas com a palavra: ok"}], max_tokens=20, temperatura=0, cfg=cfg)
    except IAIndisponivel as e:
        return {"ok": False, "erro": str(e), "modelos": modelos}
    return {"ok": True, "erro": "", "modelos": modelos, "resposta": resposta[:60], "ms": round((time.time() - inicio) * 1000)}
