# Quickstart: Story Completion Status

**Feature**: 024-story-completion

## Pré-requisitos

```bash
# Instalar dependências
poetry install

# Verificar testes existentes passam
poetry run pytest tests/ -x -q
```

## Sequência de Implementação

### 1. Domain — Nova exceção (sem dependências)

```
src/backlog_manager/domain/exceptions/dependency.py
  + class IncompleteDependencyException(DependencyException)

src/backlog_manager/domain/exceptions/__init__.py
  + export IncompleteDependencyException
```

### 2. Application — Fix DTO + Validação no Use Case

```
src/backlog_manager/application/dto/story/edit_story_dto.py
  ~ fix status validator: valores corretos do enum

src/backlog_manager/application/use_cases/story/edit_story.py
  ~ adicionar validação de dependências antes de transição para CONCLUIDO
```

### 3. Domain — Filtro na alocação

```
src/backlog_manager/domain/services/allocation_service.py
  ~ _is_eligible(): adicionar filtro status != CONCLUIDO
```

### 4. Presentation — Tratamento de erro na UI

```
src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py
  ~ edit_story(): capturar IncompleteDependencyException → exibir mensagem
```

## Validação Rápida

```bash
# Testes unitários (rápidos)
poetry run pytest tests/unit/ -x -q

# Testes de integração
poetry run pytest tests/integration/ -x -q

# Todos os testes
poetry run pytest tests/ -x -q
```
