# Research: PyPI Publish Setup

**Feature Branch**: `030-pypi-publish-setup`
**Date**: 2026-03-31

## Decision 1: Package Name vs Internal Namespace

**Decision**: Use `zion-backlog-manager` as the PyPI package name while keeping the internal Python namespace as `backlog_manager`.

**Rationale**: Poetry supports this natively via the `name` field (PyPI distribution name) and `packages` directive (importable namespace). The `name` in `[tool.poetry]` controls what users type in `pip install`, while `packages = [{include = "backlog_manager", from = "src"}]` controls the importable module. These are independent — no source code changes needed.

**Alternatives considered**:
- Renaming the internal package to `zion_backlog_manager` — rejected because it would require modifying every import in every `.py` file, violating FR-008 and FR-009.

## Decision 2: Upload Tool — twine vs poetry publish

**Decision**: Use `twine` for uploading to PyPI, invoked from a standalone publish script.

**Rationale**: The spec explicitly requires `twine` (FR-013) and forbids `poetry publish`. `twine` offers more granular control: separate build and upload steps, explicit artifact validation, TestPyPI support via `--repository-url`, and environment variable-based authentication (`TWINE_USERNAME`, `TWINE_PASSWORD`).

**Alternatives considered**:
- `poetry publish` — rejected per FR-013. Also, Poetry's publish doesn't easily support pre-upload artifact validation.
- GitHub Actions automated publishing — out of scope for this feature (no CI/CD changes).

## Decision 3: Credential Strategy

**Decision**: Support two authentication methods via environment variables:
1. `PYPI_TOKEN` — API token (preferred, maps to `TWINE_USERNAME=__token__`, `TWINE_PASSWORD=$PYPI_TOKEN`)
2. `TWINE_USERNAME` + `TWINE_PASSWORD` — legacy username/password or token pair

**Rationale**: API tokens are the modern PyPI standard. Supporting both provides flexibility. The script detects which variables are set and configures twine accordingly. No credentials are ever hardcoded (FR-015).

**Alternatives considered**:
- `.pypirc` config file — rejected because environment variables are more portable and CI-friendly, and the spec explicitly requires env vars.

## Decision 4: twine as Dev Dependency

**Decision**: Add `twine` to `[tool.poetry.group.dev.dependencies]`. The publish script also checks for `twine` at runtime.

**Rationale**: Making it a dev dependency ensures it's available in dev environments. Runtime check (FR-018) handles the case where someone runs the script outside a Poetry-managed environment.

**Alternatives considered**:
- Production dependency — rejected per FR-019.
- No dependency declaration, rely on runtime check only — rejected because explicit dev dependency is better DX.

## Decision 5: Publish Script Architecture

**Decision**: Single standalone Python script at `scripts/publish_to_pypi.py` using only stdlib modules (`subprocess`, `shutil`, `argparse`, `os`, `sys`, `pathlib`).

**Rationale**: The script is a build/deployment tool, not part of the application. Using only stdlib keeps it independent of the project's virtual environment and avoids import issues. It orchestrates external tools (`poetry build`, `twine upload`) via subprocess.

**Alternatives considered**:
- Makefile / shell script — rejected because Python script is cross-platform (Windows + Linux) and offers better error handling.
- Invoke/Nox task runner — rejected as over-engineering for a single publish workflow.

## Decision 6: TestPyPI Support

**Decision**: `--test` flag switches the upload target to `https://test.pypi.org/legacy/` via twine's `--repository-url` option.

**Rationale**: TestPyPI is the standard way to validate the publish workflow before going to production PyPI. The `--repository-url` flag is the most explicit and reliable method.

**Alternatives considered**:
- Separate `~/.pypirc` configuration — rejected per credential strategy decision above.
