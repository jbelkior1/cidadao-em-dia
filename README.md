# Dá Tempo? · Global Solution 2026.2

Saiba antes de sair se o seu trem vai te deixar na mão. App de trem e metrô de São Paulo feito na Global Solution 2026.2 da FIAP (CitizenTech, case Citizen Assist AI).

**Integrantes:** João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e Thiago de Oliveira Coelho Souza (RM 568783). Turma 1CC, Ciência da Computação.

## O que é

A **Lia**, agente do app, acompanha a pessoa antes de sair: confere a situação das linhas das seis operadoras, o aviso de chuva do INMET, os alagamentos do CGE da Prefeitura, a segurança perto das estações (SSP-SP) e o que os outros passageiros relataram, e responde com uma decisão só: **Pode ir**, **Saia mais cedo** ou **Mude o caminho**, com a chegada prevista e o desvio quando uma linha para. Toda resposta mostra a fonte e a hora da leitura, e dado pessoal (CPF, telefone, e-mail, endereço) é barrado antes de chegar à IA.

O app tem quatro abas (**Home** com os relatos dos passageiros, **Mapa**, **IA** com a Lia e **Perfil** com conta opcional de usuário e senha), com **SOS** e **sinal de alerta** em todas.

## Para os professores

**Plataforma no ar:** https://datempo.srv1596654.hstgr.cloud

Cada matéria tem a entrega no formato do seu enunciado. O código que o professor corrige é o mesmo que o app usa.

| Matéria | Onde está a entrega | Como rodar | No sistema |
|---|---|---|---|
| **PCP** · Pensamento Computacional | [`entregas/pcp/citizen-assist-ai/`](entregas/pcp/citizen-assist-ai/) | `python main.py` | Orientações oficiais nos cartões da Lia (busca por pontos) |
| **DSA** · Data Structures | [`entregas/dsa/`](entregas/dsa/) | `python main.py` | Catálogo de serviços (lista encadeada) que dá o canal de atendimento e o SOS |
| **SERS** · Energias Renováveis | [`entregas/sers/`](entregas/sers/) | `python comparar_energia.py` | Energia, custo e CO₂ da viagem no cartão da Lia |
| **MLAM** · Modelagem Linear | [`entregas/mlam/`](entregas/mlam/) | `python main.py` e `python questao07_relatorio.py` | Segurança perto das estações (SSP-SP) |
| **PAI** · Prompt and AI | [`entregas/pai/`](entregas/pai/) | `python main.py` e `python avaliar.py` | Agente das fichas (LangGraph) que a Lia chama nas dúvidas de regra |
| **CS** · Computer Science | entregue à parte (relatório e simulação) | | Página com explicação e checklist |
| **MMC** · Modelagem Matemática | entregue à parte | | Página com explicação, teste e checklist |
| **COA** · Computer Organization | entregue à parte, no Wokwi | | Página com explicação e checklist |

Na plataforma, cada matéria tem uma página com **Entenda** (o que faz, a entrega e os arquivos no GitHub), **Teste** (o núcleo da matéria rodando) e **Checklist** (o que o enunciado pede e o que está pronto). O guia de entrega no portal, matéria por matéria, está em [`entregas/portal/`](entregas/portal/).

## A plataforma

| Página | O que tem |
|---|---|
| **Como funciona** | O problema, como o sistema resolve, o fluxograma e onde cada matéria entra |
| **Sistema** | O app funcionando dentro de um celular (no celular de verdade, em tela cheia) |
| **Teste da sociedade** | Passageiros simulados vivendo uma situação do dia com o sistema de verdade |
| **Matérias** | Uma página por matéria: Entenda (com o fluxograma da matéria), Teste e Checklist, com o botão para baixar o pacote (.zip) da entrega |
| **Documentação funcional** | Tudo o que a plataforma faz, tela por tela ([`docs/DOCUMENTACAO_FUNCIONAL.md`](docs/DOCUMENTACAO_FUNCIONAL.md)) |

O **Modo banca** mostra, ao lado do app, qual matéria fez cada parte da última resposta. Para abrir só o app em tela cheia, direto pelo celular, use o endereço `/app`.

## Como rodar no computador

Precisa do [uv](https://docs.astral.sh/uv/) e, para as telas, do Node com [pnpm](https://pnpm.io/).

```bash
pnpm --dir sistema/web install
pnpm --dir sistema/web build
uv run uvicorn sistema.api:app --port 8010
```

Abre em http://localhost:8010. Sem configuração de IA, a Lia responde pelas regras e pela base; a chave fica em `config.local.json` (fora do git) ou nas variáveis de ambiente.

Testes automáticos (não dependem da internet):

```bash
uv run python -m unittest discover -s tests/sistema
uv run python -m unittest discover -s tests/pcp
uv run python -m unittest discover -s tests/dsa
uv run python -m unittest discover -s tests/pai
```

Servidor público (Docker): passo a passo em [`DEPLOY.md`](DEPLOY.md).

## Pastas

| Pasta | O que tem |
|---|---|
| `sistema/` | API (FastAPI), a Lia (`assistente.py`), barreira de dado pessoal, camada de IA, relatos, contas, mapa, SOS, testes das matérias, teste da sociedade e checklist |
| `sistema/mobilidade/` | Rede (GTFS, Dijkstra com custo de baldeação e desvio), fontes ao vivo (linhas, INMET, CGE), decisão do dia, energia e a montagem da viagem |
| `sistema/web/` | As telas (React, Vite e Tailwind) |
| `sistema/dados/` | Rede de trem e metrô, segurança por estação, personas e o checklist das entregas |
| `entregas/` | As entregas de PCP, DSA, SERS, MLAM e PAI no formato de cada enunciado, e o guia do portal |
| `pesquisa/` | Bases levantadas em fontes oficiais (orientações, serviços e energia) |
| `banco/migracoes/` | SQL do esquema `datempo` no Supabase (relatos e contas) |
| `docs/` | Documentação funcional e decisões de arquitetura |
| `tests/` | Testes das entregas e do sistema |

## Fontes de dados

GTFS da SPTrans (rede), agregador público dos avisos das operadoras (situação das linhas, não oficial), INMET (chuva), CGE da Prefeitura e GeoSampa (alagamentos), SSP-SP (ocorrências de 2026 por estação), MCTI, Metrô, INMETRO e ANP (energia). Detalhes, atualização e limitações na [documentação funcional](docs/DOCUMENTACAO_FUNCIONAL.md).

## Cuidados

- **Não é canal oficial** das operadoras nem da Defesa Civil, nem canal de emergência; o app mostra a fonte e a hora de cada informação.
- **Privacidade:** sem conta, nada da pessoa fica no servidor; o que ela escreve para a Lia não é guardado. A conta opcional guarda só usuário, hash da senha, linhas, estação de casa e rotas.
- **PAI:** o .docx do enunciado traz uma instrução escondida; foi tratada como teste de prompt injection e não foi obedecida. A troca do tema para transporte foi autorizada pelo professor em 13/11/2026.
- **CS:** tabela-verdade, Karnaugh e circuito são da equipe, feitos à mão, e entregues à parte.
- **MLAM:** a base conta registros perto da estação, sem o fluxo de passageiros; não é taxa de risco.
