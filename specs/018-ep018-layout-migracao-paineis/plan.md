# Implementation Plan: EP-018 — Layout Principal e Migração de Painéis

**Branch**: `018-ep018-layout-migracao-paineis` | **Date**: 2026-03-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-ep018-layout-migracao-paineis/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Refatoração da MainWindow para layout vertical de 5 zonas (Menu Bar, Toolbar, Filter Bar, Table, Status Bar), substituindo o QSplitter horizontal atual. Migração de painéis laterais (ConfigPanel, DependencyPanel, MetricsPanel) para dialogs modais e WarningsPanel para integração na Status Bar. Integração de ícones SVG do design system (EP-017) na toolbar com agrupamento por categoria.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 6.x, qasync, pydantic
**Storage**: SQLite (via aiosqlite) — não afetado por esta feature
**Testing**: pytest + pytest-qt + qasync
**Target Platform**: Windows 10+ (desktop), compatível Linux/macOS
**Project Type**: desktop-app (PySide6)
**Performance Goals**: ≤100ms abertura de dialogs (SC-003), ≤3s cold start (SC-004)
**Constraints**: Resolução mínima 1366x768, WCAG AA contraste 4.5:1
**Scale/Scope**: Single-user desktop, ~15 telas/dialogs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Mudanças apenas na camada Presentation (views/) |
| II. DDD | ✅ PASS | Nenhuma mudança em Domain |
| III. Repository Pattern | ✅ PASS | Nenhuma mudança em Infrastructure |
| IV. Dependency Injection | ✅ PASS | Container existente será usado para novos ViewModels se necessário |
| VIII. Async (asyncio) | ✅ PASS | Dialogs usarão qasync como componentes existentes |
| IX. Simplicidade | ✅ PASS | Migração direta painel→dialog, sem abstração extra |
| X. Type Hints | ✅ PASS | Todos os novos componentes terão type hints |
| XIV. Testes | ✅ PASS | pytest-qt com qasync; testes existentes serão adaptados |
| XV. Idioma | ✅ PASS | Código em inglês, docstrings em português |
| XIX. UI/UX (MVVM) | ✅ PASS | Views só renderização, lógica em ViewModels |
| XXI. CI/CD | ✅ PASS | Testes devem passar, cobertura mantida |

**Gate Status**: ✅ PASSED — Nenhuma violação, pode prosseguir para Phase 0.

### Post-Design Re-evaluation

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Novos componentes são Views e ViewModels na Presentation layer |
| II. DDD | ✅ PASS | Nenhuma entidade de domínio alterada ou criada |
| IV. Dependency Injection | ✅ PASS | ViewModels receberão container via construtor |
| VIII. Async (asyncio) | ✅ PASS | Dialogs usam asyncio.create_task() como padrão existente |
| IX. Simplicidade | ✅ PASS | Lógica migrada dos panels, sem over-engineering |
| X. Type Hints | ✅ PASS | data-model.md define tipos para todos os componentes |
| XIV. Testes | ✅ PASS | Estratégia de testes definida em quickstart.md |
| XIX. UI/UX (MVVM) | ✅ PASS | 3 novos ViewModels definidos para dialogs e status bar |

**Post-Design Gate**: ✅ PASSED — Design alinhado com constituição. Pronto para geração de tasks.

## Project Structure

### Documentation (this feature)

```text
specs/018-ep018-layout-migracao-paineis/
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
│   │   ├── main_window.py         # MODIFICAR: Refatorar layout para 5 zonas
│   │   ├── config_dialog.py       # CRIAR: Dialog modal de configuração
│   │   ├── dependency_dialog.py   # CRIAR: Dialog modal de dependências
│   │   ├── metrics_dialog.py      # CRIAR: Dialog modal de métricas
│   │   ├── status_bar.py          # CRIAR: Status bar com contadores e warnings
│   │   ├── config_panel.py        # MANTER: Código legado, remover de main_window
│   │   ├── dependency_panel.py    # MANTER: Código legado, remover de main_window
│   │   ├── metrics_panel.py       # MANTER: Código legado, remover de main_window
│   │   └── warnings_panel.py      # MANTER: Código legado, remover de main_window
│   ├── viewmodels/
│   │   ├── config_dialog_viewmodel.py     # CRIAR: ViewModel para ConfigDialog
│   │   ├── dependency_dialog_viewmodel.py # CRIAR: ViewModel para DependencyDialog
│   │   └── status_bar_viewmodel.py        # CRIAR: ViewModel para StatusBar
│   └── theme/
│       ├── theme.py               # EXISTENTE: IconManager já implementado
│       └── stylesheet.qss         # EXISTENTE: Estilos para novos componentes
├── assets/
│   └── icons/                     # EXISTENTE: 16 SVGs prontos para uso
│       ├── plus.svg, pencil-simple.svg, trash.svg
│       ├── arrow-up.svg, arrow-down.svg
│       ├── users.svg, package.svg, gear.svg
│       ├── calendar-check.svg, shuffle.svg
│       └── download-simple.svg, upload-simple.svg

tests/
├── integration/
│   └── presentation/
│       └── views/
│           ├── test_main_window.py        # MODIFICAR: Adaptar para novo layout
│           ├── test_config_dialog.py      # CRIAR: Testes do ConfigDialog
│           ├── test_dependency_dialog.py  # MODIFICAR: Adaptar de test_dependency_panel
│           ├── test_metrics_dialog.py     # CRIAR: Testes do MetricsDialog
│           └── test_status_bar.py         # CRIAR: Testes da StatusBar
└── unit/
    └── presentation/
        └── viewmodels/
            ├── test_config_dialog_viewmodel.py     # CRIAR
            ├── test_dependency_dialog_viewmodel.py # CRIAR
            └── test_status_bar_viewmodel.py        # CRIAR
```

**Structure Decision**: Mantém estrutura existente do Backlog Manager conforme Princípio VII (Estrutura de Diretórios). Novos dialogs seguem padrão de `story_dialog.py` e `developer_dialog.py`. ViewModels adicionados seguindo padrão MVVM existente.

## Complexity Tracking

> Nenhuma violação de Constitution Check identificada. Tabela vazia.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
