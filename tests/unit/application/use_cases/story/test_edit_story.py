"""Unit tests for EditStoryUseCase."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.story.edit_story_dto import EditStoryInputDTO
from backlog_manager.application.use_cases.story.edit_story import EditStoryUseCase
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.exceptions import IncompleteDependencyException
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@pytest.fixture
def mock_story():
    """Create a mock Story entity."""
    story = MagicMock(spec=Story)
    story.planning_id = 1
    story.id = "TEST-001"
    story.component = "TEST"
    story.name = "Test Story"
    story.story_points = StoryPoint(5)
    story.priority = 1
    story.status = StoryStatus.BACKLOG
    story.duration = 3
    story.start_date = None
    story.end_date = None
    story.developer_id = None
    story.feature_id = None
    return story


@pytest.fixture
def mock_story_repo(mock_story):
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=mock_story)
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.get_dependencies = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_feature_repo, mock_dependency_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    return uow


class TestEditStoryDeveloperId:
    """Tests for developer_id propagation in EditStoryUseCase."""

    @pytest.mark.asyncio
    async def test_edit_story_propagates_developer_id(
        self, mock_uow, mock_story
    ) -> None:
        """Verify execute() sets developer_id on entity when provided."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(
            story_id="TEST-001",
            name="Test Story",
            developer_id=42,
        )

        await use_case.execute(1, dto)

        assert mock_story.developer_id == 42

    @pytest.mark.asyncio
    async def test_edit_story_clears_developer_id(self, mock_uow, mock_story) -> None:
        """Verify execute() clears developer_id when None is provided (desatribuicao)."""
        mock_story.developer_id = 42  # Pre-assign
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(
            story_id="TEST-001",
            name="Test Story",
            developer_id=None,
        )

        await use_case.execute(1, dto)

        assert mock_story.developer_id is None


class TestEditStoryNotFound:
    """Tests for story not found error path."""

    @pytest.mark.asyncio
    async def test_raises_value_error_when_story_not_found(
        self, mock_uow, mock_story_repo
    ) -> None:
        """Verify ValueError is raised when story_id does not exist."""
        mock_story_repo.get_by_id = AsyncMock(return_value=None)
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="MISS-001")

        with pytest.raises(ValueError, match="Historia MISS-001 nao encontrada"):
            await use_case.execute(1, dto)


class TestEditStoryFeatureValidation:
    """Tests for feature_id validation."""

    @pytest.mark.asyncio
    async def test_raises_value_error_when_feature_not_exists(
        self, mock_uow, mock_feature_repo
    ) -> None:
        """Verify ValueError when feature_id references non-existent feature."""
        mock_feature_repo.exists = AsyncMock(return_value=False)
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", feature_id=999)

        with pytest.raises(ValueError, match="Feature com ID 999 nao encontrada"):
            await use_case.execute(1, dto)

    @pytest.mark.asyncio
    async def test_skips_feature_validation_when_feature_id_is_none(
        self, mock_uow, mock_feature_repo
    ) -> None:
        """Verify feature existence is not checked when feature_id is None."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001")

        await use_case.execute(1, dto)

        mock_feature_repo.exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_updates_feature_id_when_valid(
        self, mock_uow, mock_story, mock_feature_repo
    ) -> None:
        """Verify feature_id is set on entity when valid feature exists."""
        mock_feature_repo.exists = AsyncMock(return_value=True)
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", feature_id=5)

        await use_case.execute(1, dto)

        assert mock_story.feature_id == 5


class TestEditStoryPartialUpdate:
    """Tests for partial field updates (only provided fields are changed)."""

    @pytest.mark.asyncio
    async def test_updates_name_only(self, mock_uow, mock_story) -> None:
        """Verify only name is updated when only name is provided."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", name="New Name")

        await use_case.execute(1, dto)

        assert mock_story.name == "New Name"

    @pytest.mark.asyncio
    async def test_updates_story_points(self, mock_uow, mock_story) -> None:
        """Verify story_points is updated as StoryPoint value object."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", story_points=13)

        await use_case.execute(1, dto)

        assert mock_story.story_points == StoryPoint(13)

    @pytest.mark.asyncio
    async def test_updates_status(self, mock_uow, mock_story) -> None:
        """Verify status is updated as StoryStatus enum."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="EXECUCAO")

        await use_case.execute(1, dto)

        assert mock_story.status == StoryStatus.EXECUCAO

    @pytest.mark.asyncio
    async def test_updates_duration(self, mock_uow, mock_story) -> None:
        """Verify duration is updated when provided."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", duration=10)

        await use_case.execute(1, dto)

        assert mock_story.duration == 10

    @pytest.mark.asyncio
    async def test_updates_start_date(self, mock_uow, mock_story) -> None:
        """Verify start_date is updated when provided."""
        use_case = EditStoryUseCase(mock_uow)
        target_date = date(2026, 3, 15)
        dto = EditStoryInputDTO(story_id="TEST-001", start_date=target_date)

        await use_case.execute(1, dto)

        assert mock_story.start_date == target_date

    @pytest.mark.asyncio
    async def test_updates_end_date(self, mock_uow, mock_story) -> None:
        """Verify end_date is updated when provided."""
        use_case = EditStoryUseCase(mock_uow)
        target_date = date(2026, 4, 20)
        dto = EditStoryInputDTO(story_id="TEST-001", end_date=target_date)

        await use_case.execute(1, dto)

        assert mock_story.end_date == target_date

    @pytest.mark.asyncio
    async def test_no_fields_updated_when_none_provided(
        self, mock_uow, mock_story
    ) -> None:
        """Verify no fields change when only story_id is in the DTO."""
        original_name = mock_story.name
        original_points = mock_story.story_points
        original_status = mock_story.status
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001")

        await use_case.execute(1, dto)

        assert mock_story.name == original_name
        assert mock_story.story_points == original_points
        assert mock_story.status == original_status

    @pytest.mark.asyncio
    async def test_persists_updated_story(self, mock_uow, mock_story_repo) -> None:
        """Verify the updated story is persisted via repository."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", name="Updated")

        await use_case.execute(1, dto)

        mock_story_repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_story_output_dto(self, mock_uow, mock_story) -> None:
        """Verify execute returns a StoryOutputDTO from the entity."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", name="Updated")

        result = await use_case.execute(1, dto)

        assert result.id == mock_story.id


class TestEditStoryDependencyValidation:
    """Tests for dependency validation when transitioning to CONCLUIDO."""

    @pytest.mark.asyncio
    async def test_validates_dependencies_when_transitioning_to_concluido(
        self, mock_uow, mock_story, mock_dependency_repo
    ) -> None:
        """Verify dependency validation occurs on transition to CONCLUIDO."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(return_value=[])
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        await use_case.execute(1, dto)

        mock_dependency_repo.get_dependencies.assert_awaited_once_with(1, "TEST-001")

    @pytest.mark.asyncio
    async def test_skips_validation_when_already_concluido(
        self, mock_uow, mock_story, mock_dependency_repo
    ) -> None:
        """Verify no dependency check when story is already CONCLUIDO."""
        mock_story.status = StoryStatus.CONCLUIDO
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        await use_case.execute(1, dto)

        mock_dependency_repo.get_dependencies.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_validation_when_status_not_concluido(
        self, mock_uow, mock_story, mock_dependency_repo
    ) -> None:
        """Verify no dependency check when new status is not CONCLUIDO."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="EXECUCAO")

        await use_case.execute(1, dto)

        mock_dependency_repo.get_dependencies.assert_not_called()

    @pytest.mark.asyncio
    async def test_skips_validation_when_status_is_none(
        self, mock_uow, mock_story, mock_dependency_repo
    ) -> None:
        """Verify no dependency check when status is not being changed."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001")

        await use_case.execute(1, dto)

        mock_dependency_repo.get_dependencies.assert_not_called()

    @pytest.mark.asyncio
    async def test_allows_concluido_when_no_dependencies(
        self, mock_uow, mock_story, mock_dependency_repo
    ) -> None:
        """Verify transition to CONCLUIDO succeeds with no dependencies."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(return_value=[])
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        await use_case.execute(1, dto)

        assert mock_story.status == StoryStatus.CONCLUIDO

    @pytest.mark.asyncio
    async def test_allows_concluido_when_all_deps_complete(
        self, mock_uow, mock_story, mock_story_repo, mock_dependency_repo
    ) -> None:
        """Verify transition when all dependencies are CONCLUIDO."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(
            return_value=["DEP-001", "DEP-002"]
        )
        dep1 = MagicMock(spec=Story)
        dep1.id = "DEP-001"
        dep1.name = "Dep 1"
        dep1.status = StoryStatus.CONCLUIDO

        dep2 = MagicMock(spec=Story)
        dep2.id = "DEP-002"
        dep2.name = "Dep 2"
        dep2.status = StoryStatus.CONCLUIDO

        mock_story_repo.get_by_id = AsyncMock(
            side_effect=lambda pid, sid: {
                "TEST-001": mock_story,
                "DEP-001": dep1,
                "DEP-002": dep2,
            }[sid]
        )

        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        await use_case.execute(1, dto)

        assert mock_story.status == StoryStatus.CONCLUIDO

    @pytest.mark.asyncio
    async def test_raises_incomplete_dependency_exception(
        self, mock_uow, mock_story, mock_story_repo, mock_dependency_repo
    ) -> None:
        """Verify IncompleteDependencyException when deps are not CONCLUIDO."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(return_value=["DEP-001"])
        dep1 = MagicMock(spec=Story)
        dep1.id = "DEP-001"
        dep1.name = "Dep Incompleta"
        dep1.status = StoryStatus.EXECUCAO

        mock_story_repo.get_by_id = AsyncMock(
            side_effect=lambda pid, sid: {
                "TEST-001": mock_story,
                "DEP-001": dep1,
            }[sid]
        )

        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        with pytest.raises(IncompleteDependencyException):
            await use_case.execute(1, dto)

    @pytest.mark.asyncio
    async def test_skips_none_dependency_story(
        self, mock_uow, mock_story, mock_story_repo, mock_dependency_repo
    ) -> None:
        """Verify dependency is skipped when get_by_id returns None."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(
            return_value=["DEP-001", "DEP-002"]
        )
        dep2 = MagicMock(spec=Story)
        dep2.id = "DEP-002"
        dep2.name = "Dep 2"
        dep2.status = StoryStatus.CONCLUIDO

        mock_story_repo.get_by_id = AsyncMock(
            side_effect=lambda pid, sid: {
                "TEST-001": mock_story,
                "DEP-001": None,
                "DEP-002": dep2,
            }[sid]
        )

        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        # Should succeed: DEP-001 is None (skipped), DEP-002 is CONCLUIDO
        await use_case.execute(1, dto)

        assert mock_story.status == StoryStatus.CONCLUIDO

    @pytest.mark.asyncio
    async def test_incomplete_exception_contains_details(
        self, mock_uow, mock_story, mock_story_repo, mock_dependency_repo
    ) -> None:
        """Verify exception includes incomplete dependency details."""
        mock_story.status = StoryStatus.BACKLOG
        mock_dependency_repo.get_dependencies = AsyncMock(return_value=["DEP-001"])
        dep1 = MagicMock(spec=Story)
        dep1.id = "DEP-001"
        dep1.name = "Blocker Story"
        dep1.status = StoryStatus.TESTES

        mock_story_repo.get_by_id = AsyncMock(
            side_effect=lambda pid, sid: {
                "TEST-001": mock_story,
                "DEP-001": dep1,
            }[sid]
        )

        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(story_id="TEST-001", status="CONCLUIDO")

        with pytest.raises(IncompleteDependencyException) as exc_info:
            await use_case.execute(1, dto)

        assert exc_info.value.story_id == "TEST-001"
        assert ("DEP-001", "Blocker Story", "TESTES") in (
            exc_info.value.incomplete_dependencies
        )
