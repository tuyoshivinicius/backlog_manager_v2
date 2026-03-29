# Implementation Plan: EP-019 — Tabela de Backlog (GUI-003)

**Branch**: `019-backlog-table` | **Date**: 2026-03-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/019-backlog-table/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expandir o `StoryTableModel` de 8 para 13 colunas (Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao), reordenar colunas, reposicionar delegates existentes nos novos indices, enriquecer o `StoryOutputDTO` com campos resolvidos (developer_name, feature_name, wave, dependencies), aplicar estilizacao QSS (zebra, selecao, header), implementar estado vazio orientativo, e criar testes unitarios dedicados. Escopo exclusivo nas camadas Presentation e Application (DTO).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 (UI), Pydantic (DTOs), pytest + pytest-qt (testes)
**Storage**: N/A (escopo Presentation/Application — dados ja vem do SQLite via use cases existentes)
**Testing**: pytest com pytest-qt e qasync para testes de GUI; pytest-cov para cobertura
**Target Platform**: Windows 11 desktop (minimo 1366x768)
**Project Type**: desktop-app (PySide6, MVVM)
**Performance Goals**: 60fps rendering com ate 500 historias, renderizacao imperceptivel por celula
**Constraints**: Resolucao minima 1366x768; contraste WCAG AA >= 4.5:1; latencia <= 100ms
**Scale/Scope**: Ate 500 historias no backlog; 13 colunas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Relevancia | Status | Justificativa |
|-----------|-----------|--------|---------------|
| I. Clean Architecture | Alta | PASS | Mudancas restritas a Presentation (ViewModel, View, delegates) e Application (DTO). Domain intocado. Fluxo de dependencias Presentation → Application respeitado. |
| II. DDD | Baixa | PASS | Nenhuma mudanca em entidades ou value objects do dominio. |
| III. Repository Pattern | Baixa | PASS | Nenhuma mudanca em repositorios. DTO enriquecido construido no use case. |
| IV. Dependency Injection | Media | PASS | Delegates e model injetados via construtor. Container nao alterado. |
| V. SQLite | N/A | PASS | Sem mudancas em persistencia. |
| VI. Packaging | N/A | PASS | Sem mudancas em dependencias ou pacote. |
| VII. Estrutura de Diretorios | Media | PASS | Novos arquivos em `presentation/viewmodels/`, `tests/unit/presentation/`. Estrutura existente respeitada. |
| VIII. Async | Baixa | PASS | Sem novas operacoes async. Use case existente ja e async. |
| IX. Simplicidade | Alta | PASS | Expansao direta de modelo existente. Sem abstracoes especulativas. |
| X. Type Hints | Alta | PASS | Todos os novos campos e metodos terao type hints. |
| XI. Docstrings | Alta | PASS | Classes e metodos publicos novos terao docstrings Google style. |
| XII. Imports (isort) | Media | PASS | Imports organizados conforme padrao. |
| XIII. Nomenclatura | Media | PASS | PascalCase para classes, snake_case para metodos/variaveis, UPPER_SNAKE_CASE para constantes. |
| XIV. Testes | Alta | PASS | Meta >= 80% cobertura para StoryTableModel. Testes com pytest-qt. |
| XV. Idioma | Media | PASS | Codigo em ingles, textos UI em portugues. |
| XVI. Erros | Baixa | PASS | Sem novas excecoes. Valores ausentes exibem "—". |
| XVII. Logging | Baixa | PASS | Logs existentes suficientes. |
| XVIII. Configuracao | N/A | PASS | Sem mudancas em configuracao. |
| XIX. UI/UX (MVVM) | Alta | PASS | StoryTableModel e ViewModel puro. View apenas renderiza. Delegates separados. |
| XX. Validacao | Baixa | PASS | Sem entrada de usuario nova. Dados ja validados pela Application. |
| XXI. CI/CD | Media | PASS | Testes e linting existentes cobrem novos arquivos. |

**Resultado**: Todos os gates PASS. Nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/019-backlog-table/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── table-model-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── application/
│   └── dto/
│       └── story/
│           └── story_output_dto.py        # Enriquecer com developer_name, feature_name, wave, dependencies
├── presentation/
│   ├── viewmodels/
│   │   └── story_table_model.py           # Expandir 8→13 colunas, reordenar, tooltips
│   ├── views/
│   │   └── main_window.py                 # Reposicionar delegates, larguras fixas, estado vazio
│   └── theme/
│       └── stylesheet.qss                 # Ajustes QSS (selecao, header) se necessario

tests/
├── unit/
│   └── presentation/
│       └── viewmodels/
│           └── test_story_table_model.py  # Expandir testes para 13 colunas
└── integration/
    └── presentation/
        └── test_delegates_integration.py  # Atualizar para novos indices
```

**Structure Decision**: Projeto single (src layout) existente. Mudancas em arquivos existentes — nenhum novo modulo ou diretorio de codigo necessario.

## Complexity Tracking

> Nenhuma violacao de constituicao. Tabela vazia.
