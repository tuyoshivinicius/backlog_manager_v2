# UI Interaction Contracts: Column Resize

## Interações do Usuário

### 1. Arrastar borda do cabeçalho (resize)

- **Trigger**: Mouse drag na borda direita de qualquer cabeçalho de coluna
- **Cursor**: `Qt.CursorShape.SplitHCursor` (indicador de redimensionamento)
- **Constraint**: Largura mínima 30px (FR-004)
- **Side effect**: Salva estado do header no QSettings automaticamente
- **Coluna "Nome"**: Permanece em modo Stretch, não é redimensionável manualmente

### 2. Duplo-clique na borda do cabeçalho (auto-fit)

- **Trigger**: Double-click na borda direita de um cabeçalho
- **Behavior**: Ajusta largura ao conteúdo visível (`resizeSectionToContents`)
- **Constraint**: Respeita largura mínima de 30px
- **Side effect**: Salva estado do header no QSettings

### 3. Menu de contexto do cabeçalho

- **Trigger**: Right-click em qualquer área do cabeçalho horizontal
- **Items**:
  - "Restaurar larguras padrão" — aplica `COLUMN_WIDTHS` e remove estado salvo
- **Side effect**: Persiste restauração no QSettings (remove chave)

## Persistência (QSettings)

- **Format**: IniFormat
- **Scope**: UserScope
- **Organization**: "BacklogManager"
- **Application**: "Backlog Manager"
- **Group**: "column_widths"
- **Key**: "header_state" → QByteArray (via `saveState()`)

### Save trigger
- Após cada `sectionResized` signal (com debounce implícito do Qt)

### Restore trigger
- Na inicialização, em `_setup_table_columns`, antes de aplicar defaults
- Se `restoreState()` falha ou chave ausente → aplica `COLUMN_WIDTHS` defaults
