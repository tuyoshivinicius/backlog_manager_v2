"""Allocation-related exceptions."""

from __future__ import annotations

from backlog_manager.domain.exceptions.base import BacklogManagerException


class AllocationException(BacklogManagerException):
    """Erros relacionados a alocacao automatica de historias.

    Classe base para excecoes do algoritmo de alocacao.
    """


class MaxIterationsExceeded(AllocationException):
    """Numero maximo de iteracoes excedido na alocacao.

    Lancada quando o algoritmo de alocacao nao consegue
    convergir dentro do limite de iteracoes.

    Attributes:
        max_iterations: Limite de iteracoes configurado.
        stories_remaining: Numero de historias nao alocadas.

    Example:
        >>> raise MaxIterationsExceeded(
        ...     max_iterations=1000,
        ...     stories_remaining=15
        ... )
    """

    def __init__(
        self,
        max_iterations: int,
        stories_remaining: int,
        message: str | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            max_iterations: Limite de iteracoes configurado.
            stories_remaining: Numero de historias nao alocadas.
            message: Mensagem customizada (opcional).
        """
        self.max_iterations = max_iterations
        self.stories_remaining = stories_remaining
        default_message = (
            f"Alocacao nao convergiu apos {max_iterations} iteracoes: "
            f"{stories_remaining} historia(s) nao alocada(s)"
        )
        super().__init__(message or default_message)
