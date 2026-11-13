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
    // resposta de erro (4xx/5xx) ou sem a lista de canais não pode derrubar o SOS: os números de emergência ficam
    fetch(`/api/sos?${q}`)
      .then((x) => (x.ok ? x.json() : null))
      .then((d) => setR(d && Array.isArray(d.canais) ? d : null))
      .catch(() => setR(null));
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
      <button type="button" aria-label="Fechar o SOS" onClick={aoFechar} className="absolute inset-0 z-30 cursor-default bg-tinta/45" />
      <section role="dialog" aria-label="Pedir ajuda" className="subir absolute inset-x-0 bottom-0 z-40 mx-auto flex max-h-[90%] max-w-md flex-col overflow-hidden rounded-t-[28px] bg-superficie shadow-folha">
        <span className="alca" aria-hidden />
        <div className="flex items-center gap-3 px-5 pt-3 pb-2">
          <span className="flex size-10 items-center justify-center rounded-full bg-erro text-white"><Siren className="size-5" aria-hidden /></span>
          <h3 className="flex-1 text-[24px] font-bold tracking-tight">Pedir ajuda</h3>
          <button type="button" onClick={aoFechar} aria-label="Fechar" className="flex size-10 items-center justify-center rounded-full bg-cinza hover:bg-cinza-forte"><X className="size-5" /></button>
        </div>

        <div className="space-y-5 overflow-y-auto px-5 pt-2 pb-6">
          <div>
            <p className="text-[16px] font-bold">Em perigo agora, ligue</p>
            <div className="mt-2 grid grid-cols-3 gap-2">
              {(r?.emergencia ?? [{ rotulo: "Polícia", numero: "190" }, { rotulo: "SAMU", numero: "192" }, { rotulo: "Bombeiros", numero: "193" }]).map((e) => (
                <a key={e.numero} href={`tel:${e.numero}`} className="flex flex-col items-center rounded-2xl bg-erro-suave py-3 text-center text-erro hover:bg-erro hover:text-white">
                  <span className="text-[26px] leading-none font-extrabold tracking-tight">{e.numero}</span>
                  <span className="mt-1 text-[12px] font-bold">{e.rotulo}</span>
                </a>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-[16px] font-bold">Avisar a operadora: em que linha você está?</p>
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
                <label htmlFor="sos-estacao" className="block text-[14px] font-bold">Estação (opcional)</label>
                <select id="sos-estacao" value={estacao} onChange={(e) => setEstacao(e.target.value)} className="mt-1.5 h-12 w-full rounded-2xl bg-cinza px-4 text-[16px] font-medium focus:bg-superficie focus:ring-2 focus:ring-tinta focus:outline-none">
                  <option value="">Não sei / não quero dizer</option>
                  {daLinha.map((e) => <option key={e.id} value={e.nome}>{e.nome}</option>)}
                </select>
              </div>
            )}
          </div>

          {r?.canais.map((c) => (
            <div key={c.servico} className="space-y-2.5 rounded-2xl bg-cinza p-4">
              <p className="flex items-center gap-2 text-[16px] font-bold">
                {c.acao.tipo === "sms" ? <MessageSquareText className="size-[18px]" aria-hidden /> : <Phone className="size-[18px]" aria-hidden />}{c.rotulo}
              </p>
              <p className="text-[13px] text-apagado">{c.detalhe}</p>
              {c.acao.texto !== undefined && (
                <p className="rounded-xl bg-superficie px-3 py-2 text-[14px]"><span className="text-apagado">Texto que vai escrito: </span>“{c.acao.texto}”</p>
              )}
              <div className="flex flex-wrap items-center gap-2">
                <a href={c.acao.href} className="inline-flex h-11 items-center gap-2 rounded-full bg-tinta px-5 text-[14px] font-bold text-white hover:bg-tinta/85">
                  {c.acao.tipo === "sms" ? "Abrir o SMS" : "Ligar"} {c.acao.numero}
                </a>
                <button type="button" onClick={() => copiar(c.acao.texto !== undefined ? `${c.acao.numero}: ${c.acao.texto}` : c.acao.numero ?? "", c.servico)}
                  className="inline-flex h-11 items-center gap-1.5 rounded-full bg-superficie px-4 text-[14px] font-bold hover:bg-cinza-forte">
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
