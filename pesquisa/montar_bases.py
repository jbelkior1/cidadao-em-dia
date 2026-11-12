"""Monta as bases das entregas a partir da pesquisa em fontes oficiais.

    python pesquisa/montar_bases.py

Lê pesquisa/base_real_proposta.json e grava:
- entregas/pcp/citizen-assist-ai/data/base_conhecimento.json  (formato do enunciado do PCP)
- entregas/dsa/dados/servicos.json                            (formato do catálogo da DSA)

Os fatos (resposta, documentos, onde, fonte) vêm da pesquisa, sem alteração.
Aqui só se ajustam o título e as palavras-chave, para a busca por pontos
encontrar a orientação quando a pessoa escreve do jeito dela.

Cada registro sai com "conferido_pela_equipe": false. Depois de abrir a fonte e
conferir o texto, a equipe troca para true (ou apaga o campo) e atualiza a data.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# id da pesquisa -> (título curto, palavras-chave que a pessoa digitaria)
AJUSTES = {
    1: ("Atualizar o Cadastro Único",
        ["cadastro único", "cadúnico", "atualizar", "atualizo", "atualização", "desatualizado"]),
    2: ("Fazer a inscrição no Cadastro Único",
        ["cadastro único", "cadúnico", "inscrição", "inscrever", "cadastrar", "fazer cadastro"]),
    3: ("Tarifa Social de Energia: desconto na conta de luz",
        ["tarifa social", "conta de luz", "desconto na conta", "direito a desconto", "luz de graça", "80 kwh"]),
    4: ("Desconto da Tarifa Social não apareceu na conta de luz",
        ["tarifa social", "conta de luz", "não apareceu", "não veio", "sem desconto", "distribuidora"]),
    5: ("Bolsa Família bloqueado por cadastro desatualizado",
        ["bolsa família", "bloqueado", "cancelado", "revisão cadastral", "averiguação", "desbloquear"]),
    6: ("BPC para idoso ou pessoa com deficiência",
        ["bpc", "loas", "benefício de prestação continuada", "deficiência", "inss", "65 anos"]),
    7: ("Consultar e regularizar o CPF",
        ["cpf", "situação cadastral", "regularizar", "suspenso", "pendente de regularização", "receita federal"]),
    8: ("Carteira de Identidade Nacional (CIN), o novo RG",
        ["rg", "identidade", "cin", "carteira de identidade", "primeira via", "documento de identidade"]),
    9: ("Certidão de nascimento ou casamento: segunda via e gratuidade",
        ["certidão", "certidão de nascimento", "certidão de casamento", "cartório", "segunda via da certidão", "declaração de pobreza"]),
    10: ("Carteira da Pessoa Idosa para viagem interestadual",
         ["carteira do idoso", "carteira da pessoa idosa", "passagem", "viagem", "ônibus", "idoso"]),
    11: ("Valores a receber do Banco Central",
         ["valores a receber", "dinheiro esquecido", "banco central", "dinheiro a receber", "svr", "devolução"]),
    12: ("Mensagem do governo: como saber se é verdadeira",
         ["golpe", "mensagem falsa", "pix", "taxa", "site falso", "link"]),
    13: ("Golpe no Cadastro Único: não pague intermediários",
         ["golpe", "intermediário", "pagar para cadastrar", "cobrando", "fraude", "disque 121"]),
}


def main():
    pesquisa = json.loads((RAIZ / "pesquisa" / "base_real_proposta.json").read_text(encoding="utf-8"))
    pcp, dsa = [], []
    for item in pesquisa:
        titulo, palavras = AJUSTES.get(item["id"], (item["titulo"], item["palavras_chave"]))
        pcp.append({
            "id": item["id"], "categoria": item["categoria"], "titulo": titulo, "palavras_chave": palavras,
            "resposta": item["resposta"], "documentos": item["documentos"], "onde": item["onde"],
            "fonte": item["fonte"], "verificado_em": item["verificado_em"], "conferido_pela_equipe": False,
        })
        dsa.append({
            "id": f"SRV-{item['id']:03d}", "titulo": titulo, "categoria": item["categoria"], "descricao": item["resposta"],
            "publico_alvo": item["publico_alvo"], "canal": item["onde"], "prazo": item["prazo"] or "",
            "fonte": item["fonte"], "verificado_em": item["verificado_em"],
        })
    destino_pcp = RAIZ / "entregas" / "pcp" / "citizen-assist-ai" / "data" / "base_conhecimento.json"
    destino_dsa = RAIZ / "entregas" / "dsa" / "dados" / "servicos.json"
    destino_pcp.write_text(json.dumps(pcp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    destino_dsa.write_text(json.dumps(dsa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PCP: {len(pcp)} orientações em {len({o['categoria'] for o in pcp})} categorias -> {destino_pcp}")
    print(f"DSA: {len(dsa)} serviços -> {destino_dsa}")


if __name__ == "__main__":
    main()
