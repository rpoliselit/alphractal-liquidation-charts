"""Project-wide settings: paths, branding defaults, API constants and chart titles.

``PROJECT_DIR`` is the project root (the folder that contains ``src/``). Data the app reads or writes
(``assets/``, ``liquidation_db/``, ``liquidation_exports/``) lives there. The API key is kept in
``src/liquidation_dashboard/api_key.py`` (``KEY_FILE``), next to the code and git-ignored. Tests override
both through ``LIQUIDATION_PROJECT_DIR`` or by monkeypatching ``PROJECT_DIR`` / ``KEY_FILE``.
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

API_BASE = 'https://api.alphractal.com'
MAX_BYTES = 64 * 1024 * 1024   # largest accepted API response or export
MAX_CELLS = 4_000_000          # largest accepted heatmap (dates x price levels)
DEFAULT_SERIES = ('6h', '2y')  # (timeframe, lookback) preferred when available

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(os.environ.get('LIQUIDATION_PROJECT_DIR') or PACKAGE_DIR.parent.parent)  # src/liquidation_dashboard -> root
KEY_FILE = PACKAGE_DIR / 'api_key.py'  # ``alphractal_key = "..."``; written automatically after the first successful call

# Footer texts and logo folder, following printable_plot.plot_alphractal (assets_dir="assets").
# Defaults are neutral: no client name and no logo. Fill them in the UI, or set them here for a
# fixed deployment. ``logo_file`` is optional: when it exists it becomes the pre-selected logo.
BRAND = {
    'prepared_for': '',
    'copyright': '© 2026 Alphractal. All rights reserved.',
    'source': 'Alphractal.',  # rendered as "Source: Alphractal."
    'logo_file': '',          # e.g. 'client_logo.svg'; looked up in assets/ then in the project root
    'assets_dir': 'assets',
}
DB_DIRNAME = 'liquidation_db'
EXPORT_DIRNAME = 'liquidation_exports'

ASSET_NAMES = {'btc': 'Bitcoin', 'eth': 'Ethereum', 'sol': 'Solana', 'bnb': 'BNB', 'xrp': 'XRP', 'doge': 'Dogecoin',
               'ada': 'Cardano', 'avax': 'Avalanche', 'link': 'Chainlink'}
LOOKBACK_NAMES = {'12h': '12 hours', '24h': '24 hours', '3d': '3 days', '7d': '7 days', '14d': '14 days', '30d': '1 month',
                  '90d': '3 months', '180d': '6 months', '365d': '1 year', '2y': '2 years', '4y': '4 years', '6y': '6 years',
                  'demonstração': 'demonstration'}


def project_dir() -> Path:
    return Path(PROJECT_DIR)


def db_dir() -> Path:
    return project_dir() / DB_DIRNAME


def export_dir() -> Path:
    return project_dir() / EXPORT_DIRNAME


def load_api_key() -> str:
    """Return ``alphractal_key`` from ``KEY_FILE``, or '' when the file is missing or malformed.

    The file is parsed, not imported, so a broken file can never crash the app.
    """
    path = Path(KEY_FILE)
    if not path.is_file():
        return ''
    try:
        tree = ast.parse(path.read_text(encoding='utf-8'))
    except (OSError, SyntaxError, UnicodeError):
        return ''
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'alphractal_key' for t in node.targets):
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value.strip()
    return ''


def save_api_key(key: str) -> bool:
    """Store the key in ``KEY_FILE`` (owner read/write only). Returns True when the file changed."""
    key = (key or '').strip()
    if not key or key == load_api_key():
        return False
    path = Path(KEY_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.py.tmp')
    tmp.write_text('# Written automatically by liquidation_dashboard; this file is git-ignored.\n'
                   f'alphractal_key = {key!r}\n', encoding='utf-8')
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)
    return True


def forget_api_key() -> None:
    """Delete ``KEY_FILE`` if it exists."""
    Path(KEY_FILE).unlink(missing_ok=True)


def chart_title(payload=None) -> str:
    payload = payload or {'asset': 'btc', 'lookback': '2y'}
    asset = str(payload.get('asset', 'btc')).lower()
    name = ASSET_NAMES.get(asset, asset.upper())
    lookback = str(payload.get('lookback', '2y'))
    return f'{name}: Liquidation Levels ({LOOKBACK_NAMES.get(lookback, lookback)})'


def preferred_series(series):
    """Pick the default (timeframe, lookback) pair, else the longest lookback available."""
    if DEFAULT_SERIES in series:
        return DEFAULT_SERIES
    return series[-1] if series else None
