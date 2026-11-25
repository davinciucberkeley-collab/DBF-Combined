// T-105 B1b: headless Chrome check of the #sims replays. Usage: node check_replays.mjs <port> [chrome]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.argv[2] || '8099';
const CHROME = process.argv[3] || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const DBG = 9333 + Math.floor(Math.random() * 500);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const udd = fs.mkdtempSync(path.join(os.tmpdir(), 'rpchk-'));
const chrome = spawn(CHROME, ['--headless=new', '--enable-unsafe-swiftshader', '--use-angle=swiftshader', '--ignore-gpu-blocklist', '--remote-debugging-port=' + DBG,
  '--user-data-dir=' + udd, '--no-first-run', '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });

async function json(url) { for (let i = 0; i < 50; i++) { try { return await (await fetch(url)).json(); } catch { await sleep(200); } } throw new Error('no chrome'); }

function client(wsUrl) {
  const ws = new WebSocket(wsUrl); let id = 0; const pend = new Map(); const hs = [];
  ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { const { res, rej } = pend.get(d.id); pend.delete(d.id); d.error ? rej(new Error(JSON.stringify(d.error))) : res(d.result); } else hs.forEach(h => h(d)); };
  const open = new Promise(r => { ws.onopen = r; });
  return { open, on: h => hs.push(h), send: (method, params = {}) => new Promise((res, rej) => { const i = ++id; pend.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); }), close: () => ws.close() };
}

const results = { runs: [], spot: {} };
const fail = [];
const FRAMES = HERE;
const num = s => parseFloat(String(s).replace(/^[^0-9.+-]*/, ''));

async function run(w, h, theme, doSpot) {
  const tag = w + '-' + theme;
  const tgt = await (await fetch(`http://127.0.0.1:${DBG}/json/new?about:blank`, { method: 'PUT' })).json();
  const c = client(tgt.webSocketDebuggerUrl); await c.open;
  const errs = [];
  c.on(d => {
    if (d.method === 'Runtime.exceptionThrown') errs.push('exception: ' + JSON.stringify(d.params.exceptionDetails.exception?.description || d.params.exceptionDetails.text));
    if (d.method === 'Runtime.consoleAPICalled' && d.params.type === 'error') errs.push('console.error: ' + d.params.args.map(a => a.value ?? a.description).join(' '));
    if (d.method === 'Log.entryAdded' && d.params.entry.level === 'error') errs.push('log: ' + d.params.entry.text + ' ' + (d.params.entry.url || ''));
    if (d.method === 'Network.loadingFailed' && !d.params.canceled) errs.push('request failed: ' + d.params.errorText + ' ' + d.params.requestId);
    if (d.method === 'Network.responseReceived' && d.params.response.status >= 400) errs.push('HTTP ' + d.params.response.status + ' ' + d.params.response.url);
  });
  for (const m of ['Page.enable', 'Runtime.enable', 'Network.enable', 'Log.enable']) await c.send(m);
  await c.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 600 });
  await c.send('Page.addScriptToEvaluateOnNewDocument', { source: `try{localStorage.setItem('k09l.theme','${theme}')}catch(e){}` });
  await c.send('Page.navigate', { url: `http://127.0.0.1:${PORT}/index.html#sims` });
  const ev = async expr => { const r = await c.send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }); if (r.exceptionDetails) throw new Error('eval: ' + JSON.stringify(r.exceptionDetails.exception?.description || r.exceptionDetails.text)); return r.result.value; };
  const waitFor = async (expr, ms = 90000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { try { if (await ev(expr)) return true; } catch {} await sleep(300); } throw new Error('timeout: ' + expr); };
  const view = sel => `(()=>{document.querySelector('${sel}').scrollIntoView({block:'start'});return true})()`;
  const info = { tag };
  const shot = async name => { const r = await c.send('Page.captureScreenshot', { format: 'png' }); fs.writeFileSync(path.join(FRAMES, `${name}-${w}-${theme}.png`), Buffer.from(r.data, 'base64')); };
  const nonBlank = key => ev(`(async()=>{const r=window.__rp.${key};r.renderNow();const cv=document.querySelector('#rp-${key[0]}-canvas');const u=cv.toDataURL('image/png');
    const img=new Image();img.src=u;await img.decode();const o=document.createElement('canvas');o.width=img.width;o.height=img.height;const x=o.getContext('2d');x.drawImage(img,0,0);
    const d=x.getImageData(0,0,o.width,o.height).data;let n=0,s=0,s2=0;const seen=new Set();for(let i=0;i<d.length;i+=16){const v=d[i]+d[i+1]+d[i+2];n++;s+=v;s2+=v*v;seen.add(v>>3)}
    const m=s/n;return {w:o.width,h:o.height,variance:s2/n-m*m,levels:seen.size}})()`);
  const setSlider = async (p, val) => { await ev(`(()=>{const s=document.querySelector('#rp-${p}-slider');s.value='${val}';s.dispatchEvent(new Event('input',{bubbles:true}));return s.value})()`); const key = { f: ['t', 1], l: ['t', 1000], k: ['d', 1] }[p], want = parseFloat(val) * key[1];
    for (let n = 0; n < 40; n++) { await sleep(250); const r = await readout(p); if (Math.abs(num(r[key[0]]) - want) < (p === 'f' ? 0.051 : p === 'l' ? 0.51 : 0.051)) break; }
    await sleep(150); return ev(`document.querySelector('#rp-${p}-slider').value`); };
  const readout = p => ev(`(()=>{const o={};document.querySelectorAll('#rp-${p}-read dd[data-k]').forEach(d=>o[d.dataset.k]=d.textContent);return o})()`);
  try {
    await waitFor('window.__rp&&window.__rp.flight&&window.__rp.landing&&window.__rp.linkage');
    await ev(view('#rp-flight')); await waitFor('window.__rp.flight.F.D');
    await ev(view('#rp-landing')); await waitFor('window.__rp.landing.Lc.D');
    await ev(view('#rp-linkage')); await waitFor('window.__rp.linkage.K.D');
    await ev(view('#rp-flight'));
    info.default_case = await ev('document.querySelector("#rp-f-case").value');
    info.theme = await ev('document.documentElement.getAttribute("data-theme")');
    const fl = await (await fetch(`http://127.0.0.1:${PORT}/assets/sims3d/flight_${info.default_case}.json`)).json();
    const T = fl.t;
    const interp = (a, t) => { let lo = 0, hi = T.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (T[m] <= t) lo = m; else hi = m; } const f = Math.min(1, Math.max(0, (t - T[lo]) / ((T[lo + 1] - T[lo]) || 1))); return a[lo] + (a[lo + 1] - a[lo]) * f; };
    const reqT = i => (Math.round(T[i] * 10) / 10);
    const frac = q => Math.floor(q * (T.length - 1));
    if (doSpot) {
      results.spot.flight = [];
      for (const q of [0.1, 0.3, 0.5, 0.7, 0.9]) {
        const i = frac(q); const t = parseFloat(await setSlider('f', reqT(i))), r = await readout('f');
        const exp = { alt: interp(fl.alt, t), V: interp(fl.V, t), pitch: interp(fl.pitch, t), use: interp(fl.pitch_use_15, t) * 100, t };   // use is shown as a percent (T-105 fix 2)
        const got = { alt: num(r.alt), V: num(r.V), pitch: num(r.pitch), use: num(r.use), t: num(r.t) };
        const dec = { alt: 1, V: 1, pitch: 1, use: 1, t: 1 };
        const ok = Object.keys(exp).every(k => Math.abs(got[k] - exp[k]) <= 0.5 * Math.pow(10, -dec[k]) + 1e-9);
        results.spot.flight.push({ index: i, slider_t: t, displayed: { alt: r.alt, V: r.V, pitch: r.pitch, use: r.use, t: r.t }, expected_from_json: exp, match: ok });
      }
      await setSlider('f', reqT(frac(0.03))); await sleep(300);
      info.hover_pitch_text = await ev('document.querySelector("#rp-f-read [data-k=pitch]").textContent'); await shot('flight-hover');
    }
    await setSlider('f', reqT(frac(0.5))); await sleep(300);
    info.flight_blank = await nonBlank('flight'); await shot('flight');
    await ev(view('#rp-landing')); await sleep(300);
    const lc = await ev('document.querySelector("#rp-l-case").value');
    const ld = await (await fetch(`http://127.0.0.1:${PORT}/assets/sims3d/landing_${lc}.json`)).json();
    const nL = ld.t.length, dtL = (ld.t[nL - 1] - ld.t[0]) / (nL - 1);
    if (doSpot) {
      results.spot.landing = [];
      for (const q of [0.05, 0.2, 0.4, 0.6, 0.85]) {
        const i = Math.floor(q * (nL - 1)); const t = parseFloat(await setSlider('l', (i * dtL).toFixed(3))), r = await readout('l');
        const j = Math.min(nL - 2, Math.max(0, Math.floor(t / dtL))), f = Math.min(1, Math.max(0, t / dtL - j));
        const li = (a, k) => a[j][k] + (a[j + 1][k] - a[j][k]) * f;
        const exp = { n: ld.load_factor_g[j] + (ld.load_factor_g[j + 1] - ld.load_factor_g[j]) * f, tilt: ld.tilt_deg[j] + (ld.tilt_deg[j + 1] - ld.tilt_deg[j]) * f, ms: t * 1000, s: Math.max(...[0, 1, 2, 3].map(k => li(ld.crush_mm, k))) };
        const got = { n: num(r.n), tilt: num(r.tilt), ms: num(r.t), s: num(r.s) };
        const dec = { n: 2, tilt: 2, ms: 0, s: 1 };
        const ok = Object.keys(exp).every(k => Math.abs(got[k] - exp[k]) <= 0.5 * Math.pow(10, -dec[k]) + 1e-9);
        results.spot.landing.push({ index: i, slider_t: t, displayed: { n: r.n, tilt: r.tilt, t: r.t, s: r.s }, expected_from_json: exp, match: ok });
      }
    }
    await setSlider('l', (dtL * Math.floor(0.3 * (nL - 1))).toFixed(3)); await sleep(300);
    info.landing_blank = await nonBlank('landing'); await shot('landing');
    await ev(view('#rp-linkage')); await sleep(300);
    const lk = await (await fetch(`http://127.0.0.1:${PORT}/assets/sims3d/linkage.json`)).json();
    if (doSpot) {
      results.spot.linkage = [];
      for (const q of [0.1, 0.3, 0.5, 0.7, 0.9]) {
        const p = lk.R[Math.floor(q * (lk.R.length - 1))]; await setSlider('k', p.delta_deg); const r = await readout('k');
        const exp = { hm: p.hinge_moment_Nm, th: p.servo_theta_deg, rod: p.rod_len_mm, c0: p.min_clearance_mm, c1: p.min_clearance_excl_design_contact_mm, d: p.delta_deg };
        const got = { hm: num(r.hm), th: num(r.th), rod: num(r.rod), c0: num(r.c0), c1: num(r.c1), d: num(r.d) };
        const dec = { hm: 4, th: 2, rod: 2, c0: 3, c1: 3, d: 1 };
        const ok = Object.keys(exp).every(k => Math.abs(got[k] - exp[k]) <= 0.5 * Math.pow(10, -dec[k]) + 1e-9);
        results.spot.linkage.push({ delta_deg: p.delta_deg, displayed: { hm: r.hm, th: r.th, rod: r.rod, c0: r.c0, c1: r.c1, d: r.d }, expected_from_json: exp, match: ok });
      }
    }
    await setSlider('k', 12); await sleep(300);
    info.linkage_svg = await ev('document.querySelectorAll("#rp-k-top svg *, #rp-k-side svg *").length');
    await shot('linkage');
    info.label_count = await ev('[...document.querySelectorAll("b")].filter(e=>e.textContent.includes("Playback of recorded simulation output (not a new simulation)")).length');   // stated once (T-105 fix 2)
    info.wide = await ev(`[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(e=>e.tagName+'#'+e.id+'.'+String(e.className).slice(0,40)+' '+Math.round(e.getBoundingClientRect().right))`);
    info.scrollWidth = await ev('document.documentElement.scrollWidth'); info.innerWidth = await ev('innerWidth');
    info.autoplay = await ev('!!(window.__rp.flight.tl&&window.__rp.flight.tl.playing)');
  } catch (e) { errs.push('check failure: ' + e.message); }
  info.errors = errs; results.runs.push(info);
  const bl = k => info[k] && info[k].variance > 1 && info[k].levels >= 3;
  if (errs.length) fail.push(tag + ' errors: ' + errs.join(' | '));
  if (!bl('flight_blank')) fail.push(tag + ' flight canvas blank');
  if (!bl('landing_blank')) fail.push(tag + ' landing canvas blank');
  if (!(info.linkage_svg > 5)) fail.push(tag + ' linkage svg empty');
  if (w < 600 && !(info.scrollWidth <= info.innerWidth)) fail.push(tag + ' horizontal scroll ' + info.scrollWidth + ' > ' + info.innerWidth);
  if (info.label_count !== 1) fail.push(tag + ' label count ' + info.label_count);
  c.close();
}

try {
  await json(`http://127.0.0.1:${DBG}/json/version`);
  let first = true;
  for (const [w, h] of [[1280, 900], [400, 800]]) for (const theme of ['light', 'dark']) { await run(w, h, theme, first); first = false; }
  for (const k of ['flight', 'landing', 'linkage']) { const s = results.spot[k] || []; if (s.length !== 5 || !s.every(x => x.match)) fail.push('spot ' + k + ' ' + s.filter(x => x.match).length + '/5'); }
} catch (e) { fail.push('fatal: ' + e.message); }
results.matches = Object.fromEntries(Object.entries(results.spot).map(([k, v]) => [k, v.filter(x => x.match).length + ' of ' + v.length]));
results.fail = fail;
fs.writeFileSync(path.join(FRAMES, 'spot-values.json'), JSON.stringify(results, null, 1));
chrome.kill();
console.log(JSON.stringify({ matches: results.matches, fail, runs: results.runs.map(r => ({ tag: r.tag, theme: r.theme, sw: r.scrollWidth, iw: r.innerWidth, fb: r.flight_blank?.variance, lb: r.landing_blank?.variance, errs: r.errors.length, hover: r.hover_pitch_text })) }, null, 1));
process.exit(fail.length ? 1 : 0);
