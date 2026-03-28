"""Assign Developer use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class AssignDeveloperUseCase:
    """Use case para alocar/desalocar desenvolvedor em historia."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def assign(self, story_id: str, developer_id: int) -> StoryOutputDTO:
        """Aloca desenvolvedor a uma historia.

        Args:
            story_id: ID da historia.
            developer_id: ID do desenvolvedor.

        Returns:
            DTO com dados da historia atualizada.

        Raises:
            ValueError: Se historia ou desenvolvedor nao existe.
        """
        # Validate story exists
        story = await self._uow.stories.get_by_id(story_id)
        if story is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        # Validate developer exists
        developer_exists = await self._uow.developers.exists(developer_id)
        if not developer_exists:
            raise ValueError(f"Desenvolvedor com ID {developer_id} nao encontrado")

        # Assign developer
        story.developer_id = developer_id

        # Persist
        await self._uow.stories.update(story)

        return StoryOutputDTO.from_entity(story)

    async def unassign(self, story_id: str) -> StoryOutputDTO:
        """Remove alocacao de desenvolvedor de uma historia.

        Args:
            story_id: ID da historia.

        Returns:
            DTO com dados da historia atualizada.

        Raises:
            ValueError: Se historia nao existe.
        """
        # Validate story exists
        story = await self._uow.stories.get_by_id(story_id)
        if story is None:
            raise ValueError(f"Historia {story_id} nao encontrada")

        # Remove developer assignment
        story.developer_id = None

        # Persist
        await self._uow.stories.update(story)

        return StoryOutputDTO.from_entity(story)
