# Quickstart: Correção de Problemas de Interface do Roadmap

**Branch**: `042-roadmap-ux-fix` | **Date**: 2026-04-04

## Pré-requisitos

```bash
# Python 3.11+ com Poetry
poetry install

# Verificar que matplotlib está instalado
python -c "import matplotlib; print(matplotlib.__version__)"
```

## Arquivos-chave

| Arquivo | Papel |
|---------|-------|
| `src/backlog_manager/presentation/views/roadmap_dialog.py` | View — renderização Gantt, toolbar, eventos |
| `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` | ViewModel — dados, filtros, agrupamento |
| `src/backlog_manager/presentation/theme/theme.py` | Design system — STATUS_PALETTE, DESIGN_TOKENS |
| `tests/unit/presentation/views/test_roadmap_dialog.py` | Testes headless da View |
| `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py` | Testes do ViewModel |
| `tests/headless_mocks.py` | Infraestrutura de mocks para testes sem Qt |

## Executar testes existentes

```bash
# Testes do ViewModel (rápidos, sem dependência de Qt)
poetry run pytest tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py -v

# Testes da View (headless, com mocks de PySide6)
poetry run pytest tests/unit/presentation/views/test_roadmap_dialog.py -v

# Todos os testes com cobertura
poetry run pytest tests/ --cov=src/backlog_manager/presentation -v
```

## Executar a aplicação

```bash
# Iniciar a aplicação
poetry run backlog-manager

# Abrir roadmap: Ctrl+Shift+R ou menu Ferramentas → Roadmap
```

## Ordem de implementação sugerida (por prioridade)

### P1 — Crítico

1. **US3**: Controles de janela — `setWindowFlags(Qt.WindowType.Window)` no `RoadmapDialog.__init__`
2. **US1**: Cores de status — verificar/validar implementação existente (já funcional)
3. **US2**: Expand/collapse — refinar truncamento de labels, recálculo de altura, auto-scroll

### P2 — Importante

4. **US4**: Eixo temporal — substituir `WeekdayLocator` por `AutoDateLocator`
5. **US5**: Controles de zoom — ícones, indicador %, botão "Ajustar à tela", limite de 7 dias
6. **US9**: Linha "hoje" — cor laranja, espessura 2px, label, zorder
7. **US6**: Legenda — quadrados sem símbolos, font size 8
8. **US7**: Rótulos de wave — enriquecer com feature_name no ViewModel
9. **US8**: Consistência visual — herdar stylesheet global

### P3 — Melhoria

10. **US10**: Dropdown fantasma — `hidePopup()` antes de repopular
11. **US15**: Wave 7 — criar grupos para todas as waves (incluindo vazias)
12. **US11**: Escala adaptativa — "Ajustar ao conteúdo" com cálculo de densidade
13. **US12**: Setas de dependência — cor neutra, curvatura variável, toggle global
14. **US13**: Barra de status — mini-progresso colorido, indicação de filtro
15. **US14**: Navegação — contador de resultados, auto-scroll ao expandir

## Padrão de teste headless

```python
# Importar mocks ANTES dos módulos PySide6
from unittest.mock import patch
from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.views.roadmap_dialog import RoadmapDialog
```

## Pontos de atenção

- **matplotlib no Qt**: O FigureCanvas é um QWidget — estilos Qt NÃO afetam o conteúdo matplotlib (cores, fontes, grid). Estilos Qt afetam apenas widgets Qt ao redor (toolbar, status bar, combos).
- **Coordenadas**: Y-axis é invertido (`ax.invert_yaxis()`). Y=0 é o topo.
- **Datas no matplotlib**: Usar `mdates.date2num()` para converter `datetime.date` → float. `mdates.num2date()` para o inverso.
- **Performance**: `draw_idle()` é preferível a `draw()` — agenda redraw no próximo ciclo do event loop.
- **blockSignals**: Sempre usar ao manipular combos programaticamente para evitar re-renders cascata.
