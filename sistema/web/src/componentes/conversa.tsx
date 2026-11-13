import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";

import { assistente, mobilidade, type Alertas, type Cartao, type FalaHistorico, type Passo, type RespostaAssistente, type Viagem } from "../lib/api";

/*
 * Estado da conversa com a Lia, fora das telas: trocar de vista (notebook ou celular)
 * não perde a conversa. O chat começa pronto (saudação e atalhos, sem chamada ao servidor);
 * os alertas do canto (linhas, chuva, alagamento) são lidos à parte e atualizados a cada 2 min.
 * O que a pessoa escreve não é gravado; só a estação de casa fica no aparelho.
 */

export type Fala =
  | { id: number; de: "pessoa"; texto: string }
  | { id: number; de: "auxilia"; texto: string; cartoes: Cartao[]; aviso: string };
export type Notificacao = { titulo: string; texto: string; pedido: string };

type Contexto = {
  falas: Fala[];
  sugestoes: string[];
  esperando: boolean;
  erro: string;
  enviar: (texto: string) => void;
  reiniciar: () => void;
  /** Estação de casa guardada neste aparelho (id do GTFS), ou null. */
  casa: string | null;
  /** Esquece tudo da conversa em memória e a casa gravada: usado por "Apagar os dados deste aparelho". */
  esquecer: () => void;
  alertas: Alertas | null;
  rastro: Passo[];
  simular: string;
  setSimular: (n: string) => void;
  ultimaViagem: Viagem | null;
  aviso: Notificacao | null;
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

const CHAVE_CASA = "dt-casa";
const OCULTA = "Mensagem não exibida, porque parecia ter um dado pessoal.";

function lerCasa(): string | null {
  try {
    return localStorage.getItem(CHAVE_CASA) ?? localStorage.getItem("auxilia-casa") ?? localStorage.getItem("plano-b-casa");
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
  const [alertas, setAlertas] = useState<Alertas | null>(null);
  const [rastro, setRastro] = useState<Passo[]>([]);
  const [simular, setSimular] = useState("");
  const [ultimaViagem, setUltimaViagem] = useState<Viagem | null>(null);
  const [aviso, setAviso] = useState<Notificacao | null>(null);
  const contador = useRef(0);
  const ultimoPlano = useRef("");
  const temporizador = useRef(0);
  const falasRef = useRef<Fala[]>([]);
  falasRef.current = falas;
  const esperandoRef = useRef(false);
  esperandoRef.current = esperando;

  // alertas do canto: agora, a cada 2 minutos e quando a simulação muda
  useEffect(() => {
    let reintento = 0;
    const ler = () => {
      window.clearTimeout(reintento);
      assistente.alertas(simular || undefined).then(setAlertas)
        .catch(() => { reintento = window.setTimeout(ler, 5000); });   // servidor subindo ou fonte fora: tenta de novo logo
    };
    ler();
    const t = window.setInterval(ler, 120000);
    return () => { window.clearInterval(t); window.clearTimeout(reintento); };
  }, [simular]);

  const receber = useCallback((r: RespostaAssistente, idDaPergunta?: number) => {
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
      return [...lista, { id: ++contador.current, de: "auxilia", texto: r.texto, cartoes, aviso: r.ia.aviso ? "A IA não respondeu agora; respondi pela base do sistema." : "" }];
    });
    setSugestoes(r.sugestoes);
    if (r.rastro.length) setRastro(r.rastro);
    if (r.memoria?.casa) {
      gravarCasa(r.memoria.casa);
      setCasa(r.memoria.casa);
    }
    if (r.ultima_viagem) setUltimaViagem(r.ultima_viagem);
  }, []);

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
    setFalas([]);
    setSugestoes([]);
    setErro("");
    setRastro([]);
    setUltimaViagem(null);
    ultimoPlano.current = "";
  }, []);

  const esquecer = useCallback(() => {
    reiniciar();
    setCasa(null);
    try {
      [CHAVE_CASA, "auxilia-casa", "plano-b-casa"].forEach((c) => localStorage.removeItem(c));
    } catch {
      /* sem armazenamento */
    }
  }, [reiniciar]);

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
      notificar({ titulo: "Converse com a Lia primeiro", texto: "Diga para onde vai; o aviso usa a viagem que ela conferiu.", pedido: "Estou saindo agora" });
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
      falas, sugestoes, esperando, erro, enviar, reiniciar, casa, esquecer, alertas, rastro, simular, setSimular, ultimaViagem,
      aviso, fecharAviso, abrirAviso, simularAviso,
    }}>
      {children}
    </ContextoConversa.Provider>
  );
}
