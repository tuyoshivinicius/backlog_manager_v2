"""Test pytest configuration."""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestPytestConfig:
    """Test pytest is configured correctly."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_pyproject_has_pytest_config(self, project_root: Path) -> None:
        """Test pyproject.toml contains pytest configuration."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "[tool.pytest.ini_options]" in content

    def test_pytest_testpaths_configured(self, project_root: Path) -> None:
        """Test pytest testpaths is configured."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert 'testpaths = ["tests"]' in content

    def test_pytest_asyncio_mode_configured(self, project_root: Path) -> None:
        """Test pytest-asyncio mode is configured."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert 'asyncio_mode = "auto"' in content

    def test_pytest_markers_defined(self, project_root: Path) -> None:
        """Test pytest markers are defined."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "markers = [" in content
        assert "unit:" in content
        assert "integration:" in content
