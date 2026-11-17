"""Hora de São Paulo para o app inteiro.

O servidor (contêiner na VPS) roda em UTC, três horas à frente de São Paulo. Toda hora que a
pessoa vê (chegada, "lido às", horário de pico, "hoje") sai daqui, e não de datetime.now().
"""
from datetime import date, datetime
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def agora() -> datetime:
    """Data e hora de São Paulo agora, sem fuso anexado (para somar minutos e comparar com horários do dia)."""
    return datetime.now(FUSO).replace(tzinfo=None)


def hoje() -> date:
    return agora().date()
