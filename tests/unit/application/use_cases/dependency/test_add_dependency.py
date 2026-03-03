"""Unit tests for AddDependencyUseCase."""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.dependency import AddDependencyInputDTO
from backlog_manager.application.use_cases.dependency import AddDependencyUseCase
from backlog_manager.domain.exceptions.dependency import CyclicDependencyException


@dataclass
class MockStory:
    """Mock story for testing."""

    id: str
    feature_id: int | None = None


@dataclass
class MockFeature:
    """Mock feature for testing."""

    id: int
    wave: int


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    repo.get_by_id = AsyncMock(return_value=MockStory(id="AUTH-001"))
    return repo


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=False)
    repo.get_all_dependencies = AsyncMock(return_value=[])
    repo.add = AsyncMock()
    return repo


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_dependency_repo, mock_feature_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return AddDependencyUseCase(mock_uow)


class TestAddDependencySuccess:
    """Tests for successful AddDependencyUseCase execution."""

    async def test_add_dependency_success(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should successfully add dependency."""
        mock_story_repo.exists.side_effect = [True, True]  # Both stories exist
        mock_story_repo.get_by_id.side_effect = [
            MockStory(id="AUTH-002"),
            MockStory(id="AUTH-001"),
        ]

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        assert result.story_id == "AUTH-002"
        assert result.depends_on_id == "AUTH-001"
        assert result.warning is None
        mock_dependency_repo.add.assert_called_once_with("AUTH-002", "AUTH-001")

    async def test_add_dependency_returns_output_dto(self, use_case, mock_story_repo):
        """Should return AddDependencyOutputDTO with all fields."""
        mock_story_repo.exists.return_value = True
        mock_story_repo.get_by_id.return_value = MockStory(id="AUTH-001")

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        result = await use_case.execute(input_dto)

        assert hasattr(result, "success")
        assert hasattr(result, "story_id")
        assert hasattr(result, "depends_on_id")
        assert hasattr(result, "warning")


class TestAddDependencyStoryNotFound:
    """Tests for story not found errors."""

    async def test_story_not_found_source(self, use_case, mock_story_repo):
        """Should raise ValueError when source story doesn't exist."""
        mock_story_repo.exists.side_effect = [False, True]  # First story doesn't exist

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-999",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(ValueError, match="Historia AUTH-999 nao encontrada"):
            await use_case.execute(input_dto)

    async def test_story_not_found_target(self, use_case, mock_story_repo):
        """Should raise ValueError when target story doesn't exist."""
        mock_story_repo.exists.side_effect = [True, False]  # Second story doesn't exist

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-999",
        )

        with pytest.raises(ValueError, match="Historia AUTH-999 nao encontrada"):
            await use_case.execute(input_dto)


class TestAddDependencySelfDependency:
    """Tests for self-dependency errors."""

    async def test_self_dependency_error(self, use_case):
        """Should raise ValueError for self-dependency."""
        input_dto = AddDependencyInputDTO(
            story_id="AUTH-001",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(ValueError, match="Historia nao pode depender de si mesma"):
            await use_case.execute(input_dto)


class TestAddDependencyDuplicate:
    """Tests for duplicate dependency errors."""

    async def test_duplicate_dependency_error(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should raise ValueError for duplicate dependency."""
        mock_story_repo.exists.return_value = True
        mock_dependency_repo.exists.return_value = True  # Already exists

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(ValueError, match="Dependencia.*ja existe"):
            await use_case.execute(input_dto)


class TestAddDependencyCycleDetection:
    """Tests for cycle detection in AddDependencyUseCase."""

    async def test_direct_cycle_raises_exception(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should raise CyclicDependencyException for direct cycle A->B, B->A."""
        mock_story_repo.exists.return_value = True
        mock_story_repo.get_by_id.return_value = MockStory(id="AUTH-001")
        # Existing dependency: AUTH-001 depends on AUTH-002
        mock_dependency_repo.get_all_dependencies.return_value = [
            ("AUTH-001", "AUTH-002")
        ]

        # Try to add AUTH-002 depends on AUTH-001 (would create cycle)
        input_dto = AddDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(CyclicDependencyException) as exc_info:
            await use_case.execute(input_dto)

        # Should contain cycle path
        assert exc_info.value.path is not None
        assert exc_info.value.path[0] == exc_info.value.path[-1]

    async def test_indirect_cycle_raises_exception(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should raise CyclicDependencyException for indirect cycle A->B->C->A."""
        mock_story_repo.exists.return_value = True
        mock_story_repo.get_by_id.return_value = MockStory(id="AUTH-001")
        # Existing: A->B->C
        mock_dependency_repo.get_all_dependencies.return_value = [
            ("AUTH-001", "AUTH-002"),  # A depends on B
            ("AUTH-002", "AUTH-003"),  # B depends on C
        ]

        # Try to add C depends on A (would create cycle)
        input_dto = AddDependencyInputDTO(
            story_id="AUTH-003",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(CyclicDependencyException) as exc_info:
            await use_case.execute(input_dto)

        assert exc_info.value.path is not None
        cycle_nodes = set(exc_info.value.path)
        assert "AUTH-001" in cycle_nodes or "AUTH-002" in cycle_nodes

    async def test_complex_cycle_multiple_paths(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should detect cycle even with multiple paths."""
        mock_story_repo.exists.return_value = True
        mock_story_repo.get_by_id.return_value = MockStory(id="AUTH-001")
        # Complex graph with multiple paths
        mock_dependency_repo.get_all_dependencies.return_value = [
            ("A", "B"),
            ("A", "C"),
            ("B", "D"),
            ("C", "D"),
            ("D", "E"),
        ]

        # Try to add E depends on A (would create cycle)
        input_dto = AddDependencyInputDTO(
            story_id="E",
            depends_on_id="A",
        )

        with pytest.raises(CyclicDependencyException):
            await use_case.execute(input_dto)


class TestAddDependencyWaveWarning:
    """Tests for wave validation warnings."""

    async def test_wave_warning_when_depends_on_higher_wave(
        self, use_case, mock_story_repo, mock_dependency_repo, mock_feature_repo
    ):
        """Should return warning when depending on higher wave."""
        mock_story_repo.exists.return_value = True

        # Story in wave 1, depends_on in wave 2
        mock_story_repo.get_by_id.side_effect = [
            MockStory(id="AUTH-001", feature_id=1),  # wave 1
            MockStory(id="FEAT-001", feature_id=2),  # wave 2
        ]
        mock_feature_repo.get_by_id.side_effect = [
            MockFeature(id=1, wave=1),
            MockFeature(id=2, wave=2),
        ]

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-001",
            depends_on_id="FEAT-001",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        assert result.warning is not None
        assert result.warning.story_wave == 1
        assert result.warning.depends_on_wave == 2
        assert "wave posterior" in result.warning.message

    async def test_no_warning_when_depends_on_lower_wave(
        self, use_case, mock_story_repo, mock_dependency_repo, mock_feature_repo
    ):
        """Should not return warning when depending on lower wave."""
        mock_story_repo.exists.return_value = True

        # Story in wave 2, depends_on in wave 1
        mock_story_repo.get_by_id.side_effect = [
            MockStory(id="FEAT-001", feature_id=2),  # wave 2
            MockStory(id="AUTH-001", feature_id=1),  # wave 1
        ]
        mock_feature_repo.get_by_id.side_effect = [
            MockFeature(id=2, wave=2),
            MockFeature(id=1, wave=1),
        ]

        input_dto = AddDependencyInputDTO(
            story_id="FEAT-001",
            depends_on_id="AUTH-001",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        assert result.warning is None

    async def test_no_warning_when_same_wave(
        self, use_case, mock_story_repo, mock_dependency_repo, mock_feature_repo
    ):
        """Should not return warning when same wave."""
        mock_story_repo.exists.return_value = True

        # Both in wave 1
        mock_story_repo.get_by_id.side_effect = [
            MockStory(id="AUTH-001", feature_id=1),
            MockStory(id="AUTH-002", feature_id=1),
        ]
        mock_feature_repo.get_by_id.side_effect = [
            MockFeature(id=1, wave=1),
            MockFeature(id=1, wave=1),
        ]

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-001",
            depends_on_id="AUTH-002",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        assert result.warning is None

    async def test_wave_warning_with_story_without_feature(
        self, use_case, mock_story_repo, mock_dependency_repo, mock_feature_repo
    ):
        """Should return warning when story without feature depends on wave > 0."""
        mock_story_repo.exists.return_value = True

        # Story without feature (wave=0), depends_on in wave 1
        mock_story_repo.get_by_id.side_effect = [
            MockStory(id="AUTH-001", feature_id=None),  # wave 0 (no feature)
            MockStory(id="FEAT-001", feature_id=1),  # wave 1
        ]
        # Only one feature lookup happens (for depends_on story, feature_id=1)
        # First story has feature_id=None so no feature lookup is made for it
        mock_feature_repo.get_by_id.return_value = MockFeature(id=1, wave=1)

        input_dto = AddDependencyInputDTO(
            story_id="AUTH-001",
            depends_on_id="FEAT-001",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        assert result.warning is not None
        assert result.warning.story_wave == 0
        assert result.warning.depends_on_wave == 1
