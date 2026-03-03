# Implementation Plan: EP-008 Interface Grafica

**Branch**: `008-ep008-graphical-interface` | **Date**: 2026-03-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-ep008-graphical-interface/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar a camada de apresentacao (Presentation Layer) completa em PySide6 que integra todas as capacidades ja implementadas (EP-001 a EP-007) em uma interface grafica funcional. O epico implementa o padrao MVVM com Views, ViewModels, DI Container, Entry Point, e usa qasync para integracao asyncio/Qt. Testes de GUI utilizam pytest-qt.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.6.1, qasync ^0.27.1, pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0
**Storage**: SQLite via aiosqlite (schema existente com 5 tabelas: Developer, Feature, Story, Story_Dependency)
**Testing**: pytest ^8.0, pytest-qt ^4.4, pytest-asyncio ^0.23, pytest-cov ^4.0
**Target Platform**: Windows 10/11 (desktop application)
**Project Type**: Desktop application (library + GUI entry point)
**Performance Goals**: Cold start <= 3s, CRUD <= 100ms, Alocacao 100 historias <= 5s (RNF-PERF)
**Constraints**: Resolucao minima 1366x768, contraste WCAG AA 4.5:1, interface responsiva durante alocacao
**Scale/Scope**: Ate 500+ historias, 11 user stories, 184 requisitos funcionais, 23 use cases integrados

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Verificacao | Status |
|-----------|-------------|--------|
| **I. Clean Architecture** | Presentation depende apenas de Application DTOs e ViewModels. Views NAO importam Domain ou Infrastructure. | PASS |
| **II. DDD** | ViewModels consomem Use Cases que encapsulam regras de dominio. Nenhuma logica de dominio na camada de apresentacao. | PASS |
| **III. Repository Pattern** | Views/ViewModels NAO acessam repositorios diretamente - apenas atraves de Use Cases. | PASS |
| **IV. Dependency Injection** | DIContainer centralizado em presentation/container.py, configurado na raiz (main). | PASS |
| **V. SQLite** | Utiliza infraestrutura existente (SQLiteUnitOfWork, SQLiteConnection). | PASS |
| **VI. Packaging** | Adiciona PySide6, qasync, pytest-qt ao pyproject.toml. Entry point em [project.scripts]. | PASS |
| **VII. Estrutura de Diretorios** | presentation/views/ e presentation/viewmodels/ conforme Constituicao. | PASS |
| **VIII. Async** | qasync integra asyncio com Qt event loop. ViewModels usam async/await via asyncio.create_task(). | PASS |
| **IX. Simplicidade** | MVVM minimo: ViewModels apenas para MainWindow, StoryDialog, Allocation. Dialogos simples com logica inline. | PASS |
| **X. Type Hints** | Todos os componentes com type hints. mypy strict mode. | PASS |
| **XI. Docstrings** | Classes e metodos publicos com docstrings Google style. | PASS |
| **XII. Imports (isort)** | Imports organizados: stdlib -> PySide6/qasync -> local. | PASS |
| **XIII. Nomenclatura** | PascalCase para classes (MainWindow, StoryDialog), snake_case para metodos/variaveis. | PASS |
| **XIV. Testes** | ViewModels >= 80%, Views >= 50%. pytest-qt + qasync. | PASS (Target) |
| **XV. Idioma** | Codigo em ingles, textos da UI em portugues (PT-BR). | PASS |
| **XVI. Tratamento de Erros** | ViewModels capturam excecoes, emitem signal error_occurred. Views exibem QMessageBox em PT-BR. | PASS |
| **XVII. Logging** | Logger configurado. Operacoes criticas logam INFO, erros logam ERROR. | PASS |
| **XVIII. Gestao de Configuracao** | ConfigPanel sem persistencia no MVP (ADR-007). Valores passados como parametros. | PASS (ADR-007) |
| **XIX. Padroes UI/UX** | MVVM com Views -> ViewModels -> Use Cases. Latencia <= 100ms, resolucao 1366x768. | PASS |
| **XX. Validacao de Entrada** | Sanitizacao em ViewModels antes de chamar Use Cases. | PASS |
| **XXI. CI/CD** | black, isort, mypy, pytest-cov, pre-commit hooks. | PASS |

**Resultado**: Todos os gates passam. ADR-007 (ConfigPanel sem persistencia) e uma excecao justificada no spec.md.

## Project Structure

### Documentation (this feature)

specs/008-ep008-graphical-interface/
- plan.md              (This file - /speckit.plan command output)
- research.md          (Phase 0 output - /speckit.plan command)
- data-model.md        (Phase 1 output - /speckit.plan command)
- quickstart.md        (Phase 1 output - /speckit.plan command)
- contracts/           (Phase 1 output - /speckit.plan command)
- tasks.md             (Phase 2 output - /speckit.tasks command - NOT created by /speckit.plan)

### Source Code (repository root)

src/backlog_manager/
- domain/                          [EXISTENTE] EP-001 a EP-007
  - entities/                      Story, Developer, Feature
  - value_objects/                 StoryPoint, StoryStatus
  - services/                      AllocationService, SchedulingService, etc.
  - interfaces/                    Repository protocols
  - exceptions/                    BacklogManagerException hierarchy

- application/                     [EXISTENTE] 23 Use Cases, 22 DTOs
  - use_cases/                     story/, developer/, feature/, dependency/, scheduling/, allocation/
  - dto/                           Input/Output DTOs (Pydantic)
  - interfaces/

- infrastructure/                  [EXISTENTE] SQLite implementation
  - database/
    - sqlite_connection.py
    - unit_of_work.py              SQLiteUnitOfWork
    - schema.sql
    - repositories/                SQLite repository implementations
  - logging/

- presentation/                    [EP-008] Nova implementacao
  - __init__.py
  - app.py                         Entry point: main() com qasync
  - container.py                   DIContainer centralizado
  - viewmodels/                    Logica de apresentacao (MVVM)
    - __init__.py
    - main_window_viewmodel.py     ViewModel principal
    - story_table_model.py         QAbstractTableModel para tabela
    - story_dialog_viewmodel.py
    - allocation_viewmodel.py
  - views/                         Widgets PySide6
    - __init__.py
    - main_window.py               QMainWindow principal
    - story_table_view.py          QTableView do backlog
    - story_dialog.py              QDialog criar/editar historia
    - developer_dialog.py          QDialog gerenciar desenvolvedores
    - feature_dialog.py            QDialog gerenciar features
    - dependency_panel.py          QWidget dependencias
    - config_panel.py              QWidget configuracao
    - metrics_panel.py             QWidget metricas
    - warnings_panel.py            QWidget avisos
    - confirm_delete_dialog.py     QDialog confirmacao

tests/
- unit/
  - presentation/
    - viewmodels/                  Testes de ViewModels
      - test_main_window_viewmodel.py
      - test_story_dialog_viewmodel.py
      - test_story_table_model.py
      - test_allocation_viewmodel.py
  - ...                            [EXISTENTE] Testes de domain/application

- integration/
  - presentation/
    - views/                       Testes de Views com pytest-qt
      - test_main_window.py
      - test_story_dialog.py
      - test_developer_dialog.py
      - test_feature_dialog.py
      - test_dependency_panel.py

**Structure Decision**: Utiliza a estrutura existente de Clean Architecture (src/backlog_manager/) e adiciona os componentes de presentation/ conforme Constituicao VII. Testes de GUI ficam em tests/integration/presentation/views/ para usar pytest-qt com I/O real.

## Complexity Tracking

> **Nenhuma violacao de Constituicao a justificar.**

A decisao ADR-007 (ConfigPanel sem persistencia) esta documentada no spec.md e e uma simplificacao para o MVP, nao uma violacao.

## Post-Design Constitution Re-check

*Re-evaluated after Phase 1 design completion.*

| Principio | Pos-Design Verification | Status |
|-----------|------------------------|--------|
| **I. Clean Architecture** | research.md confirma Views -> ViewModels -> UseCases. data-model.md mostra DTOs como contrato. | PASS |
| **II. DDD** | ViewModels consomem apenas Use Cases. Nenhuma logica de dominio exposta. | PASS |
| **III. Repository Pattern** | DIContainer encapsula UoW. ViewModels nao acessam repositorios. | PASS |
| **IV. Dependency Injection** | container.py instancia grafo completo. Lazy loading para Use Cases. | PASS |
| **VIII. Async** | qasync @asyncSlot() decorator pattern definido em research.md. | PASS |
| **XIV. Testes** | pytest-qt fixtures customizadas definidas. Cobertura target mantida. | PASS |
| **XVI. Tratamento de Erros** | Signal error_occurred + QMessageBox definido em research.md e contracts/. | PASS |
| **XIX. Padroes UI/UX** | MVVM signals contract definido. StoryTableModel usa QAbstractTableModel. | PASS |

**Resultado Pos-Design**: Todos os gates continuam passando. Design alinhado com Constituicao.
