# Data Model: EP-010 Testes de Integracao E2E

**Date**: 2026-03-03
**Status**: Completo

## Overview

Este documento descreve as entidades de teste, fixtures e modelos de dados utilizados pela suite de testes E2E. Como EP-010 e um epico de testes, nao cria novas entidades de dominio - apenas utiliza as existentes para validacao.

---

## 1. Test Fixtures

### 1.1 E2E Fixtures (tests/e2e/conftest.py)

| Fixture | Escopo | Dependencias | Descricao |
|---------|--------|--------------|-----------|
| `qasync_loop` | function | `qapp` | Event loop asyncio integrado com Qt |
| `e2e_app` | function | `qasync_loop`, `temp_db_path` | QApplication + DIContainer configurado |
| `e2e_main_window` | function | `e2e_app`, `qtbot` | MainWindow pronta para interacao |
| `e2e_populated_db` | function | `uow` | Banco populado com dados de teste |

### 1.2 Fixture: qasync_loop

```python
@pytest.fixture
def qasync_loop(qapp):
    """Asyncio event loop integrado com Qt."""
    from qasync import QEventLoop
    loop = QEventLoop(qapp)
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()
```

**Invariantes**:
- DEVE ser usado em todos os testes E2E async
- DEVE processar eventos Qt corretamente
- NAO DEVE coexistir com outro event loop ativo

### 1.3 Fixture: e2e_main_window

```python
@pytest.fixture
async def e2e_main_window(qasync_loop, qtbot, temp_db_path):
    """MainWindow configurada para testes E2E."""
    DIContainer.reset()
    container = DIContainer.initialize(temp_db_path)
    viewmodel = MainWindowViewModel(container)
    window = MainWindow(viewmodel)
    qtbot.addWidget(window)
    window.show()
    await asyncio.sleep(0)
    yield window
    window.close()
    DIContainer.reset()
```

**Invariantes**:
- DEVE resetar DIContainer antes e depois do teste
- DEVE usar banco temporario isolado
- DEVE mostrar janela para permitir interacao

### 1.4 Fixture: e2e_populated_db

```python
@pytest.fixture
async def e2e_populated_db(uow):
    """Banco populado com dados de teste padrao."""
    # Criar 5 desenvolvedores
    for i in range(1, 6):
        await uow.developer_repo.save(Developer(id=i, name=f"Dev {i}"))

    # Criar 2 features
    await uow.feature_repo.save(Feature(id=1, name="Feature 1", wave=1))
    await uow.feature_repo.save(Feature(id=2, name="Feature 2", wave=2))

    # Criar 10 historias
    for i in range(1, 11):
        story = Story(
            id=f"TEST-{i:03d}",
            component="TEST",
            name=f"Historia {i}",
            story_points=StoryPoint(5),
            priority=i,
            status=StoryStatus.BACKLOG,
            feature_id=1 if i <= 5 else 2
        )
        await uow.story_repo.save(story)

    await uow.commit()
    yield uow
```

---

## 2. Factory Functions

### 2.1 create_stories

```python
def create_stories(
    count: int = 5,
    component: str = "TEST",
    with_dependencies: bool = False,
    story_points: int = 5,
    feature_id: int | None = None
) -> list[Story]:
```

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| count | int | 5 | Numero de historias a criar |
| component | str | "TEST" | Componente/prefixo do ID |
| with_dependencies | bool | False | Cria cadeia de dependencias |
| story_points | int | 5 | SP de cada historia |
| feature_id | int | None | ID da feature associada |

**Regras de Geracao**:
- ID segue formato `{component}-{numero:03d}` (ex: TEST-001)
- Prioridade e sequencial (1, 2, 3...)
- Status inicial e BACKLOG
- Se with_dependencies=True, cria cadeia: S-002 depende de S-001, etc.

### 2.2 create_developers

```python
def create_developers(count: int = 3) -> list[Developer]:
```

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| count | int | 3 | Numero de devs a criar |

**Regras de Geracao**:
- ID e sequencial (1, 2, 3...)
- Nome segue formato "Dev {id}"

### 2.3 create_features

```python
def create_features(count: int = 2, waves: list[int] | None = None) -> list[Feature]:
```

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| count | int | 2 | Numero de features a criar |
| waves | list[int] | None | Ondas especificas (ou sequencial) |

**Regras de Geracao**:
- ID e sequencial (1, 2, 3...)
- Nome segue formato "Feature {id}"
- Wave e sequencial se nao especificado

### 2.4 create_cyclic_graph

```python
def create_cyclic_graph(node_count: int = 50, cycle_at: int | None = None) -> dict[str, list[str]]:
```

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| node_count | int | 50 | Numero de nos no grafo |
| cycle_at | int | None | Posicao onde ciclo fecha (default: ultimo no) |

**Regras de Geracao**:
- Cria cadeia linear de dependencias
- Ultimo no (ou cycle_at) fecha ciclo voltando ao primeiro
- Usado para CT-002 (deteccao de ciclos)

---

## 3. Test Scenarios Data

### 3.1 CT-001: Backlog Completo

| Entidade | Quantidade | Configuracao |
|----------|-----------|--------------|
| Stories | 20 | 10 em wave 1, 10 em wave 2 |
| Developers | 5 | Todos ativos |
| Features | 2 | Wave 1 e Wave 2 |

**Dependencias**: Nenhuma (testa alocacao livre)

### 3.2 CT-002: Ciclo em Grafo Grande

| Entidade | Quantidade | Configuracao |
|----------|-----------|--------------|
| Stories | 50 | Cadeia linear com ciclo |
| Developers | 0 | Nao necessario |
| Features | 0 | Nao necessario |

**Dependencias**: S-001 -> S-002 -> ... -> S-050 -> S-001 (ciclo)

### 3.3 CT-003: Deadlock por Falta de Devs

| Entidade | Quantidade | Configuracao |
|----------|-----------|--------------|
| Stories | 2 | Mesmo periodo, alta carga |
| Developers | 1 | Capacidade insuficiente |
| Features | 1 | Wave 1 |

**Resultado esperado**: Ajuste de data (S-002 comeca apos S-001 terminar)

### 3.4 CT-004: Feriados em Sequencia

| Entidade | Quantidade | Configuracao |
|----------|-----------|--------------|
| Stories | 1 | 8 SP, inicio 01/04/2026 |
| Developers | 1 | Ativo |
| Features | 1 | Wave 1 |

**Feriados**: Sexta-Santa (03/04/2026) deve ser pulada

### 3.5 CT-005: Balanceamento Desigual

| Entidade | Quantidade | Configuracao |
|----------|-----------|--------------|
| Stories | 5 | 1x13SP + 4x3SP |
| Developers | 2 | Iguais em capacidade |
| Features | 1 | Wave 1 |

**Resultado esperado**: Distribuicao por contagem (nao por SP total)

---

## 4. Marcadores Pytest

### 4.1 Marcadores Existentes

| Marcador | Descricao | Uso |
|----------|-----------|-----|
| `@pytest.mark.unit` | Testes unitarios | tests/unit/ |
| `@pytest.mark.integration` | Testes de integracao | tests/integration/ |

### 4.2 Novos Marcadores (EP-010)

| Marcador | Descricao | Uso |
|----------|-----------|-----|
| `@pytest.mark.e2e` | Testes E2E com GUI | tests/e2e/ |
| `@pytest.mark.perf` | Testes de performance | tests/e2e/test_performance.py |
| `@pytest.mark.slow` | Testes > 10s | Excluidos de pre-commit |

### 4.3 Configuracao pyproject.toml

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (no I/O)",
    "integration: Integration tests (with I/O)",
    "e2e: End-to-end tests with GUI",
    "perf: Performance tests",
    "slow: Slow tests (> 10s)",
]
timeout = 30
```

---

## 5. Validacao de Entidades

### 5.1 Story (Entidade Existente)

| Campo | Tipo | Validacao |
|-------|------|-----------|
| id | str | Nao vazio, formato COMP-NNN |
| component | str | Nao vazio |
| name | str | Nao vazio |
| story_points | StoryPoint | 3, 5, 8 ou 13 |
| priority | int | >= 1 |
| status | StoryStatus | Enum valido |
| developer_id | int | None | FK existente |
| feature_id | int | None | FK existente |

### 5.2 Developer (Entidade Existente)

| Campo | Tipo | Validacao |
|-------|------|-----------|
| id | int | > 0 |
| name | str | Nao vazio |

### 5.3 Feature (Entidade Existente)

| Campo | Tipo | Validacao |
|-------|------|-----------|
| id | int | > 0 |
| name | str | Nao vazio |
| wave | int | >= 1, unico |

---

## 6. Transicoes de Estado (Testes)

### 6.1 Story Status Flow

```
BACKLOG -> DOING -> DONE
    ^         |
    +---------+  (pode voltar)
```

### 6.2 Test Execution Flow

```
test_start -> fixture_setup -> test_body -> fixture_teardown -> test_end
                   |                              |
                   v                              v
              db_created                     db_destroyed
```

---

## Conclusao

O modelo de dados para testes E2E reutiliza as entidades existentes do dominio (Story, Developer, Feature) e adiciona:

1. **Fixtures especificas**: qasync_loop, e2e_main_window, e2e_populated_db
2. **Factory functions**: Geracao flexivel de dados de teste
3. **Marcadores pytest**: e2e, perf, slow
4. **Cenarios CT**: Dados especificos por cenario de teste

Nao ha criacao de novas entidades de dominio - apenas extensao da infraestrutura de testes.
