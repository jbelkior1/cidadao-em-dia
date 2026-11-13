# Citizen Assist AI

Assistente de terminal, em Python, que responde dúvidas do cidadão **somente com o que está na base de conhecimento** (`data/base_conhecimento.json`), sempre mostrando a fonte, a data de verificação e o aviso de que o assistente não é canal oficial. Não coleta dados pessoais.

Trabalho da Global Solution 2026.2 (FIAP), tema CitizenTech, matéria Pensamento Computacional e Automação com Python.

> **ATENÇÃO: a base de conhecimento ainda está em conferência.** As 16 orientações vieram de uma pesquisa em páginas oficiais feita em 12/11/2026 (pasta `pesquisa/` do projeto Cidadão em Dia). Antes de entregar, a equipe precisa abrir cada fonte, confirmar o texto e atualizar a data em `verificado_em`. Cada registro conferido perde o campo `conferido_pela_equipe: false`.

## Integrantes

A PREENCHER PELO GRUPO: nome e RM de cada integrante.

| Nome | RM |
|------|----|
| A PREENCHER PELO GRUPO | A PREENCHER PELO GRUPO |

## Público e problema escolhidos

A PREENCHER PELO GRUPO: público atendido e o problema que a base resolve.

Contexto do enunciado: muita gente perde tempo para descobrir onde tirar um documento, o que levar para fazer o Cartão SUS ou a quem recorrer quando algo dá errado, porque a informação está espalhada, em linguagem técnica e misturada com páginas que parecem oficiais e não são.

## ODS relacionados

A PREENCHER PELO GRUPO (confirmar). Sugestões: ODS 10 (Redução das desigualdades), ODS 16 (Paz, justiça e instituições eficazes) e, conforme o tema da base, ODS 3 (Saúde e bem-estar).

## Como executar

Só biblioteca padrão do Python 3 (nenhuma instalação). Dentro desta pasta:

```
python main.py
```

Menu principal:

1. Fazer uma pergunta (texto livre, busca por pontuação)
2. Navegar por categorias
3. Ver indicadores
4. Exportar atendimentos para CSV (`data/atendimentos.csv`)
0. Sair (pede a nota de facilidade de 1 a 5)

Em todas as telas, **0 volta**. Opção inválida, resposta vazia ou s/n inválido nunca encerram o programa.

Testes automáticos (da raiz do repositório que contém esta pasta e a pasta `tests`):

```
python -m unittest discover -s tests/pcp -v
```

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py               # carrega a base e abre o menu
├── orientacao.py         # classe Orientacao
├── base_conhecimento.py  # classe BaseConhecimento e normalizar()
├── assistente.py         # classe Assistente
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    ├── atendimentos.csv          # gerado pela opção 4 do menu
    └── notas_facilidade.json     # criado ao sair; guarda as notas de 1 a 5
```

Classes, em composição: `Assistente` tem uma `base` (`BaseConhecimento`), que tem uma lista `orientacoes` de objetos `Orientacao`.

| Classe | Atributos | Métodos |
|--------|-----------|---------|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()`, `texto()`, `para_dict()`, `de_dict()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()`, `detalhar_pontuacao()`, `nivel_confianca()` |
| `Assistente` | nome, base, historico | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `responder()`, `tem_dado_pessoal()`, `menu()` |

Os métodos que decidem as coisas (`responder`, `tem_dado_pessoal`, `detalhar_pontuacao`, `registrar`, `indicadores`, `exportar_csv`) não usam `input` nem `print`; só devolvem dados. Os métodos de tela (`perguntar`, `navegar`, `menu`) fazem a conversa e chamam os primeiros. Por isso outro sistema pode importar as mesmas classes.

## Regra de pontuação

Pergunta, palavras-chave e título são normalizados antes de comparar: minúsculas, sem acentos e sem pontuação (a função `normalizar()` usa a tabela de acentos do enunciado e também troca hífen, barra e aspas por espaço). A comparação é por palavra inteira (`rg` não casa dentro de `energia`).

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 (cada) |
| Palavra da pergunta com 4 letras ou mais que aparece no título | +1 (cada palavra, contada uma vez) |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança ALTA |
| 3 a 5 pontos | Confiança MÉDIA |
| menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação (só entram orientações com pelo menos 1 ponto; em empate vale a ordem do arquivo). O assistente mostra a melhor orientação e até **duas alternativas**, desde que cada alternativa tenha pelo menos 3 pontos (decisão do grupo: alternativa com 1 ou 2 pontos seria só ruído).

Exemplo do enunciado: em "Como faço o cartão do SUS?", a orientação 3 recebe +3 por `cartao do sus`, +3 por `sus` e +1 porque `cartao` está no título: 7 pontos, confiança ALTA. Esse cálculo está num teste automático.

Os pesos e limites estão como constantes no começo de `base_conhecimento.py`; nesta versão são exatamente os do enunciado.

## Regras de atendimento

- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com **8 ou mais dígitos no total** (mesmo separados por pontos, traços ou espaços) ou com `@` é recusada com a mensagem "Atenção: não digite CPF, telefone ou e-mail. Reescreva." e **não é registrada** no histórico, no CSV nem em nenhum outro lugar.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** JSON ausente ou corrompido não derruba o programa. Base com problema vira base vazia (com aviso); registros inválidos são ignorados; histórico ilegível recomeça vazio.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: `data`, `origem` ("pergunta" ou "categoria"), `pergunta`, `orientacao_id`, `encontrou`, `ajudou`, `tentativas` e `tempo_segundos` (medido com `time.time()` e arredondado com `round(..., 1)`).

Como o grupo definiu "atendimento": uma dúvida, do primeiro momento até a pessoa responder "s" (ajudou), desistir (0) ou voltar. Perguntar de novo depois de "n" ou de "não encontrei" soma uma tentativa no mesmo atendimento. Na navegação por categorias, cada orientação aberta é um atendimento de 1 tentativa.

Indicadores (opção 3 do menu):

- Resposta encontrada (%): atendimentos em que alguma orientação foi encontrada.
- Taxa de acerto (%): atendimentos em que a pessoa respondeu "s".
- Tempo médio para encontrar: média do tempo dos atendimentos em que ajudou.
- Tentativas por atendimento: média.
- Facilidade de uso (1 a 5): média das notas dadas ao sair (`data/notas_facilidade.json`).
- Lista de dúvidas sem solução: perguntas dos atendimentos em que não ajudou.

A exportação (opção 4) grava `data/atendimentos.csv` com `csv.DictWriter` (UTF-8 com BOM, para o Excel abrir os acentos).

## Integrações com outras disciplinas

Nenhuma nesta versão. A busca por pontuação é a do enunciado. (Preencher aqui se o grupo integrar com as outras disciplinas da GS; o sistema web do projeto reaproveita estas mesmas classes.)

## Fontes consultadas

A base atual usa só endereços de órgãos oficiais, lidos em 12/11/2026 e ainda **em conferência pelo grupo**:

- https://www.gov.br/aneel/
- https://www.gov.br/mds/
- https://www.gov.br/saude
- https://valoresareceber.bcb.gov.br/
- https://www.gov.br/pt-br/servicos/

A PREENCHER PELO GRUPO: lista final das fontes oficiais da base definitiva, com a data em que cada uma foi conferida.

## Resultado do teste com usuários

A PREENCHER PELO GRUPO. O enunciado pede pelo menos 3 pessoas de fora da equipe, somando 10 atendimentos ou mais. Registrar, sem nomes nem dados das pessoas:

- número de pessoas e de atendimentos;
- indicadores obtidos (resposta encontrada, taxa de acerto, tempo médio, tentativas, facilidade de uso);
- dúvidas sem solução;
- uma melhoria feita a partir do teste (por exemplo, uma palavra-chave nova).

## Limitações

- A base tem 16 orientações; o assistente só conhece o que está nela.
- A busca é por regras: não entende sinônimos nem erros de digitação que não estejam nas palavras-chave.
- O tempo medido inclui o tempo de digitação da pessoa.
- Cada atendimento guarda só a última pergunta digitada.
- As informações podem mudar nos sites oficiais depois da data de verificação; por isso o assistente sempre mostra a fonte e o aviso de que não é canal oficial.

## Vídeo técnico

Link (YouTube, não listado): A PREENCHER PELO GRUPO
