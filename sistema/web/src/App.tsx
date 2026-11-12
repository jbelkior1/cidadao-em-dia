import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Casca from "./componentes/Casca";
import Sistema from "./componentes/Celular";
import { api, type EstadoIA } from "./lib/api";
import ComoFunciona from "./paginas/ComoFunciona";
import Configuracoes from "./paginas/Configuracoes";
import Laboratorio from "./paginas/Laboratorio";
import Materia from "./paginas/Materia";
import PainelEquipe from "./paginas/Painel";

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
      <Casca>
        <Routes>
          <Route path="/" element={<Sistema />} />
          <Route path="/sociedade" element={<Laboratorio />} />
          <Route path="/caso" element={<ComoFunciona />} />
          <Route path="/materias" element={<PainelEquipe />} />
          <Route path="/materias/:cod" element={<Materia />} />
          <Route path="/configuracoes" element={<Configuracoes />} />
          {/* endereços da versão anterior */}
          <Route path="/laboratorio" element={<Navigate to="/sociedade" replace />} />
          <Route path="/como-funciona" element={<Navigate to="/caso" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Casca>
    </ContextoApp.Provider>
  );
}
