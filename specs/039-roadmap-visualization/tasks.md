# Tasks: Visualizacao de Roadmap

**Input**: Design documents from `/specs/039-roadmap-visualization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/roadmap-ui-contract.md, quickstart.md

**Tests**: Included (plan.md specifies pytest, pytest-qt, pytest-asyncio, pytest-cov).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/presentation/`
- **Tests**: `tests/unit/presentation/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new module files and project structure for the roadmap feature

- [X] T001 Create empty module files: `src/backlog_manager/presentation/views/roadmap_dialog.py` and `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T002 [P] Create empty test files: `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py` and `tests/unit/presentation/views/test_roadmap_dialog.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Presentation-layer dataclasses, DI registration, and MainWindow entry point that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Implement RoadmapGroupMode enum, RoadmapIndicators dataclass, RoadmapGroup dataclass (with completion_percent and has_scheduled_stories properties), and RoadmapData dataclass in `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` (per data-model.md)
- [X] T004 [P] Register RoadmapViewModel in DIContainer: add `roadmap_viewmodel` property wiring ListStoriesUseCase and ListFeaturesUseCase in `src/backlog_manager/presentation/container.py`
- [X] T005 Add "Roadmap" action to MainWindow toolbar (Group 4 — Processing) and &Ferramentas menu in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Visualizar Roadmap com Timeline (Priority: P1) MVP

**Goal**: Gestor abre tela fullscreen com grafico Gantt-like mostrando barras de historia posicionadas temporalmente, agrupadas por feature (modo padrao). Valida que existem historias com datas antes de abrir.

**Independent Test**: Abrir roadmap com backlog que tenha historias com datas calculadas e verificar que todas as barras aparecem posicionadas corretamente no eixo temporal.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Unit tests for RoadmapViewModel.__init__() and async load_data() (returns RoadmapData with groups, dates, counts; returns None when no scheduled stories) in `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`
- [X] T007 [P] [US1] Widget tests for RoadmapDialog instantiation, QGraphicsScene population (correct number of bar items), and empty-state validation message in `tests/unit/presentation/views/test_roadmap_dialog.py`

### Implementation for User Story 1

- [X] T008 [US1] Implement RoadmapViewModel.__init__(list_stories_use_case, list_features_use_case) and async load_data() → RoadmapData | None: loads stories/features, groups by feature (default), calculates min/max dates and counts in `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T009 [US1] Implement StoryBarItem (QGraphicsRectItem subclass) with status-based colors from STATUS_PALETTE (theme.py), story name text inside bar, and date-based positioning (X = days offset * pixels_per_day, width = duration * pixels_per_day) in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T010 [US1] Implement RoadmapDialog constructor: QDialog with QVBoxLayout, QGraphicsView + QGraphicsScene, time axis header (date labels), group rendering with feature headers, and status bar (story count + date range) per layout in contracts/roadmap-ui-contract.md in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T011 [US1] Implement fixed group label panel (QWidget left of QGraphicsView) synced via verticalScrollBar().valueChanged signal per research.md R4 in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T012 [US1] Implement horizontal zoom (Ctrl+scroll wheel override of wheelEvent, scale X only via setTransform, factor 1.25x/0.8x, AnchorUnderMouse) and scroll navigation per research.md R3 in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T013 [US1] Wire MainWindow "Roadmap" action: async load via qasync, validate data (QMessageBox if None), instantiate RoadmapDialog(data, indicators, parent) and showMaximized() in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: User Story 1 fully functional — gestor pode abrir roadmap e ver timeline com barras posicionadas

---

## Phase 4: User Story 2 — Agrupamento e Progresso por Feature/Componente (Priority: P2)

**Goal**: Gestor alterna agrupamento entre "por Feature" e "por Componente" com indicador de percentual de conclusao por grupo.

**Independent Test**: Alternar entre modos de agrupamento e verificar que grupos mudam corretamente e percentual reflete proporcao real de historias concluidas.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US2] Unit tests for RoadmapViewModel.regroup(mode) — verify groups change between feature/component, stories without classification go to "Sem classificacao", completion_percent is accurate in `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`

### Implementation for User Story 2

- [X] T015 [US2] Implement RoadmapViewModel.regroup(mode: RoadmapGroupMode) → RoadmapData: regroups cached stories by feature or component, recalculates group completion percentages in `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T016 [US2] Add grouping toolbar with QComboBox (Feature/Componente) and group_mode_changed signal emission in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T017 [US2] Implement update_data(RoadmapData) slot: clears and re-renders QGraphicsScene with new groups, updates group label panel and completion percentages in headers in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T018 [US2] Connect group_mode_changed signal → ViewModel.regroup() → update_data() flow in MainWindow/Dialog wiring in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: User Stories 1 AND 2 independently functional — agrupamento alterna corretamente

---

## Phase 5: User Story 3 — Tooltip Rico com Detalhes da Historia (Priority: P3)

**Goal**: Hover sobre barra exibe tooltip HTML com desenvolvedor, story points, status, dependencias, datas, duracao e componente.

**Independent Test**: Passar mouse sobre diferentes barras e verificar que todas as informacoes esperadas aparecem no tooltip.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [P] [US3] Unit tests for tooltip HTML generation: verify all 7 fields present, "Nao alocado" when no developer, "Sem dependencias" when no deps in `tests/unit/presentation/views/test_roadmap_dialog.py`

### Implementation for User Story 3

- [X] T020 [US3] Implement _build_tooltip_html(story: StoryOutputDTO) helper and apply via setToolTip(html) on each StoryBarItem per contracts/roadmap-ui-contract.md tooltip format in `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: Tooltip funcional em todas as barras de historia

---

## Phase 6: User Story 4 — Indicadores Visuais Opcionais (Priority: P4)

**Goal**: Toggles independentes para atraso, criticidade de dependencias e deadlines com persistencia via QSettings.

**Independent Test**: Ativar/desativar cada indicador e verificar representacao visual; reabrir roadmap e confirmar que preferencias persistem.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T021 [P] [US4] Unit tests for is_overdue(story, today) and is_critical_blocker(story, all_stories) logic in `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`
- [X] T022 [P] [US4] Unit tests for load_indicators() and save_indicators() QSettings round-trip persistence in `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`

### Implementation for User Story 4

- [X] T023 [US4] Implement is_overdue(story, today) and is_critical_blocker(story, all_stories) methods in `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T024 [US4] Implement load_indicators() and save_indicators(indicators) with QSettings group "RoadmapIndicators" (type=bool reads) per research.md R6 in `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T025 [US4] Add indicator toggle QCheckBoxes (Atraso, Criticidade, Deadlines) to toolbar and emit indicators_changed signal in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T026 [US4] Implement update_indicators(RoadmapIndicators) slot: apply overdue highlight (red dashed border + warning icon), critical blocker highlight (thick orange border), and deadline vertical lines per data-model.md indicators table in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T027 [US4] Connect indicators_changed signal → save_indicators() + update_indicators() flow; load initial state from load_indicators() on dialog open in `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: Todos os indicadores visuais funcionais com persistencia entre sessoes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Performance, edge cases, and final validation

- [X] T028 [P] Apply performance optimizations: BspTreeIndex, DeviceCoordinateCache on bars, SmartViewportUpdate, DontAdjustForAntialiasing per research.md R2 in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T029 [P] Handle edge cases: empty groups not rendered, "Sem classificacao" group for stories without feature/component, window resize responsiveness, 200+ stories layout legibility in `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T030 Run quickstart.md validation — verify full workflow from MainWindow button to roadmap display with all interactions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion
  - US1 (P1): No dependencies on other stories — **MVP**
  - US2 (P2): Independent of US1 (uses same ViewModel data)
  - US3 (P3): Depends on US1 (needs StoryBarItem to exist for setToolTip)
  - US4 (P4): Depends on US1 (needs StoryBarItem to exist for visual overlays)
- **Polish (Phase 7)**: Depends on all user stories being complete

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- ViewModel logic before Dialog rendering
- Core rendering before interaction wiring
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel
- **Phase 2**: T003, T004 can run in parallel; T005 depends on T004 (needs DI registration)
- **Phase 3 (US1)**: T006 and T007 (tests) in parallel; T009 and T011 in parallel (different concerns in same file)
- **Phase 4 (US2)**: T014 (test) independent; T016 and T015 in parallel (dialog vs viewmodel)
- **Phase 5 (US3)**: T019 (test) then T020 (implementation)
- **Phase 6 (US4)**: T021, T022 (tests) in parallel; T023 and T024 in parallel (different methods)
- **Phase 7**: T028 and T029 in parallel

---

## Parallel Example: User Story 1

```bash
# Launch tests in parallel:
Task T006: "Unit tests for ViewModel.load_data() in tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py"
Task T007: "Widget tests for RoadmapDialog in tests/unit/presentation/views/test_roadmap_dialog.py"

# After tests written, launch independent implementation tasks:
Task T009: "StoryBarItem with status colors in roadmap_dialog.py"
Task T011: "Fixed group label panel in roadmap_dialog.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001–T002)
2. Complete Phase 2: Foundational (T003–T005)
3. Complete Phase 3: User Story 1 (T006–T013)
4. **STOP and VALIDATE**: Test timeline rendering independently
5. Deploy/demo if ready — gestor ja consegue visualizar roadmap

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test → **MVP! Timeline funcional**
3. Add US2 → Test → Agrupamento e progresso
4. Add US3 → Test → Tooltips ricos
5. Add US4 → Test → Indicadores visuais com persistencia
6. Polish → Performance + edge cases
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (timeline core)
   - Developer B: User Story 2 (agrupamento — pode iniciar em paralelo)
3. After US1 done:
   - Developer A: User Story 3 (tooltip — depende de StoryBarItem)
   - Developer B: User Story 4 (indicadores — depende de StoryBarItem)
4. Final: Polish together

---

## Notes

- [P] tasks = different files or independent concerns, no blocking dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All new code in Presentation layer only — no domain/infrastructure changes
- Reuse existing use cases (ListStoriesUseCase, ListFeaturesUseCase) and STATUS_PALETTE from theme.py
