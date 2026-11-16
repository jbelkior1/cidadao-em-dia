"""A decisão do dia: "pode ir", "saia mais cedo" ou "mude o caminho".

ESTE É O LUGAR DA MATÉRIA DE CS.
O enunciado de CS pede um módulo de decisão lógica com 3 ou 4 variáveis
booleanas, com tabela-verdade, expressão canônica, Karnaugh e circuito feitos
pelo grupo, à mão. Depois, a lógica
simplificada vira programa.

As quatro entradas que o app entrega para essa lógica são:
    F = há falha numa linha do trajeto
    C = há aviso de chuva ou tempestade do INMET para a cidade
    A = alguma estação do trajeto tem alagamento registrado por perto
    P = é horário de pico

Enquanto o grupo não terminar a parte de CS, vale a regra PROVISÓRIA abaixo,
escrita como prioridades simples. Quando a expressão simplificada do grupo
estiver pronta, ela substitui o corpo de `decidir` (mantendo as mesmas entradas
e saídas) e `REGRA_PROVISORIA` passa a False.
"""
from datetime import datetime

REGRA_PROVISORIA = True

PODE_IR = "pode_ir"
MAIS_CEDO = "mais_cedo"
PLANO_B = "plano_b"

TEXTO = {
    PODE_IR: "Pode ir",
    MAIS_CEDO: "Saia mais cedo",
    PLANO_B: "Mude o caminho",
}


def horario_de_pico(agora: datetime | None = None) -> bool:
    """Dias úteis, das 6h às 9h e das 16h às 19h30."""
    agora = agora or datetime.now()
    if agora.weekday() >= 5:
        return False
    minutos = agora.hour * 60 + agora.minute
    return 360 <= minutos < 540 or 960 <= minutos < 1170


def decidir(falha: bool, chuva: bool, alagamento: bool, pico: bool) -> str:
    """Regra provisória (não é a entrega de CS): prioridades simples."""
    if falha:
        return PLANO_B
    if chuva and (alagamento or pico):
        return MAIS_CEDO
    return PODE_IR
