"""Reset Planning ViewModel.

This module provides the ViewModel for executing planning reset
and tracking operation state.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.planning.reset_planning_dto import (
    CountAffectedStoriesOutputDTO,
    ResetPlanningInputDTO,
    ResetPlanningOutputDTO,
)

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ResetPlanningViewModel(QObject):
    """ViewModel para reset de planejamento.

    Coordena a execucao dos use cases ResetPlanning e CountAffectedStories
    e emite sinais para atualizacao da UI.

    Signals:
        reset_started: Emitted when reset begins.
        reset_completed: Emitted when reset completes (payload: output DTO).
        reset_error: Emitted when reset fails (payload: error message).
    """

    reset_started = Signal()
    reset_completed = Signal(object)  # ResetPlanningOutputDTO
    reset_error = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        self._is_running: bool = False

        logger.debug("ResetPlanningViewModel initialized")

    @property
    def is_running(self) -> bool:
        """Return True if reset is in progress."""
        return self._is_running

    async def preview(self) -> CountAffectedStoriesOutputDTO | None:
        """Get preview counts of affected stories.

        Returns:
            DTO with counts or None on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_count_affected_stories_use_case(uow)
                return await use_case.execute()
        except Exception as e:
            logger.error("Failed to get preview counts: %s", e)
            return None

    async def execute(self) -> ResetPlanningOutputDTO | None:
        """Execute the reset planning operation.

        Returns:
            DTO with results or None if already running or on error.
        """
        if self._is_running:
            logger.warning("Reset planning already running")
            return None

        self._is_running = True
        self.reset_started.emit()
        logger.info("Starting reset planning")

        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_reset_planning_use_case(uow)
                result = await use_case.execute(ResetPlanningInputDTO())

            logger.info(
                "Reset planning completed: %d stories reset", result.stories_reset
            )

            self.reset_completed.emit(result)
            return result

        except Exception as e:
            error_msg = f"Erro ao resetar planejamento: {e}"
            logger.exception("Reset planning failed")
            self.reset_error.emit(error_msg)
            return None

        finally:
            self._is_running = False
