# Tasks: PyPI Publish Setup

**Input**: Design documents from `/specs/030-pypi-publish-setup/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add twine as dev dependency so it's available for the publish workflow

- [x] T001 Add `twine` to `[tool.poetry.group.dev.dependencies]` in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational tasks needed — this feature modifies only pyproject.toml metadata and adds a standalone script. Phase 1 (twine dependency) is the only prerequisite.

**Checkpoint**: Setup ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Package Metadata Ready for PyPI (Priority: P1) 🎯 MVP

**Goal**: Update pyproject.toml with all required and recommended fields so the package is publishable on PyPI as `zion-backlog-manager`.

**Independent Test**: Run `poetry check` and `poetry build`, then inspect artifact filenames for `zion_backlog_manager`.

### Implementation for User Story 1

- [x] T002 [US1] Set `name = "zion-backlog-manager"` in `[tool.poetry]` section of pyproject.toml (FR-001)
- [x] T003 [US1] Set `description` to English description in pyproject.toml (FR-007B)
- [x] T004 [US1] Set `authors = ["Tuyoshi Vinicius <tuyoshi.dev@gmail.com>"]` in pyproject.toml (FR-003)
- [x] T005 [US1] Set `license = "MIT"` in pyproject.toml (FR-004)
- [x] T006 [US1] Add `homepage` and `repository` URLs pointing to `https://github.com/tuyoshivinicius/backlog_manager_v2` in pyproject.toml (FR-005)
- [x] T007 [US1] Add `keywords` list with domain-relevant terms (backlog, project-management, Qt, PySide6, developer-allocation) in pyproject.toml (FR-007)
- [x] T008 [US1] Add `classifiers` list with `Development Status :: 3 - Alpha`, Framework (Qt), Environment (X11 Applications), Programming Language (Python :: 3.11), and Topic (Software Development :: Project Management) in pyproject.toml (FR-006)
- [x] T009 [US1] Add `[tool.poetry.scripts]` entry `zion-backlog-manager = "backlog_manager.presentation.app:main"` in pyproject.toml (FR-002)
- [x] T010 [US1] Validate: run `poetry check` and `poetry build`, confirm artifacts contain `zion_backlog_manager` in filenames (SC-001)

**Checkpoint**: Package metadata is complete. `poetry build` produces correctly-named artifacts. US1 is independently verifiable.

---

## Phase 4: User Story 2 - Automated Build and Publish Script (Priority: P2)

**Goal**: Create a standalone publish script that automates the build-validate-upload workflow using `poetry build` + `twine upload`.

**Independent Test**: Run `python scripts/publish_to_pypi.py --test` with a TestPyPI token to verify end-to-end publish to TestPyPI.

### Implementation for User Story 2

- [x] T011 [US2] Create `scripts/publish_to_pypi.py` with module docstring, shebang, stdlib imports only (subprocess, shutil, argparse, os, sys, pathlib) per research.md Decision 5
- [x] T012 [US2] Implement `check_tool(name)` function that verifies `poetry` and `twine` are available via `shutil.which()`, exits with clear error if missing (FR-018) in scripts/publish_to_pypi.py
- [x] T013 [US2] Implement `check_credentials(use_test: bool)` function that checks for `PYPI_TOKEN` or `TWINE_USERNAME`/`TWINE_PASSWORD` env vars, exits with instruction message if missing (FR-015) in scripts/publish_to_pypi.py
- [x] T014 [US2] Implement `clean_dist()` function that removes `dist/` directory gracefully (handles non-existence) (FR-011) in scripts/publish_to_pypi.py
- [x] T015 [US2] Implement `build_package()` function that runs `poetry build` via subprocess and checks return code (FR-012) in scripts/publish_to_pypi.py
- [x] T016 [US2] Implement `validate_artifacts()` function that checks all files in `dist/` contain `zion_backlog_manager` in their names, aborts if not (FR-016) in scripts/publish_to_pypi.py
- [x] T017 [US2] Implement `upload_package(use_test: bool)` function that configures twine env vars from `PYPI_TOKEN` (precedence) or `TWINE_USERNAME`/`TWINE_PASSWORD`, calls `twine upload` with `--repository-url` for TestPyPI when `--test` flag is set (FR-013, FR-014) in scripts/publish_to_pypi.py
- [x] T018 [US2] Implement `print_summary(version, use_test)` function that displays version and package URL (PyPI or TestPyPI) per contracts/publish-script.md output format (FR-017) in scripts/publish_to_pypi.py
- [x] T019 [US2] Implement `main()` with argparse (`--test` flag), orchestrating: check_tool → check_credentials → clean_dist → build_package → validate_artifacts → upload_package → print_summary in scripts/publish_to_pypi.py
- [x] T020 [US2] Add `if __name__ == "__main__": main()` and ensure script exits with code 0 on success, 1 on any error per contracts/publish-script.md exit codes in scripts/publish_to_pypi.py

**Checkpoint**: Publish script is complete. Can verify with `python scripts/publish_to_pypi.py --test` against TestPyPI. US2 is independently verifiable.

---

## Phase 5: User Story 3 - End User Installation (Priority: P3)

**Goal**: Validate that the end-to-end installation experience works — `pip install zion-backlog-manager` installs correctly and the `zion-backlog-manager` CLI command launches the application.

**Independent Test**: Install from TestPyPI and run `zion-backlog-manager` to confirm the application launches.

### Implementation for User Story 3

- [x] T021 [US3] Verify `packages = [{include = "backlog_manager", from = "src"}]` is present and unchanged in pyproject.toml (FR-009) — ensures internal namespace is preserved for end-user imports
- [ ] T022 [US3] End-to-end validation: publish to TestPyPI via `python scripts/publish_to_pypi.py --test`, then install with `pip install --index-url https://test.pypi.org/simple/ zion-backlog-manager` and run `zion-backlog-manager` CLI command (SC-002)

**Checkpoint**: End-to-end user experience validated. All 3 user stories complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validations and constraint enforcement

- [x] T023 Verify zero Python source files (*.py) in `src/` were modified (FR-008, SC-004) — run `git diff --name-only` and confirm no `src/**/*.py` files appear
- [x] T024 Run quickstart.md verification checklist to confirm all items pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: N/A — no foundational tasks
- **User Story 1 (Phase 3)**: Depends on Phase 1 (twine dev dependency added)
- **User Story 2 (Phase 4)**: Depends on Phase 1 (twine available); independent of US1 at file level but logically follows US1
- **User Story 3 (Phase 5)**: Depends on US1 (metadata correct) AND US2 (publish script exists)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 1 — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 1 — works on a different file (`scripts/publish_to_pypi.py`) so technically parallelizable with US1
- **User Story 3 (P3)**: Depends on US1 + US2 — requires both metadata and publish script to validate end-to-end

### Within Each User Story

- US1: All metadata tasks (T002–T009) operate on the same file (`pyproject.toml`) so they should be applied sequentially; T010 is the validation step
- US2: Tasks T011–T020 build up the publish script incrementally in a single file; sequential execution recommended
- US3: Validation tasks that depend on US1 + US2 being complete

### Parallel Opportunities

- **US1 and US2 can run in parallel** — they modify different files (`pyproject.toml` vs `scripts/publish_to_pypi.py`)
- Within US1, tasks T002–T009 all touch `pyproject.toml` — apply sequentially or as a single edit
- Within US2, tasks T011–T020 all touch `scripts/publish_to_pypi.py` — apply sequentially or as a single edit

---

## Parallel Example: US1 + US2

```bash
# These can run in parallel (different files):
# Worker A: US1 — all metadata updates to pyproject.toml (T002–T010)
# Worker B: US2 — create publish script scripts/publish_to_pypi.py (T011–T020)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Add twine dev dependency
2. Complete Phase 3: Update pyproject.toml metadata
3. **STOP and VALIDATE**: `poetry check` + `poetry build` → artifacts have correct names
4. Package is buildable and metadata-complete

### Incremental Delivery

1. Phase 1 → twine available
2. Add US1 → metadata correct, package builds → **MVP!**
3. Add US2 → publish script works → can publish to TestPyPI
4. Add US3 → end-to-end validation → ready for production PyPI publish
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With two developers:

1. Complete Phase 1 together
2. Once Phase 1 is done:
   - Developer A: User Story 1 (pyproject.toml metadata)
   - Developer B: User Story 2 (publish script)
3. Both complete → Developer A or B: User Story 3 (end-to-end validation)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No tests were requested — validation is manual per spec
- Zero source code changes constraint (FR-008, FR-009) — only pyproject.toml and scripts/publish_to_pypi.py
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
