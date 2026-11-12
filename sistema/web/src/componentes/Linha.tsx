import { AlertTriangle, CircleCheck, CircleSlash, HelpCircle, OctagonX } from "lucide-react";

import { corDoTexto, type Nivel } from "../lib/api";

/** O número da linha na cor oficial. */
export function SeloLinha({ numero, cor, tamanho = "md" }: { numero: string; cor: string; tamanho?: "sm" | "md" | "lg" }) {
  const medida = tamanho === "lg" ? "size-11 text-lg" : tamanho === "sm" ? "size-6 text-[11px]" : "size-8 text-sm";
  return (
    <span className={`inline-flex shrink-0 items-center justify-center rounded-lg font-bold ${medida}`} style={{ background: cor, color: corDoTexto(cor) }}
      aria-label={`Linha ${numero}`}>
      {numero}
    </span>
  );
}

const NIVEIS: Record<Nivel, { rotulo: string; classe: string; Icone: typeof CircleCheck }> = {
  normal: { rotulo: "Normal", classe: "bg-ok-suave text-ok", Icone: CircleCheck },
  atencao: { rotulo: "Atenção", classe: "bg-alerta-suave text-alerta", Icone: AlertTriangle },
  parada: { rotulo: "Parada", classe: "bg-erro-suave text-erro", Icone: OctagonX },
  encerrada: { rotulo: "Encerrada", classe: "bg-fundo text-apagado ring-1 ring-linha ring-inset", Icone: CircleSlash },
  sem_dado: { rotulo: "Sem informação", classe: "bg-fundo text-apagado ring-1 ring-linha ring-inset", Icone: HelpCircle },
};

/** Situação sempre com ícone e palavra, nunca só cor. */
export function SituacaoLinha({ nivel }: { nivel: Nivel }) {
  const n = NIVEIS[nivel] ?? NIVEIS.sem_dado;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[13px] font-semibold ${n.classe}`}>
      <n.Icone className="size-3.5" aria-hidden />
      {n.rotulo}
    </span>
  );
}

export function hora(iso: string): string {
  return iso ? iso.slice(11, 16) : "--:--";
}
