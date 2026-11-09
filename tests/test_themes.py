import json
import re
from dataclasses import fields

import pytest

from liquidation_dashboard import frontend, rendering
from liquidation_dashboard.app import create_app
from liquidation_dashboard.themes import DEFAULT_THEME, THEMES, Theme, get_theme, theme_options


def config_of(html):
    return json.loads(re.search(r'<script id="chart-config" type="application/json">(.*?)</script>', html, re.S)[1])


def test_three_themes_with_dark_default():
    assert list(THEMES) == ['alphractal_dark', 'alphractal_light', 'classic']
    assert DEFAULT_THEME == 'alphractal_dark'
    assert get_theme().name == 'alphractal_dark'
    assert [o['value'] for o in theme_options()] == list(THEMES)


def test_legacy_values_and_unknown_names():
    assert get_theme('dark').name == 'alphractal_dark'
    assert get_theme('light').name == 'alphractal_light'
    with pytest.raises(ValueError, match='Unknown theme'):
        get_theme('neon')


def test_every_token_used_by_the_renderer_exists():
    """The JavaScript reads ``t.<token>`` and ``THEME.<token>``; each must be a Theme field."""
    javascript = frontend.CANVAS_RENDERER + frontend.CANVAS_CONTROLLER
    used = set(re.findall(r'\b(?:t|THEME)\.([a-z_]+)\b', javascript))
    assert used, 'no theme tokens found'
    assert used <= {f.name for f in fields(Theme)}
    assert 'isDark' not in javascript and 'TEXT_DARK' not in javascript


@pytest.mark.parametrize('name', list(THEMES))
def test_document_carries_the_theme(project, payload, name):
    cfg = config_of(rendering.canvas_document(payload, theme=name))
    assert cfg['themeName'] == name
    assert cfg['theme'] == THEMES[name].to_config()
    assert cfg['logo'] == frontend.LOGOS[THEMES[name].logo]


def test_default_document_uses_dark_theme(project, payload):
    cfg = config_of(rendering.canvas_document(payload))
    assert cfg['themeName'] == 'alphractal_dark' and cfg['theme']['background'] == '#0F1729'


def test_export_backgrounds_follow_printable_plot():
    # Alphractal themes export with their background (white text needs it); classic stays transparent.
    assert THEMES['alphractal_dark'].export_background and THEMES['alphractal_light'].export_background
    assert not THEMES['classic'].export_background


def find_component(node, component_id):
    """Depth-first search of a Dash component tree for a component id."""
    if isinstance(node, (list, tuple)):
        return next((found for child in node if (found := find_component(child, component_id)) is not None), None)
    if getattr(node, 'id', None) == component_id:
        return node
    children = getattr(node, 'children', None)
    return find_component(children, component_id) if children is not None else None


def test_theme_dropdown_defaults_to_alphractal_dark(project):
    dropdown = find_component(create_app(demo=False, port=8099).layout(), 'theme')
    assert dropdown.value == 'alphractal_dark'
    assert [o['label'] for o in dropdown.options] == ['Alphractal Dark', 'Alphractal Light', 'Classic']
