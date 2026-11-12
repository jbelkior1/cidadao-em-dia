"""Laboratório: simulação da sociedade (sem IA).

Inspirado no TinyTroupe (microsoft/TinyTroupe, MIT): personas descritas em JSON
avaliam uma parte do produto, cada uma com a sua realidade.

Como funciona:
  1. Cada persona é um passageiro de São Paulo com internet, familiaridade com o
     celular, confiança em aviso pelo celular, necessidades e um canal preferido
     (sistema/dados/personas.json).
  2. Para a parte do produto e os canais escolhidos, um modelo logístico calcula a
     chance de a persona usar o produto: utilidade menos barreiras.
  3. A fala de cada persona é montada a partir dos motivos que mais pesaram.
  4. Uma população sintética (milhares de pessoas parecidas com as personas, com
     variação aleatória) estima a adesão por perfil.

Tudo aqui é FICTÍCIO: pesos, personas e proporções servem para discutir o
produto, não são pesquisa. O teste com pessoas de verdade (PCP, SERS e PAI pedem)
é que vale. As falas podem vir de um modelo de IA no futuro, trocando a função `falar`.
"""
import json
import math
from pathlib import Path

import numpy as np

PERSONAS = json.loads((Path(__file__).parent / "dados" / "personas.json").read_text(encoding="utf-8"))

NIVEL_INTERNET = {"boa": 1.0, "só no celular, com pacote": 0.6, "quase nenhuma": 0.05}
NECESSIDADE_TEXTO = {"linha_parada": "saber na hora se a linha parou e por onde ir", "chuva": "fugir da chuva forte e dos alagamentos",
                     "seguranca": "saber em que horário a estação é mais tranquila", "direitos": "conseguir a declaração de atraso e saber meus direitos",
                     "custo": "comparar quanto gasto indo de carro ou de trem"}

# partes do produto: o que atendem e quanto exigem de internet e de familiaridade com o celular
PARTES = {
    "Plano B completo": {"atende": ["linha_parada", "chuva", "seguranca", "direitos", "custo"], "internet": 0.55, "letramento": 0.5},
    "Antes de sair": {"atende": ["linha_parada", "chuva", "seguranca", "custo"], "internet": 0.5, "letramento": 0.45},
    "Trem e metrô agora": {"atende": ["linha_parada"], "internet": 0.45, "letramento": 0.3},
    "Pergunte": {"atende": ["direitos", "seguranca"], "internet": 0.5, "letramento": 0.6},
}
# canais: quanto diminuem a exigência e quem os prefere
CANAIS = {
    "App e site": {"internet": 0.0, "letramento": 0.0, "combina": ["app"]},
    "Painel na estação (futuro)": {"internet": -1.0, "letramento": -0.25, "combina": ["painel", "presencial"]},
    "WhatsApp (futuro)": {"internet": -0.2, "letramento": -0.15, "combina": ["whatsapp"]},
}
BARREIRAS = {"internet": "internet", "letramento": "uso do celular", "confianca": "confiança",
             "utilidade": "não atende o que precisa", "nenhuma": "nenhuma"}
SUGESTAO = {"internet": "Mostrar o mesmo aviso em painéis nas estações, sem depender da internet da pessoa",
            "letramento": "Letra grande, áudio e uma frase só: pode ir, saia mais cedo ou use o Plano B",
            "confianca": "Mostrar sempre de onde veio o aviso (operadora, INMET) e a hora da leitura",
            "utilidade": "Incluir os ônibus e as outras linhas que a pessoa usa no dia a dia",
            "nenhuma": "Divulgar nas estações, nos terminais e nas escolas para mais gente conhecer"}


def _chance(p: dict, parte: dict, canal: dict, internet: float | None = None, letramento: float | None = None,
            confianca: float | None = None) -> tuple[float, dict]:
    """Modelo logístico: devolve (chance de usar, peso de cada motivo)."""
    internet = NIVEL_INTERNET[p["internet"]] if internet is None else internet
    letramento = p["letramento"] if letramento is None else letramento
    confianca = p["confianca"] if confianca is None else confianca
    atende = len(set(p["precisa"]) & set(parte["atende"])) / len(p["precisa"])
    utilidade = 1.8 * atende + (0.4 if p["usa_todo_dia"] and "linha_parada" in parte["atende"] else 0)
    b_internet = 4.0 * max(0.0, parte["internet"] + canal["internet"] - internet)
    b_letramento = 3.0 * max(0.0, parte["letramento"] + canal["letramento"] - letramento)
    b_confianca = 1.2 * max(0.0, 0.5 - (confianca + 0.15))   # +0,15: fonte e hora da leitura visíveis aumentam a confiança
    combina = 0.6 if p["prefere"] in canal["combina"] else 0.0
    z = -1.0 + utilidade - b_internet - b_letramento - b_confianca + combina
    pesos = {"internet": b_internet, "letramento": b_letramento, "confianca": b_confianca, "utilidade": max(0.0, 1.3 - utilidade)}
    return 1 / (1 + math.exp(-z)), pesos


def _veredito(chance: float) -> str:
    return "usaria" if chance >= 0.65 else "em dúvida" if chance >= 0.45 else "não usaria"


def falar(p: dict, veredito: str, barreira: str, canal: str, parte_nome: str, pesos: dict) -> str:
    """Monta a fala da persona a partir dos motivos. Pode ser trocada por IA no futuro."""
    terminacao = "a" if p["genero"] == "f" else "o"
    abertura = {"usaria": "Eu usaria, sim.", "em dúvida": "Talvez eu usasse.",
                "não usaria": "Do jeito que está, acho que eu não usaria."}[veredito]
    ajuda = [NECESSIDADE_TEXTO[n] for n in p["precisa"] if n in PARTES[parte_nome]["atende"]]
    frases = [abertura, f"Me ajudaria a {ajuda[0]}." if ajuda else "Não resolve o que eu mais preciso agora."]
    if barreira == "internet" and pesos["internet"] > 0.3:
        frases.append(f"Minha internet é {p['internet']}, então preciso de um jeito que não dependa dela.")
    elif barreira == "letramento" and pesos["letramento"] > 0.3:
        frases.append("Tenho dificuldade com o celular e me perco com muita tela e letra pequena.")
    elif barreira == "confianca" and pesos["confianca"] > 0.1:
        frases.append(f"Já vi aviso errado no celular. Ver de onde veio e a hora me deixa mais tranquil{terminacao}.")
    if canal.startswith("Painel"):
        frases.append("O painel na estação me ajuda porque eu vejo na hora e não gasto a minha internet.")
    frases.append(f"Meu medo é {p['medo']}.")
    return " ".join(frases)


def ouvir_personas(parte_nome: str, canais: list[str]) -> list[dict]:
    parte = PARTES[parte_nome]
    opinioes = []
    for p in PERSONAS:
        canal, chance, pesos = max(((c, *_chance(p, parte, CANAIS[c])) for c in canais), key=lambda x: x[1])
        barreira = max(pesos, key=pesos.get) if max(pesos.values()) >= 0.15 else "nenhuma"
        veredito = _veredito(chance)
        opinioes.append({
            "id": p["id"], "nome": p["nome"], "idade": p["idade"], "quem": p["quem"], "onde": p["onde"], "perfil": p["perfil"],
            "internet": p["internet"], "genero": p["genero"], "canal": canal, "chance": round(chance, 2), "veredito": veredito,
            "nota": round(1 + 4 * chance), "fala": falar(p, veredito, barreira, canal, parte_nome, pesos),
            "barreira": BARREIRAS[barreira], "sugestao": SUGESTAO[barreira], "tem_barreira": barreira != "nenhuma",
        })
    return sorted(opinioes, key=lambda o: -o["chance"])


def simular_populacao(parte_nome: str, canais: list[str], n: int, semente: int) -> dict:
    """População sintética: n pessoas sorteadas a partir das personas, com variação aleatória."""
    rng = np.random.default_rng(semente)
    parte = PARTES[parte_nome]
    pesos = np.array([p["peso"] for p in PERSONAS], dtype=float)
    sorteio = rng.choice(len(PERSONAS), size=n, p=pesos / pesos.sum())
    usam, por_perfil, barreiras = 0, {}, {}
    for i in sorteio:
        p = PERSONAS[i]
        internet = float(np.clip(NIVEL_INTERNET[p["internet"]] + rng.normal(0, 0.15), 0, 1))
        letramento = float(np.clip(p["letramento"] + rng.normal(0, 0.15), 0, 1))
        confianca = float(np.clip(p["confianca"] + rng.normal(0, 0.15), 0, 1))
        chance, motivos = max((_chance(p, parte, CANAIS[c], internet, letramento, confianca) for c in canais), key=lambda x: x[0])
        usa = bool(rng.random() < chance)
        usam += usa
        total, sim = por_perfil.get(p["perfil"], (0, 0))
        por_perfil[p["perfil"]] = (total + 1, sim + usa)
        if not usa:
            b = BARREIRAS[max(motivos, key=motivos.get)]
            barreiras[b] = barreiras.get(b, 0) + 1
    perfis = [{"perfil": k, "pessoas": t, "adesao": round(100 * s / t)} for k, (t, s) in por_perfil.items()]
    return {"adesao": round(100 * usam / n), "perfis": sorted(perfis, key=lambda x: -x["adesao"]),
            "barreiras": [{"barreira": k, "pessoas": v} for k, v in sorted(barreiras.items(), key=lambda x: -x[1])]}


def simular(parte_nome: str, canais: list[str], n: int = 3000, semente: int = 7) -> dict:
    canais = [c for c in canais if c in CANAIS] or ["App e site"]
    opinioes = ouvir_personas(parte_nome, canais)
    populacao = simular_populacao(parte_nome, canais, n, semente)
    sugestoes = {}
    for o in opinioes:
        if o["veredito"] != "usaria" or o["tem_barreira"]:
            sugestoes[o["sugestao"]] = sugestoes.get(o["sugestao"], 0) + 1
    return {
        "parte": parte_nome, "canais": canais, "n": n, "semente": semente,
        "usariam": sum(o["veredito"] == "usaria" for o in opinioes), "total_personas": len(opinioes),
        "opinioes": opinioes, **populacao,
        "sugestoes": [{"sugestao": k, "pessoas": v} for k, v in sorted(sugestoes.items(), key=lambda x: -x[1])],
    }
