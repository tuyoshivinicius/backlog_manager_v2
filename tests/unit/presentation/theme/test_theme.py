"""Headless tests for presentation/theme/theme.py.

Tests design tokens, status palette, wave palette, apply_theme,
contrast calculation, and IconManager without requiring PySide6.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict(sys.modules, _pyside6_mocks):
    from backlog_manager.presentation.theme.theme import (
        DESIGN_TOKENS,
        ICON_NAMES,
        STATUS_PALETTE,
        TABLE_SELECTION_QSS,
        WAVE_PALETTE,
        IconManager,
        StatusConfig,
        _hex_to_rgb,
        _relative_luminance,
        apply_theme,
        calculate_contrast_ratio,
    )


# ---------------------------------------------------------------------------
# DESIGN_TOKENS structure
# ---------------------------------------------------------------------------


class TestDesignTokens:
    """Validate DESIGN_TOKENS dict integrity."""

    def test_is_dict_of_strings(self):
        assert isinstance(DESIGN_TOKENS, dict)
        for key, value in DESIGN_TOKENS.items():
            assert isinstance(key, str), f"Key {key!r} is not str"
            assert isinstance(value, str), f"Value for {key!r} is not str"

    def test_contains_primary_colors(self):
        for key in ("primary", "primary-light", "primary-dark", "primary-pressed"):
            assert key in DESIGN_TOKENS

    def test_contains_semantic_colors(self):
        for key in ("background", "surface", "border", "text", "text-secondary"):
            assert key in DESIGN_TOKENS

    def test_contains_status_colors(self):
        for prefix in ("success", "warning", "error", "info"):
            assert f"{prefix}-bg" in DESIGN_TOKENS
            assert f"{prefix}-fg" in DESIGN_TOKENS

    def test_contains_typography_tokens(self):
        assert "font-family" in DESIGN_TOKENS
        assert "font-size-base" in DESIGN_TOKENS
        assert "font-weight-normal" in DESIGN_TOKENS

    def test_contains_spacing_tokens(self):
        for n in (0, 1, 2, 3, 4, 5, 6, 8):
            assert f"spacing-{n}" in DESIGN_TOKENS

    def test_contains_selection_tokens(self):
        for key in ("selection-bg", "selection-fg", "selection-border", "hover-bg"):
            assert key in DESIGN_TOKENS

    def test_hex_colors_are_valid_format(self):
        """All values that look like hex colors should be 7 chars (#RRGGBB)."""
        for key, value in DESIGN_TOKENS.items():
            if value.startswith("#"):
                assert len(value) == 7, f"Token {key!r} has bad hex: {value!r}"


# ---------------------------------------------------------------------------
# STATUS_PALETTE structure
# ---------------------------------------------------------------------------


class TestStatusPalette:
    """Validate STATUS_PALETTE dict integrity."""

    EXPECTED_STATUSES = {"BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"}

    def test_contains_all_expected_statuses(self):
        assert set(STATUS_PALETTE.keys()) == self.EXPECTED_STATUSES

    def test_values_are_status_config(self):
        for status, config in STATUS_PALETTE.items():
            assert isinstance(config, StatusConfig), f"{status} is not StatusConfig"

    def test_each_config_has_non_empty_symbol(self):
        for status, config in STATUS_PALETTE.items():
            assert config.symbol, f"{status} has empty symbol"

    def test_each_config_has_hex_colors(self):
        for status, config in STATUS_PALETTE.items():
            assert config.background.startswith("#"), f"{status} bg not hex"
            assert config.foreground.startswith("#"), f"{status} fg not hex"

    def test_status_config_is_frozen(self):
        cfg = STATUS_PALETTE["BACKLOG"]
        with pytest.raises(AttributeError):
            cfg.symbol = "X"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WAVE_PALETTE
# ---------------------------------------------------------------------------


class TestWavePalette:
    """Validate WAVE_PALETTE list."""

    def test_is_list(self):
        assert isinstance(WAVE_PALETTE, list)

    def test_index_zero_is_empty(self):
        assert WAVE_PALETTE[0] == ""

    def test_has_at_least_8_entries(self):
        assert len(WAVE_PALETTE) >= 8

    def test_non_zero_entries_are_hex(self):
        for i, color in enumerate(WAVE_PALETTE):
            if i == 0:
                continue
            assert color.startswith("#"), f"Wave {i} is not hex: {color!r}"


# ---------------------------------------------------------------------------
# TABLE_SELECTION_QSS
# ---------------------------------------------------------------------------


class TestTableSelectionQss:
    """Validate the QSS template constant."""

    def test_contains_placeholders(self):
        assert "@hover-bg" in TABLE_SELECTION_QSS
        assert "@selection-bg" in TABLE_SELECTION_QSS
        assert "@selection-fg" in TABLE_SELECTION_QSS
        assert "@selection-border" in TABLE_SELECTION_QSS

    def test_contains_qtableview_selectors(self):
        assert "QTableView::item:hover" in TABLE_SELECTION_QSS
        assert "QTableView::item:selected" in TABLE_SELECTION_QSS


# ---------------------------------------------------------------------------
# apply_theme
# ---------------------------------------------------------------------------


class TestApplyTheme:
    """Tests for apply_theme token substitution."""

    def test_basic_substitution(self):
        template = "background: @primary; color: @text;"
        tokens = {"primary": "#0066CC", "text": "#171717"}
        result = apply_theme(template, tokens)
        assert result == "background: #0066CC; color: #171717;"

    def test_longest_first_substitution(self):
        """@primary-dark must be replaced before @primary."""
        template = "color: @primary-dark; bg: @primary;"
        tokens = {"primary": "#0066CC", "primary-dark": "#004D99"}
        result = apply_theme(template, tokens)
        assert result == "color: #004D99; bg: #0066CC;"

    def test_no_placeholders_returns_original(self):
        template = "color: red;"
        result = apply_theme(template, {"primary": "#0066CC"})
        assert result == "color: red;"

    def test_empty_template(self):
        assert apply_theme("", {"x": "y"}) == ""

    def test_empty_tokens(self):
        assert apply_theme("@foo", {}) == "@foo"

    def test_multiple_occurrences(self):
        template = "@c and @c"
        result = apply_theme(template, {"c": "red"})
        assert result == "red and red"

    def test_with_real_design_tokens(self):
        """Substitute TABLE_SELECTION_QSS with the real DESIGN_TOKENS."""
        result = apply_theme(TABLE_SELECTION_QSS, DESIGN_TOKENS)
        # All @-placeholders should be resolved
        assert "@" not in result
        # Actual values should appear
        assert DESIGN_TOKENS["hover-bg"] in result
        assert DESIGN_TOKENS["selection-bg"] in result


# ---------------------------------------------------------------------------
# _hex_to_rgb
# ---------------------------------------------------------------------------


class TestHexToRgb:
    """Tests for the hex-to-RGB helper."""

    def test_black(self):
        assert _hex_to_rgb("#000000") == (0, 0, 0)

    def test_white(self):
        assert _hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_red(self):
        assert _hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_without_hash(self):
        assert _hex_to_rgb("0066CC") == (0, 102, 204)


# ---------------------------------------------------------------------------
# _relative_luminance
# ---------------------------------------------------------------------------


class TestRelativeLuminance:
    """Tests for WCAG relative luminance calculation."""

    def test_black_luminance(self):
        assert _relative_luminance(0, 0, 0) == pytest.approx(0.0)

    def test_white_luminance(self):
        assert _relative_luminance(255, 255, 255) == pytest.approx(1.0)

    def test_midgray_luminance(self):
        lum = _relative_luminance(128, 128, 128)
        assert 0.2 < lum < 0.3  # ~0.2158


# ---------------------------------------------------------------------------
# calculate_contrast_ratio
# ---------------------------------------------------------------------------


class TestCalculateContrastRatio:
    """Tests for WCAG contrast ratio calculation."""

    def test_black_on_white(self):
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert ratio == pytest.approx(21.0, abs=0.1)

    def test_white_on_black(self):
        ratio = calculate_contrast_ratio("#FFFFFF", "#000000")
        assert ratio == pytest.approx(21.0, abs=0.1)

    def test_same_color_returns_one(self):
        ratio = calculate_contrast_ratio("#0066CC", "#0066CC")
        assert ratio == pytest.approx(1.0)

    def test_status_palette_meets_wcag_aa(self):
        """All STATUS_PALETTE entries must have >= 4.5:1 contrast."""
        for status, config in STATUS_PALETTE.items():
            ratio = calculate_contrast_ratio(config.foreground, config.background)
            assert ratio >= 4.5, (
                f"{status} contrast {ratio:.2f} < 4.5 "
                f"(fg={config.foreground}, bg={config.background})"
            )


# ---------------------------------------------------------------------------
# ICON_NAMES
# ---------------------------------------------------------------------------


class TestIconNames:
    """Validate the ICON_NAMES list."""

    def test_is_list_of_strings(self):
        assert isinstance(ICON_NAMES, list)
        for name in ICON_NAMES:
            assert isinstance(name, str)

    def test_not_empty(self):
        assert len(ICON_NAMES) > 0

    def test_no_duplicates(self):
        assert len(ICON_NAMES) == len(set(ICON_NAMES))


# ---------------------------------------------------------------------------
# IconManager (with mocked QIcon)
# ---------------------------------------------------------------------------


class TestIconManager:
    """Tests for IconManager using mocked PySide6.QtGui.QIcon."""

    def test_init_loads_existing_icons(self, tmp_path: Path):
        """Icons for existing SVG files should be loaded."""
        # Create a couple of fake SVG files
        (tmp_path / "plus.svg").write_text("<svg/>")
        (tmp_path / "trash.svg").write_text("<svg/>")

        manager = IconManager(icons_dir=tmp_path)
        icon = manager.get("plus")
        # The mock QIcon was called; just verify we get something back
        assert icon is not None

    def test_get_missing_icon_returns_empty_qicon(self, tmp_path: Path):
        """Requesting an icon not in ICON_NAMES returns an empty QIcon mock."""
        manager = IconManager(icons_dir=tmp_path)
        icon = manager.get("nonexistent-icon")
        assert icon is not None  # MagicMock (empty QIcon)

    def test_get_known_name_but_no_svg_file(self, tmp_path: Path):
        """If an icon name is known but SVG is missing, still returns a QIcon."""
        manager = IconManager(icons_dir=tmp_path)
        icon = manager.get("plus")
        assert icon is not None


# ---------------------------------------------------------------------------
# get_icon_manager / _initialize_icon_manager
# ---------------------------------------------------------------------------


class TestIconManagerGlobals:
    """Tests for global icon manager lazy init and initialization."""

    def test_get_icon_manager_lazy_init(self, tmp_path: Path):
        """get_icon_manager should create an IconManager on first call."""
        import backlog_manager.presentation.theme.theme as theme_module

        # Reset the module-level singleton
        original = theme_module._icon_manager
        theme_module._icon_manager = None
        try:
            with patch.object(
                theme_module,
                "IconManager",
                return_value=IconManager(icons_dir=tmp_path),
            ) as mock_cls:
                result = theme_module.get_icon_manager()
                assert result is not None
                mock_cls.assert_called_once()
        finally:
            theme_module._icon_manager = original

    def test_get_icon_manager_returns_existing_instance(self, tmp_path: Path):
        """get_icon_manager should return existing instance if already created."""
        import backlog_manager.presentation.theme.theme as theme_module

        original = theme_module._icon_manager
        fake_manager = IconManager(icons_dir=tmp_path)
        theme_module._icon_manager = fake_manager
        try:
            result = theme_module.get_icon_manager()
            assert result is fake_manager
        finally:
            theme_module._icon_manager = original

    def test_initialize_icon_manager_sets_module_variable(self, tmp_path: Path):
        """_initialize_icon_manager should set the module-level icon_manager."""
        import backlog_manager.presentation.theme.theme as theme_module

        original_singleton = theme_module._icon_manager
        original_compat = theme_module.icon_manager
        # Set _icon_manager to a known fake so get_icon_manager returns it
        fake_manager = IconManager(icons_dir=tmp_path)
        theme_module._icon_manager = fake_manager
        try:
            theme_module._initialize_icon_manager()
            assert theme_module.icon_manager is fake_manager
        finally:
            theme_module._icon_manager = original_singleton
            theme_module.icon_manager = original_compat
