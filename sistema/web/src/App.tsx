import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Casca from "./componentes/Casca";
import Sistema from "./componentes/Celular";
import { api, type EstadoIA } from "./lib/api";
import ComoFunciona from "./paginas/ComoFunciona";
import AppCelular from "./paginas/AppCelular";
import Configuracoes from "./paginas/Configuracoes";
import Documentacao from "./paginas/Documentacao";
import AvaliacaoUsuarios from "./paginas/AvaliacaoUsuarios";
import Avaliar from "./paginas/Avaliar";
import AvaliarTeste from "./paginas/AvaliarTeste";
import Materia from "./paginas/Materia";

type Contexto = {
  modoBanca: boolean;
  alternarModoBanca: () => void;
  ia: EstadoIA | null;
  recarregarIA: () => void;
};

const ContextoApp = createContext<Contexto>({ modoBanca: true, alternarModoBanca: () => {}, ia: null, recarregarIA: () => {} });
export const useApp = () => useContext(ContextoApp);

function lerModoBanca(): boolean {
  try {
    return localStorage.getItem("modo-banca") !== "desligado";
  } catch {
    return true;
  }
}

/** A plataforma dos professores: barra lateral e as páginas. */
function Plataforma({ ia }: { ia: EstadoIA | null }) {
  return (
    <Casca>
      <Routes>
        <Route path="/" element={<ComoFunciona />} />
        <Route path="/sistema" element={<Sistema />} />
        <Route path="/avaliacao" element={<AvaliacaoUsuarios />} />
        <Route path="/avaliar" element={<Avaliar />} />
        <Route path="/avaliar/teste" element={<AvaliarTeste />} />
        <Route path="/materias/:cod" element={<Materia />} />
        <Route path="/documentacao" element={<Documentacao />} />
        {/* no servidor público a IA é fixa: a tela de configuração só existe no computador da equipe */}
        <Route path="/configuracoes" element={ia?.modo_publico ? <Navigate to="/documentacao" replace /> : <Configuracoes />} />
        {/* endereços das versões anteriores */}
        <Route path="/caso" element={<Navigate to="/" replace />} />
        <Route path="/como-funciona" element={<Navigate to="/" replace />} />
        <Route path="/materias" element={<Navigate to="/" replace />} />
        <Route path="/laboratorio" element={<Navigate to="/avaliacao" replace />} />
        <Route path="/sociedade" element={<Navigate to="/avaliacao" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Casca>
  );
}

export default function App() {
  const [modoBanca, setModoBanca] = useState(lerModoBanca);
  const [ia, setIA] = useState<EstadoIA | null>(null);

  const recarregarIA = useCallback(() => {
    api.ia().then(setIA).catch(() => setIA(null));
  }, []);
  useEffect(recarregarIA, [recarregarIA]);

  const alternarModoBanca = () => {
    setModoBanca((atual) => {
      try {
        localStorage.setItem("modo-banca", atual ? "desligado" : "ligado");
      } catch {
        /* sem armazenamento, vale só nesta visita */
      }
      return !atual;
    });
  };

  return (
    <ContextoApp.Provider value={{ modoBanca, alternarModoBanca, ia, recarregarIA }}>
      <Routes>
        {/* só o app, em tela cheia: o endereço para abrir direto pelo celular */}
        <Route path="/app" element={<AppCelular />} />
        <Route path="*" element={<Plataforma ia={ia} />} />
      </Routes>
    </ContextoApp.Provider>
  );
}
