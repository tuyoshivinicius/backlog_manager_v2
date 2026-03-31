# Quickstart: Alocacao Manual de Desenvolvedores

**Branch**: `028-manual-allocation` | **Date**: 2026-03-31

## Pre-requisitos
- Python 3.11+
- Poetry instalado
- Dependencias: `poetry install`

## Executar aplicacao
```bash
poetry run backlog-manager
```

## Fluxo de desenvolvimento

### 1. Criar DTOs (Application Layer)
```
src/backlog_manager/application/dto/allocation/
├── developer_availability_dto.py     # DeveloperAvailabilityDTO, BlockingStoryDTO
├── get_developer_availability_dto.py # Input/Output DTOs
└── manual_allocation_dto.py          # ManualAllocationInputDTO (opcional, pode usar EditStoryInputDTO)
```

### 2. Criar Use Case (Application Layer)
```
src/backlog_manager/application/use_cases/allocation/
└── get_developer_availability.py     # GetDeveloperAvailabilityUseCase
```

### 3. Criar ViewModel (Presentation Layer)
```
src/backlog_manager/presentation/viewmodels/
└── manual_allocation_dialog_viewmodel.py
```

### 4. Criar Dialog (Presentation Layer)
```
src/backlog_manager/presentation/views/
└── manual_allocation_dialog.py
```

### 5. Integrar na MainWindow
- Conectar signal `doubleClicked` da StoryTableView
- Verificar coluna == 7 (Desenvolvedor)
- Abrir ManualAllocationDialog
- Atualizar tabela apos confirmacao

### 6. Registrar no DIContainer
- Factory: `create_get_developer_availability_use_case(uow)`
- ViewModel: lazy property `manual_allocation_dialog_viewmodel`

## Executar testes
```bash
# Todos os testes
poetry run pytest

# Apenas testes desta feature
poetry run pytest tests/unit/application/test_get_developer_availability.py
poetry run pytest tests/unit/presentation/test_manual_allocation_dialog_viewmodel.py

# Com cobertura
poetry run pytest --cov=backlog_manager --cov-report=term-missing
```

## Arquivos-chave para referencia
| Arquivo | Descricao |
|---------|-----------|
| `src/backlog_manager/domain/services/allocation_service.py` | Algoritmo de alocacao (reutilizar _has_period_overlap, _select_developer) |
| `src/backlog_manager/domain/services/scheduling_service.py` | Calculo de datas (reutilizar calculate_story_dates, next_workday) |
| `src/backlog_manager/presentation/views/config_dialog.py` | Padrao de dialog existente |
| `src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py` | Padrao de ViewModel com QSettings |
| `src/backlog_manager/presentation/container.py` | DI Container para registrar novos componentes |
| `src/backlog_manager/presentation/views/main_window.py` | Ponto de integracao (double-click handler) |
| `src/backlog_manager/presentation/theme/theme.py` | Design tokens e paleta |
