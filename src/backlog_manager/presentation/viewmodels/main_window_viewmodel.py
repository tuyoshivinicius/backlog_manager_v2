"""Main Window ViewModel.

This module provides the ViewModel for the main application window,
coordinating story operations and emitting signals for UI updates.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Sequence

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.story import (
    CreateStoryInputDTO,
    EditStoryInputDTO,
    StoryOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class MainWindowViewModel(QObject):
    """ViewModel for the main application window.

    Manages story operations, selection state, and emits signals for
    UI updates following the MVVM pattern.

    Signals:
        stories_changed: Emitted when the story list changes.
        story_selected: Emitted when a story is selected (payload: story_id).
        loading: Emitted when loading state changes (payload: is_loading).
        error_occurred: Emitted when an error occurs (payload: error_message).
    """

    # Signals as per contracts/viewmodel-signals.md
    stories_changed = Signal()
    story_selected = Signal(str)
    loading = Signal(bool)
    error_occurred = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        self._stories: list[StoryOutputDTO] = []
        self._selected_story_id: str | None = None
        self._is_loading: bool = False

        # Create the table model
        self._table_model = StoryTableModel()

        logger.debug("MainWindowViewModel initialized")

    @property
    def table_model(self) -> StoryTableModel:
        """Get the story table model.

        Returns:
            The StoryTableModel instance.
        """
        return self._table_model

    @property
    def stories(self) -> list[StoryOutputDTO]:
        """Get the current list of stories.

        Returns:
            List of story DTOs.
        """
        return self._stories.copy()

    @property
    def selected_story_id(self) -> str | None:
        """Get the currently selected story ID.

        Returns:
            Selected story ID or None.
        """
        return self._selected_story_id

    @property
    def selected_story(self) -> StoryOutputDTO | None:
        """Get the currently selected story.

        Returns:
            Selected story DTO or None.
        """
        if self._selected_story_id is None:
            return None
        return self._table_model.get_story_by_id(self._selected_story_id)

    @property
    def is_loading(self) -> bool:
        """Check if an operation is in progress.

        Returns:
            True if loading, False otherwise.
        """
        return self._is_loading

    def select_story(self, story_id: str | None) -> None:
        """Select a story by ID.

        Args:
            story_id: Story ID to select, or None to clear selection.
        """
        self._selected_story_id = story_id
        if story_id:
            self.story_selected.emit(story_id)
            logger.debug("Story selected: %s", story_id)

    def _set_loading(self, is_loading: bool) -> None:
        """Set the loading state and emit signal.

        Args:
            is_loading: New loading state.
        """
        self._is_loading = is_loading
        self.loading.emit(is_loading)

    def _handle_error(self, error: Exception, context: str) -> None:
        """Handle an error by logging and emitting signal.

        Args:
            error: The exception that occurred.
            context: Context description for the error.
        """
        if isinstance(error, BacklogManagerException):
            message = str(error)
            logger.warning("Erro em %s: %s", context, message)
        else:
            message = f"Erro inesperado: {error}"
            logger.exception("Erro inesperado em %s", context)

        self.error_occurred.emit(message)

    async def load_stories(self) -> None:
        """Load all stories from the database.

        Emits stories_changed signal on success, error_occurred on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_stories_use_case(uow)
                stories = await use_case.execute()
                self._stories = list(stories)
                self._table_model.set_stories(self._stories)
                self.stories_changed.emit()
                logger.info("Loaded %d stories", len(self._stories))
        except Exception as e:
            self._handle_error(e, "carregar historias")
        finally:
            self._set_loading(False)

    async def create_story(self, dto: CreateStoryInputDTO) -> StoryOutputDTO | None:
        """Create a new story.

        Args:
            dto: Input DTO with story data.

        Returns:
            Created story DTO on success, None on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_story_use_case_factory(uow)
                story = await use_case.execute(dto)
                await self.load_stories()
                logger.info("Created story: %s", story.id)
                return story
        except Exception as e:
            self._handle_error(e, "criar historia")
            return None
        finally:
            self._set_loading(False)

    async def edit_story(self, dto: EditStoryInputDTO) -> StoryOutputDTO | None:
        """Edit an existing story.

        Args:
            dto: Input DTO with updated story data.

        Returns:
            Updated story DTO on success, None on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_edit_story_use_case(uow)
                story = await use_case.execute(dto)
                await self.load_stories()
                logger.info("Edited story: %s", story.id)
                return story
        except Exception as e:
            self._handle_error(e, "editar historia")
            return None
        finally:
            self._set_loading(False)

    async def delete_story(self, story_id: str) -> bool:
        """Delete a story.

        Args:
            story_id: ID of the story to delete.

        Returns:
            True on success, False on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_delete_story_use_case(uow)
                await use_case.execute(story_id)
                if self._selected_story_id == story_id:
                    self._selected_story_id = None
                await self.load_stories()
                logger.info("Deleted story: %s", story_id)
                return True
        except ValueError as e:
            # Story not found - likely already deleted (e.g., double-click)
            # Just refresh the list without showing error to user
            if "nao encontrada" in str(e):
                logger.debug("Story %s already deleted, refreshing list", story_id)
                if self._selected_story_id == story_id:
                    self._selected_story_id = None
                await self.load_stories()
                return True
            self._handle_error(e, "deletar historia")
            return False
        except Exception as e:
            self._handle_error(e, "deletar historia")
            return False
        finally:
            self._set_loading(False)

    async def move_priority_up(self, story_id: str) -> bool:
        """Move a story's priority up (lower priority number).

        Args:
            story_id: ID of the story to move.

        Returns:
            True on success, False on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_move_priority_use_case(uow)
                await use_case.move_up(story_id)
                await self.load_stories()
                logger.info("Moved story priority up: %s", story_id)
                return True
        except Exception as e:
            self._handle_error(e, "mover prioridade")
            return False
        finally:
            self._set_loading(False)

    async def move_priority_down(self, story_id: str) -> bool:
        """Move a story's priority down (higher priority number).

        Args:
            story_id: ID of the story to move.

        Returns:
            True on success, False on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_move_priority_use_case(uow)
                await use_case.move_down(story_id)
                await self.load_stories()
                logger.info("Moved story priority down: %s", story_id)
                return True
        except Exception as e:
            self._handle_error(e, "mover prioridade")
            return False
        finally:
            self._set_loading(False)

    async def assign_developer(
        self, story_id: str, developer_id: int
    ) -> StoryOutputDTO | None:
        """Assign a developer to a story.

        Args:
            story_id: ID of the story.
            developer_id: ID of the developer to assign.

        Returns:
            Updated story DTO on success, None on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_assign_developer_use_case(uow)
                story = await use_case.assign(story_id, developer_id)
                await self.load_stories()
                logger.info("Assigned developer %d to story %s", developer_id, story_id)
                return story
        except Exception as e:
            self._handle_error(e, "atribuir desenvolvedor")
            return None
        finally:
            self._set_loading(False)

    async def unassign_developer(self, story_id: str) -> StoryOutputDTO | None:
        """Remove developer assignment from a story.

        Args:
            story_id: ID of the story.

        Returns:
            Updated story DTO on success, None on failure.
        """
        self._set_loading(True)
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_assign_developer_use_case(uow)
                story = await use_case.unassign(story_id)
                await self.load_stories()
                logger.info("Unassigned developer from story %s", story_id)
                return story
        except Exception as e:
            self._handle_error(e, "remover desenvolvedor")
            return None
        finally:
            self._set_loading(False)

    def get_stories_by_status(self, status: str) -> Sequence[StoryOutputDTO]:
        """Filter stories by status (in-memory).

        Args:
            status: Status to filter by.

        Returns:
            Filtered list of stories.
        """
        return [s for s in self._stories if s.status == status]

    def get_stories_by_feature(self, feature_id: int) -> Sequence[StoryOutputDTO]:
        """Filter stories by feature (in-memory).

        Args:
            feature_id: Feature ID to filter by.

        Returns:
            Filtered list of stories.
        """
        return [s for s in self._stories if s.feature_id == feature_id]

    def get_stories_by_developer(self, developer_id: int) -> Sequence[StoryOutputDTO]:
        """Filter stories by developer (in-memory).

        Args:
            developer_id: Developer ID to filter by.

        Returns:
            Filtered list of stories.
        """
        return [s for s in self._stories if s.developer_id == developer_id]
