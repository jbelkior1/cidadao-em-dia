"""O pacote de cada matéria, para baixar pela plataforma (botão na aba "Checklist da entrega").

Um .zip com duas coisas:
- LEIA-ME_<MATÉRIA>.txt: curto, explica o sistema, o que a matéria faz nele, como rodar e os links;
- entrega_para_o_portal/: os arquivos no formato que o enunciado pede, os mesmos que
  scripts/montar_entregas.py grava. O que ainda está entre colchetes falta preencher.

O texto e o zip são montados na hora, a partir dos mesmos dados das páginas (sistema/materias.py e o
checklist), então não há uma segunda cópia para ficar desatualizada.
"""
import io
import zipfile
from pathlib import Path

from sistema import config, materias

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
    "O Dá Tempo? é um app de trem e metrô de São Paulo. Antes de a pessoa sair, a agente Lia confere as linhas, "
    "a chuva, os alagamentos, a segurança perto das estações e o que os passageiros relataram, e responde com uma "
    "decisão: pode ir, saia mais cedo ou mude o caminho, com a fonte de cada informação. Não pede dado pessoal e "
    "não é canal oficial das operadoras."
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
    """O LEIA-ME da matéria: curto, só o que o professor precisa para entender e abrir a entrega."""
    m = materias.POR_CODIGO[cod]
    base = url.rstrip("/")
    linhas = [f"DÁ TEMPO? · {m['nome']} ({cod})", "Global Solution 2026.2 · FIAP", ""]
    linhas += ["INTEGRANTES", *[f"- {i}" for i in INTEGRANTES], ""]
    linhas += ["O SISTEMA", SISTEMA, ""]
    linhas += [f"O QUE {cod} FAZ NO SISTEMA", m["explicacao"], ""]
    if m.get("pasta"):
        linhas += ["COMO RODAR", f"Na pasta {m['pasta']}: {m['rodar']}", ""]
    linhas.append("LINKS")
    linhas.append(f"- Código no GitHub: {m['pasta_url'] or materias.REPOSITORIO}")
    if base:
        linhas.append(f"- Página da matéria (explicação, teste e checklist): {base}/materias/{cod.lower()}")
        if cod not in materias.FORA_DO_SISTEMA:
            linhas.append(f"- O app, para abrir no celular: {base}/app")
    linhas += ["", "NESTA PASTA",
               f"- LEIA-ME_{cod}.txt: este texto.",
               "- entrega_para_o_portal: os arquivos no formato do enunciado. O que estiver entre colchetes ainda falta preencher.", ""]
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
