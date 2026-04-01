"""Headless tests for StoryTableModel.

Tests business logic (data mapping, row/column counts, display values,
alignment, tooltips, helpers) without any PySide6 dependency.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# PySide6 mock setup -- must happen BEFORE importing the module under test
# ---------------------------------------------------------------------------
from tests.headless_mocks import _SignalInstance, create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_table_model=True)

# Additional table-model-specific flags not in shared helper
_mock_qt_core.Qt.ItemFlag.ItemIsEditable = 2
_mock_qt_core.Qt.ItemFlag.ItemIsSelectable = 1
_mock_qt_core.Qt.ItemFlag.ItemIsEnabled = 32

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.story import StoryOutputDTO
    from backlog_manager.presentation.viewmodels.story_table_model import (
        StoryTableModel,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Alias the mock role constants so tests read like the originals
DisplayRole = _mock_qt_core.Qt.ItemDataRole.DisplayRole
TextAlignmentRole = _mock_qt_core.Qt.ItemDataRole.TextAlignmentRole
ToolTipRole = _mock_qt_core.Qt.ItemDataRole.ToolTipRole
BackgroundRole = _mock_qt_core.Qt.ItemDataRole.BackgroundRole
UserRole = _mock_qt_core.Qt.ItemDataRole.UserRole
EditRole = _mock_qt_core.Qt.ItemDataRole.EditRole
AlignCenter = _mock_qt_core.Qt.AlignmentFlag.AlignCenter
AlignLeft = _mock_qt_core.Qt.AlignmentFlag.AlignLeft
AlignVCenter = _mock_qt_core.Qt.AlignmentFlag.AlignVCenter
Horizontal = _mock_qt_core.Qt.Orientation.Horizontal
Vertical = _mock_qt_core.Qt.Orientation.Vertical


def _make_index(row: int, col: int):
    """Create a lightweight fake QModelIndex."""
    idx = MagicMock()
    idx.isValid.return_value = True
    idx.row.return_value = row
    idx.column.return_value = col
    return idx


def _invalid_index():
    idx = MagicMock()
    idx.isValid.return_value = False
    return idx


@pytest.fixture()
def sample_stories() -> list[StoryOutputDTO]:
    return [
        StoryOutputDTO(
            id="COMP-001",
            component="COMP",
            name="Primeira Historia",
            story_points=3,
            priority=1,
            status="BACKLOG",
            duration=2,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 16),
            developer_id=1,
            feature_id=1,
            developer_name="Joao Silva",
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=["API-001"],
        ),
        StoryOutputDTO(
            id="COMP-002",
            component="COMP",
            name="Segunda Historia",
            story_points=5,
            priority=2,
            status="BACKLOG",
            duration=3,
            start_date=date(2026, 1, 17),
            end_date=date(2026, 1, 20),
            developer_id=None,
            feature_id=1,
            developer_name=None,
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=[],
        ),
        StoryOutputDTO(
            id="API-001",
            component="API",
            name="Terceira Historia",
            story_points=8,
            priority=3,
            status="DOING",
            duration=4,
            start_date=None,
            end_date=None,
            developer_id=2,
            feature_id=None,
            developer_name="Maria Santos",
            feature_name=None,
            wave=0,
            dependency_ids=[],
        ),
    ]


def _new_model() -> StoryTableModel:
    model = StoryTableModel.__new__(StoryTableModel)
    model._stories = []
    model._story_status_map = {}
    model.status_change_requested = _SignalInstance()
    return model


def _model_with(stories: list[StoryOutputDTO]) -> StoryTableModel:
    model = _new_model()
    model._stories = list(stories)
    model._story_status_map = {s.id: s.status for s in stories}
    model.status_change_requested = _SignalInstance()
    return model


# ---------------------------------------------------------------------------
# Tests: basic model properties
# ---------------------------------------------------------------------------


class TestStoryTableModelBasics:  # noqa: D101
    def test_empty_model_has_zero_rows(self) -> None:
        model = _new_model()
        assert model.rowCount() == 0

    def test_empty_model_has_correct_columns(self) -> None:
        model = _new_model()
        assert model.columnCount() == 13
        assert [
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
        ] == StoryTableModel.COLUMNS

    def test_header_data_horizontal(self) -> None:
        model = _new_model()
        expected = StoryTableModel.COLUMNS
        for i, name in enumerate(expected):
            assert model.headerData(i, Horizontal) == name

    def test_header_data_vertical(self) -> None:
        model = _new_model()
        assert model.headerData(0, Vertical) == "1"
        assert model.headerData(99, Vertical) == "100"


# ---------------------------------------------------------------------------
# Tests: DisplayRole (fully populated DTO)
# ---------------------------------------------------------------------------


class TestStoryTableModelDisplayRole:  # noqa: D101
    @pytest.fixture()
    def model(self, sample_stories: list[StoryOutputDTO]) -> StoryTableModel:
        return _model_with(sample_stories)

    def test_set_stories_updates_row_count(self, model: StoryTableModel) -> None:
        assert model.rowCount() == 3

    def test_data_prioridade(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 0)) == "1"
        assert model.data(_make_index(2, 0)) == "3"

    def test_data_feature_name(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 1)) == "Feature Alpha"

    def test_data_onda(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 2)) == "1"

    def test_data_id(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 3)) == "COMP-001"
        assert model.data(_make_index(2, 3)) == "API-001"

    def test_data_componente(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 4)) == "COMP"
        assert model.data(_make_index(2, 4)) == "API"

    def test_data_nome(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 5)) == "Primeira Historia"

    def test_data_status(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 6)) == "BACKLOG"
        assert model.data(_make_index(2, 6)) == "DOING"

    def test_data_developer_name(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 7)) == "Joao Silva"

    def test_data_dependencias(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 8)) == "API-001"

    def test_data_sp(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 9)) == "3"
        assert model.data(_make_index(2, 9)) == "8"

    def test_data_inicio_formatted(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 10)) == "15/01/2026"

    def test_data_fim_formatted(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 11)) == "16/01/2026"

    def test_data_duracao(self, model: StoryTableModel) -> None:
        assert model.data(_make_index(0, 12)) == "2"

    def test_data_user_role_returns_story_id(self, model: StoryTableModel) -> None:
        for col in range(13):
            assert model.data(_make_index(0, col), UserRole) == "COMP-001"

    def test_data_invalid_index_returns_none(self, model: StoryTableModel) -> None:
        assert model.data(_invalid_index()) is None

    def test_data_out_of_range_row_returns_none(self, model: StoryTableModel) -> None:
        idx = _make_index(100, 0)
        assert model.data(idx) is None


# ---------------------------------------------------------------------------
# Tests: missing / None values => em-dash
# ---------------------------------------------------------------------------


class TestStoryTableModelMissingValues:
    @pytest.fixture()
    def minimal_model(self) -> StoryTableModel:
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
        return _model_with([story])

    def test_missing_feature_name(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 1)) == "\u2014"

    def test_missing_developer_name(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 7)) == "\u2014"

    def test_missing_dependency_ids(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 8)) == "\u2014"

    def test_missing_start_date(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 10)) == "\u2014"

    def test_missing_end_date(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 11)) == "\u2014"

    def test_missing_duration(self, minimal_model: StoryTableModel) -> None:
        assert minimal_model.data(_make_index(0, 12)) == "\u2014"

    def test_wave_zero_shows_dash(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 2)) == "\u2014"

    def test_empty_component_shows_dash(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 4)) == "\u2014"


# ---------------------------------------------------------------------------
# Tests: TextAlignmentRole
# ---------------------------------------------------------------------------


class TestStoryTableModelAlignment:
    @pytest.fixture()
    def model(self) -> StoryTableModel:
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
        return _model_with([story])

    def test_center_columns(self, model: StoryTableModel) -> None:
        for col in (0, 2, 6, 9, 10, 11, 12):
            alignment = model.data(_make_index(0, col), TextAlignmentRole)
            assert alignment == AlignCenter, f"Column {col} should be AlignCenter"

    def test_left_columns(self, model: StoryTableModel) -> None:
        expected = AlignLeft | AlignVCenter
        for col in (1, 3, 4, 5, 7, 8):
            alignment = model.data(_make_index(0, col), TextAlignmentRole)
            assert (
                alignment == expected
            ), f"Column {col} should be AlignLeft|AlignVCenter"


# ---------------------------------------------------------------------------
# Tests: ToolTipRole
# ---------------------------------------------------------------------------


class TestStoryTableModelTooltip:
    @pytest.fixture()
    def model(self) -> StoryTableModel:
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
        return _model_with([story])

    def test_tooltip_columns_return_text(self, model: StoryTableModel) -> None:
        expected = {
            1: "Feature Name",
            5: "A Long Name",
            7: "Developer Name",
            8: "DEP-001, DEP-002",
        }
        for col, text in expected.items():
            assert model.data(_make_index(0, col), ToolTipRole) == text

    def test_non_tooltip_columns_return_none(self, model: StoryTableModel) -> None:
        for col in (0, 2, 3, 4, 6, 9, 10, 11, 12):
            assert model.data(_make_index(0, col), ToolTipRole) is None


# ---------------------------------------------------------------------------
# Tests: helper methods
# ---------------------------------------------------------------------------


class TestStoryTableModelHelpers:
    @pytest.fixture()
    def model(self, sample_stories: list[StoryOutputDTO]) -> StoryTableModel:
        return _model_with(sample_stories)

    def test_get_story_at_valid_row(self, model: StoryTableModel) -> None:
        story = model.get_story_at(0)
        assert story is not None
        assert story.id == "COMP-001"

    def test_get_story_at_invalid_row_returns_none(
        self, model: StoryTableModel
    ) -> None:
        assert model.get_story_at(-1) is None
        assert model.get_story_at(100) is None

    def test_get_story_by_id_existing(self, model: StoryTableModel) -> None:
        story = model.get_story_by_id("COMP-002")
        assert story is not None
        assert story.name == "Segunda Historia"

    def test_get_story_by_id_nonexistent(self, model: StoryTableModel) -> None:
        assert model.get_story_by_id("NONEXISTENT") is None

    def test_get_row_for_story_existing(self, model: StoryTableModel) -> None:
        assert model.get_row_for_story("COMP-001") == 0
        assert model.get_row_for_story("COMP-002") == 1
        assert model.get_row_for_story("API-001") == 2

    def test_get_row_for_story_nonexistent(self, model: StoryTableModel) -> None:
        assert model.get_row_for_story("NONEXISTENT") == -1

    def test_stories_property_returns_copy(self, model: StoryTableModel) -> None:
        stories = model.stories
        assert len(stories) == 3
        stories.clear()
        assert model.rowCount() == 3


# ---------------------------------------------------------------------------
# Tests: edge cases
# ---------------------------------------------------------------------------


class TestStoryTableModelEdgeCases:
    def test_developer_id_no_match_shows_dash(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 7)) == "\u2014"

    def test_feature_id_no_match_shows_dash(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 1)) == "\u2014"  # Feature name
        assert model.data(_make_index(0, 2)) == "\u2014"  # Onda

    def test_orphaned_dependency_ids_displayed_as_is(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 8)) == "DELETED-001, GONE-002"

    def test_none_duration_shows_dash(self) -> None:
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
        model = _model_with([story])
        assert model.data(_make_index(0, 12)) == "\u2014"


# ---------------------------------------------------------------------------
# Tests: long text
# ---------------------------------------------------------------------------


class TestStoryTableModelLongText:
    def test_long_name_full_in_tooltip(self) -> None:
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
        model = _model_with([story])
        idx = _make_index(0, 5)
        assert model.data(idx) == long_name
        assert model.data(idx, ToolTipRole) == long_name


# ---------------------------------------------------------------------------
# Tests: rowCount / columnCount with valid parent (lines 112, 127)
# ---------------------------------------------------------------------------


class TestStoryTableModelParentIndex:
    """Cover rowCount/columnCount returning 0 when parent.isValid() is True."""

    def test_row_count_with_valid_parent_returns_zero(self) -> None:
        model = _new_model()
        parent = MagicMock()
        parent.isValid.return_value = True
        assert model.rowCount(parent) == 0

    def test_column_count_with_valid_parent_returns_zero(self) -> None:
        model = _new_model()
        parent = MagicMock()
        parent.isValid.return_value = True
        assert model.columnCount(parent) == 0


# ---------------------------------------------------------------------------
# Tests: flags method (lines 208-211)
# ---------------------------------------------------------------------------


class TestStoryTableModelFlags:
    """Cover the flags() method: status column editable, others not."""

    @pytest.fixture()
    def model(self) -> StoryTableModel:
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
        return _model_with([story])

    def test_status_column_is_editable(self, model: StoryTableModel) -> None:
        idx = _make_index(0, 6)
        flags = model.flags(idx)
        editable = _mock_qt_core.Qt.ItemFlag.ItemIsEditable
        assert flags & editable

    def test_non_status_column_not_editable(self, model: StoryTableModel) -> None:
        base = (
            _mock_qt_core.Qt.ItemFlag.ItemIsSelectable
            | _mock_qt_core.Qt.ItemFlag.ItemIsEnabled
        )
        editable = _mock_qt_core.Qt.ItemFlag.ItemIsEditable
        for col in (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12):
            idx = _make_index(0, col)
            flags = model.flags(idx)
            assert flags == base, f"Column {col} should not be editable"
            assert not (flags & editable)


# ---------------------------------------------------------------------------
# Tests: setData method (lines 220-229)
# ---------------------------------------------------------------------------


class TestStoryTableModelSetData:
    """Cover setData inline status edit signal emission."""

    @pytest.fixture()
    def model(self) -> StoryTableModel:
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
        return _model_with([story])

    def test_set_data_invalid_index_returns_false(self, model: StoryTableModel) -> None:
        assert model.setData(_invalid_index(), "DOING", EditRole) is False

    def test_set_data_wrong_role_returns_false(self, model: StoryTableModel) -> None:
        idx = _make_index(0, 6)
        assert model.setData(idx, "DOING", DisplayRole) is False

    def test_set_data_wrong_column_returns_false(self, model: StoryTableModel) -> None:
        idx = _make_index(0, 0)  # Not status column
        assert model.setData(idx, "DOING", EditRole) is False

    def test_set_data_same_status_returns_false(self, model: StoryTableModel) -> None:
        idx = _make_index(0, 6)
        assert model.setData(idx, "BACKLOG", EditRole) is False

    def test_set_data_emits_signal_and_returns_true(
        self, model: StoryTableModel
    ) -> None:
        idx = _make_index(0, 6)
        result = model.setData(idx, "doing", EditRole)
        assert result is True
        assert model.status_change_requested.emissions == [("TEST-001", "DOING")]


# ---------------------------------------------------------------------------
# Tests: _get_display_value default case (lines 282-283)
# ---------------------------------------------------------------------------


class TestStoryTableModelDisplayDefault:
    """Cover the default match case returning empty string for invalid column."""

    def test_invalid_column_returns_empty_string(self) -> None:
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
        model = _model_with([story])
        idx = _make_index(0, 99)  # Out-of-range column
        assert model.data(idx) == ""


# ---------------------------------------------------------------------------
# Tests: headerData edge cases (lines 329, 337)
# ---------------------------------------------------------------------------


class TestStoryTableModelHeaderEdgeCases:
    """Cover headerData returning None for non-display role and OOB section."""

    def test_header_data_non_display_role_returns_none(self) -> None:
        model = _new_model()
        result = model.headerData(0, Horizontal, TextAlignmentRole)
        assert result is None

    def test_header_data_out_of_range_section_returns_none(self) -> None:
        model = _new_model()
        result = model.headerData(99, Horizontal)
        assert result is None


# ---------------------------------------------------------------------------
# Tests: _get_wave_background (lines 348-352)
# ---------------------------------------------------------------------------


class TestStoryTableModelWaveBackground:
    """Cover wave background color resolution."""

    def test_wave_zero_returns_none(self) -> None:
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
        model = _model_with([story])
        result = model.data(_make_index(0, 0), BackgroundRole)
        assert result is None

    def test_wave_negative_returns_none(self) -> None:
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
            wave=-1,
        )
        model = _model_with([story])
        result = model.data(_make_index(0, 0), BackgroundRole)
        assert result is None

    def test_wave_positive_returns_qcolor(self) -> None:
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
            wave=1,
        )
        model = _model_with([story])
        result = model.data(_make_index(0, 0), BackgroundRole)
        # QColor is mocked, so result should not be None
        assert result is not None


# ---------------------------------------------------------------------------
# Tests: _resolve_dependency_role fallthrough (line 204)
# ---------------------------------------------------------------------------


class TestStoryTableModelDependencyRoleFallthrough:
    """Cover _resolve_dependency_role returning None for unknown role on col 8."""

    def test_unknown_role_on_dep_column_returns_none(self) -> None:
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
            dependency_ids=["DEP-001"],
        )
        model = _model_with([story])
        # Use a role that is not BLOCKING_STATE_ROLE or DEPENDENCY_IDS_ROLE
        # and not any standard Qt role handled in _resolve_role_data
        unknown_role = 999
        idx = _make_index(0, 8)
        result = model.data(idx, unknown_role)
        assert result is None
