# Data Model: EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)

## Entities

### Story (existing — no changes)

| Field | Type | Category | Affected by Reset |
|-------|------|----------|-------------------|
| id | str | User data | NO |
| component | str | User data | NO |
| name | str | User data | NO |
| story_points | StoryPoint \| int | User data | NO |
| priority | int | User data | NO |
| status | StoryStatus | User data | NO |
| feature_id | int \| None | User data | NO |
| duration | int \| None | Calculated | YES → set to None |
| start_date | date \| None | Calculated | YES → set to None |
| end_date | date \| None | Calculated | YES → set to None |
| developer_id | int \| None | Calculated | YES → set to None |

**File**: `src/backlog_manager/domain/entities/story.py`

### Story Dependencies (existing — no changes)

Dependencies between stories are structural data and are NOT affected by the reset operation.

**File**: `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`

## DTOs (new)

### ResetPlanningInputDTO

```python
class ResetPlanningInputDTO(BaseModel):
    """Input DTO for reset planning use case. No parameters needed."""
    pass
```

### ResetPlanningOutputDTO

```python
class ResetPlanningOutputDTO(BaseModel):
    """Output DTO with reset operation results."""
    success: bool
    stories_reset: int                    # Total stories modified
    stories_with_dates_cleared: int       # Stories that had duration/start_date/end_date
    stories_with_developer_cleared: int   # Stories that had developer_id
    warnings: list[str] = []
```

### CountAffectedStoriesOutputDTO

```python
class CountAffectedStoriesOutputDTO(BaseModel):
    """Output DTO with counts of stories that would be affected."""
    total: int           # Stories with any calculated field filled
    with_dates: int      # Stories with duration/start_date/end_date
    with_developer: int  # Stories with developer_id
```

## State Transitions

```
Before Reset:
  Story: duration=5, start_date=2026-01-05, end_date=2026-01-09, developer_id=1
  Status: EXECUCAO (unchanged)

After Reset:
  Story: duration=None, start_date=None, end_date=None, developer_id=None
  Status: EXECUCAO (preserved)
```

## Filtering Logic

A story is "affected" by the reset if ANY of the following conditions is true:
- `duration is not None`
- `start_date is not None`
- `end_date is not None`
- `developer_id is not None`

The sub-counts are:
- `with_dates`: story has `duration is not None` OR `start_date is not None` OR `end_date is not None`
- `with_developer`: story has `developer_id is not None`

## No Schema Changes

The reset operation only sets existing columns to NULL. No database migration is needed.
