"""List plannings use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.planning_dto import PlanningListItem

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class ListPlanningsUseCase:
    """Use case for listing all plannings with story counts."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self) -> list[PlanningListItem]:
        """Execute the list plannings operation.

        Returns:
            List of planning items with story counts.
        """
        plannings = await self._uow.plannings.get_all()
        result: list[PlanningListItem] = []

        for planning in plannings:
            assert planning.id is not None
            story_count = await self._uow.plannings.count_stories(planning.id)
            result.append(
                PlanningListItem(
                    id=planning.id,
                    name=planning.name,
                    story_count=story_count,
                    updated_at=planning.updated_at,
                )
            )

        logger.info("Listed %d plannings", len(result))
        return result
