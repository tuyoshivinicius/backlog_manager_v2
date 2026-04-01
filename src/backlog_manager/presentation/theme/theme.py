"""Design system tokens and utilities for Backlog Manager.

This module provides centralized design tokens (colors, fonts, spacing),
status palette configuration, and theme application utilities.
"""

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtGui import QIcon

# =============================================================================
# DESIGN TOKENS (T008)
# =============================================================================

DESIGN_TOKENS: dict[str, str] = {
    # === Primary Colors ===
    "primary": "#0066CC",
    "primary-light": "#E6F0FA",
    "primary-dark": "#004D99",
    "primary-pressed": "#003D7A",
    # === Neutral Colors (Gray Scale) ===
    "neutral-50": "#FAFAFA",
    "neutral-100": "#F5F5F5",
    "neutral-200": "#E5E5E5",
    "neutral-300": "#D4D4D4",
    "neutral-400": "#A3A3A3",
    "neutral-500": "#737373",
    "neutral-600": "#525252",
    "neutral-700": "#404040",
    "neutral-800": "#262626",
    "neutral-900": "#171717",
    # === Semantic Colors ===
    "background": "#FFFFFF",
    "surface": "#FAFAFA",
    "border": "#E5E5E5",
    "text": "#171717",
    "text-secondary": "#525252",
    "text-muted": "#737373",
    # === Status Colors (WCAG AA Validated) ===
    "success-bg": "#DDF3E4",
    "success-fg": "#18794E",
    "warning-bg": "#FEF3C7",
    "warning-fg": "#B45309",
    "error-bg": "#FECACA",
    "error-fg": "#B91C1C",
    "info-bg": "#DBEAFE",
    "info-fg": "#1E40AF",
    # === Typography ===
    "font-family": "Inter, Segoe UI, system-ui, sans-serif",
    "font-family-mono": "JetBrains Mono, Cascadia Code, Consolas, monospace",
    "font-size-xs": "10px",
    "font-size-sm": "12px",
    "font-size-base": "13px",
    "font-size-md": "14px",
    "font-size-lg": "16px",
    "font-size-xl": "18px",
    "font-size-2xl": "24px",
    "font-weight-normal": "400",
    "font-weight-medium": "500",
    "font-weight-semibold": "600",
    "font-weight-bold": "700",
    # === Spacing ===
    "spacing-0": "0px",
    "spacing-1": "4px",
    "spacing-2": "8px",
    "spacing-3": "12px",
    "spacing-4": "16px",
    "spacing-5": "20px",
    "spacing-6": "24px",
    "spacing-8": "32px",
    # === Border Radius ===
    "radius-sm": "2px",
    "radius-md": "4px",
    "radius-lg": "8px",
    "radius-full": "9999px",
    # === Shadows ===
    "shadow-sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
    "shadow-md": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "shadow-lg": "0 10px 15px rgba(0, 0, 0, 0.1)",
    # === Interactive States ===
    "focus-ring": "2px solid #0066CC",
    "hover-opacity": "0.9",
    # === Selection States (WCAG AA validated) ===
    "selection-bg": "#E6F0FA",
    "selection-fg": "#171717",
    "selection-border": "#0066CC",
    "selection-hover-bg": "#D6E8F7",
    "hover-bg": "#F5F5F5",
}


# =============================================================================
# STATUS PALETTE (T009, T010)
# =============================================================================


@dataclass(frozen=True)
class StatusConfig:
    """Configuration for status badge rendering.

    Attributes:
        symbol: Non-chromatic symbol for accessibility (e.g., ●, ▶, ✓).
        background: Background color in hex format.
        foreground: Text/symbol color in hex format.
    """

    symbol: str
    background: str
    foreground: str


# =============================================================================
# WAVE PALETTE - Subtle row background tints per wave number
# =============================================================================

# =============================================================================
# TABLE SELECTION QSS (T002)
# =============================================================================

TABLE_SELECTION_QSS: str = """
QTableView::item:hover {
    background-color: @hover-bg;
}
QTableView::item:selected {
    background-color: @selection-bg;
    color: @selection-fg;
    border-left: 3px solid @selection-border;
}
QTableView::item:selected:hover {
    background-color: @selection-hover-bg;
    color: @selection-fg;
    border-left: 3px solid @selection-border;
}
"""


WAVE_PALETTE: list[str] = [
    "",  # index 0 = no wave (no tint, default background)
    "#EFF6FF",  # wave 1 - light blue
    "#FFF7ED",  # wave 2 - light orange
    "#F0FDF4",  # wave 3 - light green
    "#FDF4FF",  # wave 4 - light purple
    "#FFFBEB",  # wave 5 - light yellow
    "#F0FDFA",  # wave 6 - light teal
    "#FFF1F2",  # wave 7 - light rose
    "#EEF2FF",  # wave 8 - light indigo
]


STATUS_PALETTE: dict[str, StatusConfig] = {
    "BACKLOG": StatusConfig(
        symbol="●",
        background="#E5E5E5",
        foreground="#525252",
    ),
    "EXECUCAO": StatusConfig(
        symbol="▶",
        background="#DBEAFE",
        foreground="#1E40AF",
    ),
    "TESTES": StatusConfig(
        symbol="◆",
        background="#FEF3C7",
        foreground="#B45309",
    ),
    "CONCLUIDO": StatusConfig(
        symbol="✓",
        background="#DDF3E4",
        foreground="#18794E",
    ),
    "IMPEDIDO": StatusConfig(
        symbol="✕",
        background="#FECACA",
        foreground="#991B1B",  # Darker red for WCAG AA compliance (4.5:1+)
    ),
}


# =============================================================================
# THEME APPLICATION (T011)
# =============================================================================


def apply_theme(qss_template: str, tokens: dict[str, str]) -> str:
    """Apply design tokens to a QSS template by substituting placeholders.

    Placeholders in the template are in the format @token-name and will be
    replaced with the corresponding value from the tokens dictionary.

    Uses longest-first substitution order to prevent partial matches
    (e.g., @primary-pressed is replaced before @primary).

    Args:
        qss_template: QSS content with @var placeholders.
        tokens: Dictionary mapping token names to values.

    Returns:
        QSS content with all placeholders substituted.

    Example:
        >>> template = "background: @primary; color: @text;"
        >>> tokens = {"primary": "#0066CC", "text": "#171717"}
        >>> apply_theme(template, tokens)
        'background: #0066CC; color: #171717;'
    """
    sorted_keys = sorted(tokens.keys(), key=len, reverse=True)
    result = qss_template
    for key in sorted_keys:
        result = result.replace(f"@{key}", tokens[key])
    return result


# =============================================================================
# CONTRAST CALCULATION (T012)
# =============================================================================


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Color in hex format (e.g., "#FFFFFF" or "FFFFFF").

    Returns:
        Tuple of (red, green, blue) values (0-255).
    """
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def _relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1.

    Args:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).

    Returns:
        Relative luminance value (0.0 to 1.0).
    """

    def _srgb_to_linear(value: int) -> float:
        v = value / 255.0
        if v <= 0.03928:
            return v / 12.92
        return ((v + 0.055) / 1.055) ** 2.4

    r_lin = _srgb_to_linear(r)
    g_lin = _srgb_to_linear(g)
    b_lin = _srgb_to_linear(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def calculate_contrast_ratio(foreground: str, background: str) -> float:
    """Calculate WCAG 2.1 contrast ratio between two colors.

    The contrast ratio is calculated using the formula:
    (L1 + 0.05) / (L2 + 0.05) where L1 is the lighter color's luminance.

    Args:
        foreground: Foreground color in hex format (e.g., "#000000").
        background: Background color in hex format (e.g., "#FFFFFF").

    Returns:
        Contrast ratio (1.0 to 21.0). WCAG AA requires >= 4.5 for normal text.

    Example:
        >>> calculate_contrast_ratio("#000000", "#FFFFFF")
        21.0
        >>> calculate_contrast_ratio("#525252", "#E5E5E5")
        5.45
    """
    fg_rgb = _hex_to_rgb(foreground)
    bg_rgb = _hex_to_rgb(background)

    fg_lum = _relative_luminance(*fg_rgb)
    bg_lum = _relative_luminance(*bg_rgb)

    lighter = max(fg_lum, bg_lum)
    darker = min(fg_lum, bg_lum)

    return (lighter + 0.05) / (darker + 0.05)


# =============================================================================
# ICON MANAGEMENT (T074-T078)
# =============================================================================

ICON_NAMES: list[str] = [
    "plus",
    "pencil-simple",
    "trash",
    "arrow-up",
    "arrow-down",
    "users",
    "package",
    "gear",
    "calendar-check",
    "shuffle",
    "download-simple",
    "upload-simple",
    "copy",
    "warning-triangle",
    "link",
    "x",
]


class IconManager:
    """Manager for SVG icons with eager loading.

    Icons are loaded from the assets/icons directory at initialization time
    to avoid latency on first use.

    Attributes:
        _icons: Dictionary mapping icon names to QIcon instances.
    """

    def __init__(self, icons_dir: Path | None = None) -> None:
        """Initialize the icon manager.

        Args:
            icons_dir: Path to the icons directory. If None, uses the default
                       location at src/backlog_manager/assets/icons/.
        """
        self._icons: dict[str, QIcon] = {}
        if icons_dir is None:
            icons_dir = Path(__file__).parent.parent.parent / "assets" / "icons"
        self._icons_dir = icons_dir
        self._load_all()

    def _load_all(self) -> None:
        """Load all icons from the icons directory."""
        for name in ICON_NAMES:
            icon_path = self._icons_dir / f"{name}.svg"
            if icon_path.exists():
                self._icons[name] = QIcon(str(icon_path))
            else:
                self._icons[name] = QIcon()

    def get(self, name: str) -> QIcon:
        """Get an icon by name.

        Args:
            name: The icon name (without .svg extension).

        Returns:
            QIcon instance, or empty QIcon if name is not found.

        Example:
            >>> manager = IconManager()
            >>> icon = manager.get("plus")
            >>> action = QAction(icon, "Add", parent)
        """
        return self._icons.get(name, QIcon())


# Create singleton instance for application-wide use
# This will be initialized lazily to avoid issues during module import
_icon_manager: IconManager | None = None


def get_icon_manager() -> IconManager:
    """Get the global icon manager instance.

    Creates the instance on first call (lazy initialization).

    Returns:
        The global IconManager instance.
    """
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager


# For backwards compatibility and convenience
icon_manager: IconManager | None = None


def _initialize_icon_manager() -> None:
    """Initialize the global icon_manager instance.

    This should be called during app startup, after QApplication is created.
    """
    global icon_manager
    icon_manager = get_icon_manager()
