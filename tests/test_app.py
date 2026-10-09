import pytest

from liquidation_dashboard.app import create_app
from liquidation_dashboard.storage import db_path, db_save


@pytest.fixture
def client(project_with_logo):
    app = create_app(demo=True, port=8099)
    app.server.config['TESTING'] = True
    return app.server.test_client()


def test_export_endpoint_writes_to_exports_folder(client, project_with_logo):
    headers = {'Host': '127.0.0.1:8099', 'Origin': 'http://127.0.0.1:8099'}
    response = client.post('/export', json={'kind': 'svg', 'content': '<svg/>', 'stem': 'test'}, headers=headers)
    assert response.status_code == 200
    assert response.get_json()['path'].startswith(str(project_with_logo / 'liquidation_exports'))
    response = client.post('/export', json={'kind': 'png', 'content': 'nope'}, headers=headers)
    assert response.status_code == 400


def test_requests_from_other_hosts_are_refused(client):
    assert client.get('/', headers={'Host': 'evil.example:8099'}).status_code == 403
    assert client.post('/export', json={}, headers={'Host': '127.0.0.1:8099', 'Origin': 'http://evil.example'}).status_code == 403
    assert client.get('/', headers={'Host': '127.0.0.1:8099'}).status_code == 200


def test_layout_is_prefilled_from_local_database(project_with_logo, payload):
    db_save(payload, db_path('btc', '6h', '2y'))
    app = create_app(demo=False, port=8099)
    layout = app.layout().to_plotly_json()
    text = str(layout)
    assert "'2y · 6h · local'" in text and "'value': 'btc'" in text
    assert 'assets/client_logo.svg' in text   # logo offered in the dropdown, not pre-selected
    assert "'BTC · Bitcoin'" in text and "'ETH · Ethereum'" in text   # built-in assets are offered before connecting
    assert 'Nenhum catálogo em cache' in text
