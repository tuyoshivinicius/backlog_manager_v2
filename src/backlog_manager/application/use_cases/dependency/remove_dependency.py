"""RemoveDependency use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.dependency import (
    RemoveDependencyInputDTO,
    RemoveDependencyOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class RemoveDependencyUseCase:
    """Use case para remover dependencia entre historias.

    Verifica existencia da dependencia antes de remover.

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
        self, input_dto: RemoveDependencyInputDTO
    ) -> RemoveDependencyOutputDTO:
        """Executa remocao de dependencia.

        Args:
            input_dto: DTO com story_id e depends_on_id.

        Returns:
            DTO com resultado da operacao.

        Raises:
            ValueError: Se dependencia nao existe.
        """
        story_id = input_dto.story_id
        depends_on_id = input_dto.depends_on_id

        # Check dependency exists before removing
        dependency_exists = await self._uow.dependencies.exists(story_id, depends_on_id)
        if not dependency_exists:
            raise ValueError(
                f"Dependencia de {story_id} para {depends_on_id} nao encontrada"
            )

        # Remove dependency
        await self._uow.dependencies.remove(story_id, depends_on_id)

        return RemoveDependencyOutputDTO(success=True)
