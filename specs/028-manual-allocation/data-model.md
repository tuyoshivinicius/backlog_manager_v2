# Data Model: Alocacao Manual de Desenvolvedores

**Branch**: `028-manual-allocation` | **Date**: 2026-03-31

## Entidades Existentes (sem modificacao)

### Story (Domain Entity)
```
Story
├── id: str                    # COMPONENTE-NNN
├── component: str
├── name: str
├── story_points: StoryPoint | int
├── priority: int
├── status: StoryStatus        # BACKLOG, EM_PROGRESSO, IMPEDIDO, CONCLUIDO
├── duration: int | None       # dias uteis (calculado)
├── start_date: date | None    # (calculado)
├── end_date: date | None      # (calculado)
├── developer_id: int | None   # FK → Developer
└── feature_id: int | None     # FK → Feature
```

### Developer (Domain Entity)
```
Developer
├── id: int | None
└── name: str                  # max 100 chars
```

## Novos DTOs (Application Layer)

### DeveloperAvailabilityDTO
```
DeveloperAvailabilityDTO (Pydantic BaseModel)
├── developer_id: int
├── developer_name: str
├── is_available: bool          # True = livre no periodo da historia
├── is_recommended: bool        # True = recomendado pelo algoritmo
├── blocking_stories: list[BlockingStoryDTO]  # historias que ocupam o dev
└── story_count: int            # total de historias alocadas (para load balancing display)
```

### BlockingStoryDTO
```
BlockingStoryDTO (Pydantic BaseModel)
├── story_id: str
├── story_name: str
├── start_date: date
└── end_date: date
```

### GetDeveloperAvailabilityInputDTO
```
GetDeveloperAvailabilityInputDTO (Pydantic BaseModel)
├── story_id: str
├── candidate_start_date: date  # data de inicio para calcular disponibilidade
├── velocity: float             # para recalcular end_date
└── allocation_criteria: str    # "LOAD_BALANCING" ou "DEPENDENCY_OWNER"
```

### GetDeveloperAvailabilityOutputDTO
```
GetDeveloperAvailabilityOutputDTO (Pydantic BaseModel)
├── developers: list[DeveloperAvailabilityDTO]
├── recommended_developer_id: int | None
├── story_start_date: date      # data de inicio usada no calculo
└── story_end_date: date        # data de fim recalculada
```

## Novos Use Cases (Application Layer)

### GetDeveloperAvailabilityUseCase
- **Input**: GetDeveloperAvailabilityInputDTO
- **Output**: GetDeveloperAvailabilityOutputDTO
- **Responsabilidade**: Dada uma historia e uma data candidata, retorna a lista de desenvolvedores com status de disponibilidade e recomendacao.
- **Logica**:
  1. Buscar historia por story_id
  2. Buscar todos os developers, stories e dependencies
  3. Recalcular end_date da historia via SchedulingService.calculate_story_dates()
  4. Para cada developer: verificar overlap com historias existentes usando AllocationService._has_period_overlap()
  5. Identificar desenvolvedor recomendado via AllocationService._select_developer()
  6. Retornar lista classificada (livres primeiro, ocupados depois)

### Nota sobre persistencia
A persistencia da alocacao manual usa **EditStoryUseCase** (existente) — nao requer novo use case de escrita. A dialog coleta `developer_id`, `start_date` e `end_date` e os envia via `EditStoryInputDTO`.

## State Transitions

```
Dialog Aberta
    ├── [data alterada] → Recalcula disponibilidade → Lista atualizada
    ├── [dev livre selecionado + confirmar] → Persiste alocacao → Dialog fecha
    ├── [dev ocupado clicado] → Nada (desabilitado)
    └── [cancelar] → Dialog fecha (sem mudancas)
```

## Relacionamentos

```
ManualAllocationDialog (View)
    └── uses → ManualAllocationDialogViewModel (ViewModel)
                ├── uses → GetDeveloperAvailabilityUseCase (Application)
                │           ├── reads → StoryRepository
                │           ├── reads → DeveloperRepository
                │           ├── reads → DependencyRepository
                │           ├── calls → SchedulingService (Domain)
                │           └── calls → AllocationService (Domain, static methods)
                └── uses → EditStoryUseCase (Application, existente)
                            └── writes → StoryRepository
```

## Schema SQLite
**Nenhuma alteracao de schema** — a feature usa apenas colunas existentes: `developer_id`, `start_date`, `end_date` na tabela `stories`.
