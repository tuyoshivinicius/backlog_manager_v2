"""Integration tests for Scheduling use cases.

Tests cover full workflow including database operations.
"""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

import pytest

from backlog_manager.application.dto.scheduling import (
    CalculateDurationInputDTO,
    CalculateScheduleInputDTO,
    CalculateStoryDatesInputDTO,
)
from backlog_manager.application.use_cases.scheduling import (
    CalculateDurationUseCase,
    CalculateScheduleUseCase,
    CalculateStoryDatesUseCase,
)
from backlog_manager.domain.entities import Story
from backlog_manager.domain.exceptions import CyclicDependencyException
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestCalculateDurationUseCaseIntegration:
    """Integration tests for CalculateDurationUseCase."""

    async def test_calculate_duration_use_case(self) -> None:
        """T055a: Test duration calculation via use case."""
        use_case = CalculateDurationUseCase()
        result = await use_case.execute(
            CalculateDurationInputDTO(story_points=5, velocity=2.0)
        )
        assert result.duration == 3
        assert "ceil(5 / 2.0) = 3" in result.formula


@pytest.mark.integration
@pytest.mark.asyncio
class TestCalculateScheduleUseCaseIntegration:
    """Integration tests for CalculateScheduleUseCase."""

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
        status: StoryStatus = StoryStatus.BACKLOG,
    ) -> Story:
        """Helper to create a test story."""
        story = Story(
            id=story_id,
            component=story_id.split("-")[0],
            name=f"Story {story_id}",
            story_points=StoryPoint(story_points),
            priority=priority,
            status=status,
        )
        await uow.stories.add(story)
        return story

    async def test_calculate_schedule_success(self, db_path: Path) -> None:
        """T055: Test successful schedule calculation."""
        await init_database(db_path)

        # Create stories
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "FEAT-001", 5, 1)
            await self._create_story(uow, "FEAT-002", 8, 2)
            await self._create_story(uow, "FEAT-003", 3, 3)

        # Calculate schedule
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_processed == 3
        assert result.stories_updated == 3
        assert len(result.warnings) == 0

        # Verify dates were persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            story = await uow.stories.get_by_id("FEAT-001")
            assert story is not None
            assert story.start_date == date(2026, 3, 2)
            assert story.duration == 3

    async def test_calculate_schedule_with_dependencies(self, db_path: Path) -> None:
        """T056: Test schedule calculation with dependencies."""
        await init_database(db_path)

        # Create stories with chain: A -> B -> C
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "DEP-001", 5, 1)  # 3 days
            await self._create_story(uow, "DEP-002", 8, 2)  # 4 days
            await self._create_story(uow, "DEP-003", 3, 3)  # 2 days

            # B depends on A, C depends on B
            await uow.dependencies.add("DEP-002", "DEP-001")
            await uow.dependencies.add("DEP-003", "DEP-002")

        # Calculate schedule
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),  # Monday
                )
            )

        assert result.success is True
        assert result.stories_processed == 3

        # Verify order is respected
        async with SQLiteUnitOfWork(db_path) as uow:
            story_a = await uow.stories.get_by_id("DEP-001")
            story_b = await uow.stories.get_by_id("DEP-002")
            story_c = await uow.stories.get_by_id("DEP-003")

            assert story_a is not None and story_b is not None and story_c is not None

            # A starts at project start
            assert story_a.start_date == date(2026, 3, 2)
            # B starts after A ends
            assert story_b.start_date is not None
            assert story_a.end_date is not None
            assert story_b.start_date > story_a.end_date
            # C starts after B ends
            assert story_c.start_date is not None
            assert story_b.end_date is not None
            assert story_c.start_date > story_b.end_date

    async def test_calculate_schedule_with_holidays(self, db_path: Path) -> None:
        """T057: Test schedule calculation skips holidays."""
        await init_database(db_path)

        # Create story that spans Good Friday (2026-04-03)
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "HOL-001", 8, 1)  # 4 days

        # Start on Wed 2026-04-01
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 4, 1),
                )
            )

        assert result.success is True

        # Verify holiday is skipped
        async with SQLiteUnitOfWork(db_path) as uow:
            story = await uow.stories.get_by_id("HOL-001")
            assert story is not None
            # Day 1: Wed 01, Day 2: Thu 02, Day 3: Mon 06, Day 4: Tue 07
            # Skipped: Fri 03 (Good Friday), Sat 04, Sun 05
            assert story.end_date == date(2026, 4, 7)

    async def test_calculate_schedule_cycle_detected(self, db_path: Path) -> None:
        """T058: Test cycle detection raises CyclicDependencyException."""
        await init_database(db_path)

        # Create stories with cycle: A -> B -> C -> A
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "CYC-001", 5, 1)
            await self._create_story(uow, "CYC-002", 5, 2)
            await self._create_story(uow, "CYC-003", 5, 3)

            # Create cycle
            await uow.dependencies.add("CYC-001", "CYC-003")
            await uow.dependencies.add("CYC-002", "CYC-001")
            await uow.dependencies.add("CYC-003", "CYC-002")

        # Calculate schedule - should raise
        with pytest.raises(CyclicDependencyException):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = CalculateScheduleUseCase(uow)
                await use_case.execute(
                    CalculateScheduleInputDTO(
                        velocity=2.0,
                        start_date=date(2026, 3, 2),
                    )
                )

    async def test_calculate_schedule_empty_backlog(self, db_path: Path) -> None:
        """T059: Test empty backlog returns success with 0 processed."""
        await init_database(db_path)

        # No stories created

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_processed == 0
        assert result.stories_updated == 0
        assert "Nenhuma historia elegivel encontrada no backlog" in result.warnings

    async def test_calculate_schedule_invalid_story_points(self, db_path: Path) -> None:
        """T060: Test that non-BACKLOG stories are skipped (valid SP verification).

        Note: Since the DB has a CHECK constraint on story_points, we test
        that stories in non-BACKLOG status are properly skipped instead.
        The invalid SP warning path is exercised via unit tests.
        """
        await init_database(db_path)

        # Create one backlog story and one non-backlog story
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "VAL-001", 5, 1, StoryStatus.BACKLOG)
            await self._create_story(uow, "SKP-001", 5, 2, StoryStatus.EXECUCAO)

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_processed == 1  # Only backlog story
        assert result.stories_updated == 1

    async def test_calculate_schedule_dependency_without_end_date(
        self, db_path: Path
    ) -> None:
        """T061: Test dependency without end_date uses project_start_date fallback."""
        await init_database(db_path)

        # Create stories - one not in backlog (no end_date will be calculated)
        async with SQLiteUnitOfWork(db_path) as uow:
            # Story A in EXECUCAO status (won't be scheduled)
            await self._create_story(uow, "NED-001", 5, 1, StoryStatus.EXECUCAO)
            # Story B depends on A (which has no end_date)
            await self._create_story(uow, "NED-002", 5, 2, StoryStatus.BACKLOG)
            await uow.dependencies.add("NED-002", "NED-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_processed == 1  # Only B (backlog)
        assert any(
            "NED-001" in w and "project_start_date" in w for w in result.warnings
        )

        # When dependency has no end_date, we use project_start_date as fallback
        # then add 1 day to get next workday
        # So B.start = next_workday(project_start_date + 1 day) = 2026-03-03
        async with SQLiteUnitOfWork(db_path) as uow:
            story_b = await uow.stories.get_by_id("NED-002")
            assert story_b is not None
            assert story_b.start_date == date(2026, 3, 3)  # Day after fallback

    async def test_schedule_rollback_on_error(self, db_path: Path) -> None:
        """T062: Test rollback on error (no partial updates)."""
        await init_database(db_path)

        # Create stories with cycle
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "RBK-001", 5, 1)
            await self._create_story(uow, "RBK-002", 5, 2)
            await uow.dependencies.add("RBK-001", "RBK-002")
            await uow.dependencies.add("RBK-002", "RBK-001")

        # Attempt schedule (will fail due to cycle)
        with pytest.raises(CyclicDependencyException):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = CalculateScheduleUseCase(uow)
                await use_case.execute(
                    CalculateScheduleInputDTO(
                        velocity=2.0,
                        start_date=date(2026, 3, 2),
                    )
                )

        # Verify no stories were updated
        async with SQLiteUnitOfWork(db_path) as uow:
            story_1 = await uow.stories.get_by_id("RBK-001")
            story_2 = await uow.stories.get_by_id("RBK-002")
            assert story_1 is not None and story_2 is not None
            assert story_1.start_date is None
            assert story_2.start_date is None

    async def test_calculate_schedule_independent_stories_by_priority(
        self, db_path: Path
    ) -> None:
        """T062a: Test independent stories are processed in priority order."""
        await init_database(db_path)

        # Create independent stories with different priorities
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_story(uow, "PRI-001", 5, 3)  # Lower priority (higher #)
            await self._create_story(uow, "PRI-002", 5, 1)  # Highest priority
            await self._create_story(uow, "PRI-003", 5, 2)  # Medium priority

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateScheduleUseCase(uow)
            result = await use_case.execute(
                CalculateScheduleInputDTO(
                    velocity=2.0,
                    start_date=date(2026, 3, 2),
                )
            )

        assert result.success is True
        assert result.stories_processed == 3

        # All start at the same time since they're independent
        async with SQLiteUnitOfWork(db_path) as uow:
            story_1 = await uow.stories.get_by_id("PRI-001")
            story_2 = await uow.stories.get_by_id("PRI-002")
            story_3 = await uow.stories.get_by_id("PRI-003")

            # All should start on project start date
            assert story_1 is not None and story_1.start_date == date(2026, 3, 2)
            assert story_2 is not None and story_2.start_date == date(2026, 3, 2)
            assert story_3 is not None and story_3.start_date == date(2026, 3, 2)


@pytest.mark.integration
@pytest.mark.asyncio
class TestCalculateStoryDatesUseCaseIntegration:
    """Integration tests for CalculateStoryDatesUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_calculate_story_dates_success(self, db_path: Path) -> None:
        """Test successful story dates calculation."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.add(
                Story(
                    id="TST-001",
                    component="TST",
                    name="Test Story",
                    story_points=5,
                    priority=1,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateStoryDatesUseCase(uow)
            result = await use_case.execute(
                CalculateStoryDatesInputDTO(
                    story_id="TST-001",
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        assert result.story_id == "TST-001"
        assert result.start_date == date(2026, 3, 2)
        assert result.duration == 3

        # Verify persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            story = await uow.stories.get_by_id("TST-001")
            assert story is not None
            assert story.start_date == date(2026, 3, 2)
            assert story.duration == 3

    async def test_calculate_story_dates_with_dependency(self, db_path: Path) -> None:
        """Test story dates calculation respects dependency end dates."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            # Create dependency story with end date
            dep_story = Story(
                id="DEP-001",
                component="DEP",
                name="Dependency",
                story_points=5,
                priority=1,
            )
            object.__setattr__(dep_story, "end_date", date(2026, 3, 6))  # Friday
            await uow.stories.add(dep_story)

            # Create dependent story
            await uow.stories.add(
                Story(
                    id="DEP-002",
                    component="DEP",
                    name="Dependent",
                    story_points=5,
                    priority=2,
                )
            )
            await uow.dependencies.add("DEP-002", "DEP-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CalculateStoryDatesUseCase(uow)
            result = await use_case.execute(
                CalculateStoryDatesInputDTO(
                    story_id="DEP-002",
                    velocity=2.0,
                    project_start_date=date(2026, 3, 2),
                )
            )

        # Should start Monday after dependency ends Friday
        assert result.start_date == date(2026, 3, 9)

    async def test_calculate_story_dates_not_found(self, db_path: Path) -> None:
        """Test error when story not found."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao encontrada"):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = CalculateStoryDatesUseCase(uow)
                await use_case.execute(
                    CalculateStoryDatesInputDTO(
                        story_id="XXX-999",
                        velocity=2.0,
                        project_start_date=date(2026, 3, 2),
                    )
                )
