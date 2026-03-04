"""Factory functions for E2E test data generation.

This module provides factory functions for creating test data with
customizable parameters, enabling flexible test scenarios without
code duplication.
"""

from __future__ import annotations

from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


def create_stories(
    count: int = 5,
    component: str = "TEST",
    with_dependencies: bool = False,
    story_points: int = 5,
    feature_id: int | None = None,
    start_priority: int = 1,
) -> list[Story]:
    """Create multiple stories for testing.

    Args:
        count: Number of stories to create.
        component: Component prefix for story IDs.
        with_dependencies: If True, creates dependency chain (S-002 depends on S-001).
        story_points: Story points for each story (3, 5, 8, or 13).
        feature_id: Optional feature ID to assign to all stories.
        start_priority: Starting priority number.

    Returns:
        List of Story instances.

    Example:
        # Create 10 stories with dependencies
        stories = create_stories(count=10, with_dependencies=True)

        # Create stories for a specific feature
        stories = create_stories(count=5, feature_id=1)
    """
    stories = []
    for i in range(1, count + 1):
        story = Story(
            id=f"{component}-{i:03d}",
            component=component,
            name=f"Historia Teste {i}",
            story_points=StoryPoint(story_points),
            priority=start_priority + i - 1,
            status=StoryStatus.BACKLOG,
            feature_id=feature_id,
        )
        stories.append(story)

    return stories


def create_stories_with_dependencies(stories: list[Story]) -> list[Story]:
    """Add dependency chain to a list of stories.

    Creates a linear dependency chain where each story depends on
    the previous one (S-002 depends on S-001, etc.).

    Args:
        stories: List of stories to add dependencies to.

    Returns:
        The same list with dependencies added.

    Note:
        Modifies stories in place and returns them for chaining.
    """
    # Note: Dependencies are stored in Story_Dependency table,
    # not directly on the Story entity in this architecture.
    # This function returns stories that can then have their
    # dependencies added via the dependency repository.
    return stories


def get_dependency_pairs(stories: list[Story]) -> list[tuple[str, str]]:
    """Generate dependency pairs for a list of stories.

    Creates a linear dependency chain where each story depends on
    the previous one.

    Args:
        stories: List of stories to create dependency pairs for.

    Returns:
        List of (story_id, depends_on_id) tuples.

    Example:
        stories = create_stories(count=5)
        pairs = get_dependency_pairs(stories)
        # Returns: [("TEST-002", "TEST-001"), ("TEST-003", "TEST-002"), ...]
    """
    pairs = []
    for i in range(1, len(stories)):
        pairs.append((stories[i].id, stories[i - 1].id))
    return pairs


def create_developers(count: int = 3) -> list[Developer]:
    """Create multiple developers for testing.

    Args:
        count: Number of developers to create.

    Returns:
        List of Developer instances (without IDs assigned).

    Example:
        developers = create_developers(count=5)
    """
    return [Developer(name=f"Dev {i}") for i in range(1, count + 1)]


def create_features(
    count: int = 2,
    waves: list[int] | None = None,
) -> list[Feature]:
    """Create multiple features for testing.

    Args:
        count: Number of features to create.
        waves: Optional list of wave numbers. If not provided,
               waves will be sequential (1, 2, 3, ...).

    Returns:
        List of Feature instances (without IDs assigned).

    Example:
        # Create features with default waves
        features = create_features(count=3)  # waves 1, 2, 3

        # Create features with specific waves
        features = create_features(waves=[1, 3, 5])  # 3 features
    """
    if waves is None:
        waves = list(range(1, count + 1))

    return [Feature(name=f"Feature {i + 1}", wave=wave) for i, wave in enumerate(waves)]


def create_cyclic_graph(
    node_count: int = 50,
    cycle_at: int | None = None,
    component: str = "CYCLE",
) -> tuple[list[Story], list[tuple[str, str]]]:
    """Create stories with a cyclic dependency graph.

    Creates a chain of stories where the last story (or story at cycle_at)
    depends on the first, creating a cycle.

    Args:
        node_count: Number of stories (nodes) in the graph.
        cycle_at: Index where cycle closes back to first node.
                  If None, uses the last node.
        component: Component prefix for story IDs.

    Returns:
        Tuple of (stories, dependency_pairs) where dependency_pairs
        includes the cycle-closing dependency.

    Example:
        # Create 50-node graph with cycle
        stories, deps = create_cyclic_graph(50)
        # deps[-1] will be ("CYCLE-050", "CYCLE-001") - the cycle

        # Create graph with cycle at position 25
        stories, deps = create_cyclic_graph(50, cycle_at=25)
    """
    stories = create_stories(count=node_count, component=component)

    # Create linear dependencies
    dependencies = get_dependency_pairs(stories)

    # Add cycle-closing dependency
    if cycle_at is None:
        cycle_at = node_count - 1

    # The story at cycle_at depends on the first story, creating a cycle
    cycle_story = stories[cycle_at]
    first_story = stories[0]
    dependencies.append((cycle_story.id, first_story.id))

    return stories, dependencies


def create_unbalanced_stories(
    large_sp: int = 13,
    small_sp: int = 3,
    small_count: int = 4,
    component: str = "BAL",
) -> list[Story]:
    """Create stories with unbalanced story points for balancing tests.

    Creates one large story followed by multiple small stories,
    useful for testing load balancing algorithms.

    Args:
        large_sp: Story points for the large story.
        small_sp: Story points for small stories.
        small_count: Number of small stories.
        component: Component prefix for story IDs.

    Returns:
        List of Story instances with unbalanced points.

    Example:
        # Create 1x13SP + 4x3SP stories for CT-005
        stories = create_unbalanced_stories(13, 3, 4)
    """
    stories = []

    # Large story
    stories.append(
        Story(
            id=f"{component}-001",
            component=component,
            name="Historia Grande",
            story_points=StoryPoint(large_sp),
            priority=1,
            status=StoryStatus.BACKLOG,
        )
    )

    # Small stories
    for i in range(2, small_count + 2):
        stories.append(
            Story(
                id=f"{component}-{i:03d}",
                component=component,
                name=f"Historia Pequena {i - 1}",
                story_points=StoryPoint(small_sp),
                priority=i,
                status=StoryStatus.BACKLOG,
            )
        )

    return stories
