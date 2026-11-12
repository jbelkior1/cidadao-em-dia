"""Fluxograma do sistema em Graphviz.

Sem destaque: visão geral, todas as matérias coloridas.
Com destaque: a matéria escolhida fica colorida e as ligações dela ficam em evidência;
o resto fica em cinza, para mostrar onde ela entra no fluxo.
"""
from nucleo.materias import ORDEM, REGISTRO

CINZA_FUNDO, CINZA_TEXTO, CINZA_LINHA = "#eef3f1", "#8a9a95", "#c9d4d0"

# ligações do fluxo: (origem, destino, rótulo, tracejado)
LIGACOES = [
    ("cidadao", "atendimento", "", False),
    ("atendimento", "duvida", "", False), ("atendimento", "direitos", "", False),
    ("atendimento", "luz", "", False), ("atendimento", "golpe", "", False),
    ("atendimento", "PCP", "entende a necessidade", False),
    ("duvida", "PCP", "", False), ("direitos", "PCP", "", False), ("golpe", "PCP", "", False),
    ("PCP", "PAI", "confiança baixa", True),
    ("direitos", "DSA", "prazo", False), ("atendimento", "DSA", "prazos", False),
    ("direitos", "SERS", "valor", False), ("luz", "SERS", "conta", False),
    ("luz", "COA", "leitura", False), ("direitos", "COA", "", True),
    ("direitos", "PAI", "o que levar", False),
    ("MLAM", "simulacao", "modelo de adesão", False), ("PAI", "simulacao", "falas (futuro)", True),
]
TELAS = {"atendimento": "1. Conte o\\nque precisa", "duvida": "Tirar uma dúvida", "direitos": "Meus direitos",
         "luz": "Minha conta de luz", "golpe": "Isso é golpe?", "simulacao": "Simulação\\nda sociedade"}


def fluxograma(destaque: str | None = None) -> str:
    linhas = ['digraph G {', 'rankdir=LR; bgcolor="transparent"; nodesep=0.22; ranksep=0.45;',
              'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11, penwidth=1.2];',
              'edge [fontname="Helvetica", fontsize=9, arrowsize=0.7];']
    ligados = {a for a, b, *_ in LIGACOES if b == destaque} | {b for a, b, *_ in LIGACOES if a == destaque}

    def no_tela(chave, rotulo):
        ativo = destaque is None or chave in ligados
        cor = "#ffffff" if ativo else CINZA_FUNDO
        texto = "#17363A" if ativo else CINZA_TEXTO
        return f'{chave} [label="{rotulo}", fillcolor="{cor}", fontcolor="{texto}", color="#cfdad6"];'

    linhas.append('cidadao [label="Cidadão", shape=ellipse, fillcolor="#17363A", fontcolor="white", color="#17363A"];')
    linhas.append(no_tela("atendimento", TELAS["atendimento"]))
    linhas.append('subgraph cluster_resolva { label="2. Resolva aqui"; fontname="Helvetica"; fontsize=10; color="#cfdad6"; style="rounded";')
    for chave in ("duvida", "direitos", "luz", "golpe"):
        linhas.append(no_tela(chave, TELAS[chave]))
    linhas.append("}")
    linhas.append(no_tela("simulacao", TELAS["simulacao"]))
    for c in ORDEM:
        cor = REGISTRO[c]["cor"]
        ativo = destaque is None or c == destaque or c in ligados
        if ativo:
            borda = ', penwidth=3, color="#17363A"' if c == destaque else f', color="{cor}"'
            linhas.append(f'{c} [label="{c}\\n{REGISTRO[c]["curto"]}", fillcolor="{cor}", fontcolor="white"{borda}];')
        else:
            linhas.append(f'{c} [label="{c}\\n{REGISTRO[c]["curto"]}", fillcolor="{CINZA_FUNDO}", fontcolor="{CINZA_TEXTO}", color="{CINZA_LINHA}"];')
    for a, b, rot, trac in LIGACOES:
        em_foco = destaque is None or destaque in (a, b)
        cor = (REGISTRO[destaque]["cor"] if destaque and em_foco else "#9aa8a4") if em_foco else CINZA_LINHA
        largura = 2.2 if destaque and em_foco else 1.0
        estilo = ', style=dashed' if trac else ''
        texto = f', label="{rot}", fontcolor="{"#17363A" if em_foco else CINZA_TEXTO}"' if rot and em_foco else ''
        linhas.append(f'{a} -> {b} [color="{cor}", penwidth={largura}{estilo}{texto}];')
    linhas.append('}')
    return "\n".join(linhas)
