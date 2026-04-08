"""Delete planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.domain.exceptions.planning_exceptions import (
    ActivePlanningDeletionException,
)

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class DeletePlanningUseCase:
    """Use case for deleting a planning."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, planning_id: int, active_planning_id: int) -> None:
        """Execute the delete planning operation.

        Args:
            planning_id: ID of the planning to delete.
            active_planning_id: ID of the currently active planning.

        Raises:
            ActivePlanningDeletionException: If attempting to delete the active planning.
        """
        if planning_id == active_planning_id:
            raise ActivePlanningDeletionException(planning_id)

        await self._uow.plannings.delete(planning_id)

        logger.info("Planning deleted: id=%d", planning_id)
