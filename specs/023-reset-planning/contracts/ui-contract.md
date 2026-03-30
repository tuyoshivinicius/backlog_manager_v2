# UI Contract: EP-023 — Novo Planejamento

## Action: Novo Planejamento

| Property | Value |
|----------|-------|
| Label | "Novo Planejamento" |
| Icon | arrows-down-up.svg |
| Shortcut | Ctrl+Shift+N |
| Tooltip | "Limpar dados de planejamento e recomecar do zero (Ctrl+Shift+N)" |
| Menu | Ferramentas (before "Calcular Cronograma") |
| Toolbar | Group 4 (before "Calcular Cronograma") |

### Enabled State

| Condition | Enabled |
|-----------|---------|
| No stories loaded | NO |
| Operation in progress (schedule/allocation/reset) | NO |
| No stories with planning data | NO |
| Stories with planning data exist | YES |

## Dialog: Confirmacao de Reset

| Property | Value |
|----------|-------|
| Type | Modal QDialog |
| Title | "Novo Planejamento" |
| Icon | warning-triangle.svg (32x32) |
| Main text | "Deseja limpar todos os dados de planejamento?" |
| Detail line 1 | "{N} historias terao datas e duracoes removidas" |
| Detail line 2 | "{M} historias terao desenvolvedores desalocados" |
| Warning | "Esta acao nao pode ser desfeita." |
| Cancel button | "Cancelar" (default focus) |
| Confirm button | "Confirmar" (destructive/error color) |
| Escape key | Closes dialog (reject) |

## Status Bar Feedback

| Event | Status Bar Behavior |
|-------|---------------------|
| Reset completed | Show "Planejamento resetado: {N} historias" for 5 seconds |
| Reset completed | Clear "Ultima alocacao: ..." text |
| Reset completed | Update SP breakdown |
| After 5 seconds | Restore normal stats display |

## ViewModel Signals

| Signal | Payload | When |
|--------|---------|------|
| reset_started | — | Before execution begins |
| reset_completed | ResetPlanningOutputDTO | After successful reset |
| reset_error | str (error message) | On exception during reset |
