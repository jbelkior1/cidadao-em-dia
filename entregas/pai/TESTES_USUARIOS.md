# PAI — testes com usuários (roteiro e registro)

> **Este arquivo é para a equipe preencher.** Nada abaixo foi testado ainda: os campos de resultado
> estão vazios de propósito. Não invente números: o enunciado pede o relatório do teste de verdade.

O enunciado (seção 4.3) pede três indicadores:

| indicador | como medir |
|---|---|
| Acerto das orientações | resultado do juiz no golden (já em `saidas/`) com conferência manual de uma amostra (abaixo) |
| Tempo para encontrar a informação | cronometrar **pelo menos 5 pessoas de fora do grupo** em **3 tarefas simples** |
| Facilidade de utilização | questionário de **5 perguntas**, escala de 1 a 5, depois do teste |

## Como aplicar

- Pessoas de fora do grupo. Não anote nome, idade exata, telefone nem e-mail: use "Pessoa 1", "Pessoa 2"...
- Cada pessoa usa o assistente pelo terminal (`python main.py`) ou pela Lia no app (aba IA).
- Leia a tarefa, dispare o cronômetro e pare quando a pessoa disser a resposta certa. Não ajude.
- Se passar de 3 minutos, anote "não achou" e siga.

## As 3 tarefas

| # | tarefa | resposta certa (ficha) |
|---|---|---|
| 1 | Descobrir como pedir a declaração de atraso de uma viagem de metrô feita hoje | site do Metrô, Declaração de Ocorrências, depois do fim da ocorrência (FT-02) |
| 2 | Descobrir se uma pessoa de 67 anos paga o metrô e o que ela precisa mostrar | não paga; basta um documento que prove a idade (FT-04) |
| 3 | Descobrir onde procurar uma mochila esquecida no trem da CPTM | achados e perdidos da CPTM, pelos canais da ficha (FT-05) |

## Tempo (segundos)

| Pessoa | Tarefa 1 | Tarefa 2 | Tarefa 3 | Usou menu ou pergunta livre? |
|---|---|---|---|---|
| Pessoa 1 | | | | |
| Pessoa 2 | | | | |
| Pessoa 3 | | | | |
| Pessoa 4 | | | | |
| Pessoa 5 | | | | |
| **Média** | | | | |

## Questionário de facilidade (1 = discordo totalmente, 5 = concordo totalmente)

1. Foi fácil fazer a pergunta.
2. A resposta foi clara.
3. Eu confiaria na resposta para agir (sabendo que devo confirmar no canal oficial).
4. Ficou claro de onde veio a informação (a ficha citada).
5. Eu usaria o assistente de novo.

| Pessoa | P1 | P2 | P3 | P4 | P5 | Média |
|---|---|---|---|---|---|---|
| Pessoa 1 | | | | | | |
| Pessoa 2 | | | | | | |
| Pessoa 3 | | | | | | |
| Pessoa 4 | | | | | | |
| Pessoa 5 | | | | | | |
| **Média** | | | | | | |

## Conferência manual do juiz (amostra)

Pegue pelo menos 8 casos de `saidas/rodada_depois.json` (sugestão: 4 acertos e todos os erros), leia a
resposta e diga se concorda com o juiz.

| caso | juiz disse | a equipe concorda? | observação |
|---|---|---|---|
| #8 | | | ver no README o achado sobre a máscara do avaliador |
| #107 | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

## Comentários e ajustes

O que as pessoas estranharam e o que o grupo mudou por causa disso (arquivo e linha).

- A PREENCHER PELO GRUPO
