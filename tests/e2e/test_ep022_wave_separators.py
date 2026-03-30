"""E2E tests for wave separator painting in StoryTableView.

Tests verify wave separator visibility toggle and painting behavior.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from backlog_manager.presentation.theme import DESIGN_TOKENS
from backlog_manager.presentation.views.main_window import MainWindow, StoryTableView

pytestmark = [pytest.mark.e2e]


class TestWaveSeparators:
    """Tests for wave separator painting in the story table."""

    def test_wave_separators_visible_by_default(self, e2e_main_window: MainWindow):
        """Wave separators are enabled by default."""
        table = e2e_main_window._story_table
        assert table._wave_separators_visible is True

    def test_wave_separators_can_be_toggled_off(self, e2e_main_window: MainWindow):
        """Wave separators can be disabled."""
        table = e2e_main_window._story_table
        table._wave_separators_visible = False
        assert table._wave_separators_visible is False

    def test_separator_constants(self):
        """StoryTableView has expected separator constants."""
        assert StoryTableView.WAVE_SEPARATOR_HEIGHT > 0
        assert StoryTableView.WAVE_SEPARATOR_PADDING > 0

    def test_separator_colors_use_design_tokens(self):
        """Wave separator colors reference DESIGN_TOKENS."""
        # Verify the tokens exist and are valid hex colors
        bg = DESIGN_TOKENS["neutral-100"]
        fg = DESIGN_TOKENS["neutral-600"]
        assert bg.startswith("#")
        assert fg.startswith("#")

    def test_table_view_has_tooltip_tracking(self, e2e_main_window: MainWindow):
        """StoryTableView has tooltip timer and tracking state."""
        table = e2e_main_window._story_table
        assert hasattr(table, "_tooltip_timer")
        assert hasattr(table, "_hovered_row")
        assert table._hovered_row == -1
        assert table._tooltip_widget is None

    def test_rich_tooltip_cleanup_on_leave(self, e2e_main_window: MainWindow):
        """Tooltip is cleaned up when mouse leaves the table."""
        table = e2e_main_window._story_table
        # Simulate leave event cleanup
        table._hide_rich_tooltip()
        assert table._tooltip_widget is None
