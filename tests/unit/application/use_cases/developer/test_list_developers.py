"""Unit tests for ListDevelopersUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.use_cases.developer import ListDevelopersUseCase
from backlog_manager.domain.entities import Developer


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_uow(mock_developer_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).developers = PropertyMock(return_value=mock_developer_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return ListDevelopersUseCase(mock_uow)


class TestListDevelopersUseCase:
    """Tests for ListDevelopersUseCase."""

    async def test_returns_empty_list_when_no_developers(
        self, use_case, mock_developer_repo
    ):
        """Should return empty list when no developers exist."""
        mock_developer_repo.get_all.return_value = []

        result = await use_case.execute()

        assert result.developers == []

    async def test_returns_all_developers(self, use_case, mock_developer_repo):
        """Should return all developers from repository."""
        developers = [
            Developer(id=1, name="Ana"),
            Developer(id=2, name="Bruno"),
        ]
        mock_developer_repo.get_all.return_value = developers

        result = await use_case.execute()

        assert len(result.developers) == 2
        assert result.developers[0].id == 1
        assert result.developers[0].name == "Ana"
        assert result.developers[1].id == 2
        assert result.developers[1].name == "Bruno"

    async def test_calls_repository_get_all(self, use_case, mock_developer_repo):
        """Should call repository get_all."""
        await use_case.execute()

        mock_developer_repo.get_all.assert_called_once()
