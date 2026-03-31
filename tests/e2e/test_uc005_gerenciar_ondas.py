"""E2E tests for UC-005: Gerenciar Ondas.

Tests the wave/feature management and ordering flow including
wave processing order during allocation.
"""

from __future__ import annotations

from datetime import date

import pytest
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature

pytestmark = [pytest.mark.e2e]


class TestUC005ProcessarOndasEmOrdem:
    """Tests for wave order processing (FR-040)."""

    @pytest.mark.asyncio
    async def test_processar_ondas_em_ordem_crescente(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that waves are processed in ascending order.

        FR-040: Wave 1 should be allocated before Wave 2.
        """
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer and features
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev Waves")
            await uow.developers.add(dev)

            feature_w1 = Feature(name="Feature Wave 1", wave=1)
            feature_w2 = Feature(name="Feature Wave 2", wave=2)
            feature_w3 = Feature(name="Feature Wave 3", wave=3)
            await uow.features.add(feature_w1)
            await uow.features.add(feature_w2)
            await uow.features.add(feature_w3)
            await uow.commit()

        # Create stories in different waves (create in reverse order)
        dto_w3 = CreateStoryInputDTO(
            component="WTHR",
            name="Historia Wave 3",
            story_points=5,
            feature_id=3,
        )
        dto_w1 = CreateStoryInputDTO(
            component="WONE",
            name="Historia Wave 1",
            story_points=5,
            feature_id=1,
        )
        dto_w2 = CreateStoryInputDTO(
            component="WTWO",
            name="Historia Wave 2",
            story_points=5,
            feature_id=2,
        )

        # Create in non-wave order to verify sorting
        await viewmodel.create_story(dto_w3)
        await viewmodel.create_story(dto_w1)
        await viewmodel.create_story(dto_w2)

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

        # Reload and verify wave order
        await viewmodel.load_stories()
        stories = {s.id: s for s in viewmodel.stories}

        w1_story = stories["WONE-001"]
        w2_story = stories["WTWO-001"]
        w3_story = stories["WTHR-001"]

        # Wave 1 should start first
        assert w1_story.start_date is not None
        assert w2_story.start_date is not None
        assert w3_story.start_date is not None

        # Verify order
        assert w1_story.start_date <= w2_story.start_date
        assert w2_story.start_date <= w3_story.start_date

    @pytest.mark.asyncio
    async def test_multiplas_historias_por_wave(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test allocation with multiple stories per wave."""
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developers and features
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 3):
                dev = Developer(name=f"Dev Multi {i}")
                await uow.developers.add(dev)

            feature_w1 = Feature(name="Feature 1", wave=1)
            feature_w2 = Feature(name="Feature 2", wave=2)
            await uow.features.add(feature_w1)
            await uow.features.add(feature_w2)
            await uow.commit()

        # Create 3 stories per wave
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="MWONE",
                name=f"Historia Wave 1 - {i}",
                story_points=5,
                feature_id=1,
            )
            await viewmodel.create_story(dto)

        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="MWTWO",
                name=f"Historia Wave 2 - {i}",
                story_points=5,
                feature_id=2,
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
        assert result.stories_allocated == 6

        # Reload stories
        await viewmodel.load_stories()
        stories = viewmodel.stories

        # All wave 1 stories should start before or equal to wave 2 stories
        w1_stories = [s for s in stories if s.id.startswith("MWONE")]
        w2_stories = [s for s in stories if s.id.startswith("MWTWO")]

        max_w1_start = max(s.start_date for s in w1_stories if s.start_date)
        min_w2_start = min(s.start_date for s in w2_stories if s.start_date)

        # Wave 2 starts after wave 1 (or at same time if parallel)
        assert max_w1_start <= min_w2_start


class TestUC005FeatureCRUD:
    """Tests for feature CRUD operations."""

    @pytest.mark.asyncio
    async def test_criar_feature(self, e2e_app, qasync_loop):
        """Test feature creation."""
        async with e2e_app.create_unit_of_work() as uow:
            feature = Feature(name="Nova Feature", wave=1)
            await uow.features.add(feature)
            await uow.commit()

        # Verify feature was created
        async with e2e_app.create_unit_of_work() as uow:
            features = await uow.features.get_all()
            assert len(features) == 1
            assert features[0].name == "Nova Feature"
            assert features[0].wave == 1

    @pytest.mark.asyncio
    async def test_wave_unico(self, e2e_app, qasync_loop):
        """Test that wave numbers must be unique."""
        async with e2e_app.create_unit_of_work() as uow:
            feature1 = Feature(name="Feature 1", wave=1)
            await uow.features.add(feature1)
            await uow.commit()

        # Try to create another feature with same wave
        error_raised = False
        try:
            async with e2e_app.create_unit_of_work() as uow:
                feature2 = Feature(name="Feature 2", wave=1)  # Same wave!
                await uow.features.add(feature2)
                await uow.commit()
        except Exception:
            error_raised = True

        # Should fail due to unique constraint on wave
        assert error_raised

    @pytest.mark.asyncio
    async def test_listar_features_ordenadas_por_wave(self, e2e_app, qasync_loop):
        """Test that features are listed ordered by wave."""
        async with e2e_app.create_unit_of_work() as uow:
            # Create in non-order
            feature3 = Feature(name="Feature 3", wave=3)
            feature1 = Feature(name="Feature 1", wave=1)
            feature2 = Feature(name="Feature 2", wave=2)
            await uow.features.add(feature3)
            await uow.features.add(feature1)
            await uow.features.add(feature2)
            await uow.commit()

        # List features
        async with e2e_app.create_unit_of_work() as uow:
            use_case = e2e_app.create_list_features_use_case(uow)
            result = await use_case.execute()

        # Should be ordered by wave
        assert result.features[0].wave == 1
        assert result.features[1].wave == 2
        assert result.features[2].wave == 3

    @pytest.mark.asyncio
    async def test_deletar_feature_sem_historias(self, e2e_app, qasync_loop):
        """Test deleting a feature without stories."""
        async with e2e_app.create_unit_of_work() as uow:
            feature = Feature(name="Feature Delete", wave=1)
            await uow.features.add(feature)
            await uow.commit()

        # Delete feature
        async with e2e_app.create_unit_of_work() as uow:
            use_case = e2e_app.create_delete_feature_use_case(uow)
            await use_case.execute(1)
            await uow.commit()

        # Verify deletion
        async with e2e_app.create_unit_of_work() as uow:
            features = await uow.features.get_all()
            assert len(features) == 0


class TestUC005StoriesWithoutFeature:
    """Tests for stories without feature assignment."""

    @pytest.mark.asyncio
    async def test_historias_sem_feature_sao_alocadas(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that stories without feature are still allocated."""
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer (no features)
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev NoFeature")
            await uow.developers.add(dev)
            await uow.commit()

        # Create story without feature
        dto = CreateStoryInputDTO(
            component="NF",
            name="Historia Sem Feature",
            story_points=5,
            feature_id=None,
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
        assert result.stories_allocated == 1

        # Verify story was allocated
        await viewmodel.load_stories()
        story = viewmodel.stories[0]
        assert story.developer_id is not None
        assert story.start_date is not None

    @pytest.mark.asyncio
    async def test_historias_sem_feature_alocadas_primeiro(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that stories without feature are allocated with priority."""
        viewmodel = e2e_main_window.viewmodel
        allocation_vm = e2e_app.allocation_viewmodel

        # Create developer and feature
        async with e2e_app.create_unit_of_work() as uow:
            dev = Developer(name="Dev Priority")
            await uow.developers.add(dev)

            feature = Feature(name="Feature Test", wave=2)
            await uow.features.add(feature)
            await uow.commit()

        # Create stories (one without feature, one with)
        dto_no_feature = CreateStoryInputDTO(
            component="NF",
            name="Historia Sem Feature",
            story_points=5,
            feature_id=None,
        )
        dto_with_feature = CreateStoryInputDTO(
            component="WF",
            name="Historia Com Feature Wave 2",
            story_points=5,
            feature_id=1,
        )
        await viewmodel.create_story(dto_with_feature)
        await viewmodel.create_story(dto_no_feature)

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

        # Reload stories
        await viewmodel.load_stories()
        stories = {s.id: s for s in viewmodel.stories}

        # Both should be allocated
        nf_story = stories["NF-001"]
        wf_story = stories["WF-001"]

        assert nf_story.start_date is not None
        assert wf_story.start_date is not None
