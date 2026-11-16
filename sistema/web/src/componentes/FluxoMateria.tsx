import type { FluxoDaMateria, PassoDoFluxo } from "../lib/api";

/*
 * O caminho do dado por dentro de uma matéria, de cima para baixo: cada caixa é uma etapa e a
 * última pode se dividir em "sim" e "não". Sem enfeite: a cor da matéria só marca as setas e as bordas.
 */

function Seta({ cor }: { cor: string }) {
  return (
    <svg viewBox="0 0 16 22" className="mx-auto h-[22px] w-4" aria-hidden>
      <path d="M8 0v16M3 11l5 6 5-6" fill="none" stroke={cor} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Caixa({ p, cor, forte = false }: { p: PassoDoFluxo; cor: string; forte?: boolean }) {
  return (
    <div className="rounded-xl border bg-superficie px-4 py-2.5 text-center" style={{ borderColor: forte ? cor : undefined, borderWidth: forte ? 2 : undefined }}>
      <p className="text-[15px] font-semibold">{p.rotulo}</p>
      {p.sub && <p className="text-[13px] text-apagado">{p.sub}</p>}
    </div>
  );
}

export default function FluxoMateria({ fluxo, cor }: { fluxo: FluxoDaMateria; cor: string }) {
  const { passos, decisao } = fluxo;
  return (
    <ol className="mx-auto flex w-full max-w-xl flex-col" aria-label="Etapas da matéria dentro do sistema">
      {passos.map((p, i) => (
        <li key={p.rotulo}>
          {i > 0 && <Seta cor={cor} />}
          <Caixa p={p} cor={cor} />
        </li>
      ))}
      {decisao && (
        <li>
          <Seta cor={cor} />
          <div className="rounded-xl px-4 py-2.5 text-center text-[15px] font-bold text-white" style={{ background: cor }}>{decisao.pergunta}</div>
          <div className="grid grid-cols-2 gap-3">
            {([["Sim", decisao.sim], ["Não", decisao.nao]] as const).map(([rotulo, saida]) => (
              <div key={rotulo}>
                <Seta cor={cor} />
                <p className="-mt-1 mb-1 text-center text-[12px] font-bold" style={{ color: cor }}>{rotulo}</p>
                <Caixa p={saida} cor={cor} forte />
              </div>
            ))}
          </div>
        </li>
      )}
    </ol>
  );
}
