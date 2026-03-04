# Contracts: Excel Import/Export GUI Integration

**Feature Branch**: `012-excel-gui-integration`
**Date**: 2026-03-04

## No External Contracts

This feature is a **GUI-only integration** that does not expose any new external interfaces:

- No new API endpoints
- No new CLI commands
- No new public library interfaces
- No changes to Excel file format (defined in EP-009)

## Internal UI Contract (Informational)

For test purposes, the following UI elements are guaranteed:

### Toolbar Actions

| Action Text | Object Name | Tooltip | Shortcut |
|-------------|-------------|---------|----------|
| "Importar Excel" | `action_import_excel` | "Importar dados de arquivo Excel (Ctrl+I)" | Ctrl+I |
| "Exportar Excel" | `action_export_excel` | "Exportar dados para arquivo Excel (Ctrl+E)" | Ctrl+E |

### File Dialog Filters

| Operation | Filter |
|-----------|--------|
| Import | `"Arquivos Excel (*.xlsx)"` |
| Export | `"Arquivos Excel (*.xlsx)"` |

### Default Export Filename

`backlog_export.xlsx`

### Message Box Titles

| Scenario | Title |
|----------|-------|
| Import success | "Importacao Concluida" |
| Export success | "Exportacao Concluida" |
| Import error | "Erro na Importacao" |
| Export error | "Erro na Exportacao" |
| Overwrite confirmation | "Confirmar Substituicao" |

These are internal implementation details for testing, not external contracts.
