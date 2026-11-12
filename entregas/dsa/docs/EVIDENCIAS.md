# Evidências de testes — DSA (Citizen Assist AI)

> **Dados trocados em 12/11/2026.** Os cenários abaixo foram rodados com os 6 registros de exemplo da primeira versão. O arquivo `dados/servicos.json` agora tem 13 serviços reais (SRV-001 a SRV-013). O grupo precisa rodar todos os cenários de novo, com os dados atuais, e colar aqui as próprias saídas e prints.


> **Atenção, grupo:** as saídas "observadas" abaixo foram obtidas executando `python main.py` com entradas simuladas (redirecionadas por `printf`), no ambiente de desenvolvimento do código. **O grupo precisa refazer os testes na própria máquina e tirar os próprios prints do terminal** para anexar na entrega. As saídas foram abreviadas: as linhas repetidas do menu e a linha "6 registro(s) carregado(s)." do início foram omitidas, e alguns blocos longos foram resumidos com "…".
>
> Todos os cenários partem dos 6 registros iniciais (`SRV-001` a `SRV-006`, em `dados/servicos.json`), salvo quando indicado. Cada cenário é uma execução nova do programa.
>
> Testes automatizados (28 testes) também passaram: `python -m unittest discover -s tests/dsa -v` → `Ran 28 tests ... OK`.

Integrantes / RM: A PREENCHER PELO GRUPO

| # | Funcionalidade | Entrada (opções digitadas) | Resultado esperado | Resultado observado |
|---|---|---|---|---|
| 1 | Listar (vários registros) | `3` | Mostra os 6 registros, um por linha | `6 registro(s) na lista.` seguido de `SRV-001 \| Tarifa social de energia elétrica \| Energia` … até `SRV-006 \| Atendimento básico de saúde \| Saúde` |
| 2 | Cadastro válido | `1`, id `SRV-007`, título `Bolsa teste`, categoria `Assistência social`, descrição, público `Famílias`, canal `CRAS`, prazo `2026-11-30`, demais vazios; depois `3` | Registro cadastrado e aparece no fim da lista | `Registro 'SRV-007' cadastrado.` / `7 registro(s) na lista.` e a última linha é `SRV-007 \| Bolsa teste \| Assistência social` |
| 3 | Cadastro com id duplicado | `1`, id `srv-001` (campos restantes preenchidos) | Recusa, informa duplicidade | `Já existe um registro com o id 'srv-001'.` |
| 4 | Cadastro com campo obrigatório vazio | `1`, id `SRV-008`, título vazio | Recusa, informa o campo | `O campo 'Título' é obrigatório e não pode ficar vazio.` |
| 5 | Cadastro com valor incompatível (prazo) | `1`, … prazo `31/12/2026` | Recusa, explica o formato | `Prazo inválido: use uma data real no formato AAAA-MM-DD (ex.: 2026-12-31).` |
| 6 | Consulta por id existente | `2`, `srv-003` | Mostra todos os campos do registro | `Registro encontrado.` e os 9 campos de SRV-003 (`Título: Valores a receber em bancos`, `Categoria: Dinheiro esquecido`, …) |
| 7 | Consulta por id inexistente | `2`, `XYZ` | Mensagem de não encontrado | `Registro 'XYZ' não encontrado.` |
| 8 | Consulta com id vazio | `2`, Enter | Pede um identificador | `Informe um identificador.` |
| 9 | Atualização válida | `4`, `SRV-002`, campo `3` (Descrição), `Novo texto de descrição`; depois `2`, `SRV-002` | Descrição alterada | `Registro 'SRV-002' atualizado.`; na consulta seguinte `Descrição: Novo texto de descrição` |
| 10 | Atualização de prazo válido | `4`, `SRV-002`, campo `6`, `2026-10-15`; depois `2`, `SRV-002` | Prazo gravado | `Registro 'SRV-002' atualizado.`; consulta mostra `Prazo (AAAA-MM-DD): 2026-10-15` |
| 11 | Atualização com campo obrigatório vazio | `4`, `SRV-002`, campo `1`, valor só com espaços | Recusa | `O campo 'Título' é obrigatório e não pode ficar vazio.` |
| 12 | Atualização com prazo inválido | `4`, `SRV-002`, campo `6`, `31/12/2026` | Recusa | `Prazo inválido: use uma data real no formato AAAA-MM-DD (ex.: 2026-12-31).` |
| 13 | Atualização com número de campo inválido | `4`, `SRV-002`, `9` e também `abc` | Mensagem de opção inválida, sem erro | `Opção inválida: digite um número da lista.` (nas duas entradas) |
| 14 | Atualização de id inexistente / vazio | `4`, `XYZ`; `4`, Enter | Mensagens claras | `Registro 'XYZ' não encontrado.` / `Informe um identificador.` |
| 15 | Exclusão da cabeça, do meio e do fim | `5` `SRV-001`; `5` `SRV-003`; `5` `SRV-006`; depois `3` | Os 3 removidos; sobram SRV-002, 004, 005 | `Registro 'SRV-001' excluído.` / `'SRV-003' excluído.` / `'SRV-006' excluído.`; lista: `SRV-002`, `SRV-004`, `SRV-005` (`3 registro(s) na lista.`) |
| 16 | Exclusão de id já removido | `5`, `SRV-006` (após o item 15) | Não encontrado | `Registro 'SRV-006' não encontrado.` |
| 17 | Pesquisa por título | `6`, `1`, `via` | Retorna "Segunda via do RG" | `1 registro(s) encontrado(s).` `SRV-004 \| Segunda via do RG \| Documentos` |
| 18 | Pesquisa por categoria (sem acento no trecho) | `6`, `2`, `edu` | Retorna a categoria Educação | `1 registro(s) encontrado(s).` `SRV-005 \| Matrícula na rede pública de ensino \| Educação` |
| 19 | Pesquisa sem resultado | `6`, `2`, `xyz` | Mensagem de nenhum resultado | `Nenhum registro com 'xyz' em categoria.` |
| 20 | Pesquisa com texto vazio / opção inválida | `6`, `1`, Enter; `6`, `3` | Mensagens claras | `Digite um texto para pesquisar.` / `Opção inválida: digite 1 ou 2.` |
| 21 | Ordenar por título | `7`, `1` | Ordem alfabética de título | `Lista ordenada por título (crescente).` Ordem observada (8 registros, após cadastrar SRV-007 e SRV-008): `SRV-006` Atendimento…, `SRV-002` Atualizar…, `SRV-007` Bolsa teste, `SRV-005` Matrícula…, `SRV-008` Outro, `SRV-004` Segunda via…, … |
| 22 | Ordenar por id | `7`, `2` | SRV-001 … SRV-006 | `Lista ordenada por id (crescente).` `SRV-001`, `SRV-002`, `SRV-003`, `SRV-004`, `SRV-005`, `SRV-006` |
| 23 | Ordenar por prazo | cadastrar `SRV-007` (prazo `2026-11-30`) e `SRV-008` (prazo `2027-02-01`); `7`, `3` | Primeiro quem tem prazo mais cedo; sem prazo no fim | `Lista ordenada por prazo (crescente).` `SRV-007` (2026-11-30), `SRV-001` (2026-12-31), `SRV-008` (2027-02-01), depois `SRV-002` … `SRV-006` (sem prazo) |
| 24 | Ordenar com opção inválida | `7`, `4` e `7`, `abc` | Mensagem de opção inválida | `Opção inválida: digite 1, 2 ou 3.` (nas duas) |
| 25 | Opção de menu inexistente | `9`, `abc`, Enter, `-1` | Mensagem e volta ao menu | `Opção inexistente: digite um número de 0 a 7.` (4 vezes), depois `0` → `Até logo!` |
| 26 | **Lista vazia**: excluir tudo e operar | `5` para cada id de `SRV-001` a `SRV-006`; depois `3`; `2` `SRV-001`; `5` `SRV-001`; `7` `1`; `6` `1` `saude`; `4` `SRV-001` | Cada operação avisa que a lista está vazia, sem erro | Os 6 `excluído`; depois, em ordem: `A lista está vazia: nenhum registro cadastrado.` (listar), idem (consultar), `A lista está vazia: nenhum registro para excluir.`, `A lista está vazia: nada para ordenar.`, `A lista está vazia: nada para pesquisar.`, `A lista está vazia: nenhum registro cadastrado.` (atualizar) |
| 27 | Sair | `0` | Encerra o programa | `Até logo!` |
| 28 | Entrada encerrada sem escolher sair (fim do arquivo/Ctrl+Z/Ctrl+D) | `3` e fim da entrada | Encerra sem traceback | Lista mostrada e depois `Entrada encerrada. Até logo!` |

## Como refazer

1. `cd entregas/dsa` e `python main.py`.
2. Digite as entradas de cada linha da tabela e tire print do terminal.
3. Confira se o observado do grupo bate com o esperado; se não bater, avise antes de entregar.
4. Rode `python -m unittest discover -s tests/dsa -v` na raiz do repositório e tire print do resumo final.
