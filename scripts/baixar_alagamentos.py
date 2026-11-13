"""Baixa os pontos de alagamento do GeoSampa e guarda só as coordenadas.

    uv run python scripts/baixar_alagamentos.py

Fonte: GeoSampa (Prefeitura de São Paulo), camada risco_ocorrencia_alagamento.
Saída: sistema/dados/alagamentos_geosampa.json, com {fonte, baixado_em, pontos: [[lat, lon], ...]}.
Nenhuma outra propriedade da camada é guardada.
"""
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
from montar_rede import URL_ALAGAMENTOS  # noqa: E402

SAIDA = RAIZ / "sistema" / "dados" / "alagamentos_geosampa.json"


def baixar() -> list[list[float]]:
    pedido = urllib.request.Request(URL_ALAGAMENTOS, headers={"User-Agent": "DaTempo-GS2026/0.1 (trabalho academico)"})
    with urllib.request.urlopen(pedido, timeout=120) as r:
        dados = json.load(r)
    pontos = []
    for f in dados.get("features", []):
        coords = (f.get("geometry") or {}).get("coordinates")
        if coords and len(coords) >= 2:
            pontos.append([round(coords[1], 5), round(coords[0], 5)])      # GeoJSON vem como [lon, lat]
    return pontos


def main() -> None:
    pontos = baixar()
    saida = {"fonte": "GeoSampa, Prefeitura de São Paulo (camada risco_ocorrencia_alagamento)",
             "baixado_em": date.today().isoformat(), "pontos": pontos}
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(pontos)} pontos gravados em {SAIDA}")


if __name__ == "__main__":
    main()
