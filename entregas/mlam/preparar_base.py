#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Prepara a base "ocorrências criminais no entorno das estações de trem e metrô de São Paulo".

Usada em duas frentes da Global Solution 2026.2 (FIAP, tema CitizenTech):
  - app "Plano B": mostra, por estação, quando e que tipo de ocorrência é mais comum por perto;
  - matéria MLAM: base real para a análise estatística (regressão etc.).

O que o script faz, em ordem:
  1. Lê a planilha oficial da SSP-SP (SPDadosCriminais_2026.xlsx, abas de dados) e guarda
     só as colunas necessárias. Logradouro, número, BO e qualquer dado de pessoa NÃO são lidos.
  2. Fica só com o município de São Paulo e com coordenadas válidas dentro do retângulo
     lat -24,0 a -23,3 / lon -47,0 a -46,3 (latitude/longitude zeradas ou nulas são descartadas).
  3. Lê o GTFS da SPTrans, pega as paradas das rotas de trilho (route_type 1 = metrô, 2 = trem)
     e agrupa estações de mesmo nome (sem o trecho entre parênteses) a menos de 350 m.
  4. Para cada estação, conta as ocorrências num raio de 300 m (Haversine), por faixa de horário
     e por tipo (roubo, furto, outros).
  5. Grava o JSON do app, o CSV da MLAM e imprime um resumo (usado no LEIA-ME).

Uso:
    python preparar_base.py CAMINHO_DO_XLSX --gtfs CAMINHO_DO_sptrans.zip [--cache-dir PASTA]

--cache-dir (opcional) guarda a leitura do xlsx (lenta) num arquivo temporário para rodadas
seguintes; o cache tem só colunas não identificadoras. O resultado final é o mesmo com ou sem cache.
Dependências: pandas, openpyxl (numpy vem junto com o pandas).
"""
import argparse
import csv
import io
import json
import math
import re
import sys
import time
import unicodedata
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------------------
# Parâmetros fixos da análise
# ----------------------------------------------------------------------------------------------
URL_FONTE = "https://www.ssp.sp.gov.br/assets/estatistica/transparencia/spDados/SPDadosCriminais_2026.xlsx"
RAIO_M = 300                    # raio de contagem ao redor da estação
RAIO_AGRUPAR_M = 350            # estações de mesmo nome a menos disso viram uma só
RAIO_MUNICIPIO_M = 500          # raio para checar se a estação está mesmo no município de SP
LAT_MIN, LAT_MAX = -24.0, -23.3
LON_MIN, LON_MAX = -47.0, -46.3
MARCO_ZERO = (-23.5503, -46.6339)   # Praça da Sé
GERADO_EM = "2026-11-12"
R_TERRA_M = 6371008.8

# Só estas colunas da planilha são lidas (nenhuma identifica pessoa ou endereço).
COLUNAS = ["NOME_MUNICIPIO", "DATA_REGISTRO", "DATA_OCORRENCIA_BO", "HORA_OCORRENCIA_BO",
           "DESC_PERIODO", "LATITUDE", "LONGITUDE", "RUBRICA", "DESCR_CONDUTA",
           "NATUREZA_APURADA", "MES_ESTATISTICA"]

FAIXAS = ["madrugada", "manha", "tarde", "noite"]
TIPOS = ["roubo", "furto", "outros"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]


def sem_acento(txt):
    """Minúsculo e sem acento, para comparar textos."""
    txt = unicodedata.normalize("NFKD", str(txt))
    return "".join(c for c in txt if not unicodedata.combining(c)).lower().strip()


# ----------------------------------------------------------------------------------------------
# 1. Leitura da planilha
# ----------------------------------------------------------------------------------------------
def ler_planilha(xlsx, cache_dir=None):
    """Lê as abas de dados (todas menos a do dicionário) e devolve um DataFrame só com COLUNAS."""
    cache = None
    if cache_dir:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        stem = Path(xlsx).stem
        tam = Path(xlsx).stat().st_size
        cache = Path(cache_dir) / f"{stem}_{tam}_leitura.pkl"
        if cache.exists():
            # Seguro: o pickle é um cache gerado por este mesmo script na pasta temporária do usuário.
            # Não aponte --cache-dir para uma pasta com arquivos de terceiros.
            print(f"[cache] usando {cache.name}")
            return pd.read_pickle(cache)

    import openpyxl
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    abas = [n for n in wb.sheetnames if not n.lower().startswith("campos")]
    print(f"Abas de dados: {abas}")
    linhas = []
    for aba in abas:
        it = wb[aba].iter_rows(values_only=True)
        cab = [str(c).strip() if c is not None else "" for c in next(it)]
        idx = [cab.index(c) for c in COLUNAS]
        n0 = len(linhas)
        for r in it:
            linhas.append(tuple(r[i] for i in idx))
        print(f"  {aba}: {len(linhas) - n0} linhas")
    wb.close()
    df = pd.DataFrame(linhas, columns=COLUNAS)
    if cache is not None:
        df.to_pickle(cache)
    return df


# ----------------------------------------------------------------------------------------------
# 2. Limpeza e classificação das ocorrências
# ----------------------------------------------------------------------------------------------
def para_float(serie):
    """Converte latitude/longitude em número (aceita vírgula decimal e texto 'NULL')."""
    s = serie.astype(str).str.strip().str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def faixa_horaria(hora, periodo):
    """Faixa pelo HORA_OCORRENCIA_BO; se faltar, usa DESC_PERIODO. Sem nenhum dos dois: 'sem_faixa'."""
    h = None
    if hasattr(hora, "hour"):                       # datetime.time / datetime
        h = hora.hour
    elif isinstance(hora, str):
        m = re.match(r"^\s*(\d{1,2}):\d{2}", hora)
        if m:
            h = int(m.group(1))
    elif isinstance(hora, (int, float)) and hora == hora and 0 <= hora < 1:   # fração do dia do Excel
        h = int(hora * 24)
    if h is not None and 0 <= h <= 23:
        return "madrugada" if h < 6 else "manha" if h < 12 else "tarde" if h < 18 else "noite"
    p = sem_acento(periodo)
    if p.startswith("de madrugada"):
        return "madrugada"
    if p.startswith("pela manha"):
        return "manha"
    if p.startswith("a tarde"):
        return "tarde"
    if p.startswith("a noite"):
        return "noite"
    return "sem_faixa"                              # 'Em hora incerta' ou vazio


def tipo_ocorrencia(rubrica, natureza):
    """Agrupa em roubo / furto / outros pela RUBRICA (e, se vazia, pela NATUREZA_APURADA).
    Latrocínio e extorsão ficam em 'outros' (rubricas próprias, não 'Roubo ...')."""
    for campo in (rubrica, natureza):
        t = sem_acento(campo)
        if t in ("", "null", "nan"):
            continue
        if t.startswith("roubo"):
            return "roubo"
        if t.startswith("furto"):
            return "furto"
        return "outros"
    return "outros"


def celular_possivel(rubrica, conduta, natureza):
    """Procura a palavra 'celular' nos campos de texto de classificação.
    Resultado esperado: a planilha SPDados não traz o objeto subtraído; ver LEIA-ME."""
    txt = sem_acento(f"{rubrica} {conduta} {natureza}")
    return ("celular" in txt) or ("telefone" in txt)


def preparar_ocorrencias(df):
    """Aplica os filtros e devolve (validas, resumo). 'validas' tem lat, lon, faixa, tipo."""
    resumo = {"linhas_lidas": int(len(df))}

    # Período coberto: maior data de registro e de ocorrência existentes na planilha.
    dreg = pd.to_datetime(df["DATA_REGISTRO"], errors="coerce")
    docr = pd.to_datetime(df["DATA_OCORRENCIA_BO"], errors="coerce")
    resumo["registro_min"] = str(dreg.min().date())
    resumo["registro_max"] = str(dreg.max().date())
    resumo["ocorrencia_min"] = str(docr.min().date())
    resumo["ocorrencia_max"] = str(docr.max().date())
    resumo["mes_estatistica_max"] = int(pd.to_numeric(df["MES_ESTATISTICA"], errors="coerce").max())
    resumo["ocorrencias_antes_de_2026"] = int((docr < "2026-01-01").sum())

    df = df.copy()
    df["lat"] = para_float(df["LATITUDE"])
    df["lon"] = para_float(df["LONGITUDE"])
    dentro = df["lat"].between(LAT_MIN, LAT_MAX) & df["lon"].between(LON_MIN, LON_MAX)
    resumo["coord_invalida_todas_cidades"] = int((~dentro).sum())

    mun = df["NOME_MUNICIPIO"].map(sem_acento)
    eh_sp = mun.isin(["s.paulo", "sao paulo", "s. paulo"])
    resumo["linhas_municipio_sp"] = int(eh_sp.sum())
    resumo["sp_coord_invalida"] = int((eh_sp & ~dentro).sum())
    resumo["sp_validas"] = int((eh_sp & dentro).sum())
    resumo["linhas_outros_municipios"] = int((~eh_sp).sum())
    resumo["outros_municipios_com_coord_valida"] = int((~eh_sp & dentro).sum())

    # Faixa e tipo calculados só para o que será usado (SP válidas e vizinhas p/ checar município).
    df["sp"] = eh_sp
    ok = df[dentro].copy()
    ok["faixa"] = [faixa_horaria(h, p) for h, p in zip(ok["HORA_OCORRENCIA_BO"], ok["DESC_PERIODO"])]
    ok["tipo"] = [tipo_ocorrencia(r, n) for r, n in zip(ok["RUBRICA"], ok["NATUREZA_APURADA"])]
    ok["celular"] = [celular_possivel(r, c, n) for r, c, n in
                     zip(ok["RUBRICA"], ok["DESCR_CONDUTA"], ok["NATUREZA_APURADA"])]
    sp = ok[ok["sp"]]
    resumo["sp_faixa"] = {k: int(v) for k, v in sp["faixa"].value_counts().items()}
    resumo["sp_tipo"] = {k: int(v) for k, v in sp["tipo"].value_counts().items()}
    resumo["sp_celular_pelo_texto"] = int(sp["celular"].sum())
    resumo["sp_hora_vazia"] = int(sp["HORA_OCORRENCIA_BO"].map(
        lambda h: not hasattr(h, "hour")).sum())
    return ok[["lat", "lon", "faixa", "tipo", "celular", "sp"]].reset_index(drop=True), resumo


# ----------------------------------------------------------------------------------------------
# 3. Estações a partir do GTFS
# ----------------------------------------------------------------------------------------------
def haversine_m(lat1, lon1, lat2, lon2):
    """Distância em metros (vale para escalares e arrays do numpy)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlmb = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * R_TERRA_M * np.arcsin(np.sqrt(a))


def nome_linha(route_short_name):
    """'CPTM L07' -> '7'; 'METRÔ L1' -> '1'; 'METRÔ 15' -> '15'; 'METRÔ17A' -> '17'."""
    m = re.search(r"(\d+)", route_short_name)
    return str(int(m.group(1))) if m else route_short_name.strip()


def ler_estacoes(gtfs_zip):
    """Paradas das rotas de trilho (route_type 1 ou 2), agrupadas por nome e proximidade."""
    def ler(zf, nome, enc, **kw):
        with zf.open(nome) as f:
            return pd.read_csv(io.TextIOWrapper(f, encoding=enc), dtype=str, **kw)

    with zipfile.ZipFile(gtfs_zip) as zf:
        # routes/trips/stop_times usam bytes em outro encoding (ids com 'METRÔ'): ler como latin-1
        # de forma consistente nos três arquivos para os ids baterem. stops.txt é UTF-8.
        rotas = ler(zf, "routes.txt", "latin-1")
        rotas = rotas[rotas["route_type"].isin(["1", "2"])]
        trips = ler(zf, "trips.txt", "latin-1")
        trips = trips[trips["route_id"].isin(rotas["route_id"])]
        st = ler(zf, "stop_times.txt", "latin-1", usecols=["trip_id", "stop_id"])
        stops = ler(zf, "stops.txt", "utf-8")

    st = st[st["trip_id"].isin(trips["trip_id"])].merge(trips[["trip_id", "route_id"]])
    st = st.drop_duplicates(["stop_id", "route_id"])
    m = st.merge(stops, on="stop_id").merge(rotas[["route_id", "route_short_name"]])
    m["lat"] = m["stop_lat"].astype(float)
    m["lon"] = m["stop_lon"].astype(float)
    m["linha"] = m["route_short_name"].map(nome_linha)
    # nome sem o trecho entre parênteses: "Lapa (linha 7)" -> "Lapa"
    m["nome"] = m["stop_name"].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
    paradas = m.groupby("stop_id").agg(nome=("nome", "first"), lat=("lat", "first"),
                                       lon=("lon", "first"),
                                       linhas=("linha", lambda s: set(s))).reset_index()

    # Agrupar paradas de mesmo nome a menos de 350 m (união por componentes conexos).
    n = len(paradas)
    pai = list(range(n))

    def achar(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    chave = paradas["nome"].map(sem_acento)
    for i in range(n):
        for j in range(i + 1, n):
            if chave[i] == chave[j] and haversine_m(paradas.lat[i], paradas.lon[i],
                                                    paradas.lat[j], paradas.lon[j]) < RAIO_AGRUPAR_M:
                pai[achar(i)] = achar(j)
    paradas["grupo"] = [achar(i) for i in range(n)]

    estacoes = []
    for _, g in paradas.groupby("grupo"):
        linhas = sorted(set().union(*g["linhas"]), key=lambda x: (int(re.sub(r"\D", "", x) or 0), x))
        estacoes.append({"estacao": g["nome"].iloc[0], "linhas": linhas,
                         "lat": float(g["lat"].mean()), "lon": float(g["lon"].mean())})
    # Nomes repetidos que não foram agrupados (ex.: Lapa das linhas 7 e 8, a mais de 350 m uma da
    # outra) ganham o sufixo da linha para ficarem distinguíveis no app e na base.
    cont = {}
    for e in estacoes:
        cont[sem_acento(e["estacao"])] = cont.get(sem_acento(e["estacao"]), 0) + 1
    for e in estacoes:
        if cont[sem_acento(e["estacao"])] > 1:
            e["estacao"] = f"{e['estacao']} (linha {'/'.join(e['linhas'])})"
    estacoes.sort(key=lambda e: sem_acento(e["estacao"]))
    return estacoes


# ----------------------------------------------------------------------------------------------
# 4. Contagem por estação
# ----------------------------------------------------------------------------------------------
def contar(estacoes, oc):
    """Preenche contagens por estação. 'oc' tem todas as válidas no retângulo (SP e vizinhas).
    Conta só as de SP; usa as vizinhas apenas para decidir se a estação está no município de SP."""
    lat, lon = oc["lat"].to_numpy(), oc["lon"].to_numpy()
    sp = oc["sp"].to_numpy()
    faixa = oc["faixa"].to_numpy()
    tipo = oc["tipo"].to_numpy()
    cel = oc["celular"].to_numpy()
    mantidas, fora = [], []
    for e in estacoes:
        d = haversine_m(e["lat"], e["lon"], lat, lon)
        # Checagem do município: a estação só fica se, entre os registros com coordenada válida num
        # raio de 500 m, os de São Paulo forem mais numerosos que os das demais cidades. Estação sem
        # nenhum registro por perto (empate em zero) também sai: está fora da área coberta
        # (ex.: Jundiaí, Mogi das Cruzes) e contaria zero por falta de dado, não por segurança.
        perto = d <= RAIO_MUNICIPIO_M
        n_sp, n_outros = int((perto & sp).sum()), int((perto & ~sp).sum())
        e["_sp500"], e["_outros500"] = n_sp, n_outros
        if n_sp <= n_outros:
            fora.append(e)
            continue
        sel = (d <= RAIO_M) & sp
        e["total"] = int(sel.sum())
        e["por_faixa"] = {f: int((sel & (faixa == f)).sum()) for f in FAIXAS}
        e["sem_faixa"] = e["total"] - sum(e["por_faixa"].values())
        e["por_tipo"] = {t: int((sel & (tipo == t)).sum()) for t in TIPOS}
        e["celular"] = None          # a base não permite identificar celular (ver LEIA-ME)
        e["_celular_texto"] = int((sel & cel).sum())
        e["faixa_mais_comum"] = (max(FAIXAS, key=lambda f: e["por_faixa"][f])
                                 if sum(e["por_faixa"].values()) else None)
        e["dist_marco_zero_km"] = round(float(haversine_m(e["lat"], e["lon"], *MARCO_ZERO)) / 1000, 3)
        mantidas.append(e)
    return mantidas, fora


# ----------------------------------------------------------------------------------------------
# 5. Saídas
# ----------------------------------------------------------------------------------------------
def gravar(mantidas, resumo, json_path, csv_path, observacao):
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(csv_path).parent.mkdir(parents=True, exist_ok=True)

    meta = {"fonte": URL_FONTE, "periodo": resumo["periodo_texto"], "raio_m": RAIO_M,
            "gerado_em": GERADO_EM, "observacao": observacao}
    lista = []
    for e in mantidas:
        lista.append({"estacao": e["estacao"], "linhas": e["linhas"],
                      "lat": round(e["lat"], 6), "lon": round(e["lon"], 6), "total": e["total"],
                      "por_faixa": e["por_faixa"], "sem_faixa": e["sem_faixa"],
                      "por_tipo": e["por_tipo"], "celular": e["celular"],
                      "faixa_mais_comum": e["faixa_mais_comum"]})
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "estacoes": lista}, f, ensure_ascii=False, indent=1)

    cols = ["estacao", "linhas", "qtd_linhas", "lat", "lon", "total", "roubo", "furto", "outros",
            "madrugada", "manha", "tarde", "noite", "sem_faixa", "celular", "dist_marco_zero_km"]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for e in mantidas:
            w.writerow([e["estacao"], "-".join(e["linhas"]), len(e["linhas"]),
                        round(e["lat"], 6), round(e["lon"], 6), e["total"],
                        e["por_tipo"]["roubo"], e["por_tipo"]["furto"], e["por_tipo"]["outros"],
                        e["por_faixa"]["madrugada"], e["por_faixa"]["manha"],
                        e["por_faixa"]["tarde"], e["por_faixa"]["noite"], e["sem_faixa"],
                        "", e["dist_marco_zero_km"]])    # celular vazio = não disponível


def main():
    aqui = Path(__file__).resolve().parent                    # .../sistema-gs/entregas/mlam
    raiz = aqui.parent.parent                                 # .../sistema-gs
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xlsx", help="caminho do SPDadosCriminais_2026.xlsx")
    ap.add_argument("--gtfs", required=True, help="caminho do sptrans.zip (GTFS da SPTrans)")
    ap.add_argument("--cache-dir", default=None, help="pasta temporária para guardar a leitura do xlsx")
    ap.add_argument("--json", default=str(raiz / "sistema" / "dados" / "seguranca_estacoes.json"))
    ap.add_argument("--csv", default=str(aqui / "dados" / "ocorrencias_estacoes_2026.csv"))
    ap.add_argument("--resumo-json", default=None, help="(opcional) grava o resumo da execução")
    a = ap.parse_args()

    t0 = time.time()
    df = ler_planilha(a.xlsx, a.cache_dir)
    oc, resumo = preparar_ocorrencias(df)
    estacoes = ler_estacoes(a.gtfs)
    resumo["estacoes_gtfs_agrupadas"] = len(estacoes)
    mantidas, fora = contar(estacoes, oc)
    resumo["estacoes_final"] = len(mantidas)
    resumo["estacoes_fora_de_sp"] = sorted(e["estacao"] for e in fora)

    # Período: o último mês com dados é o maior MES_ESTATISTICA (mês do registro).
    mes_fim = MESES[resumo["mes_estatistica_max"] - 1]
    resumo["periodo_texto"] = f"jan a {mes_fim} de 2026"
    observacao = (
        "Ocorrências registradas à SSP-SP no município de São Paulo com coordenada válida, contadas num "
        f"raio de {RAIO_M} m da estação (raios de estações vizinhas se sobrepõem, então a mesma ocorrência "
        "pode contar em mais de uma estação). Tipos: roubo e furto pela rubrica; o resto vai em 'outros'. "
        "'sem_faixa' = hora incerta ou ausente (entra no total, não nas faixas). "
        "'celular' é null: a planilha não informa o objeto subtraído. Só mostra o que foi registrado e "
        "geolocalizado, não é taxa de risco (não considera o fluxo de passageiros) e a base inclui "
        f"alguns fatos ocorridos antes de 2026, registrados de janeiro a {mes_fim} de 2026."
    )
    gravar(mantidas, resumo, a.json, a.csv, observacao)

    resumo["segundos"] = round(time.time() - t0, 1)
    top = sorted(mantidas, key=lambda e: -e["total"])[:5]
    resumo["top5"] = [(e["estacao"], e["total"]) for e in top]
    resumo["total_estacoes_soma"] = sum(e["total"] for e in mantidas)
    resumo["celular_pelo_texto_em_estacoes"] = sum(e["_celular_texto"] for e in mantidas)
    resumo["estacoes_total_zero"] = sorted(e["estacao"] for e in mantidas if e["total"] == 0)
    texto = json.dumps(resumo, ensure_ascii=False, indent=1)
    print(texto)
    if a.resumo_json:
        Path(a.resumo_json).write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
