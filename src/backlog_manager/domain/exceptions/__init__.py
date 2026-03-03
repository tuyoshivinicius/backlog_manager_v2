"""Domain exceptions and warnings."""

from backlog_manager.domain.exceptions.allocation import (
    AllocationException,
    MaxIterationsExceeded,
)
from backlog_manager.domain.exceptions.base import BacklogManagerException
from backlog_manager.domain.exceptions.dependency import (
    CyclicDependencyException,
    DependencyException,
    InvalidWaveDependencyException,
)
from backlog_manager.domain.exceptions.feature import (
    DuplicateWaveException,
    FeatureException,
    FeatureHasStoriesException,
)
from backlog_manager.domain.exceptions.warnings import (
    BacklogWarning,
    BetweenWavesIdlenessInfo,
    DeadlockWarning,
    IdlenessWarning,
)

__all__ = [
    # Base
    "BacklogManagerException",
    # Dependency
    "DependencyException",
    "CyclicDependencyException",
    "InvalidWaveDependencyException",
    # Feature
    "FeatureException",
    "DuplicateWaveException",
    "FeatureHasStoriesException",
    # Allocation
    "AllocationException",
    "MaxIterationsExceeded",
    # Warnings
    "BacklogWarning",
    "DeadlockWarning",
    "IdlenessWarning",
    "BetweenWavesIdlenessInfo",
]
