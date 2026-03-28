"""List Developers use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.developer import (
    DeveloperOutputDTO,
    ListDevelopersOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class ListDevelopersUseCase:
    """Use case para listar todos os desenvolvedores.

    Retorna desenvolvedores ordenados por nome.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self) -> ListDevelopersOutputDTO:
        """Executa listagem de desenvolvedores.

        Returns:
            DTO com lista de desenvolvedores ordenados por nome.
        """
        developers = await self._uow.developers.get_all()
        return ListDevelopersOutputDTO(
            developers=[DeveloperOutputDTO.from_entity(d) for d in developers]
        )
