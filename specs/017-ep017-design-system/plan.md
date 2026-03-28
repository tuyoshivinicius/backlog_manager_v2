# Implementation Plan: EP-017 Design System e Fundacao Visual

**Branch**: `017-ep017-design-system` | **Date**: 2026-03-27 | **Spec**: `specs/017-ep017-design-system/spec.md`
**Input**: Feature specification from `/specs/017-ep017-design-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar um design system centralizado para o Backlog Manager com tokens de design (cores, fontes, espacamentos) em theme.py, stylesheet QSS com placeholders, StatusBadgeDelegate e MonospaceDelegate para renderizacao customizada na tabela, biblioteca de 16 icones SVG Phosphor Icons, e focus rings para acessibilidade. O sistema deve garantir contraste WCAG AA (4.5:1) e zero valores hardcoded fora de theme.py.

## Technical Context

**Language/Version**: Python 3.11+ (pyproject.toml especifica >=3.11,<3.15)
**Primary Dependencies**: PySide6 ^6.10.0 (GUI), qasync ^0.27.1 (async integration)
**Storage**: N/A (este epic nao envolve persistencia)
**Testing**: pytest ^8.0, pytest-qt ^4.4, pytest-asyncio ^0.23
**Target Platform**: Desktop Windows (com suporte a diferentes escalas DPI: 100%, 125%, 150%)
**Project Type**: Desktop application (PySide6/Qt)
**Performance Goals**: Delegates devem renderizar em <= 16ms por celula para 60fps (NFR-DS-003)
**Constraints**: Contraste minimo 4.5:1 WCAG AA (NFR-DS-001), latencia resposta <= 100ms (RNF-PERF-002)
**Scale/Scope**: 15+ tipos de widget estilizados, 30+ tokens de cor, 16 icones SVG, 5 status de historia

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Observacao |
|-----------|--------|------------|
| I. Clean Architecture | PASS | Design system fica em Presentation layer. theme.py e stylesheet.qss ficam em presentation/theme/. Delegates ficam em presentation/delegates/. Nenhuma dependencia de Domain/Application/Infrastructure. |
| VII. Estrutura de Diretorios | PASS | Nova estrutura: presentation/theme/ (theme.py, stylesheet.qss), presentation/delegates/ (status_badge_delegate.py, monospace_delegate.py), assets/icons/ (16 SVGs). Segue src layout. |
| IX. Simplicidade e Legibilidade | PASS | Solucao simples: tokens em dicionario Python, QSS com placeholders, delegates nativos do Qt. Nada de metaprogramacao ou abstracoes excessivas. |
| X. Type Hints Obrigatorios | PASS | Todos os modulos terao type hints completos. |
| XI. Docstrings em Codigo Publico | PASS | Classes e funcoes publicas terao docstrings Google style. |
| XIV. Estrategia de Testes | PASS | Testes unitarios para apply_theme(), validacao de contraste, delegates. Testes de integracao para stylesheet loading. |
| XIX. Padroes de UI/UX (PySide6) | PASS | Delegates usam QStyledItemDelegate. Stylesheet aplicado via app.setStyleSheet(). Contraste WCAG AA. Navegacao por teclado com focus rings. |
| NFR-MANT-001 (Zero Hardcoded) | PASS | Todos os valores de cor/fonte/espacamento centralizados em theme.py. Validacao via grep para garantir ausencia de valores hardcoded. |

**Gate Result**: PASS - Todos os principios atendidos. Pode prosseguir para Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/017-ep017-design-system/
├── plan.md              # Este arquivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (nao aplicavel - sem contratos externos)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── presentation/
│   ├── theme/                    # NOVO - Design system
│   │   ├── __init__.py
│   │   ├── theme.py              # 30+ tokens de cor, fontes, espacamentos
│   │   └── stylesheet.qss        # Regras QSS com placeholders @var
│   ├── delegates/                # NOVO - Custom delegates
│   │   ├── __init__.py
│   │   ├── status_badge_delegate.py   # Badges pill para status
│   │   └── monospace_delegate.py      # IDs em fonte monospace
│   ├── views/
│   │   └── main_window.py        # MODIFICADO - integrar delegates
│   ├── viewmodels/
│   │   └── story_table_model.py  # MODIFICADO - usar delegates
│   └── app.py                    # MODIFICADO - aplicar tema no startup
│
└── assets/                       # NOVO - Assets estaticos
    └── icons/                    # 16 SVGs Phosphor Icons
        ├── plus.svg
        ├── pencil-simple.svg
        ├── trash.svg
        ├── arrow-up.svg
        ├── arrow-down.svg
        ├── users.svg
        ├── package.svg
        ├── gear.svg
        ├── calendar-check.svg
        ├── shuffle.svg
        ├── download-simple.svg
        ├── upload-simple.svg
        ├── copy.svg
        ├── warning-triangle.svg
        ├── link.svg
        └── x.svg

tests/
├── unit/
│   └── presentation/
│       ├── theme/                # NOVO
│       │   └── test_theme.py     # Testes de apply_theme, contraste
│       └── delegates/            # NOVO
│           ├── test_status_badge_delegate.py
│           └── test_monospace_delegate.py
└── integration/
    └── presentation/
        └── test_theme_integration.py  # NOVO - teste de carregamento QSS
```

**Structure Decision**: Segue Clean Architecture existente. Design system isolado em presentation/theme/. Delegates isolados em presentation/delegates/. Assets em src/backlog_manager/assets/icons/ para serem empacotados com o pacote Python.

## Complexity Tracking

> Nenhuma violacao de principios identificada. Implementacao segue padroes existentes.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Constitution Check (Post-Design)

*Re-evaluated after Phase 1 design completion.*

| Principio | Status | Post-Design Observacao |
|-----------|--------|------------------------|
| I. Clean Architecture | PASS | Confirmado: theme/, delegates/, assets/ todos em Presentation. StatusConfig dataclass nao tem dependencias externas. |
| VII. Estrutura de Diretorios | PASS | Confirmado: Estrutura proposta segue src layout. Testes em tests/unit/presentation/ e tests/integration/presentation/. |
| IX. Simplicidade e Legibilidade | PASS | Confirmado: apply_theme() e funcao simples de substituicao. StatusConfig e dataclass frozen. IconManager usa dicionario simples. |
| X. Type Hints Obrigatorios | PASS | Confirmado: data-model.md define todos os tipos (dict[str, str], StatusConfig dataclass, dict[str, QIcon]). |
| XI. Docstrings em Codigo Publico | PASS | Confirmado: quickstart.md documenta uso. Funcoes publicas terao docstrings. |
| XIV. Estrategia de Testes | PASS | Confirmado: Testes unitarios para apply_theme(), calculate_contrast_ratio(), StatusBadgeDelegate.paint(). Teste de integracao para carregamento de stylesheet. |
| XIX. Padroes de UI/UX (PySide6) | PASS | Confirmado: QStyledItemDelegate usado. Focus rings via :focus em QSS. Contraste WCAG AA validado em data-model.md. |
| NFR-MANT-001 (Zero Hardcoded) | PASS | Confirmado: data-model.md define validacao "Zero valores hex literais em stylesheet.qss". |

**Post-Design Gate Result**: PASS - Design completo e conforme com todos os principios da constituicao.
