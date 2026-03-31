"""Integration tests for Allocation use cases.

Tests cover full workflow including database operations.
Scenario tests: CT-001, CT-003, CT-005
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pytest
from backlog_manager.application.dto.allocation import ExecuteAllocationInputDTO
from backlog_manager.application.use_cases.allocation import ExecuteAllocationUseCase
from backlog_manager.domain.entities import Developer, Feature, Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestExecuteAllocationUseCaseIntegration:
    """Integration tests for ExecuteAllocationUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_story(
        self,
        uow: SQLiteUnitOfWork,
        story_id: str,
        story_points: int,
        priority: int,
        feature_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        duration: int | None = None,
        developer_id: int | None = None,
    ) -> Story:
        """Helper to create a test story."""
        story = Story(
            id=story_id,
            component=story_id.split("-")[0],
            name=f"Story {story_id}",
            story_points=StoryPoint(story_points),
            priority=priority,
            status=StoryStatus.BACKLOG,
            feature_id=feature_id,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            developer_id=developer_id,
        )
        await uow.stories.add(story)
        return story

    async def _create_developer(self, uow: SQLiteUnitOfWork, name: str) -> Developer:
        """Helper to create a test developer."""
        developer = Developer(name=name)
        dev_id = await uow.developers.add(developer)
        return Developer(name=name, id=dev_id)

    async def _create_feature(
        self, uow: SQLiteUnitOfWork, name: str, wave: int
    ) -> Feature:
        """Helper to create a test feature."""
        feature = Feature(name=name, wave=wave)
        feature_id = await uow.features.add(feature)
        return Feature(name=name, wave=wave, id=feature_id)

    async def test_ct001_allocation_simple(self, db_path: Path) -> None:
        """CT-001: Simple allocation - 3 stories, 2 devs, no dependencies.

        Cenario:
        - 3 historias sequenciais sem dependencia
        - 2 desenvolvedores disponiveis
        - Resultado esperado: alocacao balanceada
        """
        await init_database(db_path)

        # Setup: create developers and stories with dates
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")
            await self._create_developer(uow, "Bob")

            # Stories with sequential dates (non-overlapping)
            await self._create_story(
                uow,
                "FEAT-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )
            await self._create_story(
                uow,
                "FEAT-002",
                5,
                2,
                start_date=date(2026, 3, 5),
                end_date=date(2026, 3, 9),
                duration=3,
            )
            await self._create_story(
                uow,
                "FEAT-003",
                5,
                3,
                start_date=date(2026, 3, 10),
                end_date=date(2026, 3, 12),
                duration=3,
            )

        # Execute allocation
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                    random_seed=42,
                )
            )

        # Verify
        assert result.success is True
        assert result.stories_allocated == 3
        assert result.metrics.waves_processed >= 1
        assert result.metrics.deadlocks_detected == 0

        # Verify persistence
        async with SQLiteUnitOfWork(db_path) as uow:
            all_stories = await uow.stories.get_all()
            allocated = [s for s in all_stories if s.developer_id is not None]
            assert len(allocated) == 3

            # Check load balancing - both devs should have stories
            dev_ids = {s.developer_id for s in allocated}
            assert len(dev_ids) == 2  # Both devs have stories

    async def test_ct003_allocation_with_dependencies(self, db_path: Path) -> None:
        """CT-003: Allocation with dependencies - B depends on A.

        Cenario:
        - 3 historias onde B depende de A
        - 2 desenvolvedores
        - Resultado esperado: A alocada antes de B
        """
        await init_database(db_path)

        # Setup
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")
            await self._create_developer(uow, "Bob")

            # A has early dates
            await self._create_story(
                uow,
                "AUTH-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )
            # B depends on A, starts after A ends
            await self._create_story(
                uow,
                "AUTH-002",
                5,
                2,
                start_date=date(2026, 3, 5),
                end_date=date(2026, 3, 9),
                duration=3,
            )
            # C independent
            await self._create_story(
                uow,
                "AUTH-003",
                5,
                3,
                start_date=date(2026, 3, 10),
                end_date=date(2026, 3, 12),
                duration=3,
            )

            # Create dependency: AUTH-002 depends on AUTH-001
            await uow.dependencies.add("AUTH-002", "AUTH-001")

        # Execute allocation
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                    random_seed=42,
                )
            )

        # Verify
        assert result.success is True
        assert result.stories_allocated == 3

        # Verify dependency relationship preserved
        async with SQLiteUnitOfWork(db_path) as uow:
            story_a = await uow.stories.get_by_id("AUTH-001")
            story_b = await uow.stories.get_by_id("AUTH-002")

            assert story_a is not None
            assert story_b is not None
            assert story_a.developer_id is not None
            assert story_b.developer_id is not None

            # B's start should be >= A's end (dependency respected)
            if story_a.end_date and story_b.start_date:
                assert story_b.start_date >= story_a.end_date

    async def test_ct005_allocation_with_waves(self, db_path: Path) -> None:
        """CT-005: Allocation with waves - 2 features, 3 stories each.

        Cenario:
        - Feature 1 (wave 1): 2 historias
        - Feature 2 (wave 2): 2 historias
        - 2 desenvolvedores
        - Resultado esperado: wave 1 processada antes de wave 2
        """
        await init_database(db_path)

        # Setup
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")
            await self._create_developer(uow, "Bob")

            feature1 = await self._create_feature(uow, "Feature 1", wave=1)
            feature2 = await self._create_feature(uow, "Feature 2", wave=2)

            # Wave 1 stories (earlier dates) - use valid story ID format
            await self._create_story(
                uow,
                "WAVE-001",
                5,
                1,
                feature_id=feature1.id,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )
            await self._create_story(
                uow,
                "WAVE-002",
                5,
                2,
                feature_id=feature1.id,
                start_date=date(2026, 3, 5),
                end_date=date(2026, 3, 9),
                duration=3,
            )

            # Wave 2 stories (later dates) - use valid story ID format
            await self._create_story(
                uow,
                "WAVE-003",
                5,
                3,
                feature_id=feature2.id,
                start_date=date(2026, 3, 10),
                end_date=date(2026, 3, 12),
                duration=3,
            )
            await self._create_story(
                uow,
                "WAVE-004",
                5,
                4,
                feature_id=feature2.id,
                start_date=date(2026, 3, 13),
                end_date=date(2026, 3, 17),
                duration=3,
            )

        # Execute allocation
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                    random_seed=42,
                )
            )

        # Verify
        assert result.success is True
        assert result.stories_allocated == 4
        assert result.metrics.waves_processed == 2

        # Verify wave order: wave 1 iterations should be tracked before wave 2
        assert 1 in result.metrics.iterations_per_wave
        assert 2 in result.metrics.iterations_per_wave

    async def test_allocation_no_stories(self, db_path: Path) -> None:
        """T113: Empty backlog returns zero allocations."""
        await init_database(db_path)

        # Setup: only developers, no stories
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")

        # Execute
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_allocated == 0

    async def test_allocation_no_developers(self, db_path: Path) -> None:
        """T114: No developers produces deadlock warning."""
        await init_database(db_path)

        # Setup: only stories, no developers
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(
                uow,
                "FEAT-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )

        # Execute
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True  # Completes but with deadlock
        assert result.stories_allocated == 0
        assert result.metrics.deadlocks_detected >= 1

    async def test_allocation_dependency_owner_criteria(self, db_path: Path) -> None:
        """T115: DEPENDENCY_OWNER criteria allocates to dependency owner."""
        await init_database(db_path)

        # Setup
        async with SQLiteUnitOfWork(db_path) as uow:
            alice = await self._create_developer(uow, "Alice")
            await self._create_developer(uow, "Bob")

            # Story A already allocated to Alice
            await self._create_story(
                uow,
                "AUTH-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
                developer_id=alice.id,
            )
            # Story B depends on A, not allocated
            await self._create_story(
                uow,
                "AUTH-002",
                5,
                2,
                start_date=date(2026, 3, 5),
                end_date=date(2026, 3, 9),
                duration=3,
            )

            await uow.dependencies.add("AUTH-002", "AUTH-001")

        # Execute with DEPENDENCY_OWNER criteria
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                    allocation_criteria="DEPENDENCY_OWNER",
                    random_seed=42,
                )
            )

        # Verify
        assert result.success is True
        assert (
            result.stories_allocated == 1
        )  # Only B was eligible (A already allocated)

        # Check that B was allocated to Alice (owner of A)
        async with SQLiteUnitOfWork(db_path) as uow:
            story_b = await uow.stories.get_by_id("AUTH-002")
            assert story_b is not None
            # B should be allocated to Alice (owner of dependency A)
            assert story_b.developer_id == alice.id

    async def test_allocation_metrics_populated(self, db_path: Path) -> None:
        """T116: All metrics fields are populated correctly."""
        await init_database(db_path)

        # Setup
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")

            await self._create_story(
                uow,
                "FEAT-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )

        # Execute
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        # Verify all metrics fields exist and are valid
        metrics = result.metrics
        assert metrics.total_time_seconds >= 0
        assert metrics.stories_processed >= 0
        assert metrics.stories_allocated >= 0
        assert metrics.waves_processed >= 0
        assert metrics.total_iterations >= 0
        assert isinstance(metrics.iterations_per_wave, dict)
        assert metrics.allocations_by_dependency_owner >= 0
        assert metrics.allocations_by_load_balancing >= 0
        assert metrics.deadlocks_detected >= 0
        assert metrics.date_adjustments >= 0
        assert metrics.validation_reallocations >= 0
        assert metrics.validation_dependency_fixes >= 0
        assert metrics.validation_conflict_fixes >= 0
        assert metrics.max_idle_violations_detected >= 0
        assert metrics.max_idle_violations_fixed >= 0
        assert metrics.failed_reallocations >= 0

    async def test_allocation_persistence(self, db_path: Path) -> None:
        """T117: Allocated stories are persisted to database."""
        await init_database(db_path)

        # Setup
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_developer(uow, "Alice")

            await self._create_story(
                uow,
                "FEAT-001",
                5,
                1,
                start_date=date(2026, 3, 2),
                end_date=date(2026, 3, 4),
                duration=3,
            )

        # Execute
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = ExecuteAllocationUseCase(uow)
            result = await use_case.execute(
                ExecuteAllocationInputDTO(
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        assert result.stories_allocated == 1

        # Verify persistence in new session
        async with SQLiteUnitOfWork(db_path) as uow:
            story = await uow.stories.get_by_id("FEAT-001")
            assert story is not None
            assert story.developer_id is not None
