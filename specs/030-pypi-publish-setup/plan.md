# Implementation Plan: PyPI Publish Setup

**Branch**: `030-pypi-publish-setup` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/030-pypi-publish-setup/spec.md`

## Summary

Prepare the project for distribution on PyPI under the name `zion-backlog-manager` by updating `pyproject.toml` metadata (name, author, license, classifiers, keywords, URLs, entry point) and creating a standalone publish script (`scripts/publish_to_pypi.py`) that automates the build-validate-upload workflow using `poetry build` + `twine upload`. Zero source code changes — only metadata and tooling.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Poetry (build), twine (upload), existing project deps unchanged
**Storage**: N/A — no database changes
**Testing**: Manual validation (`poetry check`, `poetry build`, script dry-run)
**Target Platform**: PyPI (package registry), Windows + Linux (script cross-platform)
**Project Type**: Desktop application (PySide6) distributed as Python package
**Performance Goals**: N/A — packaging/distribution feature
**Constraints**: Zero `.py` source file modifications (FR-008, FR-009)
**Scale/Scope**: 1 file modified (`pyproject.toml`), 1 file created (`scripts/publish_to_pypi.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | No source code changes; no layer violations |
| II. DDD | ✅ PASS | No domain changes |
| III. Repository Pattern | ✅ PASS | No data access changes |
| IV. Dependency Injection | ✅ PASS | No DI changes |
| V. SQLite | ✅ PASS | No database changes |
| VI. Packaging & Distribution | ✅ PASS | Directly implements this principle — Poetry build, PyPI publish, semver, entry points in pyproject.toml |
| VII. Directory Structure | ✅ PASS | Script goes in existing `scripts/` directory; src layout unchanged |
| VIII. Async | ✅ PASS | No async changes |
| IX. Simplicity | ✅ PASS | Single script, stdlib only, no abstractions |
| X. Type Hints | ✅ PASS | Script uses type hints |
| XI. Docstrings | ✅ PASS | Script has module/function docstrings |
| XII. Import Organization | ✅ PASS | No source imports changed |
| XIII. Naming Conventions | ✅ PASS | Script follows PEP 8 naming |

**Pre-design gate**: ✅ ALL PASS — no violations.

**Post-design re-check**: ✅ ALL PASS — design confirmed: only `pyproject.toml` metadata + standalone script. Constitution VI explicitly mandates Poetry + PyPI distribution.

## Project Structure

### Documentation (this feature)

```text
specs/030-pypi-publish-setup/
├── plan.md              # This file
├── research.md          # Phase 0 output — design decisions
├── data-model.md        # Phase 1 output — metadata entities
├── quickstart.md        # Phase 1 output — usage guide
├── contracts/
│   ├── cli-entry-point.md   # CLI command contract
│   └── publish-script.md   # Publish script CLI contract
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
pyproject.toml                    # Modified — package metadata
scripts/
└── publish_to_pypi.py            # New — automated publish workflow
```

**Structure Decision**: Minimal footprint. Only `pyproject.toml` is modified in existing files. One new file in the existing `scripts/` directory. No new directories or source code changes.

## Complexity Tracking

No violations — table not needed.
