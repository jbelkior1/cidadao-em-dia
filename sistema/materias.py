"""O que cada matéria faz no Dá Tempo?: textos das páginas das matérias e do Como funciona.

As oito matérias entram no produto. Cada professor continua recebendo a entrega
no formato do enunciado; o código que ele corrige é o mesmo que roda no app.
"""

PRAZO_GS = "2026-11-19"

# Repositório público e ramo principal: os links das páginas das matérias apontam para cá, para o
# professor abrir o arquivo da parte dele direto no GitHub.
REPOSITORIO = "https://github.com/jbelkior1/cidadao-em-dia"
RAMO = "main"


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
    "MLAM": [("O que vai ao portal (um script por questão)", "entregas/mlam/entrega"), ("README da entrega", "entregas/mlam/README.md"),
             ("Base (.csv)", "entregas/mlam/dados/ocorrencias_estacoes_2026.csv"), ("Relatório em PDF (questão 07)", "entregas/mlam/saidas/relatorio_mlam_gs2026.pdf"),
             ("Como a base foi montada (só no repositório)", "entregas/mlam/preparar_base.py"), ("Saída completa", "entregas/mlam/saidas/relatorio.txt")],
    "PAI": [("A entrega (pasta)", "entregas/pai"), ("README da entrega", "entregas/pai/README.md"),
            ("O agente (LangGraph)", "entregas/pai/pai_agente/agente.py"), ("As 7 fichas FT", "entregas/pai/fichas"),
            ("Golden dataset", "entregas/pai/golden/golden_pai.json"), ("Juiz (LLM as a Judge)", "entregas/pai/pai_agente/juiz.py"),
            ("Validação do juiz", "entregas/pai/validar_juiz.py"), ("Rodada antes e depois", "entregas/pai/rodar_antes_e_depois.py"),
            ("Resultados gravados", "entregas/pai/saidas"),
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
        "nesta_versao": "Programa de terminal pronto e testado (56 testes automáticos): 3 classes em 4 arquivos, busca por pontos, navegação por categorias, histórico, indicadores e CSV, com 16 orientações de transporte conferidas contra as páginas oficiais em 16/11/2026.",
        "como_testar": "Escreva uma pergunta e veja a orientação que o assistente mostraria, com a confiança, a fonte e a data. Em \"Como a busca pontuou\" ficam a pergunta normalizada e a lista de buscar(), da maior para a menor pontuação. Tente também um telefone para ver a recusa.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/sistema"}],
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
        "regra": "Tabela-verdade, Karnaugh e circuito são feitos pela equipe, à mão: usar IA nessas partes tira 4 pontos. O app tem a própria regra de prioridades para a decisão do dia, independente da entrega de CS.",
        "nesta_versao": "Entregue à parte, no formato do enunciado (relatório em PDF, prints da simulação e instruções). A integração com o app é opcional e não foi feita; o teste abaixo mostra a regra do produto, uma combinação por vez.",
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
        "nesta_versao": "Pronta e testada (29 testes automáticos): lista encadeada própria com cadastro, consulta, atualização, exclusão, pesquisa e merge sort, documentação com Big-O e 23 cenários de evidência, sobre 15 serviços ao passageiro.",
        "como_testar": "Consulte, atualize, cadastre ou exclua um serviço e veja a lista se ajustar. Ordene por título, id ou prazo e pesquise por um trecho; um campo vazio mostra a validação.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/sistema"}],
    },
    {
        "cod": "SERS", "nome": "Soluções em Energias Renováveis e Sustentáveis", "curto": "A energia da viagem", "cor": "#16A34A",
        "papel": "Compara a mesma viagem de carro, de ônibus a diesel e de trem ou metrô elétrico em energia, custo e emissão de CO₂, com dados e fontes.",
        "ajuda": "A pessoa vê quanto a escolha do transporte pesa no bolso e no clima, sem estimativa tratada como garantia.",
        "quando": ["Toda vez que a Lia confere uma viagem"],
        "recebe": "A distância do trajeto em quilômetros.",
        "devolve": "Energia, custo e CO₂ por pessoa em cada alternativa, com as premissas.",
        "no_chat": "Em \"Segurança nas estações e energia\", no cartão da viagem, com premissas e fontes.",
        "entrega": "Repositório com dados, cálculos e fontes, comparação de alternativas (uma renovável), testes com usuários, vídeo de até 3 minutos e um .txt com os links.",
        "pasta": "entregas/sers", "rodar": "python comparar_energia.py",
        "regra": "Mesma necessidade (a viagem casa-trabalho), mesmo período e duas ou mais alternativas, uma delas renovável. Cada número com origem, unidade e premissa.",
        "nesta_versao": "Pronta no app e no script da entrega: a distância sai da rede, os fatores vêm de fontes oficiais (MCTI, EPE, Metrô, INMETRO, ANP) e o cartão da Lia mostra a comparação com o rótulo de estimativa, as premissas com tipo e ano e as fontes. As contas foram refeitas à mão em 16/11/2026.",
        "como_testar": "Mude a distância e compare as três alternativas no mesmo período (um mês de trabalho). A conta fica em \"Ver a conta passo a passo\".",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/sistema"}],
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
        "pasta": "entregas/mlam/entrega", "rodar": "python questao02_probabilidade.py  ·  … até questao06_logistica.py (um por questão)",
        "regra": "Base real e justificada: dado gerado ou fictício não vale. Desconto de 1,0 por item ausente e de 2,0 por entrega inadequada.",
        "nesta_versao": "Pronta: base real (SSP-SP, janeiro a setembro de 2026, raio de 300 m de 139 estações), questões 02 a 06 com interpretações e o relatório da questão 07 em PDF, com nome e RM na capa. Os resultados foram recalculados de forma independente em 16/11/2026.",
        "como_testar": "Abra \"Resultados das questões 02 a 06\" para ver probabilidade, testes de hipótese, regressões e matriz de confusão; abaixo fica o resumo da base por horário, tipo e estação.",
        "ver_funcionando": [{"rotulo": "Conversar com a Lia", "rota": "/sistema"}],
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
        "nesta_versao": "Agente em LangGraph, 7 fichas de transporte conferidas contra as páginas oficiais em 16/11/2026, golden de 26 mensagens, juiz validado com 7 respostas montadas (7 de 7) e a rodada antes e depois gravada em 16/11 com o Groq: 25/26 nas duas, com a análise dos erros no README.",
        "como_testar": "Escreva uma pergunta abaixo e veja cada etapa do grafo. Ou converse com a Lia e pergunte, por exemplo, como pedir a declaração de atraso.",
        "ver_funcionando": [{"rotulo": "Perguntar à Lia", "rota": "/sistema"}],
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
        "nesta_versao": "Entregue à parte pela equipe. O teste abaixo confere a Etapa 1 (sistema linear da frota) e as propriedades que a Etapa 2 exige de uma matriz digitada pela equipe, sem sugerir nenhuma.",
        "como_testar": "Resolva a Etapa 1 com os registros do Relatório I (dá para mudar os valores), veja a necessidade por região e digite a matriz da equipe para conferir se preserva o total e não gera negativos.",
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
        "nesta_versao": "Entregue à parte, no Wokwi, com o vídeo no YouTube.",
        "como_testar": "Abra o projeto no Wokwi, mude a leitura do sensor de nível e veja o alerta responder; o vídeo mostra o mesmo.",
        "ver_funcionando": [],
        "links": {"wokwi": "", "video": ""},
    },
]

# Entregues à parte, fora do sistema: não fazem sentido dentro da conversa (o COA depende do Wokwi,
# o MMC é um modelo matemático da frota, a CS tem integração opcional e é feita à mão pelo grupo).
# Continuam com página, teste e checklist próprios.
FORA_DO_SISTEMA = ("CS", "MMC", "COA")
A_PARTE: list[dict] = [m for m in NO_SISTEMA if m["cod"] in FORA_DO_SISTEMA]
NO_SISTEMA = [m for m in NO_SISTEMA if m["cod"] not in FORA_DO_SISTEMA]


# ---------------------------------------------------------------------------------------------
# O que a página de cada matéria mostra: um texto só (o que faz no sistema, como ajuda, quando
# entra em ação e a regra principal) e o caminho do dado por dentro dela.
# ---------------------------------------------------------------------------------------------
EXPLICACAO = {
    "PCP": "Quando a pessoa pergunta à Lia o que fazer (linha parada, celular roubado, declaração de atraso), o programa procura a orientação certa entre 16 respostas tiradas de páginas oficiais. A busca vale 3 pontos por palavra-chave e 1 ponto por palavra do título: com 6 pontos ou mais a confiança é ALTA, de 3 a 5 é MÉDIA, e abaixo de 3 o assistente diz que não encontrou. Cada resposta traz o que fazer, onde, a fonte, a data e o aviso de que não é canal oficial. Assim a pessoa não precisa procurar em cinco sites na hora do problema.",
    "DSA": "Os serviços ao passageiro (centrais de atendimento, ouvidorias, achados e perdidos, Defesa Civil) ficam numa lista encadeada feita pelo grupo: nenhuma lista pronta do Python, cada serviço é um nó que aponta para o próximo. A busca é linear e a ordenação é um merge sort que só religa os nós. Quando a orientação da Lia indica onde resolver, o canal de atendimento sai daqui, com o contato e a fonte, e a pessoa sabe a quem recorrer.",
    "SERS": "A partir da distância do trajeto, o sistema compara a mesma viagem de carro, de ônibus a diesel e de trem ou metrô elétrico em energia, custo e CO₂. Os fatores vêm de fontes oficiais (MCTI, EPE, Metrô, INMETRO, ANP) e cada número mostra origem e premissa. A conta aparece no cartão da viagem da Lia, sempre rotulada como estimativa, para a pessoa ver quanto a escolha pesa no bolso e no clima sem tratar o número como garantia.",
    "MLAM": "A matéria analisa as ocorrências registradas pela SSP-SP de janeiro a setembro de 2026, num raio de 300 m de 139 estações, com probabilidade, testes de hipótese e regressões. O resultado entra no cartão de segurança da estação, que mostra em que horário e que tipo de ocorrência é mais comum onde a pessoa embarca ou desce. A base conta registros perto da estação, sem o fluxo de passageiros: não é taxa de risco.",
    "PAI": "Um agente de três etapas (LangGraph): os guardrails barram dado pessoal e tentativas de manipulação, a busca acha a ficha certa entre as 7 fichas de transporte (FT-01 a FT-07) e o modelo responde só com o que está na ficha, citando-a. A Lia chama esse agente nas dúvidas de regra, como \"tenho 67 anos, pago metrô?\". Se a resposta não está nas fichas, o agente diz que não encontrou em vez de inventar.",
    "CS": "É uma entrega própria da matéria, feita à mão pelo grupo: quatro condições de sim ou não (falha numa linha, aviso de chuva, alagamento, horário de pico) viram tabela-verdade, expressão simplificada, mapa de Karnaugh e circuito, e um programa mostra a orientação. Usar IA nessas partes tira 4 pontos. O app tem a própria regra de prioridades para \"pode ir, saia mais cedo ou mude o caminho\"; a integração com o app é opcional e não foi feita.",
    "MMC": "É uma entrega própria da matéria, fora do app. Na etapa 1, o grupo recupera a frota de 72 ônibus por região (Norte, Sul, Leste e Oeste) resolvendo um sistema linear e mostrando se a solução é única. Na etapa 2, propõe como redistribuir os ônibus por uma transformação linear que mantém o total e não gera valores negativos, que é o que acontece quando ônibus de apoio cobrem uma linha parada. A política e a matriz são do grupo: o teste desta página só confere essas propriedades.",
    "COA": "É uma entrega própria da matéria, no Wokwi: um Raspberry Pi Pico, programado em MicroPython, lê um sensor de nível de água num ponto de alagamento e liga LED e buzina conforme o nível. Avisa no local quando a água sobe, antes de alguém tentar passar. O link do Wokwi e o vídeo são da equipe.",
}

#: Caminho do dado por dentro de cada matéria. "decisao" é o último passo, que se divide em duas saídas.
FLUXO = {
    "PCP": {
        "passos": [("Pergunta da pessoa", "escrita para a Lia"), ("Barreira de dado pessoal", "8 dígitos ou @: recusa e não registra"),
                   ("Normaliza o texto", "sem acento, minúsculas"), ("Busca por pontos", "+3 palavra-chave, +1 palavra do título")],
        "decisao": ("3 pontos ou mais?", ("Mostra a orientação", "o que fazer, onde, fonte, data e aviso"), ("Diz que não encontrou", "e sugere as categorias")),
    },
    "DSA": {
        "passos": [("Pedido do serviço", "nome, categoria ou id"), ("Lista encadeada", "cabeça, nós e cauda, sem lista pronta"),
                   ("Busca linear ou merge sort", "o merge sort só religa os nós")],
        "decisao": ("Achou o serviço?", ("Mostra o registro", "canal de atendimento, para quem é e fonte"), ("Avisa que não achou", "ou aponta o campo vazio")),
    },
    "SERS": {
        "passos": [("Distância da viagem", "em km, vinda da rede"), ("Fatores com fonte", "energia, CO₂ e custo por km"),
                   ("Calcula as três alternativas", "carro, ônibus a diesel, trem ou metrô"), ("Compara no mesmo período", "um mês de trabalho, ida e volta"),
                   ("Cartão da viagem na Lia", "com premissas, fontes e rótulo de estimativa")],
        "decisao": None,
    },
    "MLAM": {
        "passos": [("Base da SSP-SP", "jan a set de 2026, 139 estações, raio de 300 m"), ("Agrupa", "por estação, faixa de horário e tipo"),
                   ("Modelos das questões 02 a 06", "probabilidade, testes de hipótese, regressões"),
                   ("Cartão de segurança da estação", "aparece na viagem conferida pela Lia")],
        "decisao": None,
    },
    "PAI": {
        "passos": [("Pergunta", "pela Lia ou pelo terminal"), ("Guardrails", "dado pessoal e manipulação barrados antes do modelo"),
                   ("Busca nas fichas", "FT-01 a FT-07, palavra-chave vale 3 pontos"), ("Modelo responde só com a ficha", "e cita FT-xx")],
        "decisao": ("Achou a ficha?", ("Resposta com a ficha e a fonte", "curta e sem invenção"), ("Diz que não encontrou", "e orienta o canal oficial")),
    },
    "CS": {
        "passos": [("Quatro condições", "falha, chuva, alagamento e pico (0 ou 1)"), ("Tabela-verdade", "todas as combinações, à mão"),
                   ("Expressão simplificada", "álgebra booleana e Karnaugh, à mão"), ("Circuito lógico", "original e simplificado, à mão"),
                   ("Programa com a lógica simplificada", "recebe as entradas e mostra a orientação")],
        "decisao": None,
    },
    "MMC": {
        "passos": [("Registros do Relatório I", "4 equações, total de 72 ônibus"), ("Sistema Ax = b", "variáveis: ônibus por região"),
                   ("Solução e unicidade", "determinante e posto"), ("Necessidade por região", "passageiros ÷ capacidade do ônibus"),
                   ("Matriz de redistribuição da equipe", "transformação linear")],
        "decisao": ("Cada coluna soma 1 e nada fica negativo?", ("Política válida", "o total de ônibus se mantém"), ("Ajustar a matriz", "o enunciado não aceita")),
    },
    "COA": {
        "passos": [("Sensor de nível de água", "no ponto de alagamento"), ("Raspberry Pi Pico", "lê o valor em MicroPython"),
                   ("Compara com os limites", "atenção e alerta")],
        "decisao": ("Nível acima do limite?", ("Liga LED e buzina", "avisa no local"), ("Segue monitorando", "tudo apagado")),
    },
}


def _rotas(m: dict) -> list[dict]:
    """Os endereços do site em que a matéria aparece: a página dela (com o teste) e, se entra no app, o app."""
    base = f"/materias/{m['cod'].lower()}"
    rotas = [{"rotulo": f"Página da matéria {m['cod']}", "rota": base}, {"rotulo": "Teste da matéria", "rota": f"{base}?parte=teste"},
             {"rotulo": "Checklist da entrega", "rota": f"{base}?parte=checklist"}]
    if m["cod"] not in FORA_DO_SISTEMA:
        rotas += [{"rotulo": "O app com a Lia (na plataforma)", "rota": "/sistema"}, {"rotulo": "Só o app, para abrir no celular", "rota": "/app"}]
    return rotas


POR_CODIGO = {m["cod"]: m for m in NO_SISTEMA + A_PARTE}
for _cod, _m in POR_CODIGO.items():
    _m["arquivos"] = [{"rotulo": r, "caminho": c, "url": link(c)} for r, c in ARQUIVOS.get(_cod, [])]
    _m["pasta_url"] = link(_m["pasta"]) if _m["pasta"] else ""

for _cod, _m in POR_CODIGO.items():
    _m["explicacao"] = EXPLICACAO[_cod]
    _f = FLUXO[_cod]
    _d = _f["decisao"]
    _m["fluxo"] = {
        "passos": [{"rotulo": r, "sub": s} for r, s in _f["passos"]],
        "decisao": {"pergunta": _d[0], "sim": {"rotulo": _d[1][0], "sub": _d[1][1]}, "nao": {"rotulo": _d[2][0], "sub": _d[2][1]}} if _d else None,
    }
    _m["rotas"] = _rotas(_m)
