# Implementation Plan: Refatoracao do Roadmap Visualization

**Branch**: `040-roadmap-refactor` | **Date**: 2026-04-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/040-roadmap-refactor/spec.md`

## Summary

Refatoracao completa do roadmap de visualizacao, substituindo a engine QGraphicsView por matplotlib embarcado em QDialog PySide6. O objetivo e resolver o bug de historias omitidas, eliminar travamentos de UI via carregamento assincrono, simplificar a base de codigo removendo indicadores visuais (overdue, critical deps, deadlines) e suas persistencias QSettings, e entregar um visual profissional estilo Gantt com agrupamento por Feature/Componente, scroll, zoom e tooltips.

## Technical Context

**Language/Version**: Python 3.13+ (runtime), 3.11+ (compatibilidade)
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, matplotlib (nova dependencia)
**Storage**: N/A (dados lidos via use cases existentes — sem alteracoes SQLite)
**Testing**: pytest ^8.0, pytest-asyncio ^0.23, pytest-cov ^4.0, unittest.mock (headless mocks)
**Target Platform**: Windows desktop (PySide6), resolucao minima 1366x768
**Project Type**: desktop-app (library-first via Poetry)
**Performance Goals**: Renderizacao de 200+ historias em < 3 segundos, UI responsiva durante carregamento
**Constraints**: Modal dialog, maximizada, sem novas dependencias alem de matplotlib
**Scale/Scope**: Escopo puramente Presentation layer (2 arquivos fonte + 2 arquivos de teste)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | PASS | Escopo restrito a Presentation layer. Nenhuma importacao de Domain/Infrastructure diretamente. Dados via use cases existentes. |
| II. DDD | N/A | Nenhuma alteracao em entidades ou domain services. |
| III. Repository Pattern | N/A | Nenhuma alteracao em repositorios. |
| IV. Dependency Injection | PASS | ViewModel recebe `container` via construtor. Dialog recebe ViewModel via construtor. |
| V. SQLite | N/A | Nenhuma operacao de persistencia. |
| VI. Packaging | PASS | matplotlib sera adicionado ao pyproject.toml como dependencia. |
| VII. Estrutura de Diretorios | PASS | Arquivos em `presentation/views/` e `presentation/viewmodels/`. Testes em `tests/unit/presentation/`. |
| VIII. Async | PASS | Carregamento de dados via `async def load_data()` com qasync. |
| IX. Simplicidade | PASS | Refatoracao visa simplificar: remover indicadores, remover QSettings, menos classes/estados (SC-006). |
| X. Type Hints | PASS | Todas as assinaturas com type hints. Mypy strict. |
| XI. Docstrings | PASS | Classes e metodos publicos com docstrings Google style. |
| XII. isort | PASS | Imports organizados. |
| XIII. Nomenclatura | PASS | PascalCase classes, snake_case funcoes/variaveis, UPPER_SNAKE_CASE constantes. |
| XIV. Testes | PASS | Testes headless existentes serao atualizados. Cobertura alvo: viewmodels 80%+, views 50%+. |
| XV. Idioma | PASS | Codigo em ingles, docs/mensagens em portugues. |
| XVI. Tratamento de Erros | PASS | Erro de I/O no carregamento exibe mensagem amigavel, sem travar. |
| XVII. Logging | PASS | Logging de operacoes do roadmap. |
| XVIII. Configuracao | N/A | Nenhuma configuracao nova. Remocao de QSettings de indicadores (FR-014). |
| XIX. UI/UX MVVM | PASS | View (RoadmapDialog) + ViewModel (RoadmapViewModel), separacao mantida. |
| XX. Validacao | N/A | Feature read-only, sem entrada do usuario alem de controles de UI. |
| XXI. CI/CD | PASS | Testes, black, isort, mypy validados em pipeline. |

**GATE RESULT: PASS** — Nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/040-roadmap-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/presentation/
├── viewmodels/
│   └── roadmap_viewmodel.py    # ViewModel refatorado (simplificado)
├── views/
│   └── roadmap_dialog.py       # Dialog refatorada (matplotlib engine)
└── theme/
    └── theme.py                # STATUS_PALETTE (existente, sem alteracao)

tests/unit/presentation/
├── viewmodels/
│   └── test_roadmap_viewmodel.py   # Testes atualizados
└── views/
    └── test_roadmap_dialog.py      # Testes atualizados
```

**Structure Decision**: Reutiliza os mesmos 2 arquivos fonte e 2 arquivos de teste existentes. Nenhum arquivo novo necessario alem da dependencia matplotlib no pyproject.toml.

## Complexity Tracking

> Nenhuma violacao de constituicao — tabela nao aplicavel.
