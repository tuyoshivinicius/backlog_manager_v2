# Feature Specification: Story Completion Status

**Feature Branch**: `024-story-completion`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "Preciso ser capaz de colocar o status da historia como concluido e o calculo de cronograma tal como alocacao de devs deve passar a ignorar essa historia, eu so nao posso colocar uma historia em concluido caso suas dependencias nao estejam"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mark Story as Completed (Priority: P1)

As a project manager, I need to mark a story as "Concluido" (completed) so that the backlog reflects the actual progress of the project and completed work is clearly distinguished from pending work.

**Why this priority**: This is the core action the feature enables. Without the ability to mark stories as completed, all other behaviors (ignoring in scheduling, dependency validation) have no trigger.

**Independent Test**: Can be fully tested by selecting a story with no dependencies (or all dependencies already completed) and changing its status to "Concluido". The story should visually reflect the completed state.

**Acceptance Scenarios**:

1. **Given** a story in status "Backlog" with no dependencies, **When** the user changes its status to "Concluido", **Then** the story status is updated to "Concluido" and persisted.
2. **Given** a story in status "Execucao" with all dependencies already in "Concluido", **When** the user changes its status to "Concluido", **Then** the status is updated successfully.
3. **Given** a story in status "Testes" with all dependencies already in "Concluido", **When** the user changes its status to "Concluido", **Then** the status is updated successfully.
4. **Given** a story in status "Concluido", **When** the user changes its status back to any other status, **Then** the transition is allowed (status remains flexible for corrections).

---

### User Story 2 - Dependency Validation on Completion (Priority: P1)

As a project manager, I need the system to prevent me from marking a story as "Concluido" if any of its direct dependencies are not yet completed, so that logical workflow integrity is maintained.

**Why this priority**: This is a critical business rule that ensures data consistency. Without it, the backlog could represent an impossible state (a story completed before its prerequisites).

**Independent Test**: Can be tested by creating two stories where Story B depends on Story A, then attempting to mark Story B as "Concluido" while Story A is still in "Backlog". The system should reject the transition with a clear message.

**Acceptance Scenarios**:

1. **Given** Story B depends on Story A, and Story A is in status "Backlog", **When** the user tries to set Story B to "Concluido", **Then** the system rejects the transition and displays a message identifying Story A as the incomplete dependency.
2. **Given** Story C depends on Story A and Story B, and Story A is "Concluido" but Story B is "Execucao", **When** the user tries to set Story C to "Concluido", **Then** the system rejects the transition and identifies Story B as the incomplete dependency.
3. **Given** Story B depends on Story A, and Story A is "Concluido", **When** the user sets Story B to "Concluido", **Then** the transition succeeds.
4. **Given** Story D depends on Story B and Story C, and both are "Concluido", **When** the user sets Story D to "Concluido", **Then** the transition succeeds.

---

### User Story 3 - Exclude Completed Stories from Scheduling and Allocation (Priority: P1)

As a project manager, I need the scheduling engine and developer allocation to completely ignore stories marked as "Concluido", so that completed work does not consume developer capacity or affect date calculations for remaining stories.

**Why this priority**: Without this, marking a story as completed has no practical effect on project planning. The scheduling and allocation would continue treating completed stories as pending work.

**Independent Test**: Can be tested by marking a story as "Concluido", running the allocation process, and verifying that the completed story retains its existing dates/developer but is not considered when calculating dates and allocating developers for remaining stories.

**Acceptance Scenarios**:

1. **Given** a story marked as "Concluido" with an assigned developer, **When** the scheduling engine recalculates dates, **Then** the completed story is excluded from date calculations and the developer's available capacity does not account for that story.
2. **Given** three stories where Story B depends on Story A, and Story A is "Concluido", **When** the allocation runs, **Then** Story B is treated as having no pending dependencies and can be scheduled immediately (respecting only its other constraints).
3. **Given** a developer with two stories, one "Concluido" and one "Backlog", **When** allocation runs, **Then** the developer's workload only considers the "Backlog" story.
4. **Given** a story marked as "Concluido", **When** the allocation runs, **Then** the completed story's existing developer assignment, start date, and end date are preserved unchanged.

---

### User Story 4 - Clear Feedback on Blocked Completion (Priority: P2)

As a project manager, when I attempt to mark a story as completed but it has incomplete dependencies, I need to see a clear and informative message listing which dependencies are blocking the completion, so I can take action on those dependencies first.

**Why this priority**: This is a usability enhancement that makes the dependency validation actionable. The core validation (US2) works without it, but user productivity is significantly improved with clear feedback.

**Independent Test**: Can be tested by attempting to complete a story with multiple incomplete dependencies and verifying the error message lists all blocking stories with their current statuses.

**Acceptance Scenarios**:

1. **Given** Story C depends on Story A (status "Backlog") and Story B (status "Execucao"), **When** the user tries to set Story C to "Concluido", **Then** the system displays a message listing both Story A and Story B with their current statuses as blocking dependencies.
2. **Given** Story B depends on Story A (status "Testes"), **When** the user tries to set Story B to "Concluido", **Then** the message identifies Story A and shows its current status "Testes".

---

### Edge Cases

- What happens when a story has no dependencies? It can be marked as "Concluido" freely.
- What happens when a story has transitive dependencies (A -> B -> C) and the user tries to complete C? Only direct dependencies are validated (B must be "Concluido"; A is validated indirectly when B is completed).
- What happens when a completed story is moved back to a non-completed status? The transition is allowed. Stories that depend on it and are already "Concluido" remain unchanged (no cascading status changes).
- What happens when the user tries to complete a story that is in "Impedido" (blocked) status? The transition is allowed as long as all dependencies are "Concluido" (status flexibility is preserved).
- What happens when a completed story is the dependency of an in-progress story and the completed story is reverted to "Backlog"? The dependent story's status is not affected, but the next attempt to mark the dependent as "Concluido" will fail validation since its dependency is no longer completed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST validate that all direct dependencies of a story are in "Concluido" status before allowing the story to transition to "Concluido".
- **FR-002**: System MUST display a clear error message listing all incomplete dependencies (with their IDs, names, and current statuses) when a completion transition is rejected.
- **FR-003**: System MUST exclude stories in "Concluido" status from scheduling date calculations.
- **FR-004**: System MUST exclude stories in "Concluido" status from developer allocation processing.
- **FR-005**: System MUST preserve existing developer assignment, start date, and end date on completed stories (no clearing of data upon completion).
- **FR-006**: System MUST allow transitions from "Concluido" to any other status without restriction (to support corrections).
- **FR-007**: System MUST only validate direct dependencies, not transitive dependencies, when checking completion eligibility.
- **FR-008**: System MUST NOT cascade status changes when a completed story is reverted to a non-completed status.

### Key Entities

- **Story**: Extended with completion validation behavior. Key attributes: status, dependencies, developer assignment, scheduled dates.
- **Story Dependency**: Existing relationship between stories used for completion validation. Directional: "story depends on dependency".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can mark a story as completed in a single action (one click/selection) when all dependencies are satisfied.
- **SC-002**: 100% of attempts to complete a story with incomplete dependencies are blocked with an informative message.
- **SC-003**: After marking stories as completed, the next scheduling/allocation run produces a plan that excludes all completed stories from capacity calculations.
- **SC-004**: Completed stories retain their historical data (developer, dates) indefinitely after completion.
- **SC-005**: The dependency validation feedback identifies all blocking dependencies in a single message (no need for trial-and-error).

## Assumptions

- The existing "Concluido" status in the StoryStatus enum is the target status for this feature (no new status needed).
- Only direct (first-level) dependencies are validated for completion, not the full transitive dependency chain, since each story in the chain enforces its own direct dependencies upon completion.
- Reverting a completed story does not trigger any cascading validation or status changes on dependent stories.
- The existing flexible status transition model is preserved for all transitions except the new constraint on transitioning TO "Concluido".
