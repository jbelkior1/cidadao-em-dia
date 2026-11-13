import { BellRing, Check, Home, ShieldCheck, Trash2, UserRound } from "lucide-react";
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
    <div className="h-full overflow-y-auto bg-superficie">
      <div className="mx-auto max-w-2xl space-y-7 px-4 pt-2 pb-8">
        <section className="flex items-center gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="text-[30px] leading-tight font-bold tracking-tight">Passageiro</h3>
            <p className="mt-1 text-[14px] text-apagado">Sem conta: o que você escolhe aqui fica só neste aparelho.</p>
          </div>
          <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-cinza" aria-hidden><UserRound className="size-8 text-apagado" /></span>
        </section>

        <section className="grid grid-cols-2 gap-2.5">
          <div className="rounded-2xl bg-cinza p-4">
            <p className="text-[28px] leading-none font-bold tabular-nums">{minhas.length}</p>
            <p className="mt-1.5 text-[13px] font-semibold text-apagado">{minhas.length === 1 ? "linha marcada" : "linhas marcadas"}</p>
          </div>
          <div className="rounded-2xl bg-cinza p-4">
            <Home className="size-7" aria-hidden />
            <p className="mt-1.5 truncate text-[13px] font-semibold text-apagado">{nomeCasa ?? "Casa não definida"}</p>
          </div>
        </section>

        <section className="space-y-3">
          <div>
            <h3 className="text-[22px] font-bold tracking-tight">Minhas linhas</h3>
            <p className="text-[14px] text-apagado">Use o filtro “Minhas linhas” na Home para ver só os relatos delas.</p>
          </div>
          <div className="flex flex-wrap gap-2.5" role="group" aria-label="Minhas linhas">
            {linhas.map((l) => (
              <button key={l.numero} type="button" aria-pressed={minhas.includes(l.numero)} aria-label={`Linha ${l.numero}-${l.nome}`} onClick={() => alternar(l.numero)}
                className={`relative rounded-[14px] p-1 ${minhas.includes(l.numero) ? "ring-2 ring-tinta" : "opacity-60 hover:opacity-100"}`}>
                <SeloLinha numero={l.numero} cor={l.cor} tamanho="lg" />
                {minhas.includes(l.numero) && (
                  <span className="absolute -top-1.5 -right-1.5 flex size-5 items-center justify-center rounded-full bg-tinta text-white"><Check className="size-3.5" strokeWidth={3} aria-hidden /></span>
                )}
              </button>
            ))}
          </div>
        </section>

        <section>
          <h3 className="mb-1 text-[22px] font-bold tracking-tight">Ajustes</h3>
          <ul>
            <li className="flex items-center gap-4 border-b border-linha py-4">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-cinza"><Home className="size-5" aria-hidden /></span>
              <span className="min-w-0 flex-1">
                <span className="block text-[16px] font-bold">Estação perto de casa</span>
                <span className="block text-[14px] text-apagado">{nomeCasa ? `${nomeCasa}. A Lia usa para não perguntar de novo.` : "Diga à Lia de onde você sai e ela guarda aqui."}</span>
              </span>
            </li>
            <li className="flex items-center gap-4 border-b border-linha py-4">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-cinza"><BellRing className="size-5" aria-hidden /></span>
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-2 text-[16px] font-bold">Rotinas e aviso antes de sair <span className="rounded-full bg-cinza px-2 py-0.5 text-[11px] font-bold text-apagado">em breve</span></span>
                <span className="block text-[14px] text-apagado">Conte sua rotina uma vez e receba “hoje saia mais cedo”. Depende do banco de dados, ainda não ligado.</span>
              </span>
            </li>
          </ul>
        </section>

        <section className="space-y-3 rounded-2xl bg-cinza p-4">
          <h3 className="flex items-center gap-2 text-[18px] font-bold"><ShieldCheck className="size-5 text-ok" aria-hidden />Sua privacidade</h3>
          <ul className="space-y-2 text-[14px]">
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />Não pedimos nome, CPF, telefone, endereço nem localização.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />O que você escreve para a Lia não fica guardado.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />Os relatos usam só campos prontos, sem texto livre e sem foto.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />Neste aparelho ficam só as suas linhas, a estação de casa e um código aleatório.</li>
          </ul>
          <button type="button" onClick={apagarTudo} className="inline-flex h-11 items-center gap-2 rounded-full bg-superficie px-5 text-[14px] font-bold text-erro hover:bg-erro-suave">
            <Trash2 className="size-4" aria-hidden />Apagar os dados deste aparelho
          </button>
          {apagado && <p role="status" className="text-[14px] font-bold text-ok">Pronto: os dados deste aparelho foram apagados.</p>}
        </section>
      </div>
    </div>
  );
}
