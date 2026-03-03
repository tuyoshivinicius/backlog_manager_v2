# Tasks: EP-001 Fundacao e Persistencia

**Input**: Design documents from `/specs/001-ep001-foundation-persistence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Testes incluidos conforme SC-007 (cobertura minima de 80%)

**Organization**: Tasks agrupadas por user story para implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story a qual a task pertence (e.g., US1, US2, US3, US4, US5)
- Caminhos exatos incluidos nas descricoes

## Path Conventions

- **Pacote principal**: `src/backlog_manager/`
- **Testes**: `tests/` (unit/ e integration/)
- **Config**: Raiz do repositorio (pyproject.toml, .pre-commit-config.yaml)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicializacao do projeto e estrutura basica

- [X] T001 Criar estrutura de diretorios conforme plan.md em src/backlog_manager/
- [X] T002 Inicializar projeto Poetry com pyproject.toml na raiz do repositorio
- [X] T003 [P] Criar __init__.py em todos os pacotes (domain/, application/, infrastructure/, presentation/)
- [X] T004 [P] Criar estrutura de diretorios de testes em tests/ (unit/, integration/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura core que DEVE ser completada antes de qualquer user story

**CRITICO**: Nenhum trabalho de user story pode comecar ate esta fase estar completa

- [X] T005 Criar value objects StoryPoint e StoryStatus em src/backlog_manager/domain/value_objects/
- [X] T006 [P] Criar entidade Story em src/backlog_manager/domain/entities/story.py
- [X] T007 [P] Criar entidade Developer em src/backlog_manager/domain/entities/developer.py
- [X] T008 [P] Criar entidade Feature em src/backlog_manager/domain/entities/feature.py
- [X] T009 Criar __init__.py exports em src/backlog_manager/domain/entities/__init__.py
- [X] T010 Criar __init__.py exports em src/backlog_manager/domain/value_objects/__init__.py

**Checkpoint**: Entidades de dominio prontas - implementacao de user stories pode comecar

---

## Phase 3: User Story 1 - Configuracao do Ambiente de Desenvolvimento (Priority: P1)

**Goal**: Ambiente Python configurado corretamente para desenvolvimento do Backlog Manager

**Independent Test**: Executar `pip install -e .` em ambiente limpo e verificar que o pacote e importavel

### Tests for User Story 1

- [X] T011 [P] [US1] Teste de importacao do modulo em tests/unit/test_imports.py
- [X] T012 [P] [US1] Teste de coleta pytest em tests/unit/test_project_structure.py

### Implementation for User Story 1

- [X] T013 [US1] Configurar dependencias em pyproject.toml (aiosqlite, aiofiles, pydantic)
- [X] T014 [US1] Configurar dev dependencies em pyproject.toml (pytest, pytest-cov, pytest-asyncio, black, isort, mypy, pre-commit, pydocstyle)
- [X] T015 [US1] Configurar metadata do pacote em pyproject.toml (name, version, packages)
- [X] T016 [US1] Criar src/backlog_manager/__init__.py com __version__ e exports publicos
- [X] T017 [US1] Executar poetry install e validar instalacao

**Checkpoint**: User Story 1 funcional - `pip install -e .` e `python -c "import backlog_manager"` funcionam

---

## Phase 4: User Story 2 - Banco de Dados SQLite Operacional (Priority: P1)

**Goal**: Banco de dados SQLite com schema completo para persistencia de dados

**Independent Test**: Criar conexao, executar CRUD basico, verificar constraints

### Tests for User Story 2

- [X] T018 [P] [US2] Teste de criacao de schema em tests/integration/infrastructure/database/test_schema.py
- [X] T019 [P] [US2] Teste de constraints CHECK em tests/integration/infrastructure/database/test_constraints.py
- [X] T020 [P] [US2] Teste de foreign keys em tests/integration/infrastructure/database/test_foreign_keys.py
- [X] T021 [P] [US2] Teste de rollback em tests/integration/infrastructure/database/test_transactions.py

### Implementation for User Story 2

- [X] T022 [US2] Criar schema.sql em src/backlog_manager/infrastructure/database/schema.sql
- [X] T023 [US2] Implementar sqlite_connection.py em src/backlog_manager/infrastructure/database/sqlite_connection.py
- [X] T024 [US2] Criar Repository Protocols em src/backlog_manager/domain/interfaces/repositories.py
- [X] T025 [P] [US2] Implementar StoryRepository em src/backlog_manager/infrastructure/database/repositories/story_repository.py
- [X] T026 [P] [US2] Implementar DeveloperRepository em src/backlog_manager/infrastructure/database/repositories/developer_repository.py
- [X] T027 [P] [US2] Implementar FeatureRepository em src/backlog_manager/infrastructure/database/repositories/feature_repository.py
- [X] T028 [P] [US2] Implementar StoryDependencyRepository em src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py
- [X] T029 [US2] Implementar UnitOfWork em src/backlog_manager/infrastructure/database/unit_of_work.py
- [X] T030 [US2] Criar __init__.py exports em src/backlog_manager/infrastructure/database/__init__.py
- [X] T031 [US2] Criar __init__.py exports em src/backlog_manager/infrastructure/database/repositories/__init__.py
- [X] T032 [US2] Criar funcao init_database() para inicializacao do banco

**Checkpoint**: User Story 2 funcional - banco cria tabelas, CRUD funciona, constraints enforced

---

## Phase 5: User Story 3 - Hierarquia de Excecoes Customizadas (Priority: P2)

**Goal**: Excecoes customizadas bem definidas para tratamento especifico de erros

**Independent Test**: Importar modulo de excecoes e verificar hierarquia de heranca

### Tests for User Story 3

- [X] T033 [P] [US3] Teste de hierarquia de excecoes em tests/unit/domain/exceptions/test_hierarchy.py
- [X] T034 [P] [US3] Teste de atributos de CyclicDependencyException em tests/unit/domain/exceptions/test_cyclic_dependency.py
- [X] T035 [P] [US3] Teste de warnings em tests/unit/domain/exceptions/test_warnings.py

### Implementation for User Story 3

- [X] T036 [US3] Criar BacklogManagerException em src/backlog_manager/domain/exceptions/base.py
- [X] T037 [P] [US3] Criar DependencyException e filhas em src/backlog_manager/domain/exceptions/dependency.py
- [X] T038 [P] [US3] Criar FeatureException e filhas em src/backlog_manager/domain/exceptions/feature.py
- [X] T039 [P] [US3] Criar AllocationException e filhas em src/backlog_manager/domain/exceptions/allocation.py
- [X] T040 [US3] Criar BacklogWarning e filhas em src/backlog_manager/domain/exceptions/warnings.py
- [X] T041 [US3] Criar __init__.py exports em src/backlog_manager/domain/exceptions/__init__.py

**Checkpoint**: User Story 3 funcional - excecoes importaveis e capturaveis pela base

---

## Phase 6: User Story 4 - Sistema de Logging Configurado (Priority: P2)

**Goal**: Logs persistentes em local padronizado para diagnostico e auditoria

**Independent Test**: Executar operacao logavel e verificar criacao do arquivo em AppData

### Tests for User Story 4

- [X] T042 [P] [US4] Teste de criacao de diretorio em tests/unit/infrastructure/logging/test_directory_creation.py
- [X] T043 [P] [US4] Teste de formato de log em tests/unit/infrastructure/logging/test_log_format.py
- [X] T044 [P] [US4] Teste de rotacao em tests/integration/infrastructure/logging/test_rotation.py

### Implementation for User Story 4

- [X] T045 [US4] Implementar logger_config.py em src/backlog_manager/infrastructure/logging/logger_config.py
- [X] T046 [US4] Configurar RotatingFileHandler com 10MB e 3 backups
- [X] T047 [US4] Configurar formato ISO 8601 com nivel e mensagem
- [X] T048 [US4] Implementar criacao automatica de diretorio AppData
- [X] T049 [US4] Criar __init__.py exports em src/backlog_manager/infrastructure/logging/__init__.py
- [X] T050 [US4] Integrar logger no __init__.py principal do pacote

**Checkpoint**: User Story 4 funcional - logs criados em %APPDATA%/BacklogManager/logs/

---

## Phase 7: User Story 5 - Pipeline de Qualidade de Codigo (Priority: P3)

**Goal**: Ferramentas de qualidade de codigo configuradas para padroes consistentes

**Independent Test**: Executar `pre-commit run --all-files` e verificar que todos os hooks passam

### Tests for User Story 5

- [X] T051 [P] [US5] Teste de configuracao pytest em tests/unit/test_pytest_config.py
- [X] T052 [P] [US5] Teste de cobertura minima em tests/unit/test_coverage_config.py

### Implementation for User Story 5

- [X] T053 [US5] Configurar black com line-length=88 em pyproject.toml
- [X] T054 [US5] Configurar isort compativel com black em pyproject.toml
- [X] T055 [US5] Configurar mypy strict em pyproject.toml
- [X] T056 [US5] Configurar pydocstyle Google style em pyproject.toml
- [X] T057 [US5] Configurar pytest com pytest-cov em pyproject.toml
- [X] T058 [US5] Criar .pre-commit-config.yaml com hooks black, isort, mypy
- [X] T059 [US5] Executar pre-commit install
- [X] T060 [US5] Executar pre-commit run --all-files e corrigir problemas
- [X] T061 [US5] Verificar cobertura de testes >= 80%

**Checkpoint**: User Story 5 funcional - pre-commit hooks passam, cobertura >= 80%

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam multiplas user stories

- [X] T062 [P] Adicionar type hints 100% em todos os modulos
- [X] T063 [P] Adicionar docstrings Google style em classes e metodos publicos
- [X] T064 Validar quickstart.md - executar todos os comandos e verificar funcionamento
- [X] T065 Executar pytest --cov e verificar cobertura >= 80%
- [X] T066 Executar mypy src/ e corrigir erros de tipo
- [X] T067 Code review final e cleanup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias - pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEIA todas as user stories
- **User Stories (Phase 3-7)**: Todas dependem de Foundational
  - US1 e US2 podem ser feitas em paralelo (ambas P1)
  - US3 e US4 podem ser feitas em paralelo (ambas P2)
  - US5 pode comecar apos US1 (precisa do projeto configurado)
- **Polish (Phase 8)**: Depende de todas as user stories desejadas

### User Story Dependencies

- **User Story 1 (P1)**: Pode comecar apos Foundational - Setup do projeto
- **User Story 2 (P1)**: Pode comecar apos Foundational - Banco de dados
- **User Story 3 (P2)**: Pode comecar apos Foundational - Excecoes (pode ser feita antes de US2 se necessario)
- **User Story 4 (P2)**: Pode comecar apos Foundational - Logging
- **User Story 5 (P3)**: Depende de US1 - Pipeline de qualidade precisa do projeto configurado

### Within Each User Story

- Testes DEVEM ser escritos e FALHAR antes da implementacao (TDD)
- Models/Entidades antes de services/repositories
- Infraestrutura antes de integracao
- Story completa antes de mover para proxima prioridade

### Parallel Opportunities

- Todas as tasks marcadas [P] no Setup podem rodar em paralelo
- Todas as tasks marcadas [P] no Foundational podem rodar em paralelo
- Apos Foundational: US1 e US2 podem rodar em paralelo
- Apos US1/US2: US3 e US4 podem rodar em paralelo
- Testes de cada story marcados [P] podem rodar em paralelo
- Repositories marcados [P] podem rodar em paralelo

---

## Parallel Example: User Story 2 (Banco de Dados)

```bash
# Lancar todos os testes de US2 juntos:
Task: "Teste de criacao de schema em tests/integration/infrastructure/database/test_schema.py"
Task: "Teste de constraints CHECK em tests/integration/infrastructure/database/test_constraints.py"
Task: "Teste de foreign keys em tests/integration/infrastructure/database/test_foreign_keys.py"
Task: "Teste de rollback em tests/integration/infrastructure/database/test_transactions.py"

# Lancar todos os repositories de US2 juntos (apos schema e connection):
Task: "Implementar StoryRepository em src/backlog_manager/infrastructure/database/repositories/story_repository.py"
Task: "Implementar DeveloperRepository em src/backlog_manager/infrastructure/database/repositories/developer_repository.py"
Task: "Implementar FeatureRepository em src/backlog_manager/infrastructure/database/repositories/feature_repository.py"
Task: "Implementar StoryDependencyRepository em src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py"
```

---

## Parallel Example: User Story 3 (Excecoes)

```bash
# Lancar todos os testes de US3 juntos:
Task: "Teste de hierarquia de excecoes em tests/unit/domain/exceptions/test_hierarchy.py"
Task: "Teste de atributos de CyclicDependencyException em tests/unit/domain/exceptions/test_cyclic_dependency.py"
Task: "Teste de warnings em tests/unit/domain/exceptions/test_warnings.py"

# Lancar todos os tipos de excecao juntos (apos base):
Task: "Criar DependencyException e filhas em src/backlog_manager/domain/exceptions/dependency.py"
Task: "Criar FeatureException e filhas em src/backlog_manager/domain/exceptions/feature.py"
Task: "Criar AllocationException e filhas em src/backlog_manager/domain/exceptions/allocation.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICO - bloqueia todas as stories)
3. Completar Phase 3: User Story 1 (ambiente de desenvolvimento)
4. Completar Phase 4: User Story 2 (banco de dados)
5. **PARAR E VALIDAR**: Testar US1 e US2 independentemente
6. Deploy/demo se pronto - sistema persiste dados

### Incremental Delivery

1. Completar Setup + Foundational -> Fundacao pronta
2. Adicionar User Story 1 -> Testar independentemente -> Ambiente funcional
3. Adicionar User Story 2 -> Testar independentemente -> Persistencia funcional
4. Adicionar User Story 3 -> Testar independentemente -> Excecoes funcionais
5. Adicionar User Story 4 -> Testar independentemente -> Logging funcional
6. Adicionar User Story 5 -> Testar independentemente -> Pipeline de qualidade funcional
7. Cada story adiciona valor sem quebrar stories anteriores

### Single Developer Strategy

1. Completar Setup + Foundational
2. US1 (P1) -> Validar
3. US2 (P1) -> Validar
4. US3 (P2) -> Validar
5. US4 (P2) -> Validar
6. US5 (P3) -> Validar
7. Polish -> Entrega final

---

## Summary

| Metrica | Valor |
|---------|-------|
| Total de Tasks | 67 |
| Tasks User Story 1 | 7 |
| Tasks User Story 2 | 15 |
| Tasks User Story 3 | 9 |
| Tasks User Story 4 | 9 |
| Tasks User Story 5 | 11 |
| Tasks Setup | 4 |
| Tasks Foundational | 6 |
| Tasks Polish | 6 |
| Tasks Paralelizaveis | 32 |
| MVP Scope | US1 + US2 (22 tasks) |

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica para rastreabilidade
- Cada user story deve ser independentemente completavel e testavel
- Verificar que testes falham antes de implementar
- Commit apos cada task ou grupo logico
- Parar em qualquer checkpoint para validar story independentemente
- Evitar: tasks vagas, conflitos no mesmo arquivo, dependencias cross-story que quebram independencia
