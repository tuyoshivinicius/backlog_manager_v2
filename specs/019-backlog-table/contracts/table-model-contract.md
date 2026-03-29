# UI Contract: StoryTableModel — EP-019

**Date**: 2026-03-29 | **Type**: ViewModel-View Contract

## Overview

O `StoryTableModel` e o contrato entre a camada Application (via DTOs) e a View (QTableView). Ele expoe dados formatados para renderizacao e fornece metadados de alinhamento, tooltips e roles para delegates.

## Contract: QAbstractTableModel Interface

### Column Schema (13 colunas)

```
Index  Header          Role.Display            Role.Alignment   Role.ToolTip     Role.UserRole
─────  ──────────────  ──────────────────────  ───��───────────  ───────────────  ─────────────
0      Prioridade      str(priority)           AlignCenter      None             story.id
1      Feature         feature_name or "—"     AlignLeft|VCtr   feature_name     story.id
2      Onda            str(wave)               AlignCenter      None             story.id
3      ID              id                      AlignLeft|VCtr   None             story.id
4      Componente      component or "—"        AlignLeft|VCtr   None             story.id
5      Nome            name                    AlignLeft|VCtr   name             story.id
6      Status          status                  AlignCenter      None             story.id
7      Desenvolvedor   developer_name or "—"   AlignLeft|VCtr   developer_name   story.id
8      Dependencias    "ID1, ID2" or "—"       AlignLeft|VCtr   full deps str    story.id
9      SP              str(story_points)       AlignCenter      None             story.id
10     Inicio          DD/MM/YYYY or "—"       AlignCenter      None             story.id
11     Fim             DD/MM/YYYY or "—"       AlignCenter      None             story.id
12     Duracao         str(duration) or "—"    AlignCenter      None             story.id
```

### Supported Roles

| Qt Role | Retorno | Descricao |
|---------|---------|-----------|
| `DisplayRole` | `str` | Valor formatado para exibicao |
| `TextAlignmentRole` | `Qt.AlignmentFlag` | Alinhamento da celula |
| `ToolTipRole` | `str \| None` | Texto completo para tooltip (colunas 1,5,7,8) |
| `UserRole` | `str` | ID da historia (para selecao) |

### Public Methods

| Metodo | Assinatura | Descricao |
|--------|-----------|-----------|
| `rowCount` | `(parent?) → int` | Numero de historias |
| `columnCount` | `(parent?) → int` | 13 (fixo) |
| `data` | `(index, role) → Any` | Dados por celula e role |
| `headerData` | `(section, orientation, role) → Any` | Nome da coluna |
| `set_stories` | `(stories: Sequence[StoryOutputDTO]) → None` | Atualiza dados com reset signals |
| `get_story_at` | `(row: int) → StoryOutputDTO \| None` | Story por indice |
| `get_story_by_id` | `(story_id: str) → StoryOutputDTO \| None` | Story por ID |
| `get_row_for_story` | `(story_id: str) → int` | Indice da story (-1 se nao encontrada) |
| `stories` | `→ list[StoryOutputDTO]` (property) | Copia da lista de stories |

### Delegate Assignment (View-side)

| Coluna | Delegate | Lookup |
|--------|----------|--------|
| 3 (ID) | `MonospaceDelegate` | Por header text "ID" |
| 6 (Status) | `StatusBadgeDelegate` | Por header text "Status" |

### Empty State Contract

| Condicao | View Behavior |
|----------|---------------|
| `rowCount() == 0` | Exibir overlay com mensagem orientativa; desabilitar botoes de processamento |
| `rowCount() > 0` | Esconder overlay; habilitar botoes |

## Input Contract: StoryOutputDTO (enriched)

O ViewModel espera receber `StoryOutputDTO` com os seguintes campos preenchidos pela Application layer:

```python
class StoryOutputDTO(BaseModel):
    # Campos obrigatorios (sempre preenchidos)
    id: str                          # "AUTH-001"
    component: str                   # "AUTH"
    name: str                        # "Implementar login"
    story_points: int                # 5
    priority: int                    # 1
    status: str                      # "BACKLOG"

    # Campos opcionais (podem ser None)
    duration: int | None = None      # 10 (dias uteis)
    start_date: date | None = None   # 2026-04-01
    end_date: date | None = None     # 2026-04-15
    developer_id: int | None = None  # 1
    feature_id: int | None = None    # 2

    # Campos enriquecidos (novos, opcionais com defaults)
    developer_name: str | None = None      # "Joao Silva"
    feature_name: str | None = None        # "Autenticacao"
    wave: int = 0                          # 1
    dependency_ids: list[str] = []         # ["API-001", "DB-003"]
```

## Column Width Contract

```python
COLUMN_WIDTHS = [60, 120, 50, 100, 80, -1, 100, 100, 120, 40, 90, 90, 60]
# Total fixo: 60+120+50+100+80+100+100+120+40+90+90+60 = 1010px
# Nome (stretch) ocupa espaco restante, minimo 200px
# Resolucao minima funcional: 1210px (1010 + 200)
# Resolucao minima suportada: 1366px (OK — margem de 156px)
```
