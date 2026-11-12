"""O combinado entre os módulos e o Sistema.

Cada matéria devolve uma ou mais Etapas. O orquestrador junta as etapas,
desenha o cartão que o cidadão vê e o "como chegamos nessa resposta".
"""
from dataclasses import dataclass


@dataclass
class Etapa:
    materia: str          # código da matéria: "PCP", "CS", "SERS"...
    titulo: str           # o que a etapa fez, em poucas palavras ("aplicou a regra")
    texto: str            # o que o cidadão vê no cartão
    explicacao: str = ""  # como chegou nisso; aparece no "como chegamos"
    pronto: bool = True   # False = módulo em construção; o Sistema mostra e segue
