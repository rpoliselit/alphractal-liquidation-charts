# Alphractal Liquidation Levels — local app

A local Dash application that fetches Bitcoin (or any supported asset) liquidation-level heatmaps
from the Alphractal API, renders them with the same canvas routines as Alphractal's front end, and
exports branded PNG/SVG/HTML charts in the layout of `printable_plot.plot_alphractal`
(title, `Source:`, `Prepared for:`, `Copyright:` and an optional client logo in the footer).
Out of the box the footer carries no client name and no logo; both are chosen per chart in the UI.

Series are cached locally in Parquet so the API is only called when you ask for fresh data.

## Project layout

```
alphractal-liquidation-charts/     # project root: open this folder in your editor / version it with git
├── src/
│   └── liquidation_dashboard/     # the application code (import name: liquidation_dashboard)
│       ├── __main__.py            # CLI entry point
│       ├── app.py                 # Dash layout, callbacks, local /export endpoint
│       ├── api.py                 # Alphractal API client + response validation
│       ├── storage.py             # Parquet database and export files
│       ├── rendering.py           # data preparation and the chart HTML document
│       ├── frontend.py            # embedded JavaScript (canvas renderer, SVG backend, controller)
│       ├── branding.py            # logo discovery / embedding
│       ├── config.py              # paths, brand texts, constants
│       └── api_key.py             # alphractal_key = "..."  — git-ignored, written by the app
├── tests/                         # pytest suite
├── assets/                        # your logos (*.svg)          — git-ignored
├── liquidation_db/                # Parquet cache (one file per series) + catalog.json — git-ignored, created on demand
├── liquidation_exports/           # PNG / SVG / HTML exports           — git-ignored, created on demand
├── pyproject.toml                 # makes the project installable and defines the CLI command
├── requirements.txt / requirements-dev.txt
├── pytest.ini
└── README.md
```

Only `src/` holds code. Everything the app reads or writes (`assets/`, `liquidation_db/`, `liquidation_exports/`)
stays in the project root, wherever you launch the command from.

## Setup

Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .         # installs dependencies and the `alphractal-liquidation-charts` command
```

`-e` (editable) links the venv to `src/`, so code changes take effect without reinstalling.

Put your logos in `assets/` (any `*.svg`). The dropdown lists every file in that folder plus "Sem logo"
(no logo), which is the default.

### API key

No manual step is needed. Paste the key in the app the first time; after the first **successful** API
call it is written to `src/liquidation_dashboard/api_key.py` (`alphractal_key = "..."`, owner-only
permissions) and pre-filled on every later start. A key that fails (401/403) is never stored.
**Esquecer chave** clears the field and deletes the file. You can also create the file by hand.

## Run

```bash
alphractal-liquidation-charts                 # opens http://127.0.0.1:8056
alphractal-liquidation-charts --port 8057 --no-browser
alphractal-liquidation-charts --demo          # synthetic data, no API calls
python -m liquidation_dashboard               # equivalent to the command above
```

The server only accepts connections from `127.0.0.1` / `localhost`.

## Workflow

On start-up the dropdowns are filled without any API call: assets come from the cached catalog, the local
database and a built-in list (BTC, ETH, SOL, …); the lookback/timeframe and exchange lists come from the
cached catalog (`liquidation_db/catalog.json`) and the local database. Until the catalog has been fetched
once, the lookback list is empty, because only the API knows which `(timeframe, lookback)` pairs exist.

1. **Conectar / atualizar catálogo** — fetches the catalog from the API (2 calls), caches it and fills the
   lookback and exchange dropdowns for the selected asset. Needed once; afterwards switching asset uses the
   cache (an asset never seen before is fetched once and added to the cache). Series already stored locally
   are marked `· local`.
2. **↻ Carregar** — loads the selected series from `liquidation_db/` when it exists; otherwise fetches it
   from the API once and stores it.
3. **⇣ Baixar da API** — always calls the API and overwrites the local Parquet file for that series.
4. Title, *Prepared for* and logo are set in the fields below the toolbar; they apply to the
   on-screen chart and to every export. An empty *Prepared for* omits that field; with no logo
   selected nothing is drawn in the logo box.
5. **PNG ↓ / SVG ↓ / Salvar gráfico HTML** — written to `liquidation_exports/` with a timestamped name
   (`liquidation-levels-btc-2y-6h-YYYYMMDD-HHMMSS.png`). Existing files are never overwritten.
   PNG and SVG exports have a transparent background, like `plot_alphractal` with `background_alpha=0`.

Any API failure (missing or wrong key, network) is reported in the status line under the key field and
never clears what the dropdowns already show.

### API calls per series

| Action | Calls |
|---|---|
| Conectar (catalog, then series for one asset) | 2 × `GET /liquidation_levels/catalog` |
| Carregar with a local file | 0 |
| Carregar without a local file / Baixar da API | 1 × `GET /liquidation_levels/heatmap` |

## Branding geometry

The footer follows `plot_alphractal` on a 16:9 figure (figure fractions, bottom-left origin):

| Element | Position | Font |
|---|---|---|
| Title | `x=0.075`, top at `0.955` | 23 pt STIXGeneral bold, `#241E18` |
| Subtitle | `x=0.075`, top at `0.895` | 10 pt, `#887767` |
| `Source: Alphractal.` | `x=0.075`, bottom at `0.085` | 11 pt DejaVu Sans, bold label |
| `Prepared for: … \| Copyright: …` | `x=0.075`, bottom at `0.025` | 12 pt DejaVu Sans, bold labels |
| Logo | `logo_box = (0.83, 0.025, 0.14, 0.065)` | aspect-fit |

Point sizes are scaled from the Matplotlib figure width (1152 pt), so proportions are kept at any canvas width.
In the dark theme the text colours are lightened for contrast; the light theme uses the exact colours above.
For a pixel-exact title font install *STIX Two Text* on your system; otherwise the browser falls back to Times.

Brand texts and folder names live in `src/liquidation_dashboard/config.py` (`BRAND`). To pre-fill a client
for a fixed deployment set `BRAND['prepared_for']` and `BRAND['logo_file']` there; the UI fields still
override them per chart.

## Local database format

`liquidation_db/<asset>_<timeframe>_<lookback>_<exchange>.parquet`

* columns: `date` (ISO-8601 UTC string) and `L0 … Ln`, one `float64` column per price level
  (missing cells stay `null`);
* Parquet schema metadata key `alphractal`: JSON with `asset`, `timeframe`, `lookback`, `scope`,
  `exchange`, `version`, `priceSource`, the `y` price levels, the `df` candles, `topTraderLsr` and `saved_at`.

Values are stored exactly as returned by the API and revalidated when loaded.

## Tests

```bash
python -m pip install -e ".[dev]"     # or: python -m pip install -r requirements-dev.txt
python -m pytest
```

`pytest.ini` adds `src/` to the import path, so the suite also runs without installing the package.

The suite covers the API client (with a fake HTTP layer), payload validation, the Parquet round trip,
export file handling, branding/logo embedding, chart-document generation and the Flask export endpoint.
No test touches the network, your real project folders or your saved API key.

## Freezing dependencies

To pin the exact versions of your environment:

```bash
python -m pip freeze > requirements.lock.txt
```
