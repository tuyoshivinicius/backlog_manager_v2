# Quickstart: Refatoracao do Roadmap Visualization

**Feature**: 040-roadmap-refactor
**Date**: 2026-04-02

## Pre-requisitos

1. Python 3.13+ instalado
2. Poetry instalado
3. Dependencias do projeto instaladas: `poetry install`

## Adicionar matplotlib

```bash
poetry add matplotlib@^3.10.0
```

## Arquivos a Modificar

| Arquivo | Acao |
|---------|------|
| `pyproject.toml` | Adicionar matplotlib como dependencia |
| `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` | Refatorar: remover indicadores, simplificar |
| `src/backlog_manager/presentation/views/roadmap_dialog.py` | Reescrever: substituir QGraphicsView por matplotlib |
| `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py` | Atualizar: remover testes de indicadores |
| `tests/unit/presentation/views/test_roadmap_dialog.py` | Atualizar: adaptar para nova implementacao |
| `tests/headless_mocks.py` | Adicionar mocks para matplotlib se necessario |

## Executar Testes

```bash
# Todos os testes
poetry run pytest tests/ -v

# Apenas testes do roadmap
poetry run pytest tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py tests/unit/presentation/views/test_roadmap_dialog.py -v

# Com cobertura
poetry run pytest tests/ --cov=src/backlog_manager --cov-report=term-missing
```

## Verificar Qualidade

```bash
# Type checking
poetry run mypy src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py src/backlog_manager/presentation/views/roadmap_dialog.py

# Formatacao
poetry run black src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py src/backlog_manager/presentation/views/roadmap_dialog.py

# Imports
poetry run isort src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py src/backlog_manager/presentation/views/roadmap_dialog.py
```

## Validar Funcionalidade

1. Abrir a aplicacao: `poetry run backlog-manager`
2. Menu → Roadmap (ou Ctrl+Shift+R)
3. Verificar: todas as historias com datas aparecem no grafico
4. Verificar: agrupamento por Feature com percentual
5. Alternar para agrupamento por Componente
6. Testar zoom: Ctrl+scroll e botoes +/-
7. Testar scroll: horizontal e vertical
8. Hover sobre barras: verificar tooltip com detalhes
