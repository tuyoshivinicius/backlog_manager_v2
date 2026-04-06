# Tasks: Roadmap UX Refactor

**Input**: Design documents from `/specs/043-roadmap-ux-refactor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contract.md, quickstart.md

**Tests**: Incluidos — plan.md especifica testes headless para pan state, cursor changes e keyboard nav.

**Organization**: Tasks agrupadas por user story. Conforme research R13, a maioria das funcionalidades (US1-US7) ja esta implementada. O delta real e concentrado em pan/drag (US5b) e testes associados.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Validar implementacao existente e preparar para novas funcionalidades

- [x] T001 Verificar que testes existentes passam executando `python -m pytest tests/unit/presentation/ -v`
- [x] T002 Verificar imports e dependencias em `src/backlog_manager/presentation/views/roadmap_dialog.py` — confirmar que `Qt.CursorShape` esta disponivel para OpenHandCursor/ClosedHandCursor

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Adicionar constantes e infraestrutura de pan necessarias para US5b

**⚠️ CRITICAL**: US5b depende destas constantes e estado base

- [x] T003 Adicionar constantes de pan (`PAN_CLICK_THRESHOLD = 5.0`, `PAN_VISIBLE_RATIO = 0.2`, `KEYBOARD_PAN_RATIO = 0.10`) na secao de constantes em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T004 Adicionar atributos de estado de pan (`_is_panning: bool`, `_pan_start_x: float | None`, `_pan_start_xlim: tuple[float, float] | None`) no `__init__` de `RoadmapDialog` em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: Constantes e estado de pan declarados — implementacao de handlers pode comecar

---

## Phase 3: User Story 5b - Pan/Navegacao por Arrasto no Grafico (Priority: P2) 🎯 MVP

**Goal**: Permitir click+drag horizontal no grafico matplotlib com cursores visuais de mao e navegacao por teclas de seta

**Independent Test**: Aplicar zoom > 100%, click+arrastar no grafico, verificar que viewport desloca horizontalmente. Teclas de seta esquerda/direita tambem deslocam.

### Tests for User Story 5b

> **NOTE: Escrever estes testes PRIMEIRO, garantir que FALHAM antes da implementacao**

- [x] T005 [P] [US5b] Teste unitario: estado inicial de pan (`_is_panning=False`, `_pan_start_x=None`, `_pan_start_xlim=None`) em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T006 [P] [US5b] Teste unitario: `_on_pan_press` registra posicao inicial e seta `_is_panning=True` em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T007 [P] [US5b] Teste unitario: `_on_pan_move` atualiza xlim com delta horizontal quando `_is_panning=True` em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T008 [P] [US5b] Teste unitario: `_on_pan_release` seta `_is_panning=False` e distingue click vs drag pelo threshold de 5px em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T009 [P] [US5b] Teste unitario: pan clampa xlim para manter pelo menos 20% do range visivel (PAN_VISIBLE_RATIO) em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T010 [P] [US5b] Teste unitario: cursor muda para OpenHandCursor ao entrar no canvas e ClosedHandCursor durante drag em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T011 [P] [US5b] Teste unitario: navegacao via teclas de seta (Left/Right) desloca xlim em 10% da viewport em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T012 [P] [US5b] Teste unitario: teclas de seta sem efeito quando zoom = 100% em `tests/unit/presentation/views/test_roadmap_dialog.py`
- [x] T013 [P] [US5b] Teste unitario: tooltips suprimidos durante `_is_panning=True` em `tests/unit/presentation/views/test_roadmap_dialog.py`

### Implementation for User Story 5b

- [x] T014 [US5b] Implementar cursor OpenHandCursor como cursor padrao do canvas (`_canvas.setCursor()`) e troca para ClosedHandCursor durante drag em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T015 [US5b] Implementar handler `_on_pan_press(event)` — registra `_pan_start_x`, `_pan_start_xlim`, seta `_is_panning=True`, troca cursor para ClosedHandCursor. Condicoes: botao esquerdo, sem Ctrl, xdata valido, sobre axes em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T016 [US5b] Implementar handler `_on_pan_move(event)` — calcula dx entre posicao atual e `_pan_start_x`, aplica `ax.set_xlim(start_xlim - dx)` com clamping via PAN_VISIBLE_RATIO, chama `canvas.draw_idle()` em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T017 [US5b] Implementar handler `_on_pan_release(event)` — seta `_is_panning=False`, troca cursor para OpenHandCursor, distingue click vs drag (threshold < PAN_CLICK_THRESHOLD → delega para click handler existente) em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T018 [US5b] Conectar handlers de pan aos eventos matplotlib (`button_press_event`, `button_release_event`, `motion_notify_event`) integrando com handlers existentes (toggle grupo, tooltip) em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T019 [US5b] Suprimir tooltips durante `_is_panning=True` no handler de `motion_notify_event` existente em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T020 [US5b] Implementar helper `_clamp_xlim(new_left, new_right)` que garante pelo menos PAN_VISIBLE_RATIO (20%) do range total de dados permaneca visivel em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T021 [US5b] Implementar navegacao por teclas de seta — estender `keyPressEvent` para `Key_Left`/`Key_Right` deslocando xlim em KEYBOARD_PAN_RATIO (10%) da viewport, com mesmo clamping do pan em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [x] T022 [US5b] Garantir que `_on_fit_view` e `_on_fit_content` resetam posicao de pan (ja implicito via set_xlim — verificar e documentar) em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: Pan horizontal via click+drag, cursores visuais, navegacao por teclado e reset de pan funcionais e testados

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final, testes de integracao e qualidade

- [x] T023 Executar todos os testes com coverage: `python -m pytest tests/unit/presentation/ --cov=src/backlog_manager/presentation --cov-report=term-missing` — meta: viewmodels 90%+, views 50%+
- [x] T024 Verificar que pan nao interfere com zoom via Ctrl+Scroll no handler existente de `_on_scroll` em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [ ] T025 Executar validacao visual conforme `specs/043-roadmap-ux-refactor/quickstart.md` secao "Verificacao Visual"
- [x] T026 Executar `isort` e formatacao nos arquivos modificados

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA user stories
- **US5b (Phase 3)**: Depende de Foundational (Phase 2) — unica user story com trabalho pendente
- **Polish (Phase 4)**: Depende de US5b completa

### User Story Dependencies

- **US1 (Toolbar)**: ✅ Ja implementada — sem tarefas pendentes
- **US2 (Agrupamento Feature)**: ✅ Ja implementada — sem tarefas pendentes
- **US3 (Codigo nas Barras)**: ✅ Ja implementada — sem tarefas pendentes
- **US4 (Metricas Laterais)**: ✅ Ja implementada — sem tarefas pendentes
- **US5 (Zoom)**: ✅ Ja implementada — sem tarefas pendentes
- **US5b (Pan/Drag)**: ⏳ A implementar — Phase 3
- **US6 (Filtros)**: ✅ Ja implementada — sem tarefas pendentes
- **US7 (Dependencias)**: ✅ Ja implementada — sem tarefas pendentes

### Within US5b

- Testes (T005-T013) DEVEM ser escritos e FALHAR antes da implementacao
- Constantes/estado (T003-T004) antes de handlers
- Handlers de pan (T015-T017) antes de integracao (T018-T019)
- Clamping (T020) antes de navegacao por teclado (T021)
- Verificacao de reset (T022) ao final

### Parallel Opportunities

- Todos os testes T005-T013 podem rodar em paralelo (mesmo arquivo, secoes independentes)
- T003 e T004 podem rodar em paralelo (secoes distintas do mesmo arquivo)
- T014 (cursor) pode rodar em paralelo com T015-T017 (handlers)

---

## Parallel Example: User Story 5b

```bash
# Testes (rodar em paralelo — escrever primeiro):
Task T005: "Teste estado inicial de pan"
Task T006: "Teste _on_pan_press"
Task T007: "Teste _on_pan_move"
Task T008: "Teste _on_pan_release + click vs drag"
Task T009: "Teste clamping de pan"
Task T010: "Teste cursor OpenHand/ClosedHand"
Task T011: "Teste navegacao teclas de seta"
Task T012: "Teste seta sem efeito em zoom 100%"
Task T013: "Teste tooltip suprimido durante pan"

# Apos testes falharem, implementar (sequencial com paralelismo marcado):
Task T014: "Cursor padrao OpenHand"
Task T015-T017: "Handlers de pan (press/move/release)" (sequencial)
Task T018-T019: "Integracao com eventos existentes"
Task T020: "Clamping helper"
Task T021: "Navegacao teclado"
Task T022: "Verificar reset de pan"
```

---

## Implementation Strategy

### MVP First (US5b Only)

1. Complete Phase 1: Setup (validar existente)
2. Complete Phase 2: Foundational (constantes + estado)
3. Complete Phase 3: US5b (testes → implementacao → integracao)
4. **STOP and VALIDATE**: Testar pan/drag independentemente
5. Complete Phase 4: Polish

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. Testes T005-T013 → Red phase (todos falham)
3. Implementar T014-T022 → Green phase (todos passam)
4. Polish T023-T026 → Coverage e formatacao

---

## Notes

- [P] tasks = arquivos/secoes diferentes, sem dependencias
- [US5b] = unica user story com trabalho pendente nesta iteracao
- US1-US7 (exceto US5b) ja implementadas conforme research R13
- Pan e puramente estado visual do View — nao afeta ViewModel
- Distinguir click de drag por threshold (5px) e critico para nao quebrar toggle de grupos
- Commit apos cada tarefa ou grupo logico
