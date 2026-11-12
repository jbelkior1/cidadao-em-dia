"""Os fluxos do sistema, separados das telas.

Cada fluxo chama os módulos das matérias, devolve o que a tela mostra e a lista
de etapas (o "como chegamos"). Um módulo que falha vira etapa pendente e o
fluxo continua.
"""
from dataclasses import dataclass, field

from modulos import coa, dsa, pai, pcp, sers
from nucleo.contrato import Etapa


def _seguro(fn, falha: Etapa):
    try:
        return fn()
    except Exception as e:  # um módulo quebrado não derruba o fluxo
        falha.explicacao = f"erro: {e}"
        falha.pronto = False
        return falha


# ---------------------------------------------------------------- Tirar uma dúvida
@dataclass
class RespostaDuvida:
    tipo: str                      # "recusa", "orientacao", "agente" ou "nao_sei"
    titulo: str = ""
    texto: str = ""
    onde: str = ""
    fonte: str = ""
    conferido: str = ""
    motivo: str = ""
    etapas: list[Etapa] = field(default_factory=list)


def tirar_duvida(pergunta: str) -> RespostaDuvida:
    if pcp.tem_dado_pessoal(pergunta):
        return RespostaDuvida("recusa", etapas=[Etapa("PCP", "Recusou dado pessoal", "", "a pergunta foi bloqueada e não foi registrada")])
    o, conf, n = pcp.buscar(pergunta)
    etapas = [Etapa("PCP", "Procurou na base de orientações", "", f"confiança {conf}, {n} palavra(s)-chave")]
    if o and conf != "baixa":
        achadas = pcp.palavras_encontradas(pergunta, o)
        motivo = f"a pergunta tem {len(achadas)} palavra(s)-chave desta orientação ({', '.join(achadas)}), confiança {conf}"
        return RespostaDuvida("orientacao", o["titulo"], o["resposta"], o["onde"], o["fonte"], o["verificado_em"], motivo, etapas)
    texto, ficha = pai.responder(pergunta)
    if ficha:
        etapas.append(Etapa("PAI", "Agente respondeu pelas fichas", "", f"ficha {ficha['id']} (fictícia)"))
        motivo = f"a busca na base teve confiança baixa, então o agente procurou nas fichas e achou a {ficha['id']}"
        return RespostaDuvida("agente", ficha["titulo"], texto, "", f"ficha {ficha['id']}", ficha["data"], motivo, etapas)
    etapas.append(Etapa("PAI", "Agente não encontrou nas fichas", "", "resposta honesta de que não sabe"))
    return RespostaDuvida("nao_sei", etapas=etapas)


# ---------------------------------------------------------------- Meus direitos
@dataclass
class ResultadoDireitos:
    nivel: str                     # "ok", "risco" ou "comecar"
    situacao: str
    explicacao: str
    passos: list[str]
    prazo: dict | None = None
    dias: int | None = None
    economia: float | None = None
    documentos: str | None = None
    fonte: dict | None = None
    kwh: float | None = None
    ficha: dict | None = None
    etapas: list[Etapa] = field(default_factory=list)


def orientar(cad: bool, atu: bool, tit: bool):
    """Regras de orientação do sistema, em linguagem simples (parte do cérebro, PCP).

    As regras são exemplos e precisam ser conferidas nas normas da Aneel e do MDS.
    """
    if not cad:
        return ("comecar", "Comece pelo Cadastro Único",
                "O desconto na conta de luz é para famílias inscritas no CadÚnico.",
                ["Procure o CRAS da sua cidade e faça o Cadastro Único.", "Depois, confira na conta de luz se o desconto passou a aparecer."])
    if not atu:
        return ("risco", "Seu desconto pode estar em risco",
                "Cadastros sem atualização há mais de 2 anos podem perder benefícios.",
                ["Atualize o Cadastro Único no CRAS.", "Confira se a conta de luz está no nome de alguém da família."])
    if not tit:
        return ("risco", "Seu desconto pode estar em risco",
                "A conta de luz precisa estar no nome de alguém da família cadastrada.",
                ["Peça à distribuidora de energia para passar a conta para o nome de alguém da família.",
                 "Leve um documento de quem vai ser o titular da conta."])
    return ("ok", "Você parece estar em dia", "Seu cadastro e a conta de luz estão como o desconto exige.",
            ["Confira na conta de luz se o desconto aparece.", "Mantenha o Cadastro Único atualizado."])


def checar_direitos(cad: bool, atu: bool, tit: bool, kwh: float | None, kwh_do_medidor: bool) -> ResultadoDireitos:
    nivel, situacao, expl, passos = orientar(cad, atu, tit)
    etapas = [Etapa("PCP", "Aplicou as regras de orientação", "", "Cadastro Único, atualização e titular da conta de luz")]
    r = ResultadoDireitos(nivel, situacao, expl, passos, etapas=etapas)

    o, _, _ = pcp.buscar("tarifa social conta de luz")
    if o:
        r.fonte = o
        etapas.append(Etapa("PCP", "Trouxe a fonte e a data", "", f"{o['fonte']} (conferido: {o['verificado_em']})"))
    item = dsa.prazo_de("tarifa social")
    if item:
        r.prazo, r.dias = item, dsa.dias_ate(item["prazo"])
        etapas.append(Etapa("DSA", "Achou o prazo no catálogo", "", f"{item['acao']}: {dsa.data_br(item['prazo'])}"))
    if kwh is not None:
        if kwh_do_medidor:
            etapas.append(Etapa("COA", "Leu o consumo no medidor", "", f"{kwh} kWh no mês (simulação)"))
        r.economia, r.kwh = sers.economia_ano(kwh), kwh
        etapas.append(Etapa("SERS", "Calculou quanto vale o desconto", "", f"{kwh} kWh × tarifa de exemplo, faixa de exemplo"))
    texto, ficha = pai.responder("documentos para atualizar o cadastro")
    if ficha:
        r.documentos, r.ficha = texto, ficha
        etapas.append(Etapa("PAI", "Listou os documentos", "", f"ficha {ficha['id']} (fictícia)"))
    return r


# ---------------------------------------------------------------- Isso é golpe?
@dataclass
class ResultadoGolpe:
    nivel: str                     # "ok" ou "atencao"
    motivos: list[str]
    etapas: list[Etapa]


def checar_golpe(texto: str) -> ResultadoGolpe:
    nivel, motivos = pcp.checar_golpe(texto)
    return ResultadoGolpe(nivel, motivos, [Etapa("PCP", "Conferiu endereço e sinais de golpe", "", f"{len(motivos)} sinal(is) encontrado(s)")])


# ---------------------------------------------------------------- Minha conta de luz
def conta_de_luz(kwh: float, do_medidor: bool):
    cor, frase = coa.estado(kwh)
    etapas = []
    if do_medidor:
        etapas.append(Etapa("COA", "Leu o consumo no medidor", "", f"{kwh} kWh (simulação); LED {cor}"))
    etapas.append(Etapa("SERS", "Calculou a conta e o desconto", "", "consumo × tarifa de exemplo"))
    return {"kwh": kwh, "conta": sers.conta_mes(kwh), "economia": sers.economia_ano(kwh), "led": cor, "frase": frase, "etapas": etapas}
