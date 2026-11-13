import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  ArrowLeft, Check, CircleCheck, CloudRain, Flag, FlaskConical, MapPin, Megaphone, OctagonX, RefreshCw, ShieldAlert,
  ThumbsUp, UserRound, UsersRound, Waves, Wrench, X,
} from "lucide-react";

import { SeloLinha } from "../componentes/Linha";
import { mobilidade, type EstacaoEscolha, type LinhaInfo } from "../lib/api";

/* ------------------------------------------------------------------ tipos de dado */

type TipoCodigo = "lotado" | "parado" | "quebrou" | "chuva" | "alagado" | "seguranca" | "normal";
type Voto = "ainda" | "acabou";
type Relato = {
  id: string; linha: string; tipo: TipoCodigo; estacao_id: string | null; estacao_nome?: string; ha_min: number; apelido: string;
  meu: boolean; meu_voto: Voto | null; confirmacoes: number; contestacoes: number; demo: boolean;
};
type LinhaEstimada = { linha: string; nivel: "alerta" | "relato" | "normal"; tipo_principal: TipoCodigo; n_relatos: number; n_autores: number; ultimo_em: string };
type Aviso = { texto: string; erro: boolean };

const AVISO_FIXO = "Estimativa por relatos de passageiros, não dado oficial.";
const CHAVE_LINHAS = "dt-minhas-linhas";
const CHAVE_APARELHO = "dt-device-id";
const ATUALIZA_A_CADA_MS = 5000;
const COR_SEM_DADO = "#888888";

/** O que a pessoa pode ver. Sempre ícone + palavra, e a cor só reforça. */
const TIPOS: { codigo: TipoCodigo; rotulo: string; Icone: typeof UsersRound; classe: string }[] = [
  { codigo: "lotado", rotulo: "Lotado", Icone: UsersRound, classe: "bg-alerta-suave text-alerta" },
  { codigo: "parado", rotulo: "Parado", Icone: OctagonX, classe: "bg-erro-suave text-erro" },
  { codigo: "quebrou", rotulo: "Quebrou", Icone: Wrench, classe: "bg-erro-suave text-erro" },
  { codigo: "chuva", rotulo: "Chuva", Icone: CloudRain, classe: "bg-alerta-suave text-alerta" },
  { codigo: "alagado", rotulo: "Alagamento", Icone: Waves, classe: "bg-erro-suave text-erro" },
  { codigo: "seguranca", rotulo: "Segurança", Icone: ShieldAlert, classe: "bg-erro-suave text-erro" },
  { codigo: "normal", rotulo: "Tudo certo", Icone: CircleCheck, classe: "bg-ok-suave text-ok" },
];
const TIPO_POR_CODIGO = Object.fromEntries(TIPOS.map((t) => [t.codigo, t])) as Record<TipoCodigo, (typeof TIPOS)[number]>;

/* ------------------------------------------------------------------ id do aparelho e acesso à API */

let idEmMemoria: string | null = null;

function novoId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return crypto.randomUUID();
    if (typeof crypto !== "undefined" && typeof crypto.getRandomValues === "function") {
      return Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
    }
  } catch {
    /* cai no sorteio simples */
  }
  return Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
}

/** Gera na primeira vez e guarda. Se o navegador bloquear o armazenamento, vale o da memória (até recarregar). */
function idDoAparelho(): string {
  if (idEmMemoria) return idEmMemoria;
  try {
    const guardado = localStorage.getItem(CHAVE_APARELHO);
    if (guardado) return (idEmMemoria = guardado);
  } catch {
    /* sem armazenamento */
  }
  const novo = novoId();
  try {
    localStorage.setItem(CHAVE_APARELHO, novo);
  } catch {
    /* fica só na memória */
  }
  return (idEmMemoria = novo);
}

class ErroApi extends Error {
  status: number;
  constructor(mensagem: string, status: number) {
    super(mensagem);
    this.status = status;
  }
}

async function chamar<T>(caminho: string, opcoes: { metodo?: "GET" | "POST"; corpo?: unknown } = {}): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(caminho, {
      method: opcoes.metodo ?? "GET",
      headers: { "Content-Type": "application/json", "X-Device-Id": idDoAparelho() },
      body: opcoes.corpo === undefined ? undefined : JSON.stringify(opcoes.corpo),
    });
  } catch {
    throw new ErroApi("Sem conexão com o servidor.", 0);
  }
  if (!resposta.ok) {
    let detalhe = "";
    try {
      const d = (await resposta.json()).detail;
      if (typeof d === "string") detalhe = d;
    } catch {
      /* resposta sem corpo */
    }
    throw new ErroApi(detalhe || `O servidor respondeu com erro ${resposta.status}.`, resposta.status);
  }
  return resposta.json() as Promise<T>;
}

const mensagemDe = (e: unknown) => (e instanceof Error ? e.message : "Algo deu errado.");

function lerMinhasLinhas(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(CHAVE_LINHAS) ?? "[]");
    return Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
  } catch {
    return [];
  }
}

function haTempo(min: number): string {
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  const h = Math.floor(min / 60);
  const resto = min % 60;
  return resto ? `há ${h} h ${resto} min` : `há ${h} h`;
}

/* ------------------------------------------------------------------ linhas e estações */

function useRede() {
  const [linhas, setLinhas] = useState<LinhaInfo[]>([]);
  const [estacoes, setEstacoes] = useState<EstacaoEscolha[]>([]);
  const [erro, setErro] = useState(false);
  const carregar = useCallback(() => {
    mobilidade.estacoes().then(
      (d) => { setLinhas(d.linhas); setEstacoes(d.estacoes); setErro(false); },
      () => setErro(true),
    );
  }, []);
  useEffect(carregar, [carregar]);
  return { linhas, estacoes, erro, carregar };
}

function Tipo({ codigo, pequeno }: { codigo: TipoCodigo; pequeno?: boolean }) {
  const t = TIPO_POR_CODIGO[codigo] ?? TIPO_POR_CODIGO.normal;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold ${t.classe} ${pequeno ? "px-2.5 py-0.5 text-[13px]" : "px-3 py-1 text-sm"}`}>
      <t.Icone className="size-4 shrink-0" aria-hidden />
      {t.rotulo}
    </span>
  );
}

/** Grade de selos para escolher linhas. `marcadas` deixa escolher várias; sem ela, um toque escolhe. */
function GradeDeLinhas({ linhas, marcadas, onEscolher }: { linhas: LinhaInfo[]; marcadas?: string[]; onEscolher: (numero: string) => void }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(4.25rem,1fr))] gap-2">
      {linhas.map((l) => {
        const ligada = marcadas?.includes(l.numero) ?? false;
        return (
          <button
            key={l.numero}
            type="button"
            onClick={() => onEscolher(l.numero)}
            aria-pressed={marcadas ? ligada : undefined}
            aria-label={`Linha ${l.numero} ${l.nome}`}
            className={`relative flex min-h-[4.25rem] flex-col items-center justify-center gap-1 rounded-xl border px-1 py-1.5 ${
              ligada ? "border-marca bg-marca-suave ring-2 ring-marca" : "border-linha bg-superficie hover:bg-fundo"
            }`}
          >
            <SeloLinha numero={l.numero} cor={l.cor} tamanho="lg" />
            <span className="max-w-full truncate text-xs text-apagado">{l.nome}</span>
            {ligada && (
              <span className="absolute -top-1.5 -right-1.5 flex size-5 items-center justify-center rounded-full bg-marca text-superficie">
                <Check className="size-3.5" aria-hidden />
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

/* ------------------------------------------------------------------ folha de "Relatar" */

const FOCAVEIS = 'button:not(:disabled), select:not(:disabled), [href], [tabindex]:not([tabindex="-1"])';

function Folha({ linhas, estacoes, erroLinhas, recarregarLinhas, onFechar, onEnviado }: {
  linhas: LinhaInfo[]; estacoes: EstacaoEscolha[]; erroLinhas: boolean; recarregarLinhas: () => void;
  onFechar: () => void; onEnviado: () => void;
}) {
  const [linha, setLinha] = useState<string | null>(null);
  const [estacaoId, setEstacaoId] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const painel = useRef<HTMLDivElement>(null);
  const fechar = useRef(onFechar);
  fechar.current = onFechar;

  // foco entra na folha, Esc fecha, Tab não escapa, e o foco volta para o botão que abriu
  useEffect(() => {
    const anterior = document.activeElement as HTMLElement | null;
    painel.current?.focus();
    const tecla = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        fechar.current();
      } else if (e.key === "Tab" && painel.current) {
        const itens = Array.from(painel.current.querySelectorAll<HTMLElement>(FOCAVEIS));
        if (!itens.length) return;
        const primeiro = itens[0];
        const ultimo = itens[itens.length - 1];
        if (e.shiftKey && (document.activeElement === primeiro || document.activeElement === painel.current)) {
          e.preventDefault();
          ultimo.focus();
        } else if (!e.shiftKey && document.activeElement === ultimo) {
          e.preventDefault();
          primeiro.focus();
        }
      }
    };
    window.addEventListener("keydown", tecla);
    return () => {
      window.removeEventListener("keydown", tecla);
      anterior?.focus?.();
    };
  }, []);

  useEffect(() => {
    if (!enviado) return;
    const t = window.setTimeout(() => fechar.current(), 1600);
    return () => window.clearTimeout(t);
  }, [enviado]);

  const info = linhas.find((l) => l.numero === linha);
  const daLinha = useMemo(() => (linha ? estacoes.filter((e) => e.linhas.includes(linha)) : []), [estacoes, linha]);

  async function enviar(tipo: TipoCodigo) {
    if (!linha || enviando) return;
    setEnviando(true);
    setErro(null);
    try {
      await chamar("/api/relatos", { metodo: "POST", corpo: { linha, tipo, estacao_id: estacaoId || null } });
      setEnviado(true);
      onEnviado();
    } catch (e) {
      setErro(mensagemDe(e));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="absolute inset-0 z-30 flex items-end justify-center @md:items-center">
      <div className="absolute inset-0 bg-tinta/40" onClick={onFechar} aria-hidden />
      <div
        ref={painel}
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-folha"
        tabIndex={-1}
        className="relative max-h-[92%] w-full overflow-y-auto rounded-t-2xl bg-superficie p-4 shadow-xl outline-none @md:max-w-md @md:rounded-2xl"
      >
        <div className="mb-3 flex items-center gap-2">
          {linha && !enviado && (
            <button type="button" onClick={() => { setLinha(null); setErro(null); setEstacaoId(""); }}
              className="-ml-2 inline-flex min-h-11 items-center gap-1 rounded-lg px-2 text-sm font-semibold text-marca-forte">
              <ArrowLeft className="size-4" aria-hidden />
              Trocar linha
            </button>
          )}
          <h2 id="titulo-folha" className="flex-1 text-lg font-bold">
            {enviado ? "Relato enviado" : linha ? "O que você está vendo?" : "Em qual linha você está?"}
          </h2>
          <button type="button" onClick={onFechar} aria-label="Fechar"
            className="-mr-2 inline-flex size-11 items-center justify-center rounded-lg text-apagado hover:bg-fundo">
            <X className="size-5" aria-hidden />
          </button>
        </div>

        {enviado ? (
          <div role="status" className="flex flex-col items-center gap-2 py-6 text-center">
            <CircleCheck className="size-10 text-ok" aria-hidden />
            <p className="text-base font-semibold">Obrigado! Seu relato já está no feed.</p>
            <p className="text-sm text-apagado">Ele fica visível por 2 horas.</p>
            <button type="button" onClick={onFechar}
              className="mt-2 min-h-11 rounded-xl bg-marca px-5 font-semibold text-superficie hover:bg-marca-forte">
              Fechar
            </button>
          </div>
        ) : !linha ? (
          erroLinhas ? (
            <div role="alert" className="rounded-xl bg-erro-suave p-3 text-sm text-erro">
              Não foi possível carregar as linhas.
              <button type="button" onClick={recarregarLinhas} className="ml-2 min-h-11 font-semibold underline">Tentar de novo</button>
            </div>
          ) : linhas.length === 0 ? (
            <p role="status" className="py-6 text-center text-apagado">Carregando linhas…</p>
          ) : (
            <GradeDeLinhas linhas={linhas} onEscolher={setLinha} />
          )
        ) : (
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2 text-sm text-apagado">
              {info && <SeloLinha numero={info.numero} cor={info.cor} tamanho="sm" />}
              <span>Linha {linha}{info ? ` ${info.nome}` : ""}</span>
            </div>

            <div>
              <label htmlFor="estacao-relato" className="mb-1 block text-sm font-semibold">Estação (opcional)</label>
              <select id="estacao-relato" value={estacaoId} onChange={(e) => setEstacaoId(e.target.value)}
                className="min-h-11 w-full rounded-xl border border-linha bg-superficie px-3 text-base">
                <option value="">Não informar</option>
                {daLinha.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
              </select>
            </div>

            <div>
              <p className="mb-2 text-sm font-semibold">Toque no que está vendo para enviar</p>
              <div className="grid grid-cols-2 gap-2">
                {TIPOS.map((t) => (
                  <button key={t.codigo} type="button" disabled={enviando} onClick={() => enviar(t.codigo)}
                    className="flex min-h-16 items-center gap-3 rounded-xl border border-linha bg-superficie px-3 py-2 text-left text-base font-semibold hover:bg-fundo disabled:opacity-60">
                    <span className={`flex size-10 shrink-0 items-center justify-center rounded-lg ${t.classe}`}>
                      <t.Icone className="size-5" aria-hidden />
                    </span>
                    {t.rotulo}
                  </button>
                ))}
              </div>
            </div>

            {erro && <p role="alert" className="rounded-xl bg-erro-suave p-3 text-sm font-medium text-erro">{erro}</p>}
            <p className="text-xs text-apagado">Sem texto livre e sem foto: só o que está na lista. {AVISO_FIXO}</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ cartão de um relato */

function Cartao({ r, cor, ocupado, onVotar, onSinalizar }: {
  r: Relato; cor: string; ocupado: boolean; onVotar: (r: Relato, v: Voto) => void; onSinalizar: (r: Relato) => void;
}) {
  const [confirmando, setConfirmando] = useState(false);
  const votou = r.meu_voto !== null;
  const botao = (v: Voto, texto: string, n: number, Icone: typeof ThumbsUp) => {
    const escolhido = r.meu_voto === v;
    return (
      <button type="button" onClick={() => onVotar(r, v)} disabled={r.meu || votou || ocupado} aria-pressed={r.meu ? undefined : escolhido}
        className={`inline-flex min-h-11 items-center gap-1.5 rounded-xl border px-3 text-sm font-semibold disabled:cursor-default ${
          escolhido ? "border-marca bg-marca-suave text-marca-forte" : "border-linha bg-superficie hover:bg-fundo disabled:text-apagado disabled:hover:bg-superficie"
        }`}>
        {escolhido ? <Check className="size-4" aria-hidden /> : <Icone className="size-4" aria-hidden />}
        {texto} ({n})
      </button>
    );
  };

  return (
    <li className="rounded-xl border border-linha bg-superficie p-3">
      <div className="flex flex-wrap items-center gap-2">
        <SeloLinha numero={r.linha} cor={cor} />
        <Tipo codigo={r.tipo} />
        <span className="ml-auto text-sm text-apagado">{haTempo(r.ha_min)}</span>
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-apagado">
        {r.estacao_nome && (
          <span className="inline-flex items-center gap-1 font-medium text-tinta">
            <MapPin className="size-4 shrink-0" aria-hidden />
            {r.estacao_nome}
          </span>
        )}
        <span className="inline-flex items-center gap-1">
          <UserRound className="size-4 shrink-0" aria-hidden />
          {r.apelido}{r.meu ? " (você)" : ""}
        </span>
        {r.demo && (
          <span className="inline-flex items-center gap-1 rounded-full bg-fundo px-2 py-0.5 text-xs font-semibold ring-1 ring-linha ring-inset">
            <FlaskConical className="size-3.5" aria-hidden />
            demonstração
          </span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {botao("ainda", "Ainda está assim", r.confirmacoes, ThumbsUp)}
        {botao("acabou", "Já acabou", r.contestacoes, Check)}
        {confirmando ? (
          <span className="ml-auto inline-flex items-center gap-1 text-sm">
            <span className="text-apagado">Sinalizar?</span>
            <button type="button" onClick={() => { setConfirmando(false); onSinalizar(r); }}
              className="min-h-11 rounded-lg px-3 font-semibold text-erro hover:bg-erro-suave">Sim</button>
            <button type="button" onClick={() => setConfirmando(false)}
              className="min-h-11 rounded-lg px-3 font-semibold text-apagado hover:bg-fundo">Não</button>
          </span>
        ) : (
          <button type="button" onClick={() => setConfirmando(true)} disabled={r.meu}
            aria-label="Sinalizar este relato como inadequado ou falso"
            className="ml-auto inline-flex min-h-11 items-center gap-1 rounded-lg px-3 text-sm text-apagado hover:bg-fundo disabled:invisible">
            <Flag className="size-3.5" aria-hidden />
            Sinalizar
          </button>
        )}
      </div>
    </li>
  );
}

/* ------------------------------------------------------------------ a aba */

function Painel({ children, alerta }: { children: ReactNode; alerta?: boolean }) {
  return <div role={alerta ? "alert" : "status"} className="rounded-xl border border-linha bg-superficie p-6 text-center">{children}</div>;
}

export default function Feed() {
  const { linhas, estacoes, erro: erroLinhas, carregar: recarregarLinhas } = useRede();
  const [relatos, setRelatos] = useState<Relato[] | null>(null);
  const [estimativa, setEstimativa] = useState<LinhaEstimada[]>([]);
  const [erro, setErro] = useState<string | null>(null);
  const [filtro, setFiltro] = useState<"todas" | "minhas">("todas");
  const [minhas, setMinhas] = useState<string[]>(lerMinhasLinhas);
  const [escolhendo, setEscolhendo] = useState(false);
  const [folha, setFolha] = useState(false);
  const [aviso, setAviso] = useState<Aviso | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const seq = useRef(0);
  const temporizadorAviso = useRef<number | undefined>(undefined);

  const corDa = useCallback((numero: string) => linhas.find((l) => l.numero === numero)?.cor ?? COR_SEM_DADO, [linhas]);

  const atualizar = useCallback(async () => {
    const minha = ++seq.current;
    try {
      const [lista, est] = await Promise.all([
        chamar<{ relatos: Relato[] }>("/api/relatos"),
        chamar<{ linhas: LinhaEstimada[] }>("/api/relatos/estimativa"),
      ]);
      if (minha !== seq.current) return;           // chegou uma resposta mais nova enquanto esta voltava
      setRelatos(lista.relatos);
      setEstimativa(est.linhas);
      setErro(null);
    } catch (e) {
      if (minha === seq.current) setErro(mensagemDe(e));
    }
  }, []);

  // tempo real: a cada 5 s e quando a janela volta a ter foco
  useEffect(() => {
    atualizar();
    const ciclo = window.setInterval(() => { if (!document.hidden) atualizar(); }, ATUALIZA_A_CADA_MS);
    const voltou = () => { if (!document.hidden) atualizar(); };
    window.addEventListener("focus", voltou);
    document.addEventListener("visibilitychange", voltou);
    return () => {
      window.clearInterval(ciclo);
      window.removeEventListener("focus", voltou);
      document.removeEventListener("visibilitychange", voltou);
      window.clearTimeout(temporizadorAviso.current);
    };
  }, [atualizar]);

  function avisar(texto: string, comErro = false) {
    window.clearTimeout(temporizadorAviso.current);
    setAviso({ texto, erro: comErro });
    temporizadorAviso.current = window.setTimeout(() => setAviso(null), 4000);
  }

  function alternarLinha(numero: string) {
    setMinhas((atual) => {
      const novo = atual.includes(numero) ? atual.filter((n) => n !== numero) : [...atual, numero];
      try {
        localStorage.setItem(CHAVE_LINHAS, JSON.stringify(novo));
      } catch {
        /* sem armazenamento: vale só nesta sessão */
      }
      return novo;
    });
  }

  function escolherFiltro(f: "todas" | "minhas") {
    setFiltro(f);
    setEscolhendo(f === "minhas" && minhas.length === 0);
  }

  async function votar(r: Relato, valor: Voto) {
    setOcupado(true);
    try {
      await chamar(`/api/relatos/${r.id}/confirmar`, { metodo: "POST", corpo: { valor } });
      avisar(valor === "ainda" ? "Obrigado. Registramos que ainda está assim." : "Obrigado. Registramos que já acabou.");
    } catch (e) {
      avisar(mensagemDe(e), true);
    } finally {
      setOcupado(false);
      atualizar();
    }
  }

  async function sinalizar(r: Relato) {
    try {
      await chamar(`/api/relatos/${r.id}/sinalizar`, { metodo: "POST" });
      avisar("Relato sinalizado. Com 3 sinalizações ele sai do feed.");
    } catch (e) {
      avisar(mensagemDe(e), true);
    } finally {
      atualizar();
    }
  }

  const alertas = useMemo(() => estimativa.filter((e) => e.nivel === "alerta").slice(0, 3), [estimativa]);
  const visiveis = useMemo(() => {
    if (!relatos) return [];
    return filtro === "minhas" ? relatos.filter((r) => minhas.includes(r.linha)) : relatos;
  }, [relatos, filtro, minhas]);

  return (
    <div className="@container relative flex h-full flex-col bg-fundo text-tinta">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 px-4 pt-4 pb-[72px]">
          {/* 1. Agora nas linhas */}
          <section aria-labelledby="titulo-agora" className="rounded-xl border border-linha bg-superficie p-4">
            <h2 id="titulo-agora" className="text-lg font-bold">Agora nas linhas</h2>
            {alertas.length ? (
              <ul className="mt-2 grid gap-2 @md:grid-cols-2">
                {alertas.map((a) => (
                  <li key={a.linha} className="flex flex-wrap items-center gap-2 rounded-lg bg-fundo p-2">
                    <SeloLinha numero={a.linha} cor={corDa(a.linha)} />
                    <Tipo codigo={a.tipo_principal} pequeno />
                    <span className="text-sm text-apagado">{a.n_autores} pessoas relataram</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-1 inline-flex items-center gap-1.5 text-sm text-apagado">
                <UsersRound className="size-4" aria-hidden />
                Nenhum alerta dos passageiros agora
              </p>
            )}
            <p className="mt-2 text-xs text-apagado">{AVISO_FIXO}</p>
          </section>

          {/* 2. Filtro */}
          <div>
            <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Filtro do feed">
              {([["todas", "Todas"], ["minhas", "Minhas linhas"]] as const).map(([valor, rotulo]) => (
                <button key={valor} type="button" aria-pressed={filtro === valor} onClick={() => escolherFiltro(valor)}
                  className={`inline-flex min-h-11 items-center gap-1.5 rounded-full border px-4 text-sm font-semibold ${
                    filtro === valor ? "border-marca bg-marca text-superficie" : "border-linha bg-superficie hover:bg-fundo"
                  }`}>
                  {filtro === valor && <Check className="size-4" aria-hidden />}
                  {rotulo}
                </button>
              ))}
              {filtro === "minhas" && (
                <button type="button" onClick={() => setEscolhendo((v) => !v)} aria-expanded={escolhendo}
                  className="min-h-11 rounded-lg px-2 text-sm font-semibold text-marca-forte underline">
                  {escolhendo ? "Pronto" : minhas.length ? `Editar linhas (${minhas.length})` : "Escolher linhas"}
                </button>
              )}
            </div>
            {filtro === "minhas" && escolhendo && (
              <div className="mt-3 rounded-xl border border-linha bg-superficie p-3">
                <p className="mb-2 text-sm font-semibold">Marque as linhas que você usa</p>
                {erroLinhas ? (
                  <p role="alert" className="text-sm text-erro">
                    Não foi possível carregar as linhas.
                    <button type="button" onClick={recarregarLinhas} className="ml-2 min-h-11 font-semibold underline">Tentar de novo</button>
                  </p>
                ) : linhas.length === 0 ? (
                  <p role="status" className="text-sm text-apagado">Carregando linhas…</p>
                ) : (
                  <GradeDeLinhas linhas={linhas} marcadas={minhas} onEscolher={alternarLinha} />
                )}
              </div>
            )}
          </div>

          {/* 4/7. Lista e estados */}
          {erro && relatos === null ? (
            <Painel alerta>
              <p className="font-semibold text-erro">Não foi possível carregar os relatos.</p>
              <p className="mt-1 text-sm text-apagado">{erro}</p>
              <button type="button" onClick={atualizar}
                className="mt-3 inline-flex min-h-11 items-center gap-2 rounded-xl bg-marca px-5 font-semibold text-superficie hover:bg-marca-forte">
                <RefreshCw className="size-4" aria-hidden />
                Tentar de novo
              </button>
            </Painel>
          ) : relatos === null ? (
            <Painel><p className="text-apagado">Carregando relatos…</p></Painel>
          ) : (
            <>
              {erro && (
                <p role="alert" className="flex flex-wrap items-center gap-2 rounded-xl bg-alerta-suave p-3 text-sm font-medium text-alerta">
                  Sem atualização do servidor. Mostrando o que já chegou.
                  <button type="button" onClick={atualizar} className="min-h-11 font-semibold underline">Tentar de novo</button>
                </p>
              )}
              {relatos.length === 0 ? (
                <Painel><p className="text-base font-semibold">Ninguém relatou nada ainda. Seja o primeiro.</p></Painel>
              ) : filtro === "minhas" && minhas.length === 0 ? (
                <Painel><p className="text-apagado">Escolha ao menos uma linha para ver só os relatos dela.</p></Painel>
              ) : visiveis.length === 0 ? (
                <Painel><p className="text-apagado">Nenhum relato nas suas linhas agora.</p></Painel>
              ) : (
                <ul className="grid gap-3 @md:grid-cols-2">
                  {visiveis.map((r) => (
                    <Cartao key={r.id} r={r} cor={corDa(r.linha)} ocupado={ocupado} onVotar={votar} onSinalizar={sinalizar} />
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      </div>

      {/* 3. Botão Relatar, fixo no fim da aba (a barra de abas fica abaixo desta área) */}
      <div className="pointer-events-none absolute inset-x-0 bottom-2 z-10 flex flex-col items-center gap-2 px-4">
        {aviso && (
          <p role="status" className={`pointer-events-auto max-w-full rounded-xl px-4 py-2 text-sm font-medium shadow-md ${aviso.erro ? "bg-erro-suave text-erro" : "bg-tinta text-superficie"}`}>
            {aviso.texto}
          </p>
        )}
        <button type="button" onClick={() => setFolha(true)}
          className="pointer-events-auto inline-flex h-14 w-full items-center justify-center gap-2 rounded-2xl bg-marca px-6 text-lg font-bold text-superficie shadow-lg hover:bg-marca-forte @md:w-auto @md:min-w-64">
          <Megaphone className="size-5" aria-hidden />
          Relatar
        </button>
      </div>

      {folha && (
        <Folha linhas={linhas} estacoes={estacoes} erroLinhas={erroLinhas} recarregarLinhas={recarregarLinhas}
          onFechar={() => setFolha(false)} onEnviado={atualizar} />
      )}
    </div>
  );
}
