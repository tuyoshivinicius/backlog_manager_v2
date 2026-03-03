"""Unit tests for DeleteFeatureUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.use_cases.feature import DeleteFeatureUseCase
from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import FeatureHasStoriesException


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_uow(mock_feature_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return DeleteFeatureUseCase(mock_uow)


class TestDeleteFeatureUseCase:
    """Tests for DeleteFeatureUseCase."""

    async def test_deletes_feature(self, use_case, mock_feature_repo):
        """Should delete feature when no stories."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        await use_case.execute(1)

        mock_feature_repo.delete.assert_called_once_with(1)

    async def test_raises_error_for_nonexistent_feature(
        self, use_case, mock_feature_repo
    ):
        """Should raise ValueError for nonexistent feature."""
        mock_feature_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Feature nao encontrada: 999"):
            await use_case.execute(999)

        mock_feature_repo.delete.assert_not_called()

    async def test_raises_error_when_feature_has_stories(
        self, use_case, mock_feature_repo
    ):
        """Should raise FeatureHasStoriesException when feature has stories."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.delete.side_effect = FeatureHasStoriesException(
            feature_id=1,
            feature_name="Auth",
            story_count=3,
        )

        with pytest.raises(FeatureHasStoriesException) as exc_info:
            await use_case.execute(1)

        assert exc_info.value.feature_id == 1
        assert exc_info.value.story_count == 3

    async def test_returns_none(self, use_case, mock_feature_repo):
        """Should return None on success."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        result = await use_case.execute(1)

        assert result is None
