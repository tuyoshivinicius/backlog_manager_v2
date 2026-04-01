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
        default=True,
        help="Persist allocated stories to the database (default: True)",
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Do not persist allocated stories (dry-run mode)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with detailed diagnostics",
    )
    parser.add_argument(
        "--allocation-criteria",
        default="LOAD_BALANCING",
        choices=["LOAD_BALANCING", "DEPENDENCY_OWNER"],
        help="Allocation criteria: LOAD_BALANCING or DEPENDENCY_OWNER (default: LOAD_BALANCING)",
    )
    return parser.parse_args()


def diagnose_deadlock(
    original_stories: list,
    allocated_stories: list,
    blocked_story_ids: list[str],
    dependencies: list,
    features: list,
    developers: list,
    verbose: bool = False,
) -> dict[str, Any]:
    """Collect raw diagnostic data about blocked stories.

    Returns factual observations without conclusions or classifications.
    The analysis of root cause should be done by the operator based on
    the raw data presented.

    Args:
        original_stories: List of all stories before allocation.
        allocated_stories: List of stories that were successfully allocated.
        blocked_story_ids: List of story IDs that were blocked (from warnings).
        dependencies: List of all dependencies.
        features: List of all features.
        developers: List of all developers.
        verbose: If True, include additional context.

    Returns:
        dict with raw diagnostic data.
    """
    # Build lookup maps
    allocated_ids = {s.id for s in allocated_stories}
    original_map = {s.id: s for s in original_stories}
    feature_wave = {f.id: f.wave for f in features}
    story_wave = {s.id: feature_wave.get(s.feature_id, 0) for s in original_stories}

    # Build dependency graph
    dep_map: dict[str, list[str]] = {}
    for story_id, depends_on_id in dependencies:
        if story_id not in dep_map:
            dep_map[story_id] = []
        dep_map[story_id].append(depends_on_id)

    # Get blocked stories (from warnings or by checking allocation result)
    if not blocked_story_ids:
        blocked_story_ids = [
            s.id
            for s in original_stories
            if s.id not in allocated_ids
            and s.start_date is not None
            and s.end_date is not None
        ]

    # Collect raw data for each blocked story
    blocked_stories_data = []
    for story_id in blocked_story_ids:
        story = original_map.get(story_id)
        if not story:
            continue

        story_data: dict[str, Any] = {
            "story_id": story_id,
            "wave": story_wave.get(story_id, 0),
        }

        # Period info
        if story.start_date and story.end_date:
            story_data["period"] = f"{story.start_date} - {story.end_date}"
        else:
            story_data["period"] = None
            story_data["missing_dates"] = True

        # Dependencies info
        story_deps = dep_map.get(story_id, [])
        if story_deps:
            deps_info = []
            for dep_id in story_deps:
                dep_allocated = dep_id in allocated_ids
                deps_info.append(
                    {
                        "dependency_id": dep_id,
                        "allocated": dep_allocated,
                        "wave": story_wave.get(dep_id, 0),
                    }
                )
            story_data["dependencies"] = deps_info
            story_data["all_dependencies_allocated"] = all(
                d["allocated"] for d in deps_info
            )
        else:
            story_data["dependencies"] = []
            story_data["all_dependencies_allocated"] = True

        # Developer availability info (only if story has dates)
        if story.start_date and story.end_date:
            available_devs = []
            busy_devs = []

            for dev in developers:
                if dev.id is None:
                    continue

                dev_stories = [s for s in allocated_stories if s.developer_id == dev.id]
                has_conflict = False
                conflicting_story_id = None

                for dev_story in dev_stories:
                    if (
                        dev_story.start_date
                        and dev_story.end_date
                        and dev_story.start_date <= story.end_date
                        and dev_story.end_date >= story.start_date
                    ):
                        has_conflict = True
                        conflicting_story_id = dev_story.id
                        break

                if has_conflict:
                    busy_devs.append(
                        {
                            "dev_id": dev.id,
                            "dev_name": dev.name,
                            "conflicting_story": conflicting_story_id,
                        }
                    )
                else:
                    available_devs.append(
                        {
                            "dev_id": dev.id,
                            "dev_name": dev.name,
                        }
                    )

            story_data["devs_available_in_period"] = available_devs
            story_data["devs_busy_in_period"] = busy_devs

        blocked_stories_data.append(story_data)

    # Check for circular dependencies
    def find_cycle(start: str, gray: set, black: set, path: list) -> list | None:
        if start in black:
            return None
        if start in gray:
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
    black_global = set()
    for story_id in dep_map:
        if story_id not in checked and story_id not in black_global:
            cycle = find_cycle(story_id, set(), black_global, [])
            if cycle:
                cycle_key = tuple(sorted(cycle))
                if cycle_key not in checked:
                    cycles_found.append(" -> ".join(cycle + [cycle[0]]))
                    checked.add(cycle_key)

    # Build summary counts (facts, not interpretations)
    summary = {
        "total_blocked": len(blocked_story_ids),
        "with_missing_dates": sum(
            1 for s in blocked_stories_data if s.get("missing_dates")
        ),
        "with_unallocated_dependencies": sum(
            1 for s in blocked_stories_data if not s.get("all_dependencies_allocated")
        ),
        "with_available_devs": sum(
            1
            for s in blocked_stories_data
            if s.get("devs_available_in_period")
            and len(s["devs_available_in_period"]) > 0
        ),
        "with_all_devs_busy": sum(
            1
            for s in blocked_stories_data
            if s.get("devs_busy_in_period")
            and len(s.get("devs_available_in_period", [])) == 0
        ),
        "circular_dependencies_detected": len(cycles_found),
    }

    # Detect contradictions (scenarios that indicate algorithm bugs)
    contradictions = []
    for story_data in blocked_stories_data:
        available_devs = story_data.get("devs_available_in_period", [])
        deps_ok = story_data.get("all_dependencies_allocated", False)
        has_dates = story_data.get("period") is not None

        # If devs are available, dependencies are OK, and story has dates,
        # but story wasn't allocated - this is a contradiction (algorithm bug)
        if len(available_devs) > 0 and deps_ok and has_dates:
            contradictions.append(
                {
                    "story_id": story_data["story_id"],
                    "type": "DEVS_AVAILABLE_BUT_NOT_ALLOCATED",
                    "available_devs": len(available_devs),
                    "message": "Ha desenvolvedores disponiveis mas story nao foi alocada - provavel BUG no algoritmo",
                }
            )

    result: dict[str, Any] = {
        "blocked_stories": blocked_stories_data,
        "circular_dependencies": cycles_found if cycles_found else None,
        "summary": summary,
    }

    # Add contradictions if any found
    if contradictions:
        result["contradictions"] = contradictions
        result["has_algorithm_bug"] = True

    if verbose:
        result["context"] = {
            "total_stories": len(original_stories),
            "total_allocated": len(allocated_stories),
            "total_developers": len(developers),
            "total_dependencies": len(dependencies),
        }

    return result


async def run_allocation(
    db_path: Path,
    diagnose: bool = False,
    output_json: bool = False,
    persist: bool = False,
    verbose: bool = False,
    allocation_criteria: str = "LOAD_BALANCING",
):
    """Run allocation and extract metrics.

    Args:
        db_path: Path to the database file.
        diagnose: If True, run deadlock diagnosis when deadlocks detected.
        output_json: If True, output metrics in JSON format.
        persist: If True, save allocated stories to the database.
        verbose: If True, include detailed diagnostic info.
        allocation_criteria: Allocation criteria (LOAD_BALANCING or DEPENDENCY_OWNER).
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

        # Build AllocationConfig with selected criteria
        criteria = AllocationCriteria(allocation_criteria.lower())
        config = AllocationConfig(
            velocity=2.0,
            project_start_date=date.today(),
            max_idle_days=3,
            allocation_criteria=criteria,
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

        # Extract blocked story IDs from warnings
        blocked_story_ids: list[str] = []
        for warning in result.warnings:
            if hasattr(warning, "blocked_stories"):
                blocked_story_ids.extend(warning.blocked_stories)

        # Run deadlock diagnosis if requested and deadlocks were detected
        diagnosis_result = None
        if diagnose and metrics.deadlocks_detected > 0:
            diagnosis_result = diagnose_deadlock(
                original_stories=list(stories),
                allocated_stories=result.allocated_stories,
                blocked_story_ids=blocked_story_ids,
                dependencies=list(dependencies),
                features=list(features),
                developers=list(developers),
                verbose=verbose,
            )

        if output_json:
            output = {
                "allocation_criteria": allocation_criteria,
                "metrics": metrics_dict,
                "database": str(db_path),
                "persisted": persist,
            }
            if persist:
                output["persisted_count"] = len(result.allocated_stories)
            if blocked_story_ids:
                output["blocked_story_ids"] = blocked_story_ids
            if diagnosis_result:
                output["diagnosis"] = diagnosis_result
            print(json.dumps(output, indent=2))
        else:
            print()
            print("=" * 60)
            print("METRICAS DE ALOCACAO")
            print("=" * 60)
            print(f"allocation_criteria: {allocation_criteria}")
            for key, value in metrics_dict.items():
                print(f"{key}: {value}")
            print("=" * 60)

            if blocked_story_ids:
                print()
                print("=" * 60)
                print("BLOCKED STORIES")
                print("=" * 60)
                print(f"Count: {len(blocked_story_ids)}")
                print(f"IDs: {', '.join(blocked_story_ids[:10])}")
                if len(blocked_story_ids) > 10:
                    print(f"  ... and {len(blocked_story_ids) - 10} more")
                print("=" * 60)

            if diagnosis_result:
                print()
                print("=" * 60)
                print("DIAGNOSTIC DATA")
                print("=" * 60)

                # Summary
                summary = diagnosis_result.get("summary", {})
                print("Summary:")
                print(f"  Total blocked: {summary.get('total_blocked', 0)}")
                print(f"  With missing dates: {summary.get('with_missing_dates', 0)}")
                print(
                    f"  With unallocated dependencies: {summary.get('with_unallocated_dependencies', 0)}"
                )
                print(f"  With available devs: {summary.get('with_available_devs', 0)}")
                print(f"  With all devs busy: {summary.get('with_all_devs_busy', 0)}")
                print(
                    f"  Circular dependencies: {summary.get('circular_dependencies_detected', 0)}"
                )

                # Circular dependencies if any
                if diagnosis_result.get("circular_dependencies"):
                    print()
                    print("Circular Dependencies:")
                    for cycle in diagnosis_result["circular_dependencies"]:
                        print(f"  - {cycle}")

                # Blocked stories details
                print()
                print("Blocked Stories Details:")
                for story_data in diagnosis_result.get("blocked_stories", []):
                    print(
                        f"  [{story_data['story_id']}] wave={story_data.get('wave', '?')}"
                    )
                    print(f"    Period: {story_data.get('period', 'N/A')}")

                    # Dependencies
                    deps = story_data.get("dependencies", [])
                    if deps:
                        all_allocated = story_data.get(
                            "all_dependencies_allocated", False
                        )
                        print(
                            f"    Dependencies: {len(deps)} (all allocated: {all_allocated})"
                        )
                        for dep in deps[:3]:
                            status = (
                                "allocated" if dep["allocated"] else "NOT allocated"
                            )
                            print(f"      - {dep['dependency_id']}: {status}")
                        if len(deps) > 3:
                            print(f"      ... and {len(deps) - 3} more")

                    # Dev availability
                    available = story_data.get("devs_available_in_period", [])
                    busy = story_data.get("devs_busy_in_period", [])
                    if available or busy:
                        print(
                            f"    Devs available: {len(available)}, Devs busy: {len(busy)}"
                        )
                        if available:
                            names = [d["dev_name"] for d in available[:5]]
                            print(f"      Available: {', '.join(names)}")
                        if busy:
                            for b in busy[:3]:
                                print(
                                    f"      Busy: {b['dev_name']} (conflict: {b['conflicting_story']})"
                                )

                    print()

                print("=" * 60)

                # Show contradictions if found (indicates algorithm bug)
                if diagnosis_result.get("contradictions"):
                    print()
                    print("!" * 60)
                    print("CONTRADICOES DETECTADAS (provavel BUG no algoritmo)")
                    print("!" * 60)
                    for contradiction in diagnosis_result["contradictions"]:
                        print(f"  Story: {contradiction['story_id']}")
                        print(f"  Tipo: {contradiction['type']}")
                        print(f"  Devs disponiveis: {contradiction['available_devs']}")
                        print(f"  {contradiction['message']}")
                        print()
                    print("!" * 60)

                if verbose and "context" in diagnosis_result:
                    print()
                    print("CONTEXT:")
                    for key, value in diagnosis_result["context"].items():
                        print(f"  {key}: {value}")

        return metrics
    finally:
        await conn.close()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    # Resolve database path
    db_path = get_analysis_db_path(args.db_path)

    # Determine persist mode (--no-persist overrides --persist)
    persist = args.persist and not args.no_persist

    # Log database info (unless JSON output)
    if not args.json:
        log_database_info(db_path)

    # Run allocation
    asyncio.run(
        run_allocation(
            db_path,
            diagnose=args.diagnose,
            output_json=args.json,
            persist=persist,
            verbose=args.verbose,
            allocation_criteria=args.allocation_criteria,
        )
    )


if __name__ == "__main__":
    main()
