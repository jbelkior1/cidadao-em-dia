"""Roda as duas rodadas do golden nas mesmas condições e compara.

    python rodar_antes_e_depois.py                  # as 26 do enunciado e as perguntas do grupo
    python rodar_antes_e_depois.py --so-enunciado   # só as 26 (a rodada oficial, que cabe no plano gratuito)

A rodada "antes" usa a versão de antes da melhoria, guardada em `historico/antes_da_melhoria/`
(`fichas.py`, `guardrails.py` e a ficha FT-04). O script troca esses três arquivos por um momento, roda
`avaliar.py --nome antes`, devolve a versão atual (mesmo se der erro), roda `avaliar.py --nome depois` e
imprime a comparação. A régua do juiz e a máscara do avaliador são as mesmas nas duas.

Gasta cerca de 140 chamadas ao modelo com as 34 mensagens (agente e juiz, duas rodadas), ou cerca de 90 só
com as 26. No plano gratuito do Groq o limite que pesa é o de tokens por minuto e por dia.
"""
import shutil
import subprocess
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ANTES = PASTA / "historico" / "antes_da_melhoria"
TROCAS = {
    ANTES / "fichas.py": PASTA / "pai_agente" / "fichas.py",
    ANTES / "guardrails.py": PASTA / "pai_agente" / "guardrails.py",
    ANTES / "FT-04_gratuidades.md": PASTA / "fichas" / "FT-04_gratuidades.md",
}


def avaliar(*args: str) -> int:
    return subprocess.call([sys.executable, str(PASTA / "avaliar.py"), *args], cwd=PASTA)


def main() -> int:
    extras = [a for a in sys.argv[1:] if a == "--so-enunciado"]     # repassado igual às duas rodadas
    guardados = {destino: destino.read_bytes() for destino in TROCAS.values()}
    try:
        for origem, destino in TROCAS.items():
            shutil.copyfile(origem, destino)
        if avaliar("--nome", "antes", *extras) != 0:
            print("A rodada 'antes' falhou; nada foi comparado.")
            return 1
    finally:
        for destino, conteudo in guardados.items():      # a versão atual volta sempre
            destino.write_bytes(conteudo)
    if avaliar("--nome", "depois", *extras) != 0:
        print("A rodada 'depois' falhou; nada foi comparado.")
        return 1
    return avaliar("--comparar", "antes", "depois")


if __name__ == "__main__":
    raise SystemExit(main())
