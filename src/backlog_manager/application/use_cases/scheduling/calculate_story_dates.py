"""Calculate story dates use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.scheduling.calculate_story_dates_dto import (
    CalculateStoryDatesInputDTO,
    CalculateStoryDatesOutputDTO,
)
from backlog_manager.domain.services import SchedulingService
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork


class CalculateStoryDatesUseCase:
    """Use case for calculating story dates.

    Calculates and persists start date, end date, and duration for
    a specific story, considering its dependencies.

    Example:
        >>> async with SQLiteUnitOfWork() as uow:
        ...     use_case = CalculateStoryDatesUseCase(uow)
        ...     result = await use_case.execute(
        ...         CalculateStoryDatesInputDTO(
        ...             story_id="FEAT-001",
        ...             velocity=2.0,
        ...             project_start_date=date(2026, 3, 2)
        ...         )
        ...     )
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(
        self, input_dto: CalculateStoryDatesInputDTO, planning_id: int
    ) -> CalculateStoryDatesOutputDTO:
        """Execute story dates calculation.

        Args:
            input_dto: Input containing story ID, velocity, and project start date.
            planning_id: ID do planning ativo.

        Returns:
            Output DTO with calculated dates.

        Raises:
            ValueError: If story not found.
        """
        # Get story
        story = await self._uow.stories.get_by_id(planning_id, input_dto.story_id)
        if story is None:
            raise ValueError(f"Historia {input_dto.story_id} nao encontrada")

        # Get dependencies
        dep_ids = await self._uow.dependencies.get_dependencies(
            planning_id, input_dto.story_id
        )

        # Collect end dates from dependencies
        dependency_end_dates = []
        for dep_id in dep_ids:
            dep_story = await self._uow.stories.get_by_id(planning_id, dep_id)
            if dep_story is not None and dep_story.end_date is not None:
                dependency_end_dates.append(dep_story.end_date)
            else:
                # Fallback to project start date
                dependency_end_dates.append(input_dto.project_start_date)

        # Calculate dates
        start_date, end_date, duration = SchedulingService.calculate_story_dates(
            story=story,
            velocity=input_dto.velocity,
            start_date=input_dto.project_start_date,
            dependency_end_dates=dependency_end_dates,
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )

        # Update story
        # Use object.__setattr__ since Story is a frozen dataclass
        object.__setattr__(story, "start_date", start_date)
        object.__setattr__(story, "end_date", end_date)
        object.__setattr__(story, "duration", duration)

        await self._uow.stories.update(story)

        return CalculateStoryDatesOutputDTO(
            story_id=input_dto.story_id,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
        )
