import { ArrowUp, X } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent, type ReactNode } from "react";

import { CartaoDaAuxilia } from "./Cartoes";
import { useConversa, type Notificacao } from "./conversa";

/*
 * Peças da conversa com a Lia, para os layouts montarem do jeito deles:
 * - <Mensagens />: as falas, com os cartões dentro;
 * - <Entrada />: sugestões e caixa de texto;
 * - <Avatar />, <Digitando />, <AvisoNoAparelho />.
 * O estado fica em ./conversa (ProvedorConversa), então trocar de layout não perde nada.
 */

export function Avatar({ tamanho = "md" }: { tamanho?: "sm" | "md" | "lg" }) {
  const medida = tamanho === "sm" ? "size-7 text-[12px]" : tamanho === "lg" ? "size-12 text-[18px]" : "size-9 text-[14px]";
  return (
    <span className={`flex shrink-0 items-center justify-center rounded-full bg-marca font-black tracking-tighter text-white ${medida}`} aria-hidden>
      L
    </span>
  );
}

export function Digitando() {
  return (
    <div className="flex items-end gap-2" aria-label="A Lia está escrevendo">
      <Avatar tamanho="sm" />
      <span className="flex gap-1 rounded-[20px] rounded-bl-md bg-cinza px-4 py-3.5">
        {[0, 150, 300].map((d) => <span key={d} className="size-2 animate-bounce rounded-full bg-apagado/60" style={{ animationDelay: `${d}ms` }} />)}
      </span>
    </div>
  );
}

const ATALHOS: { titulo: string; sub: string; mensagem: string; icone: ReactNode }[] = [
  { titulo: "Estou saindo agora", sub: "caminho e hora de chegada", mensagem: "Estou saindo agora",
    icone: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M3 12h12" /><path d="m11 6 6 6-6 6" /><path d="M21 4v16" /></svg> },
  { titulo: "Como estão as linhas?", sub: "trem e metrô agora", mensagem: "Como estão as linhas agora?",
    icone: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="5" y="3" width="14" height="14" rx="3" /><path d="M5 11h14" /><path d="m8 21 2-4" /><path d="m16 21-2-4" /></svg> },
  { titulo: "Vai chover ou alagar?", sub: "INMET e Defesa Civil (CGE)", mensagem: "Vai chover ou alagar no caminho?",
    icone: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M7 16a5 5 0 1 1 1-9.9A6 6 0 0 1 19.5 9 4 4 0 0 1 18 17H7z" /><path d="M8 20l1-2" /><path d="M12 21l1-2" /><path d="M16 20l1-2" /></svg> },
  { titulo: "O trem parou", sub: "o que fazer e seus direitos", mensagem: "O trem parou, e agora?",
    icone: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M9 9h6v6H9z" /></svg> },
];

/** A saudação de sempre e, enquanto a conversa está vazia, os atalhos para começar. */
function Inicio() {
  const { falas, esperando, enviar } = useConversa();
  return (
    <>
      <div className="entrar flex items-end gap-2">
        <Avatar tamanho="sm" />
        <p className="max-w-[88%] rounded-[20px] rounded-bl-md bg-cinza px-4 py-3 text-[16px] leading-snug">
          Oi! Como posso te auxiliar na sua viagem hoje? Me diga de onde você sai e para onde vai, ou escolha um atalho.
        </p>
      </div>
      {falas.length === 0 && (
        <div className="entrar ml-9 space-y-2">
          <p className="pt-1 text-[14px] font-bold">Comece por aqui</p>
          <div className="grid grid-cols-2 gap-2.5 @2xl:grid-cols-4">
            {ATALHOS.map((a) => (
              <button key={a.titulo} type="button" disabled={esperando} onClick={() => enviar(a.mensagem)}
                className="flex min-h-[112px] flex-col items-start gap-2.5 rounded-2xl bg-cinza p-3.5 text-left hover:bg-cinza-forte disabled:opacity-50">
                <span className="flex size-10 items-center justify-center rounded-full bg-superficie">{a.icone}</span>
                <span className="text-[16px] leading-tight font-bold">{a.titulo}</span>
                <span className="text-[12px] leading-snug text-apagado">{a.sub}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

/** Lista de falas, com a saudação e os atalhos no começo. */
export function Mensagens({ className = "" }: { className?: string }) {
  const { falas, esperando, erro } = useConversa();
  const fim = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (falas.length) fim.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [falas, esperando]);
  return (
    <div className={`min-h-0 flex-1 overflow-y-auto px-3 py-4 @2xl:px-6 ${className}`} aria-live="polite">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-3">
        <Inicio />
        {falas.map((f) =>
          f.de === "pessoa" ? (
            <p key={f.id} className="entrar max-w-[82%] self-end rounded-[20px] rounded-br-md bg-tinta px-4 py-3 text-[16px] leading-snug whitespace-pre-wrap text-white">{f.texto}</p>
          ) : (
            <div key={f.id} className="entrar flex items-start gap-2">
              <Avatar tamanho="sm" />
              <div className="flex min-w-0 max-w-[90%] flex-1 flex-col gap-2">
                <p className="w-fit rounded-[20px] rounded-bl-md bg-cinza px-4 py-3 text-[16px] leading-snug">{f.texto}</p>
                {f.cartoes.map((c, i) => <CartaoDaAuxilia key={i} cartao={c} />)}
                {f.aviso && <p className="text-[11px] text-apagado">{f.aviso}</p>}
              </div>
            </div>
          ),
        )}
        {esperando && <Digitando />}
        {erro && <p className="rounded-2xl bg-erro-suave px-4 py-3 text-[14px] text-erro">{erro}</p>}
        <div ref={fim} />
      </div>
    </div>
  );
}

/** Sugestões e caixa de texto. */
export function Entrada({ placeholder = "Ex.: estou no Capão Redondo e vou para o Campo Limpo", semSugestoes = false }: { placeholder?: string; semSugestoes?: boolean }) {
  const { sugestoes, esperando, enviar } = useConversa();
  const [texto, setTexto] = useState("");
  const aoEnviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!texto.trim() || esperando) return;
    enviar(texto);
    setTexto("");
  };
  return (
    <div className="shrink-0 bg-superficie px-3 pt-2 pb-3 @2xl:px-6">
      <div className="mx-auto w-full max-w-2xl space-y-2">
        {!semSugestoes && sugestoes.length > 0 && !esperando && (
          <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none]">
            {sugestoes.map((s) => (
              <button key={s} type="button" onClick={() => enviar(s)}
                className="h-9 shrink-0 rounded-full bg-cinza px-4 text-[14px] font-bold whitespace-nowrap hover:bg-cinza-forte">
                {s}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={aoEnviar} className="flex items-center gap-2">
          <label htmlFor="mensagem-auxilia" className="sr-only">Mensagem para a Lia</label>
          <input id="mensagem-auxilia" value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={1000} autoComplete="off" placeholder={placeholder}
            className="h-[52px] min-w-0 flex-1 rounded-full bg-cinza px-5 text-[16px] font-medium placeholder:font-normal placeholder:text-apagado focus:bg-superficie focus:ring-2 focus:ring-tinta focus:outline-none" />
          <button type="submit" disabled={esperando || !texto.trim()} aria-label="Enviar"
            className="flex size-[52px] shrink-0 items-center justify-center rounded-full bg-tinta text-white hover:bg-tinta/85 disabled:bg-cinza-forte disabled:text-apagado">
            <ArrowUp className="size-5" aria-hidden />
          </button>
        </form>
        <p className="text-center text-[11px] text-apagado">Não escreva CPF, telefone, endereço nem senha. Não é canal oficial das operadoras.</p>
      </div>
    </div>
  );
}

/** O aviso que chega no aparelho antes de sair (tocar continua a conversa). */
export function AvisoNoAparelho({ flutuante = false }: { flutuante?: boolean }) {
  const { aviso, abrirAviso, fecharAviso } = useConversa();
  if (!aviso) return null;
  return <CaixaDeAviso n={aviso} aoAbrir={abrirAviso} aoFechar={fecharAviso} flutuante={flutuante} />;
}

function CaixaDeAviso({ n, aoAbrir, aoFechar, flutuante }: { n: Notificacao; aoAbrir: () => void; aoFechar: () => void; flutuante: boolean }) {
  return (
    <div role="alert" className={`entrar z-30 flex items-start gap-3 rounded-3xl bg-superficie/95 p-3.5 shadow-flutua backdrop-blur ${flutuante ? "fixed top-20 right-6 w-80" : "absolute inset-x-3 top-11"}`}>
      <Avatar />
      <button type="button" className="min-w-0 flex-1 text-left" onClick={aoAbrir}>
        <span className="flex items-center justify-between text-[11px] text-apagado"><span className="font-semibold">Dá Tempo?</span><span>agora</span></span>
        <span className="block text-[14px] font-semibold">{n.titulo}</span>
        <span className="block text-[13px] text-tinta/80">{n.texto}</span>
      </button>
      <button type="button" aria-label="Fechar aviso" onClick={aoFechar} className="rounded-full p-1 text-apagado hover:bg-fundo"><X className="size-4" /></button>
    </div>
  );
}
