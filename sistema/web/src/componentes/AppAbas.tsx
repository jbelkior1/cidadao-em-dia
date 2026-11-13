import { House, Map as MapaIcone, Menu, MessageCircle, RotateCcw, Siren, UserRound, type LucideIcon } from "lucide-react";
import { useState } from "react";

import Feed from "../abas/Feed";
import Mapa from "../abas/Mapa";
import Perfil from "../abas/Perfil";
import { useApp } from "../App";
import { Avatar } from "./Auxilia";
import Chat, { BotaoAlertas, PainelAlertas } from "./Chat";
import { useConversa } from "./conversa";
import Sos from "./Sos";

/*
 * A casca do app (o que vai dentro do celular): cabeçalho com SOS e sinal de alerta em todas as abas,
 * e a barra de 4 abas embaixo, como decidido na reunião de 12/11: Home (feed), Mapa, IA e Perfil.
 * A aba da IA tem o nome "IA" na barra; lá dentro a agente se chama Lia.
 */

type IdAba = "home" | "mapa" | "ia" | "perfil";
const ABAS: { id: IdAba; rotulo: string; titulo: string; Icone: LucideIcon }[] = [
  { id: "home", rotulo: "Home", titulo: "Dá Tempo?", Icone: House },
  { id: "mapa", rotulo: "Mapa", titulo: "Mapa", Icone: MapaIcone },
  { id: "ia", rotulo: "IA", titulo: "Lia", Icone: MessageCircle },
  { id: "perfil", rotulo: "Perfil", titulo: "Perfil", Icone: UserRound },
];

export default function AppAbas({ aoAbrirMenu }: { aoAbrirMenu?: () => void }) {
  const { ia } = useApp();
  const { simular, reiniciar, falas } = useConversa();
  const [aba, setAba] = useState<IdAba>("home");
  const [alertas, setAlertas] = useState(false);
  const [sos, setSos] = useState(false);
  const atual = ABAS.find((a) => a.id === aba) ?? ABAS[0];

  return (
    <div className="@container relative flex h-full min-h-0 flex-col bg-fundo">
      <header className="flex h-14 shrink-0 items-center gap-2 border-b border-linha bg-superficie px-3">
        {aoAbrirMenu && <button type="button" onClick={aoAbrirMenu} aria-label="Abrir o menu do sistema" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><Menu className="size-5" /></button>}
        {aba === "ia" ? (
          <Avatar />
        ) : (
          <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-marca text-[17px] font-black text-white" aria-hidden>D</span>
        )}
        <div className="min-w-0 flex-1 leading-tight">
          <h2 className="truncate text-[16px] font-bold">{atual.titulo}</h2>
          {aba === "ia" && <p className="truncate text-[12px] text-apagado">sua companhia no trem e no metrô</p>}
        </div>
        {simular && <span className="hidden rounded-full bg-erro-suave px-2 py-0.5 text-[11px] font-semibold text-erro @sm:inline">simulação L{simular}</span>}
        {aba === "ia" && !ia?.ligada && <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-semibold text-apagado ring-1 ring-linha">sem IA</span>}
        {aba === "ia" && falas.length > 0 && (
          <button type="button" onClick={reiniciar} aria-label="Nova conversa" title="Nova conversa" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><RotateCcw className="size-4" /></button>
        )}
        <button type="button" onClick={() => { setSos(true); setAlertas(false); }} aria-label="SOS: pedir ajuda"
          className="flex h-10 items-center gap-1.5 rounded-full bg-erro px-3 text-[13px] font-extrabold text-white hover:opacity-90">
          <Siren className="size-4" aria-hidden />SOS
        </button>
        <BotaoAlertas aberto={alertas} aoAlternar={() => { setAlertas((v) => !v); setSos(false); }} />
      </header>

      {alertas && <PainelAlertas aoFechar={() => setAlertas(false)} aoPerguntar={() => setAba("ia")} />}
      {sos && <Sos aoFechar={() => setSos(false)} />}

      <div className="min-h-0 flex-1 overflow-hidden">
        {aba === "home" && <Feed />}
        {aba === "mapa" && <Mapa simular={simular || undefined} />}
        {aba === "ia" && <Chat />}
        {aba === "perfil" && <Perfil />}
      </div>

      <nav className="grid shrink-0 grid-cols-4 border-t border-linha bg-superficie pt-1.5 pb-[max(env(safe-area-inset-bottom),6px)]" aria-label="Abas do app">
        {ABAS.map(({ id, rotulo, Icone }) => {
          const ativa = aba === id;
          return (
            <button key={id} type="button" aria-current={ativa ? "page" : undefined} onClick={() => setAba(id)}
              className={`flex flex-col items-center gap-0.5 rounded-xl py-1 text-[11px] font-bold ${ativa ? "text-marca" : "text-apagado hover:text-tinta"}`}>
              <span className={`flex h-7 w-14 items-center justify-center rounded-full ${ativa ? "bg-marca-suave" : ""}`}><Icone className="size-[20px]" aria-hidden /></span>
              {rotulo}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
