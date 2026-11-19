# MLAM · Global Solution 2026.2: análise estatística das ocorrências no entorno das estações

Integrantes:

| Nome completo | RM |
|---|---|
| João Vitor Belchior Domingos Leite | 572478 |
| João Pedro Pereira Teixeira | 569937 |
| Thiago de Oliveira Coelho Souza | 568783 |

## O que vai ao portal

A pasta `entrega/` tem exatamente o que é postado, solto: a base `ocorrencias_estacoes_2026.csv`, um script por
questão (`questao02_probabilidade.py` a `questao06_logistica.py`) e o relatório `relatorio_mlam_gs2026.pdf` (que fica em
`saidas/`). Cada script lê o `.csv` da mesma pasta, imprime os resultados da questão e salva o gráfico usado no relatório:

```bash
cd entrega
python questao02_probabilidade.py
```

Os scripts desta pasta raiz (`comum.py`, `main.py`, `questao07_relatorio.py` e `preparar_base.py`) ficam só no repositório:
montam a base a partir da planilha bruta e geram o PDF, e não vão ao portal. Os números dos dois conjuntos são os mesmos.

## O problema

O app **Dá Tempo?** (CitizenTech) acompanha quem anda de trem e metrô em São Paulo. Uma das perguntas
que ele responde é onde há mais registro de ocorrência no entorno da estação em que a pessoa embarca
ou desce. Esta entrega é a parte estatística dessa resposta: medir o que acompanha o número de
ocorrências e até onde dá para prever.

## A base (questão 01)

`dados/ocorrencias_estacoes_2026.csv`: 139 linhas, uma por estação de trem ou metrô de São Paulo.

- **Fonte:** SPDados / SSP-SP, planilha `SPDadosCriminais_2026.xlsx`, abas JAN-JUN e JUL-DEZ de 2026,
  baixada em 12/11/2026. Base pública e real; nada foi gerado artificialmente.
- **Período:** janeiro a setembro de 2026.
- **Como foi montada:** contagem de ocorrências num raio de 300 m de cada estação (coordenadas do GTFS
  da SPTrans). O passo a passo, os filtros e as limitações estão em `dados/LEIA-ME.md` (neste repositório) e
  resumidos no início do `preparar_base.py`, o script que gera a base (fica no repositório; o relatório resume a fonte e os filtros).
- **Privacidade:** só números agregados por estação. Nenhum endereço, número de BO ou dado de pessoa.

### Variáveis usadas

| papel | coluna | o que é |
|---|---|---|
| resposta | `total` | ocorrências registradas no entorno da estação |
| explicativa | `dist_marco_zero_km` | distância da estação até o Marco Zero, em km |
| explicativa | `qtd_linhas` | quantas linhas passam na estação |
| explicativa | `lat` | latitude (posição norte-sul) |

**O que ficou de fora de propósito:** `roubo`, `furto` e `outros` somam exatamente `total`, e as faixas
de horário (`madrugada`, `manha`, `tarde`, `noite`, `sem_faixa`) também. Usar qualquer um deles como
variável explicativa seria prever a resposta com ela mesma. O `comum.py` confere essas duas somas ao
carregar a base, para a regra não se perder. A coluna `celular` está vazia porque a planilha da SSP-SP
não permite identificar o aparelho (consta no `LEIA-ME.md` e no `preparar_base.py`).

## Como rodar

Precisa de Python 3.13 com as bibliotecas `pandas`, `numpy`, `scipy`, `statsmodels`, `scikit-learn`,
`matplotlib` e `reportlab` (esta última só para o PDF; o `preparar_base.py` usa ainda `openpyxl`).

**Arquivos recebidos soltos:** ponha todos na mesma pasta. O `ocorrencias_estacoes_2026.csv` pode ficar
junto dos `.py` ou numa subpasta `dados/`; o `comum.py` procura nas duas posições e avisa onde colocar se
não achar. A pasta `saidas/` é criada sozinha. Ordem de execução: `main.py` primeiro, depois
`questao07_relatorio.py` (se o `resultados.json` não existir, o relatório roda o `main.py` por conta própria).

```bash
python main.py
```

Roda as questões 02 a 06 na ordem e grava tudo em `saidas/`: `relatorio.txt` (saída completa com as
interpretações), `resultados.json` (os números) e os gráficos `.png`. Cada questão também roda sozinha,
por exemplo `python questao04_bivariada.py`.

```bash
python questao07_relatorio.py
```

Gera o relatório da questão 07 em `saidas/relatorio_mlam_gs2026.pdf` (precisa de `reportlab`): resumo para
o cliente, tabelas, gráficos, medidas, interpretações, insights e limitações. Os números saem do
`resultados.json`, então o PDF acompanha qualquer mudança na base. Nome e RM dos integrantes ficam em
`comum.INTEGRANTES` e aparecem na capa.

## Arquivos

| arquivo | questão |
|---|---|
| `comum.py` | leitura da base, escolha das variáveis e conferências |
| `questao02_probabilidade.py` | 02: P(X < média) e P(X > mediana), com classificação |
| `questao03_testes_hipotese.py` | 03: testes z para a média (α = 6% com n = 20; α = 9% com n = 25) |
| `questao04_bivariada.py` | 04: dispersão, covariância, Pearson, regressão simples, R², Teste F, previsão |
| `questao05_multivariada.py` | 05: matrizes, regressão múltipla, R², Teste F, VIF, previsão |
| `questao06_logistica.py` | 06: regressão logística, matriz de confusão, acurácia, classificação |
| `questao07_relatorio.py` | 07: monta o relatório em PDF (`saidas/relatorio_mlam_gs2026.pdf`) a partir de `resultados.json` e dos gráficos |
| `main.py` | roda tudo e grava as saídas |
| `preparar_base.py` | monta a base a partir da planilha da SSP-SP e do GTFS |

## Resultados em uma linha cada

- **02**: Assumindo normal, P(X < média) = 0,5000 (equiprovável, por simetria) e P(X > mediana) = 0,6341
  (provável). A distância entre média (341,78) e mediana (228) mostra a assimetria à direita da base.
- **03**: As 20 estações mais distantes do centro têm média abaixo da referência (z = −1,684;
  p = 0,046; rejeita H0 a 6%, por pouco) e as 25 mais próximas, acima (z = 5,741; rejeita H0 a 9%).
  Os grupos foram escolhidos pela distância, então o teste descreve esses grupos; a checagem com amostras
  sorteadas (semente 42) não rejeita H0 em nenhum dos dois casos, como se espera de uma amostra aleatória.
- **04**: Distância × ocorrências: r = −0,468, equação `total = 587,85 − 25,92 × distância_km`,
  R² = 0,219, Teste F com p-valor 6,1 × 10⁻⁹. Breusch-Pagan p = 0,005 (variância desigual); com erro
  padrão robusto (HC3) a inclinação continua significativa.
- **05**: Com distância, nº de linhas e latitude: R² sobe para 0,394 (ajustado 0,380), F(3, 135) = 29,2.
  Nº de linhas é o maior efeito (+243,6 ocorrências por linha). A latitude não acrescenta: sem ela o R²
  ajustado é 0,385, maior. A previsão do cenário (898) fica abaixo da média real das 4 estações parecidas
  (1.232, fora do IC de 95%).
- **06**: Logística para "estação acima da mediana": acurácia 70,5% contra um piso de 51,1%
  (classe majoritária), AUC 0,744. Só a distância é significativa a 5%: o nº de linhas tem p = 0,0674.
  No cenário central (p = 0,94), trocar para 1 linha leva a 0,67 e afastar para 22 km leva a 0,57.

## Limitações (valem para o relatório da questão 07)

1. **A base conta registros de BO, não risco.** Estação movimentada gera mais registro. Sem o fluxo de
   passageiros não dá para calcular ocorrência por pessoa, que seria a medida certa de risco.
2. **A normalidade é assumida por exigência do enunciado.** A variável é assimétrica à direita
   (média 341,78 contra mediana 228), então P(X > mediana) dá 0,634 no modelo e 0,5 no dado real.
3. **As amostras da questão 03 são dirigidas,** não sorteadas: as conclusões valem para aqueles grupos
   de estações (as mais distantes e as mais centrais), não para uma estação qualquer. Por isso o script
   repete as contas com amostras sorteadas, para mostrar a diferença.
4. **Os pressupostos da regressão linear não se cumprem por inteiro:** Breusch-Pagan indica variância
   desigual dos resíduos (p = 0,005 na Q04 e 0,019 na Q05) e os resíduos são assimétricos. O Teste F e os
   p-valores são aproximados; os p-valores com erro padrão robusto (HC3) confirmam as mesmas conclusões.
5. **Sobra variação sem explicar:** 60,6% na regressão múltipla. Falta na base o que mais pesaria:
   fluxo de passageiros, comércio no entorno, policiamento e hora do dia.
6. **Os modelos foram avaliados na mesma base em que foram ajustados.** Com 139 linhas e 3 variáveis o
   sobreajuste é pequeno, mas a acurácia de 70,5% descreve esta base, não uma cidade nova.
7. **O número de linhas tem poucos casos no alto da escala:** 121 estações têm 1 linha, 14 têm 2 e só 4 têm
   3 ou mais. O coeficiente dessa variável é instável, não é significativo a 5% na logística
   (p = 0,0674), e os cenários de previsão com 3 linhas são extrapolação.
8. **Os raios de 300 m se sobrepõem** entre estações próximas, então as observações não são totalmente
   independentes, como o `dados/LEIA-ME.md` registra.
9. **13,2% dos registros do município foram descartados por coordenada inválida** e 48 estações ficaram
   de fora por não serem do município (critério aproximado, descrito no `LEIA-ME.md`).

## Entrega no portal (questão 08)

Um representante posta direto no portal, sem links: a base em `.csv`, os códigos em `.py` e o relatório
em `.pdf`. Nome completo e RM de cada integrante ficam na capa do PDF e no cabeçalho de cada `.py`
(o `.csv` não comporta cabeçalho, e `.md` não é formato aceito, por isso o README e o `LEIA-ME.md` não vão).
Os arquivos vão soltos, sem pastas: veja acima como organizá-los para rodar.
