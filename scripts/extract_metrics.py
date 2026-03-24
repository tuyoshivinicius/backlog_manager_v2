"""Script to extract allocation metrics for analysis."""

import argparse
import asyncio
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

# Add src to path for imports
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
        description="Extract allocation metrics for analysis.",
        prog="extract_metrics.py",
    )
    add_db_path_argument(parser)
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run deadlock diagnosis if deadlocks detected",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output metrics in JSON format",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist allocated stories to the database",
    )
    return parser.parse_args()


async def diagnose_deadlock(
    conn,
    stories: list,
    dependencies: list,
    features: list,
) -> dict[str, Any]:
    """Diagnose the cause of deadlocks.

    Args:
        conn: Database connection.
        stories: List of all stories.
        dependencies: List of all dependencies.
        features: List of all features.

    Returns:
        dict with diagnosis results.
    """
    causes: list[dict[str, Any]] = []

    # Build lookup maps
    story_map = {s.id: s for s in stories}
    feature_wave = {f.id: f.wave for f in features}
    story_wave = {s.id: feature_wave.get(s.feature_id, 0) for s in stories}

    # Check 1: Stories without dates
    stories_without_dates = [
        s.id for s in stories if s.start_date is None or s.end_date is None
    ]
    if stories_without_dates:
        causes.append(
            {
                "type": "MISSING_DATES",
                "count": len(stories_without_dates),
                "examples": stories_without_dates[:5],
                "fix": "Run seed_test_backlog.py --clean to regenerate data with dates",
            }
        )

    # Check 2: Unallocated stories with unallocated dependencies
    dep_map: dict[str, list[str]] = {}
    for story_id, depends_on_id in dependencies:
        if story_id not in dep_map:
            dep_map[story_id] = []
        dep_map[story_id].append(depends_on_id)

    blocked_stories = []
    for story in stories:
        if story.developer_id is not None:
            continue  # Already allocated
        story_deps = dep_map.get(story.id, [])
        for dep_id in story_deps:
            dep_story = story_map.get(dep_id)
            if dep_story and dep_story.developer_id is None:
                blocked_stories.append(
                    {
                        "story_id": story.id,
                        "blocked_by": dep_id,
                        "story_wave": story_wave.get(story.id, 0),
                        "dep_wave": story_wave.get(dep_id, 0),
                    }
                )
                break

    if blocked_stories:
        causes.append(
            {
                "type": "UNSATISFIED_DEPENDENCIES",
                "count": len(blocked_stories),
                "examples": blocked_stories[:5],
                "fix": "Allocate dependency stories first or remove blocking dependencies",
            }
        )

    # Check 3: Circular dependencies
    # Uses 3-state coloring: gray (in current path), black (fully processed)
    def find_cycle(start: str, gray: set, black: set, path: list) -> list | None:
        if start in black:
            return None  # Already fully processed, no cycle
        if start in gray:
            # Found cycle - start is in current path
            cycle_start = path.index(start)
            return path[cycle_start:]

        gray.add(start)
        path.append(start)

        for dep_id in dep_map.get(start, []):
            cycle = find_cycle(dep_id, gray, black, path)
            if cycle:
                return cycle

        path.pop()
        gray.remove(start)
        black.add(start)
        return None

    cycles_found = []
    checked = set()
    black_global = set()  # Track fully processed nodes across all searches
    for story_id in dep_map:
        if story_id not in checked and story_id not in black_global:
            cycle = find_cycle(story_id, set(), black_global, [])
            if cycle:
                cycle_key = tuple(sorted(cycle))
                if cycle_key not in checked:
                    cycles_found.append(cycle)
                    checked.add(cycle_key)

    if cycles_found:
        causes.append(
            {
                "type": "CIRCULAR_DEPENDENCIES",
                "count": len(cycles_found),
                "cycles": [" -> ".join(c + [c[0]]) for c in cycles_found[:3]],
                "fix": "Remove one dependency from each cycle to break the loop",
            }
        )

    # Check 4: Cross-wave dependencies blocking allocation
    cross_wave_blocking = []
    for story in stories:
        if story.developer_id is not None:
            continue
        story_w = story_wave.get(story.id, 0)
        for dep_id in dep_map.get(story.id, []):
            dep_story = story_map.get(dep_id)
            dep_w = story_wave.get(dep_id, 0)
            if dep_story and dep_story.developer_id is None and dep_w < story_w:
                cross_wave_blocking.append(
                    {
                        "story_id": story.id,
                        "story_wave": story_w,
                        "depends_on": dep_id,
                        "dep_wave": dep_w,
                    }
                )

    if cross_wave_blocking:
        causes.append(
            {
                "type": "CROSS_WAVE_BLOCKING",
                "count": len(cross_wave_blocking),
                "examples": cross_wave_blocking[:5],
                "fix": "Earlier wave stories must be allocated before later waves can proceed",
            }
        )

    # Determine primary cause
    primary_cause = causes[0]["type"] if causes else "UNKNOWN"

    return {
        "deadlock_diagnosis": True,
        "causes_found": len(causes),
        "primary_cause": primary_cause,
        "causes": causes,
    }


async def run_allocation(
    db_path: Path,
    diagnose: bool = False,
    output_json: bool = False,
    persist: bool = False,
):
    """Run allocation and extract metrics.

    Args:
        db_path: Path to the database file.
        diagnose: If True, run deadlock diagnosis when deadlocks detected.
        output_json: If True, output metrics in JSON format.
        persist: If True, save allocated stories to the database.
    """
    from backlog_manager.domain.services import (
        AllocationConfig,
        AllocationCriteria,
        AllocationService,
    )
    from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
    from backlog_manager.infrastructure.database.repositories import (
        SQLiteDeveloperRepository,
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
        dev_repo = SQLiteDeveloperRepository(conn)
        dep_repo = SQLiteStoryDependencyRepository(conn)
        feature_repo = SQLiteFeatureRepository(conn)

        stories = await story_repo.get_all()
        developers = await dev_repo.get_all()
        features = await feature_repo.get_all()
        dependencies = await dep_repo.get_all_dependencies()

        if not output_json:
            print(
                f"Stories: {len(stories)}, Developers: {len(developers)}, Dependencies: {len(dependencies)}"
            )

        # Build AllocationConfig
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date.today(),
            max_idle_days=3,
            allocation_criteria=AllocationCriteria.LOAD_BALANCING,
            random_seed=42,
        )

        # Execute allocation (synchronous domain service)
        result = AllocationService.allocate_stories(
            stories=list(stories),
            developers=list(developers),
            dependencies=list(dependencies),
            features=list(features),
            holidays=BRAZILIAN_HOLIDAYS_2026_2028,
            config=config,
        )

        # Persist allocated stories if requested
        if persist and result.allocated_stories:
            for story in result.allocated_stories:
                await story_repo.update(story)
            await conn.commit()
            if not output_json:
                print(f"Persisted {len(result.allocated_stories)} allocated stories")

        metrics = result.metrics

        # Calculate derived metric
        total_alloc = (
            metrics.allocations_by_dependency_owner
            + metrics.allocations_by_load_balancing
        )
        skill_match_ratio = (
            metrics.allocations_by_dependency_owner / total_alloc
            if total_alloc > 0
            else 0
        )

        # Build metrics dict for JSON output
        metrics_dict = {
            "total_time_seconds": round(metrics.total_time_seconds, 4),
            "stories_processed": metrics.stories_processed,
            "stories_allocated": metrics.stories_allocated,
            "waves_processed": metrics.waves_processed,
            "total_iterations": metrics.total_iterations,
            "iterations_per_wave": dict(metrics.iterations_per_wave),
            "allocations_by_dependency_owner": metrics.allocations_by_dependency_owner,
            "allocations_by_load_balancing": metrics.allocations_by_load_balancing,
            "deadlocks_detected": metrics.deadlocks_detected,
            "date_adjustments": metrics.date_adjustments,
            "validation_reallocations": metrics.validation_reallocations,
            "validation_dependency_fixes": metrics.validation_dependency_fixes,
            "validation_conflict_fixes": metrics.validation_conflict_fixes,
            "max_idle_violations_detected": metrics.max_idle_violations_detected,
            "max_idle_violations_fixed": metrics.max_idle_violations_fixed,
            "failed_reallocations": metrics.failed_reallocations,
            "skill_match_ratio": round(skill_match_ratio, 4),
        }

        # Run deadlock diagnosis if requested and deadlocks were detected
        diagnosis_result = None
        if diagnose and metrics.deadlocks_detected > 0:
            diagnosis_result = await diagnose_deadlock(
                conn, list(stories), list(dependencies), list(features)
            )

        if output_json:
            output = {
                "metrics": metrics_dict,
                "database": str(db_path),
                "persisted": persist,
            }
            if persist:
                output["persisted_count"] = len(result.allocated_stories)
            if diagnosis_result:
                output["diagnosis"] = diagnosis_result
            print(json.dumps(output, indent=2))
        else:
            print()
            print("=" * 60)
            print("METRICAS DE ALOCACAO")
            print("=" * 60)
            for key, value in metrics_dict.items():
                print(f"{key}: {value}")
            print("=" * 60)

            if diagnosis_result:
                print()
                print("=" * 60)
                print("DEADLOCK DIAGNOSIS")
                print("=" * 60)
                print(f"Primary cause: {diagnosis_result['primary_cause']}")
                print(f"Total causes found: {diagnosis_result['causes_found']}")
                print()
                for cause in diagnosis_result["causes"]:
                    print(f"[{cause['type']}] Count: {cause['count']}")
                    if "examples" in cause:
                        print(f"  Examples: {cause['examples'][:3]}")
                    if "cycles" in cause:
                        print(f"  Cycles: {cause['cycles']}")
                    print(f"  Fix: {cause['fix']}")
                    print()
                print("=" * 60)

        return metrics
    finally:
        await conn.close()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    # Resolve database path
    db_path = get_analysis_db_path(args.db_path)

    # Log database info (unless JSON output)
    if not args.json:
        log_database_info(db_path)

    # Run allocation
    asyncio.run(
        run_allocation(
            db_path,
            diagnose=args.diagnose,
            output_json=args.json,
            persist=args.persist,
        )
    )


if __name__ == "__main__":
    main()
