# Quickstart: Corrigir Bugs de Inicialização

**Feature**: 011-fix-startup-bugs
**Date**: 2026-03-04

## Objetivo

Corrigir dois bugs críticos que impedem o funcionamento da aplicação:
1. Banco de dados não é inicializado na startup
2. Conflitos de event loop ao usar diálogos modais

## Pré-requisitos

- Python 3.11+
- Poetry instalado
- Dependências instaladas (`poetry install`)

## Correções Necessárias

### 1. Inicialização do Banco de Dados

**Arquivo**: `src/backlog_manager/presentation/app.py`

**Mudança**: Adicionar import e chamada a `init_database()`:

```python
# Adicionar import
from backlog_manager.infrastructure.database.sqlite_connection import init_database

# Em run_application(), ANTES de DIContainer.initialize():
async def run_application(db_path: Path | None = None) -> int:
    if db_path is None:
        db_path = get_default_db_path()

    logger.info("Starting Backlog Manager with database: %s", db_path)

    # ADICIONAR ESTA LINHA:
    await init_database(db_path)

    container = DIContainer.initialize(db_path)
    # ... resto do código
```

### 2. Correção do Event Loop

**Padrão**: Substituir `asyncio.create_task(...)` por `QTimer.singleShot(0, lambda: asyncio.create_task(...))` em todos os locais problemáticos.

**Arquivos e locais**:

| Arquivo | Método | Linha Aproximada |
|---------|--------|------------------|
| `main_window.py` | `_on_new_story` | ~337 |
| `main_window.py` | `_on_edit_story` | ~358 |
| `main_window.py` | `_on_delete_story` | ~379 |
| `main_window.py` | `_on_data_changed` | ~421 |
| `main_window.py` | `_on_dependency_changed` | ~427 |
| `main_window.py` | `_on_allocate` | ~441 |
| `story_dialog.py` | `__init__` | ~80 |
| `developer_dialog.py` | `__init__` | ~70 |
| `feature_dialog.py` | `__init__` | ~70 |
| `dependency_panel.py` | `__init__` | ~167 |
| `dependency_panel.py` | `_on_add_dependency` | ~258 |
| `dependency_panel.py` | `_on_remove_dependency` | ~318 |

**Adicionar import em cada arquivo**:
```python
from PySide6.QtCore import QTimer
```

## Validação

### Testar Correção 1 (Banco de Dados)

```bash
# Deletar banco existente (se houver)
rm backlog_manager.db

# Executar aplicação
poetry run python -m backlog_manager

# Esperado: Aplicação inicia sem erros
```

### Testar Correção 2 (Event Loop)

1. Iniciar aplicação
2. Criar uma nova história
3. Editar a história
4. Deletar a história
5. Gerenciar desenvolvedores
6. Gerenciar features
7. Executar alocação automática

**Esperado**: Todas as operações completam sem erros de RuntimeError

### Executar Testes Automatizados

```bash
poetry run pytest -v
```

**Esperado**: Todos os testes passam

## Troubleshooting

### Erro: "no such table: Story"
- Verifique se `init_database()` está sendo chamado em `app.py`
- Verifique se o import está correto

### Erro: "Cannot enter into task while another task is being executed"
- Verifique se `QTimer.singleShot` está sendo usado corretamente
- Verifique se o import de `QTimer` foi adicionado

### Testes falhando
- Execute `poetry install` para garantir dependências
- Verifique se não há erros de sintaxe nas mudanças
