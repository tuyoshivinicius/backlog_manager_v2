# Implementation Plan: Visualizacao de Roadmap

**Branch**: `039-roadmap-visualization` | **Date**: 2026-04-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/039-roadmap-visualization/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar tela fullscreen (QDialog maximizado) com visualizacao Gantt-like de timeline para acompanhar progresso do backlog apos planejamento. Utiliza QGraphicsView + QGraphicsScene para renderizar barras de historia posicionadas temporalmente, com agrupamento por feature/componente, tooltips ricos, indicadores visuais opcionais (atraso, criticidade, deadlines) e persistencia de preferencias via QSettings.

## Technical Context

**Language/Version**: Python 3.11+ (runtime)
**Primary Dependencies**: PySide6 ^6.10.0 (QGraphicsView, QGraphicsScene, QGraphicsItem, QDialog), qasync ^0.27.1, Pydantic ^2.0
**Storage**: QSettings (INI format) para preferencias de indicadores visuais; sem alteracoes SQLite (dados lidos via use cases existentes)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, pytest-qt (QGraphicsView headless)
**Target Platform**: Windows 11, desktop (PySide6)
**Project Type**: desktop-app (camada Presentation apenas)
**Performance Goals**: Renderizacao < 3 segundos para 200 historias; scroll/zoom responsivo a 60fps
**Constraints**: Somente leitura (nenhuma edicao de dados na tela de roadmap); integrar com design system existente (tokens de tema)
**Scale/Scope**: Ate 200 historias simultaneas na timeline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Feature reside inteiramente na camada Presentation (views + viewmodels). Dados acessados via use cases existentes (ListStoriesUseCase, ListFeaturesUseCase). Sem dependencias invertidas. |
| II. DDD | ✅ PASS | Nenhuma alteracao no dominio. Entidades Story, Feature, Developer ja existem. |
| III. Repository Pattern | ✅ PASS | Sem novos repositorios. Reutiliza repositorios existentes via UnitOfWork. |
| IV. Dependency Injection | ✅ PASS | RoadmapDialog recebera dependencias via construtor (DIContainer). ViewModel injetado. |
| V. SQLite | ✅ PASS | Sem alteracoes de schema. Dados lidos via use cases async existentes. |
| VI. Packaging | ✅ PASS | Sem novas dependencias externas. PySide6 QGraphicsView ja incluso. |
| VII. Estrutura Diretorios | ✅ PASS | Novos arquivos em `presentation/views/` e `presentation/viewmodels/`. Testes em `tests/unit/presentation/`. |
| VIII. Async | ✅ PASS | Carregamento de dados via async use cases. Renderizacao sincrona na UI thread (QGraphicsScene). |
| IX. Simplicidade | ✅ PASS | QGraphicsView e a abordagem nativa do Qt para graficos 2D — sem bibliotecas externas de charting. |
| X. Type Hints | ✅ PASS | Todos os novos modulos terao type hints completos. |
| XI. Docstrings | ✅ PASS | Classes e metodos publicos terao docstrings Google style. |
| XII. Imports (isort) | ✅ PASS | Seguira convencoes existentes. |
| XIII. Nomenclatura | ✅ PASS | PascalCase para classes, snake_case para metodos/variaveis. |
| XIV. Testes | ✅ PASS | Testes unitarios para ViewModel, testes de widget para QGraphicsView com pytest-qt. |

**Gate Result (Pre-Phase 0)**: ✅ ALL PASS — Nenhuma violacao constitucional. Prosseguir para Phase 0.

**Gate Result (Post-Phase 1 Re-check)**: ✅ ALL PASS — Design confirmado como puramente Presentation layer. Nenhum novo modelo de dominio, repositorio ou schema. Novos dataclasses (RoadmapGroup, RoadmapData, RoadmapIndicators, RoadmapGroupMode) residem exclusivamente em `presentation/viewmodels/`. Dados acessados via use cases existentes (ListStoriesUseCase, ListFeaturesUseCase). QSettings para preferencias — sem SQLite.

## Project Structure

### Documentation (this feature)

```text
specs/039-roadmap-visualization/
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
├── presentation/
│   ├── views/
│   │   └── roadmap_dialog.py          # QDialog maximizado com QGraphicsView
│   └── viewmodels/
│       └── roadmap_viewmodel.py       # Logica de apresentacao (dados, agrupamento, filtros)
tests/
├── unit/
│   └── presentation/
│       ├── test_roadmap_viewmodel.py   # Testes unitarios do ViewModel
│       └── test_roadmap_dialog.py      # Testes de widget (pytest-qt)
```

**Structure Decision**: Single project, camada Presentation apenas. Novos arquivos seguem a estrutura existente em `presentation/views/` e `presentation/viewmodels/`.

## Complexity Tracking

> Nenhuma violacao constitucional identificada. Tabela vazia.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
