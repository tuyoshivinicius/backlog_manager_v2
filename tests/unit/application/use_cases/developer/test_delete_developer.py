"""Unit tests for DeleteDeveloperUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.use_cases.developer import DeleteDeveloperUseCase
from backlog_manager.domain.entities import Developer


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.count_by_developer = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def mock_uow(mock_developer_repo, mock_story_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).developers = PropertyMock(return_value=mock_developer_repo)
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return DeleteDeveloperUseCase(mock_uow)


class TestDeleteDeveloperUseCase:
    """Tests for DeleteDeveloperUseCase."""

    async def test_deletes_developer_and_returns_count(
        self, use_case, mock_developer_repo, mock_story_repo
    ):
        """Should delete developer and return stories unassigned count."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")
        mock_story_repo.count_by_developer.return_value = 5

        result = await use_case.execute(1)

        assert result.developer_id == 1
        assert result.stories_unassigned == 5
        mock_developer_repo.delete.assert_called_once_with(1)

    async def test_returns_zero_when_no_stories(
        self, use_case, mock_developer_repo, mock_story_repo
    ):
        """Should return 0 when developer has no stories."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")
        mock_story_repo.count_by_developer.return_value = 0

        result = await use_case.execute(1)

        assert result.stories_unassigned == 0

    async def test_raises_error_for_nonexistent_developer(
        self, use_case, mock_developer_repo
    ):
        """Should raise ValueError for nonexistent developer."""
        mock_developer_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Desenvolvedor nao encontrado: 999"):
            await use_case.execute(999)

        mock_developer_repo.delete.assert_not_called()

    async def test_calls_repository_delete(
        self, use_case, mock_developer_repo, mock_story_repo
    ):
        """Should call repository delete."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        await use_case.execute(1)

        mock_developer_repo.delete.assert_called_once_with(1)
