"""Tests for StoryTableModel.

This module contains unit tests for the StoryTableModel class,
verifying correct implementation of QAbstractTableModel with 13 columns.
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
        """T024: Test that an empty model has zero rows."""
        model = StoryTableModel()
        assert model.rowCount() == 0

    def test_empty_model_has_correct_columns(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """T019: Test that the model has 13 columns."""
        model = StoryTableModel()
        assert model.columnCount() == 13
        assert model.COLUMNS == [
            "Prioridade",
            "Feature",
            "Onda",
            "ID",
            "Componente",
            "Nome",
            "Status",
            "Desenvolvedor",
            "Dependencias",
            "SP",
            "Inicio",
            "Fim",
            "Duracao",
        ]

    def test_header_data_horizontal(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """T019: Test horizontal header data returns correct names for all 13 columns."""
        model = StoryTableModel()
        expected = [
            "Prioridade",
            "Feature",
            "Onda",
            "ID",
            "Componente",
            "Nome",
            "Status",
            "Desenvolvedor",
            "Dependencias",
            "SP",
            "Inicio",
            "Fim",
            "Duracao",
        ]
        for i, name in enumerate(expected):
            assert model.headerData(i, Qt.Orientation.Horizontal) == name

    def test_header_data_vertical(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test vertical header data returns row numbers."""
        model = StoryTableModel()
        assert model.headerData(0, Qt.Orientation.Vertical) == "1"
        assert model.headerData(99, Qt.Orientation.Vertical) == "100"


class TestStoryTableModelDisplayRole:
    """T020: Tests for data(DisplayRole) with fully populated DTO."""

    @pytest.fixture
    def model_with_stories(self, sample_stories: list[StoryOutputDTO], qapp) -> StoryTableModel:  # type: ignore[no-untyped-def]
        """Create a model with sample stories."""
        model = StoryTableModel()
        model.set_stories(sample_stories)
        return model

    def test_set_stories_updates_row_count(
        self, model_with_stories: StoryTableModel
    ) -> None:
        assert model_with_stories.rowCount() == 3

    def test_data_prioridade(self, model_with_stories: StoryTableModel) -> None:
        """Column 0: Prioridade."""
        index = model_with_stories.index(0, 0)
        assert model_with_stories.data(index) == "1"
        index = model_with_stories.index(2, 0)
        assert model_with_stories.data(index) == "3"

    def test_data_feature_name(self, model_with_stories: StoryTableModel) -> None:
        """Column 1: Feature name resolved."""
        index = model_with_stories.index(0, 1)
        assert model_with_stories.data(index) == "Feature Alpha"

    def test_data_onda(self, model_with_stories: StoryTableModel) -> None:
        """Column 2: Wave number."""
        index = model_with_stories.index(0, 2)
        assert model_with_stories.data(index) == "1"

    def test_data_id(self, model_with_stories: StoryTableModel) -> None:
        """Column 3: ID in COMPONENTE-NNN format."""
        index = model_with_stories.index(0, 3)
        assert model_with_stories.data(index) == "COMP-001"
        index = model_with_stories.index(2, 3)
        assert model_with_stories.data(index) == "API-001"

    def test_data_componente(self, model_with_stories: StoryTableModel) -> None:
        """Column 4: Componente."""
        index = model_with_stories.index(0, 4)
        assert model_with_stories.data(index) == "COMP"
        index = model_with_stories.index(2, 4)
        assert model_with_stories.data(index) == "API"

    def test_data_nome(self, model_with_stories: StoryTableModel) -> None:
        """Column 5: Nome."""
        index = model_with_stories.index(0, 5)
        assert model_with_stories.data(index) == "Primeira Historia"

    def test_data_status(self, model_with_stories: StoryTableModel) -> None:
        """Column 6: Status."""
        index = model_with_stories.index(0, 6)
        assert model_with_stories.data(index) == "BACKLOG"
        index = model_with_stories.index(2, 6)
        assert model_with_stories.data(index) == "DOING"

    def test_data_developer_name(self, model_with_stories: StoryTableModel) -> None:
        """Column 7: Developer name resolved."""
        index = model_with_stories.index(0, 7)
        assert model_with_stories.data(index) == "Joao Silva"

    def test_data_dependencias(self, model_with_stories: StoryTableModel) -> None:
        """Column 8: Dependencies joined by comma."""
        index = model_with_stories.index(0, 8)
        assert model_with_stories.data(index) == "API-001"

    def test_data_sp(self, model_with_stories: StoryTableModel) -> None:
        """Column 9: Story points."""
        index = model_with_stories.index(0, 9)
        assert model_with_stories.data(index) == "3"
        index = model_with_stories.index(2, 9)
        assert model_with_stories.data(index) == "8"

    def test_data_inicio_formatted(self, model_with_stories: StoryTableModel) -> None:
        """Column 10: Start date DD/MM/YYYY."""
        index = model_with_stories.index(0, 10)
        assert model_with_stories.data(index) == "15/01/2026"

    def test_data_fim_formatted(self, model_with_stories: StoryTableModel) -> None:
        """Column 11: End date DD/MM/YYYY."""
        index = model_with_stories.index(0, 11)
        assert model_with_stories.data(index) == "16/01/2026"

    def test_data_duracao(self, model_with_stories: StoryTableModel) -> None:
        """Column 12: Duration in days."""
        index = model_with_stories.index(0, 12)
        assert model_with_stories.data(index) == "2"

    def test_data_user_role_returns_story_id(
        self, model_with_stories: StoryTableModel
    ) -> None:
        """UserRole returns the story ID for all columns."""
        for col in range(13):
            index = model_with_stories.index(0, col)
            assert (
                model_with_stories.data(index, Qt.ItemDataRole.UserRole) == "COMP-001"
            )

    def test_data_invalid_index_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        invalid_index = QModelIndex()
        assert model_with_stories.data(invalid_index) is None

    def test_data_out_of_range_row_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        index = model_with_stories.index(100, 0)
        if index.isValid():
            assert model_with_stories.data(index) is None


class TestStoryTableModelMissingValues:
    """T021: Test data(DisplayRole) for missing/None values returns em-dash."""

    def test_missing_feature_name(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 1)  # Feature
        assert model.data(index) == "\u2014"

    def test_missing_developer_name(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 7)  # Desenvolvedor
        assert model.data(index) == "\u2014"

    def test_missing_dependency_ids(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 8)  # Dependencias
        assert model.data(index) == "\u2014"

    def test_missing_start_date(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 10)  # Inicio
        assert model.data(index) == "\u2014"

    def test_missing_end_date(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 11)  # Fim
        assert model.data(index) == "\u2014"

    def test_missing_duration(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 12)  # Duracao
        assert model.data(index) == "\u2014"

    def test_wave_zero_shows_dash(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
            wave=0,
        )
        model.set_stories([story])
        index = model.index(0, 2)  # Onda
        assert model.data(index) == "\u2014"

    def test_empty_component_shows_dash(self, qapp) -> None:  # type: ignore[no-untyped-def]
        model = StoryTableModel()
        story = StoryOutputDTO(
            id="TEST-001",
            component="",
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
        index = model.index(0, 4)  # Componente
        assert model.data(index) == "\u2014"


class TestStoryTableModelAlignment:
    """T022: Test data(TextAlignmentRole) for center vs left columns."""

    def test_center_columns(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Columns {0,2,6,9,10,11,12} should be AlignCenter."""
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

        for col in (0, 2, 6, 9, 10, 11, 12):
            index = model.index(0, col)
            alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
            assert (
                alignment == Qt.AlignmentFlag.AlignCenter
            ), f"Column {col} should be AlignCenter"

    def test_left_columns(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Columns {1,3,4,5,7,8} should be AlignLeft|AlignVCenter."""
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

        expected = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        for col in (1, 3, 4, 5, 7, 8):
            index = model.index(0, col)
            alignment = model.data(index, Qt.ItemDataRole.TextAlignmentRole)
            assert (
                alignment == expected
            ), f"Column {col} should be AlignLeft|AlignVCenter"


class TestStoryTableModelTooltip:
    """T023: Test data(ToolTipRole) returns full text only for tooltip columns."""

    @pytest.fixture
    def model(self, qapp) -> StoryTableModel:  # type: ignore[no-untyped-def]
        model = StoryTableModel()
        story = StoryOutputDTO(
            id="TEST-001",
            component="TEST",
            name="A Long Name",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=2,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 16),
            developer_id=1,
            feature_id=1,
            developer_name="Developer Name",
            feature_name="Feature Name",
            wave=1,
            dependency_ids=["DEP-001", "DEP-002"],
        )
        model.set_stories([story])
        return model

    def test_tooltip_columns_return_text(self, model: StoryTableModel) -> None:
        """Columns {1,5,7,8} return tooltip text."""
        expected = {
            1: "Feature Name",
            5: "A Long Name",
            7: "Developer Name",
            8: "DEP-001, DEP-002",
        }
        for col, text in expected.items():
            index = model.index(0, col)
            assert model.data(index, Qt.ItemDataRole.ToolTipRole) == text

    def test_non_tooltip_columns_return_none(self, model: StoryTableModel) -> None:
        """Non-tooltip columns return None."""
        for col in (0, 2, 3, 4, 6, 9, 10, 11, 12):
            index = model.index(0, col)
            assert model.data(index, Qt.ItemDataRole.ToolTipRole) is None


class TestStoryTableModelHelpers:
    """Tests for StoryTableModel helper methods."""

    @pytest.fixture
    def model_with_stories(self, sample_stories: list[StoryOutputDTO], qapp) -> StoryTableModel:  # type: ignore[no-untyped-def]
        model = StoryTableModel()
        model.set_stories(sample_stories)
        return model

    def test_get_story_at_valid_row(self, model_with_stories: StoryTableModel) -> None:
        story = model_with_stories.get_story_at(0)
        assert story is not None
        assert story.id == "COMP-001"

    def test_get_story_at_invalid_row_returns_none(
        self, model_with_stories: StoryTableModel
    ) -> None:
        assert model_with_stories.get_story_at(-1) is None
        assert model_with_stories.get_story_at(100) is None

    def test_get_story_by_id_existing(
        self, model_with_stories: StoryTableModel
    ) -> None:
        story = model_with_stories.get_story_by_id("COMP-002")
        assert story is not None
        assert story.name == "Segunda Historia"

    def test_get_story_by_id_nonexistent(
        self, model_with_stories: StoryTableModel
    ) -> None:
        assert model_with_stories.get_story_by_id("NONEXISTENT") is None

    def test_get_row_for_story_existing(
        self, model_with_stories: StoryTableModel
    ) -> None:
        assert model_with_stories.get_row_for_story("COMP-001") == 0
        assert model_with_stories.get_row_for_story("COMP-002") == 1
        assert model_with_stories.get_row_for_story("API-001") == 2

    def test_get_row_for_story_nonexistent(
        self, model_with_stories: StoryTableModel
    ) -> None:
        assert model_with_stories.get_row_for_story("NONEXISTENT") == -1

    def test_stories_property_returns_copy(
        self, model_with_stories: StoryTableModel
    ) -> None:
        stories = model_with_stories.stories
        assert len(stories) == 3
        stories.clear()
        assert model_with_stories.rowCount() == 3


class TestStoryTableModelEdgeCases:
    """T025c: Test edge cases in StoryTableModel."""

    def test_developer_id_no_match_shows_dash(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Developer ID with no matching developer shows em-dash."""
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
            developer_id=99,
            feature_id=None,
            developer_name=None,
        )
        model.set_stories([story])
        index = model.index(0, 7)
        assert model.data(index) == "\u2014"

    def test_feature_id_no_match_shows_dash(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Feature ID with no matching feature shows em-dash for name and wave."""
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
            feature_id=99,
            feature_name=None,
            wave=0,
        )
        model.set_stories([story])
        assert model.data(model.index(0, 1)) == "\u2014"  # Feature name
        assert model.data(model.index(0, 2)) == "\u2014"  # Onda

    def test_orphaned_dependency_ids_displayed_as_is(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Dependency IDs with orphaned references displayed as-is."""
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
            dependency_ids=["DELETED-001", "GONE-002"],
        )
        model.set_stories([story])
        index = model.index(0, 8)
        assert model.data(index) == "DELETED-001, GONE-002"

    def test_none_duration_shows_dash(self, qapp) -> None:  # type: ignore[no-untyped-def]
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
        index = model.index(0, 12)
        assert model.data(index) == "\u2014"


class TestStoryTableModelLongText:
    """T025d: Test long text edge case."""

    def test_long_name_full_in_tooltip(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """Story name >500 chars returns full text in ToolTipRole."""
        model = StoryTableModel()
        long_name = "A" * 600
        story = StoryOutputDTO(
            id="TEST-001",
            component="TEST",
            name=long_name,
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
        # DisplayRole returns full text (elision handled by view)
        index = model.index(0, 5)
        assert model.data(index) == long_name
        # ToolTipRole returns full text
        assert model.data(index, Qt.ItemDataRole.ToolTipRole) == long_name
