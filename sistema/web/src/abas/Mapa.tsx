import { Check, ChevronUp } from "lucide-react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { SeloLinha, SituacaoLinha, hora } from "../componentes/Linha";
import { corDoTexto, type Nivel } from "../lib/api";

/*
 * Aba Mapa: linhas de trem e metrô com a situação de agora, mais camadas opcionais
 * (alagamentos do GeoSampa, ocorrências da SSP-SP por estação, relatos de passageiros).
 * Só usa circleMarker e polyline: o marcador padrão do Leaflet quebra no bundler.
 * Nada é guardado no aparelho.
 */

type LinhaMapa = { numero: string; nome: string; cor: string; nivel: Nivel; status: string; simulado: boolean; trechos: [number, number][][] };
type EstacaoMapa = { id: string; nome: string; lat: number; lon: number; linhas: string[] };
type PontoSeguranca = { estacao: string; lat: number; lon: number; total: number; faixa: string | null };
type PontoCge = { bairro: string; via: string; transitavel: boolean };
type Camadas = {
  lido_em: string;
  linhas: LinhaMapa[];
  estacoes: EstacaoMapa[];
  alagamentos: [number, number][];
  seguranca: PontoSeguranca[];
  cge: { ok: boolean; estado: { titulo: string; quando: string } | null; ativos: number | null; pontos: PontoCge[] };
};
type Relato = { id: number | string; linha: string | null; estacao_id: string | null; tipo: string; tipo_rotulo?: string; criado_em: string };
type Chave = "linhas" | "alagamentos" | "seguranca" | "relatos";

const CENTRO: [number, number] = [-23.55, -46.63];
const ZOOM_INICIAL = 11;
const ZOOM_ESTACOES = 12;
const ATUALIZA_CAMADAS_MS = 120_000;
const ATUALIZA_RELATOS_MS = 15_000;

const CHIPS: { chave: Chave; rotulo: string }[] = [
  { chave: "linhas", rotulo: "Linhas" },
  { chave: "alagamentos", rotulo: "Onde já alagou" },
  { chave: "seguranca", rotulo: "Segurança" },
  { chave: "relatos", rotulo: "Relatos" },
];

const ROTULO_NIVEL: Record<Nivel, string> = { normal: "Normal", atencao: "Atenção", parada: "Parada", encerrada: "Encerrada", sem_dado: "Sem informação" };
const ROTULO_FAIXA: Record<string, string> = { madrugada: "madrugada", manha: "manhã", tarde: "tarde", noite: "noite" };

const AVISO_SEGURANCA = "contagem de registros da SSP-SP, não é taxa de risco";
const ROTULO_RELATOS = "relatos de passageiros (estimativa, não dado oficial)";
const AZUL_ALAGAMENTO = "#5db4f0";

/** Lê um token de cor do CSS, para o mapa não ter cor de marca escrita no código. */
function cor(token: string, padrao: string): string {
  try {
    return getComputedStyle(document.documentElement).getPropertyValue(token).trim() || padrao;
  } catch {
    return padrao;
  }
}

async function lerJson<T>(url: string, sinal?: AbortSignal): Promise<T> {
  const r = await fetch(url, { signal: sinal });
  if (!r.ok) throw new Error(`Erro ${r.status}`);
  return (await r.json()) as T;
}

/* ---------------------------------------------------------------- popups em DOM (texto puro, sem HTML) */
function el<K extends keyof HTMLElementTagNameMap>(tag: K, classe = "", texto = ""): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (texto) e.textContent = texto;
  return e;
}

function seloDom(numero: string, corLinha: string): HTMLElement {
  const s = el("span", "inline-flex size-6 items-center justify-center rounded-md text-[11px] font-bold", numero);
  s.style.background = corLinha;
  s.style.color = corDoTexto(corLinha);
  return s;
}

function popupEstacao(e: EstacaoMapa, cores: Record<string, string>): HTMLElement {
  const raiz = el("div", "text-[14px] text-tinta");
  raiz.appendChild(el("p", "mb-1 font-semibold", e.nome));
  const selos = el("div", "flex flex-wrap gap-1");
  for (const n of e.linhas) selos.appendChild(seloDom(n, cores[n] ?? "#888888"));
  raiz.appendChild(selos);
  return raiz;
}

function textoDom(...linhas: string[]): HTMLElement {
  const raiz = el("div", "text-[13px] text-tinta");
  linhas.forEach((t, i) => raiz.appendChild(el("p", i === 0 ? "font-semibold" : "text-apagado", t)));
  return raiz;
}

function estiloLinha(l: LinhaMapa): L.PolylineOptions {
  const base: L.PolylineOptions = { color: l.cor, pane: "linhas", lineCap: "round", lineJoin: "round", weight: 5, opacity: 1 };
  if (l.nivel === "parada") return { ...base, weight: 7, dashArray: "12 8", lineCap: "butt" };      // tracejada e mais grossa
  if (l.nivel === "atencao") return { ...base, dashArray: "1 8" };                                  // pontilhada
  if (l.nivel === "encerrada" || l.nivel === "sem_dado") return { ...base, weight: 3, opacity: 0.45 };
  return base;
}

function resumoRelatos(lista: Relato[]): string[] {
  const por: Record<string, number> = {};
  for (const r of lista) {
    // o rótulo vem pronto da API ("Lotado", "Trem parado"); o código interno só como último recurso
    const tipo = r.tipo_rotulo || r.tipo || "relato";
    por[tipo] = (por[tipo] ?? 0) + 1;
  }
  return Object.entries(por).map(([tipo, n]) => `${tipo}: ${n}`);
}

/* ---------------------------------------------------------------- componente */
export default function Mapa() {
  const recipiente = useRef<HTMLDivElement>(null);
  const mapaRef = useRef<L.Map | null>(null);
  const grupos = useRef<Record<Chave | "estacoes", L.LayerGroup> | null>(null);
  const ajustou = useRef(false);

  const [pronto, setPronto] = useState(false);
  const [dados, setDados] = useState<Camadas | null>(null);
  const [erro, setErro] = useState("");
  const [ligadas, setLigadas] = useState<Record<Chave, boolean>>({ linhas: true, alagamentos: false, seguranca: false, relatos: false });
  const [relatos, setRelatos] = useState<Relato[]>([]);
  const [resumoAberto, setResumoAberto] = useState(false);

  const corPorLinha = useMemo(() => Object.fromEntries((dados?.linhas ?? []).map((l) => [l.numero, l.cor])), [dados]);
  const estacaoPorId = useMemo(() => new Map((dados?.estacoes ?? []).map((e) => [e.id, e])), [dados]);

  /* cria o mapa uma vez */
  useEffect(() => {
    const alvo = recipiente.current;
    if (!alvo) return;
    const mapa = L.map(alvo, { center: CENTRO, zoom: ZOOM_INICIAL, zoomControl: false, attributionControl: true });
    mapa.attributionControl.setPrefix(false);
    L.control.zoom({ position: "topright" }).addTo(mapa);
    // fundo em cinza (filtro só nos ladrilhos, classe mapa-cinza no CSS): as linhas coloridas aparecem mais
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap", className: "mapa-cinza" }).addTo(mapa);
    const camadasZ: [string, number][] = [["alagamentos", 410], ["linhas", 420], ["seguranca", 430], ["estacoes", 440], ["relatos", 450]];
    for (const [nome, z] of camadasZ) mapa.createPane(nome).style.zIndex = String(z);
    const g = {
      linhas: L.layerGroup(), alagamentos: L.layerGroup(), seguranca: L.layerGroup(), relatos: L.layerGroup(), estacoes: L.layerGroup(),
    };
    grupos.current = g;
    mapaRef.current = mapa;
    const estacoesPorZoom = () => {
      if (mapa.getZoom() >= ZOOM_ESTACOES) g.estacoes.addTo(mapa);
      else g.estacoes.removeFrom(mapa);
    };
    mapa.on("zoomend", estacoesPorZoom);
    estacoesPorZoom();
    const observador = new ResizeObserver(() => mapa.invalidateSize());
    observador.observe(alvo);
    setPronto(true);
    return () => {
      observador.disconnect();
      mapa.remove();
      mapaRef.current = null;
      grupos.current = null;
      ajustou.current = false;
      setPronto(false);
    };
  }, []);

  /* camadas: leitura inicial e a cada 120 s */
  useEffect(() => {
    const controle = new AbortController();
    const carregar = () => {
      lerJson<Camadas>("/api/mapa/camadas", controle.signal)
        .then((d) => {
          setDados(d);
          setErro("");
        })
        .catch((e: unknown) => {
          if (e instanceof DOMException && e.name === "AbortError") return;
          setErro("Não consegui atualizar o mapa agora.");
        });
    };
    carregar();
    const t = window.setInterval(carregar, ATUALIZA_CAMADAS_MS);
    return () => {
      controle.abort();
      window.clearInterval(t);
    };
  }, []);

  /* relatos: só busca enquanto a camada estiver ligada, a cada 15 s */
  useEffect(() => {
    if (!ligadas.relatos) return;
    const controle = new AbortController();
    const buscar = () => {
      lerJson<unknown>("/api/relatos", controle.signal)
        .then((d) => {
          // a rota devolve { relatos: [...] }; aceita também uma lista solta
          const lista = Array.isArray(d) ? d : (d as { relatos?: unknown } | null)?.relatos;
          setRelatos(Array.isArray(lista) ? (lista as Relato[]) : []);
        })
        .catch((e: unknown) => {
          if (e instanceof DOMException && e.name === "AbortError") return;
          setRelatos([]);
        });
    };
    buscar();
    const t = window.setInterval(buscar, ATUALIZA_RELATOS_MS);
    return () => {
      controle.abort();
      window.clearInterval(t);
    };
  }, [ligadas.relatos]);

  /* enquadra a rede inteira na primeira leitura (depois não mexe, para não tirar o mapa de onde a pessoa deixou) */
  const ajustar = useCallback(() => {
    const mapa = mapaRef.current;
    if (!mapa || !dados || ajustou.current || !dados.estacoes.length || !recipiente.current?.clientWidth) return;
    mapa.invalidateSize();
    // enquadra a capital (estações com dado de segurança da SSP-SP); sem isso, a rede inteira, que vai de Jundiaí a Rio Grande da Serra
    const base = dados.seguranca.length ? dados.seguranca : dados.estacoes;
    mapa.fitBounds(L.latLngBounds(base.map((e) => [e.lat, e.lon] as [number, number])), { padding: [12, 12], maxZoom: 12 });
    ajustou.current = true;
  }, [dados]);

  useEffect(() => {
    if (!pronto) return;
    ajustar();
    const alvo = recipiente.current;
    if (!alvo) return;
    const o = new ResizeObserver(ajustar);     // se o mapa estava escondido (tamanho 0), enquadra quando aparecer
    o.observe(alvo);
    return () => o.disconnect();
  }, [pronto, ajustar]);

  /* linhas */
  useEffect(() => {
    const g = grupos.current;
    const mapa = mapaRef.current;
    if (!g || !mapa || !pronto) return;
    g.linhas.clearLayers();
    if (!dados || !ligadas.linhas) {
      g.linhas.removeFrom(mapa);
      return;
    }
    for (const l of dados.linhas) {
      if (!l.trechos.length) continue;
      const p = L.polyline(l.trechos, estiloLinha(l));
      const titulo = `Linha ${l.numero} ${l.nome}: ${ROTULO_NIVEL[l.nivel] ?? l.status}`;
      p.bindTooltip(titulo, { sticky: true });
      p.bindPopup(textoDom(titulo, l.status));
      g.linhas.addLayer(p);
    }
    g.linhas.addTo(mapa);
  }, [dados, ligadas.linhas, pronto]);

  /* estações (aparecem a partir do zoom 12) */
  useEffect(() => {
    const g = grupos.current;
    if (!g || !pronto) return;
    g.estacoes.clearLayers();
    if (!dados) return;
    const tinta = cor("--color-tinta", "#222222");
    const fundo = cor("--color-superficie", "#ffffff");
    for (const e of dados.estacoes) {
      const p = L.circleMarker([e.lat, e.lon], { pane: "estacoes", radius: 5, color: tinta, weight: 1.5, fillColor: fundo, fillOpacity: 1 });
      p.bindPopup(popupEstacao(e, corPorLinha));
      g.estacoes.addLayer(p);
    }
  }, [dados, corPorLinha, pronto]);

  /* alagamentos */
  useEffect(() => {
    const g = grupos.current;
    const mapa = mapaRef.current;
    if (!g || !mapa || !pronto) return;
    g.alagamentos.clearLayers();
    if (!dados || !ligadas.alagamentos) {
      g.alagamentos.removeFrom(mapa);
      return;
    }
    for (const [lat, lon] of dados.alagamentos) {
      g.alagamentos.addLayer(L.circleMarker([lat, lon], { pane: "alagamentos", radius: 4, color: AZUL_ALAGAMENTO, weight: 1, fillColor: AZUL_ALAGAMENTO, fillOpacity: 0.45, interactive: false }));
    }
    g.alagamentos.addTo(mapa);
  }, [dados, ligadas.alagamentos, pronto]);

  /* segurança: círculo proporcional ao total de registros */
  useEffect(() => {
    const g = grupos.current;
    const mapa = mapaRef.current;
    if (!g || !mapa || !pronto) return;
    g.seguranca.clearLayers();
    if (!dados || !ligadas.seguranca) {
      g.seguranca.removeFrom(mapa);
      return;
    }
    const neutro = cor("--color-apagado", "#666666");
    const maior = Math.max(1, ...dados.seguranca.map((s) => s.total));
    for (const s of dados.seguranca) {
      const faixa = s.faixa ? `faixa mais comum: ${ROTULO_FAIXA[s.faixa] ?? s.faixa}` : "faixa de horário não informada";
      const linhas = [s.estacao, `${s.total} registros, ${faixa}`, `Atenção: ${AVISO_SEGURANCA}.`];
      const p = L.circleMarker([s.lat, s.lon], {
        pane: "seguranca", radius: 3 + 9 * Math.sqrt(s.total / maior), color: neutro, weight: 1.5, fillColor: neutro, fillOpacity: 0.22,
      });
      p.bindTooltip(textoDom(...linhas), { direction: "top" });
      p.bindPopup(textoDom(...linhas));
      g.seguranca.addLayer(p);
    }
    g.seguranca.addTo(mapa);
  }, [dados, ligadas.seguranca, pronto]);

  /* relatos: um círculo por estação com relato */
  useEffect(() => {
    const g = grupos.current;
    const mapa = mapaRef.current;
    if (!g || !mapa || !pronto) return;
    g.relatos.clearLayers();
    if (!ligadas.relatos) {
      g.relatos.removeFrom(mapa);
      return;
    }
    const porEstacao = new Map<string, Relato[]>();
    for (const r of relatos) {
      if (r && r.estacao_id) porEstacao.set(r.estacao_id, [...(porEstacao.get(r.estacao_id) ?? []), r]);
    }
    const destaque = cor("--color-alerta", "#9a4f06");
    for (const [id, lista] of porEstacao) {
      const e = estacaoPorId.get(id);
      if (!e) continue;
      const p = L.circleMarker([e.lat, e.lon], {
        pane: "relatos", radius: 8 + Math.min(lista.length, 6) * 2, color: destaque, weight: 2.5, dashArray: "3 3", fillColor: destaque, fillOpacity: 0.25,
      });
      const texto = [e.nome, `${lista.length} ${lista.length === 1 ? "relato" : "relatos"}: ${resumoRelatos(lista).join(", ")}`, ROTULO_RELATOS];
      p.bindTooltip(textoDom(...texto), { direction: "top" });
      p.bindPopup(textoDom(...texto));
      g.relatos.addLayer(p);
    }
    g.relatos.addTo(mapa);
  }, [relatos, ligadas.relatos, estacaoPorId, pronto]);

  const alternar = (c: Chave) => setLigadas((v) => ({ ...v, [c]: !v[c] }));

  /* resumo em texto */
  const comProblema = (dados?.linhas ?? []).filter((l) => l.nivel === "parada" || l.nivel === "atencao");
  const simuladas = (dados?.linhas ?? []).filter((l) => l.simulado);
  const cge = dados?.cge;
  const pontosCge = cge?.pontos ?? [];
  const relatosNoMapa = relatos.filter((r) => r && r.estacao_id && estacaoPorId.has(r.estacao_id)).length;

  const notas: string[] = [];
  if (ligadas.alagamentos) notas.push("Alagamentos: pontos registrados no GeoSampa (Prefeitura)");
  if (ligadas.seguranca) notas.push(`Segurança: ${AVISO_SEGURANCA}`);
  if (ligadas.relatos) notas.push(`Relatos: ${ROTULO_RELATOS}${relatosNoMapa ? `, ${relatosNoMapa} no mapa` : ", nenhum no mapa agora"}`);

  const textoCge = !cge || !cge.ok
    ? "sem leitura agora."
    : [
        cge.estado ? `${cge.estado.titulo}${cge.estado.quando ? ` (${cge.estado.quando})` : ""}` : "sem estado de atenção ou alerta",
        cge.ativos != null ? `${cge.ativos} ${cge.ativos === 1 ? "ponto de alagamento ativo" : "pontos de alagamento ativos"}` : null,
      ].filter(Boolean).join(", ") + ".";

  const titulo = !dados
    ? erro || "Carregando o mapa..."
    : comProblema.length === 0 ? "Todas as linhas normais" : `${comProblema.length} ${comProblema.length === 1 ? "linha com problema" : "linhas com problema"}`;

  return (
    <div className="relative isolate flex h-full min-h-0 w-full flex-col bg-fundo">
      <div className="relative min-h-[180px] flex-1">
        <div
          ref={recipiente}
          role="region"
          aria-label="Mapa de trens e metrô de São Paulo, com as linhas e as camadas escolhidas. O resumo em texto abaixo traz as mesmas informações."
          className="absolute inset-0"
        />
        <div role="group" aria-label="Camadas do mapa" className="sem-barra pointer-events-none absolute inset-x-0 top-0 z-[500] flex gap-2 overflow-x-auto py-3 pr-16 pl-3">
          {CHIPS.map(({ chave, rotulo }) => {
            const on = ligadas[chave];
            return (
              <button
                key={chave}
                type="button"
                aria-pressed={on}
                onClick={() => alternar(chave)}
                className={`pointer-events-auto inline-flex h-10 shrink-0 items-center gap-1.5 rounded-full px-4 text-[14px] font-bold shadow-flutua ${
                  on ? "bg-tinta text-superficie" : "bg-superficie text-tinta hover:bg-cinza"
                }`}
              >
                {on && <Check className="size-4" strokeWidth={3} aria-hidden />}
                {rotulo}
              </button>
            );
          })}
        </div>
      </div>

      <div role="region" aria-label="Resumo do mapa em texto"
        className={`relative z-[600] -mt-6 shrink-0 overflow-y-auto rounded-t-[28px] bg-superficie px-5 pb-4 shadow-folha ${resumoAberto ? "max-h-[70%]" : "max-h-[34%]"}`}>
        <button type="button" onClick={() => setResumoAberto((v) => !v)} aria-expanded={resumoAberto}
          className="sticky top-0 -mx-5 flex w-[calc(100%+2.5rem)] flex-col bg-superficie px-5 pb-2 text-left">
          <span className="alca" aria-hidden />
          <span className="mt-3 flex items-center gap-3">
            <span className={`size-3 shrink-0 rounded-full ${!dados ? "bg-cinza-forte" : comProblema.some((l) => l.nivel === "parada") ? "bg-erro" : comProblema.length ? "bg-alerta" : "bg-ok"}`} aria-hidden />
            <span className="min-w-0 flex-1 text-[20px] leading-tight font-bold tracking-tight">{titulo}</span>
            <ChevronUp className={`size-5 shrink-0 text-apagado transition-transform ${resumoAberto ? "rotate-180" : ""}`} aria-hidden />
          </span>
          {dados && <span className="mt-1 text-[13px] text-apagado">Leitura das {hora(dados.lido_em)}, atualiza a cada 2 minutos{erro ? `. ${erro}` : ""}</span>}
        </button>
        {dados && (
          <div className="space-y-3 pt-1 text-[14px]">
            {comProblema.length > 0 && (
              <ul className="space-y-2">
                {comProblema.map((l) => (
                  <li key={l.numero} className="flex items-center gap-3 rounded-2xl bg-cinza p-2.5">
                    <SeloLinha numero={l.numero} cor={l.cor} />
                    <span className="min-w-0 flex-1 truncate font-bold">{l.nome}</span>
                    <SituacaoLinha nivel={l.nivel} />
                  </li>
                ))}
              </ul>
            )}
            {simuladas.length > 0 && (
              <p className="rounded-2xl bg-erro-suave px-3 py-2 font-semibold text-erro">Simulação de falha na linha {simuladas.map((l) => `${l.numero} ${l.nome}`).join(", ")}.</p>
            )}
            <p>
              <span className="font-bold">Alagamentos (CGE): </span>
              <span className="text-apagado">{textoCge}</span>
            </p>
            {pontosCge.length > 0 && (
              <ul className="ml-4 list-disc text-[13px] text-apagado">
                {pontosCge.slice(0, 3).map((p, i) => (
                  <li key={i}>{[p.bairro, p.via].filter(Boolean).join(", ")}{p.transitavel ? " (transitável)" : " (intransitável)"}</li>
                ))}
                {pontosCge.length > 3 && <li>e mais {pontosCge.length - 3}</li>}
              </ul>
            )}
            {notas.length > 0 && (
              <ul className="space-y-0.5 text-[12px] text-apagado">
                {notas.map((n) => <li key={n}>{n}</li>)}
              </ul>
            )}
            <details>
              <summary className="cursor-pointer py-1 text-[14px] font-bold underline underline-offset-4">Todas as linhas e legenda</summary>
              <p className="mt-1 text-[12px] text-apagado">
                No mapa: traço contínuo é normal, pontilhado é atenção, tracejado grosso é parada, traço claro é encerrada ou sem informação.
              </p>
              <ul className="mt-1.5 grid gap-1.5">
                {dados.linhas.map((l) => (
                  <li key={l.numero} className="flex items-center gap-2">
                    <SeloLinha numero={l.numero} cor={l.cor} tamanho="sm" />
                    <span className="min-w-0 flex-1 truncate text-[13px]">{l.nome}</span>
                    <SituacaoLinha nivel={l.nivel} />
                  </li>
                ))}
              </ul>
            </details>
          </div>
        )}
      </div>
    </div>
  );
}
