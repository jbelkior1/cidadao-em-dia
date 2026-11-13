"""Checagem das fontes de dados: cada API externa e cada base local, com prova de que o dado é real.

Uma entrada por fonte, sempre com a mesma forma:

    {"id", "nome", "tipo", "origem", "estado", "ms", "lido_em", "amostra", "usado_em", "detalhe"}

- tipo: "api" (lida ao vivo), "base" (arquivo no repositório) ou "banco" (Supabase).
- estado: "ok" (respondeu com dado), "vazio" (respondeu, mas sem nada agora) ou "falhou".
- amostra: um pedaço do dado de verdade que veio, para dar para conferir à mão.

Roda pela API (GET /api/fontes) e pelo terminal (python -m sistema.fontes_saude).
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from sistema import banco
from sistema.mobilidade import fontes, rede

DADOS = Path(__file__).parent / "dados"
PESQUISA = Path(__file__).resolve().parent.parent / "pesquisa"


def _medir(funcao):
    inicio = time.perf_counter()
    try:
        return funcao(), None, round((time.perf_counter() - inicio) * 1000)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"[:200], round((time.perf_counter() - inicio) * 1000)


def _entrada(id_, nome, tipo, origem, usado_em, valor=None, erro=None, ms=0, estado=None, amostra="", lido_em="", detalhe=""):
    return {"id": id_, "nome": nome, "tipo": tipo, "origem": origem, "usado_em": usado_em,
            "estado": estado or ("falhou" if erro else "ok"), "ms": ms, "lido_em": lido_em,
            "amostra": amostra, "detalhe": detalhe or (erro or ""), "valor": valor}


# ------------------------------------------------------------------ APIs ao vivo

def checar_linhas() -> dict:
    valor, erro, ms = _medir(fontes.situacao_linhas)
    if erro or not valor or not valor.get("ok"):
        return _entrada("linhas", "Situação das linhas", "api", fontes.URL_LINHAS,
                        "Mapa, alertas, cartão de viagem e a ferramenta ver_linhas da Lia",
                        erro=erro or (valor or {}).get("aviso", "sem leitura"), ms=ms, estado="falhou")
    linhas = valor["linhas"]
    problema = [f"{n} {d.get('status', d.get('nivel'))}" for n, d in linhas.items() if d.get("nivel") in ("parada", "atencao")]
    return _entrada("linhas", "Situação das linhas", "api", fontes.URL_LINHAS,
                    "Mapa, alertas, cartão de viagem e a ferramenta ver_linhas da Lia", ms=ms,
                    lido_em=valor["lido_em"], estado="ok" if linhas else "vazio",
                    amostra=f"{len(linhas)} linhas; com problema agora: " + (", ".join(problema) if problema else "nenhuma"),
                    detalhe=valor.get("fonte", ""))


def checar_inmet() -> dict:
    valor, erro, ms = _medir(fontes.avisos_tempo)
    if erro or not valor or not valor.get("ok"):
        return _entrada("inmet", "Avisos do INMET", "api", fontes.URL_INMET, "Sinal de alerta e decisão do dia",
                        erro=erro or "sem leitura", ms=ms, estado="falhou")
    avisos = valor["avisos"]
    return _entrada("inmet", "Avisos do INMET", "api", fontes.URL_INMET, "Sinal de alerta e decisão do dia", ms=ms,
                    lido_em=valor["lido_em"], estado="ok" if avisos else "vazio",
                    amostra=(f"{len(avisos)} aviso(s) para São Paulo: " + "; ".join(f"{a['tipo']} ({a['severidade']}) até {a['fim']}" for a in avisos[:2]))
                    if avisos else "respondeu, sem aviso para São Paulo agora",
                    detalhe="o INMET só devolve aviso quando existe; vazio é resposta válida")


def checar_cge() -> dict:
    valor, erro, ms = _medir(fontes.alertas_cge)
    if erro or not valor or not valor.get("ok"):
        return _entrada("cge", "Alagamentos do CGE", "api", fontes.URL_CGE, "Mapa, sinal de alerta e a decisão do dia",
                        erro=erro or "sem leitura", ms=ms, estado="falhou")
    pontos, ativos = valor.get("pontos_hoje", []), valor.get("ativos")
    estado = valor.get("estado")
    return _entrada("cge", "Alagamentos do CGE", "api", fontes.URL_CGE, "Mapa, sinal de alerta e a decisão do dia", ms=ms,
                    lido_em=valor["lido_em"], estado="ok" if (pontos or ativos) else "vazio",
                    amostra=f"{len(pontos)} ponto(s) hoje, {ativos if ativos is not None else '?'} ativo(s); "
                            f"estado: {estado['titulo'] if estado else 'sem atenção nem alerta'}",
                    detalhe=valor.get("fonte", ""))


# ------------------------------------------------------------------ bases do repositório

def _json(caminho: Path):
    return json.loads(caminho.read_text(encoding="utf-8"))


def checar_rede() -> dict:
    valor, erro, ms = _medir(rede.carregar)
    if erro:
        return _entrada("rede", "Rede de trem e metrô (GTFS da SPTrans)", "base", "sistema/dados/rede.json",
                        "Caminho da viagem, mapa, lista de linhas e estações", erro=erro, ms=ms)
    meta = valor.get("meta", {})
    return _entrada("rede", "Rede de trem e metrô (GTFS da SPTrans)", "base", "sistema/dados/rede.json",
                    "Caminho da viagem, mapa, lista de linhas e estações", ms=ms, lido_em=str(meta.get("gerado_em", "")),
                    amostra=f"{len(valor['linhas'])} linhas, {len(valor['por_id'])} estações, {len(valor.get('trechos', []))} trechos",
                    detalhe=str(meta.get("fonte", "GTFS da SPTrans")))


def checar_seguranca() -> dict:
    valor, erro, ms = _medir(lambda: _json(DADOS / "seguranca_estacoes.json"))
    if erro:
        return _entrada("ssp", "Ocorrências da SSP-SP por estação", "base", "sistema/dados/seguranca_estacoes.json",
                        "Camada de segurança do mapa e detalhes do cartão de viagem", erro=erro, ms=ms)
    itens = valor.get("estacoes", valor) if isinstance(valor, dict) else valor
    lista = list(itens.values()) if isinstance(itens, dict) else itens
    maior = max(lista, key=lambda e: e.get("total", 0)) if lista else {}
    return _entrada("ssp", "Ocorrências da SSP-SP por estação", "base", "sistema/dados/seguranca_estacoes.json",
                    "Camada de segurança do mapa e detalhes do cartão de viagem", ms=ms,
                    amostra=f"{len(lista)} estações; mais registros: {maior.get('estacao', '?')} ({maior.get('total', '?')})",
                    detalhe="contagem de registros da SSP-SP num raio de 300 m, não é taxa de risco")


def checar_alagamentos_base() -> dict:
    valor, erro, ms = _medir(lambda: _json(DADOS / "alagamentos_geosampa.json"))
    if erro:
        return _entrada("geosampa", "Pontos de alagamento (GeoSampa)", "base", "sistema/dados/alagamentos_geosampa.json",
                        "Camada de alagamentos do mapa", erro=erro, ms=ms)
    pontos = valor.get("pontos", valor) if isinstance(valor, dict) else valor
    return _entrada("geosampa", "Pontos de alagamento (GeoSampa)", "base", "sistema/dados/alagamentos_geosampa.json",
                    "Camada de alagamentos do mapa", ms=ms, estado="ok" if pontos else "vazio",
                    amostra=f"{len(pontos)} pontos registrados pela Prefeitura",
                    detalhe=str((valor or {}).get("fonte", "GeoSampa, Prefeitura de São Paulo")) if isinstance(valor, dict) else "")


def checar_energia() -> dict:
    valor, erro, ms = _medir(lambda: _json(PESQUISA / "energia_modos.json"))
    if erro:
        return _entrada("energia", "Fatores de energia e CO₂ por modo", "base", "pesquisa/energia_modos.json",
                        "Comparação de energia da viagem (SERS)", erro=erro, ms=ms)
    itens = valor.get("itens", [])
    modos = sorted({i.get("modo", i.get("item", "?")) for i in itens if isinstance(i, dict)})
    return _entrada("energia", "Fatores de energia e CO₂ por modo", "base", "pesquisa/energia_modos.json",
                    "Comparação de energia da viagem (SERS)", ms=ms, estado="ok" if itens else "vazio",
                    amostra=f"{len(itens)} fatores, lidos em {valor.get('consultado_em', '?')}: " + ", ".join(modos[:5]),
                    detalhe="fatores do MCTI, Metrô, INMETRO e ANP, com unidade, ano e premissa")


def checar_base_mlam() -> dict:
    caminho = Path(__file__).resolve().parent.parent / "entregas" / "mlam" / "dados" / "ocorrencias_estacoes_2026.csv"
    valor, erro, ms = _medir(lambda: caminho.read_text(encoding="utf-8").splitlines())
    if erro:
        return _entrada("mlam", "Base da MLAM (SSP-SP 2026 por estação)", "base", "entregas/mlam/dados/ocorrencias_estacoes_2026.csv",
                        "Entrega da MLAM", erro=erro, ms=ms)
    return _entrada("mlam", "Base da MLAM (SSP-SP 2026 por estação)", "base", "entregas/mlam/dados/ocorrencias_estacoes_2026.csv",
                    "Entrega da MLAM", ms=ms,
                    amostra=f"{len(valor) - 1} estações, {len(valor[0].split(','))} colunas",
                    detalhe="base real da SSP-SP, janeiro a setembro de 2026")


# ------------------------------------------------------------------ banco e IA

def checar_banco() -> dict:
    """Fala com o Supabase de verdade: liga o repositório se o .env existir e só então lê."""
    from sistema import relatos
    if type(relatos.repo).__name__ != "RepositorioSupabase":
        banco.carregar_env()
        cred = banco.credenciais()
        if cred:
            from sistema.relatos_supabase import RepositorioSupabase
            relatos.usar_repositorio(RepositorioSupabase(*cred))
    tipo_repo = type(relatos.repo).__name__
    if tipo_repo != "RepositorioSupabase":
        return _entrada("banco", "Banco dos relatos (Supabase)", "banco", "esquema datempo", "Feed, mapa e a ferramenta de relatos da Lia",
                        estado="vazio", amostra="os relatos estão em memória (sem .env do Supabase)",
                        detalhe="com SUPABASE_URL e SUPABASE_SECRET_KEY no .env, o feed passa a gravar no banco")
    valor, erro, ms = _medir(lambda: relatos.listar_ativos())
    if erro:
        return _entrada("banco", "Banco dos relatos (Supabase)", "banco", f"{banco.ESQUEMA} em {(banco.credenciais() or ('', ''))[0]}",
                        "Feed, mapa e a ferramenta de relatos da Lia", erro=erro, ms=ms)
    demo = sum(1 for r in valor if r.demo)
    return _entrada("banco", "Banco dos relatos (Supabase)", "banco", f"esquema {banco.ESQUEMA}",
                    "Feed, mapa e a ferramenta de relatos da Lia", ms=ms, estado="ok" if valor else "vazio",
                    amostra=f"{len(valor)} relatos ativos ({demo} de demonstração)",
                    detalhe="só o servidor acessa, com a chave secreta do .env")


def checar_ia() -> dict:
    """Só diz se há provedor e modelo configurados. A chave nunca sai daqui."""
    from sistema import config
    cfg, erro, ms = _medir(config.ler)
    if erro:
        return _entrada("ia", "Modelo de linguagem da Lia", "api", "", "Conversa da Lia", erro=erro, ms=ms)
    cfg = cfg or {}
    ligada = cfg.get("provedor", "nenhum") != "nenhum" and bool(cfg.get("modelo"))
    return _entrada("ia", "Modelo de linguagem da Lia", "api", str(cfg.get("base_url", "")), "Conversa da Lia",
                    ms=ms, estado="ok" if ligada else "vazio",
                    amostra=f"{cfg.get('provedor')} / {cfg.get('modelo')}, com chave" if ligada and cfg.get("chave")
                            else f"{cfg.get('provedor')} / {cfg.get('modelo')}, sem chave" if ligada
                            else "desligada em Configurações de IA",
                    detalhe="sem IA a Lia responde pelas regras e pela base; a chave fica fora do repositório")


CHECAGENS = (checar_linhas, checar_inmet, checar_cge, checar_rede, checar_seguranca,
             checar_alagamentos_base, checar_energia, checar_base_mlam, checar_banco, checar_ia)


def checar_tudo() -> dict:
    fontes_ = []
    for checagem in CHECAGENS:
        try:
            fontes_.append(checagem())
        except Exception as e:           # uma fonte quebrada não derruba o relatório
            fontes_.append(_entrada(checagem.__name__, checagem.__name__, "api", "", "", erro=f"{type(e).__name__}: {e}"))
    for f in fontes_:
        f.pop("valor", None)
    contagem = {e: sum(1 for f in fontes_ if f["estado"] == e) for e in ("ok", "vazio", "falhou")}
    return {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "resumo": contagem | {"total": len(fontes_)}, "fontes": fontes_,
            "aviso": "\"vazio\" é resposta válida: a fonte respondeu e não há nada para mostrar agora."}


if __name__ == "__main__":
    r = checar_tudo()
    marca = {"ok": "[ok]    ", "vazio": "[vazio] ", "falhou": "[FALHOU]"}
    print(f"Fontes de dados: {r['gerado_em']}")
    print(f"ok: {r['resumo']['ok']} | vazio: {r['resumo']['vazio']} | falhou: {r['resumo']['falhou']}\n")
    for f in r["fontes"]:
        print(f"{marca[f['estado']]} {f['nome']}  ({f['tipo']}, {f['ms']} ms)")
        print(f"         {f['amostra']}")
        if f["origem"]:
            print(f"         origem: {f['origem']}")
        if f["detalhe"]:
            print(f"         nota: {f['detalhe']}")
        print(f"         usado em: {f['usado_em']}\n")
