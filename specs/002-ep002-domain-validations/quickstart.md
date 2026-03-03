# Quickstart: EP-002 Dominio Core - Entidades e Validacoes

**Date**: 2026-02-28

## Objetivo

Este guia descreve como iniciar rapidamente o desenvolvimento de EP-002, focando nas mudancas incrementais sobre EP-001.

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Ambiente virtual ativado
- EP-001 implementado e testes passando

## Setup Rapido

```bash
# Clonar/atualizar repositorio
git checkout 002-ep002-domain-validations
git pull origin 002-ep002-domain-validations

# Instalar dependencias
cd C:/Users/tvini/projects/personal/backlog_manager_v2
poetry install

# Verificar estado atual
poetry run pytest -v
```

## Arquivos a Modificar

### 1. StoryStatus (P1)

**Arquivo**: `src/backlog_manager/domain/value_objects/story_status.py`

```python
# DE (EP-001):
class StoryStatus(StrEnum):
    BACKLOG = "BACKLOG"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"

# PARA (EP-002):
class StoryStatus(StrEnum):
    BACKLOG = "BACKLOG"
    EXECUCAO = "EXECUCAO"
    TESTES = "TESTES"
    CONCLUIDO = "CONCLUIDO"
    IMPEDIDO = "IMPEDIDO"
```

### 2. Story.duration Validation (P2)

**Arquivo**: `src/backlog_manager/domain/entities/story.py`

Adicionar no `__post_init__`:

```python
if self.duration is not None and self.duration < 0:
    raise ValueError(f"Duracao deve ser >= 0: {self.duration}")
```

### 3. Auto-dependencia Validation (P2)

**Arquivo**: `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`

Adicionar no metodo `add()`:

```python
async def add(self, story_id: str, depends_on_id: str) -> None:
    # ADICIONAR: Validacao de auto-dependencia
    if story_id == depends_on_id:
        raise ValueError("Historia nao pode depender de si mesma")

    # Resto do codigo existente...
```

## Testes a Criar/Expandir

### Unit Tests

```bash
# Estrutura de testes
tests/
└── unit/
    └── domain/
        ├── entities/
        │   ├── test_story.py       # Adicionar teste duration negativo
        │   ├── test_developer.py   # Verificar cobertura existente
        │   └── test_feature.py     # Verificar cobertura existente
        └── value_objects/
            ├── test_story_point.py  # Criar se nao existir
            └── test_story_status.py # Criar - verificar 5 estados
```

### Integration Tests

```bash
tests/
└── integration/
    └── infrastructure/
        └── database/
            └── repositories/
                └── test_story_dependency_repository.py  # Adicionar teste auto-dependencia
```

## Comandos de Desenvolvimento

```bash
# Rodar todos os testes
poetry run pytest -v

# Rodar apenas testes unitarios
poetry run pytest tests/unit -v

# Rodar testes com cobertura
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing

# Verificar tipos
poetry run mypy src/backlog_manager

# Formatar codigo
poetry run black src/backlog_manager tests
poetry run isort src/backlog_manager tests

# Lint
poetry run ruff check src/backlog_manager
```

## Checklist de Implementacao

- [ ] Modificar `story_status.py` - 5 estados
- [ ] Criar `tests/unit/domain/value_objects/test_story_status.py`
- [ ] Adicionar validacao duration em `story.py`
- [ ] Adicionar teste duration negativo em `test_story.py`
- [ ] Adicionar validacao auto-dependencia em `story_dependency_repository.py`
- [ ] Adicionar teste auto-dependencia em `test_story_dependency_repository.py`
- [ ] Rodar `pytest` - todos os testes passando
- [ ] Rodar `mypy` - sem erros
- [ ] Rodar `ruff check` - sem erros
- [ ] Verificar cobertura >= 80%

## Notas Importantes

1. **Mensagens de erro**: Sempre em portugues, sem acentos
2. **Validacoes**: Executadas no `__post_init__` (fail-fast)
3. **Testes**: Manter padrao TDD - escrever teste antes da implementacao
4. **Commits**: Seguir padrao do projeto (ver CLAUDE.md)
