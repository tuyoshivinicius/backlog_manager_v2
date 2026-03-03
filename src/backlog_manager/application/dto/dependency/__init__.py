"""Dependency DTOs (Data Transfer Objects)."""

from backlog_manager.application.dto.dependency.add_dependency_dto import (
    AddDependencyInputDTO,
    AddDependencyOutputDTO,
    InvalidWaveDependencyWarningDTO,
)
from backlog_manager.application.dto.dependency.get_dependency_dto import (
    GetDependenciesInputDTO,
    GetDependenciesOutputDTO,
    GetDependentsInputDTO,
    GetDependentsOutputDTO,
)
from backlog_manager.application.dto.dependency.remove_dependency_dto import (
    RemoveDependencyInputDTO,
    RemoveDependencyOutputDTO,
)

__all__ = [
    "AddDependencyInputDTO",
    "AddDependencyOutputDTO",
    "InvalidWaveDependencyWarningDTO",
    "GetDependenciesInputDTO",
    "GetDependenciesOutputDTO",
    "GetDependentsInputDTO",
    "GetDependentsOutputDTO",
    "RemoveDependencyInputDTO",
    "RemoveDependencyOutputDTO",
]
