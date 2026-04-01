"""Headless tests for DIContainer (presentation/container.py).

Tests singleton lifecycle, use case factory methods, and lazy ViewModel
properties without requiring PySide6 at runtime.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()


# ---------------------------------------------------------------------------
# Patch PySide6 modules before importing the container
# ---------------------------------------------------------------------------
with patch.dict(sys.modules, _pyside6_mocks):
    from backlog_manager.presentation.container import DIContainer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_container():
    """Ensure every test starts with a clean singleton state."""
    DIContainer.reset()
    yield
    DIContainer.reset()


@pytest.fixture()
def container(tmp_path: Path) -> DIContainer:
    """Return an initialized DIContainer pointing to a temp DB path."""
    db = tmp_path / "test.db"
    return DIContainer.initialize(str(db))


# ---------------------------------------------------------------------------
# Singleton lifecycle
# ---------------------------------------------------------------------------


class TestSingletonLifecycle:
    """Tests for initialize / get_instance / reset."""

    def test_initialize_returns_instance(self, tmp_path: Path):
        db = tmp_path / "test.db"
        instance = DIContainer.initialize(str(db))
        assert instance is not None
        assert isinstance(instance, DIContainer)

    def test_initialize_raises_if_already_initialized(self, container):
        with pytest.raises(RuntimeError, match="already initialized"):
            DIContainer.initialize("another.db")

    def test_get_instance_returns_same_object(self, container):
        assert DIContainer.get_instance() is container

    def test_get_instance_raises_before_initialize(self):
        with pytest.raises(RuntimeError, match="not initialized"):
            DIContainer.get_instance()

    def test_reset_allows_reinitialize(self, container, tmp_path: Path):
        DIContainer.reset()
        db2 = tmp_path / "other.db"
        new_instance = DIContainer.initialize(str(db2))
        assert new_instance is not container

    def test_reset_makes_get_instance_fail(self, container):
        DIContainer.reset()
        with pytest.raises(RuntimeError, match="not initialized"):
            DIContainer.get_instance()


# ---------------------------------------------------------------------------
# Basic properties
# ---------------------------------------------------------------------------


class TestBasicProperties:
    """Tests for db_path and create_unit_of_work."""

    def test_db_path_is_pathlib_path(self, container, tmp_path: Path):
        assert isinstance(container.db_path, Path)
        assert container.db_path == tmp_path / "test.db"

    def test_create_unit_of_work(self, container):
        uow = container.create_unit_of_work()
        # SQLiteUnitOfWork is a real class; just verify it was created
        assert uow is not None


# ---------------------------------------------------------------------------
# Use case factory methods
# ---------------------------------------------------------------------------


class TestUseCaseFactories:
    """Each factory should return a freshly constructed use case instance."""

    def test_create_list_stories_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_list_stories_use_case(uow)
        assert uc is not None

    def test_create_story_use_case_factory(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_story_use_case_factory(uow)
        assert uc is not None

    def test_create_edit_story_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_edit_story_use_case(uow)
        assert uc is not None

    def test_create_delete_story_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_delete_story_use_case(uow)
        assert uc is not None

    def test_create_move_priority_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_move_priority_use_case(uow)
        assert uc is not None

    def test_create_assign_developer_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_assign_developer_use_case(uow)
        assert uc is not None

    def test_create_duplicate_story_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_duplicate_story_use_case(uow)
        assert uc is not None

    def test_create_list_developers_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_list_developers_use_case(uow)
        assert uc is not None

    def test_create_developer_use_case_factory(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_developer_use_case_factory(uow)
        assert uc is not None

    def test_create_update_developer_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_update_developer_use_case(uow)
        assert uc is not None

    def test_create_delete_developer_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_delete_developer_use_case(uow)
        assert uc is not None

    def test_create_list_features_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_list_features_use_case(uow)
        assert uc is not None

    def test_create_feature_use_case_factory(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_feature_use_case_factory(uow)
        assert uc is not None

    def test_create_update_feature_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_update_feature_use_case(uow)
        assert uc is not None

    def test_create_delete_feature_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_delete_feature_use_case(uow)
        assert uc is not None

    def test_create_add_dependency_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_add_dependency_use_case(uow)
        assert uc is not None

    def test_create_remove_dependency_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_remove_dependency_use_case(uow)
        assert uc is not None

    def test_create_get_dependencies_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_get_dependencies_use_case(uow)
        assert uc is not None

    def test_create_get_dependents_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_get_dependents_use_case(uow)
        assert uc is not None

    def test_create_execute_allocation_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_execute_allocation_use_case(uow)
        assert uc is not None

    def test_create_get_developer_availability_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_get_developer_availability_use_case(uow)
        assert uc is not None

    def test_create_calculate_schedule_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_calculate_schedule_use_case(uow)
        assert uc is not None

    def test_create_calculate_duration_use_case(self, container):
        uc = container.create_calculate_duration_use_case()
        assert uc is not None

    def test_create_calculate_story_dates_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_calculate_story_dates_use_case(uow)
        assert uc is not None

    def test_create_reset_planning_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_reset_planning_use_case(uow)
        assert uc is not None

    def test_create_count_affected_stories_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_count_affected_stories_use_case(uow)
        assert uc is not None

    def test_create_import_excel_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_import_excel_use_case(uow)
        assert uc is not None

    def test_create_import_excel_use_case_with_callback(self, container):
        uow = container.create_unit_of_work()
        cb = MagicMock()
        uc = container.create_import_excel_use_case(uow, progress_callback=cb)
        assert uc is not None

    def test_create_export_excel_use_case(self, container):
        uow = container.create_unit_of_work()
        uc = container.create_export_excel_use_case(uow)
        assert uc is not None

    def test_factory_returns_new_instance_each_call(self, container):
        """Each factory call must return a distinct object (no caching)."""
        uow = container.create_unit_of_work()
        uc1 = container.create_list_stories_use_case(uow)
        uc2 = container.create_list_stories_use_case(uow)
        assert uc1 is not uc2


# ---------------------------------------------------------------------------
# Lazy ViewModel properties
# ---------------------------------------------------------------------------


class TestViewModelProperties:
    """ViewModel properties are lazy-loaded and cached.

    We mock the ViewModel imports so we don't pull in PySide6 widgets.
    """

    def test_main_window_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.main_window_viewmodel.MainWindowViewModel",
            return_value=mock_vm,
        ):
            vm = container.main_window_viewmodel
            assert vm is mock_vm
            # Second access returns same cached instance
            assert container.main_window_viewmodel is vm

    def test_story_dialog_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.story_dialog_viewmodel.StoryDialogViewModel",
            return_value=mock_vm,
        ):
            vm = container.story_dialog_viewmodel
            assert vm is mock_vm
            assert container.story_dialog_viewmodel is vm

    def test_allocation_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.allocation_viewmodel.AllocationViewModel",
            return_value=mock_vm,
        ):
            vm = container.allocation_viewmodel
            assert vm is mock_vm
            assert container.allocation_viewmodel is vm

    def test_excel_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.excel_viewmodel.ExcelViewModel",
            return_value=mock_vm,
        ):
            vm = container.excel_viewmodel
            assert vm is mock_vm
            assert container.excel_viewmodel is vm

    def test_schedule_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.schedule_viewmodel.ScheduleViewModel",
            return_value=mock_vm,
        ):
            vm = container.schedule_viewmodel
            assert vm is mock_vm
            assert container.schedule_viewmodel is vm

    def test_config_dialog_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.config_dialog_viewmodel.ConfigDialogViewModel",
            return_value=mock_vm,
        ):
            vm = container.config_dialog_viewmodel
            assert vm is mock_vm
            assert container.config_dialog_viewmodel is vm

    def test_dependency_dialog_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.dependency_dialog_viewmodel.DependencyDialogViewModel",
            return_value=mock_vm,
        ):
            vm = container.dependency_dialog_viewmodel
            assert vm is mock_vm
            assert container.dependency_dialog_viewmodel is vm

    def test_status_bar_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.status_bar_viewmodel.StatusBarViewModel",
            return_value=mock_vm,
        ):
            vm = container.status_bar_viewmodel
            assert vm is mock_vm
            assert container.status_bar_viewmodel is vm

    def test_reset_planning_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.reset_planning_viewmodel.ResetPlanningViewModel",
            return_value=mock_vm,
        ):
            vm = container.reset_planning_viewmodel
            assert vm is mock_vm
            assert container.reset_planning_viewmodel is vm

    def test_manual_allocation_dialog_viewmodel_lazy_load(self, container):
        mock_vm = MagicMock()
        with patch(
            "backlog_manager.presentation.viewmodels.manual_allocation_dialog_viewmodel.ManualAllocationDialogViewModel",
            return_value=mock_vm,
        ):
            vm = container.manual_allocation_dialog_viewmodel
            assert vm is mock_vm
            assert container.manual_allocation_dialog_viewmodel is vm
