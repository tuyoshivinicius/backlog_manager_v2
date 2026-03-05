# Contract: ScheduleViewModel Signals

**Component**: ScheduleViewModel | **Date**: 2026-03-04

## Overview

Defines the Qt signal interface for ScheduleViewModel, enabling loose coupling between the ViewModel and MainWindow.

## Signal Definitions

### schedule_started

**Signature**: `Signal()`

**Emitted**: When schedule calculation begins

**Expected Subscriber Actions**:
- Disable "Calcular Cronograma" button
- Change cursor to WaitCursor
- Clear previous results

### schedule_completed

**Signature**: `Signal(object)`

**Payload**: `CalculateScheduleOutputDTO`

**Emitted**: When calculation completes successfully

**Payload Fields**:
```python
{
    "success": True,
    "stories_processed": 15,    # Total eligible stories
    "stories_updated": 15,      # Stories with dates calculated
    "warnings": [               # Non-fatal warnings
        "Dependencia X sem data: usando project_start_date como fallback"
    ]
}
```

**Expected Subscriber Actions**:
- Enable "Calcular Cronograma" button
- Restore cursor to ArrowCursor
- Show success dialog with story count
- Refresh backlog table
- Display warnings if any

### schedule_error

**Signature**: `Signal(str)`

**Payload**: Error message (Portuguese, no accents)

**Emitted**: When calculation fails

**Error Message Format**:
| Error Type | Message Pattern |
|------------|-----------------|
| Cyclic Dependency | "Dependencia ciclica detectada: {cycle}" |
| Validation Error | "Configuracao invalida: {details}" |
| Generic Error | "Erro ao calcular cronograma: {message}" |

**Expected Subscriber Actions**:
- Enable "Calcular Cronograma" button
- Restore cursor to ArrowCursor
- Show error dialog (QMessageBox.warning)

## Signal Connection Pattern

```python
# In MainWindow.__init__ or _setup_signals
schedule_vm = self._container.schedule_viewmodel
schedule_vm.schedule_started.connect(self._on_schedule_started)
schedule_vm.schedule_completed.connect(self._on_schedule_completed)
schedule_vm.schedule_error.connect(self._on_error)  # Reuse existing error handler
```

## Thread Safety

- Signals are emitted from async context via QTimer.singleShot
- Signal connections are Qt::AutoConnection (default)
- No direct UI updates from async methods
