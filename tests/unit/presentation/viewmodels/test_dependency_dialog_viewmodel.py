"""Headless tests for DependencyDialogViewModel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.dependency_dialog_viewmodel import (
        DependencyDialogViewModel,
    )

from backlog_manager.application.dto.story import StoryOutputDTO  # noqa: E402
from backlog_manager.domain.exceptions import (  # noqa: E402
    BacklogManagerException,
    CyclicDependencyException,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_story(story_id: str, name: str = "Story") -> StoryOutputDTO:
    """Create a minimal StoryOutputDTO for testing."""
    return StoryOutputDTO(
        planning_id=1,
        id=story_id,
        component="COMP",
        name=f"{name} {story_id}",
        story_points=3,
        status="BACKLOG",
        priority=1,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
    )


def _make_vm() -> DependencyDialogViewModel:
    """Create a DependencyDialogViewModel with mock container."""
    container = MagicMock()
    return DependencyDialogViewModel(container)


def _make_vm_with_uow() -> tuple[DependencyDialogViewModel, MagicMock]:
    """Create a DependencyDialogViewModel with a mock container that has UoW."""
    container = MagicMock()
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    return DependencyDialogViewModel(container), container


# ---------------------------------------------------------------------------
# Tests — set_story
# ---------------------------------------------------------------------------


class TestDependencyDialogViewModelSetStory:
    """Tests for set_story()."""

    def test_set_story_sets_properties(self) -> None:
        vm = _make_vm()
        stories = [_make_story("S1"), _make_story("S2"), _make_story("S3")]
        vm.set_story("S1", "Story S1", stories)

        assert vm.story_id == "S1"
        assert vm.story_name == "Story S1"
        assert len(vm.available_stories) == 2  # S2 and S3 (not S1)

    def test_set_story_excludes_current(self) -> None:
        vm = _make_vm()
        stories = [_make_story("S1"), _make_story("S2")]
        vm.set_story("S1", "Story S1", stories)

        ids = [s.id for s in vm.available_stories]
        assert "S1" not in ids
        assert "S2" in ids

    def test_set_story_clears_cycle_error(self) -> None:
        vm = _make_vm()
        vm._has_cycle_error = True
        vm._cycle_error_message = "Old error"
        vm.set_story("S1", "Story S1", [])

        assert not vm.has_cycle_error
        assert vm.cycle_error_message == ""


# ---------------------------------------------------------------------------
# Tests — Properties
# ---------------------------------------------------------------------------


class TestDependencyDialogViewModelProperties:
    """Tests for readonly properties."""

    def test_initial_state(self) -> None:
        vm = _make_vm()
        assert vm.story_id == ""
        assert vm.story_name == ""
        assert vm.depends_on == []
        assert vm.dependents == []
        assert not vm.has_cycle_error


# ---------------------------------------------------------------------------
# Tests — load_dependencies
# ---------------------------------------------------------------------------


class TestDependencyDialogViewModelLoadDependencies:
    """Tests for load_dependencies()."""

    @pytest.mark.asyncio
    async def test_load_dependencies_no_story_id(self) -> None:
        """Should return early if no story_id is set."""
        vm = _make_vm()
        await vm.load_dependencies()
        assert len(vm.dependencies_changed.emissions) == 0

    @pytest.mark.asyncio
    async def test_load_dependencies_success(self) -> None:
        """Should load depends_on and dependents and emit signal."""
        vm, container = _make_vm_with_uow()
        stories = [_make_story("S1"), _make_story("S2"), _make_story("S3")]
        vm.set_story("S1", "Story S1", stories)

        mock_deps_uc = MagicMock()
        mock_deps_result = MagicMock()
        mock_deps_result.dependencies = ["S2"]
        mock_deps_uc.execute = AsyncMock(return_value=mock_deps_result)
        container.create_get_dependencies_use_case.return_value = mock_deps_uc

        mock_dependents_uc = MagicMock()
        mock_dependents_result = MagicMock()
        mock_dependents_result.dependents = ["S3"]
        mock_dependents_uc.execute = AsyncMock(return_value=mock_dependents_result)
        container.create_get_dependents_use_case.return_value = mock_dependents_uc

        await vm.load_dependencies()

        assert len(vm.depends_on) == 1
        assert vm.depends_on[0].id == "S2"
        assert len(vm.dependents) == 1
        assert vm.dependents[0].id == "S3"
        assert len(vm.dependencies_changed.emissions) == 1

    @pytest.mark.asyncio
    async def test_load_dependencies_error_emits_signal(self) -> None:
        """Should emit error_occurred on exception."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1")])

        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=RuntimeError("DB error"))
        container.create_get_dependencies_use_case.return_value = mock_uc

        await vm.load_dependencies()

        assert len(vm.error_occurred.emissions) == 1
        assert "Erro ao carregar" in vm.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests — add_dependency
# ---------------------------------------------------------------------------


class TestDependencyDialogViewModelAddDependency:
    """Tests for add_dependency()."""

    @pytest.mark.asyncio
    async def test_add_dependency_no_story_id(self) -> None:
        """Should return early if no story_id is set."""
        vm = _make_vm()
        await vm.add_dependency("S2")
        assert len(vm.dependencies_changed.emissions) == 0

    @pytest.mark.asyncio
    async def test_add_dependency_cyclic_error(self) -> None:
        """Should emit cycle_detected on CyclicDependencyException."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])

        mock_uc = MagicMock()
        exc = CyclicDependencyException(path=["S1", "S2", "S1"])
        mock_uc.execute = AsyncMock(side_effect=exc)
        container.create_add_dependency_use_case.return_value = mock_uc

        await vm.add_dependency("S2")

        assert vm.has_cycle_error
        assert len(vm.cycle_detected.emissions) == 1
        assert "Ciclo detectado" in vm.cycle_detected.emissions[0][0]

    @pytest.mark.asyncio
    async def test_add_dependency_backlog_manager_exception(self) -> None:
        """Should emit error_occurred on BacklogManagerException."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])

        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(
            side_effect=BacklogManagerException("Dependencia duplicada")
        )
        container.create_add_dependency_use_case.return_value = mock_uc

        await vm.add_dependency("S2")

        assert len(vm.error_occurred.emissions) == 1
        assert "Dependencia duplicada" in vm.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_add_dependency_generic_exception(self) -> None:
        """Should emit error_occurred on generic Exception."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])

        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=RuntimeError("Unexpected"))
        container.create_add_dependency_use_case.return_value = mock_uc

        await vm.add_dependency("S2")

        assert len(vm.error_occurred.emissions) == 1
        assert "Erro ao adicionar" in vm.error_occurred.emissions[0][0]


# ---------------------------------------------------------------------------
# Tests — remove_dependency
# ---------------------------------------------------------------------------


class TestDependencyDialogViewModelRemoveDependency:
    """Tests for remove_dependency()."""

    @pytest.mark.asyncio
    async def test_remove_dependency_no_story_id(self) -> None:
        """Should return early if no story_id is set."""
        vm = _make_vm()
        await vm.remove_dependency("S2")
        assert len(vm.dependencies_changed.emissions) == 0

    @pytest.mark.asyncio
    async def test_remove_dependency_backlog_manager_exception(self) -> None:
        """Should emit error_occurred on BacklogManagerException."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])

        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(
            side_effect=BacklogManagerException("Nao encontrada")
        )
        container.create_remove_dependency_use_case.return_value = mock_uc

        await vm.remove_dependency("S2")

        assert len(vm.error_occurred.emissions) == 1

    @pytest.mark.asyncio
    async def test_remove_dependency_generic_exception(self) -> None:
        """Should emit error_occurred on generic Exception."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])

        mock_uc = MagicMock()
        mock_uc.execute = AsyncMock(side_effect=RuntimeError("Unexpected"))
        container.create_remove_dependency_use_case.return_value = mock_uc

        await vm.remove_dependency("S2")

        assert len(vm.error_occurred.emissions) == 1
        assert "Erro ao remover" in vm.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_add_dependency_clears_cycle_error_flag(self) -> None:
        """Should clear cycle error before attempting add."""
        vm, container = _make_vm_with_uow()
        vm.set_story("S1", "Story S1", [_make_story("S1"), _make_story("S2")])
        vm._has_cycle_error = True
        vm._cycle_error_message = "Old cycle"

        mock_add_uc = MagicMock()
        mock_add_uc.execute = AsyncMock()
        container.create_add_dependency_use_case.return_value = mock_add_uc

        mock_deps_uc = MagicMock()
        mock_deps_result = MagicMock()
        mock_deps_result.dependencies = []
        mock_deps_uc.execute = AsyncMock(return_value=mock_deps_result)
        container.create_get_dependencies_use_case.return_value = mock_deps_uc

        mock_dependents_uc = MagicMock()
        mock_dependents_result = MagicMock()
        mock_dependents_result.dependents = []
        mock_dependents_uc.execute = AsyncMock(return_value=mock_dependents_result)
        container.create_get_dependents_use_case.return_value = mock_dependents_uc

        await vm.add_dependency("S2")

        assert not vm.has_cycle_error
        assert vm.cycle_error_message == ""
