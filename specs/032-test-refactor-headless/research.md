# Research: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Feature**: 032-test-refactor-headless
**Date**: 2026-03-31

## 1. Estrategia de Mock para ViewModels com Heranca Qt

### Decisao

Usar `unittest.mock.patch` para substituir classes base Qt (`QObject`, `QAbstractTableModel`, `QSortFilterProxyModel`) por mocks puros nos testes headless. Zero imports de PySide6 nos arquivos de teste.

### Racional

Os 12 ViewModels herdam de classes Qt:
- 10 herdam de `QObject` (AllocationViewModel, ConfigDialogViewModel, DependencyDialogViewModel, ExcelViewModel, MainWindowViewModel, ManualAllocationDialogViewModel, ResetPlanningViewModel, ScheduleViewModel, StatusBarViewModel, StoryDialogViewModel)
- 1 herda de `QSortFilterProxyModel` (FilterProxyModel)
- 1 herda de `QAbstractTableModel` (StoryTableModel)

**Padrao de mock recomendado**:

```python
# Exemplo para ViewModel que herda de QObject
from unittest.mock import MagicMock, patch, PropertyMock

# Mock QObject e Signal antes de importar o ViewModel
with patch.dict("sys.modules", {
    "PySide6": MagicMock(),
    "PySide6.QtCore": MagicMock(),
    "PySide6.QtWidgets": MagicMock(),
    "PySide6.QtGui": MagicMock(),
}):
    # Agora importar o modulo sob teste — PySide6 esta mockado
    from backlog_manager.presentation.viewmodels.allocation_viewmodel import AllocationViewModel
```

**Alternativa para Signal**: Criar um mock de Signal que registra emissoes:

```python
class MockSignal:
    """Mock para PySide6 Signal que registra emissoes."""
    def __init__(self, *args):
        self.emissions = []
    def emit(self, *args):
        self.emissions.append(args)
    def connect(self, slot):
        pass
    def disconnect(self, slot=None):
        pass
```

### Alternativas Consideradas

1. **Xvfb (virtual framebuffer)**: Instalar display virtual no CI para executar testes Qt reais. Rejeitado por adicionar dependencia de sistema, fragilidade e tempo de setup.
2. **pytest-qt em modo offscreen**: Usar `QT_QPA_PLATFORM=offscreen`. Rejeitado por ainda requerer PySide6 instalado e nao resolver o problema de dependencia.
3. **Manter testes Qt e ignorar no CI**: Status quo. Rejeitado por deixar 53 arquivos de teste sem execucao no CI.

## 2. Configuracao de Cobertura — Analise de Gap

### Decisao

A configuracao de cobertura atual (`source = ["src/backlog_manager"]`) ja mede todas as 4 camadas. O problema real e que o CI ignora testes de presentation, resultando em 0% de cobertura para codigo de presentation no CI.

### Racional

**Configuracao existente** (pyproject.toml):
```toml
[tool.coverage.run]
source = ["src/backlog_manager"]  # JA inclui todas as camadas
branch = true
```

**O que acontece no CI**:
```bash
pytest tests/unit tests/integration \
    --ignore=tests/unit/presentation \      # 24 testes excluidos
    --ignore=tests/integration/presentation  # 29 testes excluidos
```

Resultado: os 39 arquivos de `src/backlog_manager/presentation/` aparecem no relatorio com 0% (ou baixa cobertura indireta), puxando a media global para baixo.

**Correcao necessaria**: Nao e na configuracao de cobertura — e na eliminacao das flags `--ignore` do CI, que so e possivel apos tornar todos os testes headless.

### Alternativas Consideradas

1. **Adicionar `omit` para presentation**: Excluir presentation da medicao. Rejeitado por esconder o problema.
2. **Manter `--ignore` e medir separadamente**: Gerar dois relatorios. Rejeitado por complexidade desnecessaria.

## 3. Migracao de Factories — Analise de Dependencias

### Decisao

Migrar `tests/e2e/factories.py` (244 linhas) para `tests/factories.py`. O arquivo contem 7 funcoes factory que criam entidades de dominio puras, sem dependencia de PySide6.

### Racional

**Funcoes factory e suas dependencias**:

| Funcao | Imports | Dependencia GUI |
|--------|---------|-----------------|
| `create_stories()` | `Story` (domain) | Nenhuma |
| `create_stories_with_dependencies()` | `Story` (domain) | Nenhuma |
| `get_dependency_pairs()` | Nenhum externo | Nenhuma |
| `create_developers()` | `Developer` (domain) | Nenhuma |
| `create_features()` | `Feature` (domain) | Nenhuma |
| `create_cyclic_graph()` | `Story` (domain) | Nenhuma |
| `create_unbalanced_stories()` | `Story` (domain) | Nenhuma |

Todas as factories usam apenas entidades de dominio — migracao direta sem alteracoes.

### Alternativas Consideradas

1. **Manter em tests/e2e/**: Rejeitado porque o diretorio e2e sera removido.
2. **Mover para tests/conftest.py**: Rejeitado por poluir o conftest global (244 linhas).
3. **Criar tests/helpers/factories.py**: Rejeitado por adicionar diretorio desnecessario para um unico arquivo.

## 4. Reestruturacao de conftest.py

### Decisao

Remover todas as fixtures Qt/qasync do `tests/conftest.py` raiz. Manter fixtures de DB e container. Remover `tests/e2e/conftest.py` integralmente. Adaptar `tests/integration/presentation/conftest.py` e `tests/integration/presentation/views/conftest.py`.

### Racional

**tests/conftest.py** (284 linhas):
- Fixtures a MANTER: `temp_db_path`, `db_connection`, `uow`, `container`, `sample_story_dto`, `sample_stories`, `create_story_input`, `create_developer_input`, `create_feature_input`, `run_async()`
- Fixtures a REMOVER: `qasync_loop`, `qapp_args` e qualquer fixture que importe PySide6

**tests/e2e/conftest.py** (295 linhas):
- REMOVER integralmente (junto com todo o diretorio e2e)

**tests/integration/presentation/conftest.py** (19 linhas):
- Contem mock de `asyncio.create_task` — MANTER mas verificar se ainda necessario apos reescrita headless

**tests/integration/presentation/views/conftest.py** (19 linhas):
- Mesmo padrao de mock asyncio — MANTER/ADAPTAR

### Alternativas Consideradas

1. **Manter conftest.py inalterado**: Rejeitado por deixar imports mortos de PySide6.
2. **Criar conftest separado para headless**: Rejeitado por fragmentar fixtures desnecessariamente.

## 5. Triagem de Testes de Integracao Presentation

### Decisao

Analisar individualmente cada um dos 29 arquivos em `tests/integration/presentation/` para classificar como "remover" ou "reescrever headless".

### Racional

**Criterios de triagem**:
1. **REMOVER** se: testa apenas renderizacao visual (QPainter, layout), ou logica ja coberta por testes unitarios de ViewModel
2. **REESCREVER** se: testa fluxo de integracao entre ViewModel e servicos que nao esta coberto em outro lugar

**Arquivos candidatos a reescrita headless** (testam logica de negocio):
- `test_main_window_filters.py` — logica de filtragem
- `test_empty_state_view.py` — estado vazio do ViewModel
- `test_theme_integration.py` — configuracao de tema (pode ser testado via dicionario)

**Arquivos candidatos a remocao** (puramente visuais ou duplicados):
- `test_delegates_integration.py` — renderizacao de delegates
- Maioria dos `views/test_*.py` — testam widgets Qt diretamente

### Alternativas Consideradas

1. **Reescrever todos**: Rejeitado por desperdicio de esforco em testes puramente visuais.
2. **Remover todos**: Rejeitado por perder cobertura de logica de negocio em fluxos de integracao.

## 6. Triagem de Testes Unitarios Presentation

### Decisao

Analisar individualmente cada um dos 24 arquivos em `tests/unit/presentation/` para classificar como "remover" ou "reescrever headless".

### Racional

**ViewModels com testes existentes** (14 arquivos):
- Maioria testa logica de negocio e transformacao de dados — REESCREVER com mocks de Qt
- `test_story_table_model.py` (544 linhas) — complexo, testa data(), rowCount(), headerData() etc. REESCREVER com mock de QAbstractTableModel
- `test_filter_proxy_model.py` (373 linhas) — testa filtragem. REESCREVER com mock de QSortFilterProxyModel

**Delegates com testes existentes** (2 arquivos):
- `test_status_badge_delegate.py` — testa sizeHint() e paint() com QPainter real. REMOVER paint tests, REESCREVER sizeHint/logica
- `test_monospace_delegate.py` — testa formatacao de fonte. REMOVER (puramente visual)

**Views com testes existentes** (2 arquivos):
- `test_sp_breakdown_label.py` — testa formatacao de texto. REESCREVER se logica util
- `test_confirm_reset_dialog.py` — testa existencia de botoes. REMOVER (puramente visual)

**Theme** (1 arquivo):
- `test_theme.py` — testa dicionario de cores/estilos. REESCREVER (nao depende de Qt widgets)

## 7. Pragmas no-cover para Arquivos Puramente Visuais

### Decisao

Adicionar `# pragma: no cover` em 3 arquivos puramente visuais nao testaveis headless, conforme excecao aprovada no spec (FR-012).

### Racional

| Arquivo | Razao | Linhas estimadas |
|---------|-------|-----------------|
| `src/backlog_manager/presentation/app.py` | Entry point Qt, cria QApplication | Arquivo inteiro |
| `src/backlog_manager/presentation/views/about_dialog.py` | Dialog puramente visual | Arquivo inteiro |
| `src/backlog_manager/presentation/views/rich_tooltip.py` | Tooltip com QPainter custom | Arquivo inteiro |

Estes 3 arquivos representam codigo que so pode ser testado com display grafico real. Excluir da cobertura e preferivel a manter testes frageis com Xvfb.

## 8. Estrategia de Ampliacao de Cobertura

### Decisao

Priorizar criacao de novos testes headless nos ViewModels com menor cobertura e maior impacto no negocio. Usar a matriz de prioridade do docs/plan-test-refactor.md como guia.

### Racional

**Prioridade alta** (cobertura < 40%, logica critica):
- `excel_viewmodel.py` (~28% cobertura)
- `schedule_viewmodel.py` (~38% cobertura)
- `manual_allocation_dialog_viewmodel.py` (baixa cobertura)

**Prioridade media** (cobertura 40-70%):
- `story_table_model.py`
- `filter_proxy_model.py`
- `dependency_dialog_viewmodel.py`

**Prioridade baixa** (cobertura > 70% ou views puramente visuais):
- Views em `src/backlog_manager/presentation/views/` — maioria puramente visual
- `constants.py`, `container.py` — configuracao

### Alternativas Consideradas

1. **Testar tudo igualmente**: Rejeitado por nao maximizar retorno por teste escrito.
2. **Focar apenas em ViewModels**: Rejeitado por ignorar delegates e theme que tambem contam para cobertura.
