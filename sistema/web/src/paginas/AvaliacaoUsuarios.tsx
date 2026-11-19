import { ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, type ResumoAvaliacoes } from "../lib/api";

/*
 * Avaliação usuários: os comentários de quem usou o Dá Tempo?, separados por grupo (família, faculdade,
 * trabalho, conhecido). Vêm do formulário "Avaliar o Dá Tempo?" (/avaliar); ninguém se identifica.
 * Quem fez o teste completo (/avaliar/teste) também entra nos números, mostrados embaixo quando existem.
 */

const fmt = (n: number | null | undefined, casas = 1) =>
  n === null || n === undefined ? "—" : n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

export default function AvaliacaoUsuarios() {
  const [r, setR] = useState<ResumoAvaliacoes | null>(null);
  const [erro, setErro] = useState(false);
  useEffect(() => {
    api.avaliacoes().then(setR).catch(() => setErro(true));
  }, []);

  return (
    <div className="mx-auto w-full max-w-4xl space-y-8 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <h2 className="text-2xl font-bold sm:text-3xl">Avaliação usuários</h2>
        <p className="max-w-3xl text-[17px] text-apagado">O que as pessoas acharam do Dá Tempo?, separado por grupo. Ninguém se identifica.</p>
        <Link to="/avaliar" className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
          Avaliar o Dá Tempo?<ArrowRight className="size-4" aria-hidden />
        </Link>
      </header>

      {erro && <p className="rounded-xl bg-fundo px-4 py-3 text-[15px] text-apagado ring-1 ring-linha ring-inset">Não deu para carregar as avaliações agora.</p>}
      {r && r.grupos.length === 0 && (
        <div className="space-y-2 rounded-xl border border-dashed border-linha bg-superficie p-6 text-center">
          <p className="text-[16px] font-semibold">Ainda não há avaliações.</p>
          <Link to="/avaliar" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">Seja o primeiro a avaliar<ArrowRight className="size-4" aria-hidden /></Link>
        </div>
      )}

      {r?.grupos.map((g) => (
        <section key={g.grupo} className="space-y-3" aria-label={g.grupo}>
          <h3 className="text-lg font-bold">{g.grupo} <span className="text-[15px] font-normal text-apagado">({g.comentarios.length})</span></h3>
          <ul className="grid gap-3 sm:grid-cols-2">
            {g.comentarios.map((c) => (
              <li key={c.pessoa} className="space-y-2 rounded-xl border border-linha bg-superficie p-4">
                {c.comentario && <p className="text-[15px] leading-relaxed">"{c.comentario}"</p>}
                {c.sugestao && <p className="text-[14px] text-apagado"><span className="font-semibold text-marca-forte">Sugestão: </span>{c.sugestao}</p>}
              </li>
            ))}
          </ul>
        </section>
      ))}

      {r && r.testes_completos > 0 && (
        <details className="rounded-xl border border-linha bg-superficie px-4 py-3">
          <summary className="cursor-pointer text-[15px] font-semibold">Números do teste completo ({r.testes_completos} {r.testes_completos === 1 ? "pessoa" : "pessoas"})</summary>
          <div className="mt-3 space-y-3 text-[14px]">
            <p>Facilidade média: <span className="font-semibold">{fmt(r.facilidade_media)} de 5</span></p>
            <ul className="space-y-1">
              {r.tarefas.map((t) => (
                <li key={t.tarefa}>
                  {t.tarefa}: {t.tempo_medio_s === null ? "—" : `${fmt(t.tempo_medio_s, 0)} s em média`}
                  {t.acerto_percentual === null ? "" : `, ${t.acerto_percentual}% de acerto`}
                </li>
              ))}
            </ul>
          </div>
        </details>
      )}
    </div>
  );
}
