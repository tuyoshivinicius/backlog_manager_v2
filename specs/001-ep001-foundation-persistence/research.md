# Research: EP-001 Fundacao e Persistencia

**Feature**: EP-001 Fundacao e Persistencia
**Date**: 2026-02-28
**Status**: Completo

## Sumario Executivo

Este documento consolida as decisoes de pesquisa para a fundacao do Backlog Manager. Todos os itens marcados como "NEEDS CLARIFICATION" no Technical Context foram resolvidos.

---

## 1. Estrutura de Projeto Python com Poetry

### Decisao
Utilizar Poetry com src layout para gerenciamento de pacotes Python.

### Racional
- Poetry oferece lockfile deterministico (poetry.lock)
- Src layout isola codigo de producao, evitando imports acidentais de testes
- Compativel com pip install -e . para desenvolvimento
- Padrao recomendado pela comunidade Python moderna (PEP 517/518)

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| setuptools puro | Configuracao mais verbosa, sem lockfile nativo |
| pipenv | Menor adocao em projetos novos, Poetry tem melhor UX |
| flit | Menos features para projetos complexos |

### Configuracao Recomendada
```toml
[tool.poetry]
name = "backlog-manager"
version = "0.1.0"
packages = [{include = "backlog_manager", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
aiosqlite = "^0.19.0"
aiofiles = "^23.0"
pydantic = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-cov = "^4.0"
pytest-asyncio = "^0.23"
black = "^24.0"
isort = "^5.13"
mypy = "^1.8"
pre-commit = "^3.6"
pydocstyle = "^6.3"
```

---

## 2. SQLite com aiosqlite para Operacoes Assincronas

### Decisao
Utilizar aiosqlite como wrapper async sobre sqlite3 padrao do Python.

### Racional
- aiosqlite e wrapper fino sobre sqlite3, nao adiciona overhead significativo
- Suporta context managers async (async with)
- Compativel com asyncio event loop
- Permite prepared statements naturalmente
- Mantido ativamente, >5M downloads/mes no PyPI

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| sqlite3 sincrono | Bloquearia event loop, incompativel com Constitution VIII |
| SQLAlchemy async | Over-engineering para caso de uso simples, adiciona complexidade |
| databases | Abstrai demais, perdemos controle sobre schema |

### Padroes de Uso
```python
import aiosqlite

async def create_connection(db_path: str) -> aiosqlite.Connection:
    """Cria conexao async com SQLite."""
    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = aiosqlite.Row
    return conn

async def execute_query(conn: aiosqlite.Connection, query: str, params: tuple) -> list:
    """Executa query parametrizada (prepared statement)."""
    async with conn.execute(query, params) as cursor:
        return await cursor.fetchall()
```

---

## 3. Schema SQLite e Migrations

### Decisao
Schema definido em arquivo SQL puro, migrations manuais versionadas.

### Racional
- Schema SQL e legivel e portavel
- Migrations manuais dao controle total sobre alteracoes
- Evita dependencia de frameworks de migracao complexos
- Alinhado com YAGNI - sistema simples para projeto single-user

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| Alembic | Over-engineering para SQLite single-user |
| Django migrations | Depende de Django ORM inteiro |
| Schema in-code | Menos legivel, dificil auditar |

### Schema Definido (schema.sql)
```sql
-- Versao: 001
-- Data: 2026-02-28

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Developer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Feature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    wave INTEGER NOT NULL UNIQUE CHECK (wave > 0)
);

CREATE TABLE IF NOT EXISTS Story (
    id VARCHAR(20) PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS Story_Dependency (
    story_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    depends_on_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    UNIQUE(story_id, depends_on_id),
    CHECK(story_id != depends_on_id)
);

CREATE INDEX IF NOT EXISTS idx_story_status ON Story(status);
CREATE INDEX IF NOT EXISTS idx_story_developer ON Story(developer_id);
CREATE INDEX IF NOT EXISTS idx_story_feature ON Story(feature_id);
CREATE INDEX IF NOT EXISTS idx_story_priority ON Story(priority);
```

---

## 4. Hierarquia de Excecoes

### Decisao
Hierarquia plana com uma base (BacklogManagerException) e categorias especificas.

### Racional
- Permite catch generico (BacklogManagerException) ou especifico
- Warnings separados para situacoes nao-bloqueantes
- Atributos ricos (ex: path em CyclicDependencyException) para debugging
- Alinhado com Constitution XVI

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| Usar excecoes built-in apenas | Perde especificidade, dificil catch seletivo |
| Hierarquia muito profunda | Complexidade desnecessaria, viola KISS |

### Implementacao Recomendada
```python
class BacklogManagerException(Exception):
    """Excecao base para todos os erros do Backlog Manager."""
    pass

class DependencyException(BacklogManagerException):
    """Erros relacionados a dependencias entre historias."""
    pass

class CyclicDependencyException(DependencyException):
    """Ciclo detectado no grafo de dependencias."""
    def __init__(self, path: list[str], message: str | None = None):
        self.path = path
        cycle_str = " -> ".join(path)
        super().__init__(message or f"Ciclo detectado: {cycle_str}")
```

---

## 5. Sistema de Logging com Rotacao

### Decisao
Utilizar logging padrao do Python com RotatingFileHandler.

### Racional
- logging e built-in, zero dependencias extras
- RotatingFileHandler suporta rotacao por tamanho
- Formato configuravel via Formatter
- Thread-safe por padrao

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| loguru | Dependencia extra para funcionalidade built-in |
| structlog | Over-engineering para logs simples |

### Configuracao Recomendada
```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

def setup_logging() -> logging.Logger:
    """Configura logging com rotacao."""
    # Diretorio AppData no Windows
    app_data = Path(os.environ.get("APPDATA", Path.home()))
    log_dir = app_data / "BacklogManager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "backlog_manager.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("backlog_manager")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
```

---

## 6. Pipeline de Qualidade de Codigo

### Decisao
pre-commit hooks com black, isort, mypy; pytest-cov para cobertura.

### Racional
- pre-commit executa automaticamente antes de commits
- black + isort garantem formatacao consistente
- mypy em modo strict detecta erros de tipo
- pytest-cov gera relatorios de cobertura

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| CI-only validation | Feedback tardio, melhor falhar local |
| ruff ao inves de black+isort | ruff e mais rapido mas black e mais estabelecido |
| pyright ao inves de mypy | mypy tem maior compatibilidade com ecossistema |

### Configuracao pre-commit
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-aiofiles]
        args: ["--strict"]
```

---

## 7. Localizacao de Dados (AppData)

### Decisao
Utilizar %APPDATA%/BacklogManager/ como raiz para dados do usuario.

### Racional
- Padrao Windows para dados de aplicacao por usuario
- Separado de Program Files (nao requer admin)
- Persistente entre reinstalacoes do app
- Facil backup pelo usuario

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| Diretorio do executavel | Requer permissoes admin, perde em reinstalacao |
| Documents | Poluicao de pasta de usuario |
| LocalAppData | AppData e mais apropriado para dados persistentes |

### Estrutura de Diretorios
```
%APPDATA%/BacklogManager/
├── data/
│   └── backlog.db          # Banco de dados SQLite
├── logs/
│   ├── backlog_manager.log     # Log atual
│   ├── backlog_manager.log.1   # Backup 1
│   ├── backlog_manager.log.2   # Backup 2
│   └── backlog_manager.log.3   # Backup 3
└── config/                 # Reservado para configuracoes futuras
```

---

## 8. Async/Await e Integracao com Qt

### Decisao
Utilizar qasync para integracao entre asyncio e Qt event loop.

### Racional
- qasync permite rodar corrotinas no contexto do Qt
- Evita threading manual para operacoes I/O
- Compativel com PySide6
- Permite uso de await em slots

### Alternativas Consideradas
| Alternativa | Razao da Rejeicao |
|-------------|-------------------|
| Threading manual | Complexidade, race conditions |
| QThread | Mais verboso, nao aproveita async/await |
| asyncqt (abandonado) | Nao mantido, qasync e sucessor |

### Padrao de Uso
```python
import asyncio
from qasync import QEventLoop
from PySide6.QtWidgets import QApplication

def main():
    app = QApplication([])
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # ... criar janelas ...

    with loop:
        loop.run_forever()
```

---

## Resolucao de NEEDS CLARIFICATION

| Item Original | Resolucao |
|--------------|-----------|
| Primary Dependencies | Poetry, aiosqlite, aiofiles, pydantic, PySide6 |
| Storage | SQLite em %APPDATA%/BacklogManager/data/backlog.db |
| Testing | pytest + pytest-cov + pytest-asyncio |
| Target Platform | Windows 10/11 |
| Project Type | library pip-installable |
| Performance Goals | <=100ms CRUD, 500 historias |
| Constraints | Arquivo unico SQLite, zero servidor externo |
| Scale/Scope | Single-user desktop, ~500 stories |

---

## Referencias

- Poetry Documentation: https://python-poetry.org/docs/
- aiosqlite: https://aiosqlite.omnilib.dev/
- Python logging: https://docs.python.org/3/library/logging.html
- pre-commit: https://pre-commit.com/
- qasync: https://github.com/CabbageDevelopment/qasync
