# Feature Specification: Schedule Calculation GUI Integration

**Feature Branch**: `013-schedule-gui-integration`
**Created**: 2026-03-04
**Status**: Draft
**Input**: User description: "EP-013: Exposicao do Calculo de Cronograma na GUI"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Calculate Schedule via Toolbar Button (Priority: P1)

As a Scrum Master or Tech Lead, I want to calculate the schedule (start and end dates) for all backlog stories by clicking a toolbar button, so that I can see when each story will be completed before allocating developers.

**Why this priority**: This is the core functionality - without the button, there is no way to trigger schedule calculation from the GUI. This completes the user workflow gap between defining stories/dependencies and automatic allocation.

**Independent Test**: Can be fully tested by clicking the "Calcular Cronograma" button with valid configuration and verifying that stories receive calculated dates. Delivers immediate value by enabling the complete backlog management workflow.

**Acceptance Scenarios**:

1. **Given** the main window is loaded, **When** I look at the toolbar, **Then** I see a "Calcular Cronograma" button positioned before "Alocar Automaticamente"
2. **Given** I have 5 backlog stories without dates and ConfigPanel shows velocity=2.0 and start_date=02/03/2026, **When** I click "Calcular Cronograma", **Then** all 5 stories have start_date and end_date calculated
3. **Given** the calculation completes successfully, **When** the operation finishes, **Then** a dialog displays "X historias tiveram datas calculadas"
4. **Given** stories have dependencies between them, **When** I calculate the schedule, **Then** dates respect topological order (dependent story starts after dependency ends)

---

### User Story 2 - Calculate Schedule via Keyboard Shortcut (Priority: P2)

As a power user, I want to trigger schedule calculation using a keyboard shortcut (Ctrl+Shift+C), so that I can quickly recalculate dates without using the mouse.

**Why this priority**: Keyboard shortcuts improve workflow efficiency for frequent users but are secondary to having the basic button functionality.

**Independent Test**: Can be tested by pressing Ctrl+Shift+C with focus on the application and verifying schedule calculation executes.

**Acceptance Scenarios**:

1. **Given** the application has focus, **When** I press Ctrl+Shift+C, **Then** the schedule calculation is executed
2. **Given** I hover over the "Calcular Cronograma" button, **When** the tooltip appears, **Then** it shows "Calcular datas de inicio e fim das historias (Ctrl+Shift+C)"

---

### User Story 3 - Receive Clear Feedback on Errors (Priority: P3)

As a user, I want to receive clear error messages when schedule calculation fails, so that I understand what went wrong and how to fix it.

**Why this priority**: Error handling is essential for usability but only applies to failure scenarios.

**Independent Test**: Can be tested by triggering errors (invalid configuration, cyclic dependencies) and verifying appropriate error dialogs appear.

**Acceptance Scenarios**:

1. **Given** ConfigPanel has velocity of 0 or invalid, **When** I click "Calcular Cronograma", **Then** an error dialog displays a clear message about the invalid parameter
2. **Given** stories have a cyclic dependency (A depends on B, B depends on A), **When** I click "Calcular Cronograma", **Then** an error dialog displays a clear message about the cycle
3. **Given** an unexpected error occurs, **When** the calculation fails, **Then** an error dialog displays the error message without crashing

---

### User Story 4 - View Updated Dates in Table (Priority: P2)

As a user, I want the backlog table to automatically refresh after schedule calculation, so that I can immediately see the calculated dates for each story.

**Why this priority**: Visual feedback is important for the user experience but is a natural consequence of the calculation completing.

**Independent Test**: Can be tested by calculating schedule and verifying the table displays updated start_date and end_date columns.

**Acceptance Scenarios**:

1. **Given** schedule calculation completes successfully, **When** the operation finishes, **Then** the backlog table refreshes to show the newly calculated dates

---

### Edge Cases

- What happens when there are no eligible stories in the backlog? System shows dialog with "0 historias tiveram datas calculadas"
- What happens when all stories already have dates? With recalculate_all=True, all dates are recalculated
- What happens when a story has invalid story points (not 3, 5, 8, or 13)? Story is skipped with a warning
- What happens when a dependency has no calculated end date? System uses project start date as fallback
- What happens when the user clicks the button multiple times quickly? Only one calculation runs (button disabled during operation)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Calcular Cronograma" button in the main toolbar, positioned before the "Alocar Automaticamente" button
- **FR-002**: System MUST provide keyboard shortcut Ctrl+Shift+C to trigger schedule calculation
- **FR-003**: System MUST display a descriptive tooltip on the button: "Calcular datas de inicio e fim das historias (Ctrl+Shift+C)"
- **FR-004**: System MUST validate configuration parameters (velocity, start_date) before executing calculation
- **FR-005**: System MUST display error dialog with clear message when configuration is invalid
- **FR-006**: System MUST execute schedule calculation using configured velocity and start_date from the configuration panel
- **FR-007**: System MUST display success dialog with count of stories that had dates calculated
- **FR-008**: System MUST display error dialog with clear message when cyclic dependency is detected
- **FR-009**: System MUST refresh the backlog table after successful calculation to show updated dates
- **FR-010**: System MUST disable the button during calculation and follow existing "Alocar Automaticamente" visual feedback pattern to prevent duplicate operations

### Key Entities

- **Schedule Calculation Input**: Configuration parameters for calculation (velocity in story points per day, project start date)
- **Schedule Calculation Result**: Outcome of the calculation (success status, count of stories processed, count of stories updated, any warnings)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can trigger schedule calculation within 2 clicks or 1 keyboard shortcut from the main window
- **SC-002**: Schedule calculation for up to 100 stories completes within 500ms
- **SC-003**: 100% of error scenarios display a user-friendly message (no cryptic errors or crashes)
- **SC-004**: Calculated dates are immediately visible in the backlog table after operation completes
- **SC-005**: The keyboard shortcut works from any focused widget in the main window

## Clarifications

### Session 2026-03-04

- Q: What visual feedback should the user see during calculation? → A: Follow existing "Alocar Automaticamente" pattern

## Assumptions

- The schedule calculation use case (`CalculateScheduleUseCase`) is already implemented and available in the DI container
- The configuration panel already exposes `velocity` and `start_date` properties with validation
- The existing "Alocar Automaticamente" implementation serves as a template for async operation patterns
- Error messages should be in Portuguese (Brazilian) without accents, following project conventions
- The `recalculate_all` parameter defaults to True, meaning all eligible stories are recalculated each time
