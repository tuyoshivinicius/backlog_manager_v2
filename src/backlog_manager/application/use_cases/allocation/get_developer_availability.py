"""Use case para consultar disponibilidade de desenvolvedores."""

from __future__ import annotations

import logging
import random
from collections.abc import Sequence
from datetime import date
from typing import TYPE_CHECKING

from backlog_manager.application.dto.allocation.developer_availability_dto import (
    BlockingStoryDTO,
    DeveloperAvailabilityDTO,
)
from backlog_manager.application.dto.allocation.get_developer_availability_dto import (
    GetDeveloperAvailabilityInputDTO,
    GetDeveloperAvailabilityOutputDTO,
)
from backlog_manager.domain.services.allocation_service import (
    AllocationConfig,
    AllocationCriteria,
    AllocationService,
)
from backlog_manager.domain.services.scheduling_service import SchedulingService
from backlog_manager.domain.value_objects import (
    BRAZILIAN_HOLIDAYS_2026_2028,
    StoryStatus,
)

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Developer, Story
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


def _find_blocking_stories(
    dev_stories: list[Story],
    target_story: Story,
) -> list[BlockingStoryDTO]:
    """Find stories that block a developer from being assigned.

    Args:
        dev_stories: Stories already allocated to the developer.
        target_story: Story to check overlap against.

    Returns:
        List of blocking story DTOs.
    """
    blocking: list[BlockingStoryDTO] = []
    for s in dev_stories:
        if (
            s.start_date is None
            or s.end_date is None
            or s.status == StoryStatus.CONCLUIDO
        ):
            continue
        if AllocationService._has_period_overlap(target_story, s):
            blocking.append(
                BlockingStoryDTO(
                    story_id=s.id,
                    story_name=s.name,
                    start_date=s.start_date,
                    end_date=s.end_date,
                )
            )
    return blocking


class GetDeveloperAvailabilityUseCase:
    """Consulta disponibilidade de desenvolvedores para alocacao manual.

    Dada uma historia e uma data candidata, retorna a lista de
    desenvolvedores com status de disponibilidade e recomendacao.
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Inicializa o use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(
        self, input_dto: GetDeveloperAvailabilityInputDTO, planning_id: int
    ) -> GetDeveloperAvailabilityOutputDTO:
        """Executa consulta de disponibilidade.

        Args:
            input_dto: Dados de entrada com story_id, data candidata, velocity e criterio.
            planning_id: ID do planning ativo.

        Returns:
            Lista de desenvolvedores com disponibilidade e recomendacao.

        Raises:
            ValueError: Se historia nao encontrada ou sem story points.
        """
        story = await self._uow.stories.get_by_id(planning_id, input_dto.story_id)
        if story is None:
            raise ValueError(f"Historia {input_dto.story_id} nao encontrada")

        if story.story_points is None:
            raise ValueError("Historia sem story points definidos")

        developers = await self._uow.developers.get_all()
        all_stories = list(await self._uow.stories.get_all(planning_id))
        all_deps = await self._uow.dependencies.get_all_dependencies(planning_id)

        dependency_graph = self._build_dependency_graph(all_deps)

        target_story, story_start, story_end = self._prepare_target_story(
            story, input_dto, all_stories, dependency_graph
        )

        story_map: dict[str, Story] = {s.id: s for s in all_stories}
        story_map[target_story.id] = target_story

        dev_availability, free_devs, dev_count = self._classify_developers(
            developers, all_stories, target_story, input_dto.story_id
        )

        recommended_id = self._determine_recommendation(
            free_devs, target_story, dev_count, dependency_graph, story_map, input_dto
        )

        result_devs = self._build_sorted_result(dev_availability, recommended_id)

        logger.info(
            "Developer availability for %s: %d free, %d occupied",
            input_dto.story_id,
            len(free_devs),
            len(dev_availability) - len(free_devs),
        )

        return GetDeveloperAvailabilityOutputDTO(
            developers=result_devs,
            recommended_developer_id=recommended_id,
            story_start_date=story_start,
            story_end_date=story_end,
        )

    @staticmethod
    def _build_dependency_graph(
        all_deps: Sequence[tuple[str, str]],
    ) -> dict[str, list[str]]:
        """Build dependency graph from dependency pairs.

        Args:
            all_deps: List of (story_id, depends_on_id) tuples.

        Returns:
            Dependency graph mapping story_id to list of dependency IDs.
        """
        dependency_graph: dict[str, list[str]] = {}
        for story_id, depends_on_id in all_deps:
            dependency_graph.setdefault(story_id, []).append(depends_on_id)
        return dependency_graph

    @staticmethod
    def _prepare_target_story(
        story: Story,
        input_dto: GetDeveloperAvailabilityInputDTO,
        all_stories: list[Story],
        dependency_graph: dict[str, list[str]],
    ) -> tuple[Story, date, date]:
        """Recalculate target story dates and create temporary copy.

        Args:
            story: Original story entity.
            input_dto: Input DTO with candidate start date and velocity.
            all_stories: All stories for dependency lookup.
            dependency_graph: Dependency graph.

        Returns:
            Tuple of (target_story_copy, start_date, end_date).
        """
        dep_end_dates: list[date] = []
        for dep_id in dependency_graph.get(input_dto.story_id, []):
            dep_story = next((s for s in all_stories if s.id == dep_id), None)
            if dep_story and dep_story.end_date:
                dep_end_dates.append(dep_story.end_date)

        story_start, story_end, _ = SchedulingService.calculate_story_dates(
            story=story,
            velocity=input_dto.velocity,
            start_date=input_dto.candidate_start_date,
            dependency_end_dates=dep_end_dates,
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )

        from dataclasses import replace

        target_story = replace(story, start_date=story_start, end_date=story_end)
        return target_story, story_start, story_end

    @staticmethod
    def _classify_developers(
        developers: Sequence[Developer],
        all_stories: list[Story],
        target_story: Story,
        excluded_story_id: str,
    ) -> tuple[list[DeveloperAvailabilityDTO], list[Developer], dict[int, int]]:
        """Classify developers by availability against target story.

        Args:
            developers: All developers.
            all_stories: All stories for allocation lookup.
            target_story: Story with recalculated dates.
            excluded_story_id: Story ID to exclude from dev's story list.

        Returns:
            Tuple of (availability DTOs, free developers, dev story counts).
        """
        dev_availability: list[DeveloperAvailabilityDTO] = []
        free_devs: list[Developer] = []
        dev_count: dict[int, int] = {}

        for dev in developers:
            if dev.id is None:
                continue

            dev_stories = [
                s
                for s in all_stories
                if s.developer_id == dev.id and s.id != excluded_story_id
            ]
            dev_count[dev.id] = len(dev_stories)

            blocking = _find_blocking_stories(dev_stories, target_story)

            is_available = len(blocking) == 0
            if is_available:
                free_devs.append(dev)

            dev_availability.append(
                DeveloperAvailabilityDTO(
                    developer_id=dev.id,
                    developer_name=dev.name,
                    is_available=is_available,
                    is_recommended=False,
                    blocking_stories=blocking,
                    story_count=len(dev_stories),
                )
            )

        return dev_availability, free_devs, dev_count

    @staticmethod
    def _determine_recommendation(
        free_devs: list[Developer],
        target_story: Story,
        dev_count: dict[int, int],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        input_dto: GetDeveloperAvailabilityInputDTO,
    ) -> int | None:
        """Determine recommended developer from free developers.

        Args:
            free_devs: List of available developers.
            target_story: Story with recalculated dates.
            dev_count: Map of developer ID to story count.
            dependency_graph: Dependency graph.
            story_map: Map of story ID to story.
            input_dto: Input DTO with allocation criteria.

        Returns:
            Recommended developer ID or None.
        """
        if not free_devs:
            return None

        criteria = AllocationCriteria(input_dto.allocation_criteria.lower())
        config = AllocationConfig(
            velocity=input_dto.velocity,
            project_start_date=input_dto.candidate_start_date,
            allocation_criteria=criteria,
        )
        rng = random.Random(42)
        recommended = AllocationService._select_developer(
            developers=free_devs,
            story=target_story,
            dev_count=dev_count,
            dependency_graph=dependency_graph,
            story_map=story_map,
            config=config,
            rng=rng,
        )
        if recommended and recommended.id is not None:
            return recommended.id
        return None

    @staticmethod
    def _build_sorted_result(
        dev_availability: list[DeveloperAvailabilityDTO],
        recommended_id: int | None,
    ) -> list[DeveloperAvailabilityDTO]:
        """Mark recommended developer and sort results.

        Args:
            dev_availability: List of availability DTOs.
            recommended_id: ID of recommended developer.

        Returns:
            Sorted list with recommendation marked.
        """
        result_devs: list[DeveloperAvailabilityDTO] = []
        for dto in dev_availability:
            if dto.developer_id == recommended_id:
                dto = dto.model_copy(update={"is_recommended": True})
            result_devs.append(dto)

        result_devs.sort(key=lambda d: (not d.is_available, d.story_count))
        return result_devs
