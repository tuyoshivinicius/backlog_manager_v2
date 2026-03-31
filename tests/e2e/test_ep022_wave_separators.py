"""E2E tests for wave background tinting in StoryTableView.

Tests verify wave palette definition and background role behavior.
"""

from __future__ import annotations

import pytest
from backlog_manager.presentation.theme import WAVE_PALETTE
from backlog_manager.presentation.views.main_window import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

pytestmark = [pytest.mark.e2e]


class TestWavePalette:
    """Tests for WAVE_PALETTE definition."""

    def test_wave_palette_has_sufficient_colors(self):
        """WAVE_PALETTE has at least 9 entries (index 0 + 8 waves)."""
        assert len(WAVE_PALETTE) >= 9

    def test_wave_palette_index_zero_is_empty(self):
        """WAVE_PALETTE[0] is empty string (no tint for unassigned waves)."""
        assert WAVE_PALETTE[0] == ""

    def test_wave_palette_colors_are_valid_hex(self):
        """All non-empty WAVE_PALETTE entries are valid hex colors."""
        for i, color in enumerate(WAVE_PALETTE):
            if i == 0:
                continue
            assert color.startswith("#"), f"WAVE_PALETTE[{i}] should be hex: {color}"
            assert len(color) == 7, f"WAVE_PALETTE[{i}] should be #RRGGBB: {color}"


class TestWaveBackground:
    """Tests for wave background role in StoryTableModel."""

    def test_wave_background_returns_color_for_wave_stories(
        self, e2e_main_window: MainWindow
    ):
        """BackgroundRole returns QColor for stories with wave > 0."""
        model = e2e_main_window._viewmodel._table_model
        # Find a story with wave > 0
        for row in range(model.rowCount()):
            story = model.get_story_at(row)
            if story and story.wave > 0:
                index = model.index(row, 0)
                bg = model.data(index, Qt.ItemDataRole.BackgroundRole)
                assert isinstance(
                    bg, QColor
                ), f"Row {row} with wave={story.wave} should return QColor"
                assert bg.isValid()
                return
        pytest.skip("No stories with wave > 0 in test data")

    def test_wave_background_returns_none_for_no_wave(
        self, e2e_main_window: MainWindow
    ):
        """BackgroundRole returns None for stories with wave == 0."""
        model = e2e_main_window._viewmodel._table_model
        # Find a story with wave == 0
        for row in range(model.rowCount()):
            story = model.get_story_at(row)
            if story and story.wave == 0:
                index = model.index(row, 0)
                bg = model.data(index, Qt.ItemDataRole.BackgroundRole)
                assert bg is None, f"Row {row} with wave=0 should return None, got {bg}"
                return
        pytest.skip("No stories with wave == 0 in test data")

    def test_wave_background_consistent_across_columns(
        self, e2e_main_window: MainWindow
    ):
        """BackgroundRole returns same color for all columns of a row."""
        model = e2e_main_window._viewmodel._table_model
        for row in range(model.rowCount()):
            story = model.get_story_at(row)
            if story and story.wave > 0:
                colors = []
                for col in range(model.columnCount()):
                    index = model.index(row, col)
                    bg = model.data(index, Qt.ItemDataRole.BackgroundRole)
                    colors.append(bg)
                # All columns should have the same color
                first = colors[0]
                for col_idx, c in enumerate(colors):
                    assert (
                        c == first
                    ), f"Column {col_idx} has different wave bg than column 0"
                return
        pytest.skip("No stories with wave > 0 in test data")


class TestTooltipTracking:
    """Tests for tooltip timer and tracking state."""

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
        table._hide_rich_tooltip()
        assert table._tooltip_widget is None
