"""StatusBadgeDelegate for rendering status badges in QTableView.

This delegate renders status values as pill-shaped badges with
non-chromatic symbols for accessibility (WCAG compliant).
"""

from typing import cast

from PySide6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
    QRect,
    QSize,
    Qt,
    QTimer,
)
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from backlog_manager.presentation.constants import STATUS_LABELS
from backlog_manager.presentation.theme import (
    DESIGN_TOKENS,
    STATUS_PALETTE,
    StatusConfig,
)


class StatusBadgeDelegate(QStyledItemDelegate):
    """Delegate for rendering status badges with symbols and colors.

    Renders status values as pill-shaped badges with:
    - Background color based on status
    - Foreground (text) color based on status
    - Non-chromatic symbol for accessibility (e.g., ●, ▶, ✓)

    All colors are WCAG AA compliant with contrast ratio >= 4.5:1.

    Example:
        >>> delegate = StatusBadgeDelegate(table_view)
        >>> table_view.setItemDelegateForColumn(STATUS_COLUMN, delegate)
    """

    # Minimum badge dimensions
    MIN_BADGE_HEIGHT = 24
    MIN_BADGE_WIDTH = 80
    BADGE_PADDING_H = 8
    BADGE_PADDING_V = 4
    BORDER_RADIUS = 12

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the delegate.

        Args:
            parent: Parent widget (typically the QTableView).
        """
        super().__init__(parent)
        self._default_config = StatusConfig(
            symbol="?",
            background="#E5E5E5",
            foreground="#525252",
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the status badge.

        Args:
            painter: QPainter instance to use for drawing.
            option: Style options for the item.
            index: Model index of the item being painted.
        """
        painter.save()
        try:
            # Get status value from model
            status = index.data(Qt.ItemDataRole.DisplayRole)
            if status is None:
                super().paint(painter, option, index)
                return

            # Convert to string and uppercase for lookup
            status_str = str(status).upper()

            # Get status configuration
            config = STATUS_PALETTE.get(status_str, self._default_config)

            # Draw cell background (wave tint or selection)
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, QColor(DESIGN_TOKENS["selection-bg"]))
            else:
                bg = index.data(Qt.ItemDataRole.BackgroundRole)
                if bg is not None:
                    painter.fillRect(option.rect, bg)

            # Calculate badge rect centered in cell
            badge_rect = self._calculate_badge_rect(option.rect, status_str, config)

            # Draw pill background
            self._draw_badge_background(painter, badge_rect, config)

            # Draw symbol and text
            self._draw_badge_content(painter, badge_rect, status_str, config, option)

        finally:
            painter.restore()

    def _calculate_badge_rect(
        self, cell_rect: QRect, status: str, config: StatusConfig
    ) -> QRect:
        """Calculate the badge rectangle centered in the cell.

        Args:
            cell_rect: The cell's bounding rectangle.
            status: The status string.
            config: Status configuration with symbol.

        Returns:
            QRect for the badge, centered in the cell.
        """
        # Calculate text width to determine badge width
        text = f"{config.symbol} {status}"
        # Use a standard font size for calculation
        font = QFont()
        font.setPointSize(9)
        from PySide6.QtGui import QFontMetrics

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)

        badge_width = max(self.MIN_BADGE_WIDTH, text_width + 2 * self.BADGE_PADDING_H)
        badge_height = self.MIN_BADGE_HEIGHT

        # Center in cell
        x = cell_rect.x() + (cell_rect.width() - badge_width) // 2
        y = cell_rect.y() + (cell_rect.height() - badge_height) // 2

        return QRect(x, y, badge_width, badge_height)

    def _draw_badge_background(
        self, painter: QPainter, rect: QRect, config: StatusConfig
    ) -> None:
        """Draw the pill-shaped badge background.

        Args:
            painter: QPainter to use.
            rect: Badge rectangle.
            config: Status configuration with colors.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set up brush and pen
        bg_color = QColor(config.background)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw rounded rectangle (pill shape)
        painter.drawRoundedRect(rect, self.BORDER_RADIUS, self.BORDER_RADIUS)

    def _draw_badge_content(
        self,
        painter: QPainter,
        rect: QRect,
        status: str,
        config: StatusConfig,
        option: QStyleOptionViewItem,
    ) -> None:
        """Draw the symbol and text inside the badge.

        Args:
            painter: QPainter to use.
            rect: Badge rectangle.
            status: Status string to display.
            config: Status configuration with symbol and colors.
            option: Style options for selection state.
        """
        # Set text color
        fg_color = QColor(config.foreground)
        painter.setPen(QPen(fg_color))

        # Set font
        font = painter.font()
        font.setPointSize(9)
        font.setWeight(QFont.Weight.Medium)
        painter.setFont(font)

        # Draw centered text with symbol
        text = f"{config.symbol} {status}"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        """Return the preferred size for the badge.

        Args:
            option: Style options.
            index: Model index.

        Returns:
            QSize with minimum dimensions for the badge.
        """
        return QSize(self.MIN_BADGE_WIDTH + 20, self.MIN_BADGE_HEIGHT + 8)

    def createEditor(
        self,
        parent: QWidget,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QWidget:
        """Create a QComboBox editor for inline status change."""
        combo = QComboBox(parent)
        for value, label in STATUS_LABELS:
            combo.addItem(label, value)
        combo.currentIndexChanged.connect(lambda: self.commitData.emit(combo))
        combo.currentIndexChanged.connect(lambda: self.closeEditor.emit(combo))
        return combo

    def setEditorData(
        self, editor: QWidget, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        """Pre-select the current status in the combo box."""
        combo = cast(QComboBox, editor)
        current_status = index.data(Qt.ItemDataRole.DisplayRole)
        if current_status:
            idx = combo.findData(str(current_status).upper())
            if idx >= 0:
                combo.setCurrentIndex(idx)
        QTimer.singleShot(0, combo.showPopup)

    def setModelData(
        self,
        editor: QWidget,
        model: QAbstractItemModel,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Pass the selected status value to the model."""
        combo = cast(QComboBox, editor)
        selected_value = combo.currentData()
        if selected_value:
            model.setData(index, selected_value, Qt.ItemDataRole.EditRole)
