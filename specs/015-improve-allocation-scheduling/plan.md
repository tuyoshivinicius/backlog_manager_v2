# Implementation Plan: Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma

**Branch**: `015-improve-allocation-scheduling` | **Date**: 2026-03-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/015-improve-allocation-scheduling/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Esta feature implementa infraestrutura de diagnostico para ciclos de melhoria iterativa dos algoritmos de alocacao e cronograma. O foco principal e adicionar logging estruturado em pontos criticos do `AllocationService`, permitindo que o usuario e Claude Code colaborem para identificar e corrigir problemas de alocacao atraves de um protocolo de 6 etapas (Observar, Descrever, Analisar logs, Diagnosticar, Propor correcao, Validar).

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0, PySide6 ^6.10.0, qasync ^0.27.1
**Storage**: SQLite (via aiosqlite)
**Testing**: pytest ^8.0 com pytest-asyncio ^0.23, pytest-cov ^4.0
**Target Platform**: Windows Desktop (compativel com Linux)
**Project Type**: desktop-app (PySide6 GUI)
**Performance Goals**: Alocacao <= 5s para 100 historias, <= 30s para 500 historias (SC-002, SC-003, SC-009)
**Constraints**: Cobertura >= 80% (SC-006), complexidade ciclomatica <= 15 (SC-007)
**Scale/Scope**: ~190 historias de teste (seed script EP-014), 7 desenvolvedores

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | PASS | Logging sera adicionado na camada Domain (AllocationService) conforme arquitetura existente |
| II. Domain-Driven Design | PASS | AllocationMetrics ja existe como estrutura de dominio; logging e comportamento observavel |
| VIII. Programacao Assincrona | PASS | AllocationService e sincrono (dominio); logging sera sincrono |
| IX. Simplicidade e Legibilidade | PASS | Adicionar logs em pontos criticos, sem complexidade adicional |
| XIV. Estrategia de Testes | PASS | Testes de integracao cobrirao logging; cobertura >= 80% |
| XV. Idioma | PASS | Logs em portugues conforme constituicao |
| XVII. Logging e Observabilidade | PASS | Conformidade total - arquivo texto, rotacao 10MB, 3 backups, ISO 8601 |
| XXI. CI/CD e Qualidade Continua | PASS | radon validara complexidade ciclomatica <= 15 |

## Project Structure

### Documentation (this feature)

```text
specs/015-improve-allocation-scheduling/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── domain/
│   ├── entities/              # Story, Developer, Feature (existentes)
│   ├── services/
│   │   └── allocation_service.py  # MODIFICAR: adicionar logging estruturado
│   └── exceptions/
│       └── warnings.py        # DeadlockWarning, IdlenessWarning (existentes)
├── infrastructure/
│   └── logging/
│       └── logger_config.py   # Configuracao existente (10MB, 3 backups)
└── application/
    └── use_cases/
        └── allocation/
            └── execute_allocation.py  # PODE MODIFICAR: logar resultado final

tests/
├── unit/
│   └── domain/
│       └── services/
│           └── test_allocation_logging.py  # NOVO: testes de logging
└── integration/
    └── infrastructure/
        └── test_allocation_integration.py  # PODE MODIFICAR: verificar logs
```

**Structure Decision**: Single project existente (Clean Architecture). Modificacoes serao isoladas em `allocation_service.py` com adicao de testes em `tests/unit/domain/services/test_allocation_logging.py`.

## Complexity Tracking

> **Nenhuma violacao identificada** - Esta feature adiciona apenas logging em pontos criticos sem introduzir nova complexidade arquitetural.
