import { ArrowRight, Bus, CalendarClock, Map as MapaIcone, Megaphone, Shuffle, ThumbsUp, type LucideIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api, type ResumoAvaliacoes } from "../lib/api";

/*
 * Avaliação usuários: o que as pessoas acharam do Dá Tempo?. Em cima, a síntese da equipe sobre as conversas
 * em que o sistema foi apresentado (cerca de 15 pessoas). Embaixo, as avaliações com nota feitas no formulário
 * "Avaliar o Dá Tempo?" (/avaliar), que alimentam os relatórios de teste com usuários da PAI, da SERS e da PCP.
 */

type Tema = { Icone: LucideIcon; titulo: string; texto: string; tom?: "critica" | "destaque" | "pedido" };

const TEMAS: Tema[] = [
  { Icone: ThumbsUp, titulo: "Ajudaria no dia a dia", texto: "A maioria gostou e disse que o app facilitaria a rotina de quem depende de trem e metrô." },
  { Icone: Shuffle, titulo: "A informação está espalhada", texto: "Hoje a pessoa vai descobrindo o problema ao longo do dia, ou só quando já chegou na estação." },
  { Icone: CalendarClock, titulo: "Falta um acompanhamento diário", texto: "Não existe nada que ajude a decidir antes de sair de casa, todos os dias." },
  { Icone: MapaIcone, titulo: "\"O Maps já faz parte disso\"", texto: "Algumas pessoas lembraram que o Google Maps já mostra rota e tempo de viagem.", tom: "critica" },
  {
    Icone: Megaphone, titulo: "O diferencial é relatar na hora",
    texto: "O que mais chamou atenção foi o Relatar: quem está no trem avisa na hora e a comunidade se comunica. As pessoas disseram não conhecer outro app que faça isso hoje.",
    tom: "destaque",
  },
  { Icone: Bus, titulo: "Pedido: dados de ônibus", texto: "Sugestão que entra como próxima etapa do projeto: incluir os ônibus, que hoje ficam de fora.", tom: "pedido" },
];

const fmt = (n: number | null | undefined, casas = 1) => (n === null || n === undefined ? "—" : n.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }));
const corDoTom: Record<string, string> = {
  critica: "bg-fundo text-apagado", destaque: "bg-marca text-white", pedido: "bg-marca-suave text-marca-forte",
};

export default function AvaliacaoUsuarios() {
  const [r, setR] = useState<ResumoAvaliacoes | null>(null);
  const [erro, setErro] = useState(false);
  useEffect(() => {
    api.avaliacoes().then(setR).catch(() => setErro(true));
  }, []);

  const tempoMedio = r && r.pessoas ? r.tarefas.filter((t) => t.tempo_medio_s !== null).map((t) => t.tempo_medio_s as number) : [];
  const acertos = r && r.pessoas ? r.tarefas.filter((t) => t.acerto_percentual !== null).map((t) => t.acerto_percentual as number) : [];

  return (
    <div className="mx-auto w-full max-w-4xl space-y-10 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <h2 className="text-2xl font-bold sm:text-3xl">Avaliação usuários</h2>
        <p className="max-w-3xl text-[17px] text-apagado">
          O que as pessoas acharam do Dá Tempo?: primeiro, o que ouvimos ao apresentar o sistema; depois, as avaliações com nota de quem fez o
          teste guiado.
        </p>
        <Link to="/avaliar" className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
          Avaliar o Dá Tempo?<ArrowRight className="size-4" aria-hidden />
        </Link>
      </header>

      <section className="space-y-4" aria-labelledby="titulo-ouvimos">
        <div className="space-y-1">
          <h3 id="titulo-ouvimos" className="text-xl font-bold">O que ouvimos ao apresentar o Dá Tempo?</h3>
          <p className="text-[15px] text-apagado">
            Apresentamos o sistema para cerca de 15 pessoas: família, colegas da faculdade, conhecidos e pessoas do trabalho. A conversa foi
            livre, sem roteiro; abaixo está o que mais apareceu, na síntese da equipe.
          </p>
        </div>
        <ul className="grid gap-3 sm:grid-cols-2">
          {TEMAS.map(({ Icone, titulo, texto, tom }) => (
            <li key={titulo} className={`flex gap-3 rounded-xl border p-4 ${tom === "destaque" ? "border-marca/50 bg-marca-suave/60" : "border-linha bg-superficie"}`}>
              <span className={`flex size-9 shrink-0 items-center justify-center rounded-full ${tom ? corDoTom[tom] : "bg-marca-suave text-marca-forte"}`}>
                <Icone className="size-[18px]" aria-hidden />
              </span>
              <div className="min-w-0 space-y-1">
                <p className="text-[16px] leading-tight font-bold">{titulo}</p>
                <p className="text-[15px] text-apagado">{texto}</p>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="space-y-4" aria-labelledby="titulo-notas">
        <div className="space-y-1">
          <h3 id="titulo-notas" className="text-xl font-bold">Avaliações com nota</h3>
          <p className="text-[15px] text-apagado">
            Cada pessoa usou o app sozinha: três tarefas cronometradas, a parte de energia e cinco perguntas de 1 a 5. Ninguém se identifica.
          </p>
        </div>

        {erro && <p className="rounded-xl bg-fundo px-4 py-3 text-[15px] text-apagado ring-1 ring-linha ring-inset">Não deu para carregar as avaliações agora.</p>}
        {r && r.pessoas === 0 && (
          <div className="space-y-2 rounded-xl border border-dashed border-linha bg-superficie p-5 text-center">
            <p className="text-[16px] font-semibold">Ainda não há avaliações com nota.</p>
            <p className="text-[15px] text-apagado">Faça a sua: leva uns 10 minutos, pelo celular.</p>
            <Link to="/avaliar" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">Avaliar agora<ArrowRight className="size-4" aria-hidden /></Link>
          </div>
        )}

        {r && r.pessoas > 0 && (
          <>
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[
                ["Pessoas", String(r.pessoas)],
                ["Facilidade média", `${fmt(r.facilidade_media)} de 5`],
                ["Tempo médio por tarefa", tempoMedio.length ? `${fmt(tempoMedio.reduce((a, b) => a + b, 0) / tempoMedio.length, 0)} s` : "—"],
                ["Acerto nas tarefas", acertos.length ? `${Math.round(acertos.reduce((a, b) => a + b, 0) / acertos.length)}%` : "—"],
              ].map(([rotulo, valor]) => (
                <div key={rotulo} className="rounded-xl border border-linha bg-superficie p-4">
                  <dt className="text-[13px] text-apagado">{rotulo}</dt>
                  <dd className="text-2xl font-bold">{valor}</dd>
                </div>
              ))}
            </dl>

            <div className="overflow-x-auto rounded-xl border border-linha bg-superficie">
              <table className="w-full text-left text-[14px]">
                <thead className="bg-fundo text-apagado">
                  <tr><th className="px-4 py-2.5 font-semibold">Tarefa</th><th className="px-3 py-2.5 font-semibold">Tempo médio</th><th className="px-3 py-2.5 font-semibold">Acharam</th><th className="px-3 py-2.5 font-semibold">Acerto</th></tr>
                </thead>
                <tbody>
                  {r.tarefas.map((t) => (
                    <tr key={t.tarefa} className="border-t border-linha">
                      <td className="px-4 py-2.5">{t.tarefa}</td>
                      <td className="px-3 py-2.5 tabular-nums">{t.tempo_medio_s === null ? "—" : `${fmt(t.tempo_medio_s, 0)} s`}</td>
                      <td className="px-3 py-2.5 tabular-nums">{t.acharam} de {t.pessoas}</td>
                      <td className="px-3 py-2.5 tabular-nums">{t.acerto_percentual === null ? "—" : `${t.acerto_percentual}%`}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
                <p className="text-[15px] font-bold">Facilidade (média de 1 a 5)</p>
                {r.facilidade.map((f) => (
                  <div key={f.pergunta} className="space-y-1">
                    <div className="flex justify-between gap-3 text-[14px]"><span>{f.pergunta}</span><span className="font-semibold tabular-nums">{fmt(f.media)}</span></div>
                    <div className="h-2 rounded-full bg-fundo"><div className="h-full rounded-full bg-marca" style={{ width: `${((f.media ?? 0) / 5) * 100}%` }} /></div>
                  </div>
                ))}
              </div>
              <div className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
                <p className="text-[15px] font-bold">Energia da viagem: entendeu?</p>
                {r.energia.map((e) => (
                  <div key={e.situacao} className="space-y-1 text-[14px]">
                    <p>{e.situacao}</p>
                    <p className="text-apagado tabular-nums">{e.sim} sim · {e["em parte"]} em parte · {e.nao} não</p>
                  </div>
                ))}
                <p className="border-t border-linha pt-2 text-[14px]">
                  Ajudaria a escolher como ir ao trabalho: <span className="font-semibold">{fmt(r.nota_energia_media)} de 5</span>
                </p>
              </div>
            </div>

            {r.comentarios.length > 0 && (
              <ul className="grid gap-3 sm:grid-cols-2">
                {r.comentarios.map((c) => (
                  <li key={c.pessoa} className="space-y-2 rounded-xl border border-linha bg-superficie p-4">
                    <p className="text-[13px] font-semibold text-apagado">
                      {c.pessoa}{c.perfil ? ` · ${c.perfil}` : ""}{c.media !== null ? ` · facilidade ${fmt(c.media)}` : ""}
                    </p>
                    {c.comentario && <p className="text-[15px]">"{c.comentario}"</p>}
                    {c.sugestao && <p className="text-[14px] text-apagado"><span className="font-semibold text-marca-forte">Sugestão: </span>{c.sugestao}</p>}
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
        <p className="text-[13px] text-apagado">
          Sem nome nem dado pessoal: os textos passam pela mesma barreira da Lia. Esses números entram nos relatórios de teste com usuários da
          PAI, da SERS e da PCP.
        </p>
      </section>
    </div>
  );
}
