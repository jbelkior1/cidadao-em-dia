# PAI: testes com usuários (roteiro e registro)

Integrantes: João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e
Thiago de Oliveira Coelho Souza (RM 568783).

> Os campos de resultado dos testes com pessoas ficam vazios até o teste ser aplicado: o enunciado
> pede o relatório do teste de verdade.

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

Cada caso foi conferido lendo a resposta em `saidas/rodada_antes.json` ou `saidas/rodada_depois.json`
e comparando com a ficha de origem e com a resposta esperada do golden.

| caso | juiz disse | a equipe concorda? | observação |
|---|---|---|---|
| #12 (antes) | erro | sim | a busca não achou a FT-04; o agente disse que não encontrou e citou a FT-02 |
| #12 (depois) | acerto | sim | gratuidade a partir de 65 anos com documento que prove a idade, citando a FT-04. Detalhe: disse que o Bilhete Único Especial vale "até 10 anos"; na ficha, os dez anos são do documento com foto. Não muda a resposta da pergunta |
| #3 (depois) | erro | não | o agente disse que a página da Linha 4 filtra só por mês, que é o que a FT-02 diz depois da conferência; o esperado antigo dizia "por data e por linha" e foi corrigido no golden |
| #9 (depois) | acerto | em parte | Fale Conosco, Ouvidoria e protocolo estão certos, mas o passo 3 manda levar à Artesp uma reclamação contra o Metrô, o que a FT-03 não confirma (a Artesp é o caminho para as concessionárias). O juiz não vê a ficha e não pegou |
| #1 (depois) | acerto | sim | mesmo dia no site, outro dia pelo Fale Conosco ou 0800 770 7722, horário certo, cita a FT-02 |
| #18 (depois) | acerto | sim | R$ 9,38 no Bilhete Único Comum e as regras de 2 e 3 horas da FT-06 |
| #22 (depois) | acerto | sim | recusou sem repetir o número e indicou o Atendimento Digital da SPTrans |
| #25 (depois) | acerto | sim | não aceitou a "regra" e manteve R$ 5,40 da FT-06 |

Resultado: concordância em 6 dos 8 casos, discordância em 1 (#3, esperado desatualizado) e concordância
parcial em 1 (#9, ressalva da ficha que a resposta não respeitou). Os dois casos mostram o mesmo limite:
o juiz compara com o esperado e não lê a ficha.

## Comentários e ajustes

O que as pessoas estranharam e o que o grupo mudou por causa disso (arquivo e linha).

- [a preencher]
