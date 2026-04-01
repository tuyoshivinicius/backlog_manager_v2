"""Headless tests for FilterProxyModel.

Tests text, status, and feature filtering with AND logic without any
PySide6 dependency.  Since the real FilterProxyModel relies heavily on
QSortFilterProxyModel plumbing (setSourceModel, rowCount via proxy, etc.)
we test the *business logic* directly by calling filterAcceptsRow and the
filter state properties.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# PySide6 mock setup
# ---------------------------------------------------------------------------
from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_table_model=True)

# Additional table-model-specific flags not in shared helper
_mock_qt_core.Qt.ItemFlag.ItemIsEditable = 2

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.story import StoryOutputDTO
    from backlog_manager.presentation.viewmodels.filter_proxy_model import (
        FilterProxyModel,
    )
    from backlog_manager.presentation.viewmodels.story_table_model import (
        StoryTableModel,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DisplayRole = _mock_qt_core.Qt.ItemDataRole.DisplayRole


def _make_story(
    id: str = "COMP-001",
    component: str = "COMP",
    name: str = "Test Story",
    status: str = "BACKLOG",
    feature_id: int | None = None,
    feature_name: str | None = None,
    wave: int = 0,
    priority: int = 0,
) -> StoryOutputDTO:
    return StoryOutputDTO(
        id=id,
        component=component,
        name=name,
        story_points=3,
        priority=priority,
        status=status,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        developer_name=None,
        feature_id=feature_id,
        feature_name=feature_name,
        wave=wave,
        dependency_ids=[],
    )


@pytest.fixture()
def stories() -> list[StoryOutputDTO]:
    return [
        _make_story(
            id="AUTH-001",
            component="AUTH",
            name="Login page",
            status="BACKLOG",
            feature_id=1,
            feature_name="Auth",
            wave=1,
            priority=0,
        ),
        _make_story(
            id="AUTH-002",
            component="AUTH",
            name="Signup form",
            status="EXECUCAO",
            feature_id=1,
            feature_name="Auth",
            wave=1,
            priority=1,
        ),
        _make_story(
            id="DASH-001",
            component="DASH",
            name="Dashboard view",
            status="BACKLOG",
            feature_id=2,
            feature_name="Dashboard",
            wave=2,
            priority=2,
        ),
        _make_story(
            id="DASH-002",
            component="DASH",
            name="Chart widget",
            status="CONCLUIDO",
            feature_id=2,
            feature_name="Dashboard",
            wave=2,
            priority=3,
        ),
        _make_story(
            id="API-001",
            component="API",
            name="REST endpoints",
            status="TESTES",
            feature_id=3,
            feature_name="API",
            wave=1,
            priority=4,
        ),
    ]


def _make_index(row: int, col: int):
    """Create a lightweight fake QModelIndex."""
    idx = MagicMock()
    idx.isValid.return_value = True
    idx.row.return_value = row
    idx.column.return_value = col
    return idx


def _build_source_model(stories: list[StoryOutputDTO]) -> StoryTableModel:
    """Build a StoryTableModel without calling super().__init__."""
    model = StoryTableModel.__new__(StoryTableModel)
    model._stories = list(stories)
    model._story_status_map = {s.id: s.status for s in stories}

    class _Sig:
        def __init__(self, *a):
            """Stub intencional para mock de teste."""

        def emit(self, *a):
            """Stub intencional para mock de teste."""

        def connect(self, *a):
            """Stub intencional para mock de teste."""

        def disconnect(self, *a):
            """Stub intencional para mock de teste."""

    model.status_change_requested = _Sig()
    # Provide index() since QAbstractTableModel.index is not available
    model.index = lambda row, col: _make_index(row, col)
    return model


def _build_proxy(source: StoryTableModel) -> FilterProxyModel:
    """Build a FilterProxyModel wired to a source model, no Qt init."""
    proxy = FilterProxyModel.__new__(FilterProxyModel)
    proxy._text_filter = ""
    proxy._status_filter = None
    proxy._feature_filter = None
    proxy._col_id = StoryTableModel.COLUMNS.index("ID")
    proxy._col_component = StoryTableModel.COLUMNS.index("Componente")
    proxy._col_name = StoryTableModel.COLUMNS.index("Nome")
    proxy._col_status = StoryTableModel.COLUMNS.index("Status")
    # Wire sourceModel() to return our source
    proxy.sourceModel = lambda: source
    # invalidateFilter is a no-op in headless mode
    proxy.invalidateFilter = lambda: None
    return proxy


def _accepted_rows(proxy: FilterProxyModel, source: StoryTableModel) -> list[int]:
    """Return list of source row indices that pass the proxy filter."""
    parent = MagicMock()
    return [
        row for row in range(source.rowCount()) if proxy.filterAcceptsRow(row, parent)
    ]


@pytest.fixture()
def proxy_and_source(
    stories: list[StoryOutputDTO],
) -> tuple[FilterProxyModel, StoryTableModel]:
    source = _build_source_model(stories)
    proxy = _build_proxy(source)
    return proxy, source


# ---------------------------------------------------------------------------
# Tests: text filter
# ---------------------------------------------------------------------------


class TestTextFilter:  # noqa: D101
    def test_text_filter_by_id(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("AUTH")
        assert len(_accepted_rows(proxy, source)) == 2

    def test_text_filter_by_name(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("Dashboard")
        assert len(_accepted_rows(proxy, source)) == 1

    def test_text_filter_by_component(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("API")
        assert len(_accepted_rows(proxy, source)) == 1

    def test_text_filter_case_insensitive(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("auth")
        assert len(_accepted_rows(proxy, source)) == 2

    def test_text_filter_partial_match(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("001")
        assert len(_accepted_rows(proxy, source)) == 3  # AUTH-001, DASH-001, API-001

    def test_text_filter_no_match(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("NONEXISTENT")
        assert len(_accepted_rows(proxy, source)) == 0

    def test_text_filter_empty_shows_all(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("AUTH")
        assert len(_accepted_rows(proxy, source)) == 2
        proxy.set_text_filter("")
        assert len(_accepted_rows(proxy, source)) == 5


# ---------------------------------------------------------------------------
# Tests: status filter
# ---------------------------------------------------------------------------


class TestStatusFilter:  # noqa: D101
    def test_status_filter_backlog(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("BACKLOG")
        assert len(_accepted_rows(proxy, source)) == 2

    def test_status_filter_execucao(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("EXECUCAO")
        assert len(_accepted_rows(proxy, source)) == 1

    def test_status_filter_concluido(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("CONCLUIDO")
        assert len(_accepted_rows(proxy, source)) == 1

    def test_status_filter_none_shows_all(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("BACKLOG")
        assert len(_accepted_rows(proxy, source)) == 2
        proxy.set_status_filter(None)
        assert len(_accepted_rows(proxy, source)) == 5

    def test_status_filter_no_match(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("IMPEDIDO")
        assert len(_accepted_rows(proxy, source)) == 0


# ---------------------------------------------------------------------------
# Tests: feature filter
# ---------------------------------------------------------------------------


class TestFeatureFilter:  # noqa: D101
    def test_feature_filter_by_id(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_feature_filter(1)
        assert len(_accepted_rows(proxy, source)) == 2

    def test_feature_filter_different_id(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_feature_filter(2)
        assert len(_accepted_rows(proxy, source)) == 2

    def test_feature_filter_none_shows_all(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_feature_filter(1)
        assert len(_accepted_rows(proxy, source)) == 2
        proxy.set_feature_filter(None)
        assert len(_accepted_rows(proxy, source)) == 5

    def test_feature_filter_no_match(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_feature_filter(999)
        assert len(_accepted_rows(proxy, source)) == 0


# ---------------------------------------------------------------------------
# Tests: composite (AND) filters
# ---------------------------------------------------------------------------


class TestCompositeFilters:  # noqa: D101
    def test_text_and_status(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        assert len(_accepted_rows(proxy, source)) == 1  # AUTH-001

    def test_text_and_feature(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("001")
        proxy.set_feature_filter(1)
        assert len(_accepted_rows(proxy, source)) == 1  # AUTH-001

    def test_status_and_feature(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)
        assert len(_accepted_rows(proxy, source)) == 1  # DASH-001

    def test_all_three_filters(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("DASH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)
        assert len(_accepted_rows(proxy, source)) == 1  # DASH-001

    def test_all_three_filters_no_match(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_and_source
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)  # AUTH is feature 1, not 2
        assert len(_accepted_rows(proxy, source)) == 0


# ---------------------------------------------------------------------------
# Tests: has_active_filters property
# ---------------------------------------------------------------------------


class TestHasActiveFilters:  # noqa: D101
    def test_no_filters_active(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        assert proxy.has_active_filters is False

    def test_text_filter_active(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_text_filter("test")
        assert proxy.has_active_filters is True

    def test_status_filter_active(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_status_filter("BACKLOG")
        assert proxy.has_active_filters is True

    def test_feature_filter_active(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_feature_filter(1)
        assert proxy.has_active_filters is True

    def test_clear_text_filter_deactivates(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_text_filter("test")
        assert proxy.has_active_filters is True
        proxy.set_text_filter("")
        assert proxy.has_active_filters is False

    def test_clear_status_filter_deactivates(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_status_filter("BACKLOG")
        assert proxy.has_active_filters is True
        proxy.set_status_filter(None)
        assert proxy.has_active_filters is False

    def test_multiple_filters_all_must_clear(
        self, proxy_and_source: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_and_source
        proxy.set_text_filter("test")
        proxy.set_status_filter("BACKLOG")
        proxy.set_text_filter("")
        assert proxy.has_active_filters is True  # status still active
        proxy.set_status_filter(None)
        assert proxy.has_active_filters is False


# ---------------------------------------------------------------------------
# Tests: __init__ constructor (lines 32-42)
# ---------------------------------------------------------------------------


class TestConstructor:  # noqa: D101
    def test_init_sets_default_filters(self) -> None:
        """Verify __init__ initializes filters and resolves column indices."""
        proxy = FilterProxyModel()
        assert proxy._text_filter == ""
        assert proxy._status_filter is None
        assert proxy._feature_filter is None

    def test_init_resolves_column_indices(self) -> None:
        """Verify __init__ resolves column indices from StoryTableModel.COLUMNS."""
        proxy = FilterProxyModel()
        assert proxy._col_id == StoryTableModel.COLUMNS.index("ID")
        assert proxy._col_component == StoryTableModel.COLUMNS.index("Componente")
        assert proxy._col_name == StoryTableModel.COLUMNS.index("Nome")
        assert proxy._col_status == StoryTableModel.COLUMNS.index("Status")

    def test_init_with_parent(self) -> None:
        """Verify __init__ accepts an optional parent argument."""
        parent = MagicMock()
        proxy = FilterProxyModel(parent)
        assert proxy._text_filter == ""
        assert proxy._col_id == StoryTableModel.COLUMNS.index("ID")


# ---------------------------------------------------------------------------
# Tests: filterAcceptsRow with non-StoryTableModel source (line 98)
# ---------------------------------------------------------------------------


class TestNonStoryTableModelSource:  # noqa: D101
    def test_filter_accepts_row_with_non_story_source_model(self) -> None:
        """When sourceModel is not a StoryTableModel, filterAcceptsRow returns True."""
        proxy = FilterProxyModel.__new__(FilterProxyModel)
        proxy._text_filter = "something"
        proxy._status_filter = "BACKLOG"
        proxy._feature_filter = 1
        proxy._col_id = StoryTableModel.COLUMNS.index("ID")
        proxy._col_component = StoryTableModel.COLUMNS.index("Componente")
        proxy._col_name = StoryTableModel.COLUMNS.index("Nome")
        proxy._col_status = StoryTableModel.COLUMNS.index("Status")
        # sourceModel returns a plain MagicMock (not StoryTableModel)
        proxy.sourceModel = lambda: MagicMock()
        proxy.invalidateFilter = lambda: None

        parent = MagicMock()
        assert proxy.filterAcceptsRow(0, parent) is True

    def test_filter_accepts_row_with_none_source_model(self) -> None:
        """When sourceModel returns None, filterAcceptsRow returns True."""
        proxy = FilterProxyModel.__new__(FilterProxyModel)
        proxy._text_filter = "test"
        proxy._status_filter = None
        proxy._feature_filter = None
        proxy._col_id = StoryTableModel.COLUMNS.index("ID")
        proxy._col_component = StoryTableModel.COLUMNS.index("Componente")
        proxy._col_name = StoryTableModel.COLUMNS.index("Nome")
        proxy._col_status = StoryTableModel.COLUMNS.index("Status")
        proxy.sourceModel = lambda: None
        proxy.invalidateFilter = lambda: None

        parent = MagicMock()
        assert proxy.filterAcceptsRow(0, parent) is True
