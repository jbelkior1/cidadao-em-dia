"""De onde vem o modelo de linguagem, e nada mais.

O provedor é trocável de propósito. O enunciado permite Ollama e Groq direto; provedor pago
(Gemini, OpenAI, Claude) precisa de autorização do professor. O grupo escolheu Gemini, e trocar
é mudar duas variáveis no `.env`, sem tocar no resto do código.

A chave NUNCA entra no repositório: ela é lida de `.env` (que está no .gitignore).

    PAI_PROVEDOR=gemini          # gemini | groq | ollama
    PAI_MODELO=gemini-3.1-flash-lite
    GEMINI_API_KEY=...           # ou GROQ_API_KEY; o Ollama não usa chave
"""
import os
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]

PROVEDORES = {
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
               "chave_env": "GEMINI_API_KEY", "modelo": "gemini-3.1-flash-lite",
               "aviso": "provedor pago: o enunciado pede autorização do professor"},
    "groq": {"base_url": "https://api.groq.com/openai/v1", "chave_env": "GROQ_API_KEY",
             "modelo": "openai/gpt-oss-120b", "aviso": ""},
    "ollama": {"base_url": "http://localhost:11434/v1", "chave_env": "", "modelo": "llama3.1",
               "aviso": "roda na máquina, sem chave"},
}


def carregar_env(caminho: Path = RAIZ / ".env") -> None:
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


@dataclass
class Config:
    provedor: str
    modelo: str
    base_url: str
    tem_chave: bool
    aviso: str


def _chave_do_sistema(provedor: str) -> str:
    """A chave que o app já usa, em config.local.json (fora do git), para não pedir de novo ao grupo."""
    import json
    arq = RAIZ / "config.local.json"
    try:
        cfg = json.loads(arq.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return ""
    return cfg.get("chave", "") if cfg.get("provedor") == provedor else ""


def chave(provedor: str) -> str:
    """Procura no .env primeiro; se não achar, usa a do app. Nunca é impressa nem gravada."""
    p = PROVEDORES.get(provedor, PROVEDORES["gemini"])
    if not p["chave_env"]:
        return "ollama"
    return os.environ.get(p["chave_env"], "") or _chave_do_sistema(provedor)


#: Quando o agente roda dentro do app, ele usa o mesmo provedor que a pessoa escolheu para a Lia
#: (Configurações de IA), em vez do .env: uma troca de provedor vale para o app inteiro.
_DO_APP: dict | None = None


def usar_config_do_app(cfg: dict | None) -> None:
    """Chamado pela ponte do sistema. `cfg` é a configuração do app (provedor, base_url, modelo, chave)."""
    global _DO_APP
    _DO_APP = cfg if cfg and cfg.get("provedor") not in (None, "", "nenhum") and cfg.get("modelo") else None


def config() -> Config:
    if _DO_APP:
        return Config(provedor=_DO_APP["provedor"], modelo=_DO_APP["modelo"], base_url=_DO_APP["base_url"],
                      tem_chave=bool(_DO_APP.get("chave")) or _DO_APP["provedor"] == "ollama", aviso="")
    carregar_env()
    nome = os.environ.get("PAI_PROVEDOR", "gemini").lower()
    p = PROVEDORES.get(nome) or PROVEDORES["gemini"]
    return Config(provedor=nome, modelo=os.environ.get("PAI_MODELO", p["modelo"]),
                  base_url=p["base_url"], tem_chave=bool(chave(nome)), aviso=p["aviso"])


def criar(temperatura: float = 0.0):
    """O cliente do modelo, pela interface compatível com OpenAI que os três provedores falam."""
    from langchain_openai import ChatOpenAI
    c = config()
    p = PROVEDORES.get(c.provedor, PROVEDORES["gemini"])
    k = (_DO_APP.get("chave") or ("ollama" if c.provedor == "ollama" else "")) if _DO_APP else chave(c.provedor)
    if not k:
        raise RuntimeError(f"falta {p['chave_env']} no .env (ou a chave do {c.provedor} em config.local.json)")
    return ChatOpenAI(model=c.modelo, base_url=c.base_url, api_key=k,
                      temperature=temperatura, timeout=60, max_retries=2)
