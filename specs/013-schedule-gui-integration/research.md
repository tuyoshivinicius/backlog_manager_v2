# Research: Schedule Calculation GUI Integration

**Feature**: EP-013 Schedule GUI Integration | **Date**: 2026-03-04

## Research Tasks

No "NEEDS CLARIFICATION" items were identified in the Technical Context. This feature follows established patterns with existing infrastructure.

## Findings

### 1. Async Operation Pattern for GUI (Allocation as Template)

**Decision**: Follow AllocationViewModel pattern exactly

**Rationale**: The existing AllocationViewModel provides a proven pattern for:
- Async execution with Qt signals (`allocation_started`, `allocation_completed`, `allocation_error`)
- State management (`_is_running` flag to prevent duplicate operations)
- Error handling with BacklogManagerException mapping
- Unit of Work integration for transactional operations

**Implementation Reference**:
```python
# From AllocationViewModel (proven pattern)
async def execute(self, velocity, start_date, ...):
    if self._is_running:
        return None
    self._is_running = True
    self.allocation_started.emit()
    try:
        async with self._container.create_unit_of_work() as uow:
            use_case = self._container.create_execute_allocation_use_case(uow)
            result = await use_case.execute(dto)
        self.allocation_completed.emit(result)
    except BacklogManagerException as e:
        self.allocation_error.emit(str(e))
    finally:
        self._is_running = False
```

**Alternatives Considered**:
- Direct use case call from MainWindow: Rejected - violates MVVM, harder to test
- QThread-based approach: Rejected - qasync integration already in place, more complex

### 2. ConfigPanel Validation Reuse

**Decision**: Reuse existing ConfigPanel.validate() method

**Rationale**: The ConfigPanel already validates:
- `velocity > 0`
- `max_idle_days` between 2-30
- `start_date` is valid (QDateEdit ensures valid dates)

The schedule calculation only needs velocity and start_date, both already validated.

**Implementation Note**: Before calling ScheduleViewModel.execute(), call ConfigPanel.validate() and show warning dialog if invalid.

### 3. Error Handling for Cyclic Dependencies

**Decision**: Map CyclicDependencyException to user-friendly Portuguese dialog

**Rationale**: CalculateScheduleUseCase raises CyclicDependencyException when cycles are detected in the dependency graph. This must be caught and displayed as a clear error message.

**Error Messages** (Portuguese, no accents per project convention):
- Cyclic dependency: "Dependencia ciclica detectada: {cycle_details}"
- Invalid configuration: "Configuracao invalida: {validation_error}"
- Generic error: "Erro ao calcular cronograma: {error_message}"

### 4. Success Dialog Message Format

**Decision**: Follow allocation success dialog pattern with story count

**Format**:
```
Cronograma Calculado

X historias tiveram datas calculadas.

[Warnings if any]
```

**Rationale**: Consistent with allocation dialog, provides clear feedback on operation scope.

### 5. Toolbar Button Placement

**Decision**: Position "Calcular Cronograma" before "Alocar Automaticamente"

**Rationale**: Schedule calculation is a prerequisite for allocation (dates must be calculated before developers can be assigned). The toolbar order reflects the workflow: Define Stories -> Calculate Schedule -> Allocate Developers.

### 6. Keyboard Shortcut

**Decision**: Use Ctrl+Shift+C

**Rationale**:
- "C" for Cronograma (Schedule)
- Ctrl+Shift modifier consistent with Ctrl+Shift+A (Allocation)
- Does not conflict with existing shortcuts (Ctrl+S save, Ctrl+Shift+A allocation)

## Dependencies Verified

| Component | Status | Location |
|-----------|--------|----------|
| CalculateScheduleUseCase | Exists | `application/use_cases/scheduling/calculate_schedule.py` |
| CalculateScheduleInputDTO | Exists | `application/dto/scheduling/calculate_schedule_dto.py` |
| CalculateScheduleOutputDTO | Exists | `application/dto/scheduling/calculate_schedule_dto.py` |
| CyclicDependencyException | Exists | `domain/exceptions/dependency_exceptions.py` |
| SchedulingService | Exists | `domain/services/scheduling_service.py` |
| DIContainer.create_calculate_schedule_use_case | Exists | `presentation/container.py` |
| ConfigPanel.validate() | Exists | `presentation/views/config_panel.py` |
| AllocationViewModel (template) | Exists | `presentation/viewmodels/allocation_viewmodel.py` |

## Conclusion

All technical uncertainties have been resolved. The implementation will:
1. Create ScheduleViewModel following AllocationViewModel pattern
2. Add schedule_viewmodel property to DIContainer
3. Add toolbar action in MainWindow with Ctrl+Shift+C shortcut
4. Wire signals for started/completed/error states
5. Reuse existing validation and error handling patterns
