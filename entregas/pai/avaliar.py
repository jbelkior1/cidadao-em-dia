# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Roda o agente e o juiz nas 26 mensagens do golden e grava o resultado.

    python avaliar.py                 # uma rodada, grava saidas/rodada_<nome>.json
    python avaliar.py --nome antes    # dá nome à rodada (padrão: a hora)
    python avaliar.py --comparar antes depois   # tabela antes x depois

O enunciado pede duas rodadas nas MESMAS mensagens, com uma melhoria concreta entre elas, e a
comparação numa tabela. Cada rodada grava tudo: resposta, veredito por critério e motivo, para a
tabela do notebook sair do arquivo e não da memória de ninguém.

Nada de dado pessoal real entra aqui: as 26 mensagens são as do enunciado, e o CPF do #22 é
fictício. Mesmo assim, a resposta gravada passa pela máscara antes de ir para o arquivo.
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from pai_agente import agente, fichas, guardrails, juiz  # noqa: E402
from pai_agente.modelo import config  # noqa: E402

GOLDEN = PASTA / "golden" / "golden_pai.json"
PAUSA_ENTRE_CASOS = 3        # segundos; o plano gratuito do Gemini limita chamadas por minuto
SAIDAS = PASTA / "saidas"


def carregar_golden(com_extras: bool = True) -> list[dict]:
    """As 26 do enunciado e, se pedido, as perguntas do grupo. As 26 nunca saem nem mudam."""
    d = json.loads(GOLDEN.read_text(encoding="utf-8"))
    casos = list(d["mensagens"])
    if com_extras:
        casos += d.get("extras_do_grupo", {}).get("mensagens", [])
    return casos


def _com_tentativas(funcao, tentativas: int = 6):
    """O provedor devolve 503 (instável) e 429 (limite por minuto). Uma rodada não pode morrer por isso."""
    espera = 10
    for n in range(1, tentativas + 1):
        try:
            return funcao()
        except Exception as e:
            if n == tentativas:
                raise
            print(f"      (tentativa {n} falhou: {type(e).__name__}; repetindo em {espera}s)")
            time.sleep(espera)
            espera *= 2


def _chave(trecho: str) -> str:
    """E-mail se compara pelo texto inteiro; telefone e outros números, pelos dígitos."""
    if "@" in trecho:
        return "email:" + trecho.strip().lower()
    return "num:" + re.sub(r"\D", "", trecho)


def _numeros_das_fichas() -> set[str]:
    """Telefones e contatos que já estão nas fichas: canal oficial é dado público, não dado pessoal."""
    return {_chave(m.group(0)) for f in fichas.carregar()
            for _, padrao in guardrails.PADROES_PESSOAIS for m in padrao.finditer(f.texto)}


def mascarar_para_o_arquivo(texto: str) -> str:
    """Esconde dado pessoal da resposta antes de gravar, mas mantém os canais oficiais das fichas.

    Na primeira versão, a resposta inteira passava por `guardrails.mascarar`, e o WhatsApp oficial da
    FT-01 virava "[DADO PESSOAL REMOVIDO]", no arquivo E no que o juiz lia. O juiz então marcou o
    golden #8 como "repetiu dado pessoal", sem a resposta real ter dado pessoal nenhum. Achado na
    conferência manual da rodada; corrigido aqui, e as duas rodadas foram refeitas com esta versão.
    """
    oficiais = _numeros_das_fichas()
    for _, padrao in guardrails.PADROES_PESSOAIS:
        texto = padrao.sub(lambda m: m.group(0) if _chave(m.group(0)) in oficiais else "[DADO PESSOAL REMOVIDO]", texto)
    return texto


def rodar(nome: str, com_extras: bool = True) -> dict:
    casos = carregar_golden(com_extras)
    cfg = config()
    print(f"Rodada '{nome}': {len(casos)} mensagens | provedor {cfg.provedor} / {cfg.modelo}\n")

    linhas, vereditos = [], []
    for caso in casos:
        r = _com_tentativas(lambda: agente.responder(caso["mensagem"]))
        resposta_limpa = mascarar_para_o_arquivo(r["resposta"])     # nada de PII no arquivo; canal oficial fica
        v = _com_tentativas(lambda: juiz.avaliar(caso, resposta_limpa))
        vereditos.append(v)
        linhas.append({**caso, "mensagem": mascarar_para_o_arquivo(caso["mensagem"]), "resposta": resposta_limpa,
                       "motivo": r["motivo"], "fichas_usadas": r["fichas"], "usou_modelo": r["usou_modelo"], "veredito": v})
        marca = "ok  " if v["acerto"] else ("????" if v["indeterminado"] else "ERRO")
        print(f"  [{marca}] #{caso['n']:2} {caso['tipo'][:16]:18} {mascarar_para_o_arquivo(caso['mensagem'])[:46]}")
        if r["usou_modelo"]:
            time.sleep(PAUSA_ENTRE_CASOS)       # respeita o limite de chamadas por minuto do provedor

    resumo = juiz.resumir(vereditos)
    resumo["so_as_26_do_enunciado"] = juiz.resumir([l["veredito"] for l in linhas if l["n"] <= 26])
    saida = {"nome": nome, "quando": datetime.now().isoformat(timespec="seconds"),
             "provedor": cfg.provedor, "modelo": cfg.modelo, "regua": juiz.REGUA.strip(),
             "resumo": resumo, "casos": linhas}
    SAIDAS.mkdir(exist_ok=True)
    arquivo = SAIDAS / f"rodada_{nome}.json"
    arquivo.write_text(json.dumps(saida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    oficial = resumo["so_as_26_do_enunciado"]
    print(f"\nAcertos nas 26 do enunciado: {oficial['acertos']}/{oficial['avaliados']} ({oficial['taxa'] * 100:.1f}%)")
    print(f"Acertos no total, com as do grupo: {resumo['acertos']}/{resumo['avaliados']} ({resumo['taxa'] * 100:.1f}%)")
    if resumo["indeterminados"]:
        print(f"Indeterminados (juiz não devolveu JSON): {resumo['indeterminados']}")
    if resumo["criterio_que_mais_falhou"]:
        print("Critérios que falharam:", ", ".join(f"{k} ({v})" for k, v in
                                                   sorted(resumo["criterio_que_mais_falhou"].items(),
                                                          key=lambda x: -x[1])))
    erros = [c for c in linhas if c["veredito"]["acerto"] is not True]
    if erros:
        print("\nErros, para orientar a melhoria:")
        for c in erros:
            print(f"  #{c['n']} ({c['tipo']}): {c['veredito']['justificativa']}")
    print(f"\nGravado em {arquivo}")
    return saida


def comparar(antes: str, depois: str) -> None:
    a = json.loads((SAIDAS / f"rodada_{antes}.json").read_text(encoding="utf-8"))
    b = json.loads((SAIDAS / f"rodada_{depois}.json").read_text(encoding="utf-8"))
    por_n_a = {c["n"]: c for c in a["casos"]}
    por_n_b = {c["n"]: c for c in b["casos"]}

    print(f"\n{'#':>3}  {'tipo':18} {'antes':7} {'depois':7}  mensagem")
    print("-" * 92)
    virou, quebrou = [], []
    for n in sorted(por_n_a):
        ca, cb = por_n_a[n], por_n_b.get(n, {})
        va = ca["veredito"]["acerto"]
        vb = cb.get("veredito", {}).get("acerto")
        rotulo = {True: "ok", False: "erro", None: "????"}
        if va is False and vb is True:
            virou.append(n)
        if va is True and vb is False:
            quebrou.append(n)
        print(f"{n:>3}  {ca['tipo'][:18]:18} {rotulo[va]:7} {rotulo.get(vb, '-'):7}  {ca['mensagem'][:42]}")
    print("-" * 92)
    print(f"{'':3}  {'TOTAL':18} {a['resumo']['acertos']:>2}/{a['resumo']['avaliados']:<4} "
          f"{b['resumo']['acertos']:>2}/{b['resumo']['avaliados']:<4}  "
          f"{a['resumo']['taxa'] * 100:.1f}% → {b['resumo']['taxa'] * 100:.1f}%")
    if virou:
        print(f"\nPassaram a acertar: {', '.join('#' + str(n) for n in virou)}")
    if quebrou:
        print(f"Deixaram de acertar: {', '.join('#' + str(n) for n in quebrou)}")


def main() -> int:
    p = argparse.ArgumentParser(description="Roda o agente e o juiz no golden dataset da PAI.")
    p.add_argument("--nome", default=datetime.now().strftime("%H%M"), help="nome da rodada")
    p.add_argument("--so-enunciado", action="store_true", help="roda so as 26, sem as perguntas do grupo")
    p.add_argument("--comparar", nargs=2, metavar=("ANTES", "DEPOIS"), help="compara duas rodadas já gravadas")
    a = p.parse_args()
    if a.comparar:
        comparar(*a.comparar)
    else:
        rodar(a.nome, com_extras=not a.so_enunciado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
