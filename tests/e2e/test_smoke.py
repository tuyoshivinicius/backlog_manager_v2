"""Smoke tests to validate E2E test infrastructure.

These tests verify that fixtures, factories, and Qt integration
work correctly before running the full E2E test suite.
"""

from __future__ import annotations

import pytest

from tests.e2e.factories import (
    create_cyclic_graph,
    create_developers,
    create_features,
    create_stories,
    create_unbalanced_stories,
    get_dependency_pairs,
)

pytestmark = [pytest.mark.e2e]


class TestFactories:
    """Tests for factory functions."""

    def test_create_stories_default(self):
        """Test create_stories with default parameters."""
        stories = create_stories()

        assert len(stories) == 5
        assert stories[0].id == "TEST-001"
        assert stories[0].story_points.value == 5
        assert stories[0].priority == 1
        assert stories[4].id == "TEST-005"
        assert stories[4].priority == 5

    def test_create_stories_custom(self):
        """Test create_stories with custom parameters."""
        stories = create_stories(
            count=10,
            component="CUSTOM",
            story_points=8,
            feature_id=1,
            start_priority=10,
        )

        assert len(stories) == 10
        assert stories[0].id == "CUSTOM-001"
        assert stories[0].story_points.value == 8
        assert stories[0].priority == 10
        assert stories[0].feature_id == 1
        assert stories[9].id == "CUSTOM-010"
        assert stories[9].priority == 19

    def test_get_dependency_pairs(self):
        """Test dependency pair generation."""
        stories = create_stories(count=5)
        pairs = get_dependency_pairs(stories)

        assert len(pairs) == 4
        assert pairs[0] == ("TEST-002", "TEST-001")
        assert pairs[3] == ("TEST-005", "TEST-004")

    def test_create_developers(self):
        """Test developer factory."""
        developers = create_developers(count=5)

        assert len(developers) == 5
        assert developers[0].name == "Dev 1"
        assert developers[4].name == "Dev 5"

    def test_create_features(self):
        """Test feature factory with default waves."""
        features = create_features(count=3)

        assert len(features) == 3
        assert features[0].name == "Feature 1"
        assert features[0].wave == 1
        assert features[2].name == "Feature 3"
        assert features[2].wave == 3

    def test_create_features_custom_waves(self):
        """Test feature factory with custom waves."""
        features = create_features(waves=[1, 3, 5])

        assert len(features) == 3
        assert features[0].wave == 1
        assert features[1].wave == 3
        assert features[2].wave == 5

    def test_create_cyclic_graph(self):
        """Test cyclic graph generation."""
        stories, deps = create_cyclic_graph(node_count=10)

        assert len(stories) == 10
        assert len(deps) == 10  # 9 linear + 1 cycle

        # Verify cycle exists
        cycle_dep = deps[-1]
        assert cycle_dep == ("CYCLE-010", "CYCLE-001")

    def test_create_cyclic_graph_custom_cycle_at(self):
        """Test cyclic graph with custom cycle point."""
        stories, deps = create_cyclic_graph(node_count=10, cycle_at=5)

        # Cycle should close at position 5 back to position 0
        cycle_dep = deps[-1]
        assert cycle_dep == ("CYCLE-006", "CYCLE-001")

    def test_create_unbalanced_stories(self):
        """Test unbalanced stories for load balancing tests."""
        stories = create_unbalanced_stories(
            large_sp=13,
            small_sp=3,
            small_count=4,
        )

        assert len(stories) == 5
        assert stories[0].story_points.value == 13
        assert stories[1].story_points.value == 3
        assert stories[4].story_points.value == 3


class TestFixtures:
    """Tests for E2E fixtures."""

    def test_qasync_loop_exists(self, qasync_loop):
        """Test that qasync_loop fixture provides an event loop."""
        import asyncio

        assert qasync_loop is not None
        assert asyncio.get_event_loop() == qasync_loop

    def test_e2e_app_exists(self, e2e_app):
        """Test that e2e_app fixture provides DIContainer."""
        from backlog_manager.presentation.container import DIContainer

        assert e2e_app is not None
        assert isinstance(e2e_app, DIContainer)

    def test_e2e_main_window_exists(self, e2e_main_window):
        """Test that e2e_main_window fixture provides MainWindow."""
        from backlog_manager.presentation.views.main_window import MainWindow

        assert e2e_main_window is not None
        assert isinstance(e2e_main_window, MainWindow)
        assert e2e_main_window.isVisible()

    def test_e2e_main_window_has_table(self, e2e_main_window):
        """Test that MainWindow has story table."""
        table = e2e_main_window.story_table
        assert table is not None
        assert table.model() is not None


class TestQtBotIntegration:
    """Tests for qtbot integration."""

    def test_qtbot_can_interact_with_window(self, e2e_main_window, qtbot):
        """Test that qtbot can interact with widgets."""
        # Should not raise
        qtbot.waitExposed(e2e_main_window, timeout=1000)

    def test_window_title(self, e2e_main_window):
        """Test window has correct title."""
        assert e2e_main_window.windowTitle() == "Backlog Manager"

    def test_window_size(self, e2e_main_window):
        """Test window has correct initial size."""
        assert e2e_main_window.width() >= 1024
        assert e2e_main_window.height() >= 600


class TestAsyncIntegration:
    """Tests for async operation integration."""

    @pytest.mark.asyncio
    async def test_can_run_async_in_test(self, qasync_loop):
        """Test that async operations work in tests."""
        import asyncio

        result = await asyncio.sleep(0, result="done")
        assert result == "done"

    @pytest.mark.asyncio
    async def test_e2e_populated_db(self, e2e_populated_db):
        """Test that populated database fixture works."""
        # The fixture should have created test data
        developers = await e2e_populated_db.developers.get_all()
        assert len(developers) == 5

        features = await e2e_populated_db.features.get_all()
        assert len(features) == 2

        stories = await e2e_populated_db.stories.get_all()
        assert len(stories) == 10
