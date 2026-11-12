import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";

import Casca from "./componentes/Casca";
import { api, type EstadoIA } from "./lib/api";
import AntesDeSair from "./paginas/AntesDeSair";
import Atendimento from "./paginas/Atendimento";
import ComoFunciona from "./paginas/ComoFunciona";
import Configuracoes from "./paginas/Configuracoes";
import Laboratorio from "./paginas/Laboratorio";
import LinhasAgora from "./paginas/LinhasAgora";
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
          <Route path="/" element={<AntesDeSair />} />
          <Route path="/linhas" element={<LinhasAgora />} />
          <Route path="/pergunte" element={<Atendimento />} />
          <Route path="/como-funciona" element={<ComoFunciona />} />
          <Route path="/laboratorio" element={<Laboratorio />} />
          <Route path="/materias" element={<PainelEquipe />} />
          <Route path="/materias/:cod" element={<Materia />} />
          <Route path="/configuracoes" element={<Configuracoes />} />
          <Route path="*" element={<AntesDeSair />} />
        </Routes>
      </Casca>
    </ContextoApp.Provider>
  );
}
