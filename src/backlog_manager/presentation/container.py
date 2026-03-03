"""Dependency Injection Container for the presentation layer.

This module provides a centralized container that instantiates and manages
all dependencies needed by the presentation layer, following Constitution IV.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from backlog_manager.application.use_cases.allocation import ExecuteAllocationUseCase
from backlog_manager.application.use_cases.dependency import (
    AddDependencyUseCase,
    GetDependenciesUseCase,
    GetDependentsUseCase,
    RemoveDependencyUseCase,
)
from backlog_manager.application.use_cases.developer import (
    CreateDeveloperUseCase,
    DeleteDeveloperUseCase,
    ListDevelopersUseCase,
    UpdateDeveloperUseCase,
)
from backlog_manager.application.use_cases.feature import (
    CreateFeatureUseCase,
    DeleteFeatureUseCase,
    ListFeaturesUseCase,
    UpdateFeatureUseCase,
)
from backlog_manager.application.use_cases.scheduling import (
    CalculateDurationUseCase,
    CalculateScheduleUseCase,
    CalculateStoryDatesUseCase,
)
from backlog_manager.application.use_cases.story import (
    AssignDeveloperUseCase,
    CreateStoryUseCase,
    DeleteStoryUseCase,
    DuplicateStoryUseCase,
    EditStoryUseCase,
    ListStoriesUseCase,
    MovePriorityUseCase,
)
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

if TYPE_CHECKING:
    from backlog_manager.presentation.viewmodels.allocation_viewmodel import (
        AllocationViewModel,
    )
    from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
        MainWindowViewModel,
    )
    from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
        StoryDialogViewModel,
    )

logger = logging.getLogger(__name__)


class DIContainer:
    """Dependency Injection Container singleton.

    Manages the instantiation and lifecycle of all dependencies needed by
    the presentation layer. Uses lazy loading for ViewModels to optimize
    startup time.

    Example:
        container = DIContainer.initialize("backlog_manager.db")
        viewmodel = container.main_window_viewmodel
    """

    _instance: DIContainer | None = None
    _initialized: bool = False

    def __init__(self, db_path: str | Path) -> None:
        """Initialize the container with database path.

        Args:
            db_path: Path to the SQLite database file.

        Note:
            Use DIContainer.initialize() instead of calling this directly.
        """
        self._db_path = Path(db_path)

        # ViewModels - lazy initialized
        self._main_window_viewmodel: MainWindowViewModel | None = None
        self._story_dialog_viewmodel: StoryDialogViewModel | None = None
        self._allocation_viewmodel: AllocationViewModel | None = None

        logger.info("DIContainer initialized with database: %s", self._db_path)

    @classmethod
    def initialize(cls, db_path: str | Path) -> DIContainer:
        """Initialize the singleton container instance.

        Args:
            db_path: Path to the SQLite database file.

        Returns:
            The initialized DIContainer instance.

        Raises:
            RuntimeError: If container is already initialized.
        """
        if cls._initialized:
            raise RuntimeError("DIContainer is already initialized")

        cls._instance = cls(db_path)
        cls._initialized = True
        logger.info("DIContainer singleton created")
        return cls._instance

    @classmethod
    def get_instance(cls) -> DIContainer:
        """Get the singleton container instance.

        Returns:
            The DIContainer instance.

        Raises:
            RuntimeError: If container is not initialized.
        """
        if cls._instance is None or not cls._initialized:
            raise RuntimeError(
                "DIContainer is not initialized. Call initialize() first."
            )
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing purposes)."""
        cls._instance = None
        cls._initialized = False
        logger.debug("DIContainer reset")

    @property
    def db_path(self) -> Path:
        """Get the database path."""
        return self._db_path

    def create_unit_of_work(self) -> SQLiteUnitOfWork:
        """Create a new Unit of Work instance.

        Returns:
            A new SQLiteUnitOfWork configured with the database path.
        """
        return SQLiteUnitOfWork(self._db_path)

    # Story Use Case Factories
    def create_list_stories_use_case(self, uow: SQLiteUnitOfWork) -> ListStoriesUseCase:
        """Create a ListStoriesUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new ListStoriesUseCase instance.
        """
        return ListStoriesUseCase(uow)

    def create_story_use_case_factory(
        self, uow: SQLiteUnitOfWork
    ) -> CreateStoryUseCase:
        """Create a CreateStoryUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CreateStoryUseCase instance.
        """
        return CreateStoryUseCase(uow)

    def create_edit_story_use_case(self, uow: SQLiteUnitOfWork) -> EditStoryUseCase:
        """Create an EditStoryUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new EditStoryUseCase instance.
        """
        return EditStoryUseCase(uow)

    def create_delete_story_use_case(self, uow: SQLiteUnitOfWork) -> DeleteStoryUseCase:
        """Create a DeleteStoryUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new DeleteStoryUseCase instance.
        """
        return DeleteStoryUseCase(uow)

    def create_move_priority_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> MovePriorityUseCase:
        """Create a MovePriorityUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new MovePriorityUseCase instance.
        """
        return MovePriorityUseCase(uow)

    def create_assign_developer_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> AssignDeveloperUseCase:
        """Create an AssignDeveloperUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new AssignDeveloperUseCase instance.
        """
        return AssignDeveloperUseCase(uow)

    def create_duplicate_story_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> DuplicateStoryUseCase:
        """Create a DuplicateStoryUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new DuplicateStoryUseCase instance.
        """
        return DuplicateStoryUseCase(uow)

    # Developer Use Case Factories
    def create_list_developers_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> ListDevelopersUseCase:
        """Create a ListDevelopersUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new ListDevelopersUseCase instance.
        """
        return ListDevelopersUseCase(uow)

    def create_developer_use_case_factory(
        self, uow: SQLiteUnitOfWork
    ) -> CreateDeveloperUseCase:
        """Create a CreateDeveloperUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CreateDeveloperUseCase instance.
        """
        return CreateDeveloperUseCase(uow)

    def create_update_developer_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> UpdateDeveloperUseCase:
        """Create an UpdateDeveloperUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new UpdateDeveloperUseCase instance.
        """
        return UpdateDeveloperUseCase(uow)

    def create_delete_developer_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> DeleteDeveloperUseCase:
        """Create a DeleteDeveloperUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new DeleteDeveloperUseCase instance.
        """
        return DeleteDeveloperUseCase(uow)

    # Feature Use Case Factories
    def create_list_features_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> ListFeaturesUseCase:
        """Create a ListFeaturesUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new ListFeaturesUseCase instance.
        """
        return ListFeaturesUseCase(uow)

    def create_feature_use_case_factory(
        self, uow: SQLiteUnitOfWork
    ) -> CreateFeatureUseCase:
        """Create a CreateFeatureUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CreateFeatureUseCase instance.
        """
        return CreateFeatureUseCase(uow)

    def create_update_feature_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> UpdateFeatureUseCase:
        """Create an UpdateFeatureUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new UpdateFeatureUseCase instance.
        """
        return UpdateFeatureUseCase(uow)

    def create_delete_feature_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> DeleteFeatureUseCase:
        """Create a DeleteFeatureUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new DeleteFeatureUseCase instance.
        """
        return DeleteFeatureUseCase(uow)

    # Dependency Use Case Factories
    def create_add_dependency_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> AddDependencyUseCase:
        """Create an AddDependencyUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new AddDependencyUseCase instance.
        """
        return AddDependencyUseCase(uow)

    def create_remove_dependency_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> RemoveDependencyUseCase:
        """Create a RemoveDependencyUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new RemoveDependencyUseCase instance.
        """
        return RemoveDependencyUseCase(uow)

    def create_get_dependencies_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> GetDependenciesUseCase:
        """Create a GetDependenciesUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new GetDependenciesUseCase instance.
        """
        return GetDependenciesUseCase(uow)

    def create_get_dependents_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> GetDependentsUseCase:
        """Create a GetDependentsUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new GetDependentsUseCase instance.
        """
        return GetDependentsUseCase(uow)

    # Allocation & Scheduling Use Case Factories
    def create_execute_allocation_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> ExecuteAllocationUseCase:
        """Create an ExecuteAllocationUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new ExecuteAllocationUseCase instance.
        """
        return ExecuteAllocationUseCase(uow)

    def create_calculate_schedule_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> CalculateScheduleUseCase:
        """Create a CalculateScheduleUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CalculateScheduleUseCase instance.
        """
        return CalculateScheduleUseCase(uow)

    def create_calculate_duration_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> CalculateDurationUseCase:
        """Create a CalculateDurationUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CalculateDurationUseCase instance.
        """
        return CalculateDurationUseCase(uow)

    def create_calculate_story_dates_use_case(
        self, uow: SQLiteUnitOfWork
    ) -> CalculateStoryDatesUseCase:
        """Create a CalculateStoryDatesUseCase instance.

        Args:
            uow: Unit of Work for repository access.

        Returns:
            A new CalculateStoryDatesUseCase instance.
        """
        return CalculateStoryDatesUseCase(uow)

    # ViewModels
    @property
    def main_window_viewmodel(self) -> MainWindowViewModel:
        """Get the MainWindowViewModel instance (lazy loaded)."""
        if self._main_window_viewmodel is None:
            from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
                MainWindowViewModel,
            )

            self._main_window_viewmodel = MainWindowViewModel(self)
        return self._main_window_viewmodel

    @property
    def story_dialog_viewmodel(self) -> StoryDialogViewModel:
        """Get the StoryDialogViewModel instance (lazy loaded)."""
        if self._story_dialog_viewmodel is None:
            from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
                StoryDialogViewModel,
            )

            self._story_dialog_viewmodel = StoryDialogViewModel(self)
        return self._story_dialog_viewmodel

    @property
    def allocation_viewmodel(self) -> AllocationViewModel:
        """Get the AllocationViewModel instance (lazy loaded)."""
        if self._allocation_viewmodel is None:
            from backlog_manager.presentation.viewmodels.allocation_viewmodel import (
                AllocationViewModel,
            )

            self._allocation_viewmodel = AllocationViewModel(self)
        return self._allocation_viewmodel
