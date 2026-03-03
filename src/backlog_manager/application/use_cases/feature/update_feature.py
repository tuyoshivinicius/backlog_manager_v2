"""Update Feature use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.feature import (
    FeatureOutputDTO,
    UpdateFeatureInputDTO,
)
from backlog_manager.domain.services import FeatureService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class UpdateFeatureUseCase:
    """Use case para atualizar feature existente.

    Suporta atualizacao parcial (nome e/ou wave).
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: UpdateFeatureInputDTO) -> FeatureOutputDTO:
        """Executa atualizacao de feature.

        Args:
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados da feature atualizada.

        Raises:
            ValueError: Se feature nao encontrada.
            ValueError: Se nome/wave invalido.
            DuplicateWaveException: Se wave ja existe em outra feature.
            ValueError: Se nome ja existe em outra feature.
        """
        service = FeatureService(self._uow.features)
        feature = await service.update_feature(
            input_dto.feature_id,
            name=input_dto.name,
            wave=input_dto.wave,
        )
        await self._uow.features.update(feature)
        return FeatureOutputDTO.from_entity(feature)
