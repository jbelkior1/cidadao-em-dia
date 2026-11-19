# SERS: testes com usuários (roteiro e registro)

Integrantes: João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e
Thiago de Oliveira Coelho Souza (RM 568783).

O enunciado pede verificar se as orientações de energia são **compreendidas e úteis**, registrando
**as situações testadas, os comentários recebidos e os ajustes realizados**, sem expor dado pessoal.

## Como foi aplicado

- Teste feito em 19/11/2026 por 5 pessoas de fora do grupo, no app, pelo formulário do portal
  (`/avaliar/teste`), junto com o teste da PAI. Ninguém se identifica: aqui elas aparecem como "Pessoa 1" a
  "Pessoa 5", na ordem em que enviaram. Os dados ficam na tabela `datempo.avaliacoes`.
- A pessoa pede uma viagem à Lia, abre "Segurança nas estações e energia" no cartão e responde, para cada
  situação, se entendeu (sim, em parte ou não). No fim dá uma nota de 1 a 5.

## Situações testadas

| # | Situação | O que a pessoa precisa conseguir dizer |
|---|---|---|
| 1 | Pedir à Lia uma viagem casa-trabalho e abrir "Segurança nas estações e energia" | quanto CO₂ e quanto custa de trilho e de carro |
| 2 | Comparar os modos na mesma viagem, pelo cartão | qual modo emite menos |
| 3 | Entender por que o trilho é a alternativa renovável | que ele usa a rede elétrica, que é majoritariamente renovável |
| 4 | Entender o limite da conta | que é estimativa por média, não medição da viagem dela |

## Registro

| Pessoa | Situação 1 | Situação 2 | Situação 3 | Situação 4 | Nota (1 a 5) |
|---|---|---|---|---|---|
| Pessoa 1 | sim | sim | sim | em parte | 5 |
| Pessoa 2 | sim | sim | sim | sim | não respondeu |
| Pessoa 3 | sim | sim | sim | sim | 5 |
| Pessoa 4 | sim | sim | sim | sim | 5 |
| Pessoa 5 | sim | sim | sim | sim | 5 |

Resumo: das 20 respostas, 19 foram "sim" e 1 foi "em parte" (Pessoa 1, na situação 4: entender que a
conta é estimativa por média). Na pergunta final, "Essas informações de energia ajudariam você a escolher
como ir ao trabalho?", as 4 pessoas que responderam deram nota 5.

Comentários recebidos: o campo de comentário era opcional e nenhuma das 5 pessoas escreveu. O único sinal
de dúvida veio da resposta "em parte" na situação 4.

## Ajustes feitos a partir do teste

- **O limite da conta ficou visível nos números.** Antes, o aviso de que a energia é estimativa ficava só
  numa linha pequena no fim do cartão ("Energia é estimativa por médias oficiais"), separada dos números.
  Como uma pessoa entendeu só em parte esse limite, a frase "Estimativa por médias oficiais, não a medição
  desta viagem." passou a abrir a própria linha de CO₂ e custo, no mesmo tamanho dos números
  (`sistema/web/src/componentes/Cartoes.tsx`, bloco de energia do cartão da viagem).
- **Limite do teste:** com notas quase todas no máximo e sem comentários escritos, o teste mostra que as
  orientações foram entendidas, mas aponta pouco o que melhorar além do ajuste acima.
