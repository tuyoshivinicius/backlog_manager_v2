# Quickstart: EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)

## Prerequisites

- Python 3.11+
- Poetry installed
- Dependencies: `poetry install`

## Running the Application

```bash
poetry run python -m backlog_manager
```

## Testing the Reset Feature

1. Import or create stories in the backlog
2. Run "Calcular Cronograma" (Ctrl+Shift+C) to generate dates
3. Run "Alocar Desenvolvedores" (Ctrl+Shift+A) to assign developers
4. Click "Novo Planejamento" (Ctrl+Shift+N) in toolbar or Ferramentas menu
5. Verify the confirmation dialog shows correct counts
6. Click "Confirmar" to execute reset
7. Verify: table shows empty calculated columns, status bar updated

## Running Tests

```bash
# Unit tests only
pytest tests/unit/application/use_cases/planning/ -v
pytest tests/unit/presentation/viewmodels/test_reset_planning_viewmodel.py -v

# E2E tests
pytest tests/e2e/test_ep023_reset_planning.py -v

# Full regression
pytest tests/ -v
```

## Key Files

| Component | File |
|-----------|------|
| DTOs | `src/backlog_manager/application/dto/planning/reset_planning_dto.py` |
| Reset Use Case | `src/backlog_manager/application/use_cases/planning/reset_planning.py` |
| Count Use Case | `src/backlog_manager/application/use_cases/planning/count_affected_stories.py` |
| ViewModel | `src/backlog_manager/presentation/viewmodels/reset_planning_viewmodel.py` |
| Dialog | `src/backlog_manager/presentation/views/confirm_reset_dialog.py` |
| Container | `src/backlog_manager/presentation/container.py` |
| Main Window | `src/backlog_manager/presentation/views/main_window.py` |
