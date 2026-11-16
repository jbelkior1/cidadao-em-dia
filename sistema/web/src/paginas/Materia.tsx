import { ExternalLink, FlaskConical, Smartphone } from "lucide-react";
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

function Entenda({ dados, aoTestar }: { dados: DadosMateria; aoTestar: () => void }) {
  const m = dados.materia;
  const botao = "inline-flex items-center gap-2 rounded-full px-4 py-2 text-[15px] font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-marca";
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
      <section className="space-y-3 rounded-xl border border-linha bg-superficie p-5">
        <h3 className="text-lg font-bold">Ver funcionando</h3>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={aoTestar} className={`${botao} bg-marca text-white hover:bg-marca-forte`}>
            <FlaskConical className="size-4" aria-hidden />Testar {m.cod} aqui
          </button>
          {dados.no_sistema && (
            <>
              <Link to="/sistema" className={`${botao} text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave`}>
                <Smartphone className="size-4" aria-hidden />Ver no app
              </Link>
              <Link to="/app" className={`${botao} text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave`}>Abrir só o app (celular)</Link>
            </>
          )}
        </div>
        <p className="text-[14px] text-apagado"><span className="font-semibold text-tinta">Nesta versão: </span>{m.nesta_versao}</p>
      </section>
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

/** Duas barras separadas: o que está no repositório e o que fica fora dele. Um número só
 *  engana: uma matéria com o código inteiro pronto aparecia pela metade por causa de vídeo e envio. */
function Andamento({ resumo }: { resumo: ResumoChecklist }) {
  const { sistema, equipe } = resumo.por_quem;
  const barras = [
    { rotulo: "No repositório", dica: "código e documentos no GitHub", dado: sistema, cor: "bg-ok" },
    { rotulo: "Fora dele", dica: "vídeo, testes com pessoas e envio no portal", dado: equipe, cor: "bg-marca" },
  ].filter((b) => b.dado.total > 0);
  return (
    <div className="space-y-2">
      <p className="text-[14px] text-apagado">
        Checklist da entrega: <span className="font-semibold text-tinta">{resumo.total} itens</span> do enunciado, {resumo.por_status.Feito} feitos
      </p>
      <div className="grid max-w-xl gap-1.5">
        {barras.map(({ rotulo, dica, dado, cor }) => (
          <div key={rotulo} className="grid grid-cols-[7.5rem_minmax(0,1fr)_3.5rem] items-center gap-2.5" title={dica}>
            <span className="text-[13px] text-apagado">{rotulo}</span>
            <span className="h-2 overflow-hidden rounded-full bg-cinza">
              <span className={`block h-full rounded-full ${cor}`} style={{ width: `${dado.percentual}%` }} />
            </span>
            <span className="text-right text-[13px] font-semibold tabular-nums">
              {dado.prontos}/{dado.total}
            </span>
          </div>
        ))}
      </div>
      {sistema.total > 0 && sistema.faltam === 0 && (
        <p className="text-[13px] text-ok">A parte desta matéria no repositório está pronta e conferida. O que falta fica fora do código: vídeo, testes com pessoas e envio.</p>
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

      <div className="grid grid-cols-3 gap-1 rounded-xl bg-superficie p-1 ring-1 ring-linha ring-inset sm:inline-grid sm:w-auto sm:grid-cols-[auto_auto_auto]" role="tablist" aria-label="Partes da página">
        {PARTES.map((p) => (
          <button key={p} type="button" role="tab" aria-selected={parte === p} onClick={() => trocar(p)}
            className={`rounded-lg px-3 py-2 text-[15px] font-semibold transition-colors sm:px-4 ${parte === p ? "bg-marca text-white" : "text-apagado hover:text-tinta"}`}>
            {p === "Checklist da entrega" ? (<><span className="sm:hidden">Checklist</span><span className="hidden sm:inline">Checklist da entrega</span></>) : p}
          </button>
        ))}
      </div>

      <div role="tabpanel">
        {parte === "Entenda" && <Entenda dados={dados} aoTestar={() => { trocar("Teste"); document.querySelector("main")?.scrollTo({ top: 0 }); }} />}
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
