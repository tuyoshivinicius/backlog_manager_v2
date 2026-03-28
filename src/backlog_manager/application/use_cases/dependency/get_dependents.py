"""GetDependents use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.dependency import (
    GetDependentsInputDTO,
    GetDependentsOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class GetDependentsUseCase:
    """Use case para consultar dependentes de uma historia.

    Retorna lista de IDs das historias que dependem desta historia.

    Attributes:
        _uow: Unit of Work para acesso aos repositorios.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: GetDependentsInputDTO) -> GetDependentsOutputDTO:
        """Executa consulta de dependentes.

        Args:
            input_dto: DTO com story_id.

        Returns:
            DTO com lista de IDs dos dependentes.
        """
        story_id = input_dto.story_id

        dependents = await self._uow.dependencies.get_dependents(story_id)

        return GetDependentsOutputDTO(
            story_id=story_id,
            dependents=list(dependents),
        )
