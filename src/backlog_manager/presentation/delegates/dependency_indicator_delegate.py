"""DependencyIndicatorDelegate for rendering blocking state in QTableView.

This delegate renders a colored circle indicator (red/green) next to
dependency IDs to show blocking state, or an em-dash for no dependencies.
"""

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from backlog_manager.presentation.theme import DESIGN_TOKENS
from backlog_manager.presentation.viewmodels.story_table_model import (
    BLOCKING_STATE_ROLE,
    DEPENDENCY_IDS_ROLE,
    BlockingState,
)

# Colors per Contract 2 — using design system tokens
COLOR_BLOCKED = QColor(DESIGN_TOKENS["error-fg"])
COLOR_FREE = QColor(DESIGN_TOKENS["success-fg"])
CIRCLE_SIZE = 8
CIRCLE_MARGIN = 6


class DependencyIndicatorDelegate(QStyledItemDelegate):
    """Delegate for rendering blocking state indicator in Dependencies column.

    Renders:
    - Red filled circle + dependency IDs for BLOCKED state
    - Green filled circle + dependency IDs for FREE state
    - Em-dash for NONE state (no dependencies)
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the delegate.

        Args:
            parent: Parent widget (typically the QTableView).
        """
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Paint the blocking indicator and dependency text.

        Args:
            painter: QPainter instance.
            option: Style options for the item.
            index: Model index of the item.
        """
        painter.save()
        try:
            blocking_state = index.data(BLOCKING_STATE_ROLE)
            if blocking_state is None:
                super().paint(painter, option, index)
                return

            # Draw cell background (wave tint or selection)
            if option.state & QStyle.StateFlag.State_Selected:
                painter.fillRect(option.rect, QColor(DESIGN_TOKENS["selection-bg"]))
            else:
                bg = index.data(Qt.ItemDataRole.BackgroundRole)
                if bg is not None:
                    painter.fillRect(option.rect, bg)

            if blocking_state == BlockingState.NONE:
                # Draw em-dash centered
                painter.setPen(QPen(option.palette.text().color()))
                painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, "\u2014")
            else:
                # Draw colored circle + dependency IDs
                color = (
                    COLOR_BLOCKED
                    if blocking_state == BlockingState.BLOCKED
                    else COLOR_FREE
                )

                dep_ids = index.data(DEPENDENCY_IDS_ROLE) or []
                text = ", ".join(dep_ids)

                # Circle position: vertically centered, left-aligned with margin
                circle_y = option.rect.y() + (option.rect.height() - CIRCLE_SIZE) // 2
                circle_x = option.rect.x() + CIRCLE_MARGIN

                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setBrush(color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(circle_x, circle_y, CIRCLE_SIZE, CIRCLE_SIZE)

                # Draw text after circle
                text_x = circle_x + CIRCLE_SIZE + CIRCLE_MARGIN
                text_rect = QRect(
                    text_x,
                    option.rect.y(),
                    option.rect.width() - (text_x - option.rect.x()),
                    option.rect.height(),
                )
                painter.setPen(QPen(option.palette.text().color()))
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    text,
                )
        finally:
            painter.restore()

    def sizeHint(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> QSize:
        """Return preferred size for the cell.

        Args:
            option: Style options.
            index: Model index.

        Returns:
            QSize with minimum dimensions.
        """
        return QSize(120, 30)
