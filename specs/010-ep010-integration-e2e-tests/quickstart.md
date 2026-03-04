# Quickstart: EP-010 Testes de Integracao E2E

**Date**: 2026-03-03
**Status**: Completo

## Pre-requisitos

1. Python 3.11+ instalado
2. Poetry instalado (`pip install poetry`)
3. Dependencias do projeto instaladas (`poetry install --with dev`)
4. Display disponivel (Windows/Linux com X11 ou xvfb)

## Setup Inicial

### 1. Verificar Ambiente

```bash
# Verificar versao Python
python --version  # Deve ser 3.11+

# Verificar Poetry
poetry --version

# Instalar dependencias
cd backlog_manager_v2
poetry install --with dev
```

### 2. Estrutura de Testes E2E

```bash
# Criar diretorio de testes E2E (se nao existir)
mkdir -p tests/e2e

# Arquivos a serem criados:
# tests/e2e/__init__.py
# tests/e2e/conftest.py
# tests/e2e/factories.py
# tests/e2e/test_*.py
```

## Executar Testes

### Executar Todos os Testes

```bash
# Todos os testes (unit + integration + e2e)
poetry run pytest

# Com cobertura
poetry run pytest --cov=src/backlog_manager --cov-fail-under=80
```

### Executar Apenas Testes E2E

```bash
# Todos E2E
poetry run pytest tests/e2e/ -v

# Apenas um arquivo
poetry run pytest tests/e2e/test_uc001_criar_priorizar_backlog.py -v

# Apenas testes marcados como e2e
poetry run pytest -m e2e -v
```

### Executar Testes de Performance

```bash
# Testes de performance
poetry run pytest -m perf -v

# Com tempo de execucao
poetry run pytest -m perf -v --durations=0
```

### Executar em CI (Linux com xvfb)

```bash
# Instalar xvfb e dependencias Qt
sudo apt-get install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 \
    libxcb-xfixes0 libegl1-mesa

# Executar com display virtual
xvfb-run -a poetry run pytest --cov=src/backlog_manager --cov-fail-under=80 -v
```

## Criar Novo Teste E2E

### Template Basico

```python
"""Test UC-XXX: [Nome do caso de uso]."""

from __future__ import annotations

import asyncio
import pytest
from PySide6.QtCore import Qt

pytestmark = [pytest.mark.e2e]


class TestUCXXX:
    """Tests for UC-XXX."""

    @pytest.mark.asyncio
    async def test_fluxo_principal(
        self, e2e_main_window, qtbot, qasync_loop
    ):
        """Test main flow of UC-XXX."""
        window = e2e_main_window

        # 1. Setup inicial
        # ...

        # 2. Executar acao via GUI
        qtbot.mouseClick(window.btn_action, Qt.LeftButton)

        # 3. Aguardar operacao completar
        with qtbot.waitSignal(window.viewmodel.operation_completed, timeout=5000):
            await asyncio.sleep(0)

        # 4. Verificar resultado
        assert window.viewmodel.stories is not None
```

### Template com Factory

```python
"""Test CT-XXX: [Nome do cenario]."""

from __future__ import annotations

import pytest
from tests.e2e.factories import create_stories, create_developers

pytestmark = [pytest.mark.e2e]


class TestCTXXX:
    """Tests for CT-XXX scenario."""

    @pytest.fixture
    async def ct_xxx_setup(self, e2e_populated_db):
        """Setup especifico para CT-XXX."""
        stories = create_stories(count=20, with_dependencies=True)
        developers = create_developers(count=5)

        for story in stories:
            await e2e_populated_db.story_repo.save(story)
        for dev in developers:
            await e2e_populated_db.developer_repo.save(dev)

        await e2e_populated_db.commit()
        return stories, developers

    @pytest.mark.asyncio
    async def test_cenario_principal(self, ct_xxx_setup, e2e_main_window):
        """Test main scenario of CT-XXX."""
        stories, developers = ct_xxx_setup
        # ...
```

## Debugar Testes

### Ver Output Detalhado

```bash
# Output completo
poetry run pytest tests/e2e/test_uc001.py -v -s

# Com print de logs
poetry run pytest tests/e2e/test_uc001.py -v --log-cli-level=DEBUG
```

### Rodar Teste Especifico

```bash
# Teste especifico por nome
poetry run pytest tests/e2e/test_uc001.py::TestUC001::test_criar_historia -v

# Com pdb em caso de falha
poetry run pytest tests/e2e/test_uc001.py -v --pdb
```

### Screenshot em Falha (opcional)

```python
# Adicionar em conftest.py para debug visual
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, qtbot):
    yield
    if request.node.rep_call.failed:
        widget = qtbot.activeWindow()
        if widget:
            widget.grab().save(f"screenshot_{request.node.name}.png")
```

## Verificar Cobertura

### Gerar Relatorio

```bash
# Relatorio terminal
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing

# Relatorio HTML
poetry run pytest --cov=src/backlog_manager --cov-report=html
open htmlcov/index.html
```

### Verificar por Modulo

```bash
# Ver cobertura de modulo especifico
poetry run pytest --cov=src/backlog_manager/domain --cov-report=term-missing
```

## Troubleshooting

### Erro: "No display"

```bash
# Windows: Display deve estar disponivel
# Linux: Usar xvfb
xvfb-run -a poetry run pytest tests/e2e/ -v

# Ou definir QT_QPA_PLATFORM
QT_QPA_PLATFORM=offscreen poetry run pytest tests/e2e/ -v  # Pode ter limitacoes
```

### Erro: "Event loop is closed"

Verificar se fixture `qasync_loop` esta sendo usada corretamente:

```python
# Correto
@pytest.mark.asyncio
async def test_example(qasync_loop, e2e_main_window):
    # qasync_loop deve ser parametro da fixture
```

### Teste Flakey

1. Aumentar timeout: `qtbot.waitSignal(..., timeout=10000)`
2. Adicionar `await asyncio.sleep(0)` para processar eventos
3. Verificar se fixture faz cleanup correto

### Cobertura Baixa

```bash
# Identificar linhas nao cobertas
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing

# Focar em modulos criticos
# domain/* deve ter 100%
# application/use_cases/* deve ter 100%
```

## Comandos Uteis

| Comando | Descricao |
|---------|-----------|
| `poetry run pytest -v` | Todos os testes |
| `poetry run pytest tests/e2e/ -v` | Apenas E2E |
| `poetry run pytest -m perf -v` | Performance |
| `poetry run pytest --cov --cov-fail-under=80` | Com cobertura |
| `poetry run pytest -x` | Para no primeiro erro |
| `poetry run pytest --lf` | Roda apenas testes que falharam |
| `poetry run pytest -k "criar"` | Testes com "criar" no nome |

## Proximos Passos

1. Criar arquivos de teste em `tests/e2e/`
2. Implementar factories em `tests/e2e/factories.py`
3. Configurar CI/CD em `.github/workflows/tests.yml`
4. Executar suite completa e verificar cobertura
