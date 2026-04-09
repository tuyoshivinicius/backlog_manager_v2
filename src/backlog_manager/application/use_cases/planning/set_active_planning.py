"""Set active planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.planning_dto import PlanningOutput

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class SetActivePlanningUseCase:
    """Use case for setting the active planning."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, planning_id: int) -> PlanningOutput:
        """Execute the set active planning operation.

        Args:
            planning_id: ID of the planning to activate.

        Returns:
            Output DTO with activated planning data.

        Raises:
            ValueError: If planning not found.
        """
        planning = await self._uow.plannings.get_by_id(planning_id)
        if planning is None:
            raise ValueError(f"Planejamento com id={planning_id} nao encontrado")

        assert planning.id is not None
        logger.info("Active planning set: id=%d, name='%s'", planning.id, planning.name)

        return PlanningOutput(
            id=planning.id,
            name=planning.name,
            created_at=planning.created_at,
            updated_at=planning.updated_at,
        )
