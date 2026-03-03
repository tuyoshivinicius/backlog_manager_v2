# Quickstart: EP-008 Interface Grafica

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- EP-001 a EP-007 implementados e funcionais

## Setup

### 1. Instalar Dependencias

```bash
# Adicionar novas dependencias ao projeto
poetry add PySide6@^6.6.1 qasync@^0.27.1

# Adicionar dependencias de desenvolvimento
poetry add --group dev pytest-qt@^4.4
```

### 2. Atualizar pyproject.toml

```toml
[tool.poetry.scripts]
backlog-manager = "backlog_manager.presentation.app:main"

[tool.pytest.ini_options]
qt_api = "pyside6"
```

### 3. Criar Estrutura de Diretorios

```bash
mkdir -p src/backlog_manager/presentation/views
mkdir -p src/backlog_manager/presentation/viewmodels
touch src/backlog_manager/presentation/__init__.py
touch src/backlog_manager/presentation/views/__init__.py
touch src/backlog_manager/presentation/viewmodels/__init__.py
```

## Executar Aplicacao

```bash
# Via poetry script
poetry run backlog-manager

# Via modulo
poetry run python -m backlog_manager
```

## Executar Testes

```bash
# Todos os testes
poetry run pytest

# Apenas testes de apresentacao
poetry run pytest tests/unit/presentation/ tests/integration/presentation/

# Com cobertura
poetry run pytest --cov=src/backlog_manager/presentation
```

## Ordem de Implementacao Sugerida

### Fase 1: Infraestrutura
1. DIContainer (container.py)
2. Entry point (app.py, __main__.py)

### Fase 2: Modelos e ViewModels
1. StoryTableModel (QAbstractTableModel)
2. MainWindowViewModel
3. StoryDialogViewModel
4. AllocationViewModel

### Fase 3: Views Principais
1. MainWindow (QMainWindow)
2. StoryTableView (QTableView)
3. StoryDialog (QDialog)

### Fase 4: Views Secundarias
1. DeveloperDialog
2. FeatureDialog
3. DependencyPanel
4. ConfigPanel
5. MetricsPanel
6. WarningsPanel
7. ConfirmDeleteDialog

### Fase 5: Integracao
1. Atalhos de teclado
2. Tratamento de erros
3. Testes de integracao

## Exemplo Minimo

```python
# app.py
import sys
import asyncio

from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.main_window import MainWindow


async def run_app() -> None:
    container = DIContainer.initialize("backlog_manager.db")
    await container.setup()

    window = MainWindow(container.main_window_viewmodel)
    window.show()

    # Carregar dados iniciais
    await container.main_window_viewmodel.load_stories()

    # Event loop
    while window.isVisible():
        await asyncio.sleep(0.1)


def main() -> None:
    app = QApplication(sys.argv)
    asyncio.run(run_app(), loop_factory=QEventLoop)


if __name__ == "__main__":
    main()
```

## Troubleshooting

### Erro: "Container nao inicializado"
Certifique-se de chamar DIContainer.initialize() antes de DIContainer.get_instance()

### Erro: "UnitOfWork nao inicializado"
Certifique-se de chamar await container.setup() antes de usar use cases

### Testes crasham aleatoriamente
Conhecido issue com PySide6 + qasync. Usar -x para parar no primeiro erro e --forked se disponivel.

### UI nao responsiva durante alocacao
Verificar se AllocationViewModel usa @asyncSlot() e se botao esta desabilitado durante execucao.
