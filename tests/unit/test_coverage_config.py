"""Test coverage configuration."""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestCoverageConfig:
    """Test coverage is configured correctly."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_pyproject_has_coverage_config(self, project_root: Path) -> None:
        """Test pyproject.toml contains coverage configuration."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "[tool.coverage.run]" in content
        assert "[tool.coverage.report]" in content

    def test_coverage_source_configured(self, project_root: Path) -> None:
        """Test coverage source is configured."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert 'source = ["src/backlog_manager"]' in content

    def test_coverage_fail_under_90(self, project_root: Path) -> None:
        """Test coverage fail_under is set to 90%."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "fail_under = 90" in content

    def test_coverage_branch_enabled(self, project_root: Path) -> None:
        """Test branch coverage is enabled."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "branch = true" in content

    def test_coverage_show_missing_enabled(self, project_root: Path) -> None:
        """Test show_missing is enabled."""
        pyproject = project_root / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "show_missing = true" in content
