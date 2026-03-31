"""Unit tests for GetDeveloperAvailabilityUseCase."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from backlog_manager.application.dto.allocation.get_developer_availability_dto import (
    GetDeveloperAvailabilityInputDTO,
)
from backlog_manager.application.use_cases.allocation.get_developer_availability import (
    GetDeveloperAvailabilityUseCase,
)
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


def _make_story(
    story_id: str = "TEST-001",
    *,
    priority: int = 1,
    start_date: date | None = None,
    end_date: date | None = None,
    developer_id: int | None = None,
    status: StoryStatus = StoryStatus.BACKLOG,
) -> Story:
    return Story(
        id=story_id,
        component=story_id.split("-")[0],
        name=f"Historia {story_id}",
        story_points=StoryPoint(5),
        priority=priority,
        status=status,
        duration=3,
        start_date=start_date,
        end_date=end_date,
        developer_id=developer_id,
    )


def _make_input(
    story_id: str = "TEST-001", start: date | None = None
) -> GetDeveloperAvailabilityInputDTO:
    return GetDeveloperAvailabilityInputDTO(
        story_id=story_id,
        candidate_start_date=start or date(2026, 4, 1),
        velocity=2.0,
        allocation_criteria="LOAD_BALANCING",
    )


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.stories = MagicMock()
    uow.developers = MagicMock()
    uow.dependencies = MagicMock()
    uow.stories.get_by_id = AsyncMock()
    uow.stories.get_all = AsyncMock(return_value=[])
    uow.developers.get_all = AsyncMock(return_value=[])
    uow.dependencies.get_all_dependencies = AsyncMock(return_value=[])

    # Context manager support
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    return uow


@pytest.mark.asyncio
async def test_story_not_found(mock_uow):
    """Deve lançar ValueError se historia nao encontrada."""
    mock_uow.stories.get_by_id.return_value = None
    use_case = GetDeveloperAvailabilityUseCase(mock_uow)

    with pytest.raises(ValueError, match="nao encontrada"):
        await use_case.execute(_make_input())


@pytest.mark.asyncio
async def test_story_without_story_points(mock_uow):
    """Deve lançar ValueError se historia sem story points."""
    story = _make_story()
    object.__setattr__(story, "story_points", None)
    mock_uow.stories.get_by_id.return_value = story
    use_case = GetDeveloperAvailabilityUseCase(mock_uow)

    with pytest.raises(ValueError, match="sem story points"):
        await use_case.execute(_make_input())


@pytest.mark.asyncio
async def test_no_developers(mock_uow):
    """Deve retornar lista vazia se nao ha desenvolvedores."""
    story = _make_story(start_date=date(2026, 4, 1), end_date=date(2026, 4, 3))
    mock_uow.stories.get_by_id.return_value = story
    mock_uow.stories.get_all.return_value = [story]
    mock_uow.developers.get_all.return_value = []

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input())

    assert len(result.developers) == 0
    assert result.recommended_developer_id is None


@pytest.mark.asyncio
async def test_all_developers_free(mock_uow):
    """Deve classificar todos como livres se nenhum tem overlap."""
    story = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )
    dev1 = Developer(id=1, name="Ana Silva")
    dev2 = Developer(id=2, name="Carlos Santos")

    mock_uow.stories.get_by_id.return_value = story
    mock_uow.stories.get_all.return_value = [story]
    mock_uow.developers.get_all.return_value = [dev1, dev2]

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001"))

    assert len(result.developers) == 2
    assert all(d.is_available for d in result.developers)
    assert result.recommended_developer_id is not None


@pytest.mark.asyncio
async def test_developer_busy_with_overlap(mock_uow):
    """Deve classificar dev como ocupado se tem historia com overlap."""
    target = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )
    # Dev1 has overlapping story
    blocking = _make_story(
        "PROJ-002",
        start_date=date(2026, 4, 2),
        end_date=date(2026, 4, 5),
        developer_id=1,
    )
    dev1 = Developer(id=1, name="Joao Pereira")
    dev2 = Developer(id=2, name="Ana Silva")

    mock_uow.stories.get_by_id.return_value = target
    mock_uow.stories.get_all.return_value = [target, blocking]
    mock_uow.developers.get_all.return_value = [dev1, dev2]

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001"))

    busy_devs = [d for d in result.developers if not d.is_available]
    free_devs = [d for d in result.developers if d.is_available]

    assert len(busy_devs) == 1
    assert busy_devs[0].developer_name == "Joao Pereira"
    assert len(busy_devs[0].blocking_stories) == 1
    assert busy_devs[0].blocking_stories[0].story_id == "PROJ-002"

    assert len(free_devs) == 1
    assert free_devs[0].developer_name == "Ana Silva"


@pytest.mark.asyncio
async def test_recommendation_goes_to_free_dev(mock_uow):
    """Recomendacao deve ser para um dev livre."""
    target = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )
    dev1 = Developer(id=1, name="Ana")
    dev2 = Developer(id=2, name="Carlos")

    mock_uow.stories.get_by_id.return_value = target
    mock_uow.stories.get_all.return_value = [target]
    mock_uow.developers.get_all.return_value = [dev1, dev2]

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001"))

    recommended = [d for d in result.developers if d.is_recommended]
    assert len(recommended) == 1
    assert recommended[0].is_available is True
    assert result.recommended_developer_id == recommended[0].developer_id


@pytest.mark.asyncio
async def test_free_devs_sorted_first(mock_uow):
    """Devs livres devem aparecer antes dos ocupados."""
    target = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )
    blocking = _make_story(
        "PROJ-002",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 5),
        developer_id=1,
    )
    dev1 = Developer(id=1, name="Ocupado")
    dev2 = Developer(id=2, name="Livre")

    mock_uow.stories.get_by_id.return_value = target
    mock_uow.stories.get_all.return_value = [target, blocking]
    mock_uow.developers.get_all.return_value = [dev1, dev2]

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001"))

    assert result.developers[0].is_available is True
    assert result.developers[1].is_available is False


@pytest.mark.asyncio
async def test_concluido_stories_dont_block(mock_uow):
    """Historias com status CONCLUIDO nao devem bloquear dev."""
    target = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )
    completed = _make_story(
        "PROJ-002",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 5),
        developer_id=1,
        status=StoryStatus.CONCLUIDO,
    )
    dev1 = Developer(id=1, name="Dev")

    mock_uow.stories.get_by_id.return_value = target
    mock_uow.stories.get_all.return_value = [target, completed]
    mock_uow.developers.get_all.return_value = [dev1]

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001"))

    assert len(result.developers) == 1
    assert result.developers[0].is_available is True


@pytest.mark.asyncio
async def test_recalculated_dates_returned(mock_uow):
    """Deve retornar datas recalculadas no output."""
    target = _make_story(
        "PROJ-001",
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 3),
    )

    mock_uow.stories.get_by_id.return_value = target
    mock_uow.stories.get_all.return_value = [target]
    mock_uow.developers.get_all.return_value = []

    use_case = GetDeveloperAvailabilityUseCase(mock_uow)
    result = await use_case.execute(_make_input("PROJ-001", start=date(2026, 4, 1)))

    assert result.story_start_date is not None
    assert result.story_end_date is not None
    assert result.story_end_date >= result.story_start_date
