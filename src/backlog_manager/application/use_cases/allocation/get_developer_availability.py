"""Use case para consultar disponibilidade de desenvolvedores."""

from __future__ import annotations

import logging
import random
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
        self, input_dto: GetDeveloperAvailabilityInputDTO
    ) -> GetDeveloperAvailabilityOutputDTO:
        """Executa consulta de disponibilidade.

        Args:
            input_dto: Dados de entrada com story_id, data candidata, velocity e criterio.

        Returns:
            Lista de desenvolvedores com disponibilidade e recomendacao.

        Raises:
            ValueError: Se historia nao encontrada ou sem story points.
        """
        story = await self._uow.stories.get_by_id(input_dto.story_id)
        if story is None:
            raise ValueError(f"Historia {input_dto.story_id} nao encontrada")

        if story.story_points is None:
            raise ValueError("Historia sem story points definidos")

        developers = await self._uow.developers.get_all()
        all_stories = list(await self._uow.stories.get_all())
        all_deps = await self._uow.dependencies.get_all_dependencies()

        # Build dependency graph: story_id -> [depends_on_ids]
        dependency_graph: dict[str, list[str]] = {}
        for story_id, depends_on_id in all_deps:
            dependency_graph.setdefault(story_id, []).append(depends_on_id)

        # Get dependency end dates for this story
        dep_end_dates: list[date] = []
        for dep_id in dependency_graph.get(input_dto.story_id, []):
            dep_story = next((s for s in all_stories if s.id == dep_id), None)
            if dep_story and dep_story.end_date:
                dep_end_dates.append(dep_story.end_date)

        # Recalculate dates for the target story with the candidate start date
        holidays = BRAZILIAN_HOLIDAYS_2026_2028
        story_start, story_end, _ = SchedulingService.calculate_story_dates(
            story=story,
            velocity=input_dto.velocity,
            start_date=input_dto.candidate_start_date,
            dependency_end_dates=dep_end_dates,
            holidays=holidays,
        )

        # Build story map for _select_developer
        story_map: dict[str, Story] = {s.id: s for s in all_stories}

        # Create a temporary story copy with recalculated dates
        # to check overlap against
        from dataclasses import replace

        target_story = replace(
            story,
            start_date=story_start,
            end_date=story_end,
        )
        story_map[target_story.id] = target_story

        # Classify developers
        dev_availability: list[DeveloperAvailabilityDTO] = []
        free_devs: list[Developer] = []
        dev_count: dict[int, int] = {}

        for dev in developers:
            if dev.id is None:
                continue

            # Count stories allocated to this dev
            dev_stories = [
                s
                for s in all_stories
                if s.developer_id == dev.id and s.id != input_dto.story_id
            ]
            dev_count[dev.id] = len(dev_stories)

            # Check overlap with each of dev's stories
            blocking: list[BlockingStoryDTO] = []
            for s in dev_stories:
                if (
                    s.start_date is not None
                    and s.end_date is not None
                    and s.status != StoryStatus.CONCLUIDO
                    and AllocationService._has_period_overlap(target_story, s)
                ):
                    blocking.append(
                        BlockingStoryDTO(
                            story_id=s.id,
                            story_name=s.name,
                            start_date=s.start_date,
                            end_date=s.end_date,
                        )
                    )

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

        # Get recommendation from domain service
        recommended_id: int | None = None
        if free_devs:
            criteria = AllocationCriteria(input_dto.allocation_criteria.lower())
            config = AllocationConfig(
                velocity=input_dto.velocity,
                project_start_date=input_dto.candidate_start_date,
                allocation_criteria=criteria,
            )
            rng = random.Random(42)  # Deterministic for consistency
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
                recommended_id = recommended.id

        # Mark recommended and sort (free first, then occupied)
        result_devs: list[DeveloperAvailabilityDTO] = []
        for dto in dev_availability:
            if dto.developer_id == recommended_id:
                dto = dto.model_copy(update={"is_recommended": True})
            result_devs.append(dto)

        result_devs.sort(key=lambda d: (not d.is_available, d.story_count))

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
