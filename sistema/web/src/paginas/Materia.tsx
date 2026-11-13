import { ArrowUpRight } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Checklist from "../componentes/Checklist";
import Fluxograma from "../componentes/Fluxograma";
import { TesteCs, TesteDsa, TesteEmConstrucao, TesteMlam, TestePcp, TesteSers } from "../componentes/Testes";
import { api, type DadosMateria, type ResumoChecklist } from "../lib/api";

const PARTES = ["Entenda", "Teste", "Checklist da entrega"] as const;
type Parte = (typeof PARTES)[number];

function Entenda({ dados }: { dados: DadosMateria }) {
  const m = dados.materia;
  const navegar = useNavigate();
  return (
    <div className="space-y-7">
      <section className="space-y-2">
        <h3 className="text-lg font-bold">O que faz no sistema</h3>
        <p className="text-[17px] leading-relaxed">{m.papel}</p>
      </section>
      <section className="space-y-2">
        <h3 className="text-lg font-bold">Como ajuda o cidadão</h3>
        <p className="text-[17px] leading-relaxed">{m.ajuda}</p>
      </section>
      {m.quando && m.quando.length > 0 && (
        <section className="space-y-2">
          <h3 className="text-lg font-bold">Quando entra em ação</h3>
          <ul className="list-disc space-y-1 pl-5 text-[16px]">{m.quando.map((q) => <li key={q}>{q}</li>)}</ul>
        </section>
      )}
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl border border-linha bg-superficie p-4">
          <p className="text-[13px] font-semibold tracking-wide text-apagado uppercase">Recebe</p>
          <p className="mt-1 text-[15px]">{m.recebe}</p>
        </div>
        <div className="rounded-xl border border-linha bg-superficie p-4">
          <p className="text-[13px] font-semibold tracking-wide text-apagado uppercase">Devolve</p>
          <p className="mt-1 text-[15px]">{m.devolve}</p>
        </div>
      </div>
      <section className="space-y-2">
        <h3 className="text-lg font-bold">A parte dela no fluxograma</h3>
        <p className="text-[14px] text-apagado">Em destaque, {m.cod} e as ligações com as telas. O resto fica em cinza.</p>
        <Fluxograma destaque={m.cod} />
      </section>
      <section className="space-y-2">
        <h3 className="text-lg font-bold">A regra principal</h3>
        <p className="text-[16px] leading-relaxed">{m.regra}</p>
      </section>
      <section className="space-y-2 rounded-xl bg-marca-suave p-4">
        <h3 className="text-[15px] font-bold text-marca-forte">Nesta versão</h3>
        <p className="text-[15px]">{m.nesta_versao}</p>
        {m.pasta && (
          <p className="text-[14px]">
            A entrega fica em <code className="rounded bg-superficie px-1.5 py-0.5 text-[13px]">{m.pasta}</code> e roda com{" "}
            <code className="rounded bg-superficie px-1.5 py-0.5 text-[13px]">{m.rodar}</code>.
          </p>
        )}
      </section>
      {!!m.ver_funcionando?.length && (
        <section className="space-y-2">
          <h3 className="text-lg font-bold">Ver funcionando</h3>
          <div className="flex flex-wrap gap-2">
            {m.ver_funcionando.map((v) => (
              <button key={v.rota} type="button" onClick={() => navegar(v.rota)}
                className="inline-flex items-center gap-1.5 rounded-full bg-superficie px-4 py-2 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave">
                {v.rotulo} <ArrowUpRight className="size-4" aria-hidden />
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Teste({ dados }: { dados: DadosMateria }) {
  const cod = dados.materia.cod;
  return (
    <div className="space-y-5">
      <p className="rounded-xl border border-linha bg-superficie px-4 py-3 text-[15px]">
        <span className="font-semibold">Como testar: </span>
        {dados.materia.como_testar}
      </p>
      {cod === "PCP" && <TestePcp />}
      {cod === "CS" && <TesteCs />}
      {cod === "DSA" && <TesteDsa />}
      {cod === "SERS" && <TesteSers />}
      {cod === "MLAM" && <TesteMlam />}
      {(cod === "PAI" || cod === "MMC" || cod === "COA") && <TesteEmConstrucao cod={cod} />}
    </div>
  );
}

const VAZIO = { total: 0, prontos: 0, faltam: 0, percentual: 0 };

/** Duas barras separadas: o código (escrito no repositório) e o que só a equipe faz. Um número só
 *  engana: uma matéria com o código inteiro pronto aparecia pela metade por causa de vídeo e RM. */
function Andamento({ resumo }: { resumo: ResumoChecklist }) {
  const { codigo, grupo } = resumo.por_quem ?? { codigo: VAZIO, grupo: VAZIO };   // API antiga não manda por_quem
  const barras = [
    { rotulo: "Código no repositório", dado: codigo, cor: "bg-ok" },
    { rotulo: "Equipe (vídeo, testes, RM, envio)", dado: grupo, cor: "bg-marca" },
  ].filter((b) => b.dado.total > 0);
  if (!barras.length) {
    return (
      <p className="text-[14px] text-apagado">
        Checklist: <span className="font-semibold text-tinta">{resumo.percentual}%</span> · {resumo.por_status.Feito} de {resumo.total}
      </p>
    );
  }
  return (
    <div className="space-y-2">
      <p className="text-[14px] text-apagado">
        Checklist da entrega: <span className="font-semibold text-tinta">{resumo.total} itens</span> do enunciado
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
      {codigo.total > 0 && codigo.faltam === 0 && (
        <p className="text-[13px] text-ok">O código desta matéria está escrito e rodando. O que falta é da equipe.</p>
      )}
    </div>
  );
}

export default function Materia() {
  const { cod = "" } = useParams();
  const [dados, setDados] = useState<DadosMateria | null>(null);
  const [erro, setErro] = useState("");
  const [parte, setParte] = useState<Parte>("Entenda");

  useEffect(() => {
    setDados(null);
    setErro("");
    setParte("Entenda");
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
          <button key={p} type="button" role="tab" aria-selected={parte === p} onClick={() => setParte(p)}
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
            <Checklist key={m.cod} cod={m.cod} dados={dados.checklist} cor={m.cor} />
          ) : (
            <p className="rounded-xl border border-dashed border-linha bg-superficie p-5 text-apagado">O checklist desta matéria ainda não foi gerado.</p>
          ))}
      </div>
    </div>
  );
}
