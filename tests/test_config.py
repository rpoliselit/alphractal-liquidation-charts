from liquidation_dashboard import config


def test_chart_title_defaults_and_names():
    assert config.chart_title() == 'Bitcoin: Liquidation Levels (2 years)'
    assert config.chart_title({'asset': 'eth', 'lookback': '4y'}) == 'Ethereum: Liquidation Levels (4 years)'
    assert config.chart_title({'asset': 'xyz', 'lookback': '9d'}) == 'XYZ: Liquidation Levels (9d)'


def test_preferred_series_prefers_default_then_longest():
    assert config.preferred_series([('1h', '7d'), ('6h', '2y'), ('12h', '4y')]) == ('6h', '2y')
    assert config.preferred_series([('1h', '7d'), ('12h', '4y')]) == ('12h', '4y')
    assert config.preferred_series([]) is None


def test_api_key_file_roundtrip(project):
    assert config.load_api_key() == ''
    assert config.save_api_key('  abc-123 ') is True
    assert config.KEY_FILE.is_file() and config.KEY_FILE.parent.name == 'liquidation_dashboard'
    assert config.load_api_key() == 'abc-123'
    assert config.save_api_key('abc-123') is False      # unchanged: nothing rewritten
    assert config.save_api_key('') is False
    assert config.save_api_key("we'ird\"key") is True   # quotes survive repr()
    assert config.load_api_key() == "we'ird\"key"
    config.forget_api_key()
    assert not config.KEY_FILE.exists() and config.load_api_key() == ''
    config.forget_api_key()  # idempotent


def test_load_api_key_tolerates_broken_files(project):
    config.KEY_FILE.parent.mkdir(parents=True)
    config.KEY_FILE.write_text('alphractal_key = 42\n', encoding='utf-8')
    assert config.load_api_key() == ''
    config.KEY_FILE.write_text('this is not python (\n', encoding='utf-8')
    assert config.load_api_key() == ''


def test_folders_follow_project_dir(project):
    assert config.db_dir() == project / 'liquidation_db'
    assert config.export_dir() == project / 'liquidation_exports'
