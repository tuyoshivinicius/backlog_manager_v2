# Contrato: Developer Use Cases

**Tipo**: Application Layer - Use Cases
**Localizacao**: `src/backlog_manager/application/use_cases/developer/`
**Data**: 2026-03-01

## Visao Geral

Use cases para operacoes CRUD de desenvolvedores. Cada use case recebe UnitOfWork, instancia DeveloperService internamente, e coordena transacoes.

## Dependencias Comuns

```python
from backlog_manager.domain.interfaces.repositories import UnitOfWork
from backlog_manager.domain.services.developer_service import DeveloperService
from backlog_manager.application.dto.developer import (
    CreateDeveloperInputDTO,
    UpdateDeveloperInputDTO,
    DeveloperOutputDTO,
    DeleteDeveloperOutputDTO,
    ListDevelopersOutputDTO,
)
```

---

## CreateDeveloperUseCase

**Arquivo**: `create_developer.py`

### Interface

```python
class CreateDeveloperUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, input_dto: CreateDeveloperInputDTO) -> DeveloperOutputDTO:
        """Cria um novo desenvolvedor."""
```

### Comportamento

```python
async def execute(self, input_dto: CreateDeveloperInputDTO) -> DeveloperOutputDTO:
    async with self._uow:
        service = DeveloperService(self._uow.developers, self._uow.stories)
        developer = await service.create_developer(input_dto.name)
        developer.id = await self._uow.developers.add(developer)
        return DeveloperOutputDTO.from_entity(developer)
```

### Entrada/Saida

**Entrada**: `CreateDeveloperInputDTO`
- `name: str` - Nome do desenvolvedor

**Saida**: `DeveloperOutputDTO`
- `id: int` - ID gerado
- `name: str` - Nome normalizado

**Erros**:
- `ValueError`: Nome invalido (propagado do service/entidade)

---

## UpdateDeveloperUseCase

**Arquivo**: `update_developer.py`

### Interface

```python
class UpdateDeveloperUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, input_dto: UpdateDeveloperInputDTO) -> DeveloperOutputDTO:
        """Atualiza um desenvolvedor existente."""
```

### Comportamento

```python
async def execute(self, input_dto: UpdateDeveloperInputDTO) -> DeveloperOutputDTO:
    async with self._uow:
        service = DeveloperService(self._uow.developers, self._uow.stories)
        developer = await service.update_developer(
            input_dto.developer_id,
            input_dto.name
        )
        await self._uow.developers.update(developer)
        return DeveloperOutputDTO.from_entity(developer)
```

### Entrada/Saida

**Entrada**: `UpdateDeveloperInputDTO`
- `developer_id: int` - ID do desenvolvedor
- `name: str` - Novo nome

**Saida**: `DeveloperOutputDTO`
- `id: int` - ID (inalterado)
- `name: str` - Nome atualizado

**Erros**:
- `ValueError("Desenvolvedor nao encontrado: {id}")`: ID nao existe
- `ValueError`: Nome invalido

---

## DeleteDeveloperUseCase

**Arquivo**: `delete_developer.py`

### Interface

```python
class DeleteDeveloperUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, developer_id: int) -> DeleteDeveloperOutputDTO:
        """Deleta um desenvolvedor e retorna contagem de desalocacoes."""
```

### Comportamento

```python
async def execute(self, developer_id: int) -> DeleteDeveloperOutputDTO:
    async with self._uow:
        service = DeveloperService(self._uow.developers, self._uow.stories)
        stories_unassigned = await service.delete_developer(developer_id)
        return DeleteDeveloperOutputDTO(
            developer_id=developer_id,
            stories_unassigned=stories_unassigned
        )
```

### Entrada/Saida

**Entrada**: `developer_id: int` - ID do desenvolvedor a deletar

**Saida**: `DeleteDeveloperOutputDTO`
- `developer_id: int` - ID deletado
- `stories_unassigned: int` - Quantidade de historias desalocadas

**Erros**:
- `ValueError("Desenvolvedor nao encontrado: {id}")`: ID nao existe

---

## ListDevelopersUseCase

**Arquivo**: `list_developers.py`

### Interface

```python
class ListDevelopersUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self) -> ListDevelopersOutputDTO:
        """Lista todos os desenvolvedores ordenados por nome."""
```

### Comportamento

```python
async def execute(self) -> ListDevelopersOutputDTO:
    async with self._uow:
        # Listagem simples - usa repositorio diretamente (sem service)
        developers = await self._uow.developers.get_all()
        return ListDevelopersOutputDTO(
            developers=[DeveloperOutputDTO.from_entity(d) for d in developers]
        )
```

### Entrada/Saida

**Entrada**: Nenhuma

**Saida**: `ListDevelopersOutputDTO`
- `developers: list[DeveloperOutputDTO]` - Lista ordenada por nome

**Erros**: Nenhum (retorna lista vazia se nao houver desenvolvedores)

---

## Notas de Implementacao

1. **UnitOfWork**: Todos use cases recebem UoW no construtor e executam dentro de `async with` para garantir transacoes.

2. **Service vs Repository**:
   - Create/Update/Delete usam DeveloperService (logica de negocio)
   - List usa repositorio diretamente (listagem simples sem logica)

3. **Commit implicito**: `async with uow` faz commit automatico ao sair com sucesso, rollback em caso de excecao.

4. **Atribuicao de ID**: Apos `add()`, o ID retornado e atribuido a entidade antes de converter para DTO.
