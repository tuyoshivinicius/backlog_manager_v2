"""Test Story entity."""

from datetime import date

import pytest

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@pytest.mark.unit
class TestStory:
    """Test Story entity creation and validation."""

    def test_valid_story_creation(self) -> None:
        """Test creating a valid story."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Implement login",
            story_points=StoryPoint.MEDIUM,
            priority=0,
        )

        assert story.id == "AUTH-001"
        assert story.component == "AUTH"
        assert story.name == "Implement login"
        assert story.story_points == StoryPoint.MEDIUM
        assert story.priority == 0
        assert story.status == StoryStatus.BACKLOG

    def test_story_with_all_fields(self) -> None:
        """Test creating a story with all optional fields."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Implement login",
            story_points=StoryPoint.LARGE,
            priority=1,
            status=StoryStatus.IN_PROGRESS,
            duration=5,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 10),
            developer_id=1,
            feature_id=1,
        )

        assert story.duration == 5
        assert story.start_date == date(2026, 1, 1)
        assert story.end_date == date(2026, 1, 10)
        assert story.developer_id == 1
        assert story.feature_id == 1

    def test_story_with_integer_story_points(self) -> None:
        """Test story accepts integer story points and converts to enum."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=5,  # type: ignore
            priority=0,
        )

        assert story.story_points == StoryPoint.MEDIUM

    def test_empty_id_raises_error(self) -> None:
        """Test empty ID raises ValueError."""
        with pytest.raises(ValueError, match="ID da historia nao pode ser vazio"):
            Story(
                id="",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_whitespace_id_raises_error(self) -> None:
        """Test whitespace-only ID raises ValueError."""
        with pytest.raises(ValueError, match="ID da historia nao pode ser vazio"):
            Story(
                id="   ",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_invalid_id_format_raises_error(self) -> None:
        """Test invalid ID format raises ValueError."""
        with pytest.raises(ValueError, match="ID deve seguir padrao COMPONENTE-NNN"):
            Story(
                id="INVALID",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_invalid_id_lowercase_raises_error(self) -> None:
        """Test lowercase ID raises ValueError."""
        with pytest.raises(ValueError, match="ID deve seguir padrao COMPONENTE-NNN"):
            Story(
                id="auth-001",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_empty_component_raises_error(self) -> None:
        """Test empty component raises ValueError."""
        with pytest.raises(ValueError, match="Componente nao pode ser vazio"):
            Story(
                id="AUTH-001",
                component="",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_long_component_raises_error(self) -> None:
        """Test component over 50 chars raises ValueError."""
        with pytest.raises(ValueError, match="Componente nao pode exceder 50"):
            Story(
                id="AUTH-001",
                component="A" * 51,
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_empty_name_raises_error(self) -> None:
        """Test empty name raises ValueError."""
        with pytest.raises(ValueError, match="Nome da historia nao pode ser vazio"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_long_name_raises_error(self) -> None:
        """Test name over 200 chars raises ValueError."""
        with pytest.raises(ValueError, match="Nome da historia nao pode exceder 200"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="A" * 201,
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_invalid_story_points_raises_error(self) -> None:
        """Test invalid story points raises ValueError."""
        with pytest.raises(ValueError, match="Story points deve ser 3, 5, 8 ou 13"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="Test",
                story_points=7,  # type: ignore
                priority=0,
            )

    def test_negative_priority_raises_error(self) -> None:
        """Test negative priority raises ValueError."""
        with pytest.raises(ValueError, match="Prioridade deve ser >= 0"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=-1,
            )

    def test_start_after_end_raises_error(self) -> None:
        """Test start_date after end_date raises ValueError."""
        with pytest.raises(
            ValueError, match="Data de inicio nao pode ser posterior"
        ):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
                start_date=date(2026, 1, 10),
                end_date=date(2026, 1, 1),
            )

    def test_valid_dates(self) -> None:
        """Test valid date range is accepted."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 10),
        )

        assert story.start_date == date(2026, 1, 1)
        assert story.end_date == date(2026, 1, 10)

    def test_same_start_end_date(self) -> None:
        """Test same start and end date is valid."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 1),
        )

        assert story.start_date == story.end_date
