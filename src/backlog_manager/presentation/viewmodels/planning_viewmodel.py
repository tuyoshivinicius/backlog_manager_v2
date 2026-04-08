"""Planning ViewModel.

This module provides the ViewModel for planning CRUD operations
and tracking operation state.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.planning.planning_dto import (
    CreatePlanningInput,
    PlanningListItem,
    PlanningOutput,
    UpdatePlanningInput,
)

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class PlanningViewModel(QObject):
    """ViewModel para operacoes CRUD de planejamento.

    Coordena a execucao dos use cases de Planning
    e emite sinais para atualizacao da UI.

    Signals:
        planning_created: Emitted when a planning is created (id, name).
        planning_activated: Emitted when a planning is activated (id, name).
        planning_renamed: Emitted when a planning is renamed (id, new_name).
        planning_deleted: Emitted when a planning is deleted (id).
        error_occurred: Emitted when an operation fails (error message).
    """

    planning_created = Signal(int, str)
    planning_activated = Signal(int, str)
    planning_renamed = Signal(int, str)
    planning_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container

        logger.debug("PlanningViewModel initialized")

    async def create_planning(self, name: str) -> PlanningOutput | None:
        """Create a new planning.

        Args:
            name: Name for the new planning.

        Returns:
            Output DTO with created planning data, or None on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_create_planning_use_case(uow)
                result = await use_case.execute(CreatePlanningInput(name=name))

            logger.info("Planning created: id=%d, name='%s'", result.id, result.name)
            self.planning_created.emit(result.id, result.name)
            return result

        except Exception as e:
            error_msg = f"Erro ao criar planejamento: {e}"
            logger.exception("Create planning failed")
            self.error_occurred.emit(error_msg)
            return None

    async def list_plannings(self) -> list[PlanningListItem]:
        """List all plannings with story counts.

        Returns:
            List of planning items, or empty list on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_plannings_use_case(uow)
                return await use_case.execute()

        except Exception as e:
            error_msg = f"Erro ao listar planejamentos: {e}"
            logger.exception("List plannings failed")
            self.error_occurred.emit(error_msg)
            return []

    async def activate_planning(self, planning_id: int) -> PlanningOutput | None:
        """Set a planning as active.

        Args:
            planning_id: ID of the planning to activate.

        Returns:
            Output DTO with activated planning data, or None on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_set_active_planning_use_case(uow)
                result = await use_case.execute(planning_id)

            logger.info("Planning activated: id=%d, name='%s'", result.id, result.name)
            self.planning_activated.emit(result.id, result.name)
            return result

        except Exception as e:
            error_msg = f"Erro ao ativar planejamento: {e}"
            logger.exception("Activate planning failed")
            self.error_occurred.emit(error_msg)
            return None

    async def rename_planning(
        self, planning_id: int, new_name: str
    ) -> PlanningOutput | None:
        """Rename an existing planning.

        Args:
            planning_id: ID of the planning to rename.
            new_name: New name for the planning.

        Returns:
            Output DTO with updated planning data, or None on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_update_planning_use_case(uow)
                result = await use_case.execute(
                    UpdatePlanningInput(planning_id=planning_id, name=new_name)
                )

            logger.info("Planning renamed: id=%d, name='%s'", result.id, result.name)
            self.planning_renamed.emit(result.id, result.name)
            return result

        except Exception as e:
            error_msg = f"Erro ao renomear planejamento: {e}"
            logger.exception("Rename planning failed")
            self.error_occurred.emit(error_msg)
            return None

    async def delete_planning(self, planning_id: int, active_planning_id: int) -> bool:
        """Delete a planning.

        Args:
            planning_id: ID of the planning to delete.
            active_planning_id: ID of the currently active planning.

        Returns:
            True if deleted successfully, False on error.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_delete_planning_use_case(uow)
                await use_case.execute(planning_id, active_planning_id)

            logger.info("Planning deleted: id=%d", planning_id)
            self.planning_deleted.emit(planning_id)
            return True

        except Exception as e:
            error_msg = f"Erro ao excluir planejamento: {e}"
            logger.exception("Delete planning failed")
            self.error_occurred.emit(error_msg)
            return False

    async def get_active_planning(
        self, last_active_id: int | None
    ) -> PlanningOutput | None:
        """Get the active planning.

        Args:
            last_active_id: ID of the last active planning, or None.

        Returns:
            Output DTO with planning data, or None if not found.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_get_active_planning_use_case(uow)
                return await use_case.execute(last_active_id)

        except Exception as e:
            error_msg = f"Erro ao obter planejamento ativo: {e}"
            logger.exception("Get active planning failed")
            self.error_occurred.emit(error_msg)
            return None
