"""Dependency Dialog ViewModel.

Gerencia estado e operacoes de dependencias de uma historia.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.dependency import (
    AddDependencyInputDTO,
    GetDependenciesInputDTO,
    GetDependentsInputDTO,
    RemoveDependencyInputDTO,
)
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.domain.exceptions import (
    BacklogManagerException,
    CyclicDependencyException,
)

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class DependencyDialogViewModel(QObject):
    """ViewModel para o DependencyDialog.

    Signals:
        dependencies_changed: Emitido quando dependencias mudam.
        error_occurred: Emitido quando ocorre erro.
        cycle_detected: Emitido quando ciclo e detectado (mensagem).
    """

    dependencies_changed = Signal()
    error_occurred = Signal(str)
    cycle_detected = Signal(str)

    def __init__(self, container: DIContainer, parent: QObject | None = None) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._container = container

        self._story_id: str = ""
        self._story_name: str = ""
        self._depends_on: list[StoryOutputDTO] = []
        self._dependents: list[StoryOutputDTO] = []
        self._available_stories: list[StoryOutputDTO] = []
        self._has_cycle_error: bool = False
        self._cycle_error_message: str = ""

    @property
    def story_id(self) -> str:
        """ID da historia."""
        return self._story_id

    @property
    def story_name(self) -> str:
        """Nome da historia."""
        return self._story_name

    @property
    def depends_on(self) -> list[StoryOutputDTO]:
        """Historias das quais esta depende."""
        return self._depends_on

    @property
    def dependents(self) -> list[StoryOutputDTO]:
        """Historias que dependem desta."""
        return self._dependents

    @property
    def available_stories(self) -> list[StoryOutputDTO]:
        """Historias disponiveis para adicionar como dependencia."""
        return self._available_stories

    @property
    def has_cycle_error(self) -> bool:
        """Indica se ha erro de ciclo."""
        return self._has_cycle_error

    @property
    def cycle_error_message(self) -> str:
        """Mensagem de erro de ciclo."""
        return self._cycle_error_message

    def set_story(
        self,
        story_id: str,
        story_name: str,
        all_stories: list[StoryOutputDTO],
    ) -> None:
        """Define a historia e lista de historias disponiveis.

        Args:
            story_id: ID da historia.
            story_name: Nome da historia.
            all_stories: Todas as historias do backlog.
        """
        self._story_id = story_id
        self._story_name = story_name
        self._available_stories = [s for s in all_stories if s.id != story_id]
        self._has_cycle_error = False
        self._cycle_error_message = ""

    async def load_dependencies(self) -> None:
        """Carrega dependencias da historia atual."""
        if not self._story_id:
            return

        try:
            planning_id = self._container.main_window_viewmodel.active_planning_id
            assert planning_id is not None, "Active planning must be set"
            async with self._container.create_unit_of_work() as uow:
                # Dependencias (historias das quais esta depende)
                deps_input = GetDependenciesInputDTO(story_id=self._story_id)
                deps_uc = self._container.create_get_dependencies_use_case(uow)
                deps_result = await deps_uc.execute(deps_input, planning_id)

                self._depends_on = [
                    s
                    for s in self._available_stories
                    if s.id in deps_result.dependencies
                ]

                # Dependentes (historias que dependem desta)
                dependents_input = GetDependentsInputDTO(story_id=self._story_id)
                dependents_uc = self._container.create_get_dependents_use_case(uow)
                dependents_result = await dependents_uc.execute(
                    dependents_input, planning_id
                )

                self._dependents = [
                    s
                    for s in self._available_stories
                    if s.id in dependents_result.dependents
                ]

            self.dependencies_changed.emit()
            logger.debug(
                "Loaded dependencies for %s: %d deps, %d dependents",
                self._story_id,
                len(self._depends_on),
                len(self._dependents),
            )
        except Exception as e:
            logger.exception("Error loading dependencies")
            self.error_occurred.emit(f"Erro ao carregar dependencias: {e}")

    async def add_dependency(self, target_id: str) -> None:
        """Adiciona dependencia.

        Args:
            target_id: ID da historia alvo.
        """
        if not self._story_id:
            return

        self._has_cycle_error = False
        self._cycle_error_message = ""

        try:
            dto = AddDependencyInputDTO(
                story_id=self._story_id,
                depends_on_id=target_id,
            )
            planning_id = self._container.main_window_viewmodel.active_planning_id
            assert planning_id is not None, "Active planning must be set"
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_add_dependency_use_case(uow)
                await use_case.execute(dto, planning_id)

            await self.load_dependencies()
            logger.info("Added dependency: %s depends on %s", self._story_id, target_id)
        except CyclicDependencyException as e:
            cycle_path = " -> ".join(e.path)
            self._has_cycle_error = True
            self._cycle_error_message = (
                f"Nao e possivel adicionar esta dependencia.\n"
                f"Ciclo detectado: {cycle_path}"
            )
            self.cycle_detected.emit(self._cycle_error_message)
        except BacklogManagerException as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.exception("Error adding dependency")
            self.error_occurred.emit(f"Erro ao adicionar dependencia: {e}")

    async def remove_dependency(self, target_id: str) -> None:
        """Remove dependencia.

        Args:
            target_id: ID da dependencia a remover.
        """
        if not self._story_id:
            return

        self._has_cycle_error = False
        self._cycle_error_message = ""

        try:
            dto = RemoveDependencyInputDTO(
                story_id=self._story_id,
                depends_on_id=target_id,
            )
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_remove_dependency_use_case(uow)
                planning_id = self._container.main_window_viewmodel.active_planning_id
                assert planning_id is not None
                await use_case.execute(dto, planning_id)

            await self.load_dependencies()
            logger.info(
                "Removed dependency: %s no longer depends on %s",
                self._story_id,
                target_id,
            )
        except BacklogManagerException as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.exception("Error removing dependency")
            self.error_occurred.emit(f"Erro ao remover dependencia: {e}")
