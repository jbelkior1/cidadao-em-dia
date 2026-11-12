import { AlertTriangle, ArrowLeft, ArrowRight, CircleCheck, CloudRain, Droplets, MessageCircle, MessageSquareText, OctagonX, Route, TrainFront, type LucideIcon } from "lucide-react";
import { useMemo, useState } from "react";

import type { Cartao, CartaoPanorama, CartaoPlano } from "../../lib/api";
import { Avatar, Digitando, Entrada, Mensagens } from "../Auxilia";
import { CartaoDaAuxilia, EtapasCompactas } from "../Cartoes";
import { SeloLinha, SituacaoLinha } from "../Linha";
import { useConversa, type Fala } from "../conversa";
import { Cabecalho, type PropsLayout } from "./comum";

/*
 * Layout 3 · Painel: a primeira coisa que se vê é o status da viagem (ou da cidade);
 * as ações rápidas vêm logo abaixo e a conversa fica numa prévia compacta, com a caixa de texto fixa no rodapé.
 */

const DECISAO = {
  pode_ir: { faixa: "bg-ok-suave text-ok ring-ok/30", Icone: CircleCheck },
  mais_cedo: { faixa: "bg-alerta-suave text-alerta ring-alerta/30", Icone: AlertTriangle },
  plano_b: { faixa: "bg-erro-suave text-erro ring-erro/30", Icone: OctagonX },
} as const;

const cartao = "rounded-2xl border border-linha bg-superficie p-4 shadow-sm";

function Esqueleto() {
  return (
    <div className={`${cartao} animate-pulse space-y-3`} aria-busy="true" aria-label="Carregando a situação da cidade">
      <div className="h-9 rounded-xl bg-fundo" />
      <div className="h-4 w-2/3 rounded bg-fundo" />
      <div className="h-12 w-1/2 rounded-xl bg-fundo" />
    </div>
  );
}

function HeroViagem({ plano }: { plano: CartaoPlano }) {
  const d = DECISAO[plano.veredito.codigo];
  const motivo = plano.motivos[0];
  return (
    <section aria-label="Status da viagem" className={`${cartao} space-y-3`}>
      <div className={`flex items-center gap-2 rounded-xl px-3.5 py-3 text-[18px] leading-tight font-extrabold ring-1 ring-inset ${d.faixa}`}>
        <d.Icone className="size-6 shrink-0" aria-hidden />
        {plano.veredito.texto}
      </div>
      <p className="flex flex-wrap items-center gap-x-1.5 text-[14px] font-semibold">
        {plano.origem}<ArrowRight className="size-4 text-apagado" aria-hidden />{plano.destino}
      </p>
      <div className="flex flex-wrap items-end justify-between gap-x-4 gap-y-1">
        <div>
          <p className="text-[11px] font-semibold tracking-wide text-apagado uppercase">Chegada prevista</p>
          <p className="text-[52px] leading-none font-black tracking-tight tabular-nums">{plano.chegada ?? "--:--"}</p>
        </div>
        <p className="pb-1 text-[14px] text-apagado">
          <span className="font-semibold text-tinta">{plano.minutos} min</span> de viagem
          {plano.atraso_min > 0 && <span className="ml-1.5 rounded-full bg-alerta-suave px-2 py-0.5 text-[12px] font-bold text-alerta">+{plano.atraso_min} min de atraso</span>}
        </p>
      </div>
      {plano.linhas.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {plano.linhas.map((l) => (
            <li key={l.numero} className="flex items-center gap-1.5 rounded-xl bg-fundo py-1 pr-1.5 pl-1">
              <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
              <SituacaoLinha nivel={l.nivel} />
            </li>
          ))}
        </ul>
      )}
      {motivo && <p className="text-[14px] leading-snug text-apagado">{motivo}</p>}
    </section>
  );
}

function HeroCidade({ panorama }: { panorama: CartaoPanorama }) {
  const problemas = panorama.problemas;
  const aviso = panorama.inmet[0];
  return (
    <section aria-label="Situação da cidade agora" className={`${cartao} space-y-3`}>
      <p className="text-[11px] font-semibold tracking-wide text-apagado uppercase">A cidade agora</p>
      {problemas.length === 0 ? (
        <p className="flex items-center gap-2 rounded-xl bg-ok-suave px-3.5 py-3 text-[18px] leading-tight font-extrabold text-ok">
          <CircleCheck className="size-6 shrink-0" aria-hidden />
          {panorama.normais} {panorama.normais === 1 ? "linha normal" : "linhas normais"}
        </p>
      ) : (
        <>
          <p className="text-[14px] text-apagado"><span className="font-semibold text-tinta">{panorama.normais}</span> {panorama.normais === 1 ? "linha normal" : "linhas normais"}; com problema:</p>
          <ul className="space-y-1.5">
            {problemas.map((l) => (
              <li key={l.numero} className="flex items-center gap-2">
                <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
                <SituacaoLinha nivel={l.nivel} />
                <span className="min-w-0 truncate text-[13px] text-apagado">{l.status}</span>
              </li>
            ))}
          </ul>
        </>
      )}
      <ul className="space-y-1 text-[13px] text-apagado">
        <li className="flex items-start gap-2"><CloudRain className="mt-0.5 size-4 shrink-0" aria-hidden />
          <span><span className="font-semibold text-tinta">INMET:</span> {aviso ? `${aviso.tipo}, severidade ${aviso.severidade.toLowerCase()}` : "sem aviso de tempo severo"}</span></li>
        <li className="flex items-start gap-2"><Droplets className="mt-0.5 size-4 shrink-0" aria-hidden />
          <span><span className="font-semibold text-tinta">CGE:</span> {panorama.cge_estado ? panorama.cge_estado.titulo : "sem estado de atenção para alagamentos"}</span></li>
      </ul>
      <p className="text-[15px] font-semibold text-marca-forte">Diga para onde você vai e eu confiro o caminho.</p>
    </section>
  );
}

type Acao = { rotulo: string; pedido: string; Icone: LucideIcon };

function Acoes({ acoes, desativado, enviar }: { acoes: Acao[]; desativado: boolean; enviar: (t: string) => void }) {
  return (
    <section aria-label="Ações rápidas">
      <div className="grid grid-cols-2 gap-2.5 @xl:grid-cols-4 @3xl:grid-cols-2">
        {acoes.map((a) => (
          <button key={a.rotulo} type="button" disabled={desativado} onClick={() => enviar(a.pedido)}
            className="flex min-h-[84px] flex-col items-start justify-between gap-2 rounded-2xl border border-linha bg-superficie p-3 text-left shadow-sm hover:border-marca hover:bg-marca-suave disabled:opacity-50">
            <span className="flex size-9 items-center justify-center rounded-xl bg-marca-suave text-marca-forte"><a.Icone className="size-5" aria-hidden /></span>
            <span className="text-[14px] leading-tight font-semibold">{a.rotulo}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function Caminho({ plano }: { plano: CartaoPlano }) {
  const desvio = plano.desvio;
  const rota = desvio?.rota ?? plano.rota;
  return (
    <section aria-label={desvio ? "Outro caminho" : "Seu caminho"} className={`${cartao} space-y-3`}>
      <h2 className="flex items-center gap-2 text-[15px] font-bold"><Route className="size-4 text-marca-forte" aria-hidden />{desvio ? "Outro caminho" : "Seu caminho"}
        <span className="ml-auto text-[12px] font-semibold text-apagado">{rota.minutos} min</span></h2>
      {desvio && <p className="rounded-xl bg-erro-suave px-3 py-2 text-[13px] leading-snug text-erro">{desvio.texto}</p>}
      <EtapasCompactas rota={rota} />
    </section>
  );
}

/** Texto da fala em formato de prévia (sem cartões). */
function Previa({ f }: { f: Fala }) {
  return f.de === "pessoa" ? (
    <p className="max-w-[85%] self-end rounded-2xl rounded-br-md bg-marca px-3 py-2 text-[14px] leading-snug text-white">{f.texto}</p>
  ) : (
    <div className="flex items-end gap-2">
      <Avatar tamanho="sm" />
      <p className="max-w-[88%] rounded-2xl rounded-bl-md bg-fundo px-3 py-2 text-[14px] leading-snug">{f.texto}</p>
    </div>
  );
}

export default function LayoutPainel({ aoAbrirMenu }: PropsLayout) {
  const { falas, esperando, erro, enviar, resumo } = useConversa();
  const [completa, setCompleta] = useState(false);
  const { plano, panorama } = resumo;

  // o último cartão que não é viagem nem cidade (orientação, segurança, alertas, mensagem...)
  const extra = useMemo<Cartao | null>(() => {
    for (let i = falas.length - 1; i >= 0; i--) {
      const f = falas[i];
      if (f.de !== "auxilia") continue;
      const c = f.cartoes.filter((x) => x.tipo !== "plano" && x.tipo !== "panorama");
      if (c.length) return c[c.length - 1];
    }
    return null;
  }, [falas]);

  const precisaAvisar = !!plano && (plano.atraso_min > 0 || plano.veredito.codigo !== "pode_ir");
  const acoes: Acao[] = [
    precisaAvisar
      ? { rotulo: "Avisar que vou atrasar", pedido: "Avisa que vou atrasar", Icone: MessageSquareText }
      : { rotulo: "Saindo de casa agora", pedido: "Estou saindo de casa agora", Icone: Route },
    { rotulo: "Como estão as linhas?", pedido: "Como estão as linhas?", Icone: TrainFront },
    { rotulo: "Alerta de alagamento?", pedido: "Tem alerta de alagamento?", Icone: Droplets },
    { rotulo: "O trem parou, e agora?", pedido: "O trem parou, e agora?", Icone: AlertTriangle },
  ];

  const ultimas = falas.slice(-3);

  return (
    <div className="@container flex h-full min-h-0 flex-col bg-fundo">
      <Cabecalho aoAbrirMenu={aoAbrirMenu} />

      {completa ? (
        <>
          <div className="flex shrink-0 items-center gap-2 border-b border-linha bg-superficie px-3 py-2">
            <button type="button" onClick={() => setCompleta(false)}
              className="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-[14px] font-semibold text-marca-forte hover:bg-marca-suave">
              <ArrowLeft className="size-4" aria-hidden />Voltar ao painel
            </button>
            <p className="ml-auto text-[13px] text-apagado">Conversa completa</p>
          </div>
          <Mensagens ocultarTipos={["plano", "panorama"]} />
        </>
      ) : (
        <div className="min-h-0 flex-1 overflow-y-auto px-3 py-3 @2xl:px-6">
          <div className="mx-auto flex w-full max-w-5xl flex-col gap-3">
            <div className="grid grid-cols-1 items-start gap-3 @3xl:grid-cols-2">
              <div className="flex flex-col gap-3">
                {plano ? <HeroViagem plano={plano} /> : panorama ? <HeroCidade panorama={panorama} /> : esperando || falas.length === 0 ? <Esqueleto /> : (
                  <section className={`${cartao} space-y-1`}>
                    <p className="text-[16px] font-bold">Para onde você vai?</p>
                    <p className="text-[14px] text-apagado">Diga o destino e eu confiro linhas, chuva e alagamento antes de você sair.</p>
                  </section>
                )}
                {plano && <Caminho plano={plano} />}
                {plano && panorama && (
                  <p className="px-1 text-[12px] text-apagado">
                    {panorama.problemas.length === 0
                      ? `${panorama.normais} linhas normais na cidade agora.`
                      : `${panorama.problemas.length} ${panorama.problemas.length === 1 ? "linha com problema" : "linhas com problema"} na cidade agora.`}
                  </p>
                )}
              </div>
              <div className="flex flex-col gap-3">
                <Acoes acoes={acoes} desativado={esperando} enviar={enviar} />
                {extra && <CartaoDaAuxilia cartao={extra} />}
              </div>
            </div>

            <section aria-label="Conversa com a Auxilia" className={`${cartao} space-y-3`}>
              <div className="flex items-center gap-2">
                <MessageCircle className="size-4 text-marca-forte" aria-hidden />
                <h2 className="text-[15px] font-bold">Conversa com a Auxilia</h2>
                <button type="button" onClick={() => setCompleta(true)}
                  className="ml-auto rounded-lg px-2 py-1 text-[13px] font-semibold text-marca-forte hover:bg-marca-suave">Ver conversa completa</button>
              </div>
              <div className="flex flex-col gap-2" aria-live="polite">
                {ultimas.length === 0 && !esperando && <p className="text-[13px] text-apagado">Nenhuma mensagem ainda.</p>}
                {ultimas.map((f) => <Previa key={f.id} f={f} />)}
                {esperando && <Digitando />}
                {erro && <p className="rounded-xl bg-erro-suave px-3 py-2 text-[13px] text-erro">{erro}</p>}
              </div>
            </section>
          </div>
        </div>
      )}

      <Entrada semSugestoes />
    </div>
  );
}
