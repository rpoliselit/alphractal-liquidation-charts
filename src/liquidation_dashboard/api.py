"""Alphractal API client and response validation.

Only the two official read-only routes are used (catalog and heatmap). Responses are validated
structurally and kept unchanged: no interpolation, resampling or gap filling."""
from __future__ import annotations

import json
import math
import re
import threading
from datetime import datetime, timezone

import requests

from .config import API_BASE, MAX_BYTES, MAX_CELLS

GATE = threading.BoundedSemaphore(1)  # one API request at a time


class APIError(ValueError):
    pass


def api_get(resource, key, params=None):
    """Only the two official read-only routes; no redirects or automatic retries."""
    if resource not in {'catalog', 'heatmap'}:
        raise APIError('Recurso não permitido.')
    if not isinstance(key, str) or not key.strip():
        raise APIError('Informe sua API Key para consultar a API.')
    if not GATE.acquire(blocking=False):
        raise APIError('Já existe uma consulta em andamento. Aguarde terminar.')
    try:
        with requests.get(API_BASE + '/liquidation_levels/' + resource,
                          params=params or {}, headers={'X-Api-Key': key.strip(), 'Accept': 'application/json'},
                          timeout=(10, 90), allow_redirects=False, stream=True) as response:
            if response.status_code != 200:
                reasons = {204: 'Nenhum dado retornado.', 400: 'Parâmetros rejeitados; confira a combinação no catálogo.',
                           401: 'API Key inválida ou expirada.', 402: 'Créditos insuficientes.',
                           403: 'Acesso não permitido; confira o plano/tier da sua chave.',
                           404: 'Endpoint ou série não encontrado.', 429: 'Limite de chamadas atingido; aguarde antes de repetir.'}
                raise APIError(f'HTTP {response.status_code}: ' + reasons.get(response.status_code, 'Resposta inesperada do serviço. Tente novamente mais tarde.'))
            chunks, size = [], 0
            for chunk in response.iter_content(1024 * 1024):
                size += len(chunk)
                if size > MAX_BYTES:
                    raise APIError('Resposta acima de 64 MB. Escolha uma janela menor; nenhum dado foi truncado.')
                chunks.append(chunk)
            try:
                def reject_constant(value):
                    raise ValueError('Non-finite number')
                body = json.loads(b''.join(chunks).decode('utf-8-sig'), parse_constant=reject_constant)
            except (ValueError, UnicodeError):
                raise APIError('HTTP 200, mas a resposta não é JSON válido. Nenhum conteúdo ou chave foi gravado.') from None
            if not isinstance(body, dict):
                raise APIError('A API retornou um formato inesperado: era esperado um objeto JSON.')
            # Whitelisting in the catalog and payload validators excludes unrelated fields.
            body = body.get('data', body) if isinstance(body.get('data'), dict) else body
            for field in ('asset', 'timeframe', 'lookback', 'scope', 'exchange', 'version', 'priceSource'):
                if isinstance(body.get(field), str):
                    body[field] = body[field].replace(key.strip(), '[CHAVE REMOVIDA]')
            return body
    except requests.Timeout:
        raise APIError('Tempo limite de 90 segundos. Escolha uma janela menor ou tente novamente.') from None
    except requests.RequestException:
        raise APIError('Não foi possível conectar à API. Confira a rede e tente novamente.') from None
    finally:
        GATE.release()


def duration(value):
    match = re.fullmatch(r'(\d+)(m|h|d|w|y)', str(value))
    return int(match[1]) * {'m': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31536000}[match[2]] if match else 0


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,99}', value) is not None


def catalog_choices(body):
    if not isinstance(body, dict):
        raise APIError('Catálogo inválido.')
    if any(not isinstance(body.get(field, []), list) for field in ('assets', 'series', 'exchanges')):
        raise APIError('Listas inválidas no catálogo.')
    assets = sorted({v for v in body.get('assets', []) if identifier(v)})
    series = sorted({(r.get('timeframe'), r.get('lookback')) for r in body.get('series', [])
                     if isinstance(r, dict) and duration(r.get('timeframe')) and duration(r.get('lookback'))},
                    key=lambda pair: (duration(pair[1]), duration(pair[0])))
    exchanges = sorted({v for v in body.get('exchanges', []) if identifier(v)})
    return assets, series, exchanges


def timestamp(value):
    if not isinstance(value, str):
        raise APIError('Timestamp inválido na resposta.')
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:
        raise APIError('Timestamp inválido na resposta.') from None


def numeric(value, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (positive and value <= 0):
        raise APIError('Valor numérico inválido na resposta.')
    return float(value)


def validate_payload(body):
    """Keep the response grid unchanged; dates, shape and amounts must be coherent."""
    if not isinstance(body, dict):
        raise APIError('Resposta inválida: esperado um objeto.')
    x, y, z = (body.get(k) for k in ('x', 'y', 'z'))
    if not all(isinstance(v, list) and v for v in (x, y, z)):
        raise APIError('A série está vazia ou faltam os campos x, y e z.')
    if len(x) * len(y) > MAX_CELLS:
        raise APIError('Mapa acima de 4 milhões de células. Escolha uma janela menor; nenhum dado foi reduzido.')
    dates = [timestamp(v) for v in x]
    prices = [numeric(v, positive=True) for v in y]
    if any(a >= b for a, b in zip(dates, dates[1:])) or any(a >= b for a, b in zip(prices, prices[1:])):
        raise APIError('Datas ou níveis de preço duplicados/fora de ordem na resposta.')
    if len(z) != len(y) or any(not isinstance(row, list) or len(row) != len(x) for row in z):
        raise APIError('Dimensões inválidas: z deve ter uma linha por preço e uma coluna por data.')
    clean_z = []
    for row in z:
        clean_row = [None if v is None else numeric(v) for v in row]
        if any(v is not None and v < 0 for v in clean_row):
            raise APIError('Volume de liquidação negativo na resposta.')
        clean_z.append(clean_row)
    candles, seen = [], set()
    for candle in body.get('df') or []:
        if not isinstance(candle, dict):
            raise APIError('Candle inválido.')
        dt = timestamp(candle.get('date'))
        if dt in seen:
            raise APIError('Candles com datas duplicadas.')
        seen.add(dt)
        values = {k: numeric(candle.get(k), positive=True) for k in ('open', 'high', 'low', 'close')}
        if values['low'] > min(values['open'], values['close']) or values['high'] < max(values['open'], values['close']):
            raise APIError('Candle com máxima/mínima inconsistente.')
        candles.append({'date': dt.isoformat(), **values})
    ratio = []
    for point in body.get('topTraderLsr') or []:
        if not isinstance(point, dict):
            raise APIError('Série Long/Short inválida.')
        value = numeric(point.get('value'))
        if value < 0:
            raise APIError('Razão Long/Short negativa.')
        ratio.append({'date': timestamp(point.get('date')).isoformat(), 'value': value})
    return {'x': [d.isoformat() for d in dates], 'y': prices, 'z': clean_z,
            'df': sorted(candles, key=lambda c: c['date']), 'topTraderLsr': sorted(ratio, key=lambda p: p['date']),
            **{k: str(body[k])[:200] for k in ('asset', 'timeframe', 'lookback', 'scope', 'exchange', 'version', 'priceSource') if body.get(k) is not None}}
