# Implementation Plan: Roadmap UX Refactor

**Branch**: `043-roadmap-ux-refactor` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/043-roadmap-ux-refactor/spec.md`

## Summary

Refatorar a visualização do roadmap para melhorar a experiência de navegação e interpretação. As mudanças principais são: (1) adição de pan/drag horizontal via click+arrasto no gráfico matplotlib com cursores visuais de mão aberta/fechada, (2) navegação horizontal alternativa via teclas de seta, (3) polimento da toolbar com ícones e tooltips em todos os controles. A implementação atual já possui toolbar agrupada, filtros (feature/componente/responsável/nome), zoom in/out/reset, agrupamento por feature com expand/collapse, código da história nas barras e legenda lateral com contagem e percentual — esses elementos serão mantidos e refinados.

## Technical Context

**Language/Version**: Python 3.13+ (runtime), 3.11+ (compatibilidade)
**Primary Dependencies**: PySide6 ^6.10.0, matplotlib ^3.10.0, qasync ^0.27.1, Pydantic ^2.0
**Storage**: N/A (dados lidos via use cases existentes — sem alterações SQLite)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, headless mocks (MockSignal, MockQBase)
**Target Platform**: Windows desktop (PySide6), mínimo 1366x768
**Project Type**: desktop-app (PySide6 + matplotlib)
**Performance Goals**: Pan/drag responsivo em tempo real (sem atraso perceptível); scroll fluido com 50+ histórias e 5+ features expandidas
**Constraints**: Contraste mínimo WCAG AA (4.5:1); sem dependências novas; escopo puramente Presentation layer
**Scale/Scope**: ~1052 linhas no dialog atual, ~345 linhas no viewmodel; refatoração de UX sem mudanças estruturais

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Nota |
|-----------|--------|------|
| I. Clean Architecture | ✅ PASS | Escopo puramente Presentation — sem imports de Domain/Infrastructure. View usa ViewModel que acessa use cases via DI |
| II. DDD | ✅ N/A | Sem alterações em entidades de domínio |
| III. Repository Pattern | ✅ N/A | Sem alterações em repositórios |
| IV. Dependency Injection | ✅ PASS | RoadmapViewModel recebido via DIContainer; sem dependências criadas internamente |
| V. SQLite | ✅ N/A | Sem alterações de banco de dados |
| VI. Packaging | ✅ PASS | Sem dependências novas; matplotlib já existente |
| VII. Estrutura de Diretórios | ✅ PASS | Alterações em `presentation/views/` e `presentation/viewmodels/` |
| VIII. Async | ✅ PASS | `load_and_render()` já async via qasync; interações de pan são síncronas (correto para eventos de mouse) |
| IX. Simplicidade | ✅ PASS | Pan usa eventos nativos do matplotlib (button_press/release/motion_notify); sem abstrações desnecessárias |
| X. Type Hints | ✅ PASS | Manter type hints em todas as assinaturas novas |
| XI. Docstrings | ✅ PASS | Docstrings em métodos públicos novos |
| XII. isort | ✅ PASS | Executar antes de commit |
| XIII. Nomenclatura | ✅ PASS | snake_case para métodos, UPPER_SNAKE_CASE para constantes |
| XIV. Testes | ✅ PASS | Testes unitários headless para pan state, cursor changes, keyboard nav |
| XV. Idioma | ✅ PASS | Código em inglês, docstrings/tooltips em português |
| XVI. Erros | ✅ N/A | Sem novos cenários de erro (pan é operação visual) |
| XVII. Logging | ✅ N/A | Sem operações logáveis (interações de UI) |
| XVIII. Configuração | ✅ N/A | Sem novos parâmetros configuráveis |
| XIX. UI/UX (MVVM) | ✅ PASS | Pan state gerenciado no View (estado visual local); ViewModel mantém dados |
| XX. Validação | ✅ N/A | Sem entrada de dados do usuário |
| XXI. CI/CD | ✅ PASS | Testes existentes + novos devem passar em CI |

**Gate Result**: ✅ PASS — nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/043-roadmap-ux-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ui-contracts.md  # Contratos de interação UI
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/presentation/
├── viewmodels/
│   └── roadmap_viewmodel.py    # RoadmapData, RoadmapGroup, RoadmapFilters, RoadmapViewModel
├── views/
│   └── roadmap_dialog.py       # RoadmapDialog (toolbar, chart, pan, zoom, filters)
└── theme/
    └── theme.py                # DESIGN_TOKENS, STATUS_PALETTE (read-only)

tests/
├── headless_mocks.py           # MockSignal, MockQBase, create_pyside6_mocks()
└── unit/presentation/
    ├── viewmodels/
    │   └── test_roadmap_viewmodel.py
    └── views/
        └── test_roadmap_dialog.py
```

**Structure Decision**: Alterações confinadas aos arquivos existentes `roadmap_dialog.py` e `roadmap_viewmodel.py`. Sem novos arquivos de código — apenas refinamento dos existentes. Testes expandidos nos arquivos de teste existentes.

## Complexity Tracking

> Nenhuma violação de constituição identificada — tabela não preenchida.
