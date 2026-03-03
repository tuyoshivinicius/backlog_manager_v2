# Contrato: Feature Use Cases

**Tipo**: Application Layer - Use Cases
**Localizacao**: `src/backlog_manager/application/use_cases/feature/`
**Data**: 2026-03-01

## Visao Geral

Use cases para operacoes CRUD de features. Cada use case recebe UnitOfWork, instancia FeatureService internamente, e coordena transacoes.

## Dependencias Comuns

```python
from backlog_manager.domain.interfaces.repositories import UnitOfWork
from backlog_manager.domain.services.feature_service import FeatureService
from backlog_manager.domain.exceptions.feature import (
    DuplicateWaveException,
    FeatureHasStoriesException,
)
from backlog_manager.application.dto.feature import (
    CreateFeatureInputDTO,
    UpdateFeatureInputDTO,
    FeatureOutputDTO,
    ListFeaturesOutputDTO,
)
```

---

## CreateFeatureUseCase

**Arquivo**: `create_feature.py`

### Interface

```python
class CreateFeatureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, input_dto: CreateFeatureInputDTO) -> FeatureOutputDTO:
        """Cria uma nova feature com validacao de unicidade."""
```

### Comportamento

```python
async def execute(self, input_dto: CreateFeatureInputDTO) -> FeatureOutputDTO:
    async with self._uow:
        service = FeatureService(self._uow.features)
        feature = await service.create_feature(input_dto.name, input_dto.wave)
        feature.id = await self._uow.features.add(feature)
        return FeatureOutputDTO.from_entity(feature)
```

### Entrada/Saida

**Entrada**: `CreateFeatureInputDTO`
- `name: str` - Nome da feature
- `wave: int` - Numero da onda (> 0)

**Saida**: `FeatureOutputDTO`
- `id: int` - ID gerado
- `name: str` - Nome normalizado
- `wave: int` - Numero da onda

**Erros**:
- `ValueError`: Nome/wave invalido
- `DuplicateWaveException`: Wave ja existe
- `ValueError("Feature com nome 'X' ja existe")`: Nome duplicado

---

## UpdateFeatureUseCase

**Arquivo**: `update_feature.py`

### Interface

```python
class UpdateFeatureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, input_dto: UpdateFeatureInputDTO) -> FeatureOutputDTO:
        """Atualiza uma feature existente (parcialmente)."""
```

### Comportamento

```python
async def execute(self, input_dto: UpdateFeatureInputDTO) -> FeatureOutputDTO:
    async with self._uow:
        service = FeatureService(self._uow.features)
        feature = await service.update_feature(
            input_dto.feature_id,
            name=input_dto.name,
            wave=input_dto.wave
        )
        await self._uow.features.update(feature)
        return FeatureOutputDTO.from_entity(feature)
```

### Entrada/Saida

**Entrada**: `UpdateFeatureInputDTO`
- `feature_id: int` - ID da feature
- `name: str | None` - Novo nome (opcional)
- `wave: int | None` - Nova wave (opcional)

**Saida**: `FeatureOutputDTO`
- `id: int` - ID (inalterado)
- `name: str` - Nome (atualizado ou original)
- `wave: int` - Wave (atualizada ou original)

**Erros**:
- `ValueError("Feature nao encontrada: {id}")`: ID nao existe
- `ValueError`: Nome/wave invalido
- `DuplicateWaveException`: Wave ja existe em outra feature
- `ValueError("Feature com nome 'X' ja existe")`: Nome duplicado

---

## DeleteFeatureUseCase

**Arquivo**: `delete_feature.py`

### Interface

```python
class DeleteFeatureUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self, feature_id: int) -> None:
        """Deleta uma feature (somente se sem historias)."""
```

### Comportamento

```python
async def execute(self, feature_id: int) -> None:
    async with self._uow:
        service = FeatureService(self._uow.features)
        await service.delete_feature(feature_id)
```

### Entrada/Saida

**Entrada**: `feature_id: int` - ID da feature a deletar

**Saida**: `None`

**Erros**:
- `ValueError("Feature nao encontrada: {id}")`: ID nao existe
- `FeatureHasStoriesException`: Feature tem historias associadas
  - `feature_id: int` - ID da feature
  - `feature_name: str` - Nome da feature
  - `story_count: int` - Quantidade de historias

---

## ListFeaturesUseCase

**Arquivo**: `list_features.py`

### Interface

```python
class ListFeaturesUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case com UnitOfWork."""

    async def execute(self) -> ListFeaturesOutputDTO:
        """Lista todas as features ordenadas por wave."""
```

### Comportamento

```python
async def execute(self) -> ListFeaturesOutputDTO:
    async with self._uow:
        # Listagem simples - usa repositorio diretamente (sem service)
        features = await self._uow.features.get_all()
        return ListFeaturesOutputDTO(
            features=[FeatureOutputDTO.from_entity(f) for f in features]
        )
```

### Entrada/Saida

**Entrada**: Nenhuma

**Saida**: `ListFeaturesOutputDTO`
- `features: list[FeatureOutputDTO]` - Lista ordenada por wave

**Erros**: Nenhum (retorna lista vazia se nao houver features)

---

## Notas de Implementacao

1. **UnitOfWork**: Todos use cases recebem UoW no construtor e executam dentro de `async with` para garantir transacoes.

2. **Service vs Repository**:
   - Create/Update/Delete usam FeatureService (validacoes de unicidade)
   - List usa repositorio diretamente (listagem simples sem logica)

3. **Commit implicito**: `async with uow` faz commit automatico ao sair com sucesso, rollback em caso de excecao.

4. **Delete sem retorno**: Diferente de Developer, Feature delete nao retorna informacoes adicionais (retorna None).

5. **FeatureHasStoriesException**: Contem informacoes ricas para mensagem de erro amigavel ao usuario.
