"""Schedule ViewModel.

This module provides the ViewModel for executing schedule calculation
and tracking calculation state.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
    CalculateScheduleInputDTO,
    CalculateScheduleOutputDTO,
)
from backlog_manager.domain.exceptions import (
    BacklogManagerException,
    CyclicDependencyException,
)

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ScheduleViewModel(QObject):
    """ViewModel para calculo de cronograma.

    Coordena a execucao do use case CalculateSchedule e
    emite sinais para atualizacao da UI.

    Signals:
        schedule_started: Emitted when calculation starts.
        schedule_completed: Emitted when calculation completes (payload: output DTO).
        schedule_error: Emitted when calculation fails (payload: error message).
    """

    # Signals as per contracts/schedule_viewmodel_signals.md
    schedule_started = Signal()
    schedule_completed = Signal(object)  # CalculateScheduleOutputDTO
    schedule_error = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        """Inicializa o ViewModel.

        Args:
            container: Container de injecao de dependencias.
        """
        super().__init__()
        self._container = container
        self._is_running: bool = False

        logger.debug("ScheduleViewModel initialized")

    @property
    def is_running(self) -> bool:
        """Retorna True se calculo esta em execucao.

        Returns:
            True if running, False otherwise.
        """
        return self._is_running

    async def execute(
        self,
        velocity: float,
        start_date: date,
    ) -> CalculateScheduleOutputDTO | None:
        """Executa o calculo de cronograma.

        Args:
            velocity: Velocidade em SP/dia.
            start_date: Data de inicio do projeto.

        Returns:
            DTO com resultado ou None se ja executando.
        """
        if self._is_running:
            logger.warning("Schedule calculation already running")
            return None

        self._is_running = True
        self.schedule_started.emit()
        logger.info(
            "Starting schedule calculation: velocity=%.2f, start=%s",
            velocity,
            start_date,
        )

        try:
            dto = CalculateScheduleInputDTO(
                velocity=velocity,
                start_date=start_date,
                recalculate_all=True,
            )

            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_calculate_schedule_use_case(uow)
                result = await use_case.execute(dto)

            logger.info(
                "Schedule calculation completed: %d stories updated",
                result.stories_updated,
            )

            self.schedule_completed.emit(result)
            return result

        except CyclicDependencyException as e:
            error_msg = f"Dependencia ciclica detectada: {' -> '.join(e.path)}"
            logger.error("Schedule calculation failed: %s", error_msg)
            self.schedule_error.emit(error_msg)
            return None

        except BacklogManagerException as e:
            error_msg = f"Erro ao calcular cronograma: {e}"
            logger.error("Schedule calculation failed: %s", error_msg)
            self.schedule_error.emit(error_msg)
            return None

        except Exception as e:
            error_msg = f"Erro inesperado ao calcular cronograma: {e}"
            logger.exception("Schedule calculation failed unexpectedly")
            self.schedule_error.emit(error_msg)
            return None

        finally:
            self._is_running = False
