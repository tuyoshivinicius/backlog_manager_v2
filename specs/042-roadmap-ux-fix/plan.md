# Implementation Plan: Correção de Problemas de Interface do Roadmap

**Branch**: `042-roadmap-ux-fix` | **Date**: 2026-04-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/042-roadmap-ux-fix/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Correção de 17 problemas críticos de usabilidade no módulo de visualização de roadmap (timeline Gantt). O módulo já existe (`roadmap_dialog.py` + `roadmap_viewmodel.py`) usando matplotlib embarcado em PySide6. As correções abrangem: cores de status nas barras (P1), expand/collapse funcional (P1), controles de janela (P1), eixo temporal adaptativo (P2), controles de zoom melhorados (P2), legenda padronizada (P2), rótulos de wave enriquecidos (P2), consistência visual (P2), linha "hoje" destacada (P2), dropdown fantasma (P3), escala adaptativa à distribuição (P3), setas de dependência (P3), barra de status enriquecida (P3), navegação para alto volume (P3), Wave 7 ausente (P3). Abordagem técnica: refatoração incremental dos arquivos existentes na camada Presentation, sem alterações em Domain/Application/Infrastructure.

## Technical Context

**Language/Version**: Python 3.13+ (runtime), 3.11+ (compatibilidade)
**Primary Dependencies**: PySide6 ^6.10.0, matplotlib ^3.10.0, qasync ^0.27.1, Pydantic ^2.0
**Storage**: N/A (dados lidos via use cases existentes — sem alterações SQLite)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, headless mocks (sem pytest-qt necessário)
**Target Platform**: Windows desktop (resolução mínima 1366x768)
**Project Type**: desktop-app (PySide6 + matplotlib Gantt chart)
**Performance Goals**: Renderização completa ≤ 2s com 190 histórias (FR-035)
**Constraints**: Latência de resposta ≤ 100ms para interações de UI; WCAG AA contraste 4.5:1
**Scale/Scope**: ~190 histórias, ~10 waves, módulo de visualização Gantt

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Escopo 100% Presentation layer — sem alterações em Domain/Application/Infrastructure. Views importam apenas de viewmodels e DTOs. |
| II. DDD | ✅ PASS | Sem alterações em entidades ou value objects de domínio. |
| III. Repository Pattern | ✅ PASS | Sem novos repositórios — dados fornecidos por use cases existentes. |
| IV. Dependency Injection | ✅ PASS | RoadmapViewModel já é injetado via DIContainer. Sem novas dependências entre camadas. |
| V. SQLite | ✅ PASS | Sem alterações de schema ou queries. |
| VI. Packaging | ✅ PASS | matplotlib já é dependência declarada (spec 040/041). Sem novas dependências. |
| VII. Estrutura de Diretórios | ✅ PASS | Arquivos já existem em `presentation/views/` e `presentation/viewmodels/`. |
| VIII. Async | ✅ PASS | `load_and_render()` já é async. Interações de UI permanecem síncronas via matplotlib event handlers. |
| IX. Simplicidade | ✅ PASS | Correções incrementais em código existente, sem abstrações especulativas. |
| X. Type Hints | ✅ PASS | Código novo seguirá type hints obrigatórios. |
| XI. Docstrings | ✅ PASS | Métodos públicos novos/modificados terão docstrings Google style. |
| XII. Imports (isort) | ✅ PASS | Imports organizados conforme convenção. |
| XIII. Nomenclatura | ✅ PASS | snake_case para funções/variáveis, PascalCase para classes, UPPER_SNAKE_CASE para constantes. |
| XIV. Testes | ✅ PASS | Testes headless existentes serão expandidos. Meta: 50%+ para views, 80%+ para viewmodel. |
| XV. Idioma | ✅ PASS | Código em inglês, docstrings/mensagens em português. |
| XVI. Tratamento de Erros | ✅ PASS | Sem novas exceções necessárias — erros de renderização tratados na camada de apresentação. |
| XVII. Logging | ✅ PASS | Logs de debug existentes mantidos. |
| XVIII. Configuração | ✅ PASS | Sem novos parâmetros de configuração persistidos. QSettings para preferências de UI se necessário. |
| XIX. UI/UX (MVVM) | ✅ PASS | Mantém separação View/ViewModel existente. Lógica de apresentação no ViewModel, renderização na View. |
| XX. Validação | ✅ PASS | Sem entrada do usuário nova (filtros já existem). |
| XXI. CI/CD | ✅ PASS | Testes devem passar no pipeline existente. |

**GATE RESULT: ✅ ALL PASS — nenhuma violação identificada.**

## Project Structure

### Documentation (this feature)

```text
specs/042-roadmap-ux-fix/
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
│   ├── viewmodels/
│   │   └── roadmap_viewmodel.py    # Lógica de apresentação (filtros, agrupamento, dados)
│   ├── views/
│   │   └── roadmap_dialog.py       # Diálogo Gantt (matplotlib canvas, toolbar, eventos)
│   └── theme/
│       ├── theme.py                # STATUS_PALETTE, DESIGN_TOKENS, calculate_contrast_ratio
│       └── stylesheet.qss          # Stylesheet global da aplicação

tests/
├── headless_mocks.py                                    # Mock infrastructure (MockSignal, MockQBase, etc.)
└── unit/presentation/
    ├── viewmodels/test_roadmap_viewmodel.py             # Testes do ViewModel
    └── views/test_roadmap_dialog.py                     # Testes headless do Dialog
```

**Structure Decision**: Refatoração de arquivos existentes — sem criação de novos módulos de código de produção. Os arquivos `roadmap_dialog.py` e `roadmap_viewmodel.py` já existem e serão modificados in-place. Os arquivos de teste correspondentes já existem e serão expandidos.

## Complexity Tracking

> Nenhuma violação identificada — seção vazia conforme esperado.
