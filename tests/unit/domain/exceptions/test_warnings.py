"""Test warnings."""

import warnings

import pytest

from backlog_manager.domain.exceptions import (
    BacklogWarning,
    BetweenWavesIdlenessInfo,
    DeadlockWarning,
    IdlenessWarning,
)


@pytest.mark.unit
class TestWarningHierarchy:
    """Test warning inheritance hierarchy."""

    def test_backlog_warning_is_warning(self) -> None:
        """Test BacklogWarning inherits from Warning."""
        assert issubclass(BacklogWarning, Warning)

    def test_deadlock_warning_inherits_backlog_warning(self) -> None:
        """Test DeadlockWarning inherits from BacklogWarning."""
        assert issubclass(DeadlockWarning, BacklogWarning)

    def test_idleness_warning_inherits_backlog_warning(self) -> None:
        """Test IdlenessWarning inherits from BacklogWarning."""
        assert issubclass(IdlenessWarning, BacklogWarning)

    def test_between_waves_info_inherits_backlog_warning(self) -> None:
        """Test BetweenWavesIdlenessInfo inherits from BacklogWarning."""
        assert issubclass(BetweenWavesIdlenessInfo, BacklogWarning)


@pytest.mark.unit
class TestDeadlockWarning:
    """Test DeadlockWarning attributes."""

    def test_attributes(self) -> None:
        """Test DeadlockWarning stores attributes correctly."""
        blocked = ["AUTH-001", "AUTH-002"]
        warning = DeadlockWarning(wave=2, blocked_stories=blocked)

        assert warning.wave == 2
        assert warning.blocked_stories == blocked

    def test_message(self) -> None:
        """Test DeadlockWarning message format."""
        warning = DeadlockWarning(wave=1, blocked_stories=["A", "B", "C"])

        assert "wave 1" in str(warning)
        assert "3 historia(s) bloqueada(s)" in str(warning)


@pytest.mark.unit
class TestIdlenessWarning:
    """Test IdlenessWarning attributes."""

    def test_attributes(self) -> None:
        """Test IdlenessWarning stores attributes correctly."""
        warning = IdlenessWarning(
            developer_id=1,
            developer_name="Joao",
            idle_days=5,
            wave=2,
        )

        assert warning.developer_id == 1
        assert warning.developer_name == "Joao"
        assert warning.idle_days == 5
        assert warning.wave == 2

    def test_message(self) -> None:
        """Test IdlenessWarning message format."""
        warning = IdlenessWarning(
            developer_id=1,
            developer_name="Maria",
            idle_days=3,
            wave=1,
        )

        assert "Maria" in str(warning)
        assert "3 dias" in str(warning)
        assert "wave 1" in str(warning)


@pytest.mark.unit
class TestBetweenWavesIdlenessInfo:
    """Test BetweenWavesIdlenessInfo attributes."""

    def test_attributes(self) -> None:
        """Test BetweenWavesIdlenessInfo stores attributes correctly."""
        warning = BetweenWavesIdlenessInfo(
            developer_id=1,
            developer_name="Carlos",
            idle_days=2,
            from_wave=1,
            to_wave=2,
        )

        assert warning.developer_id == 1
        assert warning.developer_name == "Carlos"
        assert warning.idle_days == 2
        assert warning.from_wave == 1
        assert warning.to_wave == 2

    def test_message(self) -> None:
        """Test BetweenWavesIdlenessInfo message format."""
        warning = BetweenWavesIdlenessInfo(
            developer_id=1,
            developer_name="Ana",
            idle_days=1,
            from_wave=2,
            to_wave=3,
        )

        assert "Ana" in str(warning)
        assert "1 dias" in str(warning)
        assert "wave 2" in str(warning)
        assert "wave 3" in str(warning)
        assert "esperado" in str(warning)


@pytest.mark.unit
class TestWarningEmission:
    """Test warning emission and capture."""

    def test_emit_deadlock_warning(self) -> None:
        """Test emitting DeadlockWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warnings.warn(
                DeadlockWarning(wave=1, blocked_stories=["A"]),
                category=BacklogWarning,
            )

            assert len(w) == 1
            assert issubclass(w[0].category, BacklogWarning)

    def test_filter_backlog_warnings(self) -> None:
        """Test filtering BacklogWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings("ignore", category=BacklogWarning)
            warnings.warn(
                DeadlockWarning(wave=1, blocked_stories=["A"]),
                category=DeadlockWarning,
            )

            assert len(w) == 0
