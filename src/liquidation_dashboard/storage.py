"""Local Parquet database and export files.

One Parquet file per series lives in ``liquidation_db/`` (``<asset>_<timeframe>_<lookback>_<exchange>.parquet``).
Columns are ``date`` plus ``L0..Ln`` (one per price level). Metadata (asset, timeframe, lookback, scope,
exchange, the ``y`` levels, candles, top-trader LSR and the save timestamp) is stored in the Parquet schema
metadata. Values are written exactly as the API returned them.

The API catalog (assets, valid timeframe/lookback pairs and exchanges per asset) is cached in
``liquidation_db/catalog.json`` so the dropdowns are filled on start-up without calling the API.

PNG, SVG and HTML exports are written to ``liquidation_exports/`` and never overwrite existing files.
"""
from __future__ import annotations

import base64
import json
import math
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .api import APIError, duration, identifier, validate_payload
from .config import ASSET_NAMES, MAX_BYTES, db_dir, export_dir, preferred_series

DB_META = b'alphractal'
PAYLOAD_FIELDS = ('asset', 'timeframe', 'lookback', 'scope', 'exchange', 'version', 'priceSource')


def _pyarrow():
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        raise APIError('Banco local indisponível: instale pyarrow (python -m pip install "pyarrow>=15").') from None
    return pa, pq


def db_key(asset, timeframe, lookback, exchange=None) -> str:
    return '_'.join(re.sub(r'[^a-z0-9.-]+', '-', str(v).lower()) for v in (asset, timeframe, lookback, exchange or 'all'))


def db_path(asset, timeframe, lookback, exchange=None) -> Path:
    return db_dir() / (db_key(asset, timeframe, lookback, exchange) + '.parquet')


def db_save(payload, path: Path) -> Path:
    """Atomically (over)write the series file: write to ``.tmp`` then rename."""
    pa, pq = _pyarrow()
    z = np.array(payload['z'], dtype=float)  # None -> NaN; NaN becomes None again on load
    columns = {'date': pa.array(payload['x'], pa.string())}
    for i in range(z.shape[0]):
        columns[f'L{i}'] = pa.array(z[i], pa.float64(), from_pandas=True)
    meta = {k: payload.get(k) for k in PAYLOAD_FIELDS}
    meta.update(y=payload['y'], df=payload.get('df', []), topTraderLsr=payload.get('topTraderLsr', []),
                saved_at=datetime.now(timezone.utc).isoformat(timespec='seconds'), rows=len(payload['x']), levels=len(payload['y']))
    table = pa.table(columns).replace_schema_metadata({DB_META: json.dumps(meta, ensure_ascii=False, allow_nan=False).encode('utf-8')})
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.parquet.tmp')
    try:
        pq.write_table(table, tmp, compression='zstd')
        os.replace(tmp, path)
    except OSError as exc:
        raise APIError(f'Não foi possível gravar o banco local em {path}: {exc}') from None
    finally:
        tmp.unlink(missing_ok=True)
    return path


def db_meta(path: Path):
    """Read only the schema metadata (cheap); None when the file is not a valid series."""
    _, pq = _pyarrow()
    try:
        raw = (pq.read_schema(path).metadata or {}).get(DB_META)
        meta = json.loads(raw.decode('utf-8')) if raw else None
    except (OSError, ValueError, UnicodeError):
        return None
    valid = isinstance(meta, dict) and all(duration(meta.get(k)) for k in ('timeframe', 'lookback')) and identifier(meta.get('asset'))
    return meta if valid else None


def db_load(path: Path):
    """Rebuild the payload exactly as the API returned it and validate it again."""
    _, pq = _pyarrow()
    meta = db_meta(path)
    if not meta:
        raise APIError(f'Arquivo do banco local inválido: {path.name}. Use "Baixar da API" para regravar.')
    try:
        table = pq.read_table(path)
    except (OSError, ValueError) as exc:
        raise APIError(f'Falha ao ler {path.name}: {exc}') from None
    levels = int(meta.get('levels', 0))
    if 'date' not in table.column_names or any(f'L{i}' not in table.column_names for i in range(levels)):
        raise APIError(f'Colunas ausentes em {path.name}. Use "Baixar da API" para regravar.')
    x = table.column('date').to_pylist()
    z = [[None if (v is None or (isinstance(v, float) and math.isnan(v))) else v for v in table.column(f'L{i}').to_pylist()]
         for i in range(levels)]
    body = {'x': x, 'y': meta['y'], 'z': z, 'df': meta.get('df', []), 'topTraderLsr': meta.get('topTraderLsr', []),
            **{k: meta[k] for k in PAYLOAD_FIELDS if meta.get(k) is not None}}
    return validate_payload(body), meta


def db_entries() -> list[dict]:
    """List stored series: ``[{asset, timeframe, lookback, exchange, saved_at, path}]``."""
    entries = []
    folder = db_dir()
    if not folder.is_dir():
        return entries
    try:
        _pyarrow()
    except APIError:
        return entries
    for path in sorted(folder.glob('*.parquet')):
        meta = db_meta(path)
        if meta:
            exchange = meta.get('exchange') if meta.get('scope') == 'exchange' and identifier(meta.get('exchange')) else 'all'
            entries.append({'asset': meta['asset'], 'timeframe': meta['timeframe'], 'lookback': meta['lookback'],
                            'exchange': exchange, 'saved_at': meta.get('saved_at', '?'), 'path': path})
    return entries


def db_series_options(asset, api_series=None, exchanges=None):
    """Dropdown options for one asset, marking series that already exist locally.

    Returns ``(series_options, selected_value, exchange_options, local_count)``.
    """
    local = [e for e in db_entries() if e['asset'] == asset]
    local_keys = {(e['timeframe'], e['lookback']) for e in local}
    pairs = sorted(set(api_series or []) | local_keys, key=lambda pair: (duration(pair[1]), duration(pair[0])))
    options = [{'label': f'{lookback} · {tf}' + (' · local' if (tf, lookback) in local_keys else ''), 'value': f'{tf}|{lookback}'}
               for tf, lookback in pairs]
    preferred = preferred_series(pairs)
    exchange_values = sorted({e['exchange'] for e in local if e['exchange'] != 'all'} | {e for e in (exchanges or []) if e != 'all'})
    exchange_options = [{'label': 'Todas (agregado)', 'value': 'all'}] + [{'label': e, 'value': e} for e in exchange_values]
    return options, ('|'.join(preferred) if preferred else None), exchange_options, len(local)


# ---------------------------------------------------------------------------- catalog cache

CATALOG_FILE = 'catalog.json'


def catalog_load() -> dict:
    """Cached catalog: ``{'assets': [...], 'per_asset': {asset: {'series': [[tf, lb], ...], 'exchanges': [...]}}, 'saved_at': ...}``."""
    path = db_dir() / CATALOG_FILE
    try:
        data = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    except (OSError, ValueError, UnicodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    assets = [a for a in data.get('assets', []) if identifier(a)]
    per_asset = {}
    for asset, entry in (data.get('per_asset') or {}).items():
        if not identifier(asset) or not isinstance(entry, dict):
            continue
        series = [(tf, lb) for tf, lb in (pair for pair in entry.get('series', []) if isinstance(pair, list) and len(pair) == 2)
                  if duration(tf) and duration(lb)]
        exchanges = [e for e in entry.get('exchanges', []) if identifier(e)]
        per_asset[asset] = {'series': series, 'exchanges': exchanges}
    return {'assets': assets, 'per_asset': per_asset, 'saved_at': data.get('saved_at')}


def catalog_save(assets=None, asset=None, series=None, exchanges=None) -> Path:
    """Merge new catalog data into the cache (other assets' entries are kept)."""
    current = catalog_load()
    if assets:
        current['assets'] = sorted(set(assets))
    if asset:
        current['per_asset'][asset] = {'series': [list(pair) for pair in (series or [])], 'exchanges': sorted(set(exchanges or []))}
    current['saved_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    data = {'assets': current['assets'], 'saved_at': current['saved_at'],
            'per_asset': {a: {'series': [list(pair) for pair in e['series']], 'exchanges': e['exchanges']} for a, e in current['per_asset'].items()}}
    folder = db_dir()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / CATALOG_FILE
    tmp = path.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)
    return path


def known_assets() -> list[str]:
    """Assets to offer before connecting: cached catalog, local database and the built-in list."""
    return sorted(set(catalog_load()['assets']) | {e['asset'] for e in db_entries()} | set(ASSET_NAMES))


def asset_label(asset: str) -> str:
    name = ASSET_NAMES.get(asset)
    return f'{asset.upper()} · {name}' if name else asset.upper()


def asset_options(asset):
    """Series/exchange options for an asset from the cached catalog plus the local database (no API call)."""
    entry = catalog_load()['per_asset'].get(asset, {})
    return db_series_options(asset, entry.get('series'), entry.get('exchanges'))


# ---------------------------------------------------------------------------- exports

def _safe_stem(stem) -> str:
    stem = re.sub(r'[^a-z0-9._-]+', '-', str(stem or '').lower()).strip('-')[:80]
    return stem or 'liquidation-levels'


def _write_new(folder: Path, stem: str, suffix: str, raw: bytes) -> Path:
    """Write ``raw`` to a new timestamped file; add a random suffix on a name clash."""
    folder.mkdir(parents=True, exist_ok=True)
    stamp = f'{datetime.now(timezone.utc):%Y%m%d-%H%M%S}'
    for name in (f'{stem}-{stamp}.{suffix}', f'{stem}-{stamp}-{secrets.token_hex(3)}.{suffix}'):
        target = folder / name
        try:
            with target.open('xb') as handle:
                handle.write(raw)
            return target
        except FileExistsError:
            continue
    raise OSError('could not allocate a unique export name')


def save_export(kind: str, content: str, stem=None) -> Path:
    """Persist a PNG (data URI) or SVG (text) produced by the canvas. Raises ``ValueError`` on bad input."""
    if kind not in {'png', 'svg'} or not isinstance(content, str) or not content:
        raise ValueError('Pedido inválido.')
    if kind == 'png':
        if not content.startswith('data:image/png;base64,'):
            raise ValueError('PNG inválido.')
        try:
            raw = base64.b64decode(content.split(',', 1)[1], validate=True)
        except ValueError:
            raise ValueError('PNG inválido.') from None
    else:
        if not content.lstrip().startswith('<svg'):
            raise ValueError('SVG inválido.')
        raw = content.encode('utf-8')
    if len(raw) > MAX_BYTES:
        raise ValueError('Arquivo acima de 64 MB.')
    return _write_new(export_dir(), _safe_stem(stem), kind, raw)


def save_html_export(document: str, stem=None) -> Path:
    """Persist the interactive HTML document next to the PNG/SVG exports."""
    return _write_new(export_dir(), _safe_stem(stem), 'html', document.encode('utf-8'))
