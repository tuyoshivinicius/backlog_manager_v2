# Data Model: Resolucao de Issues SonarQube

**Branch**: `033-sonarqube-issues-fix` | **Date**: 2026-04-01

## N/A - Sem Alteracoes de Modelo de Dados

Esta feature e puramente de refactoring e correcao de issues de qualidade de codigo.
Nao ha alteracoes em:

- Entidades de dominio (Story, Developer, Feature, Configuration)
- Value Objects (StoryPoint, StoryStatus)
- DTOs (Application layer)
- Schema SQLite
- Interfaces de repositorio

### Unica Adicao Estrutural

**Atributo `_pending_tasks`** em classes de View/ViewModel:

```python
# Adicionado em classes que criam tasks asyncio
_pending_tasks: set[asyncio.Task[Any]] = set()
```

Isso NAO e uma entidade de dominio — e um atributo de infraestrutura na camada Presentation para gerenciamento de ciclo de vida de tasks asyncio. Nao afeta persistencia ou modelo de dados.

### Constante Extraida

```python
# Em infrastructure/database/unit_of_work.py
_CONTEXT_MANAGER_ERROR_MSG = "UnitOfWork must be used as context manager"
```

Constante de classe para eliminar literal duplicado. Nao altera comportamento ou modelo de dados.
