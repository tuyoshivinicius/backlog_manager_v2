"""E2E tests for CT-003: Deadlock de Desenvolvedores.

Tests resource allocation when there are more stories than
developer capacity (1 dev, 2 concurrent stories).
"""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

pytestmark = [pytest.mark.e2e]


class TestCT003DeadlockDevs:
    """CT-003: Cenario com 1 dev e 2 historias concorrentes."""

    @pytest.fixture
    async def ct003_setup(self, e2e_app, qasync_loop):
        """Setup for CT-003: Create 1 developer and 2 concurrent stories.

        Test Data:
        - 1 developer
        - 2 stories that would start at the same time without sequencing
        """
        async with e2e_app.create_unit_of_work() as uow:
            # Create 1 developer
            dev = Developer(name="Dev Unico")
            await uow.developers.add(dev)

            # Create 2 stories that would conflict
            story1 = Story(
                id="CTHR-001",
                component="CTHR",
                name="Historia 1",
                story_points=StoryPoint(8),  # 8 SP = ~4 days with velocity 2
                priority=1,
                status=StoryStatus.BACKLOG,
            )
            story2 = Story(
                id="CTHR-002",
                component="CTHR",
                name="Historia 2",
                story_points=StoryPoint(8),
                priority=2,
                status=StoryStatus.BACKLOG,
            )
            await uow.stories.add(story1)
            await uow.stories.add(story2)

            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=2.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        return e2e_app

    @pytest.mark.asyncio
    async def test_ct003_ajuste_data_sem_crash(self, ct003_setup, qasync_loop):
        """Test that allocation handles resource conflict without crash.

        With 1 dev and 2 stories, the second story must wait for the first.
        """
        e2e_app = ct003_setup
        allocation_vm = e2e_app.allocation_viewmodel

        # Should not crash - allocation should sequence the stories
        result = await allocation_vm.execute(
            velocity=2.0,  # 2 SP/day
            start_date=date(2026, 1, 5),  # Monday
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 2

    @pytest.mark.asyncio
    async def test_ct003_segunda_historia_comeca_apos_primeira(
        self, ct003_setup, qasync_loop
    ):
        """Test that second story starts after first completes."""
        e2e_app = ct003_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Get stories
        async with e2e_app.create_unit_of_work() as uow:
            story1 = await uow.stories.get_by_id("CTHR-001")
            story2 = await uow.stories.get_by_id("CTHR-002")

        assert story1 is not None
        assert story2 is not None

        assert story1.end_date is not None
        assert story2.start_date is not None

        # Story 2 should start after story 1 ends
        assert story1.end_date <= story2.start_date

    @pytest.mark.asyncio
    async def test_ct003_ambas_historias_alocadas_mesmo_dev(
        self, ct003_setup, qasync_loop
    ):
        """Test that both stories are allocated to the same developer."""
        e2e_app = ct003_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Get stories
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # Both should be allocated to dev 1
        for story in stories:
            assert story.developer_id == 1

    @pytest.mark.asyncio
    async def test_ct003_prioridade_respeitada(self, ct003_setup, qasync_loop):
        """Test that priority order is respected in allocation."""
        e2e_app = ct003_setup
        allocation_vm = e2e_app.allocation_viewmodel

        await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Get stories
        async with e2e_app.create_unit_of_work() as uow:
            story1 = await uow.stories.get_by_id("CTHR-001")
            story2 = await uow.stories.get_by_id("CTHR-002")

        # Story 1 (priority 1) should start first
        assert story1.start_date < story2.start_date


class TestCT003MultipleDevs:
    """Tests for resource allocation with multiple developers."""

    @pytest.mark.asyncio
    async def test_historias_distribuidas_quando_ha_devs(self, e2e_app, qasync_loop):
        """Test that stories are distributed when there are enough devs."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create 2 developers
            for i in range(1, 3):
                dev = Developer(name=f"Dev {i}")
                await uow.developers.add(dev)

            # Create 2 stories
            for i in range(1, 3):
                story = Story(
                    id=f"DIST-{i:03d}",
                    component="DIST",
                    name=f"Historia {i}",
                    story_points=StoryPoint(8),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
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
            max_idle_days=5,
        )

        # Get stories
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # With 2 devs and 2 stories, they can work in parallel
        dev_ids = {s.developer_id for s in stories}
        assert len(dev_ids) == 2  # Each story has different dev

        # Both stories should start on the same day
        start_dates = {s.start_date for s in stories}
        assert len(start_dates) == 1  # Same start date


class TestCT003NoDevs:
    """Tests for allocation without developers."""

    @pytest.mark.asyncio
    async def test_sem_devs_nenhuma_alocacao(self, e2e_app, qasync_loop):
        """Test that no allocation happens without developers."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create story but no developers
            story = Story(
                id="NODEV-001",
                component="NODEV",
                name="Historia Sem Dev",
                story_points=StoryPoint(5),
                priority=1,
                status=StoryStatus.BACKLOG,
            )
            await uow.stories.add(story)
            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=2.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        allocation_vm = e2e_app.allocation_viewmodel

        result = await allocation_vm.execute(
            velocity=2.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Should have warnings about no developers
        if result is not None:
            assert result.stories_allocated == 0 or len(allocation_vm.last_warnings) > 0


class TestCT003LongQueue:
    """Tests for long queue with single developer."""

    @pytest.mark.asyncio
    async def test_muitas_historias_um_dev(self, e2e_app, qasync_loop):
        """Test allocation of many stories to single developer."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create 1 developer
            dev = Developer(name="Dev Solo")
            await uow.developers.add(dev)

            # Create 10 stories
            for i in range(1, 11):
                story = Story(
                    id=f"SOLO-{i:03d}",
                    component="SOLO",
                    name=f"Historia {i}",
                    story_points=StoryPoint(5),
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

        result = await allocation_vm.execute(
            velocity=1.0,  # 1 SP/day
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 10

        # Verify sequential allocation
        async with e2e_app.create_unit_of_work() as uow:
            stories = await uow.stories.get_all()

        # Sort by start date
        sorted_stories = sorted(stories, key=lambda s: (s.start_date or date.min))

        # Each story should start after previous ends
        for i in range(1, len(sorted_stories)):
            prev = sorted_stories[i - 1]
            curr = sorted_stories[i]
            if prev.end_date and curr.start_date:
                assert prev.end_date <= curr.start_date
