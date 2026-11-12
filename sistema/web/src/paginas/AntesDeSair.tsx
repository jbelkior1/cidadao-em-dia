import { ArrowDownUp, CloudLightning, Droplets, FileText, Footprints, Info, Leaf, MapPin, Route, Shield, TrainFront, Users } from "lucide-react";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import { useApp } from "../App";
import { SeloLinha, SituacaoLinha, hora } from "../componentes/Linha";
import { mobilidade, type EstacaoEscolha, type Etapa, type LinhaInfo, type PlanoDoDia, type Rota, type Seguranca } from "../lib/api";

const CHAVE = "plano-b-trajeto";
type Trajeto = { origem: string; destino: string };

function lerTrajeto(): Trajeto | null {
  try {
    const t = JSON.parse(localStorage.getItem(CHAVE) ?? "null");
    return t?.origem && t?.destino ? t : null;
  } catch {
    return null;
  }
}
function gravarTrajeto(t: Trajeto) {
  try {
    localStorage.setItem(CHAVE, JSON.stringify(t));
  } catch {
    /* sem armazenamento, vale só nesta visita */
  }
}

const VEREDITO = {
  pode_ir: "bg-ok-suave text-ok border-ok/30",
  mais_cedo: "bg-alerta-suave text-alerta border-alerta/30",
  plano_b: "bg-erro-suave text-erro border-erro/30",
};
const ICONE_MOTIVO = { falha: TrainFront, ok: TrainFront, sem_dado: Info, chuva: CloudLightning, alagamento: Droplets, pico: Users };
const kg = (valor: number) => (valor < 1 ? `${Math.round(valor * 1000).toLocaleString("pt-BR")} g` : `${valor.toLocaleString("pt-BR")} kg`);
const FAIXAS: Record<string, string> = { madrugada: "de madrugada", manha: "de manhã", tarde: "à tarde", noite: "à noite" };

/* ---------------------------------------------------------------- escolha de estação */

function CampoEstacao({ id, rotulo, valor, estacoes, aoMudar }: { id: string; rotulo: string; valor: string; estacoes: EstacaoEscolha[]; aoMudar: (id: string) => void }) {
  const atual = estacoes.find((e) => e.id === valor);
  const [texto, setTexto] = useState(atual?.nome ?? "");
  useEffect(() => setTexto(atual?.nome ?? ""), [atual?.nome]);
  return (
    <div className="min-w-0 flex-1">
      <label htmlFor={id} className="block text-[14px] font-semibold">{rotulo}</label>
      <input id={id} list={`${id}-lista`} value={texto} autoComplete="off" placeholder="Digite o nome da estação"
        onChange={(e) => {
          setTexto(e.target.value);
          const achada = estacoes.find((x) => x.nome.toLowerCase() === e.target.value.trim().toLowerCase());
          aoMudar(achada ? achada.id : "");
        }}
        className="mt-1 w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px] focus:border-marca focus:outline-none" />
      <datalist id={`${id}-lista`}>
        {estacoes.map((e) => <option key={e.id} value={e.nome}>{`Linha ${e.linhas.join(", ")}`}</option>)}
      </datalist>
    </div>
  );
}

/* ---------------------------------------------------------------- rota */

function Etapas({ rota, linhas }: { rota: Rota; linhas: Record<string, LinhaInfo> }) {
  return (
    <ol className="space-y-2">
      {rota.etapas.map((e: Etapa, i) =>
        e.via === "a pé" ? (
          <li key={i} className="flex items-center gap-3 pl-1 text-[14px] text-apagado">
            <Footprints className="size-5 shrink-0" aria-hidden />
            {e.de === e.ate ? `Troque de linha em ${e.de}, cerca de ${e.min} min a pé` : `Siga a pé de ${e.de} até ${e.ate}, cerca de ${e.min} min`}
          </li>
        ) : (
          <li key={i} className="flex items-center gap-3">
            <SeloLinha numero={e.via} cor={(e.linha ?? linhas[e.via])?.cor ?? "#888"} />
            <span className="min-w-0 text-[15px]">
              <span className="font-semibold">{e.de} → {e.ate}</span>
              <span className="block text-[13px] text-apagado">
                Linha {e.via}-{(e.linha ?? linhas[e.via])?.nome} · {e.paradas} {e.paradas === 1 ? "parada" : "paradas"} · {e.min} min
              </span>
            </span>
          </li>
        ),
      )}
    </ol>
  );
}

function CartaoSeguranca({ titulo, nome, s }: { titulo: string; nome: string; s: Seguranca }) {
  if (!s) {
    return (
      <div className="rounded-xl border border-dashed border-linha bg-superficie p-4">
        <p className="flex items-center gap-2 text-[15px] font-semibold"><Shield className="size-4" aria-hidden />{titulo}: {nome}</p>
        <p className="mt-1 text-[14px] text-apagado">Sem dado de segurança: a base da SSP-SP usada aqui cobre só as estações da capital.</p>
      </div>
    );
  }
  const tipos = Object.entries(s.por_tipo ?? {}).sort((a, b) => b[1] - a[1]);
  return (
    <div className="rounded-xl border border-linha bg-superficie p-4">
      <p className="flex items-center gap-2 text-[15px] font-semibold"><Shield className="size-4" aria-hidden />{titulo}: {s.estacao}</p>
      <p className="mt-1 text-[15px]">
        {s.total.toLocaleString("pt-BR")} ocorrências registradas a menos de {s.meta?.raio_m ?? 300} m, de {s.meta?.periodo ?? "2026"}. Mais comuns {FAIXAS[s.faixa_mais_comum] ?? s.faixa_mais_comum}
        {tipos[0] ? `, principalmente ${tipos[0][0]}` : ""}.
      </p>
      <p className="mt-1 text-[13px] text-apagado">Ande com o celular guardado e prefira saídas movimentadas. Contagem de registros da SSP-SP por estação, não taxa de risco: estação cheia tem mais registro.</p>
    </div>
  );
}

/* ---------------------------------------------------------------- página */

export default function AntesDeSair() {
  const { modoBanca } = useApp();
  const [estacoes, setEstacoes] = useState<EstacaoEscolha[]>([]);
  const [linhasInfo, setLinhasInfo] = useState<Record<string, LinhaInfo>>({});
  const [trajeto, setTrajeto] = useState<Trajeto | null>(lerTrajeto);
  const [origem, setOrigem] = useState(trajeto?.origem ?? "");
  const [destino, setDestino] = useState(trajeto?.destino ?? "");
  const [simular, setSimular] = useState("");
  const [plano, setPlano] = useState<PlanoDoDia | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    mobilidade.estacoes().then((r) => {
      setEstacoes(r.estacoes);
      setLinhasInfo(Object.fromEntries(r.linhas.map((l) => [l.numero, l])));
    }).catch(() => setErro("Não consegui carregar as estações. Confira se a API está ligada."));
  }, []);

  const conferir = async (t: Trajeto, sim = simular) => {
    setCarregando(true);
    setErro("");
    try {
      setPlano(await mobilidade.plano(t.origem, t.destino, sim || undefined));
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não consegui conferir o trajeto.");
    } finally {
      setCarregando(false);
    }
  };
  useEffect(() => {
    if (trajeto) void conferir(trajeto);
  }, [trajeto, simular]);

  const salvar = (evento: FormEvent) => {
    evento.preventDefault();
    if (!origem || !destino) return setErro("Escolha a estação de saída e a de chegada na lista.");
    if (origem === destino) return setErro("Escolha estações diferentes.");
    const t = { origem, destino };
    gravarTrajeto(t);
    setTrajeto(t);
  };
  const inverter = () => {
    setOrigem(destino);
    setDestino(origem);
  };
  const linhasDoTrajeto = useMemo(() => plano?.rota.linhas ?? [], [plano]);

  return (
    <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-6 lg:px-8">
      <form onSubmit={salvar} className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
        <p className="flex items-center gap-2 text-[15px] font-semibold"><Route className="size-4" aria-hidden />Seu trajeto</p>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <CampoEstacao id="origem" rotulo="Saio de" valor={origem} estacoes={estacoes} aoMudar={setOrigem} />
          <button type="button" onClick={inverter} aria-label="Inverter saída e chegada" className="self-center rounded-full p-2 text-apagado hover:bg-fundo sm:mb-1.5">
            <ArrowDownUp className="size-5" aria-hidden />
          </button>
          <CampoEstacao id="destino" rotulo="Vou para" valor={destino} estacoes={estacoes} aoMudar={setDestino} />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button type="submit" className="rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">Conferir e salvar</button>
          <span className="text-[13px] text-apagado">O trajeto fica só neste aparelho. Não pedimos conta nem localização.</span>
        </div>
      </form>

      {modoBanca && trajeto && (
        <div className="flex flex-wrap items-center gap-2 rounded-xl border border-dashed border-linha bg-superficie px-4 py-3 text-[14px]">
          <label htmlFor="simular" className="font-semibold">Demonstração: simular falha na linha</label>
          <select id="simular" value={simular} onChange={(e) => setSimular(e.target.value)} className="rounded-lg border border-linha bg-superficie px-2 py-1">
            <option value="">nenhuma (situação real)</option>
            {linhasDoTrajeto.map((n) => <option key={n} value={n}>{n} - {linhasInfo[n]?.nome}</option>)}
          </select>
          <span className="text-[12px] text-apagado">Só para o pitch. A falha simulada aparece marcada como simulação.</span>
        </div>
      )}

      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}

      {!trajeto && !erro && (
        <div className="space-y-2 rounded-xl border border-linha bg-superficie p-5">
          <p className="text-lg font-bold">Confira o caminho antes de sair de casa</p>
          <p className="text-[15px] text-apagado">Escolha onde você embarca e onde desce. O Plano B junta a situação das linhas, os avisos de chuva e os pontos de alagamento e diz se você pode ir, se deve sair mais cedo ou se é melhor desviar.</p>
        </div>
      )}

      {carregando && !plano && <p className="text-apagado">Conferindo as linhas e o tempo...</p>}

      {plano && (
        <>
          <section className={`space-y-3 rounded-2xl border p-5 ${VEREDITO[plano.veredito.codigo]}`} aria-live="polite">
            <p className="text-[13px] font-semibold tracking-wide uppercase opacity-80">{plano.origem} → {plano.destino} · agora</p>
            <p className="text-3xl leading-tight font-bold">{plano.veredito.texto}</p>
            <ul className="space-y-1.5 text-[15px] text-tinta">
              {plano.motivos.map((m, i) => {
                const Icone = ICONE_MOTIVO[m.tipo] ?? Info;
                return <li key={i} className="flex items-start gap-2"><Icone className="mt-0.5 size-4 shrink-0" aria-hidden />{m.texto}</li>;
              })}
            </ul>
            {modoBanca && plano.veredito.regra_provisoria && (
              <p className="text-[12px] text-apagado">Decisão pela regra provisória. A regra final sai da tabela-verdade da matéria de CS.</p>
            )}
          </section>

          {plano.plano_b && (
            <section className="space-y-4 rounded-2xl border-2 border-marca bg-superficie p-5">
              <p className="text-[13px] font-semibold tracking-wide text-marca-forte uppercase">Plano B</p>
              <p className="text-2xl font-bold">{plano.plano_b.recomendacao === "desviar" ? "Desvie" : "Espere ou use o ônibus de apoio"}</p>
              <p className="text-[16px]">{plano.plano_b.texto}</p>
              {plano.plano_b.alternativa && (
                <div className="space-y-2">
                  <p className="text-[14px] font-semibold">Caminho sem a linha com problema · {plano.plano_b.alternativa.minutos} min
                    {plano.plano_b.acrescimo_min !== null && plano.plano_b.acrescimo_min > 0 ? ` (+${plano.plano_b.acrescimo_min} min)` : ""}</p>
                  <Etapas rota={plano.plano_b.alternativa} linhas={linhasInfo} />
                </div>
              )}
              {plano.plano_b.parcial && (
                <div className="space-y-2 rounded-xl bg-fundo p-3">
                  <p className="text-[14px] font-semibold">{plano.plano_b.parcial.texto} · {plano.plano_b.parcial.rota.minutos} min</p>
                  <Etapas rota={plano.plano_b.parcial.rota} linhas={linhasInfo} />
                </div>
              )}
              <p className="text-[13px] text-apagado">
                {plano.plano_b.historico.suficiente
                  ? `Base: ${plano.plano_b.historico.episodios} falhas registradas nesta linha desde ${plano.plano_b.historico.coletando_desde}.`
                  : `Ainda há pouco histórico de falhas desta linha${plano.plano_b.historico.coletando_desde ? ` (coletando desde ${plano.plano_b.historico.coletando_desde})` : ""}. A recomendação usa só o tempo do desvio.`}{" "}
                {plano.plano_b.apoio}
              </p>
              <a href="https://www.metro.sp.gov.br/pt_BR/sua-viagem/declaracao-ocorrencias/" target="_blank" rel="noreferrer"
                className="inline-flex items-center gap-2 text-[14px] font-semibold text-marca-forte underline">
                <FileText className="size-4" aria-hidden />Vai chegar atrasado? Peça a declaração de ocorrência no mesmo dia
              </a>
            </section>
          )}

          <section className="space-y-3 rounded-xl border border-linha bg-superficie p-4">
            <p className="flex items-center gap-2 text-[15px] font-semibold"><MapPin className="size-4" aria-hidden />Seu caminho normal · {plano.rota.minutos} min · {plano.rota.km.toLocaleString("pt-BR")} km</p>
            <Etapas rota={plano.rota} linhas={linhasInfo} />
            <div className="flex flex-wrap gap-2 border-t border-linha pt-3">
              {plano.linhas.map((l) => (
                <span key={l.numero} className="inline-flex items-center gap-2 text-[14px]">
                  <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" /> <SituacaoLinha nivel={l.nivel} />
                </span>
              ))}
            </div>
          </section>

          <section className="grid gap-3 sm:grid-cols-2">
            <CartaoSeguranca titulo="Na saída" nome={plano.origem} s={plano.seguranca.origem} />
            <CartaoSeguranca titulo="Na chegada" nome={plano.destino} s={plano.seguranca.destino} />
          </section>

          {plano.energia && (
            <section className="space-y-2 rounded-xl border border-linha bg-superficie p-4">
              <p className="flex items-center gap-2 text-[15px] font-semibold"><Leaf className="size-4" aria-hidden />A mesma viagem, de {plano.energia.km.toLocaleString("pt-BR")} km, por pessoa</p>
              <ul className="grid gap-2 sm:grid-cols-3">
                {plano.energia.modos.map((m) => (
                  <li key={m.modo} className={`rounded-lg p-3 text-[14px] ${m.renovavel ? "bg-ok-suave" : "bg-fundo"}`}>
                    <span className="block font-semibold">{m.modo}{m.renovavel && <span className="ml-1.5 text-[12px] font-semibold text-ok">elétrico</span>}</span>
                    {m.co2_kg !== null && (
                      <span className="block">
                        {kg(m.co2_kg)}{m.co2_kg_max ? ` a ${kg(m.co2_kg_max)}` : ""} de CO₂
                      </span>
                    )}
                    {m.energia_kwh !== null && <span className="block text-apagado">{m.energia_kwh.toLocaleString("pt-BR")} kWh de energia</span>}
                    {m.custo_rs !== null && (
                      <span className="block text-apagado">R$ {m.custo_rs.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {m.custo_tipo === "tarifa" ? "de tarifa" : "de combustível"}</span>
                    )}
                    {m.nota && <span className="mt-1 block text-[12px] text-apagado">{m.nota}</span>}
                  </li>
                ))}
              </ul>
              {plano.energia.trilho_vs_carro !== null && (
                <p className="text-[14px]">De trem ou metrô, a viagem emite cerca de {plano.energia.trilho_vs_carro.toLocaleString("pt-BR")}% do CO₂ do carro.</p>
              )}
              <p className="text-[12px] text-apagado">{plano.energia.rotulo} Premissas: {plano.energia.premissas.join("; ")}.</p>
            </section>
          )}

          <p className="text-[12px] text-apagado">
            Situação das linhas lida às {hora(plano.fontes.linhas.lido_em)} ({plano.fontes.linhas.nome}). {plano.fontes.linhas.aviso}
            {" "}Avisos de tempo do INMET lidos às {hora(plano.fontes.tempo.lido_em)}. Rede: {plano.fontes.rede}. Confirme nos canais oficiais das operadoras.
          </p>
        </>
      )}
    </div>
  );
}
