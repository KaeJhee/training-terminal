# Performance

Measured 28 September 2026. The "before" column is the live site
(`https://kaejhee.github.io/training-terminal/`, v4.0.4). The "after"
column is this branch, served the same way GitHub Pages does: static
files, no server app.

Throttled rows use Chrome with an 80 ms round trip and a 1.6 Mbit/s
download cap, so the times are comparable. Unthrottled "after" times are
against `localhost` and are not comparable to GitHub's network.

## What a visit downloads

| | Before (live) | After (this branch) |
|---|---:|---:|
| Until the prompt is on screen | 6.06 MB transferred, because Pyodide starts immediately | 1.60 MB uncompressed for the shell, fonts, xterm, and SQL. Python is not in that number. |
| Gzipped text (GitHub Pages compresses HTML and JS; wasm and woff2 barely shrink) | The old `index.html` alone was about 123 KB on the wire | Shell + xterm + lesson bundle gzip to about 77 KB + 67 KB + 47 KB. SQL wasm gzips from 658 KB to 322 KB. |
| When you open Python | Already paid, during boot | 5.38 MB from jsDelivr (Pyodide 0.29.5 wasm + stdlib), once |
| Second visit, service worker installed | Full download again | Prompt in 55 ms. Transfer was the HTML only (network-first); wasm, xterm, and fonts came from the cache (`transferSize` 0 for those). |

## When it becomes usable

Same throttle on both.

| | Before | After |
|---|---:|---:|
| Prompt on screen | 1.6 s | 3.6 s in the ungziped local test. On GitHub Pages the blocking files gzip to roughly the same size as today's page plus the old minified xterm, so this should land near the old prompt time. The local number is slower because `python3 -m http.server` does not compress. |
| SQL ready | 7.0 s (sharing the pipe with the Pyodide download) | 4.6 s wall time in the ungziped test, and it no longer waits on a CDN |
| JavaScript and Rust ready | 1.6 s (they need no download beyond the page) | Ready when the shell is ready |
| Python ready | 30.6 s, during boot, even if you never use Python | Not loaded until you start Python. On an unthrottled link that was 1.2 s and 5.38 MB. |
| Grade one SQL answer (engine already up) | — | 7 ms |
| Grade one Python answer (runtime already up) | — | 12 ms |

## What changed in the page, and why

- **Python loads only when that track starts.** This is the large cut: about 5 MB and the 30 s throttled wait leave the first screen.
- **xterm, sql.js, and the fonts are files in the repo.** A blocked CDN no longer leaves a blank terminal. SQL does not wait on cdnjs.
- **The lesson bundle is a separate file, fetched after the prompt.** `index.html` dropped from about 518 KB to 325 KB.
- **SQL wasm is not preloaded.** Preloading it competed with xterm and made the throttled prompt slower (5.9 s). Without the preload the prompt was 3.6 s in the same test.
- **A service worker caches same-origin files and jsDelivr.** The second visit rendered in 55 ms, with the heavy files served from cache. HTML stays network-first so a new deploy is not stuck behind an old page.

xterm 5.5's published `xterm.min.js` is the same size as the file we vendor (about 289 KB). There was no smaller build to switch to. GitHub Pages will gzip it to about 67 KB.

## Would a backend make this faster?

No, not in a way that is worth leaving GitHub Pages.

Grading is already local. A warm SQL answer is 7 ms and a warm Python answer is 12 ms. A serverless function would add a network round trip to every one of those, and it would be slower.

The only wait a server could remove is the first Python download (5.38 MB, 1.2 s on a fast link, tens of seconds on a slow one). That means running strangers' Python on a server. It costs money any time someone holds a loop open, it is an untrusted-code problem, and it means the site is no longer a static GitHub Pages project. SQL, JavaScript, and Rust would not get faster.

A backend would help one thing that is not speed: progress does not sync across devices today. If that becomes the goal, a small function that stores the JSON export (the same object `localStorage` already holds) is enough. It should not execute code.

**Recommendation:** keep hosting on GitHub Pages. Do not add a server to chase UI speed.

### If progress sync is wanted later

- `POST /api/progress` with the exported JSON, after the same shape check the page already uses (`completed` object, `activity` array).
- Auth is the whole design. A private gist, or a logged-in store Kris already has for another site, avoids inventing accounts here.
- The page stays static. The function is a blob store, not a Python runner.
- Cost stays near zero if it only writes a few kilobytes of JSON.
