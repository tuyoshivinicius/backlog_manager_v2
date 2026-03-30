"""Result Dialog View.

This module provides a QDialog for showing operation results.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ResultDialog(QDialog):
    """Dialog for displaying operation results (import/export)."""

    def __init__(
        self,
        title: str,
        details: str,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            title: Title text.
            details: Details text.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self.setObjectName("result-dialog")
        self.setWindowTitle("Resultado")
        self.setMinimumWidth(350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self._title_label = QLabel(title)
        self._title_label.setObjectName("result-title")
        self._title_label.setWordWrap(True)
        layout.addWidget(self._title_label)

        self._details_label = QLabel(details)
        self._details_label.setObjectName("result-details")
        self._details_label.setWordWrap(True)
        layout.addWidget(self._details_label)

        self._close_button = QPushButton("Fechar")
        self._close_button.setObjectName("result-close-button")
        self._close_button.clicked.connect(self.accept)
        layout.addWidget(self._close_button)

        logger.debug("ResultDialog initialized")

    @classmethod
    def for_import(
        cls,
        stories_count: int,
        features_count: int,
        warnings_count: int,
        parent: QWidget | None = None,
    ) -> ResultDialog:
        """Create a result dialog for import operation.

        Args:
            stories_count: Number of stories imported.
            features_count: Number of features imported.
            warnings_count: Number of warnings.
            parent: Optional parent widget.

        Returns:
            Configured ResultDialog.
        """
        title = "Importacao Concluida"
        details = (
            f"Historias importadas: {stories_count}\n"
            f"Features importadas: {features_count}\n"
            f"Avisos: {warnings_count}"
        )
        return cls(title=title, details=details, parent=parent)

    @classmethod
    def for_export(
        cls,
        file_path: str,
        parent: QWidget | None = None,
    ) -> ResultDialog:
        """Create a result dialog for export operation.

        Args:
            file_path: Path to the exported file.
            parent: Optional parent widget.

        Returns:
            Configured ResultDialog.
        """
        title = "Exportacao Concluida"
        details = f"Arquivo salvo em: {file_path}"
        return cls(title=title, details=details, parent=parent)
