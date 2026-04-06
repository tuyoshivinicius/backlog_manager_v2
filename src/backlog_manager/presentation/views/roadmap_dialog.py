"""Roadmap Dialog View.

This module provides a fullscreen QDialog with a Gantt-like timeline
visualization of stories using matplotlib embedded in PySide6.
Features: color-coded status bars, collapsible feature groups, filtering,
enriched tooltips with dependency arrows, progress bars, and status footer.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QStyle,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.presentation.theme.theme import (
    DESIGN_TOKENS,
    STATUS_PALETTE,
    get_icon_manager,
)
from backlog_manager.presentation.viewmodels.roadmap_viewmodel import (
    RoadmapData,
    RoadmapFilters,
    RoadmapGroup,
    RoadmapViewModel,
)

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import MouseEvent

    from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

logger = logging.getLogger(__name__)

# Layout constants
BAR_HEIGHT: float = 0.6
SUMMARY_BAR_HEIGHT: float = 1.0
GROUP_SPACING: float = 1.5
LABEL_FONT_SIZE: int = 8
GROUP_FONT_SIZE: int = 9
MIN_BAR_WIDTH_DAYS: int = 1
MIN_LABEL_HEIGHT_PX: int = 14
ZOOM_FACTOR_IN: float = 1.25
ZOOM_FACTOR_OUT: float = 0.8
DEFAULT_COLOR: str = "#E5E5E5"
DEFAULT_EDGE_COLOR: str = "#525252"
FILTER_ACTIVE_STYLE: str = "border: 2px solid #0066CC;"

# Today line constants
TODAY_LINE_COLOR: str = "#ED8936"
TODAY_LINE_WIDTH: float = 2.0
TODAY_LINE_ALPHA: float = 0.8
TODAY_LINE_ZORDER: int = 10

# Dependency arrow constants
DEPENDENCY_COLOR: str = "#4A5568"

# Zoom and label constants
ZOOM_MAX_DAYS: int = 7
LEGEND_PATCH_SIZE: int = 12
MAX_LABEL_CHARS: int = 60
MIN_HEIGHT_PER_ITEM: int = 35
MIN_CANVAS_HEIGHT: int = 400

# Story code rendering constants
CODE_FONT_SIZE: int = 7
CODE_CHAR_WIDTH_PX: int = 6
CODE_MIN_BAR_PADDING: int = 4

# Progress color thresholds
PROGRESS_COLOR_HIGH: str = "#18794E"
PROGRESS_COLOR_MID: str = "#B45309"
PROGRESS_COLOR_LOW: str = "#991B1B"

# Search debounce interval
SEARCH_DEBOUNCE_MS: int = 300

# Pan/drag constants
PAN_CLICK_THRESHOLD: float = 5.0
PAN_VISIBLE_RATIO: float = 0.2
KEYBOARD_PAN_RATIO: float = 0.10

# Status progress mapping (fraction of completion per status)
STATUS_PROGRESS: dict[str, float] = {
    "BACKLOG": 0.0,
    "EXECUCAO": 0.33,
    "TESTES": 0.66,
    "CONCLUIDO": 1.0,
    "IMPEDIDO": 0.0,
}


def _count_business_days(start: date, end: date) -> int:
    """Count business days (Mon-Fri) between two dates inclusive."""
    if start > end:
        return 0
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5:
            count += 1
        current += timedelta(days=1)
    return count


def _build_tooltip_text(story: StoryOutputDTO) -> str:
    """Build enriched plain-text tooltip for a story bar."""
    start = str(story.start_date) if story.start_date else "N/A"
    end = str(story.end_date) if story.end_date else "N/A"

    if story.start_date and story.end_date:
        biz_days = _count_business_days(story.start_date, story.end_date)
        duration_text = f"{biz_days} dias uteis"
    else:
        duration_text = "N/A"

    palette = STATUS_PALETTE.get(story.status)
    symbol = palette.symbol if palette else ""
    developer = story.developer_name or "Sem responsavel"
    deps = (
        ", ".join(story.dependency_ids) if story.dependency_ids else "Sem dependencias"
    )

    return (
        f"{story.name}\n"
        f"{'─' * 30}\n"
        f"Status: {story.status} {symbol}\n"
        f"Responsavel: {developer}\n"
        f"Story Points: {story.story_points}\n"
        f"Inicio: {start}\n"
        f"Fim: {end}\n"
        f"Duracao: {duration_text}\n"
        f"Componente: {story.component}\n"
        f"Dependencias: {deps}"
    )


def _get_progress_color(percent: float) -> str:
    """Return color for progress percentage thresholds."""
    if percent > 75:
        return PROGRESS_COLOR_HIGH
    if percent >= 25:
        return PROGRESS_COLOR_MID
    return PROGRESS_COLOR_LOW


class RoadmapDialog(QDialog):
    """Fullscreen dialog with matplotlib Gantt-like roadmap timeline."""

    def __init__(
        self,
        viewmodel: RoadmapViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize roadmap dialog with viewmodel and optional parent."""
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._data: RoadmapData | None = None
        self._bar_data: list[tuple[float, float, float, StoryOutputDTO]] = []
        self._group_click_regions: list[tuple[float, float, str]] = []
        self._dependency_arrows: list[FancyArrowPatch] = []
        self._story_positions: dict[str, tuple[float, float]] = {}

        # Pan/drag state
        self._is_panning: bool = False
        self._pan_start_x: float | None = None
        self._pan_start_xlim: tuple[float, float] | None = None

        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("Roadmap - Visualizacao de Timeline")

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toolbar
        self._toolbar = self._create_toolbar()
        main_layout.addWidget(self._toolbar)

        # Loading indicator
        self._loading_label = QLabel("Carregando dados do roadmap...")
        self._loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._loading_label.setStyleSheet(
            f"font-size: {DESIGN_TOKENS['font-size-md']}; "
            f"padding: 40px; color: {DESIGN_TOKENS['text-secondary']};"
        )
        main_layout.addWidget(self._loading_label)

        # Empty message
        self._empty_label = QLabel(
            "Nenhuma historia com datas calculadas.\n"
            "Execute o cronograma e a alocacao antes de visualizar o roadmap."
        )
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(
            f"font-size: {DESIGN_TOKENS['font-size-base']}; "
            f"padding: 40px; color: {DESIGN_TOKENS['text-muted']};"
        )
        self._empty_label.hide()
        main_layout.addWidget(self._empty_label)

        # Matplotlib canvas inside scroll area for dynamic height
        self._figure = Figure(figsize=(10, 6), dpi=100)
        self._canvas = FigureCanvas(self._figure)
        self._ax: Axes = self._figure.add_subplot(111)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.setWidget(self._canvas)
        self._scroll_area.hide()
        main_layout.addWidget(self._scroll_area, 1)

        # Forward non-Ctrl wheel events to scroll area for vertical panning
        _original_wheel = self._canvas.wheelEvent

        def _wheel_handler(event):  # type: ignore[no-untyped-def]
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                _original_wheel(event)
            else:
                self._scroll_area.wheelEvent(event)

        self._canvas.wheelEvent = _wheel_handler  # type: ignore[method-assign]

        # Status bar
        self._status_label = QLabel()
        self._status_label.setStyleSheet(
            f"padding: {DESIGN_TOKENS['spacing-1']} {DESIGN_TOKENS['spacing-2']}; "
            f"background: {DESIGN_TOKENS['surface']}; "
            f"border-top: 1px solid {DESIGN_TOKENS['border']}; "
            f"font-size: {DESIGN_TOKENS['font-size-sm']};"
        )
        main_layout.addWidget(self._status_label)

        # Set default cursor for pan interaction
        self._canvas.setCursor(Qt.CursorShape.OpenHandCursor)

        # Connect matplotlib events
        self._canvas.mpl_connect("scroll_event", self._on_scroll)
        self._canvas.mpl_connect("motion_notify_event", self._on_hover)
        self._canvas.mpl_connect("button_press_event", self._on_click)
        self._canvas.mpl_connect("button_press_event", self._on_pan_press)
        self._canvas.mpl_connect("motion_notify_event", self._on_pan_move)
        self._canvas.mpl_connect("button_release_event", self._on_pan_release)

        logger.debug("RoadmapDialog initialized")

    @staticmethod
    def _create_separator() -> QFrame:
        """Create a vertical separator line for toolbar group division."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Plain)
        sep.setStyleSheet(
            f"color: {DESIGN_TOKENS['border']}; "
            f"margin: 0 {DESIGN_TOKENS['spacing-2']};"
        )
        return sep

    def _create_toolbar(self) -> QWidget:
        """Create the toolbar with zoom, filters, dependencies, and actions."""
        toolbar = QWidget()
        toolbar.setStyleSheet(
            f"background: {DESIGN_TOKENS['surface']}; "
            f"border-bottom: 1px solid {DESIGN_TOKENS['border']}; "
            f"padding: {DESIGN_TOKENS['spacing-1']};"
        )
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(8, 4, 8, 4)

        self._create_zoom_group(layout)
        layout.addWidget(self._create_separator())
        self._create_filter_group(layout)
        layout.addWidget(self._create_separator())
        self._create_dependency_group(layout)
        layout.addStretch()
        layout.addWidget(self._create_separator())
        self._create_actions_group(layout)

        return toolbar

    def _create_zoom_group(self, layout: QHBoxLayout) -> None:
        """Create zoom controls group in toolbar."""
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedWidth(30)
        zoom_in_btn.setToolTip("Ampliar (Ctrl+Scroll Up)")
        zoom_in_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        zoom_in_btn.clicked.connect(lambda: self._apply_zoom(ZOOM_FACTOR_IN))
        layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedWidth(30)
        zoom_out_btn.setToolTip("Reduzir (Ctrl+Scroll Down)")
        zoom_out_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        zoom_out_btn.clicked.connect(lambda: self._apply_zoom(ZOOM_FACTOR_OUT))
        layout.addWidget(zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setToolTip("Nivel de zoom atual")
        layout.addWidget(self._zoom_label)

        fit_btn = QPushButton("Ajustar a tela")
        fit_btn.setToolTip("Mostrar todo o periodo do roadmap")
        fit_btn.setIcon(
            fit_btn.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
        )
        fit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        fit_btn.clicked.connect(self._on_fit_view)
        layout.addWidget(fit_btn)

        fit_content_btn = QPushButton("Ajustar ao conteudo")
        fit_content_btn.setToolTip("Focar na regiao de maior densidade")
        fit_content_btn.setIcon(
            fit_content_btn.style().standardIcon(
                QStyle.StandardPixmap.SP_FileDialogContentsView
            )
        )
        fit_content_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        fit_content_btn.clicked.connect(self._on_fit_content)
        layout.addWidget(fit_content_btn)

    def _create_filter_group(self, layout: QHBoxLayout) -> None:
        """Create filter controls group in toolbar."""
        layout.addWidget(QLabel("Feature:"))
        self._feature_combo = QComboBox()
        self._feature_combo.addItem("Todas", None)
        self._feature_combo.currentIndexChanged.connect(self._on_filter_changed)
        self._feature_combo.setToolTip("Filtrar por feature")
        layout.addWidget(self._feature_combo)

        layout.addWidget(QLabel("Componente:"))
        self._component_combo = QComboBox()
        self._component_combo.addItem("Todos", None)
        self._component_combo.currentIndexChanged.connect(self._on_filter_changed)
        self._component_combo.setToolTip("Filtrar por componente")
        layout.addWidget(self._component_combo)

        layout.addWidget(QLabel("Responsavel:"))
        self._developer_combo = QComboBox()
        self._developer_combo.addItem("Todos", None)
        self._developer_combo.currentIndexChanged.connect(self._on_filter_changed)
        self._developer_combo.setToolTip("Filtrar por responsavel")
        layout.addWidget(self._developer_combo)

        self._search_field = QLineEdit()
        self._search_field.setPlaceholderText("\U0001f50d Buscar historia...")
        self._search_field.setMaximumWidth(200)
        self._search_field.setToolTip("Buscar historia por nome")
        self._search_field.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_field)

        # Search debounce timer
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(SEARCH_DEBOUNCE_MS)
        self._search_timer.timeout.connect(self._apply_search_filter)

        self._clear_filters_btn = QPushButton("Limpar filtros")
        self._clear_filters_btn.setToolTip("Limpar todos os filtros")
        self._clear_filters_btn.setIcon(get_icon_manager().get("x"))
        self._clear_filters_btn.clicked.connect(self._on_clear_filters)
        layout.addWidget(self._clear_filters_btn)

    def _create_dependency_group(self, layout: QHBoxLayout) -> None:
        """Create dependency toggle and counter in toolbar."""
        self._deps_btn = QPushButton("Dependencias")
        self._deps_btn.setToolTip("Mostrar/ocultar todas as dependencias")
        self._deps_btn.setIcon(get_icon_manager().get("link"))
        self._deps_btn.setCheckable(True)
        self._deps_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._deps_btn.clicked.connect(self._on_toggle_dependencies)
        layout.addWidget(self._deps_btn)

        self._counter_label = QLabel("")
        layout.addWidget(self._counter_label)

    def _create_actions_group(self, layout: QHBoxLayout) -> None:
        """Create close button in toolbar."""
        self._close_btn = QPushButton("Fechar")
        self._close_btn.setToolTip("Fechar roadmap (Esc)")
        self._close_btn.setIcon(
            self._close_btn.style().standardIcon(
                QStyle.StandardPixmap.SP_DialogCloseButton
            )
        )
        self._close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._close_btn.clicked.connect(self.close)
        layout.addWidget(self._close_btn)

    def _populate_filter_combos(self) -> None:
        """Populate filter combo boxes from available data."""
        available = self._viewmodel.get_available_filters()

        # Hide popups before repopulating to prevent ghost dropdown artifacts
        self._feature_combo.hidePopup()
        self._developer_combo.hidePopup()
        self._component_combo.hidePopup()

        self._feature_combo.blockSignals(True)
        self._feature_combo.clear()
        self._feature_combo.addItem("Todas", None)
        for f in available["features"]:
            self._feature_combo.addItem(f, f)
        self._feature_combo.blockSignals(False)

        self._developer_combo.blockSignals(True)
        self._developer_combo.clear()
        self._developer_combo.addItem("Todos", None)
        for d in available["developers"]:
            self._developer_combo.addItem(d, d)
        self._developer_combo.blockSignals(False)

        self._component_combo.blockSignals(True)
        self._component_combo.clear()
        self._component_combo.addItem("Todos", None)
        for c in available["components"]:
            self._component_combo.addItem(c, c)
        self._component_combo.blockSignals(False)

    def _build_current_filters(self) -> RoadmapFilters:
        """Build RoadmapFilters from current combo/search state."""
        feature = self._feature_combo.currentData()
        developer = self._developer_combo.currentData()
        component = self._component_combo.currentData()
        search_text = self._search_field.text().strip() or None

        return RoadmapFilters(
            feature=feature,
            developer=developer,
            component=component,
            search_text=search_text,
        )

    def _update_filter_styles(self) -> None:
        """Update visual indicator for active filters."""
        filters = self._build_current_filters()

        for combo, has_filter in [
            (self._feature_combo, filters.feature is not None),
            (self._developer_combo, filters.developer is not None),
            (self._component_combo, filters.component is not None),
        ]:
            combo.setStyleSheet(FILTER_ACTIVE_STYLE if has_filter else "")

        has_search = filters.search_text is not None and filters.search_text.strip()
        self._search_field.setStyleSheet(FILTER_ACTIVE_STYLE if has_search else "")

    def _on_filter_changed(self, _index: int = 0) -> None:
        """Handle filter combo change."""
        if self._data is None:
            return
        filters = self._build_current_filters()
        self._update_filter_styles()
        new_data = self._viewmodel.apply_filters(filters)
        self._data = new_data
        self._render_chart(new_data)

    def _on_search_changed(self, _text: str = "") -> None:
        """Handle search text change with debounce."""
        self._search_timer.start()

    def _apply_search_filter(self) -> None:
        """Apply search filter after debounce timeout."""
        if self._data is None:
            return
        filters = self._build_current_filters()
        self._update_filter_styles()
        new_data = self._viewmodel.apply_filters(filters)
        self._data = new_data
        self._render_chart(new_data)

    def _on_clear_filters(self) -> None:
        """Reset all filters and search."""
        self._feature_combo.blockSignals(True)
        self._feature_combo.setCurrentIndex(0)
        self._feature_combo.blockSignals(False)

        self._developer_combo.blockSignals(True)
        self._developer_combo.setCurrentIndex(0)
        self._developer_combo.blockSignals(False)

        self._component_combo.blockSignals(True)
        self._component_combo.setCurrentIndex(0)
        self._component_combo.blockSignals(False)

        self._search_field.blockSignals(True)
        self._search_field.clear()
        self._search_field.blockSignals(False)

        self._update_filter_styles()
        new_data = self._viewmodel.clear_filters()
        self._data = new_data
        self._render_chart(new_data)

    async def load_and_render(self) -> None:
        """Load data asynchronously and render the chart."""
        self._loading_label.show()
        self._empty_label.hide()
        self._scroll_area.hide()

        try:
            data = await self._viewmodel.load_data()
        except Exception:
            logger.exception("Erro ao carregar dados do roadmap")
            self._loading_label.hide()
            self._empty_label.setText(
                "Erro ao carregar dados do roadmap.\n"
                "Verifique o log para mais detalhes."
            )
            self._empty_label.show()
            return

        self._loading_label.hide()

        if data is None:
            self._empty_label.show()
            self._status_label.setText("Nenhuma historia agendada")
            return

        self._data = data
        self._populate_filter_combos()
        self._scroll_area.show()
        self._render_chart(data)

    def _render_chart(self, data: RoadmapData) -> None:
        """Render the Gantt chart from roadmap data."""
        ax = self._ax
        ax.clear()
        self._bar_data.clear()
        self._group_click_regions.clear()
        self._dependency_arrows.clear()
        self._story_positions.clear()

        y_pos = 0.0
        y_ticks: list[float] = []
        y_labels: list[str] = []
        group_label_indices: list[tuple[int, float]] = []
        has_any_content = False

        for group in data.groups:
            if not group.stories:
                has_any_content = True
                y_ticks.append(y_pos)
                y_labels.append(f"{group.name} (vazia)")
                self._group_click_regions.append((y_pos - 0.5, y_pos + 0.5, group.name))
                y_pos += SUMMARY_BAR_HEIGHT + GROUP_SPACING
                continue

            has_any_content = True
            group_label = self._build_group_label(group)

            if not group.expanded:
                self._render_collapsed_group(ax, data, group, y_pos)
                y_ticks.append(y_pos)
                y_labels.append(group_label)
                group_label_indices.append(
                    (len(y_labels) - 1, group.completion_percent)
                )
                self._group_click_regions.append(
                    (
                        y_pos - SUMMARY_BAR_HEIGHT / 2,
                        y_pos + SUMMARY_BAR_HEIGHT / 2,
                        group.name,
                    )
                )
                y_pos += SUMMARY_BAR_HEIGHT + GROUP_SPACING
            else:
                y_ticks.append(y_pos)
                y_labels.append(f"\u25bc {group_label}")
                group_label_indices.append(
                    (len(y_labels) - 1, group.completion_percent)
                )
                self._group_click_regions.append((y_pos - 0.5, y_pos + 0.5, group.name))
                y_pos += 1.0

                scheduled = [s for s in group.stories if s.start_date and s.end_date]
                for story in scheduled:
                    self._render_story_bar(ax, story, y_pos)
                    y_ticks.append(y_pos)
                    y_labels.append(self._build_story_label(story))
                    y_pos += 1.0

                y_pos += GROUP_SPACING - 1.0

        if not has_any_content:
            ax.text(
                0.5,
                0.5,
                "Nenhuma historia encontrada",
                transform=ax.transAxes,
                ha="center",
                va="center",
                fontsize=12,
                color="#737373",
            )
            self._figure.tight_layout()
            self._canvas.draw_idle()
            self._update_status_bar(data)
            return

        self._resize_canvas_to_content(len(y_ticks))
        self._configure_axes(ax, y_ticks, y_labels, data)
        self._colorize_group_labels(ax, group_label_indices)
        self._render_today_line(ax, data)
        self._render_legend(ax)

        self._figure.tight_layout()
        self._canvas.draw_idle()

        if self._viewmodel._show_all_dependencies:
            self._draw_all_dependency_arrows()

        self._update_status_bar(data)

    def _configure_axes(
        self,
        ax: Axes,
        y_ticks: list[float],
        y_labels: list[str],
        data: RoadmapData,
    ) -> None:
        """Configure axes appearance, ticks, and grid."""
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels, fontsize=LABEL_FONT_SIZE)
        ax.invert_yaxis()

        ax.xaxis_date()
        locator = mdates.AutoDateLocator(minticks=5)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        self._figure.autofmt_xdate(rotation=45)

        ax.grid(axis="x", alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        ax.set_facecolor("#FAFAFA")
        self._figure.set_facecolor("white")

    def _render_today_line(self, ax: Axes, data: RoadmapData) -> None:
        """Render the 'today' vertical line if within date range."""
        today = date.today()
        if data.min_date <= today <= data.max_date:
            today_num = mdates.date2num(today)
            ax.axvline(
                x=today_num,
                color=TODAY_LINE_COLOR,
                linestyle="-",
                alpha=TODAY_LINE_ALPHA,
                lw=TODAY_LINE_WIDTH,
                zorder=TODAY_LINE_ZORDER,
            )
            ax.text(
                today_num,
                ax.get_ylim()[1] if ax.yaxis_inverted() else ax.get_ylim()[0],
                " Hoje",
                fontsize=7,
                color=TODAY_LINE_COLOR,
                va="top",
                ha="left",
                zorder=TODAY_LINE_ZORDER,
            )

    @staticmethod
    def _build_story_label(story: StoryOutputDTO) -> str:
        """Build y-axis label with story code and name."""
        code = story.id
        name = story.name
        label = f"  {code} | {name}"
        if len(label) > MAX_LABEL_CHARS:
            available = MAX_LABEL_CHARS - len(code) - 8
            label = f"  {code} | {name[:available]}..."
        return label

    def _build_group_label(self, group: RoadmapGroup) -> str:
        """Build display label for a feature group with metrics."""
        name = group.name
        count = len(group.stories)
        pct = f"{group.completion_percent:.0f}%"
        label = f"\u25b6 {name} \u2014 {count} historias | {pct}"
        if len(label) > MAX_LABEL_CHARS:
            max_name = MAX_LABEL_CHARS - len(pct) - 20
            if max_name > 3:
                name = name[: max_name - 3] + "..."
            label = f"\u25b6 {name} \u2014 {count} historias | {pct}"
        return label

    def _colorize_group_labels(
        self, ax: Axes, group_label_indices: list[tuple[int, float]]
    ) -> None:
        """Apply color to group header labels based on completion percent."""
        tick_labels = ax.get_yticklabels()
        for idx, pct in group_label_indices:
            if idx < len(tick_labels):
                tick_labels[idx].set_color(_get_progress_color(pct))
                tick_labels[idx].set_fontweight("bold")

    def _render_collapsed_group(
        self, ax: Axes, data: RoadmapData, group: RoadmapGroup, y_pos: float
    ) -> None:
        """Render a collapsed group as a summary bar."""
        min_d = group.min_date
        max_d = group.max_date
        if min_d and max_d:
            start_num = mdates.date2num(min_d)
            end_num = mdates.date2num(max_d)
            width = max(end_num - start_num, MIN_BAR_WIDTH_DAYS)
        else:
            start_num = mdates.date2num(data.min_date)
            width = MIN_BAR_WIDTH_DAYS

        completion = group.completion_percent / 100.0
        ax.barh(
            y_pos,
            width,
            left=start_num,
            height=SUMMARY_BAR_HEIGHT,
            color="#D4D4D4",
            edgecolor="#737373",
            linewidth=0.8,
            alpha=0.5,
        )
        if completion > 0:
            ax.barh(
                y_pos,
                width * completion,
                left=start_num,
                height=SUMMARY_BAR_HEIGHT,
                color="#A3A3A3",
                edgecolor="#737373",
                linewidth=0.8,
            )

    def _render_story_bar(self, ax: Axes, story: StoryOutputDTO, y_pos: float) -> None:
        """Render an individual story bar with status color and progress."""
        start_num = mdates.date2num(story.start_date)
        end_num = mdates.date2num(story.end_date)
        width = max(end_num - start_num, MIN_BAR_WIDTH_DAYS)

        palette = STATUS_PALETTE.get(story.status)
        color = palette.background if palette else DEFAULT_COLOR
        edge_color = palette.foreground if palette else DEFAULT_EDGE_COLOR

        # Background bar (full width, reduced alpha)
        ax.barh(
            y_pos,
            width,
            left=start_num,
            height=BAR_HEIGHT,
            color=color,
            edgecolor=edge_color,
            linewidth=0.8,
            alpha=0.4,
        )

        # Progress bar (partial width, full alpha)
        progress = STATUS_PROGRESS.get(story.status, 0.0)
        if progress > 0:
            ax.barh(
                y_pos,
                width * progress,
                left=start_num,
                height=BAR_HEIGHT,
                color=color,
                edgecolor=edge_color,
                linewidth=0.8,
            )

        # IMPEDIDO special highlight: thicker red border
        if story.status == "IMPEDIDO":
            ax.barh(
                y_pos,
                width,
                left=start_num,
                height=BAR_HEIGHT,
                color="none",
                edgecolor="#991B1B",
                linewidth=2.5,
                linestyle="--",
            )

        self._bar_data.append((y_pos, start_num, start_num + width, story))
        mid_x = start_num + width / 2
        self._story_positions[story.id] = (mid_x, y_pos)

        # Render story code on bar
        self._render_story_code(ax, story, start_num, width, y_pos, edge_color)

    def _render_story_code(
        self,
        ax: Axes,
        story: StoryOutputDTO,
        start_num: float,
        width: float,
        y_pos: float,
        edge_color: str,
    ) -> None:
        """Render story code text on or next to the bar."""
        code = story.id
        code_width_est = len(code) * CODE_CHAR_WIDTH_PX
        bar_center_x = start_num + width / 2

        # Estimate bar width in pixels for inside/outside decision
        fig_w_px = self._figure.get_size_inches()[0] * self._figure.get_dpi()
        xlim = ax.get_xlim()
        x_range = xlim[1] - xlim[0] if xlim[1] > xlim[0] else 1
        bar_width_px = width * (fig_w_px / x_range)

        if bar_width_px > code_width_est + CODE_MIN_BAR_PADDING:
            ax.text(
                bar_center_x,
                y_pos,
                code,
                ha="center",
                va="center",
                fontsize=CODE_FONT_SIZE,
                fontfamily="monospace",
                color=edge_color,
                zorder=5,
            )
        else:
            ax.text(
                start_num + width + 0.5,
                y_pos,
                code,
                ha="left",
                va="center",
                fontsize=CODE_FONT_SIZE,
                fontfamily="monospace",
                color=edge_color,
                zorder=5,
            )

    def _render_legend(self, ax: Axes) -> None:
        """Render color legend for status types with standardized patches."""
        legend_patches = []
        for status, config in STATUS_PALETTE.items():
            patch = mpatches.Patch(
                facecolor=config.background,
                edgecolor=config.foreground,
                label=status,
            )
            legend_patches.append(patch)
        if legend_patches:
            ax.legend(
                handles=legend_patches,
                loc="upper right",
                fontsize=8,
                framealpha=0.9,
            )

    def _update_status_bar(self, data: RoadmapData) -> None:
        """Update the status bar with per-status counts and filter indication."""
        counts = data.status_counts
        status_order = ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]
        parts = [f"{s}: {counts.get(s, 0)}" for s in status_order]
        status_text = " | ".join(parts)

        filters = self._build_current_filters()
        total_cached = len(self._viewmodel._cached_stories)
        if filters.is_active:
            filter_info = (
                f"{data.total_stories} de {total_cached} historias (filtro ativo)"
            )
        else:
            filter_info = f"Total: {data.total_stories} historias"

        self._status_label.setText(
            f"{status_text} | {filter_info} | " f"{data.min_date} a {data.max_date}"
        )

        if filters.is_active:
            self._counter_label.setText(
                f"{data.total_stories} de {total_cached} historias"
            )
        else:
            self._counter_label.setText(f"{data.total_stories} historias")

    def _on_click(self, event: MouseEvent) -> None:
        """Handle click on group regions for toggle."""
        if event.inaxes != self._ax or event.ydata is None:
            return

        for y_min, y_max, group_name in self._group_click_regions:
            if y_min <= event.ydata <= y_max:
                new_data = self._viewmodel.toggle_group(group_name)
                self._data = new_data
                self._render_chart(new_data)
                return

    def _on_scroll(self, event: MouseEvent) -> None:
        """Handle Ctrl+scroll for horizontal zoom."""
        if event.key != "control" or event.inaxes != self._ax:
            return
        factor = ZOOM_FACTOR_IN if event.button == "up" else ZOOM_FACTOR_OUT
        self._apply_zoom(factor, center_x=event.xdata)

    def _apply_zoom(self, factor: float, center_x: float | None = None) -> None:
        """Apply horizontal zoom to the chart with max days limit."""
        if self._data is None:
            return

        xlim = self._ax.get_xlim()
        if center_x is None:
            center_x = (xlim[0] + xlim[1]) / 2.0

        new_half = (xlim[1] - xlim[0]) / 2.0 / factor

        if new_half * 2 < ZOOM_MAX_DAYS:
            new_half = ZOOM_MAX_DAYS / 2.0

        self._ax.set_xlim(center_x - new_half, center_x + new_half)
        self._canvas.draw_idle()
        self._update_zoom_label()

    def _update_zoom_label(self) -> None:
        """Update zoom level indicator in toolbar."""
        if self._data is None:
            return
        total_range = mdates.date2num(self._data.max_date) - mdates.date2num(
            self._data.min_date
        )
        if total_range <= 0:
            return
        xlim = self._ax.get_xlim()
        visible_range = xlim[1] - xlim[0]
        zoom_pct = (
            int((total_range / visible_range) * 100) if visible_range > 0 else 100
        )
        self._zoom_label.setText(f"{zoom_pct}%")

    def _resize_canvas_to_content(self, num_items: int) -> None:
        """Resize figure and canvas height to fit the number of y-axis items."""
        viewport = self._scroll_area.viewport()
        viewport_h = viewport.height() if viewport.height() > 0 else self.height()
        viewport_w = viewport.width() if viewport.width() > 0 else self.width()

        min_needed = max(num_items * MIN_HEIGHT_PER_ITEM, MIN_CANVAS_HEIGHT)
        canvas_height = max(min_needed, viewport_h)

        dpi = self._figure.get_dpi()
        self._figure.set_size_inches(viewport_w / dpi, canvas_height / dpi)
        self._canvas.setFixedSize(viewport_w, canvas_height)

    def keyPressEvent(self, event: Any) -> None:
        """Handle Escape to close, arrow keys for horizontal pan."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right) and self._data:
            self._handle_keyboard_pan(event.key())
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event: Any) -> None:
        """Re-render chart on dialog resize to adjust canvas width."""
        super().resizeEvent(event)
        if self._data is not None and self._scroll_area.isVisible():
            self._render_chart(self._data)

    def _on_fit_view(self) -> None:
        """Zoom to show entire roadmap period."""
        if self._data is None:
            return
        margin = 2
        self._ax.set_xlim(
            mdates.date2num(self._data.min_date) - margin,
            mdates.date2num(self._data.max_date) + margin,
        )
        self._canvas.draw_idle()
        self._update_zoom_label()

    def _on_fit_content(self) -> None:
        """Zoom to densest region of the roadmap."""
        if self._data is None:
            return
        start, end = self._viewmodel.get_density_region()
        margin = 2
        self._ax.set_xlim(
            mdates.date2num(start) - margin,
            mdates.date2num(end) + margin,
        )
        self._canvas.draw_idle()
        self._update_zoom_label()

    def _on_toggle_dependencies(self) -> None:
        """Toggle global dependency arrow visibility."""
        show_all = self._viewmodel.toggle_show_all_dependencies()
        self._deps_btn.setChecked(show_all)
        if self._data is not None:
            self._render_chart(self._data)

    def _on_hover(self, event: MouseEvent) -> None:
        """Show tooltip and dependency arrows on bar hover."""
        if self._is_panning:
            return

        self._remove_dependency_arrows()

        if event.inaxes != self._ax or event.xdata is None or event.ydata is None:
            QToolTip.hideText()
            return

        story = self._find_story_at(event.xdata, event.ydata)
        if story:
            pos = self._canvas.mapToGlobal(
                QPoint(int(event.x), int(self._canvas.height() - event.y))
            )
            QToolTip.showText(pos, _build_tooltip_text(story))
            self._draw_dependency_arrows(story)
        else:
            QToolTip.hideText()

    def _draw_dependency_arrows(self, story: StoryOutputDTO) -> None:
        """Draw arrows from story to its visible dependencies (FR-021)."""
        if not story.dependency_ids:
            return

        source_pos = self._story_positions.get(story.id)
        if not source_pos:
            return

        for i, dep_id in enumerate(story.dependency_ids):
            target_pos = self._story_positions.get(dep_id)
            if not target_pos:
                continue
            rad = 0.1 + 0.05 * i
            arrow = FancyArrowPatch(
                posA=source_pos,
                posB=target_pos,
                arrowstyle="->",
                connectionstyle=f"arc3,rad={rad}",
                color=DEPENDENCY_COLOR,
                linewidth=1.5,
                alpha=0.7,
            )
            self._ax.add_patch(arrow)
            self._dependency_arrows.append(arrow)

        if self._dependency_arrows:
            self._canvas.draw_idle()

    def _draw_all_dependency_arrows(self) -> None:
        """Draw dependency arrows for all visible stories (toggle mode)."""
        for _y, _left, _right, story in self._bar_data:
            if story.dependency_ids:
                self._draw_dependency_arrows(story)

    def _remove_dependency_arrows(self) -> None:
        """Remove all temporary dependency arrows."""
        if not self._dependency_arrows:
            return
        for arrow in self._dependency_arrows:
            arrow.remove()
        self._dependency_arrows.clear()
        self._canvas.draw_idle()

    def _find_story_at(self, x: float, y: float) -> StoryOutputDTO | None:
        """Find the story under the cursor coordinates."""
        for bar_y, bar_left, bar_right, story in self._bar_data:
            if (
                bar_left <= x <= bar_right
                and bar_y - BAR_HEIGHT / 2 <= y <= bar_y + BAR_HEIGHT / 2
            ):
                return story
        return None

    # ------------------------------------------------------------------
    # Pan/drag horizontal handlers (FR-022 to FR-028)
    # ------------------------------------------------------------------

    def _on_pan_press(self, event: MouseEvent) -> None:
        """Start pan on left-click over axes (without Ctrl)."""
        if (
            event.button != 1
            or event.key == "control"
            or event.inaxes != self._ax
            or event.xdata is None
        ):
            return
        self._is_panning = True
        self._pan_start_x = event.xdata
        self._pan_start_xlim = self._ax.get_xlim()
        self._canvas.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _on_pan_move(self, event: MouseEvent) -> None:
        """Update xlim with horizontal delta while panning."""
        if not self._is_panning or event.inaxes is None:
            return
        if self._pan_start_x is None or self._pan_start_xlim is None:
            return
        if event.xdata is None or self._data is None:
            return

        dx = event.xdata - self._pan_start_x
        new_left = self._pan_start_xlim[0] - dx
        new_right = self._pan_start_xlim[1] - dx

        data_min = mdates.date2num(self._data.min_date)
        data_max = mdates.date2num(self._data.max_date)
        new_left, new_right = self._clamp_xlim(new_left, new_right, data_min, data_max)

        self._ax.set_xlim(new_left, new_right)
        self._canvas.draw_idle()

    def _on_pan_release(self, event: MouseEvent) -> None:
        """End pan and distinguish click vs drag by threshold."""
        if not self._is_panning:
            return

        was_click = False
        if (
            self._pan_start_x is not None
            and event.xdata is not None
            and abs(event.xdata - self._pan_start_x) < PAN_CLICK_THRESHOLD
        ):
            was_click = True

        self._is_panning = False
        self._pan_start_x = None
        self._pan_start_xlim = None
        self._canvas.setCursor(Qt.CursorShape.OpenHandCursor)

        if was_click and event.inaxes == self._ax and event.ydata is not None:
            self._on_click(event)

    def _clamp_xlim(
        self,
        new_left: float,
        new_right: float,
        data_min: float,
        data_max: float,
    ) -> tuple[float, float]:
        """Clamp xlim so at least PAN_VISIBLE_RATIO of data stays visible."""
        total_range = data_max - data_min
        if total_range <= 0:
            return new_left, new_right

        min_visible = total_range * PAN_VISIBLE_RATIO
        view_width = new_right - new_left

        # Clamp: don't let the viewport go so far that less than
        # min_visible of the data range is within view
        max_left = data_max - min_visible
        min_left = data_min + min_visible - view_width

        if new_left > max_left:
            shift = new_left - max_left
            new_left -= shift
            new_right -= shift
        elif new_left < min_left:
            shift = min_left - new_left
            new_left += shift
            new_right += shift

        return new_left, new_right

    def _handle_keyboard_pan(self, key: int) -> None:
        """Shift xlim by KEYBOARD_PAN_RATIO on arrow key press."""
        if self._data is None:
            return
        xlim = self._ax.get_xlim()
        view_width = xlim[1] - xlim[0]

        data_min = mdates.date2num(self._data.min_date) - 2
        data_max = mdates.date2num(self._data.max_date) + 2
        total_range = data_max - data_min

        # No effect if zoom is ~100% (full range already visible)
        if view_width >= total_range:
            return

        shift = view_width * KEYBOARD_PAN_RATIO
        if key == Qt.Key.Key_Left:
            shift = -shift

        new_left = xlim[0] + shift
        new_right = xlim[1] + shift
        new_left, new_right = self._clamp_xlim(new_left, new_right, data_min, data_max)

        self._ax.set_xlim(new_left, new_right)
        self._canvas.draw_idle()
        self._update_zoom_label()
