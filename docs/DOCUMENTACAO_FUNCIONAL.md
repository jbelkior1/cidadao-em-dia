# Documentação funcional do Dá Tempo?

O Dá Tempo? é um app de trem e metrô de São Paulo que avisa, antes de a pessoa sair, se a viagem vai dar certo: confere a situação das linhas, o aviso de chuva, os alagamentos e a segurança perto das estações, e responde com uma decisão só (**Pode ir**, **Saia mais cedo** ou **Mude o caminho**). Foi feito na Global Solution 2026.2 da FIAP (CitizenTech, case Citizen Assist AI) por João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e Thiago de Oliveira Coelho Souza (RM 568783).

Esta página descreve o que a plataforma faz, tela por tela, e as regras por trás de cada função.

## 1. Visão geral

- **Para quem:** qualquer pessoa que usa trem e metrô em São Paulo, sem cadastro.
- **O que resolve:** a informação que decide a viagem está espalhada (site de cada operadora, INMET, CGE da Prefeitura, SSP-SP). O app junta tudo numa resposta, com a fonte e a hora de cada leitura.
- **O que não é:** não é canal oficial das operadoras nem da Defesa Civil, não é canal de emergência e não confirma direito nenhum. Toda resposta mostra de onde veio a informação.

## 2. Como navegar na plataforma

| Página | Para que serve |
|---|---|
| **Como funciona** | O problema, como o sistema resolve, o fluxograma e onde cada matéria entra. É a primeira página. |
| **Sistema** | O app Dá Tempo? funcionando, dentro do desenho de um celular (no celular de verdade, em tela cheia). Dá para trocar para a vista de notebook. |
| **Teste da sociedade** | Passageiros fictícios vivem uma situação do dia usando o sistema de verdade; mostra quem usaria, as barreiras e as sugestões. |
| **Matérias** | Uma página por matéria com três partes: **Entenda** (o que faz, a entrega e os arquivos no GitHub), **Teste** (o núcleo da matéria rodando) e **Checklist** (o que o enunciado pede e o que está pronto). |
| **Documentação funcional** | Esta página. |

O **Modo banca**, no rodapé da barra lateral, abre ao lado do app (em tela grande) o painel "Por trás da tela": qual matéria fez cada parte da última resposta e o quadro **Simular para demonstrar**, que liga uma falha de mentira numa linha e mostra o aviso que chegaria antes de sair. A simulação vale só para quem está usando a tela e aparece marcada como simulação no app.

## 3. O app Dá Tempo?

O app tem quatro abas (Home, Mapa, IA e Perfil). Em todas aparecem o botão **SOS** e o **sinal de alerta**.

### 3.1 Home: o que os passageiros estão vendo

- Começa com **Para onde você vai?** (abre a conversa com a Lia) e atalhos para Relatar, Mapa, Linhas e SOS.
- **Agora nas linhas** resume, linha por linha, o que os passageiros estão relatando; **Relatos recentes** lista os relatos, com o filtro Todas ou Minhas linhas.
- **Relatar** leva dois toques: a linha e o que a pessoa vê (Lotado, Parado, Quebrou, Chuva, Alagamento, Segurança ou Tudo certo); a estação é opcional.
- Não há texto livre nem foto: assim não entra ofensa, dado pessoal nem instrução escondida para a IA.
- Regras do feed: um relato por pessoa e por linha a cada 10 minutos; cada relato vale 2 horas e perde peso com o tempo (metade a cada 30 minutos); outras pessoas confirmam ("ainda está assim") ou encerram ("já acabou"); três denúncias tiram o relato da lista; o alerta de uma linha só aparece quando pelo menos duas pessoas diferentes relatam o mesmo problema.
- Tudo isso é **estimativa por relatos de passageiros, não dado oficial**, e o app diz isso na tela.
- Não precisa de conta: o aparelho manda um código aleatório e o servidor guarda só um resumo (hash) dele.

### 3.2 Mapa

- Linhas de trem e metrô coloridas pela situação atual.
- Camadas que a pessoa liga e desliga: **Alagamentos** (pontos de alagamento do GeoSampa e o estado do CGE), **Segurança** (ocorrências da SSP-SP perto das estações) e **Relatos**.
- Abaixo do mapa há um resumo em texto com as mesmas informações, para quem usa leitor de tela.

### 3.3 IA: a Lia

A Lia é a agente que acompanha a viagem. A pessoa escreve do jeito dela ("estou saindo de casa", "vou da Sé para a Paulista", "como está a linha 9?").

- **Conferir uma viagem:** a Lia pergunta para onde a pessoa vai e de onde sai (ou usa a estação de casa) e devolve o cartão da viagem: a decisão do dia, a chegada prevista, o caminho com a situação de cada linha, o desvio quando uma linha falha, o que mudou e o que merece atenção, a segurança na saída e na chegada e a energia da viagem.
- **Perguntas de regra e procedimento** (declaração de atraso, gratuidade, reclamação, achados e perdidos, tarifa, assédio, acessibilidade): a Lia chama o agente das fichas da PAI, que responde só pelas 7 fichas de transporte e cita a ficha (FT-01 a FT-07).
- **Orientação oficial e canal de atendimento:** busca por pontos da PCP e o canal certo do catálogo da DSA.
- **Mensagem de atraso:** a Lia monta o texto com o motivo e a nova previsão; quem envia é a pessoa, pelo canal que preferir.
- **Estação de casa:** quando a pessoa diz onde mora, a Lia guarda a estação no aparelho para não perguntar de novo.
- A Lia só afirma o que as ferramentas do sistema trouxeram. Se a IA falhar ou o limite do dia acabar, ela responde pelas regras e pela base, e avisa.

### 3.4 Perfil e conta (opcional)

- **Sem conta:** as linhas marcadas e a estação de casa ficam só no aparelho.
- **Com conta:** usuário e senha, sem e-mail e sem telefone. As **minhas linhas**, a **estação de casa** e as **rotas salvas** ficam no banco e voltam em qualquer aparelho.
- **Rotas salvas:** nome, estação de saída, estação de chegada, horário e dias da semana (até 10 rotas). O botão **Conferir agora** abre a Lia já perguntando aquele trajeto.
- **Segurança da conta:** a senha é guardada embaralhada (hash scrypt), nunca como foi digitada; depois de 5 erros a conta fica bloqueada por 15 minutos; a mensagem de erro não diz se o usuário existe. Não há recuperação de senha.
- **Apagar:** "Apagar os dados deste aparelho" limpa o que está no aparelho; "Apagar minha conta" (pede a senha) apaga a conta, as linhas, a casa e as rotas do banco.

### 3.5 SOS

- Atalhos para 190 (Polícia), 192 (SAMU) e 193 (Bombeiros).
- Para as linhas do Metrô (1, 2, 3, 15 e 17), abre o SMS Segurança já com a linha e a estação escritas; CPTM, ViaQuatro e ViaMobilidade têm o canal de denúncia ou a central da linha; as linhas sem canal próprio no catálogo vão para a Ouvidoria da Artesp. Os canais vêm do catálogo da DSA.
- O app não envia nada sozinho: a pessoa confere e envia. Aviso fixo: o Dá Tempo? não é canal de emergência.

### 3.6 Sinal de alerta

No canto superior, um sinal com o número de alertas ativos: linhas com problema, aviso de chuva do INMET e estado de atenção ou alerta de alagamento do CGE. Tocar no sinal abre a lista e permite perguntar à Lia.

## 4. A decisão do dia

| Situação | Decisão |
|---|---|
| Falha numa linha do trajeto | **Mude o caminho** (com o desvio até a próxima troca) |
| Aviso de chuva junto com alagamento perto do trajeto ou horário de pico | **Saia mais cedo** |
| Nenhum dos casos acima | **Pode ir** |

Horário de pico: dias úteis, das 6h às 9h e das 16h às 19h30. Esta é a regra do produto, escrita como prioridades simples. A modelagem lógica pedida em Computer Science (tabela-verdade, Karnaugh e circuito) é feita pela equipe, à parte, e pode substituir esta regra mantendo as mesmas entradas e saídas.

## 5. Privacidade e dados pessoais

- **Barreira de dado pessoal:** antes de qualquer registro e de qualquer chamada ao modelo de IA, o sistema barra números longos como CPF e telefone (mesmo separados por espaços ou pontos), e-mail (inclusive escrito por extenso) e frases que anunciam um dado ("meu nome é", "moro na rua", "minha senha é"). A mensagem não segue e a pessoa recebe um aviso.
- **No aparelho da pessoa:** estação de casa, minhas linhas, o código aleatório dos relatos e, com conta, o token da sessão.
- **No servidor:** relatos (sem texto livre, só o hash do código do aparelho) e, para quem cria conta, usuário, hash da senha, linhas, casa e rotas.
- **Nunca guardado:** o que a pessoa escreve para a Lia, localização, foto ou documento.

## 6. Fontes de dados

| Dado | Fonte | Atualização |
|---|---|---|
| Rede de trem e metrô (estações, linhas, tempos) | GTFS da SPTrans | Base montada no projeto |
| Situação das linhas | Agregador público que lê os avisos das seis operadoras (não oficial) | A cada 2 minutos, com cache de 90 segundos |
| Chuva | Avisos ativos do INMET para a cidade de São Paulo | Na hora da consulta, com cache |
| Alagamentos | CGE da Prefeitura (estado de atenção ou alerta e pontos do dia) e áreas de risco do GeoSampa | Na hora da consulta, com cache |
| Segurança perto das estações | Dados criminais da SSP-SP de 2026 (janeiro a setembro, raio de 300 m de 139 estações da capital) | Base montada no projeto |
| Energia e CO₂ | MCTI, Relatório Integrado do Metrô, INMETRO (PBEV), Inventário Nacional de Emissões e ANP | Base montada no projeto |

Quando uma fonte cai, o app mostra a última leitura com a hora dela e diz que está sem atualização.

## 7. Inteligência artificial

- Toda mensagem para a Lia passa pelo modelo de IA configurado no servidor (hoje Groq, modelo `openai/gpt-oss-120b`), com acesso às ferramentas do sistema.
- O que vai para o modelo: a mensagem depois da barreira de dado pessoal, as últimas falas da conversa e o que as ferramentas devolveram. Nada é guardado depois da resposta.
- Há um limite de chamadas por dia, que vale também para o agente das fichas; quando ele acaba, a Lia segue pelas regras e pela base. No servidor público, cada aparelho faz no máximo 20 perguntas com IA a cada 5 minutos.
- O agente das fichas (PAI) é feito em LangGraph: guardrails, busca nas fichas e resposta citada. Dado pessoal e tentativa de manipulação são barrados antes de qualquer chamada ao modelo.

## 8. Teste da sociedade

Personas fictícias (com idade, região, perfil e acesso à internet) vivem uma situação do dia (linha parada no pico, temporal, volta à noite, dia normal). A conversa de cada uma vem do sistema de verdade, e uma população sintética maior, sorteada a partir das personas, estima quantos usariam, as barreiras e as sugestões. Tudo é fictício e serve para discutir o produto, não para medir mercado.

## 9. As páginas das matérias

- **Entenda:** o que a matéria faz no sistema, a entrega do professor (formato, pasta e como rodar) e os links dos arquivos no GitHub.
- **Teste:** o núcleo da matéria rodando, do jeito que o enunciado avalia.
- **Checklist:** o que o enunciado pede, agrupado pelos critérios de avaliação, com o status de cada item: **Feito** (existe e foi conferido), **Conferir** (existe, mas depende de conferência da equipe) e **A fazer**. Cada item diz se é do sistema (código ou documento no repositório) ou da equipe (vídeo, testes com pessoas, envio no portal).

PCP, DSA, SERS, MLAM e PAI estão dentro do sistema. CS, MMC e COA são entregues à parte, no formato de cada enunciado, e têm página com explicação e checklist.

## 10. Limitações conhecidas

- A linha 7-Rubi não aparece no agregador de situação das linhas, por isso fica sem status ao vivo.
- O GTFS da SPTrans distribui o tempo dos trens da CPTM por igual entre as estações, o que alonga essas viagens; as linhas do Metrô estão coerentes.
- A situação das linhas vem de um agregador não oficial; o aviso da estação e o da operadora valem mais.
- Os relatos são estimativa de passageiros. A lotação do vagão não existe como dado público.
- A base da SSP-SP conta registros perto da estação, sem o fluxo de passageiros: estação cheia tem mais registro, e isso não é taxa de risco.
- Não há recuperação de senha da conta.
- O limite diário de IA é compartilhado por todos que usam o servidor.

## 11. Operação (para a equipe)

- **Rodar no computador:** `pnpm --dir sistema/web install`, `pnpm --dir sistema/web build` e `uv run uvicorn sistema.api:app --port 8010` (abre em http://localhost:8010).
- **Testes automáticos:** `uv run python -m unittest discover -s tests/sistema` (e `tests/pcp`, `tests/dsa`, `tests/pai`).
- **Servidor público:** passo a passo em `DEPLOY.md` (Docker). Com `MODO_PUBLICO=1`, a configuração de IA e o checklist ficam só para leitura.
- **Variáveis de ambiente:**

| Variável | Para que serve |
|---|---|
| `IA_PROVEDOR`, `IA_MODELO`, `IA_CHAVE`, `IA_BASE_URL`, `IA_LIMITE_DIARIO` | Modelo de IA da Lia e limite de chamadas por dia |
| `SUPABASE_URL`, `SUPABASE_SECRET_KEY` | Banco dos relatos e das contas (esquema `datempo`); sem elas, os relatos ficam em memória |
| `MODO_PUBLICO` | `1` no servidor aberto aos professores |
| `PASTA_DADOS_LOCAIS` | Onde gravar o contador de uso da IA e o histórico das linhas |
| `DEMO_RELATOS` | `1` sobe o feed com a cena de demonstração (relatos marcados como tal) |

- **Documentação da API:** `/api/docs` no próprio servidor.
