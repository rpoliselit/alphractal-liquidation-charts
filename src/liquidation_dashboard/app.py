"""Dash application: layout, callbacks and the local export endpoint."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

import numpy as np
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from flask import abort, request, send_file

from .api import APIError, api_get, catalog_choices, duration, identifier, timestamp, validate_payload
from .branding import default_logo, logo_choices
from .config import BRAND, DEFAULT_SERIES, chart_title, db_dir, forget_api_key, load_api_key, preferred_series, save_api_key
from .frontend import PALETTES
from .rendering import canvas_document, demo_payload, export_stem, grid_metrics
from .storage import asset_label, asset_options, catalog_load, catalog_save, db_entries, db_load, db_path, db_save, db_series_options, known_assets, save_export, save_html_export


CSS = '''
*{box-sizing:border-box}body{margin:0;background:#090e16;color:#dce6f2;font:14px system-ui,sans-serif}
.shell{max-width:1600px;margin:auto;padding:28px}.eyebrow{color:#b9e968;letter-spacing:2px;font-size:11px;font-weight:700}
h1{font-size:30px;letter-spacing:-1px;margin:8px 0}h2{font-size:17px;margin:0 0 12px}.muted{color:#9bacc2;line-height:1.65}
.top{display:flex;justify-content:space-between;align-items:center;gap:16px}.tag{border:1px solid #324158;border-radius:30px;padding:8px 14px;white-space:nowrap}
.panel{background:#101925;border:1px solid #253246;border-radius:14px;padding:20px;margin:20px 0}.controls{display:grid;grid-template-columns:2fr 2fr 1.4fr auto;gap:14px;align-items:end}
.keyrow{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}.keyrow input{flex:1;min-width:220px}
input,button{font:inherit;border-radius:7px;border:1px solid #3b4c66;padding:11px;background:#0c131e;color:#dce6f2}button{cursor:pointer;font-weight:600}button:hover{border-color:#b9e968}button:disabled{opacity:.4;cursor:wait}.primary{background:#b9e968;color:#101925;border-color:#b9e968}
label{display:block;font-size:12px;color:#b0bfd1;margin-bottom:7px}.row{display:flex;gap:18px;align-items:center;flex-wrap:wrap}.status{white-space:pre-wrap;color:#b0bfd1;line-height:1.65;margin-top:14px}.visuals{display:grid;grid-template-columns:1fr 1.1fr 1.7fr auto;gap:20px;align-items:center}
.Select-control,.Select-menu-outer{background:#101925!important;color:#dce6f2!important;border-color:#3b4c66!important}.Select-value-label,.Select-placeholder{color:#dce6f2!important}.Select-menu-outer{z-index:50!important}.Select-option{background:#101925!important;color:#dce6f2!important}.Select-option.is-focused{background:#26374b!important}a{color:#b9e968}.banner{color:#ffcc75;font-weight:600}.foot{font-size:12px;color:#91a3ba;line-height:1.7}#export-status{overflow-wrap:anywhere}
.dash-dropdown,.dash-dropdown-content,.dash-dropdown-search,.dash-dropdown-search-container,.dash-options-list,.dash-input-container{background:#101925!important;color:#dce6f2!important;border-color:#3b4c66!important}.dash-dropdown-value,.dash-dropdown-value-item,.dash-dropdown-placeholder,.dash-options-list-option,.dash-options-list-option-text,.dash-slider-mark{color:#dce6f2!important}.dash-options-list-option:hover{background:#26374b!important}.dash-slider-track{background:#34465d!important}.dash-slider-range,.dash-slider-thumb{background:#b9e968!important}#key{background:#0c131e!important;color:#dce6f2!important;min-height:42px}.controls{margin-top:16px}
.shell{max-width:1700px;padding:18px}.panel{padding:14px;margin:12px 0;background:#0b0f19;border-color:#242b39;border-radius:10px}.top h1{font-size:23px;letter-spacing:-.5px}.eyebrow{color:#96a4b9}.primary{background:#0d9276;color:white;border-color:#0d9276}.keyrow{margin:10px 0}.connection summary{cursor:pointer;color:#aab5c7;font-size:12px}.toolbar{display:grid;grid-template-columns:1fr 1.3fr 1fr 1fr .85fr 1fr .8fr auto;gap:10px;align-items:end;padding-bottom:10px;border-bottom:1px solid #232b3a}.toolbar input{width:100%;padding:7px}.threshold-pair{display:flex;gap:4px}.chartcard{padding:12px 8px}.status{font-size:11px;margin-top:5px}.foot{margin:6px 4px}.toolbar label{font-size:10px;color:#8b8fa3}.toolbar button{font-size:11px;padding:8px}.tag{font-size:10px;padding:6px 10px}iframe{display:block;width:100%;height:770px;border:0}.footeractions{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px}.footeractions button{padding:7px;font-size:11px}@media(max-width:1000px){.toolbar{grid-template-columns:repeat(4,1fr)}}
@media(max-width:900px){.shell{padding:14px}.controls,.visuals{grid-template-columns:1fr 1fr}.top{display:block}h1{font-size:26px}}
@media(max-width:600px){.toolbar{grid-template-columns:repeat(2,minmax(0,1fr))}.toolbar>div{min-width:0}.footeractions{flex-wrap:wrap}.keyrow input{min-width:0;width:100%}}
iframe{height:1040px}
.branding{grid-template-columns:2fr 1fr 1fr!important;margin-top:10px}.branding input{width:100%}
'''


def create_app(demo=False, port=8056):
    app = Dash(__name__, title='Alphractal · Liquidation Levels', update_title='Carregando…', assets_folder='__no_assets__')
    app.index_string = app.index_string.replace('</head>', '<style>' + CSS + '</style></head>')
    initial = {'payload': validate_payload(demo_payload()), 'demo': True} if demo else None
    def serve_layout():
        """Built on every page load so the dropdowns reflect the current cache, database and saved key."""
        # Dropdowns are filled without any API call: cached catalog + local database + built-in asset list.
        local = db_entries()
        catalog = catalog_load()
        assets = known_assets()
        first_asset = 'btc' if 'btc' in assets else assets[0]
        local_series, local_selected, local_exchanges, _ = asset_options(first_asset)
        if catalog['assets']:
            db_note = (f"Catálogo em cache ({catalog['saved_at']}) · {len(local)} série(s) no banco local em {db_dir().name}/. "
                       'Selecione e clique em Carregar; "Conectar" atualiza o catálogo pela API; "Baixar da API" sobrescreve a série.')
        else:
            db_note = ('Nenhum catálogo em cache. Informe a chave e clique em "Conectar / atualizar catálogo" para descobrir '
                       'as séries e exchanges válidas (2 chamadas); depois "Carregar" ou "Baixar da API".')
        return html.Div(className='shell', children=[
            html.Div(className='top', children=[html.Div([html.Div('ALPHRACTAL', className='eyebrow'), html.H1(chart_title(), id='chart-title')]), html.Div('● API · LOCAL · UTC', className='tag')]),
            html.Details(className='panel connection', open=True, children=[html.Summary('API Key · conectar / configurar'),
                html.Div(className='keyrow', children=[dcc.Input(id='key', type='password', value=load_api_key(), placeholder='Cole sua API Key da Alphractal', autoComplete='off', persistence=False),
                     html.Button('Conectar / atualizar catálogo', id='connect', className='primary'), html.Button('Esquecer chave', id='clear-key', title='Limpa o campo e apaga api_key.py'), html.Button('Ver demonstração', id='demo')]),
                html.Div(('Chave carregada do arquivo local. ' if load_api_key() else 'Nenhuma chave salva: ela será guardada em api_key.py após a primeira chamada bem-sucedida. ') + 'Os controles visuais reutilizam os dados carregados.', className='foot'),
                html.Div(id='catalog-status', className='status', children=db_note)]),
            html.Div(className='panel chartcard', children=[html.Div(className='toolbar', children=[
                html.Div([html.Label('Cryptocurrency'), dcc.Dropdown(id='asset', options=[{'label': asset_label(a), 'value': a} for a in assets], value=first_asset, placeholder='Asset', clearable=False)]),
                html.Div([html.Label('Lookback'), dcc.Dropdown(id='series', options=local_series, value=local_selected, placeholder='Conecte para listar', clearable=False)]),
                html.Div([html.Label('Exchange'), dcc.Dropdown(id='exchange', options=local_exchanges, value='all', clearable=False)]),
                html.Div([html.Label('Color Scale'), dcc.Dropdown(id='palette', options=[{'label':v.title(),'value':v} for v in PALETTES], value='inferno', clearable=False)]),
                html.Div([html.Label('Smoothing'), dcc.Dropdown(id='smoothing', options=[{'label':'True','value':'best'},{'label':'False','value':'false'}],value='false',clearable=False)]),
                html.Div([html.Label('Threshold · Min / Max %'), html.Div(className='threshold-pair',children=[dcc.Input(id='threshold',type='number',min=0,max=100,value=0,debounce=True),dcc.Input(id='threshold-max',type='number',min=0,max=100,value=100,debounce=True)])]),
                html.Div([html.Label('Theme'),dcc.Dropdown(id='theme',options=[{'label':'Dark','value':'dark'},{'label':'Light','value':'light'}],value='dark',clearable=False)]),
                html.Button('↻ Carregar', id='load', className='primary', title='Usa o banco local se a série existir; senão baixa da API e grava'),
                html.Button('⇣ Baixar da API', id='download', title='Sempre consulta a API e sobrescreve a série no banco local')]),
                html.Div(className='toolbar branding', children=[
                    html.Div([html.Label('Título (vazio = automático)'), dcc.Input(id='title-text', type='text', value='', placeholder=chart_title(), debounce=True, style={'width': '100%'})]),
                    html.Div([html.Label('Prepared for (vazio = omitido)'), dcc.Input(id='prepared-for', type='text', value=BRAND['prepared_for'], placeholder='Nome do cliente', debounce=True, style={'width': '100%'})]),
                    html.Div([html.Label(f"Logo ({BRAND['assets_dir']}/*.svg)"), dcc.Dropdown(id='logo', options=[{'label': 'Sem logo', 'value': ''}] + [{'label': c, 'value': c} for c in logo_choices()], value=default_logo(), clearable=False)])]),
                html.Div(id='load-status', className='status'), html.Div(id='data-note', className='status'),
                dcc.Loading(html.Iframe(id='chart',srcDoc=canvas_document(),sandbox='allow-scripts allow-same-origin allow-downloads',allow='fullscreen',title='Liquidation Levels Canvas'), color='#0d9276'),
                html.Div(className='footeractions',children=[html.Span('Threshold filtra o mapa, a distribuição e os totais, como no frontend.',className='foot'),html.Button('Salvar gráfico HTML', id='save')]),
                html.Div(id='export-status', className='status'),
                html.P('A distribuição usa a última coluna do mapa. Abaixo/acima são somas por posição relativa ao preço, não identificação de contas ou alavancagem. A API já aplica o tratamento do leitor; os totais representam os valores retornados. Datas sem candle ou com células ausentes não recebem totais estimados.', className='foot')]),
            dcc.Store(id='catalog-state', storage_type='memory', data={'assets': assets, 'source': 'cache'}), dcc.Store(id='payload', data=initial, storage_type='memory')])


    app.layout = serve_layout

    allowed_hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
    @app.server.before_request
    def local_only():
        if request.host not in allowed_hosts:
            abort(403)
        if request.method == 'POST' and request.headers.get('Origin') not in {f'http://{h}' for h in allowed_hosts}:
            abort(403)

    @app.server.after_request
    def security_headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @app.callback(Output('key', 'value'), Input('clear-key', 'n_clicks'), prevent_initial_call=True)
    def clear_key(_):
        forget_api_key()
        return ''

    @app.callback(Output('asset', 'options'), Output('asset', 'value'), Output('series', 'options'), Output('series', 'value'),
                  Output('exchange', 'options'), Output('exchange', 'value'), Output('catalog-status', 'children'), Output('catalog-state', 'data'),
                  Input('connect', 'n_clicks'), Input('asset', 'value'), State('key', 'value'), State('catalog-state', 'data'),
                  prevent_initial_call=True, running=[(Output('connect', 'disabled'), True, False), (Output('load', 'disabled'), True, False)])
    def connect(_, asset, key, state):
        """"Conectar" refreshes the catalog from the API; switching asset uses the cache (API only when missing)."""
        state = state or {'assets': known_assets(), 'source': 'cache'}
        try:
            if ctx.triggered_id == 'connect':
                assets, _, _ = catalog_choices(api_get('catalog', key))
                if not assets:
                    raise APIError('O catálogo não retornou assets disponíveis.')
                asset = asset if asset in assets else ('btc' if 'btc' in assets else assets[0])
                _, series, exchanges = catalog_choices(api_get('catalog', key, {'asset': asset}))
                saved = save_api_key(key)  # only a key that worked is persisted
                catalog_save(assets, asset, series, exchanges)
                source = 'api'
            else:
                assets = state['assets']
                cached = catalog_load()['per_asset'].get(asset)
                if cached:
                    series, exchanges, source = cached['series'], cached['exchanges'], 'cache'
                else:
                    # First time this asset is selected: fetch its series once and cache them.
                    _, series, exchanges = catalog_choices(api_get('catalog', key, {'asset': asset}))
                    save_api_key(key)
                    catalog_save(None, asset, series, exchanges)
                    source = 'api'
                saved = False
            options, selected, exchange_options, count = db_series_options(asset, series, exchanges)
            preferred = preferred_series(series)
            selection_note = 'Padrão: 2 anos · 6 horas.' if preferred == DEFAULT_SERIES else '2 anos · 6 horas indisponível para este asset; selecionada a janela mais longa disponível.'
            origin = 'catálogo atualizado pela API' if source == 'api' else 'catálogo em cache'
            note = (f'{asset.upper()}: {len(series)} séries · {len(exchange_options) - 1} exchanges ({origin}; {count} já no banco local, marcadas com "local"). '
                    f'{selection_note}' + (' Chave salva em api_key.py.' if saved else '')) if series else f'Nenhuma série disponível para {asset.upper()} no catálogo.'
            asset_opts = [{'label': asset_label(a), 'value': a} for a in sorted(set(assets) | {asset})]
            return asset_opts, asset, options, selected, exchange_options, 'all', note, {'assets': sorted(set(assets) | {asset}), 'source': source}
        except APIError as exc:
            # Keep whatever the dropdowns already show; only report the problem.
            return no_update, no_update, no_update, no_update, no_update, no_update, f'Falha ao consultar o catálogo: {exc}', no_update

    @app.callback(Output('payload', 'data'), Output('load-status', 'children'), Output('series', 'options', allow_duplicate=True),
                  Input('load', 'n_clicks'), Input('download', 'n_clicks'), Input('demo', 'n_clicks'), State('key', 'value'), State('asset', 'value'),
                  State('series', 'value'), State('exchange', 'value'), State('series', 'options'), prevent_initial_call=True,
                  running=[(Output('load', 'disabled'), True, False), (Output('download', 'disabled'), True, False), (Output('demo', 'disabled'), True, False)])
    def load(_, __, ___, key, asset, series, exchange, series_options):
        if ctx.triggered_id == 'demo':
            return {'payload': validate_payload(demo_payload()), 'demo': True}, 'Demonstração carregada. Nenhuma chamada à API.', no_update
        try:
            if not identifier(asset) or not series or len(series.split('|')) != 2:
                raise APIError('Conecte e selecione um asset e uma série do catálogo.')
            tf, lookback = series.split('|')
            if not duration(tf) or not duration(lookback):
                raise APIError('Série inválida.')
            params = {'asset': asset, 'timeframe': tf, 'lookback': lookback, 'scope': 'all'}
            if exchange and exchange != 'all':
                if not identifier(exchange):
                    raise APIError('Exchange inválida.')
                params.update(scope='exchange', exchange=exchange)
            path = db_path(asset, tf, lookback, params.get('exchange'))
            # "Carregar" prefers the local file; "Baixar da API" always fetches and overwrites it.
            if ctx.triggered_id == 'load' and path.is_file():
                payload, meta = db_load(path)
                for field in ('asset', 'timeframe', 'lookback'):
                    if payload.get(field) != params[field]:
                        raise APIError(f'O arquivo {path.name} não corresponde à série selecionada. Use "Baixar da API" para regravar.')
                return {'payload': payload, 'demo': False}, f"Carregado do banco local ({path.name}, gravado em {meta.get('saved_at', '?')}). Nenhuma chamada à API; use \"Baixar da API\" para atualizar.", no_update
            body = api_get('heatmap', key, params)
            save_api_key(key)
            payload = validate_payload(body)
            for field in ('asset', 'timeframe', 'lookback', 'scope', 'exchange'):
                if field in params:
                    if field in payload and payload[field] != params[field]:
                        raise APIError('A resposta não corresponde ao asset/período solicitado. O gráfico foi limpo.')
                    payload[field] = params[field]
            saved = db_save(payload, path)
            # Mark the series as "local" in the dropdown without another catalog request.
            options = [{**o, 'label': o['label'] if o['label'].endswith(' · local') or o['value'] != series else o['label'] + ' · local'} for o in (series_options or [])]
            action = 'sobrescrito' if ctx.triggered_id == 'download' else 'criado'
            return {'payload': payload, 'demo': False}, f'Baixado da API em {datetime.now(timezone.utc):%d/%m/%Y %H:%M:%S} UTC · banco local {action}: {saved}', options
        except APIError as exc:
            return None, str(exc), no_update

    @app.callback(Output('chart', 'srcDoc'), Output('data-note', 'children'), Output('chart-title', 'children'), Input('payload', 'data'), Input('palette', 'value'), Input('smoothing', 'value'), Input('threshold', 'value'), Input('threshold-max','value'), Input('theme','value'), Input('title-text', 'value'), Input('prepared-for', 'value'), Input('logo', 'value'))
    def render(data, palette, smoothing, threshold, threshold_max, theme, title, prepared_for, logo):
        if not data:
            return canvas_document(), '', (title or '').strip() or chart_title()
        payload = data['payload']
        try:
            document = canvas_document(payload, palette, smoothing, threshold or 0, 100 if threshold_max is None else threshold_max, theme, data['demo'], title, prepared_for, logo)
        except APIError as exc:
            return canvas_document(), str(exc), chart_title()
        raw, _, price, _, _ = grid_metrics(payload)
        missing = int((~np.isfinite(price)).sum())
        source = 'DEMONSTRAÇÃO · DADOS SINTÉTICOS' if data['demo'] else 'DADOS DA API'
        age = (datetime.now(timezone.utc)-timestamp(payload['x'][-1])).total_seconds()/3600
        note = f"{source} · {len(payload['x']):,} datas × {len(payload['y']):,} níveis · última data: {payload['x'][-1]}\nFonte do preço: {payload.get('priceSource', 'não informada')} · escopo: {payload.get('scope', 'all')} / {payload.get('exchange', 'todas')}"
        if missing:
            note += f'\n{missing} datas sem candle correspondente; totais abaixo/acima ficam ausentes nessas datas.'
        if np.isnan(raw).any():
            note += '\nCélulas ausentes na resposta: preservadas como lacunas, sem preenchimento.'
        if not data['demo'] and age > max(24, duration(payload.get('timeframe')) / 3600 * 3):
            note += f'\nAtenção: último ponto há {age:.1f} horas; confirme a atualização da série.'
        return document, html.Div(note, className='banner' if data['demo'] else ''), (title or '').strip() or chart_title(payload)

    @app.server.post('/export')
    def export_file():
        """Receive a PNG (data URI) or SVG (text) from the canvas and write it to liquidation_exports/."""
        body = request.get_json(silent=True) or {}
        try:
            target = save_export(body.get('kind'), body.get('content'), body.get('stem'))
        except ValueError as exc:
            return {'error': str(exc)}, 400
        except OSError:
            return {'error': 'Sem permissão para gravar na pasta de exports.'}, 500
        return {'path': str(target)}

    exports = {}

    @app.server.get('/saved/<token>')
    def saved(token):
        if token not in exports:
            abort(404)
        return send_file(exports[token], as_attachment=True)

    @app.callback(Output('export-status', 'children'), Input('save', 'n_clicks'), State('payload', 'data'),
                  State('palette', 'value'), State('smoothing', 'value'), State('threshold', 'value'), State('threshold-max', 'value'),
                  State('theme', 'value'), State('title-text', 'value'), State('prepared-for', 'value'), State('logo', 'value'), prevent_initial_call=True)
    def save(_, data, palette, smoothing, threshold, threshold_max, theme, title, prepared_for, logo):
        if not data:
            return 'Carregue um gráfico antes de salvar.'
        try:
            document = canvas_document(data['payload'], palette, smoothing, threshold or 0, 100 if threshold_max is None else threshold_max,
                                       theme, data['demo'], title, prepared_for, logo)
            target = save_html_export(document, export_stem(data['payload'], data['demo']))
            token = secrets.token_hex(12)
            exports[token] = target
            return [html.A('Baixar gráfico HTML interativo', href='/saved/' + token), html.Div('Salvo em: ' + str(target))]
        except APIError as exc:
            return str(exc)
        except OSError:
            return 'Sem permissão para salvar na pasta de exports. Mova o projeto para uma pasta gravável.'

    return app
