import {
  AlertTriangle, ChevronDown, CircleCheck, Clock, CloudLightning, Droplets, MessageSquareText, Route, Sparkles, TrainFront,
} from "lucide-react";
import { useState, type ReactNode } from "react";

import type { CartaoAlertas, CartaoPanorama, CartaoPlano, PontoCGE } from "../../lib/api";
import { Entrada, Mensagens } from "../Auxilia";
import { EtapasCompactas } from "../Cartoes";
import { useConversa } from "../conversa";
import { SeloLinha, SituacaoLinha } from "../Linha";
import { Cabecalho, type PropsLayout } from "./comum";

/*
 * Layout 2 · Copiloto: o chat acompanhado de um painel vivo ("Agora") com a viagem e a cidade.
 * Largo: duas colunas (conversa à esquerda, painel à direita). Estreito: uma faixa viva sob o
 * cabeçalho abre e fecha o painel por cima da conversa, que continua montada.
 */

const VEREDITO = {
  pode_ir: { classe: "bg-ok-suave text-ok", Icone: CircleCheck },
  mais_cedo: { classe: "bg-alerta-suave text-alerta", Icone: AlertTriangle },
  plano_b: { classe: "bg-erro-suave text-erro", Icone: Route },
} as const;

const ATALHOS = ["Como estão as linhas?", "Tem alerta de alagamento?", "O trem parou, e agora?"];

function pontosAtivos(alertas: CartaoAlertas | null): PontoCGE[] {
  return alertas ? alertas.cge_pontos.filter((p) => p.ativo) : [];
}

function Secao({ titulo, icone, children }: { titulo: string; icone: ReactNode; children: ReactNode }) {
  return (
    <section className="space-y-2.5 rounded-2xl bg-superficie p-3.5 shadow-sm ring-1 ring-linha">
      <h2 className="flex items-center gap-1.5 text-[12px] font-semibold tracking-wide text-apagado uppercase">{icone}{titulo}</h2>
      {children}
    </section>
  );
}

function SuaViagem({ plano, enviar }: { plano: CartaoPlano | null; enviar: (t: string) => void }) {
  if (!plano) {
    return (
      <Secao titulo="Sua viagem" icone={<Route className="size-3.5" aria-hidden />}>
        <p className="text-[14px] text-apagado">Nenhuma viagem em andamento. Conte para a Auxilia por onde você vai passar.</p>
        <button type="button" onClick={() => enviar("Estou saindo de casa agora")}
          className="inline-flex items-center gap-1.5 rounded-full bg-marca px-3.5 py-2 text-[13px] font-semibold text-white hover:bg-marca-forte">
          <MessageSquareText className="size-4" aria-hidden />Estou saindo de casa
        </button>
      </Secao>
    );
  }
  const v = VEREDITO[plano.veredito.codigo];
  const rota = plano.desvio?.rota ?? plano.rota;
  return (
    <Secao titulo="Sua viagem" icone={<Route className="size-3.5" aria-hidden />}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-[13px] font-semibold">{plano.origem} → {plano.destino}</p>
          <span className={`mt-1.5 inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[15px] font-bold ${v.classe}`}>
            <v.Icone className="size-4" aria-hidden />{plano.veredito.texto}
          </span>
        </div>
        <div className="shrink-0 text-right">
          <p className="flex items-center justify-end gap-1 text-[11px] font-semibold text-apagado uppercase"><Clock className="size-3" aria-hidden />chegada</p>
          <p className="text-3xl leading-none font-bold tabular-nums">{plano.chegada ?? "--:--"}</p>
          <p className="text-[11px] text-apagado">{plano.minutos} min{plano.atraso_min ? ` · +${plano.atraso_min} de atraso` : ""}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {plano.linhas.map((l) => (
          <span key={l.numero} className="inline-flex items-center gap-1.5">
            <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
            <SituacaoLinha nivel={l.nivel} />
          </span>
        ))}
      </div>
      {plano.motivos.length > 0 && (
        <ul className="space-y-1 text-[13px] text-tinta/85">
          {plano.motivos.slice(0, 3).map((m) => <li key={m} className="flex gap-1.5"><span aria-hidden>•</span>{m}</li>)}
        </ul>
      )}
      <div className={plano.desvio ? "space-y-2 rounded-xl border-2 border-marca/60 bg-marca-suave/40 p-3" : "space-y-2"}>
        {plano.desvio && <p className="text-[12px] font-bold tracking-wide text-marca-forte uppercase">Outro caminho</p>}
        <EtapasCompactas rota={rota} />
      </div>
    </Secao>
  );
}

function ACidade({ panorama, alertas }: { panorama: CartaoPanorama | null; alertas: CartaoAlertas | null }) {
  const pontos = pontosAtivos(alertas);
  const inmet = panorama?.inmet ?? alertas?.inmet ?? [];
  const estado = panorama?.cge_estado ?? alertas?.cge_estado ?? null;
  const ativos = panorama?.cge_ativos ?? alertas?.cge_ativos ?? null;
  const vazio = !panorama && !alertas;
  return (
    <Secao titulo="A cidade agora" icone={<TrainFront className="size-3.5" aria-hidden />}>
      {vazio ? (
        <p className="text-[14px] text-apagado">Ainda sem leitura. Pergunte como estão as linhas.</p>
      ) : (
        <>
          {panorama && panorama.problemas.length > 0 && (
            <ul className="space-y-1.5">
              {panorama.problemas.map((l) => (
                <li key={l.numero} className="flex items-center gap-2">
                  <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
                  <span className="min-w-0 flex-1 truncate text-[13px] font-semibold">{l.nome}</span>
                  <SituacaoLinha nivel={l.nivel} />
                </li>
              ))}
            </ul>
          )}
          {panorama && (
            <p className="text-[13px]">
              {panorama.problemas.length
                ? <span className="text-apagado">As outras {panorama.normais} linhas estão normais.</span>
                : <span className="inline-flex items-center gap-1.5 font-semibold text-ok"><CircleCheck className="size-4" aria-hidden />{panorama.normais} linhas normais</span>}
            </p>
          )}
          {inmet.length > 0 ? inmet.map((a, i) => (
            <p key={i} className="flex gap-1.5 text-[13px] text-alerta"><CloudLightning className="mt-0.5 size-4 shrink-0" aria-hidden />
              <span><span className="font-semibold">INMET:</span> {a.tipo.toLowerCase()} ({a.severidade.toLowerCase()}) até {a.fim.slice(-5)}</span></p>
          )) : <p className="flex gap-1.5 text-[13px] text-apagado"><CloudLightning className="mt-0.5 size-4 shrink-0" aria-hidden />INMET: nenhum aviso de chuva.</p>}
          <p className="flex gap-1.5 text-[13px]"><Droplets className="mt-0.5 size-4 shrink-0 text-marca" aria-hidden />
            <span><span className="font-semibold">CGE:</span> {estado ? estado.titulo : "sem estado de atenção para alagamentos"}
              {ativos !== null ? ` · ${ativos} ${ativos === 1 ? "ponto ativo" : "pontos ativos"}` : ""}</span></p>
          {pontos.length > 0 && (
            <ul className="space-y-1 rounded-lg bg-fundo p-2 text-[12px]">
              {pontos.map((p, i) => <li key={i}><span className="font-semibold">{p.bairro}</span>: {p.via.toLowerCase()} {p.transitavel ? "(transitável)" : "(intransitável)"}, desde {p.inicio}</li>)}
            </ul>
          )}
        </>
      )}
    </Secao>
  );
}

function Atalhos({ temViagem, enviar, esperando }: { temViagem: boolean; enviar: (t: string) => void; esperando: boolean }) {
  const itens = temViagem ? [...ATALHOS, "Avisa que vou atrasar"] : ATALHOS;
  return (
    <Secao titulo="Atalhos" icone={<Sparkles className="size-3.5" aria-hidden />}>
      <div className="flex flex-wrap gap-2">
        {itens.map((t) => (
          <button key={t} type="button" disabled={esperando} onClick={() => enviar(t)}
            className="rounded-full bg-marca-suave px-3 py-1.5 text-[13px] font-semibold text-marca-forte hover:bg-marca hover:text-white disabled:opacity-40">
            {t}
          </button>
        ))}
      </div>
    </Secao>
  );
}

function PainelAgora({ className = "", aoEnviar }: { className?: string; aoEnviar?: () => void }) {
  const { resumo, enviar, esperando } = useConversa();
  const acionar = (t: string) => {
    enviar(t);
    aoEnviar?.();
  };
  return (
    <aside aria-label="Painel Agora: sua viagem e a cidade" className={`space-y-3 overflow-y-auto p-3 ${className}`}>
      <SuaViagem plano={resumo.plano} enviar={acionar} />
      <ACidade panorama={resumo.panorama} alertas={resumo.alertas} />
      <Atalhos temViagem={!!resumo.plano} enviar={acionar} esperando={esperando} />
    </aside>
  );
}

function FaixaViva({ aberto, aoAlternar }: { aberto: boolean; aoAlternar: () => void }) {
  const { resumo } = useConversa();
  const { plano, panorama, alertas } = resumo;
  const v = plano ? VEREDITO[plano.veredito.codigo] : null;
  const ativos = panorama?.cge_ativos ?? alertas?.cge_ativos ?? null;
  const cge = ativos ? `CGE com ${ativos} ${ativos === 1 ? "ponto" : "pontos"}` : "CGE sem alerta";
  return (
    <button type="button" onClick={aoAlternar} aria-expanded={aberto}
      className="flex w-full shrink-0 items-center gap-2 border-b border-linha bg-superficie px-3 py-2 text-left @3xl:hidden">
      {plano && v ? (
        <>
          <span className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-0.5 text-[13px] font-bold ${v.classe}`}>
            <v.Icone className="size-3.5" aria-hidden />{plano.veredito.texto}
          </span>
          <span className="min-w-0 flex-1 truncate text-[13px] text-apagado">chega às <span className="font-bold text-tinta tabular-nums">{plano.chegada ?? "--:--"}</span></span>
        </>
      ) : (
        <span className="min-w-0 flex-1 truncate text-[13px] font-semibold">
          {panorama
            ? `${panorama.normais} ${panorama.normais === 1 ? "linha normal" : "linhas normais"}${panorama.problemas.length ? ` · ${panorama.problemas.length} com problema` : ""} · ${cge}`
            : "Ver a cidade agora"}
        </span>
      )}
      <span className="flex shrink-0 items-center gap-1 text-[12px] font-semibold text-marca-forte">
        {aberto ? "Fechar" : "Agora"}<ChevronDown className={`size-4 transition-transform ${aberto ? "rotate-180" : ""}`} aria-hidden />
      </span>
    </button>
  );
}

/** Layout 2 · Copiloto. */
export default function LayoutCopiloto({ aoAbrirMenu }: PropsLayout) {
  const [aberto, setAberto] = useState(false);
  return (
    <div className="@container flex h-full min-h-0 bg-fundo">
      <div className="flex h-full min-h-0 min-w-0 flex-1 flex-col">
        <Cabecalho aoAbrirMenu={aoAbrirMenu} />
        <FaixaViva aberto={aberto} aoAlternar={() => setAberto((a) => !a)} />
        <div className="relative flex min-h-0 flex-1 flex-col">
          <Mensagens ocultarTipos={["plano", "panorama"]} />
          {aberto && <PainelAgora className="absolute inset-0 z-10 bg-fundo @3xl:hidden" aoEnviar={() => setAberto(false)} />}
        </div>
        <Entrada />
      </div>
      <PainelAgora className="hidden h-full w-[340px] shrink-0 border-l border-linha bg-fundo @3xl:block" />
    </div>
  );
}
