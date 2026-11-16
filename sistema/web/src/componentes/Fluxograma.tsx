import { CORES_DAS_MATERIAS } from "../lib/api";

/*
 * Fluxograma do sistema. Sem destaque, mostra tudo. Com destaque (o código de uma
 * matéria), a matéria e as ligações dela ficam coloridas e o resto fica em cinza.
 */

type No = { id: string; rotulo: string; sub?: string; x: number; y: number; w: number; h: number; tipo: "pessoa" | "tela" | "materia" };
type Ligacao = { de: string; para: string; rotulo?: string; tracejada?: boolean };

const NOS: No[] = [
  { id: "cidadao", rotulo: "Passageiro", sub: "\"estou saindo de casa\"", x: 16, y: 120, w: 150, h: 60, tipo: "pessoa" },
  { id: "auxilia", rotulo: "Lia", sub: "conversa e conduz", x: 214, y: 110, w: 170, h: 80, tipo: "tela" },
  { id: "fontes", rotulo: "Fontes ao vivo", sub: "linhas, INMET, CGE", x: 430, y: 236, w: 190, h: 60, tipo: "tela" },
  { id: "SERS", rotulo: "SERS", sub: "energia da viagem", x: 730, y: 12, w: 168, h: 46, tipo: "materia" },
  { id: "MLAM", rotulo: "MLAM", sub: "segurança (SSP-SP)", x: 730, y: 64, w: 168, h: 46, tipo: "materia" },
  { id: "PCP", rotulo: "PCP", sub: "orientações oficiais", x: 730, y: 116, w: 168, h: 46, tipo: "materia" },
  { id: "DSA", rotulo: "DSA", sub: "canal de atendimento", x: 730, y: 168, w: 168, h: 46, tipo: "materia" },
  { id: "PAI", rotulo: "PAI", sub: "agente das fichas", x: 730, y: 220, w: 168, h: 46, tipo: "materia" },
  // entregues à parte: sem ligação com o sistema
  { id: "CS", rotulo: "CS", sub: "lógica · à mão", x: 560, y: 360, w: 156, h: 46, tipo: "materia" },
  { id: "COA", rotulo: "COA", sub: "sensor · Wokwi", x: 728, y: 360, w: 156, h: 46, tipo: "materia" },
  { id: "MMC", rotulo: "MMC", sub: "frota · modelo", x: 896, y: 360, w: 156, h: 46, tipo: "materia" },
];

/** Molduras de agrupamento (desenhadas atrás dos nós, sem setas). */
const GRUPOS = [{ x: 546, y: 320, w: 520, h: 98, rotulo: "Entregues à parte, fora do sistema" }];

const LIGACOES: Ligacao[] = [
  { de: "cidadao", para: "auxilia" },
  { de: "auxilia", para: "fontes", rotulo: "consulta" },
  { de: "auxilia", para: "SERS" },
  { de: "auxilia", para: "MLAM" },
  { de: "auxilia", para: "PCP", rotulo: "orienta" },
  { de: "auxilia", para: "DSA" },
  { de: "auxilia", para: "PAI", rotulo: "conversa" },
];

const POR_ID = Object.fromEntries(NOS.map((n) => [n.id, n]));
const CINZA = { fundo: "#EEF2F1", texto: "#9AA8A5", linha: "#D3DDDA" };

function caminho(a: No, b: No) {
  const x1 = a.x + a.w, y1 = a.y + a.h / 2, x2 = b.x, y2 = b.y + b.h / 2;
  const meio = (x1 + x2) / 2;
  return { d: `M${x1},${y1} C${meio},${y1} ${meio},${y2} ${x2 - 6},${y2}`, lx: meio, ly: (y1 + y2) / 2 };  // meio da curva
}

export default function Fluxograma({ destaque }: { destaque?: string }) {
  const ligados = new Set<string>(destaque ? [destaque] : []);
  if (destaque) LIGACOES.forEach((l) => (l.de === destaque ? ligados.add(l.para) : l.para === destaque ? ligados.add(l.de) : null));
  const ativo = (id: string) => !destaque || ligados.has(id);
  const corDestaque = destaque ? CORES_DAS_MATERIAS[destaque] : undefined;

  return (
    <div className="space-y-1">
    <p className="text-[12px] text-apagado sm:hidden">Arraste para o lado para ver o fluxograma inteiro.</p>
    <div className="overflow-x-auto rounded-xl border border-linha bg-superficie p-3">
      <svg viewBox="0 0 1080 424" className="w-full min-w-[620px]" role="img"
        aria-label={destaque ? `Fluxograma do sistema com a matéria ${destaque} em destaque` : "Fluxograma do sistema"}>
        <defs>
          {["normal", "foco", "cinza"].map((tipo) => (
            <marker key={tipo} id={`seta-${tipo}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill={tipo === "foco" ? corDestaque ?? "#556A6A" : tipo === "cinza" ? CINZA.linha : "#8FA19D"} />
            </marker>
          ))}
        </defs>

        {GRUPOS.map((g) => {
          const on = !destaque || NOS.some((n) => n.id === destaque && n.x >= g.x && n.y >= g.y && n.y < g.y + g.h);
          return (
            <g key={g.rotulo}>
              <rect x={g.x} y={g.y} width={g.w} height={g.h} rx={14} fill="none" stroke={on ? "#8FA19D" : CINZA.linha} strokeWidth={1.4} strokeDasharray="6 5" />
              <text x={g.x + 12} y={g.y + 22} fontSize="12.5" fontWeight="600" fill={on ? "#556A6A" : CINZA.texto}>{g.rotulo}</text>
            </g>
          );
        })}

        {LIGACOES.map((l) => {
          const emFoco = !destaque || l.de === destaque || l.para === destaque;
          const realce = Boolean(destaque && emFoco);
          const { d, lx, ly } = caminho(POR_ID[l.de], POR_ID[l.para]);
          const cor = realce ? corDestaque : emFoco ? "#8FA19D" : CINZA.linha;
          return (
            <g key={l.de + l.para}>
              <path d={d} fill="none" stroke={cor} strokeWidth={realce ? 2.6 : 1.4} strokeDasharray={l.tracejada ? "6 5" : undefined}
                markerEnd={`url(#seta-${realce ? "foco" : emFoco ? "normal" : "cinza"})`} />
              {l.rotulo && emFoco && (
                <g>
                  <rect x={lx - l.rotulo.length * 3.5 - 7} y={ly - 11} width={l.rotulo.length * 7 + 14} height={22} rx={7} fill="#FFFFFF" stroke="#E3EAE8" />
                  <text x={lx} y={ly + 4} textAnchor="middle" fontSize="12" fill="#3E5455">{l.rotulo}</text>
                </g>
              )}
            </g>
          );
        })}

        {NOS.map((n) => {
          const on = ativo(n.id);
          const ehDestaque = n.id === destaque;
          const corMateria = CORES_DAS_MATERIAS[n.id];
          let fundo = "#FFFFFF", texto = "#12292B", borda = "#CFDAD6", sub = "#556A6A";
          if (n.tipo === "pessoa") { fundo = "#12292B"; texto = "#FFFFFF"; borda = "#12292B"; }
          if (n.tipo === "materia") { fundo = corMateria; texto = "#FFFFFF"; borda = corMateria; sub = "rgba(255,255,255,0.88)"; }
          if (!on) { fundo = CINZA.fundo; texto = CINZA.texto; borda = CINZA.linha; sub = CINZA.texto; }
          return (
            <g key={n.id}>
              <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={n.tipo === "pessoa" ? n.h / 2 : 12} fill={fundo} stroke={ehDestaque ? "#12292B" : borda} strokeWidth={ehDestaque ? 3 : 1.2} />
              <text x={n.x + n.w / 2} y={n.y + n.h / 2 + (n.sub ? -4 : 5)} textAnchor="middle" fontSize="15" fontWeight="700" fill={texto}>{n.rotulo}</text>
              {n.sub && <text x={n.x + n.w / 2} y={n.y + n.h / 2 + 14} textAnchor="middle" fontSize="12.5" fill={sub}>{n.sub}</text>}
            </g>
          );
        })}
      </svg>
    </div>
    </div>
  );
}
