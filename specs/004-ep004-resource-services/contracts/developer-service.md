# Contrato: DeveloperService

**Tipo**: Domain Service
**Localizacao**: `src/backlog_manager/domain/services/developer_service.py`
**Data**: 2026-03-01

## Visao Geral

Servico de dominio responsavel por logica de negocio relacionada a desenvolvedores. Encapsula operacoes CRUD com validacoes de negocio.

## Dependencias

```python
from backlog_manager.domain.interfaces.repositories import (
    DeveloperRepository,
    StoryRepository,
)
from backlog_manager.domain.entities.developer import Developer
```

## Interface

### Construtor

```python
def __init__(
    self,
    developer_repo: DeveloperRepository,
    story_repo: StoryRepository
) -> None
```

**Parametros**:
- `developer_repo`: Protocol de repositorio de desenvolvedores
- `story_repo`: Protocol de repositorio de historias (para count_by_developer)

### Metodos

#### create_developer

```python
async def create_developer(self, name: str) -> Developer
```

**Entrada**:
- `name`: Nome do desenvolvedor (sera normalizado com strip)

**Saida**:
- `Developer`: Entidade criada (id=None, nao persistida)

**Erros**:
- `ValueError("Nome do desenvolvedor nao pode ser vazio")`: Se name vazio apos strip
- `ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")`: Se len(name) > 100

**Comportamento**:
1. Normaliza name com strip()
2. Delega validacao a entidade Developer
3. Retorna entidade sem persistir

---

#### update_developer

```python
async def update_developer(self, developer_id: int, name: str) -> Developer
```

**Entrada**:
- `developer_id`: ID do desenvolvedor existente
- `name`: Novo nome (sera normalizado com strip)

**Saida**:
- `Developer`: Nova instancia com nome atualizado e mesmo ID

**Erros**:
- `ValueError("Desenvolvedor nao encontrado: {developer_id}")`: Se ID nao existe
- `ValueError`: Se name invalido (delegado a entidade)

**Comportamento**:
1. Busca desenvolvedor via `developer_repo.get_by_id()`
2. Se nao encontrado, lanca ValueError
3. Cria nova instancia Developer com id existente e name novo
4. Retorna nova instancia (persistencia e responsabilidade do use case)

---

#### delete_developer

```python
async def delete_developer(self, developer_id: int) -> int
```

**Entrada**:
- `developer_id`: ID do desenvolvedor a deletar

**Saida**:
- `int`: Numero de historias que serao desalocadas

**Erros**:
- `ValueError("Desenvolvedor nao encontrado: {developer_id}")`: Se ID nao existe

**Comportamento**:
1. Busca desenvolvedor via `developer_repo.get_by_id()`
2. Se nao encontrado, lanca ValueError
3. Conta historias via `story_repo.count_by_developer(developer_id)`
4. Deleta via `developer_repo.delete(developer_id)`
5. Retorna contagem (historias sao desalocadas pelo banco via ON DELETE SET NULL)

---

#### list_developers

```python
async def list_developers(self) -> Sequence[Developer]
```

**Entrada**: Nenhuma

**Saida**:
- `Sequence[Developer]`: Todos desenvolvedores ordenados por nome (A-Z)

**Erros**: Nenhum (lista vazia se nao houver desenvolvedores)

**Comportamento**:
1. Delega a `developer_repo.get_all()`
2. Repositorio retorna ordenado por nome

## Exemplo de Uso

```python
# Dentro de um use case
async with uow:
    service = DeveloperService(uow.developers, uow.stories)

    # Criar
    developer = await service.create_developer("Ana Silva")
    developer.id = await uow.developers.add(developer)

    # Atualizar
    updated = await service.update_developer(1, "Ana Maria Silva")
    await uow.developers.update(updated)

    # Deletar
    count = await service.delete_developer(1)
    print(f"{count} historias desalocadas")

    # Listar
    devs = await service.list_developers()
```

## Notas de Implementacao

1. **Nao persiste**: Servico cria/modifica entidades mas NAO chama add/update/delete no repositorio. Isso e responsabilidade do use case para manter controle transacional.

2. **Excecao para delete**: `delete_developer` FAZ chamar `developer_repo.delete()` pois precisa da contagem antes e o comportamento e atomico.

3. **Validacao dupla**: DTOs validam entrada, entidade valida invariantes. Servico coordena.
