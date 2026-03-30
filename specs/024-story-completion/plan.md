# Implementation Plan: Story Completion Status

**Branch**: `024-story-completion` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/024-story-completion/spec.md`

## Summary

Implementar validação de dependências ao marcar história como "Concluído" e excluir histórias concluídas do cálculo de cronograma e alocação de desenvolvedores. A abordagem técnica envolve: (1) nova exceção de domínio para dependências incompletas, (2) validação no EditStoryUseCase antes de transição para CONCLUIDO, (3) filtro de status no CalculateScheduleUseCase e AllocationService, (4) feedback claro na UI listando dependências bloqueadoras.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite
**Storage**: SQLite (sem alteração de schema — usa status VARCHAR(20) existente)
**Testing**: pytest + pytest-qt + pytest-cov
**Target Platform**: Windows desktop (PySide6)
**Project Type**: desktop-app
**Performance Goals**: N/A (operações unitárias, sem requisitos de throughput)
**Constraints**: Validação deve ser síncrona no domínio; I/O via async em Application/Infrastructure
**Scale/Scope**: ~5 entidades, ~10 use cases existentes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Validação de dependências fica no Domain (exceção) + Application (use case orquestra I/O). UI só exibe resultado. |
| II. DDD | ✅ PASS | Nova exceção de domínio `IncompleteDependencyException` herda de `DependencyException`. Regra de negócio validada no use case com dados do repositório. |
| III. Repository Pattern | ✅ PASS | Usa `StoryDependencyRepository.get_dependencies()` e `StoryRepository.get_by_id()` existentes via UnitOfWork. |
| IV. Dependency Injection | ✅ PASS | Use case recebe UoW via construtor (padrão existente). |
| V. SQLite | ✅ PASS | Sem alteração de schema. Usa status VARCHAR(20) existente com valor "CONCLUIDO". |
| VIII. Async | ✅ PASS | Validação de dependências é async no use case (busca dependências e status via repositório). Domain permanece síncrono. |
| IX. Simplicidade | ✅ PASS | Validação direta: busca dependências → verifica status → rejeita ou permite. Sem over-engineering. |
| XIV. Testes | ✅ PASS | Testes unitários para exceção, use case (mock repo), domain service. Testes de integração para fluxo completo. |
| XV. Idioma | ✅ PASS | Código em inglês, mensagens de erro em português, docs em português. |
| XVI. Tratamento de Erros | ✅ PASS | Nova exceção `IncompleteDependencyException` herda de `DependencyException` → `BacklogManagerException`. Mensagem lista dependências incompletas. |

**Gate Result**: ✅ ALL PASS — Nenhuma violação detectada.

## Project Structure

### Documentation (this feature)

```text
specs/024-story-completion/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── domain/
│   ├── exceptions/
│   │   └── dependency.py              # + IncompleteDependencyException
│   └── value_objects/
│       └── story_status.py            # (sem alteração — CONCLUIDO já existe)
├── application/
│   ├── use_cases/
│   │   └── story/
│   │       └── edit_story.py          # + validação de dependências ao transicionar para CONCLUIDO
│   └── dto/
│       └── story/
│           └── edit_story_dto.py      # (fix: status validator com valores corretos)
├── infrastructure/                    # (sem alteração)
└── presentation/
    └── viewmodels/
        └── main_window_viewmodel.py   # + tratamento de IncompleteDependencyException → mensagem na UI

tests/
├── unit/
│   ├── domain/
│   │   └── exceptions/
│   │       └── test_incomplete_dependency.py
│   └── application/
│       └── use_cases/
│           └── story/
│               └── test_edit_story_completion.py
└── integration/
    └── test_story_completion_flow.py
```

**Structure Decision**: Segue estrutura existente do projeto. Mudanças concentradas em 3-4 arquivos existentes + 1 nova exceção de domínio.

## Complexity Tracking

> Nenhuma violação de constituição — seção não aplicável.
