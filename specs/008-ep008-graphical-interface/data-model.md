# Data Model: EP-008 Interface Grafica

## Overview

Este documento define os modelos de dados da camada de apresentacao. A camada de apresentacao
NAO cria novas entidades de dominio - apenas consome DTOs existentes da Application layer.

## Presentation Layer Models

### 1. StoryTableModel

Modelo Qt para exibicao de historias na tabela principal.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| _stories | list[StoryOutputDTO] | Lista de historias ordenadas por prioridade |
| COLUMNS | ClassVar[list[str]] | ["ID", "Nome", "SP", "Status", "Feature", "Dev", "Inicio", "Fim"] |

**Heranca**: QAbstractTableModel

**Metodos Required**:
- rowCount() -> int
- columnCount() -> int
- data(index, role) -> Any
- headerData(section, orientation, role) -> Any
- set_stories(stories: list[StoryOutputDTO]) -> None

### 2. MainWindowViewModel

ViewModel principal que coordena operacoes do backlog.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| _stories | list[StoryOutputDTO] | Cache de historias |
| _selected_story_id | str | None | ID da historia selecionada |
| _is_loading | bool | Estado de carregamento |

**Signals**:
- stories_changed: Signal() - Emitido quando lista de historias muda
- story_selected: Signal(str) - Emitido quando historia e selecionada
- loading: Signal(bool) - Emitido quando operacao inicia/termina
- error_occurred: Signal(str) - Emitido quando ocorre erro

**Use Cases Injetados**:
- ListStoriesUseCase
- CreateStoryUseCase
- EditStoryUseCase
- DeleteStoryUseCase
- MovePriorityUseCase
- AssignDeveloperUseCase
- CalculateScheduleUseCase

### 3. StoryDialogViewModel

ViewModel para dialogo de criacao/edicao de historia.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| _mode | Literal["create", "edit"] | Modo de operacao |
| _story_id | str | None | ID da historia (edit mode) |
| _component | str | Componente da historia |
| _name | str | Nome da historia |
| _story_points | int | Story points (3, 5, 8, 13) |
| _feature_id | int | None | Feature associada |

**Signals**:
- saved: Signal() - Emitido quando salvo com sucesso
- error_occurred: Signal(str) - Emitido quando ocorre erro de validacao

**Use Cases Injetados**:
- CreateStoryUseCase
- EditStoryUseCase
- ListFeaturesUseCase

### 4. AllocationViewModel

ViewModel para execucao de alocacao automatica.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| _is_running | bool | Se alocacao esta em execucao |
| _progress | float | Progresso 0.0 a 1.0 |
| _last_metrics | AllocationMetricsDTO | None | Metricas da ultima alocacao |
| _last_warnings | list[str] | Warnings da ultima alocacao |

**Signals**:
- allocation_started: Signal() - Emitido quando alocacao inicia
- allocation_completed: Signal(AllocationMetricsDTO) - Emitido ao completar
- allocation_error: Signal(str) - Emitido em caso de erro
- warnings_updated: Signal(list) - Emitido quando ha warnings

**Use Cases Injetados**:
- ExecuteAllocationUseCase

## DTOs Consumidos (da Application Layer)

Estes DTOs ja existem e serao consumidos pela Presentation Layer:

### StoryOutputDTO
```python
class StoryOutputDTO(BaseModel):
    id: str
    component: str
    name: str
    story_points: int
    priority: int
    status: str
    duration: int | None
    start_date: date | None
    end_date: date | None
    developer_id: int | None
    feature_id: int | None
```

### DeveloperOutputDTO
```python
class DeveloperOutputDTO(BaseModel):
    id: int
    name: str
```

### FeatureOutputDTO
```python
class FeatureOutputDTO(BaseModel):
    id: int
    name: str
    wave: int
```

### AllocationMetricsDTO
```python
class AllocationMetricsDTO(BaseModel):
    total_time_seconds: float
    stories_processed: int
    stories_allocated: int
    waves_processed: int
    total_iterations: int
    iterations_per_wave: dict[int, int]
    allocations_by_dependency_owner: int
    allocations_by_load_balancing: int
    deadlocks_detected: int
    date_adjustments: int
    validation_reallocations: int
    validation_dependency_fixes: int
    validation_conflict_fixes: int
    max_idle_violations_detected: int
    max_idle_violations_fixed: int
    failed_reallocations: int
```

### ExecuteAllocationInputDTO
```python
class ExecuteAllocationInputDTO(BaseModel):
    velocity: float  # SP/dia
    project_start_date: date
    max_idle_days: int = 3  # 2-30
    allocation_criteria: str = "LOAD_BALANCING"
    random_seed: int | None = None
```

## Config State (In-Memory)

Configuracao mantida em memoria no ConfigPanel (sem persistencia no MVP - ADR-007).

| Campo | Tipo | Default | Validacao |
|-------|------|---------|-----------|
| velocity | float | 2.0 | > 0 |
| start_date | date | date.today() | not None |
| max_idle_days | int | 3 | 2 <= x <= 30 |

## Fluxo de Dados

```
[View] --user action--> [ViewModel] --execute()--> [UseCase] --repository--> [Database]
                            |
                            v
                    [Signal emitido]
                            |
                            v
                   [View atualiza UI]
```

## State Machine: AllocationViewModel

```
IDLE --[execute]--> RUNNING --[success]--> COMPLETED --> IDLE
                        |
                        +--[error]--> ERROR --> IDLE
```

## Relacionamentos

```
DIContainer
    |
    +-- SQLiteUnitOfWork
    |       |
    |       +-- StoryRepository
    |       +-- DeveloperRepository
    |       +-- FeatureRepository
    |       +-- StoryDependencyRepository
    |
    +-- Use Cases (23)
    |       |
    |       +-- Story (8): Create, Edit, Delete, List, Move, Duplicate, Assign
    |       +-- Developer (4): Create, Update, Delete, List
    |       +-- Feature (4): Create, Update, Delete, List
    |       +-- Dependency (4): Add, Remove, GetDeps, GetDependents
    |       +-- Scheduling (3): Duration, Schedule, StoryDates
    |       +-- Allocation (1): Execute
    |
    +-- ViewModels
            |
            +-- MainWindowViewModel
            +-- StoryDialogViewModel
            +-- AllocationViewModel
            +-- StoryTableModel
```
