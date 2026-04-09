"""Duplicate Story use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.domain.services.story_service import StoryService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class DuplicateStoryUseCase:
    """Use case para duplicar historia existente.

    Cria copia com novo ID e prioridade no fim da fila.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, planning_id: int, story_id: str) -> StoryOutputDTO:
        """Executa duplicacao de historia.

        Args:
            planning_id: ID do planejamento.
            story_id: ID da historia a duplicar.

        Returns:
            DTO com dados da historia duplicada.

        Raises:
            ValueError: Se historia original nao existe.
        """
        # Get original story
        original = await self._uow.stories.get_by_id(planning_id, story_id)
        if original is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        # Create duplicate using domain service
        story_service = StoryService(self._uow.stories)
        duplicate = await story_service.duplicate_story(planning_id, original)

        # Persist
        await self._uow.stories.add(duplicate)

        return StoryOutputDTO.from_entity(duplicate)
