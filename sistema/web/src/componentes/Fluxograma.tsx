import { CORES_DAS_MATERIAS } from "../lib/api";

/*
 * Fluxograma do sistema. Sem destaque, mostra tudo. Com destaque (o código de uma
 * matéria), a matéria e as ligações dela ficam coloridas e o resto fica em cinza.
 */

type No = { id: string; rotulo: string; sub?: string; x: number; y: number; w: number; h: number; tipo: "pessoa" | "tela" | "materia" };
type Ligacao = { de: string; para: string; rotulo?: string; tracejada?: boolean };

const NOS: No[] = [
  { id: "cidadao", rotulo: "Passageiro", x: 16, y: 200, w: 120, h: 52, tipo: "pessoa" },
  { id: "antes", rotulo: "Antes de sair", sub: "pode ir, mais cedo ou Plano B", x: 170, y: 64, w: 200, h: 64, tipo: "tela" },
  { id: "linhas", rotulo: "Trem e metrô agora", x: 170, y: 200, w: 200, h: 52, tipo: "tela" },
  { id: "pergunte", rotulo: "Pergunte", sub: "orientação oficial", x: 170, y: 330, w: 200, h: 64, tipo: "tela" },
  { id: "fontes", rotulo: "Fontes ao vivo", sub: "operadoras, INMET, GeoSampa", x: 430, y: 190, w: 200, h: 72, tipo: "tela" },
  { id: "CS", rotulo: "CS", sub: "decisão do dia", x: 730, y: 12, w: 168, h: 46, tipo: "materia" },
  { id: "SERS", rotulo: "SERS", sub: "energia da viagem", x: 730, y: 64, w: 168, h: 46, tipo: "materia" },
  { id: "MLAM", rotulo: "MLAM", sub: "segurança (SSP-SP)", x: 730, y: 116, w: 168, h: 46, tipo: "materia" },
  { id: "MMC", rotulo: "MMC", sub: "ônibus de apoio", x: 730, y: 168, w: 168, h: 46, tipo: "materia" },
  { id: "COA", rotulo: "COA", sub: "sensor de água", x: 730, y: 230, w: 168, h: 46, tipo: "materia" },
  { id: "PCP", rotulo: "PCP", sub: "busca por pontos", x: 730, y: 296, w: 168, h: 46, tipo: "materia" },
  { id: "DSA", rotulo: "DSA", sub: "lista encadeada", x: 730, y: 348, w: 168, h: 46, tipo: "materia" },
  { id: "PAI", rotulo: "PAI", sub: "agente com IA", x: 730, y: 400, w: 168, h: 46, tipo: "materia" },
  { id: "wokwi", rotulo: "Wokwi", sub: "fora do app", x: 946, y: 230, w: 120, h: 46, tipo: "tela" },
];

const LIGACOES: Ligacao[] = [
  { de: "cidadao", para: "antes" },
  { de: "cidadao", para: "linhas" },
  { de: "cidadao", para: "pergunte" },
  { de: "antes", para: "fontes" },
  { de: "linhas", para: "fontes" },
  { de: "antes", para: "CS", rotulo: "4 entradas" },
  { de: "antes", para: "SERS", rotulo: "km da rota" },
  { de: "antes", para: "MLAM", rotulo: "estações" },
  { de: "antes", para: "MMC", rotulo: "linha parada", tracejada: true },
  { de: "fontes", para: "COA", rotulo: "alagamento", tracejada: true },
  { de: "COA", para: "wokwi" },
  { de: "pergunte", para: "PCP", rotulo: "acha a orientação" },
  { de: "pergunte", para: "DSA", rotulo: "canal do serviço" },
  { de: "pergunte", para: "PAI", rotulo: "com IA", tracejada: true },
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
      <svg viewBox="0 0 1080 456" className="min-w-[760px]" role="img"
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
