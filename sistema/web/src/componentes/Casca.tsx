import { FlaskConical, Info, LayoutDashboard, Menu, MessageCircle, SlidersHorizontal, X, type LucideIcon } from "lucide-react";
import { createContext, useContext, useState, type ReactNode } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { useApp } from "../App";
import { CORES_DAS_MATERIAS, MATERIAS_DO_SISTEMA } from "../lib/api";

type Item = { rotulo: string; para: string; icone?: LucideIcon; cor?: string };
const GRUPOS: { titulo: string; itens: Item[] }[] = [
  { titulo: "O sistema", itens: [{ rotulo: "Dá Tempo?", para: "/", icone: MessageCircle }] },
  { titulo: "A sociedade", itens: [{ rotulo: "Simulação da sociedade", para: "/sociedade", icone: FlaskConical }] },
  {
    titulo: "As matérias",
    itens: [
      { rotulo: "Case norteador", para: "/caso", icone: Info },
      { rotulo: "Painel da equipe", para: "/materias", icone: LayoutDashboard },
      ...MATERIAS_DO_SISTEMA.map((m) => ({ rotulo: `${m.cod} · ${m.curto}`, para: `/materias/${m.cod.toLowerCase()}`, cor: CORES_DAS_MATERIAS[m.cod] })),
    ],
  },
  { titulo: "Configurações", itens: [{ rotulo: "Configurações de IA", para: "/configuracoes", icone: SlidersHorizontal }] },
];
const TITULOS: Record<string, string> = {
  "/": "O sistema · Dá Tempo?",
  "/sociedade": "A sociedade usando o sistema",
  "/caso": "Case norteador",
  "/materias": "Painel da equipe",
  "/configuracoes": "Configurações de IA",
};

/** Rotas que aparecem dentro do celular. */
export const ROTAS_DO_APP = ["/"];

const ContextoMenu = createContext<{ abrirMenu: () => void }>({ abrirMenu: () => {} });
/** O app abre a gaveta do sistema pelo botão da barra dele (no celular de verdade). */
export const useMenu = () => useContext(ContextoMenu);

function tituloDa(caminho: string): string {
  if (TITULOS[caminho]) return TITULOS[caminho];
  const cod = caminho.match(/^\/materias\/([a-z]+)/)?.[1]?.toUpperCase();
  return cod ? `Matéria ${cod}` : "Dá Tempo?";
}

function Marca() {
  return (
    <div className="flex h-16 shrink-0 items-center gap-3 border-b border-linha px-5">
      <span className="flex size-9 items-center justify-center rounded-xl bg-marca text-white">
        <span className="text-[17px] font-black tracking-tight" aria-hidden>D</span>
      </span>
      <div className="min-w-0 leading-tight">
        <p className="truncate text-[15px] font-bold">Dá Tempo?</p>
        <p className="truncate text-xs text-apagado">GS 2026.2 · FIAP</p>
      </div>
    </div>
  );
}

function Navegacao({ aoNavegar }: { aoNavegar?: () => void }) {
  return (
    <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-5" aria-label="Principal">
      {GRUPOS.map((grupo) => (
        <div key={grupo.titulo} className="space-y-1">
          <p className="px-3 pb-1 text-[11px] font-semibold tracking-wider text-apagado uppercase">{grupo.titulo}</p>
          {grupo.itens.map((item) => (
            <NavLink
              key={item.para}
              to={item.para}
              end
              onClick={aoNavegar}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-2.5 text-[15px] font-medium transition-colors ${
                  isActive ? "bg-marca-suave text-marca-forte" : "text-tinta/80 hover:bg-fundo hover:text-tinta"
                }`
              }
            >
              {item.icone ? (
                <item.icone className="size-[18px] shrink-0" aria-hidden />
              ) : (
                <span className="flex size-[18px] shrink-0 items-center justify-center" aria-hidden>
                  <span className="size-2.5 rounded-full" style={{ background: item.cor }} />
                </span>
              )}
              <span className="truncate">{item.rotulo}</span>
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}

function ModoBanca() {
  const { modoBanca, alternarModoBanca } = useApp();
  return (
    <div className="shrink-0 border-t border-linha p-4">
      <button
        type="button"
        role="switch"
        aria-checked={modoBanca}
        onClick={alternarModoBanca}
        className="flex w-full items-center justify-between gap-3 rounded-xl px-1 py-1 text-left"
      >
        <span>
          <span className="block text-sm font-semibold">Modo banca</span>
          <span className="block text-xs text-apagado">Mostra qual matéria fez cada parte</span>
        </span>
        <span className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${modoBanca ? "bg-marca" : "bg-linha"}`}>
          <span className={`absolute top-0.5 size-5 rounded-full bg-white shadow transition-all ${modoBanca ? "left-[22px]" : "left-0.5"}`} />
        </span>
      </button>
    </div>
  );
}

export default function Casca({ children }: { children: ReactNode }) {
  const [menuAberto, setMenuAberto] = useState(false);
  const { ia } = useApp();
  const { pathname } = useLocation();
  // qualquer endereço desconhecido também abre o app (é a rota "*")
  const ehApp = ROTAS_DO_APP.includes(pathname) || (!(pathname in TITULOS) && !pathname.startsWith("/materias/"));
  const soNoComputador = ehApp ? "hidden lg:flex" : "flex";

  return (
    <ContextoMenu.Provider value={{ abrirMenu: () => setMenuAberto(true) }}>
    <div className="flex h-full bg-fundo">
      {/* Barra lateral fixa no computador */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-linha bg-superficie lg:flex">
        <Marca />
        <Navegacao />
        <ModoBanca />
      </aside>

      {/* Gaveta no celular */}
      {menuAberto && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button type="button" aria-label="Fechar o menu" className="absolute inset-0 bg-tinta/40" onClick={() => setMenuAberto(false)} />
          <aside className="entrar absolute inset-y-0 left-0 flex w-72 max-w-[85%] flex-col bg-superficie shadow-xl">
            <Marca />
            <Navegacao aoNavegar={() => setMenuAberto(false)} />
            <ModoBanca />
          </aside>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <header className={`${soNoComputador} h-14 shrink-0 items-center gap-3 border-b border-linha bg-superficie px-4 lg:px-6`}>
          <button
            type="button"
            className="-ml-1 rounded-lg p-2 text-apagado hover:bg-fundo lg:hidden"
            aria-label={menuAberto ? "Fechar o menu" : "Abrir o menu"}
            onClick={() => setMenuAberto((v) => !v)}
          >
            {menuAberto ? <X className="size-5" /> : <Menu className="size-5" />}
          </button>
          <h1 className="truncate text-[17px] font-semibold">{tituloDa(pathname)}</h1>
          <div className="ml-auto flex items-center gap-2">
            <span
              className={`hidden rounded-full px-2.5 py-0.5 text-xs font-medium sm:inline-block ${
                ia?.ligada ? "bg-marca-suave text-marca-forte" : "bg-fundo text-apagado ring-1 ring-linha ring-inset"
              }`}
            >
              {ia?.ligada ? `IA: ${ia.provedores[ia.config.provedor]?.nome ?? ia.config.provedor}` : "IA desligada: respondendo por regras"}
            </span>
          </div>
        </header>
        <div className={`${ehApp ? "hidden lg:block" : ""} shrink-0 border-b border-linha bg-marca-suave px-4 py-1.5 text-center text-[13px] font-medium text-marca-forte`}>
          Projeto educacional da FIAP. Usa dados públicos; não substitui os avisos oficiais das operadoras.
        </div>
        <main className="relative min-h-0 flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
    </ContextoMenu.Provider>
  );
}
