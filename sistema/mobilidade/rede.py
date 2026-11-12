"""Rede de trem e metrô: estações, rota mais rápida e desvio quando uma linha para.

Os dados vêm de sistema/dados/rede.json, montado por scripts/montar_rede.py a
partir do GTFS da SPTrans. A rota usa o algoritmo de Dijkstra: o peso de cada
trecho é o tempo de viagem do GTFS, e trocar de linha custa alguns minutos.
"""
import heapq
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "rede.json"
PENALIDADE_TROCA = 4   # minutos a mais na escolha da rota para cada troca de linha: ninguém baldeia para ganhar 1 minuto


def sem_acento(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


@lru_cache(maxsize=1)
def carregar() -> dict:
    rede = json.loads(ARQUIVO.read_text(encoding="utf-8"))
    rede["por_id"] = {e["id"]: e for e in rede["estacoes"]}
    vizinhos = {e["id"]: [] for e in rede["estacoes"]}
    for t in rede["trechos"]:                       # os trens andam nos dois sentidos
        vizinhos[t["de"]].append((t["para"], t["min"], t["linha"]))
        vizinhos[t["para"]].append((t["de"], t["min"], t["linha"]))
    for b in rede["baldeacoes"]:
        vizinhos[b["de"]].append((b["para"], b["min"], "a pé"))
        vizinhos[b["para"]].append((b["de"], b["min"], "a pé"))
    rede["vizinhos"] = vizinhos
    return rede


def linha(numero: str) -> dict:
    return carregar()["linhas"].get(numero, {"numero": numero, "nome": "", "cor": "#888888"})


def estacoes_para_escolha() -> list[dict]:
    """Uma entrada por nome de estação (Sé aparece uma vez, com as linhas 1 e 3)."""
    por_nome: dict[str, dict] = {}
    for e in carregar()["estacoes"]:
        chave = sem_acento(e["nome"])
        item = por_nome.setdefault(chave, {"id": e["id"], "nome": e["nome"], "linhas": []})
        for n in e["linhas"]:
            if n not in item["linhas"]:
                item["linhas"].append(n)
    return sorted(por_nome.values(), key=lambda x: sem_acento(x["nome"]))


def _ids_com_mesmo_nome(estacao_id: str) -> list[str]:
    rede = carregar()
    nome = sem_acento(rede["por_id"][estacao_id]["nome"])
    return [e["id"] for e in rede["estacoes"] if sem_acento(e["nome"]) == nome]


def rota(origem: str, destino: str, evitar: set[str] | None = None) -> dict | None:
    """Rota mais rápida entre duas estações, sem usar as linhas em `evitar`.

    Devolve as etapas (cada trecho contínuo numa linha), o tempo total e as estações.
    """
    rede = carregar()
    if origem not in rede["por_id"] or destino not in rede["por_id"]:
        return None
    evitar = evitar or set()
    alvos = set(_ids_com_mesmo_nome(destino))
    fila = [(0.0, 0.0, i, []) for i in _ids_com_mesmo_nome(origem)]
    heapq.heapify(fila)
    visitados = set()
    while fila:
        custo, tempo, atual, caminho = heapq.heappop(fila)
        if atual in visitados:
            continue
        visitados.add(atual)
        if atual in alvos:
            return _resumir(caminho, tempo, origem, atual)
        for proximo, minutos, via in rede["vizinhos"][atual]:
            if via in evitar or proximo in visitados:
                continue
            anterior = caminho[-1][2] if caminho else None
            troca = via == "a pé" or (anterior not in (None, "a pé") and anterior != via)   # a pé ou trocando de linha na mesma parada
            extra = PENALIDADE_TROCA if troca else 0      # só pesa na escolha; o tempo mostrado é o real
            heapq.heappush(fila, (custo + minutos + extra, tempo + minutos, proximo, caminho + [(atual, proximo, via, minutos)]))
    return None


def rota_saindo_cedo(origem: str, destino: str, falhas: set[str]) -> dict | None:
    """Desvio parcial: vai pela linha com falha só até a PRÓXIMA baldeação e troca ali.

    Serve para quem mora numa estação da própria linha que parou: se o trecho
    perto dela ainda funciona, segue até a primeira estação onde dá para trocar
    de linha (em cada sentido) e, de lá, continua sem usar a linha com falha.
    """
    rede = carregar()
    if origem not in rede["por_id"] or destino not in rede["por_id"]:
        return None
    melhor = None
    for inicio in _ids_com_mesmo_nome(origem):
        # anda pela linha com falha a partir da origem, nos dois sentidos, até achar uma baldeação
        fila = [(0.0, inicio, [])]
        vistos = {inicio}
        while fila:
            tempo, atual, caminho = fila.pop(0)
            tem_troca = any(via not in falhas for _, _, via in rede["vizinhos"][atual])
            if caminho and tem_troca:
                resto = rota(atual, destino, evitar=falhas)
                if resto:
                    total = tempo + resto["minutos"]
                    if melhor is None or total < melhor[0]:
                        melhor = (total, caminho, resto)
                continue                                   # não passa da primeira troca neste sentido
            for proximo, minutos, via in rede["vizinhos"][atual]:
                if via in falhas and proximo not in vistos:
                    vistos.add(proximo)
                    fila.append((tempo + minutos, proximo, caminho + [(atual, proximo, via, minutos)]))
    if not melhor:
        return None
    total, caminho, resto = melhor
    inicio_resto = resto["estacoes"][0]
    primeira = _resumir(caminho, total - resto["minutos"], origem, inicio_resto)
    return {
        "minutos": round(total),
        "etapas": primeira["etapas"] + resto["etapas"],
        "linhas": primeira["linhas"] + resto["linhas"],
        "estacoes": primeira["estacoes"] + resto["estacoes"][1:],
        "baldeacoes": primeira["baldeacoes"] + resto["baldeacoes"],
        "km": round(primeira["km"] + resto["km"], 1),
        "chegada": resto["chegada"],
    }


def _resumir(caminho: list, tempo: float, origem: str, chegada: str) -> dict:
    rede = carregar()
    nome = lambda i: rede["por_id"][i]["nome"]
    etapas = []
    for de, para, via, minutos in caminho:
        if etapas and etapas[-1]["via"] == via:
            etapas[-1]["ate"] = nome(para)
            etapas[-1]["paradas"] += 1
            etapas[-1]["min"] += minutos
        else:
            etapas.append({"via": via, "de": nome(de), "ate": nome(para), "paradas": 1, "min": minutos})
    etapas = [e for e in etapas if not (e["via"] == "a pé" and e["de"] == e["ate"] and e["min"] == 0)]
    for e in etapas:
        e["min"] = round(e["min"])
        if e["via"] != "a pé":
            info = linha(e["via"])
            e["linha"] = {"numero": e["via"], "nome": info["nome"], "cor": info["cor"]}
    estacoes = [origem] + [para for _, para, _, _ in caminho]
    distancia_km = 0.0
    for de, para, via, _ in caminho:
        if via != "a pé":
            a, b = rede["por_id"][de], rede["por_id"][para]
            distancia_km += _km((a["lat"], a["lon"]), (b["lat"], b["lon"]))
    return {
        "minutos": round(tempo),
        "etapas": etapas,
        "linhas": [e["via"] for e in etapas if e["via"] != "a pé"],
        "estacoes": estacoes,
        "baldeacoes": sum(1 for e in etapas if e["via"] == "a pé"),
        "km": round(distancia_km, 1),
        "chegada": chegada,
    }


def _km(a, b) -> float:
    import math
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def alagamentos_na_rota(estacoes: list[str]) -> list[dict]:
    """Estações do trajeto com alagamento registrado no GeoSampa a menos de 500 m."""
    rede = carregar()
    vistas, saida = set(), []
    for i in estacoes:
        e = rede["por_id"][i]
        if e.get("alagamentos_500m") and e["nome"] not in vistas:
            vistas.add(e["nome"])
            saida.append({"estacao": e["nome"], "ocorrencias": e["alagamentos_500m"]})
    return saida
