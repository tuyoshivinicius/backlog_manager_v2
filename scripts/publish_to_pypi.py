#!/usr/bin/env python3
"""Automated build and publish workflow for zion-backlog-manager.

Orchestrates: clean → build → validate → upload to PyPI or TestPyPI.

Usage:
    python scripts/publish_to_pypi.py          # publish to production PyPI
    python scripts/publish_to_pypi.py --test    # publish to TestPyPI
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

DIST_DIR = Path("dist")
EXPECTED_NAME = "zion_backlog_manager"
TESTPYPI_URL = "https://test.pypi.org/legacy/"
PYPI_PROJECT_URL = "https://pypi.org/project/zion-backlog-manager"
TESTPYPI_PROJECT_URL = "https://test.pypi.org/project/zion-backlog-manager"


def check_tool(name: str) -> None:
    """Verify a CLI tool is available on PATH."""
    if shutil.which(name) is None:
        print(f"ERROR: '{name}' not found on PATH. Please install it first.")
        sys.exit(1)


def resolve_token(use_test: bool) -> str | None:
    """Return the appropriate token for the target registry."""
    if use_test:
        token = os.environ.get("TESTPYPI_TOKEN") or os.environ.get("PYPI_TOKEN")
    else:
        token = os.environ.get("PYPI_TOKEN")
    return token


def check_credentials(use_test: bool) -> None:
    """Verify PyPI credentials are available via environment variables."""
    token = resolve_token(use_test)
    twine_user = os.environ.get("TWINE_USERNAME")
    twine_pass = os.environ.get("TWINE_PASSWORD")

    if token or (twine_user and twine_pass):
        return

    target = "TestPyPI" if use_test else "PyPI"
    env_var = "TESTPYPI_TOKEN" if use_test else "PYPI_TOKEN"
    print(f"ERROR: No {target} credentials found.")
    print("Set one of:")
    print(f"  - {env_var} in .env or environment (recommended)")
    print("  - TWINE_USERNAME + TWINE_PASSWORD")
    sys.exit(1)


def clean_dist() -> None:
    """Remove the dist/ directory if it exists."""
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    print("[OK] Cleaned dist/")


def build_package() -> None:
    """Run poetry build and check for success."""
    result = subprocess.run(
        ["poetry", "build"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("ERROR: poetry build failed:")
        print(result.stderr)
        sys.exit(1)


def get_version() -> str:
    """Extract the package version from poetry."""
    result = subprocess.run(
        ["poetry", "version", "-s"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_artifacts() -> None:
    """Verify all artifacts in dist/ contain the expected package name."""
    if not DIST_DIR.exists():
        print("ERROR: dist/ directory not found after build.")
        sys.exit(1)

    artifacts = list(DIST_DIR.iterdir())
    if not artifacts:
        print("ERROR: No artifacts found in dist/.")
        sys.exit(1)

    for artifact in artifacts:
        if EXPECTED_NAME not in artifact.name:
            print(
                f"ERROR: Artifact '{artifact.name}' does not contain "
                f"'{EXPECTED_NAME}'. Aborting upload."
            )
            sys.exit(1)

    print(f"[OK] Validated {len(artifacts)} artifact(s)")


def upload_package(use_test: bool) -> None:
    """Upload artifacts to PyPI or TestPyPI via twine."""
    env = os.environ.copy()

    token = resolve_token(use_test)
    if token:
        env["TWINE_USERNAME"] = "__token__"
        env["TWINE_PASSWORD"] = token

    cmd = ["twine", "upload", "dist/*"]
    if use_test:
        cmd.extend(["--repository-url", TESTPYPI_URL])

    result = subprocess.run(cmd, env=env)
    if result.returncode != 0:
        print("ERROR: twine upload failed.")
        sys.exit(1)


def print_summary(version: str, use_test: bool) -> None:
    """Display a success summary with the package URL."""
    base_url = TESTPYPI_PROJECT_URL if use_test else PYPI_PROJECT_URL
    target = "TestPyPI" if use_test else "PyPI"
    print(f"[OK] Uploaded to {target}")
    print(f"  -> {base_url}/{version}/")


def main() -> None:
    """Orchestrate the full publish workflow."""
    parser = argparse.ArgumentParser(
        description="Build and publish zion-backlog-manager to PyPI.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to TestPyPI instead of production PyPI.",
    )
    args = parser.parse_args()

    load_dotenv()
    check_tool("poetry")
    check_tool("twine")
    check_credentials(args.test)
    clean_dist()
    build_package()
    version = get_version()
    print(f"[OK] Built package v{version}")
    validate_artifacts()
    upload_package(args.test)
    print_summary(version, args.test)


if __name__ == "__main__":
    main()
