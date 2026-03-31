"""Unit tests for GetDependentsUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.dependency import GetDependentsInputDTO
from backlog_manager.application.use_cases.dependency import GetDependentsUseCase


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.get_dependents = AsyncMock(return_value=[])
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
    return GetDependentsUseCase(mock_uow)


class TestGetDependentsSuccess:
    """Tests for successful GetDependentsUseCase execution."""

    async def test_get_dependents_success(self, use_case, mock_dependency_repo):
        """Should return dependents for story."""
        mock_dependency_repo.get_dependents.return_value = ["AUTH-002", "AUTH-003"]

        input_dto = GetDependentsInputDTO(story_id="AUTH-001")

        result = await use_case.execute(input_dto)

        assert result.story_id == "AUTH-001"
        assert result.dependents == ["AUTH-002", "AUTH-003"]
        mock_dependency_repo.get_dependents.assert_called_once_with("AUTH-001")

    async def test_get_dependents_returns_output_dto(self, use_case):
        """Should return GetDependentsOutputDTO with all fields."""
        input_dto = GetDependentsInputDTO(story_id="AUTH-001")

        result = await use_case.execute(input_dto)

        assert hasattr(result, "story_id")
        assert hasattr(result, "dependents")


class TestGetDependentsEmpty:
    """Tests for empty dependents."""

    async def test_get_dependents_empty(self, use_case, mock_dependency_repo):
        """Should return empty list when no dependents."""
        mock_dependency_repo.get_dependents.return_value = []

        input_dto = GetDependentsInputDTO(story_id="AUTH-001")

        result = await use_case.execute(input_dto)

        assert result.story_id == "AUTH-001"
        assert result.dependents == []
