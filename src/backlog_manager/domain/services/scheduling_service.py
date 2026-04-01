"""Scheduling Service for schedule calculation.

Domain service that implements scheduling algorithms.
All methods are static and have no side effects.
"""

from __future__ import annotations

import heapq
import math
from collections.abc import Sequence
from datetime import date, timedelta
from typing import TYPE_CHECKING

from backlog_manager.domain.exceptions import CyclicDependencyException

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Story


class SchedulingService:
    """Domain service for scheduling calculations.

    Stateless service that implements scheduling algorithms:
    - Duration calculation based on story points and velocity
    - Workday arithmetic (considering weekends and holidays)
    - Topological sorting with priority tiebreaker
    - Story date calculation respecting dependencies

    All methods are static and receive data as parameters.

    Example:
        >>> from datetime import date
        >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
        >>> duration = SchedulingService.calculate_duration(5, 2.0)
        >>> print(duration)  # 3 days
        3
    """

    @staticmethod
    def calculate_duration(story_points: int, velocity: float) -> int:
        """Calculate story duration in workdays based on story points and velocity.

        Uses formula: max(1, ceil(story_points / velocity))

        Args:
            story_points: Story points of the story (3, 5, 8, or 13).
            velocity: Team velocity in story points per day.

        Returns:
            Duration in workdays (minimum 1).

        Raises:
            ValueError: If velocity <= 0.

        Example:
            >>> SchedulingService.calculate_duration(5, 2.0)
            3
            >>> SchedulingService.calculate_duration(3, 5.0)  # Minimum 1 day
            1
        """
        if velocity <= 0:
            raise ValueError("Velocidade deve ser maior que zero")
        return max(1, math.ceil(story_points / velocity))

    @staticmethod
    def is_workday(d: date, holidays: frozenset[date]) -> bool:
        """Check if a date is a workday (Monday-Friday, not a holiday).

        Args:
            d: Date to check.
            holidays: Set of holiday dates.

        Returns:
            True if workday, False if weekend or holiday.

        Example:
            >>> from datetime import date
            >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
            >>> SchedulingService.is_workday(date(2026, 3, 2), BRAZILIAN_HOLIDAYS_2026_2028)
            True
        """
        return d.weekday() < 5 and d not in holidays

    @staticmethod
    def next_workday(d: date, holidays: frozenset[date]) -> date:
        """Return the next workday from a date (inclusive).

        If the date is already a workday, returns the same date.
        Otherwise, advances until a workday is found.

        Args:
            d: Starting date.
            holidays: Set of holiday dates.

        Returns:
            Next workday (d if already a workday).

        Example:
            >>> from datetime import date
            >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
            >>> SchedulingService.next_workday(date(2026, 3, 7), BRAZILIAN_HOLIDAYS_2026_2028)
            datetime.date(2026, 3, 9)  # Saturday -> Monday
        """
        current = d
        while not SchedulingService.is_workday(current, holidays):
            current += timedelta(days=1)
        return current

    @staticmethod
    def add_workdays(
        start_date: date, workdays: int, holidays: frozenset[date]
    ) -> date:
        """Advance N workdays from a start date.

        The start_date counts as day 1.

        Args:
            start_date: Starting date (should be a workday).
            workdays: Number of workdays to advance (>= 1).
            holidays: Set of holiday dates.

        Returns:
            Date after advancing N workdays.

        Example:
            >>> from datetime import date
            >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
            >>> # 2 days from Monday -> Tuesday
            >>> SchedulingService.add_workdays(date(2026, 3, 2), 2, BRAZILIAN_HOLIDAYS_2026_2028)
            datetime.date(2026, 3, 3)
        """
        if workdays <= 1:
            return start_date

        current = start_date
        days_counted = 1

        while days_counted < workdays:
            current += timedelta(days=1)
            if SchedulingService.is_workday(current, holidays):
                days_counted += 1

        return current

    @staticmethod
    def count_workdays_between(
        start_date: date, end_date: date, holidays: frozenset[date]
    ) -> int:
        """Count the number of workdays between two dates (exclusive on both ends).

        Args:
            start_date: Start date (exclusive).
            end_date: End date (exclusive).
            holidays: Set of holiday dates.

        Returns:
            Number of workdays between the dates.

        Example:
            >>> from datetime import date
            >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
            >>> # Mon to Fri = 3 days (Tue, Wed, Thu)
            >>> SchedulingService.count_workdays_between(
            ...     date(2026, 3, 2), date(2026, 3, 6), BRAZILIAN_HOLIDAYS_2026_2028
            ... )
            3
        """
        count = 0
        current = start_date + timedelta(days=1)

        while current < end_date:
            if SchedulingService.is_workday(current, holidays):
                count += 1
            current += timedelta(days=1)

        return count

    @staticmethod
    def topological_sort(
        stories: Sequence[Story], dependencies: dict[str, list[str]]
    ) -> list[Story]:
        """Sort stories topologically using Kahn's algorithm with priority tiebreaker.

        Stories are sorted so that dependencies come before dependents.
        When multiple stories have no pending dependencies, the one with
        lower priority value (higher priority) is processed first.

        Args:
            stories: Sequence of stories to sort.
            dependencies: Graph where key is story_id and value is list of
                         depends_on_ids (story_id -> [depends_on_ids]).

        Returns:
            List of stories in topological order.

        Raises:
            CyclicDependencyException: If a cycle is detected in the dependency graph.

        Example:
            >>> # A -> B -> C (B depends on A, C depends on B)
            >>> sorted_stories = SchedulingService.topological_sort(
            ...     stories=[story_c, story_b, story_a],
            ...     dependencies={"B": ["A"], "C": ["B"]}
            ... )
            >>> [s.id for s in sorted_stories]
            ['A', 'B', 'C']
        """
        if not stories:
            return []

        story_map: dict[str, Story] = {s.id: s for s in stories}
        story_ids = set(story_map.keys())

        in_degree = SchedulingService._build_in_degree(stories, story_ids, dependencies)
        heap = SchedulingService._init_topo_heap(stories, in_degree)
        result = SchedulingService._process_topo_heap(
            heap, story_map, story_ids, in_degree, dependencies
        )
        SchedulingService._check_cycle(result, stories)

        return result

    @staticmethod
    def _build_in_degree(
        stories: Sequence[Story],
        story_ids: set[str],
        dependencies: dict[str, list[str]],
    ) -> dict[str, int]:
        """Build in-degree map considering only dependencies within the story set.

        Args:
            stories: Sequence of stories.
            story_ids: Set of story IDs in scope.
            dependencies: Dependency graph.

        Returns:
            Dictionary mapping story_id to its in-degree count.
        """
        in_degree: dict[str, int] = {s.id: 0 for s in stories}
        for story_id in story_ids:
            for dep_id in dependencies.get(story_id, []):
                if dep_id in story_ids:
                    in_degree[story_id] += 1
        return in_degree

    @staticmethod
    def _init_topo_heap(
        stories: Sequence[Story], in_degree: dict[str, int]
    ) -> list[tuple[int, str]]:
        """Initialize min-heap with stories that have no dependencies.

        Args:
            stories: Sequence of stories.
            in_degree: In-degree map.

        Returns:
            Heapified list of (priority, story_id) tuples.
        """
        heap: list[tuple[int, str]] = [
            (s.priority, s.id) for s in stories if in_degree[s.id] == 0
        ]
        heapq.heapify(heap)
        return heap

    @staticmethod
    def _process_topo_heap(
        heap: list[tuple[int, str]],
        story_map: dict[str, Story],
        story_ids: set[str],
        in_degree: dict[str, int],
        dependencies: dict[str, list[str]],
    ) -> list[Story]:
        """Process the topological sort heap, producing sorted results.

        Args:
            heap: Min-heap of (priority, story_id).
            story_map: Mapping of story_id to Story.
            story_ids: Set of story IDs in scope.
            in_degree: In-degree map (mutated during processing).
            dependencies: Dependency graph.

        Returns:
            List of stories in topological order.
        """
        result: list[Story] = []
        while heap:
            _, story_id = heapq.heappop(heap)
            result.append(story_map[story_id])

            for dependent_id in story_ids:
                deps = dependencies.get(dependent_id, [])
                if story_id in deps:
                    in_degree[dependent_id] -= 1
                    if in_degree[dependent_id] == 0:
                        heapq.heappush(
                            heap, (story_map[dependent_id].priority, dependent_id)
                        )
        return result

    @staticmethod
    def _check_cycle(result: list[Story], stories: Sequence[Story]) -> None:
        """Raise CyclicDependencyException if not all stories were processed.

        Args:
            result: Stories processed so far.
            stories: Original list of stories.

        Raises:
            CyclicDependencyException: If a cycle is detected.
        """
        if len(result) != len(stories):
            remaining = [s.id for s in stories if s not in result]
            cycle_path = remaining + [remaining[0]] if remaining else []
            raise CyclicDependencyException(cycle_path)

    @staticmethod
    def calculate_story_dates(
        story: Story,
        velocity: float,
        start_date: date,
        dependency_end_dates: Sequence[date],
        holidays: frozenset[date],
    ) -> tuple[date, date, int]:
        """Calculate start date, end date, and duration for a story.

        If the story has dependencies, the start date is the day after
        the maximum dependency end date (adjusted to workday).
        Otherwise, uses the project start date.

        Args:
            story: Story to calculate dates for.
            velocity: Team velocity in story points per day.
            start_date: Project start date.
            dependency_end_dates: End dates of dependencies.
            holidays: Set of holiday dates.

        Returns:
            Tuple of (start_date, end_date, duration).

        Example:
            >>> from datetime import date
            >>> from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
            >>> story_start, story_end, duration = SchedulingService.calculate_story_dates(
            ...     story=story_5sp,
            ...     velocity=2.0,
            ...     start_date=date(2026, 3, 2),
            ...     dependency_end_dates=[],
            ...     holidays=BRAZILIAN_HOLIDAYS_2026_2028
            ... )
        """
        # Get story points value (handle StoryPoint enum)
        sp_value = (
            story.story_points.value
            if hasattr(story.story_points, "value")
            else story.story_points
        )

        # Calculate duration
        duration = SchedulingService.calculate_duration(sp_value, velocity)

        # Determine base date
        if dependency_end_dates:
            max_dep_end = max(dependency_end_dates)
            base_date = max_dep_end + timedelta(days=1)
        else:
            base_date = start_date

        # Adjust to next workday
        story_start = SchedulingService.next_workday(base_date, holidays)

        # Calculate end date
        story_end = SchedulingService.add_workdays(story_start, duration, holidays)

        return story_start, story_end, duration
