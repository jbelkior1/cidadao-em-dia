import { ChevronDown, Pencil } from "lucide-react";
import { useMemo, useState } from "react";

import { api, type ChecklistMateria, type ItemChecklist, type ResumoChecklist, type Status } from "../lib/api";

const STATUS: Status[] = ["Feito", "Falta conferir", "A fazer"];
const COR_STATUS: Record<Status, string> = {
  Feito: "bg-ok-suave text-ok",
  "Falta conferir": "bg-alerta-suave text-alerta",
  "A fazer": "bg-fundo text-apagado ring-1 ring-linha ring-inset",
};
type Filtro = "Todos" | Status | "Do grupo";

export function BarraProgresso({ resumo, cor }: { resumo: ResumoChecklist; cor?: string }) {
  const { por_status: c, total } = resumo;
  const largura = (n: number) => `${total ? (100 * n) / total : 0}%`;
  return (
    <div className="space-y-1.5">
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-linha" aria-hidden>
        <span style={{ width: largura(c.Feito), background: cor ?? "var(--color-ok)" }} />
        <span className="opacity-40" style={{ width: largura(c["Falta conferir"]), background: cor ?? "var(--color-alerta)" }} />
      </div>
      <p className="text-[13px] text-apagado">
        <span className="font-semibold text-tinta">{resumo.percentual}%</span> · {c.Feito} feitos, {c["Falta conferir"]} falta conferir,{" "}
        {c["A fazer"]} a fazer
      </p>
    </div>
  );
}

function Item({ cod, item, aoMudar }: { cod: string; item: ItemChecklist; aoMudar: (novo: ItemChecklist, resumo: ResumoChecklist) => void }) {
  const [aberto, setAberto] = useState(false);
  const [editando, setEditando] = useState(false);
  const [onde, setOnde] = useState(item.onde);
  const [como, setComo] = useState(item.como);
  const [erro, setErro] = useState("");

  const salvar = async (mudancas: Partial<Pick<ItemChecklist, "status" | "onde" | "como">>) => {
    setErro("");
    try {
      const r = await api.mudarItem(cod, item.id, mudancas);
      aoMudar(r.item, r.resumo);
      setEditando(false);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não consegui salvar.");
    }
  };

  return (
    <li className="rounded-xl border border-linha bg-superficie">
      <div className="flex flex-wrap items-start gap-x-3 gap-y-2 px-4 py-3">
        <label className="sr-only" htmlFor={`status-${item.id}`}>
          Status de {item.id}
        </label>
        <select
          id={`status-${item.id}`}
          value={item.status}
          onChange={(e) => salvar({ status: e.target.value as Status })}
          className={`shrink-0 rounded-full border-0 px-2.5 py-1 text-[13px] font-semibold ${COR_STATUS[item.status]}`}
        >
          {STATUS.map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <button type="button" onClick={() => setAberto((v) => !v)} className="flex min-w-0 flex-1 items-start gap-2 text-left" aria-expanded={aberto}>
          <span className="min-w-0 flex-1">
            <span className="mr-2 font-mono text-[12px] text-apagado">{item.id}</span>
            <span className="text-[15px] font-semibold">{item.requisito}</span>
            <span className="mt-1 flex flex-wrap gap-1.5">
              <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-medium text-apagado ring-1 ring-linha ring-inset">
                {item.quem === "grupo" ? "faz o grupo" : "código"}
              </span>
              {item.peso && <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-medium text-apagado ring-1 ring-linha ring-inset">{item.peso}</span>}
            </span>
          </span>
          <ChevronDown className={`mt-1 size-4 shrink-0 text-apagado transition-transform ${aberto ? "rotate-180" : ""}`} aria-hidden />
        </button>
      </div>

      {aberto && (
        <div className="space-y-3 border-t border-linha px-4 py-3 text-[14px]">
          {item.detalhe && (
            <div>
              <p className="font-semibold">O que o enunciado diz</p>
              <p className="text-apagado">{item.detalhe}</p>
            </div>
          )}
          {item.fonte && <p className="text-[13px] text-apagado">Fonte: {item.fonte}</p>}
          {editando ? (
            <div className="space-y-2">
              <label className="block font-semibold" htmlFor={`onde-${item.id}`}>Onde está</label>
              <input id={`onde-${item.id}`} value={onde} onChange={(e) => setOnde(e.target.value)} className="w-full rounded-lg border border-linha px-3 py-2" />
              <label className="block font-semibold" htmlFor={`como-${item.id}`}>Como foi feito</label>
              <textarea id={`como-${item.id}`} value={como} onChange={(e) => setComo(e.target.value)} rows={3} className="w-full rounded-lg border border-linha px-3 py-2" />
              <div className="flex gap-2">
                <button type="button" onClick={() => salvar({ onde, como })} className="rounded-full bg-marca px-4 py-1.5 font-semibold text-white hover:bg-marca-forte">
                  Salvar
                </button>
                <button type="button" onClick={() => setEditando(false)} className="rounded-full px-4 py-1.5 font-semibold text-apagado ring-1 ring-linha ring-inset">
                  Cancelar
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div>
                <p className="font-semibold">Onde está</p>
                <p className="break-words text-apagado">{item.onde ? <code className="text-[13px]">{item.onde}</code> : "Ainda não existe."}</p>
              </div>
              <div>
                <p className="font-semibold">Como foi feito</p>
                <p className="text-apagado">{item.como || "Sem anotação."}</p>
              </div>
              <button type="button" onClick={() => setEditando(true)} className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-marca-forte underline">
                <Pencil className="size-3.5" aria-hidden />
                Editar onde e como
              </button>
            </div>
          )}
          {erro && <p className="rounded-lg bg-erro-suave px-3 py-2 text-erro">{erro}</p>}
        </div>
      )}
    </li>
  );
}

export default function Checklist({ cod, dados, cor, compacto }: { cod: string; dados: ChecklistMateria; cor?: string; compacto?: boolean }) {
  const [itens, setItens] = useState(dados.itens);
  const [resumo, setResumo] = useState(dados.resumo);
  const [filtro, setFiltro] = useState<Filtro>("Todos");

  const visiveis = useMemo(
    () =>
      itens.filter((i) =>
        filtro === "Todos" ? true : filtro === "Do grupo" ? i.quem === "grupo" && i.status !== "Feito" : i.status === filtro,
      ),
    [itens, filtro],
  );
  const aoMudar = (novo: ItemChecklist, r: ResumoChecklist) => {
    setItens((lista) => lista.map((i) => (i.id === novo.id ? novo : i)));
    setResumo(r);
  };

  return (
    <div className="space-y-4">
      {!compacto && (
        <div className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
          <BarraProgresso resumo={resumo} cor={cor} />
          <dl className="space-y-2 text-[14px]">
            <div>
              <dt className="font-semibold">O que o professor recebe</dt>
              <dd className="text-apagado">{dados.formato_entrega}</dd>
            </div>
            {dados.prazo && (
              <div>
                <dt className="font-semibold">Prazo</dt>
                <dd className="text-apagado">{dados.prazo}</dd>
              </div>
            )}
          </dl>
          {dados.rubrica && dados.rubrica.length > 0 && (
            <details className="text-[14px]">
              <summary className="cursor-pointer font-semibold">Rubrica ({dados.rubrica.length} critérios)</summary>
              <ul className="mt-2 space-y-1">
                {dados.rubrica.map((r) => (
                  <li key={r.criterio} className="flex gap-3">
                    <span className="w-14 shrink-0 font-semibold tabular-nums">{r.pontos}</span>
                    <span className="text-apagado">{r.criterio}</span>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}

      <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar itens">
        {(["Todos", "A fazer", "Falta conferir", "Feito", "Do grupo"] as Filtro[]).map((f) => (
          <button
            key={f}
            type="button"
            onClick={() => setFiltro(f)}
            aria-pressed={filtro === f}
            className={`rounded-full px-3 py-1 text-[13px] font-semibold ${filtro === f ? "bg-marca text-white" : "bg-superficie text-apagado ring-1 ring-linha ring-inset hover:text-tinta"}`}
          >
            {f}
            {f !== "Todos" && f !== "Do grupo" ? ` (${resumo.por_status[f]})` : f === "Do grupo" ? ` (${itens.filter((i) => i.quem === "grupo" && i.status !== "Feito").length})` : ` (${resumo.total})`}
          </button>
        ))}
      </div>

      <ul className="space-y-2">
        {visiveis.map((i) => (
          <Item key={i.id} cod={cod} item={i} aoMudar={aoMudar} />
        ))}
        {visiveis.length === 0 && <li className="text-[14px] text-apagado">Nenhum item neste filtro.</li>}
      </ul>
      <p className="text-[13px] text-apagado">Mudanças ficam salvas em sistema/dados/checklist.json. No progresso, item feito vale 1 e "falta conferir" vale meio.</p>
    </div>
  );
}
