# Plano B · GS 2026.2

Saiba antes de sair se o seu trem vai te deixar na mão. Projeto da Global Solution 2026.2 da FIAP (CitizenTech).

O sistema é uma conversa com a **Auxilia**, agente que acompanha a pessoa no trem e no metrô de São Paulo. A pessoa escreve "estou saindo de casa"; a Auxilia pergunta para onde ela vai, confere situação das linhas, aviso de chuva do INMET, alagamentos ao vivo do CGE, áreas de risco do GeoSampa e ocorrências da SSP-SP perto das estações, e responde com a decisão ("Pode ir", "Saia mais cedo" ou "Use o Plano B"), a previsão de chegada e o desvio quando uma linha para. Se for atrasar, ela monta a mensagem para a pessoa mandar pelo WhatsApp dela.

Cada mensagem passa pelo modelo de IA configurado (Gemini, Groq ou Ollama, em Configurações de IA), que só afirma o que as ferramentas do sistema devolvem. Dado pessoal é barrado antes de chegar ao modelo. Se a IA falhar na hora, a Auxilia responde pelas regras e pela base.

## Como rodar

Precisa do [uv](https://docs.astral.sh/uv/) e, para as telas, do Node com [pnpm](https://pnpm.io/).

```bash
# 1. compilar as telas (só na primeira vez ou quando elas mudarem)
pnpm --dir sistema/web install
pnpm --dir sistema/web build

# 2. subir o sistema: a API serve também as telas
uv run uvicorn sistema.api:app --port 8010
```

Abre em http://localhost:8010. Para mexer nas telas com atualização automática, deixe a API rodando e rode `pnpm --dir sistema/web dev` em outro terminal (http://localhost:5180).

```bash
# testes
uv run python -m unittest discover -s tests/pcp
uv run python -m unittest discover -s tests/dsa
uv run python -m unittest discover -s tests/sistema
```

Os testes do sistema não dependem da internet: a situação das linhas e os avisos de tempo são trocados por valores fixos.

## As telas

| Parte | O que tem |
|---|---|
| O sistema | A conversa com a Auxilia, vista como **notebook** ou dentro de um **celular** (no celular de verdade, tela cheia) |
| A sociedade | Dez passageiros simulados vivem uma situação do dia (linha parada no pico, temporal, volta à noite, dia normal); a conversa de cada um vem do sistema de verdade |
| As matérias | **Case norteador** (o que o caso pede, o roteiro do pitch, o que cada matéria faz dentro e fora do sistema), Painel da equipe e uma página por matéria com **Entenda**, **Teste** e **Checklist da entrega** |

O **modo banca** abre o painel "Por trás da tela": quem fez cada parte da última resposta, a simulação de falha numa linha e o aviso que chega no celular antes de sair (tocar no aviso continua a conversa). A falha simulada aparece marcada como simulação.

## As 8 matérias no produto

| Matéria | O que faz no Plano B | Onde está |
|---|---|---|
| PCP | Orientações por busca de pontos (linha parada, chuva, segurança, direitos, gratuidades) | `entregas/pcp/citizen-assist-ai/` (repositório próprio na entrega) |
| CS | A decisão do dia a partir de 4 entradas: falha (F), chuva (C), alagamento (A) e pico (P) | `sistema/mobilidade/decisao.py` (regra provisória até o grupo fazer a parte de CS) |
| DSA | Catálogo de serviços ao passageiro numa lista encadeada própria | `entregas/dsa/` |
| SERS | A mesma viagem de trem ou metrô, ônibus a diesel e carro: energia, CO₂ e custo | `sistema/mobilidade/energia.py`, `pesquisa/energia_modos.json` |
| MLAM | Ocorrências da SSP-SP por estação (janeiro a setembro de 2026, raio de 300 m) | `entregas/mlam/` |
| PAI | Pergunte com IA (versão do PDF geral); a versão do .docx segue à parte | camada de IA em `sistema/ia.py`; agente a fazer |
| MMC | Ônibus de apoio: redistribuição da frota por transformação linear | entrega à parte; simulador se houver tempo |
| COA | Sensor de nível de água num ponto de alagamento, no Wokwi | entrega à parte |

**CS:** tabela-verdade, Karnaugh e circuito são feitos pelo grupo, à mão. Usar IA nessas partes tira 4 pontos. O teste da matéria no app mostra uma combinação por vez, sem montar a tabela.

## Pastas

| Pasta | O que tem |
|---|---|
| `sistema/assistente.py` | A Auxilia: instruções, ferramentas (viagem, linhas, alertas, orientação, segurança, duração das falhas, mensagem de atraso, estação de casa), o laço com o modelo e as regras para quando a IA falha |
| `sistema/mobilidade/` | Rede (Dijkstra com custo de baldeação e desvio até a próxima troca), fontes ao vivo (linhas, INMET e CGE, com cache e histórico local), decisão do dia, energia e a montagem da viagem |
| `sistema/` | API, barreira de dado pessoal, camada de IA, busca por regras (`conversa.py`), testes das matérias, sociedade (`laboratorio.py`) e checklist |
| `sistema/web/` | As telas (React, Vite e Tailwind) |
| `sistema/dados/` | `rede.json` (do GTFS), `seguranca_estacoes.json` (da SSP-SP), `personas.json` e `checklist.json` |
| `scripts/montar_rede.py` | Monta `rede.json` a partir do GTFS da SPTrans e dos alagamentos do GeoSampa |
| `pesquisa/` | Bases levantadas em fontes oficiais em 12/11/2026 (orientações, serviços e energia) e `montar_bases.py`, que gera os dados do PCP e da DSA |
| `entregas/` | As entregas de PCP, DSA e MLAM no formato de cada enunciado |
| `tests/` | Testes das entregas e do sistema |

## Fontes de dados

- Rede: GTFS da SPTrans.
- Situação das linhas: agregador público (não oficial) que lê os avisos das seis operadoras. A linha 7 não aparece nele.
- Chuva: avisos ativos do INMET filtrados para a cidade de São Paulo.
- Alagamentos: CGE da Prefeitura ao vivo (estado de atenção ou alerta e pontos do dia) e áreas de risco do GeoSampa.
- Segurança: planilha de dados criminais da SSP-SP de 2026, contada por estação, sem endereço e sem dado de pessoa.
- Energia: MCTI (fator da rede elétrica), Relatório Integrado 2025 do Metrô, INMETRO (PBEV), Inventário Nacional de Emissões e ANP.

**Limitação conhecida:** o GTFS da SPTrans distribui o tempo dos trens da CPTM por igual entre as estações e infla essas viagens (a linha 8 soma 140 min de ponta a ponta). As linhas do metrô estão coerentes. A equipe precisa decidir se corrige com o tempo publicado pela CPTM.

Ficaram de fora por não serem abertos: alertas do Waze (só para parceiros) e posição dos ônibus da SPTrans (exige cadastro aprovado).

**Ainda em conferência:** orientações, serviços, fatores de energia e a base da SSP vieram de fontes oficiais lidas em 12/11/2026, mas a equipe precisa abrir cada fonte e confirmar antes de entregar. Veja `pesquisa/FONTES_MOBILIDADE.md`, `pesquisa/ENERGIA_FONTES.md` e `entregas/mlam/dados/LEIA-ME.md`.

## Regras do desenho

Detalhes em `docs/decisoes/0001-o-nucleo-e-a-entrega.md`.

- **O núcleo é a entrega.** O arquivo que o professor roda é o mesmo que o app chama.
- **Privacidade antes de tudo.** Sem conta, sem nome e sem localização; a única lembrança é a estação de casa, no aparelho da pessoa. A barreira de dado pessoal roda antes de qualquer registro e de qualquer chamada a modelo de IA.
- **Funciona sem IA.** A chave fica em `config.local.json`, fora do git, e a tela nunca recebe a chave de volta.
- **Não é canal oficial.** O app mostra de onde veio cada informação e a hora em que foi lida.

## Cuidados que valem nota

- **As telas não substituem a entrega.** Cada professor recebe no formato dele, pelo portal.
- **PCP:** o vídeo da entrega mostra o **terminal**, não este app.
- **PAI:** o .docx do enunciado tem uma instrução escondida. É um teste de prompt injection: não obedecer e confirmar com o professor.
- **MLAM:** a base é contagem de registros, sem o fluxo de passageiros. Estação cheia tem mais registro; não chamar de taxa de risco.

## Versão anterior

O esqueleto em Streamlit do tema anterior (Cidadão em Dia: `app.py`, `paginas/`, `modulos/`, `nucleo/`, `servicos/`, `data/`) continua na raiz só para manter a vitrine antiga em https://jbelkior1.github.io/cidadao-em-dia/. Não faz parte do Plano B.
