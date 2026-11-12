import { useEffect, useState, type FormEvent } from "react";

import { useApp } from "../App";
import { api, type TesteIA } from "../lib/api";

const CAMPO = "w-full rounded-xl border border-linha bg-superficie px-3.5 py-2.5 text-[16px] focus:border-marca focus:outline-none";

export default function Configuracoes() {
  const { ia, recarregarIA } = useApp();
  const [provedor, setProvedor] = useState("nenhum");
  const [baseUrl, setBaseUrl] = useState("");
  const [modelo, setModelo] = useState("");
  const [chave, setChave] = useState("");
  const [limite, setLimite] = useState(100);
  const [aviso, setAviso] = useState<{ tom: "ok" | "erro"; texto: string } | null>(null);
  const [teste, setTeste] = useState<TesteIA | null>(null);
  const [ocupado, setOcupado] = useState(false);

  // Preenche o formulário com o que está salvo (a chave nunca vem do servidor).
  useEffect(() => {
    if (!ia) return;
    setProvedor(ia.config.provedor);
    setBaseUrl(ia.config.base_url);
    setModelo(ia.config.modelo);
    setLimite(ia.config.limite_diario);
  }, [ia]);

  const escolherProvedor = (novo: string) => {
    setProvedor(novo);
    setTeste(null);
    const p = ia?.provedores[novo];
    setBaseUrl(p?.base_url ?? "");
    setModelo(p?.modelo ?? "");
  };

  const salvar = async (evento?: FormEvent) => {
    evento?.preventDefault();
    setOcupado(true);
    setAviso(null);
    try {
      await api.salvarIA({ provedor, base_url: baseUrl, modelo, limite_diario: limite, ...(chave ? { chave } : {}) });
      setChave("");
      recarregarIA();
      setAviso({ tom: "ok", texto: "Configuração salva neste computador." });
      return true;
    } catch (e) {
      setAviso({ tom: "erro", texto: e instanceof Error ? e.message : "Não consegui salvar." });
      return false;
    } finally {
      setOcupado(false);
    }
  };

  const testar = async () => {
    if (!(await salvar())) return;
    setOcupado(true);
    setTeste(null);
    try {
      setTeste(await api.testarIA());
    } catch (e) {
      setTeste({ ok: false, erro: e instanceof Error ? e.message : "Não consegui testar.", modelos: [] });
    } finally {
      setOcupado(false);
      recarregarIA();
    }
  };

  const apagarChave = async () => {
    setOcupado(true);
    try {
      await api.salvarIA({ apagar_chave: true });
      recarregarIA();
      setAviso({ tom: "ok", texto: "Chave apagada deste computador." });
    } finally {
      setOcupado(false);
    }
  };

  const info = ia?.provedores[provedor];
  const precisaChave = info?.precisa_chave ?? false;

  return (
    <div className="mx-auto w-full max-w-2xl space-y-8 px-4 py-8 lg:px-8">
      <header className="space-y-2">
        <h2 className="text-2xl font-bold">Modelo de inteligência artificial</h2>
        <p className="text-[17px] text-apagado">
          O sistema funciona sem IA, respondendo por regras. Com um modelo ligado, ele também explica as orientações em linguagem mais simples.
          Só o texto da base vai para o modelo, nunca o que a pessoa escreveu.
        </p>
      </header>

      <form onSubmit={salvar} className="space-y-5 rounded-xl border border-linha bg-superficie p-5">
        <div className="space-y-1.5">
          <label htmlFor="provedor" className="block text-[15px] font-semibold">
            Provedor
          </label>
          <select id="provedor" value={provedor} onChange={(e) => escolherProvedor(e.target.value)} className={CAMPO}>
            <option value="nenhum">Nenhum (só regras)</option>
            {ia &&
              Object.entries(ia.provedores).map(([chaveDoProvedor, p]) => (
                <option key={chaveDoProvedor} value={chaveDoProvedor}>
                  {p.nome}
                </option>
              ))}
          </select>
          {info && <p className="text-sm text-apagado">{info.nota}</p>}
        </div>

        {provedor !== "nenhum" && (
          <>
            <div className="space-y-1.5">
              <label htmlFor="endereco" className="block text-[15px] font-semibold">
                Endereço da API
              </label>
              <input id="endereco" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} className={CAMPO} placeholder="https://..." autoComplete="off" />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="modelo" className="block text-[15px] font-semibold">
                Modelo
              </label>
              <input id="modelo" list="modelos" value={modelo} onChange={(e) => setModelo(e.target.value)} className={CAMPO} autoComplete="off" />
              <datalist id="modelos">
                {teste?.modelos.map((m) => (
                  <option key={m} value={m} />
                ))}
              </datalist>
              <p className="text-sm text-apagado">Depois de testar a conexão, o campo sugere os modelos que o serviço oferece.</p>
            </div>

            {precisaChave && (
              <div className="space-y-1.5">
                <label htmlFor="chave" className="block text-[15px] font-semibold">
                  Chave
                </label>
                <input
                  id="chave"
                  type="password"
                  value={chave}
                  onChange={(e) => setChave(e.target.value)}
                  className={CAMPO}
                  autoComplete="off"
                  placeholder={ia?.config.tem_chave ? `Guardada (termina em ${ia.config.final_da_chave || "…"}). Deixe em branco para manter.` : "Cole a chave aqui"}
                />
                <p className="text-sm text-apagado">
                  A chave fica em um arquivo deste computador que não vai para o GitHub. A tela nunca recebe a chave de volta.
                </p>
                {ia?.config.tem_chave && (
                  <button type="button" onClick={apagarChave} disabled={ocupado} className="text-sm font-semibold text-erro underline disabled:opacity-50">
                    Apagar a chave guardada
                  </button>
                )}
              </div>
            )}

            <div className="space-y-1.5">
              <label htmlFor="limite" className="block text-[15px] font-semibold">
                Limite de chamadas por dia
              </label>
              <input
                id="limite"
                type="number"
                min={0}
                max={10000}
                value={limite}
                onChange={(e) => setLimite(Number(e.target.value) || 0)}
                className={`${CAMPO} max-w-40`}
              />
              <p className="text-sm text-apagado">Ao chegar no limite, o sistema para de chamar o modelo e continua respondendo por regras. Zero tira o limite.</p>
            </div>
          </>
        )}

        <div className="flex flex-wrap gap-2 pt-1">
          <button type="submit" disabled={ocupado} className="rounded-full bg-marca px-5 py-2.5 text-[15px] font-semibold text-white hover:bg-marca-forte disabled:opacity-50">
            Salvar
          </button>
          {provedor !== "nenhum" && (
            <button
              type="button"
              onClick={testar}
              disabled={ocupado}
              className="rounded-full px-5 py-2.5 text-[15px] font-semibold text-marca-forte ring-1 ring-marca/40 ring-inset hover:bg-marca-suave disabled:opacity-50"
            >
              Salvar e testar a conexão
            </button>
          )}
        </div>

        {aviso && (
          <p role="status" className={`rounded-xl px-4 py-3 text-[15px] ${aviso.tom === "ok" ? "bg-ok-suave text-ok" : "bg-erro-suave text-erro"}`}>
            {aviso.texto}
          </p>
        )}
        {teste && (
          <p role="status" className={`rounded-xl px-4 py-3 text-[15px] ${teste.ok ? "bg-ok-suave text-ok" : "bg-erro-suave text-erro"}`}>
            {teste.ok
              ? `Conexão funcionando. O modelo respondeu em ${teste.ms} ms e o serviço oferece ${teste.modelos.length} modelos.`
              : `Não funcionou: ${teste.erro}`}
          </p>
        )}
      </form>

      <section className="space-y-3 rounded-xl border border-linha bg-superficie p-5">
        <h3 className="text-lg font-bold">Uso de hoje</h3>
        <dl className="grid grid-cols-3 gap-3 text-center">
          {[
            ["Chamadas", ia?.uso.chamadas ?? 0],
            ["Tokens enviados", ia?.uso.tokens_entrada ?? 0],
            ["Tokens recebidos", ia?.uso.tokens_saida ?? 0],
          ].map(([rotulo, valor]) => (
            <div key={rotulo} className="rounded-xl bg-fundo px-2 py-3">
              <dd className="text-2xl font-bold tabular-nums">{valor}</dd>
              <dt className="text-[13px] text-apagado">{rotulo}</dt>
            </div>
          ))}
        </dl>
        <p className="text-sm text-apagado">
          {ia?.ligada ? `IA ligada, com limite de ${ia.config.limite_diario || "sem limite de"} chamadas por dia.` : "IA desligada. O atendimento responde por regras."}
        </p>
      </section>
    </div>
  );
}
