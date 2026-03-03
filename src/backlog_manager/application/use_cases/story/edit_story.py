"""Edit Story use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.edit_story_dto import EditStoryInputDTO
from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class EditStoryUseCase:
    """Use case para editar historia existente.

    Valida existencia e atualiza apenas campos fornecidos.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(self, input_dto: EditStoryInputDTO) -> StoryOutputDTO:
        """Executa edicao de historia.

        Args:
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados da historia atualizada.

        Raises:
            ValueError: Se historia nao existe ou feature_id invalido.
        """
        # Get existing story
        story = await self._uow.stories.get_by_id(input_dto.story_id)
        if story is None:
            raise ValueError(f"Historia {input_dto.story_id} nao encontrada")

        # Validate feature exists if changing
        if input_dto.feature_id is not None:
            feature_exists = await self._uow.features.exists(input_dto.feature_id)
            if not feature_exists:
                raise ValueError(
                    f"Feature com ID {input_dto.feature_id} nao encontrada"
                )

        # Update fields that were provided
        if input_dto.name is not None:
            story.name = input_dto.name

        if input_dto.story_points is not None:
            story.story_points = StoryPoint(input_dto.story_points)

        if input_dto.status is not None:
            story.status = StoryStatus(input_dto.status)

        if input_dto.duration is not None:
            story.duration = input_dto.duration

        if input_dto.start_date is not None:
            story.start_date = input_dto.start_date

        if input_dto.end_date is not None:
            story.end_date = input_dto.end_date

        if input_dto.feature_id is not None:
            story.feature_id = input_dto.feature_id

        # Persist changes
        await self._uow.stories.update(story)

        return StoryOutputDTO.from_entity(story)
