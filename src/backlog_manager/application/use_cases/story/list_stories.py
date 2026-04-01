"""List Stories use case."""

from __future__ import annotations

import heapq
from collections import defaultdict
from typing import TYPE_CHECKING

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

if TYPE_CHECKING:
    from collections.abc import Sequence

    from backlog_manager.domain.entities.story import Story
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class ListStoriesUseCase:
    """Use case para listar historias ordenadas por onda, dependencias e prioridade."""

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def _enrich_dtos(self, stories: Sequence[Story]) -> list[StoryOutputDTO]:
        """Enriquece DTOs com developer_name, feature_name, wave e dependency_ids.

        Args:
            stories: Sequencia de entidades Story.

        Returns:
            Lista de DTOs enriquecidos.
        """
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

        return self._sort_dtos(result)

    @staticmethod
    def _sort_dtos(dtos: list[StoryOutputDTO]) -> list[StoryOutputDTO]:
        """Ordena DTOs por onda ASC, ordem topologica por dependencias, prioridade como desempate.

        Args:
            dtos: Lista de DTOs enriquecidos.

        Returns:
            Lista de DTOs ordenados por onda, dependencias e prioridade.
        """
        if not dtos:
            return []

        by_wave = ListStoriesUseCase._group_by_wave(dtos)

        sorted_result: list[StoryOutputDTO] = []
        for wave in sorted(by_wave.keys()):
            wave_sorted = ListStoriesUseCase._sort_wave_group(by_wave[wave])
            sorted_result.extend(wave_sorted)

        return sorted_result

    @staticmethod
    def _group_by_wave(
        dtos: list[StoryOutputDTO],
    ) -> dict[int, list[StoryOutputDTO]]:
        """Agrupa DTOs por onda.

        Args:
            dtos: Lista de DTOs enriquecidos.

        Returns:
            Dicionario mapeando wave -> lista de DTOs.
        """
        by_wave: dict[int, list[StoryOutputDTO]] = defaultdict(list)
        for dto in dtos:
            by_wave[dto.wave].append(dto)
        return by_wave

    @staticmethod
    def _build_wave_dependency_graph(
        group: list[StoryOutputDTO],
    ) -> tuple[dict[str, int], dict[str, list[str]], dict[str, StoryOutputDTO]]:
        """Constroi grafo de dependencias para um grupo de onda.

        Args:
            group: Lista de DTOs de uma mesma onda.

        Returns:
            Tupla com (in_degree, dependents, dto_map).
        """
        group_ids = {d.id for d in group}
        dto_map = {d.id: d for d in group}

        in_degree: dict[str, int] = {d.id: 0 for d in group}
        dependents: dict[str, list[str]] = defaultdict(list)

        for d in group:
            for dep_id in d.dependency_ids:
                if dep_id in group_ids:
                    in_degree[d.id] += 1
                    dependents[dep_id].append(d.id)

        return in_degree, dependents, dto_map

    @staticmethod
    def _sort_wave_group(group: list[StoryOutputDTO]) -> list[StoryOutputDTO]:
        """Ordena um grupo de onda topologicamente com fallback para prioridade.

        Args:
            group: Lista de DTOs de uma mesma onda.

        Returns:
            Lista de DTOs ordenados.
        """
        in_degree, dependents, dto_map = (
            ListStoriesUseCase._build_wave_dependency_graph(group)
        )

        heap: list[tuple[int, str]] = [
            (dto_map[sid].priority, sid) for sid in in_degree if in_degree[sid] == 0
        ]
        heapq.heapify(heap)

        wave_sorted: list[StoryOutputDTO] = []

        while heap:
            _, sid = heapq.heappop(heap)
            wave_sorted.append(dto_map[sid])

            for dependent_id in dependents.get(sid, []):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    heapq.heappush(heap, (dto_map[dependent_id].priority, dependent_id))

        if len(wave_sorted) != len(group):
            return sorted(group, key=lambda d: (d.priority, d.id))

        return wave_sorted

    async def execute(self) -> Sequence[StoryOutputDTO]:
        """Lista todas as historias ordenadas por onda, dependencias e prioridade.

        Enriquece DTOs com developer_name, feature_name, wave e dependency_ids.

        Returns:
            Lista de DTOs de historias ordenadas por onda, dependencias e prioridade.
        """
        stories = await self._uow.stories.get_all()
        return await self._enrich_dtos(stories)

    async def execute_by_status(self, status: str) -> Sequence[StoryOutputDTO]:
        """Lista historias filtradas por status.

        Args:
            status: Status para filtrar (BACKLOG, IN_PROGRESS, DONE, BLOCKED).

        Returns:
            Lista de DTOs de historias com o status especificado.
        """
        stories = await self._uow.stories.get_by_status(status)
        return await self._enrich_dtos(stories)

    async def execute_by_feature(self, feature_id: int) -> Sequence[StoryOutputDTO]:
        """Lista historias de uma feature.

        Args:
            feature_id: ID da feature.

        Returns:
            Lista de DTOs de historias da feature.
        """
        stories = await self._uow.stories.get_by_feature(feature_id)
        return await self._enrich_dtos(stories)

    async def execute_by_developer(self, developer_id: int) -> Sequence[StoryOutputDTO]:
        """Lista historias alocadas a um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor.

        Returns:
            Lista de DTOs de historias do desenvolvedor.
        """
        stories = await self._uow.stories.get_by_developer(developer_id)
        return await self._enrich_dtos(stories)
