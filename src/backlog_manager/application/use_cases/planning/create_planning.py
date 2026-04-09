"""Create planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.planning_dto import (
    CreatePlanningInput,
    PlanningOutput,
)
from backlog_manager.domain.entities.planning import Planning
from backlog_manager.domain.exceptions.planning_exceptions import (
    DuplicatePlanningNameException,
)

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class CreatePlanningUseCase:
    """Use case for creating a new planning."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, input_dto: CreatePlanningInput) -> PlanningOutput:
        """Execute the create planning operation.

        Args:
            input_dto: Input DTO with planning name.

        Returns:
            Output DTO with created planning data.

        Raises:
            DuplicatePlanningNameException: If a planning with the same name exists.
        """
        existing = await self._uow.plannings.get_by_name(input_dto.name)
        if existing is not None:
            raise DuplicatePlanningNameException(input_dto.name)

        planning = Planning(id=None, name=input_dto.name)
        planning_id = await self._uow.plannings.add(planning)
        created = await self._uow.plannings.get_by_id(planning_id)
        assert created is not None, "Planning must exist after creation"

        logger.info("Planning created: id=%d, name='%s'", planning_id, input_dto.name)

        assert created.id is not None
        return PlanningOutput(
            id=created.id,
            name=created.name,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )
