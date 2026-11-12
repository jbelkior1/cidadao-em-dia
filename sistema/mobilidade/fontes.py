"""Fontes ao vivo: situação das linhas e avisos de tempo.

- Situação das linhas: agregador público usado por projetos abertos (não é
  fonte oficial). Junta Metrô, CPTM, ViaMobilidade, ViaQuatro, Linha 6 e Linha 13.
- Avisos de tempo: INMET (oficial), filtrados para a cidade de São Paulo.

Cada leitura fica guardada alguns minutos (cache). Quando uma fonte cai, o app
mostra a última leitura com a hora dela e diz que está sem atualização.

Histórico: cada leitura da situação das linhas é gravada em
sistema/dados/historico_linhas.local.jsonl, para calcular quanto as falhas
costumam durar. O arquivo fica só no computador (não vai para o git).
"""
import json
import re
import threading
import time
from datetime import datetime
from pathlib import Path

import httpx

URL_LINHAS = "https://www.tictrens.com.br/helper/line-statuses"
URL_INMET = "https://apiprevmet3.inmet.gov.br/avisos/ativos"
CODIGO_IBGE_SP = "3550308"
CACHE_SEG = 90
HISTORICO = Path(__file__).resolve().parent.parent / "dados" / "historico_linhas.local.jsonl"
CABECALHO = {"User-Agent": "PlanoB-GS2026/0.1 (trabalho academico)"}

_cache: dict[str, dict] = {}
_trava = threading.Lock()


def _agora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def nivel(status: str) -> str:
    """Traduz o texto da operadora em quatro níveis simples."""
    s = (status or "").lower()
    if not s:
        return "sem_dado"
    if "normal" in s:
        return "normal"
    if "encerrad" in s or "fechad" in s:
        return "encerrada"
    if "paralis" in s or "interromp" in s:
        return "parada"
    return "atencao"     # operação parcial, velocidade reduzida, transitória etc.


def _numero(nome: str) -> str | None:
    achado = re.search(r"(\d+)", nome or "")
    return str(int(achado.group(1))) if achado else None


OPERADORAS = {"metro": "Metrô", "cptm": "CPTM", "viamobilidade": "ViaMobilidade", "viaquatro": "ViaQuatro",
              "linhauni": "Linha Uni", "triviatrens": "Trivia Trens", "tictrens": "TIC Trens"}


def _ler_linhas() -> dict:
    r = httpx.get(URL_LINHAS, headers=CABECALHO, timeout=20)
    r.raise_for_status()
    dados = r.json()
    linhas = {}
    for grupo in dados.get("data", []):
        operadora = OPERADORAS.get(str(grupo.get("type", "")).lower(), grupo.get("type", ""))
        for item in grupo.get("listItem", []):
            n = _numero(item.get("line", ""))
            if not n:
                continue
            linhas[n] = {"numero": n, "status": item.get("status") or "", "descricao": item.get("description") or "",
                         "nivel": nivel(item.get("status")), "operadora": operadora,
                         "atualizado": str(grupo.get("dateUpdate", ""))[:19]}
    return linhas


def situacao_linhas() -> dict:
    """{'ok': bool, 'lido_em': str, 'linhas': {numero: {...}}, 'aviso': str}"""
    with _trava:
        guardado = _cache.get("linhas")
        if guardado and time.time() - guardado["t"] < CACHE_SEG:
            return guardado["valor"]
        try:
            valor = {"ok": True, "lido_em": _agora(), "linhas": _ler_linhas(), "aviso": "",
                     "fonte": "Agregador público da situação das linhas (não oficial)"}
            _gravar_historico(valor)
        except Exception:
            if guardado:
                valor = dict(guardado["valor"], ok=False,
                             aviso=f"Sem atualização desde {guardado['valor']['lido_em'][11:16]}. Mostrando a última leitura.")
            else:
                valor = {"ok": False, "lido_em": "", "linhas": {}, "aviso": "Não consegui ler a situação das linhas agora.",
                         "fonte": "Agregador público da situação das linhas (não oficial)"}
            _cache["linhas"] = {"t": time.time() - CACHE_SEG + 30, "valor": valor}   # tenta de novo em 30 s
            return valor
        _cache["linhas"] = {"t": time.time(), "valor": valor}
        return valor


def avisos_tempo() -> dict:
    """Avisos do INMET que valem para a cidade de São Paulo."""
    with _trava:
        guardado = _cache.get("inmet")
        if guardado and time.time() - guardado["t"] < CACHE_SEG * 4:
            return guardado["valor"]
        try:
            r = httpx.get(URL_INMET, headers=CABECALHO, timeout=30)
            r.raise_for_status()
            dados = r.json()
            avisos = []
            for quando in ("hoje", "futuro"):
                for a in dados.get(quando, []):
                    if CODIGO_IBGE_SP in json.dumps(a.get("geocodes", "")) or CODIGO_IBGE_SP in json.dumps(a.get("municipios", "")):
                        avisos.append({
                            "quando": quando, "tipo": a.get("descricao", ""), "severidade": a.get("severidade", ""),
                            "inicio": f"{str(a.get('data_inicio', ''))[:10]} {a.get('hora_inicio', '')}",
                            "fim": f"{str(a.get('data_fim', ''))[:10]} {a.get('hora_fim', '')}",
                            "riscos": a.get("riscos", ""), "instrucoes": a.get("instrucoes", ""),
                        })
            valor = {"ok": True, "lido_em": _agora(), "avisos": avisos, "fonte": "INMET, avisos meteorológicos"}
        except Exception:
            valor = dict(guardado["valor"], ok=False) if guardado else {"ok": False, "lido_em": "", "avisos": [], "fonte": "INMET"}
        _cache["inmet"] = {"t": time.time(), "valor": valor}
        return valor


def _gravar_historico(valor: dict) -> None:
    try:
        registro = {"t": valor["lido_em"], "l": {n: x["nivel"] for n, x in valor["linhas"].items()}}
        with HISTORICO.open("a", encoding="utf-8") as f:
            f.write(json.dumps(registro) + "\n")
    except OSError:
        pass


def duracao_tipica(numero: str) -> dict:
    """Quanto as falhas desta linha duraram no histórico gravado (mediana, em minutos)."""
    episodios, inicio, ultimo = [], None, None
    try:
        linhas = HISTORICO.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        linhas = []
    primeiro = None
    for bruto in linhas:
        try:
            reg = json.loads(bruto)
        except json.JSONDecodeError:
            continue
        t = datetime.fromisoformat(reg["t"])
        primeiro = primeiro or t
        ruim = reg["l"].get(numero) in ("atencao", "parada")
        if ruim and inicio is None:
            inicio = t
        if not ruim and inicio is not None:
            episodios.append((t - inicio).total_seconds() / 60)
            inicio = None
        ultimo = t
    episodios = sorted(e for e in episodios if e >= 2)
    coletando_desde = primeiro.strftime("%d/%m %H:%M") if primeiro else None
    if len(episodios) < 3:
        return {"suficiente": False, "episodios": len(episodios), "coletando_desde": coletando_desde}
    meio = len(episodios) // 2
    mediana = episodios[meio] if len(episodios) % 2 else (episodios[meio - 1] + episodios[meio]) / 2
    return {"suficiente": True, "episodios": len(episodios), "mediana_min": round(mediana), "coletando_desde": coletando_desde}


def coletar_em_segundo_plano(intervalo_seg: int = 120) -> None:
    """Lê a situação das linhas de tempos em tempos enquanto a API estiver ligada."""
    def laco():
        while True:
            try:
                situacao_linhas()
            except Exception:
                pass
            time.sleep(intervalo_seg)
    threading.Thread(target=laco, daemon=True, name="coletor-linhas").start()
