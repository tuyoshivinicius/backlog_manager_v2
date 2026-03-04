# Implementation Plan: EP-010 Testes de Integracao E2E

**Branch**: `010-ep010-integration-e2e-tests` | **Date**: 2026-03-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-ep010-integration-e2e-tests/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar suite completa de testes E2E que valide a integridade do sistema Backlog Manager como um todo, garantindo que todos os casos de uso (UC-001 a UC-005) e cenarios de teste (CT-001 a CT-005) funcionem corretamente quando todas as camadas estao integradas. Os testes usarao pytest-qt com qasync para validar fluxos GUI -> ViewModel -> UseCase -> Repository -> SQLite.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: pytest ^8.0, pytest-qt ^4.4, pytest-asyncio ^0.23, pytest-cov ^4.0, pytest-rerunfailures ^13.0, qasync ^0.27.1, PySide6 ^6.10.0
**Storage**: SQLite (via aiosqlite ^0.19.0)
**Testing**: pytest com pytest-qt, pytest-asyncio, pytest-cov
**Target Platform**: Windows desktop (PySide6 GUI), CI/CD Linux (GitHub Actions com xvfb)
**Project Type**: Desktop application (library-first com GUI PySide6)
**Performance Goals**: Alocacao 100 historias <= 5s (RNF-PERF-001), CRUD latencia <= 100ms (RNF-PERF-002), Suite E2E < 5 minutos
**Constraints**: Cobertura >= 80%, timeout 30s/teste E2E, sem time.sleep() em testes
**Scale/Scope**: ~70 arquivos de teste existentes, +15 arquivos E2E novos, 10+ views, 7 user stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Gate Check

| # | Principio | Requisito Relevante | Status | Notas |
|---|-----------|---------------------|--------|-------|
| XIV | Estrategia de Testes | Cobertura >= 80%, testes E2E com pytest-qt + qasync | ✅ ALINHADO | Epico implementa diretamente este principio |
| XIV | Testes GUI com qasync | DEVEM rodar sobre loop qasync, sem time.sleep() | ✅ ALINHADO | ADR-002 e ADR-011 enderecam este requisito |
| XIV | Cobertura por modulo | domain 100%, application 100%, infra 80%, views 50%+ | ✅ ALINHADO | FR-092 especifica mesmas metas |
| VII | Estrutura de Diretorios | Testes DEVEM estar em tests/ na raiz | ✅ ALINHADO | tests/e2e/ segue padrao existente |
| XXI | CI/CD | pytest-cov com fail_under=80, Gates de qualidade | ✅ ALINHADO | FR-080 a FR-084 implementam CI/CD |
| VIII | Async | Application e Infrastructure async, Domain sincrono | ✅ ALINHADO | Testes respeitam arquitetura async |
| XVI | Tratamento de Erros | Erros NAO DEVEM crashar aplicacao | ✅ ALINHADO | Edge cases tratam timeout e falhas |
| XIX | Padroes UI/UX | Views NAO DEVEM importar de domain/infrastructure | ✅ N/A | Testes validam, nao modificam views |

**Gate Status**: ✅ PASS - Nenhuma violacao identificada. Epico alinha-se completamente com Constitution.

### Post-Design Gate Check

| # | Principio | Artefato de Design | Status | Verificacao |
|---|-----------|-------------------|--------|-------------|
| XIV | pytest-qt + qasync | research.md, data-model.md | ✅ VALIDADO | Fixture qasync_loop documentada corretamente |
| XIV | Sem time.sleep() | research.md Secao 3 | ✅ VALIDADO | Padroes qtbot.waitSignal/waitUntil documentados |
| XIV | Cobertura diferenciada | data-model.md Secao 4 | ✅ VALIDADO | Marcadores e2e, perf, slow definidos |
| VII | tests/e2e/ | plan.md Project Structure | ✅ VALIDADO | Segue padrao Constitution VII |
| XXI | CI/CD config | research.md Secao 5 | ✅ VALIDADO | Workflow GitHub Actions com xvfb |
| VIII | Fixtures async | data-model.md Secao 1 | ✅ VALIDADO | Fixtures respeitam arquitetura async |
| IX | Factory functions | data-model.md Secao 2 | ✅ VALIDADO | Implementacao simples e reutilizavel |

**Post-Design Gate Status**: ✅ PASS - Design validado contra Constitution. Pronto para Phase 2 (tasks).

## Project Structure

### Documentation (this feature)

```text
specs/010-ep010-integration-e2e-tests/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command) - N/A para testes
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/           # Codigo sendo testado (existente)
├── domain/                    # Entidades, services, exceptions
├── application/               # Use cases, DTOs
├── infrastructure/            # Repositories, Excel service
└── presentation/              # Views, ViewModels, Container

tests/
├── conftest.py                # Fixtures globais (existente)
├── unit/                      # Testes unitarios (existente, ~40 arquivos)
├── integration/               # Testes de integracao (existente, ~25 arquivos)
└── e2e/                       # NOVO - Testes E2E (EP-010)
    ├── __init__.py
    ├── conftest.py            # Fixtures E2E (qasync_loop, e2e_app, e2e_main_window)
    ├── factories.py           # Factory functions para dados de teste
    ├── test_uc001_criar_priorizar_backlog.py
    ├── test_uc002_alocacao_automatica.py
    ├── test_uc003_detectar_resolver_deadlock.py
    ├── test_uc004_importar_excel.py
    ├── test_uc005_gerenciar_ondas.py
    ├── test_ct001_backlog_completo.py
    ├── test_ct002_ciclo_grafo_grande.py
    ├── test_ct003_deadlock_devs.py
    ├── test_ct004_feriados_sequencia.py
    ├── test_ct005_balanceamento.py
    ├── test_performance.py
    └── test_excel_roundtrip.py

.github/workflows/             # NOVO - CI/CD
└── tests.yml                  # Workflow para testes com xvfb
```

**Structure Decision**: Criar novo diretorio `tests/e2e/` para testes E2E separados de unit e integration (ADR-001). Estrutura segue padrao Constitution VII e organizacao existente do projeto.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*Nenhuma violacao identificada - tabela vazia.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |
