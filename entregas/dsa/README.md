# DSA: Citizen Assist AI (lista encadeada em Python)

Sistema de terminal para cadastrar, consultar, atualizar, excluir, pesquisar e ordenar serviços e orientações ao cidadão. Armazenamento em lista encadeada feita pela equipe; busca linear e merge sort escritos à mão.

Integrantes / RM: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)

## Como executar

Requisito: Python 3.8+ (só biblioteca padrão, nada para instalar).

```
cd entregas/dsa
python main.py
```

Testes automatizados (na raiz do repositório):

```
python -m unittest discover -s tests/dsa -v
```

## O que tem em cada arquivo

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Menu interativo (só `input`/`print`) |
| `catalogo.py` | Operações: cadastrar, consultar, listar, atualizar, excluir, pesquisar, ordenar, carga do JSON |
| `lista_encadeada.py` | Classes `No` e `ListaEncadeada` |
| `algoritmos.py` | Busca linear, merge sort e comparação de texto |
| `servico.py` | Classe `Servico` (registro) e validação de data |
| `dados/servicos.json` | 15 serviços iniciais, tirados de páginas oficiais em 12/11/2026 e ainda em conferência pelo grupo |
| `docs/DOCUMENTACAO.md` | Documentação técnica, algoritmos e análise Big-O |
| `docs/EVIDENCIAS.md` | Cenários de teste: entrada, esperado, observado |
| `integracao.py` | EXTRA, fora do enunciado: funções para o sistema web reutilizar o catálogo |
| `../../tests/dsa/test_dsa.py` | Testes com `unittest` |

Mais detalhes na `docs/DOCUMENTACAO.md`.
