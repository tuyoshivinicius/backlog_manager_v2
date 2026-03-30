# Data Model: EP-022 — Polimento e UX Avançado

**Date**: 2026-03-30

## Entities & Derived Models

### SP Breakdown (Derived — not persisted)

Aggregation of story points by status, computed in real-time from the loaded stories list.

| Field | Type | Description |
|-------|------|-------------|
| breakdown | dict[str, int] | Map of status → total SP (e.g., {"BACKLOG": 40, "EXECUCAO": 24, ...}) |
| total_sp | int | Sum of all SP across all statuses |
| percentages | dict[str, float] | Map of status → percentage (e.g., {"BACKLOG": 47.1, ...}) |

**Source**: Computed from `list[StoryOutputDTO]` in `StatusBarViewModel.update_sp_breakdown()`.

**Statuses**: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO (from `StoryStatus` enum).

---

### Blocking State (Derived — not persisted)

Blocking state of a story determined by comparing its `dependency_ids` against the status of corresponding stories in the model.

| Field | Type | Description |
|-------|------|-------------|
| state | BlockingState | BLOCKED, FREE, or NONE |
| dependency_ids | list[str] | IDs of dependencies |
| unresolved_ids | list[str] | IDs of dependencies not CONCLUIDO |

**Enum BlockingState**:
```python
class BlockingState(StrEnum):
    BLOCKED = "BLOCKED"    # At least one dependency not CONCLUIDO
    FREE = "FREE"          # All dependencies are CONCLUIDO
    NONE = "NONE"          # No dependencies (dependency_ids is empty)
```

**Resolution rule**: A dependency_id not found in the model is treated as "not CONCLUIDO" (BLOCKED), per spec edge case.

---

### Config Settings (Persisted via QSettings)

UI-level configuration values persisted between sessions.

| Field | Type | Default | Range | QSettings Key |
|-------|------|---------|-------|---------------|
| velocity | float | 2.0 | 0.1 – 10.0 | allocation/velocity |
| start_date | date | date.today() | — | allocation/start_date |
| max_idle_days | int | 3 | 2 – 30 | allocation/max_idle_days |

**Validation on load**: Values outside valid ranges are silently replaced with defaults.

**Storage format**: QSettings INI format. Organization: "BacklogManager", Application: "Backlog Manager".

---

### Wave Group (Derived — for visual grouping)

Visual grouping metadata computed from the sorted story list.

| Field | Type | Description |
|-------|------|-------------|
| wave | int | Wave number (0 = "Sem Onda") |
| label | str | Display label ("Onda N" or "Sem Onda") |
| first_row | int | First row index in the view for this wave |

**Computed in**: `StoryTableView` during paint, by scanning consecutive rows for wave changes.

---

### Rich Tooltip Data (Derived — for display)

Data extracted from `StoryOutputDTO` for the rich tooltip mini-card.

| Field | Source |
|-------|--------|
| ID | story.id |
| Nome | story.name |
| Status | story.status (with colored badge) |
| SP | story.story_points |
| Feature | story.feature_name or "—" |
| Desenvolvedor | story.developer_name or "—" |
| Dependencias | story.dependency_ids joined or "—" |
| Data Inicio | story.start_date formatted or "—" |
| Data Fim | story.end_date formatted or "—" |

---

## Relationships

```
StoryOutputDTO (existing)
├── SP Breakdown: aggregated by status field
├── Blocking State: resolved via dependency_ids → story status lookup
├── Wave Group: grouped by wave field
└── Rich Tooltip: all fields displayed in mini-card

ConfigDialogViewModel (existing)
└── Config Settings: persisted to/from QSettings

ProgressDialog (existing)
└── Cancellation: linked to asyncio.Task for cancel()
```

## No Schema Changes

This epic does NOT modify the SQLite schema. All new data is either:
- Derived in real-time from existing `StoryOutputDTO` data
- Persisted via QSettings (outside SQLite)
