# Entregas por matéria

Uma pasta por matéria que entrega código. Cada uma tem o próprio README, roda sozinha e aponta onde
está sua parte no repositório compartilhado, como os enunciados pedem.

| matéria | pasta | como rodar | código |
|---|---|---|---|
| **PCP** · Pensamento Computacional | [`pcp/citizen-assist-ai/`](pcp/citizen-assist-ai/) | `python main.py` | pronto |
| **DSA** · Data Structures | [`dsa/`](dsa/) | `python main.py` | pronto |
| **SERS** · Energias Renováveis | [`sers/`](sers/) | `python comparar_energia.py` | pronto |
| **MLAM** · Modelagem Linear | [`mlam/`](mlam/) | `python main.py` | pronto |
| **PAI** · Prompt and AI | [`pai/`](pai/) | — | **parado, falta material** |

**CS**, **MMC** e **COA** não entregam código neste repositório: são feitas à parte, à mão ou no
Wokwi, no formato do enunciado de cada uma. Elas continuam com página, teste e checklist no sistema.

## O que "pronto" quer dizer aqui

Só que **o código está escrito e rodando**. Cada enunciado pede também coisas que só a equipe faz:
gravar o vídeo, testar com pessoas de fora, preencher nome e RM, criar o repositório público, conferir
cada fonte e enviar no portal. O andamento completo, item por item, está no sistema, em
**Painel da equipe** e no **Checklist da entrega** de cada matéria, separado entre o que é código e o
que é da equipe.

## Onde fica a parte de cada matéria dentro do sistema

Além da pasta própria, o código de cada matéria aparece no app:

| matéria | no sistema |
|---|---|
| PCP | `sistema/adaptadores/pcp.py`, `sistema/conversa.py` — as orientações nos cartões da Lia |
| DSA | `sistema/adaptadores/dsa.py` — o canal de atendimento que acompanha cada orientação |
| SERS | `sistema/mobilidade/energia.py`, `pesquisa/energia_modos.json` — o bloco de energia da viagem |
| MLAM | `sistema/dados/seguranca_estacoes.json` — a camada de segurança do mapa e do cartão de viagem |
| PAI | `sistema/assistente.py`, `sistema/ia.py`, `sistema/privacidade.py` — a Lia no produto (ver abaixo) |

## Atenção na PAI

A **Lia do produto** (que conversa, chama as ferramentas e barra dado pessoal) está pronta e
funcionando — mas ela **não é** a entrega da matéria. O professor fixou outro assistente: documentos
pessoais, com as 7 fichas FC-01 a FC-07 da Central do Cidadão de Aurora e um golden dataset de 26
mensagens. São duas bases e dois assistentes diferentes, então o que existe no app não conta para a
nota da PAI. Detalhes e o que está travando em [`pai/README.md`](pai/README.md).
