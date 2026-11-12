// Conversa com a API em Python. Todas as rotas ficam em /api.

export type Opcao = { rotulo: string; acao: string; principal?: boolean };
export type Selo = { materia: string; papel: string };
export type Passo = { materia: string; titulo: string; detalhe: string };
export type Bloco = { tipo: string; [campo: string]: any };
export type Resumo = { assunto: string; itens: { rotulo: string; valor: string }[] } | null;
export type RespostaChat = { blocos: Bloco[]; estado: Record<string, unknown>; rastro: Passo[]; resumo: Resumo };

export type Provedor = { nome: string; base_url: string; modelo: string; precisa_chave: boolean; nota: string };
export type EstadoIA = {
  config: { provedor: string; base_url: string; modelo: string; limite_diario: number; tem_chave: boolean; final_da_chave: string };
  provedores: Record<string, Provedor>;
  ligada: boolean;
  uso: { dia: string; chamadas: number; tokens_entrada: number; tokens_saida: number };
};
export type TesteIA = { ok: boolean; erro: string; modelos: string[]; resposta?: string; ms?: number };

export type Materia = {
  cod: string; nome: string; curto?: string; cor: string; papel: string; no_chat?: string; entrega: string; pasta?: string; rodar?: string;
  regra?: string; ajuda?: string; quando?: string[]; recebe?: string; devolve?: string; nesta_versao?: string; como_testar?: string;
  ver_funcionando?: { rotulo: string; acao: string }[];
};

export type Status = "Feito" | "Falta conferir" | "A fazer";
export type ItemChecklist = {
  id: string; requisito: string; detalhe: string; peso: string; fonte: string; quem: "código" | "grupo"; onde: string; como: string; status: Status;
};
export type ResumoChecklist = { total: number; por_status: Record<Status, number>; percentual: number; do_grupo: number };
export type ChecklistMateria = {
  nome: string; formato_entrega: string; prazo: string; rubrica?: { criterio: string; pontos: string }[]; itens: ItemChecklist[]; resumo: ResumoChecklist;
};
export type DadosMateria = {
  materia: Materia; no_sistema: boolean; checklist: ChecklistMateria | null; status: Status[];
  situacao: { ok: boolean; erro: string; orientacoes?: number; categorias?: number; em_conferencia?: number; registros?: number } | null;
};
export type Painel = {
  dias: number; prazo: string; geral: ResumoChecklist; atualizado_em: string;
  materias: ({ cod: string; nome: string; cor: string; no_sistema: boolean } & ResumoChecklist)[];
  regras: { requisito: string; detalhe?: string; fonte?: string }[]; alertas: string[]; divergencias: string[];
};

export type TestePCP = {
  ok: boolean; erro: string; bloqueada: boolean;
  resultados: { pontos: number; confianca: string; id: number; titulo: string; categoria: string; palavras_chave: string[]; palavras_titulo: string[] }[];
  base: { id: number; titulo: string; categoria: string; palavras_chave: string[]; em_conferencia: boolean }[];
};
export type NoDSA = { id: string; titulo: string; categoria: string; prazo: string; publico_alvo: string; canal: string };
export type EstadoDSA = { ok: boolean; mensagem: string; tamanho: number; nos: NoDSA[]; achados: string[]; cabeca: string | null; cauda: string | null };
export type TesteSERS = {
  kwh: number; kwh_com_desconto: number; kwh_cobrados: number; preco_medio: number | null; desconto_mes: number | null; desconto_ano: number | null;
  passos: string[]; fonte: string; consultado_em: string; falta: string;
};

export type Opiniao = {
  id: string; nome: string; idade: number; quem: string; onde: string; perfil: string; internet: string; genero: string; canal: string;
  chance: number; veredito: "usaria" | "em dúvida" | "não usaria"; nota: number; fala: string; barreira: string; sugestao: string;
};
export type Simulacao = {
  parte: string; canais: string[]; n: number; semente: number; usariam: number; total_personas: number; adesao: number;
  opinioes: Opiniao[]; perfis: { perfil: string; pessoas: number; adesao: number }[];
  barreiras: { barreira: string; pessoas: number }[]; sugestoes: { sugestao: string; pessoas: number }[];
};
export type OpcoesLaboratorio = { partes: string[]; canais: string[]; personas: number; tamanhos: number[] };
export type Materias = {
  no_sistema: Materia[];
  a_parte: { cod: string; nome: string; entrega: string }[];
  situacao: Record<string, { ok: boolean; erro: string; orientacoes?: number; categorias?: number; em_conferencia?: number; registros?: number }>;
};

async function pedir<T>(caminho: string, opcoes?: RequestInit): Promise<T> {
  const resposta = await fetch(caminho, { headers: { "Content-Type": "application/json" }, ...opcoes });
  if (!resposta.ok) {
    let detalhe = "";
    try {
      detalhe = (await resposta.json()).detail ?? "";
    } catch {
      /* resposta sem corpo */
    }
    throw new Error(detalhe || `O servidor respondeu com erro ${resposta.status}.`);
  }
  return resposta.json() as Promise<T>;
}

export const api = {
  inicio: () => pedir<RespostaChat>("/api/chat/inicio"),
  chat: (corpo: { texto?: string; acao?: string; estado: Record<string, unknown> }) =>
    pedir<RespostaChat>("/api/chat", { method: "POST", body: JSON.stringify(corpo) }),
  explicar: (orientacao_id: number) =>
    pedir<{ texto: string; selos: Selo[] }>("/api/explicar", { method: "POST", body: JSON.stringify({ orientacao_id }) }),
  ia: () => pedir<EstadoIA>("/api/config/ia"),
  salvarIA: (corpo: Record<string, unknown>) => pedir<EstadoIA>("/api/config/ia", { method: "PUT", body: JSON.stringify(corpo) }),
  testarIA: () => pedir<TesteIA>("/api/config/ia/testar", { method: "POST" }),
  materias: () => pedir<Materias>("/api/materias"),
  materia: (cod: string) => pedir<DadosMateria>(`/api/materias/${cod}`),
  painel: () => pedir<Painel>("/api/painel"),
  mudarItem: (cod: string, id: string, mudancas: Partial<Pick<ItemChecklist, "status" | "onde" | "como">>) =>
    pedir<{ item: ItemChecklist; resumo: ResumoChecklist }>(`/api/checklist/${cod}/${id}`, { method: "PATCH", body: JSON.stringify(mudancas) }),
  testePCP: (pergunta: string) => pedir<TestePCP>("/api/teste/pcp", { method: "POST", body: JSON.stringify({ pergunta }) }),
  estadoDSA: () => pedir<EstadoDSA>("/api/teste/dsa"),
  operarDSA: (operacao: string, dados: Record<string, string> = {}) =>
    pedir<EstadoDSA>("/api/teste/dsa", { method: "POST", body: JSON.stringify({ operacao, dados }) }),
  testeSERS: (kwh: number, valor: number | null) => pedir<TesteSERS>("/api/teste/sers", { method: "POST", body: JSON.stringify({ kwh, valor }) }),
  laboratorio: () => pedir<OpcoesLaboratorio>("/api/laboratorio"),
  simular: (corpo: { parte: string; canais: string[]; n: number; semente: number }) =>
    pedir<Simulacao>("/api/laboratorio/simular", { method: "POST", body: JSON.stringify(corpo) }),
};

export const MATERIAS_DO_SISTEMA = [
  { cod: "PCP", curto: "Assistente" },
  { cod: "DSA", curto: "Catálogo" },
  { cod: "SERS", curto: "Energia" },
  { cod: "PAI", curto: "Agente com IA" },
  { cod: "MLAM", curto: "Dados" },
];

export const CORES_DAS_MATERIAS: Record<string, string> = {
  PCP: "#2563EB",
  DSA: "#C2410C",
  SERS: "#16A34A",
  PAI: "#7C3AED",
  MLAM: "#BE185D",
  COA: "#0891B2",
  CS: "#4338CA",
  MMC: "#6B7280",
  Sistema: "#556A6A",
};
