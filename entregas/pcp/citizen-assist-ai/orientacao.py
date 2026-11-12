"""Classe Orientacao: uma informação da base (um registro do JSON)."""

AVISO = "este assistente NÃO é um canal oficial."

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave", "resposta",
                       "documentos", "onde", "fonte", "verificado_em")


class Orientacao:
    """Guarda os dados de uma orientação e sabe se exibir na tela."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @classmethod
    def de_dict(cls, dados):
        """Cria uma Orientacao a partir de um dicionário do JSON.

        Levanta ValueError se faltar campo ou se o tipo estiver errado.
        """
        if not isinstance(dados, dict):
            raise ValueError("o registro não é um dicionário")
        faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in dados]
        if faltando:
            raise ValueError("campos faltando: " + ", ".join(faltando))
        for campo in ("palavras_chave", "documentos"):
            lista = dados[campo]
            if not isinstance(lista, list) or not all(isinstance(i, str) for i in lista):
                raise ValueError("o campo '" + campo + "' deve ser uma lista de textos")
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(dados[campo], str):
                raise ValueError("o campo '" + campo + "' deve ser texto")
        return cls(**{campo: dados[campo] for campo in CAMPOS_OBRIGATORIOS})

    def para_dict(self):
        """Devolve a orientação como dicionário (mesmo formato do JSON)."""
        return {campo: getattr(self, campo) for campo in CAMPOS_OBRIGATORIOS}

    def texto(self):
        """Monta o texto da orientação (sem imprimir nada)."""
        linhas = [">> " + self.titulo + "  [" + self.categoria + "]", self.resposta]
        if self.documentos:
            linhas.append("Documentos necessários:")
            for documento in self.documentos:
                linhas.append("  - " + documento)
        else:
            linhas.append("Documentos necessários: não informado na base.")
        linhas.append("Onde: " + self.onde)
        linhas.append("Fonte: " + self.fonte + " (verificado em " + self.verificado_em + ")")
        linhas.append("Aviso: " + AVISO)
        return "\n".join(linhas)

    def exibir(self):
        """Mostra a orientação na tela."""
        print(self.texto())
