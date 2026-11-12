"""Simulação da sociedade (MVP, sem IA).

Inspirado no TinyTroupe (microsoft/TinyTroupe, MIT): personas descritas em JSON
avaliam uma parte do produto, cada uma com a sua perspectiva.

Como funciona nesta versão:
  1. Cada persona tem internet, familiaridade com o celular, confiança no governo,
     necessidades e um canal preferido (data/personas.json).
  2. Para a parte do produto escolhida e os canais disponíveis, um modelo logístico
     calcula a chance de a persona usar o produto (utilidade menos barreiras).
  3. A fala de cada persona é montada a partir dos motivos que mais pesaram.
  4. Uma população sintética (milhares de pessoas parecidas com as personas, com
     variação aleatória) estima a adesão por perfil.

Tudo aqui é FICTÍCIO: os pesos das personas e as distribuições devem ser trocados
pelos dados reais da MLAM (IBGE, PNAD TIC). As falas podem passar a vir de um
modelo de IA (TinyTroupe ou um LLM com a persona no prompt), trocando `falar`.
"""
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PERSONAS = json.loads((Path(__file__).parent.parent / "data" / "personas.json").read_text(encoding="utf-8"))

NIVEL_INTERNET = {"boa": 1.0, "só no celular, com pacote": 0.6, "quase nenhuma": 0.05}
NECESSIDADE_TEXTO = {"documentos": "tirar documento", "beneficios": "saber dos meus direitos",
                     "conta_luz": "pagar menos na conta de luz", "golpe": "não cair em golpe"}

# partes do produto: o que atendem e quanto exigem de internet e de familiaridade com o celular
PARTES = {
    "Cidadão em Dia completo": dict(atende=["documentos", "beneficios", "conta_luz", "golpe"], internet=0.55, letramento=0.5),
    "Meus direitos": dict(atende=["beneficios", "conta_luz"], internet=0.45, letramento=0.4),
    "Tirar uma dúvida": dict(atende=["documentos"], internet=0.5, letramento=0.6),
    "Minha conta de luz": dict(atende=["conta_luz"], internet=0.45, letramento=0.5),
    "Isso é golpe?": dict(atende=["golpe"], internet=0.5, letramento=0.6),
}
# canais: quanto diminuem a exigência e quem os prefere
CANAIS = {
    "App e site": dict(internet=0.0, letramento=0.0, combina=["app"]),
    "Totem no CRAS ou posto": dict(internet=-1.0, letramento=-0.25, combina=["totem", "presencial"]),
    "WhatsApp (futuro)": dict(internet=-0.2, letramento=-0.15, combina=["whatsapp"]),
}
SUGESTAO = {"internet": "Ter um totem no CRAS ou no posto, que funcione sem a internet da pessoa",
            "letramento": "Letra grande, áudio e botões simples, com alguém para ajudar no começo",
            "confianca": "Mostrar sempre a fonte oficial e deixar claro que não pede dados pessoais",
            "utilidade": "Incluir outros serviços que eu uso no dia a dia",
            "nenhuma": "Divulgar no CRAS, na escola e no posto para mais gente conhecer"}


@dataclass
class Opiniao:
    persona: dict
    canal: str
    chance: float
    veredito: str      # "usaria", "em dúvida" ou "não usaria"
    nota: int
    fala: str
    barreira: str      # a barreira que mais pesou
    sugestao: str


def _chance(p: dict, parte: dict, canal: dict, internet: float | None = None, letramento: float | None = None,
            confianca: float | None = None):
    """Modelo logístico: devolve (chance, pesos de cada motivo)."""
    internet = NIVEL_INTERNET[p["internet"]] if internet is None else internet
    letramento = p["letramento"] if letramento is None else letramento
    confianca = p["confianca"] if confianca is None else confianca
    atende = len(set(p["precisa"]) & set(parte["atende"])) / len(p["precisa"])
    utilidade = 1.8 * atende + (0.4 if p["cadunico"] and "beneficios" in parte["atende"] else 0)
    b_internet = 4.0 * max(0.0, parte["internet"] + canal["internet"] - internet)
    b_letramento = 3.0 * max(0.0, parte["letramento"] + canal["letramento"] - letramento)
    b_confianca = 1.2 * max(0.0, 0.5 - (confianca + 0.15))   # +0,15: fonte e data visíveis aumentam a confiança
    combina = 0.6 if p["prefere"] in canal["combina"] else 0.0
    z = -1.0 + utilidade - b_internet - b_letramento - b_confianca + combina
    pesos = {"internet": b_internet, "letramento": b_letramento, "confianca": b_confianca, "utilidade": max(0.0, 1.3 - utilidade)}
    return 1 / (1 + math.exp(-z)), pesos


def _veredito(chance: float) -> str:
    return "usaria" if chance >= 0.65 else "em dúvida" if chance >= 0.45 else "não usaria"


def falar(p: dict, veredito: str, barreira: str, canal: str, parte_nome: str, pesos: dict) -> str:
    """Monta a fala da persona a partir dos motivos. Trocar por IA no futuro."""
    a = "a" if p["genero"] == "f" else "o"
    abertura = {"usaria": "Eu usaria, sim.", "em dúvida": "Talvez eu usasse.", "não usaria": "Do jeito que está, acho que eu não usaria."}[veredito]
    ajuda = [NECESSIDADE_TEXTO[n] for n in p["precisa"] if n in PARTES[parte_nome]["atende"]]
    partes_fala = [abertura]
    if ajuda:
        partes_fala.append(f"Me ajudaria a {ajuda[0]}.")
    else:
        partes_fala.append("Não resolve o que eu mais preciso agora.")
    if barreira == "internet" and pesos["internet"] > 0.3:
        partes_fala.append(f"Minha internet é {p['internet']}, então preciso de um jeito que não dependa dela.")
    elif barreira == "letramento" and pesos["letramento"] > 0.3:
        partes_fala.append("Tenho dificuldade com o celular e me perco com muita tela e letra pequena.")
    elif barreira == "confianca" and pesos["confianca"] > 0.1:
        partes_fala.append(f"Fico com o pé atrás com coisa do governo no celular. Ver a fonte me deixa mais tranquil{a}.")
    if canal.startswith("Totem"):
        partes_fala.append(f"O totem no {'posto' if p['onde'] != 'capital' else 'CRAS'} me ajuda porque é perto e não usa a minha internet.")
    partes_fala.append(f"Meu medo é {p['medo']}.")
    return " ".join(partes_fala)


def ouvir_personas(parte_nome: str, canais: list[str]) -> list[Opiniao]:
    parte = PARTES[parte_nome]
    canais = canais or ["App e site"]
    opinioes = []
    for p in PERSONAS:
        melhor = max(((c, *_chance(p, parte, CANAIS[c])) for c in canais), key=lambda x: x[1])
        canal, chance, pesos = melhor
        barreira = max(pesos, key=pesos.get) if max(pesos.values()) >= 0.15 else "nenhuma"
        v = _veredito(chance)
        opinioes.append(Opiniao(p, canal, round(chance, 2), v, round(1 + 4 * chance), falar(p, v, barreira, canal, parte_nome, pesos),
                                barreira, SUGESTAO[barreira]))
    return opinioes


def simular_populacao(parte_nome: str, canais: list[str], n: int = 3000, semente: int = 7):
    """População sintética: n pessoas sorteadas a partir das personas, com variação.

    Devolve (adesão geral, adesão por perfil, contagem da principal barreira).
    """
    rng = np.random.default_rng(semente)
    parte = PARTES[parte_nome]
    canais = canais or ["App e site"]
    pesos = np.array([p["peso"] for p in PERSONAS], dtype=float)
    idx = rng.choice(len(PERSONAS), size=n, p=pesos / pesos.sum())
    usa_total, por_perfil, barreiras = 0, {}, {}
    for i in idx:
        p = PERSONAS[i]
        internet = float(np.clip(NIVEL_INTERNET[p["internet"]] + rng.normal(0, 0.15), 0, 1))
        letr = float(np.clip(p["letramento"] + rng.normal(0, 0.15), 0, 1))
        conf = float(np.clip(p["confianca"] + rng.normal(0, 0.15), 0, 1))
        chance, pes = max((_chance(p, parte, CANAIS[c], internet, letr, conf) for c in canais), key=lambda x: x[0])
        usa = rng.random() < chance
        usa_total += usa
        tot, sim = por_perfil.get(p["perfil"], (0, 0))
        por_perfil[p["perfil"]] = (tot + 1, sim + usa)
        if not usa:
            b = max(pes, key=pes.get)
            barreiras[b] = barreiras.get(b, 0) + 1
    adesao_perfil = {k: round(100 * s / t) for k, (t, s) in por_perfil.items()}
    return round(100 * usa_total / n), dict(sorted(adesao_perfil.items(), key=lambda x: -x[1])), barreiras
