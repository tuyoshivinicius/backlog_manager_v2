"""Delete Feature use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.domain.services import FeatureService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class DeleteFeatureUseCase:
    """Use case para deletar feature.

    Somente permite delecao se nao houver historias associadas.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, feature_id: int) -> None:
        """Executa delecao de feature.

        Args:
            feature_id: ID da feature a deletar.

        Raises:
            ValueError: Se feature nao encontrada.
            FeatureHasStoriesException: Se feature tem historias.
        """
        service = FeatureService(self._uow.features)
        await service.delete_feature(feature_id)
