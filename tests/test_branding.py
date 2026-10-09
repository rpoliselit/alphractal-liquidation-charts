import base64

from liquidation_dashboard import branding, config


def test_no_logos_in_empty_project(project):
    assert branding.logo_choices() == []
    assert branding.default_logo() == ''
    assert branding.brand_logo_uri() is None


def test_logo_discovery_without_a_configured_default(project_with_logo):
    assert branding.logo_choices() == ['assets/client_logo.svg', 'assets/other.svg']
    assert branding.default_logo() == ''          # nothing pre-selected unless BRAND['logo_file'] is set
    assert branding.brand_logo_uri() is None


def test_configured_default_logo(project_with_logo, monkeypatch):
    monkeypatch.setitem(config.BRAND, 'logo_file', 'client_logo.svg')
    assert branding.default_logo() == 'assets/client_logo.svg'
    (project_with_logo / 'client_logo.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
    assert branding.logo_choices()[-1] == 'client_logo.svg'
    monkeypatch.setitem(config.BRAND, 'logo_file', 'missing.svg')
    assert branding.default_logo() == ''


def test_uri_adds_dimensions_and_rejects_unlisted(project_with_logo):
    uri = branding.brand_logo_uri('assets/other.svg')
    svg = base64.b64decode(uri.split(',', 1)[1]).decode()
    assert 'width="400"' in svg and 'height="120"' in svg
    assert branding.brand_logo_uri('../etc/passwd') is None
    assert branding.brand_logo_uri('') is None
