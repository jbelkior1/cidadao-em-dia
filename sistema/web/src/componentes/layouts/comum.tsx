import { Menu, RotateCcw } from "lucide-react";

import { useApp } from "../../App";
import { Avatar } from "../Auxilia";
import { useConversa } from "../conversa";

/*
 * Contrato dos layouts do sistema.
 *
 * Cada layout é um componente padrão em ./layouts/<Nome>.tsx que recebe PropsLayout e
 * ocupa 100% da altura do espaço que recebe. A moldura (celular ou notebook), a barra de
 * status do celular e o aviso no aparelho são da página do sistema, não do layout.
 *
 * O layout monta a tela com as peças prontas:
 * - useConversa(): falas, sugestoes, esperando, enviar(texto), reiniciar(), resumo
 *   ({ panorama, plano, alertas }: o último cartão de cada tipo), simular, rastro;
 * - <Mensagens semCartoes? />, <Entrada semSugestoes? placeholder? />, <Avatar />;
 * - <CartaoDaAuxilia cartao /> e <EtapasCompactas rota />, de ../Cartoes;
 * - <SeloLinha /> e <SituacaoLinha />, de ../Linha;
 * - <Cabecalho />, deste arquivo.
 *
 * A raiz do layout deve ter a classe "@container" e usar variantes @md:, @2xl: etc.
 * (container queries), porque o mesmo layout roda dentro do celular (392 px) e do notebook.
 */
export type PropsLayout = {
  /** true quando está dentro do desenho do celular ou no celular de verdade */
  celular: boolean;
  /** só no celular de verdade: abre o menu do sistema (matérias, sociedade) */
  aoAbrirMenu?: () => void;
};

export function Cabecalho({ aoAbrirMenu, subtitulo = "sua companhia no trem e no metrô" }: { aoAbrirMenu?: () => void; subtitulo?: string }) {
  const { ia } = useApp();
  const { simular, reiniciar } = useConversa();
  return (
    <header className="flex h-14 shrink-0 items-center gap-2.5 border-b border-linha bg-superficie px-3">
      {aoAbrirMenu && <button type="button" onClick={aoAbrirMenu} aria-label="Abrir o menu do sistema" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><Menu className="size-5" /></button>}
      <Avatar />
      <div className="min-w-0 leading-tight">
        <p className="text-[16px] font-bold">Auxilia</p>
        <p className="flex items-center gap-1 truncate text-[12px] text-apagado"><span className="size-1.5 shrink-0 rounded-full bg-ok" aria-hidden />{subtitulo}</p>
      </div>
      <div className="ml-auto flex items-center gap-1.5">
        {simular && <span className="rounded-full bg-erro-suave px-2 py-0.5 text-[11px] font-semibold text-erro">simulação L{simular}</span>}
        {!ia?.ligada && <span className="rounded-full bg-fundo px-2 py-0.5 text-[11px] font-semibold text-apagado ring-1 ring-linha">sem IA</span>}
        <button type="button" onClick={reiniciar} aria-label="Nova conversa" title="Nova conversa" className="rounded-lg p-1.5 text-apagado hover:bg-fundo"><RotateCcw className="size-4" /></button>
      </div>
    </header>
  );
}
