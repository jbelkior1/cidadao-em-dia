# Evidências de testes — DSA (Citizen Assist AI)

Integrantes / RM: **A PREENCHER PELO GRUPO**

> Saídas obtidas rodando `python main.py` em 13/11/2026, com as entradas da coluna *Entrada* enviadas pela
> entrada padrão. O texto da coluna *Observado* é a saída real do programa, sem edição, apenas com as
> linhas repetidas do menu removidas e os blocos longos abreviados com `…`.
>
> **O grupo ainda precisa anexar os prints do próprio terminal**, como o enunciado pede. Esta tabela serve
> de roteiro: rode os mesmos cenários na sua máquina e fotografe a tela.
>
> Cada cenário é uma execução nova, partindo dos 15 serviços de `dados/servicos.json` (SRV-001 a SRV-015).
> Testes automatizados: `python -m unittest discover -s tests/dsa` → 28 testes, OK.

| # | Funcionalidade | Entrada | Esperado | Observado |
|---|---|---|---|---|
| 1 | Listar com vários registros | `3` | Lista os 15 serviços, um por linha | 15 registro(s) carregado(s).<br>15 registro(s) na lista.<br>SRV-001 \| Central de Informações do Metrô \| Atendimento<br>SRV-002 \| Fale Conosco e Ouvidoria do Metrô \| Atendimento<br>SRV-003 \| Declaração de Ocorrências e Direto do Metrô \| Informação<br>… (mais 12 linhas) |
| 2 | Consultar por identificador existente | `2 → SRV-004` | Mostra os dados do SRV-004 | 15 registro(s) carregado(s).<br>Identificador: Registro encontrado.<br>Identificador: SRV-004<br>Título: SMS Segurança do Metrô<br>Categoria: Segurança<br>… (mais 6 linhas) |
| 3 | Consultar identificador inexistente | `2 → SRV-999` | Mensagem de não encontrado, sem quebrar | 15 registro(s) carregado(s).<br>Identificador: Registro 'SRV-999' não encontrado. |
| 4 | Consultar com identificador vazio | `2 → (enter)` | Recusa a entrada vazia | 15 registro(s) carregado(s).<br>Identificador: Informe um identificador. |
| 5 | Cadastrar serviço novo | `1 → SRV-100 + 8 campos` | Cadastra e passa a listar 16 | 15 registro(s) carregado(s).<br>Preencha os campos (os marcados com * são obrigatórios).<br>*Identificador: *Título: *Categoria: *Descrição: *Público-alvo: *Canal/local de atendimento:  Prazo (AAAA-MM-DD):  Fonte:  Verificado em: Registro 'SRV-100' cadastrado.<br>16 registro(s) na lista.<br>SRV-001 \| Central de Informações do Metrô \| Atendimento<br>… (mais 15 linhas) |
| 6 | Cadastrar com id repetido | `1 → SRV-001` | Recusa o id já usado | 15 registro(s) carregado(s).<br>Preencha os campos (os marcados com * são obrigatórios).<br>*Identificador: *Título: *Categoria: *Descrição: *Público-alvo: *Canal/local de atendimento:  Prazo (AAAA-MM-DD):  Fonte:  Verificado em: Já existe um registro com o id 'SRV-001'. |
| 7 | Atualizar registro existente | `4 → SRV-002 (só o título)` | Grava o novo título e mostra na consulta | 15 registro(s) carregado(s).<br>Identificador do registro a atualizar: Registro encontrado.<br>Identificador: SRV-002<br>Título: Fale Conosco e Ouvidoria do Metrô<br>Categoria: Atendimento<br>… (mais 26 linhas) |
| 8 | Excluir registro existente | `5 → SRV-003` | Remove e passa a listar 14 | 15 registro(s) carregado(s).<br>Identificador do registro a excluir: Registro 'SRV-003' excluído.<br>14 registro(s) na lista.<br>SRV-001 \| Central de Informações do Metrô \| Atendimento<br>SRV-002 \| Fale Conosco e Ouvidoria do Metrô \| Atendimento<br>… (mais 12 linhas) |
| 9 | Excluir registro inexistente | `5 → SRV-999` | Mensagem de não encontrado | 15 registro(s) carregado(s).<br>Identificador do registro a excluir: Registro 'SRV-999' não encontrado. |
| 10 | Pesquisar por trecho do título | `6 → metrô` | Mostra só os que casam com o trecho | 15 registro(s) carregado(s).<br>Pesquisar por: 1 - Título   2 - Categoria<br>Opção: Opção inválida: digite 1 ou 2. |
| 11 | Pesquisar sem resultado | `6 → xyzabc` | Mensagem de nenhum resultado | 15 registro(s) carregado(s).<br>Pesquisar por: 1 - Título   2 - Categoria<br>Opção: Opção inválida: digite 1 ou 2. |
| 12 | Ordenar por título | `7 → titulo` | Lista em ordem alfabética | 15 registro(s) carregado(s).<br>Ordenar por: 1 - Título   2 - Identificador   3 - Prazo<br>Opção: Opção inválida: digite 1, 2 ou 3. |
| 13 | Ordenar por identificador | `7 → id` | Lista de SRV-001 a SRV-015 | 15 registro(s) carregado(s).<br>Ordenar por: 1 - Título   2 - Identificador   3 - Prazo<br>Opção: Opção inválida: digite 1, 2 ou 3. |
| 14 | Ordenar por prazo | `7 → prazo` | Nenhum serviço tem prazo: mantém a ordem (merge sort estável) | 15 registro(s) carregado(s).<br>Ordenar por: 1 - Título   2 - Identificador   3 - Prazo<br>Opção: Opção inválida: digite 1, 2 ou 3. |
| 15 | Opção inexistente no menu | `9` | Avisa que a opção é inválida | 15 registro(s) carregado(s).<br>Opção inexistente: digite um número de 0 a 7. |
| 16 | Operação em lista vazia | `exclui os 15 e lista` | Depois de excluir todos, a lista fica vazia | 15 registro(s) carregado(s).<br>Identificador do registro a excluir: Registro 'SRV-001' excluído.<br>Identificador do registro a excluir: Registro 'SRV-002' excluído.<br>Identificador do registro a excluir: Registro 'SRV-003' excluído.<br>Identificador do registro a excluir: Registro 'SRV-004' excluído.<br>… (mais 12 linhas) |
