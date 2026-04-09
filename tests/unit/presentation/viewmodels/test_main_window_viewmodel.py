"""Headless tests for MainWindowViewModel.

Tests business logic (data transformation, state management, signal emissions)
without any PySide6 dependency. Uses unittest.mock to mock PySide6 modules.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# PySide6 mock setup — must happen before importing the module under test
# ---------------------------------------------------------------------------
import sys
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_table_model=True)

# Remove cached presentation modules so they get re-imported with mocked PySide6
_modules_to_purge = [
    key
    for key in sys.modules
    if key.startswith("backlog_manager.presentation.viewmodels.")
    or key.startswith("backlog_manager.presentation.theme")
]
for _key in _modules_to_purge:
    del sys.modules[_key]

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.story import (
        CreateStoryInputDTO,
        EditStoryInputDTO,
        StoryOutputDTO,
    )
    from backlog_manager.domain.exceptions import (
        BacklogManagerException,
        IncompleteDependencyException,
    )
    from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
        MainWindowViewModel,
    )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_container() -> MagicMock:
    """Create a mock DI container with async context manager for UoW."""
    container = MagicMock()
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    return container


def _sample_stories() -> list[StoryOutputDTO]:
    """Create sample stories matching conftest fixture."""
    return [
        StoryOutputDTO(
            planning_id=1,
            id="COMP-001",
            component="COMP",
            name="Primeira Historia",
            story_points=3,
            priority=1,
            status="BACKLOG",
            duration=2,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 16),
            developer_id=1,
            feature_id=1,
            developer_name="Joao Silva",
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=["API-001"],
        ),
        StoryOutputDTO(
            planning_id=1,
            id="COMP-002",
            component="COMP",
            name="Segunda Historia",
            story_points=5,
            priority=2,
            status="BACKLOG",
            duration=3,
            start_date=date(2026, 1, 17),
            end_date=date(2026, 1, 20),
            developer_id=None,
            feature_id=1,
            developer_name=None,
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=[],
        ),
        StoryOutputDTO(
            planning_id=1,
            id="API-001",
            component="API",
            name="Terceira Historia",
            story_points=8,
            priority=3,
            status="DOING",
            duration=4,
            start_date=None,
            end_date=None,
            developer_id=2,
            feature_id=None,
            developer_name="Maria Santos",
            feature_name=None,
            wave=0,
            dependency_ids=[],
        ),
    ]


# ---------------------------------------------------------------------------
# Tests: Initialization
# ---------------------------------------------------------------------------


class TestMainWindowViewModelInitialization:
    """Tests for MainWindowViewModel initialization."""

    def test_initial_state(self) -> None:
        """Test that ViewModel initializes with correct state."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        assert viewmodel.stories == []
        assert viewmodel.selected_story_id is None
        assert viewmodel.selected_story is None
        assert viewmodel.is_loading is False

    def test_table_model_created(self) -> None:
        """Test that table model is created on initialization."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        assert viewmodel.table_model is not None


# ---------------------------------------------------------------------------
# Tests: Selection
# ---------------------------------------------------------------------------


class TestMainWindowViewModelSelection:
    """Tests for story selection in MainWindowViewModel."""

    def test_select_story_updates_selected_id(self) -> None:
        """Test that selecting a story updates the selected ID."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel.select_story("TEST-001")

        assert viewmodel.selected_story_id == "TEST-001"

    def test_select_story_emits_signal(self) -> None:
        """Test that selecting a story emits story_selected signal."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        viewmodel.select_story("TEST-001")

        assert ("TEST-001",) in viewmodel.story_selected.emissions

    def test_select_none_clears_selection(self) -> None:
        """Test that selecting None clears the selection."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel.select_story("TEST-001")
        viewmodel.select_story(None)

        assert viewmodel.selected_story_id is None

    def test_selected_story_returns_dto_when_found(self) -> None:
        """Test that selected_story returns the DTO when found."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        stories = _sample_stories()
        viewmodel._table_model.set_stories(stories)
        viewmodel._stories = stories
        viewmodel.select_story("COMP-001")

        assert viewmodel.selected_story is not None
        assert viewmodel.selected_story.id == "COMP-001"


# ---------------------------------------------------------------------------
# Tests: Load Stories
# ---------------------------------------------------------------------------


class TestMainWindowViewModelLoadStories:
    """Tests for loading stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_load_stories_success(self) -> None:
        """Test successful story loading."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        stories = _sample_stories()

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=stories)

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.load_stories()

        assert len(viewmodel.stories) == 3
        # loading signal emitted True then False
        assert viewmodel.loading.emissions == [(True,), (False,)]
        # stories_changed emitted once
        assert len(viewmodel.stories_changed.emissions) == 1

    @pytest.mark.asyncio
    async def test_load_stories_error_emits_signal(self) -> None:
        """Test that error during loading emits error_occurred signal."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.load_stories()

        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro inesperado" in viewmodel.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests: Create Story
# ---------------------------------------------------------------------------


class TestMainWindowViewModelCreateStory:
    """Tests for creating stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_create_story_success(self) -> None:
        """Test successful story creation."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        created_story = StoryOutputDTO(
            planning_id=1,
            id="NEW-001",
            component="NEW",
            name="New Story",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )

        mock_create_use_case = MagicMock()
        mock_create_use_case.execute = AsyncMock(return_value=created_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[created_story])

        with (
            patch.object(
                container,
                "create_story_use_case_factory",
                return_value=mock_create_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            dto = CreateStoryInputDTO(
                component="NEW",
                name="New Story",
                story_points=5,
            )
            result = await viewmodel.create_story(dto)

        assert result is not None
        assert result.id == "NEW-001"

    @pytest.mark.asyncio
    async def test_create_story_validation_error(self) -> None:
        """Test that validation error during creation emits signal."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_create_use_case = MagicMock()
        mock_create_use_case.execute = AsyncMock(
            side_effect=ValueError("Invalid story points")
        )

        with patch.object(
            container,
            "create_story_use_case_factory",
            return_value=mock_create_use_case,
        ):
            dto = CreateStoryInputDTO(
                component="NEW",
                name="New Story",
                story_points=5,
            )
            result = await viewmodel.create_story(dto)

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1


# ---------------------------------------------------------------------------
# Tests: Edit Story
# ---------------------------------------------------------------------------


class TestMainWindowViewModelEditStory:
    """Tests for editing stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_edit_story_success(self) -> None:
        """Test successful story editing."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        edited_story = StoryOutputDTO(
            planning_id=1,
            id="COMP-001",
            component="COMP",
            name="Updated Name",
            story_points=8,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )

        mock_edit_use_case = MagicMock()
        mock_edit_use_case.execute = AsyncMock(return_value=edited_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[edited_story])

        with (
            patch.object(
                container,
                "create_edit_story_use_case",
                return_value=mock_edit_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            dto = EditStoryInputDTO(
                story_id="COMP-001",
                name="Updated Name",
                story_points=8,
            )
            result = await viewmodel.edit_story(dto)

        assert result is not None
        assert result.name == "Updated Name"
        assert result.story_points == 8


# ---------------------------------------------------------------------------
# Tests: Delete Story
# ---------------------------------------------------------------------------


class TestMainWindowViewModelDeleteStory:
    """Tests for deleting stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_delete_story_success(self) -> None:
        """Test successful story deletion."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.delete_story("COMP-001")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_story_clears_selection_if_selected(self) -> None:
        """Test that deleting the selected story clears selection."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel.select_story("COMP-001")

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.delete_story("COMP-001")

        assert viewmodel.selected_story_id is None


# ---------------------------------------------------------------------------
# Tests: Move Priority
# ---------------------------------------------------------------------------


class TestMainWindowViewModelMovePriority:
    """Tests for moving story priority in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_move_priority_up_success(self) -> None:
        """Test successful priority move up."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_move_use_case = MagicMock()
        mock_move_use_case.move_up = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_move_priority_use_case",
                return_value=mock_move_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.move_priority_up("COMP-001")

        assert result is True

    @pytest.mark.asyncio
    async def test_move_priority_down_success(self) -> None:
        """Test successful priority move down."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_move_use_case = MagicMock()
        mock_move_use_case.move_down = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_move_priority_use_case",
                return_value=mock_move_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.move_priority_down("COMP-001")

        assert result is True


# ---------------------------------------------------------------------------
# Tests: Assign Developer
# ---------------------------------------------------------------------------


class TestMainWindowViewModelAssignDeveloper:
    """Tests for developer assignment in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_assign_developer_success(self) -> None:
        """Test successful developer assignment."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        assigned_story = StoryOutputDTO(
            planning_id=1,
            id="COMP-001",
            component="COMP",
            name="Test Story",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=1,
            feature_id=None,
        )

        mock_assign_use_case = MagicMock()
        mock_assign_use_case.assign = AsyncMock(return_value=assigned_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[assigned_story])

        with (
            patch.object(
                container,
                "create_assign_developer_use_case",
                return_value=mock_assign_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.assign_developer("COMP-001", 1)

        assert result is not None
        assert result.developer_id == 1

    @pytest.mark.asyncio
    async def test_unassign_developer_success(self) -> None:
        """Test successful developer unassignment."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        unassigned_story = StoryOutputDTO(
            planning_id=1,
            id="COMP-001",
            component="COMP",
            name="Test Story",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )

        mock_assign_use_case = MagicMock()
        mock_assign_use_case.unassign = AsyncMock(return_value=unassigned_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[unassigned_story])

        with (
            patch.object(
                container,
                "create_assign_developer_use_case",
                return_value=mock_assign_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.unassign_developer("COMP-001")

        assert result is not None
        assert result.developer_id is None


# ---------------------------------------------------------------------------
# Tests: Filtering
# ---------------------------------------------------------------------------


class TestMainWindowViewModelFiltering:
    """Tests for in-memory filtering in MainWindowViewModel."""

    def test_get_stories_by_status(self) -> None:
        """Test filtering stories by status."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel._stories = _sample_stories()

        backlog_stories = viewmodel.get_stories_by_status("BACKLOG")
        assert len(backlog_stories) == 2

        doing_stories = viewmodel.get_stories_by_status("DOING")
        assert len(doing_stories) == 1

    def test_get_stories_by_feature(self) -> None:
        """Test filtering stories by feature."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel._stories = _sample_stories()

        feature_stories = viewmodel.get_stories_by_feature(1)
        assert len(feature_stories) == 2

    def test_get_stories_by_developer(self) -> None:
        """Test filtering stories by developer."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel._stories = _sample_stories()

        dev_stories = viewmodel.get_stories_by_developer(1)
        assert len(dev_stories) == 1
        assert dev_stories[0].id == "COMP-001"


# ---------------------------------------------------------------------------
# Tests: Duplicate Story
# ---------------------------------------------------------------------------


class TestMainWindowViewModelDuplicateStory:
    """Tests for duplicating stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_duplicate_story_success(self) -> None:
        """Test successful story duplication."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        duplicated_story = StoryOutputDTO(
            planning_id=1,
            id="COMP-002",
            component="COMP",
            name="Sample Story (copia)",
            story_points=5,
            priority=2,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )

        mock_duplicate_use_case = MagicMock()
        mock_duplicate_use_case.execute = AsyncMock(return_value=duplicated_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[duplicated_story])

        with (
            patch.object(
                container,
                "create_duplicate_story_use_case",
                return_value=mock_duplicate_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.duplicate_story("COMP-001")

        assert result is not None
        assert result.id == "COMP-002"
        assert result.name == "Sample Story (copia)"

    @pytest.mark.asyncio
    async def test_duplicate_story_emits_stories_changed(self) -> None:
        """Test that stories_changed signal is emitted after duplication."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        duplicated_story = StoryOutputDTO(
            planning_id=1,
            id="COMP-002",
            component="COMP",
            name="Copy",
            story_points=5,
            priority=2,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )

        mock_duplicate_use_case = MagicMock()
        mock_duplicate_use_case.execute = AsyncMock(return_value=duplicated_story)

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[duplicated_story])

        with (
            patch.object(
                container,
                "create_duplicate_story_use_case",
                return_value=mock_duplicate_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.duplicate_story("COMP-001")

        assert len(viewmodel.stories_changed.emissions) >= 1

    @pytest.mark.asyncio
    async def test_duplicate_story_error_handling(self) -> None:
        """Test error handling during duplication."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_duplicate_use_case = MagicMock()
        mock_duplicate_use_case.execute = AsyncMock(
            side_effect=Exception("Duplication failed")
        )

        with patch.object(
            container,
            "create_duplicate_story_use_case",
            return_value=mock_duplicate_use_case,
        ):
            result = await viewmodel.duplicate_story("COMP-001")

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro inesperado" in viewmodel.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests: Selection Persistence
# ---------------------------------------------------------------------------


class TestMainWindowViewModelSelectionPersistence:
    """Tests for selection persistence during operations (EP-025)."""

    @pytest.mark.asyncio
    async def test_selected_story_id_preserved_after_load_stories(self) -> None:
        """Test that selected_story_id is NOT cleared during load_stories."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel.select_story("COMP-001")
        stories = _sample_stories()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=stories)

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_list_use_case,
        ):
            await viewmodel.load_stories()

        assert viewmodel.selected_story_id == "COMP-001"

    @pytest.mark.asyncio
    async def test_delete_story_selects_adjacent_story(self) -> None:
        """Test that deleting a story selects the adjacent story."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        stories = _sample_stories()
        viewmodel._stories = stories
        viewmodel._table_model.set_stories(stories)
        viewmodel.select_story("COMP-001")

        remaining = [stories[1], stories[2]]

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=remaining)

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.delete_story("COMP-001")

        # Should select adjacent story (next one)
        assert viewmodel.selected_story_id == "COMP-002"

    @pytest.mark.asyncio
    async def test_delete_last_story_clears_selection(self) -> None:
        """Test that deleting the last story clears selection."""
        container = _make_container()
        single_story = StoryOutputDTO(
            planning_id=1,
            id="ONLY-001",
            component="COMP",
            name="Only Story",
            story_points=3,
            priority=1,
            status="BACKLOG",
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel._stories = [single_story]
        viewmodel._table_model.set_stories([single_story])
        viewmodel.select_story("ONLY-001")

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.delete_story("ONLY-001")

        assert viewmodel.selected_story_id is None

    @pytest.mark.asyncio
    async def test_delete_middle_story_selects_next(self) -> None:
        """Test deleting middle story selects next story."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        stories = _sample_stories()
        viewmodel._stories = stories
        viewmodel._table_model.set_stories(stories)
        viewmodel.select_story("COMP-002")

        remaining = [stories[0], stories[2]]

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=remaining)

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.delete_story("COMP-002")

        assert viewmodel.selected_story_id == "API-001"

    @pytest.mark.asyncio
    async def test_delete_last_row_selects_previous(self) -> None:
        """Test deleting last row selects previous story."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        stories = _sample_stories()
        viewmodel._stories = stories
        viewmodel._table_model.set_stories(stories)
        viewmodel.select_story("API-001")  # Last row (index 2)

        remaining = [stories[0], stories[1]]

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock()

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=remaining)

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            await viewmodel.delete_story("API-001")

        assert viewmodel.selected_story_id == "COMP-002"


# ---------------------------------------------------------------------------
# Tests: Error Handling
# ---------------------------------------------------------------------------


class TestMainWindowViewModelErrorHandling:
    """Tests for error handling in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_backlog_manager_exception_handling(self) -> None:
        """Test that BacklogManagerException is handled properly."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        class TestException(BacklogManagerException):
            pass

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(
            side_effect=TestException("Test error message")
        )

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.load_stories()

        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Test error message" in viewmodel.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests: Edit Story Error Handling (lines 210-225)
# ---------------------------------------------------------------------------


class TestMainWindowViewModelEditStoryErrors:
    """Tests for error handling in edit_story."""

    @pytest.mark.asyncio
    async def test_edit_story_incomplete_dependency_exception(self) -> None:
        """Test that IncompleteDependencyException shows dependency details."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        exc = IncompleteDependencyException(
            story_id="COMP-001",
            incomplete_dependencies=[
                ("DEP-001", "Dependencia A", "BACKLOG"),
                ("DEP-002", "Dependencia B", "DOING"),
            ],
        )

        mock_edit_use_case = MagicMock()
        mock_edit_use_case.execute = AsyncMock(side_effect=exc)

        with patch.object(
            container,
            "create_edit_story_use_case",
            return_value=mock_edit_use_case,
        ):
            dto = EditStoryInputDTO(
                story_id="COMP-001",
                status="CONCLUIDO",
            )
            result = await viewmodel.edit_story(dto)

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        error_msg = viewmodel.error_occurred.emissions[0][0]
        assert "COMP-001" in error_msg
        assert "DEP-001" in error_msg
        assert "Dependencia A" in error_msg
        assert "BACKLOG" in error_msg
        assert "DEP-002" in error_msg

    @pytest.mark.asyncio
    async def test_edit_story_generic_exception(self) -> None:
        """Test that generic exception in edit_story emits error signal."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_edit_use_case = MagicMock()
        mock_edit_use_case.execute = AsyncMock(
            side_effect=RuntimeError("Database failure")
        )

        with patch.object(
            container,
            "create_edit_story_use_case",
            return_value=mock_edit_use_case,
        ):
            dto = EditStoryInputDTO(
                story_id="COMP-001",
                name="Updated",
            )
            result = await viewmodel.edit_story(dto)

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro inesperado" in viewmodel.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests: Delete Story Error Handling (lines 270-283)
# ---------------------------------------------------------------------------


class TestMainWindowViewModelDeleteStoryErrors:
    """Tests for error handling in delete_story."""

    @pytest.mark.asyncio
    async def test_delete_story_not_found_refreshes_list(self) -> None:
        """Test that ValueError with 'nao encontrada' refreshes without error."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1
        viewmodel.select_story("COMP-001")

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock(
            side_effect=ValueError("Historia nao encontrada")
        )

        mock_list_use_case = MagicMock()
        mock_list_use_case.execute = AsyncMock(return_value=[])

        with (
            patch.object(
                container,
                "create_delete_story_use_case",
                return_value=mock_delete_use_case,
            ),
            patch.object(
                container,
                "create_list_stories_use_case",
                return_value=mock_list_use_case,
            ),
        ):
            result = await viewmodel.delete_story("COMP-001")

        assert result is True
        assert viewmodel.selected_story_id is None
        # No error_occurred emission for "nao encontrada"
        assert len(viewmodel.error_occurred.emissions) == 0

    @pytest.mark.asyncio
    async def test_delete_story_value_error_other(self) -> None:
        """Test that ValueError without 'nao encontrada' emits error."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock(
            side_effect=ValueError("Invalid ID format")
        )

        with patch.object(
            container,
            "create_delete_story_use_case",
            return_value=mock_delete_use_case,
        ):
            result = await viewmodel.delete_story("BAD-ID")

        assert result is False
        assert len(viewmodel.error_occurred.emissions) == 1

    @pytest.mark.asyncio
    async def test_delete_story_generic_exception(self) -> None:
        """Test that generic exception in delete_story emits error."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_delete_use_case = MagicMock()
        mock_delete_use_case.execute = AsyncMock(
            side_effect=RuntimeError("Connection lost")
        )

        with patch.object(
            container,
            "create_delete_story_use_case",
            return_value=mock_delete_use_case,
        ):
            result = await viewmodel.delete_story("COMP-001")

        assert result is False
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro inesperado" in viewmodel.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests: Move Priority Error Handling (lines 304-306, 327-329)
# ---------------------------------------------------------------------------


class TestMainWindowViewModelMovePriorityErrors:
    """Tests for error handling in move_priority_up/down."""

    @pytest.mark.asyncio
    async def test_move_priority_up_error(self) -> None:
        """Test that exception in move_priority_up emits error and returns False."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_move_use_case = MagicMock()
        mock_move_use_case.move_up = AsyncMock(
            side_effect=RuntimeError("Cannot move up")
        )

        with patch.object(
            container,
            "create_move_priority_use_case",
            return_value=mock_move_use_case,
        ):
            result = await viewmodel.move_priority_up("COMP-001")

        assert result is False
        assert len(viewmodel.error_occurred.emissions) == 1

    @pytest.mark.asyncio
    async def test_move_priority_down_error(self) -> None:
        """Test that exception in move_priority_down emits error and returns False."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_move_use_case = MagicMock()
        mock_move_use_case.move_down = AsyncMock(
            side_effect=RuntimeError("Cannot move down")
        )

        with patch.object(
            container,
            "create_move_priority_use_case",
            return_value=mock_move_use_case,
        ):
            result = await viewmodel.move_priority_down("COMP-001")

        assert result is False
        assert len(viewmodel.error_occurred.emissions) == 1


# ---------------------------------------------------------------------------
# Tests: Assign/Unassign Developer Error Handling (lines 353-355, 376-378)
# ---------------------------------------------------------------------------


class TestMainWindowViewModelAssignDeveloperErrors:
    """Tests for error handling in assign/unassign developer."""

    @pytest.mark.asyncio
    async def test_assign_developer_error(self) -> None:
        """Test that exception in assign_developer emits error and returns None."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_assign_use_case = MagicMock()
        mock_assign_use_case.assign = AsyncMock(
            side_effect=RuntimeError("Developer not found")
        )

        with patch.object(
            container,
            "create_assign_developer_use_case",
            return_value=mock_assign_use_case,
        ):
            result = await viewmodel.assign_developer("COMP-001", 999)

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1

    @pytest.mark.asyncio
    async def test_unassign_developer_error(self) -> None:
        """Test that exception in unassign_developer emits error and returns None."""
        container = _make_container()
        viewmodel = MainWindowViewModel(container)
        viewmodel._active_planning_id = 1

        mock_assign_use_case = MagicMock()
        mock_assign_use_case.unassign = AsyncMock(
            side_effect=RuntimeError("Unassign failed")
        )

        with patch.object(
            container,
            "create_assign_developer_use_case",
            return_value=mock_assign_use_case,
        ):
            result = await viewmodel.unassign_developer("COMP-001")

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
