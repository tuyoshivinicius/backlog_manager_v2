# Data Model: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Feature**: 032-test-refactor-headless
**Date**: 2026-03-31

> Esta feature nao altera entidades de dominio nem schema de banco. O "data model" aqui descreve as entidades conceituais do processo de refatoracao e suas relacoes.

## Entidades

### TestFile

Representa um arquivo de teste no repositorio.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| path | str | Caminho relativo a partir de tests/ |
| level | enum(unit, integration, e2e) | Nivel de teste |
| layer | enum(domain, application, infrastructure, presentation) | Camada arquitetural |
| has_gui_dependency | bool | Importa PySide6, pytest-qt ou qasync |
| triage_decision | enum(keep, remove, rewrite_headless) | Decisao de triagem |

**Regras de validacao**:
- Se `level == e2e` → `triage_decision = remove` (todos os E2E sao removidos)
- Se `has_gui_dependency == false` → `triage_decision = keep`
- Se `has_gui_dependency == true` e `layer != presentation` → ERRO (violacao de arquitetura)

### SourceFile

Representa um arquivo fonte em src/backlog_manager/.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| path | str | Caminho relativo a partir de src/backlog_manager/ |
| layer | enum(domain, application, infrastructure, presentation) | Camada arquitetural |
| coverage_before | float | Cobertura % antes da refatoracao |
| coverage_after | float | Cobertura % apos a refatoracao |
| is_visual_only | bool | Arquivo puramente visual (pragma: no cover) |

**Regras de validacao**:
- Se `is_visual_only == true` → excluido da meta de 90%
- `coverage_after >= 90%` (meta global, nao por arquivo)

### TriageRecord

Registro da decisao de triagem para cada teste de presentation com dependencia GUI.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| test_file | TestFile | Referencia ao arquivo de teste |
| decision | enum(remove, rewrite_headless) | Decisao |
| justification | str | Por que esta decisao |
| covered_by | list[str] | Se removido, quais testes ja cobrem a logica |
| business_scenarios | list[str] | Cenarios de negocio que o teste cobre |

## Relacoes

```
TestFile --covers--> SourceFile (N:M)
  Um teste pode cobrir multiplos arquivos fonte
  Um arquivo fonte pode ser coberto por multiplos testes

TestFile --triage--> TriageRecord (1:1)
  Cada teste de presentation com GUI tem exatamente uma decisao de triagem

SourceFile --pragma--> PragmaNoCover (1:0..1)
  Apenas 3 arquivos visuais recebem pragma: no cover
```

## Inventario de Arquivos por Decisao

### E2E — REMOVER (22 arquivos)

| Arquivo | Cenarios de Negocio |
|---------|---------------------|
| test_smoke.py | Startup basico |
| test_uc001_criar_priorizar_backlog.py | CRUD de backlog |
| test_uc002_alocacao_automatica.py | Alocacao automatica |
| test_uc003_detectar_resolver_deadlock.py | Deteccao de deadlock |
| test_uc004_importar_excel.py | Import Excel |
| test_uc005_gerenciar_ondas.py | Gestao de ondas |
| test_ct001_backlog_completo.py | Cenario completo |
| test_ct002_ciclo_grafo_grande.py | Grafo grande |
| test_ct003_deadlock_devs.py | Deadlock com devs |
| test_ct004_feriados_sequencia.py | Feriados |
| test_ct005_balanceamento.py | Balanceamento |
| test_ep022_about_dialog.py | About dialog |
| test_ep022_cancellation.py | Cancelamento |
| test_ep022_dependency_indicator.py | Indicador dependencia |
| test_ep022_responsive.py | Responsividade |
| test_ep022_rich_tooltip.py | Tooltip |
| test_ep022_wave_separators.py | Separadores de onda |
| test_ep023_reset_planning.py | Reset planning |
| test_excel_roundtrip.py | Excel roundtrip |
| test_performance.py | Performance |
| conftest.py | Fixtures E2E |
| factories.py | MIGRAR para tests/factories.py |

### Presentation Unit — TRIAR (24 arquivos)

Decisao detalhada sera feita na fase de implementacao (tasks.md) com analise arquivo-por-arquivo.

### Presentation Integration — TRIAR (29 arquivos)

Decisao detalhada sera feita na fase de implementacao (tasks.md) com analise arquivo-por-arquivo.

## Pragmas no-cover

| Arquivo Fonte | Razao |
|---------------|-------|
| `presentation/app.py` | Entry point Qt — cria QApplication, event loop |
| `presentation/views/about_dialog.py` | Dialog puramente visual sem logica |
| `presentation/views/rich_tooltip.py` | Widget QPainter custom sem logica testavel |
