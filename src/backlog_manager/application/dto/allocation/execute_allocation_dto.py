"""DTOs for automatic allocation execution."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from backlog_manager.domain.services import AllocationMetrics


class ExecuteAllocationInputDTO(BaseModel):
    """Input DTO for automatic allocation execution.

    Attributes:
        velocity: Team velocity in story points per day.
        project_start_date: Project start date.
        max_idle_days: Maximum acceptable idle days (default: 3).
        allocation_criteria: Allocation criteria (LOAD_BALANCING or DEPENDENCY_OWNER).
        random_seed: Random seed for determinism in tests (None = random).
    """

    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    project_start_date: date = Field(description="Data de inicio do projeto")
    max_idle_days: int = Field(
        default=3, ge=2, le=30, description="Dias maximos de ociosidade aceitavel"
    )
    allocation_criteria: str = Field(
        default="LOAD_BALANCING",
        description="Criterio de alocacao: LOAD_BALANCING ou DEPENDENCY_OWNER",
    )
    random_seed: int | None = Field(
        default=None, description="Seed para aleatoriedade (None = aleatorio)"
    )


class ExecuteAllocationOutputDTO(BaseModel):
    """Output DTO for automatic allocation execution.

    Attributes:
        success: Whether allocation completed successfully.
        stories_allocated: Number of stories allocated.
        total_time_seconds: Total execution time.
        warnings: List of warning messages.
        metrics: Detailed allocation metrics.
    """

    success: bool = Field(description="Alocacao completou com sucesso")
    stories_allocated: int = Field(description="Numero de historias alocadas")
    total_time_seconds: float = Field(description="Tempo total de execucao")
    warnings: list[str] = Field(default_factory=list, description="Lista de avisos")
    metrics: AllocationMetricsDTO = Field(description="Metricas detalhadas")


class AllocationMetricsDTO(BaseModel):
    """DTO for allocation metrics.

    Attributes:
        total_time_seconds: Total execution time.
        stories_processed: Total stories processed.
        stories_allocated: Stories allocated successfully.
        waves_processed: Number of waves processed.
        total_iterations: Total algorithm iterations.
        iterations_per_wave: Iterations per wave.
        allocations_by_dependency_owner: Allocations by DEPENDENCY_OWNER criteria.
        allocations_by_load_balancing: Allocations by LOAD_BALANCING criteria.
        deadlocks_detected: Deadlocks detected.
        date_adjustments: Date adjustments made.
        validation_reallocations: Successful reallocations in validation.
        validation_dependency_fixes: Dependency violations fixed.
        validation_conflict_fixes: Period conflicts resolved.
        max_idle_violations_detected: max_idle_days violations detected.
        max_idle_violations_fixed: Violations fixed by reallocation.
        failed_reallocations: Failed reallocation attempts.
    """

    total_time_seconds: float = Field(
        default=0.0, description="Tempo total de execucao"
    )
    stories_processed: int = Field(
        default=0, description="Total de historias processadas"
    )
    stories_allocated: int = Field(
        default=0, description="Historias alocadas com sucesso"
    )
    waves_processed: int = Field(default=0, description="Numero de ondas processadas")
    total_iterations: int = Field(
        default=0, description="Total de iteracoes do algoritmo"
    )
    iterations_per_wave: dict[int, int] = Field(
        default_factory=dict, description="Iteracoes por onda"
    )
    allocations_by_dependency_owner: int = Field(
        default=0, description="Alocacoes por criterio DEPENDENCY_OWNER"
    )
    allocations_by_load_balancing: int = Field(
        default=0, description="Alocacoes por criterio LOAD_BALANCING"
    )
    deadlocks_detected: int = Field(default=0, description="Deadlocks detectados")
    date_adjustments: int = Field(default=0, description="Ajustes de data realizados")
    validation_reallocations: int = Field(
        default=0, description="Realocacoes bem-sucedidas na validacao"
    )
    validation_dependency_fixes: int = Field(
        default=0, description="Violacoes de dependencia corrigidas"
    )
    validation_conflict_fixes: int = Field(
        default=0, description="Conflitos de periodo resolvidos"
    )
    max_idle_violations_detected: int = Field(
        default=0, description="Violacoes de max_idle_days detectadas"
    )
    max_idle_violations_fixed: int = Field(
        default=0, description="Violacoes corrigidas por realocacao"
    )
    failed_reallocations: int = Field(
        default=0, description="Tentativas de realocacao que falharam"
    )

    @classmethod
    def from_domain(cls, metrics: AllocationMetrics) -> AllocationMetricsDTO:
        """Create DTO from domain AllocationMetrics.

        Args:
            metrics: Domain metrics object.

        Returns:
            DTO with all metrics copied.
        """
        return cls(
            total_time_seconds=metrics.total_time_seconds,
            stories_processed=metrics.stories_processed,
            stories_allocated=metrics.stories_allocated,
            waves_processed=metrics.waves_processed,
            total_iterations=metrics.total_iterations,
            iterations_per_wave=dict(metrics.iterations_per_wave),
            allocations_by_dependency_owner=metrics.allocations_by_dependency_owner,
            allocations_by_load_balancing=metrics.allocations_by_load_balancing,
            deadlocks_detected=metrics.deadlocks_detected,
            date_adjustments=metrics.date_adjustments,
            validation_reallocations=metrics.validation_reallocations,
            validation_dependency_fixes=metrics.validation_dependency_fixes,
            validation_conflict_fixes=metrics.validation_conflict_fixes,
            max_idle_violations_detected=metrics.max_idle_violations_detected,
            max_idle_violations_fixed=metrics.max_idle_violations_fixed,
            failed_reallocations=metrics.failed_reallocations,
        )


# Forward reference resolution
ExecuteAllocationOutputDTO.model_rebuild()
