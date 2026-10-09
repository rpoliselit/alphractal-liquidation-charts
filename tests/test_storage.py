import copy

import pytest

from liquidation_dashboard import storage
from liquidation_dashboard.api import APIError


def test_db_key_and_path(project):
    assert storage.db_key('BTC', '6h', '2y') == 'btc_6h_2y_all'
    assert storage.db_path('btc', '6h', '2y', 'binance').name == 'btc_6h_2y_binance.parquet'
    assert storage.db_path('btc', '6h', '2y').parent == project / 'liquidation_db'


def test_parquet_roundtrip_keeps_values_and_gaps(project, payload):
    original = copy.deepcopy(payload)
    original['z'][3][7] = None
    path = storage.db_save(original, storage.db_path('btc', '6h', '2y'))
    assert path.is_file() and not path.with_suffix('.parquet.tmp').exists()
    back, meta = storage.db_load(path)
    for key in ('x', 'y', 'z', 'df', 'topTraderLsr', 'asset', 'timeframe', 'lookback'):
        assert back[key] == original[key]
    assert meta['levels'] == len(original['y']) and 'saved_at' in meta


def test_db_entries_and_options(project, payload):
    assert storage.db_entries() == []
    storage.db_save(payload, storage.db_path('btc', '6h', '2y'))
    other = dict(payload, lookback='4y', timeframe='12h', scope='exchange', exchange='binance')
    storage.db_save(other, storage.db_path('btc', '12h', '4y', 'binance'))
    (project / 'liquidation_db' / 'junk.parquet').write_bytes(b'not parquet')
    entries = storage.db_entries()
    assert [(e['timeframe'], e['lookback'], e['exchange']) for e in entries] == [('12h', '4y', 'binance'), ('6h', '2y', 'all')]
    options, selected, exchanges, count = storage.db_series_options('btc', api_series=[('1h', '7d')])
    assert [o['label'] for o in options] == ['7d · 1h', '2y · 6h · local', '4y · 12h · local']
    assert selected == '6h|2y' and count == 2
    assert [e['value'] for e in exchanges] == ['all', 'binance']


def test_db_load_rejects_corrupt_file(project):
    bad = project / 'liquidation_db' / 'x.parquet'
    bad.parent.mkdir()
    bad.write_bytes(b'garbage')
    with pytest.raises(APIError):
        storage.db_load(bad)


def test_save_export_png_svg_and_validation(project):
    png = storage.save_export('png', 'data:image/png;base64,' + 'iVBORw0KGgo=', 'liquidation-levels-btc-2y-6h')
    svg = storage.save_export('svg', '<svg xmlns="http://www.w3.org/2000/svg"/>', 'Weird Name!!')
    assert png.parent == project / 'liquidation_exports' and png.suffix == '.png'
    assert svg.name.startswith('weird-name-') and svg.read_text().startswith('<svg')
    for kind, content in [('png', 'data:image/jpeg;base64,xx'), ('png', 'data:image/png;base64,***'), ('svg', 'hello'), ('pdf', 'x'), ('png', '')]:
        with pytest.raises(ValueError):
            storage.save_export(kind, content)


def test_exports_never_overwrite(project, monkeypatch):
    first = storage.save_export('svg', '<svg/>', 'same')
    second = storage.save_export('svg', '<svg/>', 'same')
    html = storage.save_html_export('<!doctype html>', 'same')
    assert first != second and first.read_text() == second.read_text()
    assert html.suffix == '.html' and html.parent == first.parent


def test_catalog_cache_roundtrip_and_options(project, payload):
    assert storage.catalog_load() == {'assets': [], 'per_asset': {}, 'saved_at': None}
    storage.catalog_save(['eth', 'btc'], 'btc', [('6h', '2y'), ('12h', '4y')], ['all', 'binance'])
    storage.catalog_save(None, 'eth', [('1h', '7d')], [])
    cache = storage.catalog_load()
    assert cache['assets'] == ['btc', 'eth'] and cache['per_asset']['btc']['series'] == [('6h', '2y'), ('12h', '4y')]
    assert cache['per_asset']['eth']['series'] == [('1h', '7d')] and cache['saved_at']
    storage.db_save(payload, storage.db_path('btc', '6h', '2y'))
    options, selected, exchanges, count = storage.asset_options('btc')
    assert [o['label'] for o in options] == ['2y · 6h · local', '4y · 12h'] and selected == '6h|2y'
    assert [e['value'] for e in exchanges] == ['all', 'binance'] and count == 1
    assert 'btc' in storage.known_assets() and 'sol' in storage.known_assets()
    assert storage.asset_label('btc') == 'BTC · Bitcoin' and storage.asset_label('zzz') == 'ZZZ'
    (project / 'liquidation_db' / 'catalog.json').write_text('{broken', encoding='utf-8')
    assert storage.catalog_load()['assets'] == []
