# Data Model: Column Resize

**Feature Branch**: `027-column-resize`
**Date**: 2026-03-31

## Escopo

Esta feature é **puramente Presentation layer**. Não há entidades de domínio, value objects ou tabelas SQLite envolvidas. A persistência usa QSettings (INI format), que é um mecanismo de UI preferences, não de dados de negócio.

## Estado Persistido (QSettings)

### Grupo: `column_widths`

| Chave | Tipo | Descrição |
|-------|------|-----------|
| `header_state` | QByteArray | Estado serializado do QHeaderView (inclui larguras, ordem e modos de resize) |

### Valores Padrão (constantes existentes)

Definidos em `StoryTableModel.COLUMN_WIDTHS` (`story_table_model.py:44-78`):

| Índice | Coluna | Largura Padrão (px) | Modo |
|--------|--------|---------------------|------|
| 0 | Prioridade | 60 | Interactive |
| 1 | Feature | 120 | Interactive |
| 2 | Onda | 50 | Interactive |
| 3 | ID | 100 | Interactive |
| 4 | Componente | 80 | Interactive |
| 5 | Nome | -1 (stretch) | Stretch |
| 6 | Status | 100 | Interactive |
| 7 | Desenvolvedor | 100 | Interactive |
| 8 | Dependencias | 120 | Interactive |
| 9 | SP | 40 | Interactive |
| 10 | Inicio | 90 | Interactive |
| 11 | Fim | 90 | Interactive |
| 12 | Duracao | 60 | Interactive |

### Constantes Novas

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `MINIMUM_COLUMN_WIDTH` | 30 | Largura mínima em pixels (FR-004) |
| `QSETTINGS_GROUP` | `"column_widths"` | Grupo QSettings para estado do header |
| `QSETTINGS_KEY` | `"header_state"` | Chave para o QByteArray serializado |

## Transições de Estado

```
[Primeira execução] → Larguras padrão (COLUMN_WIDTHS)
     │
     ▼ (usuário arrasta borda)
[Redimensionado] → Salva header_state no QSettings
     │
     ▼ (fecha e reabre app)
[Restaurado] → Carrega header_state do QSettings
     │
     ▼ (usuário clica "Restaurar larguras padrão")
[Padrão restaurado] → Remove header_state do QSettings + aplica COLUMN_WIDTHS
```
