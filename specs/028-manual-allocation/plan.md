# Implementation Plan: Alocacao Manual de Desenvolvedores

**Branch**: `028-manual-allocation` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/028-manual-allocation/spec.md`

## Summary

Implementar dialog de alocacao manual de desenvolvedores, acionada por double-click na coluna "Desenvolvedor" da tabela de backlog. A dialog exibe desenvolvedores classificados em livres/ocupados, com recomendacao automatica do algoritmo e date picker para alterar data de inicio com recalculo dinamico de disponibilidade. Reutiliza AllocationService e SchedulingService existentes sem modifica-los.

## Technical Context

**Language/Version**: Python 3.11+ (PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0)
**Primary Dependencies**: PySide6 (QDialog, QTreeWidget, QDateEdit), Pydantic (DTOs), aiosqlite (repositorios)
**Storage**: SQLite (sem alteracao de schema — usa colunas existentes developer_id, start_date, end_date)
**Testing**: pytest + pytest-qt + qasync
**Target Platform**: Windows (desktop app)
**Project Type**: desktop-app
**Performance Goals**: Dialog carrega lista de devs em < 200ms; recalculo de disponibilidade ao alterar data em < 100ms
**Constraints**: Nao modificar servicos de dominio existentes (FR-010/SC-005)
**Scale/Scope**: ~10 desenvolvedores, ~200 historias

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Nota |
|-----------|--------|------|
| I. Clean Architecture | ✅ PASS | Camadas respeitadas: DTO (Application), UseCase (Application), ViewModel (Presentation), Dialog (Presentation), Domain (reutilizado sem modificacao) |
| II. DDD | ✅ PASS | Reutiliza entidades Story/Developer e domain services existentes; nenhuma entidade anemizada |
| III. Repository Pattern | ✅ PASS | Acesso via UnitOfWork existente, repositorios retornam entidades |
| IV. Dependency Injection | ✅ PASS | Dialog recebe container via construtor; ViewModel registrado no DIContainer |
| V. SQLite | ✅ PASS | Sem alteracao de schema; usa colunas existentes |
| VI. Packaging | ✅ PASS | Novos modulos em src/backlog_manager/ |
| VII. Estrutura de Diretorios | ✅ PASS | DTOs em application/dto/, use case em application/use_cases/, view em presentation/views/, viewmodel em presentation/viewmodels/ |
| VIII. Async | ✅ PASS | Use case async; ViewModel usa asyncio.create_task(); Domain permanece sync |
| IX. Simplicidade | ✅ PASS | Reutiliza servicos existentes; dialog simples com QTreeWidget |
| X. Type Hints | ✅ PASS | Todas as assinaturas tipadas |
| XI. Docstrings | ✅ PASS | Classes e metodos publicos documentados |
| XII. Imports | ✅ PASS | Organizados com isort |
| XIII. Nomenclatura | ✅ PASS | PascalCase classes, snake_case metodos |
| XIV. Testes | ✅ PASS | Unit tests para UseCase e ViewModel; integration test para dialog |
| XV. Idioma | ✅ PASS | Codigo em ingles, docstrings/mensagens em portugues |
| XVI. Erros | ✅ PASS | ValueError para validacoes, mensagens em portugues |
| XVII. Logging | ✅ PASS | Logger em UseCase e ViewModel |

**Gate Result**: ✅ ALL PASS — Prosseguir para Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/028-manual-allocation/
├── plan.md                          # This file
├── spec.md                          # Feature specification
├── research.md                      # Phase 0 output
├── data-model.md                    # Phase 1 output
├── quickstart.md                    # Phase 1 output
├── contracts/
│   ├── manual-allocation-dialog.md  # UI contract
│   └── get-developer-availability-use-case.md  # Application contract
└── tasks.md                         # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── application/
│   ├── dto/
│   │   └── allocation/
│   │       ├── developer_availability_dto.py   # NEW: DeveloperAvailabilityDTO, BlockingStoryDTO
│   │       └── get_developer_availability_dto.py # NEW: Input/Output DTOs
│   └── use_cases/
│       └── allocation/
│           └── get_developer_availability.py   # NEW: GetDeveloperAvailabilityUseCase
├── domain/
│   └── services/
│       ├── allocation_service.py               # UNCHANGED (reutilizado)
│       └── scheduling_service.py               # UNCHANGED (reutilizado)
├── presentation/
│   ├── container.py                            # MODIFIED: registrar novo use case + viewmodel
│   ├── viewmodels/
│   │   └── manual_allocation_dialog_viewmodel.py # NEW: ViewModel da dialog
│   └── views/
│       ├── main_window.py                      # MODIFIED: handler double-click coluna Developer
│       └── manual_allocation_dialog.py         # NEW: Dialog de alocacao manual
└── ...

tests/
├── unit/
│   ├── application/
│   │   └── test_get_developer_availability.py  # NEW: testes do use case
│   └── presentation/
│       └── test_manual_allocation_dialog_viewmodel.py  # NEW: testes do viewmodel
└── ...
```

**Structure Decision**: Segue a estrutura existente do projeto — novos DTOs em `application/dto/allocation/`, novo use case em `application/use_cases/allocation/`, novos componentes de UI em `presentation/views/` e `presentation/viewmodels/`.

## Complexity Tracking

> Nenhuma violacao de Constitution Check — tabela nao aplicavel.

### Desvio Aceito: Acesso a metodos privados do AllocationService

O GetDeveloperAvailabilityUseCase acessa `AllocationService._has_period_overlap()` e `AllocationService._select_developer()` (metodos com prefixo `_`, convencionalmente privados). Este desvio do Principio XIII (Nomenclatura) e aceito porque:

- FR-010/SC-005 proibem modificar servicos de dominio existentes — tornar esses metodos publicos constituiria modificacao.
- Em Python, `_` e convencao (nao enforcement) — o acesso funciona sem hack.
- Os metodos sao `@staticmethod` stateless, sem efeitos colaterais.
- A alternativa (duplicar logica no use case) violaria DRY (Principio IX).

## Post-Design Constitution Re-check

| Principio | Status | Nota |
|-----------|--------|------|
| I. Clean Architecture | ✅ PASS | Fluxo: View → ViewModel → UseCase → Domain Services. Nenhuma camada cruzada indevidamente. |
| II. DDD | ✅ PASS | Reutiliza _has_period_overlap e _select_developer do AllocationService (static, stateless). Nenhuma logica de negocio na Presentation. |
| III. Repository Pattern | ✅ PASS | GetDeveloperAvailabilityUseCase usa UnitOfWork para acessar StoryRepository, DeveloperRepository, DependencyRepository. |
| IV. DI | ✅ PASS | ManualAllocationDialog recebe DIContainer; ViewModel lazy-loaded no container. |
| IX. Simplicidade | ✅ PASS | 1 novo use case, 1 novo viewmodel, 1 nova dialog, ~3 novos DTOs. Complexidade minima. |
| X. Type Hints | ✅ PASS | Todos os contratos tipados nos DTOs Pydantic e assinaturas de metodos. |
| XIV. Testes | ✅ PASS | Unit tests para use case (mock repos) e viewmodel (mock container). |

**Post-Design Gate**: ✅ ALL PASS.
