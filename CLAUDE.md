
## Active Technologies
- Python 3.11+ + PySide6 (UI), Pydantic (DTOs), pytest + pytest-qt (testes) (019-backlog-table)
- N/A (escopo Presentation/Application — dados ja vem do SQLite via use cases existentes) (019-backlog-table)
- Python 3.11+ + PySide6 (UI), Pydantic (DTOs), qasync (async/Qt integration) (020-busca-filtros-menu-contexto)
- N/A (escopo Presentation — dados ja vem do SQLite via use cases existentes) (020-busca-filtros-menu-contexto)
- Python 3.11+ + PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0 (022-polimento-ux-avancado)
- QSettings (INI format) for UI preferences; no SQLite schema changes (022-polimento-ux-avancado)
- Python 3.11+ + PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite (023-reset-planning)
- SQLite (no schema changes — only sets existing columns to NULL) (023-reset-planning)
- SQLite (sem alteração de schema — usa status VARCHAR(20) existente) (024-story-completion)
- Python 3.11+ + PySide6 ^6.10.0 + PySide6 (QTableView, QItemSelectionModel), qasync ^0.27.1, Pydantic ^2.0 (025-table-selection-highlight)
- N/A (escopo puramente Presentation — sem alterações de schema ou persistência) (025-table-selection-highlight)
- Python 3.11+ + PySide6 ^6.10.0 + PySide6 (QTableView, QHeaderView, QSettings), qasync ^0.27.1 (027-column-resize)
- QSettings (INI format) — sem alterações SQLite (027-column-resize)
- Python 3.11+ (PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0) + PySide6 (QDialog, QTreeWidget, QDateEdit), Pydantic (DTOs), aiosqlite (repositorios) (028-manual-allocation)
- SQLite (sem alteracao de schema — usa colunas existentes developer_id, start_date, end_date) (028-manual-allocation)

## Recent Changes
- 019-backlog-table: Added Python 3.11+ + PySide6 (UI), Pydantic (DTOs), pytest + pytest-qt (testes)
