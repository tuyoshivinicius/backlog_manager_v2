# Data Model: Schedule Calculation GUI Integration

**Feature**: EP-013 Schedule GUI Integration | **Date**: 2026-03-04

## Overview

This feature exposes existing schedule calculation functionality through the GUI. No new domain entities are required. The data model documents reused components and the new ViewModel.

## Existing Entities (Reused)

### Story (Domain Entity)

**Location**: `src/backlog_manager/domain/entities/story.py`

**Relevant Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier |
| `story_points` | `StoryPoint` | Fibonacci value (3, 5, 8, 13) |
| `start_date` | `date | None` | Calculated start date |
| `end_date` | `date | None` | Calculated end date |
| `duration` | `int | None` | Duration in workdays |
| `status` | `StoryStatus` | BACKLOG, IN_PROGRESS, DONE |

**Schedule Calculation Updates**: `start_date`, `end_date`, `duration`

### Configuration (Domain Entity)

**Location**: `src/backlog_manager/domain/entities/configuration.py`

**Relevant Fields**:
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `velocity` | `float` | 2.0 | Story points per day |
| `start_date` | `date` | today | Project start date |

## Existing DTOs (Reused)

### CalculateScheduleInputDTO

**Location**: `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`

```python
class CalculateScheduleInputDTO(BaseModel):
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    start_date: date = Field(description="Data de inicio do projeto")
    recalculate_all: bool = Field(default=True)
```

### CalculateScheduleOutputDTO

**Location**: `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`

```python
class CalculateScheduleOutputDTO(BaseModel):
    success: bool
    stories_processed: int
    stories_updated: int
    warnings: list[str]
```

## New ViewModel (Presentation Layer)

### ScheduleViewModel

**Purpose**: Coordinate schedule calculation execution and UI state management

**Location**: `src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py`

**Signals**:
| Signal | Type | Description |
|--------|------|-------------|
| `schedule_started` | `Signal()` | Emitted when calculation begins |
| `schedule_completed` | `Signal(object)` | Emitted with CalculateScheduleOutputDTO |
| `schedule_error` | `Signal(str)` | Emitted with error message |

**State**:
| Property | Type | Description |
|----------|------|-------------|
| `_is_running` | `bool` | Prevents duplicate execution |
| `_container` | `DIContainer` | DI container reference |

**Methods**:
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `execute` | `velocity: float, start_date: date` | `CalculateScheduleOutputDTO | None` | Execute schedule calculation |

**Interface**:
```python
class ScheduleViewModel(QObject):
    """ViewModel para calculo de cronograma.

    Coordena a execucao do use case CalculateSchedule e
    emite sinais para atualizacao da UI.
    """

    schedule_started = Signal()
    schedule_completed = Signal(object)  # CalculateScheduleOutputDTO
    schedule_error = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        """Inicializa o ViewModel.

        Args:
            container: Container de injecao de dependencias.
        """
        ...

    @property
    def is_running(self) -> bool:
        """Retorna True se calculo esta em execucao."""
        ...

    async def execute(
        self,
        velocity: float,
        start_date: date,
    ) -> CalculateScheduleOutputDTO | None:
        """Executa o calculo de cronograma.

        Args:
            velocity: Velocidade em SP/dia.
            start_date: Data de inicio do projeto.

        Returns:
            DTO com resultado ou None se ja executando.
        """
        ...
```

## Data Flow

```
┌──────────────────┐    ┌───────────────────┐    ┌─────────────────────┐
│   ConfigPanel    │───>│  ScheduleViewModel │───>│CalculateScheduleUseCase│
│ (velocity, date) │    │    (async exec)    │    │   (business logic)   │
└──────────────────┘    └───────────────────┘    └─────────────────────┘
                               │                           │
                               │ schedule_started          │
                               │ schedule_completed        │ Updates Story
                               │ schedule_error            │ entities in DB
                               ▼                           │
                        ┌──────────────────┐               │
                        │    MainWindow    │<──────────────┘
                        │ (UI state, dialog)│
                        └──────────────────┘
```

## Validation Rules

| Rule | Layer | Implementation |
|------|-------|----------------|
| velocity > 0 | Presentation | ConfigPanel.validate() |
| start_date valid | Presentation | QDateEdit widget |
| story_points in {3,5,8,13} | Application | CalculateScheduleUseCase (skips invalid) |
| No cyclic dependencies | Application | SchedulingService.topological_sort() |

## State Transitions

### ScheduleViewModel State Machine

```
         execute()
           │
    ┌──────▼──────┐
    │   IDLE      │────────── is_running=false
    └──────┬──────┘
           │ emit schedule_started
           │ is_running=true
    ┌──────▼──────┐
    │  RUNNING    │────────── Button disabled
    └──────┬──────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│ SUCCESS │ │  ERROR  │
└────┬────┘ └────┬────┘
     │ emit      │ emit
     │ completed │ error
     │           │
     └─────┬─────┘
           │ is_running=false
    ┌──────▼──────┐
    │    IDLE     │
    └─────────────┘
```
