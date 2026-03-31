# Feature Specification: PyPI Publish Setup

**Feature Branch**: `030-pypi-publish-setup`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Preparar o projeto para distribuição no PyPI sob o nome zion-backlog-manager"

## Clarifications

### Session 2026-03-31

- Q: Which Development Status classifier should be used? → A: `Development Status :: 3 - Alpha` (appropriate for v0.1.0, first PyPI publication)
- Q: Should the PyPI package description be in English or Portuguese? → A: English — maximizes discoverability on international PyPI registry (e.g., "Backlog Manager - Automated backlog management and developer allocation system")

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Package Metadata Ready for PyPI (Priority: P1)

As a package maintainer, I want the project metadata (pyproject.toml) to contain all required and recommended fields for PyPI publication so that the package appears professional and discoverable on PyPI under the name "zion-backlog-manager".

**Why this priority**: Without correct metadata, the package cannot be published to PyPI at all. This is the foundational prerequisite for everything else.

**Independent Test**: Can be verified by running `poetry check` and inspecting the generated package metadata to confirm all required fields are present and correct.

**Acceptance Scenarios**:

1. **Given** the updated pyproject.toml, **When** a user runs `pip install zion-backlog-manager`, **Then** the package installs correctly and the CLI command `zion-backlog-manager` is available.
2. **Given** the updated pyproject.toml, **When** the package is viewed on PyPI, **Then** it displays author, license, homepage, repository URL, classifiers, and keywords.
3. **Given** the updated pyproject.toml, **When** `poetry build` is executed, **Then** the generated artifacts (sdist and wheel) contain `zion_backlog_manager` in their filenames.
4. **Given** the updated pyproject.toml, **When** any Python source file (*.py) is inspected, **Then** no internal imports, module names, or code references have been changed from the existing `backlog_manager` namespace.

---

### User Story 2 - Automated Build and Publish Script (Priority: P2)

As a package maintainer, I want a standalone publish script that automates the build-and-upload workflow so that I can publish new versions to PyPI (or TestPyPI) with a single command, reducing manual errors.

**Why this priority**: Once metadata is correct, the publish workflow is the next step. Automation reduces human error during releases.

**Independent Test**: Can be tested by running the script with `--test` flag to publish to TestPyPI and verifying the package appears there.

**Acceptance Scenarios**:

1. **Given** valid environment credentials (PYPI_TOKEN or TWINE_USERNAME/TWINE_API_TOKEN), **When** the user runs `python scripts/publish_to_pypi.py`, **Then** the script cleans previous artifacts, builds the package, uploads to PyPI, and displays a summary with version and package URL.
2. **Given** the `--test` flag, **When** the user runs `python scripts/publish_to_pypi.py --test`, **Then** the script uploads to TestPyPI instead of production PyPI.
3. **Given** no credentials are configured, **When** the user runs the script, **Then** it displays a clear error message explaining which environment variables to set.
4. **Given** the build completes, **When** the script validates artifacts, **Then** it confirms the generated files contain `zion_backlog_manager` in their names before uploading.

---

### User Story 3 - End User Installation (Priority: P3)

As an end user, I want to install the application via `pip install zion-backlog-manager` (or pipx) and run it via the `zion-backlog-manager` command so that I have a simple, standard Python package installation experience.

**Why this priority**: This validates the end-to-end experience from the user's perspective, but depends on the metadata and publish steps being correct first.

**Independent Test**: Can be tested by installing from TestPyPI and running `zion-backlog-manager` to confirm the application launches.

**Acceptance Scenarios**:

1. **Given** the package is published on PyPI, **When** a user runs `pip install zion-backlog-manager`, **Then** the package installs with all dependencies.
2. **Given** the package is installed, **When** a user runs `zion-backlog-manager` from the command line, **Then** the application launches correctly.

---

### Edge Cases

- What happens when `twine` is not installed? The publish script must detect its absence and display an installation instruction.
- What happens when `poetry` is not installed? The publish script must detect its absence and display an error.
- What happens when the `dist/` directory does not exist before cleanup? The script handles this gracefully (no error).
- What happens when the build produces artifacts with an unexpected name? The script aborts upload and warns the user.
- What happens when the upload fails mid-way (network error)? The script displays the error from twine and exits with a non-zero code.
- What happens when the user runs the script without any credentials set? Clear error message with instructions for setting PYPI_TOKEN or TWINE_USERNAME/TWINE_API_TOKEN.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pyproject.toml `name` field MUST be set to `"zion-backlog-manager"`.
- **FR-002**: The `[tool.poetry.scripts]` entry MUST define `zion-backlog-manager` as the CLI command, pointing to `backlog_manager.presentation.app:main`.
- **FR-003**: The pyproject.toml MUST include `authors = ["Tuyoshi Vinicius <tuyoshi.dev@gmail.com>"]`.
- **FR-004**: The pyproject.toml MUST include `license = "MIT"`.
- **FR-005**: The pyproject.toml MUST include `homepage` and `repository` URLs pointing to `https://github.com/tuyoshivinicius/backlog_manager_v2`.
- **FR-006**: The pyproject.toml MUST include relevant PyPI classifiers: `Development Status :: 3 - Alpha`, plus Framework (Qt), Environment (X11 Applications), Programming Language (Python :: 3.11), and Topic (Software Development :: Project Management).
- **FR-007**: The pyproject.toml MUST include keywords relevant to the project's domain (backlog, project management, Qt, etc.).
- **FR-007B**: The pyproject.toml `description` field MUST be in English (e.g., "Backlog Manager - Automated backlog management and developer allocation system").
- **FR-008**: No Python source files (*.py) in the codebase MUST be modified — only pyproject.toml metadata changes are allowed.
- **FR-009**: The internal Python namespace `backlog_manager` and all imports MUST remain unchanged.
- **FR-010**: A standalone publish script MUST exist at `scripts/publish_to_pypi.py`.
- **FR-011**: The publish script MUST clean the `dist/` directory before building.
- **FR-012**: The publish script MUST execute `poetry build` to generate sdist and wheel artifacts.
- **FR-013**: The publish script MUST upload artifacts using `twine` (not `poetry publish`).
- **FR-014**: The publish script MUST support a `--test` flag to upload to TestPyPI.
- **FR-015**: The publish script MUST authenticate via environment variables (PYPI_TOKEN or TWINE_USERNAME/TWINE_API_TOKEN) — no hardcoded credentials.
- **FR-016**: The publish script MUST validate that generated artifacts contain `zion_backlog_manager` in their filenames before uploading.
- **FR-017**: The publish script MUST display a summary after successful upload (version published, package URL).
- **FR-018**: The publish script MUST check for `twine` and `poetry` availability at startup and display clear error messages if missing.
- **FR-019**: `twine` MUST NOT be added as a production dependency — it should be a dev dependency or checked at runtime.

### Key Entities

- **Package Metadata**: The set of fields in pyproject.toml that define how the package appears on PyPI (name, version, authors, license, classifiers, keywords, URLs).
- **Build Artifacts**: The sdist (.tar.gz) and wheel (.whl) files generated by `poetry build`, which are uploaded to PyPI.
- **Publish Script**: A standalone Python script that orchestrates the build-clean-validate-upload workflow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `poetry build` produces artifacts with `zion_backlog_manager` in the filename (not `backlog_manager`).
- **SC-002**: The package can be installed from TestPyPI via `pip install --index-url https://test.pypi.org/simple/ zion-backlog-manager` and the `zion-backlog-manager` CLI command works.
- **SC-003**: The publish script completes the full build-validate-upload cycle in a single command execution.
- **SC-004**: Zero Python source files (*.py) are modified by this feature — only pyproject.toml and the new publish script.
- **SC-005**: The PyPI package page displays all metadata: author, license, homepage, repository, classifiers, and keywords.
- **SC-006**: The publish script exits with a clear error within 5 seconds when credentials are missing or tools are not installed.

## Assumptions

- The existing `backlog_manager.presentation.app:main` entry point is functional and will work as the CLI command target.
- The project already uses Poetry with poetry-core as the build backend (confirmed from pyproject.toml).
- The user will manage PyPI credentials via environment variables as per standard practice.
- `twine` will be added as a dev dependency in `[tool.poetry.group.dev.dependencies]` for convenience, but the publish script will also check for its availability at runtime.
- The version field in pyproject.toml (`0.1.0`) will be managed manually or via a separate versioning workflow — this feature does not introduce version bumping automation.
