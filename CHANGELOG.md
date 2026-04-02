# CHANGELOG


## v1.0.1 (2026-04-02)

### Bug Fixes

- Pin python-semantic-release to v9 and handle existing GitHub releases
  ([`8308a19`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/8308a19b88ae1a7ff0e538e2914ad45a939f9f16))

The CI was installing python-semantic-release v10 (latest) while the pyproject.toml config uses v9
  format, causing version detection to fail and never increment beyond v1.0.0. Also, publish.yml now
  uploads assets to an existing release instead of failing when it already exists.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>


## v1.0.0 (2026-04-02)

### Bug Fixes

- Add verbose output to pypi publish for debugging 400 error
  ([`dbefebc`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/dbefebcc525e56e78f92bfdf8b344a7d50cfcfee))

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Enhance semantic-release output handling and tag management
  ([`7a7870b`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/7a7870b651ba5608c16b40401935f1b7f2488015))

- Explicitly disable attestations in pypi publish action
  ([`5785c93`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/5785c93afc8b1260694e7cfcf949bab41deff437))

Removing the attestations: write permission was not sufficient — the action generates Sigstore
  attestations by default via id-token. This explicitly disables attestation generation to fix the
  400 Bad Request error from PyPI.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Remove attestations permission from publish jobs
  ([`5f42b24`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/5f42b2473e6c0c1c6602ad7654672424c6de2085))

- Remove auto-merge steps from CI workflows
  ([`0bf6616`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/0bf6616b168eb648cebe978c7a0010de4d571362))

- Remove hardcoded version assertion from import test
  ([`cfd54e3`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/cfd54e3122b8a6620b086888f5754e31e24a6056))

The test was asserting __version__ == "0.1.0" which breaks when semantic-release bumps the version.
  Now validates only that __version__ is a non-empty string, since version sync is already enforced
  by CI.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Remove invalid PyPI classifier 'Framework :: Qt for Python'
  ([`2e7d2c6`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/2e7d2c6c6ee331fedc242e8f8bea26c299d497b4))

This classifier does not exist in PyPI's official list and was causing all uploads to fail with 400
  Bad Request.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Resolve ambiguous refspec and deprecated commit parser
  ([`bec0159`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/bec0159fed0818117ff0b0ced3288f601e0c0e31))

Delete spurious 'main' tag that caused 'src refspec main matches more than one' error, use full
  refspec refs/heads/main in push, and switch commit_parser from deprecated 'angular' to
  'conventional'.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Update actions permissions in main release workflow
  ([`bbac44c`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/bbac44cac44ccda5ab4192ad9b73cc33edd0db37))

- Update actions permissions in main release workflow
  ([#67](https://github.com/tuyoshivinicius/zion-backlog-manager/pull/67),
  [`e335064`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/e335064a646e662f27123c488752ee94adcfb728))

Co-authored-by: Tuyoshi Vinicius <tuyoshi_vinicius@hotmail.com>

- Update pypi publish action to version 1.12.4 and add attestations permission
  ([`7a64a0f`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/7a64a0f82ef969bc07abcd34cbfc597a8877d6ce))

- Use correct commit SHA for pypi publish action docker image
  ([`a672526`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a6725261971ca94e196409cc7371e7661a24a24b))

The previous SHA was the tag object, not the actual commit. The ghcr.io Docker image is tagged with
  the commit SHA, causing "manifest unknown".

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Features

- Auto versioning cicd ([#58](https://github.com/tuyoshivinicius/zion-backlog-manager/pull/58),
  [`0e427ea`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/0e427ea41ed0d8be5fa66ff1f9e76585f3c55a82))

* feat(EP-037): add auto-versioning and CI/CD workflow automation

Add python-semantic-release config, feature CI, develop merge, and main release workflows with auto
  PR creation and backmerge support.

* fix: grant contents write permission for auto-merge in feature CI

The GITHUB_TOKEN needs contents:write to call the mergePullRequest GraphQL mutation used by `gh pr
  merge --auto`.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Tuyoshi Vinicius <tuyoshi_vinicius@hotmail.com>

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Auto versioning cicd ([#59](https://github.com/tuyoshivinicius/zion-backlog-manager/pull/59),
  [`2067b75`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/2067b75f08c621f499bc8b901c478b378abe4a84))

* feat(EP-037): add auto-versioning and CI/CD workflow automation

Add python-semantic-release config, feature CI, develop merge, and main release workflows with auto
  PR creation and backmerge support.

* fix: grant contents write permission for auto-merge in feature CI

The GITHUB_TOKEN needs contents:write to call the mergePullRequest GraphQL mutation used by `gh pr
  merge --auto`.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* test

---------

Co-authored-by: Tuyoshi Vinicius <tuyoshi_vinicius@hotmail.com>

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Rewrite README.md for Zion Backlog Manager with professional content in Brazilian Portuguese
  ([`e47c924`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/e47c924e8268461ce04cb0fd7de306467da67671))

- Updated project title and description - Added comprehensive sections: About the Project, Concept
  and Philosophy, Features, Applicability, Screenshot, Technology Stack, Architecture, Installation,
  Usage, Troubleshooting, Contribution, and License - Included badges for CI, Codecov, SonarCloud,
  PyPI, and License - Created a directory for screenshots and added a placeholder image -
  Established a detailed implementation plan and task checklist for the README update - Added
  specifications and research documents to ensure quality and completeness


## v0.1.0 (2026-04-01)

### Bug Fixes

- Add actions write permission in main release workflow
  ([`0786c27`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/0786c27272afb10609fd97beab84e4df4c98c460))

- Adjust timeout for cancel button visibility and update task cancellation assertion
  ([`fe9d917`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/fe9d9172e8d4418d0bf007465be118ebbc910d1f))

- Ensure ProgressDialog is shown before testing cancel button visibility
  ([`3d6e547`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/3d6e547eecf57674571e570434b4ade350b5d97b))

- Exclude E2E tests from coverage reporting to streamline test execution
  ([`55573a2`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/55573a2e8a63cde2e394a70f0f8df20c30eb2127))

- Exclude slow integration tests from the CI workflow to improve test execution speed
  ([`409b605`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/409b6055f1b291b98bf9d53b18557c615309119b))

- Grant contents write permission for auto-merge in feature CI
  ([`696a428`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/696a42889b12c0ea6417bc3a34148b4c56a9facb))

The GITHUB_TOKEN needs contents:write to call the mergePullRequest GraphQL mutation used by `gh pr
  merge --auto`.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Include main branch in push triggers for CI workflow
  ([`47d1331`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/47d13312d77493b6290cc550f5389b2cec28c7e6))

- Refactor CI workflow to combine linting and testing steps, update Python version to 3.13
  ([`21b5ade`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/21b5ade2a06fccc25c45f09833967b39f0602fa3))

- Refactor qasync_loop fixture to prevent event loop leaks and improve code clarity
  ([`31c1414`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/31c141408eb4c1ac8f301e9cb410b0b6dd749882))

- Remove E2E tests from CI workflow to streamline testing process
  ([`56ed26d`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/56ed26df798a1d00ab40e0a4760414ce143fff16))

- Remove timeout option from E2E tests execution in CI workflow
  ([`5babe9c`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/5babe9cafb35be46ec65b88782679d84b56677f0))

- Resolve CI failures from libEGL import error and pytest marker warnings
  ([`4e6490a`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/4e6490afd24ba1d2e6d720ba338740f974838f48))

- Delete pytest.ini that overrode pyproject.toml marker definitions, causing
  PytestUnknownMarkWarning for unit/integration markers - Move theme_module import inside PySide6
  mock patch context to prevent libEGL.so.1 ImportError on headless CI runners - Add libegl1 system
  dependency install step in CI workflow as safety net

- Resolve false-positive deadlock when developers available
  ([`c240310`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/c2403105661750ac71d994c877abf789b8faa4a8))

The allocation algorithm was selecting a developer by load balancing (based on total count) without
  considering period availability. When the selected developer had a conflict, it tried to adjust
  dates instead of trying other available developers, causing false deadlocks.

Fix: Filter developers by period availability BEFORE selection, ensuring load balancing only
  considers developers who can actually take the story.

- stories_allocated: 189 -> 190 (PAY-005 now allocated) - deadlocks_detected: 1 -> 0 -
  total_iterations: 12 -> 7 (more efficient)

Closes RF-ALOC-001 compliance gap.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

- Simplify cancel button visibility test by directly emitting timer signal
  ([`6e7f9f4`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/6e7f9f45769b973cbe2ec9326c073e7240339672))

- Update CI workflow to ignore specific test directories and improve pytest-qt integration
  ([`5a9a143`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/5a9a14319ee7c47ff1d106b213a64c021d19a7b6))

- Update CI workflow to improve caching with Python version in key
  ([`e5271d0`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/e5271d053d20719c7c50ae3c95b4cf2914a6f843))

- Update Codecov to v5 and SonarQube scan action to v6
  ([`84a25b7`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/84a25b7937edb4bfdbfe06fc087e11c62cfa2352))

- Upgrade codecov-action@v4 → v5 with token via `with` instead of `env` - Upgrade
  sonarqube-scan-action@v5 → v6 to fix security vulnerability - Remove continue-on-error from
  SonarCloud step so failures are visible

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Update project key format and Python version in sonar-project.properties
  ([`a464b88`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a464b883f943ef2c24b83c6fac8549b245f49e8b))

- Update repository URLs in README and specifications to reflect new project name
  ([`64bb12a`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/64bb12a5cc205ab582d83fb1370038c8fb0d25f9))

- Upgrade Python version to 3.13 in publish workflow
  ([`4b004e1`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/4b004e189629c00a0a827eeae9b088bacbc13a65))

Aligns the publish workflow Python version with the version used in CI testing and SonarQube
  analysis.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Use secrets inherit in publish workflow to fix startup_failure
  ([`2aec6d7`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/2aec6d788a49be152a83ce4ccf531016a8e0b81a))

The reusable workflow ci.yml did not declare accepted secrets under workflow_call, causing GitHub
  Actions to reject explicitly passed secrets and fail with startup_failure before any job could
  run.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Use xvfb-run for integration tests to support headless execution
  ([`7f75a75`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/7f75a75f0422909d0f27e261820b60cdeef28188))

- Use xvfb-run for unit tests to support headless execution
  ([`a769317`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a769317d7183c5abf6d7f634e767905237254485))

- **EP-022**: Replace hardcoded colors with DESIGN_TOKENS and add missing e2e tests
  ([`5a35fd0`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/5a35fd0b79f3f338ea0dbcee286815ab0314040f))

- Replace hex color literals with DESIGN_TOKENS references in rich_tooltip, about_dialog,
  dependency_indicator_delegate, and wave separators - Remove unused QColor import from
  rich_tooltip.py - Add 6 missing e2e test files: dependency indicator, rich tooltip, about dialog,
  cancellation flow, responsive layout, wave separators

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-026**: Fix move priority stale read and keyboard shortcuts
  ([`01f98c1`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/01f98c15ee9ded2daab6dc7bb84aad22aa691621))

Three bugs fixed: - load_stories() was called inside UoW context (before commit), causing the table
  to always show stale data after any CRUD operation. Moved load_stories() after UoW close in all 8
  affected viewmodel methods. - Alt+Up/Alt+Down keyboard shortcuts were swapped in main_window.py. -
  Priorities started at 1 instead of 0. Changed get_max_priority() to return -1 when empty, and
  allow move without swap for priority gaps.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-032**: Add PySide6 mock fixture to TestViewModelProperties for headless testing
  ([`cf13079`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/cf13079e8d14b5ac68af74b421ec3dc318ae1532))

Adds autouse fixture that manages PySide6 module mocks lifecycle, ensuring lazy imports succeed in
  headless CI environments.

- **EP-033**: Resolve SonarQube code quality issues across codebase
  ([`a1ca3ac`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a1ca3ac714d98569f9655fe41f22a239df0927b4))

Address code smells, cognitive complexity, and maintainability issues flagged by SonarQube analysis.
  Includes refactoring of allocation service, scheduling calculations, Excel import/export, and test
  improvements.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-034**: Resolve SonarQube quality gate issues
  ([`9b1b4ef`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/9b1b4efdeafcc14d7d3fe62d0ee5f6534c993817))

- Pin GitHub Actions to full SHA hashes for supply chain security - Pass secrets explicitly in
  publish workflow instead of inherit - Reduce cognitive complexity in allocation_service,
  extract_metrics, seed_test_backlog, and story_table_model via method extraction - Remove redundant
  except CancelledError:raise in main_window - Add SonarQube issue suppression for Qt mock naming
  conventions - Fix test_calculate_duration marked async but actually synchronous - Fix import
  formatting (blank line after stdlib) across test files

### Chores

- Update README.md to add spacing for better readability
  ([`2cfc938`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/2cfc938b46816769ea35323d9c25b6cf0d74d0ca))

### Code Style

- **EP-019**: Fix review issues - inline import, DTO enrichment, test fixture
  ([`1cd88ed`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/1cd88ed0c72dafd153bd5a1a121205882249b5a1))

- Move StoryTableModel import to top-level in main_window.py - Extract _enrich_dtos helper in
  ListStoriesUseCase for consistent DTO enrichment across all execute methods - Extract
  minimal_model fixture in TestStoryTableModelMissingValues - Add resizeEvent to StoryTableView for
  empty state label repositioning

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-024**: Fix formatting and linting issues
  ([`9509a06`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/9509a063c6833bb748b41832c134e2f5727c8c3d))

Auto-fix: pydocstyle missing docstring

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-029**: Fix formatting and linting issues
  ([`c322392`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/c3223920ccff013efd405f85ce5ff97e05636a22))

Auto-fix: pydocstyle missing/invalid docstrings

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-032**: Fix formatting and linting issues
  ([`0c009c8`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/0c009c8df7feff8f5d19c57027f9c9957770b996))

Add D101, D106, E402 to per-file-ignores for tests in pyproject.toml. Fix pre-existing B007/SIM102
  lint errors in scripts/.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

### Continuous Integration

- Add SonarCloud Quality Gate check to fail pipeline on gate failure
  ([`47244f5`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/47244f567590df5dd1185be3cf609389fb6daf78))

The Quality job was completing successfully even when SonarCloud Quality Gate reported ERROR status.
  Added sonarqube-quality-gate-action after the scan step to wait for server-side analysis and fail
  the job if the gate does not pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Bump minimum Python to 3.13 and update tooling targets
  ([`dffaac1`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/dffaac111fd008651d6d1af1c18674bafa6e27fd))

- Remove Python 3.11/3.12 classifiers, add 3.14 - Set python dependency to >=3.13,<3.15 - Update
  mypy python_version to 3.13 and ruff target to py312 - Remove main from CI push trigger branches

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- Restrict quality job to develop/main and SonarCloud to main only
  ([`923d60d`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/923d60d049b0359990472baf43572a9343147f41))

Quality job now only runs on push to develop/main or workflow_call events. SonarCloud scan is
  further restricted to main branch only.

- Update Python version matrix and adjust dependencies for consistency
  ([`559d2f3`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/559d2f3b9dda6f546ce18d823a8ca53eb0619a4a))

### Features

- Add --no-persist option for dry-run mode in allocation metrics extraction
  ([`6918ead`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/6918ead2a58df248219585e0aaeafb56d203d3b8))

- Add allocation criteria option for allocation analysis
  ([`16a50a0`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/16a50a0192bdacec9d6189174e7e042494003691))

- Add automated ship workflow for commit, PR, review, and merge processes
  ([`863f606`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/863f606566cf33a2d6f01d1b338d3ea411a763f3))

- Enhance allocation analysis skill with contradiction detection
  ([`964dcc0`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/964dcc0412f4a3ee627f8b811773288dbf6b70b6))

Improve diagnosis efficiency by adding:

1. Section 8.4: CC baseline capture before correction proposals 2. Section 8.2.3: Anomaly-to-code
  mapping table for quick code navigation 3. Section 8.2.2: Automatic contradiction detection rules
  4. extract_metrics.py: Detect contradictions (devs available but story not allocated) and flag as
  probable algorithm bug

These improvements reduce manual investigation time by ~25 minutes when diagnosing deadlock
  anomalies.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

- Enhance allocation analysis with validation of requirements and correction proposal process
  ([`83a63e8`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/83a63e8b15a343cc4920cc31ac46ae0af22455b5))

- Enhance deadlock diagnosis with raw data collection and verbose output
  ([`a468b9e`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a468b9e75afd5a71a34bf999f9e8b9c2e4c2e4ae))

- Enhance testing setup by adding poetry commands and adjusting E2E test timeouts
  ([`aa7a904`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/aa7a90463ed763bf9d37b3f94c57e83e685ff7ad))

- Implement EP-016 - Automacao do Ciclo de Analise de Alocacao
  ([`a3cf9f3`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a3cf9f3b2237cd4f36f06bf11a69d5c317099933))

- Add implementation plan, quickstart guide, research documentation, and feature specification for
  automating the allocation analysis cycle. - Create tasks for user stories related to the skill's
  functionality, including automated execution, log analysis, correction proposals, validation, and
  documentation. - Enhance logging in the allocation execution use case to include structured
  metrics and JSON format for easier extraction. - Modify SQLite connection to prioritize
  environment variable for database path. - Update application entry point to use the new database
  path retrieval method.

- **EP-017**: Implement design system foundation for visual standardization
  ([`4691036`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/4691036212e429a7d3bc32c1b3c619356dd2fd87))

Add comprehensive design system infrastructure: - Theme module with color tokens, typography, and
  spacing constants - QSS stylesheet with consistent styling for all Qt widgets - MonospaceDelegate
  for ID columns with proper font rendering - StatusBadgeDelegate for visual status indicators with
  color coding - SVG icon assets (Phosphor Icons) for UI actions - Integration with existing
  presentation layer

Includes: - Unit tests for delegates and theme components - Integration tests for theme application
  - Specification documents, plan, and task tracking - Epic documentation for EP-017 through EP-022
  (GUI refactor roadmap)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

- **EP-018**: Implement layout migration with panels, dialogs, and status bar
  ([`966d896`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/966d8966f940d570dcb23246412653972c7ab542))

Migrate main window to panel-based layout with config dialog, dependency dialog, metrics dialog, and
  status bar. Add corresponding viewmodels and comprehensive tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-019**: Implement backlog table with StoryTableModel and delegates
  ([`9b101e4`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/9b101e42d16608de9f6fd16f970fe243d9822c4f))

Add QTableView-based backlog table with column configuration, status badge delegate, monospace ID
  delegate, date formatting, empty state overlay, and zebra striping. Update ListStories use case
  with sorting/filtering support and extend StoryOutputDTO with display fields.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-020**: Implement search, filters, and context menu for backlog table
  ([`86546ce`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/86546ce6a0c122cb7499b382f39224bb8a64dda4))

Add FilterProxyModel with text search, status/priority/sprint filters, and right-click context menu.
  Includes toolbar UI, stylesheet updates, unit tests, integration tests, and full spec
  documentation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-021**: Style dialogs with design system and add progress/result dialogs
  ([`b7a3274`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/b7a327451225fd735a914fa9fb6e12df7a4f4818))

Implement consistent styling for all dialogs (story, feature, developer, confirm delete) using QSS
  stylesheet and object names. Add new ProgressDialog and ResultDialog components. Extend
  StoryDialog with priority/status fields and edit mode support. Include comprehensive unit and
  integration tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-022**: Add UX polish with rich tooltips, dependency indicators, and status bar enhancements
  ([`1d82bfa`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/1d82bfaf165a68c9b7cb53f0bab027a6f30b54e7))

- Add rich tooltip popup with story details and dependency info - Add dependency indicator delegate
  for table cells - Enhance status bar with SP breakdown by section - Add QSettings persistence for
  config dialog preferences - Add About dialog with app version info - Enhance progress dialog with
  cancellation support - Add keyboard shortcuts and responsive layout to main window - Add
  comprehensive unit tests for new viewmodel and view features

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-023**: Add reset planning feature with confirmation dialog
  ([`ea78707`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/ea78707267b7ee62daff7ab70d72101fe723d052))

Implement reset planning functionality that allows users to clear all sprint/priority assignments
  from stories. Includes confirmation dialog with affected story count, use cases for counting and
  resetting, DTOs, viewmodel, and comprehensive unit/e2e tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-025**: Add table selection highlight with themed styling
  ([`a568e93`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/a568e933b81c517f40e508dc7573e20b81d1eccd))

Implement row selection highlighting in QTableView with design system colors, selection-aware
  delegates, and keyboard navigation support. Includes constants module, theme selection colors, and
  comprehensive tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-027**: Add column resize with persistence via QSettings
  ([`c40e7d2`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/c40e7d2ff9668cabc72dc9a6e2aa14628adaefd8))

Implement interactive column resizing for the story table with width persistence using QSettings.
  Includes default column widths, user resize handling, save/restore logic, and comprehensive unit
  tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-028**: Add manual developer allocation dialog
  ([`45fdd7c`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/45fdd7c2e51332c38e927fcae512d051cedf80c8))

Implement manual allocation dialog triggered by double-click on Developer column. Dialog displays
  developers classified as Free/Occupied with recommendation from allocation algorithm, date picker
  with workday restriction for start date recalculation, and persist allocation via existing
  EditStoryUseCase.

New files: - GetDeveloperAvailabilityUseCase (Application layer) - ManualAllocationDialogViewModel
  (Presentation layer) - ManualAllocationDialog (QDialog with QTreeWidget) - DTOs:
  DeveloperAvailabilityDTO, BlockingStoryDTO, Input/OutputDTO - 21 unit tests (9 use case + 12
  viewmodel)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-030**: Add .env support for PyPI token management
  ([`d8ae592`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/d8ae592b86daad2af1262b54ecc7ffafbf561b8c))

- Load tokens from .env via python-dotenv - Separate PYPI_TOKEN and TESTPYPI_TOKEN for each registry
  - Replace Unicode chars with ASCII for Windows compatibility - Add python-dotenv as dev dependency

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-030**: Add PyPI publish setup with build config and publish script
  ([`214a162`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/214a1620022b4e05d0748d7fa3ee1bbc8ecdf986))

Configure pyproject.toml for PyPI distribution (name, classifiers, entry points) and add
  publish_to_pypi.py helper script. Includes full spec and planning artifacts.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-031**: Add CI/CD pipeline with GitFlow, quality gates and PyPI publish
  ([`bb8eec8`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/bb8eec8bd46bb350e5f6de9c4f5d2658aa9eff2d))

- Replace tests.yml with ci.yml (lint, test matrix 3.11/3.12/3.13, quality) - Add publish.yml with
  OIDC Trusted Publishers for PyPI/TestPyPI - Add codecov.yml and sonar-project.properties for
  quality gates - Add .github/release.yml for auto-generated release notes - Create CONTRIBUTING.md
  (GitFlow docs, versioning, migration notes) - Create SETUP_CI.md (secrets, OIDC, environments,
  branch protection) - Add badges to README.md (CI, Codecov, SonarCloud, PyPI, License) - Complete
  pyproject.toml metadata (classifiers, URLs)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-035**: Add spec artifacts and refactor seed script
  ([`f4606c7`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/f4606c766f94472c419082d0af0a30adc2678cc6))

Add specification documents (spec, plan, tasks, research, data-model, checklists, quickstart) for
  SonarQube issues resolution epic. Extract _try_create_inter_wave_dep helper to reduce cognitive
  complexity.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

- **EP-037**: Add auto-versioning and CI/CD workflow automation
  ([`caf08ab`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/caf08ab0e7a95bcdf78d6905b0958406ca8c01d6))

Add python-semantic-release config, feature CI, develop merge, and main release workflows with auto
  PR creation and backmerge support.

### Refactoring

- Rearrange imports and enhance focus event processing in StoryDialog validation tests
  ([`d7660ab`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/d7660ab7742109b0bf16244fa65e6c29355b2eef))

- Update imports and improve type hints across delegates and models
  ([`7ec9608`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/7ec960812f4a149d94740d07dbeded1bd527257b))

### Testing

- Expand test coverage from 91% to 98% and align SonarQube exclusions
  ([`2a82ebe`](https://github.com/tuyoshivinicius/zion-backlog-manager/commit/2a82ebe6d756cbe0a76ef5a67e9c9b02e776ba2c))

- Align sonar.coverage.exclusions with pytest-cov omit patterns to eliminate SonarQube vs local
  coverage divergence (56.7% → ~94% on SonarCloud) - Add 194 new unit tests covering 16 priority
  files across all tiers - All 16 target files now at 90%+ individual coverage (most at 97-100%) -
  Total coverage: 90.85% → 97.90%, 1241 tests passing with zero regressions

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
