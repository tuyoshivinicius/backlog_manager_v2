"""Story Dialog View.

This module provides a QDialog for creating and editing stories.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Literal

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from backlog_manager.application.dto.feature import FeatureOutputDTO
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
    VALID_STORY_POINTS,
    StoryDialogViewModel,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class StoryDialog(QDialog):
    """Dialog for creating and editing stories.

    Provides form fields for component, name, story points, and feature
    with validation and persistence through ViewModel.
    """

    def __init__(
        self,
        container: DIContainer,
        parent: QWidget | None = None,
        mode: Literal["create", "edit"] = "create",
        story: StoryOutputDTO | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            container: Dependency injection container.
            parent: Optional parent widget.
            mode: Dialog mode ("create" or "edit").
            story: Story to edit (required if mode is "edit").
        """
        super().__init__(parent)

        self._container = container
        self._viewmodel = StoryDialogViewModel(container)
        self._result_story: StoryOutputDTO | None = None

        self._setup_ui()
        self._connect_signals()

        # Set mode and optionally load story data
        if mode == "edit" and story:
            self._viewmodel.set_story(story)
            self._load_story_to_form()
            self.setWindowTitle("Editar Historia")
        else:
            self._viewmodel.set_mode("create")
            self.setWindowTitle("Nova Historia")

        # Load features for dropdown
        asyncio.create_task(self._load_features())

        logger.debug("StoryDialog initialized in %s mode", mode)

    @property
    def result_story(self) -> StoryOutputDTO | None:
        """Get the created/edited story after dialog is accepted.

        Returns:
            The story DTO, or None if dialog was cancelled.
        """
        return self._result_story

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Component field
        self._component_edit = QLineEdit()
        self._component_edit.setPlaceholderText("Ex: API, UI, CORE")
        self._component_edit.setMaxLength(50)
        form_layout.addRow("Componente:", self._component_edit)

        # Name field
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Nome da historia")
        self._name_edit.setMaxLength(200)
        form_layout.addRow("Nome:", self._name_edit)

        # Story Points dropdown
        self._sp_combo = QComboBox()
        for sp in VALID_STORY_POINTS:
            self._sp_combo.addItem(str(sp), sp)
        self._sp_combo.setCurrentIndex(1)  # Default to 5
        form_layout.addRow("Story Points:", self._sp_combo)

        # Feature dropdown
        self._feature_combo = QComboBox()
        self._feature_combo.addItem("Nenhuma", None)
        form_layout.addRow("Feature:", self._feature_combo)

        layout.addLayout(form_layout)

        # Validation message label
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Button box
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Salvar")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(
            "Cancelar"
        )
        layout.addWidget(self._button_box)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._button_box.accepted.connect(self._on_save)
        self._button_box.rejected.connect(self.reject)

        self._viewmodel.saved.connect(self._on_saved)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.features_loaded.connect(self._on_features_loaded)

        # Form changes
        self._component_edit.textChanged.connect(self._on_component_changed)
        self._name_edit.textChanged.connect(self._on_name_changed)
        self._sp_combo.currentIndexChanged.connect(self._on_sp_changed)
        self._feature_combo.currentIndexChanged.connect(self._on_feature_changed)

    def _load_story_to_form(self) -> None:
        """Load story data from ViewModel to form fields."""
        self._component_edit.setText(self._viewmodel.component)
        self._name_edit.setText(self._viewmodel.name)

        # Set story points
        sp_index = VALID_STORY_POINTS.index(self._viewmodel.story_points)
        self._sp_combo.setCurrentIndex(sp_index)

        # Feature will be set after features are loaded
        # Component is read-only in edit mode
        self._component_edit.setEnabled(self._viewmodel.mode == "create")

    async def _load_features(self) -> None:
        """Load features into the dropdown."""
        await self._viewmodel.load_features()

    @Slot(list)
    def _on_features_loaded(self, features: list[FeatureOutputDTO]) -> None:
        """Handle features_loaded signal.

        Args:
            features: List of feature DTOs.
        """
        # Clear and repopulate
        self._feature_combo.clear()
        self._feature_combo.addItem("Nenhuma", None)

        for feature in features:
            self._feature_combo.addItem(
                f"{feature.name} (Onda {feature.wave})", feature.id
            )

        # If editing, select the current feature
        if self._viewmodel.feature_id:
            for i in range(self._feature_combo.count()):
                if self._feature_combo.itemData(i) == self._viewmodel.feature_id:
                    self._feature_combo.setCurrentIndex(i)
                    break

    @Slot(str)
    def _on_component_changed(self, text: str) -> None:
        """Handle component text change."""
        self._viewmodel.component = text
        self._error_label.hide()

    @Slot(str)
    def _on_name_changed(self, text: str) -> None:
        """Handle name text change."""
        self._viewmodel.name = text
        self._error_label.hide()

    @Slot(int)
    def _on_sp_changed(self, index: int) -> None:
        """Handle story points selection change."""
        sp = self._sp_combo.itemData(index)
        if sp:
            self._viewmodel.story_points = sp

    @Slot(int)
    def _on_feature_changed(self, index: int) -> None:
        """Handle feature selection change."""
        feature_id = self._feature_combo.itemData(index)
        self._viewmodel.feature_id = feature_id

    @Slot()
    def _on_save(self) -> None:
        """Handle save button click."""
        # Validate before async save
        is_valid, error_msg = self._viewmodel.validate()
        if not is_valid:
            self._error_label.setText(error_msg)
            self._error_label.show()
            return

        self._error_label.hide()
        asyncio.create_task(self._save_story())

    async def _save_story(self) -> None:
        """Save the story asynchronously."""
        self._button_box.setEnabled(False)
        try:
            story = await self._viewmodel.save()
            if story:
                self._result_story = story
        finally:
            self._button_box.setEnabled(True)

    @Slot()
    def _on_saved(self) -> None:
        """Handle saved signal."""
        self.accept()

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error_occurred signal.

        Args:
            message: Error message.
        """
        self._error_label.setText(message)
        self._error_label.show()
