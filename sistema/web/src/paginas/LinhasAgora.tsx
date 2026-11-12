import { CloudLightning, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { SeloLinha, SituacaoLinha, hora } from "../componentes/Linha";
import { mobilidade, type AvisoTempo, type LinhaAgora } from "../lib/api";

export default function LinhasAgora() {
  const [linhas, setLinhas] = useState<LinhaAgora[]>([]);
  const [info, setInfo] = useState({ fonte: "", lido_em: "", aviso: "" });
  const [avisos, setAvisos] = useState<AvisoTempo[]>([]);
  const [erro, setErro] = useState("");

  const carregar = () => {
    setErro("");
    mobilidade.linhas().then((r) => {
      setLinhas(r.linhas);
      setInfo({ fonte: r.fonte, lido_em: r.lido_em, aviso: r.aviso });
    }).catch(() => setErro("Não consegui ler a situação das linhas."));
    mobilidade.tempo().then((r) => setAvisos(r.avisos.filter((a) => a.quando === "hoje"))).catch(() => setAvisos([]));
  };
  useEffect(() => {
    carregar();
    const t = setInterval(carregar, 120000);
    return () => clearInterval(t);
  }, []);

  const problemas = linhas.filter((l) => l.nivel === "parada" || l.nivel === "atencao");

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6 px-4 py-6 lg:px-8">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold">Trem e metrô agora</h2>
          <p className="text-[15px] text-apagado">
            {problemas.length ? `${problemas.length} ${problemas.length === 1 ? "linha com problema" : "linhas com problema"}.` : "Nenhuma linha com problema informada."}
            {" "}Leitura das {hora(info.lido_em)}.
          </p>
        </div>
        <button type="button" onClick={carregar} className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[14px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
          <RefreshCw className="size-4" aria-hidden />Atualizar
        </button>
      </header>

      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}
      {info.aviso && <p className="rounded-xl bg-alerta-suave px-4 py-3 text-alerta">{info.aviso}</p>}

      {avisos.map((a, i) => (
        <div key={i} className="flex items-start gap-3 rounded-xl border border-alerta/30 bg-alerta-suave p-4 text-alerta">
          <CloudLightning className="mt-0.5 size-5 shrink-0" aria-hidden />
          <div>
            <p className="font-semibold">Aviso do INMET para São Paulo: {a.tipo} ({a.severidade.toLowerCase()})</p>
            <p className="text-[14px]">Até {a.fim.slice(-5)}. {a.riscos}</p>
          </div>
        </div>
      ))}

      <ul className="grid gap-2 sm:grid-cols-2">
        {[...problemas, ...linhas.filter((l) => !problemas.includes(l))].map((l) => (
          <li key={l.numero} className="flex items-center gap-3 rounded-xl border border-linha bg-superficie p-3">
            <SeloLinha numero={l.numero} cor={l.cor} tamanho="lg" />
            <div className="min-w-0 flex-1">
              <p className="font-semibold">Linha {l.numero}-{l.nome}</p>
              <p className="truncate text-[13px] text-apagado">{l.operadora || "operadora não informada"}{l.descricao && l.descricao !== l.status ? ` · ${l.descricao}` : ""}</p>
            </div>
            <div className="text-right">
              <SituacaoLinha nivel={l.nivel} />
              {l.nivel !== "normal" && l.nivel !== "sem_dado" && <p className="mt-1 text-[12px] text-apagado">{l.status}</p>}
            </div>
          </li>
        ))}
      </ul>
      <p className="text-[12px] text-apagado">
        Fonte: {info.fonte}. A situação é atualizada a cada 2 minutos e não substitui os avisos oficiais do Metrô, da CPTM e das concessionárias.
        A Linha 7 não aparece na fonte hoje.
      </p>
    </div>
  );
}
