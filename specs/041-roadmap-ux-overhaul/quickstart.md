# Quickstart: Roadmap UX Overhaul

**Feature**: 041-roadmap-ux-overhaul
**Date**: 2026-04-03

## Visao Geral

Esta feature reformula a UX do roadmap existente para resolver 11 problemas criticos de usabilidade. O escopo e restrito a camada Presentation (View + ViewModel), sem alteracoes em Domain, Application ou Infrastructure.

## Arquivos a Modificar

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` | MODIFICAR | Adicionar agrupamento por wave, filtragem, estado colapso, contagem por status |
| `src/backlog_manager/presentation/views/roadmap_dialog.py` | MODIFICAR | Refatorar rendering com cores, colapso, filtros, tooltips, dependencias, legenda, rodape |
| `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py` | MODIFICAR | Testes para novos metodos |
| `tests/unit/presentation/views/test_roadmap_dialog.py` | MODIFICAR | Testes para novos widgets |

## Pre-Requisitos

- Python 3.13+ instalado
- Dependencias instaladas: `poetry install`
- Familiaridade com matplotlib (barh, axes, annotations)
- Familiaridade com PySide6 (QDialog, QComboBox, QLineEdit, QToolBar)

## Como Executar

```bash
# Instalar dependencias
poetry install

# Executar a aplicacao
poetry run python -m backlog_manager

# Executar testes
poetry run pytest tests/unit/presentation/ -v

# Executar testes com cobertura
poetry run pytest tests/unit/presentation/ --cov=src/backlog_manager/presentation --cov-report=term-missing
```

## Ordem de Implementacao Recomendada

1. **ViewModel primeiro**: Adicionar RoadmapFilters, agrupamento por wave, toggle_group, apply_filters
2. **Testes do ViewModel**: Validar logica antes de tocar na View
3. **View - Colapso/Expansao**: Renderizar barras-resumo para grupos colapsados
4. **View - Cores e Legenda**: Usar STATUS_PALETTE para cores + legenda
5. **View - Progresso Visual**: Barras com preenchimento parcial
6. **View - Linha "Hoje"**: Ja existente — apenas ajustar estilo
7. **View - Toolbar/Filtros**: Substituir ComboBox de agrupamento por controles de filtro
8. **View - Tooltips Enriquecidos**: Estender tooltip com todos os campos
9. **View - Setas de Dependencias**: Overlay temporario no hover
10. **View - Rodape Estatistico**: Contagem por status
11. **Testes da View**: Validar widgets e rendering

## Decisoes Arquiteturais Chave

- **Agrupamento fixo por wave**: Sem opcao de mudar criterio. RoadmapGroupMode removido.
- **Colapso via re-render**: Ao clicar no grupo, o chart e redesenhado inteiro (sem animacao).
- **Filtros no ViewModel**: Logica AND, operando sobre cache in-memory.
- **Dependencias como overlay**: Setas temporarias desenhadas no hover, removidas ao sair.
- **Performance via colapso**: Grupos colapsados por padrao reduzem renderizacao de 200 barras para ~20 barras-resumo.
