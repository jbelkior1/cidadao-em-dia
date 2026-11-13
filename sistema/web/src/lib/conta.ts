/*
 * Conta básica (usuário e senha) do Dá Tempo?: chamadas à API /api/conta e o token da sessão.
 * O token fica só neste aparelho (localStorage). A senha nunca é guardada aqui.
 */

export type Rotina = {
  id: string; nome: string; origem: string; destino: string; origem_nome: string; destino_nome: string;
  horario: string; dias: string;
};
export type PerfilConta = { usuario: string; linhas: string[]; casa: string | null; rotinas: Rotina[] };
export type NovaRotina = { nome: string; origem: string; destino: string; horario: string; dias: string };

const CHAVE_SESSAO = "dt-sessao";

export function lerToken(): string | null {
  try {
    return localStorage.getItem(CHAVE_SESSAO);
  } catch {
    return null;
  }
}
function gravarToken(token: string) {
  try {
    localStorage.setItem(CHAVE_SESSAO, token);
  } catch {
    /* sem armazenamento: a sessão vale só até recarregar */
  }
}
export function limparToken() {
  try {
    localStorage.removeItem(CHAVE_SESSAO);
  } catch {
    /* nada a limpar */
  }
}

export class ErroConta extends Error {
  constructor(mensagem: string, public status: number) {
    super(mensagem);
  }
}

async function pedir<T>(caminho: string, metodo = "GET", corpo?: unknown): Promise<T> {
  const token = lerToken();
  const r = await fetch(caminho, {
    method: metodo,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
  if (!r.ok) {
    let detalhe = "";
    try {
      const d = (await r.json()).detail;
      detalhe = typeof d === "string" ? d : "";
    } catch {
      /* resposta sem corpo */
    }
    if (r.status === 401) limparToken();
    throw new ErroConta(detalhe || `O servidor respondeu com erro ${r.status}.`, r.status);
  }
  return r.json() as Promise<T>;
}

async function abrir(caminho: string, usuario: string, senha: string): Promise<PerfilConta> {
  const r = await pedir<{ token: string; perfil: PerfilConta }>(caminho, "POST", { usuario, senha });
  gravarToken(r.token);
  return r.perfil;
}

export const conta = {
  cadastrar: (usuario: string, senha: string) => abrir("/api/conta/cadastro", usuario, senha),
  entrar: (usuario: string, senha: string) => abrir("/api/conta/entrar", usuario, senha),
  async sair() {
    try {
      await pedir("/api/conta/sair", "POST");
    } finally {
      limparToken();
    }
  },
  eu: () => pedir<PerfilConta>("/api/conta/eu"),
  preferencias: (linhas: string[], casa: string | null) => pedir<PerfilConta>("/api/conta/preferencias", "PUT", { linhas, casa }),
  novaRotina: (r: NovaRotina) => pedir<PerfilConta>("/api/conta/rotinas", "POST", r),
  apagarRotina: (id: string) => pedir<PerfilConta>(`/api/conta/rotinas/${encodeURIComponent(id)}`, "DELETE"),
  async apagarConta(senha: string) {
    await pedir("/api/conta", "DELETE", { senha });
    limparToken();
  },
};

export const DIAS = [
  { valor: "1", curto: "S", nome: "segunda" }, { valor: "2", curto: "T", nome: "terça" }, { valor: "3", curto: "Q", nome: "quarta" },
  { valor: "4", curto: "Q", nome: "quinta" }, { valor: "5", curto: "S", nome: "sexta" }, { valor: "6", curto: "S", nome: "sábado" },
  { valor: "7", curto: "D", nome: "domingo" },
];

export function descreverDias(dias: string): string {
  if (dias === "12345") return "segunda a sexta";
  if (dias === "1234567") return "todos os dias";
  if (dias === "67") return "fim de semana";
  return DIAS.filter((d) => dias.includes(d.valor)).map((d) => d.nome).join(", ");
}
