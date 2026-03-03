"""Integration tests for MainWindow.

This module contains integration tests for the MainWindow class,
verifying correct behavior with real database operations.
"""

from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
    MainWindowViewModel,
)
from backlog_manager.presentation.views.main_window import MainWindow


class TestMainWindowDisplay:
    """Tests for MainWindow display functionality."""

    def test_main_window_shows_with_correct_title(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that MainWindow displays with correct title."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window.windowTitle() == "Backlog Manager"

    def test_main_window_has_correct_initial_size(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that MainWindow has correct initial dimensions."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window.width() == 1280
        assert window.height() == 720

    def test_main_window_has_minimum_size(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that MainWindow has correct minimum dimensions."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window.minimumWidth() == 1024
        assert window.minimumHeight() == 600


class TestMainWindowToolbar:
    """Tests for MainWindow toolbar."""

    def test_toolbar_has_nova_historia_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Nova Historia action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_new_story is not None
        assert window._action_new_story.text() == "Nova Historia"

    def test_toolbar_has_editar_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Editar action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_edit_story is not None
        assert window._action_edit_story.text() == "Editar"

    def test_toolbar_has_deletar_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Deletar action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_delete_story is not None
        assert window._action_delete_story.text() == "Deletar"

    def test_toolbar_has_mover_cima_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Mover Cima action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_move_up is not None
        assert window._action_move_up.text() == "Mover Cima"

    def test_toolbar_has_mover_baixo_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Mover Baixo action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_move_down is not None
        assert window._action_move_down.text() == "Mover Baixo"

    def test_toolbar_has_alocar_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Alocar Automaticamente action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_allocate is not None
        assert window._action_allocate.text() == "Alocar Automaticamente"


class TestMainWindowTable:
    """Tests for MainWindow story table."""

    def test_table_has_correct_columns(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that table has correct column headers."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        model = window.story_table.model()
        assert model.columnCount() == 8

    def test_table_displays_stories(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that table displays stories from ViewModel."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window.story_table.model().rowCount() == 3


class TestMainWindowSelectionHandling:
    """Tests for story selection in MainWindow."""

    def test_selecting_row_updates_viewmodel(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that selecting a row updates the ViewModel."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select the first row
        index = window.story_table.model().index(0, 0)
        window.story_table.setCurrentIndex(index)

        # ViewModel should have the story selected
        assert viewmodel.selected_story_id == "COMP-001"


class TestMainWindowSignalHandling:
    """Tests for signal handling in MainWindow."""

    def test_loading_signal_changes_cursor(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that loading signal changes cursor."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Emit loading signal
        viewmodel.loading.emit(True)
        assert window.cursor().shape() == Qt.CursorShape.WaitCursor

        viewmodel.loading.emit(False)
        assert window.cursor().shape() == Qt.CursorShape.ArrowCursor

    def test_loading_signal_disables_allocate_button(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that loading signal disables allocate button."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_allocate.isEnabled()

        viewmodel.loading.emit(True)
        assert not window._action_allocate.isEnabled()

        viewmodel.loading.emit(False)
        assert window._action_allocate.isEnabled()


class TestMainWindowPriorityActions:
    """Tests for priority move actions in MainWindow."""

    @pytest.mark.asyncio
    async def test_move_up_calls_viewmodel(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that move up action calls ViewModel."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories
        viewmodel.select_story("COMP-001")

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch.object(
            viewmodel, "move_priority_up", new_callable=AsyncMock
        ) as mock_move:
            window._on_move_up()
            # Allow async task to be created
            await asyncio.sleep(0.1)
            mock_move.assert_called_once_with("COMP-001")

    @pytest.mark.asyncio
    async def test_move_down_calls_viewmodel(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that move down action calls ViewModel."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories
        viewmodel.select_story("COMP-001")

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch.object(
            viewmodel, "move_priority_down", new_callable=AsyncMock
        ) as mock_move:
            window._on_move_down()
            # Allow async task to be created
            await asyncio.sleep(0.1)
            mock_move.assert_called_once_with("COMP-001")

    def test_move_up_does_nothing_without_selection(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that move up does nothing without selection."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Should not raise
        window._on_move_up()

    def test_move_down_does_nothing_without_selection(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that move down does nothing without selection."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Should not raise
        window._on_move_down()
