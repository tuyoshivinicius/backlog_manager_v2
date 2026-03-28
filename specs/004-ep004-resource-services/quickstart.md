# Quickstart: EP-004 Gestao de Recursos

**Data**: 2026-03-01

## Pre-requisitos

- EP-001: Repositorios e UnitOfWork implementados
- EP-002: Entidades Developer e Feature validadas
- EP-003: Padrao de services/use cases/DTOs estabelecido
- Python 3.11+, Poetry instalado

## Arquivos a Criar

### 1. Domain Services

```bash
# DeveloperService
src/backlog_manager/domain/services/developer_service.py

# FeatureService
src/backlog_manager/domain/services/feature_service.py

# Atualizar __init__.py
src/backlog_manager/domain/services/__init__.py
```

### 2. DTOs - Developer

```bash
# Diretorio
src/backlog_manager/application/dto/developer/
├── __init__.py
├── create_developer_dto.py
├── update_developer_dto.py
├── delete_developer_dto.py
├── developer_output_dto.py
└── list_developers_dto.py
```

### 3. DTOs - Feature

```bash
# Diretorio
src/backlog_manager/application/dto/feature/
├── __init__.py
├── create_feature_dto.py
├── update_feature_dto.py
├── feature_output_dto.py
└── list_features_dto.py
```

### 4. Use Cases - Developer

```bash
# Diretorio
src/backlog_manager/application/use_cases/developer/
├── __init__.py
├── create_developer.py
├── update_developer.py
├── delete_developer.py
└── list_developers.py
```

### 5. Use Cases - Feature

```bash
# Diretorio
src/backlog_manager/application/use_cases/feature/
├── __init__.py
├── create_feature.py
├── update_feature.py
├── delete_feature.py
└── list_features.py
```

### 6. Extensoes de Protocol

```bash
# Atualizar
src/backlog_manager/domain/interfaces/repositories.py
# Adicionar: FeatureRepository.get_by_name, StoryRepository.count_by_developer
```

### 7. Implementacoes de Repositorio

```bash
# Atualizar
src/backlog_manager/infrastructure/database/repositories/feature_repository.py
# Adicionar: get_by_name

src/backlog_manager/infrastructure/database/repositories/story_repository.py
# Adicionar: count_by_developer
```

## Ordem de Implementacao

1. **Extensoes de Protocol** (interfaces primeiro)
2. **Implementacoes de Repositorio** (satisfazer protocols)
3. **Domain Services** (DeveloperService, FeatureService)
4. **DTOs** (input/output)
5. **Use Cases** (orquestram services e DTOs)
6. **Testes**

## Exemplo de Uso Completo

```python
import asyncio
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.application.use_cases.developer import (
    CreateDeveloperUseCase,
    ListDevelopersUseCase,
    DeleteDeveloperUseCase,
)
from backlog_manager.application.use_cases.feature import (
    CreateFeatureUseCase,
    ListFeaturesUseCase,
)
from backlog_manager.application.dto.developer import CreateDeveloperInputDTO
from backlog_manager.application.dto.feature import CreateFeatureInputDTO

async def main():
    # Inicializa UnitOfWork
    uow = SQLiteUnitOfWork()

    # === DESENVOLVEDORES ===

    # Criar desenvolvedor
    create_dev = CreateDeveloperUseCase(uow)
    dev = await create_dev.execute(CreateDeveloperInputDTO(name="Ana Silva"))
    print(f"Criado: {dev.id} - {dev.name}")

    # Listar desenvolvedores
    list_devs = ListDevelopersUseCase(uow)
    result = await list_devs.execute()
    for d in result.developers:
        print(f"  {d.id}: {d.name}")

    # === FEATURES ===

    # Criar feature
    create_feat = CreateFeatureUseCase(uow)
    feat = await create_feat.execute(
        CreateFeatureInputDTO(name="Autenticacao", wave=1)
    )
    print(f"Feature criada: {feat.id} - {feat.name} (wave {feat.wave})")

    # Listar features
    list_feats = ListFeaturesUseCase(uow)
    features = await list_feats.execute()
    for f in features.features:
        print(f"  Wave {f.wave}: {f.name}")

    # === DELETAR DESENVOLVEDOR ===

    # Deletar (retorna contagem de desalocacoes)
    delete_dev = DeleteDeveloperUseCase(uow)
    result = await delete_dev.execute(dev.id)
    print(f"Deletado ID {result.developer_id}, {result.stories_unassigned} historias desalocadas")

if __name__ == "__main__":
    asyncio.run(main())
```

## Comandos de Teste

```bash
# Executar todos os testes
cd /c/Users/tvini/projects/personal/backlog_manager_v2
poetry run pytest

# Testes especificos de EP-004
poetry run pytest tests/unit/domain/services/test_developer_service.py -v
poetry run pytest tests/unit/domain/services/test_feature_service.py -v
poetry run pytest tests/unit/application/use_cases/developer/ -v
poetry run pytest tests/unit/application/use_cases/feature/ -v

# Cobertura
poetry run pytest --cov=src/backlog_manager --cov-report=html

# Verificacao de tipos
poetry run mypy src/backlog_manager

# Formatacao
poetry run black src/backlog_manager tests
poetry run isort src/backlog_manager tests
```

## Verificacao de Conclusao

- [ ] `FeatureRepository.get_by_name()` implementado e testado
- [ ] `StoryRepository.count_by_developer()` implementado e testado
- [ ] `DeveloperService` com todos os metodos testados (100% cobertura)
- [ ] `FeatureService` com todos os metodos testados (100% cobertura)
- [ ] DTOs de Developer validando corretamente
- [ ] DTOs de Feature validando corretamente
- [ ] Use cases de Developer funcionando com transacoes
- [ ] Use cases de Feature funcionando com transacoes
- [ ] Todos os cenarios de aceitacao da spec passando
- [ ] `poetry run pytest` sem falhas
- [ ] `poetry run mypy` sem erros

## Troubleshooting

### "ValueError: Desenvolvedor nao encontrado"
Verifique se o ID existe no banco. Use `ListDevelopersUseCase` para verificar IDs disponiveis.

### "DuplicateWaveException"
Wave ja existe em outra feature. Use `ListFeaturesUseCase` para ver waves em uso.

### "FeatureHasStoriesException"
Feature tem historias associadas. Use `EditStoryUseCase` (EP-003) para desassociar historias primeiro (feature_id=None).

### Testes falhando com "table not found"
Verifique se o schema foi aplicado. Execute `SQLiteUnitOfWork` com `init_schema=True` nos fixtures de teste.
