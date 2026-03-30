# Quickstart: Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Date**: 2026-03-29

---

## Pre-requisitos

- Python 3.11+
- Poetry (dependencias ja instaladas)
- Branch `021-estilizacao-dialogs` checked out

## Executar Testes

```bash
# Todos os testes
poetry run pytest tests/ -v

# Apenas testes unitarios do ViewModel
poetry run pytest tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py -v

# Apenas testes de integracao dos dialogs
poetry run pytest tests/integration/presentation/views/ -v

# Teste especifico
poetry run pytest tests/integration/presentation/views/test_story_dialog.py -v -k "test_developer"
```

## Executar Aplicacao

```bash
poetry run python -m backlog_manager
```

## Verificar Qualidade

```bash
# Formatacao
poetry run black src/ tests/
poetry run isort src/ tests/

# Type checking
poetry run mypy src/backlog_manager/

# Cobertura
poetry run pytest tests/ --cov=src/backlog_manager --cov-report=term-missing
```

## Arquivos Chave para Implementacao

### Modificacoes

| Arquivo | O que muda |
|---------|-----------|
| `src/backlog_manager/application/dto/story/edit_story_dto.py` | +developer_id field |
| `src/backlog_manager/application/use_cases/story/edit_story.py` | +developer_id propagation |
| `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py` | +developer_id, +load_developers, +validate_field |
| `src/backlog_manager/presentation/views/story_dialog.py` | +developer combo, +validation UI, +objectNames |
| `src/backlog_manager/presentation/views/developer_dialog.py` | +icons, +hover, +empty state, +objectNames |
| `src/backlog_manager/presentation/views/feature_dialog.py` | +"Onda N — Nome", +empty state, +objectNames |
| `src/backlog_manager/presentation/views/confirm_delete_dialog.py` | +alert icon, +factory methods, +objectNames |
| `src/backlog_manager/presentation/theme/stylesheet.qss` | +dialog QSS rules |

### Novos Arquivos

| Arquivo | Descricao |
|---------|-----------|
| `src/backlog_manager/presentation/views/progress_dialog.py` | Dialog de progresso modal |
| `src/backlog_manager/presentation/views/result_dialog.py` | Dialog de resultado |
| `tests/integration/presentation/views/test_confirm_delete_dialog.py` | Testes do confirm delete |
| `tests/integration/presentation/views/test_progress_dialog.py` | Testes do progress dialog |
| `tests/integration/presentation/views/test_result_dialog.py` | Testes do result dialog |

## Ordem de Implementacao Sugerida

1. **DTO + Use Case** — EditStoryInputDTO.developer_id + EditStoryUseCase propagation
2. **ViewModel** — StoryDialogViewModel (developer_id, load_developers, validate_field) + testes unitarios
3. **Dialogs simples** — ProgressDialog, ResultDialog (novos, sem dependencias) + testes
4. **ConfirmDeleteDialog** — Factory methods + alert layout + testes
5. **DeveloperDialog** — Icons, hover, empty state, objectNames + testes
6. **FeatureDialog** — "Onda N — Nome", empty state, objectNames + testes
7. **StoryDialog** — Developer combo, validation UI, char count, objectNames + testes
8. **QSS** — Novas regras no stylesheet.qss
