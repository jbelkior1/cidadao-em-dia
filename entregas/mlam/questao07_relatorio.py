# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Questão 07 (2,0): Relatório estatístico em PDF, apresentado ao cliente.

O cliente é a equipe de produto do app "Dá Tempo?", que quer saber onde há mais registro de ocorrência
no entorno das estações e o quanto dá para prever isso. O relatório junta as tabelas, os gráficos, as
medidas, as interpretações e os insights das questões 02 a 06.

Os números não são digitados aqui: vêm de saidas/resultados.json, que o main.py grava. Se a base ou um
script mudar, basta rodar de novo e o PDF acompanha.

    python main.py                  # gera resultados.json e os gráficos
    python questao07_relatorio.py   # gera saidas/relatorio_mlam_gs2026.pdf

Nome completo e RM dos integrantes: vêm de comum.INTEGRANTES.
"""
import json
from datetime import date
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

import comum

ARQUIVO = comum.SAIDAS / "relatorio_mlam_gs2026.pdf"

# DejaVu vem junto com o matplotlib: tem os símbolos (μ, σ, α, ≥, −) e roda em qualquer máquina.
_FONTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("Texto", str(_FONTES / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Texto-Negrito", str(_FONTES / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrito")

TINTA = colors.HexColor("#1f2937")
SUAVE = colors.HexColor("#6b7280")
MARCA = colors.HexColor("#c2410c")
FUNDO = colors.HexColor("#f3f4f6")

E = {
    "capa": ParagraphStyle("capa", fontName="Texto-Negrito", fontSize=22, leading=27, textColor=TINTA),
    "sub": ParagraphStyle("sub", fontName="Texto", fontSize=12, leading=16, textColor=SUAVE),
    "h1": ParagraphStyle("h1", fontName="Texto-Negrito", fontSize=15, leading=19, textColor=MARCA,
                         spaceBefore=10, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Texto-Negrito", fontSize=11.5, leading=15, textColor=TINTA,
                         spaceBefore=8, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="Texto", fontSize=9.6, leading=13.6, textColor=TINTA, alignment=TA_LEFT,
                        spaceAfter=5),
    "nota": ParagraphStyle("nota", fontName="Texto", fontSize=8.4, leading=11.5, textColor=SUAVE, spaceAfter=4),
    "insight": ParagraphStyle("insight", fontName="Texto", fontSize=9.6, leading=13.6, textColor=TINTA,
                              backColor=colors.HexColor("#fff7ed"), borderColor=MARCA, borderWidth=0,
                              borderPadding=(6, 8, 6, 8), leftIndent=8, rightIndent=8, spaceBefore=4,
                              spaceAfter=10),
    "cel": ParagraphStyle("cel", fontName="Texto", fontSize=8.6, leading=11, textColor=TINTA),
}


def br(valor: float, casas: int = 2) -> str:
    """Número no formato brasileiro: 1.234,56."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor: float, casas: int = 1) -> str:
    return f"{br(valor * 100, casas)}%"


def p_valor(valor: float) -> str:
    return "< 0,0001" if valor < 1e-4 else br(valor, 4)


def tabela(linhas: list[list[str]], larguras: list[float]) -> Table:
    dados = [[Paragraph(str(c), E["cel"]) for c in linha] for linha in linhas]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FUNDO),
        ("FONTNAME", (0, 0), (-1, 0), "Texto-Negrito"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, TINTA),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def figura(arquivo: str, largura_cm: float, legenda: str) -> list:
    caminho = comum.SAIDAS / arquivo
    if not caminho.exists():
        return [Paragraph(f"Gráfico {arquivo} não encontrado: rode python main.py antes.", E["nota"])]
    img = Image(str(caminho))
    proporcao = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = largura_cm * cm, largura_cm * cm * proporcao
    return [KeepTogether([img, Paragraph(legenda, E["nota"])])]


def P(texto: str, estilo: str = "p") -> Paragraph:
    return Paragraph(texto, E[estilo])


def _rodape(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Texto", 7.5)
    canvas.setFillColor(SUAVE)
    canvas.drawString(2 * cm, 1.2 * cm, "MLAM · Global Solution 2026.2 · Dá Tempo?: ocorrências no entorno das estações")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"página {doc.page}")
    canvas.restoreState()


def montar(r: dict) -> list:
    q2, q3, q4, q5, q6 = (r[f"questao_0{i}"] for i in range(2, 7))
    hist = []

    # ---------------- capa e resumo
    hist += [Spacer(1, 3 * cm),
             P("Onde há mais registro de ocorrência perto das estações, e o quanto dá para prever", "capa"),
             Spacer(1, 0.4 * cm),
             P("Relatório estatístico para a equipe de produto do app Dá Tempo? · MLAM, Global Solution 2026.2", "sub"),
             Spacer(1, 0.8 * cm),
             P(f"Base: 139 estações de trem e metrô do município de São Paulo, ocorrências registradas pela "
               f"SSP-SP num raio de 300 m de cada estação, de janeiro a setembro de 2026. "
               f"Relatório gerado em {date.today().strftime('%d/%m/%Y')}."),
             Spacer(1, 0.6 * cm),
             P("Integrantes", "h2"),
             tabela([["Nome completo", "RM"], *[[n, rm] for n, rm in comum.INTEGRANTES]], [11, 4]),
             PageBreak()]

    hist += [P("Resumo para quem decide", "h1"),
             P(f"<b>1. O registro de ocorrência se concentra no centro e nas estações de baldeação.</b> Cada "
               f"quilômetro a mais de distância do Marco Zero corresponde, em média, a {br(abs(q4['inclinacao']), 1)} "
               f"registros a menos no entorno; cada linha a mais na estação, a {br(q5['coeficientes']['qtd_linhas'], 0)} "
               f"registros a mais, à mesma distância."),
             P(f"<b>2. A posição explica parte, não tudo.</b> Distância e número de linhas explicam cerca de "
               f"{pct(q5['r2'], 0)} da variação entre estações. O resto depende do que a base pública não traz, "
               f"principalmente o fluxo de passageiros."),
             P(f"<b>3. Dá para classificar estações em 'muito registro' ou 'registro normal' com acerto razoável.</b> "
               f"O modelo logístico acerta {pct(q6['acuracia'])} das estações, contra {pct(q6['piso_classe_majoritaria'])} "
               f"de quem chutasse sempre a classe maior."),
             P("<b>4. Registro não é risco.</b> Estação movimentada gera mais boletim. Sem o fluxo de passageiros "
               "não é possível dizer onde o passageiro corre mais risco, só onde há mais registro.", "p"),
             P("<b>Recomendação para o produto:</b> usar estes resultados para um aviso de atenção no entorno de "
               "estações centrais e de baldeação (\"região com muitos registros, fique atento\"), nunca para rotular "
               "uma estação como perigosa. O próximo passo de dados que mais melhoraria a análise é obter o fluxo "
               "de passageiros por estação, publicado pelo Metrô e pela CPTM, para chegar a ocorrências por pessoa.",
               "insight")]

    # ---------------- base
    hist += [P("A base de dados (questão 01)", "h1"),
             P("Fonte pública e real: planilha SPDadosCriminais_2026 da SSP-SP (abas jan–jun e jul–dez), baixada em "
               "12/11/2026, cruzada com as coordenadas das estações no GTFS da SPTrans. Cada linha é uma estação; "
               "nenhum endereço, número de BO ou dado de pessoa entrou na base."),
             tabela([["papel", "variável", "o que é"],
                     ["resposta", "total", "ocorrências registradas num raio de 300 m da estação"],
                     ["explicativa", "dist_marco_zero_km", "distância da estação até o Marco Zero, em km"],
                     ["explicativa", "qtd_linhas", "quantas linhas passam na estação"],
                     ["explicativa", "lat", "latitude (posição norte-sul)"]], [2.6, 3.8, 10.6]),
             Spacer(1, 4),
             P("Roubo, furto e outros somam exatamente o total, assim como as faixas de horário; por isso nenhum "
               "deles entra como explicativa, o que seria prever a resposta com ela mesma.", "nota")]

    # ---------------- Q02
    hist += [PageBreak(), P("Como as ocorrências se distribuem (questão 02)", "h1"),
             tabela([["medida", "valor"],
                     ["estações", f"{q2['n']}"],
                     ["média de ocorrências por estação", br(q2["media"])],
                     ["mediana", br(q2["mediana"], 0)],
                     ["desvio padrão (populacional)", br(q2["desvio_populacional"])],
                     ["P(X < média), assumindo normal", f"{br(q2['a_P_menor_que_media'], 4)}, {q2['a_classificacao']}"],
                     ["P(X > mediana), assumindo normal", f"{br(q2['b_P_maior_que_mediana'], 4)}, {q2['b_classificacao']}"],
                     ["estações reais abaixo da média", pct(q2["proporcao_real_abaixo_da_media"])]], [8, 9]),
             Spacer(1, 6),
             *figura("q02_probabilidade.png", 16, "Histograma real contra a curva normal assumida, e as áreas das letras a e b."),
             P(f"O enunciado pede assumir distribuição normal. Nela, P(X < média) é exatamente 0,5 por simetria, e "
               f"P(X > mediana) dá {br(q2['b_P_maior_que_mediana'], 4)}. Os dados reais contam outra história: "
               f"{pct(q2['proporcao_real_abaixo_da_media'])} das estações ficam abaixo da média, e a normal com esse "
               f"desvio põe {pct(q2['massa_normal_negativa'])} da probabilidade em valores negativos, impossíveis "
               f"para uma contagem."),
             P(f"<b>Insight:</b> poucas estações muito movimentadas puxam a média ({br(q2['media'], 0)}) para longe "
               f"da mediana ({br(q2['mediana'], 0)}). Para comunicar \"uma estação típica\" ao usuário, a mediana é o "
               f"número honesto; a média exagera.", "insight")]

    # ---------------- Q03
    a, b = q3["a"], q3["b"]
    sa, sb = q3["checagem_sorteada"]["a"], q3["checagem_sorteada"]["b"]
    decide = lambda x: "rejeita H0" if x["rejeita_h0"] else "não rejeita H0"
    hist += [PageBreak(), P("Centro e periferia diferem da rede? (questão 03)", "h1"),
             P(f"Teste z para a média, com a média ({br(q3['referencia']['mu0'])}) e o desvio padrão "
               f"({br(q3['referencia']['sigma'])}) da base inteira como referência, como pede o enunciado."),
             tabela([["teste", "amostra", "média", "z", "z crítico", "p-valor", "decisão"],
                     ["a) H1: μ < μ0, α = 6%", "20 mais distantes", br(a["media_amostral"], 1), br(a["z"], 3),
                      br(a["z_critico"], 3), p_valor(a["p_valor"]), decide(a)],
                     ["b) H1: μ > μ0, α = 9%", "25 mais próximas", br(b["media_amostral"], 1), br(b["z"], 3),
                      br(b["z_critico"], 3), p_valor(b["p_valor"]), decide(b)],
                     ["checagem a", "20 sorteadas", br(sa["media_amostral"], 1), br(sa["z"], 3),
                      br(sa["z_critico"], 3), p_valor(sa["p_valor"]), decide(sa)],
                     ["checagem b", "25 sorteadas", br(sb["media_amostral"], 1), br(sb["z"], 3),
                      br(sb["z_critico"], 3), p_valor(sb["p_valor"]), decide(sb)]],
                    [3.4, 2.8, 1.7, 1.6, 1.7, 1.8, 2.6]),
             Spacer(1, 6),
             *figura("q03_testes_hipotese.png", 16, "Distribuição z de cada teste, com a região de rejeição e o z observado."),
             P(f"As estações de ponta de linha têm média abaixo da rede (p = {br(a['p_valor'], 4)}, rejeitada a 6% "
               f"por pouco) e as centrais, mais que o dobro (z = {br(b['z'], 2)}). Os grupos foram escolhidos pela "
               f"distância, não sorteados, então o teste descreve esses grupos e não vale como inferência para uma "
               f"estação qualquer. Com amostras sorteadas (semente {q3['checagem_sorteada']['semente']}), nenhum dos "
               f"dois testes rejeita H0, como se espera de uma amostra aleatória da própria rede."),
             P("<b>Insight:</b> a diferença está entre grupos de estações definidos pela posição, e é isso que o app "
               "deve usar. Não faz sentido dizer \"a sua estação tem mais ocorrência\" com base neste teste.", "insight")]

    # ---------------- Q04
    bp4 = q4["pressupostos"]
    hist += [PageBreak(), P("Distância do centro e ocorrências (questão 04)", "h1"),
             tabela([["medida", "valor", "leitura"],
                     ["covariância", br(q4["covariancia"]), "negativa: as variáveis andam em sentidos opostos"],
                     ["correlação de Pearson r", br(q4["pearson_r"], 3), "negativa moderada"],
                     ["equação", q4["equacao"].replace(".", ","), "cada km a mais: menos ocorrências"],
                     ["R²", br(q4["r2"], 4), f"a distância explica {pct(q4['r2'])} da variação"],
                     ["Teste F (p-valor)", p_valor(q4["F_p_valor"]), "o modelo é melhor que a média simples"],
                     ["Breusch-Pagan (p-valor)", br(bp4["breusch_pagan_p"], 4), "variância desigual: p-valores aproximados"],
                     [f"previsão a {br(q4['previsao_km'], 0)} km", br(q4["previsao"], 0),
                      f"IC 95% da média [{br(q4['previsao_ic95'][0], 0)}; {br(q4['previsao_ic95'][1], 0)}]; "
                      f"média real na faixa {br(q4['media_real_na_faixa'], 0)}"]], [4, 4.6, 8.4]),
             Spacer(1, 6),
             *figura("q04a_dispersao.png", 13.5, "Dispersão com a reta de regressão; as três estações com mais registro estão rotuladas."),
             *figura("q04c_correlacao.png", 7, "Correlação de Pearson do par."),
             P(f"A relação é real, mas frouxa: perto do centro os valores variam muito (o \"leque\" do gráfico), e o "
               f"teste de Breusch-Pagan confirma isso. Com erro padrão robusto (HC3), a inclinação continua "
               f"significativa (p = {p_valor(bp4['p_robusto']['dist_marco_zero_km'])}), então a conclusão sobre o "
               f"sentido da relação se mantém."),
             P("<b>Insight:</b> a distância serve para comparar regiões (centro registra mais que periferia), não "
               "para prever uma estação. O R² baixo é o recado: falta informação na base.", "insight")]

    # ---------------- Q05
    c5, pv5, bp5 = q5["coeficientes"], q5["p_valores"], q5["pressupostos"]
    hist += [PageBreak(), P("Distância, linhas e latitude juntas (questão 05)", "h1"),
             tabela([["variável", "coeficiente", "p-valor", "p-valor robusto (HC3)", "VIF"],
                     *[[v, br(c5[v], 2), p_valor(pv5[v]), p_valor(bp5["p_robusto"][v]), br(q5["vif"][v], 2)]
                       for v in q5["explicativas"]]], [4.4, 3, 2.6, 4, 2]),
             Spacer(1, 4),
             tabela([["ajuste", "valor"],
                     ["R² (três variáveis)", br(q5["r2"], 4)],
                     ["R² ajustado (três variáveis)", br(q5["r2_ajustado"], 4)],
                     ["R² ajustado sem a latitude", br(q5["r2_ajustado_sem_latitude"], 4)],
                     ["R² do modelo só com distância (questão 04)", br(q5["r2_do_modelo_simples"], 4)],
                     ["Teste F (p-valor)", p_valor(q5["F_p_valor"])],
                     ["previsão: 4 km, 3 linhas", f"{br(q5['previsao'], 0)} (IC 95% [{br(q5['previsao_ic95'][0], 0)}; "
                                                   f"{br(q5['previsao_ic95'][1], 0)}]); média real das parecidas "
                                                   f"{br(q5['media_real_parecidas'], 0)}"]], [7, 10]),
             Spacer(1, 6),
             P(f"Equação: {q5['equacao'].replace('.', ',')}", "nota"),
             *figura("q05a_dispersao.png", 12.5, "Matriz de dispersão das quatro variáveis, com o histograma de cada uma na diagonal."),
             *figura("q05c_correlacao.png", 9, "Correlação de Pearson entre as quatro variáveis."),
             P(f"Acrescentar o número de linhas levou o R² de {br(q5['r2_do_modelo_simples'], 3)} para "
               f"{br(q5['r2'], 3)}. A latitude não ajuda: sem ela, o R² ajustado é maior. A previsão do cenário de "
               f"baldeação central ficou abaixo da média real das 4 estações parecidas, fora do intervalo de 95%: com "
               f"tão poucas estações de 3 ou mais linhas, esse cenário é extrapolação."),
             P("<b>Insight:</b> baldeação é o fator com maior efeito por unidade. Para o app, estações de "
               "integração merecem o aviso de atenção mesmo fora do centro.", "insight")]

    # ---------------- Q06
    mc, dc = q6["matriz_confusao"], q6["decomposicao_central"]
    hist += [PageBreak(), P("Classificar estações de muito registro (questão 06)", "h1"),
             P(f"Resposta binária: 1 se a estação tem mais que a mediana ({br(q6['corte_mediana'], 0)} ocorrências), "
               f"0 se não. Regressão logística com as mesmas três explicativas."),
             tabela([["variável", "razão de chance", "p-valor"],
                     *[[v, br(q6["razoes_de_chance"][v], 3), p_valor(q6["p_valores"][v])] for v in q5["explicativas"]]],
                    [6, 5, 5]),
             Spacer(1, 4),
             tabela([["", "previsto: normal", "previsto: alta"],
                     ["real: normal", str(mc["vn"]), str(mc["fp"])],
                     ["real: alta", str(mc["fn"]), str(mc["vp"])]], [5, 5, 5]),
             Spacer(1, 4),
             tabela([["medida", "valor"],
                     ["acurácia", pct(q6["acuracia"])],
                     ["piso (sempre a classe maior)", pct(q6["piso_classe_majoritaria"])],
                     ["precisão / revocação", f"{br(q6['precisao'], 3)} / {br(q6['revocacao'], 3)}"],
                     ["AUC", br(q6["auc"], 3)],
                     ["pseudo R² de McFadden", br(q6["pseudo_r2_mcfadden"], 3)],
                     *[[c["nome"], f"p = {br(c['probabilidade'], 2)} → {c['classe']}"] for c in q6["classificacoes"]],
                     ["cenário central com 1 linha", f"p = {br(dc['p_1_linha_2km'], 2)}"],
                     ["cenário central a 22 km", f"p = {br(dc['p_3_linhas_22km'], 2)}"]], [8, 9]),
             Spacer(1, 6),
             *figura("q06_logistica.png", 16, "Probabilidade prevista por estação e matriz de confusão."),
             P(f"O modelo erra {mc['fn']} estações de muito registro, classificando-as como normais. Para um app que "
               f"avisa o passageiro, esse é o erro caro. Só a distância é significativa a 5%; o número de linhas "
               f"pesa tanto quanto a distância no cenário central, mas se apoia em apenas 4 estações e não é "
               f"significativo. Os números foram medidos na própria base de ajuste, então são otimistas."),
             P("<b>Insight:</b> o classificador é bom para priorizar onde mostrar o aviso, não para garantir que uma "
               "estação está tranquila. Na dúvida, o app deve errar para o lado do aviso.", "insight")]

    # ---------------- limitações
    hist += [PageBreak(), P("Limitações", "h1")]
    for texto in [
        "A base conta registros de BO, não risco. Sem o fluxo de passageiros não dá para calcular ocorrência por pessoa.",
        "A normalidade da questão 02 é exigência do enunciado; a variável é assimétrica à direita.",
        "As amostras da questão 03 são dirigidas (escolhidas pela distância); a checagem sorteada mostra a diferença.",
        "Os pressupostos da regressão linear não se cumprem por inteiro (variância desigual, resíduos assimétricos); "
        "os p-valores robustos confirmam as conclusões, mas o Teste F é aproximado.",
        f"Cerca de {pct(1 - q5['r2'], 0)} da variação fica sem explicação na regressão múltipla.",
        "Os modelos foram avaliados na mesma base em que foram ajustados.",
        "Só 4 estações têm 3 linhas ou mais: os cenários com 3 linhas são extrapolação.",
        "Os raios de 300 m se sobrepõem entre estações próximas, então as observações não são totalmente independentes.",
        "Registros com coordenada inválida (13,2% do município) foram descartados; o critério de município é aproximado.",
    ]:
        hist.append(P(f"• {texto}"))
    hist += [Spacer(1, 8), P("Como reproduzir", "h2"),
             P("Na pasta entregas/mlam: python main.py e depois python questao07_relatorio.py. Os scripts de cada "
               "questão, a base em .csv e o passo a passo de montagem da base (dados/LEIA-ME.md e preparar_base.py) "
               "acompanham este relatório.")]
    return hist


def main() -> int:
    arquivo_resultados = comum.SAIDAS / "resultados.json"
    if not arquivo_resultados.exists():
        print("Rode python main.py antes: ele gera saidas/resultados.json e os gráficos.")
        return 1
    resultados = json.loads(arquivo_resultados.read_text(encoding="utf-8"))
    doc = SimpleDocTemplate(str(ARQUIVO), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="MLAM: Global Solution 2026.2", author="Grupo Dá Tempo?")
    doc.build(montar(resultados), onFirstPage=_rodape, onLaterPages=_rodape)
    print(f"Relatório gravado em {ARQUIVO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
