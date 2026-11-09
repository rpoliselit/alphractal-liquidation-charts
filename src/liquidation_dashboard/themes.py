"""Chart color themes, shared with the browser renderer.

Three themes, matching ``printable_plot``:

``alphractal_dark``  (default) the Alphractal platform in dark mode.
``alphractal_light`` the Alphractal platform in light mode.
``classic``          the original warm "paper" look of ``printable_plot``.

Every field becomes a key of ``config.theme`` in the chart document, so the
JavaScript drawing code reads ``t.text``, ``t.grid`` and so on instead of
hard-coded colors. The long/short green and red and the heatmap color scales
are data colors and stay the same in every theme.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

TITLE_SERIF = '"STIXGeneral","STIX Two Text","STIX","Times New Roman",Times,serif'
TITLE_SANS = '"DejaVu Sans",Verdana,Geneva,sans-serif'


@dataclass(frozen=True)
class Theme:
    name: str
    label: str                # Shown in the Theme dropdown.
    logo: str                 # Watermark variant: "dark" (light artwork) or "light".
    # --- Surfaces ----------------------------------------------------------------
    background: str           # Whole chart, on screen.
    export_background: bool   # Also paint it in PNG/SVG exports (False = transparent).
    panel_bg: str             # Accumulated and net-delta panels.
    side_panel_bg: str        # Liquidation distribution and key levels.
    tag_bg: str               # Value tags in the distribution panel.
    # --- Text --------------------------------------------------------------------
    text: str                 # Axis labels and small values.
    text_label: str           # Panel titles ("Key Levels", "Net Longs - Shorts").
    text_heading: str         # "Liquidation Distribution".
    text_strong: str          # Current price in the distribution panel.
    text_value: str           # Key-level prices, color-bar hover value.
    text_dim: str             # Secondary key-level values.
    # --- Lines -------------------------------------------------------------------
    grid: str
    hairline: str             # Panel edges, color-bar outline, ratio-bar track.
    panel_border: str
    divider: str
    subtle_fill: str          # Distribution chart body.
    price_line: str           # Dashed current-price line on the heatmap.
    price_label: str
    marker_line: str          # Current price inside the distribution panel.
    glow: str                 # Shadow behind the current price.
    hover_line: str           # Color-bar hover marker.
    hover_marker: str
    crosshair: str
    scroll_track: str
    scroll_thumb: str
    scroll_handle: str
    # --- Branding (title, subtitle, source and footer) --------------------------------
    brand_title: str
    brand_subtitle: str
    brand_text: str
    title_font: str

    def to_config(self) -> dict:
        """JSON-ready tokens for the chart document."""
        return asdict(self)


ALPHRACTAL_DARK = Theme(
    name='alphractal_dark', label='Alphractal Dark', logo='dark',
    background='#0F1729', export_background=True,
    panel_bg='rgba(15,23,41,0.8)', side_panel_bg='rgba(15,23,41,0.5)', tag_bg='rgba(15,23,41,0.85)',
    text='#94A3B8', text_label='#94A3B8', text_heading='#CBD5E1', text_strong='#F8FAFC',
    text_value='#E2E8F0', text_dim='#7C8AA0',
    grid='rgba(148,163,184,0.10)', hairline='rgba(148,163,184,0.16)', panel_border='rgba(148,163,184,0.18)',
    divider='rgba(148,163,184,0.12)', subtle_fill='rgba(148,163,184,0.03)',
    price_line='rgba(248,250,252,0.7)', price_label='rgba(248,250,252,0.9)', marker_line='rgba(248,250,252,0.24)',
    glow='rgba(248,250,252,0.18)', hover_line='rgba(248,250,252,0.7)', hover_marker='rgba(248,250,252,0.9)',
    crosshair='rgba(248,250,252,0.18)',
    scroll_track='rgba(148,163,184,0.06)', scroll_thumb='rgba(60,131,246,0.22)', scroll_handle='rgba(60,131,246,0.6)',
    brand_title='#F8FAFC', brand_subtitle='#94A3B8', brand_text='#94A3B8', title_font=TITLE_SANS,
)

ALPHRACTAL_LIGHT = Theme(
    name='alphractal_light', label='Alphractal Light', logo='light',
    background='#FFFFFF', export_background=True,
    panel_bg='rgba(255,255,255,0.8)', side_panel_bg='rgba(241,245,249,0.5)', tag_bg='rgba(255,255,255,0.9)',
    text='#65758B', text_label='#65758B', text_heading='#334155', text_strong='#0E0E10',
    text_value='#0E0E10', text_dim='#8792A2',
    grid='rgba(15,23,42,0.08)', hairline='rgba(15,23,42,0.08)', panel_border='rgba(15,23,42,0.10)',
    divider='rgba(15,23,42,0.06)', subtle_fill='rgba(15,23,42,0.02)',
    price_line='rgba(14,14,16,0.5)', price_label='rgba(14,14,16,0.85)', marker_line='rgba(14,14,16,0.18)',
    glow='rgba(14,14,16,0.10)', hover_line='rgba(14,14,16,0.7)', hover_marker='rgba(14,14,16,0.9)',
    crosshair='rgba(14,14,16,0.16)',
    scroll_track='rgba(15,23,42,0.04)', scroll_thumb='rgba(76,109,255,0.16)', scroll_handle='rgba(76,109,255,0.55)',
    brand_title='#0E0E10', brand_subtitle='#65758B', brand_text='#65758B', title_font=TITLE_SANS,
)

CLASSIC = Theme(
    name='classic', label='Classic', logo='light',
    background='#F8F5F2', export_background=False,
    panel_bg='rgba(248,245,242,0.8)', side_panel_bg='rgba(245,239,229,0.5)', tag_bg='rgba(248,245,242,0.9)',
    text='#76695D', text_label='#65594E', text_heading='#65594E', text_strong='#241E18',
    text_value='#241E18', text_dim='#887767',
    grid='rgba(36,30,24,0.08)', hairline='rgba(36,30,24,0.09)', panel_border='rgba(36,30,24,0.10)',
    divider='rgba(36,30,24,0.06)', subtle_fill='rgba(36,30,24,0.02)',
    price_line='rgba(36,30,24,0.5)', price_label='rgba(36,30,24,0.85)', marker_line='rgba(36,30,24,0.18)',
    glow='rgba(36,30,24,0.10)', hover_line='rgba(36,30,24,0.7)', hover_marker='rgba(36,30,24,0.9)',
    crosshair='rgba(36,30,24,0.16)',
    scroll_track='rgba(36,30,24,0.04)', scroll_thumb='rgba(75,107,255,0.15)', scroll_handle='rgba(75,107,255,0.5)',
    brand_title='#241E18', brand_subtitle='#887767', brand_text='#76695D', title_font=TITLE_SERIF,
)

THEMES = {theme.name: theme for theme in (ALPHRACTAL_DARK, ALPHRACTAL_LIGHT, CLASSIC)}
DEFAULT_THEME = ALPHRACTAL_DARK.name
# Values used before themes existed (saved links, scripts) keep working.
LEGACY_ALIASES = {'dark': ALPHRACTAL_DARK.name, 'light': ALPHRACTAL_LIGHT.name}


def get_theme(name: str | None = None) -> Theme:
    """Theme by name; None gives the default, and 'dark'/'light' map to the Alphractal themes."""
    if name is None:
        return THEMES[DEFAULT_THEME]
    name = LEGACY_ALIASES.get(name, name)
    if name not in THEMES:
        raise ValueError(f"Unknown theme {name!r}. Choose one of: {', '.join(THEMES)}.")
    return THEMES[name]


def theme_options() -> list[dict]:
    """Options for the Theme dropdown, default first."""
    return [{'label': theme.label, 'value': theme.name} for theme in THEMES.values()]
