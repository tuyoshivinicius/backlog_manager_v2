"""E2E tests for DependencyIndicatorDelegate rendering.

Tests verify that the delegate renders correctly for BLOCKED, FREE,
and NONE states in the Dependencies column.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from backlog_manager.presentation.delegates.dependency_indicator_delegate import (
    COLOR_BLOCKED,
    COLOR_FREE,
    DependencyIndicatorDelegate,
)
from backlog_manager.presentation.viewmodels.story_table_model import (
    BLOCKING_STATE_ROLE,
    DEPENDENCY_IDS_ROLE,
    BlockingState,
)
from PySide6.QtCore import QModelIndex, QRect, QSize
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QStyleOptionViewItem

pytestmark = [pytest.mark.e2e]


class TestDependencyIndicatorDelegate:
    """Tests for DependencyIndicatorDelegate paint behavior."""

    def test_size_hint_returns_minimum(self, qtbot):
        """Delegate sizeHint returns expected minimum dimensions."""
        delegate = DependencyIndicatorDelegate()
        option = QStyleOptionViewItem()
        index = QModelIndex()
        size = delegate.sizeHint(option, index)
        assert size == QSize(120, 30)

    def test_paint_none_state_draws_em_dash(self, qtbot):
        """NONE state should render an em-dash via drawText."""
        delegate = DependencyIndicatorDelegate()
        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 120, 30)

        index = MagicMock(spec=QModelIndex)
        index.data.side_effect = lambda role: {
            BLOCKING_STATE_ROLE: BlockingState.NONE,
            DEPENDENCY_IDS_ROLE: [],
        }.get(role)

        delegate.paint(painter, option, index)

        # Verify drawText was called with em-dash
        draw_calls = [c for c in painter.drawText.call_args_list if "\u2014" in str(c)]
        assert len(draw_calls) >= 1

    def test_paint_blocked_state_draws_red_circle(self, qtbot):
        """BLOCKED state should draw a red filled circle."""
        delegate = DependencyIndicatorDelegate()
        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 30)

        index = MagicMock(spec=QModelIndex)
        index.data.side_effect = lambda role: {
            BLOCKING_STATE_ROLE: BlockingState.BLOCKED,
            DEPENDENCY_IDS_ROLE: ["TEST-001"],
        }.get(role)

        delegate.paint(painter, option, index)

        # Verify setBrush was called with blocked color
        brush_calls = [
            c for c in painter.setBrush.call_args_list if c.args[0] == COLOR_BLOCKED
        ]
        assert len(brush_calls) >= 1

        # Verify drawEllipse was called
        assert painter.drawEllipse.called

    def test_paint_free_state_draws_green_circle(self, qtbot):
        """FREE state should draw a green filled circle."""
        delegate = DependencyIndicatorDelegate()
        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 30)

        index = MagicMock(spec=QModelIndex)
        index.data.side_effect = lambda role: {
            BLOCKING_STATE_ROLE: BlockingState.FREE,
            DEPENDENCY_IDS_ROLE: ["TEST-002", "TEST-003"],
        }.get(role)

        delegate.paint(painter, option, index)

        # Verify setBrush was called with free color
        brush_calls = [
            c for c in painter.setBrush.call_args_list if c.args[0] == COLOR_FREE
        ]
        assert len(brush_calls) >= 1

    def test_paint_no_blocking_state_falls_back_to_super(self, qtbot):
        """When BLOCKING_STATE_ROLE returns None, delegate falls back to super."""
        delegate = DependencyIndicatorDelegate()
        painter = MagicMock(spec=QPainter)
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 120, 30)

        index = MagicMock(spec=QModelIndex)
        index.data.return_value = None

        # Should not raise
        delegate.paint(painter, option, index)

    def test_colors_use_design_tokens(self):
        """Verify colors are derived from DESIGN_TOKENS."""
        from backlog_manager.presentation.theme import DESIGN_TOKENS

        assert COLOR_BLOCKED.name() == DESIGN_TOKENS["error-fg"].lower()
        assert COLOR_FREE.name() == DESIGN_TOKENS["success-fg"].lower()
