"""Shared fixtures: every test runs against a temporary project folder."""
from __future__ import annotations

import pytest

from liquidation_dashboard import config
from liquidation_dashboard.api import validate_payload
from liquidation_dashboard.rendering import demo_payload

LOGO_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 120"><rect width="400" height="120" fill="#f26b1d"/></svg>'


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Point the package at an empty project folder."""
    monkeypatch.setattr(config, 'PROJECT_DIR', tmp_path)
    monkeypatch.setattr(config, 'KEY_FILE', tmp_path / 'src' / 'liquidation_dashboard' / 'api_key.py')
    return tmp_path


@pytest.fixture
def project_with_logo(project):
    (project / 'assets').mkdir()
    (project / 'assets' / 'client_logo.svg').write_text(LOGO_SVG, encoding='utf-8')
    (project / 'assets' / 'other.svg').write_text(LOGO_SVG, encoding='utf-8')
    return project


@pytest.fixture(scope='session')
def payload():
    """A validated synthetic payload (same generator the --demo flag uses)."""
    return validate_payload(demo_payload())
