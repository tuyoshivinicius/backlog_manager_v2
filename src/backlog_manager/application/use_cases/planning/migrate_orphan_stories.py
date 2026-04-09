"""Migrate orphan stories use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class MigrateOrphanStoriesUseCase:
    """Use case for migrating orphan stories to a target planning.

    Placeholder implementation — migration is handled by init_database.
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(self, target_planning_id: int) -> int:
        """Execute the migrate orphan stories operation.

        Args:
            target_planning_id: ID of the planning to migrate stories to.

        Returns:
            Number of stories migrated (currently always 0).
        """
        logger.info(
            "MigrateOrphanStories called for planning_id=%d (placeholder)",
            target_planning_id,
        )
        return 0
