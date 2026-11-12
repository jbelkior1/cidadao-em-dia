import { ArrowUp } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent } from "react";

import { assistente, type Cartao, type FalaHistorico, type RespostaAssistente } from "../lib/api";
import { CartaoDaAuxilia } from "./Cartoes";
import { useSistema } from "./Celular";

/*
 * A conversa com a Auxilia. Ela fala primeiro, com a situação real da cidade,
 * e conduz: pergunta para onde a pessoa vai, de onde sai, e responde com cartões.
 * O que a pessoa escreve não fica guardado; só a estação de casa fica no aparelho.
 */

type Fala =
  | { id: number; de: "pessoa"; texto: string }
  | { id: number; de: "auxilia"; texto: string; cartoes: Cartao[]; aviso: string };

const CHAVE_CASA = "plano-b-casa";
const OCULTA = "Mensagem não exibida, porque parecia ter um dado pessoal.";

function lerCasa(): string | null {
  try {
    return localStorage.getItem(CHAVE_CASA);
  } catch {
    return null;
  }
}
function gravarCasa(id: string) {
  try {
    localStorage.setItem(CHAVE_CASA, id);
  } catch {
    /* sem armazenamento, vale só nesta conversa */
  }
}

export function Avatar({ tamanho = "md" }: { tamanho?: "sm" | "md" }) {
  return (
    <span className={`flex shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-marca to-[#14917f] font-black text-white ${tamanho === "sm" ? "size-7 text-[12px]" : "size-9 text-[14px]"}`} aria-hidden>
      A
    </span>
  );
}

function Digitando() {
  return (
    <div className="flex items-end gap-2" aria-label="A Auxilia está escrevendo">
      <Avatar tamanho="sm" />
      <span className="flex gap-1 rounded-2xl rounded-bl-md bg-superficie px-4 py-3 shadow-sm ring-1 ring-linha">
        {[0, 150, 300].map((d) => <span key={d} className="size-2 animate-bounce rounded-full bg-apagado/60" style={{ animationDelay: `${d}ms` }} />)}
      </span>
    </div>
  );
}

export default function Auxilia() {
  const { simular, setRastro, setUltimaViagem, ultimaViagem, pedido, limparPedido, reinicio } = useSistema();
  const [falas, setFalas] = useState<Fala[]>([]);
  const [sugestoes, setSugestoes] = useState<string[]>([]);
  const [texto, setTexto] = useState("");
  const [esperando, setEsperando] = useState(false);
  const [erro, setErro] = useState("");
  const [casa, setCasa] = useState<string | null>(lerCasa);
  const fim = useRef<HTMLDivElement>(null);
  const contador = useRef(0);
  const novoId = () => ++contador.current;

  const ultimoPlano = useRef("");
  const receber = (r: RespostaAssistente, idDaPergunta?: number) => {
    // o cartão da viagem só aparece de novo quando algo mudou (decisão, chegada ou simulação)
    const cartoes = r.cartoes.filter((c) => {
      if (c.tipo !== "plano") return true;
      const assinatura = [c.origem, c.destino, c.veredito.codigo, c.chegada, c.simulacao].join("|");
      if (assinatura === ultimoPlano.current) return false;
      ultimoPlano.current = assinatura;
      return true;
    });
    setFalas((atual) => {
      const lista = r.recusa && idDaPergunta ? atual.map((f) => (f.id === idDaPergunta && f.de === "pessoa" ? { ...f, texto: OCULTA } : f)) : atual;
      return [...lista, { id: novoId(), de: "auxilia", texto: r.texto, cartoes, aviso: r.ia.aviso ? "A IA não respondeu agora; respondi pela base do sistema." : "" }];
    });
    setSugestoes(r.sugestoes);
    if (r.rastro.length) setRastro(r.rastro);
    if (r.memoria?.casa) {
      gravarCasa(r.memoria.casa);
      setCasa(r.memoria.casa);
    }
    if (r.ultima_viagem) setUltimaViagem(r.ultima_viagem);
  };

  // A Auxilia abre a conversa (e de novo quando a banca pede "nova conversa")
  const aberto = useRef(-1);
  useEffect(() => {
    if (aberto.current === reinicio) return;            // o React monta duas vezes em desenvolvimento
    aberto.current = reinicio;
    setFalas([]);
    setErro("");
    ultimoPlano.current = "";
    setEsperando(true);
    assistente.inicio(lerCasa(), simular || undefined)
      .then((r) => receber(r))
      .catch(() => setErro("Não consegui falar com o servidor. Confira se a API está ligada na porta 8010."))
      .finally(() => setEsperando(false));
  }, [reinicio]);

  useEffect(() => {
    fim.current?.scrollIntoView({ block: "end", behavior: "smooth" });
  }, [falas, esperando]);

  const enviar = async (mensagem: string) => {
    const limpo = mensagem.trim();
    if (!limpo || esperando) return;
    const id = novoId();
    const historico: FalaHistorico[] = falas.slice(-10).map((f) => ({ papel: f.de === "pessoa" ? "pessoa" : "plano", texto: f.texto }));
    setFalas((atual) => [...atual, { id, de: "pessoa", texto: limpo }]);
    setTexto("");
    setSugestoes([]);
    setEsperando(true);
    setErro("");
    try {
      receber(await assistente.responder(limpo, historico, { casa, ultima_viagem: ultimaViagem }, simular || undefined), id);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Algo deu errado. Tente de novo.");
    } finally {
      setEsperando(false);
    }
  };

  // um toque no aviso do celular vira mensagem na conversa
  useEffect(() => {
    if (pedido) {
      void enviar(pedido);
      limparPedido();
    }
  }, [pedido]);

  const aoEnviar = (evento: FormEvent) => {
    evento.preventDefault();
    void enviar(texto);
  };

  return (
    <div className="flex h-full flex-col">
      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4 @2xl:px-6" aria-live="polite">
        <div className="mx-auto flex w-full max-w-2xl flex-col gap-3">
          {falas.map((f) =>
            f.de === "pessoa" ? (
              <p key={f.id} className="entrar max-w-[82%] self-end rounded-2xl rounded-br-md bg-marca px-3.5 py-2.5 text-[15px] leading-snug whitespace-pre-wrap text-white">{f.texto}</p>
            ) : (
              <div key={f.id} className="entrar flex items-end gap-2">
                <Avatar tamanho="sm" />
                <div className="flex min-w-0 max-w-[88%] flex-col gap-2">
                  <p className="rounded-2xl rounded-bl-md bg-superficie px-3.5 py-2.5 text-[15px] leading-snug shadow-sm ring-1 ring-linha">{f.texto}</p>
                  {f.cartoes.map((c, i) => <CartaoDaAuxilia key={i} cartao={c} />)}
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

      <div className="shrink-0 border-t border-linha bg-superficie px-3 pt-2 pb-3 @2xl:px-6">
        <div className="mx-auto w-full max-w-2xl space-y-2">
          {sugestoes.length > 0 && !esperando && (
            <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-0.5 [scrollbar-width:none]">
              {sugestoes.map((s) => (
                <button key={s} type="button" onClick={() => void enviar(s)}
                  className="shrink-0 rounded-full bg-marca-suave px-3 py-1.5 text-[13px] font-semibold whitespace-nowrap text-marca-forte hover:bg-marca hover:text-white">
                  {s}
                </button>
              ))}
            </div>
          )}
          <form onSubmit={aoEnviar} className="flex items-center gap-2">
            <label htmlFor="mensagem-auxilia" className="sr-only">Mensagem para a Auxilia</label>
            <input id="mensagem-auxilia" value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={1000} autoComplete="off"
              placeholder="Ex.: estou saindo de casa agora"
              className="h-11 min-w-0 flex-1 rounded-full border border-linha bg-fundo px-4 text-[15px] placeholder:text-apagado focus:border-marca focus:outline-none" />
            <button type="submit" disabled={esperando || !texto.trim()} aria-label="Enviar"
              className="flex size-11 shrink-0 items-center justify-center rounded-full bg-marca text-white hover:bg-marca-forte disabled:opacity-40">
              <ArrowUp className="size-5" aria-hidden />
            </button>
          </form>
          <p className="text-center text-[11px] text-apagado">Não escreva CPF, telefone, endereço nem senha. Não é canal oficial das operadoras.</p>
        </div>
      </div>
    </div>
  );
}
