# Contract: CLI Entry Point

## Command

```
zion-backlog-manager
```

## Behavior

- Invokes `backlog_manager.presentation.app:main`
- Launches the PySide6 GUI application
- Returns exit code 0 on normal exit, non-zero on error

## Installation

```bash
pip install zion-backlog-manager
```

## Namespace

- **PyPI name**: `zion-backlog-manager` (what users install)
- **Python import**: `backlog_manager` (unchanged internal namespace)
- **CLI command**: `zion-backlog-manager` (console_scripts entry point)
