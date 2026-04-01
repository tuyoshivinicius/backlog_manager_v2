"""Check dependency structure to diagnose deadlocks."""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.common.db_path import (
    add_db_path_argument,
    get_analysis_db_path,
    log_database_info,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Check dependency structure to diagnose deadlocks.",
        prog="check_deps.py",
    )
    add_db_path_argument(parser)
    return parser.parse_args()


async def check_deps(db_path: Path):
    """Check dependency structure.

    Args:
        db_path: Path to the database file.
    """
    from backlog_manager.infrastructure.database.repositories import (
        SQLiteFeatureRepository,
        SQLiteStoryDependencyRepository,
        SQLiteStoryRepository,
    )
    from backlog_manager.infrastructure.database.sqlite_connection import (
        create_connection,
    )

    conn = await create_connection(db_path)
    try:
        story_repo = SQLiteStoryRepository(conn)
        dep_repo = SQLiteStoryDependencyRepository(conn)
        feature_repo = SQLiteFeatureRepository(conn)

        stories = await story_repo.get_all()
        features = await feature_repo.get_all()
        deps = await dep_repo.get_all_dependencies()

        # Map story to wave
        feature_wave = {f.id: f.wave for f in features}
        story_wave = {s.id: feature_wave.get(s.feature_id, 0) for s in stories}

        # Check stories with developer_id set
        stories_with_dev = [s for s in stories if s.developer_id is not None]
        stories_without_dev = [s for s in stories if s.developer_id is None]
        print(f"Stories with developer: {len(stories_with_dev)}")
        print(f"Stories without developer: {len(stories_without_dev)}")

        # Check AUTH-021 and AUTH-025
        print("\n=== BLOCKED WAVE 1 STORIES ===")
        for story_id in ["AUTH-021", "AUTH-025"]:
            wave = story_wave.get(story_id, "N/A")
            story_deps = [d[1] for d in deps if d[0] == story_id]
            print(f"{story_id} (wave {wave}): depends on {story_deps}")
            for dep_id in story_deps:
                dep_wave = story_wave.get(dep_id, "N/A")
                # Check if dependency has developer
                dep_story = next((s for s in stories if s.id == dep_id), None)
                has_dev = dep_story.developer_id if dep_story else "N/A"
                print(f"  -> {dep_id} (wave {dep_wave}, developer_id={has_dev})")

        # Count cross-wave dependencies
        cross_wave = 0
        same_wave = 0
        for dependent_id, dependency_id in deps:
            dep_wave = story_wave.get(dependent_id, 0)
            target_wave = story_wave.get(dependency_id, 0)
            if dep_wave != target_wave:
                cross_wave += 1
            else:
                same_wave += 1

        print("\n=== DEPENDENCY STATS ===")
        print(f"Total deps: {len(deps)}")
        print(f"Same-wave deps: {same_wave}")
        print(f"Cross-wave deps: {cross_wave}")

        # Check wave 1 stories - do they all have dependencies?
        print("\n=== WAVE 1 ANALYSIS ===")
        wave1_stories = [s for s in stories if story_wave.get(s.id) == 1]
        print(f"Total wave 1 stories: {len(wave1_stories)}")

        wave1_with_deps = 0
        wave1_without_deps = 0
        for s in wave1_stories:
            story_deps = [d[1] for d in deps if d[0] == s.id]
            if story_deps:
                wave1_with_deps += 1
            else:
                wave1_without_deps += 1
                print(f"  Wave 1 story without deps: {s.id}")

        print(f"Wave 1 with deps: {wave1_with_deps}")
        print(f"Wave 1 without deps: {wave1_without_deps}")

    finally:
        await conn.close()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    # Resolve database path
    db_path = get_analysis_db_path(args.db_path)

    # Log database info
    log_database_info(db_path)

    # Run check
    asyncio.run(check_deps(db_path))


if __name__ == "__main__":
    main()
