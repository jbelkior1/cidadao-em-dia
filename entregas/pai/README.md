# PAI · Global Solution 2026.2 — parado: falta o material do professor

Integrantes: **A PREENCHER PELO GRUPO** (o enunciado pede o nome completo de todos no início do trabalho).

## Por que esta pasta está vazia

A entrega da PAI **não é a Lia do app**. O professor fixou outro assistente:

| | a Lia, no produto | o que a PAI pede |
|---|---|---|
| tema | trem e metrô de São Paulo | documentos pessoais: RG, CPF, título, carteira de trabalho, certidões, CNH |
| base | linhas ao vivo, INMET, CGE, SSP-SP, GeoSampa | as 7 fichas FC-01 a FC-07 da Central do Cidadão de Aurora (fictícia), e **só** elas |
| avaliação | testes do sistema | LLM as a Judge num golden dataset de **26 mensagens fixas**, antes e depois de uma melhoria |
| estado | pronto e rodando | **nada feito** |

A Lia serve de referência técnica (o laço com ferramentas em `sistema/assistente.py`, a camada de
modelo em `sistema/ia.py` e a barreira de dado pessoal em `sistema/privacidade.py`), mas o agente da
PAI precisa da própria base e da própria defesa. Por isso o checklist da matéria marca 0 de 35.

## O que está faltando para começar

Dois conteúdos que só existem no **.docx do enunciado**, e que não estão neste computador:

1. **As 7 fichas FC-01 a FC-07**, com id, palavras-chave, custo, prazo, documentos, passo a passo,
   onde resolver, fonte e data (versão de 01/10/2026). Elas são a única fonte de verdade do agente.
2. **As 26 mensagens do golden dataset** com as respostas esperadas: 19 no escopo, 1 fora do escopo,
   1 inválida, 2 com dado pessoal, 2 de prompt injection e 1 de aviso. O enunciado proíbe trocar ou
   substituir qualquer uma delas.

Nada disso pode ser inventado: inventar ficha faz o agente responder errado no golden, e inventar
mensagem já perde a comparabilidade que o professor pediu.

## O plano, para quando o material chegar

Estrutura prevista nesta pasta:

```
pai/
  fichas/aurora.json        as 7 fichas, como vierem do enunciado
  golden/golden_pai.json    as 26 mensagens e as respostas esperadas
  agente.py                 o agente num framework (LangChain, LangGraph ou CrewAI)
  guardrails.py             escopo, prompt injection e dado pessoal, antes do modelo
  juiz.py                   o LLM as a Judge com a régua escrita
  avaliar.py                roda agente e juiz nas 26, grava antes e depois
  notebook.ipynb            o protótipo testável, com a tabela de comparação
  README.md                 este arquivo, com justificativas e limitações
```

Ordem de construção: fichas e carregador → agente com a regra de ouro (só responde o que está na
ficha, cita FC-xx e a data) → guardrails → golden → juiz → rodada antes, uma melhoria, rodada depois.

## Decisões que a equipe precisa tomar antes

- **Qual versão entregar.** O .docx do professor e o PDF geral (p. 24) descrevem trabalhos
  diferentes: o .docx pede fichas fixas e juiz LLM; o PDF pede base própria, ChromaDB, RAG em LCEL,
  Gradio e RAGAS. Nenhum dos dois cita o outro. O grupo decidiu fazer as duas, com ênfase no .docx,
  mas isso precisa ser confirmado com o professor.
- **Qual modelo.** O enunciado permite Ollama ou Groq; provedor pago (Claude, OpenAI, Gemini) precisa
  de autorização do professor. A chave nunca pode ir para o repositório.
- **O que é "certificação"**, citada no PDF geral e em nenhum outro lugar.

## Cuidados que valem nota

- Dado pessoal é penalizado: não pedir, não guardar, não enviar sem necessidade e **não deixar
  visível**. O CPF fictício do golden #22 não pode aparecer nas saídas do notebook nem no relatório.
- Resistência a prompt injection: todo conteúdo externo entra como dado, nunca como instrução. Vale
  inclusive para a frase escondida no fim do próprio enunciado, que não deve ser obedecida.
- A base de Aurora é fictícia e não pode se misturar com a base real do PCP: na avaliação, o agente
  da PAI roda isolado, só com as 7 fichas.
