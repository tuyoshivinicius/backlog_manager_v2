"""Dependency-related exceptions."""

from __future__ import annotations

from backlog_manager.domain.exceptions.base import BacklogManagerException


class DependencyException(BacklogManagerException):
    """Erros relacionados a dependencias entre historias.

    Classe base para excecoes de ciclo e wave invalida.
    """


class CyclicDependencyException(DependencyException):
    """Ciclo detectado no grafo de dependencias.

    Lancada quando uma operacao criaria ou detecta um ciclo
    no grafo de dependencias entre historias.

    Attributes:
        path: Lista de IDs de historias formando o ciclo.
              Ex: ["AUTH-001", "AUTH-002", "AUTH-003", "AUTH-001"]

    Example:
        >>> try:
        ...     # adicionar dependencia que cria ciclo
        ...     pass
        ... except CyclicDependencyException as e:
        ...     print(f"Ciclo: {' -> '.join(e.path)}")
    """

    def __init__(self, path: list[str], message: str | None = None) -> None:
        """Initialize exception.

        Args:
            path: Lista de IDs formando o ciclo.
            message: Mensagem customizada (opcional).
        """
        self.path = path
        cycle_str = " -> ".join(path)
        default_message = f"Ciclo detectado nas dependencias: {cycle_str}"
        super().__init__(message or default_message)


class InvalidWaveDependencyException(DependencyException):
    """Dependencia invalida entre waves.

    Lancada quando uma historia tenta depender de outra
    que pertence a uma wave posterior.

    Attributes:
        story_id: ID da historia que tenta depender.
        depends_on_id: ID da historia da qual tenta depender.
        story_wave: Wave da historia.
        depends_on_wave: Wave da dependencia.

    Example:
        >>> raise InvalidWaveDependencyException(
        ...     story_id="AUTH-001",
        ...     depends_on_id="FEAT-001",
        ...     story_wave=1,
        ...     depends_on_wave=2
        ... )
    """

    def __init__(
        self,
        story_id: str,
        depends_on_id: str,
        story_wave: int,
        depends_on_wave: int,
        message: str | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            story_id: ID da historia que tenta depender.
            depends_on_id: ID da historia da qual tenta depender.
            story_wave: Wave da historia.
            depends_on_wave: Wave da dependencia.
            message: Mensagem customizada (opcional).
        """
        self.story_id = story_id
        self.depends_on_id = depends_on_id
        self.story_wave = story_wave
        self.depends_on_wave = depends_on_wave
        default_message = (
            f"Historia {story_id} (wave {story_wave}) nao pode depender de "
            f"{depends_on_id} (wave {depends_on_wave}): dependencia de wave posterior"
        )
        super().__init__(message or default_message)
