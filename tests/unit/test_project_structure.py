"""Test project structure."""

from pathlib import Path

import pytest


@pytest.mark.unit
class TestProjectStructure:
    """Test project directory structure."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_src_directory_exists(self, project_root: Path) -> None:
        """Test src directory exists."""
        assert (project_root / "src").is_dir()

    def test_backlog_manager_package_exists(self, project_root: Path) -> None:
        """Test backlog_manager package exists."""
        assert (project_root / "src" / "backlog_manager").is_dir()
        assert (project_root / "src" / "backlog_manager" / "__init__.py").is_file()

    def test_domain_layer_exists(self, project_root: Path) -> None:
        """Test domain layer exists."""
        domain_path = project_root / "src" / "backlog_manager" / "domain"
        assert domain_path.is_dir()
        assert (domain_path / "entities").is_dir()
        assert (domain_path / "value_objects").is_dir()
        assert (domain_path / "exceptions").is_dir()
        assert (domain_path / "interfaces").is_dir()

    def test_application_layer_exists(self, project_root: Path) -> None:
        """Test application layer exists."""
        app_path = project_root / "src" / "backlog_manager" / "application"
        assert app_path.is_dir()
        assert (app_path / "use_cases").is_dir()
        assert (app_path / "dto").is_dir()

    def test_infrastructure_layer_exists(self, project_root: Path) -> None:
        """Test infrastructure layer exists."""
        infra_path = project_root / "src" / "backlog_manager" / "infrastructure"
        assert infra_path.is_dir()
        assert (infra_path / "database").is_dir()
        assert (infra_path / "logging").is_dir()

    def test_presentation_layer_exists(self, project_root: Path) -> None:
        """Test presentation layer exists."""
        pres_path = project_root / "src" / "backlog_manager" / "presentation"
        assert pres_path.is_dir()

    def test_tests_directory_exists(self, project_root: Path) -> None:
        """Test tests directory structure exists."""
        tests_path = project_root / "tests"
        assert tests_path.is_dir()
        assert (tests_path / "unit").is_dir()
        assert (tests_path / "integration").is_dir()

    def test_pyproject_toml_exists(self, project_root: Path) -> None:
        """Test pyproject.toml exists."""
        assert (project_root / "pyproject.toml").is_file()
