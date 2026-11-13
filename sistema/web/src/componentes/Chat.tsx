import { AlertTriangle, CheckCircle2, CloudLightning, Droplets } from "lucide-react";
import { useEffect } from "react";

import { corDoTexto, type ItemAlerta } from "../lib/api";
import { Entrada, Mensagens } from "./Auxilia";
import { hora } from "./Linha";
import { useConversa } from "./conversa";

/*
 * A aba IA: a conversa com a Lia (saudação e atalhos no começo) e a caixa de texto.
 * O cabeçalho e o sinal de alerta ficam na casca do app (AppAbas), para valerem em todas as abas.
 */

const COR_NIVEL = {
  parada: "border-erro/30 bg-erro-suave/60",
  atencao: "border-alerta/30 bg-alerta-suave/60",
  ok: "border-linha bg-superficie",
};
const TEXTO_NIVEL = { parada: "Parada", atencao: "Atenção", ok: "Normal" };

function IconeAlerta({ item }: { item: ItemAlerta }) {
  if (item.tipo === "linha" && item.linha) {
    return (
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl text-[14px] font-extrabold" style={{ background: item.linha.cor, color: corDoTexto(item.linha.cor) }} aria-label={`Linha ${item.linha.numero}`}>
        {item.linha.numero}
      </span>
    );
  }
  const Icone = item.nivel === "ok" ? CheckCircle2 : item.tipo === "chuva" ? CloudLightning : Droplets;
  const cor = item.nivel === "ok" ? "bg-ok-suave text-ok" : item.nivel === "parada" ? "bg-erro-suave text-erro" : "bg-alerta-suave text-alerta";
  return <span className={`flex size-9 shrink-0 items-center justify-center rounded-xl ${cor}`}><Icone className="size-[18px]" aria-hidden /></span>;
}

/** Painel que abre pelo sinal de alerta. Tocar num alerta pergunta à Lia como ele afeta a viagem. */
export function PainelAlertas({ aoFechar, aoPerguntar }: { aoFechar: () => void; aoPerguntar: () => void }) {
  const { alertas, enviar } = useConversa();
  useEffect(() => {
    const aoTeclar = (e: KeyboardEvent) => e.key === "Escape" && aoFechar();
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aoFechar]);
  return (
    <>
      <button type="button" aria-label="Fechar alertas" onClick={aoFechar} className="absolute inset-x-0 top-14 bottom-0 z-20 cursor-default bg-tinta/30" />
      <section aria-label="Alertas agora" className="entrar absolute top-16 right-3 left-3 z-30 mx-auto max-w-md space-y-2.5 rounded-2xl border border-linha bg-superficie p-4 shadow-2xl">
        <div className="flex items-baseline justify-between">
          <h3 className="text-[18px] font-extrabold">Alertas agora</h3>
          <span className="text-[12px] text-apagado">{alertas?.lido_em ? `lidos às ${hora(alertas.lido_em)}` : "lendo..."}</span>
        </div>
        {alertas?.itens.length === 0 && <p className="text-[14px] text-apagado">Nada fora do normal agora.</p>}
        {alertas?.itens.map((item, i) => (
          <button key={i} type="button" onClick={() => { aoPerguntar(); enviar(item.pergunta); aoFechar(); }}
            className={`flex w-full items-start gap-3 rounded-xl border p-3 text-left hover:border-marca ${COR_NIVEL[item.nivel]}`}>
            <IconeAlerta item={item} />
            <span className="flex min-w-0 flex-col gap-0.5">
              <span className="text-[15px] font-bold">{item.titulo}</span>
              <span className="text-[13px] text-apagado">{item.texto}</span>
              <span className={`text-[12px] font-bold ${item.nivel === "ok" ? "text-ok" : item.nivel === "parada" ? "text-erro" : "text-alerta"}`}>
                {TEXTO_NIVEL[item.nivel]} · {item.fonte}
              </span>
            </span>
          </button>
        ))}
        <p className="text-[12px] text-apagado">Toque num alerta para perguntar à Lia como ele afeta a sua viagem. O aviso da estação vale mais.</p>
      </section>
    </>
  );
}

/** O sinal de alerta do canto superior direito: cinza sem alertas, âmbar com atenção, vermelho com linha parada. */
export function BotaoAlertas({ aberto, aoAlternar }: { aberto: boolean; aoAlternar: () => void }) {
  const { alertas } = useConversa();
  const total = alertas?.total ?? 0;
  const cor = !total ? "bg-fundo text-apagado ring-1 ring-linha" : alertas?.parada ? "bg-erro-suave text-erro" : "bg-alerta-suave text-alerta";
  return (
    <button type="button" onClick={aoAlternar} aria-expanded={aberto} aria-label={total ? `${total} ${total === 1 ? "alerta" : "alertas"} agora` : "Sem alertas agora"}
      className={`flex h-10 items-center gap-1.5 rounded-full px-3 text-[14px] font-bold ${cor} ${aberto ? "ring-2 ring-current" : ""}`}>
      {total ? <AlertTriangle className="size-[18px]" aria-hidden /> : <CheckCircle2 className="size-[18px]" aria-hidden />}
      {total || ""}
    </button>
  );
}

export default function Chat() {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <Mensagens />
      <Entrada />
    </div>
  );
}
