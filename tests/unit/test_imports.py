"""Test module imports."""

import pytest


@pytest.mark.unit
class TestImports:
    """Test that all modules are importable."""

    def test_import_main_module(self) -> None:
        """Test main module import."""
        import backlog_manager

        assert hasattr(backlog_manager, "__version__")
        assert isinstance(backlog_manager.__version__, str)
        assert len(backlog_manager.__version__) > 0

    def test_import_domain_entities(self) -> None:
        """Test domain entities import."""
        from backlog_manager.domain.entities import Developer, Feature, Story

        assert Story is not None
        assert Developer is not None
        assert Feature is not None

    def test_import_value_objects(self) -> None:
        """Test value objects import."""
        from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

        assert StoryPoint is not None
        assert StoryStatus is not None

    def test_import_exceptions(self) -> None:
        """Test exceptions import."""
        from backlog_manager.domain.exceptions import (
            AllocationException,
            BacklogManagerException,
            BacklogWarning,
            CyclicDependencyException,
            DependencyException,
            DuplicateWaveException,
            FeatureException,
            FeatureHasStoriesException,
            MaxIterationsExceeded,
        )

        assert BacklogManagerException is not None
        assert DependencyException is not None
        assert CyclicDependencyException is not None
        assert FeatureException is not None
        assert DuplicateWaveException is not None
        assert FeatureHasStoriesException is not None
        assert AllocationException is not None
        assert MaxIterationsExceeded is not None
        assert BacklogWarning is not None
