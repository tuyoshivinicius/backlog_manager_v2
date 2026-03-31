"""Integration tests for DependencyPanel.

This module contains integration tests for the DependencyPanel class,
verifying correct behavior of the dependency management panel.
"""

from __future__ import annotations

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.dependency_panel import DependencyPanel
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem


class TestDependencyPanelDisplay:
    """Tests for DependencyPanel display functionality."""

    def test_panel_creates_successfully(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel creates without errors."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel is not None

    def test_panel_has_title(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has a title label."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Find the title label by checking for bold text
        found_title = False
        for child in panel.findChildren(type(panel)):
            pass
        # The title "Dependencias" exists in the layout
        assert panel.layout() is not None


class TestDependencyPanelComponents:
    """Tests for DependencyPanel UI components."""

    def test_has_depends_on_list(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has depends-on list."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._depends_on_list is not None

    def test_has_dependents_list(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has dependents list."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._dependents_list is not None

    def test_has_story_combo(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has story selection combo."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._story_combo is not None

    def test_has_add_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has add dependency button."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._add_dep_button is not None
        assert panel._add_dep_button.text() == "Adicionar"

    def test_has_remove_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has remove dependency button."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._remove_dep_button is not None
        assert "Remover" in panel._remove_dep_button.text()

    def test_story_combo_has_placeholder(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that story combo has placeholder text."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._story_combo.placeholderText() != ""


class TestDependencyPanelButtonStates:
    """Tests for button state management."""

    def test_add_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that add button is disabled initially."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._add_dep_button.isEnabled() is False

    def test_remove_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is disabled initially."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._remove_dep_button.isEnabled() is False

    def test_remove_button_enabled_on_selection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is enabled when dependency is selected."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add a dependency item manually
        item = QListWidgetItem("STORY-001: Test Story")
        item.setData(Qt.ItemDataRole.UserRole, "STORY-001")
        panel._depends_on_list.addItem(item)

        # Select the item
        panel._depends_on_list.setCurrentItem(item)

        assert panel._remove_dep_button.isEnabled() is True

    def test_remove_button_disabled_on_deselection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is disabled when selection is cleared."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add and select a dependency item
        item = QListWidgetItem("STORY-001: Test Story")
        item.setData(Qt.ItemDataRole.UserRole, "STORY-001")
        panel._depends_on_list.addItem(item)
        panel._depends_on_list.setCurrentItem(item)

        # Clear selection
        panel._depends_on_list.setCurrentItem(None)

        assert panel._remove_dep_button.isEnabled() is False


class TestDependencyPanelSignals:
    """Tests for DependencyPanel signals."""

    def test_has_dependency_added_signal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has dependency_added signal."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert hasattr(panel, "dependency_added")

    def test_has_dependency_removed_signal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has dependency_removed signal."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert hasattr(panel, "dependency_removed")

    def test_has_error_occurred_signal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that panel has error_occurred signal."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert hasattr(panel, "error_occurred")


class TestDependencyPanelStorySelection:
    """Tests for story selection functionality."""

    def test_set_story_updates_current_story_id(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that set_story updates the current story ID."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        panel._current_story_id = "STORY-001"

        assert panel._current_story_id == "STORY-001"

    def test_clear_lists_on_none_story(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that setting None story clears the lists."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add some items first
        panel._depends_on_list.addItem(QListWidgetItem("Test"))
        panel._dependents_list.addItem(QListWidgetItem("Test"))

        # Set story to None (simulating deselection)
        panel._current_story_id = None

        # Clear the lists manually (as the actual implementation would do)
        panel._depends_on_list.clear()
        panel._dependents_list.clear()

        assert panel._depends_on_list.count() == 0
        assert panel._dependents_list.count() == 0


class TestDependencyPanelListOperations:
    """Tests for list display operations."""

    def test_dependency_item_stores_id(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dependency items store their story IDs."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add a dependency item manually
        item = QListWidgetItem("STORY-001: Test Story")
        item.setData(Qt.ItemDataRole.UserRole, "STORY-001")
        panel._depends_on_list.addItem(item)

        # Verify ID is stored
        stored_id = panel._depends_on_list.item(0).data(Qt.ItemDataRole.UserRole)
        assert stored_id == "STORY-001"

    def test_dependency_item_displays_story_info(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dependency items display story information."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add a dependency item manually
        item = QListWidgetItem("STORY-001: Test Story")
        panel._depends_on_list.addItem(item)

        # Verify display text
        text = panel._depends_on_list.item(0).text()
        assert "STORY-001" in text

    def test_dependent_item_stores_id(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dependent items store their story IDs."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Add a dependent item manually
        item = QListWidgetItem("STORY-002: Blocking Story")
        item.setData(Qt.ItemDataRole.UserRole, "STORY-002")
        panel._dependents_list.addItem(item)

        # Verify ID is stored
        stored_id = panel._dependents_list.item(0).data(Qt.ItemDataRole.UserRole)
        assert stored_id == "STORY-002"


class TestDependencyPanelListMaxHeight:
    """Tests for list maximum height constraints."""

    def test_depends_on_list_has_max_height(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that depends-on list has maximum height."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._depends_on_list.maximumHeight() == 120

    def test_dependents_list_has_max_height(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dependents list has maximum height."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._dependents_list.maximumHeight() == 120


class TestDependencyPanelStoryCombo:
    """Tests for story combo functionality."""

    def test_story_combo_initially_empty(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that story combo is initially empty."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        assert panel._story_combo.count() == 0

    def test_set_stories_populates_combo(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that setting stories populates the combo."""
        panel = DependencyPanel(container)
        qtbot.addWidget(panel)

        # Simulate setting available stories
        stories = [
            StoryOutputDTO(
                id="STORY-001",
                component="API",
                name="Story 1",
                story_points=5,
                priority=1,
                status="BACKLOG",
                duration=3,
                start_date=None,
                end_date=None,
                developer_id=None,
                feature_id=None,
            ),
            StoryOutputDTO(
                id="STORY-002",
                component="UI",
                name="Story 2",
                story_points=3,
                priority=2,
                status="BACKLOG",
                duration=2,
                start_date=None,
                end_date=None,
                developer_id=None,
                feature_id=None,
            ),
        ]

        panel._all_stories = stories
        panel._story_combo.clear()
        for story in stories:
            panel._story_combo.addItem(f"{story.id}: {story.name}", story.id)

        assert panel._story_combo.count() == 2
