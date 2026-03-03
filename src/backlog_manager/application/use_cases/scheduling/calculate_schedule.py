"""Calculate full schedule use case."""

from __future__ import annotations

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
        self, input_dto: CalculateScheduleInputDTO
    ) -> CalculateScheduleOutputDTO:
        """Execute full schedule calculation.

        Args:
            input_dto: Input containing velocity and project start date.

        Returns:
            Output DTO with calculation results and warnings.

        Raises:
            CyclicDependencyException: If cycle detected in dependencies.
        """
        warnings: list[str] = []

        # Get all stories
        all_stories = await self._uow.stories.get_all()

        # Filter eligible stories
        eligible_stories = []
        for story in all_stories:
            # Check status
            if story.status != StoryStatus.BACKLOG:
                continue

            # Check story points
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

            # Skip if already has dates and not recalculating all
            if (
                not input_dto.recalculate_all
                and story.start_date is not None
                and story.end_date is not None
            ):
                continue

            eligible_stories.append(story)

        # Check for empty backlog
        if not eligible_stories:
            warnings.append("Nenhuma historia elegivel encontrada no backlog")
            return CalculateScheduleOutputDTO(
                success=True,
                stories_processed=0,
                stories_updated=0,
                warnings=warnings,
            )

        # Get all dependencies
        all_deps = await self._uow.dependencies.get_all_dependencies()

        # Build dependency graph
        graph = DependencyService.build_graph(all_deps)

        # Topological sort (will raise CyclicDependencyException if cycle detected)
        sorted_stories = SchedulingService.topological_sort(eligible_stories, graph)

        # Calculate dates for each story in topological order
        story_end_dates: dict[str, date] = {}  # story_id -> end_date
        stories_updated = 0

        for story in sorted_stories:
            # Get end dates of dependencies
            dep_ids = graph.get(story.id, [])
            dependency_end_dates = []

            for dep_id in dep_ids:
                if dep_id in story_end_dates:
                    end_date = story_end_dates[dep_id]
                    if end_date is not None:
                        dependency_end_dates.append(end_date)
                else:
                    # Dependency not in current batch - get from DB
                    dep_story = await self._uow.stories.get_by_id(dep_id)
                    if dep_story is not None and dep_story.end_date is not None:
                        dependency_end_dates.append(dep_story.end_date)
                        story_end_dates[dep_id] = dep_story.end_date
                    else:
                        # Fallback to project start date
                        warnings.append(
                            f"Dependencia {dep_id} sem data: "
                            f"usando project_start_date como fallback"
                        )
                        dependency_end_dates.append(input_dto.start_date)
                        story_end_dates[dep_id] = input_dto.start_date

            # Calculate dates
            start_date, end_date, duration = SchedulingService.calculate_story_dates(
                story=story,
                velocity=input_dto.velocity,
                start_date=input_dto.start_date,
                dependency_end_dates=dependency_end_dates,
                holidays=BRAZILIAN_HOLIDAYS_2026_2028,
            )

            # Update story
            object.__setattr__(story, "start_date", start_date)
            object.__setattr__(story, "end_date", end_date)
            object.__setattr__(story, "duration", duration)

            await self._uow.stories.update(story)

            # Track end date for dependents
            story_end_dates[story.id] = end_date
            stories_updated += 1

        return CalculateScheduleOutputDTO(
            success=True,
            stories_processed=len(sorted_stories),
            stories_updated=stories_updated,
            warnings=warnings,
        )
