# Quickstart: EP-017 Design System e Fundacao Visual

**Date**: 2026-03-27

## Prerequisites

- Python 3.11+
- PySide6 6.10.0+
- Poetry instalado

## Setup

```bash
# Instalar dependencias
poetry install

# Verificar que PySide6 esta instalado
poetry run python -c "from PySide6.QtWidgets import QApplication; print('OK')"
```

## Key Files

| File | Purpose |
|------|---------|
| `src/backlog_manager/presentation/theme/theme.py` | Design tokens e funcao apply_theme() |
| `src/backlog_manager/presentation/theme/stylesheet.qss` | Regras QSS com placeholders @var |
| `src/backlog_manager/presentation/delegates/status_badge_delegate.py` | Delegate para badges de status |
| `src/backlog_manager/presentation/delegates/monospace_delegate.py` | Delegate para IDs monospace |
| `src/backlog_manager/assets/icons/*.svg` | 16 icones Phosphor Icons |

## Usage Examples

### 1. Aplicar Tema no Startup

```python
# src/backlog_manager/presentation/app.py
from pathlib import Path
from PySide6.QtWidgets import QApplication

from backlog_manager.presentation.theme import apply_theme, DESIGN_TOKENS

def main():
    app = QApplication([])

    # Carregar e aplicar stylesheet
    qss_path = Path(__file__).parent / "theme" / "stylesheet.qss"
    qss_template = qss_path.read_text(encoding="utf-8")
    stylesheet = apply_theme(qss_template, DESIGN_TOKENS)
    app.setStyleSheet(stylesheet)

    # ... resto da inicializacao
```

### 2. Usar Delegates na Tabela

```python
# src/backlog_manager/presentation/views/main_window.py
from backlog_manager.presentation.delegates import (
    StatusBadgeDelegate,
    MonospaceDelegate,
)

class MainWindow(QMainWindow):
    def _setup_table(self):
        # Coluna de status com badges
        self._table.setItemDelegateForColumn(
            self.STATUS_COLUMN,
            StatusBadgeDelegate(self._table)
        )

        # Coluna de ID com fonte monospace
        self._table.setItemDelegateForColumn(
            self.ID_COLUMN,
            MonospaceDelegate(self._table)
        )
```

### 3. Usar Icones na Toolbar

```python
# src/backlog_manager/presentation/views/main_window.py
from backlog_manager.presentation.theme import icon_manager

class MainWindow(QMainWindow):
    def _setup_toolbar(self):
        action_new = QAction(
            icon_manager.get("plus"),
            "Nova Historia",
            self
        )
        self._toolbar.addAction(action_new)
```

### 4. Validar Contraste WCAG

```python
# tests/unit/presentation/theme/test_theme.py
from backlog_manager.presentation.theme import (
    STATUS_PALETTE,
    calculate_contrast_ratio,
)

def test_status_colors_meet_wcag_aa():
    for status, config in STATUS_PALETTE.items():
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        assert ratio >= 4.5, f"{status}: {ratio:.2f}:1 < 4.5:1"
```

## Running Tests

```bash
# Testes unitarios do design system
poetry run pytest tests/unit/presentation/theme/ -v

# Testes dos delegates
poetry run pytest tests/unit/presentation/delegates/ -v

# Testes de integracao
poetry run pytest tests/integration/presentation/ -v

# Todos os testes com cobertura
poetry run pytest --cov=src/backlog_manager/presentation
```

## Common Tasks

### Adicionar novo token de cor

1. Adicionar em `theme.py` -> `DESIGN_TOKENS`
2. Usar em `stylesheet.qss` como `@nome-do-token`
3. Rodar testes para validar

### Adicionar novo icone

1. Baixar SVG do Phosphor Icons (16x16, Regular)
2. Salvar em `assets/icons/nome.svg`
3. Adicionar nome em `theme.py` -> `ICON_NAMES`
4. Usar via `icon_manager.get("nome")`

### Modificar cor de status

1. Editar `theme.py` -> `STATUS_PALETTE`
2. Verificar contraste WCAG com `calculate_contrast_ratio()`
3. Rodar teste `test_status_colors_meet_wcag_aa`

## Troubleshooting

### Placeholder nao substituido

**Sintoma**: QSS mostra `@nome` literal em vez de cor.

**Causa**: Token nao existe em `DESIGN_TOKENS`.

**Solucao**: Adicionar token ou corrigir nome no QSS.

### Icone nao carrega

**Sintoma**: QIcon vazio (sem imagem).

**Causa**: Arquivo SVG nao existe ou caminho incorreto.

**Solucao**: Verificar que arquivo existe em `assets/icons/`.

### Focus ring nao aparece

**Sintoma**: Tab entre widgets nao mostra borda de foco.

**Causa**: Widget nao aceita foco ou QSS nao aplicado.

**Solucao**: Verificar `setFocusPolicy()` e que stylesheet foi aplicado.
