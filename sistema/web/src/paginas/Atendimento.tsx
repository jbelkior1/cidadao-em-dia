import { RotateCcw, Send } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useApp } from "../App";
import { BlocoDaConversa } from "../componentes/Blocos";
import { api, CORES_DAS_MATERIAS, type Bloco, type Opcao, type Passo, type RespostaChat, type Resumo } from "../lib/api";

type Fala = { id: number; de: "cidadao"; texto: string } | { id: number; de: "sistema"; blocos: Bloco[] };

const OCULTA = "Mensagem não exibida, porque parecia ter um dado pessoal.";

export default function Atendimento() {
  const { modoBanca } = useApp();
  const [falas, setFalas] = useState<Fala[]>([]);
  const [estado, setEstado] = useState<Record<string, unknown>>({});
  const [rastro, setRastro] = useState<Passo[]>([]);
  const [resumo, setResumo] = useState<Resumo>(null);
  const [texto, setTexto] = useState("");
  const [esperando, setEsperando] = useState(false);
  const [erro, setErro] = useState("");
  const fim = useRef<HTMLDivElement>(null);
  const contador = useRef(0);
  const novoId = () => ++contador.current;

  const receber = (r: RespostaChat, idDaPergunta?: number) => {
    const recusada = r.blocos.some((b) => b.tipo === "recusa");
    setFalas((atual) => {
      const lista = recusada && idDaPergunta ? atual.map((f) => (f.id === idDaPergunta && f.de === "cidadao" ? { ...f, texto: OCULTA } : f)) : atual;
      return [...lista, { id: novoId(), de: "sistema", blocos: r.blocos }];
    });
    setEstado(r.estado);
    if (r.rastro.length) setRastro(r.rastro);
    if (r.resumo) setResumo(r.resumo);
  };

  const local = useLocation();
  const navegar = useNavigate();

  const comecar = (inicial?: { acao: string; rotulo: string }) => {
    setFalas([]);
    setRastro([]);
    setResumo(null);
    setErro("");
    api
      .inicio()
      .then(async (r) => {
        receber(r);
        if (inicial) {
          const id = novoId();
          setFalas((atual) => [...atual, { id, de: "cidadao", texto: inicial.rotulo }]);
          receber(await api.chat({ acao: inicial.acao, estado: {} }), id);
        }
      })
      .catch(() => setErro("Não consegui falar com o servidor. Confira se a API está ligada na porta 8010."));
  };
  const iniciado = useRef(false);
  useEffect(() => {
    if (iniciado.current) return; // em desenvolvimento o React monta duas vezes; a saudação vem uma vez só
    iniciado.current = true;
    const pedido = local.state as { acao?: string; rotulo?: string } | null;
    comecar(pedido?.acao ? { acao: pedido.acao, rotulo: pedido.rotulo ?? "Começar" } : undefined);
    if (pedido?.acao) navegar(".", { replace: true, state: null });   // recarregar a página não repete o pedido
  }, []);
  useEffect(() => {
    // Entre chaves de propósito: nos navegadores novos scrollIntoView devolve uma Promise, e o efeito não pode devolvê-la.
    fim.current?.scrollIntoView({ block: "end" });
  }, [falas, esperando]);

  const enviar = async (corpo: { texto?: string; acao?: string }, comoAparece: string) => {
    if (esperando) return;
    const id = novoId();
    setFalas((atual) => [...atual, { id, de: "cidadao", texto: comoAparece }]);
    setEsperando(true);
    setErro("");
    try {
      receber(await api.chat({ ...corpo, estado }), id);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Algo deu errado. Tente de novo.");
    } finally {
      setEsperando(false);
    }
  };

  const aoEnviarTexto = (evento?: FormEvent) => {
    evento?.preventDefault();
    const limpo = texto.trim();
    if (!limpo) return;
    setTexto("");
    // Mensagem colada para conferir golpe: na tela, números longos e e-mails aparecem ocultos.
    const naTela = colando ? limpo.replace(/[\w.+-]+@[\w-]+(\.[\w-]+)+/g, "[e-mail oculto]").replace(/\d[\d.\-\s()]{6,}\d/g, "[número oculto]") : limpo;
    void enviar({ texto: limpo }, naTela);
  };
  const aoTeclar = (evento: KeyboardEvent<HTMLTextAreaElement>) => {
    if (evento.key === "Enter" && !evento.shiftKey) {
      evento.preventDefault();
      aoEnviarTexto();
    }
  };
  const aoClicar = (opcao: Opcao) => void enviar({ acao: opcao.acao }, opcao.rotulo);

  const ultimaDoSistema = [...falas].reverse().find((f) => f.de === "sistema")?.id;
  const colando = estado.etapa === "golpe";

  return (
    <div className="flex h-full">
      <section className="flex min-w-0 flex-1 flex-col" aria-label="Conversa">
        <div className="relative min-h-0 flex-1 overflow-y-auto px-4 py-5 lg:px-8" aria-live="polite">
          <div className="mx-auto flex w-full max-w-2xl flex-col gap-4">
            {falas.map((fala) =>
              fala.de === "cidadao" ? (
                <p key={fala.id} className="entrar max-w-[85%] self-end rounded-2xl rounded-br-md bg-marca px-4 py-3 text-[17px] leading-relaxed whitespace-pre-wrap text-white">
                  {fala.texto}
                </p>
              ) : (
                <div key={fala.id} className="entrar flex flex-col gap-3">
                  {fala.blocos.map((bloco, i) => (
                    <BlocoDaConversa key={i} bloco={bloco} aoClicar={aoClicar} desligado={esperando || fala.id !== ultimaDoSistema} />
                  ))}
                </div>
              ),
            )}
            {esperando && <p className="text-sm text-apagado">Procurando...</p>}
            {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-[15px] text-erro">{erro}</p>}
            <div ref={fim} />
          </div>
        </div>

        <form onSubmit={aoEnviarTexto} className="shrink-0 border-t border-linha bg-superficie px-4 py-3 lg:px-8">
          <div className="mx-auto flex w-full max-w-2xl items-end gap-2">
            <label htmlFor="mensagem" className="sr-only">
              Sua mensagem
            </label>
            <textarea
              id="mensagem"
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              onKeyDown={aoTeclar}
              rows={colando ? 4 : 1}
              maxLength={1500}
              placeholder={colando ? "Cole aqui a mensagem que você recebeu" : "Escreva o que você precisa"}
              className="max-h-40 min-h-12 flex-1 resize-none rounded-xl border border-linha bg-fundo px-4 py-3 text-[17px] placeholder:text-apagado focus:border-marca focus:outline-none"
            />
            <button
              type="submit"
              disabled={esperando || !texto.trim()}
              aria-label="Enviar"
              className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-marca text-white transition-colors hover:bg-marca-forte disabled:opacity-40"
            >
              <Send className="size-5" aria-hidden />
            </button>
          </div>
          <p className="mx-auto mt-2 w-full max-w-2xl text-center text-[13px] text-apagado">Não escreva CPF, telefone, endereço nem senha.</p>
        </form>
      </section>

      <aside className="hidden w-80 shrink-0 flex-col gap-6 overflow-y-auto border-l border-linha bg-superficie p-5 xl:flex" aria-label="Resumo">
        <div className="space-y-3">
          <h2 className="text-[15px] font-bold">Resumo do atendimento</h2>
          {resumo ? (
            <dl className="space-y-3 text-[15px]">
              <div>
                <dt className="text-[13px] text-apagado">Assunto</dt>
                <dd className="font-semibold">{resumo.assunto}</dd>
              </div>
              {resumo.itens
                .filter((i) => i.valor)
                .map((i) => (
                  <div key={i.rotulo}>
                    <dt className="text-[13px] text-apagado">{i.rotulo}</dt>
                    <dd className="font-semibold">{i.valor}</dd>
                  </div>
                ))}
            </dl>
          ) : (
            <p className="text-sm text-apagado">O resumo aparece aqui quando o atendimento chegar a uma resposta.</p>
          )}
          <p className="text-[13px] text-apagado">Nada do que você escreve fica guardado.</p>
        </div>

        {modoBanca && (
          <div className="space-y-3">
            <h2 className="text-[15px] font-bold">Quem fez cada parte</h2>
            {rastro.length ? (
              <ol className="space-y-3">
                {rastro.map((p, i) => (
                  <li key={i} className="flex gap-2.5 text-[15px]">
                    <span className="mt-1.5 size-2.5 shrink-0 rounded-full" style={{ background: CORES_DAS_MATERIAS[p.materia] ?? "#556A6A" }} />
                    <span>
                      <span className="font-semibold">
                        {p.materia} · {p.titulo}
                      </span>
                      {p.detalhe && <span className="block text-[13px] text-apagado">{p.detalhe}</span>}
                    </span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="text-sm text-apagado">A cada resposta, aparece aqui a matéria responsável por cada parte.</p>
            )}
          </div>
        )}

        <button
          type="button"
          onClick={() => comecar()}
          className="mt-auto inline-flex items-center justify-center gap-2 rounded-xl px-3 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-linha ring-inset hover:bg-fundo"
        >
          <RotateCcw className="size-4" aria-hidden />
          Começar de novo
        </button>
      </aside>
    </div>
  );
}
