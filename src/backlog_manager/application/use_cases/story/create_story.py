"""Create Story use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.create_story_dto import CreateStoryInputDTO
from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.domain.services.story_service import StoryService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class CreateStoryUseCase:
    """Use case para criar nova historia.

    Gera ID automatico no formato COMPONENTE-NNN.
    Atribui prioridade ao fim da fila.
    Status inicial: BACKLOG.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(
        self, planning_id: int, input_dto: CreateStoryInputDTO
    ) -> StoryOutputDTO:
        """Executa criacao de historia.

        Args:
            planning_id: ID do planejamento.
            input_dto: Dados de entrada validados.

        Returns:
            DTO com dados da historia criada.

        Raises:
            ValueError: Se feature_id informado nao existe.
        """
        # Validate feature exists if provided
        if input_dto.feature_id is not None:
            feature_exists = await self._uow.features.exists(input_dto.feature_id)
            if not feature_exists:
                raise ValueError(
                    f"Feature com ID {input_dto.feature_id} nao encontrada"
                )

        # Create story using domain service
        story_service = StoryService(self._uow.stories)
        story = await story_service.create_story(
            planning_id=planning_id,
            component=input_dto.component,
            name=input_dto.name,
            story_points=input_dto.story_points,
            feature_id=input_dto.feature_id,
        )

        # Persist
        await self._uow.stories.add(story)

        return StoryOutputDTO.from_entity(story)
