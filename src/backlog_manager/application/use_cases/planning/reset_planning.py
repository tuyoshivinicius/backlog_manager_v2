"""Reset planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.reset_planning_dto import (
    ResetPlanningInputDTO,
    ResetPlanningOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class ResetPlanningUseCase:
    """Use case for resetting all calculated planning fields.

    Atomically clears duration, start_date, end_date, and developer_id
    from all affected stories while preserving user data and dependencies.
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, input_dto: ResetPlanningInputDTO) -> ResetPlanningOutputDTO:
        """Execute the reset planning operation.

        Args:
            input_dto: Input DTO (no parameters needed).

        Returns:
            Output DTO with reset operation results.
        """
        all_stories = await self._uow.stories.get_all()

        # Filter stories with any calculated field filled
        affected_stories = [
            s
            for s in all_stories
            if s.duration is not None
            or s.start_date is not None
            or s.end_date is not None
            or s.developer_id is not None
        ]

        if not affected_stories:
            return ResetPlanningOutputDTO(
                success=True,
                stories_reset=0,
                stories_with_dates_cleared=0,
                stories_with_developer_cleared=0,
            )

        stories_with_dates = 0
        stories_with_developer = 0

        for story in affected_stories:
            has_dates = (
                story.duration is not None
                or story.start_date is not None
                or story.end_date is not None
            )
            has_developer = story.developer_id is not None

            if has_dates:
                stories_with_dates += 1
            if has_developer:
                stories_with_developer += 1

            # Clear calculated fields using object.__setattr__() (R-001)
            object.__setattr__(story, "duration", None)
            object.__setattr__(story, "start_date", None)
            object.__setattr__(story, "end_date", None)
            object.__setattr__(story, "developer_id", None)

            await self._uow.stories.update(story)

        logger.info("Reset planning completed: %d stories reset", len(affected_stories))

        return ResetPlanningOutputDTO(
            success=True,
            stories_reset=len(affected_stories),
            stories_with_dates_cleared=stories_with_dates,
            stories_with_developer_cleared=stories_with_developer,
        )
