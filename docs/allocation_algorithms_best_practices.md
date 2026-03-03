# Resource Allocation Algorithms: Best Practices Guide

## 1. Load Balancing Algorithms for Work Distribution

### 1.1 Round-Robin Algorithm
**Best for:** Equal distribution across developers, simple fair scheduling, stateless allocation.

```python
class RoundRobinAllocator:
    """Distributes work items sequentially across available developers."""

    def __init__(self, developers: List[Developer]):
        self.developers = developers
        self.current_index = 0

    def allocate_next(self) -> Developer:
        """Get next developer in round-robin order."""
        if not self.developers:
            raise ValueError("No developers available")

        developer = self.developers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.developers)
        return developer

    def reset(self) -> None:
        """Reset to first developer (useful for reallocation rounds)."""
        self.current_index = 0
```

**Advantages:**
- Simple, deterministic, predictable
- Fair distribution without complex metrics
- Easy to understand and audit
- No state complexity

**Disadvantages:**
- Ignores actual developer capacity/availability
- Doesn't account for skill levels or task requirements
- Can lead to uneven load if not combined with validation

### 1.2 Count-Based Load Balancing
**Best for:** Capacity-aware allocation, handling varying developer workloads.

```python
class CountBasedAllocator:
    """Allocates to developer with fewest current assignments."""

    def __init__(self, developers: List[Developer]):
        self.developers = developers

    def get_allocation_counts(self) -> Dict[Developer, int]:
        """Count current tasks per developer."""
        counts = {}
        for dev in self.developers:
            counts[dev] = len([s for s in dev.stories if s.status != 'completed'])
        return counts

    def allocate_next(self, random_seed: Optional[int] = None) -> Developer:
        """Allocate to developer with least tasks.

        Args:
            random_seed: If provided, use for deterministic tie-breaking
        """
        if not self.developers:
            raise ValueError("No developers available")

        counts = self.get_allocation_counts()
        min_count = min(counts.values())

        # Find all developers with minimum count (tie case)
        candidates = [dev for dev, count in counts.items() if count == min_count]

        if len(candidates) == 1:
            return candidates[0]

        # Break ties deterministically if seed provided
        if random_seed is not None:
            rng = random.Random(random_seed)
            return rng.choice(candidates)

        return candidates[0]  # Default: return first
```

**Advantages:**
- Accounts for current workload
- Naturally balances distribution over time
- Prevents overloading specific developers

**Disadvantages:**
- Requires tracking state
- Tie-breaking can be arbitrary
- May not account for task complexity/duration

### 1.3 Hybrid Approach: Weighted Load Balancing
**Best for:** Complex scenarios with task complexity, skill matching, and availability.

```python
class WeightedAllocator:
    """Allocates based on weighted combination of factors."""

    def __init__(self, developers: List[Developer], weights: Dict[str, float] = None):
        self.developers = developers
        self.weights = weights or {
            'workload': 0.5,      # Current task count
            'capacity': 0.3,      # Available time/capacity
            'skill_match': 0.2    # Task skill requirements match
        }

    def calculate_score(self, developer: Developer, task: Task) -> float:
        """Calculate allocation score (lower = better candidate)."""
        score = 0.0

        # Workload factor (prefer developers with fewer tasks)
        task_count = len([s for s in developer.stories if s.status != 'completed'])
        workload_score = task_count / max(len(self.developers), 1)
        score += self.weights['workload'] * workload_score

        # Capacity factor (prefer developers with available capacity)
        available_hours = developer.capacity - developer.allocated_hours
        capacity_score = max(0, 1 - (available_hours / developer.capacity))
        score += self.weights['capacity'] * capacity_score

        # Skill match factor (prefer matching skills)
        required_skills = set(task.required_skills or [])
        available_skills = set(developer.skills)
        if required_skills:
            skill_match = len(required_skills & available_skills) / len(required_skills)
        else:
            skill_match = 1.0
        score += self.weights['skill_match'] * (1 - skill_match)

        return score

    def allocate_next(self, task: Task, random_seed: Optional[int] = None) -> Developer:
        """Allocate task to developer with best score."""
        if not self.developers:
            raise ValueError("No developers available")

        scores = [(dev, self.calculate_score(dev, task)) for dev in self.developers]
        scores.sort(key=lambda x: x[1])

        min_score = scores[0][1]
        candidates = [dev for dev, score in scores if abs(score - min_score) < 0.001]

        if random_seed is not None:
            rng = random.Random(random_seed)
            return rng.choice(candidates)

        return candidates[0]
```

### 1.4 Tie-Breaking and Fairness
**Critical for:** Deterministic testing, reproducible allocations, fairness across runs.

```python
class FairTieBreaker:
    """Implements deterministic, fair tie-breaking."""

    @staticmethod
    def break_tie(candidates: List[Developer],
                  seed_base: str,
                  iteration: int = 0) -> Developer:
        """Break tie deterministically using seed.

        Args:
            candidates: Tied developers
            seed_base: Base seed string (e.g., task_id)
            iteration: Iteration number (prevents same choice in loop)

        Returns:
            Selected developer
        """
        if len(candidates) == 1:
            return candidates[0]

        # Create deterministic seed from base + iteration
        seed_value = hash(f"{seed_base}_{iteration}") % (2**31)
        rng = random.Random(seed_value)
        return rng.choice(candidates)

    @staticmethod
    def get_fair_order(developers: List[Developer],
                      seed: int) -> List[Developer]:
        """Get reproducible random ordering of developers.

        Useful for: fair round-robin starting point, tie-breaking order
        """
        rng = random.Random(seed)
        order = developers.copy()
        rng.shuffle(order)
        return order
```

**Best practices for tie-breaking:**
1. Always use seeded random for deterministic behavior
2. Include iteration/round number in seed to vary selection
3. Document the seeding strategy clearly
4. Consider developer ID as tie-breaker when determinism via ID is needed

---

## 2. Conflict Detection in Scheduling

### 2.1 Period Overlap Detection
**Best for:** Identifying conflicting allocations, capacity violations.

```python
class ConflictDetector:
    """Detects scheduling conflicts and overlaps."""

    @staticmethod
    def periods_overlap(period1: Tuple[date, date],
                       period2: Tuple[date, date]) -> bool:
        """Check if two periods overlap.

        Args:
            period1: (start_date, end_date)
            period2: (start_date, end_date)

        Returns:
            True if periods overlap

        Examples:
            [2024-01-01, 2024-01-10] vs [2024-01-05, 2024-01-15] -> True
            [2024-01-01, 2024-01-10] vs [2024-01-11, 2024-01-15] -> False
            [2024-01-01, 2024-01-10] vs [2024-01-10, 2024-01-15] -> True (touch)
        """
        start1, end1 = period1
        start2, end2 = period2
        return start1 <= end2 and start2 <= end1

    @staticmethod
    def get_overlap_duration(period1: Tuple[date, date],
                            period2: Tuple[date, date]) -> Optional[int]:
        """Calculate days of overlap between periods.

        Returns:
            Number of overlapping days, or None if no overlap
        """
        start1, end1 = period1
        start2, end2 = period2

        if not ConflictDetector.periods_overlap(period1, period2):
            return None

        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        return (overlap_end - overlap_start).days + 1

    @staticmethod
    def find_conflicts(developer: Developer,
                      new_allocation: Allocation) -> List[Conflict]:
        """Find all conflicts for a new allocation.

        Args:
            developer: Developer to check
            new_allocation: Proposed allocation

        Returns:
            List of conflicts with existing allocations
        """
        conflicts = []
        new_period = (new_allocation.start_date, new_allocation.end_date)

        for existing in developer.allocations:
            if existing.status == 'cancelled':
                continue

            existing_period = (existing.start_date, existing.end_date)

            if ConflictDetector.periods_overlap(new_period, existing_period):
                overlap_days = ConflictDetector.get_overlap_duration(
                    new_period, existing_period
                )
                conflicts.append(Conflict(
                    type='schedule_overlap',
                    existing_allocation=existing,
                    new_allocation=new_allocation,
                    overlap_days=overlap_days
                ))

        return conflicts
```

### 2.2 Cascading Conflict Resolution
**Best for:** Automatic conflict resolution without losing work allocations.

```python
class ConflictResolver:
    """Implements cascading conflict resolution strategies."""

    @staticmethod
    def resolve_by_rescheduling(conflict: Conflict,
                               strategy: str = 'postpone') -> bool:
        """Attempt to resolve conflict by rescheduling.

        Strategies:
        - 'postpone': Move conflicting allocation to after new one
        - 'split': Split conflicting allocation if possible
        - 'move_new': Move new allocation instead

        Returns:
            True if successfully resolved
        """
        existing = conflict.existing_allocation
        new = conflict.new_allocation

        if strategy == 'postpone':
            # Move existing allocation to start after new one ends
            new_end = new.end_date
            duration = (existing.end_date - existing.start_date).days
            existing.start_date = new_end + timedelta(days=1)
            existing.end_date = existing.start_date + timedelta(days=duration)
            return True

        elif strategy == 'split':
            # Only possible if existing allocation can be split
            if existing.duration_days < 5:  # Too small to split
                return False

            # Split at conflict point
            conflict_start = max(existing.start_date, new.start_date)

            # Keep part before conflict
            existing.end_date = conflict_start - timedelta(days=1)

            # Create new allocation for after conflict
            remaining_duration = (
                (conflict.existing_allocation.end_date - conflict_start).days
            )
            new_allocation = Allocation(
                developer=existing.developer,
                story=existing.story,
                start_date=new.end_date + timedelta(days=1),
                end_date=new.end_date + timedelta(days=remaining_duration)
            )
            return True

        elif strategy == 'move_new':
            # Move new allocation instead
            new.start_date = existing.end_date + timedelta(days=1)
            new.end_date = (new.start_date +
                           timedelta(days=(new.duration_days)))
            return True

        return False

    @staticmethod
    def cascade_resolve(conflicts: List[Conflict],
                       max_passes: int = 10) -> Tuple[List[Conflict], int]:
        """Recursively resolve conflicts until none remain.

        Args:
            conflicts: Initial list of conflicts
            max_passes: Maximum resolution attempts

        Returns:
            (Remaining unresolved conflicts, number of passes used)

        Raises:
            AllocationError: If unable to resolve after max_passes
        """
        unresolved = conflicts.copy()
        passes = 0

        while unresolved and passes < max_passes:
            passes += 1
            resolved_this_pass = 0

            for conflict in unresolved[:]:  # Iterate over copy
                if ConflictResolver.resolve_by_rescheduling(
                    conflict,
                    strategy='postpone'
                ):
                    unresolved.remove(conflict)
                    resolved_this_pass += 1

            # Check if we made progress
            if resolved_this_pass == 0:
                break

        if unresolved:
            raise AllocationError(
                f"Unable to resolve {len(unresolved)} conflicts after {passes} passes: "
                f"{[c.type for c in unresolved]}"
            )

        return unresolved, passes
```

### 2.3 Conflict Prevention Through Validation
**Best for:** Catching issues early before allocation.

```python
class AllocationValidator:
    """Pre-validates allocations before assignment."""

    @staticmethod
    def validate_allocation(allocation: Allocation,
                           developer: Developer) -> List[ValidationError]:
        """Validate allocation against constraints.

        Checks:
        - Developer has required skills
        - Period doesn't exceed reasonable duration
        - Allocation doesn't violate developer capacity
        - No overlaps with critical allocations
        """
        errors = []

        # Skill validation
        required = set(allocation.story.required_skills or [])
        available = set(developer.skills)
        if required and not required.issubset(available):
            missing = required - available
            errors.append(ValidationError(
                'skill_mismatch',
                f"Developer missing skills: {missing}"
            ))

        # Duration validation
        if allocation.duration_days > 90:
            errors.append(ValidationError(
                'excessive_duration',
                f"Allocation duration {allocation.duration_days}d exceeds 90d limit"
            ))

        # Capacity validation
        conflicts = ConflictDetector.find_conflicts(developer, allocation)
        if conflicts:
            errors.append(ValidationError(
                'schedule_conflict',
                f"Conflicts with {len(conflicts)} existing allocations"
            ))

        return errors
```

---

## 3. Deadlock Detection Patterns

### 3.1 Progress Tracking in Iterative Algorithms
**Best for:** Detecting infinite loops, ensuring forward progress.

```python
class ProgressTracker:
    """Tracks progress through iterative allocation algorithms."""

    def __init__(self, max_passes: int = 20):
        self.max_passes = max_passes
        self.current_pass = 0
        self.allocated_count = 0
        self.previously_allocated = 0

    def start_pass(self) -> None:
        """Mark start of new allocation pass."""
        self.current_pass += 1
        self.previously_allocated = self.allocated_count

        if self.current_pass > self.max_passes:
            raise DeadlockError(
                f"Exceeded maximum passes ({self.max_passes}). "
                f"Current: {self.allocated_count}, "
                f"Previous: {self.previously_allocated}"
            )

    def record_allocation(self) -> None:
        """Track that allocation was made."""
        self.allocated_count += 1

    def check_progress(self) -> bool:
        """Verify forward progress was made in current pass.

        Returns:
            True if progress was made, False otherwise
        """
        progress = self.allocated_count > self.previously_allocated
        return progress

    def emit_warning_if_stalling(self) -> None:
        """Emit warning if progress is slowing."""
        if self.current_pass > 5 and not self.check_progress():
            logger.warning(
                f"Allocation stalling at pass {self.current_pass}: "
                f"No new allocations in this pass"
            )

    @property
    def is_complete(self) -> bool:
        """Check if allocation should complete."""
        # Complete if no progress made in last pass
        if self.current_pass > 1 and not self.check_progress():
            return True
        return False
```

### 3.2 Deadlock Detection Strategies
**Best for:** Identifying and handling stuck states.

```python
class DeadlockDetector:
    """Detects and reports deadlock conditions."""

    @staticmethod
    def detect_circular_dependency(allocations: List[Allocation]) -> bool:
        """Detect if allocations form circular dependencies.

        Example: Story A depends on Story B, B depends on A
        """
        # Build dependency graph
        graph = {}
        for alloc in allocations:
            if alloc.story.id not in graph:
                graph[alloc.story.id] = []

            for dep in alloc.story.dependencies:
                graph[alloc.story.id].append(dep.id)

        # Check for cycles using DFS
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph:
            if node_id not in visited:
                if has_cycle(node_id):
                    return True

        return False

    @staticmethod
    def detect_unallocatable(available_developers: List[Developer],
                            unallocated_stories: List[Story]) -> List[Story]:
        """Identify stories that cannot be allocated (deadlock).

        Common causes:
        - No developer has required skills
        - All developers at capacity
        - Skill gap too large
        """
        unallocatable = []

        for story in unallocated_stories:
            required_skills = set(story.required_skills or [])

            # Check if any developer has required skills
            capable_devs = [
                d for d in available_developers
                if (not required_skills or
                    required_skills.issubset(set(d.skills)))
            ]

            if not capable_devs:
                unallocatable.append(story)

        return unallocatable
```

### 3.3 Graceful Degradation
**Best for:** Handling deadlock conditions without failure.

```python
class AllocationEngine:
    """Allocates stories with deadlock handling."""

    def allocate_with_fallback(self,
                              stories: List[Story],
                              developers: List[Developer],
                              max_passes: int = 20) -> AllocationResult:
        """Allocate stories with graceful fallback handling.

        Strategy:
        1. Try full allocation with all constraints
        2. If deadlock detected, relax constraints iteratively
        3. Warn on unallocated items
        4. Never fail completely
        """
        tracker = ProgressTracker(max_passes=max_passes)
        result = AllocationResult()

        unallocated = set(stories)
        relaxation_level = 0  # 0 = strict, 3 = relaxed

        while unallocated:
            tracker.start_pass()

            if tracker.is_complete:
                logger.info(f"Allocation complete at pass {tracker.current_pass}")
                break

            newly_allocated = []
            for story in list(unallocated):
                try:
                    # Try allocation with current relaxation
                    dev = self._allocate_story(
                        story,
                        developers,
                        relaxation_level=relaxation_level
                    )

                    result.allocations.append(Allocation(
                        story=story,
                        developer=dev
                    ))
                    newly_allocated.append(story)
                    tracker.record_allocation()

                except UnallocatableError:
                    # Record for later handling
                    pass

            # Remove newly allocated from unallocated set
            for story in newly_allocated:
                unallocated.discard(story)

            tracker.emit_warning_if_stalling()

            # Check for deadlock
            if not tracker.check_progress() and relaxation_level < 3:
                relaxation_level += 1
                logger.warning(
                    f"No progress at pass {tracker.current_pass}, "
                    f"relaxing to level {relaxation_level}"
                )

        # Report unallocated
        if unallocated:
            unallocatable = DeadlockDetector.detect_unallocatable(
                developers, list(unallocated)
            )
            result.unallocated_stories = unallocatable
            result.warnings.append(
                f"{len(unallocatable)} stories unallocatable "
                f"(missing skills/capacity)"
            )

        return result

    def _allocate_story(self,
                       story: Story,
                       developers: List[Developer],
                       relaxation_level: int = 0) -> Developer:
        """Allocate story with specified relaxation level.

        Relaxation levels:
        0: Strict - require skill match, capacity, no conflicts
        1: Moderate - allow minor capacity overage
        2: Lenient - allow any developer with some capacity
        3: Force - allocate to anyone (last resort)
        """
        if relaxation_level == 0:
            # Strict: must have skills, capacity, no conflicts
            return self._allocate_strict(story, developers)
        elif relaxation_level == 1:
            # Moderate: allow 10% capacity overage
            return self._allocate_moderate(story, developers)
        elif relaxation_level == 2:
            # Lenient: ignore skill match
            return self._allocate_lenient(story, developers)
        else:
            # Force: allocate to least loaded
            return self._allocate_force(story, developers)
```

---

## 4. Stabilization Loops in Scheduling

### 4.1 Post-Allocation Validation
**Best for:** Ensuring allocation correctness after each pass.

```python
class AllocationValidator:
    """Post-validates allocations to find issues."""

    @staticmethod
    def validate_allocation_state(allocations: List[Allocation],
                                 developers: List[Developer]) -> List[Issue]:
        """Validate entire allocation state for consistency.

        Checks:
        - No developer schedule conflicts
        - No over-capacity allocations
        - All required skills assigned where needed
        - Dependencies respected (if task depends on task, schedule accordingly)
        """
        issues = []

        # Check each developer's schedule
        for dev in developers:
            dev_allocations = [a for a in allocations if a.developer == dev]

            # Sort by start date
            dev_allocations.sort(key=lambda a: a.start_date)

            # Check for overlaps
            for i, alloc1 in enumerate(dev_allocations):
                for alloc2 in dev_allocations[i+1:]:
                    if ConflictDetector.periods_overlap(
                        (alloc1.start_date, alloc1.end_date),
                        (alloc2.start_date, alloc2.end_date)
                    ):
                        issues.append(Issue(
                            type='schedule_conflict',
                            developer=dev,
                            allocations=[alloc1, alloc2],
                            description=f"Overlapping allocations: {alloc1.story.id} and {alloc2.story.id}"
                        ))

            # Check capacity
            total_days = sum(a.duration_days for a in dev_allocations)
            if total_days > dev.capacity_days_per_year:
                issues.append(Issue(
                    type='capacity_exceeded',
                    developer=dev,
                    description=f"Developer allocated {total_days}d, "
                                f"capacity is {dev.capacity_days_per_year}d"
                ))

        return issues
```

### 4.2 Fixed-Point Iteration
**Best for:** Stabilizing allocations through repeated validation and correction.

```python
class StabilizationEngine:
    """Drives allocation toward stable state through iteration."""

    def __init__(self, max_stabilization_passes: int = 10):
        self.max_passes = max_stabilization_passes
        self.current_pass = 0
        self.issues_per_pass = []

    def stabilize(self,
                  allocations: List[Allocation],
                  developers: List[Developer]) -> StabilizationResult:
        """Iteratively stabilize allocations until fixed point reached.

        Fixed-point: state where validation finds no issues.

        Strategy:
        1. Validate current allocations
        2. For each issue found:
           - Apply correction (e.g., reschedule conflicting items)
           - Record changes
        3. Repeat until no changes made (fixed point) or max passes reached
        """
        result = StabilizationResult()

        while self.current_pass < self.max_passes:
            self.current_pass += 1

            # Validate
            issues = AllocationValidator.validate_allocation_state(
                allocations,
                developers
            )
            self.issues_per_pass.append(len(issues))

            if not issues:
                # Fixed point reached - no issues found
                result.status = 'stable'
                result.passes = self.current_pass
                return result

            # Apply corrections
            corrections_made = self._apply_corrections(issues, allocations)
            result.corrections_applied += corrections_made

            # Check if we're making progress
            if corrections_made == 0:
                # Can't fix remaining issues
                break

        # Reached max passes
        remaining_issues = AllocationValidator.validate_allocation_state(
            allocations,
            developers
        )

        if remaining_issues:
            result.status = 'unstable'
            result.remaining_issues = remaining_issues
            logger.warning(
                f"Stabilization did not reach fixed point. "
                f"Remaining issues: {len(remaining_issues)}, "
                f"Passes used: {self.current_pass}"
            )
        else:
            result.status = 'stable'

        result.passes = self.current_pass
        return result

    def _apply_corrections(self,
                          issues: List[Issue],
                          allocations: List[Allocation]) -> int:
        """Apply corrections to resolve issues.

        Returns:
            Number of corrections applied
        """
        corrections = 0

        for issue in issues:
            if issue.type == 'schedule_conflict':
                # Try to postpone one of the conflicting allocations
                alloc1, alloc2 = issue.allocations

                # Postpone the second one
                alloc2.start_date = alloc1.end_date + timedelta(days=1)
                alloc2.end_date = (alloc2.start_date +
                                   timedelta(days=alloc2.duration_days))
                corrections += 1

            elif issue.type == 'capacity_exceeded':
                # Remove lower-priority allocations until under capacity
                dev = issue.developer
                dev_allocs = [a for a in allocations if a.developer == dev]
                dev_allocs.sort(key=lambda a: a.priority, reverse=True)

                total = sum(a.duration_days for a in dev_allocs)
                idx = len(dev_allocs) - 1

                while total > dev.capacity_days_per_year and idx >= 0:
                    total -= dev_allocs[idx].duration_days
                    allocations.remove(dev_allocs[idx])
                    corrections += 1
                    idx -= 1

        return corrections
```

### 4.3 Convergence Monitoring
**Best for:** Understanding stabilization behavior, detecting infinite loops.

```python
class ConvergenceMonitor:
    """Monitors stabilization progress for early termination."""

    def __init__(self, max_passes: int = 10, stall_threshold: int = 3):
        self.max_passes = max_passes
        self.stall_threshold = stall_threshold  # Passes with no improvement
        self.pass_count = 0
        self.issue_counts = []
        self.stall_count = 0

    def record_pass(self, issue_count: int) -> Tuple[bool, str]:
        """Record result of stabilization pass.

        Returns:
            (should_continue: bool, reason: str)
        """
        self.pass_count += 1
        self.issue_counts.append(issue_count)

        # Check for convergence to fixed point
        if issue_count == 0:
            return False, "Fixed point reached (no issues)"

        # Check for max passes
        if self.pass_count >= self.max_passes:
            return False, f"Maximum passes reached ({self.max_passes})"

        # Check for stalling
        if len(self.issue_counts) > 1:
            if self.issue_counts[-1] >= self.issue_counts[-2]:
                self.stall_count += 1

                if self.stall_count >= self.stall_threshold:
                    return False, (
                        f"Stalling detected: "
                        f"no improvement for {self.stall_count} passes"
                    )
            else:
                self.stall_count = 0  # Reset on progress

        return True, "Continue stabilization"

    def get_summary(self) -> Dict[str, Any]:
        """Get convergence summary."""
        return {
            'total_passes': self.pass_count,
            'initial_issues': self.issue_counts[0] if self.issue_counts else 0,
            'final_issues': self.issue_counts[-1] if self.issue_counts else 0,
            'improvement': (
                self.issue_counts[0] - self.issue_counts[-1]
                if self.issue_counts else 0
            ),
            'convergence_rate': self._calculate_convergence_rate()
        }

    def _calculate_convergence_rate(self) -> float:
        """Calculate how quickly issues are being resolved.

        Returns:
            Average issues resolved per pass
        """
        if len(self.issue_counts) < 2:
            return 0.0

        improvements = []
        for i in range(1, len(self.issue_counts)):
            improvement = max(0, self.issue_counts[i-1] - self.issue_counts[i])
            improvements.append(improvement)

        return sum(improvements) / len(improvements) if improvements else 0.0
```

---

## 5. Integration: Complete Allocation Workflow

### 5.1 Combined Algorithm Pattern
**Best for:** Production allocation systems requiring robustness.

```python
class AllocationService:
    """Complete allocation service with all patterns integrated."""

    def __init__(self,
                 developers: List[Developer],
                 max_allocation_passes: int = 20,
                 max_stabilization_passes: int = 10):
        self.developers = developers
        self.allocator = CountBasedAllocator(developers)
        self.conflict_detector = ConflictDetector()
        self.progress_tracker = ProgressTracker(max_passes=max_allocation_passes)
        self.stabilizer = StabilizationEngine(max_stabilization_passes)
        self.convergence_monitor = ConvergenceMonitor(
            max_passes=max_stabilization_passes
        )

    def allocate_stories(self,
                        stories: List[Story],
                        seed: Optional[int] = None) -> AllocationResult:
        """Complete allocation workflow.

        Steps:
        1. Phase 1: Initial allocation (load balancing)
        2. Phase 2: Conflict detection and resolution
        3. Phase 3: Stabilization (fixed-point iteration)
        4. Phase 4: Final validation
        """
        result = AllocationResult()
        allocations = []

        # Phase 1: Initial Allocation
        logger.info(f"Phase 1: Allocating {len(stories)} stories")
        unallocated = set(stories)
        seed_counter = seed or 0

        while unallocated:
            self.progress_tracker.start_pass()

            newly_allocated = []
            for story in list(unallocated):
                try:
                    dev = self.allocator.allocate_next(
                        random_seed=seed_counter
                    )
                    seed_counter += 1

                    # Check for conflicts
                    temp_alloc = Allocation(story=story, developer=dev)
                    conflicts = self.conflict_detector.find_conflicts(dev, temp_alloc)

                    if not conflicts:
                        allocations.append(temp_alloc)
                        newly_allocated.append(story)
                        self.progress_tracker.record_allocation()

                except Exception as e:
                    logger.debug(f"Could not allocate {story.id}: {e}")

            for story in newly_allocated:
                unallocated.discard(story)

            if self.progress_tracker.is_complete:
                break

        result.allocations = allocations
        result.unallocated_stories = list(unallocated)
        logger.info(
            f"Phase 1 complete: {len(allocations)} allocated, "
            f"{len(unallocated)} unallocated"
        )

        # Phase 2: Conflict Resolution
        logger.info("Phase 2: Resolving conflicts")
        try:
            # Auto-resolve conflicts if any
            if hasattr(self, 'resolver'):
                pass  # Conflicts handled in Phase 1
        except Exception as e:
            logger.warning(f"Conflict resolution encountered issue: {e}")

        # Phase 3: Stabilization
        logger.info("Phase 3: Stabilizing allocations")
        stabilization_result = self.stabilizer.stabilize(allocations, self.developers)
        result.stabilization_passes = stabilization_result.passes

        # Phase 4: Final Validation
        logger.info("Phase 4: Final validation")
        final_issues = AllocationValidator.validate_allocation_state(
            allocations,
            self.developers
        )

        if final_issues:
            logger.warning(
                f"Final validation found {len(final_issues)} issues: "
                f"{[i.type for i in final_issues]}"
            )
            result.warnings.append(f"Final validation found {len(final_issues)} issues")
        else:
            logger.info("Final validation passed")

        return result
```

---

## 6. Key Takeaways

### Algorithm Selection
- **Round-robin**: Simple, stateless, fair. Use when complexity low.
- **Count-based**: Better load balancing. Use for most cases.
- **Weighted**: Complex requirements. Use for skill/capacity matching.

### Conflict Handling
- **Detection first**: Always validate before allocating.
- **Cascading resolution**: Resolve conflicts via rescheduling automatically.
- **Graceful degradation**: Relax constraints rather than failing.

### Deadlock Prevention
- **Progress tracking**: Monitor iterations to detect stalls.
- **Circular dependency detection**: Check for impossible situations.
- **Fallback strategies**: Always have alternative allocation strategies.

### Stabilization
- **Fixed-point iteration**: Repeat validation until stable.
- **Convergence monitoring**: Track progress toward stability.
- **Issue-specific corrections**: Fix detected problems deterministically.

### Testing Strategy
- **Seeded randomness**: Use seeds for reproducible tests.
- **Deterministic tie-breaking**: Always specify how ties are broken.
- **Phase-by-phase validation**: Validate each phase independently.
