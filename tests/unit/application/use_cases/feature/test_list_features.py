"""Unit tests for ListFeaturesUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.use_cases.feature import ListFeaturesUseCase
from backlog_manager.domain.entities import Feature


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
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
    return ListFeaturesUseCase(mock_uow)


class TestListFeaturesUseCase:
    """Tests for ListFeaturesUseCase."""

    async def test_returns_empty_list_when_no_features(
        self, use_case, mock_feature_repo
    ):
        """Should return empty list when no features exist."""
        mock_feature_repo.get_all.return_value = []

        result = await use_case.execute()

        assert result.features == []

    async def test_returns_all_features(self, use_case, mock_feature_repo):
        """Should return all features from repository."""
        features = [
            Feature(id=1, name="Auth", wave=1),
            Feature(id=2, name="Dashboard", wave=2),
        ]
        mock_feature_repo.get_all.return_value = features

        result = await use_case.execute()

        assert len(result.features) == 2
        assert result.features[0].id == 1
        assert result.features[0].name == "Auth"
        assert result.features[0].wave == 1
        assert result.features[1].id == 2
        assert result.features[1].name == "Dashboard"
        assert result.features[1].wave == 2

    async def test_calls_repository_get_all(self, use_case, mock_feature_repo):
        """Should call repository get_all."""
        await use_case.execute()

        mock_feature_repo.get_all.assert_called_once()
