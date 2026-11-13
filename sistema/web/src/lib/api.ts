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
  ver_funcionando?: { rotulo: string; rota: string }[];
  arquivos?: { rotulo: string; caminho: string; url: string }[]; pasta_url?: string;
};

export type Status = "Feito" | "Falta conferir" | "A fazer";
export type ItemChecklist = {
  id: string; requisito: string; detalhe: string; peso: string; fonte: string; quem: "código" | "grupo"; onde: string; como: string; status: Status;
};
export type Andamento = { total: number; prontos: number; faltam: number; percentual: number };
export type ResumoChecklist = {
  total: number; por_status: Record<Status, number>; percentual: number; do_grupo: number;
  por_quem: { codigo: Andamento; grupo: Andamento };
};
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
export type TestePAI = {
  ok: boolean; erro?: string;
  guardrails?: { dado_pessoal: string[]; injecao: string[]; entrada_invalida: string; texto_que_segue: string };
  busca?: { ficha: string; assunto: string; pontos: number }[];
  encontrou?: boolean; resposta?: string; motivo?: string; fichas?: string[]; fonte?: string; usou_modelo?: boolean; aviso?: string;
};
export type NoDSA ={ id: string; titulo: string; categoria: string; prazo: string; publico_alvo: string; canal: string };
export type EstadoDSA = { ok: boolean; mensagem: string; tamanho: number; nos: NoDSA[]; achados: string[]; cabeca: string | null; cauda: string | null };
export type TesteSERS = NonNullable<Energia> & { passos: string[]; falta: string };
export type TesteMLAM = {
  ok: boolean; mensagem?: string; meta: { fonte: string; periodo: string; raio_m: number; observacao: string }; estacoes: number;
  faixas: Record<string, number>; tipos: Record<string, number>;
  ranking: { estacao: string; linhas: string[]; total: number; faixa_mais_comum: string }[]; falta: string;
};
export type TesteCS = { entradas: { falha: boolean; chuva: boolean; alagamento: boolean; pico: boolean }; codigo: string; texto: string; regra_provisoria: boolean; aviso: string };

export type Opiniao = {
  id: string; nome: string; idade: number; quem: string; onde: string; perfil: string; internet: string; genero: string; canal: string;
  chance: number; veredito: "usaria" | "em dúvida" | "não usaria"; nota: number; fala: string; barreira: string; sugestao: string;
  trajeto: string; conversa: { pessoa: string; auxilia: string; decisao: string } | null;
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
  testePAI: (pergunta: string) => pedir<TestePAI>("/api/teste/pai", { method: "POST", body: JSON.stringify({ pergunta }) }),
  estadoDSA: () => pedir<EstadoDSA>("/api/teste/dsa"),
  operarDSA: (operacao: string, dados: Record<string, string> = {}) =>
    pedir<EstadoDSA>("/api/teste/dsa", { method: "POST", body: JSON.stringify({ operacao, dados }) }),
  testeSERS: (km: number) => pedir<TesteSERS>("/api/teste/sers", { method: "POST", body: JSON.stringify({ km }) }),
  laboratorio: () => pedir<OpcoesLaboratorio>("/api/laboratorio"),
  simular: (corpo: { parte: string; canais: string[]; n: number; semente: number }) =>
    pedir<Simulacao>("/api/laboratorio/simular", { method: "POST", body: JSON.stringify(corpo) }),
};

export const MATERIAS_DO_SISTEMA = [
  { cod: "PCP", curto: "Orientações" },
  { cod: "CS", curto: "Lógica (à parte)" },
  { cod: "DSA", curto: "Catálogo" },
  { cod: "SERS", curto: "Energia" },
  { cod: "MLAM", curto: "Segurança" },
  { cod: "PAI", curto: "Lia (IA)" },
  { cod: "MMC", curto: "Frota (à parte)" },
  { cod: "COA", curto: "Sensor (à parte)" },
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

/* ---------------------------------------------------------------- mobilidade */
export type Nivel = "normal" | "atencao" | "parada" | "encerrada" | "sem_dado";
export type LinhaInfo = { numero: string; nome: string; cor: string };
export type EstacaoEscolha = { id: string; nome: string; linhas: string[] };
export type LinhaAgora = LinhaInfo & { status: string; descricao?: string; nivel: Nivel; operadora: string; simulado?: boolean };
export type Etapa = { via: string; de: string; ate: string; paradas: number; min: number; linha?: LinhaInfo };
export type Rota = { minutos: number; etapas: Etapa[]; linhas: string[]; estacoes: string[]; baldeacoes: number; km: number };
export type Motivo = { tipo: "falha" | "ok" | "sem_dado" | "chuva" | "alagamento" | "pico"; texto: string };
export type Seguranca = {
  estacao: string; total: number; por_faixa: Record<string, number>; por_tipo: Record<string, number>; celular: number | null;
  faixa_mais_comum: string; meta?: { fonte?: string; periodo?: string; raio_m?: number };
} | null;
export type ModoEnergia = {
  modo: string; energia_kwh: number | null; co2_kg: number | null; co2_kg_max: number | null; custo_rs: number | null;
  custo_tipo: "tarifa" | "combustível"; renovavel: boolean; nota: string;
};
export type Energia = {
  km: number; modos: ModoEnergia[]; trilho_vs_carro: number | null; premissas: string[]; rotulo: string; fontes: string[]; consultado_em: string;
} | null;
export type PlanoB = {
  recomendacao: "desviar" | "esperar"; texto: string; alternativa: Rota | null; acrescimo_min: number | null;
  historico: { suficiente: boolean; episodios?: number; mediana_min?: number; coletando_desde?: string | null };
  apoio: string; parcial?: { rota: Rota; acrescimo_min: number; texto: string };
};
export type PlanoDoDia = {
  ok: boolean; origem: string; destino: string;
  veredito: { codigo: "pode_ir" | "mais_cedo" | "plano_b"; texto: string; regra_provisoria: boolean };
  entradas: { falha: boolean; chuva: boolean; alagamento: boolean; pico: boolean };
  motivos: Motivo[]; rota: Rota; linhas: LinhaAgora[]; plano_b: PlanoB | null;
  seguranca: { origem: Seguranca; destino: Seguranca }; energia: Energia;
  fontes: { linhas: { nome: string; lido_em: string; ok: boolean; aviso: string }; tempo: { nome: string; lido_em: string; ok: boolean }; rede: string };
  simulacao: string | null;
};
export type AvisoTempo = { quando: string; tipo: string; severidade: string; inicio: string; fim: string; riscos: string; instrucoes: string };

export const mobilidade = {
  estacoes: () => pedir<{ estacoes: EstacaoEscolha[]; linhas: LinhaInfo[] }>("/api/mobilidade/estacoes"),
  linhas: () => pedir<{ linhas: LinhaAgora[]; fonte: string; lido_em: string; ok: boolean; aviso: string }>("/api/mobilidade/linhas"),
  tempo: () => pedir<{ ok: boolean; lido_em: string; avisos: AvisoTempo[]; fonte: string }>("/api/mobilidade/tempo"),
  plano: (origem: string, destino: string, simular?: string) =>
    pedir<PlanoDoDia>(`/api/mobilidade/plano?origem=${encodeURIComponent(origem)}&destino=${encodeURIComponent(destino)}${simular ? `&simular=${simular}` : ""}`),
  testeCS: (entradas: TesteCS["entradas"]) => pedir<TesteCS>("/api/teste/cs", { method: "POST", body: JSON.stringify(entradas) }),
  testeMLAM: () => pedir<TesteMLAM>("/api/teste/mlam"),
};

/* ---------------------------------------------------------------- assistente */

export type EtapaCartao = { via: string; de: string; ate: string; min: number; paradas: number; cor: string | null };
export type RotaCartao = { minutos: number; etapas: EtapaCartao[] };
export type CartaoPlano = {
  tipo: "plano"; origem: string; destino: string; veredito: PlanoDoDia["veredito"]; motivos: string[]; rota: RotaCartao;
  linhas: { numero: string; cor: string; nivel: Nivel; simulado: boolean }[]; simulacao: string | null;
  desvio: { recomendacao: "desviar" | "esperar"; texto: string; rota: RotaCartao | null; acrescimo_min: number | null } | null;
  minutos: number; atraso_min: number; chegada: string | null;
  seguranca: Partial<Record<"saida" | "chegada", { estacao: string; total: number; faixa: string }>>;
  energia: { km: number; trilho_g: number; carro_kg: number; carro_custo: number; tarifa: number; percentual: number | null } | null;
  situacao: Record<string, { nome: string; nivel: Nivel; simulado: boolean; status: string }>;
  avisos: { tipo: "chuva" | "alagamento" | "pico" | "sem_dado"; texto: string }[];
  problemas: string[];
};
export type ItemAlerta = {
  tipo: "linha" | "chuva" | "alagamento"; nivel: "parada" | "atencao" | "ok"; titulo: string; texto: string; fonte: string; pergunta: string;
  linha?: { numero: string; cor: string };
};
export type Alertas = { lido_em: string; itens: ItemAlerta[]; total: number; parada: boolean };
export type LinhaCartao = { numero: string; nome: string; cor: string; status: string; nivel: Nivel; simulado: boolean };
export type CartaoLinhas = { tipo: "linhas"; lido_em: string; linhas: LinhaCartao[] };
export type CartaoOrientacao = { tipo: "orientacao"; titulo: string; resposta: string; onde: string; canal: string; fonte: string; verificado_em: string };
export type CartaoSeguranca = { tipo: "seguranca"; estacao: string; total: number; faixa: string; por_faixa: Record<string, number>; tipo_principal: string; periodo: string };
export type PontoCGE = { zona: string; bairro: string; ativo: boolean; transitavel: boolean; inicio: string; fim: string; via: string; sentido: string; referencia: string };
export type CartaoAlertas = {
  tipo: "alertas"; lido_em: string; inmet: AvisoTempo[]; cge_estado: { titulo: string; quando: string } | null; cge_ativos: number | null;
  cge_pontos: PontoCGE[]; cge_ok: boolean;
};
export type CartaoPanorama = {
  tipo: "panorama"; lido_em: string; problemas: LinhaCartao[]; normais: number; inmet: AvisoTempo[];
  cge_estado: { titulo: string; quando: string } | null; cge_ativos: number | null;
};
export type CartaoMensagem = { tipo: "mensagem"; texto: string; para_quem: string };
export type Cartao = CartaoPlano | CartaoLinhas | CartaoOrientacao | CartaoSeguranca | CartaoAlertas | CartaoPanorama | CartaoMensagem;
export type Viagem = { origem: string; destino: string };
export type RespostaAssistente = {
  texto: string; recusa: boolean; cartoes: Cartao[]; rastro: Passo[]; sugestoes: string[]; ia: { usada: boolean; aviso: string }; aviso: string;
  memoria: { casa?: string }; ultima_viagem: Viagem | null;
};
export type FalaHistorico = { papel: "pessoa" | "plano"; texto: string };

export const assistente = {
  alertas: (simular?: string) => pedir<Alertas>(`/api/assistente/alertas${simular ? `?simular=${simular}` : ""}`),
  responder: (texto: string, historico: FalaHistorico[], contexto: { casa: string | null; ultima_viagem: Viagem | null }, simular?: string) =>
    pedir<RespostaAssistente>("/api/assistente", { method: "POST", body: JSON.stringify({ texto, historico, contexto, simular: simular || null }) }),
};

/** Texto escuro sobre cores claras (Linha 4 Amarela, 15 Prata), branco nas demais. */
export function corDoTexto(fundo: string): string {
  const h = fundo.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.62 ? "#14212B" : "#FFFFFF";
}
