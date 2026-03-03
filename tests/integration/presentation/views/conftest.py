"""Pytest fixtures for integration tests."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_asyncio_create_task():
    """Mock asyncio.create_task to prevent 'no running event loop' errors.

    Many dialog classes call asyncio.create_task in __init__ to load data.
    This fixture patches that to avoid errors in synchronous tests.
    """
    with patch("asyncio.create_task", return_value=MagicMock()) as mock:
        yield mock
