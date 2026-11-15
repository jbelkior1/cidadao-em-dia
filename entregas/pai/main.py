"""Assistente de orientação do Dá Tempo? (fichas de transporte FT-01 a FT-07), uso pelo terminal.

    python main.py

Navegação simples, como o enunciado pede (seção 2.2): menu por categorias e entrada livre em
texto, as duas no mesmo lugar. Tudo funciona só com o teclado, as linhas são curtas e cada
resposta vem com a fonte e o aviso de que não é canal oficial.

Nada é gravado: nem a pergunta, nem a resposta, nem histórico. É a forma mais simples de cumprir
a seção 3 do enunciado (não guardar dado pessoal): o que não existe não vaza.
"""
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA))

from pai_agente import agente, fichas  # noqa: E402
from pai_agente.modelo import config  # noqa: E402

LARGURA = 78


def risca(c: str = "-") -> None:
    print(c * LARGURA)


def quebrar(texto: str, recuo: str = "") -> None:
    """Imprime em linhas curtas, para ler fácil no terminal."""
    for paragrafo in texto.splitlines():
        linha = recuo
        for palavra in paragrafo.split():
            if len(linha) + len(palavra) + 1 > LARGURA:
                print(linha)
                linha = recuo + palavra
            else:
                linha = f"{linha} {palavra}".strip() if linha.strip() else recuo + palavra
        print(linha if linha.strip() else "")


def abertura() -> None:
    cfg = config()
    risca("=")
    print("DÁ TEMPO?: orientação sobre metrô, trem e ônibus em São Paulo")
    risca("=")
    quebrar("Protótipo educacional da Global Solution 2026.2. As fichas foram montadas a partir de "
            "páginas oficiais lidas em 12/11/2026, mas regras e telefones mudam. Este assistente não é "
            "canal oficial: confirme no site ou na central da operadora antes de agir.")
    print()
    quebrar("Não digite CPF, RG, endereço, telefone nem e-mail. Eu não guardo nada do que você "
            "escreve, e recuso mensagens com dado pessoal.")
    print()
    print(f"Modelo: {cfg.provedor} / {cfg.modelo}" + ("" if cfg.tem_chave else "  (SEM CHAVE: só as recusas respondem)"))
    if cfg.aviso:
        print(f"Atenção: {cfg.aviso}")


def menu() -> None:
    print()
    risca()
    print("ASSUNTOS (digite o número) ou escreva sua pergunta. 0 para sair.")
    risca()
    for i, f in enumerate(fichas.carregar(), 1):
        print(f"  {i}. {f.assunto}")
    print("  0. Sair")


PERGUNTA_DO_MENU = {
    "FT-01": "A linha parou. Como sei a situação e se tem ônibus de apoio?",
    "FT-02": "Como peço a declaração de atraso do metrô ou do trem?",
    "FT-03": "Como faço uma reclamação e o que faço se não me responderem?",
    "FT-04": "Quem tem gratuidade no transporte e como peço o bilhete especial?",
    "FT-05": "Perdi um objeto no metrô ou no trem. Onde procuro?",
    "FT-06": "Quanto custa a passagem e como funciona a integração do Bilhete Único?",
    "FT-07": "Como denuncio assédio e onde peço ajuda com acessibilidade ou chuva forte?",
}


def responder_e_mostrar(pergunta: str) -> None:
    print()
    print("...consultando as fichas")
    try:
        r = agente.responder(pergunta)
    except Exception:
        print()
        quebrar("Não consegui responder agora. Tente de novo em instantes.")   # sem termo técnico para quem usa
        return
    print()
    risca()
    quebrar(r["resposta"])
    risca()
    if r["fichas"]:
        print(f"Fichas consultadas: {', '.join(r['fichas'])}")


def main() -> int:
    abertura()
    lista = fichas.carregar()
    while True:
        menu()
        try:
            entrada = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo.")
            return 0

        if entrada == "0" or entrada.lower() in ("sair", "exit", "quit"):
            print("Até logo.")
            return 0

        if entrada.isdigit() and 1 <= int(entrada) <= len(lista):
            ficha = lista[int(entrada) - 1]
            print(f"\nAssunto escolhido: {ficha.assunto}")
            responder_e_mostrar(PERGUNTA_DO_MENU.get(ficha.id, ficha.assunto))
        else:
            responder_e_mostrar(entrada)


if __name__ == "__main__":
    raise SystemExit(main())
