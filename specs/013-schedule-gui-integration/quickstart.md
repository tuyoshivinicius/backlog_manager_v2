# Quickstart: Schedule Calculation GUI Integration

**Feature**: EP-013 | **Date**: 2026-03-04

## Development Environment

```bash
# Navigate to project root
cd backlog_manager_v2

# Ensure virtual environment is active
poetry shell

# Install dependencies (if needed)
poetry install

# Verify existing tests pass
python -m pytest tests/ -v
```

## Implementation Overview

### Files to Create

1. **ScheduleViewModel** (`src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py`)
   - Copy AllocationViewModel as starting template
   - Replace allocation-specific signals with schedule signals
   - Update execute() to call CalculateScheduleUseCase

### Files to Modify

1. **DIContainer** (`src/backlog_manager/presentation/container.py`)
   - Add `_schedule_viewmodel: ScheduleViewModel | None = None`
   - Add `schedule_viewmodel` property (lazy initialization)

2. **MainWindow** (`src/backlog_manager/presentation/views/main_window.py`)
   - Add `_action_schedule` in `_setup_toolbar()`
   - Add `_on_calculate_schedule()` handler
   - Add `_execute_schedule_calculation()` async method
   - Add `_on_schedule_started()` and `_on_schedule_completed()` signal handlers
   - Connect signals in `_setup_signals()`

### Tests to Create

1. **Unit Tests** (`tests/unit/presentation/viewmodels/test_schedule_viewmodel.py`)
   - Test signal emissions
   - Test duplicate execution prevention
   - Test error handling

2. **Integration Tests** (`tests/integration/presentation/test_schedule_gui_integration.py`)
   - Test full flow from button click to table refresh

## Implementation Steps

### Step 1: Create ScheduleViewModel

```python
# src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py
"""ViewModel para calculo de cronograma."""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
    CalculateScheduleInputDTO,
    CalculateScheduleOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ScheduleViewModel(QObject):
    """ViewModel para calculo de cronograma."""

    schedule_started = Signal()
    schedule_completed = Signal(object)
    schedule_error = Signal(str)

    def __init__(self, container: DIContainer) -> None:
        super().__init__()
        self._container = container
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def execute(
        self,
        velocity: float,
        start_date: date,
    ) -> CalculateScheduleOutputDTO | None:
        if self._is_running:
            logger.warning("Schedule calculation already running")
            return None

        self._is_running = True
        self.schedule_started.emit()

        try:
            dto = CalculateScheduleInputDTO(
                velocity=velocity,
                start_date=start_date,
                recalculate_all=True,
            )

            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_calculate_schedule_use_case(uow)
                result = await use_case.execute(dto)

            logger.info(
                "Schedule calculation completed: %d stories updated",
                result.stories_updated,
            )

            self.schedule_completed.emit(result)
            return result

        except BacklogManagerException as e:
            error_msg = str(e)
            logger.error("Schedule calculation failed: %s", error_msg)
            self.schedule_error.emit(error_msg)
            return None

        finally:
            self._is_running = False
```

### Step 2: Update DIContainer

Add to `container.py`:

```python
# After _allocation_viewmodel declaration
self._schedule_viewmodel: ScheduleViewModel | None = None

# Add property
@property
def schedule_viewmodel(self) -> ScheduleViewModel:
    if self._schedule_viewmodel is None:
        from backlog_manager.presentation.viewmodels.schedule_viewmodel import (
            ScheduleViewModel,
        )
        self._schedule_viewmodel = ScheduleViewModel(self)
    return self._schedule_viewmodel
```

### Step 3: Update MainWindow

Add toolbar action in `_setup_toolbar()`:

```python
# After Excel actions, before Allocate action
self._action_schedule = QAction("Calcular Cronograma", self)
self._action_schedule.setToolTip(
    "Calcular datas de inicio e fim das historias (Ctrl+Shift+C)"
)
self._action_schedule.setShortcut(QKeySequence("Ctrl+Shift+C"))
self._action_schedule.triggered.connect(self._on_calculate_schedule)
toolbar.addAction(self._action_schedule)
```

Add handlers:

```python
@Slot()
def _on_calculate_schedule(self) -> None:
    """Handle schedule calculation action."""
    logger.debug("Schedule calculation action triggered")

    is_valid, error = self._config_panel.validate()
    if not is_valid:
        QMessageBox.warning(self, "Configuracao Invalida", error)
        return

    QTimer.singleShot(
        0, lambda: asyncio.create_task(self._execute_schedule_calculation())
    )

async def _execute_schedule_calculation(self) -> None:
    """Execute schedule calculation with config panel values."""
    schedule_vm = self._container.schedule_viewmodel

    await schedule_vm.execute(
        velocity=self._config_panel.velocity,
        start_date=self._config_panel.start_date,
    )

    await self._viewmodel.load_stories()

@Slot()
def _on_schedule_started(self) -> None:
    """Handle schedule started signal."""
    self._action_schedule.setEnabled(False)
    self.setCursor(Qt.CursorShape.WaitCursor)

@Slot(object)
def _on_schedule_completed(self, result: CalculateScheduleOutputDTO) -> None:
    self._action_schedule.setEnabled(True)
    self.setCursor(Qt.CursorShape.ArrowCursor)

    QMessageBox.information(
        self,
        "Cronograma Calculado",
        f"{result.stories_updated} historias tiveram datas calculadas.",
    )
```

Connect signals in `_setup_signals()`:

```python
schedule_vm = self._container.schedule_viewmodel
schedule_vm.schedule_started.connect(self._on_schedule_started)
schedule_vm.schedule_completed.connect(self._on_schedule_completed)
schedule_vm.schedule_error.connect(self._on_error)
```

## Verification

```bash
# Run unit tests
python -m pytest tests/unit/presentation/viewmodels/test_schedule_viewmodel.py -v

# Run integration tests
python -m pytest tests/integration/presentation/test_schedule_gui_integration.py -v

# Run all tests
python -m pytest tests/ -v --cov=src/backlog_manager --cov-report=term-missing

# Manual testing
poetry run python -m backlog_manager
# 1. Add stories with valid story_points
# 2. Set velocity and start_date in ConfigPanel
# 3. Click "Calcular Cronograma" or press Ctrl+Shift+C
# 4. Verify success dialog and table update
```
