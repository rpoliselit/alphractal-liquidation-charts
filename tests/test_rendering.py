import json
import re

import numpy as np

from liquidation_dashboard import rendering
from liquidation_dashboard.config import BRAND


def test_export_stem():
    assert rendering.export_stem({'asset': 'btc', 'lookback': '2y', 'timeframe': '6h'}) == 'liquidation-levels-btc-2y-6h'
    assert rendering.export_stem({'asset': 'eth'}, demo=True) == 'liquidation-levels-demo-eth'


def test_grid_metrics_splits_below_and_above_price(payload):
    raw, grid, price, below, above = rendering.grid_metrics(payload)
    assert raw.shape == (len(payload['y']), len(payload['x']))
    total = np.nansum(raw, axis=0)
    assert np.allclose(below + above, total)
    assert np.isfinite(price).all()


def test_frontend_data_shapes_and_threshold(payload):
    data = rendering.frontend_data(payload, threshold=50, threshold_max=100)
    assert len(data['timestamps']) == len(payload['x']) and len(data['yValues']) == len(payload['y'])
    maximum = max(max(v for v in row if v is not None) for row in payload['z'])
    kept = [v for row in data['zMatrix'] for v in row if v]
    assert min(kept) >= maximum * 0.5
    assert abs(data['totalLongsSum'] + data['totalShortsSum'] - sum(data['liqByPrice'])) < 1e-3


def config_of(html):
    return json.loads(re.search(r'<script id="chart-config" type="application/json">(.*?)</script>', html, re.S)[1])


def test_canvas_document_embeds_branding(project_with_logo, payload):
    html = rendering.canvas_document(payload, title='Meu título', prepared_for='Cliente X', logo='assets/other.svg')
    cfg = config_of(html)
    assert cfg['title'] == 'Meu título' and cfg['brand']['preparedFor'] == 'Cliente X'
    assert cfg['brand']['copyright'] == BRAND['copyright'] and cfg['brand']['source'] == 'Alphractal.'
    assert cfg['brand']['logo'].startswith('data:image/svg+xml;base64,')
    assert cfg['fileStem'] == 'liquidation-levels-btc-2y-6h'
    assert 'drawBranding' in html and 'BRAND_LAYOUT' in html


def test_canvas_document_defaults(project, payload):
    cfg = config_of(rendering.canvas_document(payload, demo=True))
    assert cfg['title'] == 'Bitcoin: Liquidation Levels (2 years)'
    assert cfg['brand']['preparedFor'] == '' and cfg['brand']['logo'] is None  # neutral defaults
    assert cfg['fileStem'].startswith('liquidation-levels-demo-')
    assert 'Conecte sua chave' in rendering.canvas_document()
