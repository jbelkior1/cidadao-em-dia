import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";

import {
  assistente, mobilidade, type Cartao, type CartaoAlertas, type CartaoPanorama, type CartaoPlano, type FalaHistorico, type Passo,
  type RespostaAssistente, type Viagem,
} from "../lib/api";

/*
 * Estado da conversa com a Auxilia, fora das telas: assim os layouts podem ser trocados
 * sem perder a conversa. Guarda as falas, as sugestões, o resumo vivo (cidade agora,
 * viagem atual, alertas), quem fez cada parte (modo banca) e o aviso que chega no celular.
 * O que a pessoa escreve não é gravado; só a estação de casa fica no aparelho.
 */

export type Fala =
  | { id: number; de: "pessoa"; texto: string }
  | { id: number; de: "auxilia"; texto: string; cartoes: Cartao[]; aviso: string };
export type Notificacao = { titulo: string; texto: string; pedido: string };
export type Resumo = { panorama: CartaoPanorama | null; plano: CartaoPlano | null; alertas: CartaoAlertas | null };

type Contexto = {
  falas: Fala[];
  sugestoes: string[];
  esperando: boolean;
  erro: string;
  enviar: (texto: string) => void;
  reiniciar: () => void;
  resumo: Resumo;
  rastro: Passo[];
  simular: string;
  setSimular: (n: string) => void;
  ultimaViagem: Viagem | null;
  aviso: Notificacao | null;
  notificar: (n: Notificacao) => void;
  fecharAviso: () => void;
  abrirAviso: () => void;
  simularAviso: () => Promise<void>;
};

const ContextoConversa = createContext<Contexto | null>(null);

export function useConversa(): Contexto {
  const c = useContext(ContextoConversa);
  if (!c) throw new Error("useConversa precisa estar dentro de <ProvedorConversa>");
  return c;
}

const CHAVE_CASA = "auxilia-casa";
const OCULTA = "Mensagem não exibida, porque parecia ter um dado pessoal.";

function lerCasa(): string | null {
  try {
    return localStorage.getItem(CHAVE_CASA) ?? localStorage.getItem("plano-b-casa");
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

export function ProvedorConversa({ children }: { children: ReactNode }) {
  const [falas, setFalas] = useState<Fala[]>([]);
  const [sugestoes, setSugestoes] = useState<string[]>([]);
  const [esperando, setEsperando] = useState(false);
  const [erro, setErro] = useState("");
  const [casa, setCasa] = useState<string | null>(lerCasa);
  const [resumo, setResumo] = useState<Resumo>({ panorama: null, plano: null, alertas: null });
  const [rastro, setRastro] = useState<Passo[]>([]);
  const [simular, setSimular] = useState("");
  const [ultimaViagem, setUltimaViagem] = useState<Viagem | null>(null);
  const [aviso, setAviso] = useState<Notificacao | null>(null);
  const [reinicio, setReinicio] = useState(0);
  const contador = useRef(0);
  const ultimoPlano = useRef("");
  const temporizador = useRef(0);
  const falasRef = useRef<Fala[]>([]);
  falasRef.current = falas;

  const receber = useCallback((r: RespostaAssistente, idDaPergunta?: number) => {
    // o cartão da viagem só aparece de novo na conversa quando algo mudou (decisão, chegada ou simulação)
    const cartoes = r.cartoes.filter((c) => {
      if (c.tipo !== "plano") return true;
      const assinatura = [c.origem, c.destino, c.veredito.codigo, c.chegada, c.simulacao].join("|");
      if (assinatura === ultimoPlano.current) return false;
      ultimoPlano.current = assinatura;
      return true;
    });
    setFalas((atual) => {
      const lista = r.recusa && idDaPergunta ? atual.map((f) => (f.id === idDaPergunta && f.de === "pessoa" ? { ...f, texto: OCULTA } : f)) : atual;
      return [...lista, { id: ++contador.current, de: "auxilia", texto: r.texto, cartoes, aviso: r.ia.aviso ? "A IA não respondeu agora; respondi pela base do sistema." : "" }];
    });
    setResumo((atual) => {
      const novo = { ...atual };
      for (const c of r.cartoes) {
        if (c.tipo === "panorama") novo.panorama = c;
        if (c.tipo === "plano") novo.plano = c;
        if (c.tipo === "alertas") novo.alertas = c;
      }
      return novo;
    });
    setSugestoes(r.sugestoes);
    if (r.rastro.length) setRastro(r.rastro);
    if (r.memoria?.casa) {
      gravarCasa(r.memoria.casa);
      setCasa(r.memoria.casa);
    }
    if (r.ultima_viagem) setUltimaViagem(r.ultima_viagem);
  }, []);

  // a Auxilia abre a conversa (e de novo em "nova conversa")
  const aberto = useRef(-1);
  useEffect(() => {
    if (aberto.current === reinicio) return;            // o React monta duas vezes em desenvolvimento
    aberto.current = reinicio;
    setFalas([]);
    setErro("");
    setRastro([]);
    setResumo({ panorama: null, plano: null, alertas: null });
    ultimoPlano.current = "";
    setEsperando(true);
    assistente.inicio(lerCasa(), simular || undefined)
      .then((r) => receber(r))
      .catch(() => setErro("Não consegui falar com o servidor. Confira se a API está ligada na porta 8010."))
      .finally(() => setEsperando(false));
  }, [reinicio]);

  const esperandoRef = useRef(false);
  esperandoRef.current = esperando;
  const enviar = useCallback((mensagem: string) => {
    const limpo = mensagem.trim();
    if (!limpo || esperandoRef.current) return;
    const id = ++contador.current;
    const historico: FalaHistorico[] = falasRef.current.slice(-10).map((f) => ({ papel: f.de === "pessoa" ? "pessoa" : "plano", texto: f.texto }));
    setFalas((atual) => [...atual, { id, de: "pessoa", texto: limpo }]);
    setSugestoes([]);
    setEsperando(true);
    setErro("");
    assistente.responder(limpo, historico, { casa, ultima_viagem: ultimaViagem }, simular || undefined)
      .then((r) => receber(r, id))
      .catch((e) => setErro(e instanceof Error ? e.message : "Algo deu errado. Tente de novo."))
      .finally(() => setEsperando(false));
  }, [casa, ultimaViagem, simular, receber]);

  const reiniciar = useCallback(() => {
    setUltimaViagem(null);
    setReinicio((n) => n + 1);
  }, []);

  const notificar = useCallback((n: Notificacao) => {
    setAviso(n);
    window.clearTimeout(temporizador.current);
    temporizador.current = window.setTimeout(() => setAviso(null), 10000);
  }, []);
  const fecharAviso = useCallback(() => setAviso(null), []);
  const abrirAviso = useCallback(() => {
    if (aviso) enviar(aviso.pedido);
    setAviso(null);
  }, [aviso, enviar]);

  const simularAviso = useCallback(async () => {
    if (!ultimaViagem) {
      notificar({ titulo: "Converse com a Auxilia primeiro", texto: "Diga para onde vai; o aviso usa a viagem que ela conferiu.", pedido: "Estou saindo de casa agora" });
      return;
    }
    const p = await mobilidade.plano(ultimaViagem.origem, ultimaViagem.destino, simular || undefined);
    const falha = p.linhas.find((l) => l.nivel === "parada" || l.nivel === "atencao");
    notificar({
      pode_ir: { titulo: "Pode sair no horário", texto: `Linhas ${p.rota.linhas.join(" e ")} normais até ${p.destino}.`, pedido: "Vi o aviso. Posso ir mesmo?" },
      mais_cedo: { titulo: "Saia um pouco mais cedo", texto: p.motivos.find((m) => m.tipo === "chuva" || m.tipo === "alagamento")?.texto ?? "Seu caminho deve estar mais lento hoje.", pedido: "Vi o aviso. O que está acontecendo no caminho?" },
      plano_b: { titulo: `Linha ${falha?.numero ?? ""} com problema`, texto: `Antes de sair: vai precisar mudar o caminho até ${p.destino}.`, pedido: "Vi o aviso. Qual é o outro caminho?" },
    }[p.veredito.codigo]);
  }, [ultimaViagem, simular, notificar]);

  return (
    <ContextoConversa.Provider value={{
      falas, sugestoes, esperando, erro, enviar, reiniciar, resumo, rastro, simular, setSimular, ultimaViagem,
      aviso, notificar, fecharAviso, abrirAviso, simularAviso,
    }}>
      {children}
    </ContextoConversa.Provider>
  );
}
