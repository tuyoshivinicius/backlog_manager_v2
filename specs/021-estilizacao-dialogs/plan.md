# Implementation Plan: Estilizacao de Dialogs

**Branch**: `021-estilizacao-dialogs` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/021-estilizacao-dialogs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Estilizar todos os dialogs existentes com visual consistente via objectNames + QSS centralizado, adicionar campo Desenvolvedor (dropdown) ao dialog de historia em modo edicao, implementar validacao em tempo real (on-blur) com feedback visual inline, adicionar icones/hover/estados vazios nos dialogs de desenvolvedores e features, reformular o dialog de confirmacao de exclusao com alerta visual, e criar dialogs de progresso e resultado para import/export.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 (UI), Pydantic (DTOs), qasync (async/Qt integration)
**Storage**: N/A (escopo Presentation/Application — dados ja vem do SQLite via use cases existentes)
**Testing**: pytest + pytest-qt + pytest-asyncio (testes unitarios e integracao)
**Target Platform**: Desktop Windows (compativel Linux)
**Project Type**: desktop-app (PySide6 MVVM)
**Performance Goals**: Validacao on-blur ≤ 100ms, CRUD dialog response ≤ 100ms (RNF-PERF-002)
**Constraints**: Resolucao minima 1366x768 (RNF-USAB-002), contraste WCAG AA 4.5:1 (RNF-USAB-003)
**Scale/Scope**: 5 dialogs existentes refatorados + 2 novos dialogs (progresso/resultado)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Escopo limitado a Presentation (views, viewmodels) e Application (DTO). Nenhuma alteracao em Domain ou Infrastructure. |
| II. DDD | ✅ PASS | Nenhuma alteracao em entidades ou value objects. Story entity ja possui developer_id. |
| III. Repository Pattern | ✅ PASS | Nenhum repositorio novo. Reutiliza use cases existentes (ListDevelopers, EditStory). |
| IV. Dependency Injection | ✅ PASS | Novos componentes receberao dependencias via DIContainer existente. |
| V. SQLite | ✅ N/A | Sem alteracoes em persistencia. |
| VI. Packaging | ✅ PASS | Nenhum novo pacote/dependencia. Apenas novos modulos em presentation/. |
| VII. Estrutura de Diretorios | ✅ PASS | Novos arquivos em presentation/views/ e presentation/viewmodels/, testes em tests/. |
| VIII. Programacao Assincrona | ✅ PASS | Carregamento de desenvolvedores sera async via qasync, seguindo padrao existente de load_features. |
| IX. Simplicidade | ✅ PASS | Reutiliza padroes existentes (QSS, signals, MVVM). Sem abstracoes novas. |
| X. Type Hints | ✅ PASS | Todos os novos metodos terao type hints. |
| XI. Docstrings | ✅ PASS | Classes e metodos publicos terao docstrings Google style. |
| XII. Imports (isort) | ✅ PASS | |
| XIII. Nomenclatura | ✅ PASS | PascalCase para classes, snake_case para metodos/variaveis. |
| XIV. Testes | ✅ PASS | Testes unitarios para ViewModel (validacao, developer_id). Testes integracao para views (dialog rendering, estados). |
| XV. Idioma | ✅ PASS | Codigo em ingles, mensagens ao usuario em portugues (sem acentos). |
| XVI. Tratamento de Erros | ✅ PASS | Erros de carregamento de devs emitidos via signal error_occurred. |
| XVII. Logging | ✅ PASS | Operacoes de carga/save logam via logger existente. |
| XVIII. Configuracao | ✅ N/A | Sem novos parametros configuraveis. |
| XIX. UI/UX (PySide6) | ✅ PASS | MVVM mantido. Views apenas renderizam; logica no ViewModel. objectNames para QSS. |
| XX. Validacao | ✅ PASS | Validacao on-blur no ViewModel; apresentacao visual na View. |
| XXI. CI/CD | ✅ PASS | Novos testes integrados ao pytest. |

**Gate Result**: ✅ ALL PASS — nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/021-estilizacao-dialogs/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── application/
│   └── dto/story/
│       └── edit_story_dto.py        # ADD: developer_id field
├── presentation/
│   ├── theme/
│   │   └── stylesheet.qss           # MODIFY: add dialog-specific QSS rules
│   ├── viewmodels/
│   │   └── story_dialog_viewmodel.py # MODIFY: developer_id, load_developers, validate_field
│   └── views/
│       ├── story_dialog.py           # MODIFY: developer dropdown, validation UI, objectNames
│       ├── developer_dialog.py       # MODIFY: icons, hover, empty state, objectNames
│       ├── feature_dialog.py         # MODIFY: "Onda N — Nome" format, empty state, objectNames
│       ├── confirm_delete_dialog.py  # MODIFY: alert icon, entity-specific text, red button
│       ├── progress_dialog.py        # NEW: modal progress with styled bar
│       └── result_dialog.py          # NEW: modal result with formatted counts

tests/
├── unit/presentation/viewmodels/
│   └── test_story_dialog_viewmodel.py  # MODIFY: add developer + validate_field tests
└── integration/presentation/views/
    ├── test_story_dialog.py            # MODIFY: add developer field + validation UI tests
    ├── test_developer_dialog.py        # MODIFY: add icon/hover/empty state tests
    ├── test_feature_dialog.py          # MODIFY: add wave format + empty state tests
    ├── test_confirm_delete_dialog.py   # NEW: entity-specific confirmation tests
    ├── test_progress_dialog.py         # NEW: progress dialog tests
    └── test_result_dialog.py           # NEW: result dialog tests
```

**Structure Decision**: Reutiliza a estrutura existente de presentation/ (MVVM). Novos arquivos apenas para os 2 dialogs novos (progress_dialog.py, result_dialog.py) e testes correspondentes. Todas as demais alteracoes sao modificacoes em arquivos existentes.

## Complexity Tracking

> Nenhuma violacao da constituicao identificada. Tabela vazia.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
