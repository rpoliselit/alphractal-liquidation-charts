import copy
import json

import pytest

from liquidation_dashboard import api
from liquidation_dashboard.api import APIError


def test_duration_and_identifier():
    assert api.duration('6h') == 6 * 3600
    assert api.duration('2y') == 2 * 365 * 86400
    assert api.duration('abc') == 0 and api.duration(None) == 0
    assert api.identifier('btc') and api.identifier('binance-futures')
    assert not api.identifier('BTC') and not api.identifier('') and not api.identifier(3)


def test_timestamp_normalises_to_utc():
    assert api.timestamp('2026-01-01T00:00:00Z').isoformat() == '2026-01-01T00:00:00+00:00'
    assert api.timestamp('2026-01-01T03:00:00+03:00').hour == 0
    with pytest.raises(APIError):
        api.timestamp(123)


def test_catalog_choices_sorted_by_lookback_then_timeframe():
    body = {'assets': ['eth', 'btc', 'BAD!'], 'exchanges': ['binance', 'all'],
            'series': [{'timeframe': '12h', 'lookback': '4y'}, {'timeframe': '6h', 'lookback': '2y'}, {'timeframe': '1h', 'lookback': '7d'}, {'bogus': 1}]}
    assets, series, exchanges = api.catalog_choices(body)
    assert assets == ['btc', 'eth']
    assert series == [('1h', '7d'), ('6h', '2y'), ('12h', '4y')]
    assert exchanges == ['all', 'binance']
    with pytest.raises(APIError):
        api.catalog_choices({'assets': 'nope'})


def test_validate_payload_roundtrip(payload):
    again = api.validate_payload(copy.deepcopy(payload))
    assert again['x'] == payload['x'] and again['z'] == payload['z'] and again['asset'] == 'btc'


@pytest.mark.parametrize('mutate, message', [
    (lambda p: p['z'].pop(), 'Dimensões'),
    (lambda p: p['z'][0].__setitem__(0, -1), 'negativo'),
    (lambda p: p['df'][0].__setitem__('high', 1), 'inconsistente'),
    (lambda p: p['x'].__setitem__(1, p['x'][0]), 'fora de ordem'),
])
def test_validate_payload_rejects_bad_data(payload, mutate, message):
    broken = copy.deepcopy(payload)
    mutate(broken)
    with pytest.raises(APIError, match=message):
        api.validate_payload(broken)


class FakeResponse:
    def __init__(self, status, body=b'{}'):
        self.status_code, self._body = status, body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def iter_content(self, _):
        yield self._body


def test_api_get_success_and_errors(monkeypatch):
    calls = []

    def fake_get(url, params, headers, **kwargs):
        calls.append((url, params, headers['X-Api-Key']))
        return FakeResponse(200, json.dumps({'data': {'assets': ['btc'], 'series': [], 'exchanges': []}}).encode())

    monkeypatch.setattr(api.requests, 'get', fake_get)
    body = api.api_get('catalog', ' key ', {'asset': 'btc'})
    assert body['assets'] == ['btc']
    assert calls == [(api.API_BASE + '/liquidation_levels/catalog', {'asset': 'btc'}, 'key')]

    monkeypatch.setattr(api.requests, 'get', lambda *a, **k: FakeResponse(401))
    with pytest.raises(APIError, match='401'):
        api.api_get('heatmap', 'key')
    monkeypatch.setattr(api.requests, 'get', lambda *a, **k: FakeResponse(200, b'not json'))
    with pytest.raises(APIError, match='JSON'):
        api.api_get('heatmap', 'key')
    with pytest.raises(APIError):
        api.api_get('other', 'key')
    with pytest.raises(APIError):
        api.api_get('catalog', '')


def test_api_routes_are_the_official_ones(monkeypatch):
    """The HTTP path is part of the Alphractal API contract and must not follow the package name."""
    seen = []
    monkeypatch.setattr(api.requests, 'get', lambda url, **k: seen.append(url) or FakeResponse(200, b'{}'))
    api.api_get('catalog', 'key')
    api.api_get('heatmap', 'key', {'asset': 'btc'})
    assert seen == ['https://api.alphractal.com/liquidation_levels/catalog', 'https://api.alphractal.com/liquidation_levels/heatmap']
