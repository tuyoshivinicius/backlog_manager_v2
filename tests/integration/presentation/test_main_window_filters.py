"""Integration tests for composite filters in MainWindow.

Tests filter combinations (text + status + feature) with AND logic
using FilterProxyModel and StoryTableModel together.
"""

from __future__ import annotations

import pytest
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.filter_proxy_model import FilterProxyModel
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel


def _make_story(
    id: str,
    component: str,
    name: str,
    status: str,
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
def filter_setup(
    qapp,
) -> tuple[FilterProxyModel, StoryTableModel, list[StoryOutputDTO]]:
    """Create proxy+source with a rich set of stories for composite filter testing."""
    stories = [
        _make_story("AUTH-001", "AUTH", "Login page", "BACKLOG", 1, "Auth", 1, 0),
        _make_story("AUTH-002", "AUTH", "Signup form", "EXECUCAO", 1, "Auth", 1, 1),
        _make_story("AUTH-003", "AUTH", "Password reset", "BACKLOG", 1, "Auth", 1, 2),
        _make_story(
            "DASH-001", "DASH", "Dashboard view", "BACKLOG", 2, "Dashboard", 2, 3
        ),
        _make_story(
            "DASH-002", "DASH", "Chart widget", "CONCLUIDO", 2, "Dashboard", 2, 4
        ),
        _make_story("API-001", "API", "REST endpoints", "TESTES", 3, "API", 1, 5),
        _make_story("API-002", "API", "GraphQL layer", "EXECUCAO", 3, "API", 1, 6),
    ]

    source = StoryTableModel()
    source.set_stories(stories)

    proxy = FilterProxyModel()
    proxy.setSourceModel(source)

    return proxy, source, stories


class TestTextAndStatusFilter:
    """Test text + status filter combination."""

    def test_text_auth_and_status_backlog(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 2  # AUTH-001, AUTH-003

    def test_text_api_and_status_execucao(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("API")
        proxy.set_status_filter("EXECUCAO")
        assert proxy.rowCount() == 1  # API-002


class TestTextAndFeatureFilter:
    """Test text + feature filter combination."""

    def test_text_001_and_feature_auth(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("001")
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 1  # AUTH-001

    def test_text_dash_and_feature_dashboard(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("DASH")
        proxy.set_feature_filter(2)
        assert proxy.rowCount() == 2  # DASH-001, DASH-002


class TestStatusAndFeatureFilter:
    """Test status + feature filter combination."""

    def test_status_backlog_and_feature_auth(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 2  # AUTH-001, AUTH-003

    def test_status_execucao_and_feature_api(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_status_filter("EXECUCAO")
        proxy.set_feature_filter(3)
        assert proxy.rowCount() == 1  # API-002


class TestAllThreeFilters:
    """Test text + status + feature combination."""

    def test_all_three_match(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 2  # AUTH-001, AUTH-003

    def test_all_three_no_match(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("DASH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(1)  # DASH is feature 2, not 1
        assert proxy.rowCount() == 0


class TestClearingFilters:
    """Test clearing one filter while others remain active."""

    def test_clear_text_keeps_status(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 2

        proxy.set_text_filter("")
        assert proxy.rowCount() == 3  # All BACKLOG: AUTH-001, AUTH-003, DASH-001

    def test_clear_status_keeps_text(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        assert proxy.rowCount() == 2

        proxy.set_status_filter(None)
        assert proxy.rowCount() == 3  # All AUTH: AUTH-001, AUTH-002, AUTH-003

    def test_clear_feature_keeps_others(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("001")
        proxy.set_feature_filter(1)
        assert proxy.rowCount() == 1

        proxy.set_feature_filter(None)
        assert proxy.rowCount() == 3  # AUTH-001, DASH-001, API-001


class TestMoveActionsWithFilters:
    """Test that has_active_filters reflects any combination of active filters."""

    def test_no_filters_allows_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        assert proxy.has_active_filters is False

    def test_text_filter_disables_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        assert proxy.has_active_filters is True

    def test_status_filter_disables_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_status_filter("BACKLOG")
        assert proxy.has_active_filters is True

    def test_feature_filter_disables_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_feature_filter(1)
        assert proxy.has_active_filters is True

    def test_combined_filters_disables_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(1)
        assert proxy.has_active_filters is True

    def test_clear_all_enables_move(
        self, filter_setup: tuple[FilterProxyModel, StoryTableModel, list]
    ) -> None:
        proxy, _, _ = filter_setup
        proxy.set_text_filter("AUTH")
        proxy.set_status_filter("BACKLOG")
        proxy.set_feature_filter(1)

        proxy.set_text_filter("")
        proxy.set_status_filter(None)
        proxy.set_feature_filter(None)
        assert proxy.has_active_filters is False
