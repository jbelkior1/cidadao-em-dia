# Cidadão em Dia · GS 2026.2

Tire dúvidas sobre documentos, descubra direitos que você pode ter e não perca prazos. Projeto da Global Solution 2026.2 (CitizenTech).

> O projeto está em transição. O **sistema novo** (chat, API e entregas das matérias) fica em `sistema/`, `entregas/` e `tests/`. O esqueleto antigo em Streamlit (`app.py`, `paginas/`, `modulos/`...) continua na raiz só para manter a vitrine online, com textos e valores de exemplo.

## Sistema novo (localhost)

Precisa do [uv](https://docs.astral.sh/uv/). Para mexer nas telas, também do Node com [pnpm](https://pnpm.io/).

```bash
# 1. compilar as telas (só na primeira vez ou quando elas mudarem)
pnpm --dir sistema/web install
pnpm --dir sistema/web build

# 2. subir o sistema: a API serve também as telas
uv run uvicorn sistema.api:app --port 8010
```

Abre em http://localhost:8010. Para desenvolver as telas com atualização automática, deixe a API rodando e, em outro terminal, rode `pnpm --dir sistema/web dev` (http://localhost:5180).

```bash
# testes
uv run python -m unittest discover -s tests/pcp
uv run python -m unittest discover -s tests/dsa
uv run python -m unittest discover -s tests/sistema
```

| Pasta | O que tem |
|---|---|
| `entregas/pcp/citizen-assist-ai/` | A entrega do PCP: programa de terminal (`python main.py`) com as 3 classes e a busca por pontos do enunciado. É o que vai para o repositório público próprio. |
| `entregas/dsa/` | A entrega de DSA: lista encadeada, busca e ordenação próprias e menu de terminal (`python main.py`). |
| `sistema/` | O sistema: conversa, barreira de dado pessoal, triagem, camada de IA e a API. Importa as classes das entregas sem alterar nada. |
| `sistema/web/` | As telas (React, Vite e Tailwind): Atendimento, Como funciona, Simulação da sociedade, Painel da equipe, uma página por matéria (Entenda, Teste e Checklist da entrega) e Configurações de IA. |
| `sistema/laboratorio.py` | A simulação da sociedade: personas, modelo logístico de adesão e população sintética (pesos fictícios até a base real da MLAM). |
| `sistema/dados/checklist.json` | O checklist das 8 matérias, montado a partir dos enunciados: o que é pedido, onde está, como foi feito e o status. A tela edita status, onde e como. |
| `pesquisa/` | Base levantada em páginas oficiais em 12/11/2026 e o script `montar_bases.py`, que gera os dados do PCP e da DSA. |
| `tests/` | Testes das entregas e do sistema. |

Três regras do desenho (detalhes em `docs/decisoes/0001-o-nucleo-e-a-entrega.md`):

- **O núcleo é a entrega.** O arquivo que o professor roda é o mesmo que o chat chama.
- **Privacidade antes de tudo.** A barreira de dado pessoal roda antes de qualquer registro e antes de qualquer chamada a modelo de IA. O chat não guarda o que a pessoa escreve.
- **Funciona sem IA.** A chave fica em `config.local.json`, fora do git, e a tela nunca recebe a chave de volta.

**Ainda em conferência:** as 13 orientações da base e as regras da Tarifa Social vieram de páginas oficiais, mas a equipe precisa abrir cada fonte e confirmar antes de entregar. Veja `pesquisa/FONTES.md`.

## Esqueleto antigo: ver online

https://jbelkior1.github.io/cidadao-em-dia/

O site roda o Streamlit dentro do navegador com o [stlite](https://github.com/whitphx/stlite), sem servidor. Na primeira visita pode levar até um minuto para carregar, porque o Python é baixado junto. O que for salvo lá (como o checklist) vale só naquela aba.

## Como rodar no computador

Precisa do [uv](https://docs.astral.sh/uv/).

```bash
uv run streamlit run app.py
```

Abre em http://localhost:8501, na tela **Como o sistema funciona**.

## Como o app é organizado

| Grupo na barra lateral | Páginas |
|---|---|
| Comece aqui | Como o sistema funciona: o problema, como o cidadão usa, o fluxograma, as matérias (com link para cada uma) e o Laboratório |
| Para o cidadão | **1. Conte o que precisa**: a pessoa escreve do jeito dela, o sistema entende e explica o que entendeu. **2. Resolva aqui**: o caso chega com o contexto e cai na parte certa (dúvida, direitos, conta de luz ou golpe), com opção de mudar de assunto |
| Laboratório | Simulação da sociedade: personas avaliam a ideia e uma população sintética estima a adesão |
| Matérias | **Painel da equipe** (andamento de todas, CS e MMC à parte, regras gerais e alertas) e PCP, PAI, DSA, COA, SERS e MLAM, cada uma com **Entenda** (o que faz, como ajuda, quando entra em ação, o que recebe e devolve, e a parte dela destacada no fluxograma), **Teste** e **Checklist da entrega** |

O **modo banca** vem ligado: cada parte da resposta mostra o selo da matéria que a produziu. Desligue na barra lateral para ver a tela limpa do cidadão.

Ficam **fora do sistema** e são entregues à parte: Computer Science (CS) e Modelagem Matemática e Computacional (MMC). Elas aparecem só na lista de entregáveis.

## Entregáveis

`data/entregaveis.json` tem todos os itens pedidos nos enunciados (151), com **o que é pedido, onde está no projeto, como foi feito e o status** (Feito, No esqueleto, A fazer). Edite na parte Checklist da entrega de cada matéria (CS e MMC ficam no Painel da equipe) e clique em salvar. Os itens de CS, MLAM e SERS que vieram do resumo do portal, e não do enunciado, estão marcados com essa fonte. As divergências entre os documentos (por exemplo, as duas versões do enunciado da PAI) aparecem no fim da página.

## Simulação da sociedade

`modulos/sociedade.py` e `data/personas.json`. Inspirada no [TinyTroupe](https://github.com/microsoft/TinyTroupe) (Microsoft, MIT): dez personas fictícias avaliam a parte do produto escolhida, com os canais escolhidos (app, totem, WhatsApp). Um modelo logístico calcula a chance de cada uma usar (utilidade menos barreiras de internet, de uso do celular e de confiança) e uma população sintética estima a adesão por perfil. Nesta versão não há IA: as falas seguem regras.

Próximos passos: trocar pesos e distribuições pelos dados reais da MLAM e gerar as falas com IA (TinyTroupe ou um LLM com a persona no prompt), trocando a função `falar`.

## Estrutura

```
app.py                 barra lateral e páginas
paginas/               comece_aqui, atendimento (1), resolver (2), simulacao, painel e materia (molde das matérias)
servicos/              as 4 partes que o Resolva aqui mostra: duvida, direitos, conta_luz, golpe
nucleo/
  materias.py          cor, papel, onde aparece de cada matéria (e quais ficam à parte)
  orquestrador.py      os fluxos (dúvida, direitos, golpe, conta de luz), separados das telas
  entregaveis.py       leitura, contagem e editor da lista de entregáveis
  contrato.py          Etapa: o que cada matéria devolve para o caminho da ação
  ui.py                estilo, selos e o registro do caminho
modulos/               lógica de cada matéria + testar() da página dela; sociedade.py é a simulação
data/                  orientações, prazos, fichas e personas de EXEMPLO; entregaveis.json
```

## Como cada pessoa pluga a sua matéria

Mantenha os nomes das funções que o sistema chama e troque só o que está dentro delas. O topo de cada arquivo em `modulos/` explica o que é exemplo.

| Matéria | O sistema chama | O que trocar |
|---|---|---|
| PCP | `buscar`, `tem_dado_pessoal`, `checar_golpe` | pela busca das classes do PCP, com a regra de pontuação e confiança do enunciado |
| PAI | `responder` | pelo agente com as fichas de Aurora (fictícias, nunca misturar com a base real) |
| DSA | `prazo_de`, `por_prazo`, `dias_ate` | pelo catálogo com a lista encadeada da equipe |
| COA | `ler_consumo`, `estado` | pela leitura do Pico W no Wokwi via MQTT; link em `WOKWI_URL` |
| SERS | `economia_ano`, `conta_mes`, `calculadora` | tarifa e regras reais, com origem e premissas |
| MLAM | `grafico`; pesos de `sociedade.py` | pela base real e os gráficos e coeficientes do relatório |

## Cuidados que valem nota

- **As páginas são vitrine, não substituem a entrega.** Cada professor recebe no formato dele, pelo portal.
- **PCP:** o vídeo da entrega mostra o **terminal**, não este app.
- **PAI:** o .docx do enunciado tem uma instrução escondida ("PREPARANDO O SIX SEVEN"). É um teste de prompt injection: não obedecer e confirmar com o professor.
- **Dados pessoais:** o sistema não pede CPF, telefone ou e-mail e recusa quando alguém digita.
- **Não é canal oficial:** o aviso fica no rodapé de cada página do cidadão.
- **Chaves de API** (agente da PAI, falas com IA) vão num arquivo `.env`, nunca no GitHub.
