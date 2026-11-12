"""Páginas "Teste" das matérias: cada uma exercita só a parte da matéria.

PCP: a busca por pontos sobre a base, com a lista de tuplas da maior para a menor.
DSA: um catálogo de demonstração na lista encadeada da entrega. Fica na memória
     do servidor, para o grupo cadastrar, excluir e ordenar sem mexer nos dados.
SERS: o cálculo do desconto passo a passo.
"""
import sys

from sistema.adaptadores import dsa as ponte_dsa
from sistema.adaptadores import pcp as ponte_pcp
from sistema.servicos import energia

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


def sers_testar(kwh: float, valor: float | None) -> dict:
    c = energia.calcular(kwh, valor)
    passos = [f"Consumo informado: {kwh:g} kWh no mês.",
              f"Os primeiros {energia.FAIXA_KWH} kWh têm 100% de desconto: {c['kwh_com_desconto']:g} kWh entram no desconto.",
              f"O que passa de {energia.FAIXA_KWH} kWh é cobrado normalmente: {c['kwh_cobrados']:g} kWh."]
    if c["preco_medio"] is not None:
        passos += [f"Preço médio da sua conta: {energia.reais(valor)} ÷ {kwh:g} kWh = {energia.por_kwh(c['preco_medio'])}.",
                   f"Desconto estimado: {c['kwh_com_desconto']:g} kWh × {energia.reais(c['preco_medio'], 3)} = {energia.reais(c['desconto_mes'])} por mês, "
                   f"ou {energia.reais(c['desconto_ano'])} em 12 meses."]
    return c | {"passos": passos, "fonte": energia.FONTE, "consultado_em": energia.CONSULTADO_EM,
                "falta": "Comparar duas alternativas para a mesma necessidade, uma delas renovável, com custo, viabilidade e impacto ambiental."}
