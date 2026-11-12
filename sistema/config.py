"""Configuração local do sistema.

Fica em config.local.json, na raiz do projeto, e NÃO vai para o git.
É onde moram o provedor de IA, o modelo e a chave. A chave nunca sai daqui:
as telas recebem só os quatro últimos caracteres.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO = RAIZ / "config.local.json"

PROVEDORES = {
    "groq": {
        "nome": "Groq", "base_url": "https://api.groq.com/openai/v1", "modelo": "llama-3.3-70b-versatile",
        "precisa_chave": True, "nota": "Citado no enunciado da PAI. Costuma ter camada gratuita com limite de uso.",
    },
    "ollama": {
        "nome": "Ollama (no seu computador)", "base_url": "http://localhost:11434/v1", "modelo": "llama3.2",
        "precisa_chave": False, "nota": "Citado no enunciado da PAI. Roda no próprio computador: nada sai dele.",
    },
    "gemini": {
        "nome": "Gemini", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "modelo": "gemini-3.1-flash-lite",
        "precisa_chave": True, "nota": "Na entrega da PAI, só com autorização do professor.",
    },
    "outro": {
        "nome": "Outro serviço no formato OpenAI", "base_url": "", "modelo": "",
        "precisa_chave": True, "nota": "Informe o endereço da API e o nome do modelo.",
    },
}

PADRAO = {"provedor": "nenhum", "base_url": "", "modelo": "", "chave": "", "limite_diario": 100}


def ler() -> dict:
    """Devolve a configuração completa (com a chave). Só o backend usa."""
    cfg = dict(PADRAO)
    try:
        cfg.update(json.loads(ARQUIVO.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return cfg


def gravar(novo: dict) -> dict:
    """Grava só os campos conhecidos. Chave vazia ou ausente mantém a que já existe."""
    cfg = ler()
    for campo in ("provedor", "base_url", "modelo"):
        if campo in novo and isinstance(novo[campo], str):
            cfg[campo] = novo[campo].strip()
    if isinstance(novo.get("limite_diario"), int) and novo["limite_diario"] >= 0:
        cfg["limite_diario"] = novo["limite_diario"]
    if novo.get("apagar_chave"):
        cfg["chave"] = ""
    elif isinstance(novo.get("chave"), str) and novo["chave"].strip():
        cfg["chave"] = novo["chave"].strip()
    if cfg["provedor"] in PROVEDORES and not cfg["base_url"]:
        cfg["base_url"] = PROVEDORES[cfg["provedor"]]["base_url"]
    ARQUIVO.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg


def publico() -> dict:
    """A configuração que pode ir para a tela: sem a chave."""
    cfg = ler()
    chave = cfg.pop("chave", "")
    cfg["tem_chave"] = bool(chave)
    cfg["final_da_chave"] = chave[-4:] if len(chave) >= 8 else ""
    return cfg
