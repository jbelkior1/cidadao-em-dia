# Integrantes: João Vitor Belchior Domingos Leite (RM 572478); João Pedro Pereira Teixeira (RM 569937); Thiago de Oliveira Coelho Souza (RM 568783)
"""Registro de um serviço ou orientação ao cidadão (Citizen Assist AI)."""

# Campos exigidos pelo enunciado (nenhum pode ficar vazio).
CAMPOS_OBRIGATORIOS = ("id", "titulo", "categoria", "descricao", "publico_alvo", "canal")
# Campos extras do nosso projeto (podem ficar vazios).
CAMPOS_OPCIONAIS = ("prazo", "fonte", "verificado_em")
# Nomes mostrados ao usuário no menu.
ROTULOS = {
    "id": "Identificador",
    "titulo": "Título",
    "categoria": "Categoria",
    "descricao": "Descrição",
    "publico_alvo": "Público-alvo",
    "canal": "Canal/local de atendimento",
    "prazo": "Prazo (AAAA-MM-DD)",
    "fonte": "Fonte",
    "verificado_em": "Verificado em",
}


def data_valida(texto):
    """Diz se o texto é uma data real no formato AAAA-MM-DD."""
    if len(texto) != 10 or texto[4] != "-" or texto[7] != "-":
        return False
    ano, mes, dia = texto[0:4], texto[5:7], texto[8:10]
    if not (ano.isdigit() and mes.isdigit() and dia.isdigit()):
        return False
    ano, mes, dia = int(ano), int(mes), int(dia)
    if ano < 1 or mes < 1 or mes > 12 or dia < 1:
        return False
    dias_no_mes = 31
    if mes in (4, 6, 9, 11):
        dias_no_mes = 30
    elif mes == 2:
        bissexto = (ano % 4 == 0 and ano % 100 != 0) or ano % 400 == 0
        dias_no_mes = 29 if bissexto else 28
    return dia <= dias_no_mes


class Servico:
    """Um serviço ou orientação. É o 'dado' guardado em cada nó da lista."""

    def __init__(self, id, titulo, categoria, descricao, publico_alvo, canal,
                 prazo="", fonte="", verificado_em=""):
        self.id = id
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.publico_alvo = publico_alvo
        self.canal = canal
        self.prazo = prazo
        self.fonte = fonte
        self.verificado_em = verificado_em

    def como_texto(self):
        """Texto de várias linhas para exibir o registro."""
        linhas = []
        for campo in CAMPOS_OBRIGATORIOS + CAMPOS_OPCIONAIS:
            valor = getattr(self, campo)
            if valor == "" and campo in CAMPOS_OPCIONAIS:
                valor = "-"
            linhas.append("  " + ROTULOS[campo] + ": " + valor)
        return "\n".join(linhas)

    def resumo(self):
        """Uma linha só: id | título | categoria."""
        return self.id + " | " + self.titulo + " | " + self.categoria
