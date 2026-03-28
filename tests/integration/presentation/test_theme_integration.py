"""Integration tests for theme loading and application.

Tests cover:
- T018: Theme loading and application
- Theme integration with QApplication
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from backlog_manager.presentation.theme import DESIGN_TOKENS, apply_theme


class TestThemeIntegration:
    """Integration tests for theme system."""

    @pytest.fixture
    def stylesheet_path(self) -> Path:
        """Get path to stylesheet.qss."""
        return (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "backlog_manager"
            / "presentation"
            / "theme"
            / "stylesheet.qss"
        )

    @pytest.fixture
    def qss_template(self, stylesheet_path: Path) -> str:
        """Load stylesheet template."""
        return stylesheet_path.read_text(encoding="utf-8")

    def test_theme_loading_succeeds(self, qss_template: str) -> None:
        """Theme loads without errors (T018)."""
        # Act
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)

        # Assert
        assert stylesheet is not None
        assert len(stylesheet) > 0

    def test_all_placeholders_substituted(self, qss_template: str) -> None:
        """All @var placeholders are substituted after apply_theme."""
        import re

        # Act
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)

        # Remove comments (/* ... */) before checking for placeholders
        content_without_comments = re.sub(r"/\*.*?\*/", "", stylesheet, flags=re.DOTALL)

        # Assert - no @placeholder patterns should remain (excluding comments)
        placeholder_pattern = r"@[a-zA-Z][a-zA-Z0-9-]*"
        remaining = re.findall(placeholder_pattern, content_without_comments)
        assert not remaining, f"Unsubstituted placeholders: {remaining}"

    def test_stylesheet_applies_to_application(
        self, qtbot: pytest.fixture, qss_template: str
    ) -> None:
        """Stylesheet can be applied to QApplication."""
        # Arrange
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)
        app = QApplication.instance()

        # Act
        app.setStyleSheet(stylesheet)

        # Assert
        assert app.styleSheet() == stylesheet

    def test_styled_widget_renders(
        self, qtbot: pytest.fixture, qss_template: str
    ) -> None:
        """Styled widget renders without errors."""
        # Arrange
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)
        app = QApplication.instance()
        app.setStyleSheet(stylesheet)

        # Act
        widget = QWidget()
        button = QPushButton("Test Button", widget)
        qtbot.addWidget(widget)
        widget.show()

        # Assert
        assert button.isVisible()

    def test_theme_contains_primary_color(self, qss_template: str) -> None:
        """Stylesheet contains primary color after substitution."""
        # Act
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)

        # Assert
        assert DESIGN_TOKENS["primary"] in stylesheet

    def test_theme_contains_font_family(self, qss_template: str) -> None:
        """Stylesheet contains font family after substitution."""
        # Act
        stylesheet = apply_theme(qss_template, DESIGN_TOKENS)

        # Assert
        assert DESIGN_TOKENS["font-family"] in stylesheet
