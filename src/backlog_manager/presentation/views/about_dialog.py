"""About Dialog View.

Displays application information: name, version, technologies, and database path.
"""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from backlog_manager.presentation.theme import DESIGN_TOKENS

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class AboutDialog(QDialog):
    """About dialog showing application information.

    Displays app name, version, Python version, technology list, and DB path.
    Fixed size 400x300px per Contract 6.
    """

    def __init__(self, db_path: Path, parent: QWidget | None = None) -> None:
        """Initialize the dialog.

        Args:
            db_path: Path to the SQLite database.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Sobre")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # App name
        name_label = QLabel("Backlog Manager")
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        try:
            version = importlib.metadata.version("backlog-manager")
        except importlib.metadata.PackageNotFoundError:
            version = "dev"

        version_label = QLabel(f"Versao: {version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # Python version
        python_label = QLabel(f"Python: {sys.version.split()[0]}")
        python_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(python_label)

        layout.addSpacing(8)

        # Technologies
        tech_label = QLabel("Tecnologias: Python, PySide6, SQLite, Pydantic, qasync")
        tech_label.setWordWrap(True)
        tech_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tech_label)

        layout.addSpacing(8)

        # Database path
        db_label = QLabel(f"Banco de dados:\n{db_path}")
        db_label.setWordWrap(True)
        db_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        db_label.setStyleSheet(f"color: {DESIGN_TOKENS['text-muted']}; font-size: 9pt;")
        layout.addWidget(db_label)

        layout.addStretch()
