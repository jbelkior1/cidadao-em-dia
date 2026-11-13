"""Mapa: camadas para desenhar (linhas com situação, estações, alagamentos, segurança, CGE).

Tudo sai de uma chamada só, GET /api/mapa/camadas. O CGE não informa coordenadas,
então os pontos dele aparecem só como lista, nunca no mapa.
"""
import json
from pathlib import Path

from fastapi import APIRouter, Query

from sistema.mobilidade import fontes, plano, rede

router = APIRouter(prefix="/api/mapa", tags=["mapa"])

DADOS = Path(__file__).resolve().parent / "dados"
ALAGAMENTOS = DADOS / "alagamentos_geosampa.json"
SEGURANCA = DADOS / "seguranca_estacoes.json"


def _json(caminho: Path):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _alagamentos() -> list[list[float]]:
    dados = _json(ALAGAMENTOS)
    if not isinstance(dados, dict):
        return []
    return [[p[0], p[1]] for p in dados.get("pontos", []) if isinstance(p, list) and len(p) >= 2]


def _seguranca() -> list[dict]:
    dados = _json(SEGURANCA)
    if not isinstance(dados, dict):
        return []
    return [{"estacao": e["estacao"], "lat": e["lat"], "lon": e["lon"], "total": e["total"], "faixa": e.get("faixa_mais_comum")}
            for e in dados.get("estacoes", []) if "lat" in e and "lon" in e]


def _trechos_por_linha(r: dict) -> dict[str, list]:
    por_linha: dict[str, list] = {}
    for t in r["trechos"]:
        a, b = r["por_id"].get(t["de"]), r["por_id"].get(t["para"])
        if a and b:
            por_linha.setdefault(t["linha"], []).append([[a["lat"], a["lon"]], [b["lat"], b["lon"]]])
    return por_linha


def _cge(valor: dict) -> dict:
    estado = valor.get("estado")
    ativos = valor.get("ativos_lista") or []
    return {
        "ok": bool(valor.get("ok")),
        "estado": {"titulo": estado.get("titulo", ""), "quando": estado.get("quando", "")} if estado else None,
        "ativos": valor.get("ativos"),
        "pontos": [{"bairro": p.get("bairro", ""), "via": p.get("via", ""), "transitavel": bool(p.get("transitavel"))} for p in ativos],
    }


@router.get("/camadas")
def camadas(simular: str | None = Query(None, description="Número da linha para simular falha")) -> dict:
    r = rede.carregar()
    situacao = fontes.situacao_linhas()
    numeros = sorted(r["linhas"], key=lambda n: (int(n) if n.isdigit() else 999, n))
    trechos = _trechos_por_linha(r)
    linhas = [{**l, "trechos": trechos.get(l["numero"], [])}
              for l in plano._linhas_com_situacao(numeros, situacao, simular)]
    for l in linhas:
        l.pop("operadora", None)
    return {
        "lido_em": situacao.get("lido_em") or "",
        "linhas": linhas,
        "estacoes": [{"id": e["id"], "nome": e["nome"], "lat": e["lat"], "lon": e["lon"], "linhas": e["linhas"]} for e in r["estacoes"]],
        "alagamentos": _alagamentos(),
        "seguranca": _seguranca(),
        "cge": _cge(fontes.alertas_cge()),
    }
