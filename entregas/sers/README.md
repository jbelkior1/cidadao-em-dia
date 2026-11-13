# SERS · Global Solution 2026.2: a energia da viagem

Integrantes:

| Nome completo | RM |
|---|---|
| João Vitor Belchior Domingos Leite | 572478 |
| João Pedro Pereira Teixeira | 569937 |
| Thiago de Oliveira Coelho Souza | 568783 |

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
conversa com a Lia e peça uma viagem. No cartão da viagem, em "Segurança nas estações e energia", a Lia
mostra, para a distância daquele trajeto, o CO₂ e a tarifa de ir de trilho contra o CO₂ e o gasto de
gasolina de ir de carro, com o aviso de que é estimativa por médias oficiais. O
ônibus, as premissas e as fontes completas aparecem no teste da matéria (página da SERS no sistema) e
neste script; o cartão traz só o resumo, para caber na conversa.

## Onde está cada coisa (a parte da SERS no repositório compartilhado)

| arquivo | o que é |
|---|---|
| `entregas/sers/comparar_energia.py` | **esta entrega**: roda a comparação e imprime contas, premissas e fontes |
| `sistema/mobilidade/energia.py` | o cálculo em si (`comparar`), usado pelo app e por este script |
| `pesquisa/energia_modos.json` | os 30 fatores, cada um com valor, unidade, ano, fonte e premissa |
| `pesquisa/ENERGIA_FONTES.md` | o levantamento das fontes, com o que foi lido em cada documento |
| `sistema/testes.py` (`sers_testar`) | o teste da matéria dentro do sistema, que mostra conta por conta |
| `sistema/web/src/paginas/Materia.tsx` | a página da SERS no sistema, com Entenda, Teste e Checklist |
| `sistema/assistente.py` e `sistema/web/src/componentes/Cartoes.tsx` | onde a energia entra na resposta da Lia e no cartão da viagem |
| `entregas/sers/TESTES_USUARIOS.md` | roteiro e registro dos testes com usuários (a equipe preenche) |

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

O trilho emite cerca de **2,5% do CO₂ do carro** nessa distância (2,0% se comparado ao teto de 2,52 kg),
com custo parecido com o do ônibus.

### No período de referência: um mês de trabalho

O enunciado pede comparar as opções num período de referência comum. Usamos um mês de trabalho:
22 dias úteis, ida e volta, ou seja, 44 viagens de 15 km por pessoa.

| modo | energia no mês | CO₂ no mês | custo no mês |
|---|---|---|---|
| Trem ou metrô | 47,5 kWh | 2,2 kg | R$ 237,60 |
| Ônibus a diesel | sem fonte de consumo | 52,4 kg | R$ 233,20 |
| Carro a gasolina, sozinho | 444,4 kWh | 86,2 kg | R$ 315,04 |

Trocar o carro pelo trilho evita cerca de **84 kg de CO₂ por mês** por pessoa e custa cerca de
**R$ 77 a menos** (tarifa cheia do trilho contra só a gasolina do carro). Com a integração do
Bilhete Único ou com vale-transporte, o custo do transporte público muda; essas regras não foram lidas.

### Como ler a coluna de energia

O kWh do trilho é **eletricidade** usada na tração; o kWh do carro é a **energia contida na gasolina**
queimada. São formas diferentes de energia, e boa parte da energia da gasolina vira calor no motor. Por
isso a coluna de energia mostra só a ordem de grandeza, e a comparação justa entre os modos é a do
**CO₂** e a do **custo**.

### Por que o trilho conta como alternativa renovável, e o limite disso

O trilho não usa uma usina renovável própria: ele usa a **rede elétrica do país**, e **86,8% da
eletricidade gerada no Brasil em 2025 veio de fonte renovável** (hidráulica, eólica, solar e biomassa,
segundo o Balanço Energético Nacional da EPE). É nesse sentido que ele é a alternativa renovável da
comparação. O CO₂ é calculado pelo fator médio do sistema elétrico (MCTI, 46,1 g de CO₂ por kWh), que já
embute essa matriz. Se o Metrô contratar energia de uma fonte específica, o número muda; essa
informação não foi lida.

## Premissas (toda estimativa depende delas)

- Eletricidade a 46,1 g de CO₂/kWh: média do país em 2025 (MCTI/SIRENE).
- Metrô a 0,0717 kWh por passageiro-km: Relatório Integrado 2025 do Metrô de São Paulo. O trem usa o
  mesmo valor, porque a CPTM não publicou o dela.
- Carro popular a gasolina, 13,3 km/L na cidade (INMETRO/PBE Veicular), **com uma pessoa dentro**.
  Gasolina a R$ 6,35 (ANP, síntese semanal). Custo só do combustível.
- Ônibus a 79 g de CO₂ por passageiro-km: indicador publicado pelo Metrô. Esse número já considera
  uma lotação média que não é publicada em separado.
- Tarifas: R$ 5,40 no trilho e R$ 5,30 no ônibus, valores vigentes em São Paulo.

## Justificativas: custo, viabilidade e impacto

- **Custo:** para o passageiro, trilho e ônibus custam quase o mesmo e são mais baratos que o carro,
  mesmo contando só a gasolina. Somando estacionamento, manutenção e depreciação, a diferença
  aumenta, mas esses valores não entraram porque não há fonte oficial única para eles.
- **Viabilidade:** a alternativa renovável já existe e já está construída. Não se trata de instalar
  nada: trata-se de usar melhor uma rede que roda hoje. Por isso a recomendação do app é de uso, não
  de investimento.
- **Impacto ambiental:** na mesma viagem, o trilho emite cerca de 40 vezes menos CO₂ que o carro. O limite dessa conta é que ela ignora a emissão de construir e manter a infraestrutura, que
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
- [ ] Testar com usuários e preencher `TESTES_USUARIOS.md` (roteiro pronto: situações, registro e ajustes, sem dado pessoal).
- [ ] Gravar o vídeo no YouTube, não listado, de até 3 minutos.
- [ ] Enviar no portal **apenas o .txt** com nomes, RM, link do repositório e link do vídeo.

## Fontes

Listadas uma a uma em `pesquisa/ENERGIA_FONTES.md` e repetidas na saída do
`comparar_energia.py`: MCTI/SIRENE, Relatório Integrado 2025 do Metrô, INMETRO (PBE Veicular),
ANP (preços), SPTrans e Agência SP (tarifas), Ministério dos Transportes e EPE (Balanço Energético Nacional,
de onde vêm os 86,8% de renováveis e os 32,2 MJ por litro de gasolina).
