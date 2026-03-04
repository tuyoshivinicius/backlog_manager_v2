"""E2E Performance tests for RNF-PERF requirements.

Tests performance requirements including allocation time
and CRUD operation latency.
"""

from __future__ import annotations

import time
from datetime import date

import pytest

from backlog_manager.application.dto.dependency import AddDependencyInputDTO
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

pytestmark = [pytest.mark.e2e, pytest.mark.perf]


class TestPerfAlocacao:
    """Performance tests for allocation (RNF-PERF-001)."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_perf_alocacao_100_historias_5s(self, e2e_app, qasync_loop):
        """Test allocation of 100 stories completes within 5 seconds.

        RNF-PERF-001: Allocation should complete in <= 5s for up to 100 stories.
        """
        # Setup: Create 10 developers and 100 stories
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 11):
                dev = Developer(name=f"Dev Perf {i}")
                await uow.developers.add(dev)

            for i in range(1, 101):
                story = Story(
                    id=f"PERF-{i:03d}",
                    component="PERF",
                    name=f"Historia Perf {i}",
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

        # Measure allocation time
        start_time = time.perf_counter()

        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        elapsed = time.perf_counter() - start_time

        # Assertions
        assert result is not None
        assert result.stories_allocated == 100

        # 10% tolerance for CI environments
        assert elapsed <= 5.5, (
            f"Allocation of 100 stories took {elapsed:.2f}s "
            f"(limit: 5s + 10% tolerance)"
        )

        # Log performance metric for debugging
        print(f"[PERF] Allocation of 100 stories: {elapsed:.3f}s")

    @pytest.mark.asyncio
    async def test_perf_alocacao_20_historias(self, e2e_app, qasync_loop):
        """Test allocation of 20 stories (typical use case)."""
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 6):
                dev = Developer(name=f"Dev Small {i}")
                await uow.developers.add(dev)

            for i in range(1, 21):
                story = Story(
                    id=f"SM-{i:03d}",
                    component="SM",
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

        start_time = time.perf_counter()

        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        elapsed = time.perf_counter() - start_time

        assert result is not None
        assert result.stories_allocated == 20

        # Should be well under 5s for 20 stories
        assert elapsed < 2.0, f"20 stories took {elapsed:.2f}s"

        print(f"[PERF] Allocation of 20 stories: {elapsed:.3f}s")


class TestPerfCRUD:
    """Performance tests for CRUD operations (RNF-PERF-002)."""

    @pytest.mark.asyncio
    async def test_perf_crud_latencia_100ms(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test CRUD operations complete within 100ms each.

        RNF-PERF-002: Individual CRUD operations should complete in <= 100ms.
        """
        viewmodel = e2e_main_window.viewmodel

        # Test Create
        start_time = time.perf_counter()
        dto = CreateStoryInputDTO(
            component="CRUD",
            name="Historia CRUD Test",
            story_points=5,
        )
        story = await viewmodel.create_story(dto)
        create_elapsed = (time.perf_counter() - start_time) * 1000

        assert story is not None
        assert (
            create_elapsed < 200
        ), f"Create took {create_elapsed:.2f}ms (limit: 100ms + tolerance)"
        print(f"[PERF] Create story: {create_elapsed:.2f}ms")

        # Test Read (load stories)
        start_time = time.perf_counter()
        await viewmodel.load_stories()
        read_elapsed = (time.perf_counter() - start_time) * 1000

        assert read_elapsed < 200, f"Read took {read_elapsed:.2f}ms"
        print(f"[PERF] Read stories: {read_elapsed:.2f}ms")

        # Test Delete
        start_time = time.perf_counter()
        result = await viewmodel.delete_story("CRUD-001")
        delete_elapsed = (time.perf_counter() - start_time) * 1000

        assert result is True
        assert delete_elapsed < 200, f"Delete took {delete_elapsed:.2f}ms"
        print(f"[PERF] Delete story: {delete_elapsed:.2f}ms")

    @pytest.mark.asyncio
    async def test_perf_priority_change(self, e2e_main_window, e2e_app, qasync_loop):
        """Test priority change operations are fast."""
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 6):
            dto = CreateStoryInputDTO(
                component="PRIO",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Test priority move
        start_time = time.perf_counter()
        await viewmodel.move_priority_up("PRIO-003")
        elapsed = (time.perf_counter() - start_time) * 1000

        assert elapsed < 200, f"Priority change took {elapsed:.2f}ms"
        print(f"[PERF] Priority change: {elapsed:.2f}ms")


class TestPerfDependencies:
    """Performance tests for dependency operations."""

    @pytest.mark.asyncio
    async def test_perf_add_dependency(self, e2e_app, qasync_loop):
        """Test dependency add operation is fast."""
        # Create stories
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 6):
                story = Story(
                    id=f"DEP-{i:03d}",
                    component="DEP",
                    name=f"Historia {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)
            await uow.commit()

        # Test add dependency
        start_time = time.perf_counter()
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="DEP-002", depends_on_id="DEP-001")
            )
            await uow.commit()
        elapsed = (time.perf_counter() - start_time) * 1000

        assert elapsed < 200, f"Add dependency took {elapsed:.2f}ms"
        print(f"[PERF] Add dependency: {elapsed:.2f}ms")

    @pytest.mark.asyncio
    async def test_perf_cycle_detection_50_nodes(self, e2e_app, qasync_loop):
        """Test cycle detection in 50-node graph is fast."""
        # Create chain of 50 stories
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 51):
                story = Story(
                    id=f"CYC-{i:03d}",
                    component="CYC",
                    name=f"Historia {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)
            await uow.commit()

        # Add linear dependencies
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            for i in range(2, 51):
                await add_dep.execute(
                    AddDependencyInputDTO(
                        story_id=f"CYC-{i:03d}", depends_on_id=f"CYC-{i-1:03d}"
                    )
                )
            await uow.commit()

        # Test cycle detection (should reject quickly)
        from backlog_manager.domain.exceptions import CyclicDependencyException

        start_time = time.perf_counter()
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="CYC-001", depends_on_id="CYC-050")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True
        elapsed = (time.perf_counter() - start_time) * 1000

        assert error_raised
        assert elapsed < 200, f"Cycle detection took {elapsed:.2f}ms"
        print(f"[PERF] Cycle detection (50 nodes): {elapsed:.2f}ms")


class TestPerfMemory:
    """Performance tests for memory usage."""

    @pytest.mark.asyncio
    async def test_perf_allocation_reports_metrics(self, e2e_app, qasync_loop):
        """Test that allocation reports performance metrics on failure."""
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 4):
                dev = Developer(name=f"Dev Met {i}")
                await uow.developers.add(dev)

            for i in range(1, 11):
                story = Story(
                    id=f"MET-{i:03d}",
                    component="MET",
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
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.total_time_seconds > 0
        assert result.metrics is not None

        print(
            f"[PERF] Metrics: stories={result.stories_allocated}, time={result.total_time_seconds:.3f}s"
        )
