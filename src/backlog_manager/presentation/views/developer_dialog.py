"""Developer Dialog View.

This module provides a QDialog for managing developers.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)

from backlog_manager.application.dto.developer import (
    CreateDeveloperInputDTO,
    DeveloperOutputDTO,
    UpdateDeveloperInputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException
from backlog_manager.presentation.theme.theme import get_icon_manager

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class DeveloperDialog(QDialog):
    """Dialog for managing developers.

    Provides CRUD operations for developers through a list interface.

    Signals:
        developers_changed: Emitted when developer list changes.
    """

    developers_changed = Signal()

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

        self._setup_ui()
        self._connect_signals()

        # Load initial data
        QTimer.singleShot(0, lambda: asyncio.create_task(self._load_developers()))

        logger.debug("DeveloperDialog initialized")

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setWindowTitle("Gerenciar Desenvolvedores")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setModal(True)
        self.setObjectName("developer-dialog")

        layout = QVBoxLayout(self)

        # Stacked widget for list / empty state
        self._stacked = QStackedWidget()
        self._stacked.setObjectName("developer-stacked")

        # Index 0: Developer list
        self._developer_list = QListWidget()
        self._developer_list.setObjectName("developer-list")
        self._stacked.addWidget(self._developer_list)

        # Index 1: Empty state label
        self._empty_state_label = QLabel(
            "Nenhum desenvolvedor cadastrado. Clique em Adicionar para comecar."
        )
        self._empty_state_label.setObjectName("developer-empty-state")
        self._empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state_label.setWordWrap(True)
        self._stacked.addWidget(self._empty_state_label)

        layout.addWidget(self._stacked)

        # Icons
        icon_mgr = get_icon_manager()
        icon_size = QSize(16, 16)

        # Buttons
        button_layout = QHBoxLayout()

        self._add_button = QPushButton("Adicionar")
        self._add_button.setObjectName("developer-add-button")
        self._add_button.setToolTip("Adicionar novo desenvolvedor")
        self._add_button.setIcon(icon_mgr.get("plus"))
        self._add_button.setIconSize(icon_size)
        button_layout.addWidget(self._add_button)

        self._edit_button = QPushButton("Editar")
        self._edit_button.setObjectName("developer-edit-button")
        self._edit_button.setToolTip("Editar desenvolvedor selecionado")
        self._edit_button.setEnabled(False)
        self._edit_button.setIcon(icon_mgr.get("pencil-simple"))
        self._edit_button.setIconSize(icon_size)
        button_layout.addWidget(self._edit_button)

        self._remove_button = QPushButton("Remover")
        self._remove_button.setObjectName("developer-remove-button")
        self._remove_button.setToolTip("Remover desenvolvedor selecionado")
        self._remove_button.setEnabled(False)
        self._remove_button.setIcon(icon_mgr.get("trash"))
        self._remove_button.setIconSize(icon_size)
        button_layout.addWidget(self._remove_button)

        layout.addLayout(button_layout)

        # Close button
        self._close_button = QPushButton("Fechar")
        self._close_button.setObjectName("developer-close-button")
        self._close_button.setIcon(icon_mgr.get("x"))
        self._close_button.setIconSize(icon_size)
        layout.addWidget(self._close_button)

    def _connect_signals(self) -> None:
        """Connect signals to slots."""
        self._add_button.clicked.connect(self._on_add)
        self._edit_button.clicked.connect(self._on_edit)
        self._remove_button.clicked.connect(self._on_remove)
        self._close_button.clicked.connect(self.accept)

        self._developer_list.currentItemChanged.connect(self._on_selection_changed)
        self._developer_list.itemDoubleClicked.connect(self._on_edit)

    def _update_empty_state(self) -> None:
        """Toggle between list and empty state based on item count."""
        if self._developer_list.count() > 0:
            self._stacked.setCurrentIndex(0)
        else:
            self._stacked.setCurrentIndex(1)

    async def _load_developers(self) -> None:
        """Load developers into the list."""
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_developers_use_case(uow)
                result = await use_case.execute()

                self._developer_list.clear()
                for dev in result.developers:
                    item = QListWidgetItem(dev.name)
                    item.setData(Qt.ItemDataRole.UserRole, dev.id)
                    item.setSizeHint(QSize(0, 40))
                    self._developer_list.addItem(item)

                logger.debug("Loaded %d developers", len(result.developers))
        except Exception as e:
            logger.exception("Error loading developers")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar desenvolvedores: {e}")

        self._update_empty_state()

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle selection change in list."""
        has_selection = self._developer_list.currentItem() is not None
        self._edit_button.setEnabled(has_selection)
        self._remove_button.setEnabled(has_selection)

    @Slot()
    def _on_add(self) -> None:
        """Handle add button click."""
        name, ok = QInputDialog.getText(
            self,
            "Adicionar Desenvolvedor",
            "Nome do desenvolvedor:",
            QLineEdit.EchoMode.Normal,
        )

        if ok and name.strip():
            asyncio.create_task(self._create_developer(name.strip()))

    async def _create_developer(self, name: str) -> None:
        """Create a new developer.

        Args:
            name: Developer name.
        """
        try:
            dto = CreateDeveloperInputDTO(name=name)
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_developer_use_case_factory(uow)
                await use_case.execute(dto)

            await self._load_developers()
            self.developers_changed.emit()
            logger.info("Created developer: %s", name)
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error creating developer")
            QMessageBox.warning(self, "Erro", f"Erro ao criar desenvolvedor: {e}")

        self._update_empty_state()

    @Slot()
    def _on_edit(self) -> None:
        """Handle edit button click."""
        item = self._developer_list.currentItem()
        if not item:
            return

        dev_id = item.data(Qt.ItemDataRole.UserRole)
        current_name = item.text()

        name, ok = QInputDialog.getText(
            self,
            "Editar Desenvolvedor",
            "Nome do desenvolvedor:",
            QLineEdit.EchoMode.Normal,
            current_name,
        )

        if ok and name.strip() and name.strip() != current_name:
            asyncio.create_task(self._update_developer(dev_id, name.strip()))

    async def _update_developer(self, dev_id: int, name: str) -> None:
        """Update an existing developer.

        Args:
            dev_id: Developer ID.
            name: New developer name.
        """
        try:
            dto = UpdateDeveloperInputDTO(developer_id=dev_id, name=name)
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_update_developer_use_case(uow)
                await use_case.execute(dto)

            await self._load_developers()
            self.developers_changed.emit()
            logger.info("Updated developer %d: %s", dev_id, name)
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error updating developer")
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar desenvolvedor: {e}")

    @Slot()
    def _on_remove(self) -> None:
        """Handle remove button click."""
        item = self._developer_list.currentItem()
        if not item:
            return

        dev_id = item.data(Qt.ItemDataRole.UserRole)
        dev_name = item.text()

        reply = QMessageBox.question(
            self,
            "Confirmar Remocao",
            f"Deseja remover o desenvolvedor '{dev_name}'?\n\n"
            "Historias atribuidas a ele serao desalocadas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            asyncio.create_task(self._delete_developer(dev_id))

    async def _delete_developer(self, dev_id: int) -> None:
        """Delete a developer.

        Args:
            dev_id: Developer ID to delete.
        """
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_delete_developer_use_case(uow)
                result = await use_case.execute(dev_id)

            await self._load_developers()
            self.developers_changed.emit()

            if result.stories_unassigned > 0:
                QMessageBox.information(
                    self,
                    "Desenvolvedor Removido",
                    f"Desenvolvedor removido.\n"
                    f"{result.stories_unassigned} historias foram desalocadas.",
                )

            logger.info("Deleted developer %d", dev_id)
        except BacklogManagerException as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            logger.exception("Error deleting developer")
            QMessageBox.warning(self, "Erro", f"Erro ao remover desenvolvedor: {e}")

        self._update_empty_state()
