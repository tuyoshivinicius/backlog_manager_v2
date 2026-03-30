# UI Contract: Table Selection Highlight

**Feature**: 025-table-selection-highlight
**Date**: 2026-03-30

## Selection Visual Contract

### Estados Visuais da Linha

| Estado | Background | Foreground | Borda Esquerda | Descrição |
|---|---|---|---|---|
| Normal | `transparent` / wave tint | `neutral-900` | Nenhuma | Estado padrão da linha |
| Hover | `#F5F5F5` (neutral-100) | `neutral-900` | Nenhuma | Mouse sobre a linha |
| Selected | `#E6F0FA` (primary-light) | `neutral-900` | `3px solid #0066CC` | Linha selecionada |
| Selected + Hover | `#D6E8F7` | `neutral-900` | `3px solid #0066CC` | Mouse sobre linha selecionada |

### Prioridade de Estados

1. Selected + Hover (mais alta)
2. Selected
3. Hover
4. Wave tint (background por onda)
5. Normal (mais baixa)

**Nota**: Quando uma linha está selecionada, o wave tint é substituído pelo selection background. O wave tint retorna quando a linha é desselecionada.

## Selection Behavior Contract

### Ações e Efeitos na Seleção

| Ação do Usuário | Efeito na Seleção | Story ID no ViewModel |
|---|---|---|
| Click em linha | Seleciona a linha clicada | Atualizado para story_id da linha |
| Click em outra linha | Move seleção para nova linha | Atualizado para novo story_id |
| Move Up (Alt+↑) | Seleção segue a história para nova posição | Mantido (mesmo story_id) |
| Move Down (Alt+↓) | Seleção segue a história para nova posição | Mantido (mesmo story_id) |
| Edit (dialog) | Seleção preservada após fechar dialog | Mantido (mesmo story_id) |
| Delete | Seleção move para linha adjacente | Atualizado para story_id adjacente |
| Delete (última história) | Seleção limpa | Definido como None |
| Filtro exclui história | Seleção limpa | Definido como None |
| Tabela vazia | Sem seleção | None |

### Estado dos Botões de Ação

| Estado de Seleção | Edit | Delete | Move Up | Move Down |
|---|---|---|---|---|
| Nenhuma seleção | Desabilitado | Desabilitado | Desabilitado | Desabilitado |
| Primeira linha | Habilitado | Habilitado | Desabilitado | Habilitado |
| Linha intermediária | Habilitado | Habilitado | Habilitado | Habilitado |
| Última linha | Habilitado | Habilitado | Habilitado | Desabilitado |
| Única linha na tabela | Habilitado | Habilitado | Desabilitado | Desabilitado |

## Signal Contract

### Sinais Existentes (sem alteração de assinatura)

| Signal | Emissor | Payload | Quando |
|---|---|---|---|
| `story_selected(str)` | `MainWindowViewModel` | `story_id: str` | Após seleção mudar |
| `stories_changed()` | `MainWindowViewModel` | — | Após refresh da lista |
| `currentRowChanged(QModelIndex, QModelIndex)` | `QItemSelectionModel` | current, previous | Qt nativo |

### Fluxo de Restauração de Seleção

```
User action (move/edit/delete)
  → ViewModel executa use case
  → ViewModel chama load_stories()
  → stories_changed signal emitido
  → View recebe signal
  → View busca story_id no modelo (via UserRole)
  → View chama setCurrentIndex() no novo índice
  → QItemSelectionModel atualiza highlight visual
```
