"""E2E tests for UC-002: Alocacao Automatica.

Tests the automatic allocation flow including dependency handling,
holiday exclusion, and load balancing.
"""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.application.dto.dependency import AddDependencyInputDTO
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature

pytestmark = [pytest.mark.e2e]


class TestUC002AlocarComDependencias:
    """Tests for allocation with dependencies (FR-033)."""

    @pytest.mark.asyncio
    async def test_alocar_com_dependencias_respeita_ordem(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that allocation respects story dependencies.

        FR-033: Dependent stories should be scheduled after their dependencies.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developers
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev E2E")
            await uow.developers.add(dev)
            await uow.commit()

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="DEP",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Add dependencies: DEP-002 depends on DEP-001, DEP-003 depends on DEP-002
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="DEP-002", depends_on_id="DEP-001")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="DEP-003", depends_on_id="DEP-002")
            )
            await uow.commit()

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        # Execute allocation
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Verify allocation succeeded
        assert result is not None
        assert result.stories_allocated == 3

        # Reload stories to get dates
        await viewmodel.load_stories()
        stories = {s.id: s for s in viewmodel.stories}

        # Verify dependency order (DEP-001 start <= DEP-002 start <= DEP-003 start)
        # Also DEP-001 end <= DEP-002 start (dependency must complete first)
        assert stories["DEP-001"].end_date is not None
        assert stories["DEP-002"].start_date is not None
        assert stories["DEP-001"].end_date <= stories["DEP-002"].start_date

        assert stories["DEP-002"].end_date is not None
        assert stories["DEP-003"].start_date is not None
        assert stories["DEP-002"].end_date <= stories["DEP-003"].start_date


class TestUC002ExcluirFeriados:
    """Tests for holiday exclusion (FR-034)."""

    @pytest.mark.asyncio
    async def test_alocar_exclui_finais_de_semana(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that allocation excludes weekends.

        FR-034: Weekends should not be counted as working days.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev Weekend")
            await uow.developers.add(dev)
            await uow.commit()

        # Create story with 5 SP
        dto = CreateStoryInputDTO(
            component="WKD",
            name="Historia Weekend",
            story_points=5,
        )
        await viewmodel.create_story(dto)

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 2))
            )
            await uow.commit()

        # Start on Friday (2026-01-02 is a Friday)
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 2),  # Friday
            max_idle_days=5,
        )

        assert result is not None

        # Reload and check dates
        await viewmodel.load_stories()
        story = viewmodel.stories[0]

        # With velocity 1.0 and 5 SP, duration should be 5 working days
        # Starting Friday: Fri, Mon, Tue, Wed, Thu (skipping Sat/Sun)
        assert story.start_date == date(2026, 1, 2)  # Friday
        # Should end on Thursday (5 working days)
        assert story.end_date is not None
        # End date should not be on weekend
        assert story.end_date.weekday() < 5  # 0-4 = Mon-Fri


class TestUC002BalancearCarga:
    """Tests for load balancing (FR-035)."""

    @pytest.mark.asyncio
    async def test_alocar_balanceia_carga_entre_devs(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that allocation balances load across developers.

        FR-035: Stories should be distributed to balance developer workload.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create 3 developers
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 4):
                dev = Developer(name=f"Dev Balance {i}")
                await uow.developers.add(dev)
            await uow.commit()

        # Create 9 stories (should be ~3 per dev)
        for i in range(1, 10):
            dto = CreateStoryInputDTO(
                component="BAL",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        # Execute allocation
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 9

        # Reload and check distribution
        await viewmodel.load_stories()
        stories = viewmodel.stories

        # Count stories per developer
        dev_counts = {}
        for story in stories:
            dev_id = story.developer_id
            dev_counts[dev_id] = dev_counts.get(dev_id, 0) + 1

        # Should be balanced (3 stories each)
        assert len(dev_counts) == 3
        for count in dev_counts.values():
            assert count == 3

    @pytest.mark.asyncio
    async def test_alocar_sem_desenvolvedor_gera_warning(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that allocation without developers generates warning.

        FR-035: Should warn if no developers available.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create story without developers
        dto = CreateStoryInputDTO(
            component="NODEV",
            name="Historia Sem Dev",
            story_points=5,
        )
        await viewmodel.create_story(dto)

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        # Execute allocation
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        # Should fail or allocate 0 stories (no developers)
        if result is not None:
            assert result.stories_allocated == 0
            # Should have warnings
            assert len(allocation_vm.last_warnings) > 0


class TestUC002AllocationMetrics:
    """Tests for allocation metrics."""

    @pytest.mark.asyncio
    async def test_metricas_de_alocacao(self, e2e_main_window, e2e_app, qasync_loop):
        """Test that allocation returns proper metrics."""
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev Metrics")
            await uow.developers.add(dev)
            await uow.commit()

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="MET",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        # Execute allocation
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None
        assert result.stories_allocated == 3
        assert result.total_time_seconds > 0
        assert result.metrics is not None


class TestUC002FeatureWaves:
    """Tests for feature wave handling in allocation."""

    @pytest.mark.asyncio
    async def test_alocar_respeita_ordem_de_waves(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that allocation respects feature wave order.

        Stories in wave 1 should be allocated before wave 2.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer and features
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev Waves")
            await uow.developers.add(dev)

            feature1 = Feature(name="Feature Wave 1", wave=1)
            feature2 = Feature(name="Feature Wave 2", wave=2)
            await uow.features.add(feature1)
            await uow.features.add(feature2)
            await uow.commit()

        # Create stories in different waves
        dto1 = CreateStoryInputDTO(
            component="WONE",
            name="Historia Wave 1",
            story_points=5,
            feature_id=1,
        )
        dto2 = CreateStoryInputDTO(
            component="WTWO",
            name="Historia Wave 2",
            story_points=5,
            feature_id=2,
        )
        await viewmodel.create_story(dto1)
        await viewmodel.create_story(dto2)

        # Calculate schedule (required for allocation eligibility)
        async with e2e_app.create_unit_of_work() as uow:
            calc_schedule = e2e_app.create_calculate_schedule_use_case(uow)
            await calc_schedule.execute(
                CalculateScheduleInputDTO(velocity=1.0, start_date=date(2026, 1, 5))
            )
            await uow.commit()

        # Execute allocation
        result = await allocation_vm.execute(
            velocity=1.0,
            start_date=date(2026, 1, 5),
            max_idle_days=5,
        )

        assert result is not None

        # Reload and verify wave order
        await viewmodel.load_stories()
        stories = {s.id: s for s in viewmodel.stories}

        # Wave 1 should start before or equal to wave 2
        w1_story = stories["WONE-001"]
        w2_story = stories["WTWO-001"]

        assert w1_story.start_date is not None
        assert w2_story.start_date is not None
        assert w1_story.start_date <= w2_story.start_date
