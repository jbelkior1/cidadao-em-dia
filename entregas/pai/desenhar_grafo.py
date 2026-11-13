"""Desenha o grafo do agente (o enunciado pede a imagem quando a entrega é script).

    python desenhar_grafo.py      # grava grafo_agente.png e grafo_agente.mmd nesta pasta

Os nós e as arestas vêm do próprio grafo compilado (`agente.montar().get_graph()`), então a imagem
não envelhece: se o grafo mudar, basta rodar de novo. Desenha com matplotlib, sem serviço externo.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from pai_agente import agente  # noqa: E402

# posição e explicação de cada nó, de cima para baixo
LAYOUT = {
    "__start__": (0.5, 0.92, "início", "a pergunta da pessoa"),
    "guardrails": (0.5, 0.72, "guardrails", "dado pessoal, prompt injection,\nentrada inválida (código, sem modelo)"),
    "busca_fichas": (0.5, 0.50, "busca_fichas", "pontua as 7 fichas FT;\nnenhuma ficha → \"não encontrei\""),
    "responder": (0.5, 0.28, "responder", "modelo com SÓ as fichas achadas;\ncita a ficha e a data"),
    "__end__": (0.5, 0.07, "fim", "resposta + aviso de canal não oficial"),
}
ROTULO_ARESTA = {("guardrails", "__end__"): "recusa pronta", ("busca_fichas", "__end__"): "fora do escopo\nou sobre o assistente"}


def desenhar() -> Path:
    grafo = agente.montar().get_graph()
    fig, ax = plt.subplots(figsize=(7.5, 8.5))
    ax.set_axis_off()
    for no in grafo.nodes:
        x, y, titulo, detalhe = LAYOUT[no]
        borda = "#7C3AED" if no not in ("__start__", "__end__") else "#6b7280"
        ax.add_patch(FancyBboxPatch((x - 0.2, y - 0.055), 0.4, 0.11, boxstyle="round,pad=0.01,rounding_size=0.03",
                                    linewidth=1.6, edgecolor=borda, facecolor="#f5f3ff" if borda == "#7C3AED" else "white"))
        ax.text(x, y + 0.022, titulo, ha="center", va="center", fontsize=11, fontweight="bold", color="#1f2937")
        ax.text(x, y - 0.02, detalhe, ha="center", va="center", fontsize=7.6, color="#4b5563")
    for aresta in grafo.edges:
        x0, y0, *_ = LAYOUT[aresta.source]
        x1, y1, *_ = LAYOUT[aresta.target]
        if aresta.target == "__end__" and aresta.source != "responder":     # desvio lateral até o fim
            curva, lado = "arc3,rad=-0.55", 1
            ax.add_patch(FancyArrowPatch((x0 + 0.2, y0), (x1 + 0.2, y1 + 0.03), connectionstyle=curva,
                                         arrowstyle="-|>", mutation_scale=12, linestyle="--", color="#9ca3af"))
            rotulo = ROTULO_ARESTA.get((aresta.source, aresta.target), "")
            ax.text(x0 + 0.24 * lado, y0 - 0.06, rotulo, fontsize=7.5, color="#6b7280")
        else:
            ax.add_patch(FancyArrowPatch((x0, y0 - 0.055), (x1, y1 + 0.055), arrowstyle="-|>", mutation_scale=14,
                                         linestyle="--" if aresta.conditional else "-", color="#374151"))
    ax.set_xlim(0, 1.15)
    ax.set_ylim(0, 1)
    ax.set_title("Agente da PAI (LangGraph) — orientação de transporte pelas fichas FT-01 a FT-07", fontsize=10.5)
    arquivo = PASTA / "grafo_agente.png"
    fig.savefig(arquivo, dpi=150, bbox_inches="tight")
    plt.close(fig)
    (PASTA / "grafo_agente.mmd").write_text(grafo.draw_mermaid(), encoding="utf-8")
    return arquivo


if __name__ == "__main__":
    print(f"Imagem gravada em {desenhar()}")
