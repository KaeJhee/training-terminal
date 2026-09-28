# Performance

Measured 28 September 2026. The "before" column is the live site
(`https://kaejhee.github.io/training-terminal/`, v4.0.4). The "after"
column is this branch, served as static files the way GitHub Pages does.

Everything here is $0. GitHub Pages for a public repo does not need a
credit card. No paid host, no paid tier, and no account with a card on
file was added.

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

## Free speed options

Hosting stays on GitHub Pages. A "gain" is either a measurement from the
runs above or a stated estimate. Nothing in the skipped list was left out
because it costs money. They were slower, too small to notice, or they
would put a card on file.

| Option | Gain | Decision |
|---|---|---|
| Lazy-load the Python engine | Removes 5.38 MB from boot, and the 30.6 s throttled wait, for anyone who does not open Python. | **Implemented.** Pyodide loads on `start python`. |
| Self-host xterm, sql.js, and the fonts | The terminal still paints when jsDelivr is blocked. SQL ready in 4.6 s throttled, versus 7.0 s on the live site while Pyodide was sharing the pipe. | **Implemented.** Files live in `vendor/`. |
| Split the lesson bundle out of `index.html` | Shell went from about 518 KB to 325 KB (gzip about 77 KB). The 204 KB bundle (gzip about 47 KB) loads after the prompt. | **Implemented.** `content-bundle.js`. |
| Rely on GitHub Pages gzip | xterm 289 KB gzips to about 67 KB. SQL wasm 658 KB gzips to 322 KB. The shell gzips to about 77 KB. | **Already how Pages works.** No extra tool, no cost. |
| Service worker for repeat visits | Second visit: prompt in 55 ms. Heavy files report `transferSize` 0. | **Implemented.** `sw.js`. HTML is network-first so a new deploy is not stuck. |
| Prewarm SQL after first paint | The prompt does not wait on wasm compile. In the throttled test SQL was ready about 1 s after the prompt (4.6 s wall). | **Implemented.** `requestIdleCallback`, then `sql.init()`. |
| Preload sql wasm, xterm, and the lesson bundle | Throttled prompt was **5.9 s with the preloads and 3.6 s without.** They competed with the files the prompt needs. | **Skipped.** Measured slower. |
| Prewarm Python in the background after first paint | Puts the 5.38 MB download back on every visitor. That is the 30.6 s throttled cost, even for people who never open Python. | **Skipped.** It undoes the lazy-load win. |
| Ship the published `xterm.min.js` | The file on jsDelivr is the same size as the one we vendor (about 289 KB). Pages gzip is what shrinks it. | **Skipped.** No smaller build exists. |
| Brotli, or a compressor in the build | GitHub Pages gzips the response. It will not serve a hand-rolled `.br` file as `index.html`. | **Skipped.** Would not change the bytes on the wire. |
| Split the question bank out of the shell | The shell already gzips to about 77 KB. A second request costs about one round trip (80 ms in the throttle) and adds a new way for the page to fail. | **Skipped.** No measured first-screen win. |
| Keep sql.js 1.10.3 for a smaller wasm | Old CDN wasm was 277 KB. 1.14.2 is 658 KB raw / 322 KB gzip. On the throttle that is a fraction of a second, and SQL is still faster than the live site. | **Skipped.** The review asked for the library update, and the SQL answer keys pass on 1.14.2. |
| Preconnect to jsDelivr when the Python button is hovered | About one round trip, ~80 ms, off a Python start. The 2.6 MB wasm transfer dominates the 1.2 s unthrottled init. | **Skipped.** Too small to notice next to the download. |
| Minify the page script inside `build.py` | Gzip already takes the shell to about 77 KB. A minifier might save tens of KB more and would be a new fragile build step. | **Skipped.** Not a user-visible wait. |
| Move the static host to Vercel or Cloudflare Pages | Not measured as faster than GitHub Pages plus the service worker. | **Skipped.** This PR stays on GitHub Pages, which is $0 and needs no card. |

## Free-tier backends that were considered and not added

Grading is already local: 7 ms for a warm SQL answer, 12 ms for a warm
Python answer. A function call adds a network round trip, so it makes
those answers slower. The only wait a server could remove is the first
Python download (5.38 MB, 1.2 s on a fast link, about 30 s on the
throttle). Running learner code to avoid that download is a bad fit for
a free function, and it would mean leaving GitHub Pages.

Neither option is in this PR.

### Vercel Hobby

Published limits (https://vercel.com/docs/plans/hobby, read 28 September 2026):

- $0, and signing up for Hobby does not require a card.
- Included each month: 100 GB fast data transfer, 1,000,000 edge requests, 1,000,000 function invocations, 4 CPU-hours, 360 GB-hours of provisioned memory. Function max duration 300 seconds.
- Over the cap, the feature pauses until 30 days have passed. Hobby itself does not have an overage bill.
- Fair use: **non-commercial, personal use only.**

Charge risk: upgrading to Pro, or starting the Pro trial, asks for a card. Pro is $20 per developer seat, and a team with a card can turn on on-demand usage that bills past the included credit. Kris already serves economic.ghoststrategies.io from Vercel. Putting this site on that same team is how a card already on file would get charged. Hobby is also the wrong terms for a public site tied to an RIA, because the plan is personal and non-commercial.

A Python grader on a Hobby function is also how a visitor's infinite loop spends the 4 CPU-hour cap and pauses the project. That is not a speedup.

### Cloudflare Workers free

Published limits (https://developers.cloudflare.com/workers/platform/pricing/, updated 7 July 2026):

- $0. The free plan does not require a credit card. Going over the cap returns an error. It does not auto-charge.
- 100,000 requests per day. 10 ms of CPU time per invocation. 128 MB memory.
- The paid Workers plan starts at $5 per month, then $0.30 per extra million requests and $0.02 per extra million CPU-milliseconds. That plan is what puts a bill on the account.

10 ms of CPU cannot start Pyodide or grade a real Python or SQL answer. Static assets on Workers are not the reason to move: GitHub Pages already serves those for $0.

### Progress across devices

That is not a speed feature. `localStorage` is $0 and needs no account. A sync service is out of this PR. If it is ever added, it has to stay on a free store with no card attached. Do not hang it off the Vercel team that already hosts another site.

**Recommendation:** keep the site on GitHub Pages. The static changes above are the speedup. Do not add a backend, a paid tier, or any account that asks for a credit card.
