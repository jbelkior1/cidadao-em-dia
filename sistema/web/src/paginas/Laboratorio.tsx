import { Play, Shuffle } from "lucide-react";
import { useEffect, useState } from "react";

import { SeloMateria } from "../componentes/Blocos";
import { api, type OpcoesLaboratorio, type Opiniao, type Simulacao } from "../lib/api";

const VEREDITO: Record<Opiniao["veredito"], string> = {
  usaria: "bg-ok-suave text-ok",
  "em dúvida": "bg-alerta-suave text-alerta",
  "não usaria": "bg-erro-suave text-erro",
};

function Barras({ linhas, sufixo, maximo, cor }: { linhas: { rotulo: string; valor: number; extra?: string }[]; sufixo: string; maximo: number; cor: string }) {
  return (
    <ul className="space-y-2.5">
      {linhas.map((l) => (
        <li key={l.rotulo} className="grid grid-cols-1 gap-1 sm:grid-cols-[12rem_minmax(0,1fr)] sm:items-center sm:gap-3">
          <span className="text-[14px] leading-tight">
            {l.rotulo}
            {l.extra && <span className="block text-[12px] text-apagado">{l.extra}</span>}
          </span>
          <span className="flex items-center gap-2">
            <span className="relative h-3 flex-1 rounded-full bg-fundo" title={`${l.rotulo}: ${l.valor}${sufixo}`}>
              <span className="absolute inset-y-0 left-0 rounded-full" style={{ width: `${maximo ? (100 * l.valor) / maximo : 0}%`, background: cor }} />
            </span>
            <span className="w-14 shrink-0 text-right text-[14px] font-semibold tabular-nums">
              {l.valor}
              {sufixo}
            </span>
          </span>
        </li>
      ))}
    </ul>
  );
}

export default function Laboratorio() {
  const [opcoes, setOpcoes] = useState<OpcoesLaboratorio | null>(null);
  const [parte, setParte] = useState("Linha parada na hora do pico");
  const [canais, setCanais] = useState<string[]>(["App e site", "WhatsApp (futuro)"]);
  const [n, setN] = useState(3000);
  const [semente, setSemente] = useState(7);
  const [sim, setSim] = useState<Simulacao | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState("");

  const rodar = async (novaSemente = semente) => {
    setOcupado(true);
    setErro("");
    try {
      setSim(await api.simular({ parte, canais, n, semente: novaSemente }));
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não consegui rodar a simulação.");
    } finally {
      setOcupado(false);
    }
  };

  useEffect(() => {
    api.laboratorio().then(setOpcoes).catch(() => setOpcoes(null));
    void rodar();
  }, []);

  const alternarCanal = (c: string) => setCanais((atual) => (atual.includes(c) ? atual.filter((x) => x !== c) : [...atual, c]));
  const outraAmostra = () => {
    const s = semente + 1;
    setSemente(s);
    void rodar(s);
  };
  const principal = sim?.barreiras[0]?.barreira ?? "nenhuma";

  return (
    <div className="mx-auto w-full max-w-5xl space-y-8 px-4 py-8 lg:px-8">
      <header className="space-y-3">
        <h2 className="text-2xl font-bold">A sociedade usando o sistema</h2>
        <p className="max-w-3xl text-[17px] text-apagado">
          Dez passageiros simulados de São Paulo vivem uma situação do dia com a Auxilia. Cada um tem o seu trajeto, a sua internet e a sua
          familiaridade com o celular. A conversa de cada um vem do sistema de verdade (rede, desvio, decisão e segurança); a situação e as
          pessoas são simuladas.
        </p>
        <div className="flex flex-wrap items-center gap-2 text-[13px] text-apagado">
          <span className="opacity-60"><SeloMateria selo={{ materia: "PAI", papel: "falas com IA (em breve)" }} /></span>
          <span className="rounded-full bg-alerta-suave px-2.5 py-0.5 font-semibold text-alerta">personas e pesos fictícios</span>
        </div>
      </header>

      <details className="rounded-xl border border-linha bg-superficie px-4 py-3 text-[15px]">
        <summary className="cursor-pointer font-semibold">Como a simulação funciona</summary>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-apagado">
          <li><span className="font-semibold text-tinta">Personas.</span> Dez pessoas fictícias com idade, onde moram, internet, familiaridade com o celular, confiança em aviso pelo celular, o que precisam, o canal que preferem e um medo.</li>
          <li><span className="font-semibold text-tinta">Avaliação.</span> Para a parte do produto e os canais escolhidos, um modelo logístico calcula a chance de cada pessoa usar: quanto o produto atende a necessidade dela, menos as barreiras de internet, de uso do celular e de confiança. Cada pessoa usa o canal que funciona melhor para ela.</li>
          <li><span className="font-semibold text-tinta">Fala.</span> A opinião de cada pessoa é montada a partir dos motivos que mais pesaram. Nesta versão não há IA: as falas seguem regras.</li>
          <li><span className="font-semibold text-tinta">População.</span> Milhares de pessoas parecidas com as personas, com variação aleatória, estimam a adesão por perfil.</li>
        </ol>
        <p className="mt-3 text-apagado">
          A ideia vem do <a className="text-marca-forte underline" href="https://github.com/microsoft/TinyTroupe" target="_blank" rel="noreferrer">TinyTroupe</a> (Microsoft),
          que simula grupos focais com personas. Os pesos são escritos à mão e servem para discutir o produto; o teste com pessoas de verdade, que PCP, SERS e PAI pedem, é o que vale.
        </p>
      </details>

      <section className="space-y-4 rounded-xl border border-linha bg-superficie p-5">
        <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_12rem]">
          <div>
            <label htmlFor="parte" className="block text-[15px] font-semibold">Situação do dia</label>
            <select id="parte" value={parte} onChange={(e) => setParte(e.target.value)} className="mt-1 w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px]">
              {(opcoes?.partes ?? [parte]).map((p) => <option key={p}>{p}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="tamanho" className="block text-[15px] font-semibold">Tamanho da população</label>
            <select id="tamanho" value={n} onChange={(e) => setN(Number(e.target.value))} className="mt-1 w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px]">
              {(opcoes?.tamanhos ?? [n]).map((t) => <option key={t} value={t}>{t.toLocaleString("pt-BR")} pessoas</option>)}
            </select>
          </div>
        </div>
        <div>
          <p className="text-[15px] font-semibold">Por onde a Auxilia chega</p>
          <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label="Canais">
            {(opcoes?.canais ?? canais).map((c) => (
              <button key={c} type="button" aria-pressed={canais.includes(c)} onClick={() => alternarCanal(c)}
                className={`rounded-full px-4 py-2 text-[15px] font-semibold ${canais.includes(c) ? "bg-marca text-white" : "bg-superficie text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave"}`}>
                {c}
              </button>
            ))}
          </div>
          {canais.length === 0 && <p className="mt-2 text-[13px] text-apagado">Sem canal escolhido, a simulação usa App e site.</p>}
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={() => rodar()} disabled={ocupado} className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-50">
            <Play className="size-4" aria-hidden /> {ocupado ? "Rodando..." : "Rodar a simulação"}
          </button>
          <button type="button" onClick={outraAmostra} disabled={ocupado} className="inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave disabled:opacity-50">
            <Shuffle className="size-4" aria-hidden /> Rodar com outra amostra
          </button>
        </div>
      </section>

      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}

      {sim && (
        <>
          <section className="space-y-3">
            <h3 className="text-lg font-bold">Resumo</h3>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-xl border border-linha bg-superficie px-4 py-3">
                <p className="text-3xl font-bold">{sim.usariam} de {sim.total_personas}</p>
                <p className="text-[14px] font-semibold">personas usariam</p>
              </div>
              <div className="rounded-xl border border-linha bg-superficie px-4 py-3">
                <p className="text-3xl font-bold">{sim.adesao}%</p>
                <p className="text-[14px] font-semibold">adesão estimada</p>
                <p className="text-[12px] text-apagado">em {sim.n.toLocaleString("pt-BR")} pessoas sintéticas</p>
              </div>
              <div className="rounded-xl border border-linha bg-superficie px-4 py-3">
                <p className="text-2xl leading-tight font-bold">{principal}</p>
                <p className="text-[14px] font-semibold">principal barreira</p>
                <p className="text-[12px] text-apagado">entre quem não usaria</p>
              </div>
            </div>
            <p className="text-[13px] text-apagado">Testando: {sim.parte}. Canais: {sim.canais.join(", ")}. Amostra {sim.semente}. Dados fictícios.</p>
          </section>

          <section className="space-y-3">
            <h3 className="text-lg font-bold">O que as pessoas disseram</h3>
            <ul className="grid gap-3 md:grid-cols-2">
              {sim.opinioes.map((o) => (
                <li key={o.id} className="space-y-2 rounded-xl border border-linha bg-superficie p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="font-bold">{o.nome}, {o.idade} anos</p>
                    <span className={`rounded-full px-2.5 py-0.5 text-[12px] font-semibold ${VEREDITO[o.veredito]}`}>{o.veredito} · nota {o.nota} de 5</span>
                  </div>
                  <p className="text-[13px] text-apagado">{o.quem}, {o.onde}. Trajeto: {o.trajeto}. Internet: {o.internet}.</p>
                  {o.conversa && (
                    <div className="space-y-1.5 rounded-xl bg-fundo p-2.5" aria-label={`Conversa de ${o.nome} com a Auxilia`}>
                      <p className="ml-auto w-fit max-w-[90%] rounded-2xl rounded-br-md bg-marca px-3 py-1.5 text-[14px] text-white">{o.conversa.pessoa}</p>
                      <p className="w-fit max-w-[95%] rounded-2xl rounded-bl-md bg-superficie px-3 py-1.5 text-[14px] ring-1 ring-linha">{o.conversa.auxilia}</p>
                    </div>
                  )}
                  <p className="text-[15px] leading-relaxed italic">“{o.fala}”</p>
                  <p className="text-[13px] text-apagado">
                    Canal que funciona melhor para {o.genero === "f" ? "ela" : "ele"}: {o.canal}. Sugestão: {o.sugestao}.
                  </p>
                </li>
              ))}
            </ul>
          </section>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="space-y-3 rounded-xl border border-linha bg-superficie p-5">
              <h3 className="text-lg font-bold">Adesão por perfil</h3>
              <p className="text-[13px] text-apagado">Pessoas sintéticas de cada perfil que usariam o produto.</p>
              <Barras cor="#0E6B62" sufixo="%" maximo={100} linhas={sim.perfis.map((p) => ({ rotulo: p.perfil, valor: p.adesao, extra: `${p.pessoas.toLocaleString("pt-BR")} pessoas` }))} />
            </section>
            <section className="space-y-3 rounded-xl border border-linha bg-superficie p-5">
              <h3 className="text-lg font-bold">Por que não usariam</h3>
              <p className="text-[13px] text-apagado">A barreira que mais pesou para cada pessoa sintética que não usaria.</p>
              {sim.barreiras.length ? (
                <Barras cor="#9A4F06" sufixo="" maximo={Math.max(...sim.barreiras.map((b) => b.pessoas))}
                  linhas={sim.barreiras.map((b) => ({ rotulo: b.barreira, valor: b.pessoas }))} />
              ) : (
                <p className="text-[14px] text-apagado">Todas usariam.</p>
              )}
            </section>
          </div>

          {sim.sugestoes.length > 0 && (
            <section className="space-y-2">
              <h3 className="text-lg font-bold">Sugestões mais citadas</h3>
              <ul className="list-disc space-y-1 pl-5 text-[15px]">
                {sim.sugestoes.map((s) => <li key={s.sugestao}>{s.sugestao} <span className="text-apagado">({s.pessoas} {s.pessoas === 1 ? "pessoa" : "pessoas"})</span></li>)}
              </ul>
            </section>
          )}
        </>
      )}
    </div>
  );
}
