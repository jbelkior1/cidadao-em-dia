# 0001 · O núcleo é a entrega

Data: 12/11/2026 · Situação: em vigor

## Contexto

Cada professor corrige a própria entrega, no formato do enunciado: programa de terminal no PCP e na DSA, notebook na PAI, arquivos na MLAM, repositório e vídeo na SERS. Nenhum avalia o sistema integrado. A exceção é a SERS, que exige a análise de energia aparecendo nas respostas do assistente. O prazo é 19/11/2026.

O esqueleto anterior misturava regra e tela: todo módulo importava o Streamlit e não rodava sozinho.

## Decisão

1. Cada matéria vira uma pasta em `entregas/`, em Python puro, que roda sozinha no formato do enunciado. O sistema importa essas classes por adaptadores (`sistema/adaptadores/`) e não reescreve regra nenhuma.
2. O sistema é uma API em Python (FastAPI) e uma interface só em React. Sem banco de dados: o PCP exige arquivos JSON e CSV, a PAI penaliza guardar histórico, e o chat não precisa guardar nada.
3. O servidor não guarda a conversa. A tela mantém o estado e devolve a cada mensagem.
4. A barreira de dado pessoal roda antes de qualquer registro e antes de qualquer chamada a modelo. Só o texto da base vai para o modelo, nunca o que a pessoa escreveu.
5. A camada de IA é um cliente único no formato OpenAI, que atende Groq, Ollama e Gemini. Sem chave, tudo funciona por regras.
6. COA, CS e MMC ficam fora do sistema e são entregues à parte.

## Consequências

- A integração deixa de ser colagem: o chat mostra a mesma pontuação que o programa de terminal do PCP calcula.
- A entrega do PCP continua tendo exatamente 4 arquivos `.py`, e os testes ficam fora dela.
- Trocar a interface no futuro não mexe em nenhuma entrega.
- Sem banco, o checklist da equipe e os indicadores do chat não são compartilhados entre computadores. Se isso fizer falta, entra depois.

## O que ficou de fora de propósito

- Anexo de arquivo (conta de luz, carta): a PAI lista foto de documento como dado pessoal.
- Triagem por modelo de IA sobre o texto do cidadão: exigiria mandar o texto para fora.
