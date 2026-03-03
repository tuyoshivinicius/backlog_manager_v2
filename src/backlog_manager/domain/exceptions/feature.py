"""Feature-related exceptions."""

from __future__ import annotations

from backlog_manager.domain.exceptions.base import BacklogManagerException


class FeatureException(BacklogManagerException):
    """Erros relacionados a features.

    Classe base para excecoes de wave duplicada e feature com historias.
    """


class DuplicateWaveException(FeatureException):
    """Wave duplicada ao criar/atualizar feature.

    Lancada quando tenta-se criar ou atualizar uma feature
    com um numero de wave que ja existe em outra feature.

    Attributes:
        wave: Numero da wave duplicada.
        existing_feature_name: Nome da feature que ja usa a wave.

    Example:
        >>> raise DuplicateWaveException(
        ...     wave=2,
        ...     existing_feature_name="Autenticacao"
        ... )
    """

    def __init__(
        self,
        wave: int,
        existing_feature_name: str,
        message: str | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            wave: Numero da wave duplicada.
            existing_feature_name: Nome da feature que ja usa a wave.
            message: Mensagem customizada (opcional).
        """
        self.wave = wave
        self.existing_feature_name = existing_feature_name
        default_message = (
            f"Wave {wave} ja esta em uso pela feature '{existing_feature_name}'"
        )
        super().__init__(message or default_message)


class FeatureHasStoriesException(FeatureException):
    """Tentativa de deletar feature com historias associadas.

    Lancada quando tenta-se deletar uma feature que ainda
    possui historias vinculadas.

    Attributes:
        feature_id: ID da feature.
        feature_name: Nome da feature.
        story_count: Numero de historias associadas.

    Example:
        >>> raise FeatureHasStoriesException(
        ...     feature_id=1,
        ...     feature_name="Autenticacao",
        ...     story_count=5
        ... )
    """

    def __init__(
        self,
        feature_id: int,
        feature_name: str,
        story_count: int,
        message: str | None = None,
    ) -> None:
        """Initialize exception.

        Args:
            feature_id: ID da feature.
            feature_name: Nome da feature.
            story_count: Numero de historias associadas.
            message: Mensagem customizada (opcional).
        """
        self.feature_id = feature_id
        self.feature_name = feature_name
        self.story_count = story_count
        default_message = (
            f"Nao e possivel deletar feature '{feature_name}' (ID: {feature_id}): "
            f"existem {story_count} historia(s) associada(s)"
        )
        super().__init__(message or default_message)
