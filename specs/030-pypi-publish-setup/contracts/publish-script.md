# Contract: Publish Script CLI

## Location

`scripts/publish_to_pypi.py`

## Usage

```bash
# Publish to production PyPI
python scripts/publish_to_pypi.py

# Publish to TestPyPI
python scripts/publish_to_pypi.py --test
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--test` | No | False | Upload to TestPyPI instead of production PyPI |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PYPI_TOKEN` | PyPI API token (preferred). Sets `TWINE_USERNAME=__token__` and `TWINE_PASSWORD` internally. |
| `TWINE_USERNAME` | Alternative: explicit twine username |
| `TWINE_PASSWORD` | Alternative: explicit twine password/token |

**Precedence**: `PYPI_TOKEN` > `TWINE_USERNAME`/`TWINE_PASSWORD`

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success — package uploaded |
| 1 | Error — missing tool, missing credentials, build failure, validation failure, or upload failure |

## Workflow Steps

1. Check `poetry` is available
2. Check `twine` is available
3. Clean `dist/` directory
4. Run `poetry build`
5. Validate artifact names contain `zion_backlog_manager`
6. Upload via `twine upload`
7. Print summary (version, package URL)

## Output (Success)

```
✓ Cleaned dist/
✓ Built package v0.1.0
✓ Validated artifacts
✓ Uploaded to PyPI
  → https://pypi.org/project/zion-backlog-manager/0.1.0/
```

## Output (Error — Missing Credentials)

```
ERROR: No PyPI credentials found.
Set one of:
  - PYPI_TOKEN (recommended)
  - TWINE_USERNAME + TWINE_PASSWORD
```
