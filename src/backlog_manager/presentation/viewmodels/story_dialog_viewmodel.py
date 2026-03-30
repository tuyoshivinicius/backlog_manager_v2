"""Story Dialog ViewModel.

This module provides the ViewModel for the story creation/edit dialog,
handling validation and use case execution.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Literal, Sequence

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.developer import DeveloperOutputDTO
from backlog_manager.application.dto.feature import FeatureOutputDTO
from backlog_manager.application.dto.story import (
    CreateStoryInputDTO,
    EditStoryInputDTO,
    StoryOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)

# Valid story points (Fibonacci)
VALID_STORY_POINTS = [3, 5, 8, 13]


class StoryDialogViewModel(QObject):
    """ViewModel for story creation/edit dialog.

    Manages form state, validation, and persistence operations for
    creating and editing stories.

    Signals:
        saved: Emitted when story is saved successfully.
        error_occurred: Emitted when an error occurs (payload: error_message).
        features_loaded: Emitted when features are loaded.
    """

    # Signals as per contracts/viewmodel-signals.md
    saved = Signal()
    error_occurred = Signal(str)
    features_loaded = Signal(list)
    developers_loaded = Signal(list)

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container

        # Form state
        self._mode: Literal["create", "edit"] = "create"
        self._story_id: str | None = None
        self._component: str = ""
        self._name: str = ""
        self._story_points: int = 5
        self._feature_id: int | None = None
        self._developer_id: int | None = None

        # Available features and developers for dropdowns
        self._features: list[FeatureOutputDTO] = []
        self._developers: list[DeveloperOutputDTO] = []

        logger.debug("StoryDialogViewModel initialized")

    # Properties for form binding
    @property
    def mode(self) -> Literal["create", "edit"]:
        """Get the current dialog mode."""
        return self._mode

    @property
    def story_id(self) -> str | None:
        """Get the story ID (edit mode only)."""
        return self._story_id

    @property
    def component(self) -> str:
        """Get the component value."""
        return self._component

    @component.setter
    def component(self, value: str) -> None:
        """Set the component value."""
        self._component = value.strip().upper()

    @property
    def name(self) -> str:
        """Get the name value."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name value."""
        self._name = value.strip()

    @property
    def story_points(self) -> int:
        """Get the story points value."""
        return self._story_points

    @story_points.setter
    def story_points(self, value: int) -> None:
        """Set the story points value."""
        if value in VALID_STORY_POINTS:
            self._story_points = value

    @property
    def feature_id(self) -> int | None:
        """Get the feature ID."""
        return self._feature_id

    @feature_id.setter
    def feature_id(self, value: int | None) -> None:
        """Set the feature ID."""
        self._feature_id = value

    @property
    def developer_id(self) -> int | None:
        """Get the developer ID."""
        return self._developer_id

    @developer_id.setter
    def developer_id(self, value: int | None) -> None:
        """Set the developer ID."""
        self._developer_id = value

    @property
    def developers(self) -> list[DeveloperOutputDTO]:
        """Get the available developers."""
        return self._developers.copy()

    @property
    def features(self) -> list[FeatureOutputDTO]:
        """Get the available features."""
        return self._features.copy()

    def set_mode(self, mode: Literal["create", "edit"]) -> None:
        """Set the dialog mode.

        Args:
            mode: Either "create" or "edit".
        """
        self._mode = mode
        if mode == "create":
            self._reset_form()
        logger.debug("Mode set to: %s", mode)

    def set_story(self, story: StoryOutputDTO) -> None:
        """Set form values from an existing story (for edit mode).

        Args:
            story: The story to edit.
        """
        self._story_id = story.id
        self._component = story.component
        self._name = story.name
        self._story_points = story.story_points
        self._feature_id = story.feature_id
        self._developer_id = story.developer_id
        self._mode = "edit"
        logger.debug("Story set for editing: %s", story.id)

    def _reset_form(self) -> None:
        """Reset form to initial state."""
        self._story_id = None
        self._component = ""
        self._name = ""
        self._story_points = 5
        self._feature_id = None
        self._developer_id = None

    def validate_field(self, field_name: str) -> tuple[bool, str]:
        """Valida um campo individual.

        Args:
            field_name: Nome do campo ("component" ou "name").

        Returns:
            Tupla (is_valid, error_message). Para campos desconhecidos,
            retorna (True, "").
        """
        if field_name == "component":
            if not self._component:
                return False, "Campo obrigatorio"
            if len(self._component) > 50:
                return False, "Maximo de 50 caracteres"
        elif field_name == "name":
            if not self._name:
                return False, "Campo obrigatorio"
            if len(self._name) > 200:
                return False, "Maximo de 200 caracteres"
        return True, ""

    def validate(self) -> tuple[bool, str]:
        """Validate the current form values.

        Returns:
            Tuple of (is_valid, error_message).
        """
        # Validate component
        if not self._component:
            return False, "Componente e obrigatorio."
        if len(self._component) > 50:
            return False, "Componente deve ter no maximo 50 caracteres."

        # Validate name
        if not self._name:
            return False, "Nome e obrigatorio."
        if len(self._name) > 200:
            return False, "Nome deve ter no maximo 200 caracteres."

        # Validate story points
        if self._story_points not in VALID_STORY_POINTS:
            return False, f"Story Points deve ser um de: {VALID_STORY_POINTS}."

        return True, ""

    async def load_developers(self) -> None:
        """Load available developers for the dropdown."""
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_developers_use_case(uow)
                result = await use_case.execute()
                self._developers = list(result.developers)
                self.developers_loaded.emit(self._developers)
                logger.debug("Loaded %d developers", len(self._developers))
        except Exception as e:
            logger.exception("Error loading developers")
            self.error_occurred.emit(f"Erro ao carregar desenvolvedores: {e}")

    async def load_features(self) -> None:
        """Load available features for the dropdown."""
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_list_features_use_case(uow)
                result = await use_case.execute()
                self._features = list(result.features)
                self.features_loaded.emit(self._features)
                logger.debug("Loaded %d features", len(self._features))
        except Exception as e:
            logger.exception("Error loading features")
            self.error_occurred.emit(f"Erro ao carregar features: {e}")

    async def save(self) -> StoryOutputDTO | None:
        """Save the story (create or edit).

        Returns:
            Created/edited story DTO on success, None on failure.
        """
        # Validate first
        is_valid, error_message = self.validate()
        if not is_valid:
            self.error_occurred.emit(error_message)
            return None

        try:
            if self._mode == "create":
                return await self._create_story()
            else:
                return await self._edit_story()
        except BacklogManagerException as e:
            self.error_occurred.emit(str(e))
            return None
        except Exception as e:
            logger.exception("Error saving story")
            self.error_occurred.emit(f"Erro inesperado: {e}")
            return None

    async def _create_story(self) -> StoryOutputDTO:
        """Create a new story.

        Returns:
            Created story DTO.
        """
        dto = CreateStoryInputDTO(
            component=self._component,
            name=self._name,
            story_points=self._story_points,
            feature_id=self._feature_id,
        )

        async with self._container.create_unit_of_work() as uow:
            use_case = self._container.create_story_use_case_factory(uow)
            story = await use_case.execute(dto)
            self.saved.emit()
            logger.info("Created story: %s", story.id)
            return story

    async def _edit_story(self) -> StoryOutputDTO:
        """Edit an existing story.

        Returns:
            Edited story DTO.

        Raises:
            ValueError: If no story ID is set.
        """
        if not self._story_id:
            raise ValueError("Nenhuma historia selecionada para edicao.")

        dto = EditStoryInputDTO(
            story_id=self._story_id,
            name=self._name,
            story_points=self._story_points,
            feature_id=self._feature_id,
            developer_id=self._developer_id,
        )

        async with self._container.create_unit_of_work() as uow:
            use_case = self._container.create_edit_story_use_case(uow)
            story = await use_case.execute(dto)
            self.saved.emit()
            logger.info("Edited story: %s", story.id)
            return story
