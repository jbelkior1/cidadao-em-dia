"""Busca e ordenação escritas à mão sobre a lista encadeada.

Escolhas:
- Busca: busca linear (percorre os nós um a um). Simples, e é a única possível numa
  lista encadeada, que não permite acesso direto por posição.
- Ordenação: merge sort de lista encadeada. Só religa os nós (não copia dados),
  é estável e custa O(n log n), melhor que insertion sort (O(n^2)).
"""

from lista_encadeada import No

_ACENTOS = {
    "á": "a", "à": "a", "â": "a", "ã": "a", "ä": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ç": "c",
}


# ---------- texto (comparações feitas à mão) ----------
def normalizar(texto):
    """Minúsculas e sem acentos, letra a letra."""
    resultado = ""
    for letra in texto.lower():
        resultado = resultado + _ACENTOS.get(letra, letra)
    return resultado


def comparar_texto(a, b):
    """Compara dois textos letra a letra: -1 se a<b, 0 se iguais, 1 se a>b."""
    a = normalizar(a)
    b = normalizar(b)
    i = 0
    while i < len(a) and i < len(b):
        if ord(a[i]) < ord(b[i]):
            return -1
        if ord(a[i]) > ord(b[i]):
            return 1
        i += 1
    if len(a) < len(b):
        return -1
    if len(a) > len(b):
        return 1
    return 0


def contem_trecho(texto, trecho):
    """Diz se 'trecho' aparece dentro de 'texto' (sem diferenciar maiúsculas/acentos)."""
    texto = normalizar(texto)
    trecho = normalizar(trecho)
    if len(trecho) == 0:
        return True
    inicio = 0
    while inicio + len(trecho) <= len(texto):
        j = 0
        while j < len(trecho) and texto[inicio + j] == trecho[j]:
            j += 1
        if j == len(trecho):
            return True
        inicio += 1
    return False


# ---------- busca linear ----------
def buscar_por_atributo(lista, atributo, trecho):
    """Busca linear: percorre a lista e junta quem contém o trecho no atributo
    ('titulo' ou 'categoria'). Devolve uma list comum, só para exibição."""
    achados = []
    for servico in lista.percorrer():
        if contem_trecho(getattr(servico, atributo), trecho):
            achados.append(servico)
    return achados


# ---------- merge sort ----------
def _vem_antes_ou_igual(a, b, criterio):
    """True se o serviço a pode ficar antes (ou empatado) do serviço b."""
    if criterio == "prazo":
        # quem não tem prazo vai para o fim
        if a.prazo == "":
            return b.prazo == ""
        if b.prazo == "":
            return True
        return comparar_texto(a.prazo, b.prazo) <= 0
    return comparar_texto(getattr(a, criterio), getattr(b, criterio)) <= 0


def _dividir(cabeca):
    """Divide a cadeia ao meio (referência lenta e rápida). Devolve (primeira, segunda)."""
    lento = cabeca
    rapido = cabeca.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    segunda = lento.proximo
    lento.proximo = None
    return cabeca, segunda


def _mesclar(a, b, criterio):
    """Junta duas cadeias já ordenadas religando os nós. Estável (empate: sai o de a)."""
    inicio = No(None)  # nó auxiliar só para simplificar o começo
    ponta = inicio
    while a is not None and b is not None:
        if _vem_antes_ou_igual(a.dado, b.dado, criterio):
            ponta.proximo = a
            a = a.proximo
        else:
            ponta.proximo = b
            b = b.proximo
        ponta = ponta.proximo
    if a is not None:
        ponta.proximo = a
    else:
        ponta.proximo = b
    return inicio.proximo


def _merge_sort(cabeca, criterio):
    if cabeca is None or cabeca.proximo is None:
        return cabeca
    primeira, segunda = _dividir(cabeca)
    primeira = _merge_sort(primeira, criterio)
    segunda = _merge_sort(segunda, criterio)
    return _mesclar(primeira, segunda, criterio)


def ordenar(lista, criterio):
    """Ordena a lista em ordem crescente por 'titulo', 'id' ou 'prazo', religando os nós.
    Depois ajusta a cauda."""
    lista.cabeca = _merge_sort(lista.cabeca, criterio)
    ultimo = lista.cabeca
    while ultimo is not None and ultimo.proximo is not None:
        ultimo = ultimo.proximo
    lista.cauda = ultimo
