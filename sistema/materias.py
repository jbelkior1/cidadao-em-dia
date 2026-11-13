"""O que cada matéria faz na Lia: textos das páginas Entenda e do Painel da equipe.

As oito matérias entram no produto. Cada professor continua recebendo a entrega
no formato do enunciado; o código que ele corrige é o mesmo que roda no app.
"""

PRAZO_GS = "2026-11-19"

# Repositório público e ramo do sistema: os links das páginas das matérias apontam para cá, para o
# professor abrir o arquivo da parte dele direto no GitHub.
REPOSITORIO = "https://github.com/jbelkior1/cidadao-em-dia"
RAMO = "sistema-localhost"


def link(caminho: str) -> str:
    """Link do GitHub para um arquivo (blob) ou pasta (tree) do ramo do sistema."""
    caminho = caminho.strip("/")
    ultimo = caminho.rsplit("/", 1)[-1]
    tipo = "blob" if "." in ultimo else "tree"
    return f"{REPOSITORIO}/{tipo}/{RAMO}/{caminho}"


#: O que o professor de cada matéria abre no repositório: primeiro a entrega, depois onde ela entra no app.
ARQUIVOS = {
    "PCP": [("A entrega (pasta)", "entregas/pcp/citizen-assist-ai"), ("README da entrega", "entregas/pcp/citizen-assist-ai/README.md"),
            ("Programa de terminal", "entregas/pcp/citizen-assist-ai/main.py"),
            ("Classe Assistente", "entregas/pcp/citizen-assist-ai/assistente.py"),
            ("Classe BaseConhecimento (busca por pontos)", "entregas/pcp/citizen-assist-ai/base_conhecimento.py"),
            ("Classe Orientacao", "entregas/pcp/citizen-assist-ai/orientacao.py"),
            ("Base de orientações", "entregas/pcp/citizen-assist-ai/data/base_conhecimento.json"),
            ("No app: ponte com a Lia", "sistema/adaptadores/pcp.py"), ("Testes", "tests/pcp")],
    "DSA": [("A entrega (pasta)", "entregas/dsa"), ("README da entrega", "entregas/dsa/README.md"),
            ("Menu de terminal", "entregas/dsa/main.py"), ("Lista encadeada", "entregas/dsa/lista_encadeada.py"),
            ("Busca e merge sort", "entregas/dsa/algoritmos.py"), ("Documentação e Big-O", "entregas/dsa/docs/DOCUMENTACAO.md"),
            ("Evidências de teste", "entregas/dsa/docs/EVIDENCIAS.md"), ("No app: ponte com a Lia", "sistema/adaptadores/dsa.py"),
            ("Testes", "tests/dsa")],
    "SERS": [("A entrega (pasta)", "entregas/sers"), ("README da entrega", "entregas/sers/README.md"),
             ("Comparação que o professor roda", "entregas/sers/comparar_energia.py"),
             ("Cálculo usado pelo app", "sistema/mobilidade/energia.py"), ("Os 30 fatores com fonte", "pesquisa/energia_modos.json"),
             ("Levantamento das fontes", "pesquisa/ENERGIA_FONTES.md"), ("Testes com usuários (roteiro)", "entregas/sers/TESTES_USUARIOS.md")],
    "MLAM": [("A entrega (pasta)", "entregas/mlam"), ("README da entrega", "entregas/mlam/README.md"),
             ("Base (.csv)", "entregas/mlam/dados/ocorrencias_estacoes_2026.csv"), ("Como a base foi montada", "entregas/mlam/dados/LEIA-ME.md"),
             ("Roda as questões 02 a 06", "entregas/mlam/main.py"), ("Questão 07: gera o relatório", "entregas/mlam/questao07_relatorio.py"),
             ("Relatório em PDF", "entregas/mlam/saidas/relatorio_mlam_gs2026.pdf"), ("Saída completa", "entregas/mlam/saidas/relatorio.txt")],
    "PAI": [("A entrega (pasta)", "entregas/pai"), ("README da entrega", "entregas/pai/README.md"),
            ("O agente (LangGraph)", "entregas/pai/pai_agente/agente.py"), ("As 7 fichas FT", "entregas/pai/fichas"),
            ("Golden dataset", "entregas/pai/golden/golden_pai.json"), ("Juiz (LLM as a Judge)", "entregas/pai/pai_agente/juiz.py"),
            ("Resultados antes e depois", "entregas/pai/saidas"),
            ("Imagem do grafo", "entregas/pai/grafo_agente.png"), ("Testes com usuários (roteiro)", "entregas/pai/TESTES_USUARIOS.md"),
            ("No app: ponte com a Lia", "sistema/adaptadores/pai.py"), ("Testes", "tests/pai/test_pai.py")],
    "CS": [("Regra do produto (não é a entrega)", "sistema/mobilidade/decisao.py")],
    "MMC": [],
    "COA": [],
}

NO_SISTEMA = [
    {
        "cod": "PCP", "nome": "Pensamento Computacional e Automação com Python", "curto": "As orientações", "cor": "#2563EB",
        "papel": "Responde o que fazer em cada situação do transporte: linha parada, alagamento, celular roubado, atraso no trabalho, gratuidades. Usa a busca por pontos do enunciado e mostra a fonte oficial e a data.",
        "ajuda": "A pessoa sabe o que fazer na hora do problema, com o link oficial, e o assistente diz quando não encontrou.",
        "quando": ["Quando a pessoa pergunta à Lia o que fazer (linha parada, celular roubado, declaração de atraso)"],
        "recebe": "A pergunta escrita pela pessoa.",
        "devolve": "A orientação com o que fazer, onde, fonte e data, a confiança com os pontos e até duas alternativas.",
        "no_chat": "Nos cartões de orientação da conversa com a Lia.",
        "entrega": "Programa de terminal em repositório público próprio, com 3 classes em 4 arquivos, teste com 3 pessoas e vídeo técnico de 5 a 8 minutos.",
        "pasta": "entregas/pcp/citizen-assist-ai", "rodar": "python main.py",
        "regra": "3 pontos por palavra-chave e 1 ponto por palavra do título com 4 letras ou mais. Com 6 pontos ou mais a confiança é ALTA; de 3 a 5 é MÉDIA; abaixo de 3 o assistente diz que não encontrou.",
        "nesta_versao": "A lógica está pronta (classes, busca, histórico, CSV). A base passa a ser de orientações de mobilidade com fontes oficiais, que o grupo precisa conferir.",
        "como_testar": "Escreva uma pergunta e veja a pontuação de cada orientação, da maior para a menor. Depois tente um número de telefone e veja a recusa.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/"}],
    },
    {
        "cod": "CS", "nome": "Computer Science", "curto": "A decisão do dia", "cor": "#4338CA",
        "papel": "Decide a frase principal do app a partir de quatro perguntas de sim ou não: há falha numa linha do trajeto, há aviso de chuva, há alagamento perto de alguma estação, é horário de pico.",
        "ajuda": "A pessoa não precisa interpretar quatro informações: recebe uma frase só, \"pode ir\", \"saia mais cedo\" ou \"mude o caminho\".",
        "quando": ["Fora do sistema: entrega própria da matéria, feita à mão pelo grupo (tabela-verdade, Karnaugh e circuito)"],
        "recebe": "Quatro valores verdadeiro ou falso: falha (F), chuva (C), alagamento (A) e pico (P).",
        "devolve": "A decisão do dia.",
        "no_chat": "Fora do sistema. O produto tem a própria regra para \"pode ir, saia mais cedo ou mude o caminho\"; a entrega de CS segue à parte, e a integração é opcional pelo enunciado.",
        "entrega": "Relatório em PDF com tabela-verdade, forma canônica, simplificação por álgebra e Karnaugh, circuitos original e simplificado, e um programa com a lógica simplificada.",
        "pasta": "", "rodar": "",
        "regra": "Tabela-verdade, Karnaugh e circuito são feitos pelo grupo, à mão. Usar IA nessas partes tira 4 pontos. Hoje o app usa uma regra provisória de prioridades, que será trocada pela expressão simplificada do grupo.",
        "nesta_versao": "Entregue à parte. O teste abaixo mostra a regra do produto com as mesmas quatro entradas; se o grupo quiser, pode trocá-la pela expressão simplificada dele (integração opcional).",
        "como_testar": "Ligue e desligue as quatro condições e veja a decisão que sai, uma combinação por vez.",
        "ver_funcionando": [],
    },
    {
        "cod": "DSA", "nome": "Data Structures and Algorithms", "curto": "O catálogo de serviços", "cor": "#C2410C",
        "papel": "Guarda os serviços ao passageiro (centrais de atendimento, ouvidorias, achados e perdidos, Defesa Civil, delegacia do metrô) numa lista encadeada feita pelo grupo, com busca e ordenação próprias.",
        "ajuda": "A pessoa acha o canal certo para resolver o problema, com o contato e a fonte.",
        "quando": ["Quando a orientação indica onde resolver"],
        "recebe": "O nome ou a categoria do serviço.",
        "devolve": "O registro do serviço: para quem é, canal e fonte.",
        "no_chat": "No canal de atendimento que acompanha cada orientação.",
        "entrega": "Código com menu de terminal, documentação técnica com análise Big-O e evidências de teste.",
        "pasta": "entregas/dsa", "rodar": "python main.py",
        "regra": "Nenhuma lista pronta do Python guarda os registros: cada serviço é um nó que aponta para o próximo. A busca é linear e a ordenação é um merge sort que só religa os nós.",
        "nesta_versao": "A lista encadeada está pronta. Os dados passam a ser os serviços de mobilidade, com fontes oficiais.",
        "como_testar": "Ordene o catálogo por título, id ou prazo e veja os nós se religarem. Pesquise por um trecho e cadastre ou exclua um serviço.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/"}],
    },
    {
        "cod": "SERS", "nome": "Soluções em Energias Renováveis e Sustentáveis", "curto": "A energia da viagem", "cor": "#16A34A",
        "papel": "Compara a mesma viagem de carro, de ônibus a diesel e de trem ou metrô elétrico em energia, custo e emissão de CO₂, com dados e fontes.",
        "ajuda": "A pessoa vê quanto a escolha do transporte pesa no bolso e no clima, sem estimativa tratada como garantia.",
        "quando": ["Toda vez que a Lia confere uma viagem"],
        "recebe": "A distância do trajeto em quilômetros.",
        "devolve": "Energia, custo e CO₂ por pessoa em cada alternativa, com as premissas.",
        "no_chat": "Em \"Segurança e energia da viagem\", no cartão da viagem.",
        "entrega": "Repositório com dados, cálculos e fontes, comparação de alternativas (uma renovável), testes com usuários, vídeo de até 3 minutos e um .txt com os links.",
        "pasta": "entregas/sers", "rodar": "python comparar_energia.py",
        "regra": "Mesma necessidade (a viagem casa-trabalho), mesmo período e duas ou mais alternativas, uma delas renovável. Cada número com origem, unidade e premissa.",
        "nesta_versao": "Pronta no app e no script da entrega: a distância sai da rede e os fatores vêm de fontes oficiais (MCTI, Metrô, INMETRO, ANP), em pesquisa/energia_modos.json, com a comparação por viagem e por mês. Falta a equipe conferir os números lidos de PDF, aplicar os testes com usuários e gravar o vídeo.",
        "como_testar": "Mude a distância e veja cada conta, passo a passo, para trilho, ônibus e carro.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/"}],
    },
    {
        "cod": "MLAM", "nome": "Modelagem Linear para Aprendizado de Máquina", "curto": "A segurança nas estações", "cor": "#BE185D",
        "papel": "Analisa as ocorrências registradas pela SSP-SP perto das estações, com probabilidade, testes de hipótese e regressões. O resultado aparece na tela de segurança.",
        "ajuda": "A pessoa sabe em que horário e que tipo de ocorrência é mais comum perto da estação onde embarca ou desce.",
        "quando": ["Quando a Lia confere uma viagem", "Quando a pessoa pergunta se uma estação é segura"],
        "recebe": "A base real da SSP-SP de 2026, agregada por estação.",
        "devolve": "Ocorrências por estação, por faixa de horário e por tipo, e os modelos do relatório.",
        "no_chat": "Nos detalhes do cartão da viagem e no cartão de segurança da estação.",
        "entrega": "Base em .csv ou .xlsx, códigos em .py e relatório em .pdf, postados direto no portal, sem links.",
        "pasta": "entregas/mlam", "rodar": "python main.py  ·  python questao07_relatorio.py",
        "regra": "Base real e justificada: dado gerado ou fictício não vale. Desconto de 1,0 por item ausente e de 2,0 por entrega inadequada.",
        "nesta_versao": "Base real (SSP-SP, janeiro a setembro de 2026, raio de 300 m de 139 estações), questões 02 a 06 com interpretações e o relatório da questão 07 em PDF prontos. Falta a equipe preencher nome e RM (em comum.py, que alimenta o PDF) e postar no portal.",
        "como_testar": "Veja o resumo da base: estações com mais registros, faixas de horário e tipos.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/"}],
    },
    {
        "cod": "PAI", "nome": "Prompt and Artificial Intelligence", "curto": "O agente das fichas", "cor": "#7C3AED",
        "papel": "O agente de orientação da PAI: um LangGraph de três nós (guardrails, busca nas fichas, resposta) que só responde pelas 7 fichas de transporte (FT-01 a FT-07), montadas a partir de páginas oficiais, e cita a ficha. O professor autorizou em 13/11/2026 trocar as fichas de Aurora do enunciado pelo nosso tema, mantendo as mesmas regras. Na conversa, a Lia chama esse agente como ferramenta nas dúvidas de regra e procedimento.",
        "ajuda": "A pessoa pergunta do jeito dela (\"tenho 67 anos, pago metrô?\") e recebe uma resposta curta, com a ficha citada, sem nada inventado.",
        "quando": ["Na conversa, quando a dúvida é de regra ou procedimento: declaração de atraso, gratuidade, reclamação, achados e perdidos, tarifa, assédio, acessibilidade",
                   "Sozinho, pelo terminal (entregas/pai/main.py) e na avaliação com o juiz"],
        "recebe": "A pergunta, depois das barreiras de dado pessoal da Lia e do próprio agente.",
        "devolve": "A resposta com a ficha citada (FT-xx) e a data da fonte, ou o aviso de que não encontrou nas fichas.",
        "no_chat": "Ferramenta perguntar_fichas da Lia: a resposta vira um cartão de orientação com a ficha e a fonte oficial.",
        "entrega": "Repositório com o agente em LangGraph, fichas, golden dataset de 26 mensagens, juiz (LLM as a Judge) antes e depois de uma melhoria, testes com usuários e relatório.",
        "pasta": "entregas/pai", "rodar": "python main.py  ·  python avaliar.py --nome depois",
        "regra": "Só responde com o que está nas fichas e cita a ficha. Dado pessoal e tentativa de manipulação são barrados antes de qualquer chamada ao modelo.",
        "nesta_versao": "Agente, fichas de transporte, golden, juiz e a rodada antes/depois prontos. Falta a equipe aplicar os testes com usuários e preencher nome e RM.",
        "como_testar": "Escreva uma pergunta abaixo e veja cada etapa do grafo. Ou converse com a Lia e pergunte, por exemplo, como pedir a declaração de atraso.",
        "ver_funcionando": [{"rotulo": "Perguntar à Lia", "rota": "/"}],
    },
    {
        "cod": "MMC", "nome": "Modelagem Matemática e Computacional", "curto": "Os ônibus de apoio", "cor": "#6B7280",
        "papel": "Modela a frota de ônibus das regiões Norte, Sul, Leste e Oeste com um sistema linear e propõe uma redistribuição por transformação linear, que é o que acontece quando ônibus de apoio cobrem uma linha parada.",
        "ajuda": "Mostra como a cidade pode deslocar ônibus para atender uma falha sem perder ônibus e sem deixar região descoberta.",
        "quando": ["Fora do sistema: entrega própria da matéria (modelo matricial da frota e política de redistribuição)"],
        "recebe": "A frota disponível por região e a necessidade de cada uma.",
        "devolve": "A nova distribuição, com a prova de que mantém o total e não gera números negativos.",
        "no_chat": "Fora do sistema. Entregue à parte, no formato do enunciado.",
        "entrega": "Etapa 1 (modelo matricial, unicidade e solução em Python) e etapa 2 (política de redistribuição por transformação linear).",
        "pasta": "", "rodar": "",
        "regra": "Frota de 72 ônibus. A matriz da transformação é criada pelo grupo e precisa preservar o total e não gerar valores negativos.",
        "nesta_versao": "A frota foi conferida no início do projeto. O simulador está na lista do que entra se houver tempo.",
        "como_testar": "Ainda sem teste no sistema.",
        "ver_funcionando": [],
    },
    {
        "cod": "COA", "nome": "Computer Organization and Architecture", "curto": "O sensor de alagamento", "cor": "#0891B2",
        "papel": "Um Raspberry Pi Pico com sensor de nível de água, no Wokwi, acende um alerta num ponto de alagamento (passagem subterrânea ou ponto de ônibus).",
        "ajuda": "Avisa no local quando a água sobe, antes de alguém tentar passar.",
        "quando": ["Fora do sistema: entregue no Wokwi, com a Raspberry Pi Pico e o sensor de nível de água"],
        "recebe": "A leitura do sensor de nível.",
        "devolve": "LED e buzina de alerta conforme o nível.",
        "no_chat": "Fora do sistema. Entregue à parte, no Wokwi.",
        "entrega": "Link do projeto no Wokwi com a Pico e o código em MicroPython, vídeo no YouTube e nomes de todos.",
        "pasta": "", "rodar": "",
        "regra": "Sensores e atuadores ligados ao problema escolhido. O enunciado cita alerta de risco em espaço público como exemplo.",
        "nesta_versao": "Entregue à parte, no Wokwi.",
        "como_testar": "Ainda sem teste no sistema.",
        "ver_funcionando": [],
    },
]

# Entregues à parte, fora do sistema: não fazem sentido dentro da conversa (o COA depende do Wokwi,
# o MMC é um modelo matemático da frota, a CS tem integração opcional e é feita à mão pelo grupo).
# Continuam com página, teste e checklist próprios.
FORA_DO_SISTEMA = ("CS", "MMC", "COA")
A_PARTE: list[dict] = [m for m in NO_SISTEMA if m["cod"] in FORA_DO_SISTEMA]
NO_SISTEMA = [m for m in NO_SISTEMA if m["cod"] not in FORA_DO_SISTEMA]

POR_CODIGO = {m["cod"]: m for m in NO_SISTEMA + A_PARTE}
for _cod, _m in POR_CODIGO.items():
    _m["arquivos"] = [{"rotulo": r, "caminho": c, "url": link(c)} for r, c in ARQUIVOS.get(_cod, [])]
    _m["pasta_url"] = link(_m["pasta"]) if _m["pasta"] else ""
