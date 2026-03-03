"""Test Developer entity."""

import pytest

from backlog_manager.domain.entities import Developer


@pytest.mark.unit
class TestDeveloper:
    """Test Developer entity creation and validation."""

    def test_valid_developer_creation(self) -> None:
        """Test creating a valid developer."""
        dev = Developer(name="John Doe")

        assert dev.name == "John Doe"
        assert dev.id is None

    def test_developer_with_id(self) -> None:
        """Test creating a developer with ID."""
        dev = Developer(id=1, name="John Doe")

        assert dev.id == 1
        assert dev.name == "John Doe"

    def test_empty_name_raises_error(self) -> None:
        """Test empty name raises ValueError."""
        with pytest.raises(
            ValueError, match="Nome do desenvolvedor nao pode ser vazio"
        ):
            Developer(name="")

    def test_whitespace_name_raises_error(self) -> None:
        """Test whitespace-only name raises ValueError."""
        with pytest.raises(
            ValueError, match="Nome do desenvolvedor nao pode ser vazio"
        ):
            Developer(name="   ")

    def test_long_name_raises_error(self) -> None:
        """Test name over 100 chars raises ValueError."""
        with pytest.raises(
            ValueError, match="Nome do desenvolvedor nao pode exceder 100"
        ):
            Developer(name="A" * 101)

    def test_max_length_name(self) -> None:
        """Test name at exactly 100 chars is valid."""
        dev = Developer(name="A" * 100)
        assert len(dev.name) == 100
