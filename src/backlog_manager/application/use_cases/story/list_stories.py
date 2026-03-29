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

        Enriquece DTOs com developer_name, feature_name, wave e dependency_ids.

        Returns:
            Lista de DTOs de historias ordenadas por prioridade.
        """
        stories = await self._uow.stories.get_all()
        developers = await self._uow.developers.get_all()
        features = await self._uow.features.get_all()

        dev_map = {d.id: d.name for d in developers if d.id is not None}
        feat_map: dict[int, tuple[str, int]] = {
            f.id: (f.name, f.wave) for f in features if f.id is not None
        }

        result: list[StoryOutputDTO] = []
        for story in stories:
            dto = StoryOutputDTO.from_entity(story)

            if story.developer_id is not None:
                dto.developer_name = dev_map.get(story.developer_id)

            if story.feature_id is not None:
                feat_info = feat_map.get(story.feature_id)
                if feat_info:
                    dto.feature_name = feat_info[0]
                    dto.wave = feat_info[1]

            deps = await self._uow.dependencies.get_dependencies(story.id)
            dto.dependency_ids = list(deps)

            result.append(dto)

        return result

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
