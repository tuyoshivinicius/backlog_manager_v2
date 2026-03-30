# Tasks: Estilizacao de Dialogs

**Input**: Design documents from `/specs/021-estilizacao-dialogs/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included — spec.md defines explicit test specifications (unit + integration).

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup needed — project already exists. This phase is empty.

**Checkpoint**: Ready for foundational tasks.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DTO and use case changes that MUST be complete before US1 can be implemented

**⚠️ CRITICAL**: US1 (developer field) cannot begin until these tasks are complete

- [X] T001 Add `developer_id: int | None = None` field to `EditStoryInputDTO` in `src/backlog_manager/application/dto/story/edit_story_dto.py`
- [X] T002 Add `developer_id` propagation to `EditStoryUseCase.execute()` in `src/backlog_manager/application/use_cases/story/edit_story.py` — always apply value (not conditional like other fields, per R-010)
- [X] T002B [P] Unit test `test_edit_story_propagates_developer_id` — verify execute() sets developer_id on entity when provided in `tests/unit/application/use_cases/story/test_edit_story.py`
- [X] T002C [P] Unit test `test_edit_story_clears_developer_id` — verify execute() clears developer_id when None is provided (desatribuicao) in `tests/unit/application/use_cases/story/test_edit_story.py`

**Checkpoint**: Foundation ready — DTO accepts developer_id, use case propagates it, and propagation is tested. User story implementation can now begin.

---

## Phase 3: User Story 1 — Editar Historia com Atribuicao de Desenvolvedor (Priority: P1) 🎯 MVP

**Goal**: O usuario abre o dialog de edicao de historia e atribui um desenvolvedor via dropdown.

**Independent Test**: Abrir dialog edicao, verificar dropdown visivel e populado, selecionar dev, salvar, reabrir e confirmar persistencia.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T003 [P] [US1] Unit test `test_developer_id_property_get_set` — property accepts int and None in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T004 [P] [US1] Unit test `test_developer_id_initial_none` — initial value is None in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T005 [P] [US1] Unit test `test_set_story_loads_developer_id` — loading story recovers developer_id in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T006 [P] [US1] Unit test `test_load_developers_returns_list` — load populates list via ListDevelopersUseCase in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T006B [P] [US1] Unit test `test_load_developers_includes_none_option` — loaded list allows "Nenhum" (no developer) as first dropdown option in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T007 [P] [US1] Unit test `test_load_developers_error_emits_signal` — load failure emits error_occurred in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T008 [P] [US1] Unit test `test_save_with_developer_id` — save in edit mode includes developer_id in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T009 [P] [US1] Unit test `test_save_without_developer` — save in edit mode without developer in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T010 [P] [US1] Integration test `test_story_dialog_developer_field_visible_edit_mode` in `tests/integration/presentation/views/test_story_dialog.py`
- [X] T011 [P] [US1] Integration test `test_story_dialog_developer_field_hidden_create_mode` in `tests/integration/presentation/views/test_story_dialog.py`

### Implementation for User Story 1

- [X] T012 [US1] Add `_developer_id`, `_developers`, `developers_loaded` signal, `developer_id` property, `load_developers()` async method to `StoryDialogViewModel` in `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py`
- [X] T013 [US1] Update `set_story()` to load `developer_id` from `StoryOutputDTO` in `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py`
- [X] T014 [US1] Update `save()` to include `developer_id` in `EditStoryInputDTO` (always sent, per R-010) in `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py`
- [X] T015 [US1] Add developer combo (`QComboBox`), label, and container (`QWidget`) to `StoryDialog` in `src/backlog_manager/presentation/views/story_dialog.py` — visible only in edit mode (ADR-003)
- [X] T016 [US1] Connect `developers_loaded` signal to `_on_developers_loaded` handler that populates combo with "Nenhum" + developers in `src/backlog_manager/presentation/views/story_dialog.py`
- [X] T017 [US1] Add `setObjectName()` calls for story dialog widgets (`story-dialog`, `story-component-field`, `story-name-field`, `story-developer-combo`, `story-developer-container`, `story-save-button`, `story-cancel-button`, `story-points-combo`, `story-feature-combo`) in `src/backlog_manager/presentation/views/story_dialog.py`

**Checkpoint**: US1 fully functional — developer dropdown visible in edit mode, persists selection.

---

## Phase 4: User Story 2 — Validacao em Tempo Real nos Campos do Dialog de Historia (Priority: P1)

**Goal**: Feedback visual imediato on-blur em campos obrigatorios, asterisco (*), contagem de caracteres, botao Salvar desabilitado.

**Independent Test**: Abrir dialog, clicar campo obrigatorio, sair sem preencher — borda vermelha e mensagem aparecem. Botao Salvar desabilitado.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US2] Unit test `test_validate_field_component_empty` — returns (False, "Campo obrigatorio") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T019 [P] [US2] Unit test `test_validate_field_component_too_long` — returns (False, "Maximo de 50 caracteres") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T020 [P] [US2] Unit test `test_validate_field_component_valid` — returns (True, "") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T021 [P] [US2] Unit test `test_validate_field_name_empty` — returns (False, "Campo obrigatorio") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T022 [P] [US2] Unit test `test_validate_field_name_too_long` — returns (False, "Maximo de 200 caracteres") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T023 [P] [US2] Unit test `test_validate_field_name_valid` — returns (True, "") in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T024 [P] [US2] Unit test `test_validate_field_unknown` — returns (True, "") for unknown fields in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T025 [P] [US2] Unit test `test_validate_global_still_works` — existing validate() unchanged in `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- [X] T026 [P] [US2] Integration test `test_story_dialog_required_indicators` — asterisk (*) on Componente and Nome labels in `tests/integration/presentation/views/test_story_dialog.py`
- [X] T027 [P] [US2] Integration test `test_story_dialog_error_on_blur` — red border and error label on focusOut in `tests/integration/presentation/views/test_story_dialog.py`
- [X] T028 [P] [US2] Integration test `test_story_dialog_save_button_disabled` — button disabled when fields invalid in `tests/integration/presentation/views/test_story_dialog.py`

### Implementation for User Story 2

- [X] T029 [US2] Add `validate_field(field_name: str) -> tuple[bool, str]` method to `StoryDialogViewModel` with dispatch table per contracts/viewmodel-signals.md in `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py`
- [X] T030 [US2] Add required indicators (`QLabel` with `*`, objectName `required-indicator`) next to Componente and Nome labels in `src/backlog_manager/presentation/views/story_dialog.py`
- [X] T031 [US2] Add error labels (`QLabel`, objectName `field-error-label`) below Componente and Nome fields, initially hidden in `src/backlog_manager/presentation/views/story_dialog.py`
- [X] T032 [US2] Add char count labels (`QLabel`, objectName `field-char-count`) below Componente ("N/50") and Nome ("N/200") fields, connected to `textChanged` — handler MUST also toggle `setProperty("warning", "true"/"false")` when char count reaches >= 90% of limit (45/50 for Componente, 180/200 for Nome) per FR-016 in `src/backlog_manager/presentation/views/story_dialog.py`
- [X] T033 [US2] Connect `focusOut` events on Componente and Nome fields to `validate_field()` — apply/remove error border via `setProperty("error", "true"/"false")` and show/hide error label in `src/backlog_manager/presentation/views/story_dialog.py`
- [X] T034 [US2] Implement save button enable/disable logic — re-evaluate on each focusOut, re-enable on textChanged when field becomes valid (ADR-004) in `src/backlog_manager/presentation/views/story_dialog.py`

**Checkpoint**: US2 fully functional — on-blur validation, asterisks, char count, save button state management.

---

## Phase 5: User Story 4 — Dialog de Desenvolvedores com Icones, Hover e Estado Vazio (Priority: P2)

**Goal**: Icones nos botoes, hover em itens da lista, estado vazio orientativo.

**Independent Test**: Abrir dialog vazio — mensagem orientativa visivel. Adicionar dev — mensagem desaparece. Verificar icones nos botoes.

### Tests for User Story 4

- [X] T035 [P] [US4] Integration test `test_developer_dialog_icons` — all buttons have non-null icons in `tests/integration/presentation/views/test_developer_dialog.py`
- [X] T036 [P] [US4] Integration test `test_developer_dialog_empty_state` — empty list shows orientative message via QStackedWidget in `tests/integration/presentation/views/test_developer_dialog.py`

### Implementation for User Story 4

- [X] T037 [US4] Add `QStackedWidget` (objectName `developer-stacked`) with index 0 = list, index 1 = empty state label (objectName `developer-empty-state`) in `src/backlog_manager/presentation/views/developer_dialog.py`
- [X] T038 [US4] Add `_update_empty_state()` method — toggle stacked index based on `list.count()`, called after load/add/remove in `src/backlog_manager/presentation/views/developer_dialog.py`
- [X] T039 [US4] Add icons to buttons via `IconManager.get()` — plus (Adicionar), pencil-simple (Editar), trash (Remover), x (Fechar), size 16x16 in `src/backlog_manager/presentation/views/developer_dialog.py`
- [X] T040 [US4] Set `setObjectName()` for all widgets per contracts/qss-object-names.md (`developer-dialog`, `developer-list`, `developer-add-button`, `developer-edit-button`, `developer-remove-button`, `developer-close-button`) in `src/backlog_manager/presentation/views/developer_dialog.py`
- [X] T041 [US4] Set list item height to 40px via `setSizeHint` or stylesheet in `src/backlog_manager/presentation/views/developer_dialog.py`

**Checkpoint**: US4 functional — icons, hover, empty state toggling.

---

## Phase 6: User Story 5 — Dialog de Features com Formato "Onda N — Nome" e Estado Vazio (Priority: P2)

**Goal**: Itens da lista formatados como "Onda N — Nome", estado vazio orientativo.

**Independent Test**: Abrir dialog com features — formato "Onda 2 — Login". Abrir sem features — mensagem orientativa.

### Tests for User Story 5

- [X] T042 [P] [US5] Integration test `test_feature_dialog_wave_format` — items display "Onda N — Nome" format in `tests/integration/presentation/views/test_feature_dialog.py`
- [X] T043 [P] [US5] Integration test `test_feature_dialog_empty_state` — empty list shows orientative message in `tests/integration/presentation/views/test_feature_dialog.py`

### Implementation for User Story 5

- [X] T044 [US5] Add `QStackedWidget` (objectName `feature-stacked`) with index 0 = list, index 1 = empty state label (objectName `feature-empty-state`) in `src/backlog_manager/presentation/views/feature_dialog.py`
- [X] T045 [US5] Add `_update_empty_state()` method — toggle stacked index, called after load/add/remove in `src/backlog_manager/presentation/views/feature_dialog.py`
- [X] T046 [US5] Format list items as `"Onda {wave} — {name}"` in `src/backlog_manager/presentation/views/feature_dialog.py`
- [X] T047 [US5] Set `setObjectName()` for all widgets per contracts/qss-object-names.md (`feature-dialog`, `feature-list`, `feature-empty-state`, `feature-stacked`) in `src/backlog_manager/presentation/views/feature_dialog.py`

**Checkpoint**: US5 functional — wave format, empty state toggling.

---

## Phase 7: User Story 6 — Dialog de Confirmacao de Exclusao com Alerta Visual (Priority: P2)

**Goal**: Icone de alerta, texto descritivo por entidade, botao vermelho "Confirmar Exclusao".

**Independent Test**: Abrir dialog para historia — "Excluir API-001 — Criar endpoint?", icone, botao vermelho. Testar para dev e feature.

### Tests for User Story 6

- [X] T048 [P] [US6] Integration test `test_confirm_delete_dialog_story` — text "Excluir {id} — {nome}?" in `tests/integration/presentation/views/test_confirm_delete_dialog.py`
- [X] T049 [P] [US6] Integration test `test_confirm_delete_dialog_developer` — text "Excluir {nome}?" in `tests/integration/presentation/views/test_confirm_delete_dialog.py`
- [X] T050 [P] [US6] Integration test `test_confirm_delete_dialog_feature` — text "Excluir Onda {N} — {nome}?" in `tests/integration/presentation/views/test_confirm_delete_dialog.py`
- [X] T051 [P] [US6] Integration test `test_confirm_delete_dialog_red_button` — confirm button has danger style in `tests/integration/presentation/views/test_confirm_delete_dialog.py`

### Implementation for User Story 6

- [X] T052 [US6] Refactor `ConfirmDeleteDialog.__init__()` to accept generic `main_text` and `detail_text` parameters in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T053 [US6] Add factory methods `for_story()`, `for_developer()`, `for_feature()` per contracts/viewmodel-signals.md in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T054 [US6] Add alert icon (`QLabel` with `QPixmap`, 32x32px, objectName `confirm-delete-icon`) and layout with icon left, text right in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T055 [US6] Add detail text label ("Esta acao nao pode ser desfeita.", objectName `confirm-delete-detail-text`) below main text in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T056 [US6] Style confirm button ("Confirmar Exclusao", objectName `confirm-delete-button`) and cancel button (objectName `confirm-delete-cancel-button`) in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T057 [US6] Set `setObjectName("confirm-delete-dialog")` on dialog and `setObjectName("confirm-delete-main-text")` on main text label in `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- [X] T058 [US6] Update existing callers to use `ConfirmDeleteDialog.for_story()` instead of direct constructor

**Checkpoint**: US6 functional — entity-specific text, alert icon, red button.

---

## Phase 8: User Story 7 — Feedback Estilizado de Import/Export Excel (Priority: P3)

**Goal**: Dialog de progresso modal com barra estilizada durante import. Dialog de resultado com contagens apos conclusao.

**Independent Test**: Executar import Excel — dialog progresso aparece com barra, seguido por dialog resultado com contagens.

### Tests for User Story 7

- [X] T059 [P] [US7] Integration test `test_progress_dialog_creation` — bar and message label present in `tests/integration/presentation/views/test_progress_dialog.py`
- [X] T060 [P] [US7] Integration test `test_progress_dialog_update` — values reflect parameters in `tests/integration/presentation/views/test_progress_dialog.py`
- [X] T061 [P] [US7] Integration test `test_result_dialog_import` — labels show formatted counts in `tests/integration/presentation/views/test_result_dialog.py`
- [X] T062 [P] [US7] Integration test `test_result_dialog_export` — label shows file path in `tests/integration/presentation/views/test_result_dialog.py`

### Implementation for User Story 7

- [X] T063 [P] [US7] Create `ProgressDialog` in `src/backlog_manager/presentation/views/progress_dialog.py` — QDialog with QProgressBar (objectName `progress-bar`), QLabel (objectName `progress-message`), objectName `progress-dialog`, modal, not closable, supports `update_progress()` and `set_indeterminate()` (ADR-008)
- [X] T064 [P] [US7] Create `ResultDialog` in `src/backlog_manager/presentation/views/result_dialog.py` — QDialog with title label (objectName `result-title`), details label (objectName `result-details`), close button (objectName `result-close-button`), objectName `result-dialog`, factory methods `for_import()` and `for_export()`

**Checkpoint**: US7 functional — progress and result dialogs created and tested.

---

## Phase 9: User Story 3 — Dialogs com Estilizacao Visual Consistente (Priority: P2)

**Goal**: QSS centralizado com regras para todos os dialogs — bordas arredondadas, espacamento, cores, estados de erro, botoes especiais.

**Independent Test**: Abrir cada dialog e verificar estilizacao consistente — bordas, espacamento 16px, padding 24px, titulo 16px weight 600.

### Implementation for User Story 3

- [X] T065 [US3] Add dialog-level QSS rules for `#story-dialog`, `#developer-dialog`, `#feature-dialog`, `#confirm-delete-dialog`, `#progress-dialog`, `#result-dialog` (border-radius, padding 24px, spacing 16px, title font 16px weight 600) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T066 [US3] Add error state QSS rules — `QLineEdit[error="true"]` (red border), `#field-error-label` (red bg, red text, padding) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T067 [US3] Add required indicator QSS rule — `#required-indicator` (red color, bold font) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T068 [US3] Add empty state QSS rules — `#developer-empty-state`, `#feature-empty-state` (neutral color, centered) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T069 [US3] Add special button QSS rules — `#confirm-delete-button` (red bg, white text), `#story-save-button:disabled` (grey bg) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T070 [US3] Add progress bar QSS rule — `#progress-bar` (primary color) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T071 [US3] Add char count QSS rules — `#field-char-count` (secondary color, reduced font), `#field-char-count[warning="true"]` (alert color) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T072 [US3] Add hover QSS rule for developer list items — `#developer-list::item:hover` (highlight) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [X] T073 [US3] Verify no conflicts with existing QSS rules (SearchField, FilterChip, warnings-badge, etc.) in `src/backlog_manager/presentation/theme/stylesheet.qss`

**Checkpoint**: US3 functional — all dialogs visually consistent via centralized QSS.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [X] T074 Run all existing tests to verify zero regressions — `poetry run pytest tests/ -v`
- [X] T075 Run quickstart.md validation — verify all test commands and app launch work
- [X] T076 Run formatting and type checks — `poetry run black src/ tests/ && poetry run isort src/ tests/ && poetry run mypy src/backlog_manager/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: No dependencies — can start immediately. BLOCKS US1.
- **US1 (Phase 3)**: Depends on Phase 2 (DTO + UseCase)
- **US2 (Phase 4)**: Depends on Phase 3 (modifies same ViewModel/View files as US1)
- **US4 (Phase 5)**: Depends on Phase 2 only — can run in parallel with US1
- **US5 (Phase 6)**: Depends on Phase 2 only — can run in parallel with US1
- **US6 (Phase 7)**: Depends on Phase 2 only — can run in parallel with US1
- **US7 (Phase 8)**: No dependencies on other stories — can run in parallel with US1
- **US3 (Phase 9)**: Depends on US1, US2, US4, US5, US6, US7 (objectNames must be in place before QSS rules)
- **Polish (Phase 10)**: Depends on all phases complete

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational (T001, T002). No other story dependencies.
- **US2 (P1)**: Same ViewModel/View files as US1 — implement after US1 to avoid merge conflicts.
- **US3 (P2)**: Cross-cutting QSS — implement after all objectNames are set (US1, US4, US5, US6, US7).
- **US4 (P2)**: Independent — only modifies `developer_dialog.py`.
- **US5 (P2)**: Independent — only modifies `feature_dialog.py`.
- **US6 (P2)**: Independent — only modifies `confirm_delete_dialog.py`.
- **US7 (P3)**: Independent — creates new files only.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- ViewModel changes before View changes
- Core logic before integration/wiring

### Parallel Opportunities

- All test tasks marked [P] within a story can run in parallel
- **After Phase 2**: US4, US5, US6, US7 can all run in parallel (different files)
- **After US1**: US2 can start (same files but different methods)
- **QSS (US3)**: Can start partially after each dialog gets objectNames, or all at once after US1-US7
- T063 and T064 (ProgressDialog + ResultDialog) can run in parallel

---

## Parallel Example: User Story 4 (DeveloperDialog)

```bash
# Launch tests in parallel:
Task: "Integration test test_developer_dialog_icons in tests/integration/presentation/views/test_developer_dialog.py"
Task: "Integration test test_developer_dialog_empty_state in tests/integration/presentation/views/test_developer_dialog.py"

# Then implement sequentially (same file):
Task: "Add QStackedWidget with empty state"
Task: "Add _update_empty_state() method"
Task: "Add icons to buttons via IconManager"
Task: "Set objectNames"
Task: "Set list item height"
```

## Parallel Example: After Phase 2 (Independent Stories)

```bash
# These stories can run in parallel (different files):
US4: developer_dialog.py (icons, hover, empty state)
US5: feature_dialog.py (wave format, empty state)
US6: confirm_delete_dialog.py (alert, factory methods)
US7: progress_dialog.py + result_dialog.py (new files)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 2: Foundational (T001-T002)
2. Complete Phase 3: US1 — Developer field (T003-T017)
3. **STOP and VALIDATE**: Test US1 independently — dropdown visible in edit mode, persists selection
4. Deploy/demo if ready

### Incremental Delivery

1. Phase 2 → Foundation ready
2. US1 → Developer field functional → Test (MVP!)
3. US2 → Validation on-blur functional → Test
4. US4 + US5 + US6 + US7 (parallel) → All dialogs enhanced → Test each
5. US3 → QSS rules → All dialogs visually consistent → Test
6. Polish → Zero regressions confirmed

### Parallel Team Strategy

With multiple developers:

1. Team completes Foundational (Phase 2) together
2. Once Foundational is done:
   - Developer A: US1 → US2 (sequential, same files)
   - Developer B: US4 + US5 (sequential, small scope)
   - Developer C: US6 + US7 (sequential, different files)
3. Once all objectNames set: Anyone → US3 (QSS)
4. Polish together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US3 (QSS) is intentionally last because it depends on objectNames from all other stories
