"""Test CyclicDependencyException."""

import pytest
from backlog_manager.domain.exceptions import CyclicDependencyException


@pytest.mark.unit
class TestCyclicDependencyException:
    """Test CyclicDependencyException attributes and behavior."""

    def test_path_attribute(self) -> None:
        """Test path attribute is stored correctly."""
        path = ["AUTH-001", "AUTH-002", "AUTH-003", "AUTH-001"]
        exc = CyclicDependencyException(path=path)

        assert exc.path == path

    def test_default_message(self) -> None:
        """Test default message includes path."""
        path = ["A", "B", "C", "A"]
        exc = CyclicDependencyException(path=path)

        assert "A -> B -> C -> A" in str(exc)
        assert "Ciclo detectado" in str(exc)

    def test_custom_message(self) -> None:
        """Test custom message overrides default."""
        path = ["A", "B", "A"]
        custom_msg = "Mensagem customizada"
        exc = CyclicDependencyException(path=path, message=custom_msg)

        assert str(exc) == custom_msg
        assert exc.path == path

    def test_empty_path(self) -> None:
        """Test exception with empty path."""
        exc = CyclicDependencyException(path=[])

        assert exc.path == []
        assert "Ciclo detectado" in str(exc)

    def test_single_element_path(self) -> None:
        """Test exception with single element path (self-reference)."""
        exc = CyclicDependencyException(path=["AUTH-001"])

        assert exc.path == ["AUTH-001"]
        assert "AUTH-001" in str(exc)
