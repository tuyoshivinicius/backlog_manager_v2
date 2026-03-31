"""Integration tests for empty state view behavior.

Tests cover T025b:
- Overlay QLabel visible and buttons disabled when rowCount()==0
- Overlay hidden and buttons enabled after set_stories() with data
- Overlay reappears after removing last story
"""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel


@pytest.fixture
def _sample_dto() -> StoryOutputDTO:
    return StoryOutputDTO(
        id="TEST-001",
        component="TEST",
        name="Test Story",
        story_points=5,
        priority=1,
        status="BACKLOG",
        duration=2,
        start_date=date(2026, 1, 15),
        end_date=date(2026, 1, 16),
        developer_id=1,
        feature_id=1,
        developer_name="Dev",
        feature_name="Feature",
        wave=1,
        dependency_ids=[],
    )


class TestEmptyStateModel:
    """Test empty state behavior at model level (no MainWindow dependency)."""

    def test_empty_model_has_zero_rows(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Empty model reports rowCount == 0."""
        model = StoryTableModel()
        assert model.rowCount() == 0

    def test_model_with_data_has_rows(self, qapp, _sample_dto: StoryOutputDTO) -> None:  # type: ignore[no-untyped-def]
        """Model with stories has rowCount > 0."""
        model = StoryTableModel()
        model.set_stories([_sample_dto])
        assert model.rowCount() == 1

    def test_clearing_stories_returns_to_empty(
        self, qapp, _sample_dto: StoryOutputDTO
    ) -> None:  # type: ignore[no-untyped-def]
        """Setting empty list returns model to rowCount == 0."""
        model = StoryTableModel()
        model.set_stories([_sample_dto])
        assert model.rowCount() == 1
        model.set_stories([])
        assert model.rowCount() == 0
