import { BellRing, Check, Home, LogOut, Plus, Route, ShieldCheck, Trash2, UserRound, X } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

import { SeloLinha } from "../componentes/Linha";
import { useConversa } from "../componentes/conversa";
import { esquecerIdDoAparelho } from "./Feed";
import { mobilidade, type EstacaoEscolha, type LinhaInfo } from "../lib/api";
import { DIAS, conta, descreverDias, lerToken, type PerfilConta } from "../lib/conta";

/*
 * Perfil. Sem conta, as linhas e a estação de casa ficam só neste aparelho.
 * Com a conta básica (usuário e senha, sem e-mail nem telefone), linhas, casa e rotas salvas
 * ficam no banco e voltam em qualquer aparelho. A senha não é guardada aqui, só o token da sessão.
 */

const MINHAS_LINHAS = "dt-minhas-linhas";
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
const mensagem = (e: unknown) => (e instanceof Error ? e.message : "Algo deu errado. Tente de novo.");

const campo = "h-12 w-full rounded-xl border border-linha bg-superficie px-3.5 text-[15px] outline-none focus:border-tinta";
const botaoLaranja = "inline-flex h-12 items-center justify-center gap-2 rounded-full bg-laranja px-6 text-[15px] font-bold text-black hover:brightness-95 disabled:opacity-50";

export default function Perfil({ aoConferir }: { aoConferir?: (texto: string) => void }) {
  const [linhas, setLinhas] = useState<LinhaInfo[]>([]);
  const [estacoes, setEstacoes] = useState<EstacaoEscolha[]>([]);
  const [minhas, setMinhas] = useState<string[]>(() => ler<string[]>(MINHAS_LINHAS, []));
  const { casa, esquecer, definirCasa } = useConversa();
  const [perfil, setPerfil] = useState<PerfilConta | null>(null);
  const [carregando, setCarregando] = useState(() => !!lerToken());
  const [erroSync, setErroSync] = useState("");
  const [apagado, setApagado] = useState(false);

  useEffect(() => {
    mobilidade.estacoes().then((r) => { setLinhas(r.linhas.filter((l) => l.numero !== "7")); setEstacoes(r.estacoes); }).catch(() => {});
  }, []);

  // junta o que está no aparelho com o que está na conta: a conta vence; se ela estiver vazia, recebe o do aparelho
  const aplicarConta = async (p: PerfilConta) => {
    let atual = p;
    const levarLinhas = p.linhas.length === 0 && minhas.length > 0;
    const levarCasa = !p.casa && !!casa;
    if (levarLinhas || levarCasa) {
      atual = await conta.preferencias(levarLinhas ? minhas : p.linhas, levarCasa ? casa : p.casa);
    }
    setPerfil(atual);
    setMinhas(atual.linhas);
    gravar(MINHAS_LINHAS, atual.linhas);
    if (atual.casa) definirCasa(atual.casa);
  };

  useEffect(() => {
    if (!lerToken()) return;
    conta.eu().then(aplicarConta).catch(() => setPerfil(null)).finally(() => setCarregando(false));
    // só ao abrir a aba
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const salvarPrefs = (novasLinhas: string[], novaCasa: string | null) => {
    if (!perfil) return;
    setErroSync("");
    conta.preferencias(novasLinhas, novaCasa).then(setPerfil).catch((e) => setErroSync(mensagem(e)));
  };

  const alternar = (n: string) => {
    const novo = minhas.includes(n) ? minhas.filter((x) => x !== n) : [...minhas, n];
    setMinhas(novo);
    gravar(MINHAS_LINHAS, novo);
    salvarPrefs(novo, casa);
  };
  const trocarCasa = (id: string) => {
    const nova = id || null;
    definirCasa(nova);
    salvarPrefs(minhas, nova);
  };

  const sair = async () => {
    await conta.sair().catch(() => {});
    setPerfil(null);
  };

  const nomeCasa = estacoes.find((e) => e.id === casa)?.nome;
  const apagarTudo = () => {
    try {
      [MINHAS_LINHAS, ...CHAVES_ANTIGAS].forEach((c) => localStorage.removeItem(c));
    } catch {
      /* nada a apagar */
    }
    esquecer();               // casa, conversa em memória, última viagem e rastro
    esquecerIdDoAparelho();   // o código aleatório dos relatos
    void conta.sair().catch(() => {});   // sai da conta neste aparelho (a conta continua existindo)
    setPerfil(null);
    setMinhas([]);
    setApagado(true);
  };

  return (
    <div className="h-full overflow-y-auto bg-superficie">
      <div className="mx-auto max-w-2xl space-y-7 px-4 pt-2 pb-8">
        <section className="flex items-center gap-4">
          <div className="min-w-0 flex-1">
            <h3 className="truncate text-[30px] leading-tight font-bold tracking-tight">{perfil ? `Olá, ${perfil.usuario}` : "Passageiro"}</h3>
            <p className="mt-1 text-[14px] text-apagado">
              {perfil ? "Suas linhas, a estação de casa e as rotas ficam salvas na sua conta." : "Sem conta: o que você escolhe aqui fica só neste aparelho."}
            </p>
          </div>
          <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-cinza" aria-hidden><UserRound className="size-8 text-apagado" /></span>
        </section>

        {carregando ? (
          <p className="text-[14px] text-apagado">Abrindo sua conta...</p>
        ) : perfil ? (
          <div className="flex items-center justify-between gap-3 rounded-2xl bg-cinza px-4 py-3">
            <span className="text-[14px] font-semibold">Conectado como <b>{perfil.usuario}</b></span>
            <button type="button" onClick={sair} className="inline-flex h-10 items-center gap-2 rounded-full bg-superficie px-4 text-[14px] font-bold hover:bg-linha">
              <LogOut className="size-4" aria-hidden />Sair
            </button>
          </div>
        ) : (
          <FormularioConta aoAbrir={(p) => aplicarConta(p).catch((e) => setErroSync(mensagem(e)))} />
        )}
        {erroSync && <p role="alert" className="text-[14px] font-bold text-erro">{erroSync}</p>}

        <section className="grid grid-cols-3 gap-2.5">
          <div className="rounded-2xl bg-cinza p-4">
            <p className="text-[28px] leading-none font-bold tabular-nums">{minhas.length}</p>
            <p className="mt-1.5 text-[13px] font-semibold text-apagado">{minhas.length === 1 ? "linha marcada" : "linhas marcadas"}</p>
          </div>
          <div className="rounded-2xl bg-cinza p-4">
            <Home className="size-7" aria-hidden />
            <p className="mt-1.5 truncate text-[13px] font-semibold text-apagado">{nomeCasa ?? "Casa não definida"}</p>
          </div>
          <div className="rounded-2xl bg-cinza p-4">
            <p className="text-[28px] leading-none font-bold tabular-nums">{perfil?.rotinas.length ?? 0}</p>
            <p className="mt-1.5 text-[13px] font-semibold text-apagado">{perfil?.rotinas.length === 1 ? "rota salva" : "rotas salvas"}</p>
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

        <section className="space-y-3">
          <div>
            <h3 className="text-[22px] font-bold tracking-tight">Estação perto de casa</h3>
            <p className="text-[14px] text-apagado">A Lia usa para não perguntar de onde você sai. Também dá para dizer a ela no chat.</p>
          </div>
          <select aria-label="Estação perto de casa" value={casa ?? ""} onChange={(e) => trocarCasa(e.target.value)} className={campo}>
            <option value="">Nenhuma</option>
            {estacoes.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
          </select>
        </section>

        <section className="space-y-3">
          <div>
            <h3 className="flex items-center gap-2 text-[22px] font-bold tracking-tight"><Route className="size-5" aria-hidden />Rotas salvas</h3>
            <p className="text-[14px] text-apagado">Guarde os trajetos do dia a dia e confira com a Lia num toque antes de sair.</p>
          </div>
          {perfil ? (
            <>
              {perfil.rotinas.length > 0 && (
                <ul className="space-y-2.5">
                  {perfil.rotinas.map((r) => (
                    <li key={r.id} className="rounded-2xl bg-cinza p-4">
                      <div className="flex items-start gap-3">
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-[16px] font-bold">{r.nome}</p>
                          <p className="text-[14px]">{r.origem_nome} até {r.destino_nome}</p>
                          <p className="text-[13px] text-apagado">Às {r.horario}, {descreverDias(r.dias)}</p>
                        </div>
                        <button type="button" aria-label={`Apagar a rota ${r.nome}`}
                          onClick={() => conta.apagarRotina(r.id).then(setPerfil).catch((e) => setErroSync(mensagem(e)))}
                          className="flex size-9 shrink-0 items-center justify-center rounded-full hover:bg-linha"><X className="size-4" aria-hidden /></button>
                      </div>
                      {aoConferir && (
                        <button type="button" onClick={() => aoConferir(`Vou da ${r.origem_nome} para ${r.destino_nome}`)}
                          className="mt-3 inline-flex h-10 items-center gap-2 rounded-full bg-laranja px-4 text-[14px] font-bold text-black hover:brightness-95">
                          <BellRing className="size-4" aria-hidden />Conferir agora
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
              {perfil.rotinas.length < 10 && <FormularioRota estacoes={estacoes} casa={casa} aoSalvar={setPerfil} />}
            </>
          ) : (
            <p className="rounded-2xl bg-cinza p-4 text-[14px] text-apagado">Entre na sua conta (ou crie uma, leva 10 segundos) para salvar rotas.</p>
          )}
        </section>

        <section className="space-y-3 rounded-2xl bg-cinza p-4">
          <h3 className="flex items-center gap-2 text-[18px] font-bold"><ShieldCheck className="size-5 text-ok" aria-hidden />Sua privacidade</h3>
          <ul className="space-y-2 text-[14px]">
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />Não pedimos nome, CPF, e-mail, telefone, endereço nem localização. A conta é só usuário e senha.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />A senha é guardada embaralhada (hash), nunca como você digitou.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />O que você escreve para a Lia não fica guardado.</li>
            <li className="flex gap-2"><Check className="mt-0.5 size-4 shrink-0 text-ok" strokeWidth={3} aria-hidden />Os relatos usam campos prontos e, se quiser, uma descrição curta de até 140 caracteres (sem dado pessoal e sem link). Não há foto.</li>
          </ul>
          <button type="button" onClick={apagarTudo} className="inline-flex h-11 items-center gap-2 rounded-full bg-superficie px-5 text-[14px] font-bold text-erro hover:bg-erro-suave">
            <Trash2 className="size-4" aria-hidden />Apagar os dados deste aparelho
          </button>
          {apagado && <p role="status" className="text-[14px] font-bold text-ok">Pronto: suas linhas, a estação de casa, o código do aparelho e a conversa atual foram apagados deste aparelho.</p>}
          {perfil && <ApagarConta aoApagar={() => { setPerfil(null); }} />}
        </section>
      </div>
    </div>
  );
}

function FormularioConta({ aoAbrir }: { aoAbrir: (p: PerfilConta) => void }) {
  const [modo, setModo] = useState<"entrar" | "cadastro">("entrar");
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  const enviar = (e: FormEvent) => {
    e.preventDefault();
    setErro("");
    setEnviando(true);
    (modo === "entrar" ? conta.entrar(usuario, senha) : conta.cadastrar(usuario, senha))
      .then((p) => { setSenha(""); aoAbrir(p); })
      .catch((e) => setErro(mensagem(e)))
      .finally(() => setEnviando(false));
  };

  return (
    <form onSubmit={enviar} className="space-y-3 rounded-2xl bg-cinza p-4">
      <div className="flex gap-1 rounded-full bg-superficie p-1" role="tablist" aria-label="Conta">
        {(["entrar", "cadastro"] as const).map((m) => (
          <button key={m} type="button" role="tab" aria-selected={modo === m} onClick={() => { setModo(m); setErro(""); }}
            className={`h-10 flex-1 rounded-full text-[14px] font-bold ${modo === m ? "bg-tinta text-white" : "text-apagado hover:text-tinta"}`}>
            {m === "entrar" ? "Entrar" : "Criar conta"}
          </button>
        ))}
      </div>
      <label className="block">
        <span className="mb-1 block text-[13px] font-semibold">Usuário</span>
        <input className={campo} value={usuario} onChange={(e) => setUsuario(e.target.value)} autoComplete="username" autoCapitalize="none" spellCheck={false}
          maxLength={30} required placeholder="ex.: passageiro.zl" />
      </label>
      <label className="block">
        <span className="mb-1 block text-[13px] font-semibold">Senha</span>
        <input className={campo} type="password" value={senha} onChange={(e) => setSenha(e.target.value)}
          autoComplete={modo === "entrar" ? "current-password" : "new-password"} minLength={modo === "cadastro" ? 8 : undefined} maxLength={128} required />
      </label>
      {modo === "cadastro" && (
        <p className="text-[13px] text-apagado">Use um apelido (letras minúsculas, números, ponto ou _), não o seu nome. Senha com pelo menos 8 caracteres. Não há recuperação por e-mail: guarde a senha.</p>
      )}
      {erro && <p role="alert" className="text-[14px] font-bold text-erro">{erro}</p>}
      <button type="submit" disabled={enviando} className={`${botaoLaranja} w-full`}>
        {enviando ? "Um instante..." : modo === "entrar" ? "Entrar" : "Criar conta"}
      </button>
    </form>
  );
}

function FormularioRota({ estacoes, casa, aoSalvar }: { estacoes: EstacaoEscolha[]; casa: string | null; aoSalvar: (p: PerfilConta) => void }) {
  const [aberto, setAberto] = useState(false);
  const [nome, setNome] = useState("");
  const [origem, setOrigem] = useState(casa ?? "");
  const [destino, setDestino] = useState("");
  const [horario, setHorario] = useState("08:00");
  const [dias, setDias] = useState("12345");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  if (!aberto) {
    return (
      <button type="button" onClick={() => { setAberto(true); setOrigem((o) => o || casa || ""); }}
        className="inline-flex h-11 items-center gap-2 rounded-full border border-linha px-5 text-[14px] font-bold hover:bg-cinza">
        <Plus className="size-4" aria-hidden />Nova rota
      </button>
    );
  }

  const alternarDia = (d: string) => {
    const novo = dias.includes(d) ? dias.replace(d, "") : [...dias, d].sort().join("");
    setDias(novo);
  };
  const salvar = (e: FormEvent) => {
    e.preventDefault();
    setErro("");
    if (!dias) return setErro("Escolha pelo menos um dia.");
    setEnviando(true);
    conta.novaRotina({ nome: nome.trim(), origem, destino, horario, dias })
      .then((p) => { aoSalvar(p); setAberto(false); setNome(""); setDestino(""); })
      .catch((e) => setErro(mensagem(e)))
      .finally(() => setEnviando(false));
  };

  return (
    <form onSubmit={salvar} className="space-y-3 rounded-2xl border border-linha p-4">
      <label className="block">
        <span className="mb-1 block text-[13px] font-semibold">Nome da rota</span>
        <input className={campo} value={nome} onChange={(e) => setNome(e.target.value)} maxLength={40} required placeholder="ex.: Ida para a faculdade" />
      </label>
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="mb-1 block text-[13px] font-semibold">Saio de</span>
          <select className={campo} value={origem} onChange={(e) => setOrigem(e.target.value)} required>
            <option value="">Escolha a estação</option>
            {estacoes.map((x) => <option key={x.id} value={x.id}>{x.nome}</option>)}
          </select>
        </label>
        <label className="block">
          <span className="mb-1 block text-[13px] font-semibold">Vou para</span>
          <select className={campo} value={destino} onChange={(e) => setDestino(e.target.value)} required>
            <option value="">Escolha a estação</option>
            {estacoes.filter((x) => x.id !== origem).map((x) => <option key={x.id} value={x.id}>{x.nome}</option>)}
          </select>
        </label>
      </div>
      <label className="block">
        <span className="mb-1 block text-[13px] font-semibold">Costumo sair às</span>
        <input className={campo} type="time" value={horario} onChange={(e) => setHorario(e.target.value)} required />
      </label>
      <fieldset>
        <legend className="mb-1 text-[13px] font-semibold">Dias</legend>
        <div className="flex gap-1.5">
          {DIAS.map((d) => (
            <button key={d.valor} type="button" aria-pressed={dias.includes(d.valor)} aria-label={d.nome} onClick={() => alternarDia(d.valor)}
              className={`size-10 rounded-full text-[14px] font-bold ${dias.includes(d.valor) ? "bg-tinta text-white" : "bg-cinza text-apagado"}`}>
              {d.curto}
            </button>
          ))}
        </div>
      </fieldset>
      {erro && <p role="alert" className="text-[14px] font-bold text-erro">{erro}</p>}
      <div className="flex gap-2">
        <button type="submit" disabled={enviando} className={botaoLaranja}>{enviando ? "Salvando..." : "Salvar rota"}</button>
        <button type="button" onClick={() => setAberto(false)} className="inline-flex h-12 items-center rounded-full px-5 text-[15px] font-bold hover:bg-cinza">Cancelar</button>
      </div>
    </form>
  );
}

function ApagarConta({ aoApagar }: { aoApagar: () => void }) {
  const [aberto, setAberto] = useState(false);
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");

  if (!aberto) {
    return (
      <button type="button" onClick={() => setAberto(true)} className="block text-[14px] font-bold text-erro underline-offset-2 hover:underline">
        Apagar minha conta
      </button>
    );
  }
  const apagar = (e: FormEvent) => {
    e.preventDefault();
    setErro("");
    conta.apagarConta(senha).then(aoApagar).catch((e) => setErro(mensagem(e)));
  };
  return (
    <form onSubmit={apagar} className="space-y-2 rounded-xl bg-superficie p-3">
      <p className="text-[14px]">Isso apaga a conta, as linhas, a casa e as rotas salvas no banco. Não tem volta. Digite a senha para confirmar.</p>
      <input className={campo} type="password" aria-label="Senha da conta" value={senha} onChange={(e) => setSenha(e.target.value)} autoComplete="current-password" required maxLength={128} />
      {erro && <p role="alert" className="text-[14px] font-bold text-erro">{erro}</p>}
      <div className="flex gap-2">
        <button type="submit" className="inline-flex h-11 items-center gap-2 rounded-full bg-erro px-5 text-[14px] font-bold text-white"><Trash2 className="size-4" aria-hidden />Apagar de vez</button>
        <button type="button" onClick={() => { setAberto(false); setSenha(""); }} className="inline-flex h-11 items-center rounded-full px-4 text-[14px] font-bold hover:bg-cinza">Cancelar</button>
      </div>
    </form>
  );
}
