"""Integration tests for MainWindow.

This module contains integration tests for the MainWindow class,
verifying correct behavior with the new 5-zone vertical layout (EP-018).
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
from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QToolBar, QVBoxLayout

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


class TestMainWindowVerticalLayout:
    """Tests for the 5-zone vertical layout (EP-018 US2)."""

    def test_central_widget_uses_vbox_layout(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that central widget uses QVBoxLayout."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        central = window.centralWidget()
        assert central is not None
        layout = central.layout()
        assert isinstance(layout, QVBoxLayout)

    def test_no_splitter_in_layout(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that QSplitter is no longer used."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert not hasattr(window, "_splitter")

    def test_no_side_panels(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that legacy side panels are not instantiated."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert not hasattr(window, "_config_panel")
        assert not hasattr(window, "_dependency_panel")
        assert not hasattr(window, "_metrics_panel")
        assert not hasattr(window, "_warnings_panel")
        assert not hasattr(window, "_side_panel")

    def test_filter_bar_placeholder_exists(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that filter bar placeholder is present with correct height."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert hasattr(window, "_filter_bar")
        assert window._filter_bar.maximumHeight() == 36

    def test_story_table_in_central_layout(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that story table is in the central layout."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._story_table is not None
        assert window._story_table.model() is not None


class TestMainWindowMenuBar:
    """Tests for the Menu Bar (EP-018 US1)."""

    def test_menu_bar_has_four_menus(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that menu bar has 4 menus."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        menu_bar = window.menuBar()
        actions = [a for a in menu_bar.actions() if a.menu()]
        assert len(actions) == 4

    def test_menu_bar_menu_names(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that menus have correct names."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        menu_bar = window.menuBar()
        menu_names = [a.text() for a in menu_bar.actions() if a.menu()]
        assert "&Arquivo" in menu_names
        assert "&Cadastros" in menu_names
        assert "&Ferramentas" in menu_names
        assert "A&juda" in menu_names


class TestMainWindowToolbar:
    """Tests for MainWindow toolbar with icons and groups."""

    def test_toolbar_has_nova_action(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar has Nova action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_new_story is not None
        assert window._action_new_story.text() == "Nova"

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
        """Test that toolbar has Alocar action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_allocate is not None
        assert window._action_allocate.text() == "Alocar"

    def test_toolbar_uses_text_beside_icon_style(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar uses ToolButtonTextBesideIcon style."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        toolbars = window.findChildren(QToolBar)
        assert len(toolbars) >= 1
        assert (
            toolbars[0].toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )

    def test_toolbar_icon_size(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that toolbar icon size is 20x20."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        toolbars = window.findChildren(QToolBar)
        assert toolbars[0].iconSize().width() == 20
        assert toolbars[0].iconSize().height() == 20


class TestMainWindowStatusBar:
    """Tests for Status Bar (EP-018 US4)."""

    def test_status_bar_has_stats_label(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that status bar has stats label."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert hasattr(window, "_stats_label")
        assert isinstance(window._stats_label, QLabel)
        assert "0 historias" in window._stats_label.text()

    def test_status_bar_has_warnings_badge(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that status bar has warnings badge (hidden by default)."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert hasattr(window, "_warnings_badge")
        assert isinstance(window._warnings_badge, QPushButton)
        assert not window._warnings_badge.isVisible()

    def test_warnings_badge_visible_when_warnings(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that warnings badge becomes visible when warnings arrive."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        window._on_warnings_updated(["Warning 1", "Warning 2"])
        assert window._warnings_badge.isVisible()
        assert "2 avisos" in window._warnings_badge.text()

    def test_warnings_badge_hidden_when_no_warnings(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that warnings badge is hidden when warnings are cleared."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()
        qtbot.waitExposed(window)

        window._on_warnings_updated(["Warning 1"])
        assert window._warnings_badge.isVisible()

        window._on_warnings_updated([])
        assert not window._warnings_badge.isVisible()


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
        assert model.columnCount() == 13

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

    def test_table_has_context_menu_policy(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that table has custom context menu policy."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert (
            window._story_table.contextMenuPolicy()
            == Qt.ContextMenuPolicy.CustomContextMenu
        )


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


class TestMainWindowSelectionHighlight:
    """Tests for table selection highlight feature (EP-025)."""

    def test_click_row_highlights_and_click_another_moves(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test click row → highlight; click another → highlight moves."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select first row
        index0 = window.story_table.model().index(0, 0)
        window.story_table.setCurrentIndex(index0)
        assert viewmodel.selected_story_id == "COMP-001"

        # Select second row — highlight moves
        index1 = window.story_table.model().index(1, 0)
        window.story_table.setCurrentIndex(index1)
        assert viewmodel.selected_story_id == "COMP-002"

    def test_actions_disabled_when_no_selection(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that edit/delete/move actions are disabled when no selection."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Initially no selection — actions should be disabled
        assert not window._action_edit_story.isEnabled()
        assert not window._action_delete_story.isEnabled()
        assert not window._action_move_up.isEnabled()
        assert not window._action_move_down.isEnabled()

    def test_actions_enabled_after_selection(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that edit/delete actions are enabled after selecting a row."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select a row
        index0 = window.story_table.model().index(0, 0)
        window.story_table.setCurrentIndex(index0)

        assert window._action_edit_story.isEnabled()
        assert window._action_delete_story.isEnabled()

    def test_selection_follows_story_after_move(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test selection persists after stories are refreshed (move simulation)."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select second row
        index1 = window.story_table.model().index(1, 0)
        window.story_table.setCurrentIndex(index1)
        assert viewmodel.selected_story_id == "COMP-002"

        # Simulate move: reorder stories and refresh
        reordered = [sample_stories[1], sample_stories[0], sample_stories[2]]
        viewmodel._table_model.set_stories(reordered)
        viewmodel._stories = reordered
        viewmodel.stories_changed.emit()

        # Selection should be restored to COMP-002's new position (row 0)
        current = window.story_table.currentIndex()
        story_id = window.story_table.model().data(
            window.story_table.model().index(current.row(), 0),
            Qt.ItemDataRole.UserRole,
        )
        assert story_id == "COMP-002"

    def test_selection_moves_to_adjacent_after_delete(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test selection moves to adjacent row after story is deleted."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select first row
        index0 = window.story_table.model().index(0, 0)
        window.story_table.setCurrentIndex(index0)
        assert viewmodel.selected_story_id == "COMP-001"

        # Simulate delete of first story: refresh with remaining stories
        remaining = [sample_stories[1], sample_stories[2]]
        viewmodel._selected_story_id = "COMP-002"  # Adjacent story
        viewmodel._table_model.set_stories(remaining)
        viewmodel._stories = remaining
        viewmodel.stories_changed.emit()

        # Selection should move to first remaining row
        current = window.story_table.currentIndex()
        assert current.isValid()
        story_id = window.story_table.model().data(
            window.story_table.model().index(current.row(), 0),
            Qt.ItemDataRole.UserRole,
        )
        assert story_id == "COMP-002"

    def test_selection_clears_when_table_empty(
        self, container: DIContainer, sample_stories: list[StoryOutputDTO], qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test selection clears when table becomes empty after delete."""
        viewmodel = MainWindowViewModel(container)
        viewmodel._table_model.set_stories(sample_stories)
        viewmodel._stories = sample_stories

        window = MainWindow(viewmodel)
        qtbot.addWidget(window)
        window.show()

        # Select a row
        index0 = window.story_table.model().index(0, 0)
        window.story_table.setCurrentIndex(index0)

        # Empty the table
        viewmodel._selected_story_id = None
        viewmodel._table_model.set_stories([])
        viewmodel._stories = []
        viewmodel.stories_changed.emit()

        assert viewmodel.selected_story_id is None


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
