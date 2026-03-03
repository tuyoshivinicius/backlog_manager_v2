"""Story status value object."""

from enum import StrEnum


class StoryStatus(StrEnum):
    """Estados do workflow de uma historia conforme SRS 6.5.

    Transicoes: Modelo flexivel - todas as transicoes sao permitidas.
    Estados em portugues (sem acentos) para compatibilidade com interface.
    """

    BACKLOG = "BACKLOG"
    EXECUCAO = "EXECUCAO"
    TESTES = "TESTES"
    CONCLUIDO = "CONCLUIDO"
    IMPEDIDO = "IMPEDIDO"
