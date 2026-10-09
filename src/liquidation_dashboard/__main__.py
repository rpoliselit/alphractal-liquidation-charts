"""Entry point: ``alphractal-liquidation-charts [--port 8056] [--no-browser] [--demo]`` (or ``python -m liquidation_dashboard``)."""
from __future__ import annotations

import argparse
import logging
import threading
import webbrowser

from . import __version__
from .app import create_app


def main(argv=None):
    parser = argparse.ArgumentParser(prog='alphractal-liquidation-charts', description=__doc__)
    parser.add_argument('--port', type=int, default=8056)
    parser.add_argument('--no-browser', action='store_true', help='do not open the browser automatically')
    parser.add_argument('--demo', action='store_true', help='start with synthetic data (no API calls)')
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error('Escolha uma porta entre 1024 e 65535.')
    app = create_app(args.demo, args.port)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    print(f'Liquidation Levels: http://127.0.0.1:{args.port} · Ctrl+C para encerrar.', flush=True)
    if not args.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    app.run(host='127.0.0.1', port=args.port, debug=False)


if __name__ == '__main__':
    main()
