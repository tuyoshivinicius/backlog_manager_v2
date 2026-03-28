# Data Model: EP-006 Calculo de Cronograma

**Feature Branch**: `006-ep006-scheduling-calculation`
**Date**: 2026-03-02

## Entidades Existentes (Modificadas)

### Story (Existente - EP-002)

A entidade Story ja possui os campos necessarios para scheduling. Nenhuma modificacao estrutural necessaria.

| Campo | Tipo | Descricao | Validacao |
|-------|------|-----------|-----------|
| id | str | ID unico (COMPONENT-NNN) | Regex: ^[A-Z]{2,10}-\d{3}$ |
| component | str | Componente do sistema | Max 50 chars |
| name | str | Nome da historia | Max 200 chars |
| story_points | StoryPoint ou int | Estimativa de esforco | {3, 5, 8, 13} |
| priority | int | Prioridade (menor = mais prioritario) | >= 0 |
| status | StoryStatus | Status atual | BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO |
| **duration** | int ou None | **Duracao calculada em dias uteis** | >= 1 quando calculado |
| **start_date** | date ou None | **Data de inicio calculada** | Dia util |
| **end_date** | date ou None | **Data de termino calculada** | >= start_date |
| developer_id | int ou None | FK para Developer | Nullable |
| feature_id | int ou None | FK para Feature (wave) | Nullable |

**Campos usados pelo EP-006**: duration, start_date, end_date, story_points, priority, status

---

## Value Objects Novos

### BRAZILIAN_HOLIDAYS_2026_2028

**Arquivo**: `src/backlog_manager/domain/value_objects/brazilian_holidays.py`

**Tipo**: `frozenset[date]`

**Descricao**: Conjunto imutavel de todas as datas de feriados nacionais brasileiros para 2026-2028.

**Dados**:

| Ano | Datas |
|-----|-------|
| 2026 | 01/01, 16/02, 17/02, 03/04, 21/04, 01/05, 04/06, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12 |
| 2027 | 01/01, 08/02, 09/02, 26/03, 21/04, 01/05, 27/05, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12 |
| 2028 | 01/01, 28/02, 29/02, 14/04, 21/04, 01/05, 15/06, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12 |

**Funcoes auxiliares**:

- `get_holidays_for_year(year: int) -> frozenset[date]`: Retorna feriados de um ano especifico. Vazio para anos fora de 2026-2028.

---

## Domain Service

### SchedulingService

**Arquivo**: `src/backlog_manager/domain/services/scheduling_service.py`

**Tipo**: Classe com metodos estaticos (stateless)

**Metodos**:

| Metodo | Assinatura | Retorno | Descricao |
|--------|------------|---------|-----------|
| calculate_duration | (story_points: int, velocity: float) -> int | int | Duracao em dias uteis usando ceil(SP/velocity) |
| is_workday | (d: date, holidays: frozenset[date]) -> bool | bool | True se dia util (seg-sex, nao feriado) |
| next_workday | (d: date, holidays: frozenset[date]) -> date | date | Proximo dia util a partir de d (inclusive) |
| add_workdays | (start_date: date, workdays: int, holidays: frozenset[date]) -> date | date | Data apos avancar N dias uteis |
| count_workdays_between | (start_date: date, end_date: date, holidays: frozenset[date]) -> int | int | Numero de dias uteis entre datas (exclusivo) |
| topological_sort | (stories: Sequence[Story], dependencies: dict[str, list[str]]) -> list[Story] | list[Story] | Ordenacao topologica com desempate por prioridade |
| calculate_story_dates | (story: Story, velocity: float, start_date: date, dependency_end_dates: Sequence[date], holidays: frozenset[date]) -> tuple[date, date, int] | tuple | (start_date, end_date, duration) calculados |

**Excecoes**:
- `ValueError`: velocity <= 0 em calculate_duration
- `CyclicDependencyException`: ciclo detectado em topological_sort

---

## DTOs (Application Layer)

### CalculateScheduleInputDTO

**Arquivo**: `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`

| Campo | Tipo | Descricao | Validacao |
|-------|------|-----------|-----------|
| velocity | float | Velocidade em SP/dia | > 0 |
| start_date | date | Data de inicio do projeto | Nao nulo |
| recalculate_all | bool | Recalcular todas as historias | Default: True |

### CalculateScheduleOutputDTO

| Campo | Tipo | Descricao |
|-------|------|-----------|
| success | bool | True se calculo completou |
| stories_processed | int | Numero de historias processadas |
| stories_updated | int | Numero de historias atualizadas |
| warnings | list[str] | Lista de avisos (historias ignoradas, etc.) |

### CalculateDurationInputDTO

**Arquivo**: `src/backlog_manager/application/dto/scheduling/calculate_duration_dto.py`

| Campo | Tipo | Descricao | Validacao |
|-------|------|-----------|-----------|
| story_points | int | Story points da historia | {3, 5, 8, 13} |
| velocity | float | Velocidade em SP/dia | > 0 |

### CalculateDurationOutputDTO

| Campo | Tipo | Descricao |
|-------|------|-----------|
| duration | int | Duracao calculada em dias uteis |
| formula | str | Formula usada (ex: ceil(5/2.0) = 3) |

### CalculateStoryDatesInputDTO

**Arquivo**: `src/backlog_manager/application/dto/scheduling/calculate_story_dates_dto.py`

| Campo | Tipo | Descricao | Validacao |
|-------|------|-----------|-----------|
| story_id | str | ID da historia | Formato COMPONENT-NNN |
| velocity | float | Velocidade em SP/dia | > 0 |
| project_start_date | date | Data de inicio do projeto | Nao nulo |

### CalculateStoryDatesOutputDTO

| Campo | Tipo | Descricao |
|-------|------|-----------|
| story_id | str | ID da historia |
| start_date | date | Data de inicio calculada |
| end_date | date | Data de termino calculada |
| duration | int | Duracao em dias uteis |

---

## Use Cases (Application Layer)

### CalculateScheduleUseCase

**Arquivo**: `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py`

**Dependencias**: UnitOfWork

**Responsabilidades**:
1. Buscar todas as historias e dependencias
2. Filtrar historias elegiveis (status=BACKLOG, story_points valido)
3. Construir grafo via DependencyService.build_graph()
4. Ordenar topologicamente via SchedulingService.topological_sort()
5. Calcular datas em ordem topologica
6. Persistir atualizacoes via StoryRepository.update()
7. Retornar OutputDTO com resultado e warnings

### CalculateDurationUseCase

**Arquivo**: `src/backlog_manager/application/use_cases/scheduling/calculate_duration.py`

**Dependencias**: Nenhuma (calculo puro)

**Responsabilidades**:
1. Validar input
2. Calcular duracao via SchedulingService.calculate_duration()
3. Retornar OutputDTO com duracao e formula

### CalculateStoryDatesUseCase

**Arquivo**: `src/backlog_manager/application/use_cases/scheduling/calculate_story_dates.py`

**Dependencias**: UnitOfWork

**Responsabilidades**:
1. Buscar historia por ID
2. Buscar dependencias da historia
3. Buscar end_dates das dependencias
4. Calcular datas via SchedulingService.calculate_story_dates()
5. Persistir atualizacao via StoryRepository.update()
6. Retornar OutputDTO com datas calculadas

---

## Diagrama de Relacionamentos

```
Application Layer
-----------------
  CalculateScheduleUseCase
    Input: CalculateScheduleInputDTO
    Output: CalculateScheduleOutputDTO
    Dependencies: UnitOfWork

  CalculateDurationUseCase
    Input: CalculateDurationInputDTO
    Output: CalculateDurationOutputDTO

  CalculateStoryDatesUseCase
    Input: CalculateStoryDatesInputDTO
    Output: CalculateStoryDatesOutputDTO
    Dependencies: UnitOfWork
              |
              v
Domain Layer
------------
  SchedulingService (stateless)
    calculate_duration(story_points, velocity)
    is_workday(date, holidays)
    next_workday(date, holidays)
    add_workdays(start_date, workdays, holidays)
    count_workdays_between(start_date, end_date, holidays)
    topological_sort(stories, dependencies)
    calculate_story_dates(story, velocity, start, deps)

  BRAZILIAN_HOLIDAYS_2026_2028: frozenset[date]
  get_holidays_for_year(year: int) -> frozenset[date]

  DependencyService (EP-005, reutilizado)
    build_graph(dependencies) -> dict[str, list[str]]

  Story Entity (EP-002, campos existentes)
    duration, start_date, end_date

  CyclicDependencyException (EP-005, reutilizada)
```

---

## Validacoes

### Validacoes no DTO (Pydantic)

| DTO | Campo | Validacao |
|-----|-------|-----------|
| CalculateScheduleInputDTO | velocity | > 0 |
| CalculateScheduleInputDTO | start_date | Nao nulo |
| CalculateDurationInputDTO | story_points | in {3, 5, 8, 13} |
| CalculateDurationInputDTO | velocity | > 0 |
| CalculateStoryDatesInputDTO | story_id | Regex COMPONENT-NNN |
| CalculateStoryDatesInputDTO | velocity | > 0 |
| CalculateStoryDatesInputDTO | project_start_date | Nao nulo |

### Validacoes no Domain Service

| Metodo | Validacao | Excecao |
|--------|-----------|---------|
| calculate_duration | velocity <= 0 | ValueError(Velocidade deve ser maior que zero) |
| topological_sort | Ciclo detectado | CyclicDependencyException(path) |

### Validacoes no Use Case

| Use Case | Validacao | Acao |
|----------|-----------|------|
| CalculateScheduleUseCase | Historia sem story_points valido | Adiciona warning, ignora historia |
| CalculateScheduleUseCase | Dependencia sem end_date | Usa project_start_date como fallback, adiciona warning |
| CalculateScheduleUseCase | Backlog vazio | Retorna success=true, stories_processed=0, warning informativo |
