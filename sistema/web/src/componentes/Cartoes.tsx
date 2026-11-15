import { Check, CheckCircle2, ChevronDown, Clock, CloudLightning, Copy, Droplets, ExternalLink, Info, Leaf, MessageSquareText, Phone, Repeat, Shield, TrainFront, Users, XCircle } from "lucide-react";
import { useState } from "react";

import type {
  Cartao, CartaoAlertas, CartaoLinhas, CartaoMensagem, CartaoOrientacao, CartaoPanorama, CartaoPlano, CartaoSeguranca, RotaCartao,
} from "../lib/api";
import { useConversa } from "./conversa";
import { SeloLinha, SituacaoLinha, hora } from "./Linha";

/* Cartões que a Lia põe dentro da conversa. Pensados para a largura de um celular. */

const VEREDITO = { pode_ir: "bg-ok-suave text-ok", mais_cedo: "bg-alerta-suave text-alerta", plano_b: "bg-erro-suave text-erro" };
const FAIXAS: Record<string, string> = { madrugada: "Madrugada", manha: "Manhã", tarde: "Tarde", noite: "Noite" };
const FAIXA_FRASE: Record<string, string> = { madrugada: "de madrugada", manha: "de manhã", tarde: "à tarde", noite: "à noite" };
const kg = (v: number) => (v < 1 ? `${Math.round(v * 1000)} g` : `${v.toLocaleString("pt-BR")} kg`);
const reais = (v: number) => `R$ ${v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

type NoCaminho =
  | { tipo: "estacao"; nome: string; nota: string; cor: string; fim?: boolean }
  | { tipo: "trecho"; linha: string; cor: string; paradas: number; min: number }
  | { tipo: "caminhada"; min: number };

/** Transforma as etapas da rota numa linha do tempo: estação, trecho, estação de troca, trecho... */
function linhaDoTempo(rota: RotaCartao): NoCaminho[] {
  const etapas = rota.etapas;
  const nos: NoCaminho[] = [];
  const primeira = etapas.findIndex((e) => e.via !== "a pé");
  if (primeira < 0) return nos;
  nos.push({ tipo: "estacao", nome: etapas[primeira].de, nota: "embarque", cor: etapas[primeira].cor ?? "#556A6A" });
  for (let i = primeira; i < etapas.length; i++) {
    const e = etapas[i];
    if (e.via === "a pé") continue;
    nos.push({ tipo: "trecho", linha: e.via, cor: e.cor ?? "#888888", paradas: e.paradas, min: e.min });
    const prox = etapas[i + 1];
    if (!prox) {
      nos.push({ tipo: "estacao", nome: e.ate, nota: "desembarque", cor: e.cor ?? "#556A6A", fim: true });
    } else if (prox.via === "a pé" && prox.de === prox.ate) {
      const depois = etapas[i + 2];
      nos.push({ tipo: "estacao", nome: e.ate, nota: depois ? `troque para a ${depois.via}, ${prox.min} min a pé` : "desembarque", cor: depois?.cor ?? e.cor ?? "#556A6A" });
    } else if (prox.via === "a pé") {
      nos.push({ tipo: "estacao", nome: e.ate, nota: `saia e ande ${prox.min} min`, cor: "#556A6A" });
      nos.push({ tipo: "caminhada", min: prox.min });
      nos.push({ tipo: "estacao", nome: prox.ate, nota: "chegada", cor: "#12292B", fim: true });
      i++;
    } else {
      nos.push({ tipo: "estacao", nome: e.ate, nota: `troque para a ${prox.via}`, cor: prox.cor ?? "#556A6A" });
    }
  }
  return nos;
}

const NIVEL_CURTO: Record<string, { rotulo: string; classe: string }> = {
  normal: { rotulo: "✓ Normal", classe: "bg-ok-suave text-ok" },
  atencao: { rotulo: "! Atenção", classe: "bg-alerta-suave text-alerta" },
  parada: { rotulo: "✕ Parada", classe: "bg-erro-suave text-erro" },
  encerrada: { rotulo: "Encerrada", classe: "bg-fundo text-apagado ring-1 ring-linha" },
  sem_dado: { rotulo: "Sem informação", classe: "bg-fundo text-apagado ring-1 ring-linha" },
};

/** O caminho como linha do tempo, com a situação de cada linha no próprio trecho. */
export function Caminho({ rota, situacao, notaDoPrimeiro }: { rota: RotaCartao; situacao: CartaoPlano["situacao"]; notaDoPrimeiro?: string }) {
  const nos = linhaDoTempo(rota);
  let primeiroTrecho = true;
  return (
    <ol className="grid grid-cols-[22px_minmax(0,1fr)] gap-x-2.5">
      {nos.map((n, i) => {
        if (n.tipo === "estacao") {
          return (
            <li key={i} className="contents">
              <span className={`mx-auto mt-[3px] size-3.5 rounded-full ${n.fim ? "" : "border-[3px] bg-superficie"}`} style={n.fim ? { background: n.cor } : { borderColor: n.cor }} aria-hidden />
              <span className="pb-0.5 text-[14px] leading-tight font-bold">{n.nome} <span className="font-medium text-apagado">· {n.nota}</span></span>
            </li>
          );
        }
        if (n.tipo === "caminhada") {
          return (
            <li key={i} className="contents">
              <span className="mx-auto h-4 border-l-2 border-dashed border-apagado" aria-hidden />
              <span><span className="sr-only">Caminhada de {n.min} minutos</span></span>
            </li>
          );
        }
        const s = situacao[n.linha];
        const nivel = NIVEL_CURTO[s?.nivel ?? "sem_dado"] ?? NIVEL_CURTO.sem_dado;
        const nota = primeiroTrecho && notaDoPrimeiro ? notaDoPrimeiro : "";
        primeiroTrecho = false;
        return (
          <li key={i} className="contents">
            <span className="mx-auto w-1.5 rounded-full" style={{ background: n.cor }} aria-hidden />
            <span className="flex items-center gap-2 py-1.5">
              <SeloLinha numero={n.linha} cor={n.cor} tamanho="sm" />
              <span className="min-w-0 flex-1 text-[12px] leading-snug">
                <span className="font-semibold">Linha {n.linha}{s ? `-${s.nome}` : ""}</span> · {n.paradas} {n.paradas === 1 ? "parada" : "paradas"} · {n.min} min
                {nota && <span className="block text-apagado">{nota}</span>}
              </span>
              <span className={`shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold ${nivel.classe}`}>{nivel.rotulo}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}

const FAIXA_DECISAO = {
  pode_ir: { fundo: "bg-ok-suave", texto: "text-ok", Icone: CheckCircle2 },
  mais_cedo: { fundo: "bg-alerta-suave", texto: "text-alerta", Icone: Clock },
  plano_b: { fundo: "bg-erro-suave", texto: "text-erro", Icone: Repeat },
};
const ICONE_AVISO = { chuva: CloudLightning, alagamento: Droplets, pico: Users, sem_dado: Info };

function Plano({ c }: { c: CartaoPlano }) {
  const { enviar, esperando } = useConversa();
  const [detalhes, setDetalhes] = useState(false);
  const faixa = FAIXA_DECISAO[c.veredito.codigo];
  const temDetalhes = Object.keys(c.seguranca).length > 0 || !!c.energia;
  const desviando = !!c.desvio?.rota;
  const rota = c.desvio?.rota ?? c.rota;
  const linhaParada = c.linhas.some((l) => l.nivel === "parada");
  return (
    <div>
      <div className={`flex items-center justify-between gap-3 px-4 py-3 ${faixa.fundo}`}>
        <div className="min-w-0">
          <p className={`flex items-center gap-1.5 text-[19px] leading-tight font-extrabold ${faixa.texto}`}><faixa.Icone className="size-5 shrink-0" aria-hidden />{c.veredito.texto}</p>
          <p className="mt-0.5 truncate text-[12px] text-tinta/75">{c.origem} → {c.destino}</p>
        </div>
        <div className="shrink-0 text-right leading-none">
          <p className="text-[12px] font-bold text-tinta/70">Chegada</p>
          <p className="mt-1 text-[28px] font-extrabold tracking-tight tabular-nums">{c.chegada ?? "--:--"}</p>
          <p className={`mt-1 text-[12px] ${c.atraso_min ? `font-bold ${faixa.texto}` : "text-tinta/70"}`}>{c.atraso_min ? `+${c.atraso_min} min` : c.chegada ? `${c.minutos} min de viagem` : "sem previsão"}</p>
        </div>
      </div>

      {c.problemas.length > 0 && (
        <div className="mx-4 mt-3 flex gap-2 rounded-xl border border-erro/25 bg-erro-suave/50 px-3 py-2.5">
          <XCircle className="mt-0.5 size-4 shrink-0 text-erro" aria-hidden />
          <p className="text-[13px] leading-snug">
            <span className="font-bold">{c.problemas[0]}</span>
            {c.desvio && <span className="block text-apagado">{desviando ? "O caminho de sempre não está disponível agora." : c.desvio.texto}</span>}
          </p>
        </div>
      )}

      <div className="px-4 pt-3">
        <p className="mb-2 text-[12px] font-bold text-apagado">{desviando ? "Faça assim" : "Seu caminho"}</p>
        <Caminho rota={rota} situacao={c.situacao} notaDoPrimeiro={desviando && linhaParada ? "só se o trecho estiver andando" : undefined} />
      </div>

      {c.avisos.length > 0 && (
        <div className="mx-4 mt-3 border-t border-linha pt-3">
          <p className="mb-2 text-[12px] font-bold text-apagado">Fique atento</p>
          <ul className="space-y-1.5">
            {c.avisos.map((a, i) => {
              const Icone = ICONE_AVISO[a.tipo] ?? Info;
              return (
                <li key={i} className={`flex items-start gap-2 rounded-xl px-3 py-2 text-[13px] leading-snug ${a.tipo === "pico" || a.tipo === "sem_dado" ? "bg-fundo text-tinta" : "bg-alerta-suave text-[#7a3e04]"}`}>
                  <Icone className="mt-0.5 size-4 shrink-0" aria-hidden />{a.texto}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {c.veredito.codigo !== "pode_ir" && (
        <div className="mt-3 flex gap-2 border-t border-linha px-4 py-3">
          <button type="button" disabled={esperando} onClick={() => enviar("Avisa que vou atrasar")}
            className="h-11 flex-1 rounded-full bg-tinta text-[14px] font-bold text-white hover:bg-tinta/85 disabled:opacity-50">Avisar que vou atrasar</button>
          {c.problemas.length > 0 && (
            <a href="https://www.metro.sp.gov.br/pt_BR/sua-viagem/declaracao-ocorrencias/" target="_blank" rel="noreferrer"
              className="flex items-center rounded-full bg-cinza px-4 text-[14px] font-bold hover:bg-cinza-forte">Declaração</a>
          )}
        </div>
      )}

      {temDetalhes && (
        <div className={`border-t border-linha ${c.veredito.codigo === "pode_ir" ? "mt-3" : ""}`}>
          <button type="button" aria-expanded={detalhes} onClick={() => setDetalhes(!detalhes)} className="flex w-full items-center justify-between px-4 py-3 text-[14px] font-bold">
            Segurança nas estações e energia<ChevronDown className={`size-4 transition-transform ${detalhes ? "rotate-180" : ""}`} aria-hidden />
          </button>
          {detalhes && (
            <div className="space-y-2 px-4 pb-3 text-[12px]">
              {(["saida", "chegada"] as const).map((lado) => {
                const s = c.seguranca[lado];
                return s ? (
                  <p key={lado} className="flex gap-1.5"><Shield className="mt-0.5 size-3.5 shrink-0 text-[#BE185D]" aria-hidden />
                    <span><span className="font-semibold">{s.estacao}:</span> {s.total.toLocaleString("pt-BR")} registros na SSP-SP a até 300 m, mais {FAIXA_FRASE[s.faixa] ?? s.faixa}.</span></p>
                ) : null;
              })}
              {c.energia && (
                <div className="space-y-1">
                  <p className="flex gap-1.5"><Leaf className="mt-0.5 size-3.5 shrink-0 text-ok" aria-hidden />
                    <span>De trilho, cerca de {c.energia.trilho_g} g de CO₂ e {reais(c.energia.tarifa)}. De ônibus, {kg(c.energia.onibus_g / 1000)} e {reais(c.energia.onibus_tarifa)}. De carro, {kg(c.energia.carro_kg)} e {reais(c.energia.carro_custo)} de gasolina.</span></p>
                  <p className="pl-5 font-semibold text-ok">{c.energia.renovavel}</p>
                  <p className="pl-5 text-[11px] text-apagado">{c.energia.rotulo} Premissas: {c.energia.premissas.join("; ")}.</p>
                  <p className="pl-5 text-[11px] text-apagado">Fontes: {c.energia.fontes.map((f, i) => (
                    <span key={f.url}>{i > 0 && "; "}<a href={f.url} target="_blank" rel="noreferrer" className="underline">{f.nome}</a></span>
                  ))}.</p>
                </div>
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
      <p className="flex items-center gap-1.5 text-[12px] font-semibold text-apagado"><TrainFront className="size-3.5" aria-hidden />São Paulo agora · {hora(c.lido_em)}</p>
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
      <p className="text-[12px] font-semibold text-apagado">Alertas oficiais · {hora(c.lido_em)}</p>
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
      <p className="flex items-center gap-1.5 text-[12px] font-semibold text-apagado"><MessageSquareText className="size-3.5" aria-hidden />Mensagem pronta{c.para_quem ? ` · ${c.para_quem}` : ""}</p>
      <p className="rounded-xl rounded-tl-sm bg-[#e7f6e9] px-3 py-2 text-[14px] leading-snug text-tinta">{c.texto}</p>
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={copiar} className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[13px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          {copiado ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}{copiado ? "Copiado" : "Copiar"}
        </button>
      </div>
      <p className="text-[11px] text-apagado">Copie e envie pelo canal que preferir. A Lia não envia nada sozinha.</p>
    </div>
  );
}

export function CartaoDaAuxilia({ cartao }: { cartao: Cartao }) {
  return (
    <div className={`overflow-hidden rounded-[22px] border border-linha bg-superficie ${cartao.tipo === "plano" ? "" : "p-3.5"}`}>
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
