import { ArrowUp, X } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";

import type { Cartao } from "../lib/api";
import { CartaoDaAuxilia } from "./Cartoes";
import { useConversa, type Notificacao } from "./conversa";

/*
 * Peças da conversa com a Auxilia, para os layouts montarem do jeito deles:
 * - <Mensagens />: as falas, com os cartões dentro;
 * - <Entrada />: sugestões e caixa de texto;
 * - <Avatar />, <Digitando />, <AvisoNoAparelho />.
 * O estado fica em ./conversa (ProvedorConversa), então trocar de layout não perde nada.
 */

export function Avatar({ tamanho = "md" }: { tamanho?: "sm" | "md" | "lg" }) {
  const medida = tamanho === "sm" ? "size-7 text-[12px]" : tamanho === "lg" ? "size-12 text-[18px]" : "size-9 text-[14px]";
  return (
    <span className={`flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-marca to-[#14917f] font-black text-white ${medida}`} aria-hidden>
      A
    </span>
  );
}

export function Digitando() {
  return (
    <div className="flex items-end gap-2" aria-label="A Auxilia está escrevendo">
      <Avatar tamanho="sm" />
      <span className="flex gap-1 rounded-2xl rounded-bl-md bg-superficie px-4 py-3 shadow-sm ring-1 ring-linha">
        {[0, 150, 300].map((d) => <span key={d} className="size-2 animate-bounce rounded-full bg-apagado/60" style={{ animationDelay: `${d}ms` }} />)}
      </span>
    </div>
  );
}

/**
 * Lista de falas. `semCartoes` mostra só o texto; `ocultarTipos` esconde só alguns tipos de cartão
 * (por exemplo ["plano", "panorama"], quando o layout mostra a viagem e a cidade num painel fixo).
 */
export function Mensagens({ semCartoes = false, ocultarTipos = [], className = "" }: { semCartoes?: boolean; ocultarTipos?: Cartao["tipo"][]; className?: string }) {
  const { falas, esperando, erro } = useConversa();
  const fim = useRef<HTMLDivElement>(null);
  useEffect(() => {
    fim.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [falas, esperando]);
  return (
    <div className={`min-h-0 flex-1 overflow-y-auto px-3 py-4 @2xl:px-6 ${className}`} aria-live="polite">
      <div className="mx-auto flex w-full max-w-2xl flex-col gap-3">
        {falas.map((f) =>
          f.de === "pessoa" ? (
            <p key={f.id} className="entrar max-w-[82%] self-end rounded-2xl rounded-br-md bg-marca px-3.5 py-2.5 text-[15px] leading-snug whitespace-pre-wrap text-white">{f.texto}</p>
          ) : (
            <div key={f.id} className="entrar flex items-end gap-2">
              <Avatar tamanho="sm" />
              <div className="flex min-w-0 max-w-[88%] flex-col gap-2">
                <p className="rounded-2xl rounded-bl-md bg-superficie px-3.5 py-2.5 text-[15px] leading-snug shadow-sm ring-1 ring-linha">{f.texto}</p>
                {!semCartoes && f.cartoes.filter((c) => !ocultarTipos.includes(c.tipo)).map((c, i) => <CartaoDaAuxilia key={i} cartao={c} />)}
                {f.aviso && <p className="text-[11px] text-apagado">{f.aviso}</p>}
              </div>
            </div>
          ),
        )}
        {esperando && <Digitando />}
        {erro && <p className="rounded-xl bg-erro-suave px-3 py-2 text-[14px] text-erro">{erro}</p>}
        <div ref={fim} />
      </div>
    </div>
  );
}

/** Sugestões e caixa de texto. */
export function Entrada({ placeholder = "Ex.: estou saindo de casa agora", semSugestoes = false }: { placeholder?: string; semSugestoes?: boolean }) {
  const { sugestoes, esperando, enviar } = useConversa();
  const [texto, setTexto] = useState("");
  const aoEnviar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!texto.trim() || esperando) return;
    enviar(texto);
    setTexto("");
  };
  return (
    <div className="shrink-0 border-t border-linha bg-superficie px-3 pt-2 pb-3 @2xl:px-6">
      <div className="mx-auto w-full max-w-2xl space-y-2">
        {!semSugestoes && sugestoes.length > 0 && !esperando && (
          <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none]">
            {sugestoes.map((s) => (
              <button key={s} type="button" onClick={() => enviar(s)}
                className="shrink-0 rounded-full bg-marca-suave px-3 py-1.5 text-[13px] font-semibold whitespace-nowrap text-marca-forte hover:bg-marca hover:text-white">
                {s}
              </button>
            ))}
          </div>
        )}
        <form onSubmit={aoEnviar} className="flex items-center gap-2">
          <label htmlFor="mensagem-auxilia" className="sr-only">Mensagem para a Auxilia</label>
          <input id="mensagem-auxilia" value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={1000} autoComplete="off" placeholder={placeholder}
            className="h-11 min-w-0 flex-1 rounded-full border border-linha bg-fundo px-4 text-[15px] placeholder:text-apagado focus:border-marca focus:outline-none" />
          <button type="submit" disabled={esperando || !texto.trim()} aria-label="Enviar"
            className="flex size-11 shrink-0 items-center justify-center rounded-full bg-marca text-white hover:bg-marca-forte disabled:opacity-40">
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
    <div role="alert" className={`entrar z-30 flex items-start gap-3 rounded-2xl bg-superficie/95 p-3 shadow-xl ring-1 ring-linha backdrop-blur ${flutuante ? "fixed top-20 right-6 w-80" : "absolute inset-x-3 top-11"}`}>
      <Avatar />
      <button type="button" className="min-w-0 flex-1 text-left" onClick={aoAbrir}>
        <span className="flex items-center justify-between text-[11px] text-apagado"><span className="font-semibold">AUXILIA</span><span>agora</span></span>
        <span className="block text-[14px] font-semibold">{n.titulo}</span>
        <span className="block text-[13px] text-tinta/80">{n.texto}</span>
      </button>
      <button type="button" aria-label="Fechar aviso" onClick={aoFechar} className="rounded-full p-1 text-apagado hover:bg-fundo"><X className="size-4" /></button>
    </div>
  );
}
