# Contrato: FeatureService

**Tipo**: Domain Service
**Localizacao**: `src/backlog_manager/domain/services/feature_service.py`
**Data**: 2026-03-01

## Visao Geral

Servico de dominio responsavel por logica de negocio relacionada a features. Encapsula operacoes CRUD com validacoes de unicidade de wave e nome, e protecao contra delecao de features com historias.

## Dependencias

```python
from backlog_manager.domain.interfaces.repositories import FeatureRepository
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.exceptions.feature import (
    DuplicateWaveException,
    FeatureHasStoriesException,
)
```

## Interface

### Construtor

```python
def __init__(self, feature_repo: FeatureRepository) -> None
```

**Parametros**:
- `feature_repo`: Protocol de repositorio de features

### Metodos

#### create_feature

```python
async def create_feature(self, name: str, wave: int) -> Feature
```

**Entrada**:
- `name`: Nome da feature (sera normalizado com strip)
- `wave`: Numero da onda (deve ser > 0)

**Saida**:
- `Feature`: Entidade criada (id=None, nao persistida)

**Erros**:
- `ValueError("Nome da feature nao pode ser vazio")`: Se name vazio apos strip
- `ValueError("Nome da feature nao pode exceder 100 caracteres")`: Se len(name) > 100
- `ValueError("Wave deve ser > 0: {wave}")`: Se wave <= 0
- `DuplicateWaveException(wave, existing_name)`: Se wave ja existe
- `ValueError("Feature com nome '{name}' ja existe")`: Se nome ja existe

**Comportamento**:
1. Normaliza name com strip()
2. Verifica wave > 0 (fail-fast antes de consultas)
3. Verifica unicidade de wave via `feature_repo.get_by_wave(wave)`
4. Se wave existe, lanca DuplicateWaveException com nome da feature existente
5. Verifica unicidade de nome via `feature_repo.get_by_name(name)`
6. Se nome existe, lanca ValueError
7. Cria entidade Feature (validacoes de invariantes pela entidade)
8. Retorna entidade sem persistir

---

#### update_feature

```python
async def update_feature(
    self,
    feature_id: int,
    name: str | None = None,
    wave: int | None = None
) -> Feature
```

**Entrada**:
- `feature_id`: ID da feature existente
- `name`: Novo nome (opcional, sera normalizado se fornecido)
- `wave`: Nova wave (opcional)

**Saida**:
- `Feature`: Nova instancia com campos atualizados

**Erros**:
- `ValueError("Feature nao encontrada: {feature_id}")`: Se ID nao existe
- `ValueError`: Se name invalido
- `DuplicateWaveException`: Se wave ja existe em OUTRA feature
- `ValueError("Feature com nome '{name}' ja existe")`: Se nome ja existe em OUTRA feature

**Comportamento**:
1. Busca feature via `feature_repo.get_by_id(feature_id)`
2. Se nao encontrada, lanca ValueError
3. Se wave fornecida e diferente da atual:
   - Verifica wave > 0
   - Verifica unicidade via `get_by_wave(wave)`
   - Se existe e ID diferente, lanca DuplicateWaveException
4. Se name fornecido e diferente do atual:
   - Normaliza com strip()
   - Verifica unicidade via `get_by_name(name)`
   - Se existe e ID diferente, lanca ValueError
5. Cria nova instancia Feature com valores atualizados
6. Retorna nova instancia (persistencia e responsabilidade do use case)

---

#### delete_feature

```python
async def delete_feature(self, feature_id: int) -> None
```

**Entrada**:
- `feature_id`: ID da feature a deletar

**Saida**: None

**Erros**:
- `ValueError("Feature nao encontrada: {feature_id}")`: Se ID nao existe
- `FeatureHasStoriesException(feature_id, feature_name, story_count)`: Se tem historias

**Comportamento**:
1. Busca feature via `feature_repo.get_by_id(feature_id)`
2. Se nao encontrada, lanca ValueError
3. Verifica se tem historias via `feature_repo.has_stories(feature_id)`
4. Se tem historias:
   - Conta historias (pode usar len(get_by_feature) ou metodo dedicado)
   - Lanca FeatureHasStoriesException com contagem
5. Deleta via `feature_repo.delete(feature_id)`

---

#### list_features

```python
async def list_features(self) -> Sequence[Feature]
```

**Entrada**: Nenhuma

**Saida**:
- `Sequence[Feature]`: Todas features ordenadas por wave (crescente)

**Erros**: Nenhum (lista vazia se nao houver features)

**Comportamento**:
1. Delega a `feature_repo.get_all()`
2. Repositorio retorna ordenado por wave

## Exemplo de Uso

```python
# Dentro de um use case
async with uow:
    service = FeatureService(uow.features)

    # Criar
    feature = await service.create_feature("Autenticacao", wave=1)
    feature.id = await uow.features.add(feature)

    # Atualizar (parcial)
    updated = await service.update_feature(1, wave=2)
    await uow.features.update(updated)

    # Deletar (falha se tem historias)
    try:
        await service.delete_feature(1)
    except FeatureHasStoriesException as e:
        print(f"Nao pode deletar: {e.story_count} historias associadas")

    # Listar
    features = await service.list_features()
```

## Notas de Implementacao

1. **Validacao fail-fast**: Verifica unicidades ANTES de criar entidade para mensagens de erro melhores.

2. **Exclusao de self em update**: Ao verificar unicidade no update, exclui a propria feature da verificacao comparando IDs.

3. **DuplicateWaveException**: Inclui `existing_feature_name` para mensagem informativa ao usuario.

4. **FeatureHasStoriesException**: Inclui `story_count` para informar quantas historias bloqueiam a delecao.

5. **Delete faz persistencia**: Similar a DeveloperService, `delete_feature` chama `feature_repo.delete()` diretamente pois a validacao de historias e atomica com a delecao.
