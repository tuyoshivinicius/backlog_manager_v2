"""Unit tests for ListStoriesUseCase._sort_dtos ordering logic."""

from __future__ import annotations

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
from backlog_manager.application.use_cases.story.list_stories import ListStoriesUseCase


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
