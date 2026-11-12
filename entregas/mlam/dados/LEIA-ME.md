# Base de ocorrências no entorno das estações (MLAM · Global Solution 2026.2)

Base real, derivada da planilha oficial da SSP-SP, com uma linha por estação de trem ou metrô de São Paulo e a contagem de ocorrências registradas num raio de 300 m. Serve ao app "Plano B" (CitizenTech) e à análise estatística da matéria MLAM. Só há números agregados por estação: nenhum endereço, número de BO ou dado de pessoa foi gravado.

## Arquivos
- `dados/ocorrencias_estacoes_2026.csv`: a base (139 linhas, uma por estação).
- `../../sistema/dados/seguranca_estacoes.json`: a mesma contagem no formato do app (`meta` + `estacoes`).
- `preparar_base.py`: script que gera os dois arquivos. Para rodar de novo:
  `python preparar_base.py CAMINHO/SPDadosCriminais_2026.xlsx --gtfs CAMINHO/sptrans.zip` (requer `pandas` e `openpyxl`; `--cache-dir PASTA` guarda a leitura lenta do xlsx numa pasta temporária). Duas rodadas seguidas deram arquivos idênticos (conferido por hash).

## Fonte e período
- Ocorrências: SPDados / SSP-SP, planilha `SPDadosCriminais_2026.xlsx` (https://www.ssp.sp.gov.br/assets/estatistica/transparencia/spDados/SPDadosCriminais_2026.xlsx), abas `JAN-JUN_2026` e `JUL-DEZ_2026`. Baixada em 12/11/2026 (última modificação no servidor: 28/10/2026).
- Período coberto: **janeiro a setembro de 2026**. A data de registro vai de 2026-01-01 a 2026-09-30 e `MES_ESTATISTICA` chega a 9. A aba JUL-DEZ tem só julho a setembro.
- A planilha é organizada pela data de registro, então há fatos que ocorreram antes: a data do fato vai de 2006-01-01 a 2026-10-01, e 22.222 linhas (todas as cidades) têm fato anterior a 2026. Mantive todas, sem filtrar pela data do fato.
- Estações: GTFS da SPTrans, rotas com `route_type` 1 (metrô) ou 2 (trem). Estações de mesmo nome (sem o trecho entre parênteses) a menos de 350 m foram unidas (coordenada = média das paradas; linhas = união).

## Filtros aplicados
1. Linhas lidas nas duas abas: **814.900**.
2. Só `NOME_MUNICIPIO` = S.PAULO: 330.690 linhas (as outras 484.210 não entram na contagem).
3. Coordenada válida: latitude entre -24,0 e -23,3 e longitude entre -47,0 e -46,3. Coordenadas zeradas, nulas ou fora do retângulo saem. **Descartadas por coordenada inválida em São Paulo: 43.664** (13,2% das linhas do município). **Válidas em São Paulo: 287.026.**
4. Estações fora do município: o GTFS inclui estações de outras cidades (Osasco, Guarulhos, Mogi, Santo André etc.). Para não contar zero por falta de dado, a estação só entra se, num raio de 500 m, houver mais registros com coordenada válida de São Paulo do que de outras cidades (usei os registros de outras cidades só para essa checagem; estação sem nenhum registro por perto também sai). Foram excluídas 48 das 187 estações agrupadas, ficando **139**. Excluídas: Aeroporto Guarulhos, Amador Bueno, Antônio Gianetti Neto, Antônio João, Aracaré, Baltazar Fidélis, Barueri, Botujuru, Brás Cubas, Caieiras, Calmon Viana, Campo Limpo Paulista, Capuava, Carapicuíba, Comandante Sampaio, Eng Manoel Feio, Engenheiro Cardoso, Estudantes, Ferraz De Vasconcelos, Francisco Morato, Franco Da Rocha, General Miguel Costa, Guapituba, Guarulhos Cecap, Itapevi, Itaquaquecetuba, Jandira, Jardim Belval, Jardim Silveira, Jundiai, Jundiapeba, Mauá, Mogi Das Cruzes, Osasco, Poá, Prefeito Celso Daniel - Santo André, Prefeito Saladino, Presidente Altino, Quitaúna, Ribeirão Pires, Rio Grande Da Serra, Sagrado Coração, Santa Rita, Santa Terezinha, Suzano, São Caetano, Utinga, Várzea Paulista.
   - Limitação: é uma aproximação, sem o polígono oficial do município. Nos 500 m, as estações mantidas têm no mínimo 65 registros de SP e no máximo 11 de outras cidades; entre as excluídas, só Presidente Altino (14 de SP contra 241 de outras), Baltazar Fidélis (4 contra 90) e Carapicuíba (1 contra 481) têm algum registro de SP, e as demais têm zero.

## Colunas do CSV
| coluna | descrição |
|---|---|
| estacao | nome da estação, sem o trecho entre parênteses. As duas "Lapa" (linhas 7 e 8) ficam a mais de 350 m uma da outra e não foram unidas; aparecem como `Lapa (linha 7)` e `Lapa (linha 8)` |
| linhas | linhas que passam na estação, separadas por hífen (ex.: `1-3`). Metrô 1 a 6, 15 e 17 (monotrilhos); trem 7 a 13 |
| qtd_linhas | quantidade de linhas na estação (numérica) |
| lat, lon | coordenada da estação (média das paradas do grupo, do GTFS) |
| total | ocorrências no raio de 300 m |
| roubo, furto, outros | `total` por tipo (ver abaixo); a soma é igual a `total` |
| madrugada, manha, tarde, noite | `total` por faixa: madrugada 0h–5h59, manhã 6h–11h59, tarde 12h–17h59, noite 18h–23h59 |
| sem_faixa | ocorrências sem hora nem período (ex.: "hora incerta"); madrugada+manha+tarde+noite+sem_faixa = `total` |
| celular | **vazio em todas as linhas**: a planilha não permite identificar celular (ver abaixo) |
| dist_marco_zero_km | distância (Haversine) da estação à Praça da Sé (-23,5503; -46,6339), em km |

O JSON tem os mesmos números (`por_faixa`, `por_tipo`, `sem_faixa`, `celular: null`) e mais `faixa_mais_comum` (faixa com mais ocorrências; em empate vale a ordem madrugada, manhã, tarde, noite).

## Como classifiquei
- **Distância**: Haversine, raio da Terra 6.371.008,8 m; conta quem está a 300 m ou menos da estação.
- **Faixa de horário**: pela `HORA_OCORRENCIA_BO`. Se faltar (em 101.530 das 287.026 ocorrências válidas de SP, 35,4%), uso `DESC_PERIODO` (De madrugada, Pela manhã, A tarde, A noite). Sem nenhum dos dois, vai para `sem_faixa` (1.802 em SP). O período é um rótulo do próprio registro e pode ser menos preciso que a hora.
- **Tipo**: pela `RUBRICA` (se vazia, `NATUREZA_APURADA`). Rubrica que começa com "Roubo" é roubo (inclui veículo e carga); com "Furto" é furto (inclui veículo e carga); o resto (lesão corporal, tráfico, estupro, homicídio, latrocínio, extorsão etc.) é "outros". Nas válidas de SP: furto 185.017, roubo 65.549, outros 36.460.
- **Celular: não foi possível.** A planilha não traz o objeto subtraído. Procurei "celular" e "telefone" em `RUBRICA`, `DESCR_CONDUTA` e `NATUREZA_APURADA` e achei **0 ocorrências** (esses campos só dizem coisas como "Furto - Outros" ou "Transeunte"). A SSP publica à parte uma planilha de celulares subtraídos, que não usei aqui. Por isso `celular` ficou vazio (`null` no JSON), e não zero.

## Resultado
- Soma das contagens por estação: 47.508. A mesma ocorrência pode contar em mais de uma estação quando os raios se sobrepõem (por exemplo, Pinheiros e Pinheiros Metrô).
- 5 estações com mais ocorrências no raio: República (2.100), Luz (1.637), Palmeiras - Barra Funda (1.485), Sé (1.314), Anhangabaú (1.179).

## Limitações (importante para a MLAM)
- É contagem de ocorrências **registradas** com coordenada, não risco. Não há denominador (fluxo de passageiros): estações grandes e centrais tendem a ter mais ocorrências só por terem mais gente. `qtd_linhas` e `dist_marco_zero_km` ajudam a controlar parte disso, mas não resolvem.
- 13,2% das ocorrências de SP não têm coordenada válida e não aparecem. Se esse descarte não for aleatório (por tipo ou região), há viés; não testei.
- Subnotificação: o que não virou boletim não está na base. A localização é a informada no boletim e pode ser aproximada.
- Os raios de 300 m se sobrepõem entre estações próximas, então as linhas do CSV não são observações independentes (relevante para testes estatísticos).
- Estações de nomes diferentes e fisicamente coladas (ex.: Pinheiros e Pinheiros Metrô) ficaram separadas, pela regra de agrupar só nomes iguais.
- O período é parcial (nove meses) e inclui alguns fatos de anos anteriores; os totais não equivalem a um ano.
- Privacidade: o script não lê logradouro, número, BO nem nome; nada disso está nas saídas.
