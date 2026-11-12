import { ArrowRight, RotateCcw, ShieldAlert } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { api, mobilidade, type EstadoDSA, type TesteCS, type TesteMLAM, type TestePCP, type TesteSERS } from "../lib/api";

const CAMPO = "w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px] focus:border-marca focus:outline-none";
const BOTAO = "rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-50";
const BOTAO_2 = "rounded-full px-4 py-2 text-[14px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave disabled:opacity-50";

/* ---------------------------------------------------------------- PCP */

const CONFIANCA: Record<string, string> = { ALTA: "bg-ok-suave text-ok", "MÉDIA": "bg-alerta-suave text-alerta", NENHUMA: "bg-fundo text-apagado ring-1 ring-linha ring-inset" };

export function TestePcp() {
  const [pergunta, setPergunta] = useState("a linha 9 parou, e agora?");
  const [r, setR] = useState<TestePCP | null>(null);
  const [erro, setErro] = useState("");

  const buscar = async (evento?: FormEvent) => {
    evento?.preventDefault();
    setErro("");
    try {
      setR(await api.testePCP(pergunta));
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não consegui buscar.");
    }
  };
  useEffect(() => void buscar(), []);

  const melhor = r?.resultados[0];
  const maximo = Math.max(1, ...(r?.resultados.map((x) => x.pontos) ?? [1]));

  return (
    <div className="space-y-5">
      <form onSubmit={buscar} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="pergunta-pcp" className="sr-only">Pergunta</label>
        <input id="pergunta-pcp" value={pergunta} onChange={(e) => setPergunta(e.target.value)} className={CAMPO} placeholder="Escreva uma pergunta" />
        <button type="submit" className={BOTAO}>Buscar</button>
      </form>
      <div className="flex flex-wrap gap-2 text-[13px]">
        <span className="text-apagado">Experimente:</span>
        {["roubaram meu celular no trem", "como pego a declaração de atraso", "quero um unicórnio", "meu telefone é 11 91234-5678"].map((ex) => (
          <button key={ex} type="button" onClick={() => setPergunta(ex)} className="rounded-full bg-superficie px-2.5 py-0.5 text-marca-forte ring-1 ring-linha ring-inset hover:bg-marca-suave">
            {ex}
          </button>
        ))}
      </div>
      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}

      {r?.bloqueada && (
        <p className="flex items-start gap-2 rounded-xl bg-alerta-suave px-4 py-3 text-alerta">
          <ShieldAlert className="mt-0.5 size-5 shrink-0" aria-hidden />
          A pergunta tem 8 dígitos ou mais, ou um @. O assistente recusa e não registra nada, como manda o enunciado.
        </p>
      )}

      {r && !r.bloqueada && (
        <div className="space-y-3">
          <p className="text-[15px]">
            {melhor && melhor.pontos >= 3 ? (
              <>
                Resposta escolhida: <span className="font-semibold">{melhor.titulo}</span>, com {melhor.pontos} pontos{" "}
                <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${CONFIANCA[melhor.confianca]}`}>confiança {melhor.confianca}</span>
              </>
            ) : (
              <>Nenhuma orientação chegou a 3 pontos: o assistente diz que não encontrou e sugere as categorias.</>
            )}
          </p>
          <p className="text-[13px] text-apagado">A lista de tuplas que buscar() devolve, da maior para a menor pontuação:</p>
          {r.resultados.length === 0 && <p className="text-[14px] text-apagado">Nenhuma orientação recebeu ponto.</p>}
          <ol className="space-y-2">
            {r.resultados.map((x) => (
              <li key={x.id} className="rounded-xl border border-linha bg-superficie px-4 py-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="w-10 shrink-0 text-lg font-bold tabular-nums">{x.pontos}</span>
                  <span className="min-w-0 flex-1 font-semibold">{x.titulo}</span>
                  <span className={`rounded-full px-2 py-0.5 text-[12px] font-semibold ${CONFIANCA[x.confianca]}`}>{x.confianca === "NENHUMA" ? "abaixo de 3" : x.confianca}</span>
                </div>
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-fundo" aria-hidden>
                  <div className="h-full rounded-full bg-[#2563EB]" style={{ width: `${(100 * x.pontos) / maximo}%` }} />
                </div>
                <p className="mt-2 text-[13px] text-apagado">
                  {x.palavras_chave.map((k) => `+3 “${k}”`).concat(x.palavras_titulo.map((t) => `+1 “${t}” no título`)).join(" · ")}
                </p>
              </li>
            ))}
          </ol>
        </div>
      )}

      {r && (
        <details className="rounded-xl border border-linha bg-superficie px-4 py-3 text-[14px]">
          <summary className="cursor-pointer font-semibold">A base inteira ({r.base.length} orientações)</summary>
          <ul className="mt-3 space-y-2">
            {r.base.map((o) => (
              <li key={o.id}>
                <span className="font-semibold">{o.id}. {o.titulo}</span> <span className="text-apagado">[{o.categoria}]</span>
                {o.em_conferencia && <span className="ml-1 rounded-full bg-alerta-suave px-2 py-0.5 text-[11px] font-semibold text-alerta">em conferência</span>}
                <br />
                <span className="text-[13px] text-apagado">palavras-chave: {o.palavras_chave.join(", ")}</span>
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- DSA */

const VAZIO = { id: "", titulo: "", categoria: "", descricao: "", publico_alvo: "", canal: "", prazo: "" };
const ROTULOS: Record<keyof typeof VAZIO, string> = {
  id: "Identificador", titulo: "Título", categoria: "Categoria", descricao: "Descrição", publico_alvo: "Público-alvo", canal: "Canal de atendimento", prazo: "Prazo (AAAA-MM-DD, opcional)",
};

export function TesteDsa() {
  const [estado, setEstado] = useState<EstadoDSA | null>(null);
  const [trecho, setTrecho] = useState("ouvidoria");
  const [campo, setCampo] = useState("titulo");
  const [novo, setNovo] = useState(VAZIO);
  const [ocupado, setOcupado] = useState(false);

  useEffect(() => {
    api.estadoDSA().then(setEstado).catch(() => setEstado(null));
  }, []);

  const operar = async (operacao: string, dados: Record<string, string> = {}) => {
    setOcupado(true);
    try {
      const r = await api.operarDSA(operacao, dados);
      setEstado(r);
      if (operacao === "cadastrar" && r.ok) setNovo(VAZIO);
    } finally {
      setOcupado(false);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[14px] font-semibold">Ordenar por:</span>
        {[["titulo", "título"], ["id", "id"], ["prazo", "prazo"]].map(([c, r]) => (
          <button key={c} type="button" disabled={ocupado} onClick={() => operar("ordenar", { criterio: c })} className={BOTAO_2}>{r}</button>
        ))}
        <button type="button" disabled={ocupado} onClick={() => operar("reiniciar")} className="ml-auto inline-flex items-center gap-1.5 text-[13px] font-semibold text-apagado underline">
          <RotateCcw className="size-3.5" aria-hidden /> Recarregar do arquivo
        </button>
      </div>

      <form onSubmit={(e) => { e.preventDefault(); void operar("pesquisar", { campo, trecho }); }} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="campo-dsa" className="sr-only">Pesquisar em</label>
        <select id="campo-dsa" value={campo} onChange={(e) => setCampo(e.target.value)} className={`${CAMPO} sm:w-44`}>
          <option value="titulo">no título</option>
          <option value="categoria">na categoria</option>
        </select>
        <label htmlFor="trecho-dsa" className="sr-only">Trecho</label>
        <input id="trecho-dsa" value={trecho} onChange={(e) => setTrecho(e.target.value)} className={CAMPO} placeholder="Trecho para pesquisar" />
        <button type="submit" disabled={ocupado} className={BOTAO}>Pesquisar</button>
      </form>

      {estado && (
        <>
          <p role="status" className={`rounded-xl px-4 py-2.5 text-[14px] ${estado.ok ? "bg-marca-suave text-marca-forte" : "bg-erro-suave text-erro"}`}>
            {estado.mensagem || `${estado.tamanho} serviços na lista.`}
          </p>
          <div>
            <p className="mb-2 text-[13px] text-apagado">
              A lista, do primeiro nó (cabeça: {estado.cabeca ?? "vazia"}) ao último (cauda: {estado.cauda ?? "vazia"}). Cada nó aponta para o próximo.
            </p>
            <ol className="flex flex-wrap items-center gap-y-2">
              {estado.nos.map((no, i) => {
                const achado = estado.achados.includes(no.id);
                return (
                  <li key={no.id} className="flex items-center">
                    <span className={`rounded-lg border px-2.5 py-1.5 text-[13px] ${achado ? "border-[#C2410C] bg-[#C2410C]/10 font-semibold" : "border-linha bg-superficie"}`} title={no.titulo}>
                      <span className="font-mono text-[11px] text-apagado">{no.id}</span>
                      <span className="block max-w-[11rem] truncate">{no.titulo}</span>
                      {no.prazo && <span className="block text-[11px] text-alerta">prazo {no.prazo}</span>}
                    </span>
                    {i < estado.nos.length - 1 ? <ArrowRight className="mx-1 size-4 shrink-0 text-apagado" aria-hidden /> : <span className="ml-1.5 text-[12px] text-apagado">→ None</span>}
                  </li>
                );
              })}
            </ol>
          </div>

          <details className="rounded-xl border border-linha bg-superficie px-4 py-3">
            <summary className="cursor-pointer text-[15px] font-semibold">Cadastrar ou excluir um serviço</summary>
            <form onSubmit={(e) => { e.preventDefault(); void operar("cadastrar", novo); }} className="mt-3 grid gap-3 sm:grid-cols-2">
              {(Object.keys(VAZIO) as (keyof typeof VAZIO)[]).map((k) => (
                <div key={k} className={k === "descricao" ? "sm:col-span-2" : ""}>
                  <label htmlFor={`novo-${k}`} className="block text-[13px] font-semibold">{ROTULOS[k]}</label>
                  <input id={`novo-${k}`} value={novo[k]} onChange={(e) => setNovo({ ...novo, [k]: e.target.value })} className={CAMPO} />
                </div>
              ))}
              <div className="flex flex-wrap gap-2 sm:col-span-2">
                <button type="submit" disabled={ocupado} className={BOTAO}>Cadastrar no fim da lista</button>
              </div>
            </form>
            <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-linha pt-3">
              <span className="text-[14px] font-semibold">Excluir:</span>
              {estado.nos.slice(0, 20).map((no) => (
                <button key={no.id} type="button" disabled={ocupado} onClick={() => operar("excluir", { id: no.id })} className="rounded-full bg-fundo px-2.5 py-0.5 text-[12px] font-mono text-apagado ring-1 ring-linha ring-inset hover:bg-erro-suave hover:text-erro">
                  {no.id}
                </button>
              ))}
            </div>
            <p className="mt-3 text-[12px] text-apagado">Estas mudanças ficam só na memória do servidor, para teste. O arquivo da entrega não muda.</p>
          </details>
        </>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- SERS */

export function TesteSers() {
  const [km, setKm] = useState("15");
  const [r, setR] = useState<TesteSERS | null>(null);
  const [erro, setErro] = useState("");

  const calcular = async (evento?: FormEvent) => {
    evento?.preventDefault();
    setErro("");
    try {
      setR(await api.testeSERS(Number(km.replace(",", "."))));
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não consegui calcular.");
    }
  };
  useEffect(() => void calcular(), []);

  return (
    <div className="space-y-5">
      <form onSubmit={calcular} className="flex flex-col gap-2 sm:flex-row sm:items-end">
        <div className="flex-1">
          <label htmlFor="km-sers" className="block text-[14px] font-semibold">Distância da viagem (km)</label>
          <input id="km-sers" inputMode="decimal" value={km} onChange={(e) => setKm(e.target.value)} className={CAMPO} />
        </div>
        <button type="submit" className={BOTAO}>Comparar</button>
      </form>
      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}
      {r && (
        <>
          <ol className="list-decimal space-y-1.5 rounded-xl border border-linha bg-superficie py-4 pr-4 pl-9 text-[15px]">
            {r.passos.map((p) => <li key={p}>{p}</li>)}
          </ol>
          {r.trilho_vs_carro !== null && (
            <p className="text-[15px]">De trem ou metrô, a viagem emite cerca de {r.trilho_vs_carro.toLocaleString("pt-BR")}% do CO₂ do carro (parte fóssil).</p>
          )}
          <p className="text-[13px] text-apagado">
            {r.rotulo} Premissas: {r.premissas.join("; ")}. Números levantados em {r.consultado_em.split("-").reverse().join("/")}, ainda em conferência pela equipe.
          </p>
          <details className="rounded-xl border border-linha bg-superficie px-4 py-3 text-[13px]">
            <summary className="cursor-pointer font-semibold">Fontes ({r.fontes.length})</summary>
            <ul className="mt-2 space-y-1 break-all">
              {r.fontes.map((f) => <li key={f}><a href={f} target="_blank" rel="noreferrer" className="text-marca-forte underline">{f}</a></li>)}
            </ul>
          </details>
          <p className="rounded-xl bg-alerta-suave px-4 py-3 text-[14px] text-alerta"><span className="font-semibold">Falta para a entrega:</span> {r.falta}</p>
        </>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- CS */

const CONDICOES: { chave: keyof TesteCS["entradas"]; letra: string; rotulo: string }[] = [
  { chave: "falha", letra: "F", rotulo: "Falha numa linha do trajeto" },
  { chave: "chuva", letra: "C", rotulo: "Aviso de chuva do INMET" },
  { chave: "alagamento", letra: "A", rotulo: "Alagamento perto de uma estação" },
  { chave: "pico", letra: "P", rotulo: "Horário de pico" },
];
const COR_DECISAO: Record<string, string> = { pode_ir: "bg-ok-suave text-ok", mais_cedo: "bg-alerta-suave text-alerta", plano_b: "bg-erro-suave text-erro" };

export function TesteCs() {
  const [entradas, setEntradas] = useState<TesteCS["entradas"]>({ falha: false, chuva: true, alagamento: false, pico: true });
  const [r, setR] = useState<TesteCS | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    mobilidade.testeCS(entradas).then(setR).catch((e) => setErro(e instanceof Error ? e.message : "Não consegui decidir."));
  }, [entradas]);

  return (
    <div className="space-y-5">
      <div className="grid gap-2 sm:grid-cols-2">
        {CONDICOES.map((c) => (
          <label key={c.chave} className="flex cursor-pointer items-center gap-3 rounded-xl border border-linha bg-superficie px-4 py-3 text-[15px]">
            <input type="checkbox" checked={entradas[c.chave]} onChange={(e) => setEntradas({ ...entradas, [c.chave]: e.target.checked })} className="size-5 accent-[#4338CA]" />
            <span className="font-mono text-[13px] font-bold text-[#4338CA]">{c.letra} = {entradas[c.chave] ? 1 : 0}</span>
            <span>{c.rotulo}</span>
          </label>
        ))}
      </div>
      {erro && <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>}
      {r && (
        <div className="space-y-2">
          <p role="status" className={`rounded-xl px-4 py-3 text-xl font-bold ${COR_DECISAO[r.codigo] ?? ""}`}>{r.texto}</p>
          <p className="text-[13px] text-apagado">{r.aviso}</p>
        </div>
      )}
    </div>
  );
}

/* ---------------------------------------------------------------- MLAM */

const NOME_FAIXA: Record<string, string> = { madrugada: "Madrugada", manha: "Manhã", tarde: "Tarde", noite: "Noite" };

export function TesteMlam() {
  const [r, setR] = useState<TesteMLAM | null>(null);
  const [erro, setErro] = useState("");

  useEffect(() => {
    mobilidade.testeMLAM().then(setR).catch((e) => setErro(e instanceof Error ? e.message : "Não consegui ler a base."));
  }, []);

  if (erro) return <p className="rounded-xl bg-erro-suave px-4 py-3 text-erro">{erro}</p>;
  if (!r) return null;
  if (!r.ok) return <p className="rounded-xl bg-alerta-suave px-4 py-3 text-alerta">{r.mensagem}</p>;
  const maximo = Math.max(1, ...r.ranking.map((x) => x.total));
  const totalFaixas = Object.values(r.faixas).reduce((a, b) => a + b, 0) || 1;

  return (
    <div className="space-y-5">
      <p className="text-[15px]">
        {r.estacoes} estações da capital, ocorrências registradas a menos de {r.meta.raio_m} m, de {r.meta.periodo}.{" "}
        <a href={r.meta.fonte} target="_blank" rel="noreferrer" className="text-marca-forte underline">Planilha da SSP-SP</a>.
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl border border-linha bg-superficie p-4">
          <p className="mb-2 text-[14px] font-semibold">Por faixa de horário (soma das estações)</p>
          <ul className="space-y-1.5 text-[14px]">
            {Object.entries(r.faixas).map(([f, n]) => (
              <li key={f} className="flex items-center gap-2">
                <span className="w-20 shrink-0">{NOME_FAIXA[f] ?? f}</span>
                <span className="h-2 flex-1 overflow-hidden rounded-full bg-fundo" aria-hidden>
                  <span className="block h-full rounded-full bg-[#BE185D]" style={{ width: `${(100 * n) / totalFaixas}%` }} />
                </span>
                <span className="w-20 shrink-0 text-right tabular-nums">{n.toLocaleString("pt-BR")}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-linha bg-superficie p-4">
          <p className="mb-2 text-[14px] font-semibold">Por tipo (soma das estações)</p>
          <ul className="space-y-1 text-[14px]">
            {Object.entries(r.tipos).map(([t, n]) => (
              <li key={t} className="flex justify-between"><span className="capitalize">{t}</span><span className="tabular-nums">{n.toLocaleString("pt-BR")}</span></li>
            ))}
          </ul>
        </div>
      </div>
      <div>
        <p className="mb-2 text-[14px] font-semibold">Estações com mais registros</p>
        <ol className="space-y-1.5">
          {r.ranking.map((x, i) => (
            <li key={x.estacao} className="flex items-center gap-2 text-[14px]">
              <span className="w-6 shrink-0 text-right text-apagado tabular-nums">{i + 1}</span>
              <span className="w-36 shrink-0 truncate font-semibold sm:w-44">{x.estacao}</span>
              <span className="h-2 flex-1 overflow-hidden rounded-full bg-fundo" aria-hidden>
                <span className="block h-full rounded-full bg-[#BE185D]" style={{ width: `${(100 * x.total) / maximo}%` }} />
              </span>
              <span className="w-14 shrink-0 text-right tabular-nums">{x.total.toLocaleString("pt-BR")}</span>
            </li>
          ))}
        </ol>
      </div>
      <p className="text-[13px] text-apagado">{r.meta.observacao}</p>
      <p className="rounded-xl bg-alerta-suave px-4 py-3 text-[14px] text-alerta"><span className="font-semibold">Falta para a entrega:</span> {r.falta}</p>
    </div>
  );
}

/* ---------------------------------------------------------------- em construção */

export function TesteEmConstrucao({ cod }: { cod: string }) {
  const textos: Record<string, string> = {
    PAI: "O agente da entrega ainda não foi feito. Quando estiver pronto, o Pergunte com IA responde com a base de leis e regulamentos do passageiro e este teste mostra o placar do juiz antes e depois da melhoria. Hoje dá para ligar um modelo nas Configurações.",
    MMC: "O simulador dos ônibus de apoio entra se houver tempo: a frota de 72 ônibus por região e a redistribuição por transformação linear criada pelo grupo, que mantém o total e não gera número negativo.",
    COA: "Esta entrega fica fora do app, no Wokwi: um Raspberry Pi Pico com sensor de nível de água acende o alerta num ponto de alagamento. No app, os pontos de alagamento vêm do GeoSampa.",
  };
  return (
    <div className="space-y-3 rounded-xl border border-dashed border-linha bg-superficie p-5 text-[15px]">
      <p className="font-semibold">{cod === "COA" ? "Entregue à parte" : "Em construção"}</p>
      <p className="text-apagado">{textos[cod] ?? "Teste ainda não disponível."}</p>
      {cod === "PAI" && <Link to="/configuracoes" className={`${BOTAO_2} inline-flex`}>Abrir Configurações de IA</Link>}
    </div>
  );
}
