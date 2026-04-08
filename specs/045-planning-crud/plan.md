# Implementation Plan: Modulo de Planejamentos (CRUD Completo)

**Branch**: `045-planning-crud` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/045-planning-crud/spec.md`

## Summary

Adicionar um modulo completo de Planejamentos ao Backlog Manager, permitindo ao usuario criar, listar, abrir, renomear e excluir planejamentos nomeados. Cada planejamento agrupa um conjunto independente de historias. A abordagem tecnica envolve: (1) nova entidade de dominio `Planning` com tabela SQLite dedicada, (2) adicao de `planning_id` como FK composta na tabela `Story`, (3) migracao automatica de dados existentes no startup, (4) novos use cases CRUD + scoping de queries por planning_id, (5) dialogo "Abrir Planejamento" com acoes inline de editar/excluir, (6) renomeacao de "Novo Planejamento" para "Reiniciar Planejamento".

## Technical Context

**Language/Version**: Python 3.11+ (runtime), Python 3.13 (dev/CI)
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite
**Storage**: SQLite (adicao de tabela Planning + migracao de Story com planning_id)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, pytest-qt
**Target Platform**: Desktop Windows (com suporte Linux via paths portaveis)
**Project Type**: desktop-app (PySide6 GUI)
**Performance Goals**: Troca de planejamento instantanea (<100ms) para ate 500 historias (SC-004)
**Constraints**: Migracao automatica de dados existentes sem perda (FR-015), auto-save em todas operacoes (FR-017)
**Scale/Scope**: Ate 50 planejamentos simultaneos (SC-003), ate 500 historias por planejamento (SC-004)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Nova entidade Planning em Domain, use cases em Application, repositorio em Infrastructure, views/viewmodels em Presentation |
| II. DDD | ✅ PASS | Planning como entidade rica com validacoes no construtor (nome obrigatorio, unicidade) |
| III. Repository Pattern | ✅ PASS | PlanningRepository Protocol em Domain, SQLitePlanningRepository em Infrastructure |
| IV. Dependency Injection | ✅ PASS | Novos use cases e viewmodels registrados no DIContainer |
| V. SQLite | ✅ PASS | Nova tabela Planning, migracao automatica via init_database |
| VI. Packaging | ✅ PASS | Sem novas dependencias externas |
| VII. Estrutura Diretorios | ✅ PASS | Segue src layout existente |
| VIII. Async | ✅ PASS | Repositorios e use cases async; Domain sincrono |
| IX. Simplicidade | ✅ PASS | Reutiliza padroes existentes (UoW, DIContainer, MVVM) |
| X. Type Hints | ✅ PASS | Type hints em todas assinaturas |
| XI. Docstrings | ✅ PASS | Docstrings em classes/metodos publicos |
| XII. isort | ✅ PASS | Imports organizados |
| XIII. Nomenclatura | ✅ PASS | PascalCase classes, snake_case funcoes |
| XIV. Testes | ✅ PASS | Unit + integration tests para todas camadas |
| XV. Idioma | ✅ PASS | Codigo em ingles, docs em portugues, mensagens em portugues |
| XVI. Tratamento Erros | ✅ PASS | PlanningException para erros de dominio especificos |
| XVII. Logging | ✅ PASS | Logs em operacoes criticas (criacao, exclusao, migracao) |
| XVIII. Gestao Config | ✅ PASS | QSettings para last_active_planning_id |
| XIX. UI/UX MVVM | ✅ PASS | PlanningDialogViewModel + OpenPlanningDialog |
| XX. Validacao | ✅ PASS | Sanitizacao de nome na ViewModel, validacao no dominio |
| XXI. CI/CD | ✅ PASS | Testes cobrem novas funcionalidades |

## Project Structure

### Documentation (this feature)

```text
specs/045-planning-crud/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── domain/
│   ├── entities/
│   │   ├── planning.py              # NOVO - entidade Planning
│   │   └── story.py                 # MODIFICADO - adiciona planning_id
│   ├── exceptions/
│   │   └── planning_exceptions.py   # NOVO - DuplicatePlanningNameException, ActivePlanningDeletionException
│   └── interfaces/
│       └── repositories.py          # MODIFICADO - adiciona PlanningRepository Protocol
├── application/
│   ├── dto/
│   │   └── planning/
│   │       └── planning_dto.py      # NOVO - DTOs de entrada/saida para Planning
│   └── use_cases/
│       └── planning/
│           ├── create_planning.py           # NOVO
│           ├── list_plannings.py            # NOVO
│           ├── update_planning.py           # NOVO
│           ├── delete_planning.py           # NOVO
│           ├── get_active_planning.py       # NOVO
│           ├── set_active_planning.py       # NOVO
│           ├── migrate_orphan_stories.py    # NOVO
│           ├── reset_planning.py            # EXISTENTE - scoped por planning_id
│           └── count_affected_stories.py    # EXISTENTE - scoped por planning_id
├── infrastructure/
│   └── database/
│       ├── schema.sql               # MODIFICADO - adiciona Planning table, altera Story
│       ├── sqlite_connection.py     # MODIFICADO - adiciona logica de migracao
│       ├── unit_of_work.py          # MODIFICADO - adiciona plannings repository
│       └── repositories/
│           ├── planning_repository.py  # NOVO
│           └── story_repository.py     # MODIFICADO - queries scoped por planning_id
└── presentation/
    ├── viewmodels/
    │   ├── planning_viewmodel.py          # NOVO - CRUD de planejamentos
    │   ├── main_window_viewmodel.py       # MODIFICADO - active planning state
    │   └── reset_planning_viewmodel.py    # EXISTENTE - minor scope adjustment
    └── views/
        ├── open_planning_dialog.py        # NOVO - dialogo "Abrir Planejamento"
        ├── create_planning_dialog.py      # NOVO - dialogo "Novo Planejamento"
        └── main_window.py                 # MODIFICADO - menus, titulo, bootstrap

tests/
├── unit/
│   ├── domain/
│   │   └── test_planning.py               # NOVO
│   └── application/
│       └── test_planning_use_cases.py     # NOVO
└── integration/
    └── infrastructure/
        └── test_planning_repository.py    # NOVO
```

**Structure Decision**: Segue o src layout existente (Constitution VII). Novos arquivos criados nos modulos existentes de cada camada, reutilizando os padroes de Story/Feature como referencia.

## Complexity Tracking

> Sem violacoes de constituicao identificadas. A feature adiciona uma nova entidade seguindo exatamente os mesmos padroes ja estabelecidos (Planning segue o modelo de Feature/Story).
