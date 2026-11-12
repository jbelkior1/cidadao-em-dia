"""PCP · o cérebro (EXEMPLO DO ESQUELETO).

A busca aqui é simples de propósito: conta palavras-chave encontradas.
A versão que vale nota é a das classes do PCP, com a regra de pontuação e de
confiança do enunciado. Quando estiver pronta, troque o miolo de `buscar`.
"""
import json
import re
import unicodedata
from pathlib import Path

import streamlit as st

MATERIA = "PCP"
BASE = json.loads((Path(__file__).parent.parent / "data" / "orientacoes_exemplo.json").read_text(encoding="utf-8"))
SINAIS_DE_GOLPE = {"pix": "pede pagamento por Pix", "pague": "pede pagamento", "taxa": "cobra uma taxa",
                   "urgente": "pressiona com urgência", "senha": "pede senha", "bloquead": "ameaça bloqueio",
                   "suspens": "ameaça suspensão", "clique": "pede para clicar num link"}


def normal(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def tem_dado_pessoal(texto: str) -> bool:
    """Recusa sequências longas de números (CPF, telefone) e e-mails."""
    return bool(re.search(r"\d{8,}", re.sub(r"[.\-\s()]", "", texto)) or "@" in texto)


def contem(texto: str, termo: str) -> bool:
    """Procura o termo como palavra inteira: rg não casa dentro de energia."""
    limite = chr(92) + 'b'   # \b: borda de palavra
    return re.search(limite + re.escape(normal(termo)) + limite, normal(texto)) is not None


def buscar(pergunta: str):
    """Devolve (orientação ou None, confiança, quantas palavras-chave bateram)."""
    p = normal(pergunta)
    melhor, acertos = None, 0
    for o in BASE:
        n = sum(1 for k in o["palavras_chave"] if contem(p, k))
        if n > acertos:
            melhor, acertos = o, n
    confianca = "alta" if acertos >= 2 else "média" if acertos == 1 else "baixa"
    return melhor, confianca, acertos


def palavras_encontradas(pergunta: str, orientacao: dict) -> list[str]:
    """Quais palavras-chave da orientação apareceram na pergunta (para explicar a resposta)."""
    return [k for k in orientacao["palavras_chave"] if contem(pergunta, k)]


def checagens(texto: str) -> list[tuple[str, bool, str]]:
    """Lista didática do que foi conferido: (o que conferimos, passou?, detalhe)."""
    dominios = re.findall(r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})(?:/\S*)?", texto.lower())
    p = normal(texto)
    nao_oficiais = [d for d in dominios if not d.endswith(".gov.br")]
    pagamento = [c for c in ("pix", "pague", "taxa") if c in p]
    pressao = [c for c in ("urgente", "bloquead", "suspens") if c in p]
    acesso = [c for c in ("senha", "clique") if c in p]
    return [
        ("O endereço é de um site do governo (termina em .gov.br)?", not nao_oficiais,
         f"encontrado: {nao_oficiais[0]}" if nao_oficiais else ("nenhum endereço na mensagem" if not dominios else "todos terminam em .gov.br")),
        ("A mensagem pede dinheiro (Pix, taxa, pagamento)?", not pagamento, "sim: " + ", ".join(pagamento) if pagamento else "não pede"),
        ("A mensagem pressiona com urgência ou ameaça?", not pressao, "sim: " + ", ".join(pressao) if pressao else "não pressiona"),
        ("A mensagem pede senha ou para clicar num link?", not acesso, "sim: " + ", ".join(acesso) if acesso else "não pede"),
    ]


def checar_golpe(texto: str):
    """Devolve (nível 'ok' ou 'atencao', lista de motivos)."""
    dominios = re.findall(r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})(?:/\S*)?", texto.lower())
    motivos = []
    nao_oficiais = [d for d in dominios if not d.endswith(".gov.br")]
    if nao_oficiais:
        motivos.append(f"O endereço {nao_oficiais[0]} não termina em .gov.br, que é o final dos sites do governo.")
    p = normal(texto)
    motivos += [f"A mensagem {txt}." for chave, txt in SINAIS_DE_GOLPE.items() if chave in p]
    return ("atencao" if motivos else "ok"), motivos


def testar():
    st.markdown("Digite uma pergunta e veja o que a busca encontra, com a confiança.")
    q = st.text_input("Pergunta", placeholder="Exemplo: tenho direito a desconto na conta de luz?", key="pcp_q")
    if q:
        if tem_dado_pessoal(q):
            st.warning("A pergunta tem dado pessoal e foi recusada. Nada foi registrado.")
        else:
            o, conf, n = buscar(q)
            if o and conf != "baixa":
                st.success(f"{o['titulo']} · confiança {conf} ({n} palavra-chave)")
                st.caption(f"Fonte: {o['fonte']} · conferido em: {o['verificado_em']}")
            else:
                st.info("Confiança baixa: o sistema responde que não sabe e passa a pergunta para o agente da PAI.")
    st.markdown("**Base de exemplo**")
    st.dataframe([{"id": o["id"], "título": o["titulo"], "palavras-chave": ", ".join(o["palavras_chave"])} for o in BASE],
                 hide_index=True, width="stretch")


# ---------------------------------------------------------------- triagem do Atendimento
# (palavra, peso): palavras fortes de um assunto valem 2. A ordem do dicionário desempata.
INTENCOES = {
    "golpe": dict(pagina="Isso é golpe?", resumo="conferir se uma mensagem é golpe",
                  palavras=[("golpe", 2), ("link", 1), ("mensagem", 1), ("pix", 1), ("taxa", 1), ("clique", 1), ("suspensa", 1),
                            ("bloqueada", 1), ("sms", 1), ("recebi", 1), ("cobranca", 1), ("boleto", 1)],
                  proximo="Você cola a mensagem e eu mostro, item por item, o que encontrei de suspeito."),
    "direitos": dict(pagina="Meus direitos", resumo="descobrir seus direitos",
                     palavras=[("direito", 2), ("direitos", 2), ("desconto", 2), ("tarifa social", 2), ("beneficio", 2), ("bolsa familia", 1),
                               ("cadunico", 1), ("cadastro unico", 1), ("auxilio", 1), ("bpc", 1)],
                     proximo="Eu faço 4 perguntas de sim ou não e mostro sua situação, o que fazer e o prazo."),
    "conta_luz": dict(pagina="Minha conta de luz", resumo="entender sua conta de luz",
                      palavras=[("conta de luz", 1), ("energia", 1), ("kwh", 1), ("consumo", 1), ("medidor", 1), ("chuveiro", 1),
                                ("gasto", 1), ("gastando", 1), ("veio alta", 1), ("muito cara", 1)],
                      proximo="Você vê quanto cada aparelho gasta, quanto fica a conta e quanto vale o desconto."),
    "duvida": dict(pagina="Tirar uma dúvida", resumo="tirar uma dúvida sobre documentos e serviços",
                   palavras=[("rg", 2), ("cpf", 2), ("documento", 2), ("documentos", 2), ("segunda via", 2), ("identidade", 1), ("certidao", 1),
                             ("titulo", 1), ("carteira", 1), ("perdi", 1), ("como faco", 1)],
                   proximo="Sua pergunta já vai feita, e eu respondo com a fonte e a data."),
}
TEM_ENDERECO = r"https?://|www[.]|[.](com|net|org|info|xyz)([^a-z]|$)"


def entender_necessidade(texto: str):
    """Devolve (intenção ou None, confiança, palavras que indicaram)."""
    pontos, achadas = {}, {}
    for chave, info in INTENCOES.items():
        lista = [(p, w) for p, w in info["palavras"] if contem(texto, p)]
        if chave == "golpe" and re.search(TEM_ENDERECO, texto.lower()):
            lista.append(("um endereço de site", 2))
        pontos[chave] = sum(w for _, w in lista)
        achadas[chave] = [p for p, _ in lista]
    melhor = max(INTENCOES, key=lambda k: pontos[k])   # max mantém a ordem do dicionário nos empates
    if pontos[melhor] == 0:
        return None, "baixa", []
    return melhor, ("alta" if pontos[melhor] >= 2 else "média"), achadas[melhor]
