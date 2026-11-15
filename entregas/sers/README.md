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
mostra, para a distância daquele trajeto, o CO₂ e a tarifa do trilho, do ônibus e do carro, a linha que
identifica o trilho como a alternativa renovável (86,8% de fonte renovável na eletricidade do país, EPE),
o rótulo de que é estimativa, as premissas principais com o tipo e o ano de cada uma, e as fontes com
link. A Lia recebe os mesmos números da ferramenta `ver_trajeto`, só fala com eles, diz que são estimativas
e cita a fonte principal. A lista completa de premissas e fontes aparece no teste da matéria (página da
SERS no sistema) e neste script.

## Onde está cada coisa (a parte da SERS no repositório compartilhado)

| arquivo | o que é |
|---|---|
| `entregas/sers/comparar_energia.py` | **esta entrega**: roda a comparação e imprime contas, premissas e fontes |
| `sistema/mobilidade/energia.py` | o cálculo em si (`comparar`), usado pelo app e por este script |
| `pesquisa/energia_modos.json` | os 30 fatores, cada um com chave, valor, unidade, ano de referência, fonte (link), trecho do documento, confiança e observação |
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
| Carro a gasolina, sozinho | 444,4 kWh | 86,2 a 110,9 kg | R$ 315,04 |

Trocar o carro pelo trilho evita cerca de **84 a 109 kg de CO₂ por mês** por pessoa (a faixa vem do teor de etanol) e custa cerca de
**R$ 77 a menos** (tarifa cheia do trilho contra só a gasolina do carro). Com a integração do
Bilhete Único ou com vale-transporte, o custo do transporte público muda; essas regras não foram lidas.

### Como ler a coluna de energia

O kWh do trilho é **eletricidade** usada na tração; o kWh do carro é a **energia contida na gasolina**
queimada. São formas diferentes de energia, e boa parte da energia da gasolina vira calor no motor. Por
isso a coluna de energia mostra só a ordem de grandeza, e a comparação justa entre os modos é a do
**CO₂** e a do **custo**.

### Por que o trilho conta como alternativa renovável, e o limite disso

O enunciado pede ao menos uma alternativa renovável. O trilho entra nessa vaga por três razões:

1. **A fonte de energia dele é a eletricidade**, e a eletricidade do Brasil é majoritariamente renovável:
   **86,8% da oferta interna de energia elétrica em 2025** (hidráulica, eólica, solar e biomassa, segundo o
   Balanço Energético Nacional da EPE). Ônibus a diesel e carro a gasolina dependem de combustível fóssil.
2. **O CO₂ confirma:** com o fator médio da rede (MCTI, 46,1 g de CO₂ por kWh, que já embute essa matriz), o
   trilho emite cerca de 2,5% do CO₂ do carro na mesma distância.
3. **Não exige instalar nada:** a alternativa já existe e já está construída (ver viabilidade abaixo).

O **limite dessa leitura**: o trilho não usa uma usina renovável própria. O número é o **fator médio da
rede elétrica do país**, não um contrato de energia do Metrô, e muda com a hidrologia de cada ano (0,0385 em
2023, 0,0545 em 2024 e 0,0461 tCO2/MWh em 2025, no JSON). Se o Metrô comprar energia de uma fonte
específica, o número muda; essa informação não foi lida. Por isso o app diz "alternativa renovável pela
média da rede", e não "100% renovável".

## Premissas (toda estimativa depende delas)

Cada premissa é marcada com o **tipo** e o **ano** do dado, porque anos de 2023 a 2026 aparecem juntos:
**dado oficial** (publicado por órgão ou empresa, confiança "alta" no JSON), **calculado pela equipe**
(conta nossa com dois números oficiais) e **estimativa** (sem fonte oficial completa, confiança "média").

| premissa | tipo | ano |
|---|---|---|
| Eletricidade a 46,1 g de CO₂/kWh: média do país (MCTI/SIRENE) | dado oficial | 2025 |
| 86,8% da eletricidade do país vem de fonte renovável (EPE, BEN) | dado oficial | 2025 |
| Metrô a 0,0717 kWh por passageiro-km (401 GWh ÷ 5.596,3 milhões de passageiros-km, Relatório Integrado do Metrô); o trem usa o mesmo valor, porque a CPTM não publicou o dela | calculado pela equipe | 2025 |
| Carro popular a gasolina, 13,3 km/L na cidade (INMETRO/PBE Veicular), **com uma pessoa dentro**; gasolina a R$ 6,35 (ANP); custo só do combustível | dado oficial | 2026 |
| Gasolina a 2,23 kg de CO₂ por litro (inventário do Ministério dos Transportes); a faixa do carro vai da parte fóssil (78%, ensaio com 22% de etanol) ao litro inteiro | dado oficial (fator) e estimativa (fração fóssil) | 2024 |
| Ônibus a 79 g de CO₂ por passageiro-km: indicador publicado pelo Metrô, que já embute uma lotação média não publicada | estimativa | 2024 |
| Tarifas: R$ 5,40 no trilho e R$ 5,30 no ônibus, vigentes em São Paulo | dado oficial | 2026 |
| Energia da gasolina a 32,2 MJ por litro (0,770 tep/m³ × 41,87 GJ/tep, BEN da EPE) | calculado pela equipe | a confirmar |

## Justificativas: custo, viabilidade e impacto das três alternativas

**Custo** (para o passageiro, viagem de 15 km, só a ida): trilho R$ 5,40, ônibus R$ 5,30 e carro R$ 7,16 só
de gasolina. Estacionamento, manutenção, seguro e depreciação do carro não entraram, porque não há fonte
oficial única para eles; contando-os, a diferença a favor do transporte público aumenta.

| alternativa | viabilidade | impacto |
|---|---|---|
| **Trilho (renovável pela média da rede)** | Já existe e já está construído; a pessoa só precisa estar perto de uma estação. Limites: cobre só os corredores da rede, e falhas de linha existem (é o que o app ajuda a contornar). Recomendação de uso, não de investimento. | Cerca de 2,5% do CO₂ do carro na mesma distância (0,05 kg contra 1,96 a 2,52 kg). Não conta a emissão de construir e manter a infraestrutura, que não está nas fontes consultadas. |
| **Ônibus a diesel** | Alcança onde o trilho não chega e tem custo parecido com o do trilho. Limite: depende do trânsito e da lotação, e a lotação média não tem fonte oficial. | Cerca de 1,19 kg de CO₂ por viagem, uns 24 vezes o do trilho e menos que o carro sozinho. É dado do indicador do Metrô, uma estimativa. Há 2.009 ônibus elétricos na frota da SPTrans (30/09/2026), mas sem consumo oficial lido, então não foram calculados. |
| **Carro a gasolina, sozinho** | Porta a porta, sem depender de horário. Limite: custo mais alto, trânsito e estacionamento; o cálculo supõe uma pessoa dentro. | O maior CO₂ por pessoa (1,96 a 2,52 kg) e o maior custo. Com mais gente no carro, o valor por pessoa cai e a comparação fica menos favorável ao trilho. |

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
