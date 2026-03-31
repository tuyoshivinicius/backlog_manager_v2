"""E2E tests for ProgressDialog cancellation flow.

Tests verify cancel button visibility, task cancellation, and signal emission.
"""

from __future__ import annotations

import asyncio

import pytest
from backlog_manager.presentation.views.progress_dialog import ProgressDialog
from PySide6.QtWidgets import QPushButton

pytestmark = [pytest.mark.e2e]


class TestProgressDialogCancellation:
    """Tests for ProgressDialog cancellation support."""

    def test_cancel_button_hidden_initially(self, qtbot):
        """Cancel button is not visible when dialog first opens."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        cancel_btn = dialog.findChild(QPushButton, "cancel-button")
        assert cancel_btn is not None
        assert not cancel_btn.isVisible()

    def test_cancel_button_appears_after_timer(self, qtbot):
        """Cancel button becomes visible after 2s timer expires."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        loop = asyncio.new_event_loop()
        task = loop.create_task(asyncio.sleep(999))

        dialog.set_cancellable_task(task)

        # Manually trigger the timer timeout
        dialog._cancel_timer.setInterval(0)
        dialog._cancel_timer.start()
        qtbot.waitUntil(
            lambda: dialog.findChild(QPushButton, "cancel-button").isVisible(),
            timeout=500,
        )

        cancel_btn = dialog.findChild(QPushButton, "cancel-button")
        assert cancel_btn.isVisible()

        task.cancel()
        loop.close()

    def test_cancel_emits_signal(self, qtbot):
        """Clicking cancel emits the cancelled signal."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        loop = asyncio.new_event_loop()
        task = loop.create_task(asyncio.sleep(999))
        dialog.set_cancellable_task(task)

        # Show button immediately
        dialog._show_cancel_button()

        with qtbot.waitSignal(dialog.cancelled, timeout=200):
            cancel_btn = dialog.findChild(QPushButton, "cancel-button")
            cancel_btn.click()

        task.cancel()
        loop.close()

    def test_cancel_disables_button(self, qtbot):
        """After cancel click, button is disabled and text changes."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        loop = asyncio.new_event_loop()
        task = loop.create_task(asyncio.sleep(999))
        dialog.set_cancellable_task(task)
        dialog._show_cancel_button()

        cancel_btn = dialog.findChild(QPushButton, "cancel-button")
        cancel_btn.click()

        assert not cancel_btn.isEnabled()
        assert cancel_btn.text() == "Cancelando..."

        task.cancel()
        loop.close()

    def test_cancel_cancels_task(self, qtbot):
        """Clicking cancel calls task.cancel()."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        loop = asyncio.new_event_loop()
        task = loop.create_task(asyncio.sleep(999))
        dialog.set_cancellable_task(task)
        dialog._show_cancel_button()

        cancel_btn = dialog.findChild(QPushButton, "cancel-button")
        cancel_btn.click()

        assert task.cancelling()
        loop.close()

    def test_update_progress_switches_to_determinate(self, qtbot):
        """update_progress switches from indeterminate to determinate."""
        dialog = ProgressDialog("Processando...", indeterminate=True)
        qtbot.addWidget(dialog)

        assert dialog._progress_bar.maximum() == 0  # indeterminate

        dialog.update_progress(50, "Metade...")
        assert dialog._progress_bar.maximum() == 100
        assert dialog._progress_bar.value() == 50

    def test_close_stops_timer(self, qtbot):
        """Closing dialog stops the cancel timer."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        loop = asyncio.new_event_loop()
        task = loop.create_task(asyncio.sleep(999))
        dialog.set_cancellable_task(task)

        assert dialog._cancel_timer.isActive()
        dialog.close()
        assert not dialog._cancel_timer.isActive()

        task.cancel()
        loop.close()
