"""Update Developer use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.developer import (
    DeveloperOutputDTO,
    UpdateDeveloperInputDTO,
)
from backlog_manager.domain.services import DeveloperService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class UpdateDeveloperUseCase:
    """Use case para atualizar desenvolvedor existente."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: UpdateDeveloperInputDTO) -> DeveloperOutputDTO:
        """Executa atualizacao de desenvolvedor.

        Args:
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados do desenvolvedor atualizado.

        Raises:
            ValueError: Se desenvolvedor nao encontrado.
            ValueError: Se nome invalido.
        """
        service = DeveloperService(self._uow.developers, self._uow.stories)
        developer = await service.update_developer(
            input_dto.developer_id,
            input_dto.name,
        )
        await self._uow.developers.update(developer)
        return DeveloperOutputDTO.from_entity(developer)
