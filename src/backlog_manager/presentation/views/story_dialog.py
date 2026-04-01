"""Story Dialog View.

This module provides a QDialog for creating and editing stories.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Coroutine
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtCore import QEvent, QObject, QTimer, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.application.dto.developer import DeveloperOutputDTO
from backlog_manager.application.dto.feature import FeatureOutputDTO
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.constants import STATUS_LABELS
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
        self._pending_tasks: set[asyncio.Task[Any]] = set()

        self._setup_ui()
        self._connect_signals()

        # Set mode and optionally load story data
        if mode == "edit" and story:
            self._viewmodel.set_story(story)
            self._load_story_to_form()
            self.setWindowTitle("Editar Historia")
            self._developer_container.show()
            self._status_container.show()
        else:
            self._viewmodel.set_mode("create")
            self.setWindowTitle("Nova Historia")
            self._developer_container.hide()
            self._status_container.hide()

        # Load features for dropdown
        QTimer.singleShot(0, lambda: self._create_task(self._load_features()))

        # Load developers for dropdown (edit mode only)
        if mode == "edit":
            QTimer.singleShot(0, lambda: self._create_task(self._load_developers()))

        logger.debug("StoryDialog initialized in %s mode", mode)

    @property
    def result_story(self) -> StoryOutputDTO | None:
        """Get the created/edited story after dialog is accepted.

        Returns:
            The story DTO, or None if dialog was cancelled.
        """
        return self._result_story

    def _create_task(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        """Cria e rastreia uma task assincrona com limpeza automatica."""
        task = asyncio.create_task(coro)
        self._pending_tasks.add(task)
        task.add_done_callback(self._pending_tasks.discard)
        return task

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setObjectName("story-dialog")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Component field with required indicator
        component_label_layout = QHBoxLayout()
        component_label = QLabel("Componente:")
        component_label_layout.addWidget(component_label)
        component_req = QLabel("*")
        component_req.setObjectName("required-indicator")
        component_label_layout.addWidget(component_req)
        component_label_layout.addStretch()
        component_label_widget = QWidget()
        component_label_widget.setLayout(component_label_layout)
        component_label_layout.setContentsMargins(0, 0, 0, 0)

        self._component_edit = QLineEdit()
        self._component_edit.setObjectName("story-component-field")
        self._component_edit.setPlaceholderText("Ex: API, UI, CORE")
        self._component_edit.setMaxLength(50)

        # Component error label
        self._component_error_label = QLabel()
        self._component_error_label.setObjectName("field-error-label")
        self._component_error_label.setWordWrap(True)
        self._component_error_label.hide()

        # Component char count
        self._component_char_count = QLabel("0/50")
        self._component_char_count.setObjectName("field-char-count")

        component_field_widget = QWidget()
        component_field_layout = QVBoxLayout(component_field_widget)
        component_field_layout.setContentsMargins(0, 0, 0, 0)
        component_field_layout.addWidget(self._component_edit)
        component_field_layout.addWidget(self._component_error_label)
        component_field_layout.addWidget(self._component_char_count)

        form_layout.addRow(component_label_widget, component_field_widget)

        # Name field with required indicator
        name_label_layout = QHBoxLayout()
        name_label = QLabel("Nome:")
        name_label_layout.addWidget(name_label)
        name_req = QLabel("*")
        name_req.setObjectName("required-indicator")
        name_label_layout.addWidget(name_req)
        name_label_layout.addStretch()
        name_label_widget = QWidget()
        name_label_widget.setLayout(name_label_layout)
        name_label_layout.setContentsMargins(0, 0, 0, 0)

        self._name_edit = QLineEdit()
        self._name_edit.setObjectName("story-name-field")
        self._name_edit.setPlaceholderText("Nome da historia")
        self._name_edit.setMaxLength(200)

        # Name error label
        self._name_error_label = QLabel()
        self._name_error_label.setObjectName("field-error-label")
        self._name_error_label.setWordWrap(True)
        self._name_error_label.hide()

        # Name char count
        self._name_char_count = QLabel("0/200")
        self._name_char_count.setObjectName("field-char-count")

        name_field_widget = QWidget()
        name_field_layout = QVBoxLayout(name_field_widget)
        name_field_layout.setContentsMargins(0, 0, 0, 0)
        name_field_layout.addWidget(self._name_edit)
        name_field_layout.addWidget(self._name_error_label)
        name_field_layout.addWidget(self._name_char_count)

        form_layout.addRow(name_label_widget, name_field_widget)

        # Story Points dropdown
        self._sp_combo = QComboBox()
        self._sp_combo.setObjectName("story-points-combo")
        for sp in VALID_STORY_POINTS:
            self._sp_combo.addItem(str(sp), sp)
        self._sp_combo.setCurrentIndex(1)  # Default to 5
        form_layout.addRow("Story Points:", self._sp_combo)

        # Feature dropdown
        self._feature_combo = QComboBox()
        self._feature_combo.setObjectName("story-feature-combo")
        self._feature_combo.addItem("Nenhuma", None)
        form_layout.addRow("Feature:", self._feature_combo)

        # Developer dropdown (visible only in edit mode, per ADR-003)
        self._developer_container = QWidget()
        self._developer_container.setObjectName("story-developer-container")
        developer_layout = QFormLayout(self._developer_container)
        developer_layout.setContentsMargins(0, 0, 0, 0)
        self._developer_combo = QComboBox()
        self._developer_combo.setObjectName("story-developer-combo")
        self._developer_combo.addItem("Nenhum", None)
        developer_layout.addRow("Desenvolvedor:", self._developer_combo)
        self._developer_container.hide()
        layout.addLayout(form_layout)
        layout.addWidget(self._developer_container)

        # Status dropdown (visible only in edit mode)
        self._status_container = QWidget()
        self._status_container.setObjectName("story-status-container")
        status_layout = QFormLayout(self._status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        self._status_combo = QComboBox()
        self._status_combo.setObjectName("story-status-combo")
        for value, label in STATUS_LABELS:
            self._status_combo.addItem(label, value)
        status_layout.addRow("Status:", self._status_combo)
        self._status_container.hide()
        layout.addWidget(self._status_container)

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
        save_button = self._button_box.button(QDialogButtonBox.StandardButton.Ok)
        save_button.setText("Salvar")
        save_button.setObjectName("story-save-button")
        cancel_button = self._button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_button.setText("Cancelar")
        cancel_button.setObjectName("story-cancel-button")
        layout.addWidget(self._button_box)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._button_box.accepted.connect(self._on_save)
        self._button_box.rejected.connect(self.reject)

        self._viewmodel.saved.connect(self._on_saved)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.features_loaded.connect(self._on_features_loaded)
        self._viewmodel.developers_loaded.connect(self._on_developers_loaded)

        # Form changes
        self._component_edit.textChanged.connect(self._on_component_changed)
        self._name_edit.textChanged.connect(self._on_name_changed)
        self._sp_combo.currentIndexChanged.connect(self._on_sp_changed)
        self._feature_combo.currentIndexChanged.connect(self._on_feature_changed)
        self._developer_combo.currentIndexChanged.connect(self._on_developer_changed)
        self._status_combo.currentIndexChanged.connect(self._on_status_changed)

        # Install event filter for focusOut validation
        self._component_edit.installEventFilter(self)
        self._name_edit.installEventFilter(self)

    def _load_story_to_form(self) -> None:
        """Load story data from ViewModel to form fields."""
        self._component_edit.setText(self._viewmodel.component)
        self._name_edit.setText(self._viewmodel.name)

        # Set story points
        sp_index = VALID_STORY_POINTS.index(self._viewmodel.story_points)
        self._sp_combo.setCurrentIndex(sp_index)

        # Feature will be set after features are loaded
        # Pre-select current status
        status_index = self._status_combo.findData(self._viewmodel.status)
        if status_index >= 0:
            self._status_combo.setCurrentIndex(status_index)

        # Component is read-only in edit mode
        self._component_edit.setEnabled(self._viewmodel.mode == "create")

    async def _load_features(self) -> None:
        """Load features into the dropdown."""
        await self._viewmodel.load_features()

    async def _load_developers(self) -> None:
        """Load developers into the dropdown."""
        await self._viewmodel.load_developers()

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

    @Slot(list)
    def _on_developers_loaded(self, developers: list[DeveloperOutputDTO]) -> None:
        """Handle developers_loaded signal.

        Args:
            developers: List of developer DTOs.
        """
        self._developer_combo.clear()
        self._developer_combo.addItem("Nenhum", None)

        for dev in developers:
            self._developer_combo.addItem(dev.name, dev.id)

        # Pre-select current developer
        if self._viewmodel.developer_id is not None:
            index = self._developer_combo.findData(self._viewmodel.developer_id)
            if index >= 0:
                self._developer_combo.setCurrentIndex(index)

    @Slot(int)
    def _on_developer_changed(self, index: int) -> None:
        """Handle developer selection change."""
        developer_id = self._developer_combo.itemData(index)
        self._viewmodel.developer_id = developer_id

    @Slot(int)
    def _on_status_changed(self, index: int) -> None:
        """Handle status selection change."""
        status = self._status_combo.itemData(index)
        self._viewmodel.status = status

    @Slot(str)
    def _on_component_changed(self, text: str) -> None:
        """Handle component text change."""
        self._viewmodel.component = text
        self._error_label.hide()

        # Update char count
        count = len(text)
        self._component_char_count.setText(f"{count}/50")
        warning = "true" if count >= 45 else "false"
        self._component_char_count.setProperty("warning", warning)
        self._component_char_count.style().unpolish(self._component_char_count)
        self._component_char_count.style().polish(self._component_char_count)

        # Re-validate and re-enable save if field is now valid (ADR-004)
        is_valid, _ = self._viewmodel.validate_field("component")
        if is_valid:
            self._component_edit.setProperty("error", "false")
            self._component_edit.style().unpolish(self._component_edit)
            self._component_edit.style().polish(self._component_edit)
            self._component_error_label.hide()
            self._update_save_button_state()

    @Slot(str)
    def _on_name_changed(self, text: str) -> None:
        """Handle name text change."""
        self._viewmodel.name = text
        self._error_label.hide()

        # Update char count
        count = len(text)
        self._name_char_count.setText(f"{count}/200")
        warning = "true" if count >= 180 else "false"
        self._name_char_count.setProperty("warning", warning)
        self._name_char_count.style().unpolish(self._name_char_count)
        self._name_char_count.style().polish(self._name_char_count)

        # Re-validate and re-enable save if field is now valid (ADR-004)
        is_valid, _ = self._viewmodel.validate_field("name")
        if is_valid:
            self._name_edit.setProperty("error", "false")
            self._name_edit.style().unpolish(self._name_edit)
            self._name_edit.style().polish(self._name_edit)
            self._name_error_label.hide()
            self._update_save_button_state()

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
        self._create_task(self._save_story())

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

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Handle focusOut events for on-blur validation.

        Args:
            obj: The watched object.
            event: The event.

        Returns:
            False to continue event propagation.
        """
        if event.type() == QEvent.Type.FocusOut:
            if obj is self._component_edit:
                self._validate_field_ui(
                    "component", self._component_edit, self._component_error_label
                )
            elif obj is self._name_edit:
                self._validate_field_ui("name", self._name_edit, self._name_error_label)
        return super().eventFilter(obj, event)

    def _validate_field_ui(
        self, field_name: str, field: QLineEdit, error_label: QLabel
    ) -> None:
        """Validate a field and update UI accordingly.

        Args:
            field_name: Name of the field for validate_field().
            field: The QLineEdit widget.
            error_label: The error label widget.
        """
        is_valid, msg = self._viewmodel.validate_field(field_name)
        if is_valid:
            field.setProperty("error", "false")
            error_label.hide()
        else:
            field.setProperty("error", "true")
            error_label.setText(msg)
            error_label.show()
        field.style().unpolish(field)
        field.style().polish(field)
        self._update_save_button_state()

    def _update_save_button_state(self) -> None:
        """Update save button enabled state based on field validity."""
        comp_valid, _ = self._viewmodel.validate_field("component")
        name_valid, _ = self._viewmodel.validate_field("name")
        save_button = self._button_box.button(QDialogButtonBox.StandardButton.Ok)
        save_button.setEnabled(comp_valid and name_valid)
