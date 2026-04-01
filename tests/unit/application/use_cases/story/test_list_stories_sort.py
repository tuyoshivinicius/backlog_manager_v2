"""Unit tests for ListStoriesUseCase._sort_dtos ordering logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.application.use_cases.story.list_stories import ListStoriesUseCase
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.entities.story import Story


def _make_dto(
    id: str,
    wave: int = 0,
    priority: int = 0,
    dependency_ids: list[str] | None = None,
) -> StoryOutputDTO:
    """Helper to create a StoryOutputDTO for testing."""
    return StoryOutputDTO(
        id=id,
        component="COMP",
        name=f"Story {id}",
        story_points=5,
        priority=priority,
        status="BACKLOG",
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
        wave=wave,
        dependency_ids=dependency_ids or [],
    )


class TestSortDtos:
    """Tests for ListStoriesUseCase._sort_dtos."""

    def test_empty_list(self):
        result = ListStoriesUseCase._sort_dtos([])
        assert result == []

    def test_single_story(self):
        dto = _make_dto("A-001", wave=1, priority=5)
        result = ListStoriesUseCase._sort_dtos([dto])
        assert [d.id for d in result] == ["A-001"]

    def test_wave_ordering(self):
        """Stories in lower waves come before higher waves."""
        dtos = [
            _make_dto("A-001", wave=2, priority=0),
            _make_dto("A-002", wave=0, priority=5),
            _make_dto("A-003", wave=1, priority=0),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["A-002", "A-003", "A-001"]

    def test_priority_tiebreaker_within_wave(self):
        """Within same wave and no deps, lower priority value comes first."""
        dtos = [
            _make_dto("A-003", wave=1, priority=10),
            _make_dto("A-001", wave=1, priority=1),
            _make_dto("A-002", wave=1, priority=5),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["A-001", "A-002", "A-003"]

    def test_dependency_ordering_within_wave(self):
        """B depends on A, both in same wave -> A comes first."""
        dtos = [
            _make_dto("B-001", wave=1, priority=0, dependency_ids=["A-001"]),
            _make_dto("A-001", wave=1, priority=5),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["A-001", "B-001"]

    def test_dependency_chain_within_wave(self):
        """C -> B -> A chain in same wave."""
        dtos = [
            _make_dto("C-001", wave=1, priority=0, dependency_ids=["B-001"]),
            _make_dto("A-001", wave=1, priority=10),
            _make_dto("B-001", wave=1, priority=5, dependency_ids=["A-001"]),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["A-001", "B-001", "C-001"]

    def test_dependency_overrides_priority(self):
        """Even with higher priority (lower number), dependent comes after dependency."""
        dtos = [
            _make_dto("B-001", wave=1, priority=0, dependency_ids=["A-001"]),
            _make_dto("A-001", wave=1, priority=99),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["A-001", "B-001"]

    def test_combined_waves_and_dependencies(self):
        """Multiple waves with dependencies within each."""
        dtos = [
            # Wave 2
            _make_dto("W2-B", wave=2, priority=0, dependency_ids=["W2-A"]),
            _make_dto("W2-A", wave=2, priority=5),
            # Wave 0
            _make_dto("W0-A", wave=0, priority=3),
            # Wave 1
            _make_dto("W1-B", wave=1, priority=0, dependency_ids=["W1-A"]),
            _make_dto("W1-A", wave=1, priority=1),
            _make_dto("W1-C", wave=1, priority=2),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        ids = [d.id for d in result]
        # Wave 0 first, then wave 1, then wave 2
        assert ids == ["W0-A", "W1-A", "W1-B", "W1-C", "W2-A", "W2-B"]

    def test_cross_wave_dependency_ignored_for_intra_wave_sort(self):
        """Dependencies pointing to stories in other waves don't affect in-degree."""
        dtos = [
            _make_dto("W2-A", wave=2, priority=0, dependency_ids=["W1-A"]),
            _make_dto("W1-A", wave=1, priority=0),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        ids = [d.id for d in result]
        # Wave 1 first, then wave 2 — cross-wave dep doesn't block
        assert ids == ["W1-A", "W2-A"]

    def test_cycle_graceful_degradation(self):
        """Cycle within a wave falls back to priority sort (no crash)."""
        dtos = [
            _make_dto("A-001", wave=1, priority=5, dependency_ids=["B-001"]),
            _make_dto("B-001", wave=1, priority=1, dependency_ids=["A-001"]),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        # Fallback to priority sort: B-001 (priority 1) before A-001 (priority 5)
        assert [d.id for d in result] == ["B-001", "A-001"]

    def test_wave_zero_for_stories_without_feature(self):
        """Stories with wave=0 (no feature) come before wave 1."""
        dtos = [
            _make_dto("F-001", wave=1, priority=0),
            _make_dto("N-001", wave=0, priority=5),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        assert [d.id for d in result] == ["N-001", "F-001"]

    def test_multiple_independent_stories_same_wave(self):
        """Independent stories in same wave sorted by priority then ID."""
        dtos = [
            _make_dto("C-001", wave=1, priority=3),
            _make_dto("A-001", wave=1, priority=3),
            _make_dto("B-001", wave=1, priority=1),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        # B-001 first (priority 1), then A-001 and C-001 (priority 3, tiebreak by ID)
        assert [d.id for d in result] == ["B-001", "A-001", "C-001"]

    def test_diamond_dependency(self):
        """Diamond: D depends on B and C, both depend on A."""
        dtos = [
            _make_dto("D-001", wave=1, priority=0, dependency_ids=["B-001", "C-001"]),
            _make_dto("B-001", wave=1, priority=2, dependency_ids=["A-001"]),
            _make_dto("C-001", wave=1, priority=3, dependency_ids=["A-001"]),
            _make_dto("A-001", wave=1, priority=10),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        ids = [d.id for d in result]
        assert ids[0] == "A-001"  # A first (root)
        assert ids[1] == "B-001"  # B before C (lower priority)
        assert ids[2] == "C-001"
        assert ids[3] == "D-001"  # D last (depends on B and C)

    def test_missing_dependency_not_in_list(self):
        """Dependency pointing to non-existent story is ignored gracefully."""
        dtos = [
            _make_dto("A-001", wave=1, priority=0, dependency_ids=["MISSING-001"]),
            _make_dto("B-001", wave=1, priority=5),
        ]
        result = ListStoriesUseCase._sort_dtos(dtos)
        # MISSING-001 not in group, so A-001 has in-degree 0
        assert [d.id for d in result] == ["A-001", "B-001"]


def _make_story(
    story_id: str,
    component: str = "COMP",
    priority: int = 0,
    developer_id: int | None = None,
    feature_id: int | None = None,
) -> Story:
    """Helper to create a Story entity for testing."""
    return Story(
        id=story_id,
        component=component,
        name=f"Story {story_id}",
        story_points=5,
        priority=priority,
        developer_id=developer_id,
        feature_id=feature_id,
    )


def _make_uow(
    stories: list[Story] | None = None,
    developers: list[Developer] | None = None,
    features: list[Feature] | None = None,
    dependency_map: dict[str, list[str]] | None = None,
) -> MagicMock:
    """Helper to create a mock UnitOfWork."""
    uow = MagicMock()
    uow.stories = MagicMock()
    uow.developers = MagicMock()
    uow.features = MagicMock()
    uow.dependencies = MagicMock()

    uow.stories.get_all = AsyncMock(return_value=stories or [])
    uow.stories.get_by_status = AsyncMock(return_value=stories or [])
    uow.stories.get_by_feature = AsyncMock(return_value=stories or [])
    uow.stories.get_by_developer = AsyncMock(return_value=stories or [])
    uow.developers.get_all = AsyncMock(return_value=developers or [])
    uow.features.get_all = AsyncMock(return_value=features or [])

    dep_map = dependency_map or {}
    uow.dependencies.get_dependencies = AsyncMock(
        side_effect=lambda sid: dep_map.get(sid, [])
    )

    return uow


@pytest.mark.unit
class TestExecute:
    """Tests for ListStoriesUseCase.execute (lines 174-175)."""

    async def test_execute_returns_empty_for_no_stories(self):
        uow = _make_uow()
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result == []
        uow.stories.get_all.assert_awaited_once()

    async def test_execute_returns_enriched_dtos(self):
        stories = [_make_story("A-001", developer_id=1, feature_id=10)]
        developers = [Developer(name="Alice", id=1)]
        features = [Feature(name="Login", wave=1, id=10)]
        uow = _make_uow(stories=stories, developers=developers, features=features)

        use_case = ListStoriesUseCase(uow)
        result = await use_case.execute()

        assert len(result) == 1
        assert result[0].id == "A-001"
        assert result[0].developer_name == "Alice"
        assert result[0].feature_name == "Login"
        assert result[0].wave == 1


@pytest.mark.unit
class TestExecuteByStatus:
    """Tests for ListStoriesUseCase.execute_by_status (lines 186-187)."""

    async def test_execute_by_status_calls_repository(self):
        stories = [_make_story("A-001")]
        uow = _make_uow(stories=stories)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_status("BACKLOG")

        assert len(result) == 1
        uow.stories.get_by_status.assert_awaited_once_with("BACKLOG")

    async def test_execute_by_status_empty(self):
        uow = _make_uow(stories=[])
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_status("DONE")

        assert result == []


@pytest.mark.unit
class TestExecuteByFeature:
    """Tests for ListStoriesUseCase.execute_by_feature (lines 198-199)."""

    async def test_execute_by_feature_calls_repository(self):
        stories = [_make_story("A-001", feature_id=5)]
        features = [Feature(name="Feat", wave=2, id=5)]
        uow = _make_uow(stories=stories, features=features)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_feature(5)

        assert len(result) == 1
        uow.stories.get_by_feature.assert_awaited_once_with(5)
        assert result[0].feature_name == "Feat"
        assert result[0].wave == 2

    async def test_execute_by_feature_empty(self):
        uow = _make_uow(stories=[])
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_feature(999)

        assert result == []


@pytest.mark.unit
class TestExecuteByDeveloper:
    """Tests for ListStoriesUseCase.execute_by_developer (lines 210-211)."""

    async def test_execute_by_developer_calls_repository(self):
        stories = [_make_story("A-001", developer_id=3)]
        developers = [Developer(name="Bob", id=3)]
        uow = _make_uow(stories=stories, developers=developers)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_developer(3)

        assert len(result) == 1
        uow.stories.get_by_developer.assert_awaited_once_with(3)
        assert result[0].developer_name == "Bob"

    async def test_execute_by_developer_empty(self):
        uow = _make_uow(stories=[])
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute_by_developer(999)

        assert result == []


@pytest.mark.unit
class TestEnrichDtos:
    """Tests for ListStoriesUseCase._enrich_dtos (lines 38-64)."""

    async def test_enrich_sets_developer_name(self):
        stories = [_make_story("A-001", developer_id=1)]
        developers = [Developer(name="Alice", id=1)]
        uow = _make_uow(stories=stories, developers=developers)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].developer_name == "Alice"

    async def test_enrich_no_developer_id_leaves_name_none(self):
        stories = [_make_story("A-001", developer_id=None)]
        uow = _make_uow(stories=stories)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].developer_name is None

    async def test_enrich_developer_id_not_in_map_returns_none(self):
        stories = [_make_story("A-001", developer_id=999)]
        developers = [Developer(name="Alice", id=1)]
        uow = _make_uow(stories=stories, developers=developers)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].developer_name is None

    async def test_enrich_sets_feature_name_and_wave(self):
        stories = [_make_story("A-001", feature_id=10)]
        features = [Feature(name="Auth", wave=2, id=10)]
        uow = _make_uow(stories=stories, features=features)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].feature_name == "Auth"
        assert result[0].wave == 2

    async def test_enrich_no_feature_id_leaves_defaults(self):
        stories = [_make_story("A-001", feature_id=None)]
        uow = _make_uow(stories=stories)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].feature_name is None
        assert result[0].wave == 0

    async def test_enrich_feature_id_not_in_map_leaves_defaults(self):
        stories = [_make_story("A-001", feature_id=999)]
        features = [Feature(name="Auth", wave=2, id=10)]
        uow = _make_uow(stories=stories, features=features)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert result[0].feature_name is None
        assert result[0].wave == 0

    async def test_enrich_loads_dependency_ids(self):
        stories = [_make_story("A-001"), _make_story("B-001")]
        dep_map = {"A-001": ["B-001"], "B-001": []}
        uow = _make_uow(stories=stories, dependency_map=dep_map)
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        dto_a = next(d for d in result if d.id == "A-001")
        dto_b = next(d for d in result if d.id == "B-001")
        assert dto_a.dependency_ids == ["B-001"]
        assert dto_b.dependency_ids == []

    async def test_enrich_multiple_stories_full(self):
        """Full enrichment with multiple stories, developers, features, deps."""
        stories = [
            _make_story("A-001", developer_id=1, feature_id=10),
            _make_story("B-001", developer_id=2, feature_id=20),
        ]
        developers = [
            Developer(name="Alice", id=1),
            Developer(name="Bob", id=2),
        ]
        features = [
            Feature(name="Auth", wave=1, id=10),
            Feature(name="Dashboard", wave=2, id=20),
        ]
        dep_map = {"A-001": [], "B-001": ["A-001"]}
        uow = _make_uow(
            stories=stories,
            developers=developers,
            features=features,
            dependency_map=dep_map,
        )
        use_case = ListStoriesUseCase(uow)

        result = await use_case.execute()

        assert len(result) == 2
        # Wave 1 first (A-001), then wave 2 (B-001)
        assert result[0].id == "A-001"
        assert result[0].developer_name == "Alice"
        assert result[0].feature_name == "Auth"
        assert result[1].id == "B-001"
        assert result[1].developer_name == "Bob"
        assert result[1].feature_name == "Dashboard"
        assert result[1].dependency_ids == ["A-001"]
