import { Children, isValidElement, useEffect, useMemo, useState, type ReactNode } from "react";
import Markdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { api } from "../lib/api";

/*
 * Documentação funcional: o arquivo docs/DOCUMENTACAO_FUNCIONAL.md do repositório, servido pela API.
 * Uma fonte só: quem lê no GitHub e quem lê aqui vê o mesmo texto.
 */

function textoDe(no: ReactNode): string {
  return Children.toArray(no)
    .map((filho) => (typeof filho === "string" || typeof filho === "number" ? String(filho) : isValidElement<{ children?: ReactNode }>(filho) ? textoDe(filho.props.children) : ""))
    .join("");
}

function ancora(titulo: string): string {
  return titulo.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

const COMPONENTES: Components = {
  h1: ({ children }) => <h2 className="text-3xl leading-tight font-bold">{children}</h2>,
  h2: ({ children }) => <h3 id={ancora(textoDe(children))} className="mt-10 scroll-mt-6 border-t border-linha pt-6 text-xl font-bold">{children}</h3>,
  h3: ({ children }) => <h4 className="mt-6 text-lg font-bold">{children}</h4>,
  p: ({ children }) => <p className="mt-3 text-[16px] leading-relaxed">{children}</p>,
  ul: ({ children }) => <ul className="mt-3 list-disc space-y-1.5 pl-5 text-[16px] leading-relaxed">{children}</ul>,
  ol: ({ children }) => <ol className="mt-3 list-decimal space-y-1.5 pl-5 text-[16px] leading-relaxed">{children}</ol>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  a: ({ children, href }) => <a href={href} target="_blank" rel="noreferrer" className="font-semibold text-marca-forte underline">{children}</a>,
  code: ({ children }) => <code className="rounded bg-fundo px-1.5 py-0.5 font-mono text-[13px]">{children}</code>,
  table: ({ children }) => (
    <div className="mt-4 overflow-x-auto rounded-xl border border-linha bg-superficie">
      <table className="w-full min-w-[520px] text-left text-[14px]">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border-b border-linha bg-fundo px-3 py-2 font-semibold">{children}</th>,
  td: ({ children }) => <td className="border-b border-linha px-3 py-2 align-top">{children}</td>,
};

export default function Documentacao() {
  const [texto, setTexto] = useState("");
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.documentacao().then((d) => setTexto(d.texto)).catch(() => setErro("Não consegui carregar a documentação. Tente recarregar a página."));
  }, []);

  const secoes = useMemo(() => [...texto.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim()), [texto]);

  if (erro) return <p className="m-8 rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>;
  if (!texto) return <p className="m-8 text-apagado">Carregando...</p>;

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8 lg:px-8">
      <nav aria-label="Nesta página" className="mb-8 rounded-xl border border-linha bg-superficie p-4">
        <p className="text-[14px] font-semibold text-apagado">Nesta página</p>
        <ol className="mt-2 grid gap-x-6 gap-y-1 text-[15px] sm:grid-cols-2">
          {secoes.map((s) => (
            <li key={s}>
              <a href={`#${ancora(s)}`} className="text-marca-forte hover:underline">{s}</a>
            </li>
          ))}
        </ol>
      </nav>
      <article>
        <Markdown remarkPlugins={[remarkGfm]} components={COMPONENTES}>{texto}</Markdown>
      </article>
    </div>
  );
}
