"""Dialog para alocacao manual de desenvolvedor a uma historia."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Qt, Slot
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.domain.services.scheduling_service import SchedulingService
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
from backlog_manager.presentation.theme import DESIGN_TOKENS
from backlog_manager.presentation.views.date_picker import DatePicker

if TYPE_CHECKING:
    from backlog_manager.application.dto.allocation.get_developer_availability_dto import (
        GetDeveloperAvailabilityOutputDTO,
    )
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ManualAllocationDialog(QDialog):
    """Dialog para alocacao manual de desenvolvedor a uma historia."""

    def __init__(
        self,
        container: DIContainer,
        story_id: str,
        story_name: str,
        current_developer_id: int | None,
        current_start_date: date | None,
        current_end_date: date | None,
        parent: QWidget | None = None,
    ) -> None:
        """Inicializa o dialog de alocacao manual.

        Args:
            container: Dependency injection container.
            story_id: ID da historia.
            story_name: Nome da historia.
            current_developer_id: ID do desenvolvedor atual (ou None).
            current_start_date: Data de inicio atual (ou None).
            current_end_date: Data de fim atual (ou None).
            parent: Widget pai.
        """
        super().__init__(parent)
        self._container = container
        self._viewmodel = container.manual_allocation_dialog_viewmodel
        self._story_id = story_id
        self._story_name = story_name
        self._current_developer_id = current_developer_id
        self._current_start_date = current_start_date
        self._current_end_date = current_end_date

        self._setup_ui()
        self._connect_signals()

        # Check preconditions
        if current_start_date is None or current_end_date is None:
            self._show_message("Execute o agendamento antes de alocar manualmente.")
            return

        # Load data
        self._viewmodel.reset()
        self._viewmodel.load_developers(story_id, current_start_date)

        logger.debug("ManualAllocationDialog initialized for %s", story_id)

    @property
    def selected_developer_id(self) -> int | None:
        """ID do desenvolvedor selecionado."""
        return self._viewmodel.selected_developer_id

    @property
    def new_start_date(self) -> date | None:
        """Nova data de inicio (se alterada)."""
        return self._viewmodel.new_start_date

    @property
    def new_end_date(self) -> date | None:
        """Nova data de fim (se alterada)."""
        return self._viewmodel.new_end_date

    def _setup_ui(self) -> None:
        """Cria e configura a UI do dialog."""
        self.setWindowTitle("Alocar Desenvolvedor")
        self.setFixedSize(500, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Story info header
        story_label = QLabel(f"Historia: {self._story_id} - {self._story_name}")
        story_label.setWordWrap(True)
        font = story_label.font()
        font.setWeight(QFont.Weight.DemiBold)
        story_label.setFont(font)
        layout.addWidget(story_label)

        # Period label
        if self._current_start_date and self._current_end_date:
            period_text = (
                f"Periodo: {self._current_start_date.strftime('%d/%m/%Y')} - "
                f"{self._current_end_date.strftime('%d/%m/%Y')}"
            )
        else:
            period_text = "Periodo: nao calculado"
        self._period_label = QLabel(period_text)
        self._period_label.setStyleSheet(f"color: {DESIGN_TOKENS['text-secondary']};")
        layout.addWidget(self._period_label)

        # Date picker
        date_layout = QHBoxLayout()
        date_label = QLabel("Data de Inicio:")

        # Set minimum to next workday after today
        holidays = BRAZILIAN_HOLIDAYS_2026_2028
        tomorrow = date.today() + timedelta(days=1)
        min_date = SchedulingService.next_workday(tomorrow, holidays)

        self._date_edit = DatePicker(min_date=min_date)

        if self._current_start_date:
            effective_date = self._current_start_date
            if effective_date < min_date:
                effective_date = min_date
            self._date_edit.set_date(effective_date)

        date_layout.addWidget(date_label)
        date_layout.addWidget(self._date_edit, stretch=1)
        layout.addLayout(date_layout)

        # Developer tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setRootIsDecorated(True)
        self._tree.setIndentation(20)
        self._tree.setStyleSheet(
            f"QTreeWidget {{ font-size: {DESIGN_TOKENS['font-size-base']}; }}"
        )
        layout.addWidget(self._tree, stretch=1)

        # Message label (for edge cases)
        self._message_label = QLabel()
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)
        self._message_label.setStyleSheet(
            f"color: {DESIGN_TOKENS['text-muted']}; padding: 20px;"
        )
        self._message_label.setVisible(False)
        layout.addWidget(self._message_label)

        # Buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        self._btn_confirm = self._button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._btn_confirm.setText("Confirmar")
        self._btn_confirm.setEnabled(False)
        self._btn_cancel = self._button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )
        self._btn_cancel.setText("Cancelar")
        layout.addWidget(self._button_box)

    def _connect_signals(self) -> None:
        """Conecta sinais do viewmodel e widgets."""
        self._viewmodel.developers_loaded.connect(self._on_developers_loaded)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.allocation_confirmed.connect(self._on_allocation_confirmed)
        self._tree.itemClicked.connect(self._on_item_clicked)
        self._date_edit.dateChanged.connect(self._on_date_changed)
        self._button_box.accepted.connect(self._on_confirm)
        self._button_box.rejected.connect(self.reject)

    def _show_message(self, text: str) -> None:
        """Exibe mensagem centralizada no lugar da tree."""
        self._tree.setVisible(False)
        self._message_label.setText(text)
        self._message_label.setVisible(True)
        self._btn_confirm.setEnabled(False)
        self._date_edit.setEnabled(False)

    @Slot(object)
    def _on_developers_loaded(self, data: GetDeveloperAvailabilityOutputDTO) -> None:
        """Atualiza tree com dados de disponibilidade."""
        self._tree.clear()
        self._tree.setVisible(True)
        self._message_label.setVisible(False)

        if not data.developers:
            self._show_message("Nenhum desenvolvedor cadastrado.")
            return

        # Update period label
        self._period_label.setText(
            f"Periodo: {data.story_start_date.strftime('%d/%m/%Y')} - "
            f"{data.story_end_date.strftime('%d/%m/%Y')}"
        )

        free_devs = [d for d in data.developers if d.is_available]
        busy_devs = [d for d in data.developers if not d.is_available]

        # Free section
        free_section = QTreeWidgetItem(self._tree, [f"Livres ({len(free_devs)})"])
        free_section.setExpanded(True)
        free_section.setFlags(Qt.ItemFlag.ItemIsEnabled)
        section_font = free_section.font(0)
        section_font.setWeight(QFont.Weight.DemiBold)
        free_section.setFont(0, section_font)

        for dev in free_devs:
            label = dev.developer_name
            suffix = f"  {dev.story_count} hist"
            if dev.is_recommended:
                label = f"\u2605 {label} (Recomendado)"
            item = QTreeWidgetItem(free_section, [f"{label}{suffix}"])
            item.setData(0, Qt.ItemDataRole.UserRole, dev.developer_id)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            # Pre-select if this was the current developer
            if dev.developer_id == self._current_developer_id:
                self._tree.setCurrentItem(item)
                self._viewmodel.selected_developer_id = dev.developer_id
                self._btn_confirm.setEnabled(True)

        # Occupied section
        busy_section = QTreeWidgetItem(self._tree, [f"Ocupados ({len(busy_devs)})"])
        busy_section.setExpanded(True)
        busy_section.setFlags(Qt.ItemFlag.ItemIsEnabled)
        busy_section.setFont(0, section_font)

        for dev in busy_devs:
            label = f"{dev.developer_name}  {dev.story_count} hist"
            item = QTreeWidgetItem(busy_section, [label])
            item.setData(0, Qt.ItemDataRole.UserRole, dev.developer_id)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(0, Qt.GlobalColor.gray)

            # Add blocking stories as sub-items
            for blocking in dev.blocking_stories:
                sub_label = (
                    f"{blocking.story_id} "
                    f"({blocking.start_date.strftime('%d/%m')} - "
                    f"{blocking.end_date.strftime('%d/%m')})"
                )
                sub_item = QTreeWidgetItem(item, [sub_label])
                sub_item.setFlags(Qt.ItemFlag.NoItemFlags)
                sub_item.setForeground(0, Qt.GlobalColor.gray)
                sub_font = sub_item.font(0)
                sub_font.setPointSize(sub_font.pointSize() - 1)
                sub_item.setFont(0, sub_font)

    @Slot(QTreeWidgetItem, int)
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """Trata clique em item da tree."""
        dev_id = item.data(0, Qt.ItemDataRole.UserRole)
        if dev_id is not None and (item.flags() & Qt.ItemFlag.ItemIsSelectable):
            self._viewmodel.selected_developer_id = dev_id
            self._btn_confirm.setEnabled(True)
        else:
            self._viewmodel.selected_developer_id = None
            self._btn_confirm.setEnabled(False)

    @Slot(QDate)
    def _on_date_changed(self, qdate: QDate) -> None:
        """Recalcula disponibilidade ao alterar data de inicio."""
        new_date = date(qdate.year(), qdate.month(), qdate.day())

        # Auto-correct to next workday
        holidays = BRAZILIAN_HOLIDAYS_2026_2028
        corrected = SchedulingService.next_workday(new_date, holidays)
        if corrected != new_date:
            self._date_edit.blockSignals(True)
            self._date_edit.setDate(
                QDate(corrected.year, corrected.month, corrected.day)
            )
            self._date_edit.blockSignals(False)
            new_date = corrected

        self._btn_confirm.setEnabled(False)
        self._viewmodel.selected_developer_id = None
        self._viewmodel.on_date_changed(new_date)

    @Slot()
    def _on_confirm(self) -> None:
        """Confirma alocacao."""
        self._viewmodel.confirm_allocation()

    @Slot()
    def _on_allocation_confirmed(self) -> None:
        """Fecha dialog apos confirmacao."""
        self.accept()

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Exibe erro."""
        self._show_message(f"Erro: {message}")
        logger.warning("Manual allocation error: %s", message)
