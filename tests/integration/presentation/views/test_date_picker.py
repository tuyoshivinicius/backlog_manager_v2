"""Integration tests for DatePicker component (T013)."""

from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate

from backlog_manager.presentation.views.date_picker import DatePicker


class TestDatePickerDefaults:
    """Tests for DatePicker default configuration."""

    def test_init_defaults(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        assert picker.calendarPopup() is True
        assert picker.displayFormat() == "dd/MM/yyyy"

    def test_display_format_custom(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker(display_format="yyyy-MM-dd")
        qtbot.addWidget(picker)

        assert picker.displayFormat() == "yyyy-MM-dd"

    def test_calendar_popup_enabled(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        assert picker.calendarPopup() is True


class TestDatePickerMinMax:
    """Tests for min/max date constraints."""

    def test_min_date_constraint(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        min_d = date(2026, 1, 1)
        picker = DatePicker(min_date=min_d)
        qtbot.addWidget(picker)

        qmin = picker.minimumDate()
        assert qmin.year() == 2026
        assert qmin.month() == 1
        assert qmin.day() == 1

    def test_max_date_constraint(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        max_d = date(2026, 12, 31)
        picker = DatePicker(max_date=max_d)
        qtbot.addWidget(picker)

        qmax = picker.maximumDate()
        assert qmax.year() == 2026
        assert qmax.month() == 12
        assert qmax.day() == 31

    def test_min_and_max_date(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker(min_date=date(2026, 3, 1), max_date=date(2026, 3, 31))
        qtbot.addWidget(picker)

        assert picker.minimumDate() == QDate(2026, 3, 1)
        assert picker.maximumDate() == QDate(2026, 3, 31)


class TestDatePickerSignals:
    """Tests for date_changed signal emission."""

    def test_date_changed_signal_emits_date(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        received = []
        picker.date_changed.connect(received.append)

        new_date = date(2026, 6, 15)
        picker.set_date(new_date)

        assert len(received) == 1
        assert received[0] == new_date

    def test_date_changed_emits_datetime_date_type(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        received = []
        picker.date_changed.connect(received.append)

        picker.set_date(date(2026, 7, 20))

        assert isinstance(received[0], date)


class TestDatePickerGetSet:
    """Tests for get_date/set_date methods."""

    def test_get_date_returns_datetime_date(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        result = picker.get_date()
        assert isinstance(result, date)

    def test_set_date_updates_widget(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        target = date(2026, 8, 10)
        picker.set_date(target)

        assert picker.get_date() == target

    def test_set_date_roundtrip(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        for d in [date(2026, 1, 1), date(2026, 6, 15), date(2026, 12, 31)]:
            picker.set_date(d)
            assert picker.get_date() == d


class TestDatePickerStyling:
    """Tests for Design System styling."""

    def test_has_stylesheet(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        picker = DatePicker()
        qtbot.addWidget(picker)

        style = picker.styleSheet()
        assert len(style) > 0
        assert "font-family" in style or "border" in style
