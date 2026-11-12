import { BatteryFull, Bell, Laptop, Signal, Smartphone, Wifi } from "lucide-react";
import { useEffect, useState } from "react";

import { useApp } from "../App";
import { CORES_DAS_MATERIAS, mobilidade, type LinhaInfo, type Passo } from "../lib/api";
import { AvisoNoAparelho } from "./Auxilia";
import { useMenu } from "./Casca";
import { ProvedorConversa, useConversa } from "./conversa";
import Chat from "./Chat";

/*
 * A página do sistema: o chat da Auxilia, visto como notebook ou dentro do desenho de um
 * celular (no celular de verdade, tela cheia). Com o modo banca, o painel
 * "Por trás da tela" mostra quem fez cada parte e tem os controles da demonstração.
 * A conversa fica no ProvedorConversa: trocar de vista não a perde.
 */

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

function lerPreferencia<T extends string>(chave: string, validos: readonly T[], padrao: T): T {
  try {
    const v = localStorage.getItem(chave) as T | null;
    return v && validos.includes(v) ? v : padrao;
  } catch {
    return padrao;
  }
}
function gravarPreferencia(chave: string, valor: string) {
  try {
    localStorage.setItem(chave, valor);
  } catch {
    /* sem armazenamento */
  }
}

const PADRAO: Passo[] = [
  { materia: "PAI", titulo: "Conversa com IA", detalhe: "o modelo só afirma o que as ferramentas trazem" },
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

function PorTrasDaTela({ linhasInfo }: { linhasInfo: Record<string, LinhaInfo> }) {
  const { rastro, simular, setSimular, simularAviso } = useConversa();
  const [enviando, setEnviando] = useState(false);
  const passos = rastro.length ? rastro : PADRAO;
  const avisar = async () => {
    setEnviando(true);
    try {
      await simularAviso();
    } finally {
      setEnviando(false);
    }
  };
  return (
    <aside className="hidden w-80 shrink-0 flex-col gap-6 overflow-y-auto py-6 pr-6 xl:flex" aria-label="Por trás da tela">
      <div className="space-y-3 rounded-2xl border border-linha bg-superficie p-4">
        <p className="text-[15px] font-bold">Demonstração</p>
        <label htmlFor="simular-falha" className="block text-[13px] font-semibold text-apagado">Simular falha numa linha</label>
        <select id="simular-falha" value={simular} onChange={(e) => setSimular(e.target.value)} className="w-full rounded-lg border border-linha bg-superficie px-2.5 py-2 text-[14px]">
          <option value="">Nenhuma (situação real)</option>
          {Object.values(linhasInfo).filter((l) => l.numero !== "7").map((l) => <option key={l.numero} value={l.numero}>Linha {l.numero}-{l.nome}</option>)}
        </select>
        <button type="button" onClick={avisar} disabled={enviando}
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

function Seletor<T extends string>({ rotulo, opcoes, valor, aoMudar }: { rotulo: string; opcoes: { id: T; nome: string; icone?: React.ReactNode; titulo?: string }[]; valor: T; aoMudar: (v: T) => void }) {
  return (
    <div className="inline-flex shrink-0 items-center rounded-full bg-superficie p-1 shadow-sm ring-1 ring-linha" role="radiogroup" aria-label={rotulo}>
      {opcoes.map((o) => (
        <button key={o.id} type="button" role="radio" aria-checked={valor === o.id} title={o.titulo} onClick={() => aoMudar(o.id)}
          className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[13px] font-semibold ${valor === o.id ? "bg-marca text-white" : "text-apagado hover:text-tinta"}`}>
          {o.icone}{o.nome}
        </button>
      ))}
    </div>
  );
}

type Vista = "notebook" | "celular";

function Tela() {
  const { modoBanca } = useApp();
  const { abrirMenu } = useMenu();
  const computador = useLargura("(min-width: 1024px)");
  const [vista, setVista] = useState<Vista>(() => lerPreferencia<Vista>("auxilia-vista", ["notebook", "celular"], "celular"));
  const [linhasInfo, setLinhasInfo] = useState<Record<string, LinhaInfo>>({});

  useEffect(() => {
    mobilidade.estacoes().then((r) => setLinhasInfo(Object.fromEntries(r.linhas.map((l) => [l.numero, l])))).catch(() => {});
  }, []);

  if (!computador) {
    return (
      <div className="relative flex h-full flex-col bg-fundo">
        <AvisoNoAparelho />
        <Chat aoAbrirMenu={abrirMenu} />
      </div>
    );
  }

  return (
    <div className="flex h-full gap-8 bg-[radial-gradient(circle_at_30%_20%,#e3efeb,transparent_60%)] px-6">
      <div className="flex min-w-0 flex-1 flex-col items-center py-4">
        <div className="mb-3 flex shrink-0 flex-wrap items-center justify-center gap-2">
          <Seletor<Vista> rotulo="Ver como" valor={vista}
            aoMudar={(v) => { setVista(v); gravarPreferencia("auxilia-vista", v); }}
            opcoes={[{ id: "notebook", nome: "Notebook", icone: <Laptop className="size-4" aria-hidden /> }, { id: "celular", nome: "Celular", icone: <Smartphone className="size-4" aria-hidden /> }]} />
        </div>
        <div style={vista === "celular" ? { maxHeight: 860 } : undefined}
          className={vista === "celular"
            ? "relative flex min-h-0 w-[392px] flex-1 flex-col overflow-hidden rounded-[46px] border-[10px] border-tinta bg-superficie shadow-2xl"
            : "relative flex min-h-0 w-full max-w-4xl flex-1 flex-col overflow-hidden rounded-2xl border border-linha bg-superficie shadow-xl"}>
          {vista === "celular" && <BarraDeStatus />}
          <AvisoNoAparelho flutuante={vista === "notebook"} />
          <div className="min-h-0 flex-1"><Chat /></div>
          {vista === "celular" && <span className="mx-auto mt-1 mb-1.5 h-1 w-28 shrink-0 rounded-full bg-tinta/80" aria-hidden />}
        </div>
      </div>
      {modoBanca && <PorTrasDaTela linhasInfo={linhasInfo} />}
    </div>
  );
}

export default function Sistema() {
  return (
    <ProvedorConversa>
      <Tela />
    </ProvedorConversa>
  );
}
