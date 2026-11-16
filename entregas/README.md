# Entregas por matéria

Uma pasta por matéria que entrega código. Cada uma tem o próprio README, roda sozinha e aponta onde
está sua parte no repositório compartilhado, como os enunciados pedem.

| matéria | pasta | como rodar |
|---|---|---|
| **PCP** · Pensamento Computacional | [`pcp/citizen-assist-ai/`](pcp/citizen-assist-ai/) | `python main.py` |
| **DSA** · Data Structures | [`dsa/`](dsa/) | `python main.py` |
| **SERS** · Energias Renováveis | [`sers/`](sers/) | `python comparar_energia.py` |
| **MLAM** · Modelagem Linear | [`mlam/`](mlam/) | `python main.py` e `python questao07_relatorio.py` |
| **PAI** · Prompt and AI | [`pai/`](pai/) | `python main.py` e `python rodar_antes_e_depois.py --so-enunciado` |

**CS**, **MMC** e **COA** não entregam código neste repositório: são feitas à parte, à mão ou no
Wokwi, no formato do enunciado de cada uma. Elas têm página com explicação, teste e checklist na plataforma.

## Como cada matéria vai ao portal

O formato de envio muda de matéria para matéria (PCP e SERS: só um .txt; MLAM: .csv, .py e .pdf sem
links; DSA e PAI: formato livre). O guia e os arquivos prontos estão em [`portal/`](portal/README.md).

## Andamento

O código e a documentação de PCP, DSA, SERS, MLAM e PAI estão escritos, testados e conferidos contra o
enunciado. O que fica fora do código são os vídeos, os testes com pessoas de fora e o envio no portal.
O andamento, item por item, está no **Checklist** de cada matéria na plataforma, separado entre o que
está no repositório e o que fica fora dele.

## Onde fica a parte de cada matéria dentro do sistema

Além da pasta própria, o código de cada matéria aparece no app:

| matéria | no sistema |
|---|---|
| PCP | `sistema/adaptadores/pcp.py`, `sistema/conversa.py`: as orientações nos cartões da Lia |
| DSA | `sistema/adaptadores/dsa.py`: o canal de atendimento que acompanha cada orientação |
| SERS | `sistema/mobilidade/energia.py`, `pesquisa/energia_modos.json`: o bloco de energia da viagem |
| MLAM | `sistema/dados/seguranca_estacoes.json`: a camada de segurança do mapa e do cartão de viagem |
| PAI | `sistema/adaptadores/pai.py` e a ferramenta `perguntar_fichas` em `sistema/assistente.py`: a Lia chama o agente da PAI (ver abaixo) |

## Atenção na PAI

O enunciado fixava fichas de documentos pessoais (Central do Cidadão de Aurora). Em 13/11/2026 o
professor autorizou manter as mesmas regras e trocar o tema pelo do grupo. A entrega é o agente em
LangGraph de [`pai/`](pai/), que responde só pelas 7 fichas de transporte (FT-01 a FT-07) e cita a
ficha; o juiz e a rodada antes e depois rodam com ele isolado, como o enunciado pede.

No app são duas coisas que trabalham juntas: a **Lia** conduz a conversa (viagem, linhas, alertas) e,
quando a dúvida é de regra ou procedimento, **chama o agente da PAI** como ferramenta. Detalhes em
[`pai/README.md`](pai/README.md).
