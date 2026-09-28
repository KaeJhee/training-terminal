/**
 * Grade every shipped answer key in headless Chrome.
 *
 *   SQL:      each expected_query, through SqlEngine
 *   Python:   each fallback_expected, through Pyodide (includes hidden checks)
 *   JavaScript: tests/js_solutions.json, through JsEngine
 *   Rust:     each qa.accept / qa.reject, through the page's RustEngine
 *
 * Also checks progress validation, the JS sandbox, and Python abort.
 *
 * Usage:
 *   PLAYWRIGHT_MODULE=/path/to/playwright/index.js \
 *   CHROME_PATH=/usr/bin/google-chrome \
 *   node tests/answer_keys.mjs http://127.0.0.1:8765/
 */
import fs from 'fs';
import path from 'path';
import { pathToFileURL } from 'url';

const pageUrl = process.argv[2] || 'http://127.0.0.1:8765/';
const modPath = process.env.PLAYWRIGHT_MODULE || 'playwright';
const pw = await import(path.isAbsolute(modPath) ? pathToFileURL(modPath).href : modPath);
const chromium = (pw.chromium) || (pw.default && pw.default.chromium);
if (!chromium) {
  console.error('playwright chromium export not found');
  process.exit(1);
}

const solutions = JSON.parse(
  fs.readFileSync(new URL('./js_solutions.json', import.meta.url), 'utf8')
);

const launchOpts = { headless: true, args: ['--disable-dev-shm-usage'] };
if (process.env.CHROME_PATH) launchOpts.executablePath = process.env.CHROME_PATH;

const browser = await chromium.launch(launchOpts);
const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
const page = await context.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));

await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
await page.waitForFunction(() => window.__ghost && window.__ghost.app, { timeout: 20000 });

function report(label, fails) {
  if (!fails.length) {
    console.log(`PASS  ${label}`);
    return 0;
  }
  console.log(`FAIL  ${label} (${fails.length})`);
  fails.slice(0, 12).forEach((f) => console.log('      ' + f));
  return fails.length;
}

let failed = 0;

const sqlFails = await page.evaluate(async () => {
  const { QUESTIONS, app } = window.__ghost;
  const fails = [];
  const t0 = Date.now();
  while (!app.sql.ready && !app.sql.failed && Date.now() - t0 < 15000) {
    await new Promise((r) => setTimeout(r, 50));
  }
  if (!app.sql.ready) return ['sql engine not ready: ' + (app.sql.failReason || 'timeout')];
  for (const tier of Object.keys(QUESTIONS.sql)) {
    for (const q of QUESTIONS.sql[tier]) {
      const r = await app.sql.evaluate(q.expected_query, q);
      if (!r.ok) fails.push(q.id + ': ' + (r.detail || 'not ok'));
    }
  }
  return fails;
});
failed += report('SQL expected queries', sqlFails);

const jsFails = await page.evaluate(async (sols) => {
  const { QUESTIONS, app } = window.__ghost;
  const fails = [];
  const ids = [];
  for (const tier of Object.keys(QUESTIONS.javascript)) {
    for (const q of QUESTIONS.javascript[tier]) ids.push(q);
  }
  for (const q of ids) {
    const code = sols[q.id];
    if (!code) { fails.push(q.id + ': missing reference solution'); continue; }
    const r = await app.js.evaluate(code, q);
    if (!r.ok) fails.push(q.id + ': ' + (r.detail || 'not ok'));
  }
  return fails;
}, solutions);
failed += report('JavaScript reference solutions', jsFails);

const rustFails = await page.evaluate(async () => {
  const { QUESTIONS, RustEngine } = window.__ghost;
  const engine = new RustEngine();
  const fails = [];
  let accept = 0;
  let reject = 0;
  for (const tier of Object.keys(QUESTIONS.rust)) {
    for (const q of QUESTIONS.rust[tier]) {
      const qa = q.qa || { accept: [], reject: [] };
      for (const src of qa.accept || []) {
        accept++;
        const r = await engine.evaluate(src, q);
        if (!r.ok) fails.push(q.id + ' accept ' + JSON.stringify(src) + ' -> ' + (r.detail || ''));
      }
      for (const item of qa.reject || []) {
        reject++;
        const r = await engine.evaluate(item.input, q);
        if (r.ok) fails.push(q.id + ' reject was accepted: ' + JSON.stringify(item.input));
        else if (item.expect_msg && String(r.detail || '').indexOf(item.expect_msg) === -1) {
          fails.push(q.id + ' reject msg ' + JSON.stringify(r.detail) + ' missing ' + item.expect_msg);
        }
      }
    }
  }
  const variants = [
    ['rs_intro_01', 'let shop_open: bool = true;', true, null],
    ['rs_intro_01', 'let shop_open = true; // open', true, null],
    ['rs_intro_02', 'let mut counter: i32 = 0;', true, null],
    ['rs_intro_01', 'let shop_open = true // open', false, 'missing `;`'],
  ];
  const byId = {};
  for (const tier of Object.keys(QUESTIONS.rust)) {
    for (const q of QUESTIONS.rust[tier]) byId[q.id] = q;
  }
  for (const [qid, src, expectOk, msg] of variants) {
    const r = await engine.evaluate(src, byId[qid]);
    if (!!r.ok !== expectOk) fails.push('variant ' + qid + ' ' + src + ' ok=' + r.ok + ' ' + (r.detail || ''));
    else if (msg && String(r.detail || '').indexOf(msg) === -1) fails.push('variant msg ' + r.detail);
  }
  if (accept !== 168 || reject !== 151) {
    fails.push('qa case count changed: accept ' + accept + ' reject ' + reject + ' (expected 168/151)');
  }
  return fails;
});
failed += report('Rust grader (319 cases + variants)', rustFails);

const stateFails = await page.evaluate(() => {
  const { GameState } = window.__ghost;
  const fails = [];
  const gs = new GameState();
  const before = gs.exportJson();
  let threw = false;
  try { gs.importJson('{"version":4}'); }
  catch (e) {
    threw = true;
    if (!/completed/.test(String(e.message))) fails.push('bad import message: ' + e.message);
  }
  if (!threw) fails.push('malformed import did not throw');
  if (gs.exportJson() !== before) fails.push('malformed import changed saved state');
  localStorage.setItem('ghostTerminal.state', '{"version":4}');
  const recovered = new GameState();
  const parsed = JSON.parse(recovered.exportJson());
  if (!parsed.completed || !parsed.completed.python || !Array.isArray(parsed.activity)) {
    fails.push('load() did not recover a valid shape from {"version":4}');
  }
  if (recovered.getCurrentTier('python') !== 'introductory') {
    fails.push('recovered state is not at introductory');
  }
  // Old saves that only knew python/sql must keep javascript and rust keys.
  localStorage.setItem('ghostTerminal.state', JSON.stringify({
    version: 3,
    completed: { python: { py_intro_01: true }, sql: {} },
    activity: [],
  }));
  const migrated = new GameState();
  const m = JSON.parse(migrated.exportJson());
  if (!m.completed.javascript || !m.completed.rust) fails.push('migration dropped javascript or rust');
  if (!m.completed.python.py_intro_01) fails.push('migration dropped existing python progress');
  localStorage.removeItem('ghostTerminal.state');
  return fails;
});
failed += report('progress validation and migration', stateFails);

const sandboxFails = await page.evaluate(async () => {
  const { app } = window.__ghost;
  const fails = [];
  const code = [
    'let fetch_type = typeof fetch;',
    'let proto_type = "missing";',
    'try {',
    '  const proto = Object.getPrototypeOf(Object.getPrototypeOf(self));',
    '  proto_type = typeof (proto && proto.fetch);',
    '} catch (e) { proto_type = "throw"; }',
    'let beacon_type = typeof (navigator && navigator.sendBeacon);',
  ].join('\n');
  const q = {
    id: 'sandbox_probe',
    setup: '',
    assertion: {
      type: 'expression',
      expression: '[fetch_type, proto_type, beacon_type]',
      expected: ['undefined', 'undefined', 'undefined'],
    },
  };
  const r = await app.js.evaluate(code, q);
  if (!r.ok) fails.push(r.detail || 'sandbox probe failed');
  return fails;
});
failed += report('JS sandbox (fetch removed from prototype)', sandboxFails);

console.log('Python engine loading (Pyodide)…');
const pyStart = Date.now();
const pyFails = await page.evaluate(async () => {
  const { QUESTIONS, app } = window.__ghost;
  const fails = [];
  await app.py.init();
  if (!app.py.ready) return ['python not ready: ' + (app.py.failReason || 'unknown')];
  for (const tier of ['introductory', 'amateur', 'intermediate', 'experienced', 'master']) {
    for (const q of QUESTIONS.python[tier]) {
      if (!q.fallback_expected) { fails.push(q.id + ': no fallback_expected'); continue; }
      const r = await app.py.evaluate(q.fallback_expected, q);
      if (!r.ok) fails.push(q.id + ': ' + (r.detail || 'not ok'));
    }
  }
  // Literal expected value should not pass a question that has a hidden check.
  const intro = QUESTIONS.python.introductory.find((q) => q.id === 'py_intro_04');
  const cheat = await app.py.evaluate('total = 15', intro);
  if (cheat.ok) fails.push('py_intro_04 accepted the literal total = 15');
  const exp = QUESTIONS.python.experienced.find((q) => q.id === 'py_exp_04');
  const noneCheck = await app.py.evaluate(exp.fallback_expected, exp);
  if (!noneCheck.ok) fails.push('py_exp_04 reference failed: ' + noneCheck.detail);
  // Unlock Master once every experienced question is recorded complete.
  const gs = app.state;
  for (const tier of ['introductory', 'amateur', 'intermediate', 'experienced']) {
    for (const q of QUESTIONS.python[tier]) gs.markComplete('python', q.id);
  }
  if (gs.getCurrentTier('python') !== 'master') {
    fails.push('python tier after experienced gate is ' + gs.getCurrentTier('python'));
  }
  const next = gs.getNextQuestion('python');
  if (!next || !String(next.id).startsWith('py_mas_')) {
    fails.push('next python question is not a master item: ' + (next && next.id));
  }
  return fails;
});
console.log('Python grading took ' + ((Date.now() - pyStart) / 1000).toFixed(1) + 's');
failed += report('Python reference answers + Master unlock', pyFails);

const abortFails = await page.evaluate(async () => {
  const { app } = window.__ghost;
  const fails = [];
  if (!app.py.ready) await app.py.init();
  if (!app.py.ready) return ['python not ready for abort test'];
  const q = {
    id: 'abort_probe',
    setup: '',
    assertion: { type: 'stdout', value: 'hi' },
    fallback_expected: 'print("hi")',
  };
  const pending = app.py.evaluate('while True:\n    pass', q);
  await new Promise((r) => setTimeout(r, 200));
  const t0 = Date.now();
  app.py.abort();
  const result = await pending;
  const elapsed = Date.now() - t0;
  if (!result.aborted && !/abort/i.test(result.detail || '')) {
    fails.push('abort did not stop the loop: ' + JSON.stringify(result));
  }
  if (elapsed > 4000) fails.push('abort took ' + elapsed + 'ms');
  const again = await app.py.evaluate('print(1 + 1)', {
    id: 'after_abort',
    setup: '',
    assertion: { type: 'stdout', value: '2' },
  });
  if (!again.ok) fails.push('python did not recover after abort: ' + (again.detail || ''));
  return fails;
});
failed += report('Python infinite-loop abort', abortFails);

if (errors.length) {
  console.log('page errors:');
  errors.slice(0, 8).forEach((e) => console.log('  ' + e));
  failed += errors.length;
}

await browser.close();
if (failed) {
  console.log('\n' + failed + ' failure(s)');
  process.exit(1);
}
console.log('\nALL ANSWER KEYS GREEN');
