import { ArrowLeft, ArrowRight, Check, ExternalLink, Timer } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { idDoAparelho } from "../abas/Feed";
import { api, type Entendeu, type Perfil } from "../lib/api";

/*
 * Avaliar o Dá Tempo?: o teste guiado que uma pessoa faz pelo celular, em uns 10 minutos.
 * 3 tarefas cronometradas (PAI), 4 situações de energia (SERS), 5 perguntas de facilidade (1 a 5),
 * um comentário e uma sugestão. Ninguém se identifica; o resultado aparece em "Avaliação usuários".
 */

const TAREFAS = [
  {
    texto: "Descubra como pedir a declaração de atraso de uma viagem de metrô feita hoje.",
    opcoes: ["Só na bilheteria da estação, no mesmo dia", "No site do Metrô, em Declaração de Ocorrências, depois que a ocorrência termina", "Ligando para o 190"],
    certa: 1,
  },
  {
    texto: "Descubra se uma pessoa de 67 anos paga o metrô e o que ela precisa mostrar.",
    opcoes: ["Não paga: basta um documento que prove a idade", "Paga meia com o Bilhete Único Comum", "Não paga, mas precisa de cadastro prévio no Poupatempo"],
    certa: 0,
  },
  {
    texto: "Descubra onde procurar uma mochila esquecida no trem da CPTM.",
    opcoes: ["Na delegacia mais próxima", "No Achados e Perdidos do Metrô", "No Achados e Perdidos da CPTM, pelos canais oficiais dela"],
    certa: 2,
  },
];
const SITUACOES = [
  "Na Lia, peça uma viagem (por exemplo, \"vou do Capão Redondo para a Paulista\") e abra \"Segurança nas estações e energia\" no cartão. Você consegue dizer quanto CO₂ e quanto custa de trilho e de carro?",
  "Você consegue dizer qual modo emite menos nessa viagem?",
  "Ficou claro por que o trilho é a alternativa mais limpa (ele usa a rede elétrica, que é majoritariamente renovável)?",
  "Ficou claro que a conta é uma estimativa por média, não a medição da sua viagem?",
];
const PERGUNTAS = [
  "Foi fácil fazer a pergunta.",
  "A resposta foi clara.",
  "Eu confiaria na resposta para agir (sabendo que devo confirmar no canal oficial).",
  "Ficou claro de onde veio a informação.",
  "Eu usaria o Dá Tempo? de novo.",
];
const PERFIS: { valor: Perfil; rotulo: string }[] = [
  { valor: "familia", rotulo: "Família" }, { valor: "faculdade", rotulo: "Faculdade" }, { valor: "trabalho", rotulo: "Trabalho" },
  { valor: "conhecido", rotulo: "Conhecido" }, { valor: "outro", rotulo: "Outro" },
];
const MAXIMO_S = 300;

type Tarefa = { inicio: number | null; segundos: number | null; escolha: number | null; desistiu: boolean };
const tarefaVazia = (): Tarefa => ({ inicio: null, segundos: null, escolha: null, desistiu: false });

function Escala({ valor, mudar, nome }: { valor: number | null; mudar: (n: number) => void; nome: string }) {
  return (
    <div className="flex gap-2" role="radiogroup" aria-label={nome}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button key={n} type="button" role="radio" aria-checked={valor === n} onClick={() => mudar(n)}
          className={`size-11 rounded-xl text-[16px] font-bold ring-1 ring-inset ${valor === n ? "bg-marca text-white ring-marca" : "bg-superficie ring-linha hover:ring-marca/50"}`}>
          {n}
        </button>
      ))}
    </div>
  );
}

export default function Avaliar() {
  const [passo, setPasso] = useState(0);
  const [perfil, setPerfil] = useState<Perfil | null>(null);
  const [tarefas, setTarefas] = useState<Tarefa[]>([tarefaVazia(), tarefaVazia(), tarefaVazia()]);
  const [energia, setEnergia] = useState<(Entendeu | null)[]>([null, null, null, null]);
  const [notaEnergia, setNotaEnergia] = useState<number | null>(null);
  const [facilidade, setFacilidade] = useState<(number | null)[]>([null, null, null, null, null]);
  const [comentario, setComentario] = useState("");
  const [sugestao, setSugestao] = useState("");
  const [agora, setAgora] = useState(Date.now());
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  const indiceTarefa = passo >= 1 && passo <= 3 ? passo - 1 : -1;
  const atual = indiceTarefa >= 0 ? tarefas[indiceTarefa] : null;
  const contando = !!atual && atual.inicio !== null && atual.segundos === null && !atual.desistiu;

  useEffect(() => {
    if (!contando) return;
    const id = window.setInterval(() => setAgora(Date.now()), 250);
    return () => window.clearInterval(id);
  }, [contando]);

  const mudarTarefa = (i: number, m: Partial<Tarefa>) => setTarefas((ts) => ts.map((t, k) => (k === i ? { ...t, ...m } : t)));
  // o tempo sai sempre do relógio (Date.now), nunca do último quadro desenhado: no celular, com o formulário em
  // segundo plano enquanto a pessoa usa o app, o intervalo pausa e o "agora" da tela fica parado
  const segundosAte = (inicio: number, fim: number) => Math.min(MAXIMO_S, Math.round((fim - inicio) / 1000));
  const decorrido = atual?.inicio ? segundosAte(atual.inicio, agora) : 0;
  useEffect(() => {
    if (contando && atual?.inicio && segundosAte(atual.inicio, Date.now()) >= MAXIMO_S) mudarTarefa(indiceTarefa, { desistiu: true });
  }, [contando, decorrido, indiceTarefa, atual?.inicio]);
  useEffect(() => {
    // ao voltar para esta aba, atualiza na hora (e marca "não encontrou" se já passou de 5 minutos)
    const aoVoltar = () => setAgora(Date.now());
    document.addEventListener("visibilitychange", aoVoltar);
    return () => document.removeEventListener("visibilitychange", aoVoltar);
  }, []);

  const tarefaPronta = (t: Tarefa) => t.desistiu || (t.segundos !== null && t.escolha !== null);
  const podeSeguir =
    passo === 0 || (indiceTarefa >= 0 && atual !== null && tarefaPronta(atual)) || passo === 4 || (passo === 5 && facilidade.every((f) => f !== null)) || passo === 6;

  async function enviar() {
    setEnviando(true);
    setErro("");
    try {
      await api.avaliar({
        perfil,
        tempos: tarefas.map((t) => (t.desistiu ? null : t.segundos)),
        acertos: tarefas.map((t, i) => (t.desistiu || t.escolha === null ? null : t.escolha === TAREFAS[i].certa)),
        energia,
        nota_energia: notaEnergia,
        facilidade: facilidade.map((f) => f ?? 3),
        comentario: comentario.trim() || null,
        sugestao: sugestao.trim() || null,
      }, idDoAparelho());
      setPasso(7);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não deu para enviar agora. Tente de novo.");
    } finally {
      setEnviando(false);
    }
  }

  const total = 6;
  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 px-4 py-8 lg:px-8">
      <header className="space-y-2">
        <Link to="/avaliacao" className="inline-flex items-center gap-1 text-[14px] font-semibold text-marca-forte"><ArrowLeft className="size-4" aria-hidden />Avaliação usuários</Link>
        <h2 className="text-2xl font-bold">Avaliar o Dá Tempo?</h2>
        {passo < 7 && (
          <div className="flex items-center gap-3">
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-fundo ring-1 ring-linha ring-inset">
              <div className="h-full rounded-full bg-marca transition-all" style={{ width: `${(Math.min(passo, total) / total) * 100}%` }} />
            </div>
            <span className="text-[13px] font-semibold text-apagado">{Math.min(passo, total)} de {total}</span>
          </div>
        )}
      </header>

      {passo === 0 && (
        <section className="space-y-4 rounded-2xl border border-linha bg-superficie p-5">
          <p className="text-[16px] leading-relaxed">
            Leva uns 10 minutos. Você vai usar o app para achar três respostas (o tempo é medido), testar a parte de energia e dizer o que achou.
            Use o app numa outra aba e volte aqui a cada passo.
          </p>
          <a href="/app" target="_blank" rel="noopener" className="inline-flex items-center gap-2 rounded-full bg-marca-suave px-4 py-2 text-[15px] font-semibold text-marca-forte">
            Abrir o app em outra aba<ExternalLink className="size-4" aria-hidden />
          </a>
          <div className="space-y-2">
            <p className="text-[15px] font-semibold">Como você conhece o projeto? <span className="font-normal text-apagado">(opcional)</span></p>
            <div className="flex flex-wrap gap-2">
              {PERFIS.map((p) => (
                <button key={p.valor} type="button" onClick={() => setPerfil(perfil === p.valor ? null : p.valor)} aria-pressed={perfil === p.valor}
                  className={`rounded-full px-4 py-2 text-[15px] font-semibold ring-1 ring-inset ${perfil === p.valor ? "bg-marca text-white ring-marca" : "ring-linha hover:ring-marca/50"}`}>
                  {p.rotulo}
                </button>
              ))}
            </div>
          </div>
          <p className="rounded-xl bg-fundo px-3.5 py-2.5 text-[14px] text-apagado ring-1 ring-linha ring-inset">
            Não pedimos nome, e-mail nem telefone. Não escreva dado pessoal nos comentários.
          </p>
        </section>
      )}

      {atual && (
        <section className="space-y-4 rounded-2xl border border-linha bg-superficie p-5">
          <p className="text-[13px] font-semibold text-marca-forte">Tarefa {indiceTarefa + 1} de 3</p>
          <p className="text-[18px] leading-snug font-bold">{TAREFAS[indiceTarefa].texto}</p>
          <p className="text-[14px] text-apagado">Use a Lia (aba IA) ou o app como quiser. Toque em começar e, quando achar, volte e toque em "Achei".</p>
          {atual.inicio === null && (
            <button type="button" onClick={() => { mudarTarefa(indiceTarefa, { inicio: Date.now() }); setAgora(Date.now()); }}
              className="inline-flex items-center gap-2 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">
              <Timer className="size-4" aria-hidden />Começar
            </button>
          )}
          {contando && (
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-2xl font-bold tabular-nums">{Math.floor(decorrido / 60)}:{String(decorrido % 60).padStart(2, "0")}</span>
              <button type="button" onClick={() => {
                const s = segundosAte(atual.inicio as number, Date.now());
                mudarTarefa(indiceTarefa, s >= MAXIMO_S ? { desistiu: true } : { segundos: s });
              }}
                className="rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte">Achei</button>
              <button type="button" onClick={() => mudarTarefa(indiceTarefa, { desistiu: true })}
                className="rounded-full px-4 py-2.5 text-[15px] font-semibold text-apagado ring-1 ring-linha ring-inset">Não encontrei</button>
            </div>
          )}
          {atual.desistiu && <p className="text-[15px] font-semibold text-apagado">Tudo bem, essa fica como "não encontrou". Siga para a próxima.</p>}
          {atual.segundos !== null && !atual.desistiu && (
            <div className="space-y-2">
              <p className="text-[15px] font-semibold">Achou em {atual.segundos} s. Qual foi a resposta?</p>
              {TAREFAS[indiceTarefa].opcoes.map((o, k) => (
                <button key={o} type="button" onClick={() => mudarTarefa(indiceTarefa, { escolha: k })} aria-pressed={atual.escolha === k}
                  className={`flex w-full items-start gap-2 rounded-xl px-3.5 py-2.5 text-left text-[15px] ring-1 ring-inset ${atual.escolha === k ? "bg-marca-suave ring-marca" : "ring-linha hover:ring-marca/50"}`}>
                  <span className={`mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full ring-1 ${atual.escolha === k ? "bg-marca ring-marca" : "ring-linha"}`}>
                    {atual.escolha === k && <Check className="size-3 text-white" aria-hidden />}
                  </span>
                  {o}
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      {passo === 4 && (
        <section className="space-y-4 rounded-2xl border border-linha bg-superficie p-5">
          <p className="text-[13px] font-semibold text-marca-forte">Energia da viagem</p>
          {SITUACOES.map((s, i) => (
            <div key={s} className="space-y-2">
              <p className="text-[15px]">{s}</p>
              <div className="flex flex-wrap gap-2">
                {(["sim", "em parte", "nao"] as Entendeu[]).map((e) => (
                  <button key={e} type="button" onClick={() => setEnergia((v) => v.map((x, k) => (k === i ? e : x)))} aria-pressed={energia[i] === e}
                    className={`rounded-full px-4 py-1.5 text-[14px] font-semibold ring-1 ring-inset ${energia[i] === e ? "bg-marca text-white ring-marca" : "ring-linha hover:ring-marca/50"}`}>
                    {e === "sim" ? "Sim" : e === "em parte" ? "Em parte" : "Não"}
                  </button>
                ))}
              </div>
            </div>
          ))}
          <div className="space-y-2 border-t border-linha pt-4">
            <p className="text-[15px] font-semibold">Essas informações de energia ajudariam você a escolher como ir ao trabalho? (1 a 5)</p>
            <Escala valor={notaEnergia} mudar={setNotaEnergia} nome="Nota da energia" />
          </div>
        </section>
      )}

      {passo === 5 && (
        <section className="space-y-5 rounded-2xl border border-linha bg-superficie p-5">
          <p className="text-[14px] text-apagado">1 = discordo totalmente, 5 = concordo totalmente</p>
          {PERGUNTAS.map((p, i) => (
            <div key={p} className="space-y-2">
              <p className="text-[15px] font-semibold">{i + 1}. {p}</p>
              <Escala valor={facilidade[i]} mudar={(n) => setFacilidade((v) => v.map((x, k) => (k === i ? n : x)))} nome={p} />
            </div>
          ))}
        </section>
      )}

      {passo === 6 && (
        <section className="space-y-4 rounded-2xl border border-linha bg-superficie p-5">
          <label className="block space-y-1.5">
            <span className="text-[15px] font-semibold">O que você achou? <span className="font-normal text-apagado">(opcional)</span></span>
            <textarea value={comentario} onChange={(e) => setComentario(e.target.value)} maxLength={500} rows={4}
              className="w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px]" placeholder="Do que gostou, o que estranhou, o que faria você usar." />
          </label>
          <label className="block space-y-1.5">
            <span className="text-[15px] font-semibold">Uma sugestão de melhoria <span className="font-normal text-apagado">(opcional)</span></span>
            <textarea value={sugestao} onChange={(e) => setSugestao(e.target.value)} maxLength={300} rows={3}
              className="w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px]" />
          </label>
          <p className="text-[13px] text-apagado">Sem nome, telefone ou e-mail: textos com dado pessoal são recusados.</p>
          {erro && <p className="rounded-xl bg-erro/10 px-3.5 py-2.5 text-[14px] font-semibold text-erro" role="alert">{erro}</p>}
        </section>
      )}

      {passo === 7 && (
        <section className="space-y-3 rounded-2xl border border-linha bg-superficie p-6 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-full bg-marca-suave text-marca-forte"><Check className="size-6" aria-hidden /></span>
          <p className="text-xl font-bold">Obrigado pela avaliação!</p>
          <p className="text-[15px] text-apagado">Ela já aparece, sem identificar você, na página de avaliação.</p>
          <Link to="/avaliacao" className="inline-flex items-center gap-1 text-[15px] font-semibold text-marca-forte">Ver as avaliações<ArrowRight className="size-4" aria-hidden /></Link>
        </section>
      )}

      {passo < 7 && (
        <div className="flex items-center justify-between">
          <button type="button" disabled={passo === 0 || contando} onClick={() => setPasso((p) => p - 1)}
            className="inline-flex items-center gap-1 rounded-full px-4 py-2 text-[15px] font-semibold text-apagado disabled:opacity-30">
            <ArrowLeft className="size-4" aria-hidden />Voltar
          </button>
          {passo < 6 ? (
            <button type="button" disabled={!podeSeguir} onClick={() => setPasso((p) => p + 1)}
              className="inline-flex items-center gap-1 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-40">
              {passo === 0 ? "Começar o teste" : "Seguir"}<ArrowRight className="size-4" aria-hidden />
            </button>
          ) : (
            <button type="button" disabled={enviando} onClick={() => void enviar()}
              className="inline-flex items-center gap-1 rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-40">
              {enviando ? "Enviando..." : "Enviar avaliação"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
