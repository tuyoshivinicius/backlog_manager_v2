"""Calculate duration use case."""

from __future__ import annotations

from backlog_manager.application.dto.scheduling.calculate_duration_dto import (
    CalculateDurationInputDTO,
    CalculateDurationOutputDTO,
)
from backlog_manager.domain.services import SchedulingService


class CalculateDurationUseCase:
    """Use case for calculating story duration.

    Calculates the duration in workdays for a story based on
    story points and team velocity. This is a pure calculation
    with no side effects or persistence.

    Example:
        >>> use_case = CalculateDurationUseCase()
        >>> result = use_case.execute(
        ...     CalculateDurationInputDTO(story_points=5, velocity=2.0)
        ... )
        >>> print(result.duration)  # 3
    """

    def execute(
        self, input_dto: CalculateDurationInputDTO
    ) -> CalculateDurationOutputDTO:
        """Execute duration calculation.

        Args:
            input_dto: Input containing story points and velocity.

        Returns:
            Output DTO with duration and formula used.
        """
        duration = SchedulingService.calculate_duration(
            input_dto.story_points, input_dto.velocity
        )

        formula = f"ceil({input_dto.story_points} / {input_dto.velocity}) = {duration}"

        return CalculateDurationOutputDTO(
            duration=duration,
            formula=formula,
        )
