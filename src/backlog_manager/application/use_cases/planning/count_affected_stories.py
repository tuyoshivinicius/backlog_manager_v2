"""Count affected stories use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.reset_planning_dto import (
    CountAffectedStoriesOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class CountAffectedStoriesUseCase:
    """Use case for counting stories that would be affected by a reset.

    Reads stories without modifying any data, returning counts
    for preview in the confirmation dialog.
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, planning_id: int) -> CountAffectedStoriesOutputDTO:
        """Execute the count operation.

        Args:
            planning_id: ID do planning ativo.

        Returns:
            Output DTO with counts of affected stories.
        """
        all_stories = await self._uow.stories.get_all(planning_id)

        total = 0
        with_dates = 0
        with_developer = 0

        for story in all_stories:
            has_dates = (
                story.duration is not None
                or story.start_date is not None
                or story.end_date is not None
            )
            has_dev = story.developer_id is not None

            if has_dates or has_dev:
                total += 1
            if has_dates:
                with_dates += 1
            if has_dev:
                with_developer += 1

        logger.debug(
            "Count affected stories: total=%d, with_dates=%d, with_developer=%d",
            total,
            with_dates,
            with_developer,
        )

        return CountAffectedStoriesOutputDTO(
            total=total,
            with_dates=with_dates,
            with_developer=with_developer,
        )
