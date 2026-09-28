# Performance

Measured 28 September 2026. "Before" is the live site
(`https://kaejhee.github.io/training-terminal/`, v4.0.4). "After" is this
branch, served as static files the way GitHub Pages does.

Everything that shipped is $0. GitHub Pages for a public repo does not
need a credit card. No paid host and no paid tier was added.

Throttled rows use Chrome with an 80 ms round trip and a 1.6 Mbit/s cap.
Unthrottled "after" times are on localhost and are not comparable to
GitHub's network. They are still the right split of download versus
startup versus grading, because localhost makes the download cheap and
leaves the CPU time visible.

## Where the time goes

| Phase | Before (live, throttled) | After |
|---|---|---|
| Page load until the prompt | 1.6 s, while a 6.06 MB download is already running | 3.6 s throttled without gzip (local server). Unthrottled localhost: the prompt is up in about 0.1 s. xterm.js itself is 289 KB and took 4 ms from disk. |
| SQL engine | Ready at 7.0 s. sql.js came from cdnjs and shared the pipe with Pyodide. | Wasm is 658 KB, local. Throttled ready time 4.6 s wall, mostly the download. A grade after that is 4 ms. |
| JavaScript engine | Ready with the page (1.6 s). No extra download. | Same. A grade is a fresh worker, well under the 3 s execution cap for the reference answers. |
| Rust engine | Ready with the page. No runtime. | Same. A grade is a string compare. |
| Python download | Inside the 6.06 MB boot download. | Not started until Start Python is hovered, focused, or chosen. Wire size below. |
| Python startup | Ready at 30.6 s throttled, during boot. | Unthrottled, hover-to-ready is 1.2 s (download plus wasm compile). A click after that returns in 0 ms. |
| Python grade, runtime already up | — | 16 ms for `py_exp_04`, including its hidden checks. |

The slow part is the Python download. Grading is not. Startup after the
bytes are here is about a second of wasm compile on this machine, then
each answer is tens of milliseconds.

### Python bytes, on the wire

jsDelivr serves Pyodide 0.29.5 with Brotli. Measured response sizes:

| File | Uncompressed | On the wire |
|---|---:|---:|
| `pyodide.asm.wasm` | 8,647,684 | 2,672,398 (Brotli) |
| `python_stdlib.zip` | 2,424,003 (the zip; the files inside are 9.2 MB) | 2,424,003 |
| `pyodide.asm.js` | 1,074,322 | ~226 KB in Chrome |
| `pyodide.js` + lockfile | 141 KB | ~34 KB in Chrome |
| **Total the browser transfers** | | **about 5.4 MB** |

No scientific packages are in that total. `loadPyodide` is already the
core distribution (`fullStdLib` defaults to false, so ssl, lzma, sqlite3,
and the test suite stay out). The 5.4 MB is the interpreter plus the
stdlib zip.

## Replacing the Python download

### MicroPython compiled to WebAssembly

A current MicroPython wasm build is a few hundred kilobytes instead of
5.4 MB. It would not grade every Python question correctly.

MicroPython is a Python 3 subset. These reference answers use modules it
does not ship:

| Question | What it needs | On MicroPython |
|---|---|---|
| `py_exp_09` | `collections.Counter` | Missing. MicroPython's `collections` has `deque`, `OrderedDict`, and `namedtuple`, not `Counter`. |
| `py_exp_10` | `collections.defaultdict` | Missing. |
| `py_mas_05` | `functools.reduce` | Missing. MicroPython's `functools` has `partial` and `wraps`, not `reduce`. |
| `py_mas_08` | `dataclasses.dataclass` | Missing. There is no `dataclasses` module. |

That is 4 of 50 questions failed before any other difference. Dict unpacking
in `py_mas_01` (`{**m, 'rank': i+1}`) is also newer than the core language
MicroPython started from, so it is not a sure pass. Classes, `@property`,
`@staticmethod`, generators, f-strings, and `nonlocal` on a current build
would likely pass. "Likely" is not every question.

A MicroPython build with extra frozen modules still would not include
`dataclasses` without a large backport. **Not implemented.**

### A trimmed Pyodide

The download is already trimmed of the packages people assume are the
bulk (numpy, pandas, matplotlib). Those are separate files and this site
never requests them.

What is left to trim is inside `python_stdlib.zip` (2.42 MB). The largest
trees the questions do not import:

| Tree | Uncompressed size |
|---|---:|
| encodings | 1.42 MB (must stay; Python cannot decode text without it) |
| asyncio | 519 KB |
| email | 386 KB |
| xml | 303 KB |
| multiprocessing | 287 KB |
| unittest | 253 KB |
| http, logging, urllib, pydoc, tarfile, argparse, html, doctest | about 1.1 MB combined |

Dropping the unused trees and keeping encodings is on the order of
**0.7 MB** off the 2.42 MB zip, so the 5.4 MB transfer becomes about
**4.6 MB**. The 2.67 MB Brotli wasm does not shrink unless Pyodide itself
is rebuilt. A hand-edited zip can also break Pyodide's importer, because
the runtime and the stdlib are built together.

Every current Python question would still grade on stock Pyodide, which
is what CI runs. A custom zip would still grade them only if `collections`,
`functools`, `dataclasses`, `io`, and the import machinery stay intact.
**Not done in this PR.** It is a next step, and the win is about 15
percent of the Python download, not an order of magnitude.

## Free CDN and cache headers

| Cache | What it does here | Limit |
|---|---|---|
| jsDelivr | Hosts Pyodide. `cache-control: public, max-age=31536000`. The wasm response was a Cloudflare HIT. No account and no card. | The right free CDN for the one blob we do not vendor. Self-hosting it on GitHub Pages would use a 10 minute cache instead of a year. |
| GitHub Pages | The live HTML response is `cache-control: max-age=600` (10 minutes), `server: GitHub.com`. Pages does not read a `_headers` file, so this repo cannot set a longer edge cache. | $0 for a public repo. Repeat visits inside 10 minutes can be a browser cache hit. After that, the service worker is what keeps wasm and xterm local. |
| Cloudflare Pages free | A free static host with its own edge cache. No card to start. Moving the site there is a hosting change, and it was not faster than Pages plus the service worker in any measurement we have. | Out of this PR. Pages stays the host. |

The service worker is the long-lived cache Pages will not give us.
Second visit: prompt in 55 ms, heavy files `transferSize` 0, HTML still
network-first so a deploy is not stuck for a year.

## WebAssembly, and what can be computed ahead of time

| Engine | Runtime | Computed at build time |
|---|---|---|
| SQL | sql.js wasm, 658 KB, vendored, started after first paint | The expected query is already in the question. Running it twice (user, then expected) on a fresh database is 4 ms. Snapshotting the expected rows would save a couple of milliseconds. Not worth a second source of truth. |
| Python | Pyodide wasm, lazy | Expected values are already in the question. The user's code still has to run. Nothing else to pre-grade. |
| JavaScript | No wasm. A fresh worker per answer. | Same. The reference solutions in `tests/js_solutions.json` are for CI, not a shortcut around running the answer. |
| Rust | No wasm, on purpose. There is no compiler in the page. | The canonical string, the alternatives, and the 319 cases are the precomputation. A grade does not download or compile anything. |

## Static assets

| Asset | Treatment | Result |
|---|---|---|
| `index.html` | Lesson bundle split out. Pages gzips the shell to about 77 KB. | Shipped. |
| xterm | Vendored 5.5.0. The published `xterm.min.js` is the same 289 KB. Gzip on Pages takes it to about 67 KB. | Minified file skipped. No smaller build. |
| sql.js wasm | Vendored. Gzip about 322 KB. Not preloaded. | Preload made the throttled prompt slower (5.9 s vs 3.6 s). |
| Fonts | Three woff2 files, latin only, `font-display: swap`. About 67 KB and already compressed. | Shipped. |
| Images | Favicon and `og.png`. The social image is not requested by the app. | Nothing further to cut on the first screen. |
| Brotli of our own files | Pages gzips. It will not serve a hand-built `.br` as the page. | Skipped. |
| Preload hints | Tried for wasm, xterm, and the bundle. | Skipped. Measured slower. |
| Prefetch | Hover or focus on Start Python starts Pyodide without setting the header to LOADING. | **Shipped in this pass.** A click with no prior hover still pays the 1.2 s. A hover that finishes first makes the click's wait 0 ms. |

## Code splitting and client cache

| Split | Status |
|---|---|
| Python runtime | Separate `pyodide-worker.js`, loaded only for that track. |
| SQL runtime | Separate wasm, after first paint. |
| Lessons | `content-bundle.js`, after the prompt. |
| Question bank | Still inside the shell. The shell gzips to about 77 KB. Pulling the four tracks into their own files would save on the order of a few dozen KB and cost a round trip. Next step, not a first-screen win. |
| Service worker / Cache API | `sw.js` precaches the shell, lessons, fonts, xterm, and sql.js. jsDelivr is cache-first after the first Python load. HTML is network-first. |

## Ranked plan

Ranked by the speedup a visitor actually feels, then by how much work
and risk it takes. Cost of every row is $0.

| Rank | Change | Expected speedup | Effort | This PR |
|---|---|---|---|---|
| 1 | Do not download Python until that track is chosen | Removes 5.4 MB and the 30.6 s throttled boot wait | Done | Shipped |
| 2 | Self-host xterm, sql.js, and fonts | Terminal works with jsDelivr blocked. SQL ready 4.6 s throttled instead of 7.0 s | Done | Shipped |
| 3 | Service worker | Second visit prompt in 55 ms | Done | Shipped |
| 4 | Split lessons out of the HTML, and do not preload the wasm | Throttled prompt 5.9 s with preloads, 3.6 s without | Done | Shipped |
| 5 | Start SQL after first paint | Prompt does not wait on wasm compile | Done | Shipped |
| 6 | Start the Python download on hover or focus of Start Python | The 1.2 s startup overlaps the time the pointer is on the button. Click after a finished hover waits 0 ms. Header stays ONLINE. | Small | **Shipped now** |
| 7 | Custom stdlib zip, dropping unused modules | About 0.7 MB off the Python download (~15%). Encodings and the wasm stay. | High, and a bad zip breaks imports | Next |
| 8 | Split the question bank per track | A few dozen KB off a shell that is already ~77 KB gzipped | Medium | Next, only if a profile says the shell parse matters |
| 9 | MicroPython instead of Pyodide | Would cut megabytes | — | **Do not.** `py_exp_09`, `py_exp_10`, `py_mas_05`, and `py_mas_08` would not grade. |
| 10 | Precompute SQL expected rows, or minify the page script | A few milliseconds, or tens of KB off a gzipped 77 KB shell | Medium | Not worth it |
| 11 | Move the host to Cloudflare Pages, or grade on Vercel Hobby / Workers free | Not a measured win. Warm grades are 4–16 ms locally; a function adds a round trip. Workers free allows 10 ms of CPU, which cannot run Pyodide. Hobby is non-commercial only, and a team with a card can bill. | — | Do not. Stay on GitHub Pages. |

## Recommendation

Keep GitHub Pages. The visitor-facing wait that remains is the first
Python download, and only for someone who opens that track. The safe
cuts for that wait are already in: lazy load, jsDelivr's year-long cache,
the service worker after the first run, and a hover/focus head start.

Next, if Python's first open is still too slow: build a stdlib zip that
drops the unused trees listed above, host it next to a stock Pyodide wasm,
and re-run the 50 Python answer keys before trusting it. Do not switch
the runtime to MicroPython. Do not add a server.
