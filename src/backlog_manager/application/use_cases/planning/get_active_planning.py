"""Get active planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.planning_dto import PlanningOutput

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class GetActivePlanningUseCase:
    """Use case for retrieving the active planning."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, last_active_id: int | None) -> PlanningOutput | None:
        """Execute the get active planning operation.

        Args:
            last_active_id: ID of the last active planning, or None.

        Returns:
            Output DTO with planning data, or None if not found.
        """
        if last_active_id is None:
            return None

        planning = await self._uow.plannings.get_by_id(last_active_id)
        if planning is None:
            logger.warning("Active planning id=%d not found", last_active_id)
            return None

        assert planning.id is not None
        logger.info(
            "Active planning retrieved: id=%d, name='%s'", planning.id, planning.name
        )

        return PlanningOutput(
            id=planning.id,
            name=planning.name,
            created_at=planning.created_at,
            updated_at=planning.updated_at,
        )
