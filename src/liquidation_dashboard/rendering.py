"""Data preparation for the canvas and the self-contained chart HTML document."""
from __future__ import annotations

import html as html_escape
import json
import math
from datetime import datetime, timedelta, timezone

import numpy as np

from .api import APIError, timestamp
from .branding import brand_logo_uri
from .config import BRAND, chart_title
from .frontend import CANVAS_CONTROLLER, CANVAS_RENDERER, LOGOS, SVG_CONTEXT, VIEW_CONTROLS


def grid_metrics(payload):
    raw = np.asarray(payload['z'], dtype=float)
    grid = np.asarray(payload['y'], dtype=float)
    by_time = {timestamp(c['date']): c['close'] for c in payload['df']}
    price = np.asarray([by_time.get(timestamp(d), np.nan) for d in payload['x']])
    valid = np.isfinite(price) & np.isfinite(raw).all(axis=0)
    below = np.where(valid, np.where(grid[:, None] <= price, raw, 0).sum(axis=0), np.nan)
    above = np.where(valid, np.where(grid[:, None] > price, raw, 0).sum(axis=0), np.nan)
    return raw, grid, price, below, above

def frontend_data(payload, threshold=0, threshold_max=100):
    raw = np.asarray(payload['z'], dtype=float)
    finite = raw[np.isfinite(raw)]
    maximum = float(finite.max()) if finite.size else 0
    low, high = sorted((max(0, min(100, float(threshold))), max(0, min(100, float(threshold_max)))))
    filtered = np.where(np.isnan(raw), np.nan, np.where((raw >= maximum*low/100) & (raw <= maximum*high/100), raw, 0))
    processed = {**payload, 'z': filtered.tolist()}
    _, grid, price, longs, shorts = grid_metrics(processed)
    last = filtered[:, -1]
    known = np.isfinite(price[-1]) and np.isfinite(last).all()
    long_acc = np.cumsum(np.where(grid <= price[-1], last, 0)[::-1])[::-1] if known else np.full(len(grid), np.nan)
    short_acc = np.cumsum(np.where(grid > price[-1], last, 0)) if known else np.full(len(grid), np.nan)
    by_time = {timestamp(c['date']): c for c in payload['df']}
    result = {'zMatrix': filtered.tolist(), 'timestamps': [timestamp(d).timestamp()*1000 for d in payload['x']],
              'timeStrings': payload['x'], 'yValues': payload['y'], 'priceStep': float(grid[1]-grid[0]) if len(grid)>1 else 1,
              'currentPrice': float(price[-1]), 'maxZ': float(np.nanmax(filtered)) if finite.size else 0,
              'candles': [by_time.get(timestamp(d)) for d in payload['x']], 'liqByPrice': last.tolist(),
              'longsAccumByPrice': long_acc.tolist(), 'shortsAccumByPrice': short_acc.tolist(),
              'totalLongs': longs.tolist(), 'totalShorts': shorts.tolist(), 'netDelta': (longs-shorts).tolist(),
              'totalLongsSum': float(longs[-1]), 'totalShortsSum': float(shorts[-1])}
    def safe(value):
        if isinstance(value, float) and not math.isfinite(value): return None
        if isinstance(value, dict): return {k:safe(v) for k,v in value.items()}
        if isinstance(value, list): return [safe(v) for v in value]
        return value
    return safe(result)


def export_stem(payload, demo=False) -> str:
    """File-name stem shared by PNG, SVG and HTML exports, e.g. ``liquidation-levels-btc-2y-6h``."""
    parts = [str(payload.get(k)) for k in ('asset', 'lookback', 'timeframe') if payload.get(k)]
    return 'liquidation-levels-' + ('demo-' if demo else '') + '-'.join(parts)


def canvas_document(payload=None, palette='inferno', smoothing='false', threshold=0, threshold_max=100, theme='dark', demo=False, title=None, prepared_for=None, logo=None):
    if not payload:
        return '<!doctype html><html><body style="background:#0b0f19;color:#8b8fa3;font:14px system-ui;display:grid;place-items:center;height:650px;margin:0">Conecte sua chave e carregue uma série, ou abra a demonstração.</body></html>'
    if len(payload['y']) < 2:
        raise APIError('O desenho Canvas requer pelo menos dois níveis de preço.')
    config = {'data': frontend_data(payload, threshold, threshold_max), 'palette': palette, 'smoothing': smoothing, 'theme': theme, 'logo': LOGOS['light' if theme == 'light' else 'dark'], 'title': (title or '').strip() or chart_title(payload), 'demo': demo,
              'brand': {'preparedFor': (BRAND['prepared_for'] if prepared_for is None else prepared_for).strip(), 'copyright': BRAND['copyright'], 'source': BRAND['source'], 'logo': brand_logo_uri(logo)}}
    bg, fg = ('#0b0f19','#c5cad7') if theme == 'dark' else ('#f5f6f9','#374151')
    caption = ('DEMONSTRAÇÃO SINTÉTICA · ' if demo else '') + config['title']
    config['subtitle'] = ('DEMONSTRAÇÃO · DADOS SINTÉTICOS · ' if demo else '') + f"{payload.get('timeframe', '')} · {payload.get('exchange') or 'All exchanges'} · USD"
    config['caption'] = caption
    config['fileStem'] = export_stem(payload, demo)
    encoded = json.dumps(config, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    caption = html_escape.escape(caption)
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Liquidation Levels</title>
<style>body{{margin:0;background:{bg};color:{fg};font:11px system-ui}}*{{box-sizing:border-box}}.tools{{height:36px;display:flex;align-items:center;gap:6px;padding:0 8px;white-space:nowrap}}button{{background:transparent;color:{fg};border:1px solid #64748b55;border-radius:5px;padding:4px 9px;cursor:pointer}}button:hover,.selected{{border-color:#0d9276;color:#0d9276}}#viewport{{width:100%;overflow:auto;position:relative}}#canvas{{display:block;touch-action:none;cursor:grab}}#tip{{position:absolute;pointer-events:none;background:#101624f2;color:#e5e7eb;border:1px solid #475569;padding:9px;border-radius:5px;white-space:pre;font:11px system-ui;z-index:5}}.caption{{margin-left:auto;color:{'#e9b66d' if demo else fg};font-size:10px}}.hint{{font-size:10px;color:#8b8fa3;padding:3px 10px;display:flex;justify-content:space-between}}:fullscreen #viewport{{max-width:1800px;margin:auto}}</style></head><body>
<style>.tools{{overflow-x:auto;overflow-y:hidden}}.tools button{{flex-shrink:0}}.hint{{flex-wrap:wrap;gap:4px}}</style>
<div class="tools"><button data-tool="pan" class="selected" title="Arrastar">↔</button><button data-tool="hline" title="Linha horizontal">━</button><button data-tool="trendline" title="Linha de tendência: clique em dois pontos">╱</button><button id="clear-lines">Limpar linhas</button><button id="reset">Reset zoom</button><button id="png" title="Salva na pasta do projeto">PNG ↓</button><button id="svg" title="Textos, linhas e logo vetoriais; heatmap incorporado como imagem. Salva na pasta do projeto">SVG ↓</button><button id="full">⛶</button><span class="caption">{caption}</span></div>
<div id="viewport"><canvas id="canvas" aria-label="Liquidation Levels: heatmap, candles, distribuição acumulada, key levels e delta"></canvas><div id="tip" hidden></div></div>
<div class="hint"><span>Slider: arraste as pontas para ampliar ou o centro para mover · Scroll: zoom como na plataforma · Duplo clique: reset · UTC</span><span id="canvas-status"></span></div>
<div id="export-note" class="hint" role="status"></div>
<div id="view-status" class="hint" role="status"></div>
<script id="chart-config" type="application/json">{encoded}</script><script>{CANVAS_RENDERER}\n{SVG_CONTEXT}\n{VIEW_CONTROLS}\n{CANVAS_CONTROLLER}</script></body></html>'''


def demo_payload():
    rng = np.random.default_rng(27)
    n, count = 2921, 100
    start = datetime(2024, 10, 3, tzinfo=timezone.utc)
    x = [(start + timedelta(hours=6*i)).isoformat() for i in range(n)]
    close = 64000 + 650*np.sin(np.linspace(0, 9, n)) + np.cumsum(rng.normal(0, 8, n))
    y = np.linspace(61000, 68500, count)
    z = np.zeros((count, n))
    for center, strength in [(62000, 45e6), (63300, 25e6), (66200, 60e6), (67500, 35e6)]:
        z += np.exp(-((y[:, None]-center)/110)**2) * strength * (.55+.45*np.sin(np.linspace(0, 4, n)[None, :])**2)
    z[:, :18] *= np.linspace(0, 1, 18)**2
    z[z < 5e4] = 0
    df = [{'date': t, 'open': float(close[max(0, i-1)]), 'high': float(max(close[max(0, i-1)], close[i])+70),
           'low': float(min(close[max(0, i-1)], close[i])-70), 'close': float(close[i])} for i, t in enumerate(x)]
    return {'asset': 'btc', 'timeframe': '6h', 'lookback': '2y', 'scope': 'all', 'priceSource': 'SINTÉTICO',
            'x': x, 'y': y.tolist(), 'z': z.tolist(), 'df': df,
            'topTraderLsr': [{'date': t, 'value': float(1.2+.17*np.sin(i/23))} for i, t in enumerate(x)]}
