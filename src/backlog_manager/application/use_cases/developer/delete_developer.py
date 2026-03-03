"""Delete Developer use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.developer import DeleteDeveloperOutputDTO
from backlog_manager.domain.services import DeveloperService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class DeleteDeveloperUseCase:
    """Use case para deletar desenvolvedor.

    Historias alocadas sao desalocadas via ON DELETE SET NULL.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, developer_id: int) -> DeleteDeveloperOutputDTO:
        """Executa delecao de desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor a deletar.

        Returns:
            DTO com ID deletado e quantidade de historias desalocadas.

        Raises:
            ValueError: Se desenvolvedor nao encontrado.
        """
        service = DeveloperService(self._uow.developers, self._uow.stories)
        stories_unassigned = await service.delete_developer(developer_id)
        return DeleteDeveloperOutputDTO(
            developer_id=developer_id,
            stories_unassigned=stories_unassigned,
        )
