"""A decisão do dia: "pode ir", "saia mais cedo" ou "mude o caminho".

As quatro entradas que o app entrega para a decisão são:
    F = há falha numa linha do trajeto
    C = há aviso de chuva ou tempestade do INMET para a cidade
    A = alguma estação do trajeto tem alagamento registrado por perto
    P = é horário de pico

A regra é escrita como prioridades simples: falha numa linha muda o caminho; aviso de chuva junto com
alagamento ou pico manda sair mais cedo; fora disso, pode ir.
"""
from datetime import datetime

from sistema import hora

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
    agora = agora or hora.agora()
    if agora.weekday() >= 5:
        return False
    minutos = agora.hour * 60 + agora.minute
    return 360 <= minutos < 540 or 960 <= minutos < 1170


def decidir(falha: bool, chuva: bool, alagamento: bool, pico: bool) -> str:
    """Prioridades simples: falha, depois chuva com alagamento ou pico."""
    if falha:
        return PLANO_B
    if chuva and (alagamento or pico):
        return MAIS_CEDO
    return PODE_IR
