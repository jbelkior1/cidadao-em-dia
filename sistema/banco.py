"""Conexão com o Supabase (esquema próprio "datempo").

As chaves ficam no arquivo .env na raiz do projeto (fora do git) e nunca vão para o navegador:
só o servidor fala com o banco. Sem .env, o sistema continua funcionando com os relatos em memória.

    SUPABASE_URL=https://<ref>.supabase.co
    SUPABASE_SECRET_KEY=<chave secreta do projeto>

A leitura do .env só acontece quando a API sobe (ciclo de vida), não nos testes.
"""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ESQUEMA = "datempo"


def carregar_env(caminho: Path = RAIZ / ".env") -> None:
    """Lê CHAVE=valor do .env sem sobrescrever o que já está no ambiente."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def credenciais() -> tuple[str, str] | None:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    chave = os.environ.get("SUPABASE_SECRET_KEY", "")
    return (url, chave) if url and chave else None
