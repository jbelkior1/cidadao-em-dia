import { Entrada, Mensagens } from "../Auxilia";
import { Cabecalho, type PropsLayout } from "./comum";

/** Layout 1 · Conversa: a tela é o chat, com os cartões dentro das falas (como um app de mensagens). */
export default function LayoutConversa({ aoAbrirMenu }: PropsLayout) {
  return (
    <div className="@container flex h-full min-h-0 flex-col bg-fundo">
      <Cabecalho aoAbrirMenu={aoAbrirMenu} />
      <Mensagens />
      <Entrada />
    </div>
  );
}
