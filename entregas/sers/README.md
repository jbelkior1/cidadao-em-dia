# SERS · Global Solution 2026.2 — a energia da viagem

Integrantes: **A PREENCHER PELO GRUPO** (nome completo e RM de cada um).

> Este repositório é compartilhado entre as matérias da Global Solution. O enunciado da SERS pede
> que a contribuição dela esteja claramente identificada: é o que a seção **Onde está cada coisa**
> faz, mais abaixo.

## Contexto: público, necessidade energética e como as orientações ajudam

- **Público:** quem usa trem e metrô em São Paulo todo dia, principalmente no trajeto casa-trabalho.
- **Necessidade energética:** o deslocamento diário. A mesma viagem pode ser feita de carro a
  gasolina, de ônibus a diesel ou de trem e metrô elétricos, e as três consomem energia muito
  diferente para entregar a mesma coisa: levar uma pessoa de A até B.
- **Como ajuda:** no app **Dá Tempo?**, quando a Lia confere uma viagem, ela mostra quanto aquela
  distância custa em energia, em dinheiro e em CO₂ nos três modos. A pessoa vê o peso da escolha no
  bolso e no clima na hora de decidir, sem precisar procurar nada.

## Como rodar

```bash
python comparar_energia.py
```

Mostra a comparação de uma viagem de 15 km com todas as contas, as premissas e as fontes. Para outra
distância: `python comparar_energia.py 8.5`. Precisa de Python 3.13; não usa biblioteca de fora.

O mesmo cálculo aparece no app: suba o sistema (`uv run uvicorn sistema.api:app --port 8010`), abra a
conversa com a Lia e peça uma viagem; o bloco de energia vem no cartão.

## Onde está cada coisa (a parte da SERS no repositório compartilhado)

| arquivo | o que é |
|---|---|
| `entregas/sers/comparar_energia.py` | **esta entrega**: roda a comparação e imprime contas, premissas e fontes |
| `sistema/mobilidade/energia.py` | o cálculo em si (`comparar`), usado pelo app e por este script |
| `pesquisa/energia_modos.json` | os 30 fatores, cada um com valor, unidade, ano, fonte e premissa |
| `pesquisa/ENERGIA_FONTES.md` | o levantamento das fontes, com o que foi lido em cada documento |
| `sistema/testes.py` (`sers_testar`) | o teste da matéria dentro do sistema, que mostra conta por conta |
| `sistema/web/src/paginas/Materia.tsx` | a página da SERS no sistema, com Entenda, Teste e Checklist |

O cálculo não foi copiado para cá de propósito: existe um só, usado pelo app e por esta entrega. Se a
equipe corrigir um fator no JSON, a tela e este script mudam juntos, e não há risco de uma versão
divergir da outra.

## As três alternativas, para a mesma necessidade e o mesmo período

Resultado para uma viagem de 15 km, por pessoa, só a ida (números de 12/11/2026):

| modo | energia | CO₂ | custo | renovável |
|---|---|---|---|---|
| Trem ou metrô | 1,08 kWh | 0,05 kg | R$ 5,40 | **sim** |
| Ônibus a diesel | sem fonte de consumo | 1,19 kg | R$ 5,30 | não |
| Carro a gasolina, sozinho | 10,1 kWh | 1,96 a 2,52 kg | R$ 7,16 | não |

O trilho emite **2,6% do CO₂ do carro** nessa distância, com custo parecido com o do ônibus.

### Por que o trilho conta como alternativa renovável

A tração é elétrica e **86,8% da eletricidade gerada no país em 2025 veio de fonte renovável**
(hidráulica, eólica, solar e biomassa). O fator de emissão do sistema elétrico usado na conta é o do
MCTI, 46,1 g de CO₂ por kWh, que já embute essa matriz.

## Premissas (toda estimativa depende delas)

- Eletricidade a 46,1 g de CO₂/kWh — média do país em 2025 (MCTI/SIRENE).
- Metrô a 0,0717 kWh por passageiro-km — Relatório Integrado 2025 do Metrô de São Paulo. O trem usa o
  mesmo valor, porque a CPTM não publicou o dela.
- Carro popular a gasolina, 13,3 km/L na cidade (INMETRO/PBE Veicular), **com uma pessoa dentro**.
  Gasolina a R$ 6,35 (ANP, síntese semanal). Custo só do combustível.
- Ônibus a 79 g de CO₂ por passageiro-km — indicador publicado pelo Metrô. Esse número já considera
  uma lotação média que não é publicada em separado.
- Tarifas: R$ 5,40 no trilho e R$ 5,30 no ônibus, valores vigentes em São Paulo.

## Justificativas: custo, viabilidade e impacto

- **Custo:** para o passageiro, trilho e ônibus custam quase o mesmo e são mais baratos que o carro,
  mesmo contando só a gasolina. Somando estacionamento, manutenção e depreciação, a diferença
  aumenta, mas esses valores não entraram porque não há fonte oficial única para eles.
- **Viabilidade:** a alternativa renovável já existe e já está construída. Não se trata de instalar
  nada: trata-se de usar melhor uma rede que roda hoje. Por isso a recomendação do app é de uso, não
  de investimento.
- **Impacto ambiental:** a diferença de CO₂ entre trilho e carro é de duas ordens de grandeza na mesma
  viagem. O limite dessa conta é que ela ignora a emissão de construir e manter a infraestrutura, que
  não está nas fontes consultadas.

## Limitações (não tratar estimativa como resultado garantido)

1. Todos os números são **médias oficiais**, não medição da viagem de ninguém. O app diz isso em tela.
2. O **consumo de energia do ônibus não tem fonte oficial** de litros por passageiro-km; por isso a
   tabela traz o CO₂ dele por um indicador publicado e deixa a energia em branco, em vez de inventar.
3. O **teor de etanol na gasolina** muda por norma; a faixa de CO₂ do carro (1,96 a 2,52 kg) existe
   justamente por causa dessa incerteza.
4. O **carro é considerado com uma pessoa**. Com duas ou mais, o CO₂ por pessoa cai pela metade ou
   mais, e a comparação muda.
5. O fator da eletricidade é **a média do país**, não a do horário nem a da região da viagem.

## O que falta à equipe (não é código)

- [ ] Conferir cada número nas fontes, principalmente os lidos de PDF, e o teor de etanol.
- [ ] Testar com usuários: situações testadas, comentários e ajustes (sem dado pessoal).
- [ ] Preencher nome completo e RM de todos.
- [ ] Gravar o vídeo no YouTube, não listado, de até 3 minutos.
- [ ] Enviar no portal **apenas o .txt** com nomes, RM, link do repositório e link do vídeo.

## Fontes

Listadas uma a uma em `pesquisa/ENERGIA_FONTES.md` e repetidas na saída do
`comparar_energia.py`: MCTI/SIRENE, Relatório Integrado 2025 do Metrô, INMETRO (PBE Veicular),
ANP (preços), SPTrans e Agência SP (tarifas), Ministério dos Transportes.
