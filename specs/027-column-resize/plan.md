# Implementation Plan: Column Resize

**Branch**: `027-column-resize` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/027-column-resize/spec.md`

## Summary

Permitir redimensionamento interativo de colunas da tabela do backlog via drag na borda dos cabeçalhos, com persistência automática de larguras via QSettings, auto-fit por duplo-clique e restauração para padrão via menu de contexto. Feature puramente Presentation layer — troca `ResizeMode.Fixed` por `Interactive`, usa `saveState()`/`restoreState()` do QHeaderView para persistência.

## Technical Context

**Language/Version**: Python 3.11+ + PySide6 ^6.10.0
**Primary Dependencies**: PySide6 (QTableView, QHeaderView, QSettings), qasync ^0.27.1
**Storage**: QSettings (INI format) — sem alterações SQLite
**Testing**: pytest + pytest-qt
**Target Platform**: Desktop (Windows 11, Linux)
**Project Type**: desktop-app
**Performance Goals**: Redimensionamento responsivo (< 100ms), save/restore < 1s
**Constraints**: Largura mínima 30px por coluna, coluna "Nome" sempre Stretch
**Scale/Scope**: 13 colunas na tabela, 1 grupo QSettings adicional

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Feature 100% Presentation layer. Não toca Domain, Application ou Infrastructure. |
| II. DDD | ✅ N/A | Sem entidades de domínio envolvidas. |
| III. Repository Pattern | ✅ N/A | Usa QSettings (UI preferences), não repositórios de domínio. |
| IV. Dependency Injection | ✅ PASS | QSettings instanciado localmente na View (padrão existente em ConfigDialogViewModel). |
| V. SQLite | ✅ N/A | Sem alterações de banco de dados. |
| VIII. Async | ✅ N/A | Operações QSettings são síncronas e instantâneas. Não requerem async. |
| IX. Simplicidade | ✅ PASS | Usa APIs nativas do Qt (`saveState`/`restoreState`), sem abstrações extras. |
| X. Type Hints | ✅ PASS | Será aplicado em todo código novo. |
| XI. Docstrings | ✅ PASS | Métodos públicos terão docstrings Google style. |
| XIV. Testes | ✅ PASS | Testes com pytest-qt para lógica de resize e persistência. |
| XV. Idioma | ✅ PASS | Código em inglês, docs em português. |
| XIX. UI/UX MVVM | ⚠️ NOTA | Lógica de save/restore é simples o suficiente para ficar na View (QSettings é mecanismo de UI). Não justifica ViewModel separado — consistente com padrão existente no ConfigDialogViewModel. |

**Gate Result**: ✅ PASS — Nenhuma violação.

## Project Structure

### Documentation (this feature)

```text
specs/027-column-resize/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ui-interactions.md
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/
└── presentation/
    ├── views/
    │   └── main_window.py          # Modificar: resize modes, save/restore, context menu
    └── viewmodels/
        └── story_table_model.py    # Modificar: adicionar MINIMUM_COLUMN_WIDTH

tests/
└── unit/
    └── presentation/
        └── test_column_resize.py   # Criar: testes de redimensionamento
```

**Structure Decision**: Segue estrutura existente. Sem novos módulos ou camadas — apenas modificação de 2 arquivos existentes e criação de 1 arquivo de testes.
