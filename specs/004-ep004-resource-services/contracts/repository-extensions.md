# Contrato: Extensoes de Repository Protocol

**Tipo**: Domain Interfaces
**Localizacao**: `src/backlog_manager/domain/interfaces/repositories.py`
**Data**: 2026-03-01

## Visao Geral

Extensoes aos protocols de repositorio existentes para suportar as funcionalidades de EP-004.

---

## FeatureRepository - Novo Metodo

### get_by_name

**Adicionar ao Protocol existente**:

```python
class FeatureRepository(Protocol):
    # ... metodos existentes ...

    async def get_by_name(self, name: str) -> Feature | None:
        """Busca feature pelo nome exato.

        Args:
            name: Nome da feature (case-sensitive)

        Returns:
            Feature se encontrada, None caso contrario

        Note:
            Busca e case-sensitive conforme default SQLite.
        """
        ...
```

### Implementacao SQLite

**Arquivo**: `src/backlog_manager/infrastructure/database/repositories/feature_repository.py`

```python
async def get_by_name(self, name: str) -> Feature | None:
    async with self._conn.execute(
        "SELECT id, name, wave FROM features WHERE name = ?",
        (name,)
    ) as cursor:
        row = await cursor.fetchone()
        if row is None:
            return None
        return self._row_to_feature(row)
```

### Caso de Uso

Validacao de unicidade de nome no FeatureService:

```python
async def create_feature(self, name: str, wave: int) -> Feature:
    # Verifica unicidade de nome
    existing = await self._repo.get_by_name(name)
    if existing:
        raise ValueError(f"Feature com nome '{name}' ja existe")
    # ...
```

---

## StoryRepository - Novo Metodo

### count_by_developer

**Adicionar ao Protocol existente**:

```python
class StoryRepository(Protocol):
    # ... metodos existentes ...

    async def count_by_developer(self, developer_id: int) -> int:
        """Conta historias alocadas a um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor

        Returns:
            Numero de historias alocadas (0 se nenhuma)

        Note:
            Mais eficiente que len(get_by_developer()) pois
            nao carrega todas as entidades.
        """
        ...
```

### Implementacao SQLite

**Arquivo**: `src/backlog_manager/infrastructure/database/repositories/story_repository.py`

```python
async def count_by_developer(self, developer_id: int) -> int:
    async with self._conn.execute(
        "SELECT COUNT(*) FROM stories WHERE developer_id = ?",
        (developer_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row[0] if row else 0
```

### Caso de Uso

Retornar contagem de historias desalocadas no DeveloperService:

```python
async def delete_developer(self, developer_id: int) -> int:
    # Conta ANTES de deletar (ON DELETE SET NULL vai zerar)
    count = await self._story_repo.count_by_developer(developer_id)
    await self._repo.delete(developer_id)
    return count
```

---

## Resumo de Alteracoes

| Protocol | Metodo | Assinatura | Retorno |
|----------|--------|------------|---------|
| FeatureRepository | get_by_name | `(name: str)` | `Feature \| None` |
| StoryRepository | count_by_developer | `(developer_id: int)` | `int` |

## Testes de Integracao

### test_feature_repository.py

```python
@pytest.mark.asyncio
async def test_get_by_name_returns_feature_when_exists(self):
    # Arrange
    feature = Feature(name="Auth", wave=1)
    await self.repo.add(feature)

    # Act
    result = await self.repo.get_by_name("Auth")

    # Assert
    assert result is not None
    assert result.name == "Auth"
    assert result.wave == 1

@pytest.mark.asyncio
async def test_get_by_name_returns_none_when_not_exists(self):
    # Act
    result = await self.repo.get_by_name("NonExistent")

    # Assert
    assert result is None

@pytest.mark.asyncio
async def test_get_by_name_is_case_sensitive(self):
    # Arrange
    await self.repo.add(Feature(name="Auth", wave=1))

    # Act
    result = await self.repo.get_by_name("auth")

    # Assert
    assert result is None  # Case-sensitive
```

### test_story_repository.py

```python
@pytest.mark.asyncio
async def test_count_by_developer_returns_correct_count(self):
    # Arrange
    dev_id = 1
    for i in range(3):
        story = Story(id=f"TEST-{i:03d}", ...)
        story.developer_id = dev_id
        await self.repo.add(story)

    # Act
    count = await self.repo.count_by_developer(dev_id)

    # Assert
    assert count == 3

@pytest.mark.asyncio
async def test_count_by_developer_returns_zero_when_none(self):
    # Act
    count = await self.repo.count_by_developer(999)

    # Assert
    assert count == 0
```
