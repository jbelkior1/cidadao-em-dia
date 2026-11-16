"""O pacote de cada matéria, para baixar pela plataforma (botão na aba "Checklist da entrega").

Um .zip com duas coisas:
- LEIA-ME_<MATÉRIA>.txt: explica a solução (o que é o sistema, o que a matéria faz nele, como foi feito,
  o caminho por dentro, os arquivos no GitHub e os endereços do site);
- entrega_para_o_portal/: os arquivos no formato que o enunciado pede, os mesmos que
  scripts/montar_entregas.py grava. O que ainda está entre colchetes é da equipe preencher.

O texto e o zip são montados na hora, a partir dos mesmos dados das páginas (sistema/materias.py e o
checklist), então não há uma segunda cópia para ficar desatualizada.
"""
import io
import zipfile
from pathlib import Path

from sistema import checklist, config, materias

ENTREGAS = config.RAIZ / "entregas"
MODELOS = ENTREGAS / "portal"

INTEGRANTES = [
    "João Vitor Belchior Domingos Leite (RM 572478)",
    "João Pedro Pereira Teixeira (RM 569937)",
    "Thiago de Oliveira Coelho Souza (RM 568783)",
]

#: Textos do portal por matéria (modelos em entregas/portal/<matéria>/).
TEXTOS = {
    "PCP": ["pcp/PCP_entrega.txt"], "SERS": ["sers/SERS_entrega.txt"], "CS": ["cs/LEIA-ME.txt"], "MMC": ["mmc/LEIA-ME.txt"],
    "COA": ["coa/COA_entrega.txt"], "MLAM": ["mlam/COMO_ENVIAR.txt"], "DSA": ["dsa/LEIA-ME.txt"], "PAI": ["pai/LEIA-ME.txt"],
}
#: Pastas do repositório que vão inteiras para o portal ou para o repositório próprio da matéria.
PASTAS = {"PCP": ENTREGAS / "pcp" / "citizen-assist-ai", "DSA": ENTREGAS / "dsa", "PAI": ENTREGAS / "pai"}
MLAM_SOLTOS = [ENTREGAS / "mlam" / "dados" / "ocorrencias_estacoes_2026.csv", ENTREGAS / "mlam" / "saidas" / "relatorio_mlam_gs2026.pdf"]
NUNCA = {"__pycache__", ".env", "config.local.json", "uso_ia.local.json"}

SISTEMA = (
    "O Dá Tempo? é um app de trem e metrô de São Paulo que diz se dá tempo. Antes de a pessoa sair, a Lia, a agente do app, "
    "confere a situação das linhas, o aviso de chuva, os alagamentos, a segurança perto das estações e o que os outros passageiros "
    "relataram, e responde com uma decisão só: pode ir, saia mais cedo ou mude o caminho, com a chegada prevista e o desvio quando "
    "uma linha para. Toda resposta mostra a fonte e a hora da leitura, e dado pessoal (CPF, telefone, e-mail, endereço) é barrado "
    "antes de chegar à IA. Não é canal oficial das operadoras nem da Defesa Civil."
)


def preencher(texto: str, url: str) -> str:
    """Troca {URL_SISTEMA} pelo endereço; sem endereço, a linha inteira sai (link quebrado não vai ao professor)."""
    linhas = []
    for linha in texto.splitlines():
        if "{URL_SISTEMA}" in linha:
            if not url:
                continue
            linha = linha.replace("{URL_SISTEMA}", url.rstrip("/"))
        linhas.append(linha)
    return "\n".join(linhas).rstrip() + "\n"


def _arquivos_da_pasta(pasta: Path, destino: str):
    for arquivo in sorted(pasta.rglob("*")):
        relativo = arquivo.relative_to(pasta)
        if arquivo.is_file() and not (set(relativo.parts) & NUNCA) and arquivo.suffix != ".pyc":
            yield f"{destino}/{pasta.name}/{relativo.as_posix()}", arquivo.read_bytes()


def explicacao(cod: str, url: str) -> str:
    """O LEIA-ME da matéria, em texto simples."""
    m = materias.POR_CODIGO[cod]
    ck = checklist.ler()["materias"].get(cod, {})
    base = url.rstrip("/")
    linhas = [f"DÁ TEMPO? · {m['nome']} ({cod})", "Global Solution 2026.2 · FIAP · CitizenTech, case Citizen Assist AI", ""]
    linhas += ["INTEGRANTES", *[f"- {i}" for i in INTEGRANTES], ""]
    linhas += ["O SISTEMA", SISTEMA, ""]
    linhas += [f"O QUE {cod} FAZ NO SISTEMA", m["explicacao"], ""]
    linhas += ["COMO FOI FEITO", m["nesta_versao"], f"Regra principal: {m['regra']}"]
    if m.get("pasta"):
        linhas.append(f"Como rodar: entre na pasta {m['pasta']} e execute {m['rodar']}")
    linhas.append("")
    linhas += ["O CAMINHO POR DENTRO"]
    fluxo = m["fluxo"]
    for i, p in enumerate(fluxo["passos"], 1):
        linhas.append(f"{i}. {p['rotulo']}: {p['sub']}")
    if fluxo["decisao"]:
        d = fluxo["decisao"]
        linhas += [f"{len(fluxo['passos']) + 1}. {d['pergunta']}", f"   - sim: {d['sim']['rotulo']} ({d['sim']['sub']})",
                   f"   - não: {d['nao']['rotulo']} ({d['nao']['sub']})"]
    linhas.append("")
    if m["arquivos"]:
        linhas += ["ARQUIVOS NO GITHUB", f"Repositório: {materias.REPOSITORIO} (ramo {materias.RAMO})", *[f"- {a['rotulo']}: {a['url']}" for a in m["arquivos"]], ""]
    if base:
        linhas += ["ONDE VER NO SITE", *[f"- {r['rotulo']}: {base}{r['rota']}" for r in m["rotas"]], f"- Documentação funcional: {base}/documentacao", ""]
    if ck:
        linhas += ["O QUE VAI PARA O PORTAL", ck.get("formato_entrega", ""), f"Prazo: {ck.get('prazo', materias.PRAZO_GS)}", ""]
    linhas += ["NESTA PASTA", f"- LEIA-ME_{cod}.txt: este texto.",
               "- entrega_para_o_portal: os arquivos no formato do enunciado. O que estiver entre colchetes ainda é da equipe preencher (links do vídeo e do repositório, por exemplo).", ""]
    return "\n".join(linhas)


def pacote(cod: str, url: str = "") -> bytes:
    """O .zip da matéria, na memória."""
    cod = cod.upper()
    if cod not in materias.POR_CODIGO:
        raise KeyError(cod)
    arquivos: list[tuple[str, bytes]] = [(f"LEIA-ME_{cod}.txt", explicacao(cod, url).encode("utf-8"))]
    entrega = "entrega_para_o_portal"
    for modelo in TEXTOS[cod]:
        arquivos.append((f"{entrega}/{Path(modelo).name}", preencher((MODELOS / modelo).read_text(encoding="utf-8"), url).encode("utf-8")))
    if cod in PASTAS:
        arquivos += list(_arquivos_da_pasta(PASTAS[cod], entrega))
    if cod == "MLAM":
        pasta = ENTREGAS / "mlam"
        for arquivo in [*MLAM_SOLTOS, *sorted(pasta.glob("*.py"))]:
            arquivos.append((f"{entrega}/MLAM_para_enviar/{arquivo.name}", arquivo.read_bytes()))
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in arquivos:
            z.writestr(nome, dados)
    return memoria.getvalue()
