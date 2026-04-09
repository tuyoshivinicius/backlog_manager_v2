"""Calculate full schedule use case."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import TYPE_CHECKING

from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
    CalculateScheduleInputDTO,
    CalculateScheduleOutputDTO,
)
from backlog_manager.domain.services import DependencyService, SchedulingService
from backlog_manager.domain.value_objects import (
    BRAZILIAN_HOLIDAYS_2026_2028,
    StoryStatus,
)

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Story
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork


class CalculateScheduleUseCase:
    """Use case for calculating the full backlog schedule.

    Calculates start date, end date, and duration for all eligible
    stories in the backlog, respecting dependencies and workdays.

    Example:
        >>> async with SQLiteUnitOfWork() as uow:
        ...     use_case = CalculateScheduleUseCase(uow)
        ...     result = await use_case.execute(
        ...         CalculateScheduleInputDTO(
        ...             velocity=2.0,
        ...             start_date=date(2026, 3, 2)
        ...         )
        ...     )
        ...     print(f"Updated {result.stories_updated} stories")
    """

    VALID_STORY_POINTS = {3, 5, 8, 13}

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(
        self, input_dto: CalculateScheduleInputDTO, planning_id: int
    ) -> CalculateScheduleOutputDTO:
        """Execute full schedule calculation.

        Args:
            input_dto: Input containing velocity and project start date.
            planning_id: ID do planning ativo.

        Returns:
            Output DTO with calculation results and warnings.

        Raises:
            CyclicDependencyException: If cycle detected in dependencies.
        """
        warnings: list[str] = []

        all_stories = await self._uow.stories.get_all(planning_id)
        eligible_stories = self._filter_eligible_stories(
            all_stories, input_dto.recalculate_all, warnings
        )

        if not eligible_stories:
            warnings.append("Nenhuma historia elegivel encontrada no backlog")
            return CalculateScheduleOutputDTO(
                success=True,
                stories_processed=0,
                stories_updated=0,
                warnings=warnings,
            )

        all_deps = await self._uow.dependencies.get_all_dependencies(planning_id)
        graph = DependencyService.build_graph(all_deps)
        sorted_stories = SchedulingService.topological_sort(eligible_stories, graph)

        stories_updated = await self._calculate_and_update_dates(
            planning_id, sorted_stories, graph, input_dto, warnings
        )

        return CalculateScheduleOutputDTO(
            success=True,
            stories_processed=len(sorted_stories),
            stories_updated=stories_updated,
            warnings=warnings,
        )

    def _filter_eligible_stories(
        self,
        all_stories: Sequence[Story],
        recalculate_all: bool,
        warnings: list[str],
    ) -> list[Story]:
        """Filter stories eligible for scheduling.

        Args:
            all_stories: All stories from repository.
            recalculate_all: Whether to recalculate stories that already have dates.
            warnings: List to accumulate warnings.

        Returns:
            List of eligible stories.
        """
        eligible_stories = []
        for story in all_stories:
            if story.status != StoryStatus.BACKLOG:
                continue

            sp_value = (
                story.story_points.value
                if hasattr(story.story_points, "value")
                else story.story_points
            )
            if sp_value not in self.VALID_STORY_POINTS:
                warnings.append(
                    f"Historia {story.id} ignorada: story_points invalido ou ausente"
                )
                continue

            if (
                not recalculate_all
                and story.start_date is not None
                and story.end_date is not None
            ):
                continue

            eligible_stories.append(story)
        return eligible_stories

    async def _resolve_dependency_end_dates(
        self,
        planning_id: int,
        dep_ids: list[str],
        story_end_dates: dict[str, date],
        fallback_date: date,
        warnings: list[str],
    ) -> list[date]:
        """Resolve end dates for a story's dependencies.

        Args:
            planning_id: ID do planning ativo.
            dep_ids: List of dependency story IDs.
            story_end_dates: Cache of already-calculated end dates.
            fallback_date: Date to use when dependency has no end date.
            warnings: List to accumulate warnings.

        Returns:
            List of dependency end dates.
        """
        dependency_end_dates: list[date] = []
        for dep_id in dep_ids:
            if dep_id in story_end_dates:
                end_date = story_end_dates[dep_id]
                if end_date is not None:
                    dependency_end_dates.append(end_date)
                continue

            dep_story = await self._uow.stories.get_by_id(planning_id, dep_id)
            if dep_story is not None and dep_story.end_date is not None:
                dependency_end_dates.append(dep_story.end_date)
                story_end_dates[dep_id] = dep_story.end_date
            else:
                warnings.append(
                    f"Dependencia {dep_id} sem data: "
                    f"usando project_start_date como fallback"
                )
                dependency_end_dates.append(fallback_date)
                story_end_dates[dep_id] = fallback_date
        return dependency_end_dates

    async def _calculate_and_update_dates(
        self,
        planning_id: int,
        sorted_stories: list[Story],
        graph: dict[str, list[str]],
        input_dto: CalculateScheduleInputDTO,
        warnings: list[str],
    ) -> int:
        """Calculate dates for sorted stories and persist updates.

        Args:
            planning_id: ID do planning ativo.
            sorted_stories: Stories in topological order.
            graph: Dependency graph.
            input_dto: Input with velocity and start date.
            warnings: List to accumulate warnings.

        Returns:
            Number of stories updated.
        """
        story_end_dates: dict[str, date] = {}
        stories_updated = 0

        for story in sorted_stories:
            dep_ids = graph.get(story.id, [])
            dependency_end_dates = await self._resolve_dependency_end_dates(
                planning_id, dep_ids, story_end_dates, input_dto.start_date, warnings
            )

            start_date, end_date, duration = SchedulingService.calculate_story_dates(
                story=story,
                velocity=input_dto.velocity,
                start_date=input_dto.start_date,
                dependency_end_dates=dependency_end_dates,
                holidays=BRAZILIAN_HOLIDAYS_2026_2028,
            )

            object.__setattr__(story, "start_date", start_date)
            object.__setattr__(story, "end_date", end_date)
            object.__setattr__(story, "duration", duration)

            await self._uow.stories.update(story)

            story_end_dates[story.id] = end_date
            stories_updated += 1

        return stories_updated
