import { ArrowUpRight, ChevronDown } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Checklist, { BarraProgresso } from "../componentes/Checklist";
import { api, type DadosMateria, type Painel } from "../lib/api";

function Numero({ valor, rotulo, detalhe }: { valor: string | number; rotulo: string; detalhe?: string }) {
  return (
    <div className="rounded-xl border border-linha bg-superficie px-4 py-3">
      <p className="text-3xl font-bold">{valor}</p>
      <p className="text-[14px] font-semibold">{rotulo}</p>
      {detalhe && <p className="text-[12px] text-apagado">{detalhe}</p>}
    </div>
  );
}

function APartePainel({ cod, nome, cor }: { cod: string; nome: string; cor: string }) {
  const [aberto, setAberto] = useState(false);
  const [dados, setDados] = useState<DadosMateria | null>(null);
  useEffect(() => {
    if (aberto && !dados) api.materia(cod).then(setDados).catch(() => setDados(null));
  }, [aberto, cod, dados]);
  return (
    <div>
      <button type="button" onClick={() => setAberto((v) => !v)} aria-expanded={aberto}
        className="flex w-full items-center gap-2 text-left text-[14px] font-semibold text-marca-forte">
        <ChevronDown className={`size-4 transition-transform ${aberto ? "rotate-180" : ""}`} aria-hidden />
        {aberto ? "Fechar o checklist" : "Abrir o checklist"}
      </button>
      {aberto && (
        <div className="mt-3">
          {dados?.checklist ? (
            <Checklist cod={cod} dados={dados.checklist} cor={cor} />
          ) : (
            <p className="text-[14px] text-apagado">{dados ? `O checklist de ${nome} ainda não foi gerado.` : "Carregando..."}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default function PainelEquipe() {
  const [p, setP] = useState<Painel | null>(null);
  const [erro, setErro] = useState("");
  useEffect(() => {
    api.painel().then(setP).catch((e) => setErro(e instanceof Error ? e.message : "Não consegui carregar."));
  }, []);

  if (erro) return <p className="m-8 rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>;
  if (!p) return <p className="m-8 text-apagado">Carregando...</p>;
  const g = p.geral;
  const noSistema = p.materias.filter((m) => m.no_sistema);
  const aParte = p.materias.filter((m) => !m.no_sistema);

  return (
    <div className="mx-auto w-full max-w-4xl space-y-8 px-4 py-8 lg:px-8">
      <header className="space-y-2">
        <h2 className="text-2xl font-bold">Painel da equipe</h2>
        <p className="text-[16px] text-apagado">O andamento de cada matéria. O checklist completo de cada uma fica na página dela, na parte Checklist da entrega.</p>
      </header>

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Numero valor={p.dias} rotulo="dias até a entrega" detalhe="19/11 às 23h55. Enviem até as 18h." />
        <Numero valor={`${g.por_status.Feito} de ${g.total}`} rotulo="itens feitos" />
        <Numero valor={g.por_status["Falta conferir"]} rotulo="falta conferir" detalhe="existe, mas o grupo precisa revisar" />
        <Numero valor={g.por_status["A fazer"]} rotulo="a fazer" detalhe={`${g.do_grupo} dependem do grupo`} />
      </div>

      <section className="space-y-3">
        <h3 className="text-lg font-bold">Matérias dentro do sistema</h3>
        <ul className="space-y-2">
          {noSistema.map((m) => (
            <li key={m.cod} className="grid gap-3 rounded-xl border border-linha bg-superficie p-4 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] sm:items-center">
              <div className="min-w-0">
                <p className="flex items-center gap-2 font-semibold">
                  <span className="size-2.5 shrink-0 rounded-full" style={{ background: m.cor }} />
                  {m.cod} · {m.nome}
                </p>
                <Link to={`/materias/${m.cod.toLowerCase()}`} className="mt-1 inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte underline">
                  Abrir a matéria e o checklist <ArrowUpRight className="size-3.5" aria-hidden />
                </Link>
              </div>
              {m.total ? <BarraProgresso resumo={m} cor={m.cor} /> : <p className="text-[13px] text-apagado">Checklist ainda não gerado.</p>}
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-lg font-bold">Entregues à parte</h3>
        <p className="text-[14px] text-apagado">Não entram no sistema. O checklist delas fica aqui.</p>
        <ul className="space-y-2">
          {aParte.map((m) => (
            <li key={m.cod} className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
              <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] sm:items-center">
                <p className="flex items-center gap-2 font-semibold">
                  <span className="size-2.5 shrink-0 rounded-full" style={{ background: m.cor }} />
                  {m.cod} · {m.nome}
                </p>
                {m.total ? <BarraProgresso resumo={m} cor={m.cor} /> : <p className="text-[13px] text-apagado">Checklist ainda não gerado.</p>}
              </div>
              <APartePainel cod={m.cod} nome={m.nome} cor={m.cor} />
            </li>
          ))}
        </ul>
      </section>

      {p.regras.length > 0 && (
        <details className="rounded-xl border border-linha bg-superficie px-4 py-3">
          <summary className="cursor-pointer text-[15px] font-semibold">Regras gerais da GS ({p.regras.length})</summary>
          <ul className="mt-3 space-y-2 text-[14px]">
            {p.regras.map((r) => (
              <li key={r.requisito}>
                <span className="font-semibold">{r.requisito}.</span> <span className="text-apagado">{r.detalhe}</span>
                {r.fonte && <span className="block text-[12px] text-apagado">{r.fonte}</span>}
              </li>
            ))}
          </ul>
        </details>
      )}
      {(p.alertas.length > 0 || p.divergencias.length > 0) && (
        <details className="rounded-xl border border-linha bg-superficie px-4 py-3">
          <summary className="cursor-pointer text-[15px] font-semibold">Alertas e divergências entre os documentos ({p.alertas.length + p.divergencias.length})</summary>
          <ul className="mt-3 list-disc space-y-1.5 pl-5 text-[14px] text-apagado">
            {[...p.alertas, ...p.divergencias].map((a) => <li key={a}>{a}</li>)}
          </ul>
        </details>
      )}
      {p.atualizado_em && <p className="text-[12px] text-apagado">Checklist atualizado em {p.atualizado_em.split("-").reverse().join("/")}.</p>}
    </div>
  );
}
