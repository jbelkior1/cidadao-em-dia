import { Check, ChevronDown, Clock, CloudLightning, Copy, Droplets, ExternalLink, Footprints, Leaf, MessageSquareText, Phone, Repeat, Shield, TrainFront } from "lucide-react";
import { useState } from "react";

import type {
  Cartao, CartaoAlertas, CartaoLinhas, CartaoMensagem, CartaoOrientacao, CartaoPanorama, CartaoPlano, CartaoSeguranca, EtapaCartao, RotaCartao,
} from "../lib/api";
import { SeloLinha, SituacaoLinha, hora } from "./Linha";

/* Cartões que a Auxilia põe dentro da conversa. Pensados para a largura de um celular. */

const VEREDITO = { pode_ir: "bg-ok-suave text-ok", mais_cedo: "bg-alerta-suave text-alerta", plano_b: "bg-erro-suave text-erro" };
const FAIXAS: Record<string, string> = { madrugada: "Madrugada", manha: "Manhã", tarde: "Tarde", noite: "Noite" };
const FAIXA_FRASE: Record<string, string> = { madrugada: "de madrugada", manha: "de manhã", tarde: "à tarde", noite: "à noite" };
const kg = (v: number) => (v < 1 ? `${Math.round(v * 1000)} g` : `${v.toLocaleString("pt-BR")} kg`);
const reais = (v: number) => `R$ ${v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

/** Etapas do caminho; avisa a troca de linha mesmo quando ela acontece na mesma parada. */
export function EtapasCompactas({ rota }: { rota: RotaCartao }) {
  const itens: (EtapaCartao | { troca: string; para: string })[] = [];
  rota.etapas.forEach((e, i) => {
    const anterior = rota.etapas[i - 1];
    if (anterior && anterior.via !== "a pé" && e.via !== "a pé" && anterior.via !== e.via) itens.push({ troca: e.de, para: e.via });
    itens.push(e);
  });
  return (
    <ol className="space-y-1.5">
      {itens.map((e, i) =>
        "troca" in e ? (
          <li key={i} className="flex items-center gap-2 pl-0.5 text-[12px] text-apagado"><Repeat className="size-4 shrink-0" aria-hidden />Troque para a Linha {e.para} em {e.troca}</li>
        ) : e.via === "a pé" ? (
          <li key={i} className="flex items-center gap-2 pl-0.5 text-[12px] text-apagado">
            <Footprints className="size-4 shrink-0" aria-hidden />
            {e.de === e.ate ? `Troque de linha em ${e.de} (${e.min} min a pé)` : `A pé até ${e.ate} (${e.min} min)`}
          </li>
        ) : (
          <li key={i} className="flex items-center gap-2">
            <SeloLinha numero={e.via} cor={e.cor ?? "#888"} tamanho="sm" />
            <span className="min-w-0 text-[13px] leading-tight">
              <span className="font-semibold">{e.de} → {e.ate}</span>
              <span className="text-apagado"> · {e.paradas} {e.paradas === 1 ? "parada" : "paradas"}, {e.min} min</span>
            </span>
          </li>
        ),
      )}
    </ol>
  );
}

function Plano({ c }: { c: CartaoPlano }) {
  const [detalhes, setDetalhes] = useState(false);
  const temDetalhes = Object.keys(c.seguranca).length > 0 || !!c.energia;
  return (
    <div className="space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-[12px] font-semibold tracking-wide text-apagado uppercase">{c.origem} → {c.destino}</p>
          <span className={`mt-1 inline-block rounded-full px-3 py-1 text-[15px] font-bold ${VEREDITO[c.veredito.codigo]}`}>{c.veredito.texto}</span>
        </div>
        <div className="shrink-0 text-right">
          <p className="flex items-center justify-end gap-1 text-[11px] font-semibold text-apagado uppercase"><Clock className="size-3" aria-hidden />chegada</p>
          <p className="text-2xl leading-none font-bold tabular-nums">{c.chegada ?? "--:--"}</p>
          <p className="text-[11px] text-apagado">{c.minutos} min{c.atraso_min ? ` · +${c.atraso_min}` : ""}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {c.linhas.map((l) => (
          <span key={l.numero} className="inline-flex items-center gap-1.5">
            <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
            <SituacaoLinha nivel={l.nivel} />
          </span>
        ))}
      </div>
      {c.motivos.length > 0 && (
        <ul className="space-y-1 text-[13px] text-tinta/85">
          {c.motivos.slice(0, 3).map((m) => <li key={m} className="flex gap-1.5"><span aria-hidden>•</span>{m}</li>)}
        </ul>
      )}
      {c.desvio ? (
        <div className="space-y-2 rounded-xl border-2 border-marca/60 bg-marca-suave/40 p-3">
          <p className="text-[12px] font-bold tracking-wide text-marca-forte uppercase">Outro caminho · {c.desvio.recomendacao === "desviar" ? "desvie" : "espere"}</p>
          <p className="text-[13px]">{c.desvio.texto}</p>
          {c.desvio.rota && <EtapasCompactas rota={c.desvio.rota} />}
        </div>
      ) : (
        <EtapasCompactas rota={c.rota} />
      )}
      {temDetalhes && (
        <div className="border-t border-linha pt-2">
          <button type="button" onClick={() => setDetalhes(!detalhes)} className="flex w-full items-center justify-between text-[12px] font-semibold text-marca-forte">
            Segurança e energia da viagem<ChevronDown className={`size-4 transition-transform ${detalhes ? "rotate-180" : ""}`} aria-hidden />
          </button>
          {detalhes && (
            <div className="mt-2 space-y-2 text-[12px]">
              {(["saida", "chegada"] as const).map((lado) => {
                const s = c.seguranca[lado];
                return s ? (
                  <p key={lado} className="flex gap-1.5"><Shield className="mt-0.5 size-3.5 shrink-0 text-[#BE185D]" aria-hidden />
                    <span><span className="font-semibold">{s.estacao}:</span> {s.total.toLocaleString("pt-BR")} registros na SSP-SP a até 300 m, mais {FAIXA_FRASE[s.faixa] ?? s.faixa}.</span></p>
                ) : null;
              })}
              {c.energia && (
                <p className="flex gap-1.5"><Leaf className="mt-0.5 size-3.5 shrink-0 text-ok" aria-hidden />
                  <span>De trilho, cerca de {c.energia.trilho_g} g de CO₂ e {reais(c.energia.tarifa)}. De carro, {kg(c.energia.carro_kg)} e {reais(c.energia.carro_custo)} de gasolina.</span></p>
              )}
              <p className="text-[11px] text-apagado">Segurança é contagem de registros, não risco. Energia é estimativa por médias oficiais.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ListaDeLinhas({ linhas }: { linhas: CartaoLinhas["linhas"] }) {
  return (
    <ul className="grid grid-cols-1 gap-1.5 @md:grid-cols-2">
      {linhas.map((l) => (
        <li key={l.numero} className="flex items-center gap-2 rounded-lg bg-fundo px-2 py-1.5">
          <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
          <span className="min-w-0 flex-1 truncate text-[13px] font-semibold">{l.nome}</span>
          <SituacaoLinha nivel={l.nivel} />
        </li>
      ))}
    </ul>
  );
}

function Linhas({ c }: { c: CartaoLinhas }) {
  const ordem = [...c.linhas].sort((a, b) => Number(a.nivel === "normal") - Number(b.nivel === "normal"));
  return (
    <div className="space-y-2">
      <ListaDeLinhas linhas={ordem} />
      <p className="text-[11px] text-apagado">Leitura das {hora(c.lido_em)}. O aviso da estação vale mais.</p>
    </div>
  );
}

function Panorama({ c }: { c: CartaoPanorama }) {
  return (
    <div className="space-y-2.5">
      <p className="flex items-center gap-1.5 text-[12px] font-semibold tracking-wide text-apagado uppercase"><TrainFront className="size-3.5" aria-hidden />São Paulo agora · {hora(c.lido_em)}</p>
      {c.problemas.length ? <ListaDeLinhas linhas={c.problemas} /> : <p className="text-[13px]"><span className="font-semibold text-ok">{c.normais} linhas normais.</span> Nenhum problema informado.</p>}
      {c.problemas.length > 0 && <p className="text-[12px] text-apagado">As outras {c.normais} linhas estão normais.</p>}
      {c.inmet.map((a, i) => (
        <p key={i} className="flex gap-1.5 text-[12px] text-alerta"><CloudLightning className="mt-0.5 size-3.5 shrink-0" aria-hidden />INMET: {a.tipo.toLowerCase()} ({a.severidade.toLowerCase()}) até {a.fim.slice(-5)}</p>
      ))}
      <p className="flex gap-1.5 text-[12px] text-apagado"><Droplets className="mt-0.5 size-3.5 shrink-0" aria-hidden />
        CGE: {c.cge_estado ? c.cge_estado.titulo : "sem estado de atenção para alagamentos"}{c.cge_ativos !== null ? ` · ${c.cge_ativos} ${c.cge_ativos === 1 ? "ponto ativo" : "pontos ativos"}` : ""}</p>
    </div>
  );
}

function Alertas({ c }: { c: CartaoAlertas }) {
  return (
    <div className="space-y-2">
      <p className="text-[12px] font-semibold tracking-wide text-apagado uppercase">Alertas oficiais · {hora(c.lido_em)}</p>
      {c.inmet.length ? c.inmet.map((a, i) => (
        <p key={i} className="flex gap-1.5 text-[13px] text-alerta"><CloudLightning className="mt-0.5 size-4 shrink-0" aria-hidden />
          <span><span className="font-semibold">INMET:</span> {a.tipo.toLowerCase()} ({a.severidade.toLowerCase()}) até {a.fim.slice(-5)}</span></p>
      )) : <p className="text-[13px] text-apagado">INMET: nenhum aviso de chuva para hoje.</p>}
      <p className="flex gap-1.5 text-[13px]"><Droplets className="mt-0.5 size-4 shrink-0 text-marca" aria-hidden />
        <span><span className="font-semibold">CGE:</span> {c.cge_ok ? (c.cge_estado ? c.cge_estado.titulo : "sem estado de atenção ou alerta para alagamentos") : "sem leitura agora"}
          {c.cge_ativos !== null ? `. ${c.cge_ativos} ${c.cge_ativos === 1 ? "ponto de alagamento ativo" : "pontos de alagamento ativos"}.` : ""}</span></p>
      {c.cge_pontos.length > 0 && (
        <ul className="space-y-1 rounded-lg bg-fundo p-2 text-[12px]">
          {c.cge_pontos.map((p, i) => <li key={i}><span className="font-semibold">{p.bairro}</span>: {p.via.toLowerCase()} {p.transitavel ? "(transitável)" : "(intransitável)"}, desde {p.inicio}</li>)}
        </ul>
      )}
    </div>
  );
}

function Orientacao({ c }: { c: CartaoOrientacao }) {
  const [aberto, setAberto] = useState(false);
  return (
    <div className="space-y-2">
      <p className="text-[14px] font-bold">{c.titulo}</p>
      <p className={`text-[13px] leading-relaxed ${aberto ? "" : "line-clamp-4"}`}>{c.resposta}</p>
      {c.resposta.length > 220 && (
        <button type="button" onClick={() => setAberto(!aberto)} className="inline-flex items-center gap-1 text-[12px] font-semibold text-marca-forte">
          {aberto ? "Mostrar menos" : "Ler tudo"}<ChevronDown className={`size-3.5 transition-transform ${aberto ? "rotate-180" : ""}`} aria-hidden />
        </button>
      )}
      {c.canal && <p className="flex items-start gap-1.5 rounded-lg bg-fundo px-2.5 py-2 text-[12px]"><Phone className="mt-0.5 size-3.5 shrink-0 text-marca" aria-hidden />{c.canal}</p>}
      {c.fonte && (
        <a href={c.fonte} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-[12px] font-semibold text-marca-forte underline">
          Fonte oficial{c.verificado_em ? `, lida em ${c.verificado_em.split("-").reverse().join("/")}` : ""}<ExternalLink className="size-3" aria-hidden />
        </a>
      )}
    </div>
  );
}

function Seguranca({ c }: { c: CartaoSeguranca }) {
  const total = Object.values(c.por_faixa).reduce((a, b) => a + b, 0) || 1;
  return (
    <div className="space-y-2">
      <p className="flex items-center gap-1.5 text-[14px] font-bold"><Shield className="size-4 text-[#BE185D]" aria-hidden />{c.estacao}</p>
      <p className="text-[13px]">{c.total.toLocaleString("pt-BR")} registros a menos de 300 m ({c.periodo}), principalmente {c.tipo_principal}.</p>
      <ul className="space-y-1">
        {Object.entries(c.por_faixa).map(([f, n]) => (
          <li key={f} className="flex items-center gap-2 text-[12px]">
            <span className={`w-16 shrink-0 ${f === c.faixa ? "font-bold" : ""}`}>{FAIXAS[f] ?? f}</span>
            <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-fundo" aria-hidden><span className="block h-full rounded-full bg-[#BE185D]" style={{ width: `${(100 * n) / total}%` }} /></span>
            <span className="w-10 shrink-0 text-right tabular-nums text-apagado">{n.toLocaleString("pt-BR")}</span>
          </li>
        ))}
      </ul>
      <p className="text-[11px] text-apagado">Contagem de registros da SSP-SP, não taxa de risco: estação cheia tem mais registro.</p>
    </div>
  );
}

function Mensagem({ c }: { c: CartaoMensagem }) {
  const [copiado, setCopiado] = useState(false);
  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(c.texto);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      /* sem permissão de área de transferência: a pessoa copia na mão */
    }
  };
  return (
    <div className="space-y-2.5">
      <p className="flex items-center gap-1.5 text-[12px] font-semibold tracking-wide text-apagado uppercase"><MessageSquareText className="size-3.5" aria-hidden />Mensagem pronta{c.para_quem ? ` · ${c.para_quem}` : ""}</p>
      <p className="rounded-xl rounded-tl-sm bg-[#e7f6e9] px-3 py-2 text-[14px] leading-snug text-tinta">{c.texto}</p>
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={copiar} className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[13px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          {copiado ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}{copiado ? "Copiado" : "Copiar"}
        </button>
        <a href={`https://wa.me/?text=${encodeURIComponent(c.texto)}`} target="_blank" rel="noreferrer"
          className="inline-flex items-center gap-1.5 rounded-full bg-[#1f8f4e] px-3 py-1.5 text-[13px] font-semibold text-white hover:bg-[#187a42]">
          Abrir no WhatsApp
        </a>
      </div>
      <p className="text-[11px] text-apagado">Você escolhe para quem enviar. A Auxilia não envia nada sozinha.</p>
    </div>
  );
}

export function CartaoDaAuxilia({ cartao }: { cartao: Cartao }) {
  return (
    <div className="rounded-2xl border border-linha bg-superficie p-3.5 shadow-sm">
      {cartao.tipo === "plano" && <Plano c={cartao} />}
      {cartao.tipo === "linhas" && <Linhas c={cartao} />}
      {cartao.tipo === "panorama" && <Panorama c={cartao} />}
      {cartao.tipo === "alertas" && <Alertas c={cartao} />}
      {cartao.tipo === "orientacao" && <Orientacao c={cartao} />}
      {cartao.tipo === "seguranca" && <Seguranca c={cartao} />}
      {cartao.tipo === "mensagem" && <Mensagem c={cartao} />}
    </div>
  );
}
