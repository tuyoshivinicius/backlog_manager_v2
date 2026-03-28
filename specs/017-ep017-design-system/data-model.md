# Data Model: EP-017 Design System e Fundacao Visual

**Date**: 2026-03-27
**Status**: Draft

## Overview

Este documento descreve as entidades de dados e estruturas usadas pelo design system. Como o epic e focado em UI/Presentation layer, nao ha persistencia em banco de dados - todas as estruturas sao em memoria.

## Entities

### 1. DesignTokens (theme.py)

**Description**: Dicionario contendo todos os tokens de design (cores, fontes, espacamentos).

**Location**: `src/backlog_manager/presentation/theme/theme.py`

**Structure**:
```python
DESIGN_TOKENS: dict[str, str] = {
    # === Primary Colors ===
    "primary": "#0066CC",
    "primary-light": "#E6F0FA",
    "primary-dark": "#004D99",
    "primary-pressed": "#003D7A",

    # === Neutral Colors (Gray Scale) ===
    "neutral-50": "#FAFAFA",
    "neutral-100": "#F5F5F5",
    "neutral-200": "#E5E5E5",
    "neutral-300": "#D4D4D4",
    "neutral-400": "#A3A3A3",
    "neutral-500": "#737373",
    "neutral-600": "#525252",
    "neutral-700": "#404040",
    "neutral-800": "#262626",
    "neutral-900": "#171717",

    # === Semantic Colors ===
    "background": "#FFFFFF",
    "surface": "#FAFAFA",
    "border": "#E5E5E5",
    "text": "#171717",
    "text-secondary": "#525252",
    "text-muted": "#737373",

    # === Status Colors (WCAG AA Validated) ===
    "success-bg": "#DDF3E4",
    "success-fg": "#18794E",
    "warning-bg": "#FEF3C7",
    "warning-fg": "#B45309",
    "error-bg": "#FECACA",
    "error-fg": "#B91C1C",
    "info-bg": "#DBEAFE",
    "info-fg": "#1E40AF",

    # === Typography ===
    "font-family": "Inter, Segoe UI, system-ui, sans-serif",
    "font-family-mono": "JetBrains Mono, Cascadia Code, Consolas, monospace",
    "font-size-xs": "10px",
    "font-size-sm": "12px",
    "font-size-base": "13px",
    "font-size-md": "14px",
    "font-size-lg": "16px",
    "font-size-xl": "18px",
    "font-size-2xl": "24px",
    "font-weight-normal": "400",
    "font-weight-medium": "500",
    "font-weight-bold": "700",

    # === Spacing ===
    "spacing-0": "0px",
    "spacing-1": "4px",
    "spacing-2": "8px",
    "spacing-3": "12px",
    "spacing-4": "16px",
    "spacing-5": "20px",
    "spacing-6": "24px",
    "spacing-8": "32px",

    # === Border Radius ===
    "radius-sm": "2px",
    "radius-md": "4px",
    "radius-lg": "8px",
    "radius-full": "9999px",

    # === Shadows ===
    "shadow-sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
    "shadow-md": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "shadow-lg": "0 10px 15px rgba(0, 0, 0, 0.1)",

    # === Interactive States ===
    "focus-ring": "2px solid #0066CC",
    "hover-opacity": "0.9",
}
```

**Fields Summary**:
| Category | Count | Example |
|----------|-------|---------|
| Primary Colors | 4 | primary, primary-light |
| Neutral Colors | 10 | neutral-50 to neutral-900 |
| Semantic Colors | 6 | background, text, border |
| Status Colors | 8 | success-bg, success-fg |
| Typography | 12 | font-family, font-size-base |
| Spacing | 8 | spacing-0 to spacing-8 |
| Border Radius | 4 | radius-sm to radius-full |
| Shadows | 3 | shadow-sm to shadow-lg |
| Interactive | 2 | focus-ring, hover-opacity |
| **Total** | **57** | |

---

### 2. StatusPalette (theme.py)

**Description**: Mapeamento de status de historia para configuracao visual (simbolo, cores).

**Location**: `src/backlog_manager/presentation/theme/theme.py`

**Structure**:
```python
@dataclass(frozen=True)
class StatusConfig:
    symbol: str      # Simbolo nao-cromatico (acessibilidade)
    background: str  # Cor de fundo (hex)
    foreground: str  # Cor do texto (hex)

STATUS_PALETTE: dict[str, StatusConfig] = {
    "BACKLOG": StatusConfig(
        symbol="●",
        background="#E5E5E5",
        foreground="#525252",
    ),
    "EXECUCAO": StatusConfig(
        symbol="▶",
        background="#DBEAFE",
        foreground="#1E40AF",
    ),
    "TESTES": StatusConfig(
        symbol="◆",
        background="#FEF3C7",
        foreground="#B45309",
    ),
    "CONCLUIDO": StatusConfig(
        symbol="✓",
        background="#DDF3E4",
        foreground="#18794E",
    ),
    "IMPEDIDO": StatusConfig(
        symbol="✕",
        background="#FECACA",
        foreground="#B91C1C",
    ),
}
```

**Validation Rules**:
- Todos os status do enum `StoryStatus` devem ter entrada correspondente
- Contraste background/foreground deve ser >= 4.5:1 (WCAG AA)
- Simbolos devem ser caracteres Unicode validos

---

### 3. IconRegistry

**Description**: Registro de icones SVG pre-carregados.

**Location**: `src/backlog_manager/presentation/theme/theme.py`

**Structure**:
```python
ICON_NAMES: list[str] = [
    "plus",
    "pencil-simple",
    "trash",
    "arrow-up",
    "arrow-down",
    "users",
    "package",
    "gear",
    "calendar-check",
    "shuffle",
    "download-simple",
    "upload-simple",
    "copy",
    "warning-triangle",
    "link",
    "x",
]

class IconManager:
    def __init__(self, icons_dir: Path) -> None:
        self._icons: dict[str, QIcon] = {}
        self._load_all(icons_dir)

    def get(self, name: str) -> QIcon:
        return self._icons.get(name, QIcon())
```

**Validation Rules**:
- Todos os 16 icones devem existir em `assets/icons/`
- Cada icone deve carregar sem erro via `QIcon(path)`
- Icones devem renderizar em 16x16px sem distorcao

---

## Relationships

```
+------------------+       uses        +------------------+
|  stylesheet.qss  | <---------------- |   apply_theme()  |
+------------------+                   +------------------+
        |                                      |
        | @var placeholders                    | substitutes with
        v                                      v
+------------------+                   +------------------+
|  DESIGN_TOKENS   |                   |  STATUS_PALETTE  |
+------------------+                   +------------------+
                                               |
                                               | used by
                                               v
                                      +---------------------+
                                      | StatusBadgeDelegate |
                                      +---------------------+
```

## State Transitions

**N/A** - Design system nao possui estados mutaveis. Todos os tokens sao constantes.

## Validation Rules Summary

| Entity | Rule | Consequence |
|--------|------|-------------|
| DESIGN_TOKENS | Todas as keys devem comecar com prefixo valido | ValueError em testes |
| STATUS_PALETTE | Contraste >= 4.5:1 | Teste WCAG falha |
| STATUS_PALETTE | Todas as keys do StoryStatus enum | KeyError em runtime |
| IconManager | Todos os 16 icones existem | FileNotFoundError |
| stylesheet.qss | Zero valores hex literais | Teste de validacao falha |
| stylesheet.qss | Todos os @var tem correspondencia em DESIGN_TOKENS | MissingTokenError |
