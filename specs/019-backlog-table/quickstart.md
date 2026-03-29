# Quickstart: EP-019 — Tabela de Backlog (GUI-003)

**Date**: 2026-03-29 | **Branch**: `019-backlog-table`

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- EP-017 (design system) e EP-018 (layout migration) ja integrados na branch principal

## Setup

```bash
git checkout 019-backlog-table
poetry install
```

## Ordem de Implementacao Recomendada

### 1. Enriquecer StoryOutputDTO (Application Layer)

**Arquivo**: `src/backlog_manager/application/dto/story/story_output_dto.py`

Adicionar 4 campos opcionais com defaults:

```python
developer_name: str | None = None
feature_name: str | None = None
wave: int = 0
dependency_ids: list[str] = Field(default_factory=list)
```

### 2. Atualizar ListStoriesUseCase (Application Layer)

**Arquivo**: `src/backlog_manager/application/use_cases/story/list_stories.py`

No `execute()`, apos buscar stories, construir lookup maps de developers e features, resolver nomes e dependencias, e popular os novos campos do DTO.

Referencia: `ExportExcelUseCase._build_stories_data()` usa padrao identico.

### 3. Expandir StoryTableModel (Presentation Layer)

**Arquivo**: `src/backlog_manager/presentation/viewmodels/story_table_model.py`

- Atualizar `COLUMNS` para 13 colunas na nova ordem
- Adicionar constantes `COLUMN_WIDTHS`, `CENTER_COLUMNS`, `TOOLTIP_COLUMNS`
- Reescrever `_get_display_value()` para 13 colunas
- Reescrever `_get_alignment()` usando `CENTER_COLUMNS`
- Adicionar suporte a `ToolTipRole` em `data()`

### 4. Atualizar MainWindow (Presentation Layer)

**Arquivo**: `src/backlog_manager/presentation/views/main_window.py`

- Reposicionar delegates usando busca por header text
- Configurar larguras fixas e stretch via `QHeaderView.setSectionResizeMode()`
- Adicionar overlay QLabel para estado vazio
- Conectar `stories_changed` a logica de empty state (toggle overlay + botoes)
- Verificar/ajustar `setStretchLastSection(False)`

### 5. Verificar QSS (Presentation Layer)

**Arquivo**: `src/backlog_manager/presentation/theme/stylesheet.qss`

Verificar que:
- Zebra striping funciona com `alternatingRowColors: true`
- Selecao usa `#E6F0FA` com texto escuro
- Header tem peso 600 e borda inferior

### 6. Testes Unitarios

**Arquivo**: `tests/unit/presentation/viewmodels/test_story_table_model.py`

- Testar `columnCount() == 13`
- Testar `headerData()` para todas as 13 colunas
- Testar `data(DisplayRole)` para cada coluna com formatacao
- Testar `data(TextAlignmentRole)` — centro vs esquerda
- Testar `data(ToolTipRole)` — apenas colunas 1,5,7,8
- Testar valores ausentes ("—")
- Testar estado vazio (rowCount == 0)

### 7. Atualizar Testes de Integracao

**Arquivo**: `tests/integration/presentation/test_delegates_integration.py`

- Atualizar indices de coluna para delegates
- Verificar que testes existentes passam com 13 colunas

## Executar Testes

```bash
# Testes unitarios
poetry run pytest tests/unit/presentation/viewmodels/test_story_table_model.py -v

# Testes de integracao de delegates
poetry run pytest tests/integration/presentation/test_delegates_integration.py -v

# Cobertura
poetry run pytest tests/unit/presentation/viewmodels/test_story_table_model.py --cov=src/backlog_manager/presentation/viewmodels/story_table_model --cov-report=term-missing

# Todos os testes (verificar zero regressoes)
poetry run pytest -v
```

## Verificacao Visual

1. Executar a aplicacao: `poetry run backlog-manager`
2. Verificar 13 colunas na ordem correta
3. Verificar larguras fixas e Nome com stretch
4. Verificar ID em monospace e Status como badge
5. Redimensionar janela — apenas Nome deve expandir
6. Verificar zebra striping e selecao azul claro
7. Sem historias — verificar mensagem orientativa e botoes desabilitados
8. Criar historia — verificar que mensagem desaparece
