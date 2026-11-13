# 0002 · Dá Tempo?: escopo da v2 e ordem de construção

Data: 13/11/2026. Origem: reunião do grupo de 12/11 (ata do Gemini) e respostas do João Belchior no dia seguinte. A análise completa está em `projeto/Auxilia_v2_Analise_da_Reuniao.pdf` (o nome do arquivo é do nome provisório).

## Decisões fechadas

| Tema | Decisão |
|---|---|
| Nome | App **Dá Tempo?**; agente (chatbot) **Lia**. Escolhido por mim a pedido do grupo. Conferir loja e INPI antes de usar fora da faculdade. |
| Telas | 4 abas: **Home** (feed de relatos), **Mapa**, **IA** (a Lia) e **Perfil**. SOS e sinal de alerta ficam no cabeçalho de todas as abas. |
| Login | Ler o feed **sem conta**. Ficou a confirmar se há conta para postar, usar a IA e ter perfil, ou nenhuma (ver "Em aberto"). |
| Privacidade | Sem GPS, sem foto, sem texto livre no feed, sem gravar o que se escreve à IA. Apelido no lugar de nome. |
| Lotação | Estimativa por relatos de passageiros, sempre rotulada "não é dado oficial". |
| SOS | Abre o SMS ou a ligação já preenchidos. Não envia nada e não é canal de emergência. Os canais vêm do catálogo da DSA. |
| WhatsApp | **Fora por enquanto**: sem botão, sem automação. A mensagem de atraso só tem "Copiar". |
| MiroFish | Fica para depois. Primeiro as outras partes do sistema. |
| Matérias | No sistema: PCP, DSA, SERS, MLAM e PAI. À parte: **CS, COA e MMC** (com outro integrante). CS proíbe IA na tabela-verdade, no Karnaugh e no circuito (−4 pontos). Os enunciados de COA e MMC não falam de IA, nem para proibir nem para permitir (conferido em 13/11). |
| PAI | O professor autorizou em 13/11 manter as regras do enunciado e trocar as fichas de Aurora pelo tema do grupo: 7 fichas de transporte (FT-01 a FT-07). Na conversa, a Lia chama o agente da PAI como ferramenta. |
| Cores | Laranja e branco, sem modo escuro. Marca `#c2410c` (passa 4,5:1 com texto branco); o amarelo de "atenção" fica separado. |

## Ordem de construção (definida por mim, com o critério "o que o pitch e as matérias precisam")

**Feito nesta etapa (não depende do banco):** nome e cores; casca de 4 abas; mapa com camadas (linhas, alagamentos, segurança, relatos); feed de relatos em memória; SOS; perfil local.

**Próximo, ainda sem banco:**
1. A Lia usa os relatos (ferramenta nova) e responde "como está a Linha 3?" com o que os passageiros relataram.
2. Modo de gravação: simular temporal e alagamento (hoje só simula falha de linha) e semear relatos de demonstração, tudo marcado como simulação.

> Situação em 13/11, fim do dia: os itens 1 e 2 foram feitos, e o banco foi ligado (Supabase, esquema
> `datempo`). Do item 3, os relatos já persistem; histórico das linhas, simulações e Realtime seguem abertos.

**Depende do banco (Supabase):**
3. Relatos, histórico das linhas e simulações persistentes; tempo real pelo Realtime.
4. Rotinas e aviso antes de sair (caixa de entrada + notificação no aparelho).
5. Simulação da sociedade com Gemini, guardada no banco.
6. Cota de uso da IA por pessoa (ou por aparelho, se não houver conta).

**Fora por enquanto:** WhatsApp, foto, GPS, MiroFish, Telegram, dashboard, modo escuro, rota de ônibus e de rua.

## Em aberto

- **Conta ou nenhuma conta para postar e usar a IA?** Entendi "não precisa de login" como "ler o feed sem conta". Se for nenhuma conta em lugar nenhum, o banco fica mais simples (código aleatório do aparelho em vez de login) e a cota da IA passa a ser por aparelho. A casca já funciona dos dois jeitos.
- ~~Como o banco será acessado~~ Resolvido: chaves no `.env` (fora do git), pela API REST; nunca no chat.

## Consequências

- O feed e o perfil nascem com repositório trocável (memória agora, Supabase depois), então a ligação do banco não obriga a reescrever telas.
- As matérias não ganham nem perdem integração por causa do feed e do mapa: só a SERS exige integração com o assistente.
