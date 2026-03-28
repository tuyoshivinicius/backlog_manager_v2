# Contract: ExecuteAllocationUseCase

## Visao Geral

ExecuteAllocationUseCase e um application service assincrono que coordena a alocacao automatica de desenvolvedores, buscando dados dos repositorios, invocando o AllocationService, e persistindo os resultados.

## Interface Publica

### __init__

```python
def __init__(self, uow: SQLiteUnitOfWork) -> None:
    """Inicializa o use case com UnitOfWork.

    Args:
        uow: UnitOfWork para acesso a repositorios.
    """
```

### execute

```python
async def execute(
    self, input_dto: ExecuteAllocationInputDTO
) -> ExecuteAllocationOutputDTO:
    """Executa alocacao automatica de desenvolvedores.

    Fluxo:
    1. Busca dados (stories, developers, dependencies, features)
    2. Emite warning se backlog > 500 historias
    3. Prepara AllocationConfig
    4. Chama AllocationService.allocate_stories() (sync)
    5. Atualiza historias alocadas via repository
    6. Converte resultado para DTO

    Args:
        input_dto: Parametros de alocacao.

    Returns:
        ExecuteAllocationOutputDTO com resultado e metricas.

    Raises:
        ValueError: Se input_dto invalido (validacao Pydantic).

    Example:
        >>> async with SQLiteUnitOfWork() as uow:
        ...     use_case = ExecuteAllocationUseCase(uow)
        ...     result = await use_case.execute(
        ...         ExecuteAllocationInputDTO(
        ...             velocity=2.0,
        ...             project_start_date=date(2026, 3, 2),
        ...         )
        ...     )
    """
```

## DTOs

### ExecuteAllocationInputDTO

```python
class ExecuteAllocationInputDTO(BaseModel):
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    project_start_date: date = Field(description="Data de inicio do projeto")
    max_idle_days: int = Field(
        default=3, ge=2, le=30,
        description="Dias maximos de ociosidade aceitavel"
    )
    allocation_criteria: str = Field(
        default="LOAD_BALANCING",
        description="Criterio de alocacao: LOAD_BALANCING ou DEPENDENCY_OWNER"
    )
    random_seed: int | None = Field(
        default=None,
        description="Seed para aleatoriedade (None = aleatorio)"
    )
```

### ExecuteAllocationOutputDTO

```python
class ExecuteAllocationOutputDTO(BaseModel):
    success: bool = Field(description="Alocacao completou com sucesso")
    stories_allocated: int = Field(description="Numero de historias alocadas")
    total_time_seconds: float = Field(description="Tempo total de execucao")
    warnings: list[str] = Field(
        default_factory=list,
        description="Lista de avisos (mensagens)"
    )
    metrics: AllocationMetricsDTO = Field(description="Metricas detalhadas")
```

### AllocationMetricsDTO

```python
class AllocationMetricsDTO(BaseModel):
    total_time_seconds: float = 0.0
    stories_processed: int = 0
    stories_allocated: int = 0
    waves_processed: int = 0
    total_iterations: int = 0
    iterations_per_wave: dict[int, int] = Field(default_factory=dict)
    allocations_by_dependency_owner: int = 0
    allocations_by_load_balancing: int = 0
    deadlocks_detected: int = 0
    date_adjustments: int = 0
    validation_reallocations: int = 0
    validation_dependency_fixes: int = 0
    validation_conflict_fixes: int = 0
    max_idle_violations_detected: int = 0
    max_idle_violations_fixed: int = 0
    failed_reallocations: int = 0

    @classmethod
    def from_domain(cls, metrics: AllocationMetrics) -> AllocationMetricsDTO:
        """Cria DTO a partir de AllocationMetrics do dominio."""
```

## Pre-condicoes

| Condicao | Descricao |
|----------|-----------|
| UnitOfWork valido | Conexao com banco disponivel |
| input_dto valido | Validacao Pydantic passa |
| velocity > 0 | Campo obrigatorio e positivo |
| max_idle_days in [2, 30] | Dentro do range valido |
| allocation_criteria valido | LOAD_BALANCING ou DEPENDENCY_OWNER |

## Pos-condicoes

| Condicao | Descricao |
|----------|-----------|
| historias persistidas | Todas as alocacoes salvas no banco |
| transacao atomica | Commit apos sucesso, rollback se erro |
| resultado valido | DTO com todos os campos preenchidos |

## Comportamento por Cenario

### Cenario: Alocacao Bem-Sucedida

- **Entrada**: backlog valido com historias elegiveis
- **Saida**: success=True, stories_allocated > 0
- **Efeito**: historias atualizadas no banco

### Cenario: Backlog Vazio

- **Entrada**: nenhuma historia no banco
- **Saida**: success=True, stories_allocated=0, warnings=[]

### Cenario: Backlog Grande (> 500)

- **Entrada**: mais de 500 historias
- **Comportamento**: emite warning antes de alocar
- **Saida**: warnings inclui aviso de limite

### Cenario: Erro de Validacao

- **Entrada**: velocity <= 0
- **Saida**: ValueError lancado (Pydantic validation)

## Integracao com Repositorios

### Dados Buscados

| Repositorio | Metodo | Proposito |
|-------------|--------|-----------|
| stories | get_all() | Todas as historias |
| developers | get_all() | Todos os desenvolvedores |
| dependencies | get_all_dependencies() | Grafo de dependencias |
| features | get_all() | Todas as features |

### Dados Persistidos

| Repositorio | Metodo | Proposito |
|-------------|--------|-----------|
| stories | update(story) | Atualiza developer_id, datas |

## Transacao

```python
async with self._uow as uow:
    # Buscar dados
    stories = await uow.stories.get_all()
    # ...

    # Chamar domain service
    result = AllocationService.allocate_stories(...)

    # Persistir alteracoes
    for story in result.allocated_stories:
        await uow.stories.update(story)

    # Commit automatico no __aexit__ se sem excecao
```

## Logging

| Nivel | Evento |
|-------|--------|
| INFO | Inicio da alocacao (count de historias) |
| INFO | Fim da alocacao (count alocadas, tempo) |
| WARNING | Backlog > 500 historias |
| WARNING | Deadlock detectado |
| ERROR | Falha na alocacao (com stack trace) |
