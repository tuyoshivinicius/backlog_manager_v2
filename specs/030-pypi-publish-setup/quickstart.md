# Quickstart: PyPI Publish Setup

**Feature Branch**: `030-pypi-publish-setup`

## What This Feature Does

Prepares the project for distribution on PyPI under the name `zion-backlog-manager` by:
1. Updating `pyproject.toml` with complete package metadata
2. Adding a standalone publish script at `scripts/publish_to_pypi.py`

## Files Changed

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Modified | Package name, metadata, classifiers, entry point, twine dev dependency |
| `scripts/publish_to_pypi.py` | Created | Automated build + upload workflow |

## Zero Source Code Changes

No `.py` files in `src/` are modified. The internal namespace remains `backlog_manager`.

## How to Build

```bash
poetry build
# Produces: dist/zion_backlog_manager-0.1.0.tar.gz
#           dist/zion_backlog_manager-0.1.0-py3-none-any.whl
```

## How to Publish

### To TestPyPI (validation)

```bash
export PYPI_TOKEN="pypi-your-test-token"
python scripts/publish_to_pypi.py --test
```

### To Production PyPI

```bash
export PYPI_TOKEN="pypi-your-production-token"
python scripts/publish_to_pypi.py
```

## How End Users Install

```bash
pip install zion-backlog-manager
zion-backlog-manager  # launches the application
```

## Verification Checklist

- [ ] `poetry check` passes
- [ ] `poetry build` produces artifacts with `zion_backlog_manager` in names
- [ ] Script validates artifacts before upload
- [ ] Script errors clearly when credentials missing
- [ ] Script errors clearly when poetry/twine not installed
