import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import Checklist from "../componentes/Checklist";
import Fluxograma from "../componentes/Fluxograma";
import FluxoMateria from "../componentes/FluxoMateria";
import { TesteCoa, TesteCs, TesteDsa, TesteMlam, TesteMmc, TestePai, TestePcp, TesteSers } from "../componentes/Testes";
import { api, type DadosMateria, type ResumoChecklist } from "../lib/api";

const PARTES = ["Entenda", "Teste", "Checklist da entrega"] as const;
type Parte = (typeof PARTES)[number];
/** O endereço aceita ?parte=teste ou ?parte=checklist, para linkar direto numa parte. */
const POR_ENDERECO: Record<string, Parte> = { teste: "Teste", checklist: "Checklist da entrega" };
const NO_ENDERECO: Partial<Record<Parte, string>> = { Teste: "teste", "Checklist da entrega": "checklist" };

/** O que o professor abre primeiro: o formato da entrega, como rodar e os arquivos no GitHub. */
function Entrega({ m }: { m: DadosMateria["materia"] }) {
  const arquivos = m.arquivos ?? [];
  return (
    <section aria-labelledby="titulo-entrega" className="space-y-4 rounded-xl border border-linha bg-superficie p-5">
      <div className="space-y-1">
        <h3 id="titulo-entrega" className="text-lg font-bold">A entrega desta matéria</h3>
        <p className="text-[15px] leading-relaxed">{m.entrega}</p>
      </div>
      {m.pasta ? (
        <p className="text-[14px]">
          Pasta{" "}
          <a href={m.pasta_url} target="_blank" rel="noreferrer" className="rounded bg-fundo px-1.5 py-0.5 font-mono text-[13px] text-marca-forte underline">
            {m.pasta}
          </a>
          {m.rodar && (
            <>
              {" "}· roda com <code className="rounded bg-fundo px-1.5 py-0.5 text-[13px]">{m.rodar}</code>
            </>
          )}
        </p>
      ) : (
        <p className="text-[14px] text-apagado">Entregue à parte, fora deste repositório, no formato do enunciado.</p>
      )}
      {arquivos.length > 0 && (
        <div className="space-y-2">
          <p className="text-[13px] font-semibold text-apagado">Arquivos no GitHub</p>
          <ul className="grid gap-1.5 sm:grid-cols-2">
            {arquivos.map((a) => (
              <li key={a.caminho}>
                <a href={a.url} target="_blank" rel="noreferrer"
                  className="group flex items-start gap-2 rounded-lg px-2.5 py-2 hover:bg-fundo focus-visible:outline-2 focus-visible:outline-marca">
                  <ExternalLink className="mt-0.5 size-4 shrink-0 text-marca" aria-hidden />
                  <span className="min-w-0">
                    <span className="block text-[14px] font-semibold group-hover:underline">{a.rotulo}</span>
                    <span className="block truncate font-mono text-[12px] text-apagado">{a.caminho}</span>
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Entenda({ dados }: { dados: DadosMateria }) {
  const m = dados.materia;
  return (
    <div className="space-y-8">
      <Entrega m={m} />
      <section className="space-y-2">
        <h3 className="text-lg font-bold">O que faz no sistema</h3>
        <p className="text-[17px] leading-relaxed">{m.explicacao}</p>
      </section>
      <section className="space-y-3">
        <h3 className="text-lg font-bold">O caminho por dentro de {m.cod}</h3>
        <FluxoMateria fluxo={m.fluxo} cor={m.cor} />
      </section>
      <section className="space-y-2">
        <h3 className="text-lg font-bold">Onde {m.cod} entra no sistema</h3>
        <Fluxograma destaque={m.cod} />
      </section>
      <section className="space-y-2">
        <h3 className="text-lg font-bold">Onde ver no site</h3>
        <ul className="grid gap-1.5 sm:grid-cols-2">
          {m.rotas.map((r) => (
            <li key={r.rota}>
              <Link to={r.rota} className="flex items-baseline justify-between gap-3 rounded-lg px-2.5 py-2 hover:bg-superficie focus-visible:outline-2 focus-visible:outline-marca">
                <span className="text-[14px] font-semibold text-marca-forte">{r.rotulo}</span>
                <span className="truncate font-mono text-[12px] text-apagado">{r.rota}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <p className="rounded-xl bg-marca-suave px-4 py-3 text-[15px]"><span className="font-bold text-marca-forte">Nesta versão: </span>{m.nesta_versao}</p>
    </div>
  );
}

function Teste({ dados }: { dados: DadosMateria }) {
  const cod = dados.materia.cod;
  return (
    <div className="space-y-5">
      <p className="text-[14px] text-apagado">{dados.materia.como_testar}</p>
      {cod === "PCP" && <TestePcp />}
      {cod === "CS" && <TesteCs />}
      {cod === "DSA" && <TesteDsa />}
      {cod === "SERS" && <TesteSers />}
      {cod === "MLAM" && <TesteMlam />}
      {cod === "PAI" && <TestePai />}
      {cod === "MMC" && <TesteMmc />}
      {cod === "COA" && <TesteCoa links={dados.materia.links} />}
    </div>
  );
}

/** Duas barras separadas: o que está no repositório e o que só a equipe faz. Um número só
 *  engana: uma matéria com o código inteiro pronto aparecia pela metade por causa de vídeo e envio. */
function Andamento({ resumo }: { resumo: ResumoChecklist }) {
  const { sistema, equipe } = resumo.por_quem;
  const barras = [
    { rotulo: "No repositório", dado: sistema, cor: "bg-ok" },
    { rotulo: "Da equipe (vídeo, testes, envio)", dado: equipe, cor: "bg-marca" },
  ].filter((b) => b.dado.total > 0);
  return (
    <div className="space-y-2">
      <p className="text-[14px] text-apagado">
        Checklist da entrega: <span className="font-semibold text-tinta">{resumo.total} itens</span> do enunciado, {resumo.por_status.Feito} feitos
      </p>
      <div className="grid max-w-xl gap-1.5">
        {barras.map(({ rotulo, dado, cor }) => (
          <div key={rotulo} className="flex items-center gap-2.5">
            <span className="w-56 shrink-0 text-[13px] text-apagado">{rotulo}</span>
            <span className="h-2 min-w-0 flex-1 overflow-hidden rounded-full bg-cinza">
              <span className={`block h-full rounded-full ${cor}`} style={{ width: `${dado.percentual}%` }} />
            </span>
            <span className="w-16 shrink-0 text-right text-[13px] font-semibold tabular-nums">
              {dado.prontos}/{dado.total}
            </span>
          </div>
        ))}
      </div>
      {sistema.total > 0 && sistema.faltam === 0 && (
        <p className="text-[13px] text-ok">A parte desta matéria no repositório está pronta e conferida. O que falta é da equipe.</p>
      )}
    </div>
  );
}

export default function Materia() {
  const { cod = "" } = useParams();
  const [dados, setDados] = useState<DadosMateria | null>(null);
  const [erro, setErro] = useState("");
  const [busca, setBusca] = useSearchParams();
  const parte = POR_ENDERECO[busca.get("parte") ?? ""] ?? "Entenda";
  const trocar = (p: Parte) => setBusca(NO_ENDERECO[p] ? { parte: NO_ENDERECO[p] as string } : {}, { replace: true });

  useEffect(() => {
    setDados(null);
    setErro("");
    api.materia(cod).then(setDados).catch((e) => setErro(e instanceof Error ? e.message : "Não consegui carregar."));
  }, [cod]);

  if (erro) return <p className="m-8 rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>;
  if (!dados) return <p className="m-8 text-apagado">Carregando...</p>;
  const m = dados.materia;
  const resumo = dados.checklist?.resumo;

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6 px-4 py-8 lg:px-8">
      <header className="space-y-3 border-l-4 pl-4" style={{ borderColor: m.cor }}>
        <p className="text-[13px] font-semibold tracking-wide text-apagado uppercase">{m.nome} ({m.cod})</p>
        <h2 className="text-3xl leading-tight font-bold">{m.curto}</h2>
        {resumo && <Andamento resumo={resumo} />}
      </header>

      <div className="flex flex-wrap gap-1 rounded-xl bg-superficie p-1 ring-1 ring-linha ring-inset sm:inline-flex" role="tablist" aria-label="Partes da página">
        {PARTES.map((p) => (
          <button key={p} type="button" role="tab" aria-selected={parte === p} onClick={() => trocar(p)}
            className={`rounded-lg px-4 py-2 text-[15px] font-semibold transition-colors ${parte === p ? "bg-marca text-white" : "text-apagado hover:text-tinta"}`}>
            {p}
          </button>
        ))}
      </div>

      <div role="tabpanel">
        {parte === "Entenda" && <Entenda dados={dados} />}
        {parte === "Teste" && <Teste dados={dados} />}
        {parte === "Checklist da entrega" &&
          (dados.checklist ? (
            <Checklist key={m.cod} cod={m.cod} dados={dados.checklist} editavel={dados.editavel} />
          ) : (
            <p className="rounded-xl border border-dashed border-linha bg-superficie p-5 text-apagado">O checklist desta matéria ainda não foi gerado.</p>
          ))}
      </div>
    </div>
  );
}
