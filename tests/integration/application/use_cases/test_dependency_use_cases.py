"""Integration tests for Dependency use cases."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.application.dto.dependency import (
    AddDependencyInputDTO,
    GetDependenciesInputDTO,
    GetDependentsInputDTO,
    RemoveDependencyInputDTO,
)
from backlog_manager.application.use_cases.dependency import (
    AddDependencyUseCase,
    GetDependenciesUseCase,
    GetDependentsUseCase,
    RemoveDependencyUseCase,
)
from backlog_manager.domain.entities import Feature, Story
from backlog_manager.domain.exceptions.dependency import CyclicDependencyException
from backlog_manager.domain.value_objects import StoryPoint
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestAddDependencyUseCaseIntegration:
    """Integration tests for AddDependencyUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow: SQLiteUnitOfWork) -> None:
        """Helper to create test stories."""
        for i in range(1, 5):
            await uow.stories.add(
                Story(
                    id=f"TEST-{i:03d}",
                    component="TEST",
                    name=f"Story {i}",
                    story_points=StoryPoint.SMALL,
                    priority=i,
                )
            )

    async def _create_features_with_waves(
        self, uow: SQLiteUnitOfWork
    ) -> tuple[int, int]:
        """Create features with different waves."""
        feature1_id = await uow.features.add(
            Feature(id=0, name="Wave 1 Feature", wave=1)
        )
        feature2_id = await uow.features.add(
            Feature(id=0, name="Wave 2 Feature", wave=2)
        )
        return feature1_id, feature2_id

    async def test_add_dependency_success(self, db_path: Path) -> None:
        """Integration test for successful dependency addition."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = AddDependencyUseCase(uow)
            result = await use_case.execute(
                AddDependencyInputDTO(
                    story_id="TEST-002",
                    depends_on_id="TEST-001",
                )
            )

        assert result.success is True
        assert result.story_id == "TEST-002"
        assert result.depends_on_id == "TEST-001"

        # Verify dependency persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("TEST-002")
            assert "TEST-001" in deps

    async def test_cycle_detection_direct(self, db_path: Path) -> None:
        """Integration test for direct cycle detection A->B, B->A."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)

        # Add TEST-001 -> TEST-002
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = AddDependencyUseCase(uow)
            await use_case.execute(
                AddDependencyInputDTO(
                    story_id="TEST-001",
                    depends_on_id="TEST-002",
                )
            )

        # Try to add TEST-002 -> TEST-001 (would create cycle)
        with pytest.raises(CyclicDependencyException) as exc_info:
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = AddDependencyUseCase(uow)
                await use_case.execute(
                    AddDependencyInputDTO(
                        story_id="TEST-002",
                        depends_on_id="TEST-001",
                    )
                )

        assert exc_info.value.path[0] == exc_info.value.path[-1]

    async def test_cycle_detection_indirect(self, db_path: Path) -> None:
        """Integration test for indirect cycle detection A->B->C->A."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)

        # Build chain: TEST-001 -> TEST-002 -> TEST-003
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = AddDependencyUseCase(uow)
            await use_case.execute(
                AddDependencyInputDTO(story_id="TEST-001", depends_on_id="TEST-002")
            )
            await use_case.execute(
                AddDependencyInputDTO(story_id="TEST-002", depends_on_id="TEST-003")
            )

        # Try to add TEST-003 -> TEST-001 (would create cycle)
        with pytest.raises(CyclicDependencyException):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = AddDependencyUseCase(uow)
                await use_case.execute(
                    AddDependencyInputDTO(
                        story_id="TEST-003",
                        depends_on_id="TEST-001",
                    )
                )

    async def test_wave_warning(self, db_path: Path) -> None:
        """Integration test for wave warning."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feature1_id, feature2_id = await self._create_features_with_waves(uow)

            # Create story in wave 1
            await uow.stories.add(
                Story(
                    id="WAVE-001",
                    component="WAVE",
                    name="Wave 1 Story",
                    story_points=StoryPoint.SMALL,
                    priority=1,
                    feature_id=feature1_id,
                )
            )
            # Create story in wave 2
            await uow.stories.add(
                Story(
                    id="WAVE-002",
                    component="WAVE",
                    name="Wave 2 Story",
                    story_points=StoryPoint.SMALL,
                    priority=2,
                    feature_id=feature2_id,
                )
            )

        # Add dependency from wave 1 to wave 2 (should generate warning)
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = AddDependencyUseCase(uow)
            result = await use_case.execute(
                AddDependencyInputDTO(
                    story_id="WAVE-001",
                    depends_on_id="WAVE-002",
                )
            )

        assert result.success is True
        assert result.warning is not None
        assert result.warning.story_wave == 1
        assert result.warning.depends_on_wave == 2


@pytest.mark.integration
@pytest.mark.asyncio
class TestRemoveDependencyUseCaseIntegration:
    """Integration tests for RemoveDependencyUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow: SQLiteUnitOfWork) -> None:
        """Helper to create test stories."""
        for i in range(1, 4):
            await uow.stories.add(
                Story(
                    id=f"TEST-{i:03d}",
                    component="TEST",
                    name=f"Story {i}",
                    story_points=StoryPoint.SMALL,
                    priority=i,
                )
            )

    async def test_remove_dependency_success(self, db_path: Path) -> None:
        """Integration test for successful dependency removal."""
        await init_database(db_path)

        # Setup: create stories and dependency
        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")

        # Remove dependency
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = RemoveDependencyUseCase(uow)
            result = await use_case.execute(
                RemoveDependencyInputDTO(
                    story_id="TEST-002",
                    depends_on_id="TEST-001",
                )
            )

        assert result.success is True

        # Verify removal
        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("TEST-002")
            assert "TEST-001" not in deps


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetDependenciesUseCaseIntegration:
    """Integration tests for GetDependenciesUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow: SQLiteUnitOfWork) -> None:
        """Helper to create test stories."""
        for i in range(1, 5):
            await uow.stories.add(
                Story(
                    id=f"TEST-{i:03d}",
                    component="TEST",
                    name=f"Story {i}",
                    story_points=StoryPoint.SMALL,
                    priority=i,
                )
            )

    async def test_get_dependencies_success(self, db_path: Path) -> None:
        """Integration test for getting dependencies."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-003", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-002")

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = GetDependenciesUseCase(uow)
            result = await use_case.execute(
                GetDependenciesInputDTO(story_id="TEST-003")
            )

        assert result.story_id == "TEST-003"
        assert len(result.dependencies) == 2
        assert "TEST-001" in result.dependencies
        assert "TEST-002" in result.dependencies


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetDependentsUseCaseIntegration:
    """Integration tests for GetDependentsUseCase."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow: SQLiteUnitOfWork) -> None:
        """Helper to create test stories."""
        for i in range(1, 5):
            await uow.stories.add(
                Story(
                    id=f"TEST-{i:03d}",
                    component="TEST",
                    name=f"Story {i}",
                    story_points=StoryPoint.SMALL,
                    priority=i,
                )
            )

    async def test_get_dependents_success(self, db_path: Path) -> None:
        """Integration test for getting dependents."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = GetDependentsUseCase(uow)
            result = await use_case.execute(GetDependentsInputDTO(story_id="TEST-001"))

        assert result.story_id == "TEST-001"
        assert len(result.dependents) == 2
        assert "TEST-002" in result.dependents
        assert "TEST-003" in result.dependents
