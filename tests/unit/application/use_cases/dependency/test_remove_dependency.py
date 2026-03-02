"""Unit tests for RemoveDependencyUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.dependency import RemoveDependencyInputDTO
from backlog_manager.application.use_cases.dependency.remove_dependency import (
    RemoveDependencyUseCase,
)


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    repo.remove = AsyncMock()
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
    return RemoveDependencyUseCase(mock_uow)


class TestRemoveDependencySuccess:
    """Tests for successful removal."""

    async def test_remove_dependency_success(self, use_case, mock_dependency_repo):
        """Should successfully remove existing dependency."""
        mock_dependency_repo.exists.return_value = True

        input_dto = RemoveDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        result = await use_case.execute(input_dto)

        assert result.success is True
        mock_dependency_repo.remove.assert_called_once_with("AUTH-002", "AUTH-001")

    async def test_remove_calls_exists_before_remove(
        self, use_case, mock_dependency_repo
    ):
        """Should check existence before removing."""
        input_dto = RemoveDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        await use_case.execute(input_dto)

        mock_dependency_repo.exists.assert_called_once_with("AUTH-002", "AUTH-001")


class TestRemoveDependencyNotFound:
    """Tests for not found errors."""

    async def test_remove_dependency_not_found(self, use_case, mock_dependency_repo):
        """Should raise ValueError when dependency doesn't exist."""
        mock_dependency_repo.exists.return_value = False

        input_dto = RemoveDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        with pytest.raises(ValueError, match="nao encontrada"):
            await use_case.execute(input_dto)

        mock_dependency_repo.remove.assert_not_called()


class TestRemovePreservesOtherDependencies:
    """Tests for preserving other dependencies."""

    async def test_remove_preserves_other_dependencies(
        self, use_case, mock_dependency_repo
    ):
        """Should only remove specified dependency."""
        mock_dependency_repo.exists.return_value = True

        input_dto = RemoveDependencyInputDTO(
            story_id="AUTH-002",
            depends_on_id="AUTH-001",
        )

        await use_case.execute(input_dto)

        # Only the specified dependency should be removed
        mock_dependency_repo.remove.assert_called_once_with("AUTH-002", "AUTH-001")
        # Other dependencies should not be affected (verified by single call)
        assert mock_dependency_repo.remove.call_count == 1
