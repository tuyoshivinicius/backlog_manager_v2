"""E2E tests for CT-001: Backlog Completo.

Tests the complete backlog allocation scenario with
20 stories, 5 developers, and 2 features.
"""

from __future__ import annotations

import time
from datetime import date

import pytest
import pytest_asyncio
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

pytestmark = [pytest.mark.e2e]


class TestCT001BacklogCompleto:
    """CT-001: Backlog completo com 20 historias, 5 devs, 2 features."""

    @pytest_asyncio.fixture
    async def ct001_setup(self, e2e_app, qasync_loop):
        """Setup for CT-001: Create required test data.

        Test Data:
        - 5 developers
        - 2 features (wave 1 and wave 2)
        - 20 stories (10 per feature)
        """
        async with e2e_app.create_unit_of_work() as uow:
            # Create 5 developers
            for i in range(1, 6):
                dev = Developer(name=f"Dev CT001-{i}")
                await uow.developers.add(dev)

            # Create 2 features
            feature1 = Feature(name="Feature Wave 1", wave=1)
            feature2 = Feature(name="Feature Wave 2", wave=2)
            await uow.features.add(feature1)
            await uow.features.add(feature2)

            # Create 20 stories (10 per wave)
            for i in range(1, 11):
                story = Story(
                    id=f"CTWA-{i:03d}",
                    component="CTWA",
                    name=f"Historia Wave 1 - {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                    feature_id=1,
                )
                await uow.stories.add(story)

            for i in range(1, 11):
                story = Story(
                    id=f"CTWB-{i:03d}",
                    component="CTWB",
                    name=f"Historia Wave 2 - {i}",
                    story_points=StoryPoint(5),
                    priority=10 + i,
                    status=StoryStatus.BACKLOG,
                    feature_id=2,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        return e2e_app

    @pytest.mark.asyncio
    async def test_ct001_tempo_menor_5s(self, ct001_setup, qasync_loop):
        """Test that allocation completes in less than 5 seconds.

        RNF-PERF-001: Allocation should complete within 5s for up to 100 stories.
        """
        e2e_app = ct001_setup
        allocation_vm = e2e_app.allocation_viewmodel

        start_time = time.perf_counter()

        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        elapsed = time.perf_counter() - start_time

        assert result is not None
        # Tolerance of 10% for CI environments
        assert elapsed < 5.5, f"Allocation took {elapsed:.2f}s (limit: 5s + 10%)"

    @pytest.mark.asyncio
    async def test_ct001_todas_alocadas(self, ct001_setup, qasync_loop):
        """Test that all 20 stories are allocated."""
        e2e_app = ct001_setup
        allocation_vm = e2e_app.allocation_viewmodel

        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 20

        # Verify all stories have developer and dates
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        for story in stories:
            assert story.developer_id is not None, f"Story {story.id} has no developer"
            assert story.start_date is not None, f"Story {story.id} has no start_date"
            assert story.end_date is not None, f"Story {story.id} has no end_date"

    @pytest.mark.asyncio
    async def test_ct001_distribuicao_balanceada(self, ct001_setup, qasync_loop):
        """Test that stories are balanced across developers.

        With 20 stories and 5 developers, each should have ~4 stories.
        """
        e2e_app = ct001_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Count stories per developer
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        dev_counts: dict[int, int] = {}
        for story in stories:
            if story.developer_id:
                dev_counts[story.developer_id] = (
                    dev_counts.get(story.developer_id, 0) + 1
                )

        # All 5 developers should have stories
        assert len(dev_counts) == 5

        # Each should have approximately 4 stories (allow +-1 for balancing)
        for dev_id, count in dev_counts.items():
            assert 3 <= count <= 5, f"Dev {dev_id} has {count} stories (expected ~4)"

    @pytest.mark.asyncio
    async def test_ct001_wave_order_respected(self, ct001_setup, qasync_loop):
        """Test that wave 1 stories start before wave 2."""
        e2e_app = ct001_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Get stories by wave
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        w1_stories = [s for s in stories if s.id.startswith("CTWA")]
        w2_stories = [s for s in stories if s.id.startswith("CTWB")]

        # Get latest start date in wave 1
        max_w1_start = max(s.start_date for s in w1_stories if s.start_date)

        # Get earliest start date in wave 2
        min_w2_start = min(s.start_date for s in w2_stories if s.start_date)

        # Wave 2 should not start before wave 1
        assert max_w1_start <= min_w2_start

    @pytest.mark.asyncio
    async def test_ct001_metrics_returned(self, ct001_setup, qasync_loop):
        """Test that allocation returns proper metrics."""
        e2e_app = ct001_setup
        allocation_vm = e2e_app.allocation_viewmodel

        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 20
        assert result.total_time_seconds > 0
        assert result.metrics is not None
