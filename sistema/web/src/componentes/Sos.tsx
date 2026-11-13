import { Check, Copy, MessageSquareText, Phone, Siren, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { mobilidade, type EstacaoEscolha, type LinhaInfo } from "../lib/api";
import { SeloLinha } from "./Linha";

/*
 * SOS: abre o canal certo já preenchido. O app NÃO envia nada: quem toca em "enviar" é a pessoa.
 * Os canais vêm de /api/sos (catálogo da DSA). Não é canal de emergência.
 */

type Acao = { tipo: "sms" | "tel" | "link"; numero?: string; href: string; texto?: string };
type Canal = { servico: string; rotulo: string; detalhe: string; acao: Acao; catalogo: string };
type RespostaSos = { linha: string | null; operadora: string | null; canais: Canal[]; emergencia: { rotulo: string; numero: string }[]; aviso: string };

export default function Sos({ aoFechar }: { aoFechar: () => void }) {
  const [linhas, setLinhas] = useState<LinhaInfo[]>([]);
  const [estacoes, setEstacoes] = useState<EstacaoEscolha[]>([]);
  const [linha, setLinha] = useState("");
  const [estacao, setEstacao] = useState("");
  const [r, setR] = useState<RespostaSos | null>(null);
  const [copiado, setCopiado] = useState("");

  useEffect(() => {
    mobilidade.estacoes().then((x) => { setLinhas(x.linhas.filter((l) => l.numero !== "7")); setEstacoes(x.estacoes); }).catch(() => {});
    const aoTeclar = (e: KeyboardEvent) => e.key === "Escape" && aoFechar();
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aoFechar]);

  useEffect(() => {
    const q = new URLSearchParams();
    if (linha) q.set("linha", linha);
    if (estacao) q.set("estacao", estacao);
    fetch(`/api/sos?${q}`).then((x) => x.json()).then(setR).catch(() => setR(null));
  }, [linha, estacao]);

  const daLinha = useMemo(() => estacoes.filter((e) => !linha || e.linhas.includes(linha)), [estacoes, linha]);
  const copiar = async (texto: string, chave: string) => {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(chave);
      setTimeout(() => setCopiado(""), 2000);
    } catch {
      /* sem permissão: a pessoa copia na mão */
    }
  };

  return (
    <>
      <button type="button" aria-label="Fechar o SOS" onClick={aoFechar} className="absolute inset-0 z-30 cursor-default bg-tinta/40" />
      <section role="dialog" aria-label="Pedir ajuda" className="entrar absolute inset-x-0 bottom-0 z-40 mx-auto flex max-h-[88%] max-w-md flex-col overflow-hidden rounded-t-3xl border border-linha bg-superficie shadow-2xl">
        <div className="flex items-center gap-2 border-b border-linha px-4 py-3">
          <span className="flex size-9 items-center justify-center rounded-xl bg-erro-suave text-erro"><Siren className="size-5" aria-hidden /></span>
          <h3 className="flex-1 text-[18px] font-extrabold">Pedir ajuda</h3>
          <button type="button" onClick={aoFechar} aria-label="Fechar" className="rounded-full p-2 text-apagado hover:bg-fundo"><X className="size-5" /></button>
        </div>

        <div className="space-y-4 overflow-y-auto px-4 py-4">
          <div className="rounded-xl border border-erro/30 bg-erro-suave/60 p-3">
            <p className="text-[14px] font-bold">Em perigo agora, ligue</p>
            <div className="mt-2 grid grid-cols-3 gap-2">
              {(r?.emergencia ?? [{ rotulo: "Polícia", numero: "190" }, { rotulo: "SAMU", numero: "192" }, { rotulo: "Bombeiros", numero: "193" }]).map((e) => (
                <a key={e.numero} href={`tel:${e.numero}`} className="flex flex-col items-center rounded-xl bg-superficie py-2 text-center ring-1 ring-erro/40 hover:bg-erro hover:text-white">
                  <span className="text-[20px] leading-none font-extrabold">{e.numero}</span>
                  <span className="text-[12px] font-semibold">{e.rotulo}</span>
                </a>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-[14px] font-bold">Quer denunciar ou avisar a operadora? Em que linha você está?</p>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Linha">
              {linhas.map((l) => (
                <button key={l.numero} type="button" aria-pressed={linha === l.numero} aria-label={`Linha ${l.numero}-${l.nome}`}
                  onClick={() => { setLinha(linha === l.numero ? "" : l.numero); setEstacao(""); }}
                  className={`rounded-xl p-0.5 ${linha === l.numero ? "ring-2 ring-tinta ring-offset-2" : ""}`}>
                  <SeloLinha numero={l.numero} cor={l.cor} />
                </button>
              ))}
            </div>
            {linha && (
              <div>
                <label htmlFor="sos-estacao" className="block text-[13px] font-semibold text-apagado">Estação (opcional)</label>
                <select id="sos-estacao" value={estacao} onChange={(e) => setEstacao(e.target.value)} className="mt-1 w-full rounded-xl border border-linha bg-superficie px-3 py-2 text-[15px]">
                  <option value="">Não sei / não quero dizer</option>
                  {daLinha.map((e) => <option key={e.id} value={e.nome}>{e.nome}</option>)}
                </select>
              </div>
            )}
          </div>

          {r?.canais.map((c) => (
            <div key={c.servico} className="space-y-2 rounded-xl border border-linha p-3">
              <p className="flex items-center gap-2 text-[15px] font-bold">
                {c.acao.tipo === "sms" ? <MessageSquareText className="size-4 text-marca" aria-hidden /> : <Phone className="size-4 text-marca" aria-hidden />}{c.rotulo}
              </p>
              <p className="text-[13px] text-apagado">{c.detalhe}</p>
              {c.acao.texto !== undefined && (
                <p className="rounded-lg bg-fundo px-3 py-2 text-[13px]"><span className="text-apagado">Texto que vai escrito: </span>“{c.acao.texto}”</p>
              )}
              <div className="flex flex-wrap items-center gap-2">
                <a href={c.acao.href} className="inline-flex h-10 items-center gap-2 rounded-full bg-marca px-4 text-[14px] font-bold text-white hover:bg-marca-forte">
                  {c.acao.tipo === "sms" ? "Abrir o SMS" : "Ligar"} {c.acao.numero}
                </a>
                <button type="button" onClick={() => copiar(c.acao.texto !== undefined ? `${c.acao.numero}: ${c.acao.texto}` : c.acao.numero ?? "", c.servico)}
                  className="inline-flex h-10 items-center gap-1.5 rounded-full px-3 text-[13px] font-bold text-marca-forte ring-1 ring-marca ring-inset hover:bg-marca-suave">
                  {copiado === c.servico ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}{copiado === c.servico ? "Copiado" : "Copiar"}
                </button>
              </div>
              <p className="text-[11px] text-apagado">Fonte: catálogo de serviços ({c.servico}). Quem envia é você.</p>
            </div>
          ))}
          <p className="text-[12px] text-apagado">{r?.aviso ?? "O Dá Tempo? não é canal de emergência nem canal oficial."} O app não envia a sua localização nem guarda nada desta tela.</p>
        </div>
      </section>
    </>
  );
}
