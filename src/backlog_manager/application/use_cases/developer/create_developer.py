"""Create Developer use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.developer import (
    CreateDeveloperInputDTO,
    DeveloperOutputDTO,
)
from backlog_manager.domain.services import DeveloperService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class CreateDeveloperUseCase:
    """Use case para criar novo desenvolvedor.

    Cria desenvolvedor com ID gerado automaticamente.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: CreateDeveloperInputDTO) -> DeveloperOutputDTO:
        """Executa criacao de desenvolvedor.

        Args:
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados do desenvolvedor criado.

        Raises:
            ValueError: Se nome invalido.
        """
        service = DeveloperService(self._uow.developers, self._uow.stories)
        developer = await service.create_developer(input_dto.name)
        developer.id = await self._uow.developers.add(developer)
        return DeveloperOutputDTO.from_entity(developer)
