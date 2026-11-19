# Documentação funcional do Dá Tempo?

O Dá Tempo? é um app de trem e metrô de São Paulo que avisa, antes de a pessoa sair, se a viagem vai dar certo. Confere a situação das linhas, o aviso de chuva, os alagamentos e a segurança perto das estações e responde com uma decisão só: **Pode ir**, **Saia mais cedo** ou **Mude o caminho**. Foi feito na Global Solution 2026.2 da FIAP (CitizenTech, case Citizen Assist AI) por João Vitor Belchior Domingos Leite (RM 572478), João Pedro Pereira Teixeira (RM 569937) e Thiago de Oliveira Coelho Souza (RM 568783).

## 1. O que é

- **Para quem:** quem usa trem e metrô em São Paulo, sem cadastro.
- **O que resolve:** a informação que decide a viagem está espalhada (site de cada operadora, INMET, CGE da Prefeitura, SSP-SP). O app junta tudo numa resposta, com a fonte e a hora de cada leitura.
- **O que não é:** canal oficial das operadoras ou da Defesa Civil, canal de emergência, nem confirmação de direito.

## 2. A plataforma

| Endereço | O que abre |
|---|---|
| `/` **Como funciona** | O vídeo do pitch (abre no YouTube), o problema, o uso aba por aba, o fluxograma e onde cada matéria entra. |
| `/sistema` **Sistema** | O app dentro do desenho de um celular (no celular de verdade, em tela cheia). |
| `/app` **Só o app** | O app em tela cheia, sem a barra da plataforma. É o endereço para abrir direto pelo celular. |
| `/avaliacao` **Avaliação usuários** | O que as pessoas acharam do app, separado por grupo (Família, Faculdade, Trabalho, Conhecido). Ninguém se identifica. Quando há testes completos, mostra também os números deles. |
| `/avaliar` **Avaliar o Dá Tempo?** | O formulário simples: como a pessoa conhece o projeto (opcional) e o campo "O que você achou do sistema?", de até 500 caracteres. |
| `/avaliar/teste` **Teste completo** | Três tarefas cronometradas no app, com acerto, perguntas sobre o cartão de energia da viagem e notas de facilidade de 1 a 5 (cerca de 10 minutos). |
| `/materias/pcp`, `/dsa`, `/sers`, `/mlam`, `/pai`, `/cs`, `/mmc`, `/coa` **Matérias** | Cada página tem **Entenda** (entrega, arquivos no GitHub, o que faz no sistema e o fluxograma), **Teste** e **Checklist da entrega**, com o botão para baixar o pacote (.zip) da matéria. |
| `/documentacao` **Documentação funcional** | Esta página. |
| `/configuracoes` **Configurações de IA** | Só no computador: escolhe o provedor e o modelo da Lia. No servidor público não aparece. |

As avaliações seguem a mesma barreira do resto do app: texto com dado pessoal ou link é recusado. O mesmo aparelho pode enviar várias avaliações seguidas, para que um teste passe de mão em mão; no servidor público, o limite é de 20 envios a cada 5 minutos por endereço.

O **Modo banca**, no rodapé da barra lateral, mostra ao lado do app qual matéria fez cada parte da última resposta.

## 3. O app, aba por aba

Quatro abas embaixo (Home, Mapa, IA, Perfil). Em todas, no topo, ficam o SOS e o sinal de alerta.

**Home.** Mostra o que os passageiros relatam agora.
- *Agora nas linhas* resume cada linha; *Relatos recentes* lista os relatos (filtro Todas ou Minhas linhas).
- *Relatar* leva dois toques: a linha e o que a pessoa vê (Lotado, Parado, Quebrou, Chuva, Alagamento, Segurança ou Tudo certo). Há um campo opcional de descrição, de até 140 caracteres, que barra CPF, telefone, e-mail, endereço, nome e link; só aparece no feed. Também dá para anexar uma foto como evidência: ela é recomprimida no servidor (a localização do arquivo é descartada), fica num bucket privado, só aparece enquanto o relato está ativo e é apagada quando ele vence ou recebe 3 sinalizações (uma faxina automática roda a cada poucos minutos). Cada envio tem limite de tamanho (5 MB) e de relatos por endereço. A Lia não lê nem o texto nem a foto.
- Regras: um relato por pessoa e por linha a cada 10 minutos; cada relato vale 2 horas; outras pessoas confirmam ou encerram; três denúncias tiram o relato; o alerta de uma linha só aparece com dois autores diferentes. É estimativa, não dado oficial.

**Mapa.** Linhas coloridas pela situação de agora, com camadas para ligar e desligar: Alagamentos (GeoSampa e CGE), Segurança (SSP-SP perto das estações) e Relatos. Há um resumo em texto abaixo do mapa, para leitor de tela.

**IA, a Lia.** A pessoa escreve do jeito dela ("vou da Sé para a Paulista").
- *Conferir a viagem:* devolve a decisão do dia, a chegada prevista, a situação de cada linha, o desvio quando uma linha falha, a segurança na saída e na chegada e a energia da viagem.
- *Dúvida de regra* (declaração de atraso, gratuidade, reclamação, achados e perdidos, tarifa, assédio, acessibilidade): chama o agente das fichas da PAI, que cita a ficha.
- *Orientação oficial e canal de atendimento:* busca por pontos da PCP e catálogo da DSA.
- *Mensagem de atraso:* a Lia monta o texto; quem envia é a pessoa.
- Só afirma o que as ferramentas trouxeram. Se a IA falhar ou o limite do dia acabar, responde pelas regras e pela base e avisa.

**Perfil.** Sem conta, as linhas e a estação de casa ficam só no aparelho. Com conta (usuário e senha, sem e-mail nem telefone), elas e até 10 rotas salvas voltam em qualquer aparelho; *Conferir agora* abre a Lia já perguntando o trajeto. A senha é guardada com hash, a conta trava 15 minutos depois de 5 erros e não há recuperação de senha. Dá para apagar os dados do aparelho e a conta inteira.

**SOS.** Atalhos para 190, 192 e 193 e o canal da linha já preenchido (SMS Segurança do Metrô; central da CPTM, ViaQuatro ou ViaMobilidade; Ouvidoria da Artesp quando a linha não tem canal próprio). O app não envia nada: a pessoa confere e envia.

**Sinal de alerta.** Conta os alertas ativos (linhas com problema, chuva do INMET, atenção ou alerta de alagamento do CGE) e leva a pergunta para a Lia.

## 4. A decisão do dia

| Situação | Decisão |
|---|---|
| Falha numa linha do trajeto | **Mude o caminho**, com o desvio até a próxima troca |
| Aviso de chuva do INMET e, junto com ele, alagamento perto do trajeto ou horário de pico | **Saia mais cedo** |
| Nenhum dos casos (inclusive pico sem chuva, ou chuva sem alagamento fora do pico) | **Pode ir** |

Horário de pico: dias úteis, das 6h às 9h e das 16h às 19h30. A modelagem lógica de Computer Science (tabela-verdade, Karnaugh e circuito) é feita pela equipe, à parte, e pode substituir esta regra com as mesmas entradas e saídas.

## 5. Privacidade

- Antes de qualquer registro e de qualquer chamada à IA, o sistema barra números longos (CPF, telefone), e-mail e frases que anunciam um dado ("meu nome é", "moro na rua", "minha senha é").
- **No aparelho:** estação de casa, minhas linhas, um código aleatório dos relatos e, com conta, o token da sessão.
- **No servidor:** os relatos e as avaliações (só o hash do código do aparelho) e, com conta, usuário, hash da senha, linhas, casa e rotas. A avaliação guarda o grupo, se a pessoa escolheu, o comentário e, no teste completo, os tempos, os acertos, as respostas sobre energia e as notas.
- **Nunca guardado:** o que a pessoa escreve para a Lia, localização ou documento. A foto do relato é a única imagem que o servidor guarda: sai recomprimida e sem metadados, num bucket privado, e é apagada quando o relato vence ou recebe 3 sinalizações.

## 6. Dados e IA

| Dado | Fonte |
|---|---|
| Rede (estações, linhas, tempos) | GTFS da SPTrans |
| Situação das linhas | Agregador público dos avisos das seis operadoras (não oficial), lido a cada 2 minutos |
| Chuva | Avisos ativos do INMET para São Paulo |
| Alagamentos | CGE da Prefeitura e áreas de risco do GeoSampa |
| Segurança | SSP-SP, janeiro a setembro de 2026, raio de 300 m de 139 estações |
| Energia e CO₂ | MCTI, Relatório Integrado do Metrô, INMETRO, Inventário Nacional de Emissões e ANP |

Quando uma fonte cai, o app mostra a última leitura com a hora dela e diz que está sem atualização.

- A Lia usa o modelo configurado no servidor (hoje Groq, `openai/gpt-oss-120b`) com as ferramentas do sistema. Para o modelo vai só a mensagem já filtrada, as últimas falas e o que as ferramentas devolveram; nada é guardado depois.
- Há um limite diário de chamadas, compartilhado com o agente da PAI, e, no servidor público, 20 perguntas com IA a cada 5 minutos por aparelho. Passado o limite, a Lia segue pelas regras.

## 7. Limitações

- A linha 7-Rubi não aparece no agregador, então fica sem status ao vivo.
- O GTFS distribui por igual o tempo entre as estações da CPTM, o que alonga essas viagens.
- A situação das linhas vem de um agregador não oficial; o aviso da estação e o da operadora valem mais.
- A lotação do vagão não existe como dado público; os relatos são estimativa.
- A base da SSP-SP conta registros perto da estação, sem o fluxo de passageiros: não é taxa de risco.
