"""E2E tests for EP-023: Reset Planning feature."""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.presentation.container import DIContainer

pytestmark = [pytest.mark.e2e]


async def _populate_stories_with_planning(container: DIContainer) -> None:
    """Populate database with stories that have planning data."""
    async with container.create_unit_of_work() as uow:
        # Create developers first (FK constraint)
        for i in range(1, 6):
            dev = Developer(name=f"Dev {i}")
            await uow.developers.add(dev)

        for i in range(1, 6):
            story = Story(
                id=f"TEST-{i:03d}",
                component="TEST",
                name=f"Historia {i}",
                story_points=StoryPoint(5),
                priority=i,
                status=StoryStatus.BACKLOG,
                duration=5,
                start_date=date(2026, 1, 5 + i),
                end_date=date(2026, 1, 9 + i),
                developer_id=i,
                feature_id=None,
            )
            await uow.stories.add(story)
        await uow.commit()


async def _populate_stories_without_planning(container: DIContainer) -> None:
    """Populate database with stories that have NO planning data."""
    async with container.create_unit_of_work() as uow:
        for i in range(1, 4):
            story = Story(
                id=f"TEST-{i:03d}",
                component="TEST",
                name=f"Historia {i}",
                story_points=StoryPoint(5),
                priority=i,
                status=StoryStatus.BACKLOG,
            )
            await uow.stories.add(story)
        await uow.commit()


class TestButtonDisabledDuringOperation:
    """T024: Button should be disabled during reset operation."""

    def test_button_disabled_during_operation(
        self, qasync_loop, e2e_app, e2e_main_window, qtbot
    ):
        """Button should be disabled when reset is running."""
        qasync_loop.run_until_complete(_populate_stories_with_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        # Set _has_planning_data so button becomes enabled
        e2e_main_window._has_planning_data = True
        e2e_main_window._action_new_planning.setEnabled(True)

        # Simulate reset started
        e2e_main_window._on_reset_started()
        assert not e2e_main_window._action_new_planning.isEnabled()


class TestButtonDisabledNoPlanningData:
    """T025: Button should be disabled when no planning data exists."""

    def test_button_disabled_no_planning_data(
        self, qasync_loop, e2e_app, e2e_main_window, qtbot
    ):
        """Button should be disabled when stories have no calculated fields."""
        qasync_loop.run_until_complete(_populate_stories_without_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        assert not e2e_main_window._action_new_planning.isEnabled()


class TestButtonEnabledAfterSchedule:
    """T026: Button should be enabled after schedule calculation."""

    def test_button_enabled_after_schedule(
        self, qasync_loop, e2e_app, e2e_main_window, qtbot
    ):
        """Button should be enabled after stories get planning data."""
        qasync_loop.run_until_complete(_populate_stories_with_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        # _update_has_planning_data was called in _on_stories_changed
        assert e2e_main_window._has_planning_data is True
        assert e2e_main_window._action_new_planning.isEnabled()


class TestFullResetFlow:
    """T031: Full reset flow E2E test."""

    def test_full_reset_flow(self, qasync_loop, e2e_app, e2e_main_window, qtbot):
        """Load stories with planning -> execute reset -> verify cleared."""
        qasync_loop.run_until_complete(_populate_stories_with_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        assert e2e_main_window._has_planning_data is True

        # Execute reset directly via ViewModel
        reset_vm = e2e_app.reset_planning_viewmodel
        result = qasync_loop.run_until_complete(reset_vm.execute())

        assert result is not None
        assert result.success is True
        assert result.stories_reset == 5

        # Reload stories and verify fields cleared
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        # All stories should have no planning data now
        for story in e2e_main_window.viewmodel.stories:
            assert story.duration is None
            assert story.start_date is None
            assert story.end_date is None
            assert story.developer_id is None

        assert e2e_main_window._has_planning_data is False


class TestCancelFlow:
    """T032: Cancel flow preserves data."""

    def test_cancel_preserves_data(self, qasync_loop, e2e_app, e2e_main_window, qtbot):
        """Dialog cancel should preserve planning data."""
        qasync_loop.run_until_complete(_populate_stories_with_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        assert e2e_main_window._has_planning_data is True

        # Preview counts without executing reset
        reset_vm = e2e_app.reset_planning_viewmodel
        counts = qasync_loop.run_until_complete(reset_vm.preview())

        assert counts is not None
        assert counts.total == 5

        # Verify data is still intact (cancel scenario = no execute)
        for story in e2e_main_window.viewmodel.stories:
            assert story.duration is not None


class TestDoubleReset:
    """T033: Double reset shows 0 affected, button disabled."""

    def test_double_reset(self, qasync_loop, e2e_app, e2e_main_window, qtbot):
        """Second reset should find 0 affected stories."""
        qasync_loop.run_until_complete(_populate_stories_with_planning(e2e_app))
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        # First reset
        reset_vm = e2e_app.reset_planning_viewmodel
        result1 = qasync_loop.run_until_complete(reset_vm.execute())
        assert result1.stories_reset == 5

        # Reload to update state
        qasync_loop.run_until_complete(e2e_main_window.viewmodel.load_stories())

        # Second reset attempt - preview shows 0
        counts = qasync_loop.run_until_complete(reset_vm.preview())
        assert counts.total == 0

        # Button should be disabled
        assert e2e_main_window._has_planning_data is False
        assert not e2e_main_window._action_new_planning.isEnabled()
