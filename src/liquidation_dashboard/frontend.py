"""Browser-side code: FrontEnd_V2 canvas drawing routines, SVG backend, view controls and the controller script.

The JavaScript is embedded as Python strings so the app ships as a plain package with no Node/React toolchain."""
from __future__ import annotations

# Official FrontEnd_V2 logos, embedded so no asset files are required.
LOGOS = {"dark":"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTY1IiBoZWlnaHQ9IjI0NyIgdmlld0JveD0iMCAwIDk2NSAyNDciIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+DQo8cGF0aCBkPSJNMCAyMTIuOTQ2TDU2LjY0NDggMjUuOTU4OUM2OC42MDEgMzIuMjMxIDc3LjgxMzIgNTMuMzk5MyA3NS40NjExIDcyLjAxOTZMNDYuNDUyNyAxNjMuMzU3QzIzLjEyODMgMTY4LjI1NyAxOC4wMzIzIDIwNy44NSAwIDIxMi45NDZaIiBmaWxsPSJ1cmwoI3BhaW50MF9saW5lYXJfMV8yKSIvPg0KPHBhdGggZD0iTTM1Ljg2ODUgMjAzLjU4MkMyOC4yMjQ0IDIxNi41MTggNi4yMDY3NiAyMTMuOTA1IDAgMjEzLjU3OEM0LjExNjA2IDE5MC42MTUgMTEuMTMzMyAxNjYuMDQ1IDM1Ljg2ODUgMTQxLjk1NEM1MC4zNjYzIDEyNy44MzQgNjkuNjc3NyAxMTkuNDQ4IDc3LjgxMzIgMTE5LjQ1MkM4Mi44MTEzIDExOS40NTUgODYuNjQxNiAxMjAuMzg3IDg4Ljk4NTMgMTI0LjMxN0M5Mi41MTM0IDEzMC4yMzIgOTYuNjI5NCAxNDEuMDEzIDk4Ljc4NTUgMTQ3LjA4OUM4NC4wODUzIDE1Mi4wMiA3NS40NjExIDE1NC43MzMgNjIuNzIwOSAxNjYuMTQ1QzQ2LjI4NDUgMTgwLjg2OSA0My41MTI3IDE5MC42NDYgMzUuODY4NSAyMDMuNTgyWiIgZmlsbD0idXJsKCNwYWludDFfbGluZWFyXzFfMikiLz4NCjxwYXRoIGQ9Ik0yMDQuMDU2IDcyLjE2NjJDMTg3Ljk2OCAxNy4yMzczIDEyNC4yNjYgMjYuNTQ2OSA5My40OTMzIDI2LjU0NjlDOTguMDAxNCAzNi41MjQ5IDEwMy4yOTMgNDguMTA3MyAxMDcuOTk4IDUxLjQzOTNDMTE3LjYwMiA1Ny41MTU0IDEyOC4zODIgNTMuMDE1MSAxNDUuMjM4IDU2LjMzOTRDMTc5LjkzMSA2My4xODEzIDE3OS4xNDcgOTEuMjI3OSAxNTkuOTM4IDk5LjY1NkMxNTIuMzc3IDEwMi45NzQgMTQzLjI3OCAxMDMuNDA5IDEzNi40MTggMTA2LjcxMkMxMzEuMTI2IDEwOS4yNiAxMzAuMDY2IDExMi4xMiAxMzAuNzM0IDExNS43MjhDMTMxLjg1OSAxMjEuODA0IDEzNC44NSAxMjguMjcyIDEzOC43NyAxMzguMDczQzE2Ny45NzQgMTMzLjM2OSAyMTguMzc4IDEyMS4wNjUgMjA0LjA1NiA3Mi4xNjYyWiIgZmlsbD0idXJsKCNwYWludDJfbGluZWFyXzFfMikiLz4NCjxwYXRoIGQ9Ik0xMTUuMzAxIDE4MS45MzRDMTIzLjk0NyAyMDcuNDA5IDE0OS4zNTkgMjE0Ljc4NiAxNjEuOTMgMjEzLjQ4MkMxNDEuNjE2IDE1NS40NjUgOTkuNzEwNSA0My44ODE2IDkyLjM5OTUgMzQuMjM3NkM4NC44MTk5IDI0LjIzOTQgNjYuNjkyOCAyNS45MTM1IDU2LjUwNzIgMjUuOTEwN0M3MC43MjIyIDY0Ljc1NTEgMTA0LjQ4IDE1MC4wNDkgMTE1LjMwMSAxODEuOTM0WiIgZmlsbD0idXJsKCNwYWludDNfbGluZWFyXzFfMikiLz4NCjxwYXRoIGQ9Ik0yMjcuMjM4IDE4MkwyNjcuNjY1IDc1LjczMjlIMjgzLjUwNkwzMjMuNzY5IDE4MkgzMDkuOTA4TDI5OC42ODcgMTUyLjc5M0gyNTIuNDg0TDI0MS4yNjQgMTgySDIyNy4yMzhaTTI1NC43OTUgMTQyLjA2N0gyOTYuMjEyTDI3NS40MjEgODcuNDQ4N0wyNTQuNzk1IDE0Mi4wNjdaTTM1Mi4xMTYgMTgzLjY1QzM0Ni44MzYgMTgzLjY1IDM0Mi42NTYgMTgyLjI3NSAzMzkuNTc1IDE3OS41MjVDMzM2LjYwNSAxNzYuNjY1IDMzNS4xMiAxNzEuODc5IDMzNS4xMiAxNjUuMTY5VjcwLjc4MjZIMzQ4LjY1MVYxNjMuNjg0QzM0OC42NTEgMTY2Ljk4NCAzNDkuMjAxIDE2OS4yMzkgMzUwLjMwMSAxNzAuNDQ5QzM1MS40MDEgMTcxLjY1OSAzNTMuMTA2IDE3Mi4yNjQgMzU1LjQxNiAxNzIuMjY0QzM1Ny45NDcgMTcyLjI2NCAzNjAuNDIyIDE3MS45MzQgMzYyLjg0MiAxNzEuMjc0VjE4MkMzNjEuMDgyIDE4Mi42NiAzNTkuMzIyIDE4My4xIDM1Ny41NjIgMTgzLjMyQzM1NS44MDEgMTgzLjU0IDM1My45ODYgMTgzLjY1IDM1Mi4xMTYgMTgzLjY1Wk0zNzguNDY4IDIxNy42NDJWMTAzLjc4NUgzOTAuMDE4TDM5MS4wMDkgMTEyLjAzNUMzOTQuNjM5IDEwOC42MjUgMzk4LjU5OSAxMDYuMTUgNDAyLjg4OSAxMDQuNjFDNDA3LjI5IDEwMi45NiA0MTIuNDA1IDEwMi4xMzUgNDE4LjIzNSAxMDIuMTM1QzQyOS4yMzYgMTAyLjEzNSA0MzcuODcyIDEwNS4yMTUgNDQ0LjE0MiAxMTEuMzc1QzQ1MC40MTIgMTE3LjQyNiA0NTMuNTQ4IDEyNy41NDYgNDUzLjU0OCAxNDEuNzM3QzQ1My41NDggMTU1LjgxOCA0NTAuNDEyIDE2Ni4zMjQgNDQ0LjE0MiAxNzMuMjU0QzQzNy44NzIgMTgwLjE4NSA0MjkuMTgxIDE4My42NSA0MTguMDcgMTgzLjY1QzQwNy44NCAxODMuNjUgMzk5LjE0OSAxODEuMTc1IDM5MS45OTkgMTc2LjIyNVYyMTcuNjQySDM3OC40NjhaTTQxNC40NCAxNzIuNzU5QzQyMy4yNDEgMTcyLjc1OSA0MjkuNjc2IDE3MC4yODQgNDMzLjc0NiAxNjUuMzM0QzQzNy45MjcgMTYwLjI3NCA0NDAuMDE3IDE1Mi40MDggNDQwLjAxNyAxNDEuNzM3QzQ0MC4wMTcgMTMxLjUwNyA0MzguMDkyIDEyNC4xOTEgNDM0LjI0MSAxMTkuNzkxQzQzMC4zOTEgMTE1LjI4MSA0MjMuOTAxIDExMy4wMjUgNDE0Ljc3IDExMy4wMjVDNDEwLjI2IDExMy4wMjUgNDA2LjA4IDExMy43OTUgNDAyLjIyOSAxMTUuMzM2QzM5OC4zNzkgMTE2Ljg3NiAzOTQuOTY5IDExOS4yNDEgMzkxLjk5OSAxMjIuNDMxVjE2NS4wMDRDMzk0Ljc0OSAxNjcuNDI0IDM5Ny45OTQgMTY5LjM0OSA0MDEuNzM0IDE3MC43NzlDNDA1LjQ3NCAxNzIuMDk5IDQwOS43MSAxNzIuNzU5IDQxNC40NCAxNzIuNzU5Wk00NzMuMzgxIDE4MlY3MC43ODI2SDQ4Ni45MTJWMTEyLjJDNDkwLjU0MiAxMDkuMjMgNDk0Ljc3OCAxMDYuODEgNDk5LjYxOCAxMDQuOTRDNTA0LjU2OCAxMDMuMDcgNTEwLjI4OSAxMDIuMTM1IDUxNi43NzkgMTAyLjEzNUM1MjYuMjQgMTAyLjEzNSA1MzMuMzM1IDEwNC40NDUgNTM4LjA2NiAxMDkuMDY1QzU0Mi43OTYgMTEzLjY4NSA1NDUuMTYxIDEyMC45NDYgNTQ1LjE2MSAxMzAuODQ3VjE4Mkg1MzEuNjNWMTMxLjM0MkM1MzEuNjMgMTI0LjUyMSA1MzAuMDkgMTE5Ljc5MSA1MjcuMDEgMTE3LjE1MUM1MjQuMDQgMTE0LjQgNTE5LjA4OSAxMTMuMDI1IDUxMi4xNTkgMTEzLjAyNUM1MDcuNzU5IDExMy4wMjUgNTAzLjE5MyAxMTQuMDE1IDQ5OC40NjMgMTE1Ljk5NkM0OTMuODQzIDExNy44NjYgNDg5Ljk5MiAxMjAuMzQxIDQ4Ni45MTIgMTIzLjQyMVYxODJINDczLjM4MVpNNTY3LjQ4OSAxODJWMTAzLjc4NUg1NzkuN0w1ODAuNjkgMTEzLjY4NUM1ODQuNTQgMTExLjE1NSA1ODkuMDUxIDEwOC44NDUgNTk0LjIyMSAxMDYuNzU1QzU5OS41MDEgMTA0LjY2NSA2MDQuNjcyIDEwMy4xMjUgNjA5LjczMiAxMDIuMTM1VjExMi42OTVDNjA2LjY1MiAxMTMuMzU1IDYwMy4yOTYgMTE0LjI5IDU5OS42NjYgMTE1LjUwMUM1OTYuMDM2IDExNi42MDEgNTkyLjU3MSAxMTcuODY2IDU4OS4yNzEgMTE5LjI5NkM1ODUuOTcgMTIwLjcyNiA1ODMuMjIgMTIyLjIxMSA1ODEuMDIgMTIzLjc1MVYxODJINTY3LjQ4OVpNNjQzLjc5NSAxODMuNjVDNjM4Ljg0NSAxODMuNjUgNjM0LjI3OSAxODIuNzcgNjMwLjA5OSAxODEuMDFDNjI1LjkxOSAxNzkuMjUgNjIyLjU2NCAxNzYuNjY1IDYyMC4wMzMgMTczLjI1NEM2MTcuNTAzIDE2OS43MzQgNjE2LjIzOCAxNjUuMzM0IDYxNi4yMzggMTYwLjA1NEM2MTYuMjM4IDE1Mi45MDMgNjE4LjYwMyAxNDcuMDczIDYyMy4zMzQgMTQyLjU2MkM2MjguMDY0IDEzNy45NDIgNjM1Ljc2NSAxMzUuNjMyIDY0Ni40MzUgMTM1LjYzMkg2NzMuNjYyVjEzMC44NDdDNjczLjY2MiAxMjYuNTU2IDY3My4wNTcgMTIzLjE0NiA2NzEuODQ3IDEyMC42MTZDNjcwLjc0NyAxMTguMDg2IDY2OC42MDIgMTE2LjI3MSA2NjUuNDEyIDExNS4xNzFDNjYyLjIyMSAxMTQuMDcgNjU3LjU0NiAxMTMuNTIgNjUxLjM4NiAxMTMuNTJDNjQ2LjY1NSAxMTMuNTIgNjQyLjA5IDExMy45MDUgNjM3LjY5IDExNC42NzZDNjMzLjI4OSAxMTUuNDQ2IDYyOS4xNjQgMTE2LjQ5MSA2MjUuMzE0IDExNy44MTFWMTA2LjU5QzYyOC44MzQgMTA1LjI3IDYzMi45NTkgMTA0LjIyNSA2MzcuNjkgMTAzLjQ1NUM2NDIuNTMgMTAyLjU3NSA2NDcuNyAxMDIuMTM1IDY1My4yMDEgMTAyLjEzNUM2NjQuMzExIDEwMi4xMzUgNjcyLjYxNyAxMDQuMzkgNjc4LjExNyAxMDguOUM2ODMuNzI4IDExMy40MSA2ODYuNTMzIDEyMC43MjYgNjg2LjUzMyAxMzAuODQ3VjE4Mkg2NzUuMTQ3TDY3NC4xNTcgMTczLjA4OUM2NzAuNzQ3IDE3Ni42MSA2NjYuNjIyIDE3OS4yNSA2NjEuNzgxIDE4MS4wMUM2NTYuOTQxIDE4Mi43NyA2NTAuOTQ2IDE4My42NSA2NDMuNzk1IDE4My42NVpNNjQ3LjI2IDE3Mi41OTRDNjUyLjk4MSAxNzIuNTk0IDY1OC4wNDEgMTcxLjYwNCA2NjIuNDQxIDE2OS42MjRDNjY2Ljg0MiAxNjcuNTM0IDY3MC41ODIgMTY0LjcyOSA2NzMuNjYyIDE2MS4yMDlWMTQ2LjAyOEg2NDYuNzY1QzY0MC42MDUgMTQ2LjAyOCA2MzYuMjA1IDE0Ny4xODMgNjMzLjU2NCAxNDkuNDkzQzYzMC45MjQgMTUxLjgwMyA2MjkuNjA0IDE1NS4zMjMgNjI5LjYwNCAxNjAuMDU0QzYyOS42MDQgMTY0Ljc4NCA2MzEuMTk5IDE2OC4wODQgNjM0LjM4OSAxNjkuOTU0QzYzNy41OCAxNzEuNzE0IDY0MS44NyAxNzIuNTk0IDY0Ny4yNiAxNzIuNTk0Wk03NDUuNzc0IDE4My42NUM3MzIuMTM0IDE4My42NSA3MjIuMDEzIDE4MC4xMyA3MTUuNDEyIDE3My4wODlDNzA4LjgxMiAxNjUuOTM5IDcwNS41MTIgMTU1Ljg3MyA3MDUuNTEyIDE0Mi44OTJDNzA1LjUxMiAxMjkuMTQxIDcwOS4yNTIgMTE4LjkxMSA3MTYuNzMyIDExMi4yQzcyNC4yMTMgMTA1LjQ5IDczNC4yNzkgMTAyLjEzNSA3NDYuOTMgMTAyLjEzNUM3NTIuMSAxMDIuMTM1IDc1Ni4zOSAxMDIuNTIgNzU5LjggMTAzLjI5Qzc2My4yMTEgMTAzLjk1IDc2Ni41MTEgMTA1LjA1IDc2OS43MDEgMTA2LjU5VjExNy4zMTZDNzYzLjc2MSAxMTQuNDU1IDc1Ni45OTUgMTEzLjAyNSA3NDkuNDA1IDExMy4wMjVDNzM5LjcyNCAxMTMuMDI1IDczMi4yNDQgMTE1LjMzNiA3MjYuOTYzIDExOS45NTZDNzIxLjY4MyAxMjQuNDY2IDcxOS4wNDMgMTMyLjExMiA3MTkuMDQzIDE0Mi44OTJDNzE5LjA0MyAxNTMuMjMzIDcyMS4zNTMgMTYwLjgyNCA3MjUuOTczIDE2NS42NjRDNzMwLjU5MyAxNzAuMzk0IDczOC4yMzkgMTcyLjc1OSA3NDguOTEgMTcyLjc1OUM3NTYuNSAxNzIuNzU5IDc2My40ODYgMTcxLjMyOSA3NjkuODY2IDE2OC40NjlWMTc5LjM2Qzc2Ni40NTYgMTgwLjc5IDc2Mi43NzEgMTgxLjgzNSA3NTguODEgMTgyLjQ5NUM3NTQuOTYgMTgzLjI2NSA3NTAuNjE1IDE4My42NSA3NDUuNzc0IDE4My42NVpNODEzLjU4IDE4My42NUM4MDUuODc5IDE4My42NSA4MDAuMDQ5IDE4MS42MTUgNzk2LjA4OSAxNzcuNTQ1Qzc5Mi4yMzggMTczLjM2NCA3OTAuMzEzIDE2Ny41ODkgNzkwLjMxMyAxNjAuMjE5VjExNC41MUg3NzguNDMyVjEwMy43ODVINzkwLjMxM1Y4NC40Nzg1TDgwMy44NDQgODAuMzUzMlYxMDMuNzg1SDgyNS40NjFMODI0LjYzNiAxMTQuNTFIODAzLjg0NFYxNTkuNTU5QzgwMy44NDQgMTY0LjI4OSA4MDQuODg5IDE2Ny42OTkgODA2Ljk3OSAxNjkuNzg5QzgwOS4xNzkgMTcxLjc2OSA4MTIuOTIgMTcyLjc1OSA4MTguMiAxNzIuNzU5QzgyMS4wNiAxNzIuNzU5IDgyNC4xOTYgMTcyLjIwOSA4MjcuNjA2IDE3MS4xMDlWMTgxLjM0QzgyMy41MzUgMTgyLjg4IDgxOC44NiAxODMuNjUgODEzLjU4IDE4My42NVpNODY3LjQ2MiAxODMuNjVDODYyLjUxMiAxODMuNjUgODU3Ljk0NyAxODIuNzcgODUzLjc2NiAxODEuMDFDODQ5LjU4NiAxNzkuMjUgODQ2LjIzMSAxNzYuNjY1IDg0My43MDEgMTczLjI1NEM4NDEuMTcxIDE2OS43MzQgODM5LjkwNSAxNjUuMzM0IDgzOS45MDUgMTYwLjA1NEM4MzkuOTA1IDE1Mi45MDMgODQyLjI3MSAxNDcuMDczIDg0Ny4wMDEgMTQyLjU2MkM4NTEuNzMxIDEzNy45NDIgODU5LjQzMiAxMzUuNjMyIDg3MC4xMDIgMTM1LjYzMkg4OTcuMzI5VjEzMC44NDdDODk3LjMyOSAxMjYuNTU2IDg5Ni43MjQgMTIzLjE0NiA4OTUuNTE0IDEyMC42MTZDODk0LjQxNCAxMTguMDg2IDg5Mi4yNjkgMTE2LjI3MSA4ODkuMDc5IDExNS4xNzFDODg1Ljg4OSAxMTQuMDcgODgxLjIxMyAxMTMuNTIgODc1LjA1MyAxMTMuNTJDODcwLjMyMiAxMTMuNTIgODY1Ljc1NyAxMTMuOTA1IDg2MS4zNTcgMTE0LjY3NkM4NTYuOTU3IDExNS40NDYgODUyLjgzMSAxMTYuNDkxIDg0OC45ODEgMTE3LjgxMVYxMDYuNTlDODUyLjUwMSAxMDUuMjcgODU2LjYyNyAxMDQuMjI1IDg2MS4zNTcgMTAzLjQ1NUM4NjYuMTk3IDEwMi41NzUgODcxLjM2OCAxMDIuMTM1IDg3Ni44NjggMTAyLjEzNUM4ODcuOTc5IDEwMi4xMzUgODk2LjI4NCAxMDQuMzkgOTAxLjc4NSAxMDguOUM5MDcuMzk1IDExMy40MSA5MTAuMiAxMjAuNzI2IDkxMC4yIDEzMC44NDdWMTgySDg5OC44MTRMODk3LjgyNCAxNzMuMDg5Qzg5NC40MTQgMTc2LjYxIDg5MC4yODkgMTc5LjI1IDg4NS40NDggMTgxLjAxQzg4MC42MDggMTgyLjc3IDg3NC42MTMgMTgzLjY1IDg2Ny40NjIgMTgzLjY1Wk04NzAuOTI4IDE3Mi41OTRDODc2LjY0OCAxNzIuNTk0IDg4MS43MDggMTcxLjYwNCA4ODYuMTA5IDE2OS42MjRDODkwLjUwOSAxNjcuNTM0IDg5NC4yNDkgMTY0LjcyOSA4OTcuMzI5IDE2MS4yMDlWMTQ2LjAyOEg4NzAuNDMyQzg2NC4yNzIgMTQ2LjAyOCA4NTkuODcyIDE0Ny4xODMgODU3LjIzMiAxNDkuNDkzQzg1NC41OTEgMTUxLjgwMyA4NTMuMjcxIDE1NS4zMjMgODUzLjI3MSAxNjAuMDU0Qzg1My4yNzEgMTY0Ljc4NCA4NTQuODY2IDE2OC4wODQgODU4LjA1NyAxNjkuOTU0Qzg2MS4yNDcgMTcxLjcxNCA4NjUuNTM3IDE3Mi41OTQgODcwLjkyOCAxNzIuNTk0Wk05NDkuNDc1IDE4My42NUM5NDQuMTk1IDE4My42NSA5NDAuMDE1IDE4Mi4yNzUgOTM2LjkzNSAxNzkuNTI1QzkzMy45NjQgMTc2LjY2NSA5MzIuNDc5IDE3MS44NzkgOTMyLjQ3OSAxNjUuMTY5VjcwLjc4MjZIOTQ2LjAxVjE2My42ODRDOTQ2LjAxIDE2Ni45ODQgOTQ2LjU2IDE2OS4yMzkgOTQ3LjY2IDE3MC40NDlDOTQ4Ljc2IDE3MS42NTkgOTUwLjQ2NSAxNzIuMjY0IDk1Mi43NzYgMTcyLjI2NEM5NTUuMzA2IDE3Mi4yNjQgOTU3Ljc4MSAxNzEuOTM0IDk2MC4yMDEgMTcxLjI3NFYxODJDOTU4LjQ0MSAxODIuNjYgOTU2LjY4MSAxODMuMSA5NTQuOTIxIDE4My4zMkM5NTMuMTYxIDE4My41NCA5NTEuMzQ1IDE4My42NSA5NDkuNDc1IDE4My42NVoiIGZpbGw9IiNFQUVBRUEiLz4NCjxkZWZzPg0KPGxpbmVhckdyYWRpZW50IGlkPSJwYWludDBfbGluZWFyXzFfMiIgeDE9IjM4LjIwMDEiIHkxPSIzNy43MTkxIiB4Mj0iMzguMjAwMSIgeTI9IjE2NS4zMTciIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4NCjxzdG9wIHN0b3AtY29sb3I9IiNFQUVBRUEiIHN0b3Atb3BhY2l0eT0iMC45MTc2NDciLz4NCjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzRFNEU0RSIvPg0KPC9saW5lYXJHcmFkaWVudD4NCjxsaW5lYXJHcmFkaWVudCBpZD0icGFpbnQxX2xpbmVhcl8xXzIiIHgxPSI2MS4zNjU2IiB5MT0iMzcuNTIiIHgyPSI2MS4zNjU2IiB5Mj0iMjE5LjMxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+DQo8c3RvcCBvZmZzZXQ9IjAuNDQ2NjY2IiBzdG9wLWNvbG9yPSIjRUFFQUVBIi8+DQo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM0RTRFNEUiLz4NCjwvbGluZWFyR3JhZGllbnQ+DQo8bGluZWFyR3JhZGllbnQgaWQ9InBhaW50Ml9saW5lYXJfMV8yIiB4MT0iMTUwLjUzOCIgeTE9IjIyLjUyMDEiIHgyPSIxNTAuNTM4IiB5Mj0iMTM1Ljg2NSIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPg0KPHN0b3Agc3RvcC1jb2xvcj0iI0VBRUFFQSIvPg0KPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjNEU0RTRFIi8+DQo8L2xpbmVhckdyYWRpZW50Pg0KPGxpbmVhckdyYWRpZW50IGlkPSJwYWludDNfbGluZWFyXzFfMiIgeDE9IjExNS45MTkiIHkxPSIyNy4zMDQ2IiB4Mj0iMTAyLjYxMSIgeTI9IjIxMC44MTkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4NCjxzdG9wIHN0b3AtY29sb3I9IiM0RTRFNEUiLz4NCjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI0VBRUFFQSIvPg0KPC9saW5lYXJHcmFkaWVudD4NCjwvZGVmcz4NCjwvc3ZnPiA=","light":"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iOTY1IiBoZWlnaHQ9IjI0NyIgdmlld0JveD0iMCAwIDk2NSAyNDciIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+DQo8cGF0aCBkPSJNMCAyMTIuOTQ2TDU2LjY0NDggMjUuOTU4OUM2OC42MDEgMzIuMjMxIDc3LjgxMzIgNTMuMzk5MyA3NS40NjExIDcyLjAxOTZMNDYuNDUyNyAxNjMuMzU3QzIzLjEyODMgMTY4LjI1NyAxOC4wMzIzIDIwNy44NSAwIDIxMi45NDZaIiBmaWxsPSJ1cmwoI3BhaW50MF9saW5lYXJfNF80NCkiLz4NCjxwYXRoIGQ9Ik0zNS44Njg1IDIwMy41ODJDMjguMjI0NCAyMTYuNTE4IDYuMjA2NzYgMjEzLjkwNSAwIDIxMy41NzhDNC4xMTYwNiAxOTAuNjE1IDExLjEzMzMgMTY2LjA0NSAzNS44Njg1IDE0MS45NTRDNTAuMzY2MyAxMjcuODM0IDY5LjY3NzcgMTE5LjQ0OCA3Ny44MTMyIDExOS40NTJDODIuODExMyAxMTkuNDU1IDg2LjY0MTYgMTIwLjM4NyA4OC45ODUzIDEyNC4zMTdDOTIuNTEzNCAxMzAuMjMyIDk2LjYyOTQgMTQxLjAxMyA5OC43ODU1IDE0Ny4wODlDODQuMDg1MyAxNTIuMDIgNzUuNDYxMSAxNTQuNzMzIDYyLjcyMDkgMTY2LjE0NUM0Ni4yODQ1IDE4MC44NjkgNDMuNTEyNyAxOTAuNjQ2IDM1Ljg2ODUgMjAzLjU4MloiIGZpbGw9InVybCgjcGFpbnQxX2xpbmVhcl80XzQ0KSIvPg0KPHBhdGggZD0iTTIwNC4wNTYgNzIuMTY2MkMxODcuOTY4IDE3LjIzNzMgMTI0LjI2NiAyNi41NDY5IDkzLjQ5MzMgMjYuNTQ2OUM5OC4wMDE0IDM2LjUyNDkgMTAzLjI5MyA0OC4xMDczIDEwNy45OTggNTEuNDM5M0MxMTcuNjAyIDU3LjUxNTQgMTI4LjM4MiA1My4wMTUxIDE0NS4yMzggNTYuMzM5NEMxNzkuOTMxIDYzLjE4MTMgMTc5LjE0NyA5MS4yMjc5IDE1OS45MzggOTkuNjU2QzE1Mi4zNzcgMTAyLjk3NCAxNDMuMjc4IDEwMy40MDkgMTM2LjQxOCAxMDYuNzEyQzEzMS4xMjYgMTA5LjI2IDEzMC4wNjYgMTEyLjEyIDEzMC43MzQgMTE1LjcyOEMxMzEuODU5IDEyMS44MDQgMTM0Ljg1IDEyOC4yNzIgMTM4Ljc3IDEzOC4wNzNDMTY3Ljk3NCAxMzMuMzY5IDIxOC4zNzggMTIxLjA2NSAyMDQuMDU2IDcyLjE2NjJaIiBmaWxsPSJ1cmwoI3BhaW50Ml9saW5lYXJfNF80NCkiLz4NCjxwYXRoIGQ9Ik0xMTUuMzAxIDE4MS45MzRDMTIzLjk0NyAyMDcuNDA5IDE0OS4zNTkgMjE0Ljc4NiAxNjEuOTMgMjEzLjQ4MkMxNDEuNjE2IDE1NS40NjUgOTkuNzEwNSA0My44ODE2IDkyLjM5OTUgMzQuMjM3NkM4NC44MTk5IDI0LjIzOTQgNjYuNjkyOCAyNS45MTM1IDU2LjUwNzIgMjUuOTEwN0M3MC43MjIyIDY0Ljc1NTEgMTA0LjQ4IDE1MC4wNDkgMTE1LjMwMSAxODEuOTM0WiIgZmlsbD0idXJsKCNwYWludDNfbGluZWFyXzRfNDQpIi8+DQo8cGF0aCBkPSJNMjI3LjIzOCAxODJMMjY3LjY2NSA3NS43MzI5SDI4My41MDZMMzIzLjc2OSAxODJIMzA5LjkwOEwyOTguNjg3IDE1Mi43OTNIMjUyLjQ4NEwyNDEuMjY0IDE4MkgyMjcuMjM4Wk0yNTQuNzk1IDE0Mi4wNjdIMjk2LjIxMkwyNzUuNDIxIDg3LjQ0ODdMMjU0Ljc5NSAxNDIuMDY3Wk0zNTIuMTE2IDE4My42NUMzNDYuODM2IDE4My42NSAzNDIuNjU2IDE4Mi4yNzUgMzM5LjU3NSAxNzkuNTI1QzMzNi42MDUgMTc2LjY2NSAzMzUuMTIgMTcxLjg3OSAzMzUuMTIgMTY1LjE2OVY3MC43ODI2SDM0OC42NTFWMTYzLjY4NEMzNDguNjUxIDE2Ni45ODQgMzQ5LjIwMSAxNjkuMjM5IDM1MC4zMDEgMTcwLjQ0OUMzNTEuNDAxIDE3MS42NTkgMzUzLjEwNiAxNzIuMjY0IDM1NS40MTYgMTcyLjI2NEMzNTcuOTQ3IDE3Mi4yNjQgMzYwLjQyMiAxNzEuOTM0IDM2Mi44NDIgMTcxLjI3NFYxODJDMzYxLjA4MiAxODIuNjYgMzU5LjMyMiAxODMuMSAzNTcuNTYyIDE4My4zMkMzNTUuODAxIDE4My41NCAzNTMuOTg2IDE4My42NSAzNTIuMTE2IDE4My42NVpNMzc4LjQ2OCAyMTcuNjQyVjEwMy43ODVIMzkwLjAxOEwzOTEuMDA5IDExMi4wMzVDMzk0LjYzOSAxMDguNjI1IDM5OC41OTkgMTA2LjE1IDQwMi44ODkgMTA0LjYxQzQwNy4yOSAxMDIuOTYgNDEyLjQwNSAxMDIuMTM1IDQxOC4yMzUgMTAyLjEzNUM0MjkuMjM2IDEwMi4xMzUgNDM3Ljg3MiAxMDUuMjE1IDQ0NC4xNDIgMTExLjM3NUM0NTAuNDEyIDExNy40MjYgNDUzLjU0OCAxMjcuNTQ2IDQ1My41NDggMTQxLjczN0M0NTMuNTQ4IDE1NS44MTggNDUwLjQxMiAxNjYuMzI0IDQ0NC4xNDIgMTczLjI1NEM0MzcuODcyIDE4MC4xODUgNDI5LjE4MSAxODMuNjUgNDE4LjA3IDE4My42NUM0MDcuODQgMTgzLjY1IDM5OS4xNDkgMTgxLjE3NSAzOTEuOTk5IDE3Ni4yMjVWMjE3LjY0MkgzNzguNDY4Wk00MTQuNDQgMTcyLjc1OUM0MjMuMjQxIDE3Mi43NTkgNDI5LjY3NiAxNzAuMjg0IDQzMy43NDYgMTY1LjMzNEM0MzcuOTI3IDE2MC4yNzQgNDQwLjAxNyAxNTIuNDA4IDQ0MC4wMTcgMTQxLjczN0M0NDAuMDE3IDEzMS41MDcgNDM4LjA5MiAxMjQuMTkxIDQzNC4yNDEgMTE5Ljc5MUM0MzAuMzkxIDExNS4yODEgNDIzLjkwMSAxMTMuMDI1IDQxNC43NyAxMTMuMDI1QzQxMC4yNiAxMTMuMDI1IDQwNi4wOCAxMTMuNzk1IDQwMi4yMjkgMTE1LjMzNkMzOTguMzc5IDExNi44NzYgMzk0Ljk2OSAxMTkuMjQxIDM5MS45OTkgMTIyLjQzMVYxNjUuMDA0QzM5NC43NDkgMTY3LjQyNCAzOTcuOTk0IDE2OS4zNDkgNDAxLjczNCAxNzAuNzc5QzQwNS40NzQgMTcyLjA5OSA0MDkuNzEgMTcyLjc1OSA0MTQuNDQgMTcyLjc1OVpNNDczLjM4MSAxODJWNzAuNzgyNkg0ODYuOTEyVjExMi4yQzQ5MC41NDIgMTA5LjIzIDQ5NC43NzggMTA2LjgxIDQ5OS42MTggMTA0Ljk0QzUwNC41NjggMTAzLjA3IDUxMC4yODkgMTAyLjEzNSA1MTYuNzc5IDEwMi4xMzVDNTI2LjI0IDEwMi4xMzUgNTMzLjMzNSAxMDQuNDQ1IDUzOC4wNjYgMTA5LjA2NUM1NDIuNzk2IDExMy42ODUgNTQ1LjE2MSAxMjAuOTQ2IDU0NS4xNjEgMTMwLjg0N1YxODJINTMxLjYzVjEzMS4zNDJDNTMxLjYzIDEyNC41MjEgNTMwLjA5IDExOS43OTEgNTI3LjAxIDExNy4xNTFDNTI0LjA0IDExNC40IDUxOS4wODkgMTEzLjAyNSA1MTIuMTU5IDExMy4wMjVDNTA3Ljc1OSAxMTMuMDI1IDUwMy4xOTMgMTE0LjAxNSA0OTguNDYzIDExNS45OTZDNDkzLjg0MyAxMTcuODY2IDQ4OS45OTIgMTIwLjM0MSA0ODYuOTEyIDEyMy40MjFWMTgySDQ3My4zODFaTTU2Ny40ODkgMTgyVjEwMy43ODVINTc5LjdMNTgwLjY5IDExMy42ODVDNTg0LjU0IDExMS4xNTUgNTg5LjA1MSAxMDguODQ1IDU5NC4yMjEgMTA2Ljc1NUM1OTkuNTAxIDEwNC42NjUgNjA0LjY3MiAxMDMuMTI1IDYwOS43MzIgMTAyLjEzNVYxMTIuNjk1QzYwNi42NTIgMTEzLjM1NSA2MDMuMjk2IDExNC4yOSA1OTkuNjY2IDExNS41MDFDNTk2LjAzNiAxMTYuNjAxIDU5Mi41NzEgMTE3Ljg2NiA1ODkuMjcxIDExOS4yOTZDNTg1Ljk3IDEyMC43MjYgNTgzLjIyIDEyMi4yMTEgNTgxLjAyIDEyMy43NTFWMTgySDU2Ny40ODlaTTY0My43OTUgMTgzLjY1QzYzOC44NDUgMTgzLjY1IDYzNC4yNzkgMTgyLjc3IDYzMC4wOTkgMTgxLjAxQzYyNS45MTkgMTc5LjI1IDYyMi41NjQgMTc2LjY2NSA2MjAuMDMzIDE3My4yNTRDNjE3LjUwMyAxNjkuNzM0IDYxNi4yMzggMTY1LjMzNCA2MTYuMjM4IDE2MC4wNTRDNjE2LjIzOCAxNTIuOTAzIDYxOC42MDMgMTQ3LjA3MyA2MjMuMzM0IDE0Mi41NjJDNjI4LjA2NCAxMzcuOTQyIDYzNS43NjUgMTM1LjYzMiA2NDYuNDM1IDEzNS42MzJINjczLjY2MlYxMzAuODQ3QzY3My42NjIgMTI2LjU1NiA2NzMuMDU3IDEyMy4xNDYgNjcxLjg0NyAxMjAuNjE2QzY3MC43NDcgMTE4LjA4NiA2NjguNjAyIDExNi4yNzEgNjY1LjQxMiAxMTUuMTcxQzY2Mi4yMjEgMTE0LjA3IDY1Ny41NDYgMTEzLjUyIDY1MS4zODYgMTEzLjUyQzY0Ni42NTUgMTEzLjUyIDY0Mi4wOSAxMTMuOTA1IDYzNy42OSAxMTQuNjc2QzYzMy4yODkgMTE1LjQ0NiA2MjkuMTY0IDExNi40OTEgNjI1LjMxNCAxMTcuODExVjEwNi41OUM2MjguODM0IDEwNS4yNyA2MzIuOTU5IDEwNC4yMjUgNjM3LjY5IDEwMy40NTVDNjQyLjUzIDEwMi41NzUgNjQ3LjcgMTAyLjEzNSA2NTMuMjAxIDEwMi4xMzVDNjY0LjMxMSAxMDIuMTM1IDY3Mi42MTcgMTA0LjM5IDY3OC4xMTcgMTA4LjlDNjgzLjcyOCAxMTMuNDEgNjg2LjUzMyAxMjAuNzI2IDY4Ni41MzMgMTMwLjg0N1YxODJINjc1LjE0N0w2NzQuMTU3IDE3My4wODlDNjcwLjc0NyAxNzYuNjEgNjY2LjYyMiAxNzkuMjUgNjYxLjc4MSAxODEuMDFDNjU2Ljk0MSAxODIuNzcgNjUwLjk0NiAxODMuNjUgNjQzLjc5NSAxODMuNjVaTTY0Ny4yNiAxNzIuNTk0QzY1Mi45ODEgMTcyLjU5NCA2NTguMDQxIDE3MS42MDQgNjYyLjQ0MSAxNjkuNjI0QzY2Ni44NDIgMTY3LjUzNCA2NzAuNTgyIDE2NC43MjkgNjczLjY2MiAxNjEuMjA5VjE0Ni4wMjhINjQ2Ljc2NUM2NDAuNjA1IDE0Ni4wMjggNjM2LjIwNSAxNDcuMTgzIDYzMy41NjQgMTQ5LjQ5M0M2MzAuOTI0IDE1MS44MDMgNjI5LjYwNCAxNTUuMzIzIDYyOS42MDQgMTYwLjA1NEM2MjkuNjA0IDE2NC43ODQgNjMxLjE5OSAxNjguMDg0IDYzNC4zODkgMTY5Ljk1NEM2MzcuNTggMTcxLjcxNCA2NDEuODcgMTcyLjU5NCA2NDcuMjYgMTcyLjU5NFpNNzQ1Ljc3NCAxODMuNjVDNzMyLjEzNCAxODMuNjUgNzIyLjAxMyAxODAuMTMgNzE1LjQxMiAxNzMuMDg5QzcwOC44MTIgMTY1LjkzOSA3MDUuNTEyIDE1NS44NzMgNzA1LjUxMiAxNDIuODkyQzcwNS41MTIgMTI5LjE0MSA3MDkuMjUyIDExOC45MTEgNzE2LjczMiAxMTIuMkM3MjQuMjEzIDEwNS40OSA3MzQuMjc5IDEwMi4xMzUgNzQ2LjkzIDEwMi4xMzVDNzUyLjEgMTAyLjEzNSA3NTYuMzkgMTAyLjUyIDc1OS44IDEwMy4yOUM3NjMuMjExIDEwMy45NSA3NjYuNTExIDEwNS4wNSA3NjkuNzAxIDEwNi41OVYxMTcuMzE2Qzc2My43NjEgMTE0LjQ1NSA3NTYuOTk1IDExMy4wMjUgNzQ5LjQwNSAxMTMuMDI1QzczOS43MjQgMTEzLjAyNSA3MzIuMjQ0IDExNS4zMzYgNzI2Ljk2MyAxMTkuOTU2QzcyMS42ODMgMTI0LjQ2NiA3MTkuMDQzIDEzMi4xMTIgNzE5LjA0MyAxNDIuODkyQzcxOS4wNDMgMTUzLjIzMyA3MjEuMzUzIDE2MC44MjQgNzI1Ljk3MyAxNjUuNjY0QzczMC41OTMgMTcwLjM5NCA3MzguMjM5IDE3Mi43NTkgNzQ4LjkxIDE3Mi43NTlDNzU2LjUgMTcyLjc1OSA3NjMuNDg2IDE3MS4zMjkgNzY5Ljg2NiAxNjguNDY5VjE3OS4zNkM3NjYuNDU2IDE4MC43OSA3NjIuNzcxIDE4MS44MzUgNzU4LjgxIDE4Mi40OTVDNzU0Ljk2IDE4My4yNjUgNzUwLjYxNSAxODMuNjUgNzQ1Ljc3NCAxODMuNjVaTTgxMy41OCAxODMuNjVDODA1Ljg3OSAxODMuNjUgODAwLjA0OSAxODEuNjE1IDc5Ni4wODkgMTc3LjU0NUM3OTIuMjM4IDE3My4zNjQgNzkwLjMxMyAxNjcuNTg5IDc5MC4zMTMgMTYwLjIxOVYxMTQuNTFINzc4LjQzMlYxMDMuNzg1SDc5MC4zMTNWODQuNDc4NUw4MDMuODQ0IDgwLjM1MzJWMTAzLjc4NUg4MjUuNDYxTDgyNC42MzYgMTE0LjUxSDgwMy44NDRWMTU5LjU1OUM4MDMuODQ0IDE2NC4yODkgODA0Ljg4OSAxNjcuNjk5IDgwNi45NzkgMTY5Ljc4OUM4MDkuMTc5IDE3MS43NjkgODEyLjkyIDE3Mi43NTkgODE4LjIgMTcyLjc1OUM4MjEuMDYgMTcyLjc1OSA4MjQuMTk2IDE3Mi4yMDkgODI3LjYwNiAxNzEuMTA5VjE4MS4zNEM4MjMuNTM1IDE4Mi44OCA4MTguODYgMTgzLjY1IDgxMy41OCAxODMuNjVaTTg2Ny40NjIgMTgzLjY1Qzg2Mi41MTIgMTgzLjY1IDg1Ny45NDcgMTgyLjc3IDg1My43NjYgMTgxLjAxQzg0OS41ODYgMTc5LjI1IDg0Ni4yMzEgMTc2LjY2NSA4NDMuNzAxIDE3My4yNTRDODQxLjE3MSAxNjkuNzM0IDgzOS45MDUgMTY1LjMzNCA4MzkuOTA1IDE2MC4wNTRDODM5LjkwNSAxNTIuOTAzIDg0Mi4yNzEgMTQ3LjA3MyA4NDcuMDAxIDE0Mi41NjJDODUxLjczMSAxMzcuOTQyIDg1OS40MzIgMTM1LjYzMiA4NzAuMTAyIDEzNS42MzJIODk3LjMyOVYxMzAuODQ3Qzg5Ny4zMjkgMTI2LjU1NiA4OTYuNzI0IDEyMy4xNDYgODk1LjUxNCAxMjAuNjE2Qzg5NC40MTQgMTE4LjA4NiA4OTIuMjY5IDExNi4yNzEgODg5LjA3OSAxMTUuMTcxQzg4NS44ODkgMTE0LjA3IDg4MS4yMTMgMTEzLjUyIDg3NS4wNTMgMTEzLjUyQzg3MC4zMjIgMTEzLjUyIDg2NS43NTcgMTEzLjkwNSA4NjEuMzU3IDExNC42NzZDODU2Ljk1NyAxMTUuNDQ2IDg1Mi44MzEgMTE2LjQ5MSA4NDguOTgxIDExNy44MTFWMTA2LjU5Qzg1Mi41MDEgMTA1LjI3IDg1Ni42MjcgMTA0LjIyNSA4NjEuMzU3IDEwMy40NTVDODY2LjE5NyAxMDIuNTc1IDg3MS4zNjggMTAyLjEzNSA4NzYuODY4IDEwMi4xMzVDODg3Ljk3OSAxMDIuMTM1IDg5Ni4yODQgMTA0LjM5IDkwMS43ODUgMTA4LjlDOTA3LjM5NSAxMTMuNDEgOTEwLjIgMTIwLjcyNiA5MTAuMiAxMzAuODQ3VjE4Mkg4OTguODE0TDg5Ny44MjQgMTczLjA4OUM4OTQuNDE0IDE3Ni42MSA4OTAuMjg5IDE3OS4yNSA4ODUuNDQ4IDE4MS4wMUM4ODAuNjA4IDE4Mi43NyA4NzQuNjEzIDE4My42NSA4NjcuNDYyIDE4My42NVpNODcwLjkyOCAxNzIuNTk0Qzg3Ni42NDggMTcyLjU5NCA4ODEuNzA4IDE3MS42MDQgODg2LjEwOSAxNjkuNjI0Qzg5MC41MDkgMTY3LjUzNCA4OTQuMjQ5IDE2NC43MjkgODk3LjMyOSAxNjEuMjA5VjE0Ni4wMjhIODcwLjQzMkM4NjQuMjcyIDE0Ni4wMjggODU5Ljg3MiAxNDcuMTgzIDg1Ny4yMzIgMTQ5LjQ5M0M4NTQuNTkxIDE1MS44MDMgODUzLjI3MSAxNTUuMzIzIDg1My4yNzEgMTYwLjA1NEM4NTMuMjcxIDE2NC43ODQgODU0Ljg2NiAxNjguMDg0IDg1OC4wNTcgMTY5Ljk1NEM4NjEuMjQ3IDE3MS43MTQgODY1LjUzNyAxNzIuNTk0IDg3MC45MjggMTcyLjU5NFpNOTQ5LjQ3NSAxODMuNjVDOTQ0LjE5NSAxODMuNjUgOTQwLjAxNSAxODIuMjc1IDkzNi45MzUgMTc5LjUyNUM5MzMuOTY0IDE3Ni42NjUgOTMyLjQ3OSAxNzEuODc5IDkzMi40NzkgMTY1LjE2OVY3MC43ODI2SDk0Ni4wMVYxNjMuNjg0Qzk0Ni4wMSAxNjYuOTg0IDk0Ni41NiAxNjkuMjM5IDk0Ny42NiAxNzAuNDQ5Qzk0OC43NiAxNzEuNjU5IDk1MC40NjUgMTcyLjI2NCA5NTIuNzc2IDE3Mi4yNjRDOTU1LjMwNiAxNzIuMjY0IDk1Ny43ODEgMTcxLjkzNCA5NjAuMjAxIDE3MS4yNzRWMTgyQzk1OC40NDEgMTgyLjY2IDk1Ni42ODEgMTgzLjEgOTU0LjkyMSAxODMuMzJDOTUzLjE2MSAxODMuNTQgOTUxLjM0NSAxODMuNjUgOTQ5LjQ3NSAxODMuNjVaIiBmaWxsPSJibGFjayIvPg0KPGRlZnM+DQo8bGluZWFyR3JhZGllbnQgaWQ9InBhaW50MF9saW5lYXJfNF80NCIgeDE9IjM4LjIwMDEiIHkxPSIzNy43MTkxIiB4Mj0iMzguMjAwMSIgeTI9IjE2NS4zMTciIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4NCjxzdG9wIHN0b3AtY29sb3I9IiMxOTQ2RTUiLz4NCjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzAyMDA1NSIvPg0KPC9saW5lYXJHcmFkaWVudD4NCjxsaW5lYXJHcmFkaWVudCBpZD0icGFpbnQxX2xpbmVhcl80XzQ0IiB4MT0iNjEuMzY1NiIgeTE9IjM3LjUyIiB4Mj0iNjEuMzY1NiIgeTI9IjIxOS4zMSIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPg0KPHN0b3Agb2Zmc2V0PSIwLjQ0NjY2NiIgc3RvcC1jb2xvcj0iIzE5NDZFNSIvPg0KPHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjMDIwMDY4Ii8+DQo8L2xpbmVhckdyYWRpZW50Pg0KPGxpbmVhckdyYWRpZW50IGlkPSJwYWludDJfbGluZWFyXzRfNDQiIHgxPSIxNTAuNTM4IiB5MT0iMjIuNTIwMSIgeDI9IjE1MC41MzgiIHkyPSIxMzUuODY1IiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+DQo8c3RvcCBzdG9wLWNvbG9yPSIjMTk0NkU1Ii8+DQo8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiMwMjAwNjgiLz4NCjwvbGluZWFyR3JhZGllbnQ+DQo8bGluZWFyR3JhZGllbnQgaWQ9InBhaW50M19saW5lYXJfNF80NCIgeDE9IjExNS45MTkiIHkxPSIyNy4zMDQ2IiB4Mj0iMTAyLjYxMSIgeTI9IjIxMC44MTkiIGdyYWRpZW50VW5pdHM9InVzZXJTcGFjZU9uVXNlIj4NCjxzdG9wIHN0b3AtY29sb3I9IiMwMjAwNjgiLz4NCjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzE5NDZFNSIvPg0KPC9saW5lYXJHcmFkaWVudD4NCjwvZGVmcz4NCjwvc3ZnPg0K"}

# Drawing routines from FrontEnd_V2 @ 4bfe313cca9c (2026-10-03).
# TypeScript types removed at build time; no Node/React dependency at runtime.
PALETTES = ["inferno","viridis","plasma","magma","hot","cividis","spectral","blackbody","bluered","blues","earth","electric","greens","greys","picnic","portland","rainbow","rdbu","reds","ylgn","ylgnbu","ylorbr","ylorrd","jet"]
CANVAS_RENDERER = r"""
const arrayMax = values => { let m = -Infinity; for (const v of values) if (v > m) m = v; return m; };
const COLORSCALE_MAP = {
    inferno: ["#000004", "#1b0c41", "#4a0c6b", "#781c6d", "#a52c60", "#cf4446", "#ed6925", "#fb9b06", "#f7d13d", "#fcffa4"],
    viridis: ["#440154", "#482777", "#3f4a8a", "#31678e", "#26838f", "#1f9d8a", "#6cce5a", "#b6de2b", "#fee825"],
    plasma: ["#0d0887", "#4b03a1", "#7d03a8", "#a82296", "#cb4679", "#e56b5d", "#f89441", "#fdc328", "#f0f921"],
    magma: ["#000004", "#180f3d", "#440f76", "#721f81", "#9e2f7f", "#cd4071", "#f1605d", "#fd9668", "#fec488", "#fcfdbf"],
    hot: ["#000000", "#730000", "#e60000", "#ff6a00", "#ffd400", "#ffff6b", "#ffffff"],
    cividis: ["#002051", "#0d346b", "#2b4a77", "#4d6176", "#717872", "#988f6e", "#c2a862", "#ecc34b", "#fdea45"],
    spectral: ["#9e0142", "#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#e6f598", "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2"],
    blackbody: ["#000000", "#e60000", "#ff8c00", "#ffff00", "#ffffff"],
    bluered: ["#0000ff", "#4444ff", "#8888ff", "#ffffff", "#ff8888", "#ff4444", "#ff0000"],
    blues: ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
    earth: ["#006837", "#31a354", "#78c679", "#c2e699", "#ffffcc", "#fed976", "#fd8d3c", "#e31a1c", "#800026"],
    electric: ["#000000", "#1e0a3c", "#511674", "#832681", "#b63679", "#e65164", "#fb8761", "#fec287", "#fcfdbf"],
    greens: ["#f7fcf5", "#c7e9c0", "#74c476", "#238b45", "#00441b"],
    greys: ["#ffffff", "#bdbdbd", "#636363", "#000000"],
    picnic: ["#0000ff", "#3399ff", "#66ccff", "#99ffcc", "#ccff66", "#ffcc33", "#ff6600", "#ff0000"],
    portland: ["#0c3383", "#0a88ba", "#f2d338", "#f28f38", "#d91e1e"],
    rainbow: ["#96005a", "#0000c8", "#0019ff", "#0098ff", "#2cdf00", "#86f400", "#ffef00", "#ff8c00", "#ff0000"],
    rdbu: ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"],
    reds: ["#fff5f0", "#fcbba1", "#fb6a4a", "#cb181d", "#67000d"],
    ylgn: ["#ffffe5", "#d9f0a3", "#78c679", "#238443", "#004529"],
    ylgnbu: ["#ffffd9", "#c7e9b4", "#41b6c4", "#225ea8", "#081d58"],
    ylorbr: ["#ffffe5", "#fec44f", "#fe9929", "#d95f0e", "#662506"],
    ylorrd: ["#ffffcc", "#fed976", "#fd8d3c", "#e31a1c", "#800026"],
    jet: ["#000080", "#0000ff", "#00b0ff", "#00ff00", "#b0ff00", "#ffff00", "#ff7000", "#ff0000", "#800000"],
};
function hexToRgb(hex) {
    const h = hex.replace("#", "");
    return [
        parseInt(h.substring(0, 2), 16),
        parseInt(h.substring(2, 4), 16),
        parseInt(h.substring(4, 6), 16),
    ];
}
function buildColorLUT(hexColors, fadeBgHex) {
    const rgbColors = hexColors.map(hexToRgb);
    const lut = new Uint8Array(256 * 4);
    const bg = fadeBgHex ? hexToRgb(fadeBgHex) : null;
    const fadeBelow = 40;
    for (let i = 0; i < 256; i++) {
        const t = i / 255;
        const segF = t * (rgbColors.length - 1);
        const segIdx = Math.min(Math.floor(segF), rgbColors.length - 2);
        const segT = segF - segIdx;
        const a = rgbColors[segIdx];
        const b = rgbColors[segIdx + 1];
        const off = i * 4;
        let r = Math.round(a[0] + (b[0] - a[0]) * segT);
        let g = Math.round(a[1] + (b[1] - a[1]) * segT);
        let bl = Math.round(a[2] + (b[2] - a[2]) * segT);
        if (bg && i < fadeBelow) {
            const fadeT = i / fadeBelow;
            r = Math.round(bg[0] + (r - bg[0]) * fadeT);
            g = Math.round(bg[1] + (g - bg[1]) * fadeT);
            bl = Math.round(bg[2] + (bl - bg[2]) * fadeT);
        }
        lut[off] = r;
        lut[off + 1] = g;
        lut[off + 2] = bl;
        lut[off + 3] = 255;
    }
    return lut;
}
function heatmapLut(palette){
    // Match FrontEnd_V2: true palette in both themes, no RGB inversion or fade.
    return buildColorLUT(COLORSCALE_MAP[palette]||COLORSCALE_MAP.inferno,null);
}
function formatCompactUSD(v) {
    const sign = v < 0 ? '-$' : '$', n = Math.abs(v);
    if (n >= 1e12) return `${sign}${(n / 1e12).toFixed(1)}T`;
    if (n >= 1e9) return `${sign}${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `${sign}${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `${sign}${(n / 1e3).toFixed(1)}K`;
    return `${sign}${n.toFixed(0)}`;
}
function formatPrice(v) {
    if (v >= 1000)
        return `$${v.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
    if (v >= 1)
        return `$${v.toFixed(2)}`;
    return `$${v.toPrecision(4)}`;
}
function computeLayout(w, h) {
    const cbW = 52;
    const rpW = Math.min(220, w * 0.22);
    const yAxisW = 72;
    const scrollH = 20;
    const xAxisH = 24;
    const gap = 4;
    const accumH = Math.max(50, h * 0.14);
    const deltaH = Math.max(40, h * 0.10);
    const bottomTotal = accumH + deltaH + xAxisH + scrollH + gap * 4;
    const heatH = Math.max(100, h - bottomTotal - 10);
    const left = cbW + 8;
    const chartW = w - left - yAxisW - rpW - 12;
    const rpX = left + chartW + yAxisW + 4;
    const rightSummaryH = 70;
    const rightPanelH = heatH + rightSummaryH;
    const klY = 8 + rightPanelH + gap;
    const klH = h - klY - 4;
    return {
        heatmap: { x: left, y: 8, w: chartW, h: heatH },
        rightPanel: { x: rpX, y: 8, w: rpW, h: rightPanelH },
        keyLevels: { x: rpX, y: klY, w: rpW, h: Math.max(0, klH) },
        accumPanel: { x: left, y: 8 + heatH + gap + 14, w: chartW, h: accumH },
        deltaPanel: { x: left, y: 8 + heatH + gap + 14 + accumH + gap + 14, w: chartW, h: deltaH },
        colorBar: { x: 4, y: 8, w: cbW - 4, h: heatH },
        scrollbar: { x: left, y: h - scrollH - 2, w: chartW, h: scrollH },
        width: w,
        height: h,
    };
}
const FONT = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
const FONT_SMALL = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
const BG_DARK = "#0b0f19";
const BG_LIGHT = "#f5f6f9";
function getLiquidationCanvasPixelRatio(screenshotState) {
    if (screenshotState?.pixelRatio)
        return screenshotState.pixelRatio;
    return typeof window === "undefined" ? 1 : window.devicePixelRatio || 1;
}
const TEXT_DARK = "#8b8fa3";
const TEXT_LIGHT = "#6b7280";
const GRID_DARK = "rgba(255,255,255,0.06)";
const GRID_LIGHT = "rgba(0,0,0,0.08)";
const GREEN = "#0D9276";
const RED = "#DF1C41";
function buildHeatmapCache(data, lut) {
    const { zMatrix, yValues, timestamps, maxZ } = data;
    const numT = timestamps.length;
    const numP = yValues.length;
    const c = document.createElement("canvas");
    c.width = numT;
    c.height = numP;
    const ctx = c.getContext("2d");
    const img = ctx.createImageData(numT, numP);
    const px = img.data;
    for (let pi = 0; pi < numP; pi++) {
        const row = zMatrix[pi];
        const canvasY = numP - 1 - pi;
        for (let ti = 0; ti < numT; ti++) {
            const off = (canvasY * numT + ti) * 4;
            const val = row[ti]; if (val == null || !Number.isFinite(val)) { px[off + 3] = 0; continue; }
            if (val <= 0) {
                px[off] = lut[0];
                px[off + 1] = lut[1];
                px[off + 2] = lut[2];
                px[off + 3] = 255;
            }
            else {
                const t = Math.min(val / maxZ, 1);
                const li = Math.floor(t * 255) * 4;
                px[off] = lut[li];
                px[off + 1] = lut[li + 1];
                px[off + 2] = lut[li + 2];
                px[off + 3] = 255;
            }
        }
    }
    ctx.putImageData(img, 0, 0);
    return c;
}
function drawHeatmap(ctx, cache, r, viewStart, viewEnd, yStart, yEnd, smooth) {
    const srcX = Math.max(0, Math.floor(viewStart * cache.width));
    const srcW = Math.max(1, Math.min(Math.ceil((viewEnd - viewStart) * cache.width), cache.width - srcX));
    const rawSrcY = (1 - yEnd) * cache.height;
    const rawSrcBottom = (1 - yStart) * cache.height;
    const rawSrcH = rawSrcBottom - rawSrcY;
    const clampedSrcY = Math.max(0, rawSrcY);
    const clampedSrcBottom = Math.min(cache.height, rawSrcBottom);
    const clampedSrcH = clampedSrcBottom - clampedSrcY;
    if (clampedSrcH <= 0 || srcW <= 0)
        return;
    const dstYOffset = ((clampedSrcY - rawSrcY) / rawSrcH) * r.h;
    const dstH = (clampedSrcH / rawSrcH) * r.h;
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    ctx.imageSmoothingEnabled = smooth;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(cache, srcX, clampedSrcY, srcW, clampedSrcH, r.x, r.y + dstYOffset, r.w, dstH);
    ctx.restore();
}
function drawCandlesticks(ctx, data, r, viewStart, viewEnd, yStart, yEnd) {
    const { candles, yValues } = data;
    const fullYMin = yValues[0];
    const fullYMax = yValues[yValues.length - 1];
    const yRange = fullYMax - fullYMin;
    const visYMin = fullYMin + yStart * yRange;
    const visYMax = fullYMin + yEnd * yRange;
    const startIdx = Math.floor(viewStart * candles.length);
    const endIdx = Math.ceil(viewEnd * candles.length);
    const visible = endIdx - startIdx;
    if (visible <= 0)
        return;
    const candleW = Math.max(2, (r.w / visible) * 0.85);
    const mapY = (price) => r.y + r.h * (1 - (price - visYMin) / (visYMax - visYMin));
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    for (let i = startIdx; i < endIdx && i < candles.length; i++) {
        const c = candles[i]; if (!c || !Number.isFinite(c.close)) continue;
        const cx = r.x + ((i - startIdx + 0.5) / visible) * r.w;
        const isUp = c.close >= c.open;
        const color = isUp ? GREEN : RED;
        ctx.strokeStyle = color;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(cx, mapY(c.high));
        ctx.lineTo(cx, mapY(c.low));
        ctx.stroke();
        const bodyTop = mapY(Math.max(c.open, c.close));
        const bodyBot = mapY(Math.min(c.open, c.close));
        const bodyH = Math.max(1, bodyBot - bodyTop);
        ctx.fillStyle = color;
        ctx.fillRect(cx - candleW / 2, bodyTop, candleW, bodyH);
    }
    ctx.restore();
}
function drawCurrentPriceLine(ctx, data, r, yStart, yEnd, isDark) {
    const { currentPrice, yValues } = data;
    const fullYMin = yValues[0];
    const fullYMax = yValues[yValues.length - 1];
    const yRange = fullYMax - fullYMin;
    const visYMin = fullYMin + yStart * yRange;
    const visYMax = fullYMin + yEnd * yRange;
    const py = r.y + r.h * (1 - (currentPrice - visYMin) / (visYMax - visYMin));
    if (py < r.y || py > r.y + r.h)
        return;
    ctx.save();
    ctx.setLineDash([4, 3]);
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.5)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r.x, py);
    ctx.lineTo(r.x + r.w, py);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = isDark ? "rgba(255,255,255,0.85)" : "rgba(0,0,0,0.85)";
    ctx.font = FONT_SMALL;
    ctx.textAlign = "left";
    ctx.fillText(formatPrice(currentPrice), r.x + r.w + 4, py + 3);
    ctx.restore();
}
function drawRightPanel(ctx, data, r, isDark, yStart, yEnd) {
    const { liqByPrice, yValues, currentPrice, longsAccumByPrice, shortsAccumByPrice, totalLongsSum, totalShortsSum, } = data;
    const numP = yValues.length;
    const fullYMin = yValues[0];
    const fullYMax = yValues[yValues.length - 1];
    const yRange = fullYMax - fullYMin;
    const visYMin = fullYMin + yStart * yRange;
    const visYMax = fullYMin + yEnd * yRange;
    const yMin = visYMin;
    const yMax = visYMax;
    const visiblePriceIndexes = [];
    for (let i = 0; i < numP; i++) {
        if (yValues[i] >= visYMin && yValues[i] <= visYMax)
            visiblePriceIndexes.push(i);
    }
    const visibleBarValues = visiblePriceIndexes
        .map((i) => liqByPrice[i])
        .filter((val) => val > 0)
        .sort((a, b) => a - b);
    const maxBar = Math.max(visibleBarValues[visibleBarValues.length - 1] || 0, 1);
    const infoFooterH = 70;
    const chartAreaY = r.y;
    const chartAreaH = r.h - infoFooterH;
    const summaryY = chartAreaY + chartAreaH;
    const chartBodyX = r.x + 2;
    const chartBodyW = Math.max(20, r.w - 6);
    const barAreaW = chartBodyW;
    const accumX = chartBodyX;
    const accumAreaW = chartBodyW;
    const visibleAccumValues = visiblePriceIndexes.reduce((acc, i) => {
        acc.push(longsAccumByPrice[i], shortsAccumByPrice[i]);
        return acc;
    }, []);
    const maxAccum = Math.max(arrayMax(visibleAccumValues), 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    ctx.fillStyle = isDark ? "rgba(11,15,25,0.5)" : "rgba(245,245,250,0.5)";
    ctx.fillRect(r.x, r.y, r.w, r.h);
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.09)" : "rgba(0,0,0,0.09)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(r.x + 0.5, r.y + 0.5, r.w - 1, r.h - 1, 4);
    ctx.stroke();
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.055)" : "rgba(0,0,0,0.055)";
    ctx.beginPath();
    ctx.moveTo(r.x + 4, summaryY + 1);
    ctx.lineTo(r.x + r.w - 4, summaryY + 1);
    ctx.stroke();
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r.x, r.y);
    ctx.lineTo(r.x, r.y + r.h);
    ctx.stroke();
    const total = totalLongsSum + totalShortsSum;
    const longPct = total > 0 ? totalLongsSum / total : 0.5;
    const shortPct = 1 - longPct;
    ctx.font = '10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = isDark ? "#c5cad7" : "#374151";
    ctx.textAlign = "center";
    ctx.fillText("Liquidation Distribution", r.x + r.w / 2, summaryY + 13);
    const valueY = summaryY + 34;
    ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = GREEN;
    ctx.textAlign = "left";
    ctx.fillText(formatCompactUSD(totalLongsSum), r.x + 5, valueY);
    ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = isDark ? "#f1f5f9" : "#111827";
    ctx.textAlign = "center";
    ctx.shadowColor = isDark ? "rgba(255,255,255,0.18)" : "rgba(0,0,0,0.10)";
    ctx.shadowBlur = 2;
    ctx.fillText(formatPrice(currentPrice), r.x + r.w / 2, valueY + 1);
    ctx.shadowBlur = 0;
    ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = RED;
    ctx.textAlign = "right";
    ctx.fillText(formatCompactUSD(totalShortsSum), r.x + r.w - 5, valueY);
    const ratioX = r.x + 6;
    const ratioY = summaryY + 43;
    const ratioW = r.w - 12;
    const ratioH = 6;
    ctx.fillStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    ctx.beginPath();
    ctx.roundRect(ratioX, ratioY, ratioW, ratioH, 3);
    ctx.fill();
    ctx.fillStyle = GREEN;
    ctx.beginPath();
    ctx.roundRect(ratioX, ratioY, ratioW * longPct, ratioH, 3);
    ctx.fill();
    ctx.fillStyle = RED;
    ctx.beginPath();
    ctx.roundRect(ratioX + ratioW * longPct, ratioY, ratioW * shortPct, ratioH, 3);
    ctx.fill();
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = GREEN;
    ctx.textAlign = "left";
    ctx.fillText(`${Math.round(longPct * 100)}%`, r.x + 6, summaryY + 64);
    ctx.fillStyle = RED;
    ctx.textAlign = "right";
    ctx.fillText(`${Math.round(shortPct * 100)}%`, r.x + r.w - 6, summaryY + 64);
    ctx.fillStyle = isDark ? "rgba(255,255,255,0.018)" : "rgba(0,0,0,0.018)";
    ctx.fillRect(chartBodyX, chartAreaY, chartBodyW, chartAreaH);
    const mapPriceToY = (price) => chartAreaY + chartAreaH * (1 - (price - yMin) / (yMax - yMin));
    ctx.save();
    ctx.beginPath();
    ctx.rect(chartBodyX, chartAreaY, chartBodyW, chartAreaH);
    ctx.clip();
    for (const i of visiblePriceIndexes) {
        const val = liqByPrice[i];
        if (val <= 0)
            continue;
        const price = yValues[i];
        const scaledBarW = (val / maxBar) * (barAreaW - 4);
        const bw = Math.min(Math.max(scaledBarW, 1.25), barAreaW - 4);
        const by = mapPriceToY(price);
        const bh = Math.max(1, chartAreaH / ((visYMax - visYMin) / (fullYMax - fullYMin) * numP));
        const isLong = price <= currentPrice;
        ctx.fillStyle = isLong ? GREEN : RED;
        ctx.globalAlpha = 0.72;
        ctx.fillRect(chartBodyX, by - bh / 2, bw, Math.max(1, bh - 0.5));
    }
    ctx.restore();
    ctx.globalAlpha = 1;
    const cpY = mapPriceToY(currentPrice);
    if (cpY >= chartAreaY && cpY <= chartAreaY + chartAreaH) {
        ctx.strokeStyle = isDark ? "rgba(255,255,255,0.24)" : "rgba(0,0,0,0.18)";
        ctx.lineWidth = 1;
        ctx.setLineDash([2, 2]);
        ctx.beginPath();
        ctx.moveTo(r.x, cpY);
        ctx.lineTo(r.x + r.w, cpY);
        ctx.stroke();
        ctx.setLineDash([]);
    }
    const mapPY = (i) => {
        const price = yValues[i];
        return chartAreaY + chartAreaH * (1 - (price - yMin) / (yMax - yMin));
    };
    const currentPriceVisible = currentPrice >= yMin && currentPrice <= yMax;
    const currentY = mapPriceToY(currentPrice);
    const shortCurveIndexes = visiblePriceIndexes.filter((i) => yValues[i] >= currentPrice);
    const longCurveIndexes = visiblePriceIndexes.filter((i) => yValues[i] <= currentPrice).reverse();
    const drawAccumCurve = (values, indexes, color) => {
        if (indexes.length === 0)
            return;
        ctx.beginPath();
        if (currentPriceVisible) {
            ctx.moveTo(accumX, currentY);
        }
        else {
            ctx.moveTo(accumX, mapPY(indexes[0]));
        }
        for (const i of indexes) {
            const cx = accumX + (values[i] / maxAccum) * accumAreaW;
            ctx.lineTo(cx, mapPY(i));
        }
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = 0.86;
        ctx.stroke();
        ctx.globalAlpha = 1;
    };
    ctx.save();
    ctx.beginPath();
    ctx.rect(accumX - 1, chartAreaY, r.x + r.w - accumX + 1, chartAreaH);
    ctx.clip();
    drawAccumCurve(shortsAccumByPrice, shortCurveIndexes, RED);
    drawAccumCurve(longsAccumByPrice, longCurveIndexes, GREEN);
    ctx.restore();
    const drawValueTag = (text, x, y, color, align = "center") => {
        const tagPadX = 4;
        const tagH = 14;
        ctx.font = 'bold 8px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        const tagMaxW = Math.max(24, r.x + r.w - accumX - 4);
        const tagW = Math.min(tagMaxW, ctx.measureText(text).width + tagPadX * 2);
        const rawX = align === "left" ? x : align === "right" ? x - tagW : x - tagW / 2;
        const minTagX = accumX + 2;
        const maxTagX = r.x + r.w - tagW - 2;
        const tagX = maxTagX < minTagX ? minTagX : Math.max(minTagX, Math.min(maxTagX, rawX));
        const tagY = Math.max(chartAreaY + 2, Math.min(chartAreaY + chartAreaH - tagH - 2, y - tagH / 2));
        ctx.fillStyle = isDark ? "rgba(11,15,25,0.82)" : "rgba(245,246,249,0.86)";
        ctx.strokeStyle = color;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.roundRect(tagX, tagY, tagW, tagH, 4);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = color;
        ctx.textAlign = "center";
        ctx.fillText(text, tagX + tagW / 2, tagY + 10);
    };
    const shortEndpointIdx = shortCurveIndexes[shortCurveIndexes.length - 1];
    if (shortEndpointIdx !== undefined) {
        const shortsEndpointValue = shortsAccumByPrice[shortEndpointIdx] || totalShortsSum;
        const shortsEndpointY = mapPY(shortEndpointIdx);
        const shortsEndpointX = accumX + (shortsEndpointValue / maxAccum) * accumAreaW;
        drawValueTag(`Short ${formatCompactUSD(shortsEndpointValue)}`, shortsEndpointX - 2, shortsEndpointY + 10, RED, "right");
    }
    const longEndpointIdx = longCurveIndexes[longCurveIndexes.length - 1];
    if (longEndpointIdx !== undefined) {
        const longsEndpointValue = longsAccumByPrice[longEndpointIdx] || totalLongsSum;
        const longsEndpointY = mapPY(longEndpointIdx);
        const longsEndpointX = accumX + (longsEndpointValue / maxAccum) * accumAreaW;
        drawValueTag(`Long ${formatCompactUSD(longsEndpointValue)}`, longsEndpointX - 2, longsEndpointY - 10, GREEN, "right");
    }
    ctx.restore();
}
function drawAccumPanel(ctx, data, r, viewStart, viewEnd, isDark) {
    const { totalLongs, totalShorts, timestamps } = data;
    const startIdx = Math.floor(viewStart * timestamps.length);
    const endIdx = Math.ceil(viewEnd * timestamps.length);
    const visible = endIdx - startIdx;
    if (visible <= 0)
        return;
    const longsSlice = totalLongs.slice(startIdx, endIdx);
    const shortsSlice = totalShorts.slice(startIdx, endIdx);
    const maxVal = Math.max(arrayMax(longsSlice), arrayMax(shortsSlice), 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    const panelBg = isDark ? "rgba(11,15,25,0.8)" : "rgba(255,255,255,0.8)";
    ctx.fillStyle = panelBg;
    ctx.fillRect(r.x, r.y, r.w, r.h);
    const mapX = (i) => r.x + ((i) / visible) * r.w;
    const mapY = (v) => r.y + r.h * (1 - v / maxVal);
    const drawArea = (values, color, fill) => {
        ctx.beginPath();
        ctx.moveTo(mapX(0), mapY(values[0]));
        for (let i = 1; i < values.length; i++)
            ctx.lineTo(mapX(i), mapY(values[i]));
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.lineTo(mapX(values.length - 1), r.y + r.h);
        ctx.lineTo(mapX(0), r.y + r.h);
        ctx.closePath();
        ctx.fillStyle = fill;
        ctx.fill();
    };
    drawArea(shortsSlice, RED, "rgba(223,28,65,0.12)");
    drawArea(longsSlice, GREEN, "rgba(13,146,118,0.12)");
    ctx.fillStyle = isDark ? TEXT_DARK : TEXT_LIGHT;
    ctx.font = FONT_SMALL;
    ctx.textAlign = "right";
    ctx.fillText(formatCompactUSD(maxVal), r.x + r.w - 2, r.y + 10);
    ctx.restore();
}
function drawDeltaPanel(ctx, data, r, viewStart, viewEnd, isDark) {
    const { netDelta, timestamps } = data;
    const startIdx = Math.floor(viewStart * timestamps.length);
    const endIdx = Math.ceil(viewEnd * timestamps.length);
    const visible = endIdx - startIdx;
    if (visible <= 0)
        return;
    const slice = netDelta.slice(startIdx, endIdx);
    const absMax = Math.max(arrayMax(slice.map(Math.abs)), 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    const panelBg = isDark ? "rgba(11,15,25,0.8)" : "rgba(255,255,255,0.8)";
    ctx.fillStyle = panelBg;
    ctx.fillRect(r.x, r.y, r.w, r.h);
    const midY = r.y + r.h / 2;
    const barW = Math.max(1, r.w / visible - 1);
    for (let i = 0; i < slice.length; i++) {
        const val = slice[i];
        const bh = (Math.abs(val) / absMax) * (r.h / 2 - 2);
        const bx = r.x + (i / visible) * r.w;
        ctx.fillStyle = val >= 0 ? GREEN : RED;
        ctx.globalAlpha = 0.8;
        if (val >= 0) {
            ctx.fillRect(bx, midY - bh, barW, bh);
        }
        else {
            ctx.fillRect(bx, midY, barW, bh);
        }
    }
    ctx.globalAlpha = 1;
    ctx.strokeStyle = isDark ? GRID_DARK : GRID_LIGHT;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r.x, midY);
    ctx.lineTo(r.x + r.w, midY);
    ctx.stroke();
    ctx.restore();
}
function drawAxes(ctx, data, layout, viewStart, viewEnd, yStart, yEnd, isDark) {
    const { yValues, timestamps, timeStrings } = data;
    const textColor = isDark ? TEXT_DARK : TEXT_LIGHT;
    ctx.font = FONT_SMALL;
    ctx.fillStyle = textColor;
    const r = layout.heatmap;
    const fullYMin = yValues[0];
    const fullYMax = yValues[yValues.length - 1];
    const yRange = fullYMax - fullYMin;
    const visYMin = fullYMin + yStart * yRange;
    const visYMax = fullYMin + yEnd * yRange;
    const numLabels = Math.min(12, Math.max(4, Math.floor(r.h / 50)));
    const priceStep = (visYMax - visYMin) / numLabels;
    ctx.textAlign = "left";
    for (let i = 0; i <= numLabels; i++) {
        const price = visYMin + i * priceStep;
        const py = r.y + r.h * (1 - (price - visYMin) / (visYMax - visYMin));
        if (py < r.y - 5 || py > r.y + r.h + 5)
            continue;
        ctx.fillStyle = textColor;
        ctx.fillText(formatPrice(price), r.x + r.w + 4, py + 3);
        ctx.strokeStyle = isDark ? GRID_DARK : GRID_LIGHT;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(r.x, py);
        ctx.lineTo(r.x + r.w, py);
        ctx.stroke();
    }
    const startIdx = Math.floor(viewStart * timestamps.length);
    const endIdx = Math.ceil(viewEnd * timestamps.length);
    const visible = endIdx - startIdx;
    const xLabelStep = Math.max(1, Math.floor(visible / 8));
    const bottomY = layout.deltaPanel.y + layout.deltaPanel.h + 4;
    ctx.textAlign = "center";
    for (let i = 0; i < visible; i += xLabelStep) {
        const idx = startIdx + i;
        if (idx >= timeStrings.length)
            break;
        const px = r.x + (i / visible) * r.w;
        const d = new Date(timeStrings[idx]);
        const label = `${d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" })}`;
        ctx.fillText(label, px, bottomY + 10);
    }
}
function drawColorBar(ctx, maxZ, lut, r, isDark, hoverY) {
    const labelPad = 14;
    const barW = 14;
    const bx = r.x + (r.w - barW) / 2;
    const barTop = r.y + labelPad;
    const barH = r.h - labelPad * 2;
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(bx, barTop, barW, barH, 3);
    ctx.clip();
    for (let py = 0; py < barH; py++) {
        const t = 1 - py / barH;
        const li = Math.floor(t * 255) * 4;
        ctx.fillStyle = `rgb(${lut[li]},${lut[li + 1]},${lut[li + 2]})`;
        ctx.fillRect(bx, barTop + py, barW, 1);
    }
    ctx.restore();
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(bx, barTop, barW, barH, 3);
    ctx.stroke();
    ctx.font = FONT_SMALL;
    ctx.fillStyle = isDark ? TEXT_DARK : TEXT_LIGHT;
    ctx.textAlign = "center";
    ctx.fillText(formatCompactUSD(maxZ), bx + barW / 2, barTop - 3);
    ctx.fillText("$0", bx + barW / 2, barTop + barH + 10);
    if (hoverY !== undefined && hoverY >= barTop && hoverY <= barTop + barH) {
        const t = 1 - (hoverY - barTop) / barH;
        const val = t * maxZ;
        ctx.strokeStyle = isDark ? "rgba(255,255,255,0.7)" : "rgba(0,0,0,0.7)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(bx - 2, hoverY);
        ctx.lineTo(bx + barW + 2, hoverY);
        ctx.stroke();
        ctx.fillStyle = isDark ? "rgba(255,255,255,0.9)" : "rgba(0,0,0,0.9)";
        ctx.beginPath();
        ctx.moveTo(bx + barW + 3, hoverY);
        ctx.lineTo(bx + barW + 7, hoverY - 3);
        ctx.lineTo(bx + barW + 7, hoverY + 3);
        ctx.closePath();
        ctx.fill();
        ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillStyle = isDark ? "#e4e6eb" : "#111827";
        ctx.textAlign = "left";
        ctx.fillText(formatCompactUSD(val), bx + barW + 9, hoverY + 3);
    }
}
function drawPanelLabels(ctx, layout, isDark) {
    ctx.font = '11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = isDark ? "#a0a8c0" : "#555";
    ctx.textAlign = "left";
    ctx.fillText("Accumulated Longs vs Shorts", layout.accumPanel.x, layout.accumPanel.y - 4);
    ctx.fillText("Net Longs \u2212 Shorts", layout.deltaPanel.x, layout.deltaPanel.y - 4);
}
function drawCrosshair(ctx, mx, my, r, isDark) {
    ctx.save();
    ctx.setLineDash([3, 3]);
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.18)" : "rgba(0,0,0,0.16)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(mx, r.y);
    ctx.lineTo(mx, r.y + r.h);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(r.x, my);
    ctx.lineTo(r.x + r.w, my);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
}
function drawScrollbar(ctx, r, viewStart, viewEnd, isDark) {
    ctx.fillStyle = isDark ? "rgba(255,255,255,0.04)" : "rgba(0,0,0,0.04)";
    ctx.beginPath();
    ctx.roundRect(r.x, r.y, r.w, r.h, 4);
    ctx.fill();
    const hx = r.x + viewStart * r.w;
    const hw = (viewEnd - viewStart) * r.w;
    ctx.fillStyle = isDark ? "rgba(75,107,255,0.2)" : "rgba(75,107,255,0.15)";
    ctx.beginPath();
    ctx.roundRect(hx, r.y + 2, hw, r.h - 4, 3);
    ctx.fill();
    ctx.fillStyle = "rgba(75,107,255,0.5)";
    ctx.beginPath();
    ctx.roundRect(hx, r.y + 2, 4, r.h - 4, 2);
    ctx.fill();
    ctx.beginPath();
    ctx.roundRect(hx + hw - 4, r.y + 2, 4, r.h - 4, 2);
    ctx.fill();
}
function drawKeyLevels(ctx, data, r, isDark) {
    if (r.h < 40)
        return;
    const { yValues, zMatrix, timestamps, currentPrice } = data;
    const numT = timestamps.length;
    const windowStart = Math.max(0, Math.floor(numT * 0.9));
    const recentValues = [];
    let recentMax = 0;
    for (let pi = 0; pi < yValues.length; pi++) {
        let peak = 0;
        for (let ti = windowStart; ti < numT; ti++) {
            if (zMatrix[pi][ti] > peak)
                peak = zMatrix[pi][ti];
        }
        recentValues.push(peak);
        if (peak > recentMax)
            recentMax = peak;
    }
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    ctx.fillStyle = isDark ? "rgba(11,15,25,0.5)" : "rgba(245,245,250,0.5)";
    ctx.fillRect(r.x, r.y, r.w, r.h);
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r.x, r.y);
    ctx.lineTo(r.x, r.y + r.h);
    ctx.stroke();
    const above = [];
    const below = [];
    for (let i = 0; i < yValues.length; i++) {
        const price = yValues[i];
        const val = recentValues[i];
        if (val <= 0)
            continue;
        const dist = ((price - currentPrice) / currentPrice) * 100;
        const isLong = price <= currentPrice;
        if (price > currentPrice)
            above.push({ price, value: val, dist, isLong });
        else
            below.push({ price, value: val, dist, isLong });
    }
    above.sort((a, b) => b.value - a.value);
    below.sort((a, b) => b.value - a.value);
    const levelLimit = r.h < 130 ? 2 : 3;
    const topAbove = above.slice(0, levelLimit);
    const topBelow = below.slice(0, levelLimit);
    topAbove.sort((a, b) => a.dist - b.dist);
    topBelow.sort((a, b) => Math.abs(a.dist) - Math.abs(b.dist));
    const pad = 6;
    let cy = r.y + 2;
    ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    ctx.fillStyle = isDark ? "#a0a8c0" : "#555";
    ctx.textAlign = "center";
    ctx.fillText("Key Levels", r.x + r.w / 2, cy + 9);
    cy += 14;
    ctx.strokeStyle = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
    ctx.beginPath();
    ctx.moveTo(r.x + pad, cy);
    ctx.lineTo(r.x + r.w - pad, cy);
    ctx.stroke();
    cy += 5;
    const sectionFont = '8px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    const priceFont = 'bold 9px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    const metaFont = '8px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    const dimColor = isDark ? "#7f8498" : "#7b8190";
    const drawLevel = (level, y) => {
        if (y + 15 > r.y + r.h - 4)
            return y;
        const color = level.isLong ? GREEN : RED;
        const pctSign = level.dist > 0 ? "+" : "";
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(r.x + pad + 3, y + 6, 3, 0, Math.PI * 2);
        ctx.fill();
        const priceText = formatPrice(level.price);
        const valueText = `(${formatCompactUSD(level.value)})`;
        const percentText = `${pctSign}${level.dist.toFixed(1)}%`;
        const priceX = r.x + pad + 10;
        const percentX = r.x + r.w - 2;
        ctx.font = priceFont;
        ctx.fillStyle = isDark ? "#e4e6eb" : "#1f2937";
        ctx.textAlign = "left";
        ctx.fillText(priceText, priceX, y + 9);
        const priceWidth = ctx.measureText(priceText).width;
        ctx.font = metaFont;
        ctx.fillStyle = dimColor;
        ctx.textAlign = "left";
        ctx.fillText(valueText, priceX + priceWidth + 4, y + 9);
        ctx.fillStyle = color;
        ctx.textAlign = "right";
        ctx.fillText(percentText, percentX, y + 9);
        const barW = (level.value / Math.max(recentMax, 1)) * (r.w - pad * 2 - 2);
        ctx.globalAlpha = 0.22;
        ctx.beginPath();
        ctx.roundRect(r.x + pad, y + 12, barW, 3, 1.5);
        ctx.fill();
        ctx.globalAlpha = 1;
        return y + 16;
    };
    const drawSection = (label, levels, color, y) => {
        if (levels.length === 0 || y + 11 > r.y + r.h)
            return y;
        ctx.font = sectionFont;
        ctx.fillStyle = color;
        ctx.textAlign = "left";
        ctx.globalAlpha = 0.95;
        ctx.fillText(label, r.x + pad, y + 8);
        ctx.globalAlpha = 1;
        y += 12;
        for (const level of levels)
            y = drawLevel(level, y);
        return y + 3;
    };
    cy = drawSection("▲ SHORT LEVELS", topAbove, RED, cy);
    if (topBelow.length > 0 && cy + 16 < r.y + r.h) {
        ctx.strokeStyle = isDark ? "rgba(255,255,255,0.06)" : "rgba(0,0,0,0.06)";
        ctx.beginPath();
        ctx.moveTo(r.x + pad, cy);
        ctx.lineTo(r.x + r.w - pad, cy);
        ctx.stroke();
        cy += 5;
        cy = drawSection("▼ LONG LEVELS", topBelow, GREEN, cy);
    }
    ctx.restore();
}
function drawUserObjects(ctx, objects, data, r, viewStart, viewEnd, yStart, yEnd, isDark) {
    if (objects.length === 0)
        return;
    const { yValues } = data;
    const fullYMin = yValues[0];
    const fullYMax = yValues[yValues.length - 1];
    const yRange = fullYMax - fullYMin;
    const visYMin = fullYMin + yStart * yRange;
    const visYMax = fullYMin + yEnd * yRange;
    const mapY = (price) => r.y + r.h * (1 - (price - visYMin) / (visYMax - visYMin));
    const mapX = (xFrac) => r.x + ((xFrac - viewStart) / (viewEnd - viewStart)) * r.w;
    ctx.save();
    ctx.beginPath();
    ctx.rect(r.x, r.y, r.w, r.h);
    ctx.clip();
    for (const obj of objects) {
        if (obj.type === "hline" && obj.price !== undefined) {
            const py = mapY(obj.price);
            ctx.strokeStyle = "#f59e0b";
            ctx.lineWidth = 1.5;
            ctx.setLineDash([6, 3]);
            ctx.beginPath();
            ctx.moveTo(r.x, py);
            ctx.lineTo(r.x + r.w, py);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.fillStyle = "#f59e0b";
            ctx.font = FONT_SMALL;
            ctx.textAlign = "right";
            ctx.fillText(formatPrice(obj.price), r.x + r.w - 4, py - 4);
        }
        else if (obj.type === "trendline" && obj.x1 !== undefined && obj.y1 !== undefined && obj.x2 !== undefined && obj.y2 !== undefined) {
            ctx.strokeStyle = "#3b82f6";
            ctx.lineWidth = 1.5;
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.moveTo(mapX(obj.x1), mapY(obj.y1));
            ctx.lineTo(mapX(obj.x2), mapY(obj.y2));
            ctx.stroke();
            ctx.fillStyle = "#3b82f6";
            [{ x: obj.x1, y: obj.y1 }, { x: obj.x2, y: obj.y2 }].forEach((p) => {
                ctx.beginPath();
                ctx.arc(mapX(p.x), mapY(p.y), 3, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    }
    ctx.restore();
}
function isInRect(x, y, r) {
    return x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h;
}

"""

SVG_CONTEXT = r"""
// Small SVG backend for the exact drawing primitives used by this chart.
// Text, paths, candles, drawings and logo stay vector; the smoothed heatmap
// is embedded at its native grid resolution, without external resources.
class SvgContext {
 constructor(w,h){this.w=w;this.h=h;this.parts=[];this.defs=[];this.stack=[];this.path='';this.clips=[];
  this.fillStyle='#000';this.strokeStyle='#000';this.lineWidth=1;this.globalAlpha=1;this.font='10px sans-serif';this.textAlign='left';this.dash=[];
  this.measure=document.createElement('canvas').getContext('2d');}
 esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));}
 save(){const s={};for(const k of ['fillStyle','strokeStyle','lineWidth','globalAlpha','font','textAlign','imageSmoothingEnabled','shadowBlur','shadowColor'])s[k]=this[k];s.clips=[...this.clips];s.dash=[...this.dash];this.stack.push(s);}
 restore(){Object.assign(this,this.stack.pop()||{});}
 setTransform(){} // All chart coordinates are CSS pixels; ignore screen DPR.
 clearRect(){this.parts=[];this.defs=[];this.clips=[];}
 setLineDash(a){this.dash=[...a];}
 beginPath(){this.path='';}
 closePath(){this.path+='Z ';}
 moveTo(x,y){this.path+=`M${x},${y} `;}
 lineTo(x,y){this.path+=`L${x},${y} `;}
 rect(x,y,w,h){this.path+=`M${x},${y}h${w}v${h}h${-w}Z `;}
 roundRect(x,y,w,h,r){r=Math.max(0,Math.min(Number(r)||0,Math.abs(w)/2,Math.abs(h)/2));
  this.path+=`M${x+r},${y}H${x+w-r}Q${x+w},${y} ${x+w},${y+r}V${y+h-r}Q${x+w},${y+h} ${x+w-r},${y+h}H${x+r}Q${x},${y+h} ${x},${y+h-r}V${y+r}Q${x},${y} ${x+r},${y}Z `;}
 arc(x,y,r,a,b){const x1=x+r*Math.cos(a),y1=y+r*Math.sin(a);this.path+=`M${x1},${y1} `;
  if(Math.abs(b-a)>=Math.PI*2-.00001)this.path+=`a${r},${r} 0 1,1 ${-2*r*Math.cos(a)},${-2*r*Math.sin(a)}a${r},${r} 0 1,1 ${2*r*Math.cos(a)},${2*r*Math.sin(a)} `;
  else this.path+=`A${r},${r} 0 ${Math.abs(b-a)>Math.PI?1:0},1 ${x+r*Math.cos(b)},${y+r*Math.sin(b)} `;}
 emit(s){this.parts.push(this.clips.map(id=>`<g clip-path="url(#${id})">`).join('')+s+'</g>'.repeat(this.clips.length));}
 clip(){const id='clip'+this.defs.length;this.defs.push(`<clipPath id="${id}"><path d="${this.path}"/></clipPath>`);this.clips.push(id);}
 fill(){this.emit(`<path d="${this.path}" fill="${this.esc(this.fillStyle)}" opacity="${this.globalAlpha}"/>`);}
 stroke(){this.emit(`<path d="${this.path}" fill="none" stroke="${this.esc(this.strokeStyle)}" stroke-width="${this.lineWidth}" stroke-dasharray="${this.dash.join(',')}" opacity="${this.globalAlpha}"/>`);}
 fillRect(x,y,w,h){this.emit(`<rect x="${Math.min(x,x+w)}" y="${Math.min(y,y+h)}" width="${Math.abs(w)}" height="${Math.abs(h)}" fill="${this.esc(this.fillStyle)}" opacity="${this.globalAlpha}"/>`);}
 measureText(t){this.measure.font=this.font;return this.measure.measureText(String(t));}
 fillText(t,x,y){const anchor=this.textAlign==='center'?'middle':(['right','end'].includes(this.textAlign)?'end':'start');
  this.emit(`<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${this.esc(this.fillStyle)}" opacity="${this.globalAlpha}" style="font:${this.esc(this.font)}">${this.esc(t)}</text>`);}
 drawImage(img,...args){let sx=0,sy=0,sw=img.naturalWidth||img.width,sh=img.naturalHeight||img.height,dx,dy,dw,dh;
  if(args.length===8)[sx,sy,sw,sh,dx,dy,dw,dh]=args;else [dx,dy,dw,dh]=args;
  const iw=img.naturalWidth||img.width,ih=img.naturalHeight||img.height;
  dw=dw??iw;dh=dh??ih;const src=img.src||img.toDataURL('image/png');
  this.emit(`<svg x="${dx}" y="${dy}" width="${dw}" height="${dh}" viewBox="${sx} ${sy} ${sw} ${sh}" preserveAspectRatio="none" overflow="hidden" opacity="${this.globalAlpha}"><image width="${iw}" height="${ih}" href="${this.esc(src)}" preserveAspectRatio="none" style="image-rendering:${this.imageSmoothingEnabled===false?'pixelated':'auto'}"/></svg>`);}
 toSVG(caption){return `<svg xmlns="http://www.w3.org/2000/svg" width="${this.w}" height="${this.h}" viewBox="0 0 ${this.w} ${this.h}" role="img"><title>${this.esc(caption)}</title><desc>Valores em USD. Textos, candles, curvas e logo vetoriais; heatmap incorporado como imagem para preservar a suavização.</desc><defs>${this.defs.join('')}</defs>${this.parts.join('')}</svg>`;}
}
"""


VIEW_CONTROLS = r"""
// Same handle hit zones, minimum range and anchoring as LiquidationLevels.tsx.
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function sliderHit(v,r,x){const left=r.x+v.start*r.w,right=r.x+v.end*r.w;
 if(Math.abs(x-left)<=10)return 'left';if(Math.abs(x-right)<=10)return 'right';
 return x>=left&&x<=right?'move':'track';}
function sliderJump(v,fraction){const span=v.end-v.start,start=clamp(fraction-span/2,0,1-span);return {...v,start,end:start+span};}
function sliderDrag(v,mode,dx){
 if(mode==='left')return {...v,start:clamp(v.start+dx,0,v.end-.02)};
 if(mode==='right')return {...v,end:clamp(v.end+dx,v.start+.02,1)};
 const span=v.end-v.start,start=clamp(v.start+dx,0,1-span);return {...v,start,end:start+span};}
function wheelView(v,delta,priceFraction){const factor=delta>0?1.1:.9,xSpan=clamp((v.end-v.start)*factor,.02,1);
 let end=v.end,start=end-xSpan;if(start<0){start=0;end=xSpan;}
 const ySpan=clamp((v.yEnd-v.yStart)*factor,.02,2),anchor=clamp(priceFraction,0,1),relative=(anchor-v.yStart)/(v.yEnd-v.yStart);
 const yStart=clamp(anchor-relative*ySpan,-.5,1.5-ySpan);return {start,end,yStart,yEnd:yStart+ySpan};}
"""


CANVAS_CONTROLLER = r"""
const config = JSON.parse(document.getElementById('chart-config').textContent);
const data = config.data;
const dark = config.theme !== 'light';
const canvas = document.getElementById('canvas'), tip = document.getElementById('tip');
let ctx = canvas.getContext('2d');
const logo = new Image();
logo.onload = ()=>redraw();
logo.src = config.logo;
// Client logo (assets/*.svg), placed like printable_plot's logo_box.
const brandLogo = new Image();
let brandLogoReady = false;
if (config.brand && config.brand.logo) { brandLogo.onload = ()=>{brandLogoReady=true;redraw();}; brandLogo.src = config.brand.logo; }
// Same geometry as printable_plot.plot_alphractal: 16:9 figure (figsize 16x9 in = 1152 pt wide),
// figure fractions with a bottom-left origin and font sizes in points.
const BRAND_LAYOUT = {x0:.075, x1:.925, titleTop:.955, subtitleTop:.895, sourceBottom:.085, footerBottom:.025,
 logoBox:[.83,.025,.14,.065], figWidthPt:1152, titlePt:23, subtitlePt:10, sourcePt:11, footerPt:12, chartBottom:.20};
const TITLE_FONT='"STIXGeneral","STIX Two Text","STIX","Times New Roman",Times,serif';
const BODY_FONT='"DejaVu Sans",Verdana,Geneva,sans-serif';
const pt2px = pt => pt/BRAND_LAYOUT.figWidthPt*width;   // same relative scale as the Matplotlib figure
function brandColors(){ return dark ? {title:'#e4e6eb',subtitle:'#9aa3b3',text:'#9aa3b3'} : {title:'#241E18',subtitle:'#887767',text:'#76695D'}; }
function drawTextRun(parts, x, y){ // parts: [{text, bold, px}] drawn in sequence (bold labels, as in printable_plot)
 ctx.textAlign='left'; let cx=x;
 for(const part of parts){ ctx.font=(part.bold?'bold ':'')+part.px+'px '+BODY_FONT; ctx.fillText(part.text,cx,y); cx+=ctx.measureText(part.text).width; }
 return cx; }
function drawBranding(){
 const c=brandColors(), B=BRAND_LAYOUT, x0=B.x0*width;
 // Title: x0, top at 0.955 (va='top'), 23 pt, STIXGeneral bold, #241E18.
 const titlePx=pt2px(B.titlePt);
 ctx.fillStyle=c.title; ctx.textAlign='left'; ctx.font='bold '+titlePx+'px '+TITLE_FONT;
 ctx.fillText(config.title, x0, (1-B.titleTop)*height + titlePx*.78);
 // Subtitle: x0, top at 0.895, 10 pt, #887767.
 const subPx=pt2px(B.subtitlePt);
 ctx.fillStyle=config.demo?'#c58a35':c.subtitle; ctx.font=subPx+'px '+BODY_FONT;
 ctx.fillText(config.subtitle, x0, (1-B.subtitleTop)*height + subPx*.78);
 // Source: lower-left anchor at (x0, 0.085), 11 pt, bold label, #76695D.
 const srcPx=pt2px(B.sourcePt);
 ctx.fillStyle=c.text;
 drawTextRun([{text:'Source: ',bold:true,px:srcPx},{text:config.brand.source,bold:false,px:srcPx}], x0, (1-B.sourceBottom)*height - srcPx*.22);
 // Prepared for | Copyright: lower-left anchor at (x0, 0.025), 12 pt, bold labels.
 const ftPx=pt2px(B.footerPt), parts=[];
 if(config.brand.preparedFor) parts.push({text:'Prepared for: ',bold:true,px:ftPx},{text:config.brand.preparedFor,bold:false,px:ftPx});
 if(config.brand.copyright){ if(parts.length) parts.push({text:' | ',bold:false,px:ftPx}); parts.push({text:'Copyright: ',bold:true,px:ftPx},{text:config.brand.copyright,bold:false,px:ftPx}); }
 if(parts.length) drawTextRun(parts, x0, (1-B.footerBottom)*height - ftPx*.22);
 // Logo: logo_box=(0.83, 0.025, 0.14, 0.065), fitted like preserveAspectRatio xMidYMid meet.
 if(brandLogoReady && brandLogo.naturalWidth && brandLogo.naturalHeight){
  const [bx,by,bw,bh]=B.logoBox, boxX=bx*width, boxY=(1-by-bh)*height, boxW=bw*width, boxH=bh*height;
  const scale=Math.min(boxW/brandLogo.naturalWidth, boxH/brandLogo.naturalHeight), w=brandLogo.naturalWidth*scale, h=brandLogo.naturalHeight*scale;
  ctx.drawImage(brandLogo, boxX+(boxW-w)/2, boxY+(boxH-h)/2, w, h);
 }
}
const lut = heatmapLut(config.palette);
const cache = buildHeatmapCache(data, lut);
let view = {start:0,end:1,yStart:0,yEnd:1}, layout, width, height, hover=null, drag=null, tool='pan', pending=null, objects=[];
// As in printable_plot (background_alpha=0, figure_background_alpha=0): exported PNG/SVG have no opaque background.
let exporting=false;
const finite=v=>typeof v==='number' && Number.isFinite(v);
function label(message,r) { ctx.fillStyle=dark?TEXT_DARK:TEXT_LIGHT;ctx.font=FONT;ctx.textAlign='center';ctx.fillText(message,r.x+r.w/2,r.y+r.h/2); }
function draw(){
 const dpr=window.devicePixelRatio||1;
 ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);
 if(!exporting){ctx.fillStyle=dark?BG_DARK:BG_LIGHT;ctx.fillRect(0,0,width,height);} // background on screen only; exports stay transparent
 drawBranding();
 const {start,end,yStart,yEnd}=view;
 drawHeatmap(ctx,cache,layout.heatmap,start,end,yStart,yEnd,config.smoothing==='best');
 drawCandlesticks(ctx,data,layout.heatmap,start,end,yStart,yEnd);
 drawAxes(ctx,data,layout,start,end,yStart,yEnd,dark);
 if(finite(data.currentPrice))drawCurrentPriceLine(ctx,data,layout.heatmap,yStart,yEnd,dark);
 if(finite(data.currentPrice)&&finite(data.totalLongsSum)&&finite(data.totalShortsSum)){
  drawRightPanel(ctx,data,layout.rightPanel,dark,yStart,yEnd);drawKeyLevels(ctx,data,layout.keyLevels,dark);
 }else{label('Última data incompleta',layout.rightPanel);label('Key Levels · N/D',layout.keyLevels);}
 const begin=Math.floor(start*data.timestamps.length), stop=Math.ceil(end*data.timestamps.length);
 if(data.totalLongs.slice(begin,stop).every(finite)&&data.totalShorts.slice(begin,stop).every(finite)){
  drawAccumPanel(ctx,data,layout.accumPanel,start,end,dark);drawDeltaPanel(ctx,data,layout.deltaPanel,start,end,dark);
 }else{label('N/D · há datas sem preço ou células ausentes',layout.accumPanel);label('N/D · dados incompletos',layout.deltaPanel);}
 drawColorBar(ctx,data.maxZ,lut,layout.colorBar,dark);drawPanelLabels(ctx,layout,dark);drawScrollbar(ctx,layout.scrollbar,start,end,dark);
 drawUserObjects(ctx,objects,data,layout.heatmap,start,end,yStart,yEnd,dark);
 if(logo.complete&&logo.naturalWidth){const r=layout.heatmap,w=Math.min(360,r.w*.56),h=w*logo.naturalHeight/logo.naturalWidth;
  ctx.save();ctx.globalAlpha=.28;ctx.drawImage(logo,r.x+(r.w-w)/2,r.y+(r.h-h)/2,w,h);ctx.restore();}
 if(hover&&isInRect(hover.x,hover.y,layout.heatmap))drawCrosshair(ctx,hover.x,hover.y,layout.heatmap,dark);
 const first=Math.floor(start*(data.timestamps.length-1)),last=Math.ceil(end*(data.timestamps.length-1));
 const status=document.getElementById('view-status');
 const text='Período visível: '+new Date(data.timestamps[first]).toISOString().slice(0,16).replace('T',' ')+' — '+new Date(data.timestamps[last]).toISOString().slice(0,16).replace('T',' ')+' UTC';
 if(status.textContent!==text)status.textContent=text;
}
 let raf=0;function redraw(){cancelAnimationFrame(raf);raf=requestAnimationFrame(draw);}
function chartLayout(w,h){
 // Chart area between printable_plot's x0..x1 margins, below the subtitle and above Source/footer.
 const B=BRAND_LAYOUT, left=B.x0*w, innerW=(B.x1-B.x0)*w;
 const top=Math.round((1-B.subtitleTop)*h + (B.subtitlePt/B.figWidthPt*w) + 10);
 const bottom=Math.round((1-B.chartBottom)*h + 0.05*h);   // ~0.85h: the X axis and slider live inside this area
 const result=computeLayout(innerW,bottom-top);
 for(const r of Object.values(result))if(r&&typeof r==='object'&&'y' in r){r.y+=top;r.x+=left;}
 return result;}
function resize(){width=Math.max(620,document.getElementById('viewport').clientWidth);height=Math.round(width*9/16);const dpr=window.devicePixelRatio||1;canvas.width=width*dpr;canvas.height=height*dpr;canvas.style.width=width+'px';canvas.style.height=height+'px';layout=chartLayout(width,height);redraw();}
function coords(e){const r=canvas.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};}
function chartPoint(p){const r=layout.heatmap;return{x:view.start+(p.x-r.x)/r.w*(view.end-view.start),y:data.yValues[0]+(view.yEnd-(p.y-r.y)/r.h*(view.yEnd-view.yStart))*(data.yValues.at(-1)-data.yValues[0])};}
function reset(){view={start:0,end:1,yStart:0,yEnd:1};redraw();}
canvas.addEventListener('wheel',e=>{const p=coords(e);if(!isInRect(p.x,p.y,layout.heatmap))return;e.preventDefault();e.stopPropagation();
 const fraction=finite(data.currentPrice)?(data.currentPrice-data.yValues[0])/(data.yValues.at(-1)-data.yValues[0]):.5;
 view=wheelView(view,e.deltaY,fraction);redraw();},{passive:false});
canvas.addEventListener('pointerdown',e=>{const p=coords(e);if(isInRect(p.x,p.y,layout.heatmap)){
 if(tool==='hline'){objects.push({type:'hline',price:chartPoint(p).y});redraw();return;}
 if(tool==='trendline'){const q=chartPoint(p);if(!pending)pending=q;else{objects.push({type:'trendline',x1:pending.x,y1:pending.y,x2:q.x,y2:q.y});pending=null;redraw();}return;}
 drag={p,view:{...view},mode:'pan'};canvas.style.cursor='grabbing';canvas.setPointerCapture(e.pointerId);
 }else if(isInRect(p.x,p.y,layout.scrollbar)){let mode=sliderHit(view,layout.scrollbar,p.x);
  if(mode==='track'){view=sliderJump(view,(p.x-layout.scrollbar.x)/layout.scrollbar.w);mode='move';redraw();}
  drag={p,view:{...view},mode};canvas.style.cursor=['left','right'].includes(mode)?'ew-resize':'grabbing';canvas.setPointerCapture(e.pointerId);}});
canvas.addEventListener('pointermove',e=>{const p=coords(e);if(drag){const span=drag.view.end-drag.view.start,dy=drag.view.yEnd-drag.view.yStart;
 if(drag.mode!=='pan')view=sliderDrag(drag.view,drag.mode,(p.x-drag.p.x)/layout.scrollbar.w);
 else{view.start=clamp(drag.view.start-(p.x-drag.p.x)/layout.heatmap.w*span,0,1-span);view.end=view.start+span;
 view.yStart=clamp(drag.view.yStart+(p.y-drag.p.y)/layout.heatmap.h*dy,-.5,1.5-dy);view.yEnd=view.yStart+dy;}tip.hidden=true;redraw();return;}
 canvas.style.cursor=isInRect(p.x,p.y,layout.scrollbar)?(['left','right'].includes(sliderHit(view,layout.scrollbar,p.x))?'ew-resize':'grab'):(tool==='pan'?'grab':'crosshair');
 hover=p;if(isInRect(p.x,p.y,layout.heatmap)){const q=chartPoint(p),ti=clamp(Math.floor(q.x*data.timestamps.length),0,data.timestamps.length-1),pi=clamp(Math.round((q.y-data.yValues[0])/(data.yValues.at(-1)-data.yValues[0])*(data.yValues.length-1)),0,data.yValues.length-1);const val=data.zMatrix[pi][ti];
 tip.textContent=new Date(data.timestamps[ti]).toISOString().replace('T',' ').replace('.000Z',' UTC')+'\n'+formatPrice(data.yValues[pi])+' · '+(val==null?'N/D':formatCompactUSD(val));tip.style.left=Math.min(p.x+14,width-250)+'px';tip.style.top=(p.y+42)+'px';tip.hidden=false;
 }else tip.hidden=true;redraw();});
canvas.addEventListener('pointerup',()=>{drag=null;});canvas.addEventListener('pointercancel',()=>{drag=null;});canvas.addEventListener('pointerleave',()=>{hover=null;tip.hidden=true;redraw();});canvas.addEventListener('dblclick',reset);
document.getElementById('reset').onclick=reset;
document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>{tool=b.dataset.tool;pending=null;document.querySelectorAll('[data-tool]').forEach(x=>x.classList.toggle('selected',x===b));canvas.style.cursor=tool==='pan'?'grab':'crosshair';});
document.getElementById('clear-lines').onclick=()=>{objects=[];pending=null;redraw();};
// PNG and SVG are posted to the local server (same origin), which writes them to the exports folder.
async function saveExport(kind,content){const status=document.getElementById('export-note');status.textContent='Salvando '+kind.toUpperCase()+'…';
 try{const r=await fetch('/export',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind,content,stem:config.fileStem})});
  const j=await r.json();status.textContent=r.ok?(kind.toUpperCase()+' salvo em: '+j.path):('Erro ao salvar: '+(j.error||r.status));}
 catch(e){status.textContent='Não foi possível salvar na pasta do projeto (o app precisa estar rodando pelo Python).';}}
document.getElementById('png').onclick=()=>{const h=hover;hover=null;exporting=true;let data;try{draw();data=canvas.toDataURL('image/png');}finally{exporting=false;hover=h;redraw();}saveExport('png',data);};
document.getElementById('svg').onclick=async()=>{
 const status=document.getElementById('export-note'),button=document.getElementById('svg');button.disabled=true;
 try{
  await logo.decode();
  const original={ctx,width,height,layout,hover};let result;
  try{width=Math.max(1200,width);height=Math.round(width*9/16);layout=chartLayout(width,height);ctx=new SvgContext(width,height);hover=null;exporting=true;draw();
   result=ctx.toSVG(config.caption+' · USD');
  }finally{exporting=false;({ctx,width,height,layout,hover}=original);redraw();}
  await saveExport('svg',result);
 }catch(e){status.textContent='Não foi possível gerar o SVG. Tente novamente.';}finally{button.disabled=false;}
};
document.getElementById('full').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen?.();else document.exitFullscreen?.();};
new ResizeObserver(resize).observe(document.getElementById('viewport'));resize();
document.getElementById('canvas-status').textContent='Canvas carregado · '+data.timestamps.length+' datas × '+data.yValues.length+' níveis';
"""
