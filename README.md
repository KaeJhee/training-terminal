# Ghost Training Terminal

A Bloomberg-style terminal for practicing **Python** and **SQL** from your browser. Part of the Ghost Strategies LLC terminal suite (alongside the Garage, Portfolio, and Budget terminals).

![version](https://img.shields.io/badge/version-3.7-e8a020?style=flat-square)
![license](https://img.shields.io/badge/license-MIT-8a5e13?style=flat-square)

---

## What it does

- **100 hand-authored questions**: 10 per tier × 5 tiers × 2 tracks (Python, SQL).
- **Real code execution**: Python runs via [Pyodide](https://pyodide.org/) in-browser; SQL runs via [sql.js](https://sql.js.org/).
- **Two-button answer flow**: type your answer, click **▶ RUN** to preview results, click **✓ SUBMIT** to grade. Enter is always a newline — nothing grades until you explicitly submit.
- **Gated progression**: Introductory → Amateur → Intermediate → Experienced → Master. Each tier unlocks after you clear the 10 questions in the previous one.
- **Bloomberg-style UI**: watchlist with tier progress, live KPIs (attempts, accuracy, streak, session timer), ticker tape, activity feed, inline SQL schema reference, persistent action bar with Run / Submit / Hint buttons.
- **In-track database inspection** (SQL): `tables`, `describe <table>`, `peek <table>` for column-aligned previews of the training DB before you commit to an answer.
- **Persistent**: progress saves to `localStorage`. Export/import as JSON.
- **Mobile-friendly**: responsive breakpoints at 900, 720, and 600px. iOS hardened (90s Pyodide timeout, pattern-match fallback if Pyodide fails).
- **Single file**: one `index.html`, zero build step, deployable anywhere that serves static files.

---

## Running it locally

No build step. Open `index.html` in a modern browser, or serve it locally:

```bash
# Python 3 (if installed):
python3 -m http.server 8000
# Then open http://localhost:8000

# Or Node's http-server:
npx http-server -p 8000
```

The first time you run it, Pyodide downloads ~10MB. SQL is ready instantly.

---

## Deploying it

Because it's a single static file, anywhere will do:

- **GitHub Pages** — push to a repo, enable Pages in Settings. Free. (See [GitHub setup below](#pushing-this-to-github-step-by-step).)
- **Netlify / Vercel** — drag-drop the file, or connect the GitHub repo.
- **Cloudflare Pages** — same idea, connect a repo.

---

## Wiring the cross-terminal nav pills

The top of the app has four nav pills: `GARAGE · PORTFOLIO · BUDGET · TRAINING`. Right now three of them point to `#` placeholders. Once you have the other terminals deployed, wire them up like this:

### Step 1 — Open `index.html` in a text editor

Find this block (near the top of the `<script>` section — around line 480):

```javascript
const PRODUCT_NAV = [
  { key:'garage',    label:'GARAGE',    url:'#', active:false },
  { key:'portfolio', label:'PORTFOLIO', url:'#', active:false },
  { key:'budget',    label:'BUDGET',    url:'#', active:false },
  { key:'training',  label:'TRAINING',  url:'#', active:true  },
];
```

### Step 2 — Replace the `#` with your real URLs

For example, if your terminals are hosted at Netlify subdomains:

```javascript
const PRODUCT_NAV = [
  { key:'garage',    label:'GARAGE',    url:'https://ghost-garage.netlify.app',    active:false },
  { key:'portfolio', label:'PORTFOLIO', url:'https://ghost-portfolio.netlify.app', active:false },
  { key:'budget',    label:'BUDGET',    url:'https://ghost-budget.netlify.app',    active:false },
  { key:'training',  label:'TRAINING',  url:'#',                                   active:true  },
];
```

Or if they share a domain with path prefixes:

```javascript
const PRODUCT_NAV = [
  { key:'garage',    label:'GARAGE',    url:'/garage',    active:false },
  { key:'portfolio', label:'PORTFOLIO', url:'/portfolio', active:false },
  { key:'budget',    label:'BUDGET',    url:'/budget',    active:false },
  { key:'training',  label:'TRAINING',  url:'#',          active:true  },
];
```

### Rules

- **Leave TRAINING's `url` as `'#'` and `active` as `true`** in *this* terminal's file. The active pill doesn't navigate — it marks "you are here."
- In the **other three terminals**, you'd flip it: their own pill gets `active:true, url:'#'`, and the other three including training get real URLs.
- Label text and order can be anything. Changing `label` changes what shows in the header; `key` is internal and not displayed.

### Step 3 — Save and reload

Save the file, hard-refresh the browser (Cmd/Ctrl + Shift + R), and click a pill. It should navigate to the URL you set.

---

## Pushing this to GitHub (step by step)

If you've never used git from the command line, follow along. If you already have a GitHub account and git installed, skip to step 4.

### Step 1 — One-time setup

Install git if you don't have it. Check by opening Terminal (Mac) or PowerShell (Windows) and typing:

```bash
git --version
```

- **If you see a version number**, you're good.
- **If you see "command not found"** or an error:
  - Mac: `xcode-select --install`, then follow the prompt.
  - Windows: download [Git for Windows](https://git-scm.com/download/win) and run the installer with default options.
  - Linux: `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora).

Then tell git who you are (use the email your GitHub account uses):

```bash
git config --global user.name "Kristopher Gallow"
git config --global user.email "you@example.com"
```

### Step 2 — Create the repo on GitHub

1. Go to [github.com/new](https://github.com/new).
2. **Repository name**: `ghost-training-terminal` (or whatever you like).
3. **Visibility**: Public if you want GitHub Pages on the free tier, Private if you don't need Pages.
4. **Do NOT check** "Initialize this repository with a README" — we already have one.
5. Click **Create repository**.

GitHub will show a page with commands. You'll use the HTTPS URL that ends in `.git`. It looks like:

```
https://github.com/YOUR-USERNAME/ghost-training-terminal.git
```

Keep that page open.

### Step 3 — Unzip the project

Unzip `ghost-training-terminal.zip` wherever you keep your projects. You should end up with a folder like:

```
~/Projects/ghost-training-terminal/
├── index.html
├── README.md
├── LICENSE
└── .gitignore
```

### Step 4 — Turn the folder into a git repo and push

Open Terminal (or PowerShell on Windows), and `cd` into the folder:

```bash
cd ~/Projects/ghost-training-terminal
```

Then run these commands, one at a time, in order:

```bash
# 1. Turn this folder into a git repo
git init

# 2. Make the default branch "main" (matches GitHub's default)
git branch -M main

# 3. Stage all files
git add .

# 4. Commit them with a message
git commit -m "Initial commit: Ghost Training Terminal v3.1"

# 5. Tell git where to push. REPLACE the URL below with your own.
git remote add origin https://github.com/YOUR-USERNAME/ghost-training-terminal.git

# 6. Push it up
git push -u origin main
```

On the last step, git will prompt you to authenticate. **GitHub no longer accepts passwords** for command-line git — you'll need either:

- **A Personal Access Token** (recommended for beginners): go to [github.com/settings/tokens](https://github.com/settings/tokens), click *Generate new token (classic)*, give it the `repo` scope, copy the token, paste it when git prompts for a password.
- **GitHub CLI** (simpler long-term): install [gh](https://cli.github.com/), run `gh auth login`, then re-run `git push`.
- **SSH keys** (most secure, one-time setup): see [GitHub's SSH docs](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

Refresh your GitHub repo page — all the files should be there.

### Step 5 — (Optional) Turn on GitHub Pages

If you want a public URL for your terminal:

1. On GitHub, go to your repo → **Settings** → **Pages** (left sidebar).
2. Under *Build and deployment*, set **Source** to `Deploy from a branch`.
3. Set **Branch** to `main` and folder to `/ (root)`. Click **Save**.
4. Wait ~60 seconds, then refresh. At the top you'll see:
   ```
   Your site is live at https://YOUR-USERNAME.github.io/ghost-training-terminal/
   ```
5. That URL is your deployed terminal. Put it into the other three terminals' `PRODUCT_NAV` arrays so their `TRAINING` pill links here.

### Making future changes

After the initial push, the flow for updates is:

```bash
# edit files...

git add .
git commit -m "Describe what you changed"
git push
```

GitHub Pages redeploys within a minute.

---

## Project structure

```
ghost-training-terminal/
├── index.html        # The entire app. Single file, zero build step.
├── README.md         # This file.
├── LICENSE           # MIT.
├── CHANGELOG.md      # Version history and shipped changes.
├── PROMPTS.md        # Version-by-version prompts for future development work.
└── .gitignore        # Excludes editor and OS cruft.
```

---

## Tech stack

| Piece             | Library                            | Version |
| ----------------- | ---------------------------------- | ------- |
| Terminal emulator | [xterm.js](https://xtermjs.org/)   | 5.3.0   |
| Python runtime    | [Pyodide](https://pyodide.org/)    | 0.26.4  |
| SQL engine        | [sql.js](https://sql.js.org/)      | 1.10.3  |
| Fonts             | DM Mono, DM Sans (Google Fonts)    | —       |

All loaded from public CDNs at runtime. No bundler.

---

## Commands reference

In the base terminal:

| Command           | What it does                             |
| ----------------- | ---------------------------------------- |
| `help`            | Show the command list                    |
| `status`          | Show current track, rank, and progress   |
| `start python`    | Begin the Python track                   |
| `start sql`       | Begin the SQL track                      |
| `schema`          | Show the SQL training database schema    |
| `clear`           | Clear the screen                         |
| `export`          | Dump progress as a JSON string           |
| `import <json>`   | Restore progress from exported JSON      |
| `reset`           | Wipe all saved progress (with confirm)   |

Inside a track — **answer flow**:

| Input                    | What it does                                                            |
| ------------------------ | ----------------------------------------------------------------------- |
| **▶ RUN** button         | Execute whatever's in the buffer (query OR meta-command)                |
| **✓ SUBMIT** button      | Grade query; meta-commands in the buffer just execute                   |
| **💡 HINT** button       | Show the hint for the active question                                   |
| `Enter`                  | **Newline only** — never executes anything                              |
| `Shift+Enter`            | Newline (same as Enter)                                                 |
| `Ctrl+Enter`             | Keyboard shortcut for Run                                               |
| `Ctrl+Shift+Enter`       | Keyboard shortcut for Submit                                            |
| `Tab`                    | Insert 4 spaces for indentation                                         |

Inside a track — **line editing** (works mid-buffer, including across line breaks):

| Input                    | What it does                                                            |
| ------------------------ | ----------------------------------------------------------------------- |
| `←` `→`                  | Move cursor left / right (wraps across newlines)                        |
| `Home` / `Ctrl+A`        | Jump to start of current line                                           |
| `End` / `Ctrl+E`         | Jump to end of current line                                             |
| `Backspace`              | Delete the character before the cursor                                  |
| `Delete`                 | Delete the character at the cursor                                      |
| `Ctrl+K`                 | Delete from cursor to end of current line                               |
| `Ctrl+U`                 | Delete from start of current line to cursor                             |
| `↑` / `↓`                | Cycle through input history                                             |
| `Ctrl+C`                 | Abort current context                                                   |

Inside a track — **meta-commands** (type alone in the buffer, then click ▶ RUN or press Ctrl+Enter):

| Input               | What it does                                     |
| ------------------- | ------------------------------------------------ |
| `hint`              | Show the hint for the current question           |
| `schema`            | Show the SQL schema overview                     |
| `help`              | Show the in-track help card                      |
| `exit`              | Return to base terminal                          |
| `clear`             | Clear the screen                                 |

Inside a track — **SQL database inspection** (SQL track only, type alone + click ▶ RUN):

| Input                 | What it does                                         |
| --------------------- | ---------------------------------------------------- |
| `tables`              | List all tables in the training DB                   |
| `describe <table>`    | Show columns, types, and constraints for a table     |
| `peek <table>`        | Sample the first 5 rows of a table (column-aligned)  |

Keyboard:

- `Tab` — complete commands (base terminal only)
- `↑` / `↓` — cycle input history
- `Ctrl+C` — abort current context

### Typical SQL workflow

```
sql> tables
  customers  mechanics  vehicles  work_orders

sql> describe customers
  id     INTEGER  PRIMARY KEY
  name   TEXT     NOT NULL
  phone  TEXT

sql> peek customers
  id  name               phone
  ──  ─────────────────  ────────────
  1   Kristopher Gallow  210-555-0101
  2   Alice Chen         512-555-0102
  ...

sql> SELECT name         ← Enter for newline
...> FROM customers      ← Enter for newline
...> WHERE phone IS NULL;
[click ▶ RUN]
  name
  ───────────
  Riley Evans
  Pat Zhao
  → 2 rows

[click ✓ SUBMIT]
  ✓ Submitted. Correct.
```

---

## License

MIT. See [LICENSE](LICENSE).

---

## Credits

Built for Ghost Strategies LLC.
