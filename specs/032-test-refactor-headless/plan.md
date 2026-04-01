# Implementation Plan: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Branch**: `032-test-refactor-headless` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/032-test-refactor-headless/spec.md`

## Summary

Refatorar a suite de testes para eliminar todas as dependencias graficas (PySide6, pytest-qt, qasync), permitindo execucao 100% headless no CI. A abordagem envolve: (1) corrigir medicao de cobertura para incluir todas as 4 camadas, (2) remover 22 testes E2E graficos, (3) triar e reescrever/remover 33 testes de presentation (16 integracao + 17 unitarios), (4) ampliar cobertura para >= 90% com novos testes headless, (5) atualizar CI para executar suite completa sem `--ignore`. ViewModels que herdam de QObject/QAbstractTableModel serao testados via `unittest.mock.patch` substituindo classes base Qt por mocks puros.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, unittest.mock (stdlib)
**Storage**: N/A (sem alteracoes de banco — escopo puramente de testes)
**Testing**: pytest + pytest-cov + pytest-asyncio (remover pytest-qt ^4.4)
**Target Platform**: GitHub Actions (Ubuntu headless, sem display grafico)
**Project Type**: desktop-app (refatoracao da suite de testes)
**Performance Goals**: Suite completa de testes <= 5 minutos no CI
**Constraints**: Zero imports de PySide6 nos arquivos de teste; zero alteracoes em src/ (exceto pragma: no cover em 3 arquivos visuais)
**Scale/Scope**: 119 arquivos fonte, ~157 arquivos de teste → meta 90% cobertura global

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Sem alteracoes em src/; testes continuam organizados por camada |
| II. DDD | ✅ PASS | Sem alteracoes em entidades de dominio |
| III. Repository Pattern | ✅ PASS | Sem alteracoes em repositorios |
| IV. Dependency Injection | ✅ PASS | Testes headless continuam usando mocks de container |
| V. SQLite | ✅ PASS | Sem alteracoes de banco |
| VI. Packaging | ✅ PASS | Remocao de pytest-qt e PySide6 de dev deps e compativel |
| VII. Estrutura de Diretorios | ✅ PASS | Testes reescritos permanecem nos mesmos diretorios |
| VIII. Async | ✅ PASS | Testes async continuam com pytest-asyncio |
| IX. Simplicidade | ✅ PASS | Mock puro e mais simples que dependencia de display grafico |
| X. Type Hints | ✅ PASS | Testes nao exigem type hints strict |
| XIV. Estrategia de Testes | ⚠️ JUSTIFIED | Constituicao exige pytest-qt para testes GUI. Esta feature REMOVE testes GUI e substitui por headless — violacao intencional e justificada. Constituicao deve ser atualizada pos-feature. |

**Gate Result**: PASS (1 violacao justificada)

## Project Structure

### Documentation (this feature)

```text
specs/032-test-refactor-headless/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Estrutura de testes ATUAL (antes da refatoracao)
tests/
├── conftest.py                    # Fixtures globais (DB, container, async)
├── e2e/                           # 22 arquivos — REMOVER INTEIRO
│   ├── conftest.py                # Fixtures Qt/async — REMOVER
│   ├── factories.py               # MIGRAR para tests/factories.py
│   └── test_*.py                  # 20 testes GUI — REMOVER
├── unit/
│   ├── domain/                    # 13 testes — SEM ALTERACAO
│   ├── application/               # 34 testes — SEM ALTERACAO
│   ├── infrastructure/            # 2 testes — SEM ALTERACAO
│   └── presentation/              # 24 arquivos totais — TRIAR (17 com dependencia Qt, 7 ja headless)
│       ├── delegates/             # 2 testes — TRIAR
│       ├── theme/                 # 1 teste — TRIAR
│       ├── views/                 # 3 testes — TRIAR
│       └── viewmodels/            # 14 testes — TRIAR
└── integration/
    ├── application/               # 5 testes — SEM ALTERACAO
    ├── infrastructure/            # 13 testes — SEM ALTERACAO
    └── presentation/              # 29 arquivos totais — TRIAR (16 com dependencia Qt, 13 ja headless)
        ├── conftest.py            # Mock asyncio — MANTER/ADAPTAR
        └── views/                 # 24 testes — TRIAR
            └── conftest.py        # Mock asyncio — MANTER/ADAPTAR

# Estrutura de testes ALVO (apos refatoracao)
tests/
├── conftest.py                    # Fixtures globais (SEM Qt/qasync)
├── factories.py                   # Migrado de tests/e2e/factories.py
├── unit/
│   ├── domain/                    # 13 testes — intactos
│   ├── application/               # 34 testes — intactos
│   ├── infrastructure/            # 2 testes — intactos
│   └── presentation/              # N testes headless (triados)
│       ├── delegates/             # Triados: logica de formatacao
│       ├── theme/                 # Triado
│       ├── views/                 # Triados: logica de negocio
│       └── viewmodels/            # Triados + novos headless
└── integration/
    ├── application/               # 5 testes — intactos
    ├── infrastructure/            # 13 testes — intactos
    └── presentation/              # N testes headless (triados)
```

**Structure Decision**: Manter estrutura existente por camada. Testes reescritos ficam nos mesmos diretorios. Diretorio `tests/e2e/` e removido integralmente. `tests/factories.py` criado como local compartilhado.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Principio XIV (pytest-qt para GUI) | Feature remove todos os testes GUI por design — CI headless nao suporta display | Manter pytest-qt requer virtual framebuffer (Xvfb) que adiciona complexidade e fragilidade ao CI |
