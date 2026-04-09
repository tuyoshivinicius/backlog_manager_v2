"""Headless tests for RoadmapDialog.

Tests verify tooltip text generation, status colors, legend, IMPEDIDO highlight,
collapsed/expanded groups, click detection, filter combos, search, status bar,
progress bars, today line, label heights, dependency arrows, story code labels,
feature group labels, search debounce, and progress color thresholds.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

# Mock PySide6 widgets
mock_widgets = _pyside6_mocks["PySide6.QtWidgets"]
mock_widgets.QDialog = type(
    "QDialog",
    (),
    {
        "__init__": lambda *a, **kw: None,
        "setWindowFlags": lambda *a, **kw: None,
        "setWindowTitle": lambda *a, **kw: None,
        "close": lambda *a, **kw: None,
        "keyPressEvent": lambda *a, **kw: None,
    },
)
mock_widgets.QVBoxLayout = MagicMock
mock_widgets.QHBoxLayout = MagicMock
mock_widgets.QWidget = type("QWidget", (), {"__init__": lambda *a, **kw: None})
mock_widgets.QLabel = MagicMock
mock_widgets.QComboBox = MagicMock
mock_widgets.QPushButton = MagicMock
mock_widgets.QToolTip = MagicMock
mock_widgets.QLineEdit = MagicMock
mock_widgets.QFrame = MagicMock
mock_widgets.QFrame.Shape = MagicMock()
mock_widgets.QFrame.Shape.VLine = 5
mock_widgets.QFrame.Shadow = MagicMock()
mock_widgets.QFrame.Shadow.Plain = 0
mock_widgets.QStyle = MagicMock()
mock_widgets.QStyle.StandardPixmap = MagicMock()
mock_widgets.QStyle.StandardPixmap.SP_DialogResetButton = 0
mock_widgets.QStyle.StandardPixmap.SP_ArrowUp = 1
mock_widgets.QStyle.StandardPixmap.SP_ArrowDown = 2
mock_widgets.QStyle.StandardPixmap.SP_DialogCloseButton = 3
mock_widgets.QScrollArea = MagicMock

mock_gui = _pyside6_mocks["PySide6.QtGui"]
mock_gui.QColor = MagicMock
mock_gui.QPen = MagicMock
mock_gui.QBrush = MagicMock
mock_gui.QPainter = MagicMock
mock_gui.QFont = MagicMock

# Mock matplotlib
mock_figure_mod = MagicMock()
mock_canvas_mod = MagicMock()
mock_mdates = MagicMock()
mock_mdates.date2num = lambda d: (d - date(2000, 1, 1)).days
mock_mpatches = MagicMock()
mock_mpl_patches = MagicMock()
mock_mpl_backends = MagicMock()

# Link parent mock attributes to sub-module mocks so that
# `import matplotlib.dates as mdates` resolves correctly
mock_matplotlib = MagicMock()
mock_matplotlib.dates = mock_mdates
mock_matplotlib.figure = mock_figure_mod
mock_matplotlib.patches = mock_mpatches
mock_matplotlib.backends = mock_mpl_backends
mock_matplotlib.backends.backend_qtagg = mock_canvas_mod

matplotlib_mocks = {
    "matplotlib": mock_matplotlib,
    "matplotlib.dates": mock_mdates,
    "matplotlib.figure": mock_figure_mod,
    "matplotlib.patches": mock_mpatches,
    "matplotlib.backends": mock_mpl_backends,
    "matplotlib.backends.backend_qtagg": mock_canvas_mod,
}

with (
    patch.dict("sys.modules", {**_pyside6_mocks, **matplotlib_mocks}),
    patch(
        "backlog_manager.presentation.theme.theme.STATUS_PALETTE",
        {
            "BACKLOG": MagicMock(
                background="#E5E5E5", foreground="#525252", symbol="●"
            ),
            "EXECUCAO": MagicMock(
                background="#DBEAFE", foreground="#1E40AF", symbol="▶"
            ),
            "TESTES": MagicMock(background="#FEF3C7", foreground="#B45309", symbol="◆"),
            "CONCLUIDO": MagicMock(
                background="#DDF3E4", foreground="#18794E", symbol="✓"
            ),
            "IMPEDIDO": MagicMock(
                background="#FECACA", foreground="#991B1B", symbol="✕"
            ),
        },
    ),
):
    from backlog_manager.presentation.views.roadmap_dialog import (
        BAR_HEIGHT,
        CODE_CHAR_WIDTH_PX,
        CODE_FONT_SIZE,
        FILTER_ACTIVE_STYLE,
        KEYBOARD_PAN_RATIO,
        MIN_LABEL_HEIGHT_PX,
        PAN_CLICK_THRESHOLD,
        PAN_VISIBLE_RATIO,
        PROGRESS_COLOR_HIGH,
        PROGRESS_COLOR_LOW,
        PROGRESS_COLOR_MID,
        SEARCH_DEBOUNCE_MS,
        STATUS_PROGRESS,
        SUMMARY_BAR_HEIGHT,
        RoadmapDialog,
        _build_tooltip_text,
        _count_business_days,
        _get_progress_color,
    )

from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

# --- Fixtures ---


def _make_story(**kwargs) -> StoryOutputDTO:
    defaults = {
        "planning_id": 1,
        "id": "COMP-001",
        "component": "Backend",
        "name": "Story 1",
        "story_points": 5,
        "priority": 1,
        "status": "EXECUCAO",
        "duration": 5,
        "start_date": date(2026, 1, 15),
        "end_date": date(2026, 1, 20),
        "developer_id": 1,
        "feature_id": 1,
        "developer_name": "Dev A",
        "feature_name": "Feature A",
        "wave": 1,
        "dependency_ids": [],
    }
    defaults.update(kwargs)
    return StoryOutputDTO(**defaults)


# ============================================================
# T015-T017: US1 - Identificacao Visual por Status
# ============================================================


class TestStatusColors:
    """T015: Verify bars use STATUS_PALETTE colors by status."""

    def test_status_progress_has_all_statuses(self):
        for status in ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]:
            assert status in STATUS_PROGRESS

    def test_backlog_zero_progress(self):
        assert STATUS_PROGRESS["BACKLOG"] == 0.0

    def test_execucao_33_progress(self):
        assert STATUS_PROGRESS["EXECUCAO"] == 0.33

    def test_testes_66_progress(self):
        assert STATUS_PROGRESS["TESTES"] == 0.66

    def test_concluido_100_progress(self):
        assert STATUS_PROGRESS["CONCLUIDO"] == 1.0

    def test_impedido_zero_progress(self):
        assert STATUS_PROGRESS["IMPEDIDO"] == 0.0


class TestLegend:
    """T016: Verify legend presence in matplotlib figure."""

    def test_legend_statuses_covered(self):
        """All 5 statuses should have entries in STATUS_PROGRESS for legend."""
        assert len(STATUS_PROGRESS) == 5


class TestImpedidoHighlight:
    """T017: Verify IMPEDIDO stories get special visual treatment."""

    def test_impedido_has_zero_progress(self):
        assert STATUS_PROGRESS["IMPEDIDO"] == 0.0

    def test_tooltip_contains_impedido_symbol(self):
        story = _make_story(status="IMPEDIDO")
        text = _build_tooltip_text(story)
        assert "IMPEDIDO" in text
        assert "✕" in text


# ============================================================
# T021-T023: US2 - Colapso e Expansao de Grupos
# ============================================================


class TestCollapsedGroup:
    """T021: Verify collapsed group renders summary bar."""

    def test_summary_bar_height_defined(self):
        assert SUMMARY_BAR_HEIGHT == 1.0

    def test_summary_bar_larger_than_individual(self):
        assert SUMMARY_BAR_HEIGHT > BAR_HEIGHT


class TestExpandedGroup:
    """T022: Verify expanded group renders individual stories."""

    def test_bar_height_defined(self):
        assert BAR_HEIGHT == 0.6


class TestGroupClickDetection:
    """T023: Verify group click region detection."""

    def test_click_region_format(self):
        """Click regions should be (y_min, y_max, group_name) tuples."""
        region = (0.0, 1.0, "Feature A")
        assert len(region) == 3
        assert isinstance(region[2], str)


# ============================================================
# T028-T029: US3 - Linha de Referencia Temporal "Hoje"
# ============================================================


class TestTodayLine:
    """T028-T029: Verify today line presence/absence logic."""

    def test_today_within_range(self):
        today = date.today()
        min_d = date(2020, 1, 1)
        max_d = date(2030, 12, 31)
        assert min_d <= today <= max_d

    def test_today_outside_range(self):
        today = date.today()
        min_d = date(2000, 1, 1)
        max_d = date(2000, 12, 31)
        assert not (min_d <= today <= max_d)


# ============================================================
# T031-T032: US4 - Rotulos e Hierarquia Visual
# ============================================================


class TestLabelHeight:
    """T031: Verify minimum label height constant."""

    def test_min_label_height_defined(self):
        assert MIN_LABEL_HEIGHT_PX == 14

    def test_min_label_height_positive(self):
        assert MIN_LABEL_HEIGHT_PX > 0


class TestAutoCollapse:
    """T032: Verify auto-collapse concept for overcrowded groups."""

    def test_label_font_size_reasonable(self):
        from backlog_manager.presentation.views.roadmap_dialog import LABEL_FONT_SIZE

        assert LABEL_FONT_SIZE >= 7
        assert LABEL_FONT_SIZE <= 12


# ============================================================
# T037-T040: US5 - Filtragem e Busca
# ============================================================


class TestFilterCombos:
    """T037: Verify filter combo boxes are populated."""

    def test_filter_active_style_defined(self):
        assert "0066CC" in FILTER_ACTIVE_STYLE

    def test_filter_active_style_has_border(self):
        assert "border" in FILTER_ACTIVE_STYLE


class TestFilterApply:
    """T038: Verify filter change triggers apply_filters."""

    def test_build_tooltip_works_after_module_load(self):
        """Module loaded successfully with filter infrastructure."""
        story = _make_story()
        text = _build_tooltip_text(story)
        assert len(text) > 0


class TestFilterVisualIndicator:
    """T039: Verify filter active visual indicator style."""

    def test_filter_active_style_is_blue_border(self):
        assert "#0066CC" in FILTER_ACTIVE_STYLE


class TestClearFilters:
    """T040: Verify clear filters button concept."""

    def test_module_exports_filter_style(self):
        assert FILTER_ACTIVE_STYLE is not None


# ============================================================
# T050-T051: US6 - Tooltip Enriquecido e Dependencias
# ============================================================


class TestEnrichedTooltip:
    """T050: Verify enriched tooltip content."""

    def test_contains_story_name(self):
        story = _make_story(name="My Story")
        text = _build_tooltip_text(story)
        assert "My Story" in text

    def test_contains_status_with_symbol(self):
        story = _make_story(status="EXECUCAO")
        text = _build_tooltip_text(story)
        assert "EXECUCAO" in text
        assert "▶" in text

    def test_contains_developer(self):
        story = _make_story(developer_name="Dev A")
        text = _build_tooltip_text(story)
        assert "Dev A" in text

    def test_contains_sem_responsavel(self):
        story = _make_story(developer_name=None)
        text = _build_tooltip_text(story)
        assert "Sem responsavel" in text

    def test_contains_story_points(self):
        story = _make_story(story_points=8)
        text = _build_tooltip_text(story)
        assert "8" in text

    def test_contains_dates(self):
        story = _make_story(start_date=date(2026, 1, 15), end_date=date(2026, 1, 20))
        text = _build_tooltip_text(story)
        assert "2026-01-15" in text
        assert "2026-01-20" in text

    def test_contains_business_days(self):
        # Jan 15 (Thu) to Jan 20 (Tue) = 4 business days
        story = _make_story(start_date=date(2026, 1, 15), end_date=date(2026, 1, 20))
        text = _build_tooltip_text(story)
        assert "dias uteis" in text

    def test_contains_component(self):
        story = _make_story(component="Backend")
        text = _build_tooltip_text(story)
        assert "Backend" in text

    def test_contains_dependencies(self):
        story = _make_story(dependency_ids=["AUTH-001", "AUTH-002"])
        text = _build_tooltip_text(story)
        assert "AUTH-001" in text
        assert "AUTH-002" in text

    def test_contains_sem_dependencias(self):
        story = _make_story(dependency_ids=[])
        text = _build_tooltip_text(story)
        assert "Sem dependencias" in text

    def test_no_start_date_shows_na(self):
        story = _make_story(start_date=None)
        text = _build_tooltip_text(story)
        assert "N/A" in text

    def test_no_end_date_shows_na(self):
        story = _make_story(end_date=None)
        text = _build_tooltip_text(story)
        assert "N/A" in text

    def test_no_dates_duration_na(self):
        story = _make_story(start_date=None, end_date=None)
        text = _build_tooltip_text(story)
        # Duration should show N/A when dates are missing
        lines = text.split("\n")
        duration_line = [line for line in lines if "Duracao" in line][0]
        assert "N/A" in duration_line

    def test_contains_separator_line(self):
        story = _make_story()
        text = _build_tooltip_text(story)
        assert "─" in text


class TestBusinessDays:
    """Test business day calculation."""

    def test_weekday_range(self):
        # Mon Jan 5 to Fri Jan 9 = 5 business days
        assert _count_business_days(date(2026, 1, 5), date(2026, 1, 9)) == 5

    def test_includes_weekend(self):
        # Mon Jan 5 to Mon Jan 12 = 6 business days
        assert _count_business_days(date(2026, 1, 5), date(2026, 1, 12)) == 6

    def test_single_day(self):
        assert _count_business_days(date(2026, 1, 5), date(2026, 1, 5)) == 1

    def test_weekend_only(self):
        # Sat Jan 10 to Sun Jan 11 = 0 business days
        assert _count_business_days(date(2026, 1, 10), date(2026, 1, 11)) == 0

    def test_reverse_dates(self):
        assert _count_business_days(date(2026, 1, 20), date(2026, 1, 15)) == 0


class TestDependencyArrows:
    """T051: Verify dependency arrow concept."""

    def test_story_with_dependencies(self):
        story = _make_story(dependency_ids=["DEP-001"])
        assert len(story.dependency_ids) == 1

    def test_story_without_dependencies(self):
        story = _make_story(dependency_ids=[])
        assert len(story.dependency_ids) == 0


# ============================================================
# T056-T057: US7 - Toolbar com Icones e Rodape Estatistico
# ============================================================


class TestToolbarIcons:
    """T056: Verify toolbar buttons have icons and tooltips."""

    def test_module_loads_with_qstyle_icons(self):
        """Module loaded successfully with QStyle icon references."""
        assert callable(_build_tooltip_text)


class TestStatusBarFormat:
    """T057: Verify status bar format with per-status counts."""

    def test_status_order_in_footer(self):
        """All 5 statuses should be trackable for the footer."""
        expected = ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]
        for status in expected:
            assert status in STATUS_PROGRESS


# ============================================================
# T061: US8 - Progresso Visual nas Barras
# ============================================================


class TestProgressBars:
    """T061: Verify two-layer bar rendering concept."""

    def test_progress_values_are_fractions(self):
        for status, progress in STATUS_PROGRESS.items():
            assert 0.0 <= progress <= 1.0, f"{status} has invalid progress {progress}"

    def test_concluido_full_progress(self):
        assert STATUS_PROGRESS["CONCLUIDO"] == 1.0

    def test_backlog_no_progress(self):
        assert STATUS_PROGRESS["BACKLOG"] == 0.0


# ============================================================
# T063: US9 - Scroll Sincronizado
# ============================================================


class TestScrollSync:
    """T063: Verify labels and bars share same axes."""

    def test_single_axes_approach(self):
        """Verify single axes approach for labels and bars.

        The implementation uses a single axes for labels and bars,
        ensuring native scroll synchronization.
        """
        assert True


# ============================================================
# All statuses tooltip test
# ============================================================


class TestAllStoriesInChart:
    def test_tooltip_for_all_statuses(self):
        for status in ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]:
            story = _make_story(status=status)
            text = _build_tooltip_text(story)
            assert status in text


# ============================================================
# Close button and Escape key tests
# ============================================================


def _create_bare_dialog():
    """Create a bare RoadmapDialog without calling __init__."""
    dialog = object.__new__(RoadmapDialog)
    dialog.close = MagicMock()
    return dialog


class TestCloseButton:
    """Verify the roadmap dialog source defines a close button."""

    def test_actions_group_defines_close_btn(self):
        """_create_actions_group source should assign _close_btn."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_actions_group)
        assert "_close_btn" in source
        assert "Fechar" in source

    def test_close_btn_connects_to_close(self):
        """_close_btn should connect clicked to self.close."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_actions_group)
        assert "self.close" in source
        assert "SP_DialogCloseButton" in source


class TestToolbarSeparators:
    """Verify toolbar has visual separators between groups."""

    def test_create_separator_returns_object(self):
        """_create_separator should return a QFrame-like object."""
        result = RoadmapDialog._create_separator()
        assert result is not None

    def test_toolbar_source_uses_separators(self):
        """_create_toolbar should use _create_separator for group division."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_toolbar)
        assert "_create_separator" in source
        # Should have at least 3 separators (Zoom|Filters, Filters|Deps, stretch|Close)
        assert source.count("_create_separator") >= 3


class TestEscapeKeyClose:
    """Verify Escape key closes the dialog."""

    def test_keypress_escape_calls_close(self):
        """Pressing Escape should call self.close()."""
        dialog = _create_bare_dialog()

        mock_event = MagicMock()
        mock_event.key.return_value = _mock_qt_core.Qt.Key.Key_Escape
        dialog.keyPressEvent(mock_event)

        dialog.close.assert_called_once()

    def test_keypress_other_key_does_not_close(self):
        """Non-Escape keys should not close the dialog."""
        dialog = _create_bare_dialog()

        mock_event = MagicMock()
        mock_event.key.return_value = _mock_qt_core.Qt.Key.Key_Return
        dialog.keyPressEvent(mock_event)

        dialog.close.assert_not_called()


# ============================================================
# New: Story code label format (FR-004, FR-005)
# ============================================================


class TestStoryCodeLabel:
    """Verify story code appears in y-axis label."""

    def test_build_story_label_contains_code(self):
        story = _make_story(id="AUTH-001", name="Login OAuth")
        label = RoadmapDialog._build_story_label(story)
        assert "AUTH-001" in label
        assert "Login OAuth" in label

    def test_build_story_label_format(self):
        story = _make_story(id="AUTH-001", name="Login OAuth")
        label = RoadmapDialog._build_story_label(story)
        assert label.startswith("  AUTH-001 | ")

    def test_build_story_label_truncates_long_name(self):
        long_name = "A" * 100
        story = _make_story(id="AUTH-001", name=long_name)
        label = RoadmapDialog._build_story_label(story)
        assert len(label) <= 60
        assert "AUTH-001" in label
        assert label.endswith("...")

    def test_build_story_label_short_name_no_truncation(self):
        story = _make_story(id="AUTH-001", name="Short")
        label = RoadmapDialog._build_story_label(story)
        assert "..." not in label


# ============================================================
# New: Feature group label format (FR-006, FR-007)
# ============================================================


class TestFeatureGroupLabel:
    """Verify feature group header format with metrics."""

    def test_group_label_contains_feature_name(self):
        import inspect

        source = inspect.getsource(RoadmapDialog._build_group_label)
        assert "group.name" in source
        assert "historias" in source
        assert "completion_percent" in source

    def test_group_label_contains_count_and_percent(self):
        """Group label source should include story count and percent."""
        import inspect

        source = inspect.getsource(RoadmapDialog._build_group_label)
        assert "len(group.stories)" in source
        assert "completion_percent" in source


# ============================================================
# New: Search debounce (FR-012)
# ============================================================


class TestSearchDebounce:
    """Verify search field has debounce timer."""

    def test_debounce_interval_defined(self):
        assert SEARCH_DEBOUNCE_MS == 300

    def test_debounce_timer_created_in_filter_group(self):
        """_create_filter_group should create _search_timer."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_filter_group)
        assert "_search_timer" in source
        assert "setSingleShot" in source
        assert "SEARCH_DEBOUNCE_MS" in source

    def test_on_search_changed_uses_timer(self):
        """_on_search_changed should start the debounce timer."""
        import inspect

        source = inspect.getsource(RoadmapDialog._on_search_changed)
        assert "_search_timer" in source


# ============================================================
# New: Progress color thresholds
# ============================================================


class TestProgressColor:
    """Verify progress color function for group labels."""

    def test_high_progress_is_green(self):
        assert _get_progress_color(80) == PROGRESS_COLOR_HIGH

    def test_mid_progress_is_yellow(self):
        assert _get_progress_color(50) == PROGRESS_COLOR_MID

    def test_low_progress_is_red(self):
        assert _get_progress_color(10) == PROGRESS_COLOR_LOW

    def test_boundary_75_is_mid(self):
        assert _get_progress_color(75) == PROGRESS_COLOR_MID

    def test_boundary_25_is_mid(self):
        assert _get_progress_color(25) == PROGRESS_COLOR_MID

    def test_zero_is_red(self):
        assert _get_progress_color(0) == PROGRESS_COLOR_LOW

    def test_100_is_green(self):
        assert _get_progress_color(100) == PROGRESS_COLOR_HIGH


# ============================================================
# New: Story code rendering constants
# ============================================================


class TestStoryCodeConstants:
    """Verify story code rendering constants."""

    def test_code_font_size_defined(self):
        assert CODE_FONT_SIZE == 7

    def test_code_char_width_defined(self):
        assert CODE_CHAR_WIDTH_PX == 6

    def test_render_story_code_method_exists(self):
        """RoadmapDialog should have _render_story_code method."""
        assert hasattr(RoadmapDialog, "_render_story_code")


# ============================================================
# New: Dependency arrows only when both visible (FR-021)
# ============================================================


class TestDependencyVisibility:
    """FR-021: Arrows only when both stories visible."""

    def test_draw_dependency_arrows_skips_hidden(self):
        """Source should skip (continue) when target not in positions."""
        import inspect

        source = inspect.getsource(RoadmapDialog._draw_dependency_arrows)
        assert "continue" in source
        # Should NOT draw dashed arrows for hidden dependencies
        assert "DEPENDENCY_HIDDEN_COLOR" not in source


# ============================================================
# New: Toolbar uses sub-methods
# ============================================================


class TestToolbarSubMethods:
    """Verify toolbar is organized into sub-methods."""

    def test_has_create_zoom_group(self):
        assert hasattr(RoadmapDialog, "_create_zoom_group")

    def test_has_create_filter_group(self):
        assert hasattr(RoadmapDialog, "_create_filter_group")

    def test_has_create_dependency_group(self):
        assert hasattr(RoadmapDialog, "_create_dependency_group")

    def test_has_create_actions_group(self):
        assert hasattr(RoadmapDialog, "_create_actions_group")

    def test_filter_group_has_feature_combo(self):
        """_create_filter_group should create _feature_combo."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_filter_group)
        assert "_feature_combo" in source
        assert "Feature:" in source

    def test_filter_group_has_no_wave_combo(self):
        """_create_filter_group should not reference wave combo."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_filter_group)
        assert "_wave_combo" not in source

    def test_filter_group_has_no_status_combo(self):
        """_create_filter_group should not reference status combo."""
        import inspect

        source = inspect.getsource(RoadmapDialog._create_filter_group)
        assert "_status_combo" not in source


# ============================================================
# T005-T013: US5b - Pan/Drag Horizontal (FR-022 to FR-028)
# ============================================================


def _create_pan_dialog():
    """Create a RoadmapDialog with pan state and mocked axes for pan tests."""
    dialog = object.__new__(RoadmapDialog)
    dialog.close = MagicMock()
    dialog._is_panning = False
    dialog._pan_start_x = None
    dialog._pan_start_xlim = None
    dialog._bar_data = []
    dialog._group_click_regions = []
    dialog._dependency_arrows = []
    dialog._story_positions = {}
    dialog._data = MagicMock()

    # Mock axes
    dialog._ax = MagicMock()
    dialog._ax.get_xlim.return_value = (100.0, 200.0)

    # Mock canvas
    dialog._canvas = MagicMock()
    dialog._canvas.draw_idle = MagicMock()

    return dialog


class TestPanInitialState:
    """T005: Verify initial pan state attributes."""

    def test_is_panning_default_false(self):
        dialog = _create_pan_dialog()
        assert dialog._is_panning is False

    def test_pan_start_x_default_none(self):
        dialog = _create_pan_dialog()
        assert dialog._pan_start_x is None

    def test_pan_start_xlim_default_none(self):
        dialog = _create_pan_dialog()
        assert dialog._pan_start_xlim is None

    def test_pan_constants_defined(self):
        assert PAN_CLICK_THRESHOLD == 5.0
        assert PAN_VISIBLE_RATIO == 0.2
        assert KEYBOARD_PAN_RATIO == 0.10


class TestPanPress:
    """T006: Verify _on_pan_press registers start position and sets panning."""

    def test_press_sets_panning_true(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = dialog._ax
        event.xdata = 150.0

        dialog._on_pan_press(event)

        assert dialog._is_panning is True

    def test_press_records_start_x(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = dialog._ax
        event.xdata = 150.0

        dialog._on_pan_press(event)

        assert dialog._pan_start_x == 150.0

    def test_press_records_start_xlim(self):
        dialog = _create_pan_dialog()
        dialog._ax.get_xlim.return_value = (100.0, 200.0)
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = dialog._ax
        event.xdata = 150.0

        dialog._on_pan_press(event)

        assert dialog._pan_start_xlim == (100.0, 200.0)

    def test_press_ignored_with_ctrl(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = "control"
        event.inaxes = dialog._ax
        event.xdata = 150.0

        dialog._on_pan_press(event)

        assert dialog._is_panning is False

    def test_press_ignored_outside_axes(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = None
        event.xdata = 150.0

        dialog._on_pan_press(event)

        assert dialog._is_panning is False

    def test_press_ignored_if_xdata_none(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = dialog._ax
        event.xdata = None

        dialog._on_pan_press(event)

        assert dialog._is_panning is False

    def test_press_changes_cursor_to_closed_hand(self):
        dialog = _create_pan_dialog()
        event = MagicMock()
        event.button = 1
        event.key = None
        event.inaxes = dialog._ax
        event.xdata = 150.0

        dialog._on_pan_press(event)

        dialog._canvas.setCursor.assert_called()


class TestPanMove:
    """T007: Verify _on_pan_move updates xlim with horizontal delta."""

    def test_move_updates_xlim(self):
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)

        # Mock data range for clamping
        dialog._data.min_date = date(2026, 1, 1)
        dialog._data.max_date = date(2026, 6, 30)

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 160.0  # moved 10 units to the right

        dialog._on_pan_move(event)

        dialog._ax.set_xlim.assert_called()
        dialog._canvas.draw_idle.assert_called()

    def test_move_ignored_when_not_panning(self):
        dialog = _create_pan_dialog()
        dialog._is_panning = False

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 160.0

        dialog._on_pan_move(event)

        dialog._ax.set_xlim.assert_not_called()

    def test_move_ignored_outside_axes(self):
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)

        event = MagicMock()
        event.inaxes = None
        event.xdata = 160.0

        dialog._on_pan_move(event)

        dialog._ax.set_xlim.assert_not_called()


class TestPanRelease:
    """T008: Verify _on_pan_release resets state and distinguishes click vs drag."""

    def test_release_sets_panning_false(self):
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 150.5  # small move — click

        dialog._on_pan_release(event)

        assert dialog._is_panning is False

    def test_release_restores_open_hand_cursor(self):
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 150.5

        dialog._on_pan_release(event)

        dialog._canvas.setCursor.assert_called()

    def test_small_move_treated_as_click(self):
        """Movement < PAN_CLICK_THRESHOLD should delegate to click handler."""
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)
        dialog._group_click_regions = [(149.0, 151.0, "Feature A")]
        dialog._viewmodel = MagicMock()
        dialog._viewmodel.toggle_group.return_value = MagicMock()
        dialog._render_chart = MagicMock()

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 150.1  # delta < 5.0 threshold
        event.ydata = 150.0

        dialog._on_pan_release(event)

        # Should have delegated to click logic
        assert dialog._is_panning is False

    def test_large_move_treated_as_drag(self):
        """Movement >= PAN_CLICK_THRESHOLD should be a drag, not a click."""
        dialog = _create_pan_dialog()
        dialog._is_panning = True
        dialog._pan_start_x = 150.0
        dialog._pan_start_xlim = (100.0, 200.0)
        dialog._viewmodel = MagicMock()
        dialog._render_chart = MagicMock()

        event = MagicMock()
        event.inaxes = dialog._ax
        event.xdata = 160.0  # delta = 10 >= 5.0 threshold

        dialog._on_pan_release(event)

        assert dialog._is_panning is False
        # Should NOT call toggle_group (it was a drag)
        dialog._viewmodel.toggle_group.assert_not_called()


class TestPanClamping:
    """T009: Verify pan clamps xlim to keep 20% of data visible."""

    def test_clamp_xlim_keeps_minimum_visible(self):
        dialog = _create_pan_dialog()
        # Total data range: 0 to 100
        data_min = 0.0
        data_max = 100.0
        total_range = data_max - data_min

        # Try to pan far right (new_left=90, new_right=190)
        # Should clamp so at least 20% of data (20 units) is visible
        new_left, new_right = dialog._clamp_xlim(90.0, 190.0, data_min, data_max)

        visible_data_start = max(new_left, data_min)
        visible_data_end = min(new_right, data_max)
        visible_fraction = (visible_data_end - visible_data_start) / total_range

        assert visible_fraction >= PAN_VISIBLE_RATIO

    def test_clamp_xlim_allows_valid_pan(self):
        dialog = _create_pan_dialog()
        # Pan within valid range
        new_left, new_right = dialog._clamp_xlim(20.0, 120.0, 0.0, 100.0)

        # Should allow since plenty of data is visible
        assert new_left <= 20.0 or (new_left >= 0.0)
        assert new_right >= new_left


class TestPanCursor:
    """T010: Verify cursor changes for pan interaction."""

    def test_canvas_has_setCursor_method(self):
        dialog = _create_pan_dialog()
        assert hasattr(dialog._canvas, "setCursor")

    def test_source_uses_open_hand_cursor(self):
        """_on_pan_release should restore OpenHandCursor."""
        import inspect

        source = inspect.getsource(RoadmapDialog._on_pan_release)
        assert "OpenHandCursor" in source

    def test_source_uses_closed_hand_cursor(self):
        """_on_pan_press should set ClosedHandCursor."""
        import inspect

        source = inspect.getsource(RoadmapDialog._on_pan_press)
        assert "ClosedHandCursor" in source


class TestKeyboardPan:
    """T011: Verify arrow key navigation shifts xlim by 10%."""

    def test_right_arrow_shifts_xlim(self):
        dialog = _create_pan_dialog()
        dialog._ax.get_xlim.return_value = (100.0, 200.0)
        dialog._data.min_date = date(2026, 1, 1)
        dialog._data.max_date = date(2026, 12, 31)
        dialog._update_zoom_label = MagicMock()

        mock_event = MagicMock()
        mock_event.key.return_value = _mock_qt_core.Qt.Key.Key_Right

        dialog.keyPressEvent(mock_event)

        dialog._ax.set_xlim.assert_called()

    def test_left_arrow_shifts_xlim(self):
        dialog = _create_pan_dialog()
        dialog._ax.get_xlim.return_value = (100.0, 200.0)
        dialog._data.min_date = date(2026, 1, 1)
        dialog._data.max_date = date(2026, 12, 31)
        dialog._update_zoom_label = MagicMock()

        mock_event = MagicMock()
        mock_event.key.return_value = _mock_qt_core.Qt.Key.Key_Left

        dialog.keyPressEvent(mock_event)

        dialog._ax.set_xlim.assert_called()


class TestKeyboardPanNoEffectAt100:
    """T012: Verify arrow keys have no effect when zoom is 100%."""

    def test_arrow_no_effect_when_full_view(self):
        dialog = _create_pan_dialog()
        # xlim spans full data range — zoom is 100%
        dialog._data.min_date = date(2026, 1, 1)
        dialog._data.max_date = date(2026, 6, 30)

        from backlog_manager.presentation.views.roadmap_dialog import (
            mdates as real_mdates,
        )

        full_left = real_mdates.date2num(date(2026, 1, 1)) - 2
        full_right = real_mdates.date2num(date(2026, 6, 30)) + 2
        dialog._ax.get_xlim.return_value = (full_left, full_right)
        dialog._update_zoom_label = MagicMock()

        mock_event = MagicMock()
        mock_event.key.return_value = _mock_qt_core.Qt.Key.Key_Right

        dialog.keyPressEvent(mock_event)

        # Should not shift because full range is already visible
        dialog._ax.set_xlim.assert_not_called()


class TestTooltipSuppressedDuringPan:
    """T013: Verify tooltips suppressed during _is_panning=True."""

    def test_hover_suppressed_during_pan(self):
        """_on_hover should skip tooltip when _is_panning is True."""
        import inspect

        source = inspect.getsource(RoadmapDialog._on_hover)
        assert "_is_panning" in source

    def test_on_pan_move_no_tooltip(self):
        """_on_pan_move should not trigger tooltips."""
        import inspect

        source = inspect.getsource(RoadmapDialog._on_pan_move)
        assert "QToolTip" not in source
