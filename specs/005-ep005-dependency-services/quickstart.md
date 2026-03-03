# Quickstart: EP-005 Dependency Services

**Date**: 2026-03-01
**Status**: Complete

## Prerequisites

- Python 3.11+
- Poetry instalado
- Dependencias do projeto instaladas (poetry install)

## Estrutura de Arquivos a Criar

```
src/backlog_manager/
  domain/services/
    dependency_service.py   # NEW
  application/
    use_cases/dependency/
      __init__.py           # NEW
      add_dependency.py     # NEW
      remove_dependency.py  # NEW
      get_dependencies.py   # NEW
      get_dependents.py     # NEW
    dto/dependency/
      __init__.py           # NEW
      add_dependency_dto.py # NEW
      remove_dependency_dto.py # NEW
      get_dependency_dto.py # NEW

tests/
  unit/
    domain/services/
      test_dependency_service.py  # NEW
    application/use_cases/dependency/
      __init__.py                  # NEW
      test_add_dependency.py       # NEW
      test_remove_dependency.py    # NEW
      test_get_dependencies.py     # NEW
      test_get_dependents.py       # NEW
  integration/
    application/use_cases/
      test_dependency_use_cases.py # NEW
```

## Ordem de Implementacao

### 1. Domain Service (independente)

```bash
# Implementar primeiro pois nao tem dependencias
src/backlog_manager/domain/services/dependency_service.py

# Testar isoladamente
pytest tests/unit/domain/services/test_dependency_service.py -v
```

### 2. DTOs (independente)

```bash
# Implementar DTOs Pydantic
src/backlog_manager/application/dto/dependency/

# Testar validacoes
pytest tests/unit/application/dto/test_dependency_dtos.py -v
```

### 3. Use Cases (dependem de 1 e 2)

```bash
# Implementar use cases em ordem:
# 1. GetDependenciesUseCase (mais simples)
# 2. GetDependentsUseCase
# 3. RemoveDependencyUseCase
# 4. AddDependencyUseCase (mais complexo)

# Testar com mocks
pytest tests/unit/application/use_cases/dependency/ -v
```

### 4. Testes de Integracao

```bash
# Testar com banco SQLite real
pytest tests/integration/application/use_cases/test_dependency_use_cases.py -v
```

## Exemplo de Uso

```python
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.application.use_cases.dependency import AddDependencyUseCase
from backlog_manager.application.dto.dependency import AddDependencyInputDTO

async def main():
    async with SQLiteUnitOfWork() as uow:
        use_case = AddDependencyUseCase(uow)

        result = await use_case.execute(
            AddDependencyInputDTO(
                story_id="AUTH-002",
                depends_on_id="AUTH-001"
            )
        )

        if result.warning:
            print(f"Warning: {result.warning.message}")

        print(f"Success: {result.success}")
```

## Comandos de Desenvolvimento

```bash
# Rodar todos os testes do epico
pytest tests/unit/domain/services/test_dependency_service.py tests/unit/application/use_cases/dependency/ -v

# Verificar types
mypy src/backlog_manager/domain/services/dependency_service.py
mypy src/backlog_manager/application/use_cases/dependency/
mypy src/backlog_manager/application/dto/dependency/

# Formatar codigo
black src/backlog_manager/domain/services/dependency_service.py
black src/backlog_manager/application/use_cases/dependency/
black src/backlog_manager/application/dto/dependency/

# Coverage
pytest --cov=src/backlog_manager/domain/services/dependency_service --cov=src/backlog_manager/application/use_cases/dependency --cov-report=term-missing
```

## Validacao Final

Antes de considerar completo:
- [ ] Todos os testes unitarios passando
- [ ] Testes de integracao passando
- [ ] mypy sem erros
- [ ] Coverage >= 80%
- [ ] black/isort aplicados
