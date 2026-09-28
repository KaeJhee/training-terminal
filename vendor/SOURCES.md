# Vendored libraries

These files are served from this repository so the terminal shell and SQL
engine work when a CDN is blocked. Upstream licenses apply (MIT).

| File | Upstream | Version |
|---|---|---|
| `xterm/xterm.js`, `xterm/xterm.css` | [@xterm/xterm](https://www.npmjs.com/package/@xterm/xterm) | 5.5.0 |
| `xterm/addon-fit.js` | [@xterm/addon-fit](https://www.npmjs.com/package/@xterm/addon-fit) | 0.10.0 |
| `sql.js/sql-wasm.js`, `sql.js/sql-wasm.wasm` | [sql.js](https://github.com/sql-js/sql.js) | 1.14.2 |
| `fonts/*` | [DM Sans](https://fonts.google.com/specimen/DM+Sans), [DM Mono](https://fonts.google.com/specimen/DM+Mono) (SIL Open Font License) | latin subsets |

xterm 6 changes the browser bundle shape the line editor is written against,
so this stays on the 5.5 line of the renamed `@xterm/xterm` package (up from
the old `xterm@5.3.0` CDN build).

Pyodide stays on jsDelivr and loads only when the Python track starts.
