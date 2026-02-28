# Quickstart: EP-001 Fundacao e Persistencia

**Feature**: EP-001 Fundacao e Persistencia
**Date**: 2026-02-28
**Status**: Completo

## Pre-requisitos

- Python 3.11+
- Poetry instalado (`pip install poetry` ou via instalador oficial)
- Git

---

## Setup do Ambiente

### 1. Clonar Repositorio

```bash
git clone <repo-url>
cd backlog_manager_v2
```

### 2. Instalar Dependencias

```bash
# Instalar Poetry (se nao instalado)
pip install poetry

# Instalar dependencias do projeto
poetry install

# Ativar ambiente virtual
poetry shell
```

### 3. Instalar Pre-commit Hooks

```bash
pre-commit install
```

### 4. Verificar Instalacao

```bash
# Importar modulo
python -c "import backlog_manager; print('OK')"

# Executar testes
pytest

# Verificar formatacao
black --check src/
isort --check src/

# Verificar tipos
mypy src/
```

---

## Estrutura do Projeto

```
backlog_manager_v2/
├── src/
│   └── backlog_manager/           # Pacote principal
│       ├── __init__.py
│       ├── domain/                # Entidades e regras de negocio
│       │   ├── entities/          # Story, Developer, Feature
│       │   ├── value_objects/     # StoryPoint, StoryStatus
│       │   ├── interfaces/        # Repository Protocols
│       │   └── exceptions/        # Hierarquia de excecoes
│       ├── application/           # Casos de uso
│       │   ├── use_cases/
│       │   └── dto/
│       ├── infrastructure/        # Implementacoes concretas
│       │   ├── database/          # SQLite, migrations
│       │   └── logging/           # Sistema de logging
│       └── presentation/          # UI (futuro)
├── tests/
│   ├── unit/                      # Testes rapidos
│   └── integration/               # Testes com I/O
├── pyproject.toml                 # Configuracao Poetry
├── .pre-commit-config.yaml        # Hooks de qualidade
└── README.md
```

---

## Comandos Essenciais

### Desenvolvimento

```bash
# Instalar em modo editavel
poetry install

# Adicionar dependencia
poetry add <pacote>

# Adicionar dependencia de dev
poetry add --group dev <pacote>

# Atualizar dependencias
poetry update
```

### Qualidade de Codigo

```bash
# Formatar codigo
black src/ tests/
isort src/ tests/

# Verificar tipos
mypy src/

# Verificar docstrings
pydocstyle src/

# Executar todos os hooks
pre-commit run --all-files
```

### Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=backlog_manager --cov-report=html

# Executar testes especificos
pytest tests/unit/
pytest tests/integration/

# Executar teste especifico
pytest tests/unit/domain/test_story.py -v
```

### Build e Publicacao

```bash
# Gerar pacote
poetry build

# Publicar no PyPI (requer credenciais)
poetry publish
```

---

## Exemplo de Uso

### Criar Entidades

```python
from backlog_manager.domain.entities import Story, Developer, Feature
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

# Criar desenvolvedor
dev = Developer(id=1, name="Joao Silva")

# Criar feature
feature = Feature(id=1, name="Autenticacao", wave=1)

# Criar historia
story = Story(
    id="AUTH-001",
    component="AUTH",
    name="Implementar login com email/senha",
    story_points=StoryPoint.MEDIUM,  # 5 pontos
    priority=1,
    status=StoryStatus.BACKLOG
)
```

### Usar Repositorios

```python
from backlog_manager.infrastructure.database import SQLiteUnitOfWork

async def example():
    async with SQLiteUnitOfWork() as uow:
        # Adicionar desenvolvedor
        dev_id = await uow.developers.add(Developer(name="Maria"))

        # Adicionar historia
        await uow.stories.add(story)

        # Buscar historias
        stories = await uow.stories.get_by_status("BACKLOG")

        # Commit automatico ao sair do contexto
```

### Tratar Excecoes

```python
from backlog_manager.domain.exceptions import (
    BacklogManagerException,
    CyclicDependencyException,
    DuplicateWaveException
)

try:
    await dependency_service.add_dependency("A", "B")
except CyclicDependencyException as e:
    print(f"Ciclo detectado: {' -> '.join(e.path)}")
except BacklogManagerException as e:
    print(f"Erro: {e}")
```

---

## Localizacao de Arquivos

| Tipo | Localizacao |
|------|-------------|
| Banco de dados | `%APPDATA%/BacklogManager/data/backlog.db` |
| Logs | `%APPDATA%/BacklogManager/logs/backlog_manager.log` |
| Configuracao | `%APPDATA%/BacklogManager/config/` |

---

## Verificacao de Saude

```bash
# Script de verificacao rapida
python -c "
import sys
import backlog_manager
print(f'Python: {sys.version}')
print(f'Backlog Manager: importado com sucesso')
"

# Verificar se banco inicializa
python -c "
import asyncio
from backlog_manager.infrastructure.database import init_database
asyncio.run(init_database())
print('Banco de dados inicializado')
"
```

---

## Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'backlog_manager'"

```bash
# Certifique-se de estar no ambiente virtual
poetry shell

# Reinstale o pacote
poetry install
```

### Erro: "PRAGMA foreign_keys = ON" nao funciona

```bash
# Verificar versao do SQLite
python -c "import sqlite3; print(sqlite3.sqlite_version)"
# Deve ser >= 3.6.19
```

### Pre-commit falha

```bash
# Atualizar hooks
pre-commit autoupdate

# Limpar cache
pre-commit clean
pre-commit install
```

### Testes falham com "database is locked"

```bash
# Usar pytest com isolamento
pytest --forked

# Ou limpar banco de testes
rm -f %APPDATA%/BacklogManager/data/test_*.db
```

---

## Proximos Passos

1. Implementar entidades de dominio (Story, Developer, Feature)
2. Implementar hierarquia de excecoes
3. Configurar sistema de logging
4. Criar schema SQLite e repositorios
5. Configurar pipeline de qualidade (pre-commit, mypy, pytest)
