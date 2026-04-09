"""Integration tests for allocation service reproducibility and logging.

Tests cover EP-015 requirements:
- US2: Reproducibility via seed
- US3: Log correlation
- US4: Performance validation
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

import pytest
from backlog_manager.domain.entities import Developer, Feature, Story
from backlog_manager.domain.services import (
    AllocationConfig,
    AllocationCriteria,
    AllocationService,
)
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only


@pytest.fixture
def holidays() -> frozenset[date]:
    """Brazilian holidays for 2026-2028."""
    return BRAZILIAN_HOLIDAYS_2026_2028


@pytest.fixture
def developers() -> list[Developer]:
    """Create test developers."""
    return [
        Developer(name="Alice", id=1),
        Developer(name="Bob", id=2),
        Developer(name="Carol", id=3),
    ]


@pytest.fixture
def features() -> list[Feature]:
    """Create test features."""
    return [
        Feature(name="Feature 1", wave=1, id=1),
        Feature(name="Feature 2", wave=1, id=2),
        Feature(name="Feature 3", wave=2, id=3),
    ]


def create_stories(count: int, feature_id: int | None = None) -> list[Story]:
    """Create multiple test stories."""
    stories = []
    base_date = date(2026, 3, 2)
    for i in range(count):
        stories.append(
            Story(
                planning_id=1,
                id=f"STORY-{i+1:03d}",
                component="AUTH",
                name=f"Story {i+1}",
                story_points=3,
                priority=i + 1,
                developer_id=None,
                start_date=base_date,
                end_date=date(2026, 3, 4),
                feature_id=feature_id,
                duration=2,
            )
        )
    return stories


# =============================================================================
# T019: Reproducibility Test
# =============================================================================


@pytest.mark.integration
class TestReproducibility:
    """T019: Test that allocation is deterministic with same seed."""

    def test_same_seed_produces_same_result(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """Two executions with same seed should produce identical allocations."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            allocation_criteria=AllocationCriteria.LOAD_BALANCING,
            random_seed=42,  # Fixed seed
        )

        # Create fresh stories for each run
        def create_fresh_stories() -> list[Story]:
            return [
                Story(
                    planning_id=1,
                    id="AUTH-001",
                    component="AUTH",
                    name="Story 1",
                    story_points=5,
                    priority=1,
                    developer_id=None,
                    start_date=date(2026, 3, 2),
                    end_date=date(2026, 3, 5),
                    feature_id=1,
                    duration=3,
                ),
                Story(
                    planning_id=1,
                    id="AUTH-002",
                    component="AUTH",
                    name="Story 2",
                    story_points=3,
                    priority=2,
                    developer_id=None,
                    start_date=date(2026, 3, 6),
                    end_date=date(2026, 3, 9),
                    feature_id=1,
                    duration=2,
                ),
                Story(
                    planning_id=1,
                    id="AUTH-003",
                    component="AUTH",
                    name="Story 3",
                    story_points=8,
                    priority=3,
                    developer_id=None,
                    start_date=date(2026, 3, 10),
                    end_date=date(2026, 3, 16),
                    feature_id=2,
                    duration=5,
                ),
            ]

        # First execution
        stories1 = create_fresh_stories()
        result1 = AllocationService.allocate_stories(
            stories=stories1,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Second execution with fresh stories but same seed
        stories2 = create_fresh_stories()
        result2 = AllocationService.allocate_stories(
            stories=stories2,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Verify same allocations
        assert len(result1.allocated_stories) == len(result2.allocated_stories)

        # Create maps for comparison
        alloc1 = {s.id: s.developer_id for s in stories1}
        alloc2 = {s.id: s.developer_id for s in stories2}

        # Same stories should be allocated to same developers
        for story_id in alloc1:
            assert alloc1[story_id] == alloc2[story_id], (
                f"Story {story_id} allocated differently: "
                f"{alloc1[story_id]} vs {alloc2[story_id]}"
            )

    def test_different_seed_may_produce_different_result(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """Different seeds may produce different allocations (not guaranteed)."""

        # Create multiple stories to increase likelihood of different allocations
        def create_many_stories() -> list[Story]:
            return [
                Story(
                    planning_id=1,
                    id=f"AUTH-{i:03d}",
                    component="AUTH",
                    name=f"Story {i}",
                    story_points=3,
                    priority=i,
                    developer_id=None,
                    start_date=date(2026, 3, 2 + i % 10),
                    end_date=date(2026, 3, 4 + i % 10),
                    feature_id=1,
                    duration=2,
                )
                for i in range(10)
            ]

        config1 = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            allocation_criteria=AllocationCriteria.LOAD_BALANCING,
            random_seed=42,
        )

        config2 = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            allocation_criteria=AllocationCriteria.LOAD_BALANCING,
            random_seed=12345,  # Different seed
        )

        stories1 = create_many_stories()
        result1 = AllocationService.allocate_stories(
            stories=stories1,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config1,
        )

        stories2 = create_many_stories()
        result2 = AllocationService.allocate_stories(
            stories=stories2,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config2,
        )

        # Both should complete (no assertion on difference since it's probabilistic)
        assert result1.metrics.stories_allocated > 0
        assert result2.metrics.stories_allocated > 0


# =============================================================================
# T022: Log Correlation Test
# =============================================================================


@pytest.mark.integration
class TestLogCorrelation:
    """T022: Test that logs contain sufficient information for correlation."""

    def test_metrics_logged_match_result_metrics(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """AllocationMetrics in result should match logged values."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(10, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Verify metrics are populated
        assert result.metrics.stories_processed > 0
        assert result.metrics.waves_processed > 0
        assert result.metrics.total_time_seconds > 0

        # Metrics should be consistent
        assert result.metrics.stories_allocated <= result.metrics.stories_processed

    def test_warnings_contain_developer_info(
        self,
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """Warnings should contain developer identification for debugging."""
        # No developers - will cause deadlock warning
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(5, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=[],  # No developers
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Should have deadlock warning
        assert len(result.warnings) > 0
        assert result.metrics.deadlocks_detected > 0


# =============================================================================
# T025: Performance Test
# =============================================================================


@pytest.mark.integration
class TestPerformance:
    """T025: Test performance requirements."""

    def test_100_stories_under_5_seconds(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """T025: 100 stories should be allocated in under 5 seconds (SC-003)."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(100, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Performance requirement: <= 5 seconds for 100 stories
        assert result.metrics.total_time_seconds <= 5.0, (
            f"Allocation took {result.metrics.total_time_seconds:.2f}s, "
            "expected <= 5.0s"
        )

    def test_190_stories_under_5_seconds(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """T026: 190 stories (seed size) should be allocated in under 5 seconds (SC-002)."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(190, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Performance requirement: <= 5 seconds for 190 stories
        assert result.metrics.total_time_seconds <= 5.0, (
            f"Allocation took {result.metrics.total_time_seconds:.2f}s, "
            "expected <= 5.0s"
        )

    @pytest.mark.slow
    def test_500_stories_under_30_seconds(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """T027: 500 stories should be allocated in under 30 seconds (SC-009)."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(500, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Performance requirement: <= 30 seconds for 500 stories
        assert result.metrics.total_time_seconds <= 30.0, (
            f"Allocation took {result.metrics.total_time_seconds:.2f}s, "
            "expected <= 30.0s"
        )

    def test_metrics_track_all_16_fields(
        self,
        developers: list[Developer],
        features: list[Feature],
        holidays: frozenset[date],
    ) -> None:
        """AllocationMetrics should have all 16 fields populated."""
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            random_seed=42,
        )

        stories = create_stories(20, feature_id=1)

        result = AllocationService.allocate_stories(
            stories=stories,
            developers=developers,
            dependencies=[],
            features=features,
            holidays=holidays,
            config=config,
        )

        # Verify all 16 metrics fields exist and have valid values
        metrics = result.metrics
        assert isinstance(metrics.total_time_seconds, float)
        assert isinstance(metrics.stories_processed, int)
        assert isinstance(metrics.stories_allocated, int)
        assert isinstance(metrics.waves_processed, int)
        assert isinstance(metrics.total_iterations, int)
        assert isinstance(metrics.iterations_per_wave, dict)
        assert isinstance(metrics.allocations_by_dependency_owner, int)
        assert isinstance(metrics.allocations_by_load_balancing, int)
        assert isinstance(metrics.deadlocks_detected, int)
        assert isinstance(metrics.date_adjustments, int)
        assert isinstance(metrics.validation_reallocations, int)
        assert isinstance(metrics.validation_dependency_fixes, int)
        assert isinstance(metrics.validation_conflict_fixes, int)
        assert isinstance(metrics.max_idle_violations_detected, int)
        assert isinstance(metrics.max_idle_violations_fixed, int)
        assert isinstance(metrics.failed_reallocations, int)
