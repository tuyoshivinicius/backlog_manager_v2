"""Tests for StoryTableModel.

This module contains unit tests for the StoryTableModel class,
verifying correct implementation of QAbstractTableModel.
"""

from __future__ import annotations

from datetime import date

import pytest
from PySide6.QtCore import QModelIndex, Qt

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel


class TestStoryTableModelBasics:
    """Tests for basic StoryTableModel functionality."""

    def test_empty_model_has_zero_rows(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that an empty model has zero rows."""
        model = StoryTableModel()
        assert model.rowCount() == 0

    def test_empty_model_has_correct_columns(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that the model has the correct number of columns."""
        model = StoryTableModel()
        assert model.columnCount() == 8
        assert model.COLUMNS == [
            "ID",
            "Nome",
            "SP",
            "Status",
            "Feature",
            "Dev",
            "Inicio",
            "Fim",
        ]

    def test_header_data_horizontal(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test horizontal header data returns column names."""
        model = StoryTableModel()

        assert model.headerData(0, Qt.Orientation.Horizontal) == "ID"
        assert model.headerData(1, Qt.Orientation.Horizontal) == "Nome"
        assert model.headerData(2, Qt.Orientation.Horizontal) == "SP"
        assert model.headerData(3, Qt.Orientation.Horizontal) == "Status"
        assert model.headerData(4, Qt.Orientation.Horizontal) == "Feature"
        assert model.headerData(5, Qt.Orientation.Horizontal) == "Dev"
        assert model.headerData(6, Qt.Orientation.Horizontal) == "Inicio"
        assert model.headerData(7, Qt.Orientation.Horizontal) == "Fim"

    def test_header_data_vertical(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test vertical header data returns row numbers."""
        model = StoryTableModel()

        assert model.headerData(0, Qt.Orientation.Vertical) == "1"
        assert model.headerData(1, Qt.Orientation.Vertical) == "2"
        assert model.headerData(99, Qt.Orientation.Vertical) == "100"


class TestStoryTableModelWithData:
    """Tests for StoryTableModel with story data."""

    @pytest.fixture
    def model_with_stories(self, sample_stories: list[StoryOutputDTO], qapp) -> StoryTableModel:  # type: ignore[no-untyped-def]
        """Create a model with sample stories."""
        model = StoryTableModel()
        model.set_stories(sample_stories)
        return model

    def test_set_stories_updates_row_count(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that setting stories updates the row count."""
        assert model_with_stories.rowCount() == 3

    def test_data_returns_correct_id(self, model_with_stories: StoryTableModel) -> None:
        """Test that data returns correct ID values."""
        index = model_with_stories.index(0, 0)
        assert model_with_stories.data(index) == "COMP-001"

        index = model_with_stories.index(1, 0)
        assert model_with_stories.data(index) == "COMP-002"

        index = model_with_stories.index(2, 0)
        assert model_with_stories.data(index) == "API-001"

    def test_data_returns_correct_name(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns correct name values."""
        index = model_with_stories.index(0, 1)
        assert model_with_stories.data(index) == "Primeira Historia"

    def test_data_returns_correct_story_points(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns correct story points."""
        index = model_with_stories.index(0, 2)
        assert model_with_stories.data(index) == "3"

        index = model_with_stories.index(1, 2)
        assert model_with_stories.data(index) == "5"

        index = model_with_stories.index(2, 2)
        assert model_with_stories.data(index) == "8"

    def test_data_returns_correct_status(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns correct status values."""
        index = model_with_stories.index(0, 3)
        assert model_with_stories.data(index) == "BACKLOG"

        index = model_with_stories.index(2, 3)
        assert model_with_stories.data(index) == "DOING"

    def test_data_returns_dash_for_null_feature(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns '-' for null feature_id."""
        index = model_with_stories.index(2, 4)  # API-001 has no feature
        assert model_with_stories.data(index) == "-"

    def test_data_returns_feature_id(self, model_with_stories: StoryTableModel) -> None:
        """Test that data returns feature_id as string."""
        index = model_with_stories.index(0, 4)
        assert model_with_stories.data(index) == "1"

    def test_data_returns_dash_for_null_developer(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns '-' for null developer_id."""
        index = model_with_stories.index(1, 5)  # COMP-002 has no developer
        assert model_with_stories.data(index) == "-"

    def test_data_returns_developer_id(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns developer_id as string."""
        index = model_with_stories.index(0, 5)
        assert model_with_stories.data(index) == "1"

    def test_data_returns_formatted_start_date(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns formatted start date."""
        index = model_with_stories.index(0, 6)
        assert model_with_stories.data(index) == "15/01/2026"

    def test_data_returns_dash_for_null_start_date(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns '-' for null start_date."""
        index = model_with_stories.index(2, 6)  # API-001 has no start_date
        assert model_with_stories.data(index) == "-"

    def test_data_returns_formatted_end_date(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns formatted end date."""
        index = model_with_stories.index(0, 7)
        assert model_with_stories.data(index) == "16/01/2026"

    def test_data_returns_dash_for_null_end_date(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that data returns '-' for null end_date."""
        index = model_with_stories.index(2, 7)  # API-001 has no end_date
        assert model_with_stories.data(index) == "-"

    def test_data_user_role_returns_story_id(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that UserRole returns the story ID."""
        index = model_with_stories.index(0, 0)
        story_id = model_with_stories.data(index, Qt.ItemDataRole.UserRole)
        assert story_id == "COMP-001"

    def test_data_invalid_index_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that invalid index returns None."""
        invalid_index = QModelIndex()
        assert model_with_stories.data(invalid_index) is None

    def test_data_out_of_range_row_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that out of range row returns None."""
        index = model_with_stories.index(100, 0)
        # Note: index() may create an index but data() should handle it
        if index.isValid():
            assert model_with_stories.data(index) is None


class TestStoryTableModelHelpers:
    """Tests for StoryTableModel helper methods."""

    @pytest.fixture
    def model_with_stories(self, sample_stories: list[StoryOutputDTO], qapp) -> StoryTableModel:  # type: ignore[no-untyped-def]
        """Create a model with sample stories."""
        model = StoryTableModel()
        model.set_stories(sample_stories)
        return model

    def test_get_story_at_valid_row(self, model_with_stories: StoryTableModel) -> None:
        """Test getting story at a valid row."""
        story = model_with_stories.get_story_at(0)
        assert story is not None
        assert story.id == "COMP-001"

    def test_get_story_at_invalid_row_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test getting story at invalid row returns None."""
        assert model_with_stories.get_story_at(-1) is None
        assert model_with_stories.get_story_at(100) is None

    def test_get_story_by_id_existing(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test getting story by existing ID."""
        story = model_with_stories.get_story_by_id("COMP-002")
        assert story is not None
        assert story.name == "Segunda Historia"

    def test_get_story_by_id_nonexistent(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test getting story by nonexistent ID returns None."""
        assert model_with_stories.get_story_by_id("NONEXISTENT") is None

    def test_get_row_for_story_existing(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test getting row for existing story."""
        assert model_with_stories.get_row_for_story("COMP-001") == 0
        assert model_with_stories.get_row_for_story("COMP-002") == 1
        assert model_with_stories.get_row_for_story("API-001") == 2

    def test_get_row_for_story_nonexistent(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test getting row for nonexistent story returns -1."""
        assert model_with_stories.get_row_for_story("NONEXISTENT") == -1

    def test_stories_property_returns_copy(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """Test that stories property returns a copy."""
        stories = model_with_stories.stories
        assert len(stories) == 3

        # Modifying the copy should not affect the model
        stories.clear()
        assert model_with_stories.rowCount() == 3


class TestStoryTableModelAlignment:
    """Tests for text alignment in StoryTableModel."""

    def test_numeric_columns_centered(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that numeric and date columns are centered."""
        model = StoryTableModel()
        story = StoryOutputDTO(
            id="TEST-001",
            component="TEST",
            name="Test",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )
        model.set_stories([story])

        # SP column (2) should be centered
        index = model.index(0, 2)
        alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
        assert alignment == Qt.AlignmentFlag.AlignCenter

        # Feature column (4) should be centered
        index = model.index(0, 4)
        alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
        assert alignment == Qt.AlignmentFlag.AlignCenter

    def test_text_columns_left_aligned(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that text columns are left-aligned."""
        model = StoryTableModel()
        story = StoryOutputDTO(
            id="TEST-001",
            component="TEST",
            name="Test",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )
        model.set_stories([story])

        # ID column (0) should be left-aligned
        index = model.index(0, 0)
        alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
        assert alignment == Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        # Nome column (1) should be left-aligned
        index = model.index(0, 1)
        alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
        assert alignment == Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
