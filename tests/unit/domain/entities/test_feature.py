"""Test Feature entity."""

import pytest

from backlog_manager.domain.entities import Feature


@pytest.mark.unit
class TestFeature:
    """Test Feature entity creation and validation."""

    def test_valid_feature_creation(self) -> None:
        """Test creating a valid feature."""
        feature = Feature(name="Authentication", wave=1)

        assert feature.name == "Authentication"
        assert feature.wave == 1
        assert feature.id is None

    def test_feature_with_id(self) -> None:
        """Test creating a feature with ID."""
        feature = Feature(id=1, name="Authentication", wave=1)

        assert feature.id == 1
        assert feature.name == "Authentication"
        assert feature.wave == 1

    def test_empty_name_raises_error(self) -> None:
        """Test empty name raises ValueError."""
        with pytest.raises(ValueError, match="Nome da feature nao pode ser vazio"):
            Feature(name="", wave=1)

    def test_whitespace_name_raises_error(self) -> None:
        """Test whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Nome da feature nao pode ser vazio"):
            Feature(name="   ", wave=1)

    def test_long_name_raises_error(self) -> None:
        """Test name over 100 chars raises ValueError."""
        with pytest.raises(ValueError, match="Nome da feature nao pode exceder 100"):
            Feature(name="A" * 101, wave=1)

    def test_zero_wave_raises_error(self) -> None:
        """Test wave = 0 raises ValueError."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            Feature(name="Test", wave=0)

    def test_negative_wave_raises_error(self) -> None:
        """Test negative wave raises ValueError."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            Feature(name="Test", wave=-1)

    def test_max_length_name(self) -> None:
        """Test name at exactly 100 chars is valid."""
        feature = Feature(name="A" * 100, wave=1)
        assert len(feature.name) == 100
