"""Tests for FilterProxyModel.

This module contains unit tests for the FilterProxyModel class,
verifying text, status, and feature filtering with AND logic.
"""

from __future__ import annotations

import pytest
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.filter_proxy_model import FilterProxyModel
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel
from PySide6.QtCore import Qt


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
    """Create a StoryOutputDTO for testing."""
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
    """Sample stories for filter tests."""
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


@pytest.fixture()
def proxy_with_stories(
    qapp, stories: list[StoryOutputDTO]
) -> tuple[FilterProxyModel, StoryTableModel]:
    """Create a FilterProxyModel with a populated StoryTableModel."""
    source = StoryTableModel()
    source.set_stories(stories)

    proxy = FilterProxyModel()
    proxy.setSourceModel(source)

    return proxy, source


class TestTextFilter:
    """Tests for text filter functionality."""

    def test_text_filter_by_id(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("AUTH")
        assert proxy.rowCount() == 2

    def test_text_filter_by_name(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("Dashboard")
        assert proxy.rowCount() == 1

    def test_text_filter_by_component(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("API")
        assert proxy.rowCount() == 1

    def test_text_filter_case_insensitive(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("auth")
        assert proxy.rowCount() == 2

    def test_text_filter_partial_match(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("001")
        assert proxy.rowCount() == 3  # AUTH-001, DASH-001, API-001

    def test_text_filter_no_match(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("NONEXISTENT")
        assert proxy.rowCount() == 0

    def test_text_filter_empty_shows_all(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("AUTH")
        assert proxy.rowCount() == 2
        proxy.set_text_filter("")
        assert proxy.rowCount() == 5


class TestStatusFilter:
    """Tests for status filter functionality."""

    def test_status_filter_backlog(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 2

    def test_status_filter_execucao(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("EXECUCAO")
        assert proxy.rowCount() == 1

    def test_status_filter_concluido(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("CONCLUIDO")
        assert proxy.rowCount() == 1

    def test_status_filter_none_shows_all(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 2
        proxy.set_status_filter(None)
        assert proxy.rowCount() == 5

    def test_status_filter_no_match(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("IMPEDIDO")
        assert proxy.rowCount() == 0


class TestFeatureFilter:
    """Tests for feature filter functionality."""

    def test_feature_filter_by_id(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 2

    def test_feature_filter_different_id(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_feature_filter(2)
        assert proxy.rowCount() == 2

    def test_feature_filter_none_shows_all(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 2
        proxy.set_feature_filter(None)
        assert proxy.rowCount() == 5

    def test_feature_filter_no_match(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_feature_filter(999)
        assert proxy.rowCount() == 0


class TestCompositeFilters:
    """Tests for AND combination of multiple filters."""

    def test_text_and_status(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 1  # Only AUTH-001

    def test_text_and_feature(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("001")
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 1  # Only AUTH-001

    def test_status_and_feature(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)
        assert proxy.rowCount() == 1  # Only DASH-001

    def test_all_three_filters(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("DASH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)
        assert proxy.rowCount() == 1  # Only DASH-001

    def test_all_three_filters_no_match(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(2)  # AUTH is feature 1, not 2
        assert proxy.rowCount() == 0


class TestHasActiveFilters:
    """Tests for the has_active_filters property."""

    def test_no_filters_active(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        assert proxy.has_active_filters is False

    def test_text_filter_active(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("test")
        assert proxy.has_active_filters is True

    def test_status_filter_active(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("BACKLOG")
        assert proxy.has_active_filters is True

    def test_feature_filter_active(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_feature_filter(1)
        assert proxy.has_active_filters is True

    def test_clear_text_filter_deactivates(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("test")
        assert proxy.has_active_filters is True
        proxy.set_text_filter("")
        assert proxy.has_active_filters is False

    def test_clear_status_filter_deactivates(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("BACKLOG")
        assert proxy.has_active_filters is True
        proxy.set_status_filter(None)
        assert proxy.has_active_filters is False

    def test_multiple_filters_all_must_clear(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_text_filter("test")
        proxy.set_status_filter("BACKLOG")
        proxy.set_text_filter("")
        assert proxy.has_active_filters is True  # status still active
        proxy.set_status_filter(None)
        assert proxy.has_active_filters is False


class TestProxyDataAccess:
    """Tests for accessing data through the proxy model."""

    def test_user_role_returns_story_id(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, source = proxy_with_stories
        index = proxy.index(0, 0)
        story_id = proxy.data(index, Qt.ItemDataRole.UserRole)
        assert story_id == "AUTH-001"

    def test_filtered_proxy_returns_correct_ids(
        self, proxy_with_stories: tuple[FilterProxyModel, StoryTableModel]
    ) -> None:
        proxy, _ = proxy_with_stories
        proxy.set_status_filter("EXECUCAO")
        assert proxy.rowCount() == 1
        index = proxy.index(0, 0)
        story_id = proxy.data(index, Qt.ItemDataRole.UserRole)
        assert story_id == "AUTH-002"
