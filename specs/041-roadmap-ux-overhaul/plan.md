# Implementation Plan: Roadmap UX Overhaul

**Branch**: `041-roadmap-ux-overhaul` | **Date**: 2026-04-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/041-roadmap-ux-overhaul/spec.md`

## Summary

Reformulacao completa da UX do roadmap existente (RoadmapDialog + RoadmapViewModel) para resolver 11 problemas criticos de usabilidade: codificacao por cor de status, colapso/expansao de grupos por wave, linha de "hoje", correcao de rotulos, filtragem/busca, tooltips enriquecidos com dependencias, toolbar com icones, progresso visual nas barras, scroll sincronizado e rodape estatistico. A implementacao modifica exclusivamente a camada Presentation (View + ViewModel), reutilizando os use cases existentes (ListStoriesUseCase, ListFeaturesUseCase) e o design system (STATUS_PALETTE, WAVE_PALETTE). Renderizacao via matplotlib ja existente e estendida com novos recursos visuais.

## Technical Context

**Language/Version**: Python 3.13+ (runtime), 3.11+ (compatibilidade)
**Primary Dependencies**: PySide6 ^6.10.0, matplotlib ^3.10.0, qasync ^0.27.1, Pydantic ^2.0
**Storage**: N/A (dados lidos via use cases existentes — sem alteracoes SQLite)
**Testing**: pytest ^8.0, pytest-asyncio ^0.23, pytest-cov ^4.0, headless mocks (create_pyside6_mocks)
**Target Platform**: Desktop Windows/Linux (PySide6)
**Project Type**: desktop-app (biblioteca Python instalavel com GUI PySide6)
**Performance Goals**: Renderizacao de 200+ historias em <3s; colapso/expansao em <500ms; busca em <5s
**Constraints**: Somente camada Presentation; sem novos use cases; sem alteracoes de schema SQLite
**Scale/Scope**: ~190+ historias, agrupadas por waves, com dependencias diretas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Alteracoes restritas a Presentation (View + ViewModel). Dados via use cases existentes. Sem importacoes cruzadas. |
| II. DDD | ✅ PASS | Sem alteracoes no dominio. Entidades e value objects inalterados. |
| III. Repository Pattern | ✅ PASS | Sem novos repositorios. Dados acessados via use cases existentes. |
| IV. Dependency Injection | ✅ PASS | ViewModel recebe DIContainer via construtor. Dialog recebe ViewModel. |
| V. SQLite | ✅ PASS | Sem alteracoes de schema ou queries. |
| VI. Packaging | ✅ PASS | Sem novas dependencias. matplotlib ja presente. |
| VII. Estrutura de Diretorios | ✅ PASS | Arquivos em presentation/views/ e presentation/viewmodels/. Testes em tests/unit/presentation/. |
| VIII. Async | ✅ PASS | load_data() ja e async. Novos metodos de filtragem sao sincronos (operam sobre cache). |
| IX. Simplicidade | ✅ PASS | Funcoes focadas (<=30 linhas), sem abstrações especulativas. |
| X. Type Hints | ✅ PASS | Todos os metodos com type hints completos. |
| XI. Docstrings | ✅ PASS | Classes e metodos publicos com docstrings Google style. |
| XII. Imports (isort) | ✅ PASS | Imports organizados conforme padrao. |
| XIII. Nomenclatura | ✅ PASS | PascalCase para classes, snake_case para metodos/variaveis. |
| XIV. Testes | ✅ PASS | Testes unitarios headless para ViewModel (80%+) e View (50%+). |
| XV. Idioma | ✅ PASS | Codigo em ingles, docs em portugues, logs em portugues. |
| XVI. Erros | ✅ PASS | Sem novas excecoes. Erros tratados na camada de apresentacao. |
| XVII. Logging | ✅ PASS | Logger existente reutilizado para eventos de debug. |
| XVIII. Configuracao | ✅ PASS | Sem novos parametros de configuracao. |
| XIX. UI/UX (MVVM) | ✅ PASS | View contem apenas UI; logica de filtragem/agrupamento no ViewModel. |
| XX. Validacao | ✅ PASS | Filtros operam sobre dados ja validados pelos use cases. |
| XXI. CI/CD | ✅ PASS | Testes, mypy, black, isort validados no pipeline existente. |

**Gate Result**: ✅ ALL PASS — nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/041-roadmap-ux-overhaul/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI contracts)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/presentation/
├── viewmodels/
│   └── roadmap_viewmodel.py     # MODIFY: adicionar filtragem, agrupamento por wave, estado colapso
├── views/
│   └── roadmap_dialog.py        # MODIFY: refatorar rendering com cores, colapso, filtros, tooltips, dependencias
└── theme/
    └── theme.py                 # READ-ONLY: reutilizar STATUS_PALETTE, WAVE_PALETTE

tests/unit/presentation/
├── viewmodels/
│   └── test_roadmap_viewmodel.py  # MODIFY: testes para novos metodos de filtragem/agrupamento
└── views/
    └── test_roadmap_dialog.py     # MODIFY: testes para novos widgets e rendering
```

**Structure Decision**: Modificacao dos 2 arquivos existentes (roadmap_viewmodel.py, roadmap_dialog.py) + seus testes. Sem novos arquivos de producao. Sem alteracoes em outras camadas.

## Complexity Tracking

> Nenhuma violacao identificada — secao vazia.
