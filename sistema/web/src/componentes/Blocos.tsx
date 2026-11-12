import { Check, ExternalLink, ShieldAlert, Sparkles, TriangleAlert, X } from "lucide-react";
import { useState, type ReactNode } from "react";

import { useApp } from "../App";
import { api, CORES_DAS_MATERIAS, type Bloco, type Opcao, type Selo } from "../lib/api";

type Clicar = (opcao: Opcao) => void;

/* ---------- peças pequenas ---------- */

export function SeloMateria({ selo }: { selo: Selo }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-superficie px-2 py-0.5 text-xs font-medium text-apagado ring-1 ring-linha ring-inset">
      <span className="size-2 rounded-full" style={{ background: CORES_DAS_MATERIAS[selo.materia] ?? "#556A6A" }} />
      {selo.materia} · {selo.papel}
    </span>
  );
}

function Selos({ selos }: { selos?: Selo[] }) {
  const { modoBanca } = useApp();
  if (!modoBanca || !selos?.length) return null;
  return (
    <div className="flex flex-wrap gap-1.5">
      {selos.map((s) => (
        <SeloMateria key={s.materia + s.papel} selo={s} />
      ))}
    </div>
  );
}

function Botoes({ opcoes, aoClicar, desligado, empilhado }: { opcoes: Opcao[]; aoClicar: Clicar; desligado: boolean; empilhado?: boolean }) {
  return (
    <div className={empilhado ? "flex flex-col gap-2" : "flex flex-wrap gap-2"}>
      {opcoes.map((o) => (
        <button
          key={o.acao}
          type="button"
          disabled={desligado}
          onClick={() => aoClicar(o)}
          className={`rounded-full px-4 py-2 text-[15px] font-semibold transition-colors disabled:cursor-default disabled:opacity-50 ${
            empilhado ? "rounded-xl text-left" : ""
          } ${
            o.principal
              ? "bg-marca text-white hover:bg-marca-forte"
              : "bg-superficie text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave"
          }`}
        >
          {o.rotulo}
        </button>
      ))}
    </div>
  );
}

function Cartao({ children }: { children: ReactNode }) {
  return <div className="space-y-3 rounded-xl border border-linha bg-superficie p-4 shadow-sm">{children}</div>;
}

function Rodape({ fonte, data, aviso, emConferencia }: { fonte?: string; data?: string; aviso?: string; emConferencia?: boolean }) {
  return (
    <div className="space-y-1.5 border-t border-linha pt-3 text-[13px] text-apagado">
      {fonte && (
        <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
          <span className="font-semibold text-tinta">Fonte:</span>
          <a href={fonte} target="_blank" rel="noreferrer" className="inline-flex min-w-0 items-center gap-1 break-all text-marca-forte underline">
            {fonte.replace(/^https?:\/\//, "").split("/")[0]}
            <ExternalLink className="size-3.5 shrink-0" aria-hidden />
          </a>
          {data && <span>consultada em {formatarData(data)}</span>}
          {emConferencia && <span className="rounded-full bg-alerta-suave px-2 py-0.5 text-xs font-semibold text-alerta">em conferência pela equipe</span>}
        </p>
      )}
      {aviso && <p>{aviso}</p>}
    </div>
  );
}

function formatarData(iso: string): string {
  const partes = iso.split("-");
  return partes.length === 3 ? `${partes[2]}/${partes[1]}/${partes[0]}` : iso;
}

const TONS: Record<string, string> = {
  ok: "bg-ok-suave text-ok",
  risco: "bg-alerta-suave text-alerta",
  inicio: "bg-marca-suave text-marca-forte",
  neutro: "bg-fundo text-tinta ring-1 ring-linha ring-inset",
};

/* ---------- blocos ---------- */

function Orientacao({ bloco, aoClicar, desligado }: { bloco: Bloco; aoClicar: Clicar; desligado: boolean }) {
  const { ia, recarregarIA } = useApp();
  const [simples, setSimples] = useState<{ texto?: string; erro?: string; carregando?: boolean }>({});

  const explicar = async () => {
    setSimples({ carregando: true });
    try {
      const r = await api.explicar(bloco.id);
      setSimples({ texto: r.texto });
    } catch (e) {
      setSimples({ erro: e instanceof Error ? e.message : "Não deu para explicar agora." });
    }
    recarregarIA();
  };

  return (
    <Cartao>
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg leading-snug font-bold">{bloco.titulo}</h3>
        <span className="rounded-full bg-fundo px-2.5 py-0.5 text-xs font-medium text-apagado ring-1 ring-linha ring-inset">{bloco.categoria}</span>
      </div>

      {bloco.confianca && (
        <details className="rounded-lg bg-fundo px-3 py-2 text-sm">
          <summary className="cursor-pointer font-semibold">
            Confiança {bloco.confianca} · {bloco.pontos} pontos
            <span className="ml-1 font-normal text-apagado">(ver por quê)</span>
          </summary>
          <ul className="mt-2 space-y-1 text-apagado">
            {bloco.detalhe.map((d: { termo: string; pontos: number; origem: string }) => (
              <li key={d.origem + d.termo}>
                <span className="font-semibold text-tinta">+{d.pontos}</span> {d.origem}: “{d.termo}”
              </li>
            ))}
          </ul>
        </details>
      )}

      <p className="text-[17px] leading-relaxed">{bloco.resposta}</p>

      {simples.texto && (
        <div className="space-y-2 rounded-lg bg-marca-suave p-3">
          <p className="text-sm font-semibold text-marca-forte">De um jeito mais simples</p>
          <p className="text-[17px] leading-relaxed">{simples.texto}</p>
          <Selos selos={[{ materia: "PAI", papel: "explicação" }]} />
        </div>
      )}
      {simples.erro && <p className="rounded-lg bg-alerta-suave p-3 text-sm text-alerta">{simples.erro}</p>}

      <dl className="space-y-2 text-[15px]">
        {bloco.documentos?.length > 0 && (
          <div>
            <dt className="font-semibold">O que levar</dt>
            <dd>
              <ul className="list-disc pl-5">
                {bloco.documentos.map((d: string) => (
                  <li key={d}>{d}</li>
                ))}
              </ul>
            </dd>
          </div>
        )}
        {bloco.onde && (
          <div>
            <dt className="font-semibold">Onde resolver</dt>
            <dd>{bloco.onde}</dd>
          </div>
        )}
        {bloco.para_quem && (
          <div>
            <dt className="font-semibold">Para quem é</dt>
            <dd>{bloco.para_quem}</dd>
          </div>
        )}
        {bloco.prazo && (
          <div>
            <dt className="font-semibold">Prazo</dt>
            <dd>
              {bloco.prazo.texto} <span className="rounded-md bg-alerta-suave px-1.5 font-semibold text-alerta">{bloco.prazo.faltam}</span>
            </dd>
          </div>
        )}
      </dl>

      {ia?.ligada && !simples.texto && (
        <button
          type="button"
          onClick={explicar}
          disabled={simples.carregando}
          className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave disabled:opacity-60"
        >
          <Sparkles className="size-4" aria-hidden />
          {simples.carregando ? "Explicando..." : "Explicar de um jeito mais simples"}
        </button>
      )}

      {bloco.alternativas?.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-semibold">Talvez você queira ver também:</p>
          <Botoes
            opcoes={bloco.alternativas.map((a: { id: number; titulo: string }) => ({ rotulo: a.titulo, acao: `orientacao:${a.id}` }))}
            aoClicar={aoClicar}
            desligado={desligado}
            empilhado
          />
        </div>
      )}

      <Selos selos={bloco.selos} />
      <Rodape fonte={bloco.fonte} data={bloco.verificado_em} aviso={bloco.aviso} emConferencia={bloco.em_conferencia} />
    </Cartao>
  );
}

function Ficha({ bloco }: { bloco: Bloco }) {
  return (
    <Cartao>
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-lg leading-snug font-bold">{bloco.titulo}</h3>
        <span className={`rounded-full px-2.5 py-0.5 text-sm font-semibold ${TONS[bloco.tom] ?? TONS.neutro}`}>{bloco.situacao}</span>
      </div>
      {bloco.explicacao && <p className="text-[17px] leading-relaxed">{bloco.explicacao}</p>}
      {bloco.linhas?.length > 0 && (
        <dl className="grid grid-cols-1 gap-x-4 gap-y-2 text-[15px] sm:grid-cols-[auto_minmax(0,1fr)]">
          {bloco.linhas.map((l: { rotulo: string; valor: string; destaque?: string }) => (
            <div key={l.rotulo} className="contents">
              <dt className="text-apagado">{l.rotulo}</dt>
              <dd className="font-semibold">
                {l.valor} {l.destaque && <span className="rounded-md bg-alerta-suave px-1.5 font-semibold text-alerta">{l.destaque}</span>}
              </dd>
            </div>
          ))}
        </dl>
      )}
      {bloco.passos?.length > 0 && (
        <div>
          <p className="text-[15px] font-semibold">O que fazer agora</p>
          <ol className="mt-1 list-decimal space-y-1 pl-5 text-[16px]">
            {bloco.passos.map((p: string) => (
              <li key={p}>{p}</li>
            ))}
          </ol>
        </div>
      )}
      <Selos selos={bloco.selos} />
      <Rodape fonte={bloco.fonte} data={bloco.verificado_em} aviso={bloco.aviso} emConferencia={bloco.em_conferencia} />
    </Cartao>
  );
}

function Sinais({ bloco }: { bloco: Bloco }) {
  const atencao = bloco.nivel === "atencao";
  return (
    <Cartao>
      <h3 className={`flex items-start gap-2 text-lg leading-snug font-bold ${atencao ? "text-alerta" : "text-ok"}`}>
        {atencao ? <TriangleAlert className="mt-0.5 size-5 shrink-0" aria-hidden /> : <Check className="mt-0.5 size-5 shrink-0" aria-hidden />}
        {bloco.titulo}
      </h3>
      <ul className="space-y-2 text-[15px]">
        {bloco.itens.map((i: { pergunta: string; ok: boolean; detalhe: string }) => (
          <li key={i.pergunta} className="flex items-start gap-2.5">
            <span className={`mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full ${i.ok ? "bg-ok-suave text-ok" : "bg-alerta-suave text-alerta"}`}>
              {i.ok ? <Check className="size-3.5" aria-hidden /> : <X className="size-3.5" aria-hidden />}
            </span>
            <span>
              <span className="font-semibold">{i.pergunta}</span> <span className="text-apagado">{i.ok ? "Tudo certo: " : "Atenção: "}{i.detalhe}.</span>
            </span>
          </li>
        ))}
      </ul>
      <p className="text-[17px] leading-relaxed">{bloco.orientacao}</p>
      <Rodape aviso={bloco.aviso} />
    </Cartao>
  );
}

export function BlocoDaConversa({ bloco, aoClicar, desligado }: { bloco: Bloco; aoClicar: Clicar; desligado: boolean }) {
  switch (bloco.tipo) {
    case "texto":
      return <p className="max-w-[90%] rounded-2xl rounded-bl-md border border-linha bg-superficie px-4 py-3 text-[17px] leading-relaxed shadow-sm">{bloco.texto}</p>;
    case "recusa":
      return (
        <p className="flex max-w-[90%] items-start gap-2.5 rounded-2xl rounded-bl-md bg-alerta-suave px-4 py-3 text-[16px] leading-relaxed text-alerta">
          <ShieldAlert className="mt-0.5 size-5 shrink-0" aria-hidden />
          {bloco.texto}
        </p>
      );
    case "entendi":
      return (
        <Cartao>
          <p className="text-sm font-semibold text-apagado">Entendi assim</p>
          <p className="text-[18px] leading-snug font-semibold">{bloco.resumo}</p>
          <p className="text-sm text-apagado">
            Por quê: encontrei {bloco.porque.map((p: string) => `“${p}”`).join(" e ")} na sua mensagem.
          </p>
          <Botoes opcoes={bloco.opcoes} aoClicar={aoClicar} desligado={desligado} />
        </Cartao>
      );
    case "opcoes":
      return (
        <div className="space-y-2">
          {bloco.passo && <p className="text-xs font-semibold tracking-wide text-apagado uppercase">{bloco.passo}</p>}
          {bloco.texto && <p className="text-[17px] leading-snug font-semibold">{bloco.texto}</p>}
          <Botoes opcoes={bloco.opcoes} aoClicar={aoClicar} desligado={desligado} empilhado={bloco.empilhado} />
        </div>
      );
    case "numero":
      return (
        <div className="space-y-2">
          <p className="text-[17px] leading-snug font-semibold">{bloco.texto}</p>
          {bloco.ajuda && <p className="text-sm text-apagado">{bloco.ajuda}</p>}
          <p className="text-sm text-apagado">
            Escreva o número no campo abaixo{bloco.sufixo === "R$" ? ", em reais." : `, em ${bloco.sufixo}.`}
          </p>
          {bloco.opcoes && <Botoes opcoes={bloco.opcoes} aoClicar={aoClicar} desligado={desligado} />}
        </div>
      );
    case "orientacao":
      return <Orientacao bloco={bloco} aoClicar={aoClicar} desligado={desligado} />;
    case "ficha":
      return <Ficha bloco={bloco} />;
    case "sinais":
      return <Sinais bloco={bloco} />;
    default:
      return null;
  }
}
