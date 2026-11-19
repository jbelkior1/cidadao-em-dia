import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  ArrowLeft, Camera, Check, CircleCheck, CloudRain, Flag, FlaskConical, Map as MapaIcone, Megaphone, OctagonX, Plus, RefreshCw, Search,
  ShieldAlert, Siren, ThumbsUp, TrainFront, UsersRound, Waves, Wrench, X,
} from "lucide-react";

import type { IdAba } from "../componentes/AppAbas";
import { Avatar } from "../componentes/Auxilia";
import { SeloLinha } from "../componentes/Linha";
import { useConversa } from "../componentes/conversa";
import { mobilidade, type EstacaoEscolha, type LinhaInfo } from "../lib/api";

/* ------------------------------------------------------------------ tipos de dado */

type TipoCodigo = "lotado" | "parado" | "quebrou" | "chuva" | "alagado" | "seguranca" | "normal";
type Voto = "ainda" | "acabou";
type Relato = {
  id: string; linha: string; tipo: TipoCodigo; estacao_id: string | null; estacao_nome?: string; ha_min: number; apelido: string;
  meu: boolean; meu_voto: Voto | null; confirmacoes: number; contestacoes: number; demo: boolean; descricao: string;
  tem_foto: boolean; foto_url: string | null;
};
type LinhaEstimada = { linha: string; nivel: "alerta" | "relato" | "normal"; tipo_principal: TipoCodigo; n_relatos: number; n_autores: number; ultimo_em: string };
type Aviso = { texto: string; erro: boolean };

const AVISO_FIXO = "Estimativa por relatos de passageiros, não dado oficial.";
const LIMITE_DESCRICAO = 140;
const LADO_FOTO = 1280;        // px do lado maior: o celular reduz antes de enviar (o servidor confere de novo)

/** Abre a imagem escolhida, reduz e devolve um JPEG em base64 (data URL). O JPEG novo não leva os metadados do original. */
async function prepararFoto(arquivo: File): Promise<string> {
  if (!arquivo.type.startsWith("image/")) throw new Error("Escolha um arquivo de imagem.");
  const endereco = URL.createObjectURL(arquivo);
  try {
    const imagem = await new Promise<HTMLImageElement>((ok, falha) => {
      const i = new Image();
      i.onload = () => ok(i);
      i.onerror = () => falha(new Error("Não consegui abrir essa foto. Tente tirar de novo."));
      i.src = endereco;
    });
    const escala = Math.min(1, LADO_FOTO / Math.max(imagem.naturalWidth, imagem.naturalHeight));
    const tela = document.createElement("canvas");
    tela.width = Math.max(1, Math.round(imagem.naturalWidth * escala));
    tela.height = Math.max(1, Math.round(imagem.naturalHeight * escala));
    const contexto = tela.getContext("2d");
    if (!contexto) throw new Error("Este aparelho não conseguiu preparar a foto.");
    contexto.drawImage(imagem, 0, 0, tela.width, tela.height);
    return tela.toDataURL("image/jpeg", 0.8);
  } finally {
    URL.revokeObjectURL(endereco);
  }
}
const CHAVE_LINHAS = "dt-minhas-linhas";
const CHAVE_APARELHO = "dt-device-id";
const ATUALIZA_A_CADA_MS = 5000;
const COR_SEM_DADO = "#888888";

/** O que a pessoa pode ver. Sempre ícone + palavra, e a cor só reforça. */
const TIPOS: { codigo: TipoCodigo; rotulo: string; Icone: typeof UsersRound; classe: string; cor: string }[] = [
  { codigo: "lotado", rotulo: "Lotado", Icone: UsersRound, classe: "bg-alerta-suave text-alerta", cor: "text-alerta" },
  { codigo: "parado", rotulo: "Parado", Icone: OctagonX, classe: "bg-erro-suave text-erro", cor: "text-erro" },
  { codigo: "quebrou", rotulo: "Quebrou", Icone: Wrench, classe: "bg-erro-suave text-erro", cor: "text-erro" },
  { codigo: "chuva", rotulo: "Chuva", Icone: CloudRain, classe: "bg-alerta-suave text-alerta", cor: "text-alerta" },
  { codigo: "alagado", rotulo: "Alagamento", Icone: Waves, classe: "bg-erro-suave text-erro", cor: "text-erro" },
  { codigo: "seguranca", rotulo: "Segurança", Icone: ShieldAlert, classe: "bg-erro-suave text-erro", cor: "text-erro" },
  { codigo: "normal", rotulo: "Tudo certo", Icone: CircleCheck, classe: "bg-ok-suave text-ok", cor: "text-ok" },
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

/** Esquece o código do aparelho (em memória e no armazenamento): o próximo relato gera outro. */
export function esquecerIdDoAparelho(): void {
  idEmMemoria = null;
  try {
    localStorage.removeItem(CHAVE_APARELHO);
  } catch {
    /* sem armazenamento */
  }
}

/** Gera na primeira vez e guarda. Se o navegador bloquear o armazenamento, vale o da memória (até recarregar). */
export function idDoAparelho(): string {
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
    <span className={`inline-flex items-center gap-1.5 rounded-full font-bold ${t.classe} ${pequeno ? "px-2.5 py-0.5 text-[12px]" : "px-3 py-1 text-[13px]"}`}>
      <t.Icone className="size-3.5 shrink-0" aria-hidden />
      {t.rotulo}
    </span>
  );
}

/** Grade de selos para escolher linhas. `marcadas` deixa escolher várias; sem ela, um toque escolhe. */
function GradeDeLinhas({ linhas, marcadas, onEscolher }: { linhas: LinhaInfo[]; marcadas?: string[]; onEscolher: (numero: string) => void }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(4.5rem,1fr))] gap-2">
      {linhas.map((l) => {
        const ligada = marcadas?.includes(l.numero) ?? false;
        return (
          <button
            key={l.numero}
            type="button"
            onClick={() => onEscolher(l.numero)}
            aria-pressed={marcadas ? ligada : undefined}
            aria-label={`Linha ${l.numero} ${l.nome}`}
            className={`relative flex min-h-[4.75rem] flex-col items-center justify-center gap-1.5 rounded-2xl px-1 py-2 ${
              ligada ? "bg-superficie ring-2 ring-tinta" : "bg-cinza hover:bg-cinza-forte"
            }`}
          >
            <SeloLinha numero={l.numero} cor={l.cor} tamanho="lg" />
            <span className="max-w-full truncate text-[12px] font-medium text-apagado">{l.nome}</span>
            {ligada && (
              <span className="absolute -top-1.5 -right-1.5 flex size-5 items-center justify-center rounded-full bg-tinta text-superficie">
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

const FOCAVEIS = 'button:not(:disabled), select:not(:disabled), textarea:not(:disabled), input:not(:disabled), [href], [tabindex]:not([tabindex="-1"])';

function Folha({ linhas, estacoes, erroLinhas, recarregarLinhas, onFechar, onEnviado }: {
  linhas: LinhaInfo[]; estacoes: EstacaoEscolha[]; erroLinhas: boolean; recarregarLinhas: () => void;
  onFechar: () => void; onEnviado: () => void;
}) {
  const [linha, setLinha] = useState<string | null>(null);
  const [estacaoId, setEstacaoId] = useState("");
  const [descricao, setDescricao] = useState("");
  const [foto, setFoto] = useState<string | null>(null);
  const [erroFoto, setErroFoto] = useState<string | null>(null);
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

  async function escolherFoto(arquivo: File | undefined) {
    if (!arquivo) return;
    setErroFoto(null);
    try {
      setFoto(await prepararFoto(arquivo));
    } catch (e) {
      setFoto(null);
      setErroFoto(mensagemDe(e));
    }
  }

  async function enviar(tipo: TipoCodigo) {
    if (!linha || enviando) return;
    setEnviando(true);
    setErro(null);
    try {
      await chamar("/api/relatos", { metodo: "POST", corpo: { linha, tipo, estacao_id: estacaoId || null, descricao: descricao.trim() || null, foto } });
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
      <div className="absolute inset-0 bg-tinta/45" onClick={onFechar} aria-hidden />
      <div
        ref={painel}
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-folha"
        tabIndex={-1}
        className="subir relative max-h-[92%] w-full overflow-y-auto rounded-t-[28px] bg-superficie px-5 pb-6 shadow-folha outline-none @md:max-w-md @md:rounded-[28px]"
      >
        <span className="alca @md:hidden" aria-hidden />
        <div className="mt-3 mb-4 flex items-center gap-2">
          <h2 id="titulo-folha" className="flex-1 text-[24px] leading-tight font-bold tracking-tight">
            {enviado ? "Relato enviado" : linha ? "O que você está vendo?" : "Em qual linha você está?"}
          </h2>
          <button type="button" onClick={onFechar} aria-label="Fechar"
            className="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-cinza hover:bg-cinza-forte">
            <X className="size-5" aria-hidden />
          </button>
        </div>

        {enviado ? (
          <div role="status" className="flex flex-col items-center gap-2 py-6 text-center">
            <span className="flex size-16 items-center justify-center rounded-full bg-ok-suave text-ok"><Check className="size-8" strokeWidth={3} aria-hidden /></span>
            <p className="mt-2 text-[18px] font-bold">Seu relato já está no feed.</p>
            <p className="text-[14px] text-apagado">Ele fica visível por 2 horas.</p>
            <button type="button" onClick={onFechar}
              className="mt-4 h-14 w-full rounded-2xl bg-tinta text-[17px] font-bold text-superficie hover:bg-tinta/85">
              Fechar
            </button>
          </div>
        ) : !linha ? (
          erroLinhas ? (
            <div role="alert" className="rounded-2xl bg-erro-suave p-4 text-[14px] text-erro">
              Não foi possível carregar as linhas.
              <button type="button" onClick={recarregarLinhas} className="ml-2 min-h-11 font-bold underline">Tentar de novo</button>
            </div>
          ) : linhas.length === 0 ? (
            <p role="status" className="py-6 text-center text-apagado">Carregando linhas…</p>
          ) : (
            <GradeDeLinhas linhas={linhas} onEscolher={setLinha} />
          )
        ) : (
          <div className="flex flex-col gap-5">
            <div className="flex items-center gap-3 rounded-2xl bg-cinza p-3">
              {info && <SeloLinha numero={info.numero} cor={info.cor} />}
              <span className="min-w-0 flex-1 truncate text-[16px] font-bold">Linha {linha}{info ? ` ${info.nome}` : ""}</span>
              <button type="button" onClick={() => { setLinha(null); setErro(null); setEstacaoId(""); setDescricao(""); setFoto(null); setErroFoto(null); }}
                className="inline-flex h-9 items-center gap-1 rounded-full bg-superficie px-3 text-[13px] font-bold hover:bg-cinza-forte">
                <ArrowLeft className="size-4" aria-hidden />
                Trocar
              </button>
            </div>

            <div>
              <label htmlFor="estacao-relato" className="mb-1.5 block text-[14px] font-bold">Estação (opcional)</label>
              <select id="estacao-relato" value={estacaoId} onChange={(e) => setEstacaoId(e.target.value)}
                className="h-12 w-full rounded-2xl bg-cinza px-4 text-[16px] font-medium focus:bg-superficie focus:ring-2 focus:ring-tinta focus:outline-none">
                <option value="">Não informar</option>
                {daLinha.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
              </select>
            </div>

            <div>
              <label htmlFor="descricao-relato" className="mb-1.5 flex items-baseline justify-between text-[14px] font-bold">
                <span>Descrição (opcional)</span>
                <span className={`text-[12px] font-medium tabular-nums ${descricao.length >= LIMITE_DESCRICAO ? "text-erro" : "text-apagado"}`}>
                  {descricao.length}/{LIMITE_DESCRICAO}
                </span>
              </label>
              <textarea id="descricao-relato" value={descricao} rows={2} maxLength={LIMITE_DESCRICAO}
                onChange={(e) => setDescricao(e.target.value)} placeholder="Ex.: porta travada no vagão 3"
                className="w-full resize-none rounded-2xl bg-cinza px-4 py-3 text-[16px] font-medium placeholder:text-apagado/70 focus:bg-superficie focus:ring-2 focus:ring-tinta focus:outline-none" />
            </div>

            <div>
              <p className="mb-1.5 text-[14px] font-bold">Foto como evidência (opcional)</p>
              {foto ? (
                <div className="flex items-center gap-3 rounded-2xl bg-cinza p-2">
                  <img src={foto} alt="Foto que será enviada com o relato" className="size-16 shrink-0 rounded-xl object-cover" />
                  <p className="min-w-0 flex-1 text-[14px] font-medium">Foto pronta para enviar</p>
                  <button type="button" onClick={() => setFoto(null)} aria-label="Remover a foto"
                    className="inline-flex size-10 shrink-0 items-center justify-center rounded-full bg-superficie hover:bg-cinza-forte">
                    <X className="size-4" aria-hidden />
                  </button>
                </div>
              ) : (
                <>
                  <input id="foto-relato" type="file" accept="image/*" className="peer sr-only"
                    onChange={(e) => { void escolherFoto(e.target.files?.[0]); e.target.value = ""; }} />
                  <label htmlFor="foto-relato"
                    className="flex min-h-12 cursor-pointer items-center justify-center gap-2 rounded-2xl bg-cinza px-4 text-[15px] font-bold hover:bg-cinza-forte peer-focus-visible:ring-2 peer-focus-visible:ring-tinta">
                    <Camera className="size-5" aria-hidden />
                    Tirar ou escolher uma foto
                  </label>
                </>
              )}
              {erroFoto && <p role="alert" className="mt-2 text-[13px] font-medium text-erro">{erroFoto}</p>}
              <p className="mt-1.5 text-[12px] text-apagado">
                Mostre só o problema. Evite rostos e placas de veículos. A localização da foto é apagada, e ela sai do app quando o relato vence.
              </p>
            </div>

            <div>
              <p className="mb-2 text-[14px] font-bold">Toque no que está vendo para enviar</p>
              <div className="grid grid-cols-2 gap-2">
                {TIPOS.map((t) => (
                  <button key={t.codigo} type="button" disabled={enviando} onClick={() => enviar(t.codigo)}
                    className="flex min-h-[68px] items-center gap-3 rounded-2xl bg-cinza px-3 py-2 text-left text-[16px] font-bold hover:bg-cinza-forte disabled:opacity-60">
                    <span className={`flex size-10 shrink-0 items-center justify-center rounded-full bg-superficie ${t.cor}`}>
                      <t.Icone className="size-5" aria-hidden />
                    </span>
                    {t.rotulo}
                  </button>
                ))}
              </div>
            </div>

            {erro && <p role="alert" className="rounded-2xl bg-erro-suave p-3 text-[14px] font-medium text-erro">{erro}</p>}
            <p className="text-[12px] text-apagado">Não escreva CPF, telefone, e-mail, endereço, nome nem link. {AVISO_FIXO}</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ um relato na lista */

function Cartao({ r, cor, ocupado, onVotar, onSinalizar }: {
  r: Relato; cor: string; ocupado: boolean; onVotar: (r: Relato, v: Voto) => void; onSinalizar: (r: Relato) => void;
}) {
  const [confirmando, setConfirmando] = useState(false);
  const t = TIPO_POR_CODIGO[r.tipo] ?? TIPO_POR_CODIGO.normal;
  const votou = r.meu_voto !== null;
  const botao = (v: Voto, texto: string, n: number, Icone: typeof ThumbsUp) => {
    const escolhido = r.meu_voto === v;
    return (
      <button type="button" onClick={() => onVotar(r, v)} disabled={r.meu || votou || ocupado} aria-pressed={r.meu ? undefined : escolhido}
        className={`inline-flex h-9 items-center gap-1.5 rounded-full px-3.5 text-[13px] font-bold disabled:cursor-default ${
          escolhido ? "bg-tinta text-superficie" : "bg-cinza hover:bg-cinza-forte disabled:text-apagado disabled:hover:bg-cinza"
        }`}>
        {escolhido ? <Check className="size-4" aria-hidden /> : <Icone className="size-4" aria-hidden />}
        {texto}
        <span className={`tabular-nums ${escolhido ? "" : "text-apagado"}`}>{n}</span>
      </button>
    );
  };
  const sobre = [r.estacao_nome, `${r.apelido}${r.meu ? " (você)" : ""}`].filter(Boolean).join(", ");

  return (
    <li className="flex gap-3.5 border-b border-linha py-4 last:border-b-0">
      <SeloLinha numero={r.linha} cor={cor} tamanho="lg" />
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <t.Icone className={`size-[18px] shrink-0 ${t.cor}`} aria-hidden />
          <p className="min-w-0 flex-1 truncate text-[17px] leading-tight font-bold">{t.rotulo}</p>
          <span className="shrink-0 text-[13px] text-apagado">{haTempo(r.ha_min)}</span>
        </div>
        <p className="mt-0.5 truncate text-[14px] text-apagado">{sobre}</p>
        {r.descricao && <p className="mt-1.5 text-[15px] leading-snug break-words">{r.descricao}</p>}
        {r.foto_url && (
          <a href={r.foto_url} target="_blank" rel="noreferrer" aria-label="Abrir a foto do relato em tamanho maior" className="mt-2 block w-fit">
            <img src={r.foto_url} alt="Foto enviada por quem relatou" loading="lazy" className="h-24 w-36 max-w-full rounded-xl bg-cinza object-cover" />
          </a>
        )}
        {r.demo && (
          <span className="mt-1.5 inline-flex items-center gap-1 rounded-full bg-cinza px-2 py-0.5 text-[11px] font-bold text-apagado">
            <FlaskConical className="size-3.5" aria-hidden />
            demonstração
          </span>
        )}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {botao("ainda", "Continua", r.confirmacoes, ThumbsUp)}
          {botao("acabou", "Já acabou", r.contestacoes, Check)}
          {confirmando ? (
            <span className="ml-auto inline-flex items-center gap-1 text-[13px]">
              <span className="text-apagado">Sinalizar?</span>
              <button type="button" onClick={() => { setConfirmando(false); onSinalizar(r); }}
                className="h-9 rounded-full px-3 font-bold text-erro hover:bg-erro-suave">Sim</button>
              <button type="button" onClick={() => setConfirmando(false)}
                className="h-9 rounded-full px-3 font-bold text-apagado hover:bg-cinza">Não</button>
            </span>
          ) : (
            <button type="button" onClick={() => setConfirmando(true)} disabled={r.meu} title="Sinalizar"
              aria-label="Sinalizar este relato como inadequado ou falso"
              className="ml-auto inline-flex size-9 items-center justify-center rounded-full text-apagado hover:bg-cinza disabled:invisible">
              <Flag className="size-4" aria-hidden />
            </button>
          )}
        </div>
      </div>
    </li>
  );
}

/* ------------------------------------------------------------------ a aba */

function Painel({ children, alerta }: { children: ReactNode; alerta?: boolean }) {
  return <div role={alerta ? "alert" : "status"} className="rounded-2xl bg-cinza p-6 text-center">{children}</div>;
}

export default function Feed({ aoIr, aoSos }: { aoIr?: (aba: IdAba, focarConversa?: boolean) => void; aoSos?: () => void } = {}) {
  const { linhas, estacoes, erro: erroLinhas, carregar: recarregarLinhas } = useRede();
  const { enviar } = useConversa();
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
  const nomeDa = useCallback((numero: string) => linhas.find((l) => l.numero === numero)?.nome ?? "", [linhas]);

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

  const alertas = useMemo(() => estimativa.filter((e) => e.nivel === "alerta").slice(0, 6), [estimativa]);
  const visiveis = useMemo(() => {
    if (!relatos) return [];
    return filtro === "minhas" ? relatos.filter((r) => minhas.includes(r.linha)) : relatos;
  }, [relatos, filtro, minhas]);

  const atalhos: { rotulo: string; Icone: typeof Plus; acao: () => void }[] = [
    { rotulo: "Relatar", Icone: Megaphone, acao: () => setFolha(true) },
    { rotulo: "Mapa", Icone: MapaIcone, acao: () => aoIr?.("mapa") },
    { rotulo: "Linhas", Icone: TrainFront, acao: () => { aoIr?.("ia"); enviar("Como estão as linhas agora?"); } },
    { rotulo: "SOS", Icone: Siren, acao: () => aoSos?.() },
  ];

  return (
    <div className="@container relative flex h-full flex-col bg-superficie text-tinta">
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-7 px-4 pt-1 pb-28">
          {/* a pergunta que o app responde: tocar leva para a conversa com a Lia */}
          <section className="space-y-3">
            <button type="button" onClick={() => aoIr?.("ia", true)}
              className="flex h-[60px] w-full items-center gap-3 rounded-full bg-cinza pr-2 pl-5 text-left hover:bg-cinza-forte">
              <Search className="size-[22px] shrink-0" strokeWidth={2.4} aria-hidden />
              <span className="min-w-0 flex-1 truncate text-[19px] font-bold tracking-tight">Para onde você vai?</span>
              <span className="flex h-11 shrink-0 items-center gap-2 rounded-full bg-superficie pr-4 pl-1.5 text-[14px] font-bold shadow-sm">
                <Avatar tamanho="sm" />Lia
              </span>
            </button>
            <div className="grid grid-cols-4 gap-2.5">
              {atalhos.map(({ rotulo, Icone, acao }) => (
                <button key={rotulo} type="button" onClick={acao}
                  className="flex h-[84px] flex-col items-center justify-center gap-2 rounded-2xl bg-cinza text-[13px] font-bold hover:bg-cinza-forte">
                  <Icone className={`size-7 ${rotulo === "SOS" ? "text-erro" : ""}`} strokeWidth={1.9} aria-hidden />
                  {rotulo}
                </button>
              ))}
            </div>
          </section>

          {/* Agora nas linhas: o que os passageiros estão relatando juntos */}
          <section aria-labelledby="titulo-agora">
            <div className="mb-3 flex items-baseline justify-between gap-2">
              <h2 id="titulo-agora" className="text-[22px] font-bold tracking-tight">Agora nas linhas</h2>
              <span className="text-[12px] text-apagado">por relatos</span>
            </div>
            {alertas.length ? (
              <ul className="sem-barra -mx-4 flex snap-x gap-2.5 overflow-x-auto px-4 pb-1">
                {alertas.map((a) => {
                  const t = TIPO_POR_CODIGO[a.tipo_principal] ?? TIPO_POR_CODIGO.normal;
                  return (
                    <li key={a.linha} className="flex w-[172px] shrink-0 snap-start flex-col gap-3 rounded-[20px] bg-tinta p-3.5 text-white">
                      <div className="flex items-center justify-between">
                        <SeloLinha numero={a.linha} cor={corDa(a.linha)} tamanho="lg" />
                        <span className={`flex size-9 items-center justify-center rounded-full bg-superficie ${t.cor}`}><t.Icone className="size-[18px]" aria-hidden /></span>
                      </div>
                      <div>
                        <p className="text-[18px] leading-tight font-extrabold">{t.rotulo}</p>
                        <p className="truncate text-[13px] text-[#B8BDC5]">{nomeDa(a.linha) ? `${nomeDa(a.linha)}, ` : ""}{a.n_autores === 1 ? "1 pessoa relatou" : `${a.n_autores} pessoas relataram`}</p>
                      </div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="flex items-center gap-3 rounded-2xl bg-cinza p-4 text-[15px] font-medium">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-superficie text-ok"><CircleCheck className="size-5" aria-hidden /></span>
                Nenhum alerta dos passageiros agora
              </p>
            )}
            <p className="mt-2 text-[12px] text-apagado">{AVISO_FIXO}</p>
          </section>

          {/* Relatos recentes */}
          <section aria-labelledby="titulo-relatos">
            <div className="mb-1 flex flex-wrap items-center justify-between gap-2">
              <h2 id="titulo-relatos" className="text-[22px] font-bold tracking-tight">Relatos recentes</h2>
              <div className="inline-flex rounded-full bg-cinza p-1" role="group" aria-label="Filtro do feed">
                {([["todas", "Todas"], ["minhas", "Minhas linhas"]] as const).map(([valor, rotulo]) => (
                  <button key={valor} type="button" aria-pressed={filtro === valor} onClick={() => escolherFiltro(valor)}
                    className={`h-9 rounded-full px-3.5 text-[13px] ${filtro === valor ? "bg-superficie font-bold shadow-sm" : "font-semibold text-apagado hover:text-tinta"}`}>
                    {rotulo}
                  </button>
                ))}
              </div>
            </div>
            {filtro === "minhas" && (
              <button type="button" onClick={() => setEscolhendo((v) => !v)} aria-expanded={escolhendo}
                className="mt-1 min-h-10 text-[14px] font-bold underline underline-offset-4">
                {escolhendo ? "Pronto" : minhas.length ? `Editar linhas (${minhas.length})` : "Escolher linhas"}
              </button>
            )}
            {filtro === "minhas" && escolhendo && (
              <div className="mt-2 mb-2 rounded-2xl border border-linha p-3">
                <p className="mb-2 text-[14px] font-bold">Marque as linhas que você usa</p>
                {erroLinhas ? (
                  <p role="alert" className="text-[14px] text-erro">
                    Não foi possível carregar as linhas.
                    <button type="button" onClick={recarregarLinhas} className="ml-2 min-h-11 font-bold underline">Tentar de novo</button>
                  </p>
                ) : linhas.length === 0 ? (
                  <p role="status" className="text-[14px] text-apagado">Carregando linhas…</p>
                ) : (
                  <GradeDeLinhas linhas={linhas} marcadas={minhas} onEscolher={alternarLinha} />
                )}
              </div>
            )}

            {erro && relatos === null ? (
              <Painel alerta>
                <p className="font-bold text-erro">Não foi possível carregar os relatos.</p>
                <p className="mt-1 text-[14px] text-apagado">{erro}</p>
                <button type="button" onClick={atualizar}
                  className="mt-4 inline-flex h-12 items-center gap-2 rounded-full bg-tinta px-6 font-bold text-superficie hover:bg-tinta/85">
                  <RefreshCw className="size-4" aria-hidden />
                  Tentar de novo
                </button>
              </Painel>
            ) : relatos === null ? (
              <Painel><p className="text-apagado">Carregando relatos…</p></Painel>
            ) : (
              <>
                {erro && (
                  <p role="alert" className="my-2 flex flex-wrap items-center gap-2 rounded-2xl bg-alerta-suave p-3 text-[14px] font-medium text-alerta">
                    Sem atualização do servidor. Mostrando o que já chegou.
                    <button type="button" onClick={atualizar} className="min-h-11 font-bold underline">Tentar de novo</button>
                  </p>
                )}
                {relatos.length === 0 ? (
                  <Painel>
                    <p className="text-[16px] font-bold">Ninguém relatou nada ainda.</p>
                    <p className="mt-1 text-[14px] text-apagado">Viu algo na sua linha? Toque em Relatar.</p>
                  </Painel>
                ) : filtro === "minhas" && minhas.length === 0 ? (
                  <Painel><p className="text-apagado">Escolha ao menos uma linha para ver só os relatos dela.</p></Painel>
                ) : visiveis.length === 0 ? (
                  <Painel><p className="text-apagado">Nenhum relato nas suas linhas agora.</p></Painel>
                ) : (
                  <ul className="grid @md:grid-cols-2 @md:gap-x-8">
                    {visiveis.map((r) => (
                      <Cartao key={r.id} r={r} cor={corDa(r.linha)} ocupado={ocupado} onVotar={votar} onSinalizar={sinalizar} />
                    ))}
                  </ul>
                )}
              </>
            )}
          </section>
        </div>
      </div>

      {/* Relatar: botão preto flutuante, sempre à mão (a barra de abas fica abaixo desta área) */}
      <div className="pointer-events-none absolute inset-x-0 bottom-4 z-10 flex flex-col items-center gap-2 px-4">
        {aviso && (
          <p role="status" className={`entrar pointer-events-auto max-w-full rounded-2xl px-4 py-3 text-[14px] font-semibold shadow-flutua ${aviso.erro ? "bg-erro text-superficie" : "bg-tinta text-superficie"}`}>
            {aviso.texto}
          </p>
        )}
        <button type="button" onClick={() => setFolha(true)}
          className="pointer-events-auto inline-flex h-14 items-center justify-center gap-2 rounded-full bg-laranja pr-7 pl-5 text-[17px] font-extrabold text-tinta shadow-[0_8px_20px_rgb(255_92_0/0.35)] hover:brightness-95">
          <Plus className="size-6" strokeWidth={2.8} aria-hidden />
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
