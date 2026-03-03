"""Execute automatic allocation use case."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backlog_manager.application.dto.allocation.execute_allocation_dto import (
    AllocationMetricsDTO,
    ExecuteAllocationInputDTO,
    ExecuteAllocationOutputDTO,
)
from backlog_manager.domain.services import (
    AllocationConfig,
    AllocationCriteria,
    AllocationService,
)
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

if TYPE_CHECKING:
    from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)

# Warning threshold for large backlogs
LARGE_BACKLOG_THRESHOLD = 500


class ExecuteAllocationUseCase:
    """Use case for executing automatic developer allocation.

    Coordinates the allocation of developers to stories in the backlog,
    using the AllocationService domain service.

    Example:
        >>> async with SQLiteUnitOfWork() as uow:
        ...     use_case = ExecuteAllocationUseCase(uow)
        ...     result = await use_case.execute(
        ...         ExecuteAllocationInputDTO(
        ...             velocity=2.0,
        ...             project_start_date=date(2026, 3, 2)
        ...         )
        ...     )
        ...     print(f"Allocated {result.stories_allocated} stories")
    """

    def __init__(self, uow: SQLiteUnitOfWork) -> None:
        """Initialize use case.

        Args:
            uow: Unit of work for database operations.
        """
        self._uow = uow

    async def execute(
        self, input_dto: ExecuteAllocationInputDTO
    ) -> ExecuteAllocationOutputDTO:
        """Execute automatic allocation of developers to stories.

        Fluxo:
        1. Busca dados (stories, developers, dependencies, features)
        2. Emite warning se backlog > 500 historias
        3. Prepara AllocationConfig
        4. Chama AllocationService.allocate_stories() (sync)
        5. Atualiza historias alocadas via repository
        6. Converte resultado para DTO

        Args:
            input_dto: Allocation parameters.

        Returns:
            ExecuteAllocationOutputDTO with result and metrics.

        Raises:
            ValueError: If input_dto is invalid (Pydantic validation).
        """
        warnings: list[str] = []

        # Get all data
        all_stories = await self._uow.stories.get_all()
        all_developers = await self._uow.developers.get_all()
        all_features = await self._uow.features.get_all()
        all_deps = await self._uow.dependencies.get_all_dependencies()

        logger.info(
            "Starting allocation: %d stories, %d developers",
            len(all_stories),
            len(all_developers),
        )

        # Check for large backlog
        if len(all_stories) > LARGE_BACKLOG_THRESHOLD:
            warning_msg = (
                f"Backlog muito grande ({len(all_stories)} historias). "
                f"Recomendado: ate {LARGE_BACKLOG_THRESHOLD} historias."
            )
            warnings.append(warning_msg)
            logger.warning(warning_msg)

        # Convert allocation criteria string to enum
        try:
            criteria = AllocationCriteria(input_dto.allocation_criteria.lower())
        except ValueError:
            criteria = AllocationCriteria.LOAD_BALANCING
            warnings.append(
                f"Criterio invalido '{input_dto.allocation_criteria}', "
                f"usando LOAD_BALANCING"
            )

        # Build AllocationConfig
        config = AllocationConfig(
            velocity=input_dto.velocity,
            project_start_date=input_dto.project_start_date,
            max_idle_days=input_dto.max_idle_days,
            allocation_criteria=criteria,
            random_seed=input_dto.random_seed,
        )

        # Execute allocation (synchronous domain service)
        result = AllocationService.allocate_stories(
            stories=all_stories,
            developers=all_developers,
            dependencies=all_deps,
            features=all_features,
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
            config=config,
        )

        # Collect warnings from allocation result
        for warning in result.warnings:
            warnings.append(str(warning))

        # Persist allocated stories
        for story in result.allocated_stories:
            await self._uow.stories.update(story)

        logger.info(
            "Allocation completed: %d stories allocated in %.2fs",
            result.metrics.stories_allocated,
            result.metrics.total_time_seconds,
        )

        # Log deadlock warnings
        if result.metrics.deadlocks_detected > 0:
            logger.warning("Deadlocks detected: %d", result.metrics.deadlocks_detected)

        # Convert metrics to DTO
        metrics_dto = AllocationMetricsDTO.from_domain(result.metrics)

        return ExecuteAllocationOutputDTO(
            success=True,
            stories_allocated=result.metrics.stories_allocated,
            total_time_seconds=result.metrics.total_time_seconds,
            warnings=warnings,
            metrics=metrics_dto,
        )
