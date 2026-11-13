# Fontes da pesquisa de energia (SERS): consultado em 12/11/2026

Regra seguida: só entra número lido em página ou arquivo oficial nesta sessão. Busca na web serviu só para achar o endereço. Os dados estruturados estão em `energia_modos.json`.

## O que abriu e foi usado

| Fonte | URL | Abriu? | O que foi lido |
|---|---|---|---|
| MCTI, planilha do fator médio do SIN | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao/arquivo/Inventario_2026_janset.xlsx | Sim (baixada pelo link direto) | Fator médio anual 2006-2025 e mensal até set/2026. 2025 = 0,0461; 2024 = 0,0545; 2023 = 0,0385 tCO2/MWh |
| MCTI, nota técnica jun/2025 | https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/cgcl/paginas/NT_FE_jun25.pdf | Sim | Mudança de base de dados do ONS desde jan/2025; metodologia inalterada |
| EPE, BEN 2026 Relatório Síntese | https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-975/topico-847/BEN_Síntese_2026_PT.pdf | Sim (PDF baixado e lido) | Renováveis na matriz elétrica 2025: 86,8% (2024: 88,2%) |
| Metrô SP, Relatório Integrado 2025 | https://af0020-61294dc44a8f38122c35-endpoint.azureedge.net/blobaf00201eecb0af9a/wp-content/uploads/2026/03/RI-2025_MetroSP_130326-3.pdf | Sim | Energia da operação 401 GWh, 892,7 milhões de passageiros, 5.596,3 milhões de pkm, 2,62 kWh/carro-km, 3 gCO2e/pkm, comparativos de ônibus e carro |
| Metrô SP, Relatório Integrado 2023 | https://ri.metrosp.com.br/wp-content/uploads/2024/03/Relatorio-integrado-2023.pdf | Sim | Unidade "milhões" do passageiro-km; série de 2017 a 2023 |
| MMA e Ministério dos Transportes, Inventário Nacional de Emissões por Veículos Rodoviários, ano-base 2024 | https://www.gov.br/transportes/pt-br/assuntos/sustentabilidade/mudanca-do-clima/0_ineavar_2025.pdf (baixado com /@@download/file) | Sim | Fatores kg CO2/L (diesel mineral 2,63; gasolina automotiva 2,23; etanol hidratado 1,51; anidro 1,58); km/L de ônibus urbano 2,10 (dado CETESB) |
| INMETRO, Tabela PBEV 2026 (atualização 14/ago/26) | https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/veiculos-automotivos-pbe-veicular/mascara-pbev-2026_19_jan-rev01.pdf | Sim | Consumo e CO2 por modelo (HB20 Sense, Mobi Like, Argo); combustível de ensaio E22 |
| ANP, Síntese Semanal 45/2026 | https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/arq-sintese-semanal/2026/sintese-precos-45.pdf | Sim | São Paulo capital, 01-07/11/2026: gasolina 6,35; diesel S10 7,25; etanol 4,01 |
| Agência SP (Governo do Estado) | https://www.agenciasp.sp.gov.br/trens-e-metro-terao-nova-tarifa-a-partir-de-6-de-janeiro-com-valor-abaixo-da-inflacao/ | Sim | Tarifa de trem e metrô R$ 5,40 desde 06/01/2026 |
| Metrô SP, página de bilhetes | https://www.metro.sp.gov.br/sua-viagem/bilhetes-cartoes/ | Sim | R$ 5,40 por viagem |
| SPTrans, tarifas | https://www.sptrans.com.br/tarifas/ | Sim (só com User-Agent de navegador) | Ônibus R$ 5,30; metroferroviário R$ 5,40; atualizado em 06/01/2026 |
| Prefeitura de São Paulo, nota dos 2 mil ônibus elétricos | https://prefeitura.sp.gov.br/w/prefeitura-atinge-marco-hist%C3%B3rico-de-2-mil-%C3%B4nibus-el%C3%A9tricos-na-frota-de-s%C3%A3o-paulo-com-entrega-de-mais-250-ve%C3%ADculos | Sim | 1.821 a bateria e 188 trólebus |
| MME, notícia sobre o fator de 2023 | https://www.gov.br/mme/pt-br/assuntos/noticias/2023-2026/geracao-de-energia-eletrica-tem-a-menor-emissao-de-co2-dos-ultimos-onze-anos | Sim | 38,5 kg CO2/MWh em 2023 (confere com o MCTI) |

## O que não abriu ou não serviu

| Fonte | Resultado |
|---|---|
| Páginas HTML do MCTI (`/mudancadoclima/dados-e-ferramentas/fatores-de-emissao`, `/sirene/dados-e-ferramentas/fatores-de-emissao`, `/cgcl/paginas/fator-medio-inventarios-corporativos`, notícia de jun/2025) | Mostraram verificação anti-robô ("What code is in the image?"). Não tentei resolver. Os arquivos .xlsx e .pdf por link direto abriram normalmente |
| Portal de transparência do Metrô (OD 2023, inventário de GEE 2024, `node/5383`, `node/5366`, `node/5555`) | Resposta "Site em manutenção". Sem ocupação de automóvel da Pesquisa OD |
| Site ESG da CPTM (`/cptm/esg-consciente/meio-ambiente`) | Abriu, mas sem link para o inventário de GEE 2024. CPTM sem número oficial |
| MMA, `inventario_emissoes_rodoviarias_2025_mma.pdf` | Devolveu página HTML, não PDF. Usei a cópia do Ministério dos Transportes |
| INMETRO, páginas de notícia da tabela PBEV | Resposta vazia no download; usei o PDF da tabela |
| SPTrans/Prefeitura: consumo e lotação da frota | Não achei documento oficial. Resultados de busca (ICCT, Diário do Transporte, estudos de 2025) não foram abertos na origem e não foram usados como fonte de número |

## Dúvidas para a equipe

1. Ocupação média do carro e do ônibus: sem número oficial lido. O exemplo usa ocupação 1 para o carro, como premissa declarada.
2. CPTM: sem dado. A viagem "trem ou metrô" usa o Metrô.
3. Gasolina C: o fator de 2,23 kg/L é de gasolina A. O ensaio do INMETRO usa E22; o teor atual de posto não foi verificado.
4. Os g CO2/km do INMETRO (Mobi: 106) e litros × fator (cerca de 116 a 149) divergem. Não misturar os dois métodos.
5. Valores lidos por posição de célula em PDF (ônibus 2,10 km/L, fatores kg/L, linha de São Paulo da ANP): conferir olhando o documento.
6. Períodos diferentes entre as fontes (2025 para Metrô e SIN, 2026 para PBEV e preços): declarar na tela.

## Conteúdo de página que tentou dar instrução

Nenhuma página lida trazia instrução dirigida ao agente. Os únicos textos estranhos foram as verificações anti-robô do gov.br, ignoradas.
