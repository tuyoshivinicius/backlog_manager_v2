# Quickstart: Column Resize

**Feature Branch**: `027-column-resize`
**Date**: 2026-03-31

## Resumo

Permitir que o usuário redimensione colunas da tabela do backlog arrastando bordas dos cabeçalhos, com persistência via QSettings e restauração para padrão via menu de contexto.

## Pré-requisitos

- Python 3.11+
- PySide6 ^6.10.0
- Dependências do projeto instaladas (`poetry install`)

## Arquivos Impactados

| Arquivo | Tipo de Mudança |
|---------|----------------|
| `src/backlog_manager/presentation/views/main_window.py` | Modificar: trocar `Fixed` por `Interactive`, adicionar save/restore de estado, menu de contexto, handler duplo-clique |
| `src/backlog_manager/presentation/viewmodels/story_table_model.py` | Modificar: adicionar constante `MINIMUM_COLUMN_WIDTH` |
| `tests/unit/presentation/test_column_resize.py` | Criar: testes unitários para lógica de redimensionamento |

## Mudanças por Camada

### Presentation (única camada afetada)

1. **`StoryTableView`** (`main_window.py`):
   - Conectar `sectionResized` signal para auto-save
   - Conectar `sectionDoubleClicked` para auto-fit
   - Adicionar context menu no header com "Restaurar larguras padrão"

2. **`MainWindow._setup_table_columns`** (`main_window.py`):
   - Trocar `ResizeMode.Fixed` por `ResizeMode.Interactive`
   - Definir `setMinimumSectionSize(30)`
   - Tentar `restoreState()` do QSettings antes de aplicar defaults
   - Conectar `sectionResized` → `_save_column_widths()`

3. **`StoryTableModel`** (`story_table_model.py`):
   - Adicionar `MINIMUM_COLUMN_WIDTH = 30`

## Fluxo de Implementação

```
1. Trocar Fixed → Interactive (habilita arraste)
2. Adicionar minimumSectionSize (FR-004)
3. Implementar save/restore via QSettings (FR-005, FR-006)
4. Implementar duplo-clique auto-fit (FR-008)
5. Implementar menu de contexto "Restaurar padrão" (FR-007)
6. Testes
```

## Como Testar Manualmente

1. `poetry run backlog-manager` — abrir o aplicativo
2. Arrastar borda direita de qualquer cabeçalho → coluna redimensiona
3. Fechar e reabrir → larguras preservadas
4. Duplo-clique na borda → auto-fit ao conteúdo
5. Clique direito no cabeçalho → "Restaurar larguras padrão" → volta ao original
