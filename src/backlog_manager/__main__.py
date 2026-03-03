"""Module entry point for running backlog_manager as a module.

Usage:
    python -m backlog_manager
"""

import sys

from backlog_manager.presentation.app import main

if __name__ == "__main__":
    sys.exit(main())
