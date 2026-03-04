# Implementation Plan: Corrigir Bugs de Inicialização

**Branch**: `011-fix-startup-bugs` | **Date**: 2026-03-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-fix-startup-bugs/spec.md`

## Summary

Corrigir dois bugs críticos que impedem o funcionamento da aplicação:
1. **Inicialização do banco de dados**: Adicionar chamada a `init_database()` em `app.py` antes de `DIContainer.initialize()` para garantir que as tabelas existam
2. **Conflitos de event loop asyncio/qasync**: Usar `QTimer.singleShot(0, ...)` para agendar tasks assíncronas para o próximo ciclo do event loop, evitando conflitos com diálogos modais

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, aiosqlite ^0.19.0, pydantic ^2.0
**Storage**: SQLite via aiosqlite (arquivo `backlog_manager.db`)
**Testing**: pytest ^8.0, pytest-qt ^4.4, pytest-asyncio ^0.23
**Target Platform**: Windows (desktop application)
**Project Type**: Desktop GUI application (PySide6 + MVVM)
**Performance Goals**: Latência ≤ 100ms para operações CRUD (RNF-PERF-002)
**Constraints**: Aplicação single-user, sem acesso concorrente ao banco
**Scale/Scope**: Aplicação local para gerenciamento de backlog

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Mudanças respeitam as camadas: `app.py` (Presentation), views (Presentation) |
| II. DDD | ✅ PASS | Sem mudanças no domínio |
| III. Repository Pattern | ✅ PASS | Sem mudanças em repositórios |
| IV. Dependency Injection | ✅ PASS | `init_database()` chamada antes de DIContainer |
| V. SQLite | ✅ PASS | Usa schema existente com IF NOT EXISTS |
| VIII. Asyncio | ✅ PASS | Mantém integração qasync, corrige uso de create_task |
| XIV. Testes | ✅ PASS | Testes existentes devem continuar passando |
| XIX. UI/UX (MVVM) | ✅ PASS | Views continuam usando ViewModels, apenas agendamento de tasks muda |

**Gate Result**: ✅ PASS - Todas as correções são consistentes com a constituição

## Project Structure

### Documentation (this feature)

```text
specs/011-fix-startup-bugs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files to modify)

```text
src/backlog_manager/
├── presentation/
│   ├── app.py                    # ADD: init_database() call
│   └── views/
│       ├── main_window.py        # FIX: QTimer.singleShot for create_task
│       ├── story_dialog.py       # FIX: QTimer.singleShot in __init__
│       ├── developer_dialog.py   # FIX: QTimer.singleShot in __init__
│       ├── feature_dialog.py     # FIX: QTimer.singleShot in __init__
│       └── dependency_panel.py   # FIX: QTimer.singleShot for create_task
└── infrastructure/
    └── database/
        └── sqlite_connection.py  # EXISTS: init_database() function (no changes)
```

**Structure Decision**: Modificações mínimas nos arquivos existentes da camada Presentation. Sem criação de novos arquivos.

## Complexity Tracking

> Nenhuma violação da constituição identificada. Correções são simples e diretas.

| Item | Justificativa |
|------|---------------|
| N/A | Sem complexidade adicional necessária |
