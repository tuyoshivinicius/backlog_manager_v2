"""Dependency Panel View.

This module provides a QWidget for managing story dependencies.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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


class DependencyPanel(QWidget):
    """Panel for viewing and managing story dependencies.

    Displays "Depende de" (dependencies) and "Dependentes" (dependents)
    lists with add/remove functionality.

    Signals:
        dependency_added: Emitted when a dependency is added (story_id, depends_on_id).
        dependency_removed: Emitted when a dependency is removed (story_id, depends_on_id).
        error_occurred: Emitted when an error occurs (message).
    """

    dependency_added = Signal(str, str)
    dependency_removed = Signal(str, str)
    error_occurred = Signal(str)

    def __init__(
        self,
        container: DIContainer,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the panel.

        Args:
            container: Dependency injection container.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._container = container
        self._current_story_id: str | None = None
        self._all_stories: list[StoryOutputDTO] = []

        self._setup_ui()
        self._connect_signals()

        logger.debug("DependencyPanel initialized")

    def _setup_ui(self) -> None:
        """Create and configure the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Dependencias")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # "Depende de" group
        depends_on_group = QGroupBox("Depende de")
        depends_on_layout = QVBoxLayout(depends_on_group)

        self._depends_on_list = QListWidget()
        self._depends_on_list.setMaximumHeight(120)
        depends_on_layout.addWidget(self._depends_on_list)

        # Add dependency controls
        add_layout = QHBoxLayout()
        self._story_combo = QComboBox()
        self._story_combo.setPlaceholderText("Selecione uma historia...")
        add_layout.addWidget(self._story_combo, 1)

        self._add_dep_button = QPushButton("Adicionar")
        self._add_dep_button.setEnabled(False)
        add_layout.addWidget(self._add_dep_button)

        depends_on_layout.addLayout(add_layout)

        self._remove_dep_button = QPushButton("Remover Selecionada")
        self._remove_dep_button.setEnabled(False)
        depends_on_layout.addWidget(self._remove_dep_button)

        layout.addWidget(depends_on_group)

        # "Dependentes" group
        dependents_group = QGroupBox("Dependentes (bloqueiam esta)")
        dependents_layout = QVBoxLayout(dependents_group)

        self._dependents_list = QListWidget()
        self._dependents_list.setMaximumHeight(120)
        dependents_layout.addWidget(self._dependents_list)

        layout.addWidget(dependents_group)

        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._add_dep_button.clicked.connect(self._on_add_dependency)
        self._remove_dep_button.clicked.connect(self._on_remove_dependency)
        self._depends_on_list.currentItemChanged.connect(self._on_dep_selection_changed)
        self._story_combo.currentIndexChanged.connect(self._on_combo_changed)

    def set_stories(self, stories: list[StoryOutputDTO]) -> None:
        """Set the available stories for the dependency dropdown.

        Args:
            stories: List of all stories.
        """
        self._all_stories = stories
        self._update_combo()

    def _update_combo(self) -> None:
        """Update the story combo with available stories."""
        self._story_combo.clear()
        self._story_combo.addItem("", None)

        for story in self._all_stories:
            if story.id != self._current_story_id:
                self._story_combo.addItem(f"{story.id}: {story.name[:30]}", story.id)

    @Slot(str)
    def set_current_story(self, story_id: str | None) -> None:
        """Set the current story to display dependencies for.

        Args:
            story_id: Story ID, or None to clear.
        """
        self._current_story_id = story_id
        self._update_combo()

        if story_id:
            try:
                QTimer.singleShot(
                    0, lambda: asyncio.create_task(self._load_dependencies())
                )
            except RuntimeError:
                # No event loop running (e.g., during tests)
                logger.debug("No event loop to load dependencies for %s", story_id)
        else:
            self._clear_lists()

    def _clear_lists(self) -> None:
        """Clear the dependency lists."""
        self._depends_on_list.clear()
        self._dependents_list.clear()

    async def _load_dependencies(self) -> None:
        """Load dependencies for the current story."""
        if not self._current_story_id:
            return

        try:
            async with self._container.create_unit_of_work() as uow:
                # Get dependencies (stories this one depends on)
                deps_input = GetDependenciesInputDTO(story_id=self._current_story_id)
                deps_use_case = self._container.create_get_dependencies_use_case(uow)
                planning_id = self._container.main_window_viewmodel.active_planning_id
                assert planning_id is not None
                deps_result = await deps_use_case.execute(deps_input, planning_id)

                self._depends_on_list.clear()
                for dep_id in deps_result.dependencies:
                    item = QListWidgetItem(self._get_story_label(dep_id))
                    item.setData(Qt.ItemDataRole.UserRole, dep_id)
                    self._depends_on_list.addItem(item)

                # Get dependents (stories that depend on this one)
                dependents_input = GetDependentsInputDTO(
                    story_id=self._current_story_id
                )
                dependents_use_case = self._container.create_get_dependents_use_case(
                    uow
                )
                dependents_result = await dependents_use_case.execute(
                    dependents_input, planning_id
                )

                self._dependents_list.clear()
                for dep_id in dependents_result.dependents:
                    item = QListWidgetItem(self._get_story_label(dep_id))
                    item.setData(Qt.ItemDataRole.UserRole, dep_id)
                    self._dependents_list.addItem(item)

                logger.debug(
                    "Loaded dependencies for %s: %d deps, %d dependents",
                    self._current_story_id,
                    len(deps_result.dependencies),
                    len(dependents_result.dependents),
                )
        except Exception as e:
            logger.exception("Error loading dependencies")
            self.error_occurred.emit(f"Erro ao carregar dependencias: {e}")

    def _get_story_label(self, story_id: str) -> str:
        """Get a display label for a story ID.

        Args:
            story_id: Story ID.

        Returns:
            Display label with ID and truncated name.
        """
        for story in self._all_stories:
            if story.id == story_id:
                return f"{story.id}: {story.name[:25]}"
        return story_id

    @Slot()
    def _on_dep_selection_changed(self) -> None:
        """Handle selection change in depends_on list."""
        has_selection = self._depends_on_list.currentItem() is not None
        self._remove_dep_button.setEnabled(has_selection)

    @Slot(int)
    def _on_combo_changed(self, index: int) -> None:
        """Handle combo box selection change."""
        has_selection = index > 0 and self._story_combo.currentData() is not None
        self._add_dep_button.setEnabled(has_selection)

    @Slot()
    def _on_add_dependency(self) -> None:
        """Handle add dependency button click."""
        if not self._current_story_id:
            return

        depends_on_id = self._story_combo.currentData()
        if not depends_on_id:
            return

        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._add_dependency(depends_on_id))
        )

    async def _add_dependency(self, depends_on_id: str) -> None:
        """Add a dependency.

        Args:
            depends_on_id: ID of the story to depend on.
        """
        if not self._current_story_id:
            return

        try:
            dto = AddDependencyInputDTO(
                story_id=self._current_story_id,
                depends_on_id=depends_on_id,
            )
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_add_dependency_use_case(uow)
                planning_id = self._container.main_window_viewmodel.active_planning_id
                assert planning_id is not None
                result = await use_case.execute(dto, planning_id)

                if result.warning:
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        result.warning.message,
                    )

            await self._load_dependencies()
            self._story_combo.setCurrentIndex(0)
            self.dependency_added.emit(self._current_story_id, depends_on_id)
            logger.info(
                "Added dependency: %s depends on %s",
                self._current_story_id,
                depends_on_id,
            )
        except CyclicDependencyException as e:
            cycle_path = " -> ".join(e.path)
            QMessageBox.warning(
                self,
                "Dependencia Ciclica Detectada",
                f"Nao e possivel adicionar esta dependencia.\n\n"
                f"Ciclo detectado:\n{cycle_path}",
            )
        except BacklogManagerException as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.exception("Error adding dependency")
            self.error_occurred.emit(f"Erro ao adicionar dependencia: {e}")

    @Slot()
    def _on_remove_dependency(self) -> None:
        """Handle remove dependency button click."""
        if not self._current_story_id:
            return

        item = self._depends_on_list.currentItem()
        if not item:
            return

        depends_on_id = item.data(Qt.ItemDataRole.UserRole)
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._remove_dependency(depends_on_id))
        )

    async def _remove_dependency(self, depends_on_id: str) -> None:
        """Remove a dependency.

        Args:
            depends_on_id: ID of the dependency to remove.
        """
        if not self._current_story_id:
            return

        try:
            dto = RemoveDependencyInputDTO(
                story_id=self._current_story_id,
                depends_on_id=depends_on_id,
            )
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_remove_dependency_use_case(uow)
                planning_id = self._container.main_window_viewmodel.active_planning_id
                assert planning_id is not None
                await use_case.execute(dto, planning_id)

            await self._load_dependencies()
            self.dependency_removed.emit(self._current_story_id, depends_on_id)
            logger.info(
                "Removed dependency: %s no longer depends on %s",
                self._current_story_id,
                depends_on_id,
            )
        except BacklogManagerException as e:
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.exception("Error removing dependency")
            self.error_occurred.emit(f"Erro ao remover dependencia: {e}")
