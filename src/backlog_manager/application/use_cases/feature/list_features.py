"""List Features use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.feature import (
    FeatureOutputDTO,
    ListFeaturesOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class ListFeaturesUseCase:
    """Use case para listar todas as features.

    Retorna features ordenadas por wave.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self) -> ListFeaturesOutputDTO:
        """Executa listagem de features.

        Returns:
            DTO com lista de features ordenadas por wave.
        """
        features = await self._uow.features.get_all()
        return ListFeaturesOutputDTO(
            features=[FeatureOutputDTO.from_entity(f) for f in features]
        )
