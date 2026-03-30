"""Rich Tooltip Widget for table hover.

Displays a mini-card popup with complete story details after 300ms hover.
"""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.presentation.theme import DESIGN_TOKENS, STATUS_PALETTE


class RichTooltipWidget(QWidget):
    """Rich tooltip mini-card showing complete story details.

    Displayed as a frameless popup near the cursor position.
    """

    MAX_WIDTH = 350

    def __init__(self, data: dict[str, str], parent: QWidget | None = None) -> None:
        """Initialize the tooltip widget.

        Args:
            data: Dictionary mapping column names to display values.
            parent: Optional parent widget.
        """
        super().__init__(
            parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMaximumWidth(self.MAX_WIDTH)
        self.setStyleSheet(
            f"QWidget {{ background: {DESIGN_TOKENS['background']}; "
            f"border: 1px solid {DESIGN_TOKENS['neutral-300']}; "
            f"border-radius: 6px; padding: 8px; }}"
        )

        self._build_layout(data)

    def _build_layout(self, data: dict[str, str]) -> None:
        """Build the tooltip layout per Contract 4.

        Args:
            data: Column name -> display value mapping.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Row 1: ID + Status badge
        header = QHBoxLayout()
        id_label = QLabel(data.get("ID", "\u2014"))
        id_font = QFont()
        id_font.setBold(True)
        id_font.setPointSize(10)
        id_label.setFont(id_font)
        id_label.setStyleSheet("border: none;")
        header.addWidget(id_label)
        header.addStretch()

        status = data.get("Status", "")
        status_label = QLabel(status)
        status_config = STATUS_PALETTE.get(status.upper())
        if status_config:
            status_label.setStyleSheet(
                f"background: {status_config.background}; "
                f"color: {status_config.foreground}; "
                f"border-radius: 8px; padding: 2px 8px; border: none;"
            )
        else:
            status_label.setStyleSheet("border: none;")
        header.addWidget(status_label)
        layout.addLayout(header)

        # Row 2: Nome
        name_label = QLabel(data.get("Nome", "\u2014"))
        name_label.setWordWrap(True)
        name_label.setStyleSheet(f"color: {DESIGN_TOKENS['text']}; border: none;")
        layout.addWidget(name_label)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(
            f"color: {DESIGN_TOKENS['neutral-200']}; border: none; "
            f"border-top: 1px solid {DESIGN_TOKENS['neutral-200']};"
        )
        layout.addWidget(line)

        # Grid: SP, Feature, Dev, Deps, dates
        grid = QGridLayout()
        grid.setSpacing(4)

        fields = [
            ("SP", data.get("SP", "\u2014")),
            ("Feature", data.get("Feature", "\u2014")),
            ("Dev", data.get("Desenvolvedor", "\u2014")),
            ("Dep", data.get("Dependencias", "\u2014")),
            ("Inicio", data.get("Inicio", "\u2014")),
            ("Fim", data.get("Fim", "\u2014")),
        ]

        for row, (label_text, value) in enumerate(fields):
            lbl = QLabel(f"{label_text}:")
            lbl.setStyleSheet(
                f"color: {DESIGN_TOKENS['text-muted']}; font-size: 9pt; border: none;"
            )
            val = QLabel(value)
            val.setStyleSheet(
                f"color: {DESIGN_TOKENS['text']}; font-size: 9pt; border: none;"
            )
            val.setWordWrap(True)
            grid.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(val, row, 1, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(grid)

    def sizeHint(self) -> QSize:
        """Return preferred size."""
        return QSize(
            min(self.MAX_WIDTH, super().sizeHint().width()), super().sizeHint().height()
        )
