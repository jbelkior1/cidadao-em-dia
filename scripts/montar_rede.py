"""Monta a rede de trem e metrô do Plano B: estações, linhas, tempos e baldeações.

    uv run python scripts/montar_rede.py [caminho_do_gtfs.zip]

Fontes (públicas, sem cadastro):
- GTFS da SPTrans: sequência de estações e horários de cada linha de trem e metrô.
  Se o caminho não for informado, o arquivo é baixado do site da SPTrans.
- GeoSampa (Prefeitura de SP): ocorrências de alagamento registradas, para contar
  quantas ficam a menos de 500 m de cada estação.

Saída: sistema/dados/rede.json
"""
import csv
import io
import json
import math
import re
import sys
import unicodedata
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "sistema" / "dados" / "rede.json"
URL_GTFS = "http://www.sptrans.com.br/umbraco/Surface/PerfilDesenvolvedor/BaixarGTFS"
URL_ALAGAMENTOS = ("https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature"
                   "&typeNames=geoportal:risco_ocorrencia_alagamento&outputFormat=application/json&srsName=EPSG:4326")

# Número, nome e cor oficial de cada linha
LINHAS = {
    "1": ("Azul", "#0455A1"), "2": ("Verde", "#007E5E"), "3": ("Vermelha", "#EE372F"), "4": ("Amarela", "#FFD400"),
    "5": ("Lilás", "#9B3894"), "6": ("Laranja", "#F68B1F"), "7": ("Rubi", "#CA016B"), "8": ("Diamante", "#97A098"),
    "9": ("Esmeralda", "#01A9A7"), "10": ("Turquesa", "#049FC3"), "11": ("Coral", "#F68368"), "12": ("Safira", "#133C8D"),
    "13": ("Jade", "#00B352"), "15": ("Prata", "#868686"), "17": ("Ouro", "#C9A227"),
}
BALDEACAO_MIN = 5          # minutos para trocar de linha a pé
RAIO_BALDEACAO_M = 400     # estações de linhas diferentes até esta distância viram baldeação
RAIO_ALAGAMENTO_M = 500


def distancia_m(a, b):
    """Distância em metros entre dois pontos (lat, lon), pela fórmula de Haversine."""
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def sem_acento(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


def nome_limpo(nome):
    """'Lapa (linha 7)' vira 'Lapa'; 'Corinthians-itaquera' vira 'Corinthians-Itaquera'."""
    nome = re.sub(r"\s*\(.*?\)\s*", " ", nome).strip()
    nome = re.sub(r"\s+Metr[ôo]$", "", nome)                  # 'Pinheiros Metrô' vira 'Pinheiros'
    maiuscula = lambda p: p if (p.isupper() and len(p) <= 3) or p in ("de", "da", "do", "das", "dos") else p[:1].upper() + p[1:]
    return " ".join("-".join(maiuscula(q) for q in p.split("-")) for p in nome.split())


def numero_da_linha(nome_curto):
    """'CPTM L07' -> '7', 'METRÔ L1' -> '1', 'METRÔ 15' -> '15', 'METRÔ17A' -> '17'."""
    achado = re.search(r"(\d+)", nome_curto)
    return str(int(achado.group(1))) if achado else None


def minutos(hora):
    h, m, s = (int(x) for x in hora.split(":"))
    return h * 60 + m + s / 60


def ler_gtfs(caminho):
    if caminho:
        dados = Path(caminho).read_bytes()
    else:
        print("Baixando o GTFS da SPTrans...")
        dados = urllib.request.urlopen(URL_GTFS, timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(dados))
    ler = lambda nome: csv.DictReader(io.TextIOWrapper(z.open(nome), encoding="utf-8-sig"))
    rotas = {r["route_id"]: r for r in ler("routes.txt") if r["route_type"] in ("1", "2")}
    viagens = defaultdict(list)
    for t in ler("trips.txt"):
        if t["route_id"] in rotas:
            viagens[t["route_id"]].append(t["trip_id"])
    escolhidas = {ids[0]: rid for rid, ids in viagens.items()}     # uma viagem por rota basta para a sequência
    sequencia = defaultdict(list)
    for st in ler("stop_times.txt"):
        if st["trip_id"] in escolhidas:
            sequencia[st["trip_id"]].append((int(st["stop_sequence"]), st["stop_id"], st["arrival_time"]))
    paradas = {p["stop_id"]: p for p in ler("stops.txt")}
    return rotas, escolhidas, sequencia, paradas


def montar(caminho_gtfs=None):
    rotas, escolhidas, sequencia, paradas = ler_gtfs(caminho_gtfs)

    estacoes = {}          # id -> {nome, lat, lon, linhas}
    trechos = []           # (de, para, minutos, linha)
    por_linha = defaultdict(list)
    for trip_id, rota_id in escolhidas.items():
        linha = numero_da_linha(rotas[rota_id]["route_short_name"])
        if linha not in LINHAS:
            continue
        seq = sorted(sequencia[trip_id])
        anterior = None
        for _, stop_id, hora in seq:
            p = paradas[stop_id]
            if stop_id not in estacoes:
                estacoes[stop_id] = {"id": stop_id, "nome": nome_limpo(p["stop_name"]), "lat": float(p["stop_lat"]),
                                     "lon": float(p["stop_lon"]), "linhas": []}
            if linha not in estacoes[stop_id]["linhas"]:
                estacoes[stop_id]["linhas"].append(linha)
            if stop_id not in por_linha[linha]:
                por_linha[linha].append(stop_id)
            if anterior:
                duracao = max(1.0, round(minutos(hora) - minutos(anterior[1]), 1))
                trechos.append({"de": anterior[0], "para": stop_id, "min": duracao, "linha": linha})
            anterior = (stop_id, hora)

    # baldeações: estações de linhas diferentes perto uma da outra
    baldeacoes = []
    ids = list(estacoes)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            ea, eb = estacoes[a], estacoes[b]
            if set(ea["linhas"]) & set(eb["linhas"]):
                continue
            d = distancia_m((ea["lat"], ea["lon"]), (eb["lat"], eb["lon"]))
            mesmo_nome = sem_acento(ea["nome"]) == sem_acento(eb["nome"])
            if d <= RAIO_BALDEACAO_M or (mesmo_nome and d <= 800):
                baldeacoes.append({"de": a, "para": b, "min": BALDEACAO_MIN, "metros": round(d)})

    # alagamentos registrados perto de cada estação
    try:
        geo = json.loads(urllib.request.urlopen(URL_ALAGAMENTOS, timeout=120).read())
        pontos = [(f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0]) for f in geo["features"] if f.get("geometry")]
    except Exception as erro:  # sem GeoSampa a rede sai do mesmo jeito, só sem essa informação
        print("Aviso: não consegui ler os alagamentos do GeoSampa:", erro)
        pontos = []
    for e in estacoes.values():
        e["alagamentos_500m"] = sum(1 for p in pontos if distancia_m((e["lat"], e["lon"]), p) <= RAIO_ALAGAMENTO_M)

    rede = {
        "meta": {"gerado_em": date.today().isoformat(), "fonte_rede": "GTFS da SPTrans (linhas de trem e metrô)",
                 "fonte_alagamentos": "GeoSampa, camada risco_ocorrencia_alagamento", "alagamentos_lidos": len(pontos),
                 "raio_alagamento_m": RAIO_ALAGAMENTO_M, "baldeacao_min": BALDEACAO_MIN},
        "linhas": {n: {"numero": n, "nome": LINHAS[n][0], "cor": LINHAS[n][1], "estacoes": por_linha[n]} for n in LINHAS if n in por_linha},
        "estacoes": sorted(estacoes.values(), key=lambda e: sem_acento(e["nome"])),
        "trechos": trechos,
        "baldeacoes": baldeacoes,
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(rede, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(estacoes)} estações, {len(rede['linhas'])} linhas, {len(trechos)} trechos, {len(baldeacoes)} baldeações, "
          f"{len(pontos)} alagamentos lidos -> {SAIDA}")
    return rede


if __name__ == "__main__":
    montar(sys.argv[1] if len(sys.argv) > 1 else None)
