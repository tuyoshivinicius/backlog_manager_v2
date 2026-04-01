# Quickstart: Cobertura de Testes 90% e Quality Gate SonarQube

**Feature**: 036-test-coverage-90 | **Date**: 2026-04-01

## Pré-requisitos

- Python 3.11+ instalado
- Poetry instalado (`pip install poetry`)
- Dependências do projeto instaladas (`poetry install`)

## Comandos Essenciais

### Executar todos os testes com cobertura

```bash
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing --cov-report=xml -m "not slow"
```

### Executar testes de um arquivo específico

```bash
poetry run pytest tests/unit/application/test_edit_story.py -v
```

### Verificar cobertura de um arquivo específico

```bash
poetry run pytest --cov=src/backlog_manager/application/use_cases/story/edit_story.py --cov-report=term-missing tests/unit/application/test_edit_story.py
```

### Gerar relatório HTML de cobertura

```bash
poetry run pytest --cov=src/backlog_manager --cov-report=html -m "not slow"
# Abrir htmlcov/index.html no navegador
```

### Executar análise SonarQube local (requer sonar-scanner)

```bash
sonar-scanner
```

## Fluxo de Trabalho

1. **Alinhar exclusões** → Editar `sonar-project.properties`
2. **Verificar impacto** → Executar `sonar-scanner` e checar cobertura no SonarCloud
3. **Identificar gaps** → Executar pytest-cov e analisar `term-missing`
4. **Escrever testes** → Seguir padrões de `tests/unit/` existentes
5. **Validar** → Re-executar pytest-cov e confirmar >= 90%
6. **CI/CD** → Push para branch, verificar Quality Gate no SonarCloud

## Padrões de Teste

### Teste unitário de use case (async)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.unit
async def test_use_case_happy_path():
    repo = AsyncMock()
    uow = AsyncMock()
    use_case = SomeUseCase(repo, uow)

    repo.find_by_id.return_value = some_entity
    result = await use_case.execute(input_dto)

    assert result is not None
    repo.find_by_id.assert_called_once_with(expected_id)
```

### Teste unitário de viewmodel (headless)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tests.headless_mocks import MockQObject

@pytest.mark.unit
async def test_viewmodel_loads_data():
    use_case = AsyncMock()
    use_case.execute.return_value = [some_dto]

    vm = SomeViewModel(use_case)
    await vm.load_data()

    assert len(vm.items) == 1
```

### Teste de DTO com validação

```python
import pytest

@pytest.mark.unit
def test_dto_with_optional_fields():
    dto = EditStoryDTO(story_id=1, name="Updated")
    assert dto.name == "Updated"
    assert dto.story_points is None  # campo opcional
```

## Arquivos-Chave

| Arquivo | Propósito |
|---|---|
| `sonar-project.properties` | Configuração SonarQube (exclusões de cobertura) |
| `pyproject.toml` | Configuração pytest-cov (exclusões, threshold) |
| `tests/conftest.py` | Fixtures compartilhadas (DB, DI, async) |
| `tests/factories.py` | Builders de objetos de teste |
| `tests/headless_mocks.py` | Mocks PySide6 para testes sem display |
