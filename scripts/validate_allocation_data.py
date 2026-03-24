"""Validate data integrity for allocation analysis.

This script performs pre-allocation validation to ensure data quality
and prevent incorrect diagnoses during allocation analysis.
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.common.db_path import (
    add_db_path_argument,
    get_analysis_db_path,
    log_database_info,
)


class ValidationResult(NamedTuple):
    """Result of a validation check."""

    passed: bool
    message: str
    fix_suggestion: str | None = None


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Validate data integrity for allocation analysis.",
        prog="validate_allocation_data.py",
    )
    add_db_path_argument(parser)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if any validation fails",
    )
    return parser.parse_args()


async def check_story_dates(conn) -> ValidationResult:
    """Check if all stories have start_date and end_date.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    cursor = await conn.execute(
        """
        SELECT COUNT(*) FROM Story
        WHERE start_date IS NULL OR end_date IS NULL
        """
    )
    row = await cursor.fetchone()
    count = row[0] if row else 0

    if count == 0:
        return ValidationResult(
            passed=True,
            message="All stories have dates",
        )

    # Get sample of stories without dates
    cursor = await conn.execute(
        """
        SELECT id, component, name FROM Story
        WHERE start_date IS NULL OR end_date IS NULL
        LIMIT 5
        """
    )
    samples = await cursor.fetchall()
    sample_ids = [row[0] for row in samples]

    return ValidationResult(
        passed=False,
        message=f"{count} stories missing dates (e.g., {', '.join(sample_ids)})",
        fix_suggestion="Run SchedulingService.calculate_schedule() or seed with --clean",
    )


async def check_developers(conn) -> ValidationResult:
    """Check if active developers exist.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    cursor = await conn.execute("SELECT COUNT(*) FROM Developer")
    row = await cursor.fetchone()
    count = row[0] if row else 0

    if count > 0:
        return ValidationResult(
            passed=True,
            message=f"{count} developers found",
        )

    return ValidationResult(
        passed=False,
        message="No developers found",
        fix_suggestion="Run seed_test_backlog.py --clean to create test data",
    )


async def check_dependencies(conn) -> ValidationResult:
    """Check if all dependencies point to existing stories.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    # Check for orphan dependencies (pointing to non-existent stories)
    cursor = await conn.execute(
        """
        SELECT sd.story_id, sd.depends_on_id
        FROM Story_Dependency sd
        LEFT JOIN Story s1 ON sd.story_id = s1.id
        LEFT JOIN Story s2 ON sd.depends_on_id = s2.id
        WHERE s1.id IS NULL OR s2.id IS NULL
        """
    )
    orphans = await cursor.fetchall()

    if not orphans:
        # Count total dependencies
        cursor = await conn.execute("SELECT COUNT(*) FROM Story_Dependency")
        row = await cursor.fetchone()
        total = row[0] if row else 0
        return ValidationResult(
            passed=True,
            message=f"All {total} dependencies are valid",
        )

    orphan_details = [f"{row[0]} -> {row[1]}" for row in orphans[:5]]
    return ValidationResult(
        passed=False,
        message=f"{len(orphans)} orphan dependencies (e.g., {', '.join(orphan_details)})",
        fix_suggestion="Delete orphan dependencies or recreate data with seed --clean",
    )


async def check_feature_waves(conn) -> ValidationResult:
    """Check if features have valid wave numbers.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    cursor = await conn.execute(
        """
        SELECT COUNT(*) FROM Feature
        WHERE wave IS NULL OR wave < 1
        """
    )
    row = await cursor.fetchone()
    invalid_count = row[0] if row else 0

    if invalid_count == 0:
        cursor = await conn.execute("SELECT COUNT(*) FROM Feature")
        row = await cursor.fetchone()
        total = row[0] if row else 0
        return ValidationResult(
            passed=True,
            message=f"All {total} features have valid waves",
        )

    return ValidationResult(
        passed=False,
        message=f"{invalid_count} features have invalid wave numbers",
        fix_suggestion="Update features with valid wave numbers (>= 1)",
    )


async def check_circular_dependencies(conn) -> ValidationResult:
    """Check for circular dependencies using CTE.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    # Use recursive CTE to detect cycles
    # This query finds cycles by following dependency chains
    cursor = await conn.execute(
        """
        WITH RECURSIVE dep_chain(start_id, current_id, path, is_cycle) AS (
            -- Base case: start from each dependency
            SELECT story_id, depends_on_id, story_id || '->' || depends_on_id, 0
            FROM Story_Dependency

            UNION ALL

            -- Recursive case: follow the chain
            SELECT dc.start_id, sd.depends_on_id,
                   dc.path || '->' || sd.depends_on_id,
                   CASE WHEN dc.start_id = sd.depends_on_id THEN 1 ELSE 0 END
            FROM dep_chain dc
            JOIN Story_Dependency sd ON dc.current_id = sd.story_id
            WHERE dc.is_cycle = 0 AND length(dc.path) < 500
        )
        SELECT DISTINCT start_id, path
        FROM dep_chain
        WHERE is_cycle = 1
        LIMIT 5
        """
    )
    cycles = await cursor.fetchall()

    if not cycles:
        return ValidationResult(
            passed=True,
            message="No circular dependencies detected",
        )

    cycle_details = [f"{row[0]}: {row[1]}" for row in cycles]
    return ValidationResult(
        passed=False,
        message=f"Circular dependencies detected: {'; '.join(cycle_details)}",
        fix_suggestion="Remove one dependency from each cycle to break the loop",
    )


async def check_stories_exist(conn) -> ValidationResult:
    """Check if any stories exist.

    Args:
        conn: Database connection.

    Returns:
        ValidationResult with pass/fail status.
    """
    cursor = await conn.execute("SELECT COUNT(*) FROM Story")
    row = await cursor.fetchone()
    count = row[0] if row else 0

    if count > 0:
        return ValidationResult(
            passed=True,
            message=f"{count} stories found",
        )

    return ValidationResult(
        passed=False,
        message="No stories found",
        fix_suggestion="Run seed_test_backlog.py --clean to create test data",
    )


async def validate_data(db_path: Path, strict: bool = False) -> bool:
    """Run all validation checks.

    Args:
        db_path: Path to the database file.
        strict: If True, exit with error code on failure.

    Returns:
        True if all checks passed, False otherwise.
    """
    from backlog_manager.infrastructure.database.sqlite_connection import (
        create_connection,
    )

    conn = await create_connection(db_path)

    try:
        checks = [
            ("Stories exist", check_stories_exist),
            ("Stories with dates", check_story_dates),
            ("Active developers", check_developers),
            ("Valid dependencies", check_dependencies),
            ("Feature waves", check_feature_waves),
            ("Circular dependencies", check_circular_dependencies),
        ]

        results: list[tuple[str, ValidationResult]] = []
        for name, check_fn in checks:
            result = await check_fn(conn)
            results.append((name, result))

        # Generate report
        all_passed = all(r[1].passed for r in results)

        print("=" * 60)
        print("DATA VALIDATION REPORT")
        print("=" * 60)

        for name, result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {name}: {result.message}")

        if not all_passed:
            print()
            print("SUGGESTED FIXES:")
            print("-" * 40)
            for name, result in results:
                if not result.passed and result.fix_suggestion:
                    print(f"  - {name}: {result.fix_suggestion}")

            print()
            print("VALIDATION FAILED - Fix issues before running allocation")
        else:
            print()
            print("VALIDATION PASSED - Data is ready for allocation")

        print("=" * 60)

        return all_passed

    finally:
        await conn.close()


def main() -> None:
    """Entry point for the script."""
    args = parse_args()

    # Resolve database path
    db_path = get_analysis_db_path(args.db_path)

    # Log database info
    log_database_info(db_path)
    print()

    # Run validation
    passed = asyncio.run(validate_data(db_path, args.strict))

    if args.strict and not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
