# Data Model: Table Selection Highlight

**Feature**: 025-table-selection-highlight
**Date**: 2026-03-30

## Overview

Esta feature não introduz novas entidades de domínio nem altera o schema de banco de dados. O "modelo de dados" relevante são os estados de UI e tokens de design system.

## UI State Model

### SelectionState (conceitual — vive no ViewModel e View)

| Propriedade | Tipo | Localização | Descrição |
|---|---|---|---|
| `selected_story_id` | `str \| None` | `MainWindowViewModel` | ID da história selecionada (já existe) |
| `selected_story` | `StoryOutputDTO \| None` | `MainWindowViewModel` | DTO completo da história selecionada (já existe) |
| `current_selection_index` | `QModelIndex` | `QTableView.selectionModel()` | Índice da linha selecionada no modelo visual (gerenciado pelo Qt) |

### Transições de Estado

```
[Nenhuma seleção] --click row--> [Linha selecionada]
[Linha selecionada] --click outra row--> [Nova linha selecionada]
[Linha selecionada] --move up/down--> [Mesma história, nova posição] (restauração automática)
[Linha selecionada] --delete--> [Linha adjacente selecionada] ou [Nenhuma seleção] (se tabela vazia)
[Linha selecionada] --filtro exclui--> [Nenhuma seleção]
[Linha selecionada] --edit dialog--> [Mesma linha selecionada] (preservada após refresh)
```

## Design Tokens (novos)

Tokens a adicionar em `DESIGN_TOKENS` (theme.py):

| Token | Valor | Uso |
|---|---|---|
| `selection-bg` | `#E6F0FA` (= primary-light) | Background da linha selecionada |
| `selection-fg` | `#171717` (= neutral-900) | Foreground do texto na linha selecionada |
| `selection-border` | `#0066CC` (= primary) | Borda lateral esquerda da linha selecionada |
| `hover-bg` | `#F5F5F5` (= neutral-100) | Background da linha em hover |

### Validação de Contraste (WCAG AA)

| Combinação | Ratio | Resultado |
|---|---|---|
| selection-fg (#171717) sobre selection-bg (#E6F0FA) | ~15.5:1 | ✅ AAA |
| selection-fg (#171717) sobre hover-bg (#F5F5F5) | ~17.4:1 | ✅ AAA |
| Status badge foregrounds sobre selection-bg | Mínimo ~3.8:1 (BACKLOG #525252) | ✅ AA (badges mantêm cores próprias) |

## Entidades Existentes (sem alteração)

- `Story` (domain entity) — sem mudanças
- `StoryOutputDTO` (application DTO) — sem mudanças
- `StoryTableModel` (presentation model) — possível adição de role para seleção, ou uso do QSS nativo
- `FilterProxyModel` (presentation proxy) — sem mudanças
