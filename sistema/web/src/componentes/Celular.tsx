import { BatteryFull, Bell, Laptop, Menu, RotateCcw, Signal, Smartphone, Wifi, X } from "lucide-react";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";

import { useApp } from "../App";
import { CORES_DAS_MATERIAS, mobilidade, type LinhaInfo, type Passo, type Viagem } from "../lib/api";
import Auxilia, { Avatar } from "./Auxilia";
import { useMenu } from "./Casca";

/*
 * O sistema: a conversa com a Auxilia. No computador dá para ver como tela de notebook
 * ou dentro do desenho de um celular; no celular de verdade, ocupa a tela toda.
 * Com o modo banca, o painel "Por trás da tela" mostra quem fez cada parte e tem os
 * controles da demonstração (falha simulada e aviso antes de sair).
 */

type Notificacao = { titulo: string; texto: string; pedido: string };
type ContextoSistema = {
  simular: string;
  setRastro: (r: Passo[]) => void;
  ultimaViagem: Viagem | null;
  setUltimaViagem: (v: Viagem) => void;
  pedido: string;
  limparPedido: () => void;
  reinicio: number;
};
const Contexto = createContext<ContextoSistema>({
  simular: "", setRastro: () => {}, ultimaViagem: null, setUltimaViagem: () => {}, pedido: "", limparPedido: () => {}, reinicio: 0,
});
export const useSistema = () => useContext(Contexto);

function useLargura(consulta: string): boolean {
  const [casa, setCasa] = useState(() => window.matchMedia(consulta).matches);
  useEffect(() => {
    const m = window.matchMedia(consulta);
    const mudar = () => setCasa(m.matches);
    m.addEventListener("change", mudar);
    return () => m.removeEventListener("change", mudar);
  }, [consulta]);
  return casa;
}

type Vista = "notebook" | "celular";
function lerVista(): Vista {
  try {
    return localStorage.getItem("plano-b-vista") === "notebook" ? "notebook" : "celular";
  } catch {
    return "celular";
  }
}

const PADRAO: Passo[] = [
  { materia: "PAI", titulo: "Conversa com IA", detalhe: "o Gemini só afirma o que as ferramentas trazem" },
  { materia: "CS", titulo: "Decide a viagem", detalhe: "falha, chuva, alagamento e pico" },
  { materia: "PCP", titulo: "Orientações oficiais", detalhe: "busca por pontos" },
  { materia: "DSA", titulo: "Canal de atendimento", detalhe: "lista encadeada" },
  { materia: "MLAM", titulo: "Segurança nas estações", detalhe: "SSP-SP por estação" },
  { materia: "SERS", titulo: "Energia da viagem", detalhe: "trilho, ônibus e carro" },
];

function horaAgora() {
  return new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function BarraDeStatus() {
  const [h, setH] = useState(horaAgora);
  useEffect(() => {
    const t = setInterval(() => setH(horaAgora()), 20000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="relative flex h-10 shrink-0 items-center justify-between px-7 pt-1 text-[13px] font-semibold text-tinta" aria-hidden>
      <span>{h}</span>
      <span className="absolute top-2.5 left-1/2 h-6 w-24 -translate-x-1/2 rounded-full bg-tinta" />
      <span className="flex items-center gap-1.5"><Signal className="size-3.5" /><Wifi className="size-3.5" /><BatteryFull className="size-4" /></span>
    </div>
  );
}

function Aviso({ n, aoAbrir, aoFechar, flutuante }: { n: Notificacao; aoAbrir: () => void; aoFechar: () => void; flutuante?: boolean }) {
  return (
    <div role="alert" className={`entrar z-30 flex items-start gap-3 rounded-2xl bg-superficie/95 p-3 shadow-xl ring-1 ring-linha backdrop-blur ${flutuante ? "fixed top-20 right-6 w-80" : "absolute inset-x-3 top-11"}`}>
      <Avatar />
      <button type="button" className="min-w-0 flex-1 text-left" onClick={aoAbrir}>
        <span className="flex items-center justify-between text-[11px] text-apagado"><span className="font-semibold">PLANO B · AUXILIA</span><span>agora</span></span>
        <span className="block text-[14px] font-semibold">{n.titulo}</span>
        <span className="block text-[13px] text-tinta/80">{n.texto}</span>
      </button>
      <button type="button" aria-label="Fechar aviso" onClick={aoFechar} className="rounded-full p-1 text-apagado hover:bg-fundo"><X className="size-4" /></button>
    </div>
  );
}

function Cabecalho({ aoReiniciar, comMenu }: { aoReiniciar: () => void; comMenu: boolean }) {
  const { ia } = useApp();
  const { abrirMenu } = useMenu();
  const { simular } = useSistema();
  return (
    <header className="flex h-14 shrink-0 items-center gap-2.5 border-b border-linha bg-superficie px-3">
      {comMenu && <button type="button" onClick={abrirMenu} aria-label="Abrir o menu do sistema" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><Menu className="size-5" /></button>}
      <Avatar />
      <div className="min-w-0 leading-tight">
        <p className="text-[16px] font-bold">Auxilia</p>
        <p className="flex items-center gap-1 text-[12px] text-apagado"><span className="size-1.5 rounded-full bg-ok" aria-hidden />seu Plano B no trem e no metrô</p>
      </div>
      <div className="ml-auto flex items-center gap-1.5">
        {simular && <span className="rounded-full bg-erro-suave px-2 py-0.5 text-[11px] font-semibold text-erro">simulação L{simular}</span>}
        {!ia?.ligada && <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-semibold text-apagado ring-1 ring-linha">sem IA</span>}
        <button type="button" onClick={aoReiniciar} aria-label="Nova conversa" title="Nova conversa" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><RotateCcw className="size-4" /></button>
      </div>
    </header>
  );
}

function PorTrasDaTela({ linhasInfo, rastro, simular, setSimular, aoSimularAviso, enviando }: {
  linhasInfo: Record<string, LinhaInfo>; rastro: Passo[]; simular: string; setSimular: (s: string) => void; aoSimularAviso: () => void; enviando: boolean;
}) {
  const passos = rastro.length ? rastro : PADRAO;
  return (
    <aside className="hidden w-80 shrink-0 flex-col gap-6 overflow-y-auto py-6 pr-6 xl:flex" aria-label="Por trás da tela">
      <div className="space-y-3 rounded-2xl border border-linha bg-superficie p-4">
        <p className="text-[15px] font-bold">Demonstração</p>
        <label htmlFor="simular-falha" className="block text-[13px] font-semibold text-apagado">Simular falha numa linha</label>
        <select id="simular-falha" value={simular} onChange={(e) => setSimular(e.target.value)} className="w-full rounded-lg border border-linha bg-superficie px-2.5 py-2 text-[14px]">
          <option value="">Nenhuma (situação real)</option>
          {Object.values(linhasInfo).filter((l) => l.numero !== "7").map((l) => <option key={l.numero} value={l.numero}>Linha {l.numero}-{l.nome}</option>)}
        </select>
        <button type="button" onClick={aoSimularAviso} disabled={enviando}
          className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-marca px-3 py-2.5 text-[14px] font-semibold text-white hover:bg-marca-forte disabled:opacity-50">
          <Bell className="size-4" aria-hidden />Simular o aviso antes de sair
        </button>
        <p className="text-[12px] text-apagado">O aviso usa a última viagem conferida na conversa. No app de verdade, chegaria no horário de saída, sem a pessoa abrir o app.</p>
      </div>
      <div className="space-y-3">
        <p className="text-[15px] font-bold">{rastro.length ? "Quem fez esta resposta" : "Quem trabalha por trás"}</p>
        <ol className="space-y-3">
          {passos.map((p, i) => (
            <li key={i} className="flex gap-2.5 text-[14px]">
              <span className="mt-1.5 size-2.5 shrink-0 rounded-full" style={{ background: CORES_DAS_MATERIAS[p.materia] ?? "#8FA19D" }} />
              <span><span className="font-semibold">{p.materia} · {p.titulo}</span>{p.detalhe && <span className="block text-[12px] text-apagado">{p.detalhe}</span>}</span>
            </li>
          ))}
        </ol>
      </div>
      <p className="mt-auto text-[12px] text-apagado">Fontes ao vivo: situação das linhas (agregador público), INMET, CGE da Prefeitura. Base: GTFS da SPTrans, SSP-SP, GeoSampa.</p>
    </aside>
  );
}

export default function Sistema() {
  const { modoBanca } = useApp();
  const computador = useLargura("(min-width: 1024px)");
  const [vista, setVista] = useState<Vista>(lerVista);
  const [simular, setSimular] = useState("");
  const [rastro, setRastro] = useState<Passo[]>([]);
  const [ultimaViagem, setUltimaViagem] = useState<Viagem | null>(null);
  const [pedido, setPedido] = useState("");
  const [reinicio, setReinicio] = useState(0);
  const [aviso, setAviso] = useState<Notificacao | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [linhasInfo, setLinhasInfo] = useState<Record<string, LinhaInfo>>({});
  const temporizador = useRef(0);

  useEffect(() => {
    mobilidade.estacoes().then((r) => setLinhasInfo(Object.fromEntries(r.linhas.map((l) => [l.numero, l])))).catch(() => {});
  }, []);

  const trocarVista = (v: Vista) => {
    setVista(v);
    try {
      localStorage.setItem("plano-b-vista", v);
    } catch {
      /* sem armazenamento */
    }
  };
  const notificar = useCallback((n: Notificacao) => {
    setAviso(n);
    window.clearTimeout(temporizador.current);
    temporizador.current = window.setTimeout(() => setAviso(null), 10000);
  }, []);
  const reiniciar = () => {
    setRastro([]);
    setUltimaViagem(null);
    setReinicio((n) => n + 1);
  };

  const simularAviso = async () => {
    if (!ultimaViagem) {
      return notificar({ titulo: "Converse com a Auxilia primeiro", texto: "Diga para onde vai; o aviso usa a viagem que ela conferiu.", pedido: "Estou saindo de casa agora" });
    }
    setEnviando(true);
    try {
      const p = await mobilidade.plano(ultimaViagem.origem, ultimaViagem.destino, simular || undefined);
      const falha = p.linhas.find((l) => l.nivel === "parada" || l.nivel === "atencao");
      notificar({
        pode_ir: { titulo: "Pode sair no horário", texto: `Linhas ${p.rota.linhas.join(" e ")} normais até ${p.destino}.`, pedido: "Vi o aviso. Posso ir mesmo?" },
        mais_cedo: { titulo: "Saia um pouco mais cedo", texto: p.motivos.find((m) => m.tipo === "chuva" || m.tipo === "alagamento")?.texto ?? "Seu caminho deve estar mais lento hoje.", pedido: "Vi o aviso. O que está acontecendo no caminho?" },
        plano_b: { titulo: `Linha ${falha?.numero ?? ""} com problema`, texto: `Antes de sair: vai precisar de um Plano B até ${p.destino}.`, pedido: "Vi o aviso. Qual é o Plano B?" },
      }[p.veredito.codigo]);
    } finally {
      setEnviando(false);
    }
  };
  const abrirAviso = () => {
    if (aviso) setPedido(aviso.pedido);
    setAviso(null);
  };

  const contexto = { simular, setRastro, ultimaViagem, setUltimaViagem, pedido, limparPedido: () => setPedido(""), reinicio };

  if (!computador) {
    return (
      <Contexto.Provider value={contexto}>
        <div className="@container relative flex h-full flex-col bg-fundo">
          {aviso && <Aviso n={aviso} aoAbrir={abrirAviso} aoFechar={() => setAviso(null)} />}
          <Cabecalho aoReiniciar={reiniciar} comMenu />
          <div className="min-h-0 flex-1"><Auxilia /></div>
        </div>
      </Contexto.Provider>
    );
  }

  return (
    <Contexto.Provider value={contexto}>
      <div className="flex h-full gap-8 bg-[radial-gradient(circle_at_30%_20%,#e3efeb,transparent_60%)] px-6">
        <div className="flex min-w-0 flex-1 flex-col items-center py-4">
          <div className="mb-3 inline-flex shrink-0 rounded-full bg-superficie p-1 shadow-sm ring-1 ring-linha" role="radiogroup" aria-label="Ver como">
            {([["notebook", "Notebook", Laptop], ["celular", "Celular", Smartphone]] as const).map(([v, rotulo, Icone]) => (
              <button key={v} type="button" role="radio" aria-checked={vista === v} onClick={() => trocarVista(v)}
                className={`inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-[13px] font-semibold ${vista === v ? "bg-marca text-white" : "text-apagado hover:text-tinta"}`}>
                <Icone className="size-4" aria-hidden />{rotulo}
              </button>
            ))}
          </div>

          {/* mesma árvore nas duas vistas: trocar de notebook para celular não reinicia a conversa */}
          <div style={vista === "celular" ? { maxHeight: 860 } : undefined}
            className={vista === "celular"
              ? "relative flex min-h-0 w-[392px] flex-1 flex-col overflow-hidden rounded-[46px] border-[10px] border-tinta bg-superficie shadow-2xl"
              : "relative flex min-h-0 w-full max-w-4xl flex-1 flex-col overflow-hidden rounded-2xl border border-linha bg-superficie shadow-xl"}>
            {vista === "celular" && <BarraDeStatus />}
            {aviso && <Aviso n={aviso} aoAbrir={abrirAviso} aoFechar={() => setAviso(null)} flutuante={vista === "notebook"} />}
            <Cabecalho aoReiniciar={reiniciar} comMenu={false} />
            <div className="@container min-h-0 flex-1 bg-fundo"><Auxilia /></div>
            {vista === "celular" && <span className="mx-auto mt-1 mb-1.5 h-1 w-28 shrink-0 rounded-full bg-tinta/80" aria-hidden />}
          </div>
        </div>
        {modoBanca && <PorTrasDaTela linhasInfo={linhasInfo} rastro={rastro} simular={simular} setSimular={setSimular} aoSimularAviso={simularAviso} enviando={enviando} />}
      </div>
    </Contexto.Provider>
  );
}
