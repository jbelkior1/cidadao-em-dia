# Dá Tempo? em um container só: a API em Python serve também as telas compiladas.
# Passo a passo do servidor em DEPLOY.md.

# 1. Telas (React, Vite e Tailwind)
FROM node:24-alpine AS telas
WORKDIR /web
RUN npm install -g pnpm@11.25.0
COPY sistema/web/package.json sistema/web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY sistema/web/ ./
RUN pnpm build

# 2. API (FastAPI) com as entregas que o app usa
FROM python:3.13-slim AS api
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
# o que o app lê enquanto roda (sistema, entregas, pesquisa, documentação) e o que o checklist cita com link
COPY sistema/ sistema/
COPY entregas/ entregas/
COPY pesquisa/ pesquisa/
COPY docs/ docs/
COPY tests/ tests/
COPY scripts/ scripts/
COPY banco/ banco/
COPY README.md DEPLOY.md ./
COPY --from=telas /web/dist sistema/web/dist

# usuário sem privilégio; /dados guarda o contador de uso da IA e o histórico das linhas (volume)
RUN useradd --create-home --uid 10001 datempo && mkdir -p /dados && chown datempo /dados
USER datempo
ENV PATH="/app/.venv/bin:$PATH" PASTA_DADOS_LOCAIS=/dados MODO_PUBLICO=1
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/api/saude', timeout=4)"
# um processo só: os relatos de demonstração, o teste da DSA e o coletor das linhas vivem na memória dele
CMD ["uvicorn", "sistema.api:app", "--host", "0.0.0.0", "--port", "8010", "--proxy-headers", "--forwarded-allow-ips", "*"]
