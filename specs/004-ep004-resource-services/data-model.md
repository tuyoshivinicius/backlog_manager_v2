# Modelo de Dados: EP-004 Gestao de Recursos

**Data**: 2026-03-01
**Status**: Completo

## Visao Geral

Este documento define as estruturas de dados para os servicos e camada de aplicacao de gestao de recursos. As entidades Developer e Feature ja existem (EP-002); este documento foca nos **domain services**, **DTOs** e **extensoes de protocols**.

## Entidades de Dominio (Existentes)

### Developer

**Localizacao**: `src/backlog_manager/domain/entities/developer.py`

```python
@dataclass
class Developer:
    name: str           # Obrigatorio, max 100 caracteres, nao vazio
    id: int | None = None  # Auto-gerado pelo repositorio
```

**Invariantes**:
- `name` nao pode ser vazio ou apenas espacos
- `name` nao pode exceder 100 caracteres
- `id` e opcional na criacao (atribuido pelo banco)
- Nomes duplicados SAO PERMITIDOS (ver ADR-008 na spec)

### Feature

**Localizacao**: `src/backlog_manager/domain/entities/feature.py`

```python
@dataclass
class Feature:
    name: str           # Obrigatorio, max 100 caracteres, nao vazio, UNICO
    wave: int           # Obrigatorio, > 0, UNICO
    id: int | None = None  # Auto-gerado pelo repositorio
```

**Invariantes**:
- `name` nao pode ser vazio ou apenas espacos
- `name` nao pode exceder 100 caracteres
- `name` deve ser unico (validado pelo servico/banco)
- `wave` deve ser > 0
- `wave` deve ser unico (validado pelo servico/banco)

## Domain Services (Novos)

### DeveloperService

**Localizacao**: `src/backlog_manager/domain/services/developer_service.py`

```python
class DeveloperService:
    """Servico de dominio para logica de negocio de desenvolvedores."""

    def __init__(
        self,
        developer_repo: DeveloperRepository,
        story_repo: StoryRepository
    ) -> None:
        """Inicializa o servico com repositorios necessarios.

        Args:
            developer_repo: Repositorio de desenvolvedores
            story_repo: Repositorio de historias (para contagem)
        """

    async def create_developer(self, name: str) -> Developer:
        """Cria uma nova entidade Developer validada.

        Args:
            name: Nome do desenvolvedor

        Returns:
            Entidade Developer (sem ID, nao persistida)

        Raises:
            ValueError: Se nome vazio ou excede 100 caracteres
        """

    async def update_developer(
        self,
        developer_id: int,
        name: str
    ) -> Developer:
        """Busca e atualiza desenvolvedor existente.

        Args:
            developer_id: ID do desenvolvedor
            name: Novo nome

        Returns:
            Nova instancia Developer com nome atualizado

        Raises:
            ValueError: Se desenvolvedor nao encontrado
            ValueError: Se nome invalido
        """

    async def delete_developer(self, developer_id: int) -> int:
        """Deleta desenvolvedor e retorna contagem de historias desalocadas.

        Args:
            developer_id: ID do desenvolvedor

        Returns:
            Numero de historias que foram desalocadas (via ON DELETE SET NULL)

        Raises:
            ValueError: Se desenvolvedor nao encontrado
        """

    async def list_developers(self) -> Sequence[Developer]:
        """Lista todos os desenvolvedores ordenados por nome.

        Returns:
            Sequencia de desenvolvedores ordenados alfabeticamente
        """
```

**Dependencias**:
- `DeveloperRepository`: Para operacoes CRUD
- `StoryRepository`: Para `count_by_developer()` antes de delete

### FeatureService

**Localizacao**: `src/backlog_manager/domain/services/feature_service.py`

```python
class FeatureService:
    """Servico de dominio para logica de negocio de features."""

    def __init__(self, feature_repo: FeatureRepository) -> None:
        """Inicializa o servico com repositorio de features.

        Args:
            feature_repo: Repositorio de features
        """

    async def create_feature(self, name: str, wave: int) -> Feature:
        """Cria uma nova entidade Feature com validacao de unicidade.

        Args:
            name: Nome da feature
            wave: Numero da onda

        Returns:
            Entidade Feature (sem ID, nao persistida)

        Raises:
            ValueError: Se nome vazio ou excede 100 caracteres
            ValueError: Se wave <= 0
            DuplicateWaveException: Se wave ja existe em outra feature
            ValueError: Se nome ja existe em outra feature
        """

    async def update_feature(
        self,
        feature_id: int,
        name: str | None = None,
        wave: int | None = None
    ) -> Feature:
        """Busca e atualiza feature existente (parcial).

        Args:
            feature_id: ID da feature
            name: Novo nome (opcional)
            wave: Nova wave (opcional)

        Returns:
            Nova instancia Feature com campos atualizados

        Raises:
            ValueError: Se feature nao encontrada
            ValueError: Se nome invalido ou duplicado
            DuplicateWaveException: Se wave ja existe em outra feature
        """

    async def delete_feature(self, feature_id: int) -> None:
        """Deleta feature somente se nao houver historias associadas.

        Args:
            feature_id: ID da feature

        Raises:
            ValueError: Se feature nao encontrada
            FeatureHasStoriesException: Se feature tem historias associadas
        """

    async def list_features(self) -> Sequence[Feature]:
        """Lista todas as features ordenadas por wave.

        Returns:
            Sequencia de features ordenadas por wave crescente
        """
```

**Dependencias**:
- `FeatureRepository`: Para operacoes CRUD e validacoes

## DTOs - Developer

### CreateDeveloperInputDTO

**Localizacao**: `src/backlog_manager/application/dto/developer/create_developer_dto.py`

```python
class CreateDeveloperInputDTO(BaseModel):
    """DTO de entrada para criacao de desenvolvedor."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome do desenvolvedor nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")
        return v
```

### UpdateDeveloperInputDTO

**Localizacao**: `src/backlog_manager/application/dto/developer/update_developer_dto.py`

```python
class UpdateDeveloperInputDTO(BaseModel):
    """DTO de entrada para atualizacao de desenvolvedor."""

    developer_id: int
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome do desenvolvedor nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")
        return v
```

### DeveloperOutputDTO

**Localizacao**: `src/backlog_manager/application/dto/developer/developer_output_dto.py`

```python
class DeveloperOutputDTO(BaseModel):
    """DTO de saida para desenvolvedor."""

    id: int
    name: str

    @classmethod
    def from_entity(cls, entity: Developer) -> Self:
        """Converte entidade Developer para DTO.

        Args:
            entity: Entidade Developer

        Returns:
            DTO com dados da entidade
        """
        return cls(id=entity.id, name=entity.name)
```

### DeleteDeveloperOutputDTO

**Localizacao**: `src/backlog_manager/application/dto/developer/delete_developer_dto.py`

```python
class DeleteDeveloperOutputDTO(BaseModel):
    """DTO de saida para delecao de desenvolvedor."""

    developer_id: int
    stories_unassigned: int  # Contagem de historias desalocadas
```

### ListDevelopersOutputDTO

**Localizacao**: `src/backlog_manager/application/dto/developer/list_developers_dto.py`

```python
class ListDevelopersOutputDTO(BaseModel):
    """DTO de saida para listagem de desenvolvedores."""

    developers: list[DeveloperOutputDTO]
```

## DTOs - Feature

### CreateFeatureInputDTO

**Localizacao**: `src/backlog_manager/application/dto/feature/create_feature_dto.py`

```python
class CreateFeatureInputDTO(BaseModel):
    """DTO de entrada para criacao de feature."""

    name: str
    wave: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome da feature nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome da feature nao pode exceder 100 caracteres")
        return v

    @field_validator("wave")
    @classmethod
    def validate_wave(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(f"Wave deve ser > 0: {v}")
        return v
```

### UpdateFeatureInputDTO

**Localizacao**: `src/backlog_manager/application/dto/feature/update_feature_dto.py`

```python
class UpdateFeatureInputDTO(BaseModel):
    """DTO de entrada para atualizacao de feature."""

    feature_id: int
    name: str | None = None
    wave: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Nome da feature nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome da feature nao pode exceder 100 caracteres")
        return v

    @field_validator("wave")
    @classmethod
    def validate_wave(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v <= 0:
            raise ValueError(f"Wave deve ser > 0: {v}")
        return v
```

### FeatureOutputDTO

**Localizacao**: `src/backlog_manager/application/dto/feature/feature_output_dto.py`

```python
class FeatureOutputDTO(BaseModel):
    """DTO de saida para feature."""

    id: int
    name: str
    wave: int

    @classmethod
    def from_entity(cls, entity: Feature) -> Self:
        """Converte entidade Feature para DTO.

        Args:
            entity: Entidade Feature

        Returns:
            DTO com dados da entidade
        """
        return cls(id=entity.id, name=entity.name, wave=entity.wave)
```

### ListFeaturesOutputDTO

**Localizacao**: `src/backlog_manager/application/dto/feature/list_features_dto.py`

```python
class ListFeaturesOutputDTO(BaseModel):
    """DTO de saida para listagem de features."""

    features: list[FeatureOutputDTO]
```

## Extensoes de Protocol de Repositorio

### FeatureRepository - Novo Metodo

**Localizacao**: `src/backlog_manager/domain/interfaces/repositories.py`

```python
class FeatureRepository(Protocol):
    # ... metodos existentes ...

    async def get_by_name(self, name: str) -> Feature | None:
        """Busca feature pelo nome exato.

        Args:
            name: Nome da feature

        Returns:
            Feature se encontrada, None caso contrario
        """
        ...
```

### StoryRepository - Novo Metodo

**Localizacao**: `src/backlog_manager/domain/interfaces/repositories.py`

```python
class StoryRepository(Protocol):
    # ... metodos existentes ...

    async def count_by_developer(self, developer_id: int) -> int:
        """Conta historias alocadas a um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor

        Returns:
            Numero de historias alocadas (0 se nenhuma)
        """
        ...
```

## Diagrama de Relacionamentos

```text
┌─────────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │  DeveloperService│         │  FeatureService  │                 │
│  ├──────────────────┤         ├──────────────────┤                 │
│  │ - developer_repo │         │ - feature_repo   │                 │
│  │ - story_repo     │         └────────┬─────────┘                 │
│  └────────┬─────────┘                  │                           │
│           │                            │                           │
│           ▼                            ▼                           │
│  ┌──────────────────┐         ┌──────────────────┐                 │
│  │    Developer     │         │     Feature      │                 │
│  ├──────────────────┤         ├──────────────────┤                 │
│  │ id: int | None   │         │ id: int | None   │                 │
│  │ name: str        │         │ name: str (UK)   │                 │
│  └──────────────────┘         │ wave: int (UK)   │                 │
│                               └──────────────────┘                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       APPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Use Cases (Developer)          Use Cases (Feature)                 │
│  ┌─────────────────────┐       ┌─────────────────────┐             │
│  │ CreateDeveloperUC   │       │ CreateFeatureUC     │             │
│  │ UpdateDeveloperUC   │       │ UpdateFeatureUC     │             │
│  │ DeleteDeveloperUC   │       │ DeleteFeatureUC     │             │
│  │ ListDevelopersUC    │       │ ListFeaturesUC      │             │
│  └─────────────────────┘       └─────────────────────┘             │
│           │                            │                           │
│           ▼                            ▼                           │
│  DTOs (Developer)               DTOs (Feature)                     │
│  ┌─────────────────────┐       ┌─────────────────────┐             │
│  │ CreateDeveloperIn   │       │ CreateFeatureIn     │             │
│  │ UpdateDeveloperIn   │       │ UpdateFeatureIn     │             │
│  │ DeveloperOutput     │       │ FeatureOutput       │             │
│  │ DeleteDeveloperOut  │       │ ListFeaturesOut     │             │
│  │ ListDevelopersOut   │       └─────────────────────┘             │
│  └─────────────────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Legenda:
  UK = Unique Key (unicidade validada)
  UC = Use Case
  In = Input DTO
  Out = Output DTO
```

## Regras de Validacao

### Developer

| Campo | Regra | Mensagem de Erro |
|-------|-------|------------------|
| name | Nao vazio | "Nome do desenvolvedor nao pode ser vazio" |
| name | Max 100 chars | "Nome do desenvolvedor nao pode exceder 100 caracteres" |
| id (delete) | Deve existir | "Desenvolvedor nao encontrado: {id}" |

### Feature

| Campo | Regra | Mensagem de Erro |
|-------|-------|------------------|
| name | Nao vazio | "Nome da feature nao pode ser vazio" |
| name | Max 100 chars | "Nome da feature nao pode exceder 100 caracteres" |
| name | Unico | "Feature com nome 'X' ja existe" |
| wave | > 0 | "Wave deve ser > 0: {value}" |
| wave | Unico | DuplicateWaveException com nome da feature existente |
| id (delete) | Deve existir | "Feature nao encontrada: {id}" |
| id (delete) | Sem historias | FeatureHasStoriesException com contagem |

## Transicoes de Estado

### Developer

```text
[Nao Existe] --create--> [Existe]
[Existe] --update--> [Existe] (novo nome)
[Existe] --delete--> [Nao Existe]
                     └── ON DELETE SET NULL nas historias associadas
```

### Feature

```text
[Nao Existe] --create--> [Existe]
[Existe] --update--> [Existe] (novo nome/wave)
[Existe] --delete--> [Nao Existe] (somente se sem historias)
[Existe] --delete--> [ERRO] (se tem historias)
```
