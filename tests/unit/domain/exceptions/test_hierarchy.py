"""Test exception hierarchy."""

import pytest

from backlog_manager.domain.exceptions import (
    AllocationException,
    BacklogManagerException,
    CyclicDependencyException,
    DependencyException,
    DuplicateWaveException,
    FeatureException,
    FeatureHasStoriesException,
    InvalidWaveDependencyException,
    MaxIterationsExceeded,
)


@pytest.mark.unit
class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_backlog_manager_exception_is_exception(self) -> None:
        """Test BacklogManagerException inherits from Exception."""
        assert issubclass(BacklogManagerException, Exception)

    def test_dependency_exception_inherits_base(self) -> None:
        """Test DependencyException inherits from BacklogManagerException."""
        assert issubclass(DependencyException, BacklogManagerException)

    def test_cyclic_dependency_inherits_dependency(self) -> None:
        """Test CyclicDependencyException inherits from DependencyException."""
        assert issubclass(CyclicDependencyException, DependencyException)
        assert issubclass(CyclicDependencyException, BacklogManagerException)

    def test_invalid_wave_dependency_inherits_dependency(self) -> None:
        """Test InvalidWaveDependencyException inherits from DependencyException."""
        assert issubclass(InvalidWaveDependencyException, DependencyException)
        assert issubclass(InvalidWaveDependencyException, BacklogManagerException)

    def test_feature_exception_inherits_base(self) -> None:
        """Test FeatureException inherits from BacklogManagerException."""
        assert issubclass(FeatureException, BacklogManagerException)

    def test_duplicate_wave_inherits_feature(self) -> None:
        """Test DuplicateWaveException inherits from FeatureException."""
        assert issubclass(DuplicateWaveException, FeatureException)
        assert issubclass(DuplicateWaveException, BacklogManagerException)

    def test_feature_has_stories_inherits_feature(self) -> None:
        """Test FeatureHasStoriesException inherits from FeatureException."""
        assert issubclass(FeatureHasStoriesException, FeatureException)
        assert issubclass(FeatureHasStoriesException, BacklogManagerException)

    def test_allocation_exception_inherits_base(self) -> None:
        """Test AllocationException inherits from BacklogManagerException."""
        assert issubclass(AllocationException, BacklogManagerException)

    def test_max_iterations_inherits_allocation(self) -> None:
        """Test MaxIterationsExceeded inherits from AllocationException."""
        assert issubclass(MaxIterationsExceeded, AllocationException)
        assert issubclass(MaxIterationsExceeded, BacklogManagerException)

    def test_catch_all_with_base_exception(self) -> None:
        """Test all exceptions can be caught with BacklogManagerException."""
        exceptions = [
            CyclicDependencyException(path=["A", "B", "A"]),
            InvalidWaveDependencyException("A", "B", 1, 2),
            DuplicateWaveException(wave=1, existing_feature_name="Test"),
            FeatureHasStoriesException(1, "Test", 5),
            MaxIterationsExceeded(1000, 10),
        ]

        for exc in exceptions:
            with pytest.raises(BacklogManagerException):
                raise exc
