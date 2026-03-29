# Implementation Plan: EP-020 — Busca, Filtros e Menu de Contexto

**Branch**: `020-busca-filtros-menu-contexto` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/020-busca-filtros-menu-contexto/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar busca incremental com debounce, filtros por status (chips) e feature/onda (dropdown), menu de contexto com right-click e acao de Duplicar Historia na UI. A abordagem tecnica usa QSortFilterProxyModel como intermediario entre StoryTableModel e StoryTableView, mantendo o modelo original intacto. Filtros combinam com AND logico. Menu de contexto e criado dinamicamente a cada right-click. Duplicacao reutiliza DuplicateStoryUseCase existente.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 (UI), Pydantic (DTOs), qasync (async/Qt integration)
**Storage**: N/A (escopo Presentation — dados ja vem do SQLite via use cases existentes)
**Testing**: pytest + pytest-qt + qasync
**Target Platform**: Desktop Windows/Linux (resolucao minima 1366x768)
**Project Type**: desktop-app (PySide6 MVVM)
**Performance Goals**: Debounce 150ms na busca; filtragem < 100ms; duplicacao < 500ms com feedback
**Constraints**: Delegates (MonospaceDelegate col 3, StatusBadgeDelegate col 6) devem funcionar com proxy model; atalhos Ctrl+D e Ctrl+F sem conflito
**Scale/Scope**: Centenas de historias (~500 max), 5 status, dezenas de features

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Escopo 100% Presentation layer. FilterProxyModel e widget de filtros ficam em presentation/. Nenhuma mudanca em Domain/Application/Infrastructure. DuplicateStoryUseCase ja existe em Application. |
| II. DDD | ✅ PASS | Nenhuma entidade de dominio modificada. Logica de duplicacao ja esta em StoryService.duplicate_story(). |
| III. Repository Pattern | ✅ PASS | Nenhum repositorio modificado. |
| IV. Dependency Injection | ✅ PASS | DuplicateStoryUseCase ja disponivel via DIContainer.create_duplicate_story_use_case(). |
| V. SQLite | ✅ PASS | Nenhuma alteracao de banco. |
| VI. Packaging | ✅ PASS | Novos modulos ficam dentro do pacote existente. |
| VII. Estrutura de Diretorios | ✅ PASS | Novos arquivos seguem estrutura existente: presentation/viewmodels/ e presentation/views/. |
| VIII. Programacao Assincrona | ✅ PASS | duplicate_story no ViewModel segue padrao async existente (create_task pattern). FilterProxyModel e sincrono (Qt model layer). |
| IX. Simplicidade | ✅ PASS | QSortFilterProxyModel e o padrao Qt nativo para filtragem. Sem over-engineering. |
| X. Type Hints | ✅ PASS | Todos os novos metodos terao type hints completos. |
| XI. Docstrings | ✅ PASS | Classes e metodos publicos terao docstrings Google style. |
| XII. Imports (isort) | ✅ PASS | Seguir organizacao padrao. |
| XIII. Nomenclatura | ✅ PASS | PascalCase para classes, snake_case para metodos. |
| XIV. Testes | ✅ PASS | FilterProxyModel tera cobertura >= 80%. Testes com pytest-qt. |
| XV. Idioma | ✅ PASS | Codigo em ingles, docs em portugues. |
| XVI. Tratamento de Erros | ✅ PASS | Erros de duplicacao tratados no ViewModel com error_occurred signal. |
| XVII. Logging | ✅ PASS | Operacoes criticas (duplicacao) terao log INFO. |
| XVIII. Configuracao | ✅ PASS | Nenhuma configuracao nova necessaria. |
| XIX. UI/UX (MVVM) | ✅ PASS | FilterProxyModel e logica de filtros no ViewModel. View apenas renderiza e captura eventos. |
| XX. Validacao de Entrada | ✅ PASS | Busca trata texto como literal (sem regex). Filtros usam valores predefinidos. |
| XXI. CI/CD | ✅ PASS | Novos testes integrados ao pytest. Black/isort/mypy aplicados. |

**Gate Result**: ✅ ALL PASS — nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/020-busca-filtros-menu-contexto/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ui-contracts.md  # UI component contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── presentation/
│   ├── viewmodels/
│   │   ├── story_table_model.py          # Existente (sem alteracao)
│   │   ├── main_window_viewmodel.py      # Modificado: +duplicate_story(), +signals filtros
│   │   └── filter_proxy_model.py         # NOVO: QSortFilterProxyModel customizado
│   ├── views/
│   │   └── main_window.py                # Modificado: +zona 3 widgets, +menu contexto, +Ctrl+D/F
│   ├── delegates/                        # Existente (sem alteracao)
│   └── theme/
│       └── stylesheet.qss               # Modificado: +estilos chips, search field, menu destructive

tests/
├── unit/
│   └── presentation/
│       ├── test_filter_proxy_model.py    # NOVO: testes do FilterProxyModel
│       └── test_main_window_viewmodel.py # Modificado: +testes duplicate_story
└── integration/
    └── presentation/
        └── test_main_window_filters.py   # NOVO: testes integrados filtros+contexto (pytest-qt)
```

**Structure Decision**: Segue estrutura existente. Unico arquivo novo de producao e `filter_proxy_model.py` em viewmodels/. Demais sao modificacoes em arquivos existentes.

## Complexity Tracking

> Nenhuma violacao de constituicao — tabela nao aplicavel.
