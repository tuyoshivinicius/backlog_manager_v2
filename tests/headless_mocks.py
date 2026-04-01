"""Shared mock infrastructure for headless PySide6 tests.

Provides MockSignal (descriptor-based), MockQBase, and a helper to create
the sys.modules mock dict for PySide6.
"""

from __future__ import annotations

from unittest.mock import MagicMock


class _SignalInstance:
    """Per-instance signal that records emissions."""

    def __init__(self):
        self.emissions = []

    def emit(self, *args):
        self.emissions.append(args)

    def connect(self, slot):
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def disconnect(self, slot=None):
        """Stub: simula interface QAbstractItemModel para testes headless."""


class MockSignal:
    """Descriptor-based Signal mock.

    When used as a class attribute (like PySide6's Signal), creates a
    per-instance _SignalInstance so emissions don't leak between tests.
    """

    def __init__(self, *args):
        self._args = args

    def __set_name__(self, owner, name):
        self._attr = f"_sig_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if not hasattr(obj, self._attr):
            setattr(obj, self._attr, _SignalInstance())
        return getattr(obj, self._attr)

    def emit(self, *args):
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def connect(self, slot):
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def disconnect(self, slot=None):
        """Stub: simula interface QAbstractItemModel para testes headless."""


class MockQBase:
    """Base class mock for QObject, QAbstractTableModel, etc.

    Accepts any arguments in __init__ to mimic Qt base classes.
    Also provides no-op stubs for common QAbstractItemModel methods
    so that subclasses like StoryTableModel work headlessly.
    """

    def __init__(self, *args, **kwargs):
        """Stub: simula interface QAbstractItemModel para testes headless."""

    # QAbstractItemModel stubs used by set_stories / data reset
    def beginResetModel(self):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def endResetModel(self):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def beginInsertRows(self, *args):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def endInsertRows(self):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def beginRemoveRows(self, *args):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""

    def endRemoveRows(self):  # noqa: N802
        """Stub: simula interface QAbstractItemModel para testes headless."""


class MockQSettings:
    """Dict-based QSettings mock for headless tests."""

    _store: dict[str, object] = {}
    _group: str = ""

    def __init__(self, *args, **kwargs):
        """Stub: simula interface QSettings para testes headless."""

    def beginGroup(self, group):  # noqa: N802
        self._group = group

    def endGroup(self):  # noqa: N802
        self._group = ""

    def setValue(self, key, value):  # noqa: N802
        MockQSettings._store[f"{self._group}/{key}"] = value

    def value(self, key, default=None):
        return MockQSettings._store.get(f"{self._group}/{key}", default)

    def remove(self, key):
        prefix = f"{key}/"
        to_remove = [k for k in MockQSettings._store if k.startswith(prefix)]
        for k in to_remove:
            del MockQSettings._store[k]

    def sync(self):
        """Stub: simula interface QSettings para testes headless."""

    class Format:  # noqa: D106
        IniFormat = 0  # noqa: N815 - Simula enum Qt.QSettings.Format

    class Scope:  # noqa: D106
        UserScope = 0  # noqa: N815 - Simula enum Qt.QSettings.Scope

    @classmethod
    def reset(cls):
        cls._store = {}


def create_pyside6_mocks(
    *,
    with_qsettings: bool = False,
    with_table_model: bool = False,
) -> tuple[MagicMock, dict[str, MagicMock]]:
    """Create mock PySide6 modules for sys.modules patching.

    Returns:
        Tuple of (mock_qt_core, modules_dict) where modules_dict is suitable
        for use with patch.dict("sys.modules", ...).
    """
    mock_qt_core = MagicMock()
    mock_qt_core.Signal = MockSignal
    mock_qt_core.QObject = MockQBase

    if with_qsettings:
        mock_qt_core.QSettings = MockQSettings

    if with_table_model:
        mock_qt_core.QAbstractTableModel = MockQBase
        mock_qt_core.QSortFilterProxyModel = MockQBase
        mock_qt_core.QModelIndex = MagicMock
        mock_qt_core.QPersistentModelIndex = MagicMock

        # Qt roles / flags as plain ints matching real Qt values
        mock_qt_core.Qt = MagicMock()
        mock_qt_core.Qt.ItemDataRole.DisplayRole = 0
        mock_qt_core.Qt.ItemDataRole.TextAlignmentRole = 7
        mock_qt_core.Qt.ItemDataRole.ToolTipRole = 3
        mock_qt_core.Qt.ItemDataRole.BackgroundRole = 8
        mock_qt_core.Qt.ItemDataRole.UserRole = 256
        mock_qt_core.Qt.ItemDataRole.EditRole = 2
        mock_qt_core.Qt.AlignmentFlag.AlignCenter = 4
        mock_qt_core.Qt.AlignmentFlag.AlignLeft = 1
        mock_qt_core.Qt.AlignmentFlag.AlignVCenter = 128
        mock_qt_core.Qt.Orientation.Horizontal = 1
        mock_qt_core.Qt.Orientation.Vertical = 2

    modules_dict = {
        "PySide6": MagicMock(),
        "PySide6.QtCore": mock_qt_core,
        "PySide6.QtWidgets": MagicMock(),
        "PySide6.QtGui": MagicMock(),
    }

    return mock_qt_core, modules_dict
