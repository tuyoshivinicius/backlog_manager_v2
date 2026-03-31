# Implementation Plan: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Branch**: `029-velocity-sprint-datepicker` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/029-velocity-sprint-datepicker/spec.md`

## Summary

Alterar a unidade de medida de velocidade na configuracao de alocacao de SP/dia para SP/Sprint, adicionando campo de dias uteis por sprint. A conversao SP/Sprint → SP/dia ocorre na camada de apresentacao (ViewModel), mantendo o dominio inalterado. Adicionalmente, criar componente DatePicker reutilizavel para substituir QDateEdit inline existentes.

## Technical Context

**Language/Version**: Python 3.11+ (PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0)
**Primary Dependencies**: PySide6 (QDialog, QSpinBox, QDateEdit, QCalendarWidget), QSettings (INI format)
**Storage**: QSettings (INI format) para preferencias de UI; sem alteracoes SQLite
**Testing**: pytest + pytest-qt (testes de GUI com qtbot)
**Target Platform**: Windows 11 (desktop app PySide6)
**Project Type**: desktop-app (Clean Architecture, MVVM)
**Performance Goals**: Resposta de UI <= 100ms (RNF-PERF-002)
**Constraints**: Nenhuma alteracao na camada de dominio ou aplicacao; conversao SP/Sprint → SP/dia e responsabilidade exclusiva da Presentation layer
**Scale/Scope**: 3 views afetadas (ConfigDialog, ConfigPanel, ManualAllocationDialog), 1 viewmodel, 1 novo componente

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Todas as alteracoes ficam na Presentation layer. Dominio (AllocationConfig, SchedulingService) continua recebendo velocity_per_day (float). Nenhuma dependencia de fora para dentro violada. |
| II. DDD | ✅ PASS | Nenhuma entidade de dominio e alterada. SP/Sprint e conceito de UX, nao de dominio. |
| III. Repository Pattern | ✅ N/A | Nenhum repositorio envolvido (apenas QSettings). |
| IV. Dependency Injection | ✅ PASS | DatePicker recebe config via construtor. ConfigDialogViewModel continua injetado via DIContainer. |
| V. SQLite | ✅ N/A | Sem alteracoes de banco. |
| VII. Estrutura Diretorios | ✅ PASS | Novo componente em `presentation/views/`, seguindo padrao existente. |
| VIII. Async | ✅ N/A | Nenhuma operacao I/O envolvida (QSettings e sincrono). |
| IX. Simplicidade | ✅ PASS | DatePicker extrai duplicacao de 3 views. Conversao SP/Sprint→SP/dia e uma divisao simples. |
| X. Type Hints | ✅ PASS | Type hints em todas as assinaturas. |
| XIV. Testes | ✅ PASS | Testes unitarios para ViewModel (validacao, conversao, persistencia). Testes pytest-qt para DatePicker. |
| XV. Idioma | ✅ PASS | Codigo em ingles, labels/tooltips em portugues. |
| XVIII. Gestao Config | ✅ PASS | Novos campos (sp_per_sprint, workdays_per_sprint) persistidos via QSettings no grupo "allocation". |
| XIX. UI/UX MVVM | ✅ PASS | Logica de conversao e validacao no ViewModel. View apenas renderiza e captura eventos. |
| XX. Validacao Entrada | ✅ PASS | Validacao na Presentation (ViewModel): SP/Sprint >= 1, workdays >= 1 (evita divisao por zero). |

**Gate Result**: PASS — nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/029-velocity-sprint-datepicker/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ui-contracts.md  # DatePicker and velocity config UI contracts
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── presentation/
│   ├── views/
│   │   ├── date_picker.py           # NOVO: Componente DatePicker reutilizavel
│   │   ├── config_dialog.py         # MODIFICADO: SP/Sprint + workdays + DatePicker
│   │   ├── config_panel.py          # MODIFICADO: SP/Sprint + workdays + DatePicker
│   │   └── manual_allocation_dialog.py  # MODIFICADO: Usa DatePicker
│   └── viewmodels/
│       └── config_dialog_viewmodel.py   # MODIFICADO: sp_per_sprint, workdays_per_sprint, conversao

tests/
├── unit/
│   └── presentation/
│       └── viewmodels/
│           └── test_config_dialog_viewmodel.py  # MODIFICADO: Novos testes
└── integration/
    └── presentation/
        └── views/
            └── test_date_picker.py              # NOVO: Testes pytest-qt
```

**Structure Decision**: Single project, src layout existente. Novo componente `date_picker.py` em `presentation/views/` seguindo o padrao de componentes reutilizaveis.

## Complexity Tracking

Nenhuma violacao a justificar.
