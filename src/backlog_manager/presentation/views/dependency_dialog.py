"""Dependency Dialog View.

Dialog modal para gestao de dependencias de uma historia.
Dimensoes: 500x420px (fixo, per FR-017).
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.application.dto.story import StoryOutputDTO

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class DependencyDialog(QDialog):
    """Dialog modal para gestao de dependencias.

    Exibe listas de "Depende de" (editavel) e "Dependentes" (readonly).
    Detecta ciclos com feedback visual.
    """

    def __init__(
        self,
        container: DIContainer,
        story_id: str,
        story_name: str,
        all_stories: list[StoryOutputDTO],
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            container: Dependency injection container.
            story_id: ID da historia.
            story_name: Nome da historia.
            all_stories: Todas as historias do backlog.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._container = container
        self._viewmodel = container.dependency_dialog_viewmodel
        self._viewmodel.set_story(story_id, story_name, all_stories)

        self._setup_ui()
        self._connect_signals()

        # Load dependencies
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_dependencies())
        )

        logger.debug("DependencyDialog initialized for %s", story_id)

    def _setup_ui(self) -> None:
        """Cria e configura a UI do dialog."""
        self.setWindowTitle(
            f"Dependencias: {self._viewmodel.story_id} - {self._viewmodel.story_name}"
        )
        self.setFixedSize(500, 420)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Error banner (cycle detection)
        self._error_banner = QLabel()
        self._error_banner.setStyleSheet(
            "background-color: #FFEEEE; color: red; padding: 8px; "
            "border-radius: 4px;"
        )
        self._error_banner.setVisible(False)
        self._error_banner.setWordWrap(True)
        layout.addWidget(self._error_banner)

        # "Depende de" group (editable)
        depends_on_group = QGroupBox("Depende de")
        depends_on_layout = QVBoxLayout(depends_on_group)

        self._depends_on_list = QListWidget()
        self._depends_on_list.setMaximumHeight(120)
        depends_on_layout.addWidget(self._depends_on_list)

        # Add controls
        add_layout = QHBoxLayout()
        self._story_combo = QComboBox()
        self._story_combo.setPlaceholderText("Selecione uma historia...")
        add_layout.addWidget(self._story_combo, 1)

        self._add_button = QPushButton("Adicionar")
        self._add_button.setEnabled(False)
        add_layout.addWidget(self._add_button)
        depends_on_layout.addLayout(add_layout)

        self._remove_button = QPushButton("Remover Selecionada")
        self._remove_button.setEnabled(False)
        depends_on_layout.addWidget(self._remove_button)

        layout.addWidget(depends_on_group)

        # "Dependentes" group (readonly)
        dependents_group = QGroupBox("Dependentes (bloqueiam esta)")
        dependents_layout = QVBoxLayout(dependents_group)

        self._dependents_list = QListWidget()
        self._dependents_list.setMaximumHeight(120)
        dependents_layout.addWidget(self._dependents_list)

        layout.addWidget(dependents_group)

        # Close button
        close_button = QPushButton("Fechar")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Populate combo
        self._update_combo()

    def _update_combo(self) -> None:
        """Atualiza combo com historias disponiveis."""
        self._story_combo.clear()
        self._story_combo.addItem("", None)
        for story in self._viewmodel.available_stories:
            self._story_combo.addItem(f"{story.id}: {story.name[:30]}", story.id)

    def _connect_signals(self) -> None:
        """Conecta signals."""
        self._add_button.clicked.connect(self._on_add)
        self._remove_button.clicked.connect(self._on_remove)
        self._depends_on_list.currentItemChanged.connect(self._on_dep_selection_changed)
        self._story_combo.currentIndexChanged.connect(self._on_combo_changed)

        # ViewModel signals
        self._viewmodel.dependencies_changed.connect(self._on_dependencies_changed)
        self._viewmodel.cycle_detected.connect(self._on_cycle_detected)
        self._viewmodel.error_occurred.connect(self._on_error)

    @Slot()
    def _on_dependencies_changed(self) -> None:
        """Atualiza listas quando dependencias mudam."""
        self._depends_on_list.clear()
        for story in self._viewmodel.depends_on:
            item = QListWidgetItem(f"{story.id}: {story.name[:25]}")
            item.setData(Qt.ItemDataRole.UserRole, story.id)
            self._depends_on_list.addItem(item)

        self._dependents_list.clear()
        for story in self._viewmodel.dependents:
            item = QListWidgetItem(f"{story.id}: {story.name[:25]}")
            self._dependents_list.addItem(item)

        # Clear cycle error on successful update
        if not self._viewmodel.has_cycle_error:
            self._error_banner.setVisible(False)

    @Slot(str)
    def _on_cycle_detected(self, message: str) -> None:
        """Exibe erro de ciclo."""
        self._error_banner.setText(message)
        self._error_banner.setVisible(True)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Exibe erro generico."""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.warning(self, "Erro", message)

    @Slot()
    def _on_dep_selection_changed(self) -> None:
        """Handle selecao na lista de dependencias."""
        has_selection = self._depends_on_list.currentItem() is not None
        self._remove_button.setEnabled(has_selection)

    @Slot(int)
    def _on_combo_changed(self, index: int) -> None:
        """Handle mudanca no combo."""
        has_selection = index > 0 and self._story_combo.currentData() is not None
        self._add_button.setEnabled(has_selection)

    @Slot()
    def _on_add(self) -> None:
        """Handle adicionar dependencia."""
        target_id = self._story_combo.currentData()
        if not target_id:
            return

        QTimer.singleShot(
            0,
            lambda: asyncio.create_task(self._viewmodel.add_dependency(target_id)),
        )
        self._story_combo.setCurrentIndex(0)

    @Slot()
    def _on_remove(self) -> None:
        """Handle remover dependencia."""
        item = self._depends_on_list.currentItem()
        if not item:
            return

        target_id = item.data(Qt.ItemDataRole.UserRole)
        QTimer.singleShot(
            0,
            lambda: asyncio.create_task(self._viewmodel.remove_dependency(target_id)),
        )
