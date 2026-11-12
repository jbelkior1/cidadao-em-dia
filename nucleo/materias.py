"""Cadastro das matérias: cor, papel no sistema, onde aparece e checklist da entrega.

As páginas das matérias e o painel da equipe são gerados a partir daqui.
"""

NOME_DO_SISTEMA = "Cidadão em Dia"
FRASE_DO_SISTEMA = "Tire dúvidas sobre documentos, descubra direitos que você pode ter e não perca prazos."
PRAZO_GS = "2026-11-19"

ORDEM = ["PCP", "PAI", "DSA", "COA", "SERS", "MLAM"]          # entram no sistema
A_PARTE = ["CS", "MMC"]                                        # feitas por fora, só na lista de entregáveis
TODAS = ORDEM + A_PARTE

REGISTRO = {
    "PCP": dict(
        nome="Pensamento Computacional e Automação com Python", curto="O cérebro", cor="#3b6ea8", icone=":material/psychology:",
        papel="Encontra a orientação certa na base, aplica as regras de orientação, mostra a fonte e a data, avisa quando não sabe e recusa dados pessoais.",
        aparece_em=["Tirar uma dúvida", "Meus direitos", "Isso é golpe?"],
        entrega="Repositório público com a estrutura do enunciado, vídeo técnico de 5 a 8 minutos mostrando o terminal e um .txt com os links.",
        checklist=["Base JSON com 10 ou mais orientações reais, com fonte e data", "Três classes (orientação, base de conhecimento e assistente)",
                   "Busca por pontuação com nível de confiança", "Histórico e CSV de indicadores", "Recusa de dados pessoais sem registrar",
                   "Teste com 3 pessoas e pelo menos 10 atendimentos", "README e repositório público", "Vídeo técnico de 5 a 8 min (terminal)",
                   ".txt com os links enviado no portal"]),
    "PAI": dict(
        nome="Prompt and Artificial Intelligence", curto="O agente com IA", cor="#7a52c7", icone=":material/smart_toy:",
        papel="Responde perguntas sobre documentos quando a busca simples não tem confiança, sempre citando a ficha e a data. No futuro, dá voz às personas da simulação.",
        aparece_em=["Tirar uma dúvida", "Meus direitos", "Simulação da sociedade"],
        entrega="Protótipo testável com as fichas de Aurora, o juiz nas 26 mensagens antes e depois de uma melhoria e o relatório de testes com pessoas.",
        checklist=["Confirmar com o professor qual enunciado vale", "Fichas de Aurora organizadas", "Agente montado no framework escolhido",
                   "Juiz nas 26 mensagens (antes)", "Melhoria aplicada", "Juiz nas 26 mensagens (depois)", "Teste de resistência a prompt injection",
                   "Testes com 5 pessoas em 3 tarefas", "Relatório com justificativas e limitações"]),
    "CS": dict(
        nome="Computer Science", curto="A regra lógica", cor="#2f6fb5", icone=":material/account_tree:",
        papel="Feita à parte: o relatório com tabela-verdade, Karnaugh e circuito, sem ligação com o sistema.",
        aparece_em=[],
        entrega="Relatório em PDF com tabela-verdade, expressão, Karnaugh e circuito feitos à mão, prints do simulador e o programa que testa todas as combinações. IA só no texto.",
        checklist=["Problema e 3 ou 4 variáveis definidos", "Tabela-verdade feita à mão", "Expressão canônica", "Simplificação com Karnaugh, à mão",
                   "Circuito original e simplificado no simulador", "Programa que testa todas as combinações", "Relatório em PDF (IA só no texto)"]),
    "DSA": dict(
        nome="Data Structures and Algorithms", curto="O catálogo de prazos", cor="#1d9a8e", icone=":material/event_note:",
        papel="Guarda os direitos e seus prazos numa lista encadeada, com cadastro, busca e ordenação por prazo.",
        aparece_em=["Conte o que precisa", "Meus direitos"],
        entrega="Código com lista encadeada própria, documentação, Big-O de inserir, buscar, excluir e ordenar e testes com prints.",
        checklist=["Lista encadeada própria (sem a lista pronta)", "Cadastro com menu e validação", "Busca e ordenação por prazo",
                   "Big-O de cada operação", "Documentação técnica", "Testes com prints, incluindo lista vazia"]),
    "COA": dict(
        nome="Computer Organization and Architecture", curto="O medidor de energia", cor="#e08a2e", icone=":material/bolt:",
        papel="Mede o consumo de energia da casa no Pico e avisa com LED quando a faixa com desconto está acabando.",
        aparece_em=["Minha conta de luz", "Meus direitos"],
        entrega="Link do projeto no Wokwi (circuito e código em MicroPython) e vídeo mostrando o problema e o funcionamento.",
        checklist=["Confirmar com o professor se o Pico W vale", "Circuito montado no Wokwi", "Código em MicroPython",
                   "Leituras mudando e LED respondendo no vídeo", "Vídeo no YouTube", "Link e nomes enviados no portal"]),
    "SERS": dict(
        nome="Soluções em Energias Renováveis e Sustentáveis", curto="A calculadora de energia", cor="#3f9d54", icone=":material/solar_power:",
        papel="Calcula consumo, conta do mês e quanto a família deixa de economizar sem o desconto.",
        aparece_em=["Minha conta de luz", "Meus direitos"],
        entrega="Repositório com códigos, dados com origem e premissas, cálculos, comparação de alternativas e referências, vídeo de até 3 minutos e .txt.",
        checklist=["Dados com origem, unidade, período e premissas", "Cálculo de consumo", "Comparação de 2 alternativas, 1 renovável",
                   "Justificativa por custo, viabilidade e impacto", "Integração com o assistente", "Registro dos testes com pessoas",
                   "Vídeo de até 3 min", ".txt com os links"]),
    "MLAM": dict(
        nome="Modelagem Linear para Aprendizado de Máquina", curto="Os dados do problema", cor="#d04f87", icone=":material/bar_chart:",
        papel="Mostra com dados reais onde mais famílias deixam de receber o que têm direito e dá o modelo de adesão da simulação da sociedade.",
        aparece_em=["Comece aqui", "Simulação da sociedade"],
        entrega="Base real (.csv ou .xlsx), códigos (.py) e relatório estatístico (.pdf), enviados direto no portal.",
        checklist=["Base real escolhida e justificada", "Probabilidades (Q2)", "Testes de hipótese (Q3)", "Regressão simples (Q4)",
                   "Regressão múltipla (Q5)", "Regressão logística e matriz de confusão (Q6)", "Relatório para um cliente (Q7)",
                   "Arquivos .csv, .py e .pdf no portal"]),
    "MMC": dict(
        nome="Modelagem Matemática e Computacional", curto="A frota de ônibus", cor="#6b7280", icone=":material/directions_bus:",
        papel="Módulo independente: redistribui a frota de ônibus por sistema linear e transformação linear. Não entra no fluxo do cidadão.",
        aparece_em=[],
        entrega="Etapas 1 e 2 do enunciado com o código Python. Formato a confirmar com o professor.",
        checklist=["Confirmar o formato com o professor", "Variáveis e modelo (etapa 1)", "Sistema em matriz e prova de solução única",
                   "Solução em Python e verificação", "Necessidade por região e desequilíbrios (etapa 2)", "Política e matriz da transformação",
                   "Prova de que mantém o total e não gera negativos"]),
}


# ---------------------------------------------------------------- explicação didática de cada matéria
EXTRA = {
    "PCP": dict(
        ajuda="Faz o cidadão receber uma resposta certa e honesta: com fonte, com data e dizendo que não sabe quando não sabe.",
        quando=["Entende o que a pessoa precisa no Atendimento", "Responde as perguntas de Tirar uma dúvida",
                "Aplica as regras e traz a fonte em Meus direitos", "Confere a mensagem em Isso é golpe?"],
        entrada="O que a pessoa escreveu e as respostas de sim ou não.",
        saida="A orientação, a confiança, a fonte e a data, ou o aviso de que não sabe. Recusa dados pessoais.",
        como_testar="Pergunte 'perdi meu RG' e veja a confiança. Depois digite um número de telefone e veja a recusa.",
        nesta_versao="Busca simples por palavra-chave numa base de exemplo. A versão final usa as classes e a regra de pontuação do enunciado."),
    "PAI": dict(
        ajuda="Quando a pergunta foge da base, o agente ainda ajuda com documentos, sem inventar: só responde o que está nas fichas.",
        quando=["Responde em Tirar uma dúvida quando a busca não teve confiança", "Lista o que levar no comprovante de Meus direitos",
                "Vai dar voz às personas da simulação (futuro)"],
        entrada="A pergunta que a busca não respondeu com confiança.",
        saida="A resposta com a ficha citada e a data, ou que não sabe.",
        como_testar="Pergunte algo sobre documentos que não esteja na base, como 'que documentos levar para atualizar o cadastro'.",
        nesta_versao="Busca em fichas fictícias, ainda sem IA. A versão final é o agente com as fichas de Aurora e o juiz nas 26 mensagens."),
    "DSA": dict(
        ajuda="Faz o cidadão não perder prazos: guarda cada direito com a sua data e mostra primeiro o que vence antes.",
        quando=["Mostra os prazos que vencem primeiro no Atendimento", "Traz o prazo do comprovante de Meus direitos"],
        entrada="O nome do direito procurado.",
        saida="O prazo, o que fazer e quantos dias faltam, e a lista ordenada pelo prazo.",
        como_testar="Cadastre um direito com uma data e veja a lista se reordenar pelo prazo mais próximo.",
        nesta_versao="Catálogo usando a lista pronta do Python. A versão final usa a lista encadeada da equipe."),
    "COA": dict(
        ajuda="Mostra quanto a casa gastou de energia no mês e acende uma luz quando a faixa com desconto está acabando.",
        quando=["Lê o medidor em Minha conta de luz", "Fornece o consumo quando a pessoa escolhe 'Usar o medidor da casa' em Meus direitos"],
        entrada="A leitura de consumo feita pelo Pico (hoje simulada).",
        saida="Os kWh do mês e a cor da luz: verde, amarela ou vermelha.",
        como_testar="Clique em Ler o medidor algumas vezes e veja o consumo e a cor da luz mudarem.",
        nesta_versao="Leitura simulada. A versão final recebe a leitura do Pico W no Wokwi."),
    "SERS": dict(
        ajuda="Traduz energia em dinheiro: quanto a família gasta, quanto paga e quanto o desconto vale por ano.",
        quando=["Calcula a conta em Minha conta de luz", "Calcula quanto vale o desconto no comprovante de Meus direitos"],
        entrada="O consumo em kWh: informado, calculado pelos aparelhos ou lido no medidor.",
        saida="A conta estimada do mês e quanto o desconto vale por ano.",
        como_testar="Mexa nas horas de uso dos aparelhos e veja a conta e o desconto mudarem.",
        nesta_versao="Calculadora com tarifa e faixa de exemplo. A versão final usa dados com origem e premissas."),
    "MLAM": dict(
        ajuda="Mostra com números onde o problema é maior e estima quantas pessoas usariam o produto.",
        quando=["Dá os números do problema em Como o sistema funciona", "É o modelo de adesão da Simulação da sociedade"],
        entrada="A base de dados real (hoje, dados fictícios).",
        saida="Gráficos, regressões e a chance de cada perfil usar o produto.",
        como_testar="Veja o gráfico abaixo e rode a Simulação da sociedade com canais diferentes.",
        nesta_versao="Gráfico e população com dados fictícios. A versão final usa a base real e as regressões do relatório."),
}
for _c, _d in EXTRA.items():
    REGISTRO[_c].update(_d)
REGISTRO["DSA"]["aparece_em"] = ["Conte o que precisa", "Meus direitos"]
REGISTRO["PCP"]["aparece_em"] = ["Conte o que precisa", "Tirar uma dúvida", "Meus direitos", "Isso é golpe?"]
REGISTRO["MLAM"]["aparece_em"] = ["Simulação da sociedade"]
