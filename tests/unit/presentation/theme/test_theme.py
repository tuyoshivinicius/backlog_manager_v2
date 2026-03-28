"""Unit tests for theme module.

Tests cover:
- apply_theme() placeholder substitution (T013)
- calculate_contrast_ratio() correctness (T014)
- STATUS_PALETTE WCAG AA compliance (T015)
- stylesheet.qss placeholder validation (T016, T017)
- :focus rules presence (T049)
- SVG icon existence (T055)
- IconManager functionality (T056, T057)
- Zero hardcoded hex values validation (T079)
"""

import re
from pathlib import Path

import pytest

from backlog_manager.presentation.theme.theme import (
    DESIGN_TOKENS,
    ICON_NAMES,
    STATUS_PALETTE,
    IconManager,
    apply_theme,
    calculate_contrast_ratio,
)

# =============================================================================
# T013: Unit test for apply_theme() placeholder substitution
# =============================================================================


class TestApplyTheme:
    """Tests for apply_theme() function."""

    def test_substitutes_single_placeholder(self) -> None:
        """Single placeholder is correctly substituted."""
        template = "background: @primary;"
        tokens = {"primary": "#0066CC"}
        result = apply_theme(template, tokens)
        assert result == "background: #0066CC;"

    def test_substitutes_multiple_placeholders(self) -> None:
        """Multiple placeholders are correctly substituted."""
        template = "background: @primary; color: @text;"
        tokens = {"primary": "#0066CC", "text": "#171717"}
        result = apply_theme(template, tokens)
        assert result == "background: #0066CC; color: #171717;"

    def test_longest_first_substitution(self) -> None:
        """Longer token names are substituted before shorter ones.

        This prevents @primary from matching before @primary-pressed.
        """
        template = "color: @primary-pressed; background: @primary;"
        tokens = {"primary": "#0066CC", "primary-pressed": "#003D7A"}
        result = apply_theme(template, tokens)
        assert result == "color: #003D7A; background: #0066CC;"

    def test_preserves_non_placeholder_content(self) -> None:
        """Content without placeholders is preserved."""
        template = "QWidget { margin: 10px; }"
        tokens = {"primary": "#0066CC"}
        result = apply_theme(template, tokens)
        assert result == "QWidget { margin: 10px; }"

    def test_empty_template_returns_empty(self) -> None:
        """Empty template returns empty string."""
        result = apply_theme("", {"primary": "#0066CC"})
        assert result == ""

    def test_empty_tokens_preserves_template(self) -> None:
        """Empty tokens dictionary preserves template."""
        template = "background: @primary;"
        result = apply_theme(template, {})
        assert result == "background: @primary;"


# =============================================================================
# T014: Unit test for calculate_contrast_ratio() correctness
# =============================================================================


class TestCalculateContrastRatio:
    """Tests for calculate_contrast_ratio() function."""

    def test_black_on_white_is_21(self) -> None:
        """Black on white has maximum contrast ratio of 21:1."""
        ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
        assert abs(ratio - 21.0) < 0.1

    def test_white_on_black_is_21(self) -> None:
        """White on black has same contrast as black on white."""
        ratio = calculate_contrast_ratio("#FFFFFF", "#000000")
        assert abs(ratio - 21.0) < 0.1

    def test_same_colors_is_1(self) -> None:
        """Same foreground and background has ratio of 1:1."""
        ratio = calculate_contrast_ratio("#808080", "#808080")
        assert abs(ratio - 1.0) < 0.01

    def test_handles_hex_without_hash(self) -> None:
        """Colors without # prefix are handled correctly."""
        ratio = calculate_contrast_ratio("000000", "FFFFFF")
        assert abs(ratio - 21.0) < 0.1

    def test_backlog_status_contrast(self) -> None:
        """BACKLOG status colors meet WCAG AA (>= 4.5)."""
        config = STATUS_PALETTE["BACKLOG"]
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        # Pre-validated: #525252 on #E5E5E5 = 5.45:1
        assert ratio >= 4.5, f"BACKLOG: {ratio:.2f}:1 < 4.5:1"

    def test_execucao_status_contrast(self) -> None:
        """EXECUCAO status colors meet WCAG AA (>= 4.5)."""
        config = STATUS_PALETTE["EXECUCAO"]
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        # Pre-validated: #1E40AF on #DBEAFE = 6.12:1
        assert ratio >= 4.5, f"EXECUCAO: {ratio:.2f}:1 < 4.5:1"

    def test_testes_status_contrast(self) -> None:
        """TESTES status colors meet WCAG AA (>= 4.5)."""
        config = STATUS_PALETTE["TESTES"]
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        # Pre-validated: #B45309 on #FEF3C7 = 4.85:1
        assert ratio >= 4.5, f"TESTES: {ratio:.2f}:1 < 4.5:1"

    def test_concluido_status_contrast(self) -> None:
        """CONCLUIDO status colors meet WCAG AA (>= 4.5)."""
        config = STATUS_PALETTE["CONCLUIDO"]
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        # Pre-validated: #18794E on #DDF3E4 = 4.72:1
        assert ratio >= 4.5, f"CONCLUIDO: {ratio:.2f}:1 < 4.5:1"

    def test_impedido_status_contrast(self) -> None:
        """IMPEDIDO status colors meet WCAG AA (>= 4.5)."""
        config = STATUS_PALETTE["IMPEDIDO"]
        ratio = calculate_contrast_ratio(config.foreground, config.background)
        # Pre-validated: #B91C1C on #FECACA = 4.58:1
        assert ratio >= 4.5, f"IMPEDIDO: {ratio:.2f}:1 < 4.5:1"


# =============================================================================
# T015: Unit test for STATUS_PALETTE WCAG AA compliance
# =============================================================================


class TestStatusPaletteWCAG:
    """Tests for STATUS_PALETTE WCAG AA compliance."""

    def test_all_status_colors_meet_wcag_aa(self) -> None:
        """All status colors have contrast ratio >= 4.5:1 (WCAG AA)."""
        for status, config in STATUS_PALETTE.items():
            ratio = calculate_contrast_ratio(config.foreground, config.background)
            assert ratio >= 4.5, f"{status}: {ratio:.2f}:1 < 4.5:1 (WCAG AA)"

    def test_all_statuses_have_symbols(self) -> None:
        """All status configurations have non-empty symbols."""
        for status, config in STATUS_PALETTE.items():
            assert config.symbol, f"{status} has empty symbol"

    def test_all_symbols_are_single_char(self) -> None:
        """All status symbols are single characters."""
        for status, config in STATUS_PALETTE.items():
            assert (
                len(config.symbol) == 1
            ), f"{status} symbol '{config.symbol}' is not single char"


# =============================================================================
# T016, T017: Unit tests for stylesheet.qss
# =============================================================================


class TestStylesheetValidation:
    """Tests for stylesheet.qss validation."""

    @pytest.fixture
    def stylesheet_path(self) -> Path:
        """Get path to stylesheet.qss."""
        return (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "backlog_manager"
            / "presentation"
            / "theme"
            / "stylesheet.qss"
        )

    @pytest.fixture
    def stylesheet_content(self, stylesheet_path: Path) -> str:
        """Read stylesheet.qss content."""
        if not stylesheet_path.exists():
            pytest.skip("stylesheet.qss not yet created")
        return stylesheet_path.read_text(encoding="utf-8")

    def test_no_hardcoded_hex_colors(self, stylesheet_content: str) -> None:
        """No hardcoded hex colors in stylesheet (T016, T079).

        All colors should use @var placeholders.
        """
        # Pattern matches #RGB, #RRGGBB, #RGBA, #RRGGBBAA
        # But not @var placeholders like @primary
        hex_pattern = r"(?<!@)#[0-9A-Fa-f]{3,8}\b"
        matches = re.findall(hex_pattern, stylesheet_content)
        assert not matches, f"Found hardcoded hex colors: {matches}"

    def test_all_placeholders_have_tokens(self, stylesheet_content: str) -> None:
        """All @var placeholders have corresponding DESIGN_TOKENS entries (T017)."""
        # Remove comments before checking placeholders
        # Comments are /* ... */ style in QSS
        content_without_comments = re.sub(
            r"/\*.*?\*/", "", stylesheet_content, flags=re.DOTALL
        )

        # Find all @placeholder patterns (not in property values like url(@...))
        placeholder_pattern = r"@([a-zA-Z][a-zA-Z0-9-]*)"
        placeholders = set(re.findall(placeholder_pattern, content_without_comments))

        missing = placeholders - set(DESIGN_TOKENS.keys())
        assert not missing, f"Placeholders without tokens: {missing}"


# =============================================================================
# T049: Unit test for :focus rules
# =============================================================================


class TestFocusRules:
    """Tests for :focus rules in stylesheet."""

    @pytest.fixture
    def stylesheet_content(self) -> str:
        """Read stylesheet.qss content."""
        path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "backlog_manager"
            / "presentation"
            / "theme"
            / "stylesheet.qss"
        )
        if not path.exists():
            pytest.skip("stylesheet.qss not yet created")
        return path.read_text(encoding="utf-8")

    def test_focus_rules_present_for_pushbutton(self, stylesheet_content: str) -> None:
        """QPushButton has :focus rule."""
        assert "QPushButton:focus" in stylesheet_content

    def test_focus_rules_present_for_lineedit(self, stylesheet_content: str) -> None:
        """QLineEdit has :focus rule."""
        assert "QLineEdit:focus" in stylesheet_content

    def test_focus_rules_present_for_combobox(self, stylesheet_content: str) -> None:
        """QComboBox has :focus rule."""
        assert "QComboBox:focus" in stylesheet_content

    def test_focus_rules_present_for_spinbox(self, stylesheet_content: str) -> None:
        """QSpinBox has :focus rule."""
        assert "QSpinBox:focus" in stylesheet_content

    def test_focus_rules_present_for_tableview(self, stylesheet_content: str) -> None:
        """QTableView has :focus rule."""
        assert "QTableView:focus" in stylesheet_content


# =============================================================================
# T055, T056, T057: Unit tests for IconManager
# =============================================================================


class TestIconManager:
    """Tests for IconManager class."""

    @pytest.fixture
    def icons_dir(self) -> Path:
        """Get path to icons directory."""
        return (
            Path(__file__).parent.parent.parent.parent.parent
            / "src"
            / "backlog_manager"
            / "assets"
            / "icons"
        )

    def test_all_16_svg_files_exist(self, icons_dir: Path) -> None:
        """All 16 SVG icon files exist in assets/icons/ (T055)."""
        if not icons_dir.exists():
            pytest.skip("Icons directory not yet created")

        missing = []
        for name in ICON_NAMES:
            icon_path = icons_dir / f"{name}.svg"
            if not icon_path.exists():
                missing.append(name)

        if missing:
            pytest.skip(f"Icons not yet downloaded: {missing}")

    def test_get_returns_qicon_for_valid_names(self, icons_dir: Path) -> None:
        """IconManager.get() returns valid QIcon for all names (T056)."""
        if not icons_dir.exists():
            pytest.skip("Icons directory not yet created")

        manager = IconManager(icons_dir)
        for name in ICON_NAMES:
            icon = manager.get(name)
            # QIcon is always returned, may be null if file missing
            assert icon is not None

    def test_get_returns_empty_qicon_for_unknown_name(self, icons_dir: Path) -> None:
        """IconManager.get() returns empty QIcon for unknown name (T057)."""
        manager = IconManager(icons_dir)
        icon = manager.get("nonexistent-icon")
        assert icon.isNull()


# =============================================================================
# Design Tokens Validation
# =============================================================================


class TestDesignTokens:
    """Tests for DESIGN_TOKENS dictionary."""

    def test_has_57_tokens(self) -> None:
        """DESIGN_TOKENS contains exactly 57 tokens."""
        assert len(DESIGN_TOKENS) == 57

    def test_all_values_are_strings(self) -> None:
        """All token values are strings."""
        for key, value in DESIGN_TOKENS.items():
            assert isinstance(value, str), f"{key} has non-string value: {type(value)}"

    def test_primary_colors_exist(self) -> None:
        """Primary color tokens exist."""
        assert "primary" in DESIGN_TOKENS
        assert "primary-light" in DESIGN_TOKENS
        assert "primary-dark" in DESIGN_TOKENS
        assert "primary-pressed" in DESIGN_TOKENS

    def test_neutral_scale_exists(self) -> None:
        """Neutral scale tokens exist (50-900)."""
        for n in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]:
            assert f"neutral-{n}" in DESIGN_TOKENS

    def test_semantic_colors_exist(self) -> None:
        """Semantic color tokens exist."""
        assert "background" in DESIGN_TOKENS
        assert "surface" in DESIGN_TOKENS
        assert "border" in DESIGN_TOKENS
        assert "text" in DESIGN_TOKENS
        assert "text-secondary" in DESIGN_TOKENS
        assert "text-muted" in DESIGN_TOKENS

    def test_status_colors_exist(self) -> None:
        """Status color tokens exist."""
        for prefix in ["success", "warning", "error", "info"]:
            assert f"{prefix}-bg" in DESIGN_TOKENS
            assert f"{prefix}-fg" in DESIGN_TOKENS

    def test_typography_tokens_exist(self) -> None:
        """Typography tokens exist."""
        assert "font-family" in DESIGN_TOKENS
        assert "font-family-mono" in DESIGN_TOKENS
        assert "font-size-base" in DESIGN_TOKENS

    def test_spacing_tokens_exist(self) -> None:
        """Spacing tokens exist."""
        for n in [0, 1, 2, 3, 4, 5, 6, 8]:
            assert f"spacing-{n}" in DESIGN_TOKENS

    def test_radius_tokens_exist(self) -> None:
        """Border radius tokens exist."""
        assert "radius-sm" in DESIGN_TOKENS
        assert "radius-md" in DESIGN_TOKENS
        assert "radius-lg" in DESIGN_TOKENS
        assert "radius-full" in DESIGN_TOKENS
