import { Home, ShieldCheck, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { SeloLinha } from "../componentes/Linha";
import { mobilidade, type EstacaoEscolha, type LinhaInfo } from "../lib/api";

/*
 * Perfil (versão sem banco): o que fica só neste aparelho. As rotinas e os avisos antes de sair
 * entram quando o banco for ligado. Nada aqui é enviado ao servidor.
 */

const MINHAS_LINHAS = "dt-minhas-linhas";
const CASA = "dt-casa";
const CHAVES_ANTIGAS = ["auxilia-casa", "plano-b-casa", "plano-b-trajeto", "plano-b-trajetos", "auxilia-vista", "auxilia-layout", "plano-b-vista"];

function ler<T>(chave: string, padrao: T): T {
  try {
    const v = JSON.parse(localStorage.getItem(chave) ?? "null");
    return v ?? padrao;
  } catch {
    return padrao;
  }
}
function gravar(chave: string, valor: unknown) {
  try {
    localStorage.setItem(chave, JSON.stringify(valor));
  } catch {
    /* sem armazenamento, vale só nesta visita */
  }
}

export default function Perfil() {
  const [linhas, setLinhas] = useState<LinhaInfo[]>([]);
  const [estacoes, setEstacoes] = useState<EstacaoEscolha[]>([]);
  const [minhas, setMinhas] = useState<string[]>(() => ler<string[]>(MINHAS_LINHAS, []));
  const [casa, setCasa] = useState<string>(() => ler<string>(CASA, "") || (typeof localStorage !== "undefined" ? localStorage.getItem("auxilia-casa") ?? "" : ""));
  const [apagado, setApagado] = useState(false);

  useEffect(() => {
    mobilidade.estacoes().then((r) => { setLinhas(r.linhas.filter((l) => l.numero !== "7")); setEstacoes(r.estacoes); }).catch(() => {});
  }, []);

  const alternar = (n: string) => {
    const novo = minhas.includes(n) ? minhas.filter((x) => x !== n) : [...minhas, n];
    setMinhas(novo);
    gravar(MINHAS_LINHAS, novo);
  };
  const nomeCasa = estacoes.find((e) => e.id === casa)?.nome;
  const apagarTudo = () => {
    try {
      [MINHAS_LINHAS, CASA, "dt-device-id", ...CHAVES_ANTIGAS].forEach((c) => localStorage.removeItem(c));
    } catch {
      /* nada a apagar */
    }
    setMinhas([]);
    setCasa("");
    setApagado(true);
  };

  return (
    <div className="h-full space-y-4 overflow-y-auto px-4 py-4">
      <section className="space-y-2.5 rounded-2xl border border-linha bg-superficie p-4">
        <h3 className="text-[16px] font-extrabold">Minhas linhas</h3>
        <p className="text-[13px] text-apagado">O feed mostra primeiro os relatos dessas linhas (use o filtro “Minhas linhas” na Home).</p>
        <div className="flex flex-wrap gap-2" role="group" aria-label="Minhas linhas">
          {linhas.map((l) => (
            <button key={l.numero} type="button" aria-pressed={minhas.includes(l.numero)} aria-label={`Linha ${l.numero}-${l.nome}`} onClick={() => alternar(l.numero)}
              className={`rounded-xl p-0.5 ${minhas.includes(l.numero) ? "ring-2 ring-tinta ring-offset-2" : "opacity-70 hover:opacity-100"}`}>
              <SeloLinha numero={l.numero} cor={l.cor} />
            </button>
          ))}
        </div>
      </section>

      <section className="space-y-2 rounded-2xl border border-linha bg-superficie p-4">
        <h3 className="flex items-center gap-2 text-[16px] font-extrabold"><Home className="size-4 text-marca" aria-hidden />Estação perto de casa</h3>
        <p className="text-[14px]">{nomeCasa ? <><b>{nomeCasa}</b>. A Lia usa para não perguntar de novo de onde você sai.</> : "Ainda não definida. Diga à Lia de onde você sai e ela guarda aqui."}</p>
      </section>

      <section className="space-y-1 rounded-2xl border border-dashed border-linha bg-superficie p-4">
        <h3 className="text-[16px] font-extrabold">Rotinas e avisos antes de sair</h3>
        <p className="text-[13px] text-apagado">Em breve: conte sua rotina uma vez e receba o aviso “hoje saia mais cedo” antes do horário. Isso depende do banco de dados, que ainda não foi ligado.</p>
      </section>

      <section className="space-y-2 rounded-2xl border border-linha bg-ok-suave/50 p-4">
        <h3 className="flex items-center gap-2 text-[16px] font-extrabold"><ShieldCheck className="size-4 text-ok" aria-hidden />Sua privacidade</h3>
        <ul className="list-disc space-y-1 pl-5 text-[13px]">
          <li>Não pedimos nome, CPF, telefone, endereço nem localização.</li>
          <li>O que você escreve para a Lia não fica guardado.</li>
          <li>Os relatos do feed usam só campos prontos, sem texto livre e sem foto.</li>
          <li>Neste aparelho ficam apenas as suas linhas, a estação de casa e um código aleatório do aparelho.</li>
        </ul>
        <button type="button" onClick={apagarTudo} className="inline-flex h-10 items-center gap-2 rounded-full px-4 text-[13px] font-bold text-erro ring-1 ring-erro/50 ring-inset hover:bg-erro-suave">
          <Trash2 className="size-4" aria-hidden />Apagar os dados deste aparelho
        </button>
        {apagado && <p role="status" className="text-[13px] font-semibold text-ok">Pronto: os dados deste aparelho foram apagados.</p>}
      </section>
    </div>
  );
}
