"""GetDependencies use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.dependency import (
    GetDependenciesInputDTO,
    GetDependenciesOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class GetDependenciesUseCase:
    """Use case para consultar dependencias de uma historia.

    Retorna lista de IDs das historias das quais a historia depende.

    Attributes:
        _uow: Unit of Work para acesso aos repositorios.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(
        self, input_dto: GetDependenciesInputDTO
    ) -> GetDependenciesOutputDTO:
        """Executa consulta de dependencias.

        Args:
            input_dto: DTO com story_id.

        Returns:
            DTO com lista de IDs das dependencias.
        """
        story_id = input_dto.story_id

        dependencies = await self._uow.dependencies.get_dependencies(story_id)

        return GetDependenciesOutputDTO(
            story_id=story_id,
            dependencies=list(dependencies),
        )
