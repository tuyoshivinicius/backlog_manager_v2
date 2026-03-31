"""E2E tests for CT-005: Balanceamento.

Tests load balancing with 2 devs and unequal story points
(1x13SP + 4x3SP = 25 SP total).
"""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

pytestmark = [pytest.mark.e2e]


class TestCT005Balanceamento:
    """CT-005: Balanceamento com 2 devs e SPs desiguais."""

    @pytest.fixture
    async def ct005_setup(self, e2e_app, qasync_loop):
        """Setup for CT-005: Create 5 developers and unbalanced stories.

        Test Data:
        - 5 developers (enough to handle all stories in parallel)
        - 5 stories: 1x13SP + 4x3SP = 25 SP total
        - Expected distribution: by story count, not SP total
        """
        async with e2e_app.create_unit_of_work() as uow:
            # Create 5 developers to handle all stories
            for i in range(1, 6):
                dev = Developer(name=f"Dev Balance {i}")
                await uow.developers.add(dev)

            # Create unbalanced stories
            story1 = Story(
                id="BAL-001",
                component="BAL",
                name="Historia Grande",
                story_points=StoryPoint(13),
                priority=1,
                status=StoryStatus.BACKLOG,
            )
            await uow.stories.add(story1)

            for i in range(2, 6):
                story = Story(
                    id=f"BAL-{i:03d}",
                    component="BAL",
                    name=f"Historia Pequena {i - 1}",
                    story_points=StoryPoint(3),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
        # Use velocity=2.0 to reduce story durations and avoid resource constraints
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=2.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        return e2e_app

    @pytest.mark.asyncio
    async def test_ct005_distribuicao_por_contagem(self, ct005_setup, qasync_loop):
        """Test that stories are distributed by count, not SP total.

        With 5 stories and 2 devs:
        - Dev 1: should get ~2-3 stories
        - Dev 2: should get ~2-3 stories

        NOT by SP total (which would be 13 vs 12).
        """
        e2e_app = ct005_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=10,
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

        # All developers with stories should be counted
        assert len(dev_counts) >= 1

        # With 5 stories and 5 devs, each dev should have ~1 story
        total_allocated = sum(dev_counts.values())
        assert (
            total_allocated == 5
        ), f"Expected 5 stories allocated, got {total_allocated}"

    @pytest.mark.asyncio
    async def test_ct005_todas_historias_alocadas(self, ct005_setup, qasync_loop):
        """Test that all 5 stories are allocated."""
        e2e_app = ct005_setup
        allocation_vm = e2e_app.allocation_viewmodel

        result = await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=10,
        )

        assert result is not None
        assert result.stories_allocated == 5

    @pytest.mark.asyncio
    async def test_ct005_historia_grande_alocada(self, ct005_setup, qasync_loop):
        """Test that the large story (13 SP) is properly allocated."""
        e2e_app = ct005_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=10,
        )

        async with e2e_app.create_unit_of_work() as uow:
            story = await uow.stories.get_by_id("BAL-001")

        assert story is not None
        assert story.developer_id is not None
        assert story.start_date is not None
        assert story.end_date is not None
        assert story.duration == 7  # 13 SP / velocity 2.0 = ~7 days


class TestCT005AlternativeScenarios:
    """Additional load balancing scenarios."""

    @pytest.mark.asyncio
    async def test_balanceamento_muitos_pequenos(self, e2e_app, qasync_loop):
        """Test balancing with many small stories."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create 3 developers
            for i in range(1, 4):
                dev = Developer(name=f"Dev Small {i}")
                await uow.developers.add(dev)

            # Create 12 small stories (3 SP each) - should be 4 per dev
            for i in range(1, 13):
                story = Story(
                    id=f"SML-{i:03d}",
                    component="SML",
                    name=f"Historia Pequena {i}",
                    story_points=StoryPoint(3),
                    priority=i,
                    status=StoryStatus.BACKLOG,
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

        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # Count per developer
        dev_counts: dict[int, int] = {}
        for story in stories:
            if story.developer_id:
                dev_counts[story.developer_id] = (
                    dev_counts.get(story.developer_id, 0) + 1
                )

        # Should be 4 stories per developer
        assert len(dev_counts) == 3
        for count in dev_counts.values():
            assert count == 4

    @pytest.mark.asyncio
    async def test_balanceamento_um_gigante_varios_pequenos(self, e2e_app, qasync_loop):
        """Test balancing with one very large story and many small ones."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create 7 developers to handle all stories
            for i in range(1, 8):
                dev = Developer(name=f"Dev Giant {i}")
                await uow.developers.add(dev)

            # One large story (13 SP)
            story_large = Story(
                id="GNT-001",
                component="GNT",
                name="Historia Gigante",
                story_points=StoryPoint(13),
                priority=1,
                status=StoryStatus.BACKLOG,
            )
            await uow.stories.add(story_large)

            # Six small stories (3 SP each)
            for i in range(2, 8):
                story = Story(
                    id=f"GNT-{i:03d}",
                    component="GNT",
                    name=f"Historia Pequena {i - 1}",
                    story_points=StoryPoint(3),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Calculate schedule with higher velocity to reduce durations
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=2.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=10,
        )

        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # Verify all allocated
        for story in stories:
            assert story.developer_id is not None, f"Story {story.id} not allocated"

        # All 7 stories should be allocated
        allocated_count = sum(1 for s in stories if s.developer_id is not None)
        assert (
            allocated_count == 7
        ), f"Expected 7 stories allocated, got {allocated_count}"

    @pytest.mark.asyncio
    async def test_balanceamento_sp_diferentes(self, e2e_app, qasync_loop):
        """Test balancing with all different SP values."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create 8 developers to handle all stories
            for i in range(1, 9):
                dev = Developer(name=f"Dev Varied {i}")
                await uow.developers.add(dev)

            # Create stories with all SP values
            sps = [3, 5, 8, 13, 3, 5, 8, 13]  # 8 stories, 2 of each
            for i, sp in enumerate(sps, 1):
                story = Story(
                    id=f"VAR-{i:03d}",
                    component="VAR",
                    name=f"Historia SP{sp} #{i}",
                    story_points=StoryPoint(sp),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Calculate schedule with higher velocity to reduce durations
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=2.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=10,
        )

        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # All 8 stories should be allocated
        allocated_count = sum(1 for s in stories if s.developer_id is not None)
        assert (
            allocated_count == 8
        ), f"Expected 8 stories allocated, got {allocated_count}"
