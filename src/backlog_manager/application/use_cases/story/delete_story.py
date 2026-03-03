"""Delete Story use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class DeleteStoryUseCase:
    """Use case para deletar historia.

    Remove historia e todas suas dependencias associadas.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, story_id: str) -> None:
        """Executa delecao de historia.

        Args:
            story_id: ID da historia a deletar.

        Raises:
            ValueError: Se historia nao existe.
        """
        # Validate story exists
        story = await self._uow.stories.get_by_id(story_id)
        if story is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        # Remove all dependencies involving this story
        await self._uow.dependencies.remove_all_for_story(story_id)

        # Delete the story
        await self._uow.stories.delete(story_id)
