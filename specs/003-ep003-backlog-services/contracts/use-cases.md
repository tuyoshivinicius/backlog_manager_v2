# Use Case Contracts: EP-003 Gestao de Backlog

**Date**: 2026-02-28
**Type**: Python Library Interface

## Overview

Este documento define os contratos publicos dos Use Cases da camada de aplicacao. Estes sao os pontos de entrada para consumidores da biblioteca (UI, CLI, testes).

## Contract Format

Cada use case segue o padrao:
- Construtor recebe `Callable[[], UnitOfWork]` (factory)
- Metodo `execute(input_dto) -> output_dto` async
- Excecoes documentadas

---

## CreateStoryUseCase

**Purpose**: Cria uma nova historia no backlog com ID e prioridade automaticos.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: CreateStoryInputDTO) -> CreateStoryOutputDTO
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| component | str | Yes | Componente/modulo (uppercase) |
| name | str | Yes | Nome da historia |
| story_points | int | Yes | Estimativa (3, 5, 8, 13) |
| feature_id | int or None | No | Feature associada |

**Output**: StoryOutputDTO com todos os campos da historia criada

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValidationError (Pydantic) | Campos invalidos no input |
| ValueError | Componente vazio ou > 50 chars |

**Postconditions**:
- Historia persistida com ID no formato COMPONENTE-NNN
- Prioridade = max(existentes) + 1
- Status = BACKLOG

---

## UpdateStoryUseCase

**Purpose**: Atualiza campos editaveis de uma historia existente.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: UpdateStoryInputDTO) -> StoryOutputDTO
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | str | Yes | ID da historia |
| name | str or None | No | Novo nome |
| story_points | int or None | No | Nova estimativa |
| status | str or None | No | Novo status |
| feature_id | int or None | No | Nova feature |
| clear_feature | bool | No | Se True, remove feature |

**Output**: StoryOutputDTO com campos atualizados

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValueError | Historia nao encontrada |
| ValidationError | Campos invalidos |

**Postconditions**:
- Campos fornecidos atualizados
- ID e component inalterados (imutaveis)

---

## DeleteStoryUseCase

**Purpose**: Remove uma historia e limpa suas dependencias.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: DeleteStoryInputDTO) -> None
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | str | Yes | ID da historia |

**Output**: None

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValueError | Historia nao encontrada |

**Postconditions**:
- Historia removida do banco
- Todas as dependencias (onde aparece como dependente ou dependencia) removidas

---

## DuplicateStoryUseCase

**Purpose**: Cria copia de uma historia com novo ID e campos de alocacao resetados.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: DuplicateStoryInputDTO) -> StoryOutputDTO
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | str | Yes | ID da historia a duplicar |

**Output**: StoryOutputDTO da nova historia

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValueError | Historia nao encontrada |

**Postconditions**:
- Nova historia com novo ID (mesmo componente, proximo numero)
- Campos copiados: component, name, story_points, feature_id
- Campos resetados: developer_id=None, start_date=None, end_date=None, duration=None
- Status = BACKLOG (independente do original)
- Prioridade = max(existentes) + 1

---

## ListStoriesUseCase

**Purpose**: Lista todas as historias ordenadas por prioridade.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self) -> ListStoriesOutputDTO
```

**Input**: Nenhum

**Output**:
| Field | Type | Description |
|-------|------|-------------|
| stories | list[StoryOutputDTO] | Lista ordenada por prioridade |

**Exceptions**: Nenhuma especifica

**Postconditions**:
- Lista vazia se backlog vazio
- Ordenacao ascendente por prioridade

---

## MovePriorityUseCase

**Purpose**: Move prioridade de uma historia para cima ou baixo.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: MovePriorityInputDTO) -> MovePriorityOutputDTO
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | str | Yes | ID da historia |
| direction | Literal["up", "down"] | Yes | Direcao do movimento |

**Output**:
| Field | Type | Description |
|-------|------|-------------|
| moved | bool | True se movimento ocorreu |
| story | StoryOutputDTO | Historia apos operacao |

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValueError | Historia nao encontrada |

**Postconditions**:
- Se moved=True: prioridades trocadas com historia adjacente
- Se moved=False: ja estava na borda (mais prioritario ou menos prioritario)
- Swap atomico (ambas historias atualizadas na mesma transacao)

---

## AssignDeveloperUseCase

**Purpose**: Atribui ou desatribui desenvolvedor a uma historia.

**Constructor**:
```python
def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None
```

**Execute**:
```python
async def execute(self, input_dto: AssignDeveloperInputDTO) -> StoryOutputDTO
```

**Input**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| story_id | str | Yes | ID da historia |
| developer_id | int or None | Yes | ID do desenvolvedor ou None |

**Output**: StoryOutputDTO com developer_id atualizado

**Exceptions**:
| Exception | Condition |
|-----------|-----------|
| ValueError | Historia nao encontrada |
| ValueError | Desenvolvedor nao encontrado (quando developer_id != None) |

**Postconditions**:
- developer_id atualizado
- Se developer_id=None: historia desalocada
