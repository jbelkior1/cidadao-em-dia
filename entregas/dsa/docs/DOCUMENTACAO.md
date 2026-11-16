# Documentação técnica: DSA (Citizen Assist AI)

Global Solution 2026.2 · CitizenTech · Disciplina: Data Structures and Algorithms (DSA)
Grupo / integrantes / RM: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)

## 1. Objetivo e linguagem

Sistema de gerenciamento e consulta de serviços e orientações ao cidadão (emissão de documentos, assistência social, educação, saúde, atendimento comunitário), controlado por um menu interativo de terminal.

**Linguagem escolhida: Python 3** (somente biblioteca padrão). Os registros e os nós são objetos (classes) com referências explícitas entre nós, e a estrutura principal de armazenamento é uma lista encadeada implementada pela equipe. Nenhuma `list`, `dict` ou `set` nativa guarda os registros nem serve de índice.

Os dados iniciais (`dados/servicos.json`) são 15 serviços tirados de páginas oficiais em 12/11/2026 e conferidos de novo em 16/11/2026. Não há integração com plataformas governamentais nem IA generativa.

## 2. Campos dos registros

Classe `Servico` (`servico.py`). Todos os campos são texto.

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | sim | Identificador único (ex.: `SRV-001`). Não diferencia maiúsculas de minúsculas e nunca muda depois de cadastrado. |
| `titulo` | sim | Nome do serviço ou orientação. |
| `categoria` | sim | Ex.: Documentos, Assistência social, Educação, Saúde. |
| `descricao` | sim | Explicação resumida. |
| `publico_alvo` | sim | A quem se destina. |
| `canal` | sim | Canal ou local de atendimento. |
| `prazo` | não | Data no formato `AAAA-MM-DD` (validada). Pode ficar vazio. |
| `fonte` | não | Link ou órgão de referência. |
| `verificado_em` | não | Quando a informação foi conferida. |

## 3. A lista encadeada

Implementada em `lista_encadeada.py` com duas classes:

- `No`: guarda `dado` (um `Servico`) e `proximo` (referência para o próximo nó, ou `None` no último).
- `ListaEncadeada`: guarda `cabeca` (primeiro nó), `cauda` (último nó) e o contador de tamanho.

```
cabeca                                              cauda
  |                                                   |
  v                                                   v
[ SRV-001 | • ] --> [ SRV-002 | • ] --> [ SRV-003 | None ]
```

Operações:

| Operação | Método | O que faz |
|---|---|---|
| Inserção | `inserir_fim`, `inserir_inicio` | Cria um `No` e religa as referências (fim usa a `cauda`). |
| Percurso | `percorrer` | Gerador que visita os nós do primeiro ao último. |
| Busca por id | `buscar_por_id` | Percorre até achar o id. |
| Atualização | `atualizar` | Acha o registro pelo id e troca os campos. |
| Remoção | `remover` | Acha o nó e o "pula" (casos: cabeça, meio, fim, nó único; ajusta `cauda` e tamanho). |
| Tamanho / vazia | `tamanho`, `esta_vazia` | Contador e teste de `cabeca is None`. |

Remoção, por caso:

```
cabeça:   cabeca = no.proximo
meio:     anterior.proximo = no.proximo
fim:      anterior.proximo = None   e   cauda = anterior
único:    cabeca = None   e   cauda = None   (lista volta a ficar vazia)
```

Observação: a leitura do JSON usa uma `list` temporária produzida por `json.load`, apenas durante a carga; cada item é inserido nó a nó e a `list` é descartada. Listas comuns também aparecem como **valor de retorno para exibição** (resultado de listar e de pesquisar).

## 4. Organização do código

```
entregas/dsa/
  main.py              menu de terminal (só input/print)
  catalogo.py          operações do sistema sobre a lista (sem input/print)
  lista_encadeada.py   No e ListaEncadeada
  algoritmos.py        busca linear, merge sort e comparação de texto
  servico.py           classe Servico e validação de data
  integracao.py        EXTRA: funções para o sistema web (não faz parte da entrega de DSA)
  dados/servicos.json  15 serviços iniciais (fontes oficiais, conferidas)
  docs/                esta documentação e EVIDENCIAS.md
tests/dsa/test_dsa.py  testes automatizados (unittest)
```

Fluxo: `main.py` lê o que o usuário digita → chama `Catalogo` → `Catalogo` valida e usa `ListaEncadeada` e `algoritmos` → devolve `(sucesso, mensagem, dado)` → `main.py` imprime.

## 5. Instruções de uso

Requisito: Python 3.8 ou superior, sem instalar nada.

```
cd entregas/dsa
python main.py
```

Menu:

| Opção | Ação |
|---|---|
| 1 | Cadastrar (pede os campos; os 6 primeiros são obrigatórios) |
| 2 | Consultar por identificador |
| 3 | Listar todos |
| 4 | Atualizar um campo de um registro (o id não muda) |
| 5 | Excluir por identificador |
| 6 | Pesquisar por título ou categoria (trecho do texto) |
| 7 | Ordenar por título, identificador ou prazo (crescente); a lista fica reordenada |
| 0 | Sair |

Tratamento de erros: opção inexistente, valor incompatível, campo obrigatório vazio, id duplicado, prazo inválido, registro não encontrado e lista vazia geram uma mensagem clara e o programa continua.

Testes automatizados, a partir da raiz do repositório:

```
python -m unittest discover -s tests/dsa -v
```

## 6. Algoritmos

Notação: **n** = número de registros na lista (número de nós). **L** = tamanho de um texto (título/categoria/id) e **m** = tamanho do trecho pesquisado; são pequenos e limitados, então as comparações de texto são tratadas como custo constante.

### 6.1 Busca linear (por id, título ou categoria)

Escolhida porque uma lista encadeada só permite chegar a um nó percorrendo desde a cabeça; não há acesso direto por posição, então busca binária não se aplica.

Passo a passo (`buscar_por_atributo` em `algoritmos.py`; `buscar_por_id` em `lista_encadeada.py`):

1. Comece no primeiro nó (`cabeca`).
2. Compare o campo do registro do nó com o que se procura. Para o id, a comparação é de igualdade (sem diferenciar maiúsculas). Para título/categoria, procura-se o trecho dentro do texto: `contem_trecho` normaliza os dois textos (minúsculas, sem acento) e tenta casar o trecho em cada posição do texto, letra a letra.
3. Se casou, guarda/devolve o registro (a busca por id para aqui; a por título/categoria continua até o fim para achar todos).
4. Vá para `proximo`. Se chegou a `None`, termina.

Exemplo: lista `A1 Tarifa social`, `B2 Segunda via do RG`, `C3 Atendimento de saúde`; pesquisar título por `"via"`:
- A1: "tarifa social" não contém "via" → segue.
- B2: "segunda via do rg" contém "via" (a partir da posição 8) → guarda B2.
- C3: "atendimento de saude" não contém → segue. Fim: resultado = B2.

### 6.2 Ordenação: merge sort sobre a lista encadeada

Escolhido por ser O(n log n) e por combinar bem com listas encadeadas: dividir ao meio e juntar só exigem religar referências, sem copiar dados e sem acesso por índice. É estável (registros empatados mantêm a ordem anterior). Critérios: título, id ou prazo (quem não tem prazo vai para o fim). Funções: `ordenar`, `_merge_sort`, `_dividir`, `_mesclar` em `algoritmos.py`.

Passo a passo:

1. Se a cadeia tem 0 ou 1 nó, já está ordenada.
2. **Dividir**: com duas referências, uma que anda 1 nó por vez (lenta) e outra que anda 2 (rápida); quando a rápida chega ao fim, a lenta está no meio. Corta-se a cadeia ali (`lento.proximo = None`) em duas metades.
3. Ordene cada metade recursivamente.
4. **Mesclar**: compare os primeiros nós das duas metades; o menor (ou igual, vindo da primeira metade) é ligado ao resultado e a referência daquela metade avança. Repita até uma metade acabar e ligue o resto da outra.
5. Ao final, `ordenar` atualiza `cabeca` e percorre a lista uma vez para reposicionar a `cauda`.

Exemplo, ordenar por título `[Tarifa, Segunda via, Atendimento, Bolsa]`:
- Divide: `[Tarifa, Segunda via]` e `[Atendimento, Bolsa]`.
- Divide de novo até nós sozinhos; mescla `[Tarifa]`+`[Segunda via]` → `[Segunda via, Tarifa]`; mescla `[Atendimento]`+`[Bolsa]` → `[Atendimento, Bolsa]`.
- Mescla final: Atendimento < Segunda via? sim → Atendimento; Bolsa < Segunda via? sim → Bolsa; sobram `Segunda via, Tarifa`. Resultado: `[Atendimento, Bolsa, Segunda via, Tarifa]`.

A comparação de textos (`comparar_texto`) é feita à mão, letra a letra, ignorando maiúsculas e acentos. Nenhuma função pronta de ordenação (`sorted`, `list.sort`) nem de busca (`in`, `index`, `find`) é usada nesses algoritmos; um teste automatizado confere isso lendo o código-fonte.

## 7. Análise Big-O

Hipóteses: n = número de nós; a lista guarda referência para a **cabeça e para a cauda**; as comparações de texto custam O(1) (L e m pequenos, ver seção 6); o id é buscado percorrendo a lista (não há índice paralelo, de propósito).

| Operação | Melhor caso | Pior caso | Justificativa (código) |
|---|---|---|---|
| Inserção no fim (`inserir_fim`) | O(1) | O(1) | Usa a `cauda`: cria o nó e liga `cauda.proximo`. Sem ponteiro de cauda teria de percorrer a lista: O(n). |
| Inserção no início (`inserir_inicio`) | O(1) | O(1) | Só religa a cabeça. |
| Cadastrar (`Catalogo.cadastrar`) | O(n) | O(n) | Antes de inserir, verifica id duplicado com `buscar_por_id`, que percorre a lista toda quando o id é novo. A inserção em si é O(1). |
| Busca por id (`buscar_por_id`) | O(1) | O(n) | Percorre nó a nó; melhor caso é o id estar na cabeça. |
| Busca por título/categoria (`buscar_por_atributo`) | O(n) | O(n) | Sempre percorre todos os nós (devolve todos os que casam); cada comparação de trecho é O(1) pela hipótese (na verdade O(L·m)). |
| Atualização (`atualizar`) | O(1) | O(n) | Busca o nó pelo id; trocar o campo é O(1). |
| Exclusão (`remover`) | O(1) | O(n) | Percorre guardando o `anterior` até achar; religar é O(1). Melhor caso: a cabeça. Id inexistente percorre tudo: O(n). |
| Listar / percurso | O(n) | O(n) | Visita cada nó uma vez. |
| Ordenação (merge sort) | O(n log n) | O(n log n) | Cada nível da recursão divide e mescla n nós (O(n)); há cerca de log₂ n níveis. Vale para qualquer ordem inicial. Espaço extra O(log n) (pilha da recursão), pois os nós são só religados. |

Para comparação: insertion sort numa lista encadeada seria O(n²) no pior caso; por isso o merge sort foi escolhido.

## 8. Limitações

- A ordenação é sempre crescente.
- O id é ordenado como texto: sem zeros à esquerda, SRV-10 viria antes de SRV-2 (os ids da base têm 3 dígitos, como SRV-002).
- Os dados iniciais vieram de páginas oficiais, mas o grupo ainda precisa abrir cada fonte e confirmar o texto.
- A lista só existe em memória: alterações feitas no menu não são gravadas no JSON.
