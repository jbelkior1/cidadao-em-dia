import { House, Map as MapaIcone, Menu, MessageCircle, RotateCcw, Siren, UserRound, type LucideIcon } from "lucide-react";
import { useState } from "react";

import Feed from "../abas/Feed";
import Mapa from "../abas/Mapa";
import Perfil from "../abas/Perfil";
import { useApp } from "../App";
import { Avatar } from "./Auxilia";
import Chat, { BotaoAlertas, PainelAlertas } from "./Chat";
import { MarcaDaTempo } from "./Logo";
import { useConversa } from "./conversa";
import Sos from "./Sos";

/*
 * A casca do app (o que vai dentro do celular): cabeçalho com SOS e sinal de alerta em todas as abas,
 * e a barra de 4 abas embaixo, como decidido na reunião de 12/11: Home (feed), Mapa, IA e Perfil.
 * Desenho no padrão dos apps de mobilidade: branco, preto para ação, laranja só na marca e na aba ativa.
 */

export type IdAba = "home" | "mapa" | "ia" | "perfil";
const ABAS: { id: IdAba; rotulo: string; titulo: string; Icone: LucideIcon }[] = [
  { id: "home", rotulo: "Home", titulo: "Dá Tempo?", Icone: House },
  { id: "mapa", rotulo: "Mapa", titulo: "Mapa", Icone: MapaIcone },
  { id: "ia", rotulo: "IA", titulo: "Lia", Icone: MessageCircle },
  { id: "perfil", rotulo: "Perfil", titulo: "Perfil", Icone: UserRound },
];

export default function AppAbas({ aoAbrirMenu }: { aoAbrirMenu?: () => void }) {
  const { ia } = useApp();
  const { simular, reiniciar, falas, enviar } = useConversa();
  const [aba, setAba] = useState<IdAba>("home");
  const [alertas, setAlertas] = useState(false);
  const [sos, setSos] = useState(false);
  const atual = ABAS.find((a) => a.id === aba) ?? ABAS[0];

  const ir = (destino: IdAba, focarConversa = false) => {
    setAba(destino);
    setAlertas(false);
    if (focarConversa) window.setTimeout(() => document.getElementById("mensagem-auxilia")?.focus(), 60);
  };
  const abrirSos = () => { setSos(true); setAlertas(false); };

  return (
    <div className="@container relative flex h-full min-h-0 flex-col bg-superficie">
      <header className="relative z-20 flex h-[60px] shrink-0 items-center gap-2 bg-superficie px-4">
        {aoAbrirMenu && (
          <button type="button" onClick={aoAbrirMenu} aria-label="Abrir o menu do sistema" className="-ml-1.5 flex size-10 items-center justify-center rounded-full hover:bg-cinza">
            <Menu className="size-5" />
          </button>
        )}
        {aba === "ia" ? <Avatar /> : <MarcaDaTempo tamanho={36} />}
        <div className="min-w-0 flex-1 leading-none">
          <h2 className="truncate text-[21px] font-extrabold tracking-tight">{aba === "home" ? "dá tempo?" : atual.titulo}</h2>
          {aba === "ia" && <p className="mt-1 truncate text-[12px] text-apagado">sua companhia no trem e no metrô</p>}
        </div>
        {simular && <span className="hidden rounded-full bg-erro-suave px-2.5 py-1 text-[11px] font-bold text-erro @sm:inline">simulação L{simular}</span>}
        {aba === "ia" && !ia?.ligada && <span className="rounded-full bg-cinza px-2.5 py-1 text-[11px] font-bold text-apagado">sem IA</span>}
        {aba === "ia" && falas.length > 0 && (
          <button type="button" onClick={reiniciar} aria-label="Nova conversa" title="Nova conversa" className="flex size-10 items-center justify-center rounded-full bg-cinza hover:bg-cinza-forte">
            <RotateCcw className="size-[18px]" />
          </button>
        )}
        <button type="button" onClick={abrirSos} aria-label="SOS: pedir ajuda"
          className="flex h-10 items-center gap-1.5 rounded-full bg-erro px-3.5 text-[14px] font-bold text-white hover:brightness-110">
          <Siren className="size-[18px]" aria-hidden />SOS
        </button>
        <BotaoAlertas aberto={alertas} aoAlternar={() => { setAlertas((v) => !v); setSos(false); }} />
      </header>

      {alertas && <PainelAlertas aoFechar={() => setAlertas(false)} aoPerguntar={() => ir("ia")} />}
      {sos && <Sos aoFechar={() => setSos(false)} />}

      <div className="min-h-0 flex-1 overflow-hidden">
        {aba === "home" && <Feed aoIr={ir} aoSos={abrirSos} />}
        {aba === "mapa" && <Mapa simular={simular || undefined} />}
        {aba === "ia" && <Chat />}
        {aba === "perfil" && <Perfil aoConferir={(texto) => { ir("ia"); enviar(texto); }} />}
      </div>

      <nav className="grid shrink-0 grid-cols-4 border-t border-linha bg-superficie pb-[max(env(safe-area-inset-bottom),8px)]" aria-label="Abas do app">
        {ABAS.map(({ id, rotulo, Icone }) => {
          const ativa = aba === id;
          return (
            <button key={id} type="button" aria-current={ativa ? "page" : undefined} onClick={() => ir(id)}
              className={`relative flex flex-col items-center gap-1 pt-2.5 pb-1 text-[12px] ${ativa ? "font-bold text-tinta" : "font-medium text-apagado hover:text-tinta"}`}>
              <span className={`absolute top-0 h-[3px] w-8 rounded-b-full ${ativa ? "bg-laranja" : "bg-transparent"}`} aria-hidden />
              <Icone className="size-[22px]" strokeWidth={ativa ? 2.4 : 1.8} aria-hidden />
              {rotulo}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
