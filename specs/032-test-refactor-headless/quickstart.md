# Quickstart: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Feature**: 032-test-refactor-headless
**Date**: 2026-03-31

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Repositorio clonado na branch `032-test-refactor-headless`

## Setup

```bash
# Instalar dependencias
poetry install

# Verificar estado atual dos testes (com ignores do CI)
poetry run pytest tests/unit tests/integration \
    --ignore=tests/unit/presentation \
    --ignore=tests/integration/presentation \
    -m "not slow" \
    --cov=src/backlog_manager \
    --cov-report=term-missing
```

## Fluxo de Implementacao

### 1. Corrigir Medicao de Cobertura

```bash
# Executar cobertura SEM ignores para ver estado real
poetry run pytest tests/unit tests/integration \
    --ignore=tests/unit/presentation \
    --ignore=tests/integration/presentation \
    --cov=src/backlog_manager \
    --cov-report=html

# Abrir relatorio HTML
open htmlcov/index.html
```

### 2. Remover Testes E2E

```bash
# Migrar factories primeiro
cp tests/e2e/factories.py tests/factories.py

# Remover diretorio E2E
rm -rf tests/e2e/

# Verificar que nada quebrou
poetry run pytest tests/unit tests/integration \
    --ignore=tests/unit/presentation \
    --ignore=tests/integration/presentation
```

### 3. Reescrever Testes Headless

**Padrao de mock para ViewModels (QObject)**:

```python
"""Exemplo: test_allocation_viewmodel.py headless."""
import sys
from unittest.mock import MagicMock, AsyncMock, patch

# Mock PySide6 antes de importar o modulo sob teste
mock_pyside6 = MagicMock()
mock_qt_core = MagicMock()

# Criar mock de Signal que registra emissoes
class MockSignal:
    def __init__(self, *args):
        self.emissions = []
    def emit(self, *args):
        self.emissions.append(args)
    def connect(self, slot):
        pass
    def disconnect(self, slot=None):
        pass

mock_qt_core.Signal = MockSignal
mock_qt_core.QObject = object  # Substitui QObject por object puro

with patch.dict("sys.modules", {
    "PySide6": mock_pyside6,
    "PySide6.QtCore": mock_qt_core,
    "PySide6.QtWidgets": MagicMock(),
    "PySide6.QtGui": MagicMock(),
}):
    from backlog_manager.presentation.viewmodels.allocation_viewmodel import (
        AllocationViewModel,
    )

class TestAllocationViewModel:
    def test_load_data(self):
        container = MagicMock()
        vm = AllocationViewModel(container)
        # Testar logica de negocio sem GUI
        assert vm is not None
```

**Padrao de mock para QAbstractTableModel**:

```python
"""Exemplo: test_story_table_model.py headless."""
from unittest.mock import MagicMock, patch

mock_qt_core = MagicMock()
mock_qt_core.QAbstractTableModel = object
mock_qt_core.Qt = MagicMock()
mock_qt_core.QModelIndex = MagicMock
mock_qt_core.Signal = MagicMock()

with patch.dict("sys.modules", {
    "PySide6": MagicMock(),
    "PySide6.QtCore": mock_qt_core,
    "PySide6.QtWidgets": MagicMock(),
    "PySide6.QtGui": MagicMock(),
}):
    from backlog_manager.presentation.viewmodels.story_table_model import (
        StoryTableModel,
    )
```

### 4. Adicionar Pragmas

```python
# Em src/backlog_manager/presentation/app.py
# Adicionar no topo da classe ou funcao principal:
class BacklogManagerApp:  # pragma: no cover
    ...
```

### 5. Atualizar CI

```yaml
# .github/workflows/ci.yml — ANTES
- name: Test with coverage
  run: |
    poetry run pytest tests/unit tests/integration \
      -p no:pytest-qt \
      --ignore=tests/unit/presentation \
      --ignore=tests/integration/presentation \
      ...

# .github/workflows/ci.yml — DEPOIS
- name: Test with coverage
  run: |
    poetry run pytest tests/unit tests/integration \
      -m "not slow" \
      --cov=src/backlog_manager \
      --cov-report=xml \
      --cov-report=term-missing
```

### 6. Remover Dependencias Qt de Dev

```bash
# Remover pytest-qt das dev dependencies
poetry remove --group dev pytest-qt

# Verificar que tudo ainda funciona
poetry run pytest tests/unit tests/integration
```

## Verificacao Final

```bash
# Suite completa sem ignores, sem pytest-qt
poetry run pytest tests/unit tests/integration \
    --cov=src/backlog_manager \
    --cov-report=term-missing

# Verificar meta: >= 90% cobertura global
# Verificar: zero erros de import PySide6
# Verificar: zero testes skipados
```

## Comandos Uteis

```bash
# Ver cobertura por arquivo (ordenado por %)
poetry run pytest tests/ --cov=src/backlog_manager --cov-report=term-missing | sort -t% -k2 -n

# Verificar imports de PySide6 em testes
grep -r "from PySide6" tests/ --include="*.py"
grep -r "import PySide6" tests/ --include="*.py"

# Verificar testes skipados
grep -r "pytest.mark.skip\|pytest.mark.xfail\|@skip" tests/ --include="*.py"

# Verificar uso de pytest-qt fixtures
grep -r "qtbot\|qapp\|qasync_loop" tests/ --include="*.py"
```
