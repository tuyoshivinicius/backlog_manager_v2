"""Create Feature use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.feature import (
    CreateFeatureInputDTO,
    FeatureOutputDTO,
)
from backlog_manager.domain.services import FeatureService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class CreateFeatureUseCase:
    """Use case para criar nova feature.

    Cria feature com validacao de unicidade de wave e nome.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: CreateFeatureInputDTO) -> FeatureOutputDTO:
        """Executa criacao de feature.

        Args:
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados da feature criada.

        Raises:
            ValueError: Se nome/wave invalido.
            DuplicateWaveException: Se wave ja existe.
            ValueError: Se nome ja existe.
        """
        service = FeatureService(self._uow.features)
        feature = await service.create_feature(input_dto.name, input_dto.wave)
        feature.id = await self._uow.features.add(feature)
        return FeatureOutputDTO.from_entity(feature)
