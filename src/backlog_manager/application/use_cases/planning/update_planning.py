"""Update planning use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.planning.planning_dto import (
    PlanningOutput,
    UpdatePlanningInput,
)
from backlog_manager.domain.exceptions.planning_exceptions import (
    DuplicatePlanningNameException,
)

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class UpdatePlanningUseCase:
    """Use case for updating an existing planning."""

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, input_dto: UpdatePlanningInput) -> PlanningOutput:
        """Execute the update planning operation.

        Args:
            input_dto: Input DTO with planning_id and new name.

        Returns:
            Output DTO with updated planning data.

        Raises:
            ValueError: If planning not found.
            DuplicatePlanningNameException: If another planning has the same name.
        """
        planning = await self._uow.plannings.get_by_id(input_dto.planning_id)
        if planning is None:
            raise ValueError(
                f"Planejamento com id={input_dto.planning_id} nao encontrado"
            )

        existing = await self._uow.plannings.get_by_name(input_dto.name)
        if existing is not None and existing.id != input_dto.planning_id:
            raise DuplicatePlanningNameException(input_dto.name)

        planning.name = input_dto.name
        await self._uow.plannings.update(planning)
        await self._uow.plannings.update_timestamp(input_dto.planning_id)

        updated = await self._uow.plannings.get_by_id(input_dto.planning_id)
        assert updated is not None, "Planning must exist after update"

        logger.info(
            "Planning updated: id=%d, name='%s'",
            input_dto.planning_id,
            input_dto.name,
        )

        assert updated.id is not None
        return PlanningOutput(
            id=updated.id,
            name=updated.name,
            created_at=updated.created_at,
            updated_at=updated.updated_at,
        )
