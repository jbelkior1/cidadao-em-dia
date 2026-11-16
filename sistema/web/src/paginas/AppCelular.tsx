import { useEffect } from "react";

import AppAbas from "../componentes/AppAbas";
import { ProvedorConversa } from "../componentes/conversa";

/*
 * Rota /app: só o app Dá Tempo?, em tela cheia, sem a barra da plataforma. É o endereço para
 * abrir direto pelo celular (e para "adicionar à tela inicial"). Em tela larga, o app fica
 * centralizado com a largura de um celular.
 */
export default function AppCelular() {
  useEffect(() => {
    const anterior = document.title;
    document.title = "Dá Tempo?";
    return () => { document.title = anterior; };
  }, []);

  return (
    <ProvedorConversa>
      <div className="fixed inset-0 flex justify-center bg-fundo">
        <div className="h-full w-full max-w-[460px] bg-superficie sm:border-x sm:border-linha">
          <AppAbas />
        </div>
      </div>
    </ProvedorConversa>
  );
}
