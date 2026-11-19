"""Monta os pacotes de entrega no portal, matéria por matéria, no formato de cada enunciado.

    python scripts/montar_entregas.py                               # sem o endereço da plataforma
    python scripts/montar_entregas.py --url https://SEU-DOMINIO     # depois do deploy

Lê os modelos de entregas/portal/<matéria>/ e grava em entregas/portal/saida/ (fora do git):
- PCP e SERS: um único .txt, como os enunciados mandam;
- DSA e PAI: um .zip com a pasta da entrega e o LEIA-ME.txt;
- MLAM: a pasta MLAM_para_enviar com o .csv, os .py de entregas/mlam/entrega e o .pdf soltos (o enunciado proíbe links e
  aceita só esses formatos);
- CS, MMC, COA e o vídeo pitch: o modelo de texto a completar.

Sem --url, a linha "Página da matéria no sistema" sai do texto (link quebrado não vai ao professor).
No fim, lista o que ainda está entre colchetes, por preencher.
"""
import argparse
import re
import shutil
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MODELOS = RAIZ / "entregas" / "portal"
SAIDA = MODELOS / "saida"
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".env", "config.local.json", "uso_ia.local.json")

TEXTOS = {
    "PCP": ["pcp/PCP_entrega.txt"],
    "SERS": ["sers/SERS_entrega.txt"],
    "CS": ["cs/LEIA-ME.txt"],
    "MMC": ["mmc/LEIA-ME.txt"],
    "COA": ["coa/COA_entrega.txt"],
    "PITCH": ["pitch/PITCH_entrega.txt"],
    "MLAM": ["mlam/MLAM_entrega.txt", "mlam/COMO_ENVIAR.txt"],
}
ZIPS = {"DSA": ("dsa/LEIA-ME.txt", RAIZ / "entregas" / "dsa"), "PAI": ("pai/LEIA-ME.txt", RAIZ / "entregas" / "pai")}
MLAM = RAIZ / "entregas" / "mlam"


def preencher(texto: str, url: str) -> str:
    """Troca {URL_SISTEMA} pelo endereço; sem endereço, a linha inteira sai."""
    linhas = []
    for linha in texto.splitlines():
        if "{URL_SISTEMA}" in linha:
            if not url:
                continue
            linha = linha.replace("{URL_SISTEMA}", url.rstrip("/"))
        linhas.append(linha)
    return "\n".join(linhas).rstrip() + "\n"


def zipar(pasta: Path, destino: Path, leia_me: str | None = None) -> None:
    temporaria = destino.with_suffix("")
    if temporaria.exists():
        shutil.rmtree(temporaria)
    shutil.copytree(pasta, temporaria / pasta.name, ignore=IGNORAR)
    if leia_me:
        (temporaria / "LEIA-ME.txt").write_text(leia_me, encoding="utf-8")
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for arquivo in sorted(temporaria.rglob("*")):
            if arquivo.is_file():
                z.write(arquivo, arquivo.relative_to(temporaria))
    shutil.rmtree(temporaria)


def main() -> int:
    p = argparse.ArgumentParser(description="Monta os pacotes de entrega do portal.")
    p.add_argument("--url", default="", help="endereço público da plataforma, por exemplo https://datempo.exemplo.com.br")
    url = p.parse_args().url
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    SAIDA.mkdir(parents=True)

    gerados = []
    for materia, modelos in TEXTOS.items():
        pasta = SAIDA / materia
        pasta.mkdir()
        for modelo in modelos:
            destino = pasta / Path(modelo).name
            destino.write_text(preencher((MODELOS / modelo).read_text(encoding="utf-8"), url), encoding="utf-8")
            gerados.append(destino)

    for materia, (modelo, pasta_entrega) in ZIPS.items():
        destino = SAIDA / materia / f"{materia}_entrega.zip"
        destino.parent.mkdir(exist_ok=True)
        zipar(pasta_entrega, destino, preencher((MODELOS / modelo).read_text(encoding="utf-8"), url))
        gerados.append(destino)

    soltos = SAIDA / "MLAM" / "MLAM_para_enviar"
    soltos.mkdir(parents=True, exist_ok=True)
    for arquivo in [MLAM / "dados" / "ocorrencias_estacoes_2026.csv", *sorted((MLAM / "entrega").glob("questao*.py")),
                    MLAM / "saidas" / "relatorio_mlam_gs2026.pdf"]:
        shutil.copy2(arquivo, soltos / arquivo.name)
    gerados.append(soltos)
    mlam_zip = SAIDA / "MLAM" / "MLAM_entrega.zip"          # os mesmos 7 arquivos num zip, para quem preferir
    with zipfile.ZipFile(mlam_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for arquivo in sorted(soltos.iterdir()):
            z.write(arquivo, arquivo.name)
    gerados.append(mlam_zip)

    pcp_repo = SAIDA / "PCP" / "citizen-assist-ai.zip"          # conteúdo do repositório público que o PCP pede
    zipar(RAIZ / "entregas" / "pcp" / "citizen-assist-ai", pcp_repo)
    gerados.append(pcp_repo)

    print(f"Pacotes em {SAIDA}:")
    for g in gerados:
        print("  -", g.relative_to(SAIDA))
    pendentes = []
    for arquivo in SAIDA.rglob("*.txt"):
        for marca in sorted(set(re.findall(r"\[[^\]\n]{3,240}\]", arquivo.read_text(encoding="utf-8")))):
            pendentes.append(f"{arquivo.relative_to(SAIDA)}: {marca}")
    if pendentes:
        print("\nAinda por preencher:")
        for item in pendentes:
            print("  -", item)
    if not url:
        print("\nSem --url: as linhas com o endereço da plataforma ficaram de fora. Depois do deploy, rode de novo com --url.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
