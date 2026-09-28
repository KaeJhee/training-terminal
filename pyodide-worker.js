/* Pyodide runs in this worker so a Python infinite loop can be terminated
   from the main thread. The page posts {id, kind, ...} and this file replies
   with {id, kind, ...}. There is no shared state with the page. */
'use strict';

let pyodide = null;

function pyToJs(val) {
  // Pyodide turns Python None into JS undefined. Graders compare against null.
  if (val === undefined || val === null) return null;
  if (typeof val === 'object' && typeof val.toJs === 'function') {
    let js;
    try {
      js = val.toJs({ dict_converter: Object.fromEntries });
    } finally {
      try { if (typeof val.destroy === 'function') val.destroy(); } catch (_) {}
    }
    if (js === undefined || js === null) return null;
    return js;
  }
  return val;
}

function deepEq(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null) return a === b;
  if (Array.isArray(a)) {
    if (!Array.isArray(b) || a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) if (!deepEq(a[i], b[i])) return false;
    return true;
  }
  if (typeof a === 'object') {
    const ak = Object.keys(a), bk = Object.keys(b);
    if (ak.length !== bk.length) return false;
    for (const k of ak) if (!deepEq(a[k], b[k])) return false;
    return true;
  }
  if (typeof a === 'number' && typeof b === 'number') return Math.abs(a - b) < 1e-9;
  return false;
}

function truncate(s, n) {
  s = String(s);
  return s.length > (n || 120) ? s.slice(0, (n || 120) - 1) + '…' : s;
}

function cleanError(e) {
  const msg = String((e && e.message) || e);
  return msg.split('\n').map(l => l.trimEnd()).filter(l => l.length).slice(-3).join('\n   ');
}

async function gradeOne(userCode, setup, assertion) {
  const ns = pyodide.toPy({});
  try {
    await pyodide.runPythonAsync(
      "import sys, io\n__stdout__ = io.StringIO()\nsys.stdout = __stdout__",
      { globals: ns }
    );
    if (setup) {
      try { await pyodide.runPythonAsync(setup, { globals: ns }); }
      catch (e) { return { ok: false, detail: 'setup error: ' + cleanError(e) }; }
    }
    try { await pyodide.runPythonAsync(userCode, { globals: ns }); }
    catch (e) { return { ok: false, detail: cleanError(e) }; }
    const stdout = String(await pyodide.runPythonAsync("__stdout__.getvalue()", { globals: ns }));
    const a = assertion;
    if (!a) return { ok: false, detail: 'Question is missing an assertion.' };

    if (a.type === 'binding') {
      const pyVal = ns.get(a.name);
      if (pyVal === undefined) return { ok: false, detail: "Variable '" + a.name + "' was not defined." };
      const js = pyToJs(pyVal);
      const ok = deepEq(js, a.value);
      return ok ? { ok: true } : {
        ok: false,
        detail: 'expected  ' + a.name + ' = ' + truncate(JSON.stringify(a.value)) +
                '\n   got       ' + a.name + ' = ' + truncate(JSON.stringify(js)),
      };
    }
    if (a.type === 'stdout') {
      const exp = String(a.value).trim();
      const got = stdout.trim();
      return exp === got ? { ok: true } : {
        ok: false,
        detail: 'expected stdout: ' + truncate(JSON.stringify(exp)) +
                '\n   got stdout:      ' + truncate(JSON.stringify(got)),
      };
    }
    if (a.type === 'call' || a.type === 'expression') {
      const expr = a.call || a.expression;
      let pyResult;
      try { pyResult = await pyodide.runPythonAsync(expr, { globals: ns }); }
      catch (e) { return { ok: false, detail: "error evaluating '" + expr + "': " + cleanError(e) }; }
      const js = pyToJs(pyResult);
      const ok = deepEq(js, a.expected);
      return ok ? { ok: true } : {
        ok: false,
        detail: 'expected  ' + expr + ' == ' + truncate(JSON.stringify(a.expected)) +
                '\n   got       ' + expr + ' == ' + truncate(JSON.stringify(js)),
      };
    }
    return { ok: false, detail: 'unknown assertion type: ' + a.type };
  } finally {
    try { if (ns && ns.destroy) ns.destroy(); } catch (_) {}
  }
}

async function previewOne(userCode, setup, assertion) {
  const ns = pyodide.toPy({});
  try {
    await pyodide.runPythonAsync(
      "import sys, io\n__stdout__ = io.StringIO()\nsys.stdout = __stdout__",
      { globals: ns }
    );
    if (setup) {
      try { await pyodide.runPythonAsync(setup, { globals: ns }); }
      catch (e) { return { error: 'setup error: ' + cleanError(e) }; }
    }
    try { await pyodide.runPythonAsync(userCode, { globals: ns }); }
    catch (e) { return { error: cleanError(e) }; }
    const stdout = String(await pyodide.runPythonAsync("__stdout__.getvalue()", { globals: ns }));
    const a = assertion;
    let probe = null;
    if (a && a.type === 'binding') {
      const v = ns.get(a.name);
      if (v === undefined) probe = { label: a.name, undef: true };
      else probe = { label: a.name, value: pyToJs(v) };
    } else if (a && (a.type === 'call' || a.type === 'expression')) {
      const expr = a.call || a.expression;
      try {
        const r = await pyodide.runPythonAsync(expr, { globals: ns });
        probe = { label: expr, value: pyToJs(r) };
      } catch (e) {
        probe = { label: expr, error: cleanError(e) };
      }
    }
    return { stdout, probe };
  } finally {
    try { if (ns && ns.destroy) ns.destroy(); } catch (_) {}
  }
}

async function evaluateMessage(msg) {
  const primary = await gradeOne(msg.userCode || '', msg.setup || '', msg.assertion);
  if (!primary.ok) return primary;
  const hidden = Array.isArray(msg.hidden) ? msg.hidden : [];
  for (let i = 0; i < hidden.length; i++) {
    const h = hidden[i] || {};
    const setup = Object.prototype.hasOwnProperty.call(h, 'setup') ? (h.setup || '') : (msg.setup || '');
    const extra = await gradeOne(msg.userCode || '', setup, h.assertion);
    if (!extra.ok) {
      return {
        ok: false,
        detail: 'Passed the sample but failed a hidden check.\n   ' + (extra.detail || ''),
      };
    }
  }
  return primary;
}

self.onmessage = async (event) => {
  const msg = event.data || {};
  const id = msg.id;
  try {
    if (msg.kind === 'init') {
      importScripts(msg.jsUrl);
      pyodide = await loadPyodide({ indexURL: msg.indexURL });
      self.postMessage({ id, kind: 'ready' });
      return;
    }
    if (!pyodide) {
      self.postMessage({ id, kind: 'error', detail: 'Python runtime is not initialized.' });
      return;
    }
    if (msg.kind === 'evaluate') {
      const result = await evaluateMessage(msg);
      self.postMessage({ id, kind: 'result', ok: !!result.ok, detail: result.detail || '' });
      return;
    }
    if (msg.kind === 'preview') {
      const result = await previewOne(msg.userCode || '', msg.setup || '', msg.assertion);
      self.postMessage({ id, kind: 'preview', stdout: result.stdout || '', probe: result.probe || null, error: result.error || '' });
      return;
    }
    self.postMessage({ id, kind: 'error', detail: 'Unknown worker message.' });
  } catch (err) {
    self.postMessage({ id, kind: 'error', detail: String((err && err.message) || err) });
  }
};
