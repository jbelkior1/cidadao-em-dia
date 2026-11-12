"""Lista encadeada simples feita à mão (sem usar list/dict para guardar os registros)."""


class No:
    """Um nó: guarda um dado (Servico) e a referência para o próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None  # None = fim da lista


class ListaEncadeada:
    """Lista encadeada com referência para a cabeça e para a cauda.

    cabeca -> [dado|•] -> [dado|•] -> [dado|None]   <- cauda
    """

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0

    # ---------- consultas ----------
    def tamanho(self):
        return self._tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def percorrer(self):
        """Gerador: devolve cada dado, do primeiro ao último nó."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def buscar_por_id(self, id):
        """Busca linear pelo id (sem diferenciar maiúsculas). Devolve o dado ou None."""
        alvo = id.upper()
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id.upper() == alvo:
                return atual.dado
            atual = atual.proximo
        return None

    # ---------- inserção ----------
    def inserir_inicio(self, dado):
        """Insere antes da cabeça. O(1)."""
        novo = No(dado)
        novo.proximo = self.cabeca
        self.cabeca = novo
        if self.cauda is None:  # a lista estava vazia
            self.cauda = novo
        self._tamanho += 1

    def inserir_fim(self, dado):
        """Insere depois da cauda. O(1) porque guardamos a referência da cauda."""
        novo = No(dado)
        if self.cabeca is None:
            self.cabeca = novo
        else:
            self.cauda.proximo = novo
        self.cauda = novo
        self._tamanho += 1

    # ---------- atualização ----------
    def atualizar(self, id, **campos):
        """Troca campos do registro com esse id. Devolve True se achou, False se não."""
        dado = self.buscar_por_id(id)
        if dado is None:
            return False
        for nome, valor in campos.items():
            setattr(dado, nome, valor)
        return True

    # ---------- remoção ----------
    def remover(self, id):
        """Remove o nó com esse id. Trata cabeça, meio, fim e nó único. Devolve True/False."""
        alvo = id.upper()
        anterior = None
        atual = self.cabeca
        while atual is not None and atual.dado.id.upper() != alvo:
            anterior = atual
            atual = atual.proximo
        if atual is None:
            return False  # não encontrou (inclui lista vazia)
        if anterior is None:
            # remove a cabeça (se for o único nó, a cabeça vira None)
            self.cabeca = atual.proximo
        else:
            # remove meio ou fim: o anterior pula o nó removido
            anterior.proximo = atual.proximo
        if atual is self.cauda:
            self.cauda = anterior  # se era o único, anterior é None -> lista vazia
        atual.proximo = None
        self._tamanho -= 1
        return True
