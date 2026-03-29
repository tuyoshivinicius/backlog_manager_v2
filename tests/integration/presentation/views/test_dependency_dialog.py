"""Integration tests for DependencyDialog."""

from __future__ import annotations

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.dependency_dialog import DependencyDialog


def _make_stories() -> list[StoryOutputDTO]:
    """Create sample stories for testing."""
    return [
        StoryOutputDTO(
            id="S1",
            component="COMP",
            name="Story 1",
            story_points=3,
            status="BACKLOG",
            priority=1,
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        ),
        StoryOutputDTO(
            id="S2",
            component="COMP",
            name="Story 2",
            story_points=5,
            status="BACKLOG",
            priority=2,
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        ),
        StoryOutputDTO(
            id="S3",
            component="COMP",
            name="Story 3",
            story_points=2,
            status="BACKLOG",
            priority=3,
            duration=None,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        ),
    ]


class TestDependencyDialogDisplay:
    """Tests for DependencyDialog display."""

    def test_dialog_title_contains_story_id(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test dialog title contains story ID and name."""
        stories = _make_stories()
        dialog = DependencyDialog(container, "S1", "Story 1", stories)
        qtbot.addWidget(dialog)

        assert "S1" in dialog.windowTitle()
        assert "Story 1" in dialog.windowTitle()

    def test_dialog_fixed_size(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test dialog has fixed size 500x420."""
        stories = _make_stories()
        dialog = DependencyDialog(container, "S1", "Story 1", stories)
        qtbot.addWidget(dialog)

        assert dialog.width() == 500
        assert dialog.height() == 420

    def test_dialog_is_modal(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test dialog is modal."""
        stories = _make_stories()
        dialog = DependencyDialog(container, "S1", "Story 1", stories)
        qtbot.addWidget(dialog)

        assert dialog.isModal()

    def test_combo_excludes_current_story(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that combo box excludes the current story."""
        stories = _make_stories()
        dialog = DependencyDialog(container, "S1", "Story 1", stories)
        qtbot.addWidget(dialog)

        # Combo should have placeholder + S2 + S3 (not S1)
        combo_items = [
            dialog._story_combo.itemText(i) for i in range(dialog._story_combo.count())
        ]
        assert not any("S1:" in item for item in combo_items)
        assert any("S2:" in item for item in combo_items)
        assert any("S3:" in item for item in combo_items)

    def test_cycle_error_banner_hidden_initially(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that cycle error banner is hidden initially."""
        stories = _make_stories()
        dialog = DependencyDialog(container, "S1", "Story 1", stories)
        qtbot.addWidget(dialog)

        assert not dialog._error_banner.isVisible()
