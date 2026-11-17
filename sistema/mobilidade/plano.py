"""Monta o "Antes de sair": rota, situação das linhas, chuva, alagamento,
segurança, energia e, se uma linha do trajeto falhar, esperar ou desviar.
"""
import json
from datetime import datetime
from pathlib import Path

from sistema import hora

from sistema.mobilidade import decisao, fontes, rede

DADOS = Path(__file__).resolve().parent.parent / "dados"
LIMITE_DESVIO_MIN = 20     # até este acréscimo, desviar costuma compensar


def _carregar_json(nome: str):
    try:
        return json.loads((DADOS / nome).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


RAIO_CASAMENTO_KM = 0.4    # a base da SSP usa os nomes crus do GTFS; se o nome não bater, vale a estação mais próxima


def seguranca_da_estacao(estacao_id: str) -> dict | None:
    """Ocorrências da SSP perto da estação: pelo nome e, se não bater, pela mais próxima em até 400 m."""
    dados = _carregar_json("seguranca_estacoes.json")
    if not dados:
        return None
    alvo = rede.carregar()["por_id"][estacao_id]
    lista = dados.get("estacoes", [])
    achada = next((e for e in lista if rede.sem_acento(e.get("estacao", "")) == rede.sem_acento(alvo["nome"])), None)
    if not achada:
        perto = sorted(lista, key=lambda e: rede._km((alvo["lat"], alvo["lon"]), (e["lat"], e["lon"])))
        if perto and rede._km((alvo["lat"], alvo["lon"]), (perto[0]["lat"], perto[0]["lon"])) <= RAIO_CASAMENTO_KM:
            achada = perto[0]
    if not achada:
        return None                       # estação fora do município de São Paulo: a base só cobre a capital
    return {**achada, "estacao": alvo["nome"], "meta": dados.get("meta", {})}


def energia_da_rota(km: float) -> dict | None:
    try:
        from sistema.mobilidade import energia
    except ImportError:
        return None
    return energia.comparar(km)


def _linhas_com_situacao(numeros: list[str], situacao: dict, simular: str | None) -> list[dict]:
    saida = []
    for n in dict.fromkeys(numeros):
        info = rede.linha(n)
        atual = situacao["linhas"].get(n)
        item = {"numero": n, "nome": info["nome"], "cor": info["cor"],
                "status": atual["status"] if atual else "Sem informação", "nivel": atual["nivel"] if atual else "sem_dado",
                "operadora": atual["operadora"] if atual else "", "simulado": False}
        if simular == n:
            item.update(status="Circulação interrompida (simulação)", nivel="parada", simulado=True)
        saida.append(item)
    return saida


def aviso_alagamento(al: dict) -> str:
    pontos = "1 ponto" if al["ocorrencias"] == 1 else f"{al['ocorrencias']} pontos"
    return f"{al['estacao']}: área com histórico de alagamento ({pontos} a menos de 500 m, GeoSampa); com chuva, atenção"


def antes_de_sair(origem: str, destino: str, simular_falha: str | None = None, agora: datetime | None = None) -> dict:
    agora = agora or hora.agora()
    normal = rede.rota(origem, destino)
    if not normal:
        return {"ok": False, "erro": "Não encontrei um caminho de trem ou metrô entre essas estações."}

    situacao = fontes.situacao_linhas()
    tempo = fontes.avisos_tempo()
    linhas = _linhas_com_situacao(normal["linhas"], situacao, simular_falha)
    com_falha = [l for l in linhas if l["nivel"] in ("parada", "atencao", "encerrada")]
    sem_dado = [l for l in linhas if l["nivel"] == "sem_dado"]
    alagamentos = rede.alagamentos_na_rota(normal["estacoes"])
    avisos_hoje = [a for a in tempo["avisos"] if a["quando"] == "hoje"]

    entradas = {"falha": bool(com_falha), "chuva": bool(avisos_hoje), "alagamento": bool(alagamentos),
                "pico": decisao.horario_de_pico(agora)}
    veredito = decisao.decidir(**entradas)

    motivos = []
    for l in com_falha:
        motivos.append({"tipo": "falha", "texto": f"Linha {l['numero']}-{l['nome']}: {l['status'].lower()}"})
    if not com_falha:
        ok = [l for l in linhas if l["nivel"] == "normal"]
        if ok:
            nums = [l["numero"] for l in ok]
            lista = nums[0] if len(nums) == 1 else ", ".join(nums[:-1]) + " e " + nums[-1]
            motivos.append({"tipo": "ok", "texto": f"Linha{'s' if len(nums) > 1 else ''} {lista} em operação normal agora"})
    for l in sem_dado:
        motivos.append({"tipo": "sem_dado", "texto": f"Linha {l['numero']}: a fonte não traz a situação desta linha"})
    for a in avisos_hoje:
        motivos.append({"tipo": "chuva", "texto": f"Aviso do INMET para São Paulo: {a['tipo'].lower()} ({a['severidade'].lower()}), até {a['fim'][-5:]}"})
    # GeoSampa é histórico (onde já alagou), não alagamento de agora: só vira aviso quando há chuva hoje
    if avisos_hoje:
        for al in alagamentos:
            motivos.append({"tipo": "alagamento", "texto": aviso_alagamento(al)})
    if entradas["pico"]:
        motivos.append({"tipo": "pico", "texto": "Horário de pico: trens mais cheios"})

    plano_b = None
    if com_falha:
        evitar = {l["numero"] for l in com_falha}
        alternativa = rede.rota(origem, destino, evitar=evitar)
        parcial = rede.rota_saindo_cedo(origem, destino, evitar)
        usa_falha = bool(parcial and parcial["linhas"] and parcial["linhas"][0] in evitar)
        espera = {n: fontes.duracao_tipica(n) for n in evitar}
        plano_b = _comparar(normal, alternativa, espera)
        if parcial and usa_falha and (not alternativa or parcial["minutos"] < alternativa["minutos"]):
            primeira = parcial["etapas"][0]
            plano_b["parcial"] = {
                "rota": parcial,
                "acrescimo_min": parcial["minutos"] - normal["minutos"],
                "texto": f"Se o trecho perto de você ainda estiver andando: vá pela Linha {primeira['via']} só até {primeira['ate']} e troque de linha.",
            }
            if not alternativa:
                plano_b["recomendacao"] = "desviar"
                plano_b["texto"] = ("Não há caminho sem essa linha desde a sua estação. Se o trecho perto de você estiver andando, "
                                    f"siga só até {primeira['ate']} e troque. Se estiver parado, procure o ônibus de apoio (PAESE).")

    destino_nome = rede.carregar()["por_id"][normal["chegada"]]["nome"]
    origem_nome = rede.carregar()["por_id"][origem]["nome"]
    return {
        "ok": True,
        "origem": origem_nome, "destino": destino_nome,
        "veredito": {"codigo": veredito, "texto": decisao.TEXTO[veredito], "regra_provisoria": decisao.REGRA_PROVISORIA},
        "entradas": entradas,
        "motivos": motivos,
        "rota": normal,
        "linhas": linhas,
        "plano_b": plano_b,
        "seguranca": {"origem": seguranca_da_estacao(origem), "destino": seguranca_da_estacao(normal["chegada"])},
        "energia": energia_da_rota(normal["km"]),
        "fontes": {
            "linhas": {"nome": situacao["fonte"], "lido_em": situacao["lido_em"], "ok": situacao["ok"], "aviso": situacao.get("aviso", "")},
            "tempo": {"nome": tempo["fonte"], "lido_em": tempo["lido_em"], "ok": tempo["ok"]},
            "rede": "GTFS da SPTrans; alagamentos do GeoSampa",
        },
        "simulacao": simular_falha,
    }


def _comparar(normal: dict, alternativa: dict | None, espera: dict) -> dict:
    historico = next(iter(espera.values())) if espera else {"suficiente": False}
    if not alternativa:
        recomendacao = "esperar"
        texto = "Não há caminho só por trem e metrô sem essa linha. Espere ou procure o ônibus de apoio (PAESE) na estação."
        acrescimo = None
    else:
        acrescimo = alternativa["minutos"] - normal["minutos"]
        if historico.get("suficiente") and historico["mediana_min"] < acrescimo:
            recomendacao = "esperar"
            texto = f"Falhas nesta linha costumam durar cerca de {historico['mediana_min']} min, menos que o desvio (+{acrescimo} min)."
        elif acrescimo <= LIMITE_DESVIO_MIN:
            recomendacao = "desviar"
            texto = f"Desvie: chega cerca de {acrescimo} min depois do normal." if acrescimo > 0 else "Desvie: o caminho alternativo leva o mesmo tempo."
        else:
            recomendacao = "desviar" if not historico.get("suficiente") else "esperar"
            texto = (f"O desvio leva +{acrescimo} min. Ainda não sabemos quanto as falhas desta linha costumam durar, "
                     "então vale considerar o desvio se a falha acabou de começar.")
    return {"recomendacao": recomendacao, "texto": texto, "alternativa": alternativa, "acrescimo_min": acrescimo,
            "historico": historico,
            "apoio": "Ônibus de apoio (PAESE) podem ser acionados pela operadora; em emergência, podem demorar para chegar."}
