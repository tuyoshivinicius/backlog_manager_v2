# Plano de Implementacao: EP-004 Gestao de Recursos - Servicos e Aplicacao

**Branch**: `004-ep004-resource-services` | **Data**: 2026-03-01 | **Spec**: [spec.md](./spec.md)
**Input**: Especificacao de feature de `/specs/004-ep004-resource-services/spec.md`

## Sumario

Implementacao da camada de servico de dominio e aplicacao para gestao de desenvolvedores e features. Inclui DeveloperService e FeatureService como domain services, Use Cases para operacoes CRUD, e DTOs Pydantic para transferencia de dados. Construido sobre a infraestrutura existente (EP-001), entidades validadas (EP-002), e seguindo os padroes arquiteturais estabelecidos em EP-003 (StoryService, Use Cases de Story).

## Contexto Tecnico

**Linguagem/Versao**: Python 3.11+
**Dependencias Principais**: aiosqlite (async SQLite), aiofiles (async I/O), pydantic v2 (DTOs com validacao)
**Armazenamento**: SQLite (arquivo unico, sem servidor)
**Testes**: pytest + pytest-asyncio + pytest-cov
**Plataforma Alvo**: Desktop (Windows/Linux)
**Tipo de Projeto**: Library Python (instalavel via pip)
**Objetivos de Performance**: Operacoes CRUD < 100ms
**Restricoes**: Todas as operacoes de I/O devem ser assincronas
**Escopo**: CRUD completo para Developer e Feature via servicos de dominio e use cases

## Verificacao da Constituicao

*GATE: Deve passar antes da Fase 0 de pesquisa. Reverificar apos Fase 1 de design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | OK | Domain services em `domain/services/`, Use Cases em `application/use_cases/`, DTOs em `application/dto/`. Nenhuma violacao de dependencia. |
| II. DDD | OK | Services sao stateless, delegam validacoes para entidades (Developer, Feature), usam excecoes de dominio (DuplicateWaveException, FeatureHasStoriesException). |
| III. Repository Pattern | OK | Services recebem Protocols como dependencia. Use Cases usam UnitOfWork. |
| IV. Dependency Injection | OK | Services e Use Cases recebem dependencias via construtor. |
| V. SQLite | OK | Reutiliza repositorios SQLite existentes de EP-001. |
| VI. Packaging | OK | Codigo em `src/backlog_manager/`, segue src layout. |
| VII. Estrutura de Diretorios | OK | Novos arquivos seguem estrutura estabelecida: `domain/services/*.py`, `application/use_cases/developer/*.py`, `application/dto/developer/*.py`. |
| VIII. Programacao Assincrona | OK | Todos os metodos de Services e Use Cases sao `async def`. Domain layer (entidades) permanece sincrono. |
| IX. Simplicidade | OK | Segue padroes de EP-003, sem over-engineering. |
| X. Type Hints | OK | Obrigatorios em todas as assinaturas. |
| XI. Docstrings | OK | Todas as classes e metodos publicos documentados em portugues, formato Google. |
| XII. Imports | OK | Organizados com isort. |
| XIII. Nomenclatura | OK | Classes PascalCase, metodos snake_case, constantes UPPER_SNAKE_CASE. |
| XIV. Testes | OK | Cobertura 100% para Services e Use Cases. Unitarios com mocks, integracao com SQLite real. |
| XV. Idioma | OK | Documentacao em portugues, codigo em ingles. |
| XVI. Tratamento de Erros | OK | ValueError para validacoes, DuplicateWaveException/FeatureHasStoriesException para erros de negocio. |

## Estrutura do Projeto

### Documentacao (esta feature)

```text
specs/004-ep004-resource-services/
├── plan.md              # Este arquivo
├── research.md          # Fase 0: decisoes tecnicas
├── data-model.md        # Fase 1: modelo de dados
├── quickstart.md        # Fase 1: guia rapido
└── tasks.md             # Fase 2: tarefas de implementacao (via /speckit.tasks)
```

### Codigo Fonte (raiz do repositorio)

```text
src/backlog_manager/
├── domain/
│   ├── entities/
│   │   ├── developer.py         # Existente (EP-002)
│   │   └── feature.py           # Existente (EP-002)
│   ├── services/
│   │   ├── __init__.py          # Existente
│   │   ├── story_service.py     # Existente (EP-003) - padrao a seguir
│   │   ├── developer_service.py # NOVO: Domain service para Developer
│   │   └── feature_service.py   # NOVO: Domain service para Feature
│   ├── interfaces/
│   │   └── repositories.py      # Existente - adicionar get_by_name(), count_by_developer()
│   └── exceptions/
│       └── feature.py           # Existente (DuplicateWaveException, FeatureHasStoriesException)
├── application/
│   ├── dto/
│   │   ├── story/               # Existente (EP-003) - padrao a seguir
│   │   ├── developer/           # NOVO
│   │   │   ├── __init__.py
│   │   │   ├── create_developer_dto.py
│   │   │   ├── update_developer_dto.py
│   │   │   ├── developer_output_dto.py
│   │   │   ├── delete_developer_dto.py
│   │   │   └── list_developers_dto.py
│   │   └── feature/             # NOVO
│   │       ├── __init__.py
│   │       ├── create_feature_dto.py
│   │       ├── update_feature_dto.py
│   │       ├── feature_output_dto.py
│   │       └── list_features_dto.py
│   └── use_cases/
│       ├── story/               # Existente (EP-003) - padrao a seguir
│       ├── developer/           # NOVO
│       │   ├── __init__.py
│       │   ├── create_developer.py
│       │   ├── update_developer.py
│       │   ├── delete_developer.py
│       │   └── list_developers.py
│       └── feature/             # NOVO
│           ├── __init__.py
│           ├── create_feature.py
│           ├── update_feature.py
│           ├── delete_feature.py
│           └── list_features.py
└── infrastructure/
    └── database/
        └── repositories/
            ├── developer_repository.py  # Existente - implementar count_by_developer()
            └── feature_repository.py    # Existente - implementar get_by_name()

tests/
├── unit/
│   ├── domain/
│   │   └── services/
│   │       ├── test_developer_service.py  # NOVO
│   │       └── test_feature_service.py    # NOVO
│   └── application/
│       └── use_cases/
│           ├── developer/                  # NOVO
│           │   ├── test_create_developer.py
│           │   ├── test_update_developer.py
│           │   ├── test_delete_developer.py
│           │   └── test_list_developers.py
│           └── feature/                    # NOVO
│               ├── test_create_feature.py
│               ├── test_update_feature.py
│               ├── test_delete_feature.py
│               └── test_list_features.py
└── integration/
    └── infrastructure/
        └── database/
            └── repositories/
                ├── test_developer_repository.py  # Adicionar test para count_by_developer
                └── test_feature_repository.py    # Adicionar test para get_by_name
```

**Decisao de Estrutura**: Segue a estrutura existente de EP-003, criando diretorios paralelos em `dto/developer/`, `dto/feature/`, `use_cases/developer/`, `use_cases/feature/`.

## Rastreamento de Complexidade

> Nenhuma violacao da Constituicao requer justificativa.

| Violacao | Motivo | Alternativa Mais Simples Rejeitada Porque |
|----------|--------|-------------------------------------------|
| N/A | N/A | N/A |
