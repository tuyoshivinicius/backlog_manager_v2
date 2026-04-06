# Quickstart: Visualizacao de Roadmap

**Feature Branch**: `039-roadmap-visualization`

## Pre-requisitos

1. Backlog com historias que possuem `start_date` e `end_date` preenchidos (executar planejamento antes)
2. Ambiente de desenvolvimento configurado (`poetry install`)

## Como Usar

1. Abra o Backlog Manager
2. Execute o planejamento (scheduling + alocacao) para que as historias tenham datas calculadas
3. Clique no botao/menu **"Roadmap"** na tela principal
4. A tela de roadmap abre maximizada com a timeline Gantt-like

## Interacao

- **Zoom**: `Ctrl + scroll wheel` (muda granularidade temporal)
- **Scroll horizontal**: Navega na timeline
- **Scroll vertical**: Navega entre grupos de historias
- **Hover**: Passa o mouse sobre uma barra para ver detalhes (tooltip)
- **Agrupamento**: Alterne entre "por Feature" e "por Componente" na toolbar
- **Indicadores**: Ative/desative indicadores de atraso, criticidade e deadlines
- **Fechar**: `Escape` ou botao de fechar

## Estrutura de Codigo

```
src/backlog_manager/presentation/
├── views/
│   └── roadmap_dialog.py          # Dialog principal com QGraphicsView
└── viewmodels/
    └── roadmap_viewmodel.py       # Logica de dados, agrupamento, preferencias
```

## Desenvolvimento

```bash
# Rodar testes
poetry run pytest tests/unit/presentation/test_roadmap_viewmodel.py -v
poetry run pytest tests/unit/presentation/test_roadmap_dialog.py -v

# Rodar aplicacao
poetry run backlog-manager
```

## Decisoes Tecnicas

| Decisao | Escolha | Referencia |
|---------|---------|------------|
| Renderizacao | QGraphicsView + QGraphicsScene | research.md R1 |
| Itens graficos | Subclasse de QGraphicsRectItem | research.md R1 |
| Zoom | Escala X via setTransform, Y fixo | research.md R3 |
| Labels fixos | Painel lateral sincronizado | research.md R4 |
| Tooltips | item.setToolTip(HTML) nativo | research.md R5 |
| Preferencias | QSettings grupo RoadmapIndicators | research.md R6 |
| Dialog | QDialog.showMaximized() | research.md R7 |
| Cores | STATUS_PALETTE do design system | research.md R8 |
