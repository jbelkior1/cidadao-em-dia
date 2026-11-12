"""Monta as bases das entregas a partir da pesquisa em fontes oficiais (tema do Plano B).

    python pesquisa/montar_bases.py

Lê:
- pesquisa/base_mobilidade.json      (orientações de mobilidade, levantadas em 12/11/2026)
- pesquisa/servicos_mobilidade.json  (serviços ao passageiro, levantados em 12/11/2026)

Grava:
- entregas/pcp/citizen-assist-ai/data/base_conhecimento.json  (formato do enunciado do PCP)
- entregas/dsa/dados/servicos.json                            (formato do catálogo da DSA)

Os fatos (resposta, documentos, onde, fonte) vêm da pesquisa, sem alteração.
Aqui só se ajustam o título e as palavras-chave, para a busca por pontos
encontrar a orientação quando a pessoa escreve do jeito dela.

Cada orientação sai com "conferido_pela_equipe": false. Depois de abrir a fonte
e conferir o texto, a equipe troca para true (ou apaga o campo) e atualiza a data.

A base anterior (tema Cidadão em Dia) continua em pesquisa/base_real_proposta.json.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# id da pesquisa -> (título curto, palavras-chave que a pessoa digitaria)
AJUSTES = {
    1: ("Declaração de atraso do Metrô (linhas 1, 2, 3 e 15)",
        ["declaração", "atraso", "comprovante de atraso", "declaração de ocorrência", "justificar atraso", "cheguei atrasado"]),
    2: ("Declaração de atraso nas linhas 4, 5, 8 e 9",
        ["declaração", "atraso", "viaquatro", "viamobilidade", "linha 4", "linha 8", "linha 9"]),
    3: ("Declaração de atraso da CPTM",
        ["declaração", "atraso", "cptm", "trem atrasou", "comunicado de ocorrência"]),
    4: ("Ônibus de apoio (PAESE) quando a linha para",
        ["paese", "ônibus de apoio", "linha parou", "parou", "ônibus emergencial", "e agora"]),
    5: ("Trem parado entre estações",
        ["trem parado", "parou entre estações", "túnel", "evacuação", "descer na via"]),
    6: ("Onde ver a situação das linhas",
        ["situação das linhas", "status", "linha parada", "como está a linha", "direto do metrô", "funcionando"]),
    7: ("Chuva forte e alagamento: o que fazer",
        ["alagamento", "chuva", "chovendo", "enchente", "tempestade", "alagada", "inundação"]),
    8: ("Defesa Civil: telefone 199 e alerta por SMS",
        ["defesa civil", "199", "40199", "alerta", "sms", "emergência"]),
    9: ("Celular roubado ou furtado",
        ["celular", "roubado", "furtado", "roubaram", "bloquear", "boletim de ocorrência"]),
    10: ("Assédio ou importunação: como denunciar",
         ["assédio", "importunação", "denunciar", "denúncia", "abuso", "sms segurança"]),
    11: ("Achados e perdidos",
         ["achados e perdidos", "perdi", "esqueci", "perdido", "objeto", "documento perdido"]),
    12: ("Como reclamar: ouvidorias e Artesp",
         ["reclamação", "reclamar", "ouvidoria", "artesp", "protocolo", "lei 13.460"]),
    13: ("Gratuidade para 65 anos ou mais",
         ["gratuidade", "idoso", "65 anos", "passe livre idoso", "de graça", "estatuto da pessoa idosa"]),
    14: ("Gratuidade para pessoas com deficiência",
         ["gratuidade", "deficiência", "pcd", "bilhete especial", "passe livre", "isenção"]),
    15: ("Acessibilidade e atendimento preferencial nas estações",
         ["acessibilidade", "cadeirante", "mobilidade reduzida", "elevador", "atendimento preferencial", "embarque assistido"]),
    16: ("Tarifas e integração do Bilhete Único",
         ["tarifa", "preço", "passagem", "quanto custa", "integração", "bilhete único"]),
}


def main():
    pesquisa = json.loads((RAIZ / "pesquisa" / "base_mobilidade.json").read_text(encoding="utf-8"))
    servicos = json.loads((RAIZ / "pesquisa" / "servicos_mobilidade.json").read_text(encoding="utf-8"))

    pcp = []
    for item in pesquisa:
        titulo, palavras = AJUSTES.get(item["id"], (item["titulo"], item["palavras_chave"]))
        pcp.append({
            "id": item["id"], "categoria": item["categoria"], "titulo": titulo, "palavras_chave": palavras,
            "resposta": item["resposta"], "documentos": item["documentos"], "onde": item["onde"],
            "fonte": item["fonte"], "verificado_em": item["verificado_em"], "conferido_pela_equipe": False,
        })

    dsa = []
    for s in servicos:
        descricao = s["descricao"]
        prazo = s.get("prazo", "")
        if prazo and not (len(prazo) == 10 and prazo[4] == "-" and prazo[7] == "-"):
            descricao = f"{descricao} Prazo: {prazo}."           # a DSA só aceita data AAAA-MM-DD no campo prazo
            prazo = ""
        dsa.append({"id": s["id"], "titulo": s["titulo"], "categoria": s["categoria"], "descricao": descricao,
                    "publico_alvo": s["publico_alvo"], "canal": s["canal"], "prazo": prazo,
                    "fonte": s["fonte"], "verificado_em": s["verificado_em"]})

    destino_pcp = RAIZ / "entregas" / "pcp" / "citizen-assist-ai" / "data" / "base_conhecimento.json"
    destino_dsa = RAIZ / "entregas" / "dsa" / "dados" / "servicos.json"
    destino_pcp.write_text(json.dumps(pcp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino_dsa.write_text(json.dumps(dsa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PCP: {len(pcp)} orientações em {len({o['categoria'] for o in pcp})} categorias -> {destino_pcp}")
    print(f"DSA: {len(dsa)} serviços -> {destino_dsa}")


if __name__ == "__main__":
    main()
