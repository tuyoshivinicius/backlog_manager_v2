"""Feature Dialog View.

This module provides a QDialog for managing features.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
)

from backlog_manager.application.dto.feature import (
    CreateFeatureInputDTO,
    FeatureOutputDTO,
    UpdateFeatureInputDTO,
)
from backlog_manager.domain.exceptions import (
    BacklogManagerException,
    DuplicateWaveException,
    FeatureHasStoriesException,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class FeatureDialog(QDialog):
    """Dialog for managing features.

    Provides CRUD operations for features with wave validation.

    Signals:
        features_changed: Emitted when feature list changes.
    """

    features_changed = Signal()

    def __init__(
        self,
        container: DIContainer,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            container: Dependency injection container.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._container = container
        self._editing_feature_id: int | None = None

        self._setup_ui()
        self._connect_signals()

        # Load initial data
        QTimer.singleShot(0, lambda: asyncio.create_task(self._load_features()))

        logger.debug("FeatureDialog initialized")

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setWindowTitle("Gerenciar Features")
        self.setMinimumWidth(450)
        self.setMinimumHeight(400)
        self.setModal(True)
        self.setObjectName("feature-dialog")

        layout = QVBoxLayout(self)

        # Feature list with empty state
        self._feature_list = QListWidget()
        self._feature_list.setObjectName("feature-list")

        self._empty_state_label = QLabel(
            "Nenhuma feature cadastrada. Clique em Adicionar para comecar."
        )
        self._empty_state_label.setObjectName("feature-empty-state")
        self._empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state_label.setWordWrap(True)

        self._stacked_widget = QStackedWidget()
        self._stacked_widget.setObjectName("feature-stacked")
        self._stacked_widget.addWidget(self._feature_list)
        self._stacked_widget.addWidget(self._empty_state_label)

        layout.addWidget(self._stacked_widget)

        # Form for add/edit
        form_layout = QFormLayout()

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Nome da feature")
        self._name_edit.setMaxLength(100)
        form_layout.addRow("Nome:", self._name_edit)

        self._wave_spinbox = QSpinBox()
        self._wave_spinbox.setMinimum(1)
        self._wave_spinbox.setMaximum(100)
        self._wave_spinbox.setValue(1)
        form_layout.addRow("Onda:", self._wave_spinbox)

        layout.addLayout(form_layout)

        # Action buttons
        action_layout = QHBoxLayout()

        self._add_button = QPushButton("Adicionar")
        self._add_button.setToolTip("Adicionar nova feature")
        action_layout.addWidget(self._add_button)

        self._save_button = QPushButton("Salvar")
        self._save_button.setToolTip("Salvar alteracoes")
        self._save_button.setEnabled(False)
        self._save_button.hide()
        action_layout.addWidget(self._save_button)

        self._cancel_edit_button = QPushButton("Cancelar Edicao")
        self._cancel_edit_button.setToolTip("Cancelar edicao")
        self._cancel_edit_button.hide()
        action_layout.addWidget(self._cancel_edit_button)

        self._remove_button = QPushButton("Remover")
        self._remove_button.setToolTip("Remover feature selecionada")
        self._remove_button.setEnabled(False)
        action_layout.addWidget(self._remove_button)

        layout.addLayout(action_layout)

        # Close button
        self._close_button = QPushButton("Fechar")
        layout.addWidget(self._close_button)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._add_button.clicked.connect(self._on_add)
        self._save_button.clicked.connect(self._on_save)
        self._cancel_edit_button.clicked.connect(self._on_cancel_edit)
        self._remove_button.clicked.connect(self._on_remove)
        self._close_button.clicked.connect(self.accept)

        self._feature_list.currentItemChanged.connect(self._on_selection_changed)
        self._feature_list.itemDoubleClicked.connect(self._on_edit)

    async def _load_features(self) -> None:
        """Load features into the list."""
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_features_use_case(uow)
                result = await use_case.execute()

                self._feature_list.clear()
                for feature in sorted(result.features, key=lambda f: f.wave):
                    item = QListWidgetItem(f"Onda {feature.wave} \u2014 {feature.name}")
                    item.setData(Qt.ItemDataRole.UserRole, feature.id)
                    item.setData(Qt.ItemDataRole.UserRole + 1, feature.name)
                    item.setData(Qt.ItemDataRole.UserRole + 2, feature.wave)
                    self._feature_list.addItem(item)

                logger.debug("Loaded %d features", len(result.features))
                self._update_empty_state()
        except Exception as e:
            logger.exception("Error loading features")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar features: {e}")

    def _update_empty_state(self) -> None:
        """Toggle between list and empty state based on item count."""
        if self._feature_list.count() > 0:
            self._stacked_widget.setCurrentIndex(0)
        else:
            self._stacked_widget.setCurrentIndex(1)

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection change in list."""
        has_selection = self._feature_list.currentItem() is not None
        self._remove_button.setEnabled(
            has_selection and self._editing_feature_id is None
        )

    @Slot()
    def _on_add(self) -> None:
        """Handle add button click."""
        name = self._name_edit.text().strip()
        wave = self._wave_spinbox.value()

        if not name:
            QMessageBox.warning(self, "Erro", "Nome da feature e obrigatorio.")
            return

        asyncio.create_task(self._create_feature(name, wave))

    async def _create_feature(self, name: str, wave: int) -> None:
        """Create a new feature.

        Args:
            name: Feature name.
            wave: Feature wave.
        """
        try:
            dto = CreateFeatureInputDTO(name=name, wave=wave)
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_feature_use_case_factory(uow)
                await use_case.execute(dto)

            self._name_edit.clear()
            self._wave_spinbox.setValue(1)
            await self._load_features()
            self.features_changed.emit()
            logger.info("Created feature: %s (wave %d)", name, wave)
        except DuplicateWaveException as e:
            QMessageBox.warning(
                self,
                "Onda Duplicada",
                f"Ja existe uma feature na onda {wave}.\n"
                f"Feature existente: {e.existing_feature_name}",
            )
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error creating feature")
            QMessageBox.warning(self, "Erro", f"Erro ao criar feature: {e}")

    @Slot()
    def _on_edit(self) -> None:
        """Handle double-click for editing."""
        item = self._feature_list.currentItem()
        if not item:
            return

        self._editing_feature_id = item.data(Qt.ItemDataRole.UserRole)
        feature_name = item.data(Qt.ItemDataRole.UserRole + 1)
        feature_wave = item.data(Qt.ItemDataRole.UserRole + 2)

        self._name_edit.setText(feature_name)
        self._wave_spinbox.setValue(feature_wave)

        # Switch to edit mode
        self._add_button.hide()
        self._save_button.show()
        self._save_button.setEnabled(True)
        self._cancel_edit_button.show()
        self._remove_button.setEnabled(False)

    @Slot()
    def _on_save(self) -> None:
        """Handle save button click (edit mode)."""
        if not self._editing_feature_id:
            return

        name = self._name_edit.text().strip()
        wave = self._wave_spinbox.value()

        if not name:
            QMessageBox.warning(self, "Erro", "Nome da feature e obrigatorio.")
            return

        asyncio.create_task(self._update_feature(self._editing_feature_id, name, wave))

    async def _update_feature(self, feature_id: int, name: str, wave: int) -> None:
        """Update an existing feature.

        Args:
            feature_id: Feature ID.
            name: New feature name.
            wave: New feature wave.
        """
        try:
            dto = UpdateFeatureInputDTO(feature_id=feature_id, name=name, wave=wave)
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_update_feature_use_case(uow)
                await use_case.execute(dto)

            self._cancel_editing_mode()
            await self._load_features()
            self.features_changed.emit()
            logger.info("Updated feature %d: %s (wave %d)", feature_id, name, wave)
        except DuplicateWaveException as e:
            QMessageBox.warning(
                self,
                "Onda Duplicada",
                f"Ja existe uma feature na onda {wave}.\n"
                f"Feature existente: {e.existing_feature_name}",
            )
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error updating feature")
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar feature: {e}")

    @Slot()
    def _on_cancel_edit(self) -> None:
        """Handle cancel edit button click."""
        self._cancel_editing_mode()

    def _cancel_editing_mode(self) -> None:
        """Cancel editing mode and restore add mode."""
        self._editing_feature_id = None
        self._name_edit.clear()
        self._wave_spinbox.setValue(1)

        self._add_button.show()
        self._save_button.hide()
        self._cancel_edit_button.hide()
        self._remove_button.setEnabled(self._feature_list.currentItem() is not None)

    @Slot()
    def _on_remove(self) -> None:
        """Handle remove button click."""
        item = self._feature_list.currentItem()
        if not item:
            return

        feature_id = item.data(Qt.ItemDataRole.UserRole)
        feature_name = item.data(Qt.ItemDataRole.UserRole + 1)

        reply = QMessageBox.question(
            self,
            "Confirmar Remocao",
            f"Deseja remover a feature '{feature_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._delete_feature(feature_id))

    async def _delete_feature(self, feature_id: int) -> None:
        """Delete a feature.

        Args:
            feature_id: Feature ID to delete.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_delete_feature_use_case(uow)
                await use_case.execute(feature_id)

            await self._load_features()
            self.features_changed.emit()
            logger.info("Deleted feature %d", feature_id)
        except FeatureHasStoriesException as e:
            QMessageBox.warning(
                self,
                "Feature em Uso",
                f"Nao e possivel remover a feature '{e.feature_name}'.\n"
                f"Ela possui {e.story_count} historias associadas.",
            )
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error deleting feature")
            QMessageBox.warning(self, "Erro", f"Erro ao remover feature: {e}")
