import { CORES_DAS_MATERIAS } from "../lib/api";

/*
 * Fluxograma do sistema. Sem destaque, mostra tudo. Com destaque (o código de uma
 * matéria), a matéria e as ligações dela ficam coloridas e o resto fica em cinza.
 */

type No = { id: string; rotulo: string; sub?: string; x: number; y: number; w: number; h: number; tipo: "pessoa" | "tela" | "materia" };
type Ligacao = { de: string; para: string; rotulo?: string; tracejada?: boolean };

const NOS: No[] = [
  { id: "cidadao", rotulo: "Cidadão", x: 16, y: 196, w: 112, h: 52, tipo: "pessoa" },
  { id: "atendimento", rotulo: "Atendimento", sub: "entende o pedido", x: 168, y: 186, w: 156, h: 72, tipo: "tela" },
  { id: "duvida", rotulo: "Tirar uma dúvida", x: 380, y: 40, w: 172, h: 52, tipo: "tela" },
  { id: "direitos", rotulo: "Tenho algum direito?", x: 380, y: 144, w: 172, h: 52, tipo: "tela" },
  { id: "luz", rotulo: "Minha conta de luz", x: 380, y: 248, w: 172, h: 52, tipo: "tela" },
  { id: "golpe", rotulo: "Isso é golpe?", sub: "regras do sistema", x: 380, y: 352, w: 172, h: 60, tipo: "tela" },
  { id: "PCP", rotulo: "PCP", sub: "busca por pontos", x: 716, y: 20, w: 168, h: 56, tipo: "materia" },
  { id: "DSA", rotulo: "DSA", sub: "lista encadeada", x: 716, y: 104, w: 168, h: 56, tipo: "materia" },
  { id: "SERS", rotulo: "SERS", sub: "contas de energia", x: 716, y: 188, w: 168, h: 56, tipo: "materia" },
  { id: "PAI", rotulo: "PAI", sub: "agente com IA", x: 716, y: 272, w: 168, h: 56, tipo: "materia" },
  { id: "MLAM", rotulo: "MLAM", sub: "dados reais", x: 716, y: 356, w: 168, h: 56, tipo: "materia" },
  { id: "laboratorio", rotulo: "Laboratório", sub: "simulação", x: 940, y: 356, w: 128, h: 56, tipo: "tela" },
];

const LIGACOES: Ligacao[] = [
  { de: "cidadao", para: "atendimento" },
  { de: "atendimento", para: "duvida" },
  { de: "atendimento", para: "direitos" },
  { de: "atendimento", para: "luz" },
  { de: "atendimento", para: "golpe" },
  { de: "duvida", para: "PCP", rotulo: "acha a orientação" },
  { de: "duvida", para: "DSA", rotulo: "para quem é" },
  { de: "duvida", para: "PAI", rotulo: "explica (com IA)", tracejada: true },
  { de: "direitos", para: "DSA", rotulo: "catálogo" },
  { de: "luz", para: "SERS", rotulo: "desconto" },
  { de: "MLAM", para: "laboratorio", rotulo: "adesão" },
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
    <div className="overflow-x-auto rounded-xl border border-linha bg-superficie p-3">
      <svg viewBox="0 0 1080 430" className="min-w-[760px]" role="img"
        aria-label={destaque ? `Fluxograma do sistema com a matéria ${destaque} em destaque` : "Fluxograma do sistema"}>
        <defs>
          {["normal", "foco", "cinza"].map((tipo) => (
            <marker key={tipo} id={`seta-${tipo}`} viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill={tipo === "foco" ? corDestaque ?? "#556A6A" : tipo === "cinza" ? CINZA.linha : "#8FA19D"} />
            </marker>
          ))}
        </defs>

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
  );
}
