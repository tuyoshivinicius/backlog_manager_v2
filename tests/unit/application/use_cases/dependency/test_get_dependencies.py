"""Unit tests for GetDependenciesUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.dependency import GetDependenciesInputDTO
from backlog_manager.application.use_cases.dependency import GetDependenciesUseCase


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.get_dependencies = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_uow(mock_dependency_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return GetDependenciesUseCase(mock_uow)


class TestGetDependenciesSuccess:
    """Tests for successful GetDependenciesUseCase execution."""

    async def test_get_dependencies_success(self, use_case, mock_dependency_repo):
        """Should return dependencies for story."""
        mock_dependency_repo.get_dependencies.return_value = ["AUTH-001", "AUTH-002"]

        input_dto = GetDependenciesInputDTO(story_id="AUTH-003")

        result = await use_case.execute(input_dto)

        assert result.story_id == "AUTH-003"
        assert result.dependencies == ["AUTH-001", "AUTH-002"]
        mock_dependency_repo.get_dependencies.assert_called_once_with("AUTH-003")

    async def test_get_dependencies_returns_output_dto(self, use_case):
        """Should return GetDependenciesOutputDTO with all fields."""
        input_dto = GetDependenciesInputDTO(story_id="AUTH-001")

        result = await use_case.execute(input_dto)

        assert hasattr(result, "story_id")
        assert hasattr(result, "dependencies")


class TestGetDependenciesEmpty:
    """Tests for empty dependencies."""

    async def test_get_dependencies_empty(self, use_case, mock_dependency_repo):
        """Should return empty list when no dependencies."""
        mock_dependency_repo.get_dependencies.return_value = []

        input_dto = GetDependenciesInputDTO(story_id="AUTH-001")

        result = await use_case.execute(input_dto)

        assert result.story_id == "AUTH-001"
        assert result.dependencies == []
