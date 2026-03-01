"""List Stories use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

if TYPE_CHECKING:
    from collections.abc import Sequence

    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class ListStoriesUseCase:
    """Use case para listar historias ordenadas por prioridade."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self) -> Sequence[StoryOutputDTO]:
        """Lista todas as historias ordenadas por prioridade.

        Returns:
            Lista de DTOs de historias ordenadas por prioridade.
        """
        stories = await self._uow.stories.get_all()
        return [StoryOutputDTO.from_entity(story) for story in stories]

    async def execute_by_status(self, status: str) -> Sequence[StoryOutputDTO]:
        """Lista historias filtradas por status.

        Args:
            status: Status para filtrar (BACKLOG, IN_PROGRESS, DONE, BLOCKED).

        Returns:
            Lista de DTOs de historias com o status especificado.
        """
        stories = await self._uow.stories.get_by_status(status)
        return [StoryOutputDTO.from_entity(story) for story in stories]

    async def execute_by_feature(self, feature_id: int) -> Sequence[StoryOutputDTO]:
        """Lista historias de uma feature.

        Args:
            feature_id: ID da feature.

        Returns:
            Lista de DTOs de historias da feature.
        """
        stories = await self._uow.stories.get_by_feature(feature_id)
        return [StoryOutputDTO.from_entity(story) for story in stories]

    async def execute_by_developer(self, developer_id: int) -> Sequence[StoryOutputDTO]:
        """Lista historias alocadas a um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor.

        Returns:
            Lista de DTOs de historias do desenvolvedor.
        """
        stories = await self._uow.stories.get_by_developer(developer_id)
        return [StoryOutputDTO.from_entity(story) for story in stories]
