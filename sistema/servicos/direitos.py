"""Tenho algum direito? Perguntas de sim ou não sobre a Tarifa Social de Energia.

As regras vêm da página da Aneel sobre a Tarifa Social, lida em 12/11/2026
(ver pesquisa/dados_tarifa_social.json). A equipe ainda precisa abrir a fonte
e confirmar cada trecho; enquanto isso, EM_CONFERENCIA fica ligado e a tela avisa.
"""

EM_CONFERENCIA = True
FONTE = "https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-social"
CONSULTADO_EM = "2026-11-12"

PERGUNTAS = [
    {"chave": "cadastro", "texto": "Sua família está inscrita no Cadastro Único (CadÚnico)?"},
    {"chave": "renda", "texto": "A renda da família é de até meio salário mínimo por pessoa, ou alguém da casa recebe o BPC?"},
    {"chave": "atualizado", "texto": "O Cadastro Único foi atualizado nos últimos 2 anos?"},
    {"chave": "titular", "texto": "A conta de luz está no nome de alguém da família?"},
]
OPCOES = ["Sim", "Não", "Não sei"]


def orientar(respostas: dict) -> dict | None:
    """Recebe as respostas dadas até agora. Devolve o resultado, ou None se ainda falta perguntar."""
    r = respostas.get
    if r("cadastro") in ("Não", "Não sei"):
        return {"tom": "inicio", "situacao": "Comece pelo Cadastro Único",
                "explicacao": "O desconto na conta de luz é dado a partir do Cadastro Único ou do cadastro do BPC.",
                "passos": ["Faça a inscrição no posto do Cadastro Único da sua cidade, como o CRAS. É gratuito.",
                           "Leve o CPF de todas as pessoas da família e um documento de identificação."]}
    if r("renda") == "Não":
        return {"tom": "neutro", "situacao": "Pela renda, o desconto pode não valer para a sua família",
                "explicacao": ("A Tarifa Social é para famílias com renda de até meio salário mínimo por pessoa, para quem recebe o BPC "
                               "e para famílias com pessoa com doença ou deficiência e renda de até 3 salários mínimos."),
                "passos": ["Confira os critérios na página da Aneel ou com a distribuidora de energia.",
                           "Se a renda da família mudar, atualize o Cadastro Único."]}
    if r("atualizado") in ("Não", "Não sei"):
        return {"tom": "risco", "situacao": "Atualize o Cadastro Único",
                "explicacao": "Para ter o desconto, o Cadastro Único precisa ter sido atualizado nos últimos 2 anos. Isso é conferido na concessão.",
                "passos": ["Atualize no CRAS ou no posto do Cadastro Único. É gratuito.",
                           "Leve o CPF de todas as pessoas da família e um documento de identificação."]}
    if r("titular") in ("Não", "Não sei"):
        return {"tom": "risco", "situacao": "Confira quem é o titular da conta de luz",
                "explicacao": "O desconto é automático para as famílias em que uma pessoa da família é titular do contrato com a distribuidora.",
                "passos": ["Procure a distribuidora de energia e pergunte como deixar a conta no nome de alguém da família."]}
    if len(respostas) < len(PERGUNTAS):
        return None
    aviso_renda = " Como você não tem certeza da renda, confirme esse ponto no CRAS." if r("renda") == "Não sei" else ""
    return {"tom": "ok", "situacao": "Você parece ter direito ao desconto",
            "explicacao": ("Pela regra das contas emitidas a partir de 5 de julho de 2025, o desconto é de 100% no consumo de até 80 kWh por mês. "
                           "O que passar de 80 kWh é cobrado normalmente." + aviso_renda),
            "passos": ["O desconto é automático: não precisa pedir.",
                       "Confira na conta de luz se ele aparece. Se não aparecer, procure a distribuidora de energia."]}
