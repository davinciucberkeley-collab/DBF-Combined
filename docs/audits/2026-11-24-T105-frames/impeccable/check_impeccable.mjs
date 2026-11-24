// T-105 Impeccable fixes, pass checks 1-7 (docs/audits/2026-11-24-impeccable-replays-review.md, "Fixes applied").
// Usage: node check_impeccable.mjs <port> <scratch dir for the Chrome profile> [chrome path]
// Writes PNG captures into this folder's impeccable/ subfolder and prints one JSON summary on stdout.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(HERE, 'impeccable');
fs.mkdirSync(OUT, { recursive: true });
const PORT = process.argv[2] || '8765';
const TMP = process.argv[3] || process.env.TEMP || '.';
const CHROME = process.argv[4] || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const DBG = 9333 + Math.floor(Math.random() * 500);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const udd = fs.mkdtempSync(path.join(TMP, 'impchk-'));
const chrome = spawn(CHROME, ['--headless=new', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--remote-debugging-port=' + DBG,
  '--user-data-dir=' + udd, '--no-first-run', '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });

async function json(url) { for (let i = 0; i < 60; i++) { try { return await (await fetch(url)).json(); } catch { await sleep(200); } } throw new Error('no chrome'); }

function client(wsUrl) {
  const ws = new WebSocket(wsUrl); let id = 0; const pend = new Map(); const hs = [];
  ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } else hs.forEach(h => h(d)); };
  const open = new Promise(r => { ws.onopen = r; });
  return { open, on: h => hs.push(h), send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }), close: () => ws.close() };
}

async function openPage(w, h, theme, reduce) {
  const tgt = await (await fetch(`http://127.0.0.1:${DBG}/json/new?about:blank`, { method: 'PUT' })).json();
  const c = client(tgt.webSocketDebuggerUrl); await c.open;
  const errs = [];
  c.on(d => {
    if (d.method === 'Runtime.exceptionThrown') errs.push('exception: ' + (d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text));
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push('console.error: ' + d.params.args.map(a => a.value ?? a.description).join(' '));
    if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') errs.push('log: ' + d.params.entry.text + ' ' + (d.params.entry.url || ''));
    if (d.method === 'Network.loadingFailed' && !d.params.canceled) errs.push('request failed: ' + d.params.errorText);
    if (d.method === 'Network.responseReceived' && d.params.response.status >= 400) errs.push('HTTP ' + d.params.response.status + ' ' + d.params.response.url);
  });
  for (const m of ['Page.enable', 'Runtime.enable', 'Network.enable', 'Log.enable']) await c.send(m);
  await c.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 600 });
  if (reduce) await c.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `try{localStorage.setItem('k09l.theme','${theme}')}catch(e){}` });
  await c.send('Page.navigate', { url: `http://127.0.0.1:${PORT}/index.html#sims` });
  const ev = async expr => { const r = await c.send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error('eval: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text)); return r.result.value; };
  const waitFor = async (expr, ms = 150000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { try { if (await ev(expr)) return true; } catch {} await sleep(300); } throw new Error('timeout: ' + expr); };
  return { c, ev, waitFor, errs, close: () => c.close() };
}

async function readyAll(p) {
  await p.waitFor('window.__rp&&window.__rp.flight&&window.__rp.landing&&window.__rp.linkage');
  for (const [sec, dv] of [['rp-flight', 'window.__rp.flight.F.D'], ['rp-landing', 'window.__rp.landing.Lc.D'], ['rp-linkage', 'window.__rp.linkage.K.D']]) {
    await p.ev(`document.getElementById('${sec}').scrollIntoView({block:'start'})`);
    await p.waitFor(dv); await sleep(700);
  }
}

async function capture(p, id, headId, name) {
  const r = await p.ev(`(()=>{const h=document.getElementById('${headId}'), s=document.getElementById('${id}');
    const top=h.getBoundingClientRect().top+scrollY, bottom=s.getBoundingClientRect().bottom+scrollY; return {top, bottom, w:innerWidth}})()`);
  await p.ev(`document.getElementById('${id}').scrollIntoView({block:'start'})`); await sleep(500);
  const s = await p.c.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: r.top, width: r.w, height: r.bottom - r.top, scale: 1 } });
  fs.writeFileSync(path.join(OUT, name), Buffer.from(s.data, 'base64'));
  return Math.round(r.bottom - r.top);
}

const SECTIONS = [['rp-flight', 'sims-replay-flight', 'flight'], ['rp-landing', 'sims-replay-landing', 'landing'], ['rp-linkage', 'sims-replay-linkage', 'linkage']];
const summary = { pages: [], reduced: null, fail: [] };

try {
  await json(`http://127.0.0.1:${DBG}/json/version`);
  for (const [w, theme] of [[1280, 'light'], [1280, 'dark'], [400, 'light'], [400, 'dark']]) {
    const h = w === 1280 ? 900 : 800, tag = w + '-' + theme;
    const p = await openPage(w, h, theme, false);
    const info = { tag };
    try {
      await readyAll(p);
      info.capture_heights = {};
      for (const [sec, head, name] of SECTIONS) info.capture_heights[name] = await capture(p, sec, head, `${name}-${w}-${theme}.png`);
      // check 3: sideways scroll, including every element inside the replay sections
      info.scrollWidth = await p.ev('document.documentElement.scrollWidth'); info.innerWidth = await p.ev('innerWidth');
      info.overflow = await p.ev(`(()=>{const W=innerWidth, roots=[...document.querySelectorAll('#sims-replay,#sims-replay-flight,#sims-replay-landing,#sims-replay-linkage,#rp-flight,#rp-landing,#rp-linkage')], out=[];
        const seen=new Set(); for (const r of roots) for (const el of [r,...r.querySelectorAll('*')]) { if (seen.has(el)) continue; seen.add(el); if (el.tagName==='CANVAS'||!el.getClientRects().length) continue;
          const bb=el.getBoundingClientRect(); if (bb.right>W+0.5) out.push(el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+'.'+String(el.getAttribute('class')||'').slice(0,30)+' right='+Math.round(bb.right));
          if (el instanceof HTMLElement && el.scrollWidth>el.clientWidth+1 && getComputedStyle(el).overflowX!=='visible') out.push('scroller '+el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+' '+el.scrollWidth+'>'+el.clientWidth); }
        return out.slice(0,20)})()`);
      // check 4: rendered plot tick and limit label size (SVG scale applied)
      info.ticks = await p.ev(`(()=>{const els=[...document.querySelectorAll('#rp-flight .rp-tick,#rp-landing .rp-tick,#rp-linkage .rp-tick,#rp-flight .rp-limit-t,#rp-landing .rp-limit-t,#rp-linkage .rp-limit-t,#rp-flight .rp-peak-t,#rp-landing .rp-peak-t,#rp-linkage .rp-peak-t')].filter(e=>e.getClientRects().length);
        const v=els.map(e=>{const m=e.getScreenCTM(); const sc=m?Math.hypot(m.a,m.b):1; return parseFloat(getComputedStyle(e).fontSize)*sc}); return {n:v.length, min:Math.round(Math.min(...v)*10)/10, below12:v.filter(x=>x<12).length}})()`);
      // check 5: touch targets
      info.touch = await p.ev(`(()=>{const els=[...document.querySelectorAll('#rp-flight .rp-btn,#rp-flight .rp-chip,#rp-landing .rp-btn,#rp-linkage .rp-btn,#rp-linkage .rp-chip')].filter(e=>e.getClientRects().length);
        const hs=els.map(e=>[e.textContent.trim().slice(0,24), Math.round(e.getBoundingClientRect().height*10)/10]); return {n:hs.length, min:Math.min(...hs.map(x=>x[1])), below44:hs.filter(x=>x[1]<44)}})()`);
      // check 6: aria-valuetext on every replay slider
      info.aria = await p.ev(`[...document.querySelectorAll('#rp-flight input[type=range],#rp-landing input[type=range],#rp-linkage input[type=range]')].map(i=>[i.id, i.getAttribute('aria-valuetext')||''])`);
      info.aria_missing = info.aria.filter(x => !x[1]).map(x => x[0]);
      // the flight run list text and the readouts (for the report)
      info.flight_verdict = await p.ev(`document.getElementById('rp-f-verdict').textContent`);
      info.landing_verdict = await p.ev(`document.getElementById('rp-l-verdict').textContent`);
      info.linkage_verdict = await p.ev(`document.getElementById('rp-k-verdict').textContent`);
      info.pf_table_rows = await p.ev(`document.querySelectorAll('#rp-f-pf tbody tr').length`);
      info.errors = p.errs.slice();
    } catch (e) { info.errors = p.errs.concat(['check failure: ' + e.message]); }
    summary.pages.push(info);
    p.close();
  }

  // check 7: reduced motion (propellers still while playing; linkage sweep stops after one pass)
  const r = await openPage(1280, 900, 'light', true);
  const rr = { errors: [] };
  try {
    await readyAll(r);
    rr.media = await r.ev(`matchMedia('(prefers-reduced-motion: reduce)').matches`);
    await capture(r, 'rp-flight', 'sims-replay-flight', 'flight-1280-light-reduced-motion.png');
    const props = `window.__rp.flight.rg.props.UL.map(p=>p.node.matrix.elements.join(',')).join('|')`;
    rr.props_before = await r.ev(props);
    await r.ev(`document.getElementById('rp-f-play').click()`); await sleep(2000);
    rr.flight_t_after_2s = await r.ev(`window.__rp.flight.tl.t`);
    rr.props_after = await r.ev(props);
    rr.props_still = rr.props_before === rr.props_after;
    await r.ev(`document.getElementById('rp-f-play').click()`);
    // the linkage panel only ticks while on screen: scroll it into view before starting the sweep
    await r.ev(`document.getElementById('rp-linkage').scrollIntoView({block:'start'})`); await sleep(700);
    await r.ev(`document.getElementById('rp-k-play').click()`);
    await r.waitFor(`window.__rp.linkage.K.playing===false`, 90000);
    rr.linkage_stopped_at_index = await r.ev(`window.__rp.linkage.K.i + ' of ' + (window.__rp.linkage.K.D[window.__rp.linkage.K.side].length-1)`);
    rr.linkage_button_after_stop = await r.ev(`document.getElementById('rp-k-play').textContent`);
    const i0 = await r.ev(`window.__rp.linkage.K.i`); await sleep(3000); const i1 = await r.ev(`window.__rp.linkage.K.i`);
    rr.linkage_still_after_3s = i0 === i1;
  } catch (e) { rr.errors.push('check failure: ' + e.message); }
  rr.errors = r.errs.concat(rr.errors);
  summary.reduced = rr;
  r.close();
} catch (e) { summary.fail.push('fatal: ' + e.message); }

// mechanical verdicts for checks 2-7
for (const p of summary.pages) {
  if (p.errors && p.errors.length) summary.fail.push(p.tag + ' errors ' + p.errors.length);
  if (p.innerWidth === 400 && p.scrollWidth !== 400) summary.fail.push(p.tag + ' scrollWidth ' + p.scrollWidth);
  if (p.overflow && p.overflow.length) summary.fail.push(p.tag + ' overflow ' + p.overflow.length);
  if (p.ticks && (p.ticks.below12 > 0 || p.ticks.n === 0)) summary.fail.push(p.tag + ' tick font below 12 px (' + p.ticks.below12 + ')');
  if (p.touch && (p.touch.below44.length > 0 || p.touch.n === 0)) summary.fail.push(p.tag + ' touch below 44 px (' + p.touch.below44.length + ')');
  if (p.aria_missing && p.aria_missing.length) summary.fail.push(p.tag + ' aria-valuetext missing ' + p.aria_missing.join(','));
}
if (summary.reduced) {
  const rr = summary.reduced;
  if (rr.errors.length) summary.fail.push('reduced errors ' + rr.errors.length);
  if (!rr.media) summary.fail.push('reduced: media query not emulated');
  if (!rr.props_still) summary.fail.push('reduced: propellers moved while playing');
  if (!(rr.flight_t_after_2s > 0.2)) summary.fail.push('reduced: flight did not play (test invalid)');   // headless frames are slow (dt capped at 0.25 s per frame)
  if (!rr.linkage_still_after_3s || rr.linkage_button_after_stop !== 'Sweep') summary.fail.push('reduced: linkage sweep did not stop');
}
summary.fail_count = summary.fail.length;
fs.writeFileSync(path.join(HERE, 'check_impeccable-result.json'), JSON.stringify(summary, null, 1));
chrome.kill();
console.log(JSON.stringify(summary, null, 1));
process.exit(summary.fail.length ? 1 : 0);
