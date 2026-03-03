"""Tests for MainWindowViewModel.

This module contains unit tests for the MainWindowViewModel class,
verifying signal emissions and proper operation handling.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from PySide6.QtCore import SignalInstance

from backlog_manager.application.dto.story import (
    CreateStoryInputDTO,
    EditStoryInputDTO,
    StoryOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
    MainWindowViewModel,
)


class TestMainWindowViewModelInitialization:
    """Tests for MainWindowViewModel initialization."""

    def test_initial_state(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that ViewModel initializes with correct state."""
        viewmodel = MainWindowViewModel(container)

        assert viewmodel.stories == []
        assert viewmodel.selected_story_id is None
        assert viewmodel.selected_story is None
        assert viewmodel.is_loading is False

    def test_table_model_created(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that table model is created on initialization."""
        viewmodel = MainWindowViewModel(container)

        assert viewmodel.table_model is not None
        assert viewmodel.table_model.rowCount() == 0


class TestMainWindowViewModelSelection:
    """Tests for story selection in MainWindowViewModel."""

    def test_select_story_updates_selected_id(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that selecting a story updates the selected ID."""
        viewmodel = MainWindowViewModel(container)
        viewmodel.select_story("TEST-001")

        assert viewmodel.selected_story_id == "TEST-001"

    def test_select_story_emits_signal(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that selecting a story emits story_selected signal."""
        viewmodel = MainWindowViewModel(container)

        signal_received = []

        def on_story_selected(story_id: str) -> None:
            signal_received.append(story_id)

        viewmodel.story_selected.connect(on_story_selected)
        viewmodel.select_story("TEST-001")

        assert signal_received == ["TEST-001"]

    def test_select_none_clears_selection(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that selecting None clears the selection."""
        viewmodel = MainWindowViewModel(container)
        viewmodel.select_story("TEST-001")
        viewmodel.select_story(None)

        assert viewmodel.selected_story_id is None

    def test_selected_story_returns_dto_when_found(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that selected_story returns the DTO when found."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories
        viewmodel.select_story("COMP-001")

        assert viewmodel.selected_story is not None
        assert viewmodel.selected_story.id == "COMP-001"


class TestMainWindowViewModelLoadStories:
    """Tests for loading stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_load_stories_success(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story loading."""
        viewmodel = MainWindowViewModel(container)

        # Track signals
        loading_states: list[bool] = []
        stories_changed_count = [0]

        viewmodel.loading.connect(lambda x: loading_states.append(x))
        viewmodel.stories_changed.connect(
            lambda: stories_changed_count.__setitem__(0, stories_changed_count[0] + 1)
        )

        # Mock the use case factory
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=sample_stories)

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.load_stories()

        assert len(viewmodel.stories) == 3
        assert viewmodel.table_model.rowCount() == 3
        assert loading_states == [True, False]
        assert stories_changed_count[0] == 1

    @pytest.mark.asyncio
    async def test_load_stories_error_emits_signal(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that error during loading emits error_occurred signal."""
        viewmodel = MainWindowViewModel(container)

        errors: list[str] = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        # Mock the use case factory to raise an exception
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(side_effect=Exception("Database error"))

        with patch.object(
            container,
            "create_list_stories_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.load_stories()

        assert len(errors) == 1
        assert "Erro inesperado" in errors[0]


class TestMainWindowViewModelCreateStory:
    """Tests for creating stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_create_story_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story creation."""
        viewmodel = MainWindowViewModel(container)

        created_story = StoryOutputDTO(
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
    async def test_create_story_validation_error(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that validation error during creation emits signal."""
        viewmodel = MainWindowViewModel(container)

        errors: list[str] = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

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
        assert len(errors) == 1


class TestMainWindowViewModelEditStory:
    """Tests for editing stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_edit_story_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story editing."""
        viewmodel = MainWindowViewModel(container)

        edited_story = StoryOutputDTO(
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


class TestMainWindowViewModelDeleteStory:
    """Tests for deleting stories in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_delete_story_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story deletion."""
        viewmodel = MainWindowViewModel(container)

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
    async def test_delete_story_clears_selection_if_selected(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that deleting the selected story clears selection."""
        viewmodel = MainWindowViewModel(container)
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


class TestMainWindowViewModelMovePriority:
    """Tests for moving story priority in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_move_priority_up_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful priority move up."""
        viewmodel = MainWindowViewModel(container)

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
    async def test_move_priority_down_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful priority move down."""
        viewmodel = MainWindowViewModel(container)

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


class TestMainWindowViewModelAssignDeveloper:
    """Tests for developer assignment in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_assign_developer_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful developer assignment."""
        viewmodel = MainWindowViewModel(container)

        assigned_story = StoryOutputDTO(
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
    async def test_unassign_developer_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful developer unassignment."""
        viewmodel = MainWindowViewModel(container)

        unassigned_story = StoryOutputDTO(
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


class TestMainWindowViewModelFiltering:
    """Tests for in-memory filtering in MainWindowViewModel."""

    def test_get_stories_by_status(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test filtering stories by status."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._stories = sample_stories

        backlog_stories = viewmodel.get_stories_by_status("BACKLOG")
        assert len(backlog_stories) == 2

        doing_stories = viewmodel.get_stories_by_status("DOING")
        assert len(doing_stories) == 1

    def test_get_stories_by_feature(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test filtering stories by feature."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._stories = sample_stories

        feature_stories = viewmodel.get_stories_by_feature(1)
        assert len(feature_stories) == 2

    def test_get_stories_by_developer(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test filtering stories by developer."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._stories = sample_stories

        dev_stories = viewmodel.get_stories_by_developer(1)
        assert len(dev_stories) == 1
        assert dev_stories[0].id == "COMP-001"


class TestMainWindowViewModelErrorHandling:
    """Tests for error handling in MainWindowViewModel."""

    @pytest.mark.asyncio
    async def test_backlog_manager_exception_handling(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that BacklogManagerException is handled properly."""
        viewmodel = MainWindowViewModel(container)

        errors: list[str] = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

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

        assert len(errors) == 1
        assert "Test error message" in errors[0]
