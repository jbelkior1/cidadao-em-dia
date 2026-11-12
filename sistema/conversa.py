"""A conversa do atendimento.

Recebe um texto ou um clique e devolve:
- blocos: o que a tela mostra (texto, cartão, perguntas, ficha);
- estado: onde a conversa parou (a tela guarda e manda de volta; o servidor não guarda nada);
- rastro: qual matéria fez cada parte (aparece no modo banca);
- resumo: o que vai para o painel "Resumo do atendimento".

Nada do que a pessoa escreve é gravado.
"""
import re

from sistema import privacidade, triagem
from sistema.adaptadores import dsa, pcp
from sistema.servicos import direitos, energia, golpe

AVISO = "Não sou um canal oficial. Confirme no órgão responsável antes de decidir."
TAMANHO_MAXIMO = 1500


def _passo(materia: str, titulo: str, detalhe: str = "") -> dict:
    return {"materia": materia, "titulo": titulo, "detalhe": detalhe}


def _resposta(blocos: list, estado: dict, rastro: list | None = None, resumo: dict | None = None) -> dict:
    return {"blocos": blocos, "estado": estado, "rastro": rastro or [], "resumo": resumo}


def _texto(texto: str) -> dict:
    return {"tipo": "texto", "texto": texto}


def _assuntos(texto: str = "Sobre o que você quer falar?") -> dict:
    opcoes = [{"rotulo": info["rotulo"], "acao": f"assunto:{chave}"} for chave, info in triagem.ASSUNTOS.items()]
    return {"tipo": "opcoes", "texto": texto, "opcoes": opcoes}


def boas_vindas() -> dict:
    return _resposta(
        [_texto("Oi! Conte com as suas palavras o que você precisa. Não precisa de CPF nem de nome."),
         _assuntos("Ou escolha um assunto:")], {})


# ------------------------------------------------------------------ entrada

def processar(texto: str | None, acao: str | None, estado: dict | None) -> dict:
    estado = dict(estado or {})
    if acao:
        return _clique(acao, estado)
    texto = (texto or "").strip()
    if not texto:
        return _resposta([_texto("Escreva o que você precisa ou escolha um assunto."), _assuntos()], estado)
    if len(texto) > TAMANHO_MAXIMO:
        return _resposta([_texto("O texto ficou muito longo. Pode resumir em poucas frases?")], estado)

    if estado.get("etapa") == "golpe":            # mensagem colada: analisa sem guardar e sem barrar
        return _conferir_golpe(texto)

    motivo = privacidade.motivo(texto)
    if motivo:
        rastro = [_passo("PCP", "Barrou dado pessoal", f"{motivo}; a mensagem não foi registrada")]
        return _resposta([{"tipo": "recusa", "texto": privacidade.AVISO}], estado, rastro)

    if estado.get("etapa") == "luz":
        return _luz_consumo(texto, estado)
    if estado.get("etapa") == "luz_valor":
        return _luz_valor(texto, estado)
    if estado.get("etapa") == "duvida":
        return _tirar_duvida(texto)
    return _triar(texto)


def _clique(acao: str, estado: dict) -> dict:
    nome, _, valor = acao.partition(":")
    if nome == "confirmar" and estado.get("assunto"):
        return _iniciar(estado["assunto"], estado.get("texto", ""))
    if nome == "negar":
        return _resposta([_assuntos("Sem problema. Escolha o assunto:")], {})
    if nome == "assunto" and valor in triagem.ASSUNTOS:
        return _iniciar(valor, "")
    if nome == "resp" and estado.get("etapa") == "direitos":
        return _responder_direitos(valor, estado)
    if nome == "pular" and estado.get("etapa") == "luz_valor":
        return _luz_resultado(estado.get("kwh", 0), None)
    if nome == "categorias":
        return _listar_categorias()
    if nome == "categoria":
        return _listar_orientacoes(valor)
    if nome == "orientacao" and valor.isdigit():
        return _abrir_orientacao(int(valor))
    return boas_vindas()


# ------------------------------------------------------------------ triagem

def _triar(texto: str) -> dict:
    assunto, confianca, palavras = triagem.entender(texto)
    achado = pcp.responder(texto)
    botoes = [{"rotulo": "É isso", "acao": "confirmar", "principal": True}, {"rotulo": "Não é isso", "acao": "negar"}]

    # A busca oficial achou uma orientação com confiança ALTA: é uma dúvida, e a base tem a resposta.
    if achado["encontrou"] and achado["confianca"] == "ALTA" and assunto != "golpe":
        termos = [d["termo"] for d in achado["detalhe"] if d["pontos"] == 3] or [d["termo"] for d in achado["detalhe"]]
        bloco = {"tipo": "entendi", "resumo": f"Você quer saber sobre: {achado['orientacao']['titulo']}.", "porque": termos,
                 "confianca": "alta", "opcoes": botoes}
        rastro = [_passo("PCP", "Entendeu pela busca por pontos", f"{achado['pontos']} pontos, confiança ALTA")]
        return _resposta([bloco], {"etapa": "confirmar", "assunto": "duvida", "texto": texto}, rastro)

    if assunto is None:
        if achado["encontrou"]:                   # sem assunto claro, mas a base tem algo com confiança MÉDIA
            return _mostrar_orientacao(achado)
        return _resposta([_texto("Não entendi bem o que você precisa. Pode escolher um assunto?"), _assuntos("Assuntos:")], {})
    info = triagem.ASSUNTOS[assunto]
    bloco = {"tipo": "entendi", "resumo": f"Você quer {info['resumo']}.", "porque": palavras, "confianca": confianca, "opcoes": botoes}
    rastro = [_passo("Sistema", "Entendeu o assunto", "triagem por palavras: " + ", ".join(palavras))]
    return _resposta([bloco], {"etapa": "confirmar", "assunto": assunto, "texto": texto}, rastro)


def _iniciar(assunto: str, texto: str) -> dict:
    if assunto == "duvida":
        if texto:
            return _tirar_duvida(texto)
        blocos = [_texto("Escreva a sua dúvida do jeito que você falaria."),
                  {"tipo": "opcoes", "texto": "", "opcoes": [{"rotulo": "Ver os assuntos por categoria", "acao": "categorias"}]}]
        return _resposta(blocos, {"etapa": "duvida"})
    if assunto == "direitos":
        pergunta = direitos.PERGUNTAS[0]
        bloco = {"tipo": "opcoes", "texto": pergunta["texto"], "passo": f"Pergunta 1 de {len(direitos.PERGUNTAS)}",
                 "opcoes": [{"rotulo": o, "acao": f"resp:{o}"} for o in direitos.OPCOES]}
        return _resposta([_texto("São poucas perguntas de sim ou não."), bloco], {"etapa": "direitos", "passo": 0, "respostas": {}})
    if assunto == "luz":
        bloco = {"tipo": "numero", "texto": "Quantos kWh aparecem na sua conta deste mês?", "sufixo": "kWh",
                 "ajuda": "O número fica perto de \"Consumo\" ou \"kWh\" na conta de luz."}
        return _resposta([bloco], {"etapa": "luz"})
    blocos = [_texto("Cole aqui a mensagem que você recebeu. Eu analiso na hora e não guardo o texto.")]
    return _resposta(blocos, {"etapa": "golpe"})


# ------------------------------------------------------------------ tirar uma dúvida (PCP)

def _bloco_orientacao(achado: dict) -> dict:
    o = achado["orientacao"]
    return {"tipo": "orientacao", "id": o["id"], "titulo": o["titulo"], "categoria": o["categoria"],
            "confianca": achado.get("confianca"), "pontos": achado.get("pontos"), "detalhe": achado.get("detalhe", []),
            "resposta": o["resposta"], "documentos": o.get("documentos", []), "onde": o.get("onde", ""),
            "fonte": o.get("fonte", ""), "verificado_em": o.get("verificado_em", ""),
            "alternativas": achado.get("alternativas", []), "aviso": AVISO, "em_conferencia": o.get("em_conferencia", False),
            "selos": [{"materia": "PCP", "papel": "busca"}]}


def _mostrar_orientacao(achado: dict) -> dict:
    o = achado["orientacao"]
    bloco = _bloco_orientacao(achado)
    if achado.get("pontos") is not None:
        detalhe = f"busca por pontos: {achado['pontos']}, confiança {achado['confianca']}"
    else:
        detalhe = "aberta pela navegação por categoria"
    rastro = [_passo("PCP", "Achou a orientação", detalhe)]
    resumo = {"assunto": o["titulo"], "itens": [{"rotulo": "Onde resolver", "valor": o.get("onde", "")}]}
    servico = dsa.servico_de(o["titulo"])
    if servico:
        bloco["para_quem"] = servico["publico_alvo"]
        bloco["prazo"] = servico["prazo"]
        bloco["selos"].append({"materia": "DSA", "papel": "catálogo"})
        rastro.append(_passo("DSA", "Trouxe o registro do catálogo", f"{servico['id']}, guardado na lista encadeada"))
        if servico["prazo"]:
            resumo["itens"].append({"rotulo": "Prazo", "valor": servico["prazo"]["texto"]})
    blocos = [bloco]
    if o["categoria"] == "Conta de luz":          # da orientação para o caso da pessoa
        blocos.append({"tipo": "opcoes", "texto": "Quer ver o seu caso?",
                       "opcoes": [{"rotulo": "Ver se eu tenho direito", "acao": "assunto:direitos"},
                                  {"rotulo": "Calcular com a minha conta", "acao": "assunto:luz"}]})
    return _resposta(blocos, {}, rastro, resumo)


def _tirar_duvida(texto: str) -> dict:
    achado = pcp.responder(texto)
    if achado["bloqueada"]:
        return _resposta([{"tipo": "recusa", "texto": privacidade.AVISO}], {"etapa": "duvida"},
                         [_passo("PCP", "Barrou dado pessoal", "regra do enunciado: 8 dígitos ou mais, ou @")])
    if achado["encontrou"]:
        return _mostrar_orientacao(achado)
    blocos = [_texto("Não encontrei uma orientação sobre isso na minha base. Prefiro dizer que não sei a inventar uma resposta."),
              _categorias("Estes são os assuntos que eu conheço:")]
    rastro = [_passo("PCP", "Não encontrou", "a melhor orientação ficou abaixo de 3 pontos")]
    return _resposta(blocos, {"etapa": "duvida"}, rastro)


def _categorias(texto: str) -> dict:
    return {"tipo": "opcoes", "texto": texto, "opcoes": [{"rotulo": c, "acao": f"categoria:{c}"} for c in pcp.categorias()]}


def _listar_categorias() -> dict:
    return _resposta([_categorias("Escolha uma categoria:")], {"etapa": "duvida"},
                     [_passo("PCP", "Listou as categorias", "navegação por categoria")])


def _listar_orientacoes(categoria: str) -> dict:
    itens = pcp.por_categoria(categoria)
    if not itens:
        return _listar_categorias()
    bloco = {"tipo": "opcoes", "texto": f"Orientações em {categoria}:", "empilhado": True,
             "opcoes": [{"rotulo": o["titulo"], "acao": f"orientacao:{o['id']}"} for o in itens]}
    return _resposta([bloco], {"etapa": "duvida"}, [_passo("PCP", "Listou as orientações", categoria)])


def _abrir_orientacao(identificador: int) -> dict:
    o = pcp.orientacao(identificador)
    if not o:
        return _listar_categorias()
    return _mostrar_orientacao({"encontrou": True, "orientacao": o, "confianca": None, "pontos": None})


# ------------------------------------------------------------------ tenho algum direito?

def _responder_direitos(valor: str, estado: dict) -> dict:
    if valor not in direitos.OPCOES:
        return _iniciar("direitos", "")
    passo = estado.get("passo", 0)
    respostas = dict(estado.get("respostas", {}))
    respostas[direitos.PERGUNTAS[passo]["chave"]] = valor
    passo += 1
    resultado = direitos.orientar(respostas)
    if resultado is None:
        pergunta = direitos.PERGUNTAS[passo]
        bloco = {"tipo": "opcoes", "texto": pergunta["texto"], "passo": f"Pergunta {passo + 1} de {len(direitos.PERGUNTAS)}",
                 "opcoes": [{"rotulo": o, "acao": f"resp:{o}"} for o in direitos.OPCOES]}
        return _resposta([bloco], {"etapa": "direitos", "passo": passo, "respostas": respostas})

    rastro = [_passo("Sistema", "Aplicou as regras da Tarifa Social", f"{len(respostas)} resposta(s) de sim ou não")]
    linhas, selos = [], []
    servico = dsa.servico_de("tarifa social")
    if servico:
        linhas.append({"rotulo": "Para quem é", "valor": servico["publico_alvo"]})
        selos.append({"materia": "DSA", "papel": "catálogo"})
        rastro.append(_passo("DSA", "Trouxe o registro do catálogo", f"{servico['id']}, guardado na lista encadeada"))
    ficha = {"tipo": "ficha", "titulo": "Tarifa Social de Energia", "situacao": resultado["situacao"], "tom": resultado["tom"],
             "explicacao": resultado["explicacao"], "passos": resultado["passos"], "linhas": linhas,
             "fonte": direitos.FONTE, "verificado_em": direitos.CONSULTADO_EM, "selos": selos,
             "em_conferencia": direitos.EM_CONFERENCIA, "aviso": AVISO}
    blocos = [ficha]
    if resultado["tom"] == "ok":
        blocos.append({"tipo": "opcoes", "texto": "Quer ver quanto do seu consumo entra no desconto?",
                       "opcoes": [{"rotulo": "Calcular com a minha conta", "acao": "assunto:luz"}]})
    resumo = {"assunto": "Desconto na conta de luz",
              "itens": [{"rotulo": p["texto"], "valor": respostas[p["chave"]]} for p in direitos.PERGUNTAS if p["chave"] in respostas]}
    return _resposta(blocos, {}, rastro, resumo)


# ------------------------------------------------------------------ minha conta de luz

def _numero(texto: str) -> float | None:
    """Lê o primeiro número do texto. Aceita vírgula decimal (310,5) e ponto de milhar (1.250)."""
    achou = re.search(r"\d[\d.]*(?:,\d+)?", texto)
    if not achou:
        return None
    bruto = achou.group()
    if "," in bruto or re.fullmatch(r"\d{1,3}(\.\d{3})+", bruto):
        bruto = bruto.replace(".", "").replace(",", ".")
    try:
        return float(bruto)
    except ValueError:
        return None


def _luz_consumo(texto: str, estado: dict) -> dict:
    kwh = _numero(texto)
    if kwh is None or kwh <= 0 or kwh > 5000:
        return _resposta([_texto("Não consegui ler o consumo. Escreva só o número de kWh, por exemplo: 180.")], estado)
    bloco = {"tipo": "numero", "texto": "E quanto veio a conta, em reais?", "sufixo": "R$",
             "ajuda": "Serve só para estimar o desconto em dinheiro. Se preferir, pule.",
             "opcoes": [{"rotulo": "Pular", "acao": "pular"}]}
    return _resposta([bloco], {"etapa": "luz_valor", "kwh": kwh})


def _luz_valor(texto: str, estado: dict) -> dict:
    valor = _numero(texto)
    if valor is None or valor <= 0 or valor > 20000:
        return _resposta([_texto("Não consegui ler o valor. Escreva só o número, por exemplo: 280.")], estado)
    return _luz_resultado(estado.get("kwh", 0), valor)


def _luz_resultado(kwh: float, valor: float | None) -> dict:
    if not kwh:
        return _iniciar("luz", "")
    c = energia.calcular(kwh, valor)
    linhas = [{"rotulo": "Entra no desconto", "valor": f"{c['kwh_com_desconto']:g} kWh, sem cobrança de energia"},
              {"rotulo": "Continua cobrado", "valor": f"{c['kwh_cobrados']:g} kWh"}]
    aviso = "Impostos e iluminação pública continuam cobrados. "
    if c["desconto_mes"] is not None:
        linhas.append({"rotulo": "Preço médio na sua conta", "valor": energia.por_kwh(c["preco_medio"])})
        linhas.append({"rotulo": "Desconto estimado", "valor": "cerca de " + energia.reais(c["desconto_mes"]) + " por mês",
                       "destaque": "cerca de " + energia.reais(c["desconto_ano"]) + " em um ano"})
        aviso = "Estimativa pelo preço médio da sua conta, não é garantia. " + aviso + "Por isso o desconto real é menor. "
    ficha = {"tipo": "ficha", "titulo": "Sua conta de luz com a Tarifa Social", "situacao": f"{c['kwh']:g} kWh no mês", "tom": "neutro",
             "explicacao": f"Quem tem direito à Tarifa Social não paga a energia dos primeiros {energia.FAIXA_KWH} kWh do mês.",
             "passos": [], "linhas": linhas, "fonte": energia.FONTE, "verificado_em": energia.CONSULTADO_EM,
             "selos": [{"materia": "SERS", "papel": "cálculo"}], "em_conferencia": energia.EM_CONFERENCIA, "aviso": aviso + AVISO}
    seguir = {"tipo": "opcoes", "texto": "Quer saber se você tem direito ao desconto?",
              "opcoes": [{"rotulo": "Responder às perguntas", "acao": "assunto:direitos"}]}
    rastro = [_passo("SERS", "Calculou o desconto", f"faixa de {energia.FAIXA_KWH} kWh com 100% de desconto")]
    itens = [{"rotulo": "Consumo informado", "valor": f"{c['kwh']:g} kWh"}]
    if valor:
        itens.append({"rotulo": "Valor da conta", "valor": energia.reais(valor)})
    return _resposta([ficha, seguir], {}, rastro, {"assunto": "Conta de luz", "itens": itens})


# ------------------------------------------------------------------ isso é golpe?

def _conferir_golpe(texto: str) -> dict:
    r = golpe.conferir(texto)
    bloco = {"tipo": "sinais", "nivel": r["nivel"], "titulo": r["titulo"], "itens": r["itens"], "orientacao": r["orientacao"],
             "aviso": AVISO, "selos": []}
    rastro = [_passo("Sistema", "Conferiu a mensagem", f"{r['sinais']} sinal(is) de golpe; o texto não foi guardado")]
    resumo = {"assunto": "Mensagem suspeita", "itens": [{"rotulo": "Sinais encontrados", "valor": str(r["sinais"])}]}
    return _resposta([bloco], {}, rastro, resumo)
