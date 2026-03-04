# Research: EP-010 Testes de Integracao E2E

**Date**: 2026-03-03
**Status**: Completo

## Research Tasks

Este documento consolida a pesquisa sobre tecnologias, padroes e melhores praticas para implementacao dos testes E2E.

---

## 1. Integracao pytest-qt + qasync

### Decisao

Usar fixture `qasync_loop` com escopo `function` para cada teste E2E, integrada ao `qtbot` do pytest-qt.

### Rationale

- qasync permite executar corrotinas asyncio no event loop do Qt (QEventLoop)
- pytest-qt fornece `qtbot` para simulacao de interacoes de usuario
- Combinacao permite testar fluxos completos: GUI -> async use case -> banco

### Alternativas Consideradas

1. **pytest-asyncio puro**: Nao funciona com Qt - event loops incompativeis
2. **Mocking total de async**: Perde fidelidade do teste E2E
3. **time.sleep() para sincronizacao**: Flakey e proibido pela Constitution XIV

### Padrao de Implementacao

```python
# tests/e2e/conftest.py
import asyncio
import pytest
from qasync import QEventLoop
from pathlib import Path

@pytest.fixture
def qasync_loop(qapp):
    """Create asyncio event loop integrated with Qt."""
    loop = QEventLoop(qapp)
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
async def e2e_main_window(qasync_loop, qtbot, temp_db_path):
    """Create MainWindow with full DI integration for E2E testing."""
    from backlog_manager.presentation.container import DIContainer
    from backlog_manager.presentation.viewmodels.main_window_viewmodel import MainWindowViewModel
    from backlog_manager.presentation.views.main_window import MainWindow

    DIContainer.reset()
    container = DIContainer.initialize(temp_db_path)
    viewmodel = MainWindowViewModel(container)
    window = MainWindow(viewmodel)
    qtbot.addWidget(window)
    window.show()

    # Process pending Qt events
    await asyncio.sleep(0)
    qasync_loop.processEvents()

    yield window

    window.close()
    DIContainer.reset()
```

---

## 2. Factory Functions para Dados de Teste

### Decisao

Criar factory functions em `tests/e2e/factories.py` para geracao dinamica de dados de teste.

### Rationale

- Permite customizacao por cenario de teste
- Evita duplicacao de codigo de setup
- Facilita implementacao dos CTs com setups especificos (20 historias, 50 nos, etc.)

### Alternativas Consideradas

1. **Dados hardcoded por teste**: Duplicacao massiva
2. **Arquivo Excel externo**: Dependencia de arquivo, dificil manter
3. **Fixtures pytest parametrizadas**: Menos flexivel para cenarios complexos

### Padrao de Implementacao

```python
# tests/e2e/factories.py
from datetime import date
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.value_objects.story_point import StoryPoint
from backlog_manager.domain.value_objects.story_status import StoryStatus

def create_stories(
    count: int = 5,
    component: str = "TEST",
    with_dependencies: bool = False,
    story_points: int = 5
) -> list[Story]:
    """Factory para criar multiplas historias de teste."""
    stories = []
    for i in range(1, count + 1):
        story = Story(
            id=f"{component}-{i:03d}",
            component=component,
            name=f"Historia Teste {i}",
            story_points=StoryPoint(story_points),
            priority=i,
            status=StoryStatus.BACKLOG
        )
        stories.append(story)

    if with_dependencies and len(stories) > 1:
        # Cria cadeia de dependencias: S-002 depende de S-001, etc.
        for i in range(1, len(stories)):
            stories[i].dependencies.append(stories[i-1].id)

    return stories

def create_developers(count: int = 3) -> list[Developer]:
    """Factory para criar desenvolvedores de teste."""
    return [
        Developer(id=i, name=f"Dev {i}")
        for i in range(1, count + 1)
    ]
```

---

## 3. Sincronizacao sem time.sleep()

### Decisao

Usar `qtbot.waitSignal()`, `qtbot.waitUntil()` e `asyncio.sleep(0)` para sincronizacao.

### Rationale

- Constitution XIV proibe time.sleep() em testes E2E
- waitSignal e waitUntil sao deterministicos e event-driven
- asyncio.sleep(0) apenas processa eventos pendentes sem delay real

### Alternativas Consideradas

1. **time.sleep(0.1)**: Flakey, pode ser muito curto ou muito longo
2. **Polling manual**: Implementacao propria de wait, propenso a erros
3. **Timeouts fixos**: Nao adaptam a velocidade da maquina

### Padrao de Implementacao

```python
# Aguardar sinal emitido
async def test_allocation_completes(e2e_main_window, qtbot):
    window = e2e_main_window

    with qtbot.waitSignal(window.viewmodel.allocation_completed, timeout=30000):
        await window.viewmodel.run_allocation()

# Aguardar condicao de UI
def test_table_populated(e2e_main_window, qtbot):
    window = e2e_main_window

    qtbot.waitUntil(lambda: window.story_table.model().rowCount() > 0, timeout=5000)

    assert window.story_table.model().rowCount() == expected_count
```

---

## 4. Tratamento de Dialogos Modais

### Decisao

Usar `QTimer.singleShot()` para interagir com dialogos modais antes de serem bloqueantes.

### Rationale

- Dialogos modais bloqueiam o event loop quando exec() e chamado
- Timer programado antes de abrir o dialogo executa durante o loop modal
- Permite simular cliques em botoes do dialogo

### Alternativas Consideradas

1. **patch QMessageBox**: Perde teste real de integracao UI
2. **Chamar directamente accept()/reject()**: Nao testa fluxo real
3. **Thread separada**: Complexidade desnecessaria

### Padrao de Implementacao

```python
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog, QMessageBox

async def test_delete_with_confirmation(e2e_main_window, qtbot):
    window = e2e_main_window

    # Programa acao para quando dialogo abrir
    def handle_dialog():
        dialog = window.findChild(QMessageBox)
        if dialog:
            dialog.accept()

    QTimer.singleShot(100, handle_dialog)

    # Dispara acao que abre dialogo
    window._on_delete_story()
```

---

## 5. Configuracao CI/CD com xvfb

### Decisao

Usar `xvfb-run` no GitHub Actions para rodar testes que precisam de display.

### Rationale

- GitHub Actions runners nao tem display fisico
- xvfb (X Virtual Framebuffer) fornece display virtual headless
- Suporte maduro no ecossistema Linux

### Alternativas Consideradas

1. **QT_QPA_PLATFORM=offscreen**: Alguns widgets nao funcionam corretamente
2. **Docker com X11**: Complexidade adicional
3. **Pular testes GUI no CI**: Perde validacao E2E

### Padrao de Implementacao

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Cache Poetry dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pypoetry
          key: ${{ runner.os }}-poetry-${{ hashFiles('poetry.lock') }}

      - name: Install dependencies
        run: poetry install --with dev

      - name: Install xvfb and Qt dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 libegl1-mesa

      - name: Run tests with coverage
        run: xvfb-run -a poetry run pytest --cov=src/backlog_manager --cov-fail-under=80 --cov-report=xml -v
```

---

## 6. Mapeamento CT -> Testes

### Decisao

Criar arquivo separado por CT com setup especifico conforme SRS.

### Rationale

- Cada CT tem requisitos de setup distintos (quantidade de dados, configuracao)
- Separacao facilita execucao seletiva e manutencao
- Nomenclatura `test_ctXXX_*.py` segue padrao do spec

### Setup por CT

| CT | Setup Necessario | Assercoes Principais |
|----|------------------|---------------------|
| CT-001 | 20 historias, 5 devs, 2 features (ondas 1 e 2) | Tempo < 5s, 20/20 alocadas, ~4/dev |
| CT-002 | 50 historias com ciclo no grafo | CyclicDependencyException em < 100ms |
| CT-003 | 1 dev, 2 historias concorrentes | Ajuste de data sem deadlock |
| CT-004 | Historia 8 SP, inicio 01/04/2026 | Pula feriado Sexta-Santa (03/04) |
| CT-005 | 2 devs, SPs desbalanceados | Distribuicao por contagem de stories |

---

## 7. Metricas de Performance

### Decisao

Usar `time.perf_counter()` para medicao precisa de tempo em testes de performance.

### Rationale

- `perf_counter()` tem maior resolucao que `time.time()`
- Mede tempo real (wall clock), adequado para testes de usuario
- Resultado em float permite assercoes precisas

### Padrao de Implementacao

```python
import time

@pytest.mark.perf
@pytest.mark.e2e
async def test_perf_alocacao_100_historias(e2e_populated_db):
    """RNF-PERF-001: Alocacao <= 5s para 100 historias."""
    stories = create_stories(100)
    developers = create_developers(10)

    start = time.perf_counter()
    await allocation_use_case.execute(...)
    elapsed = time.perf_counter() - start

    # Tolerancia de 10% para CI
    assert elapsed <= 5.5, f"Alocacao levou {elapsed:.2f}s (limite: 5s + 10%)"
```

---

## 8. Isolamento entre Testes

### Decisao

Cada teste E2E usa banco SQLite isolado via `tmp_path` fixture do pytest.

### Rationale

- Evita contaminacao de estado entre testes
- Banco em memoria ou temp file e apagado automaticamente
- Permite paralelizacao com pytest-xdist

### Padrao Existente (conftest.py)

O projeto ja possui:
- `temp_db_path` fixture: Cria path temporario
- `db_connection` fixture: Conexao inicializada
- `uow` fixture: Unit of Work em contexto
- `container` fixture: DIContainer com reset

Testes E2E vao reutilizar estas fixtures existentes.

---

## Conclusao

Todas as decisoes tecnicas foram documentadas com rationale e padroes de implementacao. Nao ha itens pendentes de clarificacao - o projeto ja possui infraestrutura de testes madura que sera estendida para E2E.

**Proximos passos**: Phase 1 - Criar data-model.md e quickstart.md.
