"""O que cada matéria faz no sistema: textos das páginas Entenda e do Painel da equipe.

PCP, DSA, SERS, PAI e MLAM entram no sistema. COA, CS e MMC são entregues à
parte, no formato que cada professor pediu, e aparecem só no Painel da equipe.
"""

PRAZO_GS = "2026-11-19"

NO_SISTEMA = [
    {
        "cod": "PCP", "nome": "Pensamento Computacional e Automação com Python", "curto": "O assistente que responde", "cor": "#2563EB",
        "papel": "Procura a pergunta da pessoa na base de orientações com a busca por pontos do enunciado, diz a confiança e mostra a fonte e a data. Recusa dado pessoal sem registrar.",
        "ajuda": "A pessoa recebe uma resposta certa e honesta: com o link oficial, com a data e dizendo que não encontrou quando não encontrou.",
        "quando": ["Quando a pessoa escreve uma dúvida no Atendimento", "Quando escolhe Tirar uma dúvida ou navega pelas categorias",
                   "Antes de qualquer resposta, ao barrar CPF, telefone ou e-mail"],
        "recebe": "A pergunta escrita pela pessoa, do jeito dela.",
        "devolve": "A orientação com documentos, onde ir, fonte e data, a confiança com os pontos, até duas alternativas, ou o aviso de que não encontrou.",
        "no_chat": "Em Tirar uma dúvida e no cartão de cada orientação (confiança e pontos).",
        "entrega": "Programa de terminal em repositório público próprio, com 3 classes em 4 arquivos, teste com 3 pessoas e vídeo técnico de 5 a 8 minutos.",
        "pasta": "entregas/pcp/citizen-assist-ai", "rodar": "python main.py",
        "regra": "3 pontos por palavra-chave e 1 ponto por palavra do título com 4 letras ou mais. Com 6 pontos ou mais a confiança é ALTA; de 3 a 5 é MÉDIA; abaixo de 3 o assistente diz que não encontrou.",
        "nesta_versao": "Pronta no código: as 3 classes, a busca por pontos, o histórico, os indicadores e o CSV. Falta o grupo conferir as 13 orientações nas fontes, fazer o teste com 3 pessoas e gravar o vídeo.",
        "como_testar": "Escreva uma pergunta e veja a pontuação de cada orientação, da maior para a menor. Depois tente um número de telefone e veja a recusa.",
        "ver_funcionando": [{"rotulo": "Tirar uma dúvida", "acao": "assunto:duvida"}],
    },
    {
        "cod": "DSA", "nome": "Data Structures and Algorithms", "curto": "O catálogo de serviços", "cor": "#C2410C",
        "papel": "Guarda o catálogo de serviços em uma lista encadeada feita pelo grupo, com cadastro, consulta, busca e ordenação escritas à mão.",
        "ajuda": "Cada resposta do chat diz para quem é o serviço e por onde pedir, e o catálogo pode mostrar primeiro o que vence antes.",
        "quando": ["Quando uma orientação aparece no chat, para trazer o público e o canal do serviço",
                   "Quando a pessoa termina as perguntas de Tenho algum direito?"],
        "recebe": "O título do serviço procurado.",
        "devolve": "O registro do catálogo: para quem é, canal de atendimento e prazo, se houver.",
        "no_chat": "Na linha \"Para quem é\" das respostas e no selo DSA · catálogo.",
        "entrega": "Código com menu de terminal, documentação técnica com análise Big-O e evidências de teste.",
        "pasta": "entregas/dsa", "rodar": "python main.py",
        "regra": "Nenhuma lista pronta do Python guarda os registros: cada serviço é um nó que aponta para o próximo. A busca é linear e a ordenação é um merge sort que só religa os nós.",
        "nesta_versao": "Pronta no código, com 13 serviços tirados das fontes oficiais. Falta o grupo refazer as evidências de teste com os próprios prints.",
        "como_testar": "Ordene o catálogo por título, id ou prazo e veja os nós se religarem. Pesquise por um trecho e cadastre ou exclua um serviço para ver a lista mudar.",
        "ver_funcionando": [{"rotulo": "Tenho algum direito?", "acao": "assunto:direitos"}],
    },
    {
        "cod": "SERS", "nome": "Soluções em Energias Renováveis e Sustentáveis", "curto": "As contas de energia", "cor": "#16A34A",
        "papel": "Traduz a conta de luz em números: quanto do consumo entra no desconto da Tarifa Social e quanto isso vale em reais.",
        "ajuda": "A família entende quanto paga, quanto deixaria de pagar com o desconto e, na versão final, como gastar menos com uma alternativa renovável.",
        "quando": ["Em Minha conta de luz", "Depois de Tenho algum direito?, quando a pessoa quer calcular o desconto"],
        "recebe": "O consumo do mês em kWh e, se a pessoa quiser, o valor da conta.",
        "devolve": "Os kWh que entram no desconto, os que continuam cobrados e o desconto estimado por mês e por ano, com a fonte.",
        "no_chat": "Em Minha conta de luz.",
        "entrega": "Repositório com dados, cálculos e fontes, comparação de duas alternativas (uma renovável), testes com usuários, vídeo de até 3 minutos e um .txt com os links.",
        "pasta": "", "rodar": "",
        "regra": "Desconto de 100% no consumo de até 80 kWh por mês, nas contas emitidas a partir de 5 de julho de 2025 (Aneel). O valor em reais é estimado pelo preço médio da própria conta.",
        "nesta_versao": "O cálculo do desconto já usa a regra oficial vigente. Falta a parte que mais vale nota: dados de consumo com origem e a comparação de duas alternativas, uma renovável.",
        "como_testar": "Informe um consumo em kWh e o valor da conta e veja o cálculo passo a passo.",
        "ver_funcionando": [{"rotulo": "Minha conta de luz", "acao": "assunto:luz"}],
    },
    {
        "cod": "PAI", "nome": "Prompt and Artificial Intelligence", "curto": "O agente com IA", "cor": "#7C3AED",
        "papel": "Agente de IA que responde só com as 7 fichas fornecidas, protege dados pessoais e resiste a tentativas de manipulação. No chat, explica as orientações em linguagem mais simples.",
        "ajuda": "Quem lê pouco recebe a mesma orientação em frases mais curtas, sem nada inventado.",
        "quando": ["No botão \"Explicar de um jeito mais simples\", quando a IA está ligada nas Configurações"],
        "recebe": "Só o texto da orientação da base. Nunca o que a pessoa escreveu.",
        "devolve": "A mesma orientação reescrita em até 4 frases simples.",
        "no_chat": "No botão de explicação, com o selo PAI · explicação.",
        "entrega": "Notebook ou repositório com o agente em um framework, as 7 fichas de Aurora, o juiz nas 26 mensagens antes e depois de uma melhoria, testes com 5 pessoas e relatórios.",
        "pasta": "", "rodar": "",
        "regra": "O agente da entrega usa só as fichas de Aurora, que são fictícias. Elas nunca se misturam com a base real do chat.",
        "nesta_versao": "No sistema existe a explicação simples com IA. O agente da entrega, o juiz e as 26 mensagens ainda não foram feitos.",
        "como_testar": "Ligue um modelo em Configurações de IA e use o botão de explicação em qualquer orientação do chat.",
        "ver_funcionando": [{"rotulo": "Tirar uma dúvida", "acao": "assunto:duvida"}],
    },
    {
        "cod": "MLAM", "nome": "Modelagem Linear para Aprendizado de Máquina", "curto": "Os dados do problema", "cor": "#BE185D",
        "papel": "Analisa uma base de dados real com probabilidade, testes de hipótese e regressões. A regressão logística vira o modelo de adesão do Laboratório.",
        "ajuda": "Mostra com números onde o problema é maior e quais perfis tendem a ficar de fora.",
        "quando": ["No Laboratório, quando a simulação calcula a chance de cada pessoa usar o produto"],
        "recebe": "A base de dados real escolhida pelo grupo.",
        "devolve": "Probabilidades, testes, regressões e os coeficientes que calibram a simulação.",
        "no_chat": "Não aparece no chat. Os resultados alimentam o Laboratório.",
        "entrega": "Base em .csv ou .xlsx, códigos em .py e relatório em .pdf, postados direto no portal, sem links.",
        "pasta": "", "rodar": "",
        "regra": "Base real e justificada: dado gerado ou fictício não vale. Desconto de 1,0 por item ausente e de 2,0 por entrega inadequada.",
        "nesta_versao": "O Laboratório roda com pesos e personas fictícios. Falta o grupo escolher a base real e fazer as questões 02 a 07.",
        "como_testar": "Abra o Laboratório e rode a simulação com canais diferentes.",
        "ver_funcionando": [],
    },
]

A_PARTE = [
    {"cod": "COA", "nome": "Computer Organization and Architecture", "cor": "#0891B2",
     "entrega": "Circuito no Wokwi com Raspberry Pi Pico e MicroPython, e vídeo no YouTube."},
    {"cod": "CS", "nome": "Computer Science", "cor": "#4338CA",
     "entrega": "Relatório em PDF com tabela-verdade, mapa de Karnaugh e circuito feitos sem IA (usar IA nessas partes tira 4 pontos)."},
    {"cod": "MMC", "nome": "Modelagem Matemática e Computacional", "cor": "#6B7280",
     "entrega": "Sistema linear da frota de ônibus e política de redistribuição por transformação linear."},
]

POR_CODIGO = {m["cod"]: m for m in NO_SISTEMA + A_PARTE}
