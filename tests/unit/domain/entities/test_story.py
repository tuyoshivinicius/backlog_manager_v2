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
            status=StoryStatus.EXECUCAO,
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
        with pytest.raises(ValueError, match="Data de inicio nao pode ser posterior"):
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

    # US1 - Additional Story Points tests
    def test_story_points_value_3_valid(self) -> None:
        """Story points 3 deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=3,  # type: ignore
            priority=0,
        )
        assert story.story_points == StoryPoint.SMALL

    def test_story_points_value_8_valid(self) -> None:
        """Story points 8 deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=8,  # type: ignore
            priority=0,
        )
        assert story.story_points == StoryPoint.LARGE

    def test_story_points_value_13_valid(self) -> None:
        """Story points 13 deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=13,  # type: ignore
            priority=0,
        )
        assert story.story_points == StoryPoint.EXTRA_LARGE

    def test_story_points_invalid_values(self) -> None:
        """Valores invalidos de story points devem lancar ValueError."""
        invalid_values = [1, 2, 4, 7, 10, 20]
        for value in invalid_values:
            with pytest.raises(ValueError, match="Story points deve ser 3, 5, 8 ou 13"):
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Test",
                    story_points=value,  # type: ignore
                    priority=0,
                )

    # US2 - Status tests
    def test_default_status_is_backlog(self) -> None:
        """Status padrao deve ser BACKLOG."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
        )
        assert story.status == StoryStatus.BACKLOG

    def test_status_execucao_valid(self) -> None:
        """Status EXECUCAO deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            status=StoryStatus.EXECUCAO,
        )
        assert story.status == StoryStatus.EXECUCAO

    def test_status_testes_valid(self) -> None:
        """Status TESTES deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            status=StoryStatus.TESTES,
        )
        assert story.status == StoryStatus.TESTES

    def test_status_concluido_valid(self) -> None:
        """Status CONCLUIDO deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            status=StoryStatus.CONCLUIDO,
        )
        assert story.status == StoryStatus.CONCLUIDO

    def test_status_impedido_valid(self) -> None:
        """Status IMPEDIDO deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            status=StoryStatus.IMPEDIDO,
        )
        assert story.status == StoryStatus.IMPEDIDO

    # US3 - Additional Invariant tests
    def test_max_component_length_valid(self) -> None:
        """Component com exatamente 50 chars deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="A" * 50,
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
        )
        assert len(story.component) == 50

    def test_max_name_length_valid(self) -> None:
        """Name com exatamente 200 chars deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="A" * 200,
            story_points=StoryPoint.SMALL,
            priority=0,
        )
        assert len(story.name) == 200

    def test_whitespace_component_raises_error(self) -> None:
        """Component com apenas espacos deve lancar ValueError."""
        with pytest.raises(ValueError, match="Componente nao pode ser vazio"):
            Story(
                id="AUTH-001",
                component="   ",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_whitespace_name_raises_error(self) -> None:
        """Name com apenas espacos deve lancar ValueError."""
        with pytest.raises(ValueError, match="Nome da historia nao pode ser vazio"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="   ",
                story_points=StoryPoint.SMALL,
                priority=0,
            )

    def test_priority_zero_valid(self) -> None:
        """Prioridade zero deve ser valida."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
        )
        assert story.priority == 0

    def test_priority_positive_valid(self) -> None:
        """Prioridade positiva deve ser valida."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=100,
        )
        assert story.priority == 100

    # US4 - Duration validation tests
    def test_duration_none_valid(self) -> None:
        """Duration None deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            duration=None,
        )
        assert story.duration is None

    def test_duration_zero_valid(self) -> None:
        """Duration 0 deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            duration=0,
        )
        assert story.duration == 0

    def test_duration_positive_valid(self) -> None:
        """Duration positivo deve ser valido."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Test",
            story_points=StoryPoint.SMALL,
            priority=0,
            duration=3,
        )
        assert story.duration == 3

    def test_duration_negative_raises_error(self) -> None:
        """Duration negativo deve lancar ValueError."""
        with pytest.raises(ValueError, match="Duracao deve ser >= 0"):
            Story(
                id="AUTH-001",
                component="AUTH",
                name="Test",
                story_points=StoryPoint.SMALL,
                priority=0,
                duration=-1,
            )
