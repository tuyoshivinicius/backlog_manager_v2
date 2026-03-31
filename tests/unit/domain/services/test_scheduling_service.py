"""Unit tests for SchedulingService.

Tests cover all domain service methods for scheduling calculation.
"""

from __future__ import annotations

import time
from datetime import date

import pytest
from backlog_manager.domain.entities import Story
from backlog_manager.domain.exceptions import CyclicDependencyException
from backlog_manager.domain.services import SchedulingService
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

# =============================================================================
# User Story 1: Duration Calculation Tests (T009-T013)
# =============================================================================


class TestCalculateDuration:
    """Tests for SchedulingService.calculate_duration()."""

    def test_calculate_duration_normal(self) -> None:
        """T009: Normal case - SP=5, velocity=2 -> 3 days."""
        result = SchedulingService.calculate_duration(5, 2.0)
        assert result == 3

    def test_calculate_duration_minimum(self) -> None:
        """T010: Minimum duration - SP=3, velocity=5 -> 1 day (minimum)."""
        result = SchedulingService.calculate_duration(3, 5.0)
        assert result == 1

    def test_calculate_duration_exact(self) -> None:
        """T011: Exact division - SP=8, velocity=4 -> 2 days."""
        result = SchedulingService.calculate_duration(8, 4.0)
        assert result == 2

    def test_calculate_duration_invalid_velocity(self) -> None:
        """T012: Invalid velocity (0) -> ValueError."""
        with pytest.raises(ValueError, match="Velocidade deve ser maior que zero"):
            SchedulingService.calculate_duration(5, 0)

    def test_calculate_duration_negative_velocity(self) -> None:
        """Additional: Negative velocity -> ValueError."""
        with pytest.raises(ValueError, match="Velocidade deve ser maior que zero"):
            SchedulingService.calculate_duration(5, -1.0)

    def test_calculate_duration_large_sp(self) -> None:
        """T013: Large story points - SP=13, velocity=2 -> 7 days."""
        result = SchedulingService.calculate_duration(13, 2.0)
        assert result == 7


# =============================================================================
# User Story 2: Workday Arithmetic Tests (T020-T028)
# =============================================================================


class TestIsWorkday:
    """Tests for SchedulingService.is_workday()."""

    def test_is_workday_monday(self) -> None:
        """T020: Monday is a workday."""
        result = SchedulingService.is_workday(
            date(2026, 3, 2), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result is True

    def test_is_workday_saturday(self) -> None:
        """T021: Saturday is not a workday."""
        result = SchedulingService.is_workday(
            date(2026, 3, 7), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result is False

    def test_is_workday_sunday(self) -> None:
        """T022: Sunday is not a workday."""
        result = SchedulingService.is_workday(
            date(2026, 3, 8), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result is False

    def test_is_workday_holiday(self) -> None:
        """T023: Holiday (Tiradentes 2026-04-21) is not a workday."""
        result = SchedulingService.is_workday(
            date(2026, 4, 21), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result is False


class TestAddWorkdays:
    """Tests for SchedulingService.add_workdays()."""

    def test_add_workdays_same_week(self) -> None:
        """T024: 2 days in same week (Mon -> Tue)."""
        result = SchedulingService.add_workdays(
            date(2026, 3, 2), 2, BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 3)

    def test_add_workdays_across_weekend(self) -> None:
        """T025: 2 days across weekend (Fri -> Mon)."""
        result = SchedulingService.add_workdays(
            date(2026, 3, 6), 2, BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 9)

    def test_add_workdays_with_holiday(self) -> None:
        """T026: 2 days with holiday (Mon before Tiradentes -> Wed)."""
        # 2026-04-20 is Monday, 2026-04-21 is Tiradentes (Tue)
        result = SchedulingService.add_workdays(
            date(2026, 4, 20), 2, BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 4, 22)

    def test_add_workdays_ct004(self) -> None:
        """T027: CT-004 scenario - 4 days with Good Friday + weekend.

        Start: 2026-04-01 (Wed)
        Day 1: Wed 01/04
        Day 2: Thu 02/04
        Day 3: Skip Fri 03/04 (Good Friday), Skip Sat/Sun, Mon 06/04
        Day 4: Tue 07/04
        End: 2026-04-07
        """
        result = SchedulingService.add_workdays(
            date(2026, 4, 1), 4, BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 4, 7)

    def test_add_workdays_single_day(self) -> None:
        """Additional: 1 day returns same date."""
        result = SchedulingService.add_workdays(
            date(2026, 3, 2), 1, BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 2)


class TestCountWorkdaysBetween:
    """Tests for SchedulingService.count_workdays_between()."""

    def test_count_workdays_between(self) -> None:
        """T028: Count workdays Mon 02/03 to Fri 06/03 = 3 (Tue, Wed, Thu)."""
        result = SchedulingService.count_workdays_between(
            date(2026, 3, 2), date(2026, 3, 6), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == 3


# =============================================================================
# User Story 3: Next Workday Adjustment Tests (T032-T036)
# =============================================================================


class TestNextWorkday:
    """Tests for SchedulingService.next_workday()."""

    def test_next_workday_already_workday(self) -> None:
        """T032: Monday returns same date."""
        result = SchedulingService.next_workday(
            date(2026, 3, 2), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 2)

    def test_next_workday_from_saturday(self) -> None:
        """T033: Saturday -> Monday."""
        result = SchedulingService.next_workday(
            date(2026, 3, 7), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 9)

    def test_next_workday_from_sunday(self) -> None:
        """T034: Sunday -> Monday."""
        result = SchedulingService.next_workday(
            date(2026, 3, 8), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 3, 9)

    def test_next_workday_from_holiday(self) -> None:
        """T035: Tiradentes (Tue 21/04) -> Wed 22/04."""
        result = SchedulingService.next_workday(
            date(2026, 4, 21), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 4, 22)

    def test_next_workday_from_good_friday(self) -> None:
        """T036: Good Friday (Fri 03/04) -> Mon 06/04."""
        result = SchedulingService.next_workday(
            date(2026, 4, 3), BRAZILIAN_HOLIDAYS_2026_2028
        )
        assert result == date(2026, 4, 6)


# =============================================================================
# User Story 4: Story Dates Calculation Tests (T038-T042)
# =============================================================================


class TestCalculateStoryDates:
    """Tests for SchedulingService.calculate_story_dates()."""

    @pytest.fixture
    def story_5sp(self) -> Story:
        """Create a story with 5 story points."""
        return Story(
            id="TEST-001",
            component="TEST",
            name="Test Story",
            story_points=5,
            priority=1,
        )

    def test_calculate_story_dates_no_dependencies(self, story_5sp: Story) -> None:
        """T038: Story without dependencies uses project start date."""
        start, end, duration = SchedulingService.calculate_story_dates(
            story=story_5sp,
            velocity=2.0,
            start_date=date(2026, 3, 2),
            dependency_end_dates=[],
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )
        assert start == date(2026, 3, 2)
        assert end == date(2026, 3, 4)  # 3 days from Mon -> Wed
        assert duration == 3

    def test_calculate_story_dates_single_dependency(self, story_5sp: Story) -> None:
        """T039: Story with single dependency (A.end=Wed -> B.start=Thu)."""
        start, end, duration = SchedulingService.calculate_story_dates(
            story=story_5sp,
            velocity=2.0,
            start_date=date(2026, 3, 2),
            dependency_end_dates=[date(2026, 3, 4)],  # Wed
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )
        assert start == date(2026, 3, 5)  # Thu
        assert duration == 3

    def test_calculate_story_dates_multiple_dependencies(
        self, story_5sp: Story
    ) -> None:
        """T040: Story with multiple dependencies uses max end date."""
        start, end, duration = SchedulingService.calculate_story_dates(
            story=story_5sp,
            velocity=2.0,
            start_date=date(2026, 3, 2),
            dependency_end_dates=[date(2026, 3, 4), date(2026, 3, 10)],  # Wed, Tue
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )
        assert start == date(2026, 3, 11)  # Wed (day after max)
        assert duration == 3

    def test_calculate_story_dates_dependency_ends_friday(
        self, story_5sp: Story
    ) -> None:
        """T041: Dependency ends Friday -> Story starts Monday."""
        start, end, duration = SchedulingService.calculate_story_dates(
            story=story_5sp,
            velocity=2.0,
            start_date=date(2026, 3, 2),
            dependency_end_dates=[date(2026, 3, 6)],  # Fri
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )
        assert start == date(2026, 3, 9)  # Mon
        assert duration == 3

    def test_calculate_story_dates_dependency_ends_before_holiday(
        self, story_5sp: Story
    ) -> None:
        """T042: Dependency ends 2026-04-20 -> Story starts 2026-04-22."""
        # 2026-04-20 is Mon, 2026-04-21 is Tiradentes (Tue)
        start, end, duration = SchedulingService.calculate_story_dates(
            story=story_5sp,
            velocity=2.0,
            start_date=date(2026, 3, 2),
            dependency_end_dates=[date(2026, 4, 20)],  # Mon before Tiradentes
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        )
        assert start == date(2026, 4, 22)  # Wed (skip Tiradentes)
        assert duration == 3


# =============================================================================
# User Story 5: Topological Sort Tests (T049-T053)
# =============================================================================


class TestTopologicalSort:
    """Tests for SchedulingService.topological_sort()."""

    @pytest.fixture
    def stories_abc(self) -> list[Story]:
        """Create stories A, B, C."""
        return [
            Story(
                id="A-001", component="A", name="Story A", story_points=5, priority=1
            ),
            Story(
                id="B-001", component="B", name="Story B", story_points=5, priority=2
            ),
            Story(
                id="C-001", component="C", name="Story C", story_points=5, priority=3
            ),
        ]

    def test_topological_sort_linear(self, stories_abc: list[Story]) -> None:
        """T049: Linear chain A->B->C -> [A, B, C]."""
        # B depends on A, C depends on B
        deps = {"B-001": ["A-001"], "C-001": ["B-001"]}
        result = SchedulingService.topological_sort(stories_abc, deps)
        ids = [s.id for s in result]
        assert ids == ["A-001", "B-001", "C-001"]

    def test_topological_sort_priority_tiebreak(self) -> None:
        """T050: A.prio=2, B.prio=1, independent -> [B, A]."""
        stories = [
            Story(
                id="A-001", component="A", name="Story A", story_points=5, priority=2
            ),
            Story(
                id="B-001", component="B", name="Story B", story_points=5, priority=1
            ),
        ]
        deps: dict[str, list[str]] = {}
        result = SchedulingService.topological_sort(stories, deps)
        ids = [s.id for s in result]
        assert ids == ["B-001", "A-001"]  # B first (lower priority)

    def test_topological_sort_complex(self) -> None:
        """T051: A->C, B->C, A.prio=2, B.prio=1 -> [B, A, C]."""
        stories = [
            Story(
                id="A-001", component="A", name="Story A", story_points=5, priority=2
            ),
            Story(
                id="B-001", component="B", name="Story B", story_points=5, priority=1
            ),
            Story(
                id="C-001", component="C", name="Story C", story_points=5, priority=3
            ),
        ]
        # C depends on both A and B
        deps = {"C-001": ["A-001", "B-001"]}
        result = SchedulingService.topological_sort(stories, deps)
        ids = [s.id for s in result]
        # B comes before A (lower priority), C comes last (depends on both)
        assert ids == ["B-001", "A-001", "C-001"]

    def test_topological_sort_cycle(self) -> None:
        """T052: Cycle detected -> CyclicDependencyException."""
        stories = [
            Story(
                id="A-001", component="A", name="Story A", story_points=5, priority=1
            ),
            Story(
                id="B-001", component="B", name="Story B", story_points=5, priority=2
            ),
            Story(
                id="C-001", component="C", name="Story C", story_points=5, priority=3
            ),
        ]
        # A->B->C->A (cycle)
        deps = {"A-001": ["C-001"], "B-001": ["A-001"], "C-001": ["B-001"]}
        with pytest.raises(CyclicDependencyException):
            SchedulingService.topological_sort(stories, deps)

    def test_topological_sort_performance(self) -> None:
        """T053: 100 stories in < 100ms."""
        # Create 100 stories
        stories = [
            Story(
                id=f"T-{i:03d}",
                component="T",
                name=f"Story {i}",
                story_points=5,
                priority=i,
            )
            for i in range(100)
        ]
        # Linear chain: each depends on previous
        deps: dict[str, list[str]] = {}
        for i in range(1, 100):
            deps[f"T-{i:03d}"] = [f"T-{i-1:03d}"]

        start_time = time.time()
        result = SchedulingService.topological_sort(stories, deps)
        elapsed_ms = (time.time() - start_time) * 1000

        assert len(result) == 100
        assert elapsed_ms < 100, f"Took {elapsed_ms:.2f}ms, expected < 100ms"

    def test_topological_sort_empty(self) -> None:
        """Additional: Empty input returns empty list."""
        result = SchedulingService.topological_sort([], {})
        assert result == []
