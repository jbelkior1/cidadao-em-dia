"""Páginas "Teste" das matérias: cada uma exercita só a parte da matéria.

PCP: a busca por pontos sobre a base, com a lista de tuplas da maior para a menor.
DSA: um catálogo de demonstração na lista encadeada da entrega. Fica na memória
     do servidor, para o grupo cadastrar, excluir e ordenar sem mexer nos dados.
MLAM: os resultados das questões 02 a 06, lidos do que a entrega gravou, e um resumo da base da SSP-SP.
SERS: a mesma viagem de carro, ônibus e trilho, com cada conta passo a passo.
MMC: a Etapa 1 do enunciado (o sistema linear da frota) e a conferência das duas propriedades
     que a Etapa 2 exige de uma matriz de redistribuição digitada pela equipe. A matriz e a
     política são da equipe, como o enunciado manda: o teste não sugere nenhuma.
"""
import math
import sys
import threading

from sistema.adaptadores import dsa as ponte_dsa
from sistema.adaptadores import pcp as ponte_pcp
from sistema.mobilidade import energia

_demo = None


def _catalogo_demo(reiniciar: bool = False):
    global _demo
    if _demo is None or reiniciar:
        ponte_dsa._carregar()                      # garante a pasta da entrega no caminho de importação
        if str(ponte_dsa.PASTA) not in sys.path:
            sys.path.insert(0, str(ponte_dsa.PASTA))
        import integracao
        _demo = integracao.carregar_catalogo()
    return _demo


def _cadeia(catalogo) -> list[dict]:
    """Percorre a lista do primeiro ao último nó."""
    return [{"id": s.id, "titulo": s.titulo, "categoria": s.categoria, "prazo": s.prazo, "publico_alvo": s.publico_alvo, "canal": s.canal}
            for s in catalogo.lista.percorrer()]


def dsa_estado(mensagem: str = "", ok: bool = True, achados: list | None = None) -> dict:
    c = _catalogo_demo()
    return {"ok": ok, "mensagem": mensagem, "tamanho": c.lista.tamanho(), "nos": _cadeia(c), "achados": achados or [],
            "cabeca": c.lista.cabeca.dado.id if c.lista.cabeca else None, "cauda": c.lista.cauda.dado.id if c.lista.cauda else None}


#: O catálogo de teste é um só, na memória do servidor, e todos os visitantes mexem nele: com teto.
DSA_MAXIMO_DE_NOS = 60
DSA_MAXIMO_POR_CAMPO = 200
_trava_dsa = threading.Lock()


def dsa_operar(operacao: str, dados: dict) -> dict:
    # tudo que chega vira texto curto: número ou texto enorme no lugar de um campo não derruba a rota
    d = {k: str(v)[:DSA_MAXIMO_POR_CAMPO] for k, v in (dados or {}).items() if v is not None}
    with _trava_dsa:
        c = _catalogo_demo(reiniciar=operacao == "reiniciar")
        if operacao == "reiniciar":
            return dsa_estado("Catálogo recarregado do arquivo da entrega.")
        if operacao == "ordenar":
            ok, msg, _ = c.ordenar(d.get("criterio", ""))
            return dsa_estado(msg, ok)
        if operacao == "pesquisar":
            ok, msg, achados = c.pesquisar(d.get("campo", "titulo"), d.get("trecho", ""))
            return dsa_estado(msg, ok, [s.id for s in achados] if ok else [])
        if operacao == "consultar":
            ok, msg, servico = c.consultar(d.get("id", ""))
            return dsa_estado(msg, ok, [servico.id] if ok else [])
        if operacao == "atualizar":
            ok, msg, servico = c.atualizar(d.get("id", ""), d.get("campo", ""), d.get("valor", ""))
            return dsa_estado(msg, ok, [servico.id] if ok else [])
        if operacao == "excluir":
            ok, msg, _ = c.excluir(d.get("id", ""))
            return dsa_estado(msg, ok)
        if operacao == "cadastrar":
            if c.lista.tamanho() >= DSA_MAXIMO_DE_NOS:
                return dsa_estado(f"O catálogo de teste vai até {DSA_MAXIMO_DE_NOS} serviços. Exclua algum ou recarregue do arquivo.", False)
            campos = ("id", "titulo", "categoria", "descricao", "publico_alvo", "canal", "prazo")
            ok, msg, _ = c.cadastrar(*(d.get(k, "") for k in campos))
            return dsa_estado(msg, ok)
        return dsa_estado("Operação desconhecida.", False)


def pcp_testar(pergunta: str) -> dict:
    """A lista de tuplas de buscar(), a pergunta como normalizar() a vê e a orientação que o assistente mostraria."""
    r = ponte_pcp.pontuar_todas(pergunta) | {"base": ponte_pcp.base_resumida()}
    if r.get("ok") and not r.get("bloqueada"):
        from base_conhecimento import normalizar          # a função da entrega (a pasta entrou no caminho ao carregar)
        r["normalizada"] = normalizar(pergunta).strip()
        resposta = ponte_pcp.responder(pergunta)
        r["escolhida"] = resposta["orientacao"] if resposta["encontrou"] else None
    r["aviso"] = "Aviso: este assistente NÃO é um canal oficial."
    return r


def _reais(valor: float) -> str:
    return f"R$ {valor:.2f}".replace(".", ",")


def sers_testar(km: float) -> dict:
    c = energia.comparar(km)
    trilho, onibus, carro = c["modos"]
    v, br = energia._v, energia._br
    litros = round(c["km"] / v("carro_consumo_hb20_sense_gasolina"), 2)
    passos = [
        f"Distância: {br(c['km'])} km.",
        f"Trem ou metrô: {br(c['km'])} km × {br(v('metro_sp_energia_por_passageiro_km'))} kWh por passageiro-km = {br(trilho['energia_kwh'])} kWh; "
        f"× {br(round(v('fator_emissao_sin') * 1000, 1))} g de CO₂ por kWh = {br(round(trilho['co2_kg'] * 1000))} g de CO₂. Tarifa de {_reais(trilho['custo_rs'])}.",
        f"Carro: {br(c['km'])} km ÷ {br(v('carro_consumo_hb20_sense_gasolina'))} km/L = {br(litros)} L de gasolina; "
        f"× {br(v('fator_emissao_gasolina_automotiva'))} kg de CO₂ por litro = {br(carro['co2_kg_max'])} kg (só a parte fóssil, 78%: {br(carro['co2_kg'])} kg); "
        f"× {_reais(v('preco_gasolina_sp_capital'))} por litro = {_reais(carro['custo_rs'])} de combustível.",
        f"Ônibus a diesel: {br(c['km'])} km × {br(v('comparativo_metro_onibus_sp_gco2e_pkm'))} g de CO₂ por passageiro-km = {br(onibus['co2_kg'])} kg de CO₂. "
        f"Tarifa de {_reais(onibus['custo_rs'])}.",
    ]
    # mesmo período de referência para as três (o enunciado pede): um mês de trabalho, ida e volta
    viagens = DIAS_UTEIS_NO_MES * 2
    mensal = [{"modo": m["modo"], "renovavel": m["renovavel"],
               "energia_kwh": round(m["energia_kwh"] * viagens, 1) if m["energia_kwh"] is not None else None,
               "co2_kg": round(m["co2_kg"] * viagens, 1),
               "co2_kg_max": round(m["co2_kg_max"] * viagens, 1) if m.get("co2_kg_max") else None,
               "custo_rs": round(m["custo_rs"] * viagens, 2), "custo_tipo": m["custo_tipo"]} for m in c["modos"]]
    return c | {"passos": passos, "mensal": {"viagens": viagens, "dias_uteis": DIAS_UTEIS_NO_MES, "modos": mensal}}


DIAS_UTEIS_NO_MES = 22     # o mesmo período do script da entrega (entregas/sers/comparar_energia.py)


def _resultados_mlam() -> dict | None:
    """Os números das questões 02 a 06, como main.py da entrega gravou (só leitura, nada é recalculado aqui)."""
    import json
    from pathlib import Path
    arquivo = Path(__file__).resolve().parent.parent / "entregas" / "mlam" / "saidas" / "resultados.json"
    try:
        d = json.loads(arquivo.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    q2, q3, q4, q5, q6 = (d[f"questao_0{n}"] for n in range(2, 7))
    return {
        "q02": {"media": q2["media"], "mediana": q2["mediana"], "desvio": q2["desvio_populacional"],
                "p_menor_media": q2["a_P_menor_que_media"], "classe_a": q2["a_classificacao"],
                "p_maior_mediana": q2["b_P_maior_que_mediana"], "classe_b": q2["b_classificacao"]},
        "q03": [{"item": k, "lado": q3[k]["lado"], "alfa": q3[k]["alfa"], "n": q3[k]["n"], "media_amostral": q3[k]["media_amostral"],
                 "z": q3[k]["z"], "z_critico": q3[k]["z_critico"], "p_valor": q3[k]["p_valor"], "rejeita_h0": q3[k]["rejeita_h0"]} for k in ("a", "b")],
        "q04": {"equacao": q4["equacao"], "covariancia": q4["covariancia"], "pearson_r": q4["pearson_r"], "r2": q4["r2"], "F": q4["F"],
                "F_p": q4["F_p_valor"], "previsao_km": q4["previsao_km"], "previsao": q4["previsao"]},
        "q05": {"equacao": q5["equacao"], "r2": q5["r2"], "r2_ajustado": q5["r2_ajustado"], "F": q5["F"], "F_p": q5["F_p_valor"],
                "previsao": q5["previsao"], "explicativas": q5["explicativas"]},
        "q06": {"coeficientes": q6["coeficientes"], "matriz": q6["matriz_confusao"], "acuracia": q6["acuracia"],
                "piso": q6["piso_classe_majoritaria"], "classificacao": (q6.get("classificacoes") or [None])[0]},
    }


def mlam_resumo(quantas: int = 15) -> dict:
    """Os resultados das questões 02 a 06 (da entrega) e um resumo descritivo da base da SSP-SP por estação."""
    import json
    from pathlib import Path
    arquivo = Path(__file__).resolve().parent / "dados" / "seguranca_estacoes.json"
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"ok": False, "mensagem": "A base ainda não foi gerada. Rode python entregas/mlam/preparar_base.py."}
    estacoes = dados["estacoes"]
    faixas = {f: sum(e["por_faixa"].get(f, 0) for e in estacoes) for f in ("madrugada", "manha", "tarde", "noite")}
    tipos: dict[str, int] = {}
    for e in estacoes:
        for t, n in e["por_tipo"].items():
            tipos[t] = tipos.get(t, 0) + n
    ranking = sorted(estacoes, key=lambda e: e["total"], reverse=True)[:quantas]
    return {"ok": True, "meta": dados["meta"], "estacoes": len(estacoes),
            "faixas": faixas, "tipos": dict(sorted(tipos.items(), key=lambda x: -x[1])),
            "ranking": [{"estacao": e["estacao"], "linhas": e["linhas"], "total": e["total"], "faixa_mais_comum": e["faixa_mais_comum"]} for e in ranking],
            "questoes": _resultados_mlam()}


# ---------------------------------------------------------------- MMC
MMC_REGIOES = ["Norte", "Sul", "Leste", "Oeste"]
#: Relatório I do enunciado, na ordem N, S, L, O: frota total e os três indicadores consolidados.
MMC_EQUACOES = [
    ("N + S + L + O", [1, 1, 1, 1], 72),
    ("N + 2S + O", [1, 2, 0, 1], 76),
    ("S + 2L", [0, 1, 2, 0], 52),
    ("N + L + 2O", [1, 0, 1, 2], 76),
]
#: Relatório II do enunciado: passageiros no pico e capacidade por ônibus.
MMC_PASSAGEIROS = [560, 760, 720, 840]
MMC_CAPACIDADE = 40


def _br(x: float) -> str:
    return (f"{x:.4f}".rstrip("0").rstrip(".") if x != int(x) else str(int(x))).replace(".", ",")


def mmc_etapa1(lados: list[float] | None = None) -> dict:
    """Etapa 1: monta Ax = b com os registros, decide se a solução é única e resolve."""
    import numpy as np
    b = [float(v) for v in (lados or [e[2] for e in MMC_EQUACOES])]
    if len(b) != 4:
        return {"ok": False, "mensagem": "Informe os quatro valores do Relatório I."}
    A = np.array([e[1] for e in MMC_EQUACOES], dtype=float)
    vb = np.array(b)
    if not np.isfinite(vb).all() or (np.abs(vb) > 1e6).any():          # a API já barra; aqui é a segunda trava
        return {"ok": False, "mensagem": "Use números finitos, de até 1 milhão em valor absoluto."}
    det = float(np.linalg.det(A))
    posto_a = int(np.linalg.matrix_rank(A))
    posto_ab = int(np.linalg.matrix_rank(np.column_stack([A, vb])))
    base = {"ok": True, "equacoes": [{"texto": e[0], "coeficientes": e[1], "valor": v} for e, v in zip(MMC_EQUACOES, b)],
            "determinante": round(det, 6), "posto_a": posto_a, "posto_ampliada": posto_ab}
    if posto_a < 4:
        tipo = "infinitas soluções" if posto_a == posto_ab else "nenhuma solução"
        return base | {"unica": False, "conclusao": f"det(A) = 0 e posto(A) = {posto_a}: o sistema tem {tipo}."}
    x = np.linalg.solve(A, vb)
    sobra = A @ x - vb
    inteira = bool(np.allclose(x, np.round(x), atol=1e-9))
    nao_negativa = bool((x >= -1e-9).all())
    frota = {r: (int(round(v)) if inteira else round(float(v), 4)) for r, v in zip(MMC_REGIOES, x)}
    conferencia = [f"{e[0]} = {_br(sum(c * float(v) for c, v in zip(e[1], x)))} (esperado {_br(valor)})" for e, valor in zip(MMC_EQUACOES, b)]
    return base | {"unica": True, "frota": frota, "inteira": inteira, "nao_negativa": nao_negativa,
                   "residuo_max": float(abs(sobra).max()), "conferencia": conferencia,
                   "conclusao": (f"det(A) = {_br(round(det, 6))} ≠ 0 e posto(A) = posto(A|b) = 4: a distribuição é única."
                                 + ("" if inteira and nao_negativa else " Mas o resultado não é inteiro e não negativo: confira os registros."))}


def mmc_necessidade() -> dict:
    """Etapa 2a e 2b: ônibus necessários por região (passageiros ÷ capacidade, arredondando para cima) e o desequilíbrio."""
    atual = mmc_etapa1()["frota"]
    necessidade = {r: math.ceil(p / MMC_CAPACIDADE) for r, p in zip(MMC_REGIOES, MMC_PASSAGEIROS)}
    return {"capacidade": MMC_CAPACIDADE, "passageiros": dict(zip(MMC_REGIOES, MMC_PASSAGEIROS)), "atual": atual,
            "necessidade": necessidade, "diferenca": {r: atual[r] - necessidade[r] for r in MMC_REGIOES},
            "total_atual": sum(atual.values()), "total_necessario": sum(necessidade.values())}


def mmc_conferir_matriz(matriz: list[list[float]]) -> dict:
    """Etapa 2: confere se a matriz da equipe preserva o total e não gera alocação negativa.

    Convenção: a coluna j diz para onde vão os ônibus da região j (a entrada [i][j] é a fração que
    sai de j para i). Preservar o total para qualquer frota equivale a cada coluna somar 1; com todas
    as entradas maiores ou iguais a zero, nenhuma região fica negativa.
    """
    import numpy as np
    try:
        M = np.array(matriz, dtype=float)
    except (TypeError, ValueError):
        return {"ok": False, "mensagem": "Use só números na matriz."}
    if M.shape != (4, 4):
        return {"ok": False, "mensagem": "A matriz precisa ter 4 linhas e 4 colunas (Norte, Sul, Leste, Oeste)."}
    if not np.isfinite(M).all() or (np.abs(M) > 1e6).any():
        return {"ok": False, "mensagem": "Use números finitos, de até 1 milhão em valor absoluto."}
    atual = mmc_necessidade()
    x = np.array([atual["atual"][r] for r in MMC_REGIOES], dtype=float)
    y = M @ x
    somas = M.sum(axis=0)
    preserva = bool(np.allclose(somas, 1.0, atol=1e-9))
    sem_negativo = bool((M >= -1e-12).all())
    inteira = bool(np.allclose(y, np.round(y), atol=1e-9))
    nova = {r: (int(round(v)) if inteira else round(float(v), 4)) for r, v in zip(MMC_REGIOES, y)}
    return {"ok": True, "somas_das_colunas": [round(float(s), 6) for s in somas], "preserva_total": preserva,
            "sem_entrada_negativa": sem_negativo, "nova_distribuicao": nova, "inteira": inteira,
            "total_antes": int(x.sum()), "total_depois": round(float(y.sum()), 6),
            "atende": {r: (float(y[i]) >= atual["necessidade"][r] - 1e-9) for i, r in enumerate(MMC_REGIOES)},
            "necessidade": atual["necessidade"]}
