# Research: Corrigir Bugs de Inicialização

**Feature**: 011-fix-startup-bugs
**Date**: 2026-03-04

## Resumo

Este documento consolida a pesquisa realizada para resolver os bugs de inicialização da aplicação. Não há "NEEDS CLARIFICATION" pois a análise do código fonte revelou claramente as causas raiz.

## Bug 1: Tabelas do Banco de Dados Não Existem

### Decisão
Adicionar chamada a `init_database(db_path)` em `run_application()` antes de `DIContainer.initialize()`.

### Racional
- A função `init_database()` já existe em `sqlite_connection.py` (linhas 49-64)
- O schema SQL usa `IF NOT EXISTS` para todas as tabelas
- Os testes já chamam `init_database()` explicitamente (ver `tests/e2e/conftest.py:87`)
- A aplicação simplesmente esqueceu de chamar esta função no startup

### Alternativas Consideradas

| Alternativa | Rejeitada Porque |
|-------------|------------------|
| Inicializar no DIContainer | Viola separação de responsabilidades - container não deve fazer I/O |
| Lazy initialization | Adiciona complexidade desnecessária para um problema simples |
| Migration system | Over-engineering - schema já usa IF NOT EXISTS |

### Implementação
```python
# Em app.py, run_application()
from backlog_manager.infrastructure.database.sqlite_connection import init_database

async def run_application(db_path: Path | None = None) -> int:
    if db_path is None:
        db_path = get_default_db_path()

    # ADICIONAR: Inicializar banco antes do container
    await init_database(db_path)

    container = DIContainer.initialize(db_path)
    # ...
```

## Bug 2: Conflito de Event Loop asyncio/qasync

### Decisão
Usar `QTimer.singleShot(0, lambda: asyncio.create_task(...))` para agendar tasks assíncronas após diálogos modais.

### Racional
- `dialog.exec()` roda um event loop Qt aninhado bloqueante
- `asyncio.create_task()` chamado imediatamente após `dialog.exec()` conflita com o event loop principal
- `QTimer.singleShot(0, ...)` agenda execução para o próximo ciclo do event loop Qt
- Isso permite que o qasync processe a task sem conflitos

### Alternativas Consideradas

| Alternativa | Rejeitada Porque |
|-------------|------------------|
| QueuedConnection signals | Mais complexo, requer refatoração significativa |
| Usar dialog.open() (não-modal) | Mudaria UX da aplicação (diálogos não bloqueariam) |
| asyncSlot decorator | Requer biblioteca adicional (qasync_slot) |
| asyncio.ensure_future | Mesmo problema que create_task |

### Implementação

**Padrão para callbacks após dialog.exec():**
```python
# ANTES (problemático)
if dialog.exec():
    asyncio.create_task(self._viewmodel.load_stories())

# DEPOIS (corrigido)
if dialog.exec():
    QTimer.singleShot(0, lambda: asyncio.create_task(self._viewmodel.load_stories()))
```

**Padrão para tasks em __init__ de diálogos:**
```python
# ANTES (problemático)
def __init__(self, ...):
    asyncio.create_task(self._load_features())

# DEPOIS (corrigido)
def __init__(self, ...):
    QTimer.singleShot(0, lambda: asyncio.create_task(self._load_features()))
```

### Arquivos Afetados

| Arquivo | Locais de Mudança |
|---------|-------------------|
| `main_window.py` | `_on_new_story`, `_on_edit_story`, `_on_delete_story`, `_on_data_changed`, `_on_dependency_changed`, `_on_allocate` |
| `story_dialog.py` | `__init__` (load_features) |
| `developer_dialog.py` | `__init__` (load_developers) |
| `feature_dialog.py` | `__init__` (load_features) |
| `dependency_panel.py` | `__init__`, `_on_add_dependency`, `_on_remove_dependency` |

## Referências

- qasync documentation: https://github.com/CabbageDevelopment/qasync
- Qt Event Loop: https://doc.qt.io/qt-6/threads-qobject.html
- asyncio task scheduling: https://docs.python.org/3/library/asyncio-task.html
