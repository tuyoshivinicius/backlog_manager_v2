"""MonospaceDelegate for rendering text in monospace font.

This delegate renders text values using a monospace font family
with fallback chain for cross-platform compatibility.
"""

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QFont, QFontDatabase, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget


class MonospaceDelegate(QStyledItemDelegate):
    """Delegate for rendering text in monospace font.

    Uses a fallback chain of monospace fonts:
    1. JetBrains Mono (modern, readable)
    2. Cascadia Code (Windows 11 default)
    3. Consolas (Windows fallback)
    4. monospace (system default)

    Example:
        >>> delegate = MonospaceDelegate(table_view)
        >>> table_view.setItemDelegateForColumn(ID_COLUMN, delegate)
    """

    # Monospace font fallback chain
    FONT_FAMILIES = ["JetBrains Mono", "Cascadia Code", "Consolas", "monospace"]

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the delegate.

        Args:
            parent: Parent widget (typically the QTableView).
        """
        super().__init__(parent)
        self._font_family = self._find_available_font()

    def _find_available_font(self) -> str:
        """Find the first available font from the fallback chain.

        Returns:
            Name of the first available font family.
        """
        available_families = QFontDatabase.families()

        for family in self.FONT_FAMILIES:
            if family in available_families:
                return family

        # Fallback to generic monospace
        return "monospace"

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """Paint the text in monospace font.

        Args:
            painter: QPainter instance to use for drawing.
            option: Style options for the item.
            index: Model index of the item being painted.
        """
        # Create a copy of the option with modified font
        modified_option = QStyleOptionViewItem(option)

        # Set monospace font
        font = modified_option.font
        font.setFamily(self._font_family)
        font.setStyleHint(QFont.StyleHint.Monospace)
        modified_option.font = font

        # Delegate to parent class for actual rendering
        super().paint(painter, modified_option, index)

    def get_font_family(self) -> str:
        """Get the selected monospace font family.

        Returns:
            The font family name being used.
        """
        return self._font_family
