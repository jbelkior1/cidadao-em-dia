# Evidências de testes: DSA (Citizen Assist AI)

Integrantes / RM: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)

Saídas obtidas em 13/11/2026 rodando `python main.py` com os 15 serviços de `dados/servicos.json`
(SRV-001 a SRV-015). Cada cenário é uma execução nova do programa. O bloco **Observado** é a
transcrição real do terminal, com o valor digitado aparecendo logo depois de cada pergunta; só o
menu, que se repete a cada volta, foi trocado por `[menu]`.

> **Falta à equipe:** repetir estes cenários na própria máquina e anexar os prints do terminal,
> como o enunciado pede. Esta transcrição serve de roteiro e de conferência.

Testes automatizados: `python -m unittest discover -s tests/dsa` → 28 testes, OK.

## Resumo

| # | Cenário | Funcionalidade |
|---|---|---|
| 1 | Listar com vários registros | listar |
| 2 | Consultar por identificador existente | consultar |
| 3 | Consultar identificador inexistente | consultar |
| 4 | Consultar com identificador vazio | consultar |
| 5 | Cadastrar serviço novo e listar | cadastrar |
| 6 | Cadastrar com identificador repetido | cadastrar |
| 7 | Cadastrar sem campo obrigatório | cadastrar |
| 8 | Atualizar o título e consultar | atualizar |
| 9 | Excluir registro existente e listar | excluir |
| 10 | Excluir registro inexistente | excluir |
| 11 | Pesquisar por trecho do título | pesquisar |
| 12 | Pesquisar por categoria | pesquisar |
| 13 | Pesquisar sem resultado | pesquisar |
| 14 | Ordenar por título | ordenar |
| 15 | Ordenar por identificador | ordenar |
| 16 | Ordenar por prazo | ordenar |
| 17 | Opção inexistente no menu | opção |
| 18 | Operação em lista vazia | operação |

## 1. Listar com vários registros

**Entrada:** `3`, `0`

**Esperado:** Mostra os 15 serviços de dados/servicos.json, um por linha.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 3
15 registro(s) na lista.
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-015 | Atende+ da SPTrans | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 2. Consultar por identificador existente

**Entrada:** `2`, `SRV-004`, `0`

**Esperado:** Mostra todos os campos do SRV-004.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 2
Identificador: SRV-004
Registro encontrado.
  Identificador: SRV-004
  Título: SMS Segurança do Metrô
  Categoria: Segurança
  Descrição: Serviço para comunicar ocorrência de segurança por mensagem de texto; o Metrô também indica o aplicativo Metrô Conecta e os empregados das estações.
  Público-alvo: Passageiros do Metrô
  Canal/local de atendimento: SMS para (11) 97333-2252 (todos os dias, das 4h40 às 0h, segundo a Carta de Serviços de 2023); aplicativo Metrô Conecta
  Prazo (AAAA-MM-DD): -
  Fonte: https://www.metro.sp.gov.br/pt_BR/fale-conosco/
  Verificado em: 2026-11-12

[menu]
Escolha uma opção: 0
Até logo!
```

## 3. Consultar identificador inexistente

**Entrada:** `2`, `SRV-999`, `0`

**Esperado:** Avisa que o registro não foi encontrado, sem quebrar.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 2
Identificador: SRV-999
Registro 'SRV-999' não encontrado.

[menu]
Escolha uma opção: 0
Até logo!
```

## 4. Consultar com identificador vazio

**Entrada:** `2`, `(Enter)`, `0`

**Esperado:** Recusa a entrada vazia e pede um identificador.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 2
Identificador:
Informe um identificador.

[menu]
Escolha uma opção: 0
Até logo!
```

## 5. Cadastrar serviço novo e listar

**Entrada:** `1`, `SRV-100`, `Serviço de teste`, `Teste`, `Registro criado para a evidência`, `Equipe`, `Balcão de teste`, `(Enter)`, `(Enter)`, `(Enter)`, `3`, `0`

**Esperado:** Cadastra o SRV-100 e a listagem passa a ter 16 registros, com o novo no fim.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 1
Preencha os campos (os marcados com * são obrigatórios).
*Identificador: SRV-100
*Título: Serviço de teste
*Categoria: Teste
*Descrição: Registro criado para a evidência
*Público-alvo: Equipe
*Canal/local de atendimento: Balcão de teste
 Prazo (AAAA-MM-DD):
 Fonte:
 Verificado em:
Registro 'SRV-100' cadastrado.

[menu]
Escolha uma opção: 3
16 registro(s) na lista.
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-015 | Atende+ da SPTrans | Acessibilidade
SRV-100 | Serviço de teste | Teste

[menu]
Escolha uma opção: 0
Até logo!
```

## 6. Cadastrar com identificador repetido

**Entrada:** `1`, `SRV-001`, `Outro título`, `Teste`, `Descrição`, `Equipe`, `Balcão`, `(Enter)`, `(Enter)`, `(Enter)`, `0`

**Esperado:** Recusa o cadastro porque o SRV-001 já existe.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 1
Preencha os campos (os marcados com * são obrigatórios).
*Identificador: SRV-001
*Título: Outro título
*Categoria: Teste
*Descrição: Descrição
*Público-alvo: Equipe
*Canal/local de atendimento: Balcão
 Prazo (AAAA-MM-DD):
 Fonte:
 Verificado em:
Já existe um registro com o id 'SRV-001'.

[menu]
Escolha uma opção: 0
Até logo!
```

## 7. Cadastrar sem campo obrigatório

**Entrada:** `1`, `SRV-101`, `(Enter)`, `Teste`, `Descrição`, `Equipe`, `Balcão`, `(Enter)`, `(Enter)`, `(Enter)`, `0`

**Esperado:** Recusa o cadastro porque o título é obrigatório.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 1
Preencha os campos (os marcados com * são obrigatórios).
*Identificador: SRV-101
*Título:
*Categoria: Teste
*Descrição: Descrição
*Público-alvo: Equipe
*Canal/local de atendimento: Balcão
 Prazo (AAAA-MM-DD):
 Fonte:
 Verificado em:
O campo 'Título' é obrigatório e não pode ficar vazio.

[menu]
Escolha uma opção: 0
Até logo!
```

## 8. Atualizar o título e consultar

**Entrada:** `4`, `SRV-002`, `1`, `Título atualizado na evidência`, `2`, `SRV-002`, `0`

**Esperado:** Grava o novo título e a consulta seguinte mostra o título novo.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 4
Identificador do registro a atualizar: SRV-002
Registro encontrado.
  Identificador: SRV-002
  Título: Fale Conosco e Ouvidoria do Metrô
  Categoria: Atendimento
  Descrição: Registro de manifestações (reclamação, solicitação, elogio) pelo formulário do site, 24 horas, e Ouvidoria como segunda instância, por telefone ou formulário.
  Público-alvo: Passageiros do Metrô
  Canal/local de atendimento: site do Metrô (Fale Conosco); Ouvidoria pelos telefones (11) 3291-2890 e (11) 3291-2891, segunda a sexta, das 8h às 16h30 (Carta de Serviços de 2023)
  Prazo (AAAA-MM-DD): -
  Fonte: https://www.metro.sp.gov.br/pt_BR/fale-conosco/
  Verificado em: 2026-11-12
Qual campo deseja alterar?
1 - Título
2 - Categoria
3 - Descrição
4 - Público-alvo
5 - Canal/local de atendimento
6 - Prazo (AAAA-MM-DD)
7 - Fonte
8 - Verificado em
Número do campo: 1
Novo valor para 'Título': Título atualizado na evidência
Registro 'SRV-002' atualizado.

[menu]
Escolha uma opção: 2
Identificador: SRV-002
Registro encontrado.
  Identificador: SRV-002
  Título: Título atualizado na evidência
  Categoria: Atendimento
  Descrição: Registro de manifestações (reclamação, solicitação, elogio) pelo formulário do site, 24 horas, e Ouvidoria como segunda instância, por telefone ou formulário.
  Público-alvo: Passageiros do Metrô
  Canal/local de atendimento: site do Metrô (Fale Conosco); Ouvidoria pelos telefones (11) 3291-2890 e (11) 3291-2891, segunda a sexta, das 8h às 16h30 (Carta de Serviços de 2023)
  Prazo (AAAA-MM-DD): -
  Fonte: https://www.metro.sp.gov.br/pt_BR/fale-conosco/
  Verificado em: 2026-11-12

[menu]
Escolha uma opção: 0
Até logo!
```

## 9. Excluir registro existente e listar

**Entrada:** `5`, `SRV-003`, `3`, `0`

**Esperado:** Remove o SRV-003 e a listagem passa a ter 14 registros, sem ele.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-003
Registro 'SRV-003' excluído.

[menu]
Escolha uma opção: 3
14 registro(s) na lista.
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-015 | Atende+ da SPTrans | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 10. Excluir registro inexistente

**Entrada:** `5`, `SRV-999`, `0`

**Esperado:** Avisa que o registro não foi encontrado.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-999
Registro 'SRV-999' não encontrado.

[menu]
Escolha uma opção: 0
Até logo!
```

## 11. Pesquisar por trecho do título

**Entrada:** `6`, `1`, `metrô`, `0`

**Esperado:** Mostra só os serviços com 'metrô' no título, sem diferenciar maiúscula e acento.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 6
Pesquisar por: 1 - Título   2 - Categoria
Opção: 1
Trecho a procurar: metrô
6 registro(s) encontrado(s).
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 12. Pesquisar por categoria

**Entrada:** `6`, `2`, `segurança`, `0`

**Esperado:** Mostra só os serviços da categoria pesquisada.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 6
Pesquisar por: 1 - Título   2 - Categoria
Opção: 2
Trecho a procurar: segurança
3 registro(s) encontrado(s).
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança

[menu]
Escolha uma opção: 0
Até logo!
```

## 13. Pesquisar sem resultado

**Entrada:** `6`, `1`, `xyzabc`, `0`

**Esperado:** Avisa que nenhum registro foi encontrado.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 6
Pesquisar por: 1 - Título   2 - Categoria
Opção: 1
Trecho a procurar: xyzabc
Nenhum registro com 'xyzabc' em título.

[menu]
Escolha uma opção: 0
Até logo!
```

## 14. Ordenar por título

**Entrada:** `7`, `1`, `0`

**Esperado:** Religa os nós em ordem alfabética de título e mostra a lista ordenada.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 7
Ordenar por: 1 - Título   2 - Identificador   3 - Prazo
Opção: 1
Lista ordenada por título (crescente).
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-015 | Atende+ da SPTrans | Acessibilidade
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 15. Ordenar por identificador

**Entrada:** `7`, `2`, `0`

**Esperado:** Mostra a lista de SRV-001 a SRV-015.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 7
Ordenar por: 1 - Título   2 - Identificador   3 - Prazo
Opção: 2
Lista ordenada por id (crescente).
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-015 | Atende+ da SPTrans | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 16. Ordenar por prazo

**Entrada:** `7`, `3`, `0`

**Esperado:** Nenhum serviço tem prazo: o merge sort é estável e mantém a ordem original.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 7
Ordenar por: 1 - Título   2 - Identificador   3 - Prazo
Opção: 3
Lista ordenada por prazo (crescente).
SRV-001 | Central de Informações do Metrô | Atendimento
SRV-002 | Fale Conosco e Ouvidoria do Metrô | Atendimento
SRV-003 | Declaração de Ocorrências e Direto do Metrô | Informação
SRV-004 | SMS Segurança do Metrô | Segurança
SRV-005 | Achados e Perdidos do Metrô | Atendimento
SRV-006 | Atendimento Preferencial no Metrô | Acessibilidade
SRV-007 | Central de Relacionamento e Ouvidoria da CPTM | Atendimento
SRV-008 | Achados e Perdidos da CPTM | Atendimento
SRV-009 | Canal de Denúncia da CPTM | Segurança
SRV-010 | Táxi Acessível da CPTM | Acessibilidade
SRV-011 | Central de atendimento da ViaQuatro e da ViaMobilidade | Atendimento
SRV-012 | Ouvidoria da Artesp | Atendimento
SRV-013 | Defesa Civil 199 e alerta por SMS 40199 | Emergência
SRV-014 | Delegacia Eletrônica da Polícia Civil de SP | Segurança
SRV-015 | Atende+ da SPTrans | Acessibilidade

[menu]
Escolha uma opção: 0
Até logo!
```

## 17. Opção inexistente no menu

**Entrada:** `9`, `0`

**Esperado:** Avisa que a opção não existe e volta ao menu.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 9
Opção inexistente: digite um número de 0 a 7.

[menu]
Escolha uma opção: 0
Até logo!
```

## 18. Operação em lista vazia

**Entrada:** `5`, `SRV-001`, `5`, `SRV-002`, `5`, `SRV-003`, `5`, `SRV-004`, `5`, `SRV-005`, `5`, `SRV-006`, `5`, `SRV-007`, `5`, `SRV-008`, `5`, `SRV-009`, `5`, `SRV-010`, `5`, `SRV-011`, `5`, `SRV-012`, `5`, `SRV-013`, `5`, `SRV-014`, `5`, `SRV-015`, `3`, `6`, `1`, `metrô`, `7`, `1`, `0`

**Esperado:** Depois de excluir os 15, listar, pesquisar e ordenar avisam que a lista está vazia, sem erro.

**Observado:**

```text
15 registro(s) carregado(s).

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-001
Registro 'SRV-001' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-002
Registro 'SRV-002' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-003
Registro 'SRV-003' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-004
Registro 'SRV-004' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-005
Registro 'SRV-005' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-006
Registro 'SRV-006' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-007
Registro 'SRV-007' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-008
Registro 'SRV-008' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-009
Registro 'SRV-009' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-010
Registro 'SRV-010' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-011
Registro 'SRV-011' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-012
Registro 'SRV-012' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-013
Registro 'SRV-013' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-014
Registro 'SRV-014' excluído.

[menu]
Escolha uma opção: 5
Identificador do registro a excluir: SRV-015
Registro 'SRV-015' excluído.

[menu]
Escolha uma opção: 3
A lista está vazia: nenhum registro cadastrado.

[menu]
Escolha uma opção: 6
Pesquisar por: 1 - Título   2 - Categoria
Opção: 1
Trecho a procurar: metrô
A lista está vazia: nada para pesquisar.

[menu]
Escolha uma opção: 7
Ordenar por: 1 - Título   2 - Identificador   3 - Prazo
Opção: 1
A lista está vazia: nada para ordenar.

[menu]
Escolha uma opção: 0
Até logo!
```

