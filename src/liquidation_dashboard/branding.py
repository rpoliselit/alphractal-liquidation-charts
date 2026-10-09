"""Logo discovery and embedding for the chart footer."""
from __future__ import annotations

import base64
import re

from .config import BRAND, project_dir


def logo_choices() -> list[str]:
    """SVG files offered in the UI: ``assets/*.svg`` plus the default logo in the project root, if present."""
    choices = []
    assets = project_dir() / BRAND['assets_dir']
    if assets.is_dir():
        choices += [f"{BRAND['assets_dir']}/{f.name}" for f in sorted(assets.glob('*.svg')) if f.is_file()]
    if BRAND['logo_file'] and (project_dir() / BRAND['logo_file']).is_file():
        choices.append(BRAND['logo_file'])
    return choices


def default_logo() -> str:
    """Pre-selected logo: ``BRAND['logo_file']`` when configured and present, otherwise none."""
    if not BRAND['logo_file']:
        return ''
    choices = logo_choices()
    for preferred in (f"{BRAND['assets_dir']}/{BRAND['logo_file']}", BRAND['logo_file']):
        if preferred in choices:
            return preferred
    return ''


def brand_logo_uri(logo: str | None = None) -> str | None:
    """Embed the chosen SVG as a data URI. Only files returned by ``logo_choices`` are accepted."""
    if logo is None:
        logo = default_logo()
    if not logo or logo not in logo_choices():
        return None
    try:
        svg = (project_dir() / logo).read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError):
        return None
    match = re.search(r'<svg\b[^>]*>', svg, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    tag = match[0]
    # Firefox reports naturalWidth=0 for an SVG without width/height; derive them from the viewBox.
    if not re.search(r'\swidth\s*=', tag) or not re.search(r'\sheight\s*=', tag):
        box = re.search(r'viewBox\s*=\s*["\']\s*([\d.eE+-]+)[\s,]+([\d.eE+-]+)[\s,]+([\d.eE+-]+)[\s,]+([\d.eE+-]+)', tag)
        if box:
            tag = tag[:-1] + f' width="{box[3]}" height="{box[4]}">'
            svg = svg[:match.start()] + tag + svg[match.end():]
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('ascii')
