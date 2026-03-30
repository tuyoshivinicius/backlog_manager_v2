"""Allocation ViewModel.

This module provides the ViewModel for executing automatic allocation
and tracking allocation metrics and warnings.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.allocation import (
    AllocationMetricsDTO,
    ExecuteAllocationInputDTO,
    ExecuteAllocationOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class AllocationViewModel(QObject):
    """ViewModel for automatic allocation execution.

    Manages allocation state, progress, metrics, and warnings.

    Signals:
        allocation_started: Emitted when allocation starts.
        allocation_completed: Emitted when allocation completes (payload: metrics).
        allocation_error: Emitted when allocation fails (payload: error message).
        warnings_updated: Emitted when warnings are updated (payload: warning list).
    """

    # Signals as per contracts/viewmodel-signals.md
    allocation_started = Signal()
    allocation_completed = Signal(object)  # AllocationMetricsDTO
    allocation_error = Signal(str)
    allocation_cancelled = Signal()
    warnings_updated = Signal(list)

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container

        self._is_running: bool = False
        self._last_metrics: AllocationMetricsDTO | None = None
        self._last_warnings: list[str] = []

        logger.debug("AllocationViewModel initialized")

    @property
    def is_running(self) -> bool:
        """Check if allocation is currently running.

        Returns:
            True if running, False otherwise.
        """
        return self._is_running

    @property
    def last_metrics(self) -> AllocationMetricsDTO | None:
        """Get the metrics from the last allocation.

        Returns:
            Metrics DTO or None if no allocation has been run.
        """
        return self._last_metrics

    @property
    def last_warnings(self) -> list[str]:
        """Get the warnings from the last allocation.

        Returns:
            List of warning messages.
        """
        return self._last_warnings.copy()

    def can_execute(self) -> bool:
        """Check if allocation can be executed.

        Returns:
            True if not currently running, False otherwise.
        """
        return not self._is_running

    async def execute(
        self,
        velocity: float,
        start_date: date,
        max_idle_days: int = 3,
        allocation_criteria: str = "LOAD_BALANCING",
    ) -> ExecuteAllocationOutputDTO | None:
        """Execute automatic allocation.

        Args:
            velocity: Story points per day.
            start_date: Project start date.
            max_idle_days: Maximum idle days before warning (2-30).
            allocation_criteria: Allocation strategy.

        Returns:
            Allocation output DTO on success, None on failure.
        """
        if self._is_running:
            logger.warning("Allocation already running")
            return None

        self._is_running = True
        self.allocation_started.emit()
        logger.info(
            "Starting allocation: velocity=%.2f, start=%s, max_idle=%d",
            velocity,
            start_date,
            max_idle_days,
        )

        try:
            dto = ExecuteAllocationInputDTO(
                velocity=velocity,
                project_start_date=start_date,
                max_idle_days=max_idle_days,
                allocation_criteria=allocation_criteria,
            )

            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_execute_allocation_use_case(uow)
                result = await use_case.execute(dto)

            self._last_metrics = result.metrics
            self._last_warnings = [str(w) for w in result.warnings]

            self.warnings_updated.emit(self._last_warnings)
            self.allocation_completed.emit(result.metrics)

            logger.info(
                "Allocation completed: %d stories allocated in %.2fs",
                result.stories_allocated,
                result.total_time_seconds,
            )

            return result

        except asyncio.CancelledError:
            logger.info("Allocation cancelled by user")
            self.allocation_cancelled.emit()
            return None
        except BacklogManagerException as e:
            error_msg = str(e)
            logger.warning("Allocation failed: %s", error_msg)
            self.allocation_error.emit(error_msg)
            return None
        except Exception as e:
            error_msg = f"Erro inesperado na alocacao: {e}"
            logger.exception("Allocation failed unexpectedly")
            self.allocation_error.emit(error_msg)
            return None
        finally:
            self._is_running = False

    def clear_results(self) -> None:
        """Clear the last allocation results."""
        self._last_metrics = None
        self._last_warnings = []
        self.warnings_updated.emit([])
