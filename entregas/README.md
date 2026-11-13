# Entregas por matéria

Uma pasta por matéria que entrega código. Cada uma tem o próprio README, roda sozinha e aponta onde
está sua parte no repositório compartilhado, como os enunciados pedem.

| matéria | pasta | como rodar | código |
|---|---|---|---|
| **PCP** · Pensamento Computacional | [`pcp/citizen-assist-ai/`](pcp/citizen-assist-ai/) | `python main.py` | pronto |
| **DSA** · Data Structures | [`dsa/`](dsa/) | `python main.py` | pronto |
| **SERS** · Energias Renováveis | [`sers/`](sers/) | `python comparar_energia.py` | pronto |
| **MLAM** · Modelagem Linear | [`mlam/`](mlam/) | `python main.py` | pronto |
| **PAI** · Prompt and AI | [`pai/`](pai/) | `python main.py` · `python avaliar.py` | pronto |

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
| PAI | `sistema/adaptadores/pai.py` e a ferramenta `perguntar_fichas` em `sistema/assistente.py` — a Lia chama o agente da PAI (ver abaixo) |

## Atenção na PAI

O enunciado fixava fichas de documentos pessoais (Central do Cidadão de Aurora). Em 13/11/2026 o
professor autorizou manter as mesmas regras e trocar o tema pelo do grupo. A entrega é o agente em
LangGraph de [`pai/`](pai/), que responde só pelas 7 fichas de transporte (FT-01 a FT-07) e cita a
ficha; o juiz e a rodada antes e depois rodam com ele isolado, como o enunciado pede.

No app são duas coisas que trabalham juntas: a **Lia** conduz a conversa (viagem, linhas, alertas) e,
quando a dúvida é de regra ou procedimento, **chama o agente da PAI** como ferramenta. Detalhes em
[`pai/README.md`](pai/README.md).
