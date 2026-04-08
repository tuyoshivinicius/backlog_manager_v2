"""Headless tests for blocking state resolution in StoryTableModel.

Tests BlockingState computation (NONE / FREE / BLOCKED) and the
DEPENDENCY_IDS_ROLE custom role without any PySide6 dependency.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# PySide6 mock setup
# ---------------------------------------------------------------------------
from tests.headless_mocks import MockSignal, create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_table_model=True)

# Additional table-model-specific flags not in shared helper
_mock_qt_core.Qt.ItemFlag.ItemIsEditable = 2

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.story import StoryOutputDTO
    from backlog_manager.presentation.viewmodels.story_table_model import (
        BLOCKING_STATE_ROLE,
        DEPENDENCY_IDS_ROLE,
        BlockingState,
        StoryTableModel,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_index(row: int, col: int):
    idx = MagicMock()
    idx.isValid.return_value = True
    idx.row.return_value = row
    idx.column.return_value = col
    return idx


def _make_story(
    story_id: str = "US-001",
    status: str = "BACKLOG",
    dependency_ids: list[str] | None = None,
) -> StoryOutputDTO:
    return StoryOutputDTO(
        planning_id=1,
        id=story_id,
        component="comp",
        name="Test Story",
        story_points=5,
        priority=1,
        status=status,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
        dependency_ids=dependency_ids or [],
    )


def _model_with(stories: list[StoryOutputDTO]) -> StoryTableModel:
    model = StoryTableModel.__new__(StoryTableModel)
    model._stories = list(stories)
    model._story_status_map = {s.id: s.status for s in stories}
    model.status_change_requested = MockSignal("str", "str")
    return model


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBlockingStateResolution:  # noqa: D101
    def test_no_dependencies_returns_none(self) -> None:
        model = _model_with([_make_story("US-001", "BACKLOG", [])])
        state = model.data(_make_index(0, 8), BLOCKING_STATE_ROLE)
        assert state == BlockingState.NONE

    def test_all_deps_concluido_returns_free(self) -> None:
        model = _model_with(
            [
                _make_story("US-001", "CONCLUIDO"),
                _make_story("US-002", "BACKLOG", ["US-001"]),
            ]
        )
        state = model.data(_make_index(1, 8), BLOCKING_STATE_ROLE)
        assert state == BlockingState.FREE

    def test_dep_not_concluido_returns_blocked(self) -> None:
        model = _model_with(
            [
                _make_story("US-001", "EXECUCAO"),
                _make_story("US-002", "BACKLOG", ["US-001"]),
            ]
        )
        state = model.data(_make_index(1, 8), BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_missing_dep_treated_as_blocked(self) -> None:
        model = _model_with([_make_story("US-002", "BACKLOG", ["US-999"])])
        state = model.data(_make_index(0, 8), BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_mixed_deps_some_not_concluido(self) -> None:
        model = _model_with(
            [
                _make_story("US-001", "CONCLUIDO"),
                _make_story("US-002", "EXECUCAO"),
                _make_story("US-003", "BACKLOG", ["US-001", "US-002"]),
            ]
        )
        state = model.data(_make_index(2, 8), BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_dependency_ids_role_returns_list(self) -> None:
        model = _model_with([_make_story("US-001", "BACKLOG", ["US-002", "US-003"])])
        ids = model.data(_make_index(0, 8), DEPENDENCY_IDS_ROLE)
        assert ids == ["US-002", "US-003"]

    def test_blocking_state_role_wrong_column_returns_none(self) -> None:
        model = _model_with([_make_story("US-001", "BACKLOG", ["US-002"])])
        state = model.data(_make_index(0, 0), BLOCKING_STATE_ROLE)
        assert state is None
