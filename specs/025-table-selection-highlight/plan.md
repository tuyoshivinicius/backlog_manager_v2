# Implementation Plan: Table Selection Highlight

**Branch**: `025-table-selection-highlight` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/025-table-selection-highlight/spec.md`

## Summary

Implementar destaque visual persistente para a linha selecionada na tabela de backlog, garantindo que a seleção acompanhe a história durante operações de reordenação (move up/down) e forneça feedback claro para ações de edição/exclusão. A abordagem técnica utiliza QSS (Qt Style Sheets) com tokens do design system existente para estilizar o estado `::item:selected` da `QTableView`, além de restauração programática da seleção após refresh do modelo.

## Technical Context

**Language/Version**: Python 3.11+ + PySide6 ^6.10.0
**Primary Dependencies**: PySide6 (QTableView, QItemSelectionModel), qasync ^0.27.1, Pydantic ^2.0
**Storage**: N/A (escopo puramente Presentation — sem alterações de schema ou persistência)
**Testing**: pytest + pytest-qt (testes unitários e integração de GUI)
**Target Platform**: Windows 11 (desktop), resolução mínima 1366x768
**Project Type**: desktop-app (PySide6/MVVM)
**Performance Goals**: Latência de resposta ≤ 100ms para operações CRUD; seleção sem flicker
**Constraints**: Contraste WCAG AA (4.5:1 mínimo) para cores de seleção vs texto
**Scale/Scope**: Tabela com até ~500 histórias; operação single-selection

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Alterações apenas em Presentation layer (views, viewmodels, theme) |
| II. DDD | ✅ PASS | Nenhuma alteração no domínio |
| III. Repository Pattern | ✅ PASS | Nenhum repositório novo ou alterado |
| IV. Dependency Injection | ✅ PASS | Nenhuma nova dependência a injetar |
| V. SQLite | ✅ PASS | Nenhuma alteração de banco de dados |
| VII. Estrutura de Diretórios | ✅ PASS | Arquivos em presentation/ e tests/ conforme padrão |
| VIII. Async | ✅ PASS | Move up/down já são async; restauração de seleção é síncrona pós-refresh |
| IX. Simplicidade | ✅ PASS | QSS para estilo visual (abordagem mais simples); restauração via `setCurrentIndex` |
| X. Type Hints | ✅ PASS | Todos os métodos novos terão type hints |
| XI. Docstrings | ✅ PASS | Métodos públicos terão docstrings Google style |
| XIV. Testes | ✅ PASS | Testes unitários para lógica de restauração; testes de integração para visual |
| XIX. UI/UX (MVVM) | ✅ PASS | Lógica de seleção no ViewModel; View apenas renderiza |
| XXI. CI/CD | ✅ PASS | Black, isort, mypy conformes |

**Gate Result**: ✅ ALL PASS — nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/025-table-selection-highlight/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/presentation/
├── theme/
│   └── theme.py                    # MODIFIED: adicionar tokens de seleção (selection-bg, selection-fg)
├── viewmodels/
│   ├── main_window_viewmodel.py    # MODIFIED: restauração de seleção após move/delete/refresh
│   └── story_table_model.py        # MODIFIED: role para highlight de seleção (se necessário)
├── views/
│   └── main_window.py              # MODIFIED: QSS de seleção, restauração programática de seleção
└── delegates/
    └── status_badge_delegate.py    # MODIFIED: respeitar estado de seleção na pintura do badge

tests/
├── unit/presentation/viewmodels/
│   └── test_main_window_viewmodel.py  # MODIFIED: testes de restauração de seleção
└── integration/presentation/views/
    └── test_main_window.py            # MODIFIED: testes de seleção visual e persistência
```

**Structure Decision**: Apenas modificação de arquivos existentes na camada `presentation/`. Nenhum arquivo novo de produção necessário (exceto se tokens de seleção justificarem constante dedicada). Testes em unit/ e integration/ conforme padrão existente.

## Complexity Tracking

> Nenhuma violação — tabela não aplicável.
