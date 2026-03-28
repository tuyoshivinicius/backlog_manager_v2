"""Move Priority use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.domain.services.story_service import StoryService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class MovePriorityUseCase:
    """Use case para mover prioridade de historia.

    Move historia para cima (menor prioridade) ou para baixo (maior prioridade).
    Troca prioridade com historia adjacente.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def move_up(self, story_id: str) -> StoryOutputDTO:
        """Move historia para cima (menor prioridade = mais prioritaria).

        Args:
            story_id: ID da historia a mover.

        Returns:
            DTO com dados da historia atualizada.

        Raises:
            ValueError: Se historia nao existe ou ja esta no topo.
        """
        story = await self._uow.stories.get_by_id(story_id)
        if story is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        story_service = StoryService(self._uow.stories)

        can_move = await story_service.validate_can_move_up(story)
        if not can_move:
            raise ValueError(f"Historia {story_id} ja esta no topo do backlog")

        # Get adjacent story
        adjacent = await self._uow.stories.get_by_priority(story.priority - 1)
        if adjacent is None:
            raise ValueError("Historia adjacente nao encontrada")

        # Swap priorities
        await story_service.swap_priorities(story, adjacent)

        # Persist both
        await self._uow.stories.update(story)
        await self._uow.stories.update(adjacent)

        return StoryOutputDTO.from_entity(story)

    async def move_down(self, story_id: str) -> StoryOutputDTO:
        """Move historia para baixo (maior prioridade = menos prioritaria).

        Args:
            story_id: ID da historia a mover.

        Returns:
            DTO com dados da historia atualizada.

        Raises:
            ValueError: Se historia nao existe ou ja esta no fim.
        """
        story = await self._uow.stories.get_by_id(story_id)
        if story is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        story_service = StoryService(self._uow.stories)

        can_move = await story_service.validate_can_move_down(story)
        if not can_move:
            raise ValueError(f"Historia {story_id} ja esta no fim do backlog")

        # Get adjacent story
        adjacent = await self._uow.stories.get_by_priority(story.priority + 1)
        if adjacent is None:
            raise ValueError("Historia adjacente nao encontrada")

        # Swap priorities
        await story_service.swap_priorities(story, adjacent)

        # Persist both
        await self._uow.stories.update(story)
        await self._uow.stories.update(adjacent)

        return StoryOutputDTO.from_entity(story)
