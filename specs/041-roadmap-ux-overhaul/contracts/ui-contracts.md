# UI Contracts: Roadmap UX Overhaul

**Feature**: 041-roadmap-ux-overhaul
**Date**: 2026-04-03

## Contract 1: RoadmapViewModel API

### Metodos Publicos

```python
class RoadmapViewModel(QObject):
    """ViewModel do roadmap com filtragem, agrupamento por wave e colapso."""

    async def load_data(self) -> RoadmapData | None:
        """Carrega historias e features, agrupa por wave.

        Returns:
            RoadmapData com grupos colapsados por padrao, ou None se sem historias agendadas.
        """

    def toggle_group(self, group_name: str) -> RoadmapData:
        """Alterna estado de expansao/colapso de um grupo.

        Args:
            group_name: Nome do grupo (wave) a alternar.

        Returns:
            RoadmapData atualizado com estado de expansao alterado.
        """

    def apply_filters(self, filters: RoadmapFilters) -> RoadmapData:
        """Aplica filtros sobre historias cacheadas e reconstroi grupos.

        Args:
            filters: Criterios de filtragem (AND logico).

        Returns:
            RoadmapData filtrado. Grupos sem historias apos filtro sao omitidos.
        """

    def clear_filters(self) -> RoadmapData:
        """Remove todos os filtros e retorna dados completos.

        Returns:
            RoadmapData sem filtros aplicados.
        """

    def get_available_filters(self) -> dict[str, list[str]]:
        """Retorna opcoes disponiveis para cada filtro.

        Returns:
            Dict com chaves: "waves", "statuses", "developers", "components".
            Cada valor e uma lista de opcoes unicas extraidas dos dados cacheados.
        """
```

### Sinais

```python
# Nenhum sinal novo necessario — View coordena via chamadas diretas
# (padrao existente: View chama ViewModel, recebe dados, re-renderiza)
```

## Contract 2: RoadmapDialog UI

### Toolbar

| Controle | Tipo | Comportamento |
|----------|------|---------------|
| Wave filter | QComboBox | Opcoes: "Todas" + waves disponiveis. Filtra por wave selecionada. |
| Status filter | QComboBox | Opcoes: "Todos" + 5 status. Filtra por status. |
| Developer filter | QComboBox | Opcoes: "Todos" + responsaveis unicos + "Nao atribuido". |
| Component filter | QComboBox | Opcoes: "Todos" + componentes unicos. |
| Search | QLineEdit | Placeholder "Buscar historia...". Filtra por nome (case-insensitive). |
| Clear filters | QPushButton | Icone + tooltip "Limpar filtros". Reseta todos os filtros. |
| Zoom + | QPushButton | Icone + tooltip "Ampliar (Ctrl+Scroll Up)". |
| Zoom - | QPushButton | Icone + tooltip "Reduzir (Ctrl+Scroll Down)". |

### Filtro Ativo Badge

- Quando filtro ativo: ComboBox com borda colorida (#0066CC) ou badge numerico
- Quando busca ativa: QLineEdit com borda colorida

### Chart Area

| Elemento | Renderizacao | Interacao |
|----------|-------------|-----------|
| Grupo colapsado | Barra-resumo (SUMMARY_BAR_HEIGHT=1.0), cor neutra, texto "{nome} - {N}% [{total} historias]" | Click → expande grupo |
| Grupo expandido | Header texto + historias individuais como barras coloridas | Click no header → colapsa grupo |
| Historia (barra) | Cor de fundo = STATUS_PALETTE[status].background, borda = foreground, preenchimento parcial conforme STATUS_PROGRESS | Hover → tooltip + setas dependencia |
| Legenda | matplotlib legend com patches coloridos para cada status | Estatica, posicao automática |
| Linha "Hoje" | Vertical tracejada, cor #991B1B, alpha=0.5 | Nenhuma |
| Setas dependencia | FancyArrowPatch entre historia hover e suas dependencias | Aparecem no hover, desaparecem ao sair |

### Status Bar (Rodape)

Formato: `"BACKLOG: N | EXECUCAO: N | TESTES: N | CONCLUIDO: N | IMPEDIDO: N | Total: N historias | {min_date} a {max_date}"`

Reflete filtros ativos (contagem apenas das historias visiveis).

### Tooltip Enriquecido

```
{nome}
─────────────────
Status: {status} {symbol}
Responsavel: {developer_name ou "Sem responsavel"}
Story Points: {story_points}
Inicio: {start_date ou "N/A"}
Fim: {end_date ou "N/A"}
Duracao: {dias_uteis} dias uteis
Componente: {component}
Dependencias: {dep_ids ou "Sem dependencias"}
```

## Contract 3: Event Flow

### User Interactions

```
[Click grupo colapsado] → View._on_group_click(name) → ViewModel.toggle_group(name) → View._render_chart(data)
[Click grupo expandido]  → View._on_group_click(name) → ViewModel.toggle_group(name) → View._render_chart(data)
[Alterar filtro]         → View._on_filter_changed()   → ViewModel.apply_filters(f)   → View._render_chart(data)
[Digitar busca]          → View._on_search_changed()   → ViewModel.apply_filters(f)   → View._render_chart(data)
[Limpar filtros]         → View._on_clear_filters()    → ViewModel.clear_filters()     → View._render_chart(data)
[Hover historia]         → View._on_hover(event)       → Show tooltip + Draw arrows
[Hover exit]             → View._on_hover(event)       → Hide tooltip + Remove arrows
[Ctrl+Scroll]            → View._on_scroll(event)      → View._apply_zoom(factor)
[Zoom + button]          → View._on_zoom_in()          → View._apply_zoom(1.25)
[Zoom - button]          → View._on_zoom_out()         → View._apply_zoom(0.8)
```

### Group Click Detection

Para detectar click em grupo (barra-resumo ou header):
- Armazenar posicoes Y dos grupos em `_group_click_regions: list[tuple[float, float, str]]` (y_min, y_max, group_name)
- No evento `button_press_event` do matplotlib, verificar se click esta em regiao de grupo
- Se sim, chamar `_on_group_click(group_name)`
