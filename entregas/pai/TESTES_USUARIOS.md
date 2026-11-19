# PAI: testes com usuários (roteiro e registro)

Integrantes: João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e
Thiago de Oliveira Coelho Souza (RM 568783).

O enunciado (seção 4.3) pede três indicadores:

| indicador | como medir |
|---|---|
| Acerto das orientações | resultado do juiz no golden (já em `saidas/`) com conferência manual de uma amostra (abaixo) |
| Tempo para encontrar a informação | cronometrar **pelo menos 5 pessoas de fora do grupo** em **3 tarefas simples** |
| Facilidade de utilização | questionário de **5 perguntas**, escala de 1 a 5, depois do teste |

## Como foi aplicado

- Teste feito em 19/11/2026 por 5 pessoas de fora do grupo, pelo formulário do portal (`/avaliar/teste`),
  que guarda as respostas sem nome nem dado pessoal (só o hash de um código aleatório do aparelho). Aqui
  elas aparecem como "Pessoa 1" a "Pessoa 5", na ordem em que enviaram.
- Em cada tarefa, a pessoa clica em "Começar", procura a resposta com a Lia no app e clica em "Achei"; o
  tempo vai do primeiro clique ao segundo, medido pelo relógio do aparelho. Depois ela marca a resposta
  entre três alternativas, e o formulário confere se acertou. Passando de 5 minutos, conta como "não achou".
- Os dados ficam na tabela `datempo.avaliacoes` do banco do projeto.

## As 3 tarefas

| # | tarefa | resposta certa (ficha) |
|---|---|---|
| 1 | Descobrir como pedir a declaração de atraso de uma viagem de metrô feita hoje | site do Metrô, Declaração de Ocorrências, depois do fim da ocorrência (FT-02) |
| 2 | Descobrir se uma pessoa de 67 anos paga o metrô e o que ela precisa mostrar | não paga; basta um documento que prove a idade (FT-04) |
| 3 | Descobrir onde procurar uma mochila esquecida no trem da CPTM | achados e perdidos da CPTM, pelos canais da ficha (FT-05) |

## Tempo (segundos)

| Pessoa | Tarefa 1 | Tarefa 2 | Tarefa 3 | Acertos |
|---|---|---|---|---|
| Pessoa 1 | 6 | 2 | 11 | 3 de 3 |
| Pessoa 2 | 19 | 1 | 43 | 3 de 3 |
| Pessoa 3 | 8 | 1 | 4 | 2 de 3 (errou a tarefa 1) |
| Pessoa 4 | 26 | 1 | 34 | 3 de 3 |
| Pessoa 5 | 14 | 24 | 11 | 3 de 3 |
| **Média** | **14,6** | **5,8** | **20,6** | **14 de 15 (93%)** |

Acerto por tarefa: tarefa 1, 4 de 5 (80%); tarefa 2, 5 de 5; tarefa 3, 5 de 5. Ninguém passou do limite
de 5 minutos.

## Questionário de facilidade (1 = discordo totalmente, 5 = concordo totalmente)

1. Foi fácil fazer a pergunta.
2. A resposta foi clara.
3. Eu confiaria na resposta para agir (sabendo que devo confirmar no canal oficial).
4. Ficou claro de onde veio a informação (a ficha citada).
5. Eu usaria o assistente de novo.

| Pessoa | P1 | P2 | P3 | P4 | P5 | Média |
|---|---|---|---|---|---|---|
| Pessoa 1 | 5 | 5 | 4 | 5 | 5 | 4,8 |
| Pessoa 2 | 5 | 5 | 5 | 5 | 5 | 5,0 |
| Pessoa 3 | 5 | 5 | 5 | 5 | 5 | 5,0 |
| Pessoa 4 | 5 | 5 | 5 | 5 | 5 | 5,0 |
| Pessoa 5 | 5 | 5 | 5 | 5 | 5 | 5,0 |
| **Média** | **5,0** | **5,0** | **4,8** | **5,0** | **5,0** | **5,0** (4,96) |

No formulário, a pergunta 4 saiu como "Ficou claro de onde veio a informação." e a 5 como "Eu usaria o
Dá Tempo? de novo.", porque o teste foi feito no app, onde a Lia chama o agente das fichas.

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

- **Comentários:** o campo era opcional e nenhuma das 5 pessoas escreveu comentário ou sugestão. O que
  segue sai dos números.
- **Tarefa 2 não mediu o sistema.** Quatro das cinco pessoas responderam em 1 ou 2 segundos se uma pessoa
  de 67 anos paga o metrô. Não dá tempo de perguntar à Lia e ler a resposta: elas responderam de cabeça.
  A média de 5,8 s dessa tarefa mede o quanto a gratuidade do idoso é conhecida, não a facilidade de achar
  a informação no app. Ajuste para a próxima rodada: trocar a tarefa 2 por uma que dependa da ficha, como
  "quanto custa a integração do ônibus com o metrô no Bilhete Único" (R$ 9,38, FT-06). A troca não foi
  feita no formulário agora para não misturar, na mesma coluna do banco, respostas de tarefas diferentes.
- **Tarefa 1 teve o único erro** (Pessoa 3, em 8 s). O formulário guarda só se acertou, não qual
  alternativa foi marcada, então não dá para saber o que confundiu. Fica para a próxima rodada guardar a
  alternativa escolhida.
- **Facilidade quase no teto (4,96 de 5).** Com 5 pessoas e notas quase todas 5, o número mostra que
  ninguém teve dificuldade, mas não separa bem o que pode melhorar. A única nota abaixo de 5 foi na
  confiança para agir (Pessoa 1, nota 4), o que bate com o aviso do assistente de confirmar no canal oficial.
- **Ajuste feito no app por causa do teste:** o cartão de energia passou a dizer, na mesma linha dos
  números, que a conta é estimativa por médias oficiais (`sistema/web/src/componentes/Cartoes.tsx`), porque
  uma pessoa respondeu "em parte" a essa pergunta (detalhes no teste da SERS, `entregas/sers/TESTES_USUARIOS.md`).
