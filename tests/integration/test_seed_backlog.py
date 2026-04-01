"""Integration tests for seed_test_backlog script."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite
import pytest

# Add src and scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from seed_test_backlog import seed_database

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_seed.db"


@pytest.mark.asyncio
async def test_seed_creates_expected_entities(temp_db_path: Path) -> None:
    """Test that seed creates expected counts of all entities.

    Verifies:
    - 7 developers created
    - 7 features created (one per wave)
    - 150-200 stories created
    - 80-120 dependencies created
    - Story IDs match COMPONENTE-NNN format (FR-012)
    - All stories have status=BACKLOG and developer_id=NULL (FR-013)
    """
    # Run seed
    result = await seed_database(db_path=temp_db_path)

    # Verify counts
    assert result["developers"] == 7
    assert result["features"] == 7
    assert 150 <= result["stories"] <= 200
    assert 80 <= result["dependencies"] <= 120

    # Verify in database
    conn = await aiosqlite.connect(temp_db_path)
    try:
        # Check developers
        cursor = await conn.execute("SELECT COUNT(*) FROM Developer")
        row = await cursor.fetchone()
        assert row[0] == 7

        # Check features
        cursor = await conn.execute("SELECT COUNT(*) FROM Feature")
        row = await cursor.fetchone()
        assert row[0] == 7

        # Check stories
        cursor = await conn.execute("SELECT COUNT(*) FROM Story")
        row = await cursor.fetchone()
        story_count = row[0]
        assert 150 <= story_count <= 200

        # Check dependencies
        cursor = await conn.execute("SELECT COUNT(*) FROM Story_Dependency")
        row = await cursor.fetchone()
        dep_count = row[0]
        assert 80 <= dep_count <= 120

        # Verify story ID format (FR-012): COMPONENTE-NNN
        cursor = await conn.execute("SELECT id FROM Story")
        rows = await cursor.fetchall()
        pattern = re.compile(r"^[A-Z]+-\d{3}$")
        for row in rows:
            story_id = row[0]
            assert pattern.match(story_id), f"Invalid story ID format: {story_id}"

        # Verify status=BACKLOG and developer_id=NULL (FR-013)
        cursor = await conn.execute(
            "SELECT id, status, developer_id FROM Story WHERE status != 'BACKLOG' OR developer_id IS NOT NULL"
        )
        invalid_stories = await cursor.fetchall()
        assert (
            len(invalid_stories) == 0
        ), f"Stories with invalid status or developer: {invalid_stories}"

    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_no_cycles_in_dependencies(temp_db_path: Path) -> None:
    """Test that generated dependencies form a DAG (no cycles).

    Uses DFS-based cycle detection algorithm.
    """
    await seed_database(db_path=temp_db_path)

    conn = await aiosqlite.connect(temp_db_path)
    try:
        # Build adjacency list
        cursor = await conn.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency"
        )
        rows = await cursor.fetchall()

        # Graph: story -> list of dependencies (stories it depends on)
        graph: dict[str, list[str]] = defaultdict(list)
        all_nodes: set[str] = set()
        for story_id, depends_on_id in rows:
            graph[story_id].append(depends_on_id)
            all_nodes.add(story_id)
            all_nodes.add(depends_on_id)

        # DFS-based cycle detection
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = dict.fromkeys(all_nodes, WHITE)

        def has_cycle_from(node: str) -> bool:
            """DFS to detect cycle starting from node."""
            color[node] = GRAY
            for neighbor in graph.get(node, []):
                if color[neighbor] == GRAY:
                    # Back edge found - cycle detected
                    return True
                if color[neighbor] == WHITE and has_cycle_from(neighbor):
                    return True
            color[node] = BLACK
            return False

        # Check for cycles from each unvisited node
        for node in all_nodes:
            if color[node] == WHITE:
                assert not has_cycle_from(node), f"Cycle detected starting from {node}"

    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_wave_rules_respected(temp_db_path: Path) -> None:
    """Test that inter-wave dependencies only point to earlier waves.

    A story in wave N can only depend on stories from waves 1..N.
    """
    await seed_database(db_path=temp_db_path)

    conn = await aiosqlite.connect(temp_db_path)
    try:
        # Get wave for each story (through feature)
        cursor = await conn.execute(
            """
            SELECT s.id, f.wave
            FROM Story s
            JOIN Feature f ON s.feature_id = f.id
            """
        )
        story_waves = {row[0]: row[1] for row in await cursor.fetchall()}

        # Check all dependencies
        cursor = await conn.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency"
        )
        dependencies = await cursor.fetchall()

        for story_id, depends_on_id in dependencies:
            story_wave = story_waves.get(story_id)
            dep_wave = story_waves.get(depends_on_id)

            assert story_wave is not None, f"Story {story_id} has no wave"
            assert dep_wave is not None, f"Dependency {depends_on_id} has no wave"
            assert dep_wave <= story_wave, (
                f"Invalid dependency: {story_id} (wave {story_wave}) "
                f"depends on {depends_on_id} (wave {dep_wave})"
            )

    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_critical_scenarios(temp_db_path: Path) -> None:
    """Test that critical scenarios from FR-014 are present.

    Verifies:
    - At least one dependency chain crosses 3+ waves
    - At least one story has 3 dependencies
    - Wave density varies (PROD denser than REPORT)
    """
    await seed_database(db_path=temp_db_path)

    conn = await aiosqlite.connect(temp_db_path)
    try:
        # Get wave for each story
        cursor = await conn.execute(
            """
            SELECT s.id, f.wave
            FROM Story s
            JOIN Feature f ON s.feature_id = f.id
            """
        )
        story_waves = {row[0]: row[1] for row in await cursor.fetchall()}

        # Build dependency graph
        cursor = await conn.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency"
        )
        dependencies = await cursor.fetchall()

        graph: dict[str, list[str]] = defaultdict(list)
        reverse_graph: dict[str, list[str]] = defaultdict(list)
        dep_count_per_story: dict[str, int] = defaultdict(int)

        for story_id, depends_on_id in dependencies:
            graph[story_id].append(depends_on_id)
            reverse_graph[depends_on_id].append(story_id)
            dep_count_per_story[story_id] += 1

        # 1. Check for dependency chain crossing 3+ waves
        def get_chain_wave_span(start: str, visited: set[str] | None = None) -> int:
            """Get the wave span of the longest dependency chain from start."""
            if visited is None:
                visited = set()
            if start in visited:
                return 0
            visited.add(start)

            start_wave = story_waves.get(start, 0)
            max_span = 0

            for dep in graph.get(start, []):
                dep_span = get_chain_wave_span(dep, visited.copy())
                dep_wave = story_waves.get(dep, 0)
                span = abs(start_wave - dep_wave) + dep_span
                max_span = max(max_span, span)

            return max_span

        # Find longest chain
        max_wave_span = 0
        for story_id in story_waves:
            span = get_chain_wave_span(story_id)
            max_wave_span = max(max_wave_span, span)

        assert (
            max_wave_span >= 2
        ), f"No dependency chain crosses 3+ waves. Max span: {max_wave_span + 1}"

        # 2. Check that at least one story has 3 dependencies
        max_deps = max(dep_count_per_story.values()) if dep_count_per_story else 0
        assert max_deps >= 3, f"No story has 3 dependencies. Max: {max_deps}"

        # 3. Check wave density variation (PROD wave 3 vs REPORT wave 6)
        cursor = await conn.execute(
            """
            SELECT f.wave, COUNT(*) as story_count
            FROM Story s
            JOIN Feature f ON s.feature_id = f.id
            GROUP BY f.wave
            """
        )
        wave_counts = {row[0]: row[1] for row in await cursor.fetchall()}

        prod_count = wave_counts.get(3, 0)  # Wave 3 = PROD
        report_count = wave_counts.get(6, 0)  # Wave 6 = REPORT

        assert prod_count > report_count, (
            f"PROD wave should be denser than REPORT. "
            f"PROD: {prod_count}, REPORT: {report_count}"
        )

    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_clean_flag_removes_data(temp_db_path: Path) -> None:
    """Test that --clean flag properly removes existing data before seeding."""
    # First seed
    result1 = await seed_database(db_path=temp_db_path)
    assert result1["stories"] >= 150

    # Second seed without clean should fail
    with pytest.raises(RuntimeError, match="ja contem dados"):
        await seed_database(db_path=temp_db_path, clean=False)

    # Third seed with clean should succeed
    result3 = await seed_database(db_path=temp_db_path, clean=True)
    assert result3["stories"] >= 150

    # Verify data was replaced (same counts due to reproducibility)
    conn = await aiosqlite.connect(temp_db_path)
    try:
        cursor = await conn.execute("SELECT COUNT(*) FROM Story")
        row = await cursor.fetchone()
        assert row[0] == result3["stories"]
    finally:
        await conn.close()


@pytest.mark.asyncio
async def test_reproducibility(temp_db_path: Path, tmp_path: Path) -> None:
    """Test that two executions produce identical output."""
    db_path_1 = temp_db_path
    db_path_2 = tmp_path / "test_seed_2.db"

    # Run seed twice on different databases
    result1 = await seed_database(db_path=db_path_1)
    result2 = await seed_database(db_path=db_path_2)

    # Verify same counts
    assert result1 == result2

    # Verify same data
    conn1 = await aiosqlite.connect(db_path_1)
    conn2 = await aiosqlite.connect(db_path_2)
    try:
        # Compare developers
        cursor1 = await conn1.execute("SELECT name FROM Developer ORDER BY name")
        cursor2 = await conn2.execute("SELECT name FROM Developer ORDER BY name")
        devs1 = await cursor1.fetchall()
        devs2 = await cursor2.fetchall()
        assert devs1 == devs2

        # Compare stories (id, component, name, story_points, priority)
        cursor1 = await conn1.execute(
            "SELECT id, component, name, story_points, priority FROM Story ORDER BY id"
        )
        cursor2 = await conn2.execute(
            "SELECT id, component, name, story_points, priority FROM Story ORDER BY id"
        )
        stories1 = await cursor1.fetchall()
        stories2 = await cursor2.fetchall()
        assert stories1 == stories2

        # Compare dependencies
        cursor1 = await conn1.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency ORDER BY story_id, depends_on_id"
        )
        cursor2 = await conn2.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency ORDER BY story_id, depends_on_id"
        )
        deps1 = await cursor1.fetchall()
        deps2 = await cursor2.fetchall()
        assert deps1 == deps2

    finally:
        await conn1.close()
        await conn2.close()
