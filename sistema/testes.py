"""Páginas "Teste" das matérias: cada uma exercita só a parte da matéria.

PCP: a busca por pontos sobre a base, com a lista de tuplas da maior para a menor.
DSA: um catálogo de demonstração na lista encadeada da entrega. Fica na memória
     do servidor, para o grupo cadastrar, excluir e ordenar sem mexer nos dados.
MLAM: um resumo da base real da SSP-SP agregada por estação (só leitura).
SERS: a mesma viagem de carro, ônibus e trilho, com cada conta passo a passo.
"""
import sys

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


def dsa_operar(operacao: str, dados: dict) -> dict:
    c = _catalogo_demo(reiniciar=operacao == "reiniciar")
    if operacao == "reiniciar":
        return dsa_estado("Catálogo recarregado do arquivo da entrega.")
    if operacao == "ordenar":
        ok, msg, _ = c.ordenar(dados.get("criterio", ""))
        return dsa_estado(msg, ok)
    if operacao == "pesquisar":
        ok, msg, achados = c.pesquisar(dados.get("campo", "titulo"), dados.get("trecho", ""))
        return dsa_estado(msg, ok, [s.id for s in achados] if ok else [])
    if operacao == "excluir":
        ok, msg, _ = c.excluir(dados.get("id", ""))
        return dsa_estado(msg, ok)
    if operacao == "cadastrar":
        campos = ("id", "titulo", "categoria", "descricao", "publico_alvo", "canal", "prazo")
        ok, msg, _ = c.cadastrar(*(str(dados.get(k, "")) for k in campos))
        return dsa_estado(msg, ok)
    return dsa_estado("Operação desconhecida.", False)


def pcp_testar(pergunta: str) -> dict:
    return ponte_pcp.pontuar_todas(pergunta) | {"base": ponte_pcp.base_resumida()}


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
    return c | {"passos": passos,
                "falta": "Testes com usuários, vídeo de até 3 minutos e o .txt com os links. A equipe precisa abrir as fontes e conferir os números lidos de PDF."}


def mlam_resumo(quantas: int = 15) -> dict:
    """Resumo descritivo da base da MLAM. As questões 02 a 07 (probabilidade, testes e regressões) são do grupo."""
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
            "falta": "Questões 02 a 07: probabilidade, testes de hipótese e regressões, com o relatório em PDF. A base não tem o fluxo de passageiros, então é contagem, não taxa."}
