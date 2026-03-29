# Data Model: EP-019 — Tabela de Backlog (GUI-003)

**Date**: 2026-03-29 | **Branch**: `019-backlog-table`

## Entities

### StoryOutputDTO (Application Layer — DTO enriquecido)

**File**: `src/backlog_manager/application/dto/story/story_output_dto.py`

| Campo | Tipo | Origem | Novo? | Descricao |
|-------|------|--------|-------|-----------|
| `id` | `str` | Story.id | Nao | ID no formato COMPONENTE-NNN |
| `component` | `str` | Story.component | Nao | Prefixo de componente |
| `name` | `str` | Story.name | Nao | Nome da historia |
| `story_points` | `int` | Story.story_points | Nao | Story points (3,5,8,13) |
| `priority` | `int` | Story.priority | Nao | Prioridade numerica |
| `status` | `str` | Story.status | Nao | Status textual |
| `duration` | `int \| None` | Story.duration | Nao | Dias uteis calculados |
| `start_date` | `date \| None` | Story.start_date | Nao | Data inicio calculada |
| `end_date` | `date \| None` | Story.end_date | Nao | Data fim calculada |
| `developer_id` | `int \| None` | Story.developer_id | Nao | FK para Developer |
| `feature_id` | `int \| None` | Story.feature_id | Nao | FK para Feature |
| `developer_name` | `str \| None` | DeveloperRepo lookup | **Sim** | Nome resolvido do desenvolvedor |
| `feature_name` | `str \| None` | FeatureRepo lookup | **Sim** | Nome resolvido da feature |
| `wave` | `int` | FeatureRepo lookup | **Sim** | Numero da onda (0 se sem feature) |
| `dependency_ids` | `list[str]` | DependencyRepo | **Sim** | IDs das dependencias (ex: ["AUTH-001", "API-003"]) |

**Validacao**: Campos novos sao opcionais com defaults (`None`, `0`, `[]`). Backward compatible.

---

### StoryTableModel (Presentation Layer — ViewModel)

**File**: `src/backlog_manager/presentation/viewmodels/story_table_model.py`

#### Colunas (13 total, nova ordem)

| Index | Header | Campo DTO | Largura | Alinhamento | Delegate | Tooltip |
|-------|--------|-----------|---------|-------------|----------|---------|
| 0 | Prioridade | `priority` | 60px Fixed | Centro | — | Nao |
| 1 | Feature | `feature_name` | 120px Fixed | Esquerda | — | Sim |
| 2 | Onda | `wave` | 50px Fixed | Centro | — | Nao |
| 3 | ID | `id` | 100px Fixed | Esquerda | MonospaceDelegate | Nao |
| 4 | Componente | `component` | 80px Fixed | Esquerda | — | Nao |
| 5 | Nome | `name` | Stretch (min 200px) | Esquerda | — | Sim |
| 6 | Status | `status` | 100px Fixed | Centro | StatusBadgeDelegate | Nao |
| 7 | Desenvolvedor | `developer_name` | 100px Fixed | Esquerda | — | Sim |
| 8 | Dependencias | `dependency_ids` (formatado) | 120px Fixed | Esquerda | — | Sim |
| 9 | SP | `story_points` | 40px Fixed | Centro | — | Nao |
| 10 | Inicio | `start_date` | 90px Fixed | Centro | — | Nao |
| 11 | Fim | `end_date` | 90px Fixed | Centro | — | Nao |
| 12 | Duracao | `duration` | 60px Fixed | Centro | — | Nao |

#### Constantes

```python
COLUMNS: ClassVar[list[str]] = [
    "Prioridade", "Feature", "Onda", "ID", "Componente", "Nome",
    "Status", "Desenvolvedor", "Dependencias", "SP", "Inicio", "Fim", "Duracao",
]

COLUMN_WIDTHS: ClassVar[list[int]] = [
    60, 120, 50, 100, 80, -1, 100, 100, 120, 40, 90, 90, 60,
]
# -1 = Stretch

CENTER_COLUMNS: ClassVar[set[int]] = {0, 2, 6, 9, 10, 11, 12}
# Prioridade, Onda, Status, SP, Inicio, Fim, Duracao

TOOLTIP_COLUMNS: ClassVar[set[int]] = {1, 5, 7, 8}
# Feature, Nome, Desenvolvedor, Dependencias
```

#### Formatacao por Coluna

| Index | Formatacao | Valor Ausente |
|-------|-----------|---------------|
| 0 (Prioridade) | `str(story.priority)` | — (sempre presente) |
| 1 (Feature) | `story.feature_name` | "—" |
| 2 (Onda) | `str(story.wave)` if wave > 0 else "—" | "—" |
| 3 (ID) | `story.id` | — (sempre presente) |
| 4 (Componente) | `story.component` | "—" se vazio |
| 5 (Nome) | `story.name` | — (sempre presente) |
| 6 (Status) | `story.status` | — (sempre presente) |
| 7 (Desenvolvedor) | `story.developer_name` | "—" |
| 8 (Dependencias) | `", ".join(story.dependency_ids)` | "—" |
| 9 (SP) | `str(story.story_points)` | — (sempre presente) |
| 10 (Inicio) | `story.start_date.strftime("%d/%m/%Y")` | "—" |
| 11 (Fim) | `story.end_date.strftime("%d/%m/%Y")` | "—" |
| 12 (Duracao) | `str(story.duration)` | "—" |

---

### Estado Vazio (MainWindow)

**File**: `src/backlog_manager/presentation/views/main_window.py`

| Estado | Condicao | Acoes |
|--------|----------|-------|
| Vazio | `table_model.rowCount() == 0` | Exibir overlay QLabel; desabilitar `_action_schedule` e `_action_allocate` |
| Populado | `table_model.rowCount() > 0` | Esconder overlay; habilitar botoes |

**Transicoes**:
- Vazio → Populado: Apos `set_stories()` com lista nao-vazia (cadastro, import)
- Populado → Vazio: Apos `set_stories()` com lista vazia (delete ultima historia)

---

## Relationships

```
StoryOutputDTO (enriched)
├── developer_name ← resolve via DeveloperRepository.get_all() lookup map
├── feature_name ← resolve via FeatureRepository.get_all() lookup map
├── wave ← resolve via FeatureRepository.get_all() lookup map
└── dependency_ids ← resolve via StoryDependencyRepository.get_dependencies()

StoryTableModel
└── consumes [StoryOutputDTO] via set_stories()
    └── renders 13 columns from DTO fields

MainWindow
├── owns StoryTableView
│   ├── MonospaceDelegate → column 3 (ID)
│   └── StatusBadgeDelegate → column 6 (Status)
└── owns empty state QLabel (overlay)
```
