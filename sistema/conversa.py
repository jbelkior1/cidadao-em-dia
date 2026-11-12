"""O Pergunte do Plano B.

A pessoa escreve o que aconteceu ("a linha parou", "roubaram meu celular") e
recebe a orientação oficial pela busca por pontos do PCP, com o serviço do
catálogo da DSA quando houver. Também dá para navegar pelas categorias.

Devolve:
- blocos: o que a tela mostra (texto, cartão, opções);
- estado: onde a conversa parou (a tela guarda e manda de volta; o servidor não guarda nada);
- rastro: qual matéria fez cada parte (aparece no modo banca);
- resumo: o que vai para o painel lateral.

Nada do que a pessoa escreve é gravado.
"""
from sistema import privacidade
from sistema.adaptadores import dsa, pcp

AVISO = "O Plano B não é canal oficial. Confirme com a operadora ou o órgão responsável."
TAMANHO_MAXIMO = 1500
EXEMPLOS = ["A linha parou, e agora?", "Como pego a declaração de atraso?", "Roubaram meu celular no trem", "Está chovendo muito"]

# orientação do PCP -> serviço do catálogo da DSA onde a pessoa resolve (sem serviço certo, fica de fora)
SERVICO_DA_ORIENTACAO = {1: "SRV-003", 2: "SRV-011", 3: "SRV-007", 4: "SRV-001", 5: "SRV-004", 6: "SRV-003", 7: "SRV-013",
                         8: "SRV-013", 9: "SRV-014", 10: "SRV-004", 11: "SRV-005", 12: "SRV-012", 15: "SRV-006"}


def _passo(materia: str, titulo: str, detalhe: str = "") -> dict:
    return {"materia": materia, "titulo": titulo, "detalhe": detalhe}


def _resposta(blocos: list, estado: dict, rastro: list | None = None, resumo: dict | None = None) -> dict:
    return {"blocos": blocos, "estado": estado, "rastro": rastro or [], "resumo": resumo}


def _texto(texto: str) -> dict:
    return {"tipo": "texto", "texto": texto}


def _categorias(texto: str) -> dict:
    return {"tipo": "opcoes", "texto": texto, "opcoes": [{"rotulo": c, "acao": f"categoria:{c}"} for c in pcp.categorias()]}


def boas_vindas() -> dict:
    blocos = [_texto("Oi! Conte o que aconteceu no seu trajeto ou o que você quer saber. Eu respondo com a orientação oficial e a fonte."),
              {"tipo": "opcoes", "texto": "Por exemplo:", "opcoes": [{"rotulo": e, "acao": f"exemplo:{e}"} for e in EXEMPLOS]},
              _categorias("Ou escolha um assunto:")]
    return _resposta(blocos, {})


# ------------------------------------------------------------------ entrada

def processar(texto: str | None, acao: str | None, estado: dict | None) -> dict:
    estado = dict(estado or {})
    if acao:
        return _clique(acao)
    texto = (texto or "").strip()
    if not texto:
        return _resposta([_texto("Escreva o que aconteceu ou escolha um assunto."), _categorias("Assuntos:")], estado)
    if len(texto) > TAMANHO_MAXIMO:
        return _resposta([_texto("O texto ficou muito longo. Pode resumir em poucas frases?")], estado)
    motivo = privacidade.motivo(texto)
    if motivo:
        rastro = [_passo("PCP", "Barrou dado pessoal", f"{motivo}; a mensagem não foi registrada")]
        return _resposta([{"tipo": "recusa", "texto": privacidade.AVISO}], estado, rastro)
    return _buscar(texto)


def _clique(acao: str) -> dict:
    nome, _, valor = acao.partition(":")
    if nome == "exemplo" and valor:
        return _buscar(valor)
    if nome == "categorias":
        return _resposta([_categorias("Escolha um assunto:")], {}, [_passo("PCP", "Listou as categorias", "navegação por categoria")])
    if nome == "categoria":
        return _listar(valor)
    if nome == "orientacao" and valor.isdigit():
        o = pcp.orientacao(int(valor))
        if o:
            return _mostrar({"encontrou": True, "orientacao": o, "confianca": None, "pontos": None, "detalhe": [], "alternativas": []})
    return boas_vindas()


# ------------------------------------------------------------------ busca do PCP e catálogo da DSA

def _buscar(texto: str) -> dict:
    achado = pcp.responder(texto)
    if achado["bloqueada"]:
        return _resposta([{"tipo": "recusa", "texto": privacidade.AVISO}], {},
                         [_passo("PCP", "Barrou dado pessoal", "regra do enunciado: 8 dígitos ou mais, ou @")])
    if achado["encontrou"]:
        return _mostrar(achado)
    blocos = [_texto("Não encontrei uma orientação sobre isso. Prefiro dizer que não sei a inventar uma resposta."),
              _categorias("Estes são os assuntos que eu conheço:")]
    return _resposta(blocos, {}, [_passo("PCP", "Não encontrou", "a melhor orientação ficou abaixo de 3 pontos")])


def _mostrar(achado: dict) -> dict:
    o = achado["orientacao"]
    bloco = {"tipo": "orientacao", "id": o["id"], "titulo": o["titulo"], "categoria": o["categoria"],
             "confianca": achado.get("confianca"), "pontos": achado.get("pontos"), "detalhe": achado.get("detalhe", []),
             "resposta": o["resposta"], "documentos": o.get("documentos", []), "onde": o.get("onde", ""),
             "fonte": o.get("fonte", ""), "verificado_em": o.get("verificado_em", ""),
             "alternativas": achado.get("alternativas", []), "aviso": AVISO, "em_conferencia": o.get("em_conferencia", False),
             "selos": [{"materia": "PCP", "papel": "orientação"}]}
    if achado.get("pontos") is not None:
        rastro = [_passo("PCP", "Achou a orientação", f"busca por pontos: {achado['pontos']}, confiança {achado['confianca']}")]
    else:
        rastro = [_passo("PCP", "Abriu a orientação", "navegação por categoria")]
    resumo = {"assunto": o["titulo"], "itens": [{"rotulo": "Onde resolver", "valor": o.get("onde", "")}]}
    id_servico = SERVICO_DA_ORIENTACAO.get(o["id"])
    servico = dsa.servico_por_id(id_servico) if id_servico else None
    if servico:
        bloco["para_quem"] = servico["publico_alvo"]
        bloco["canal"] = servico["canal"]           # o prazo da DSA fica de fora: nos serviços de mobilidade ele vai na descrição
        bloco["selos"].append({"materia": "DSA", "papel": "catálogo"})
        rastro.append(_passo("DSA", "Trouxe o serviço do catálogo", f"{servico['id']}, guardado na lista encadeada"))
    seguir = {"tipo": "opcoes", "texto": "", "opcoes": [{"rotulo": "Ver outros assuntos", "acao": "categorias"}]}
    return _resposta([bloco, seguir], {}, rastro, resumo)


def _listar(categoria: str) -> dict:
    itens = pcp.por_categoria(categoria)
    if not itens:
        return _resposta([_categorias("Escolha um assunto:")], {})
    bloco = {"tipo": "opcoes", "texto": f"{categoria}:", "empilhado": True,
             "opcoes": [{"rotulo": o["titulo"], "acao": f"orientacao:{o['id']}"} for o in itens]}
    return _resposta([bloco], {}, [_passo("PCP", "Listou as orientações", categoria)])
