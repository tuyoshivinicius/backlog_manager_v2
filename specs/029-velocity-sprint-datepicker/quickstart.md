# Quickstart: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Feature Branch**: `029-velocity-sprint-datepicker`
**Date**: 2026-03-31

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Dependencias instaladas: `poetry install`

## Executar a aplicacao

```bash
poetry run python -m backlog_manager
```

## Verificar a feature

### 1. Configuracao de Velocidade SP/Sprint

1. Abra a aplicacao
2. Abra o ConfigDialog (menu Configuracao ou atalho)
3. Verifique que os campos exibem:
   - "Velocidade (SP/Sprint)" com QSpinBox (int, range 1-100, default 20)
   - "Dias Uteis por Sprint" com QSpinBox (int, range 1-30, default 10)
   - Label derivada "= 2.0 SP/dia"
4. Altere SP/Sprint para 15 e dias uteis para 5
5. Verifique que a label atualiza para "= 3.0 SP/dia"
6. Clique "Aplicar"
7. Reabra o ConfigDialog e verifique que os valores foram restaurados

### 2. DatePicker

1. Abra o ConfigDialog
2. Verifique que o campo "Data Inicio" usa DatePicker com:
   - Calendar popup ao clicar
   - Formato dd/MM/yyyy
   - Estilizacao consistente com Design System
3. Abra o ManualAllocationDialog (selecione uma historia, menu de contexto)
4. Verifique que o campo de data usa DatePicker com:
   - Data minima configurada (proximo dia util)
   - Calendar popup funcional

### 3. Migracao

1. Se voce tinha uma versao anterior com velocity em SP/dia:
   - Abra o ConfigDialog
   - Verifique que exibe defaults (20 SP/Sprint, 10 dias)
   - Nenhum erro ou crash

## Executar testes

```bash
# Testes unitarios do ViewModel
poetry run pytest tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py -v

# Testes do DatePicker
poetry run pytest tests/integration/presentation/views/test_date_picker.py -v

# Todos os testes
poetry run pytest -v
```

## Arquivos modificados

| Arquivo | Alteracao |
|---------|-----------|
| `presentation/views/date_picker.py` | NOVO — componente DatePicker reutilizavel |
| `presentation/views/config_dialog.py` | SP/Sprint + workdays + DatePicker |
| `presentation/views/config_panel.py` | SP/Sprint + workdays + DatePicker |
| `presentation/views/manual_allocation_dialog.py` | Usa DatePicker |
| `presentation/viewmodels/config_dialog_viewmodel.py` | sp_per_sprint, workdays_per_sprint, conversao, migracao QSettings |
