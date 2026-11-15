import { ChevronDown, ExternalLink, Pencil } from "lucide-react";
import { useMemo, useState } from "react";

import { api, type ChecklistMateria, type ItemChecklist, type ResumoChecklist, type Status } from "../lib/api";

/*
 * Checklist da entrega: o que o enunciado pede, agrupado pelos critérios da rubrica.
 * Feito = existe e foi conferido; Conferir = existe, mas falta a equipe conferir; A fazer = ainda não existe.
 * No servidor público é só leitura; no computador da equipe dá para mudar status, onde e como.
 */

const STATUS: Status[] = ["Feito", "Conferir", "A fazer"];
const COR_STATUS: Record<Status, string> = {
  Feito: "bg-ok-suave text-ok",
  Conferir: "bg-alerta-suave text-alerta",
  "A fazer": "bg-fundo text-apagado ring-1 ring-linha ring-inset",
};
type Filtro = "Todos" | Status | "Da equipe";

function Item({ cod, item, editavel, aoMudar }: {
  cod: string; item: ItemChecklist; editavel: boolean; aoMudar: (novo: ItemChecklist, resumo: ResumoChecklist) => void;
}) {
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
        {editavel ? (
          <>
            <label className="sr-only" htmlFor={`status-${item.id}`}>Status de {item.id}</label>
            <select id={`status-${item.id}`} value={item.status} onChange={(e) => salvar({ status: e.target.value as Status })}
              className={`shrink-0 rounded-full border-0 px-2.5 py-1 text-[13px] font-semibold ${COR_STATUS[item.status]}`}>
              {STATUS.map((s) => <option key={s}>{s}</option>)}
            </select>
          </>
        ) : (
          <span className={`shrink-0 rounded-full px-2.5 py-1 text-[13px] font-semibold ${COR_STATUS[item.status]}`}>{item.status}</span>
        )}
        <button type="button" onClick={() => setAberto((v) => !v)} className="flex min-w-0 flex-1 items-start gap-2 text-left" aria-expanded={aberto}>
          <span className="min-w-0 flex-1">
            <span className="mr-2 font-mono text-[12px] text-apagado">{item.id}</span>
            <span className="text-[15px] font-semibold">{item.requisito}</span>
            <span className="mt-1 flex flex-wrap gap-1.5">
              <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-medium text-apagado ring-1 ring-linha ring-inset">
                {item.quem === "equipe" ? "da equipe" : "no repositório"}
              </span>
              {item.criterio && <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-medium text-apagado ring-1 ring-linha ring-inset">{item.criterio}</span>}
            </span>
          </span>
          <ChevronDown className={`mt-1 size-4 shrink-0 text-apagado transition-transform ${aberto ? "rotate-180" : ""}`} aria-hidden />
        </button>
      </div>

      {aberto && (
        <div className="space-y-3 border-t border-linha px-4 py-3 text-[14px]">
          {editando ? (
            <div className="space-y-2">
              <label className="block font-semibold" htmlFor={`onde-${item.id}`}>Onde está</label>
              <input id={`onde-${item.id}`} value={onde} onChange={(e) => setOnde(e.target.value)} className="w-full rounded-lg border border-linha px-3 py-2" />
              <label className="block font-semibold" htmlFor={`como-${item.id}`}>Como foi feito</label>
              <textarea id={`como-${item.id}`} value={como} onChange={(e) => setComo(e.target.value)} rows={3} className="w-full rounded-lg border border-linha px-3 py-2" />
              <div className="flex gap-2">
                <button type="button" onClick={() => salvar({ onde, como })} className="rounded-full bg-marca px-4 py-1.5 font-semibold text-white hover:bg-marca-forte">Salvar</button>
                <button type="button" onClick={() => setEditando(false)} className="rounded-full px-4 py-1.5 font-semibold text-apagado ring-1 ring-linha ring-inset">Cancelar</button>
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <div>
                <p className="font-semibold">Onde está</p>
                {item.onde_url ? (
                  <a href={item.onde_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 break-all font-mono text-[13px] text-marca-forte underline">
                    <ExternalLink className="size-3.5 shrink-0" aria-hidden />{item.onde}
                  </a>
                ) : (
                  <p className="break-words text-apagado">{item.onde || "Ainda não existe."}</p>
                )}
              </div>
              <div>
                <p className="font-semibold">Como foi feito</p>
                <p className="text-apagado">{item.como || "Sem anotação."}</p>
              </div>
              {editavel && (
                <button type="button" onClick={() => setEditando(true)} className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-marca-forte underline">
                  <Pencil className="size-3.5" aria-hidden />Editar onde e como
                </button>
              )}
            </div>
          )}
          {erro && <p className="rounded-lg bg-erro-suave px-3 py-2 text-erro">{erro}</p>}
        </div>
      )}
    </li>
  );
}

export default function Checklist({ cod, dados, editavel }: { cod: string; dados: ChecklistMateria; editavel: boolean }) {
  const [secoes, setSecoes] = useState(dados.secoes);
  const [resumo, setResumo] = useState(dados.resumo);
  const [filtro, setFiltro] = useState<Filtro>("Todos");

  const passa = (i: ItemChecklist) => (filtro === "Todos" ? true : filtro === "Da equipe" ? i.quem === "equipe" && i.status !== "Feito" : i.status === filtro);
  const daEquipe = useMemo(() => secoes.flatMap((s) => s.itens).filter((i) => i.quem === "equipe" && i.status !== "Feito").length, [secoes]);
  const aoMudar = (novo: ItemChecklist, r: ResumoChecklist) => {
    setSecoes((lista) => lista.map((s) => ({ ...s, itens: s.itens.map((i) => (i.id === novo.id ? novo : i)) })));
    setResumo(r);
  };
  const contagem = (f: Filtro) => (f === "Todos" ? resumo.total : f === "Da equipe" ? daEquipe : resumo.por_status[f]);

  return (
    <div className="space-y-5">
      <div className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
        <dl className="space-y-2 text-[14px]">
          <div>
            <dt className="font-semibold">O que vai para o portal</dt>
            <dd className="text-apagado">{dados.formato_entrega}</dd>
          </div>
          {dados.prazo && (
            <div>
              <dt className="font-semibold">Prazo</dt>
              <dd className="text-apagado">{dados.prazo}</dd>
            </div>
          )}
        </dl>
        {!!dados.rubrica?.length && (
          <details className="text-[14px]">
            <summary className="cursor-pointer font-semibold">Critérios de avaliação do enunciado ({dados.rubrica.length})</summary>
            <ul className="mt-2 space-y-1">
              {dados.rubrica.map((r) => (
                <li key={r.criterio} className="flex gap-3">
                  <span className="w-16 shrink-0 font-semibold tabular-nums">{r.pontos}</span>
                  <span className="text-apagado">{r.criterio}</span>
                </li>
              ))}
            </ul>
          </details>
        )}
        {!!dados.observacoes?.length && (
          <details className="text-[14px]">
            <summary className="cursor-pointer font-semibold">Observações</summary>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-apagado">{dados.observacoes.map((o) => <li key={o}>{o}</li>)}</ul>
          </details>
        )}
      </div>

      <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar itens">
        {(["Todos", "A fazer", "Conferir", "Feito", "Da equipe"] as Filtro[]).map((f) => (
          <button key={f} type="button" onClick={() => setFiltro(f)} aria-pressed={filtro === f}
            className={`rounded-full px-3 py-1 text-[13px] font-semibold ${filtro === f ? "bg-marca text-white" : "bg-superficie text-apagado ring-1 ring-linha ring-inset hover:text-tinta"}`}>
            {f} ({contagem(f)})
          </button>
        ))}
      </div>

      {secoes.map((s) => {
        const itens = s.itens.filter(passa);
        if (!itens.length) return null;
        return (
          <section key={s.titulo} className="space-y-2">
            <h4 className="text-[15px] font-bold">{s.titulo}</h4>
            <ul className="space-y-2">
              {itens.map((i) => <Item key={i.id} cod={cod} item={i} editavel={editavel} aoMudar={aoMudar} />)}
            </ul>
          </section>
        );
      })}
      {secoes.every((s) => !s.itens.some(passa)) && <p className="text-[14px] text-apagado">Nenhum item neste filtro.</p>}

      <p className="text-[13px] text-apagado">
        Feito: existe e foi conferido. Conferir: existe, mas a equipe ainda precisa conferir (fonte oficial, número, roteiro). A fazer: ainda não existe.
        {editavel ? " Mudanças ficam salvas em sistema/dados/checklist.json." : " Nesta versão pública o checklist é só leitura."}
      </p>
    </div>
  );
}
