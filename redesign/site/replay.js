// Replays inside the #sims view (T-105 B1): flight, landing and linkage playback of the recorded files in assets/sims3d/.
// Lazy: site.js imports this module the first time #sims is shown; each panel starts when it scrolls into view, each case
// JSON is fetched when picked, and the GLB (same GLTFLoader + MeshoptDecoder as viewer.js) is parsed once and cloned for the
// second 3-D panel (two renderers, one parsed model). Rendering and animation run only while a panel is on screen.
// Nothing here simulates anything: it poses the CAD model from the recorded samples and draws plots of the same samples.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import M from './model.js?v=20261116e';

const VER = '20261124b', GLB_URL = 'assets/concept-a.opt.glb?v=20261118f', GLB_B64 = 'data/assembly.opt.glb.part1.js?v=20261118f';
const REDUCE = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const nf = (v, d = 2) => (v === null || v === undefined || Number.isNaN(v)) ? '\u2014' : Number(v).toFixed(d);
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const RAD = Math.PI / 180;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

let manifest = null, mounted = false, themeVer = 0;
const panels = [];
new MutationObserver(() => themeVer++).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => themeVer++);

// ---------------------------------------------------------------- data fetch (bytes counted)
const cache = new Map();
async function fetchJSON(url) {
  if (cache.has(url)) return cache.get(url);
  const p = (async () => {
    const r = await fetch(url); if (!r.ok) throw new Error(url.split('?')[0] + ' HTTP ' + r.status);
    const buf = await r.arrayBuffer();
    return { data: JSON.parse(new TextDecoder().decode(buf)), bytes: buf.byteLength };
  })();
  cache.set(url, p); p.catch(() => cache.delete(url));
  return p;
}

// ---------------------------------------------------------------- model (parsed once, shared)
let modelP = null; const modelInfo = { bytes: 0, done: false, listeners: [] };
function loadModel() {
  if (modelP) return modelP;
  const mk = () => new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  const addScript = src => new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = () => no(new Error(src.split('?')[0] + ' not found')); document.head.appendChild(s); });
  modelP = (async () => {
    let gltf;
    try {
      gltf = await new Promise((res, rej) => mk().load(GLB_URL, res, ev => { modelInfo.bytes = ev.loaded || 0; modelInfo.listeners.forEach(f => f()); }, rej));
    } catch (e) {
      window.VIEWER_GLB_B64_PARTS = [];
      await addScript(GLB_B64);
      const bin = atob(window.VIEWER_GLB_B64_PARTS.join('')), buf = new Uint8Array(bin.length);
      window.VIEWER_GLB_B64_PARTS = null;
      for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
      modelInfo.bytes = buf.length;
      gltf = await new Promise((res, rej) => mk().parse(buf.buffer, '', res, rej));
    }
    modelInfo.done = true; modelInfo.listeners.forEach(f => f());
    return gltf;
  })();
  modelP.catch(() => { modelP = null; });
  return modelP;
}

// ---------------------------------------------------------------- rigging: parts, hinges, pads, props
const AX = M.AXIS_AC;
function rig(root) {
  root.updateMatrixWorld(true);
  const parts = new Map(), joints = [];
  root.traverse(o => {
    const u = o.userData || {};
    if (u.part_id) parts.set(u.part_id, { node: o, base: o.matrix.clone() });
    else if (u.edge && u.kind !== 'wire') joints.push({ data: u, pos: o.getWorldPosition(new THREE.Vector3()) });
  });
  const hinges = {};
  for (const j of joints) if (j.data.kind === 'revolute' && /^WNG-006-[LR]$/.test(j.data.part_a || '') && parts.has(j.data.part_a)) {
    const ax = AX[String(j.data.axis || 'Y').toUpperCase()] || [0, 1, 0];
    hinges[j.data.part_a.slice(-1)] = { pivot: j.pos.clone(), axis: new THREE.Vector3(...M.ac2gl(ax)).normalize(), edge: j.data.edge };
  }
  for (const p of parts.values()) p.node.matrixAutoUpdate = false;
  const get = ids => ids.filter(i => parts.has(i)).map(i => parts.get(i));
  const side = {};
  for (const s of ['L', 'R']) side[s] = get(['WNG-006-', 'WNG-007-', 'WNG-010-', 'MEC-004-', 'MEC-005-'].map(x => x + s));
  const pads = {};
  for (const c of ['UR', 'LR', 'UL', 'LL']) {
    const p = parts.get('GER-002-' + c); if (!p) continue;
    const b = new THREE.Box3().setFromObject(p.node);                 // root is at identity here, so this is the root frame
    pads[c] = { part: p, x0: b.min.x, len: b.max.x - b.min.x, center: b.getCenter(new THREE.Vector3()) };       // gl x = CAD x (aft): the end nearest the shoe is the smaller x
  }
  const props = {};
  for (const c of ['UL', 'UR', 'LL', 'LR']) props[c] = get(['PRP-002-', 'PRP-004-', 'PRP-005-'].map(x => x + c));
  return { root, parts, hinges, side, pads, props };
}
const _a = new THREE.Matrix4(), _b = new THREE.Matrix4(), _c = new THREE.Matrix4();
function placeAbout(parts, pivot, axis, ang) {      // rotate parts about a line (pivot, axis) in the root frame
  _a.makeTranslation(pivot.x, pivot.y, pivot.z).multiply(_b.makeRotationAxis(axis, ang)).multiply(_c.makeTranslation(-pivot.x, -pivot.y, -pivot.z));
  for (const p of parts) { p.node.matrix.copy(_a).multiply(p.base); p.node.matrixWorldNeedsUpdate = true; }
}

// ---------------------------------------------------------------- 3-D stage
function palette() {
  return { grid: new THREE.Color(cssv('--stage-grid') || '#B3AC98'), trail: new THREE.Color(cssv('--accent') || '#1F5A82'), fg3: new THREE.Color(cssv('--fg-3') || '#566070') };
}
function makeStage(canvas, opt) {
  const st = { canvas, ok: false, dirty: true, theme: -1, lastTarget: null, opt };
  try { st.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' }); }
  catch (e) { return st; }
  const r = st.renderer;
  r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  r.outputColorSpace = THREE.SRGBColorSpace; r.toneMapping = THREE.AgXToneMapping; r.toneMappingExposure = 1.25;
  st.scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(r); st.scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; pm.dispose();
  st.scene.environmentIntensity = 0.9;
  st.scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa4b0, 0.3));
  const key = new THREE.DirectionalLight(0xfff8f0, 1.6); key.position.set(2, 4, 3); st.scene.add(key);
  st.camera = new THREE.PerspectiveCamera(30, 1, 0.02, 4000);
  st.controls = new OrbitControls(st.camera, canvas);
  Object.assign(st.controls, { enableDamping: !REDUCE, dampingFactor: 0.12, screenSpacePanning: true });
  st.controls.addEventListener('change', () => { st.dirty = true; });
  new ResizeObserver(() => resizeStage(st)).observe(canvas);
  st.ok = true; resizeStage(st);
  return st;
}
function resizeStage(st) {
  const w = st.canvas.clientWidth, h = st.canvas.clientHeight; if (!w || !h) return;
  st.renderer.setSize(w, h, false); st.camera.aspect = w / h; st.camera.updateProjectionMatrix(); st.dirty = true;
}
function makeGrid(st, size, div) {
  if (st.grid) { st.scene.remove(st.grid); st.grid.geometry.dispose(); st.grid.material.dispose(); }
  const c = palette().grid;
  st.grid = new THREE.GridHelper(size, div, c, c); st.grid.material.transparent = true; st.grid.material.opacity = 0.7;
  st.scene.add(st.grid);
}
function recolour(st) {
  if (st.theme === themeVer) return; st.theme = themeVer;
  const p = palette();
  if (st.grid) { const g = st.grid; st.scene.remove(g); g.geometry.dispose(); g.material.dispose(); st.grid = new THREE.GridHelper(st.opt.gridSize, st.opt.gridDiv, p.grid, p.grid); st.grid.material.transparent = true; st.grid.material.opacity = 0.7; st.grid.scale.copy(g.scale); st.grid.position.copy(g.position); st.scene.add(st.grid); }
  if (st.trail) st.trail.material.color.copy(p.trail);
  if (st.drop) st.drop.material.color.copy(p.fg3);
  st.dirty = true;
}
function renderStage(st) {
  if (!st.ok) return;
  recolour(st);
  if (st.controls.update()) st.dirty = true;
  if (!st.dirty) return; st.dirty = false;
  st.renderer.render(st.scene, st.camera);
}

// ---------------------------------------------------------------- plots (inline SVG, no library)
const SNS = 'http://www.w3.org/2000/svg';
function svgEl(tag, attrs, parent) { const n = document.createElementNS(SNS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; }
// spec: title, xs, series[{ys, label}], lines[{y, label}], bands[{x0, x1}], vlines[{x}], xlabel, onSet(x), xmin, xmax,
//       floor0 (axis starts at 0 when no value is below 0), peak (fmt of the highest value; its time is shown too)
// Drawn at the width of its own grid cell (1 SVG unit = 1 CSS px), so the 12 px tick text is 12 px on screen.
function makePlot(host, spec) {
  const H = 150, ML = 46, MR = 10, MT = 8, MB = 22;
  const wrap = document.createElement('div'); wrap.className = 'rp-plot';
  const head = document.createElement('div'); head.className = 'rp-plot-h';
  head.innerHTML = '<span>' + esc(spec.title) + '</span><b class="rp-plot-v"></b>';
  wrap.appendChild(head);
  host.appendChild(wrap);
  const W = Math.max(240, Math.round(wrap.clientWidth || 420)), pw = W - ML - MR, ph = H - MT - MB;
  const svg = svgEl('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': spec.title + ' against time' }, wrap);
  const xmin = spec.xmin, xmax = spec.xmax;
  let lo = Infinity, hi = -Infinity;
  for (const s of spec.series) for (const y of s.ys) { if (y < lo) lo = y; if (y > hi) hi = y; }
  for (const l of spec.lines || []) { lo = Math.min(lo, l.y); hi = Math.max(hi, l.y); }
  if (!(hi > lo)) { hi = lo + 1; }
  const floor0 = !!spec.floor0 && lo >= 0;
  const pad = (hi - lo) * 0.06; lo = floor0 ? 0 : lo - pad; hi += pad;
  // round-number y ticks: a step of 1, 2 or 5 times a power of ten, about four intervals
  const raw = (hi - lo) / 4, mag = Math.pow(10, Math.floor(Math.log10(raw))), fr = raw / mag;
  const step = (fr <= 1 ? 1 : fr <= 2 ? 2 : fr <= 5 ? 5 : 10) * mag;
  const dec = step >= 1 ? 0 : step >= 0.1 ? 1 : step >= 0.01 ? 2 : 3;
  const X = x => ML + (x - xmin) / (xmax - xmin || 1) * pw, Y = y => MT + (1 - (y - lo) / (hi - lo)) * ph;
  for (const b of spec.bands || []) svgEl('rect', { x: X(b.x0), y: MT, width: Math.max(1, X(b.x1) - X(b.x0)), height: ph, class: 'rp-band' }, svg);
  for (let k = Math.ceil(lo / step - 1e-9); k * step <= hi + 1e-9; k++) {
    const y = k * step;
    svgEl('line', { x1: ML, x2: ML + pw, y1: Y(y), y2: Y(y), class: 'rp-grid' }, svg);
    const t = svgEl('text', { x: ML - 5, y: Y(y) + 4, class: 'rp-tick', 'text-anchor': 'end' }, svg); t.textContent = nf(y, dec);
  }
  const nt = Math.min(6, Math.max(2, Math.floor(pw / 80)));
  for (let k = 0; k <= nt; k++) {
    const x = xmin + (xmax - xmin) * k / nt;
    const t = svgEl('text', { x: X(x), y: H - 6, class: 'rp-tick', 'text-anchor': k === 0 ? 'start' : k === nt ? 'end' : 'middle' }, svg); t.textContent = nf(x, xmax - xmin < 5 ? 2 : xmax - xmin < 50 ? 1 : 0) + (k === nt ? ' ' + (spec.xlabel || 's') : '');
  }
  for (const v of spec.vlines || []) if (v.x >= xmin && v.x <= xmax) svgEl('line', { x1: X(v.x), x2: X(v.x), y1: MT, y2: MT + ph, class: 'rp-vline' }, svg);
  for (const l of spec.lines || []) {
    svgEl('line', { x1: ML, x2: ML + pw, y1: Y(l.y), y2: Y(l.y), class: 'rp-limit' }, svg);
    const t = svgEl('text', { x: ML + pw - 3, y: Y(l.y) - 4, class: 'rp-limit-t', 'text-anchor': 'end' }, svg); t.textContent = l.label;
  }
  spec.series.forEach((s, k) => {
    let d = ''; const n = spec.xs.length;
    for (let i = 0; i < n; i++) d += (i ? 'L' : 'M') + X(spec.xs[i]).toFixed(1) + ' ' + Y(s.ys[i]).toFixed(1);
    svgEl('path', { d, class: 'rp-line rp-s' + k, fill: 'none' }, svg);
  });
  if (spec.peak) {   // the highest value on the plot, with its time
    let bi = 0, bv = -Infinity;
    spec.series.forEach(s => s.ys.forEach((y, i) => { if (y > bv) { bv = y; bi = i; } }));
    const px = X(spec.xs[bi]), py = Y(bv), right = px > ML + pw * 0.6;
    svgEl('circle', { cx: px, cy: py, r: 3, class: 'rp-peak-dot' }, svg);
    const t = svgEl('text', { x: px + (right ? -6 : 6), y: Math.max(MT + 12, py - 6), class: 'rp-peak-t', 'text-anchor': right ? 'end' : 'start' }, svg);
    t.textContent = 'peak ' + spec.peak(bv) + ' at ' + nf(spec.xs[bi], 1) + ' s';
  }
  if (spec.series.length > 1) {   // direct labels: colour is not the only cue (each trace also has its own dash)
    const lg = document.createElement('div'); lg.className = 'rp-legend';
    lg.innerHTML = spec.series.map((s, k) => '<span><svg width="22" height="8" aria-hidden="true"><line x1="0" x2="22" y1="4" y2="4" class="rp-line rp-s' + k + '"/></svg>' + esc(s.label) + '</span>').join('');
    wrap.appendChild(lg);
  }
  const cur = svgEl('line', { x1: ML, x2: ML, y1: MT, y2: MT + ph, class: 'rp-cursor' }, svg);
  const dots = spec.series.map((s, k) => svgEl('circle', { r: 3, cx: ML, cy: MT, class: 'rp-dot rp-d' + k }, svg));
  const readX = ev => { const r = svg.getBoundingClientRect(); return clamp(xmin + ((ev.clientX - r.left) * (W / r.width) - ML) / pw * (xmax - xmin), xmin, xmax); };
  if (spec.onSet) {
    svg.classList.add('rp-click');
    svg.addEventListener('pointerdown', ev => { svg.setPointerCapture(ev.pointerId); spec.onSet(readX(ev)); });
    svg.addEventListener('pointermove', ev => { if (ev.buttons) spec.onSet(readX(ev)); });
  }
  const vEl = head.querySelector('.rp-plot-v');
  return { set(x, vals, text) {
    const px = X(clamp(x, xmin, xmax)); cur.setAttribute('x1', px); cur.setAttribute('x2', px);
    dots.forEach((d, k) => { d.setAttribute('cx', px); d.setAttribute('cy', Y(vals[k])); });
    vEl.textContent = text;
  } };
}

// ---------------------------------------------------------------- timeline control (slider, play, speed)
function timeline(root, p, opts) {
  const tl = { t: 0, tmax: 1, playing: false, speed: opts.speed, onChange: opts.onChange, changed: true };
  const slider = $('#rp-' + p + '-slider', root), play = $('#rp-' + p + '-play', root), label = $('#rp-' + p + '-time', root);
  tl.set = t => { tl.t = clamp(t, 0, tl.tmax); tl.changed = true; };
  tl.range = (tmax, step) => { tl.tmax = tmax; slider.max = String(tmax); if (step) slider.step = String(step); tl.t = 0; tl.changed = true; setPlaying(false); };
  const setPlaying = on => { tl.playing = on; play.textContent = on ? 'Pause' : 'Play'; if (on) kick(); };   // the label is the state (no aria-pressed)
  tl.setPlaying = setPlaying;
  slider.addEventListener('input', () => tl.set(parseFloat(slider.value)));
  play.addEventListener('click', () => { if (!tl.playing && tl.t >= tl.tmax) tl.set(0); setPlaying(!tl.playing); });
  root.addEventListener('click', ev => {
    const b = ev.target.closest('button[data-speed]'); if (!b || !root.contains(b)) return;
    tl.speed = parseFloat(b.dataset.speed);
    b.parentElement.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  });
  tl.tick = dt => {
    if (tl.playing) { tl.t += dt * tl.speed; tl.changed = true; if (tl.t >= tl.tmax) { tl.t = tl.tmax; setPlaying(false); } }
    if (!tl.changed) return false;
    tl.changed = false; slider.value = String(tl.t); slider.setAttribute('aria-valuetext', opts.vt(tl.t)); label.textContent = opts.fmt(tl.t); tl.onChange(tl.t); return true;
  };
  return tl;
}

// ---------------------------------------------------------------- generic panel: visible -> init once -> tick while on screen
function addPanel(root, init) {
  const P = { root, visible: false, ready: false, starting: false, tick: () => false, render: () => {} };
  const io = new IntersectionObserver(es => {
    for (const en of es) {
      P.visible = en.isIntersecting;
      if (P.visible && !P.ready && !P.starting) { P.starting = true; Promise.resolve(init(P)).then(() => { P.ready = true; kick(); }).catch(err => { P.starting = false; P.fail && P.fail(err); console.warn('replay panel failed: ' + (err && err.message)); }); }
    }
    kick();
  }, { rootMargin: '120px' });
  io.observe(root); panels.push(P); return P;
}
let raf = 0, last = 0;
function kick() { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } }
function tick(now) {
  raf = 0; const dt = Math.min(0.25, (now - last) / 1000); last = now;
  let any = false;
  for (const P of panels) if (P.visible && P.ready) { any = true; P.tick(dt); P.render(); }
  if (any) raf = requestAnimationFrame(tick);
}

// ================================================================ FLIGHT
const MARK_LABEL = { t_armed: 'Motors armed', t_climb_done: 'Climb finished', t_qstab: 'QSTABILIZE (transition starts)', t_fbwa: 'FBWA mode', t_fwdone: 'Forward transition done',
  t_cruise_mode: 'CRUISE mode', t_cruise_end: 'Cruise ended', t_back: 'Back-transition starts', t_desc0: 'Descent starts', t_qland: 'QLAND (landing)' };
// pass lines in words: [name, unit]; the value and the limit come from the file's own strings
const PF_LABEL = { alt_peak_abs: ['Peak altitude', 'm'], alt_max_gain: ['Highest climb during the transition', 'm'], 't_to_1.3Vs_s': ['Time to 1.3 × stall speed', 's'],
  t_cap_run_s: ['Longest run at the motor cap', 's'], t_ge85_s: ['Time with a motor at 85 % or more', 's'], pitch_use_15: ['Elevon pitch use, share of ±15°', '%'],
  t_elevon_sat_s: ['Time with the elevons saturated', 's'], touch_in_flight: ['Fin-foot contacts while flying', 'contacts'] };
// ArduPilot mode names kept (so they match the logs), with a plain-words gloss
const MODE_GLOSS = { MANUAL: 'pilot flies', QHOVER: 'hover, altitude hold', QLOITER: 'hover, position hold', QSTAB: 'stabilised, transition starts', FBWA: 'fixed wing, attitude held', CRUISE: 'forward cruise', QLAND: 'landing' };
const MARK_MODE = { t_qstab: 'QSTAB', t_fbwa: 'FBWA', t_cruise_mode: 'CRUISE' };   // event marks at the same moment as a mode entry
const CG_AC = [0.02205, -0.00332, 0.00656];      // CAD-frame CG, m (cad_mass.json, T-098 basis); only offsets where the model hangs from the recorded position
const TH_PROP = () => manifest.th_to_prop;       // th1..th4 -> prop corner (a_plant.py motor order 1 FR, 2 RL, 3 FL, 4 RR in the belly-forward copter frame)
const PCT = k => k === 'pitch_use_15';
const fmtNum = x => { const r = Math.round(x * 1e6) / 1e6; return Number.isInteger(r) ? String(r) : nf(r, 1); };
const pfValue = (k, v) => fmtNum(PCT(k) ? v * 100 : v) + ' ' + (PF_LABEL[k] || [0, ''])[1];
function pfLimit(k, s) {
  const m = /^(<=|>=|==|<|>)\s*([0-9.]+)/.exec(String(s).trim()); if (!m) return String(s);
  const op = { '<': '<', '<=': '≤', '>=': '≥', '>': '>', '==': '=' }[m[1]];
  return op + ' ' + fmtNum(PCT(k) ? parseFloat(m[2]) * 100 : parseFloat(m[2])) + ' ' + (PF_LABEL[k] || [0, ''])[1];
}

function mountFlight() {
  const root = $('#rp-flight'); if (!root) return;
  const sel = $('#rp-f-case', root), msg = $('#rp-f-msg', root), over = $('#rp-f-over', root), verdict = $('#rp-f-verdict');
  const F = { D: null, key: null };
  let st = null, rg = null, tl = null, plots = [], read = null;
  const showMsg = (t, err) => { msg.textContent = t || ''; msg.hidden = !t; msg.classList.toggle('rp-err', !!err); };

  const P = addPanel(root, async () => {
    showMsg('Loading 3-D model…');
    st = makeStage($('#rp-f-canvas', root), { gridSize: 100, gridDiv: 100 });
    if (!st.ok) { showMsg('3-D is not available in this browser. The plots below still work.', true); }
    if (st.ok) {
      makeGrid(st, 100, 100);
      const gltf = await loadModel(); rg = rig(gltf.scene.clone(true)); st.scene.add(rg.root);   // clone: the parsed scene stays pristine for the landing panel
      st.trailGeo = new THREE.BufferGeometry(); st.trail = new THREE.Line(st.trailGeo, new THREE.LineBasicMaterial({ color: palette().trail })); st.trail.frustumCulled = false; st.scene.add(st.trail);
      const dg = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, -1, 0)]);
      st.drop = new THREE.Line(dg, new THREE.LineBasicMaterial({ color: palette().fg3, transparent: true, opacity: 0.6 })); st.drop.frustumCulled = false; st.scene.add(st.drop);
    }
    tl = timeline(root, 'f', { speed: 1, fmt: t => 't = ' + nf(t, 1) + ' s', vt: t => nf(t, 1) + ' seconds', onChange: t => apply(t) });
    P.tl = tl;
    read = buildRead($('#rp-f-read', root), [['run', 'Run', 'txt'], ['mass', 'Mass'], ['t', 'Time'], ['alt', 'Altitude'], ['V', 'Airspeed'], ['pitch', 'Pitch (90° = nose straight up)'],
      ['use', 'Elevon pitch use, share of ±15°'], ['dl', 'Left elevon angle (trailing edge down +)'], ['dr', 'Right elevon angle (trailing edge down +)']],
      $('#rp-f-key', root), [['alt', 'Altitude'], ['V', 'Airspeed'], ['pitch', 'Pitch']]);
    sel.addEventListener('change', () => load(sel.value));
    root.addEventListener('click', ev => {
      const c = ev.target.closest('button[data-t]'); if (c) { tl.set(parseFloat(c.dataset.t)); return; }
      const dir = ev.target.closest('#rp-f-prev') ? -1 : ev.target.closest('#rp-f-next') ? 1 : 0;
      if (dir && F.D) { const ts = F.events; const t = tl.t; const nxt = dir > 0 ? ts.find(x => x > t + 0.05) : [...ts].reverse().find(x => x < t - 0.05); if (nxt !== undefined) tl.set(nxt); }
      if (ev.target.closest('#rp-f-reset') && st && st.ok) { st.lastTarget = null; tl.changed = true; }
    });
    new ResizeObserver(() => { const w = Math.round($('#rp-f-plots', root).clientWidth); if (F.D && Math.abs(w - (F.plotW || 0)) > 6) buildPlots(); }).observe($('#rp-f-plots', root));
    await load(sel.value);
  });
  P.fail = err => showMsg('Could not load: ' + err.message, true);
  P.tick = dt => { const c = tl.tick(dt); if (c && st.ok) st.dirty = true; return c; };
  P.render = () => { if (st && st.ok) renderStage(st); };

  async function load(key) {
    F.key = key; showMsg('Loading run data…'); if (tl) tl.setPlaying(false);
    const m = manifest.flight.find(c => c.id === key);
    const { data } = await fetchJSON('assets/sims3d/' + m.file + '?v=' + VER);
    F.D = data; derive(data);
    tl.range(data.t[data.t.length - 1], 0.1);
    buildTimeline(); buildVerdict(); buildPF(); buildPlots();
    if (st.ok) {
      const n = data.t.length, pos = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { pos[3 * i] = data.pe[i]; pos[3 * i + 1] = data.alt[i]; pos[3 * i + 2] = -data.pn[i]; }
      st.trailGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); st.trailGeo.setDrawRange(0, 1); st.trailGeo.computeBoundingSphere();
      st.lastTarget = null;
    }
    read.set('run', m.label, 'txt'); read.set('mass', nf(data.meta.mass_kg, 3) + ' kg');
    showMsg(st.ok ? '' : '3-D is not available in this browser. The plots below still work.', !st.ok);
    tl.changed = true; apply(0);
  }
  function derive(D) {
    const n = D.t.length; let r0 = 0, h0 = 0, found = false;
    for (let i = 0; i < n; i++) if (D.pitch[i] < 80) { r0 = D.roll[i]; h0 = D.hdg_nose[i]; found = true; break; }
    F.rollH = new Float64Array(n); F.hdgH = new Float64Array(n);
    let r = found ? r0 : 0, h = found ? h0 : 0;     // before the first valid sample: hold the first valid one so the stance does not snap
    for (let i = 0; i < n; i++) { if (D.pitch[i] < 80) { r = D.roll[i]; h = D.hdg_nose[i]; } F.rollH[i] = r; F.hdgH[i] = h; }
    F.ang = [0, 1, 2, 3].map(k => { const a = new Float64Array(n); for (let i = 0; i < n - 1; i++) { const th = Math.max(0, D['th' + (k + 1)][i]); a[i + 1] = a[i] + Math.min(36, 12 * Math.sqrt(th)) * (D.t[i + 1] - D.t[i]); } return a; });
    const mk = D.events.marks;
    F.marks = Object.keys(mk).filter(k => k.startsWith('t_')).map(k => ({ k, t: mk[k] })).sort((a, b) => a.t - b.t);
    F.modes = (D.events.modes || []).filter(m => typeof m[1] === 'string' && m[0] > 0).map(m => ({ t: m[0], label: m[1] }));
    const w0 = mk.t_fbwa, w1 = mk.t_cruise_end; let mx = null;
    if (w0 !== undefined && w1 !== undefined) { for (let i = 0; i < n; i++) if (D.t[i] >= w0 && D.t[i] <= w1) mx = Math.max(mx === null ? -1 : mx, D.pitch_use_15[i]); }
    F.useMax10Hz = mx;
    const pl = D.meta.pass_fail.lines.pitch_use_15; F.useLimit = pl ? parseFloat(String(pl.limit).replace(/[^0-9.]/g, '')) : 0.6;
  }
  // one time-ordered list. Each autopilot mode is one entry on the simulation clock (its event mark, if it has one, is the same entry).
  // The other event marks keep the test driver's clock and carry a dagger.
  function buildTimeline() {
    const D = F.D, host = $('#rp-f-marks', root), tmax = D.t[D.t.length - 1];
    const items = F.modes.map(m => ({ t: m.t, text: m.label + (MODE_GLOSS[m.label] ? ' (' + MODE_GLOSS[m.label] + ')' : '') }));
    for (const x of F.marks) {
      if (MARK_MODE[x.k] && F.modes.some(m => m.label === MARK_MODE[x.k])) continue;
      items.push({ t: x.t, text: MARK_LABEL[x.k] || x.k, dagger: true });
    }
    items.sort((a, b) => a.t - b.t);
    host.innerHTML = '<span class="rp-chip-h">Timeline</span>' + items.map(it => '<button type="button" class="rp-chip" data-t="' + it.t + '" aria-label="Jump to ' + esc(it.text) + ' at ' + nf(it.t, 1) + ' seconds">'
      + esc(it.text) + (it.dagger ? ' †' : '') + ' <small>' + nf(it.t, 1) + ' s</small></button>').join('');
    F.events = items.map(i => i.t);
    $('#rp-f-ticks', root).innerHTML = F.events.map(t => '<i style="left:' + (100 * t / tmax).toFixed(2) + '%"></i>').join('');
  }
  function buildVerdict() {
    const pf = F.D.meta.pass_fail, lines = Object.entries(pf.lines), fails = lines.filter(([, l]) => !l.pass);
    const describe = ([k, l]) => (PF_LABEL[k] || [k])[0] + ' is ' + pfValue(k, l.value) + ' (limit ' + pfLimit(k, l.limit) + ')';
    verdict.textContent = fails.length ? 'Fails ' + fails.length + ' of ' + lines.length + ' recorded lines: ' + fails.map(describe).join('; ') + '.'
      : 'Passes all ' + lines.length + ' recorded lines.';
    verdict.classList.toggle('rp-bad', fails.length > 0); verdict.classList.toggle('rp-ok', fails.length === 0);
  }
  function buildPF() {
    const D = F.D, pf = D.meta.pass_fail, host = $('#rp-f-pf', root), ps = D.meta.pitch_use_scalar;
    const rows = Object.entries(pf.lines).map(([k, l]) => '<tr><th scope="row" class="first">' + esc((PF_LABEL[k] || [k])[0]) + '</th><td class="val">' + esc(pfValue(k, l.value))
      + '</td><td class="val">' + esc(pfLimit(k, l.limit)) + '</td><td class="' + (l.pass ? 'rp-ok' : 'rp-bad') + '">' + (l.pass ? 'pass' : 'FAIL') + '</td></tr>').join('');
    host.innerHTML = '<table class="ds-table rp-pftab"><caption>Recorded pass lines</caption><thead><tr><th scope="col">Line</th><th scope="col">Value</th><th scope="col">Limit</th><th scope="col">Result</th></tr></thead><tbody>' + rows + '</tbody></table>'
      + '<p class="rp-cap">Elevon pitch use is the largest share of ±15° between FBWA and the end of cruise. The recorded summary gives ' + esc(pfValue('pitch_use_15', ps.pitch_use_15))
      + '; this 10 Hz file gives ' + (F.useMax10Hz === null ? '—' : nf(F.useMax10Hz * 100, 1) + ' %') + ' in the same window.</p>'
      + '<span class="ds-source">Lines from mechanism/out/T101_results.json via the export (<code class="ds-inline">meta.pass_fail</code>).</span>';
  }
  function buildPlots() {
    const D = F.D, host = $('#rp-f-plots', root); F.plotW = Math.round(host.clientWidth || 0);
    host.innerHTML = ''; plots = [];
    const mk = D.events.marks, tmax = D.t[D.t.length - 1], vl = F.events.map(x => ({ x })), set = x => tl.set(x);
    const base = { xs: D.t, xmin: 0, xmax: tmax, vlines: vl, onSet: set, xlabel: 's' };
    const useY = D.pitch_use_15.map(v => v * 100), lim = F.useLimit * 100;
    plots.push({ key: 'alt', p: makePlot(host, { ...base, floor0: true, title: 'Altitude, m', series: [{ ys: D.alt }], peak: v => nf(v, 1) + ' m' }) });
    plots.push({ key: 'V', p: makePlot(host, { ...base, floor0: true, title: 'Airspeed, m/s', series: [{ ys: D.V }], peak: v => nf(v, 1) + ' m/s' }) });
    plots.push({ key: 'pitch', p: makePlot(host, { ...base, title: 'Pitch, deg (90 = nose straight up)', series: [{ ys: D.pitch }], peak: v => nf(v, 1) + '°' }) });
    const bands = mk.t_fbwa !== undefined && mk.t_cruise_end !== undefined ? [{ x0: mk.t_fbwa, x1: mk.t_cruise_end }] : [];
    plots.push({ key: 'use', p: makePlot(host, { ...base, floor0: true, title: 'Elevon pitch use, % of ±15° (shaded: FBWA to end of cruise)', series: [{ ys: useY }],
      lines: [{ y: lim, label: 'limit ' + nf(lim, 0) + ' %' }], bands, peak: v => nf(v, 1) + ' %' }) });
    tl.changed = true;
  }
  function apply(t) {
    const D = F.D; if (!D) return;
    const ts = D.t, n = ts.length;
    let lo = 0, hi = n - 1; while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (ts[mid] <= t) lo = mid; else hi = mid; }
    const i = lo, f = clamp((t - ts[i]) / ((ts[i + 1] - ts[i]) || 1), 0, 1);
    const L = a => a[i] + (a[i + 1] - a[i]) * f;
    const LA = a => { let d = a[i + 1] - a[i]; d -= 360 * Math.round(d / 360); return a[i] + d * f; };
    const pitch = L(D.pitch), roll = LA(F.rollH), hdg = LA(F.hdgH), dl = L(D.dl), dr = L(D.dr);
    const alt = L(D.alt), V = L(D.V), use = L(D.pitch_use_15) * 100, lim = F.useLimit * 100;
    read.set('t', nf(t, 1) + ' s'); read.set('alt', nf(alt, 1) + ' m'); read.set('V', nf(V, 1) + ' m/s'); read.set('pitch', nf(pitch, 1) + '°');
    read.set('use', nf(use, 1) + ' % (limit ' + nf(lim, 0) + ' %)', use > lim ? 'rp-bad' : '');
    read.set('dl', nf(dl, 1) + '°'); read.set('dr', nf(dr, 1) + '°');
    for (const pl of plots) {
      if (pl.key === 'alt') pl.p.set(t, [alt], nf(alt, 1) + ' m');
      else if (pl.key === 'V') pl.p.set(t, [V], nf(V, 1) + ' m/s');
      else if (pl.key === 'pitch') pl.p.set(t, [pitch], nf(pitch, 1) + '°');
      else pl.p.set(t, [use], nf(use, 1) + ' % ' + (use > lim ? 'FAIL, above ' : 'pass, within ') + nf(lim, 0) + ' %');
    }
    if (!st || !st.ok || !rg) return;
    // attitude: body (CAD x aft, y right, z up) -> scene (x east, y up, z -north); pitch about the body y axis, nose up positive.
    const cp = Math.cos(pitch * RAD), sp = Math.sin(pitch * RAD), ch = Math.cos(hdg * RAD), sh = Math.sin(hdg * RAD), cr = Math.cos(roll * RAD), sr = Math.sin(roll * RAD);
    const nose = new THREE.Vector3(cp * sh, cp * ch, sp), r0 = new THREE.Vector3(ch, -sh, 0), u0 = new THREE.Vector3().crossVectors(r0, nose);   // ENU
    const right = r0.clone().multiplyScalar(cr).addScaledVector(u0, -sr), up = u0.clone().multiplyScalar(cr).addScaledVector(r0, sr);
    const S = v => new THREE.Vector3(v.x, v.z, -v.y);                      // ENU -> scene (x east, y up, z -north)
    const xg = S(nose).negate(), yg = S(up), zg = S(right).negate();      // glTF axes: x aft = -nose, y up, z = -right
    const Rm = new THREE.Matrix4().makeBasis(xg, yg, zg);
    const q = new THREE.Quaternion().setFromRotationMatrix(Rm);
    const P = new THREE.Vector3(L(D.pe), alt, -L(D.pn));
    const cg = new THREE.Vector3(...M.ac2gl(CG_AC)).applyQuaternion(q);
    rg.root.quaternion.copy(q); rg.root.position.copy(P).sub(cg); rg.root.updateMatrixWorld(true);
    for (const s of ['L', 'R']) { const h = rg.hinges[s]; if (h) placeAbout(rg.side[s], h.pivot, h.axis, (s === 'L' ? dl : dr) * RAD); }
    // propellers are still when reduced motion is on (the spin is the only motion of the props)
    TH_PROP().forEach((c, k) => {
      const pg = manifest.props[c], ang = REDUCE ? 0 : (F.ang[k][i] + (F.ang[k][i + 1] - F.ang[k][i]) * f) * pg.dir;
      placeAbout(rg.props[c], new THREE.Vector3(...M.ac2gl(pg.center)), new THREE.Vector3(...M.ac2gl(pg.axis)).normalize(), ang);
    });
    st.trailGeo.setDrawRange(0, i + 1);
    const pa = st.drop.geometry.attributes.position; pa.setXYZ(0, P.x, P.y, P.z); pa.setXYZ(1, P.x, 0, P.z); pa.needsUpdate = true;
    // camera follows the aircraft (offset kept), grid snaps under it
    if (!st.lastTarget) { st.lastTarget = P.clone(); st.camera.position.copy(P).add(new THREE.Vector3(1.0, 0.7, 1.8)); st.controls.target.copy(P); }
    else { const d = P.clone().sub(st.lastTarget); st.camera.position.add(d); st.controls.target.copy(P); st.lastTarget.copy(P); }
    const dist = st.camera.position.distanceTo(st.controls.target), cell = dist < 6 ? 1 : dist < 60 ? 10 : 100;
    st.grid.scale.setScalar(cell); st.grid.position.set(Math.round(P.x / cell) * cell, 0, Math.round(P.z / cell) * cell);
    over.textContent = 'grid cell ' + cell + ' m · height ' + nf(alt, 1) + ' m · initial view from the south (north is away from you)';
    st.dirty = true;
  }
  window.__rp = window.__rp || {}; window.__rp.flight = { get st() { return st; }, get rg() { return rg; }, get tl() { return tl; }, F, apply, load, renderNow: () => { st.dirty = true; renderStage(st); } };
  return P;
}

// ---------------------------------------------------------------- live readout helper
// rows: [key, label, 'txt' for words (sans face) or omitted for numbers]; strip: optional compact copy under the slider (keys: [key, short label])
function buildRead(host, rows, strip, keys) {
  host.innerHTML = '<dl>' + rows.map(([k, l, t]) => '<div><dt>' + esc(l) + '</dt><dd data-k="' + k + '"' + (t ? ' class="txt"' : '') + '></dd></div>').join('') + '</dl>';
  const m = {}, s = {};
  host.querySelectorAll('dd').forEach(d => { m[d.dataset.k] = d; });
  if (strip && keys) {
    strip.innerHTML = keys.map(([k, l]) => '<div><span>' + esc(l) + '</span><b data-s="' + k + '"></b></div>').join('');
    strip.querySelectorAll('b').forEach(d => { s[d.dataset.s] = d; });
  }
  return { set(k, text, cls, short) {
    const d = m[k]; if (!d) return;
    if (d.textContent !== text) d.textContent = text;
    d.classList.toggle('rp-ok', cls === 'rp-ok'); d.classList.toggle('rp-bad', cls === 'rp-bad');
    const b = s[k]; if (b) { const v = short === undefined ? text : short; if (b.textContent !== v) b.textContent = v; b.classList.toggle('rp-ok', cls === 'rp-ok'); b.classList.toggle('rp-bad', cls === 'rp-bad'); }
  }, el: m };
}

// ================================================================ LANDING
const LAND_LABEL = ['UR', 'LR', 'UL', 'LL'];
// pads as 3-D labels: sprites at each pad centre, children of the posed root so they move with the aircraft; rebuilt on a theme change
function padLabels(rgx) {
  if (rgx.labels) { rgx.root.remove(rgx.labels); rgx.labels.traverse(o => { if (o.material) { if (o.material.map) o.material.map.dispose(); o.material.dispose(); } }); }
  const grp = new THREE.Group(); rgx.labels = grp; rgx.labelTheme = themeVer;
  const fg = cssv('--fg') || '#1B2230', bg = cssv('--bg') || '#F4F1E8';
  for (const c of LAND_LABEL) {
    const pd = rgx.pads[c]; if (!pd) continue;
    const cv = document.createElement('canvas'); cv.width = 96; cv.height = 48;
    const g = cv.getContext('2d'); g.font = '600 30px "IBM Plex Sans", "Segoe UI", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.lineWidth = 8; g.strokeStyle = bg; g.strokeText(c, 48, 25); g.fillStyle = fg; g.fillText(c, 48, 25);
    const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
    sp.position.copy(pd.center); sp.scale.set(0.09, 0.045, 1); sp.renderOrder = 10;
    grp.add(sp);
  }
  rgx.root.add(grp);
}
function mountLanding() {
  const root = $('#rp-landing'); if (!root) return;
  const sel = $('#rp-l-case', root), msg = $('#rp-l-msg', root), over = $('#rp-l-over', root), verdict = $('#rp-l-verdict');
  const Lc = { D: null, key: null };
  let st = null, rg = null, tl = null, plots = [], read = null;
  const showMsg = (t, err) => { msg.textContent = t || ''; msg.hidden = !t; msg.classList.toggle('rp-err', !!err); };
  const Cm = new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1), CmT = Cm.clone().transpose();   // world (x, y, z-up) -> scene (x, z, -y)

  const P = addPanel(root, async () => {
    showMsg('Loading 3-D model…');
    st = makeStage($('#rp-l-canvas', root), { gridSize: 4, gridDiv: 40 });
    if (!st.ok) showMsg('3-D is not available in this browser. The plots below still work.', true);
    else {
      makeGrid(st, 4, 40);
      const gltf = await loadModel(); rg = rig(gltf.scene.clone(true)); st.scene.add(rg.root);   // second scene: clone of the shared parsed model
      padLabels(rg);
      st.home = { pos: new THREE.Vector3(0.95, 0.6, 1.4), target: new THREE.Vector3(0, 0.2, 0) };
      st.camera.position.copy(st.home.pos); st.controls.target.copy(st.home.target);
    }
    tl = timeline(root, 'l', { speed: 0.1, fmt: t => 't = ' + nf(t * 1000, 0) + ' ms', vt: t => nf(t * 1000, 0) + ' milliseconds', onChange: t => apply(t) });
    read = buildRead($('#rp-l-read', root), [['case', 'Case', 'txt'], ['mass', 'Mass'], ['t', 'Time'], ['n', 'Load factor now'], ['nmax', 'Peak load factor so far'],
      ['s', 'Stroke now, worst pad'], ['smax', 'Stroke, largest so far'], ['tilt', 'Tilt'], ['pads', 'Crush per pad now']],
      $('#rp-l-key', root), [['n', 'Load factor'], ['s', 'Stroke'], ['tilt', 'Tilt']]);
    sel.addEventListener('change', () => load(sel.value));
    root.addEventListener('click', ev => {
      if (ev.target.closest('#rp-l-reset') && st && st.ok) { st.camera.position.copy(st.home.pos); st.controls.target.copy(st.home.target); st.dirty = true; }
    });
    new ResizeObserver(() => { const w = Math.round($('#rp-l-plots', root).clientWidth); if (Lc.D && Math.abs(w - (Lc.plotW || 0)) > 6) buildPlots(); }).observe($('#rp-l-plots', root));
    await load(sel.value);
  });
  P.fail = err => showMsg('Could not load: ' + err.message, true);
  P.tick = dt => { const c = tl.tick(dt); if (c && st.ok) st.dirty = true; return c; };
  P.render = () => { if (st && st.ok) { if (rg && rg.labelTheme !== themeVer) padLabels(rg); renderStage(st); } };

  async function load(key) {
    Lc.key = key; showMsg('Loading case data…'); if (tl) tl.setPlaying(false);
    const m = manifest.landing.find(c => c.id === key);
    const { data } = await fetchJSON('assets/sims3d/' + m.file + '?v=' + VER);
    Lc.D = data;
    const n = data.t.length; Lc.maxCrush = new Float64Array(n); Lc.maxN = new Float64Array(n); let mc = 0, mn = 0;
    for (let i = 0; i < n; i++) { mc = Math.max(mc, ...data.crush_mm[i]); mn = Math.max(mn, data.load_factor_g[i]); Lc.maxCrush[i] = mc; Lc.maxN[i] = mn; }
    tl.range(data.t[n - 1], 0.005);
    read.set('case', m.label + ' (T-098: ' + m.case + ')', 'txt'); read.set('mass', nf(data.meta.mass_kg, 3) + ' kg');
    buildVerdict(); buildPlots(); showMsg(st.ok ? '' : '3-D is not available in this browser. The plots below still work.', !st.ok);
    tl.changed = true; apply(0);
  }
  // the verdict: the three limits, judged on the peaks of the run (peak load factor, largest pad crush, final tilt, the limit basis in the file)
  function buildVerdict() {
    const D = Lc.D, lim = D.meta.limits, last = Lc.maxN.length - 1;
    const items = [['peak load factor', nf(Lc.maxN[last], 2) + ' g', lim.load_factor_g + ' g', Lc.maxN[last] <= lim.load_factor_g],
      ['largest pad crush', nf(Lc.maxCrush[last], 2) + ' mm', lim.stroke_mm + ' mm', Lc.maxCrush[last] <= lim.stroke_mm],
      ['final tilt', nf(D.peaks.tilt_end_deg, 2) + '°', lim.tilt_deg + '°', D.peaks.tilt_end_deg <= lim.tilt_deg]];
    const fails = items.filter(it => !it[3]);
    const txt = it => it[0] + ' ' + it[1] + ' (limit ' + it[2] + ')';
    verdict.textContent = fails.length ? 'Fails: ' + fails.map(txt).join('; ') + '.' : 'Passes all three limits: ' + items.map(txt).join('; ') + '.';
    verdict.classList.toggle('rp-bad', fails.length > 0); verdict.classList.toggle('rp-ok', fails.length === 0);
  }
  function buildPlots() {
    const D = Lc.D, host = $('#rp-l-plots', root); Lc.plotW = Math.round(host.clientWidth || 0);
    host.innerHTML = ''; plots = []; const lim = D.meta.limits, tmax = D.t[D.t.length - 1], set = x => tl.set(x);
    const base = { xs: D.t, xmin: 0, xmax: tmax, onSet: set, xlabel: 's', floor0: true };
    plots.push({ key: 'n', p: makePlot(host, { ...base, title: 'Load factor, g', series: [{ ys: D.load_factor_g }], lines: [{ y: lim.load_factor_g, label: 'limit ' + lim.load_factor_g + ' g' }], peak: v => nf(v, 2) + ' g' }) });
    const cs = [0, 1, 2, 3].map(k => D.crush_mm.map(r => r[k]));
    plots.push({ key: 'c', p: makePlot(host, { ...base, title: 'Pad crush, mm (four pads)', series: cs.map((ys, k) => ({ ys, label: LAND_LABEL[k] })), lines: [{ y: lim.stroke_mm, label: 'limit ' + lim.stroke_mm + ' mm' }], peak: v => nf(v, 1) + ' mm' }) });
    plots.push({ key: 't', p: makePlot(host, { ...base, title: 'Tilt, deg', series: [{ ys: D.tilt_deg }], lines: [{ y: lim.tilt_deg, label: 'limit ' + lim.tilt_deg + '°' }], peak: v => nf(v, 2) + '°' }) });
    tl.changed = true;
  }
  const passTxt = (v, L, u) => (v <= L ? 'pass' : 'FAIL') + ' (limit ' + L + ' ' + u + ')';
  const qa = new THREE.Quaternion(), qb = new THREE.Quaternion(), Rw = new THREE.Matrix4(), Rs = new THREE.Matrix4();
  function apply(t) {
    const D = Lc.D; if (!D) return;
    const ts = D.t, n = ts.length, dt = (ts[n - 1] - ts[0]) / (n - 1);
    const i = clamp(Math.floor(t / dt), 0, n - 2), f = clamp(t / dt - i, 0, 1), lim = D.meta.limits;
    const L = (a, k) => a[i][k] + (a[i + 1][k] - a[i][k]) * f;
    const nNow = D.load_factor_g[i] + (D.load_factor_g[i + 1] - D.load_factor_g[i]) * f, tilt = D.tilt_deg[i] + (D.tilt_deg[i + 1] - D.tilt_deg[i]) * f;
    const crush = [0, 1, 2, 3].map(k => L(D.crush_mm, k)), cmax = Math.max(...crush), cm = Lc.maxCrush[i], nm = Lc.maxN[i], tEnd = D.peaks.tilt_end_deg;
    read.set('t', nf(t * 1000, 0) + ' ms');
    read.set('n', nf(nNow, 2) + ' g (limit ' + lim.load_factor_g + ' g)', '', nf(nNow, 2) + ' g');
    read.set('nmax', nf(nm, 2) + ' g; ' + passTxt(nm, lim.load_factor_g, 'g'), nm <= lim.load_factor_g ? 'rp-ok' : 'rp-bad');
    read.set('s', nf(cmax, 1) + ' mm', '', nf(cmax, 1) + ' mm');
    read.set('smax', nf(cm, 1) + ' mm; ' + passTxt(cm, lim.stroke_mm, 'mm'), cm <= lim.stroke_mm ? 'rp-ok' : 'rp-bad');
    read.set('tilt', 'now ' + nf(tilt, 2) + '°; limit ' + lim.tilt_deg + '° on the final tilt, which is ' + nf(tEnd, 2) + '° (' + (tEnd <= lim.tilt_deg ? 'pass' : 'FAIL') + ')',
      tEnd <= lim.tilt_deg ? 'rp-ok' : 'rp-bad', nf(tilt, 2) + '°');
    read.set('pads', LAND_LABEL.map((l, k) => l + ' ' + nf(crush[k], 1) + ' mm').join(' · '));
    for (const pl of plots) {
      if (pl.key === 'n') pl.p.set(t, [nNow], nf(nNow, 2) + ' g; peak so far ' + nf(nm, 2) + ' g, ' + (nm <= lim.load_factor_g ? 'pass' : 'FAIL'));
      else if (pl.key === 'c') pl.p.set(t, crush, nf(cm, 1) + ' mm largest so far, ' + (cm <= lim.stroke_mm ? 'pass' : 'FAIL'));
      else pl.p.set(t, [tilt], nf(tilt, 2) + '° now');
    }
    if (!st || !st.ok || !rg) return;
    // body (CAD axes: x aft, y right, z up) -> world (x, y, z up) by quat_wxyz; the glTF root frame is the CAD frame mapped by Cm, so R_scene = Cm R_world Cm^T.
    const a = D.quat_wxyz[i], b = D.quat_wxyz[i + 1];
    qa.set(a[1], a[2], a[3], a[0]); qb.set(b[1], b[2], b[3], b[0]); if (qa.dot(qb) < 0) qb.set(-qb.x, -qb.y, -qb.z, -qb.w); qa.slerp(qb, f);
    Rw.makeRotationFromQuaternion(qa); Rs.copy(Cm).multiply(Rw).multiply(CmT);
    const q = new THREE.Quaternion().setFromRotationMatrix(Rs);
    const p = [0, 1, 2].map(k => D.p[i][k] + (D.p[i + 1][k] - D.p[i][k]) * f), Ps = new THREE.Vector3(p[0], p[2], -p[1]);
    const cg = new THREE.Vector3(...M.ac2gl(D.meta.cg_m)).applyQuaternion(q);
    rg.root.quaternion.copy(q); rg.root.position.copy(Ps).sub(cg); rg.root.updateMatrixWorld(true);
    // pads: shortened by the recorded crush about the end that meets the shoe (smaller CAD x); the free end moves up off the ground
    manifest.pad_order.forEach((c, k) => { const pd = rg.pads[c]; if (!pd) return; const s = clamp(1 - crush[k] / 1000 / pd.len, 0.05, 1);
      _a.makeTranslation(pd.x0, 0, 0).multiply(_b.makeScale(s, 1, 1)).multiply(_c.makeTranslation(-pd.x0, 0, 0)); pd.part.node.matrix.copy(_a).multiply(pd.part.base); pd.part.node.matrixWorldNeedsUpdate = true; });
    over.textContent = 'pads ' + LAND_LABEL.join(', ') + ' drawn shortened by their crush · grid cell 0.1 m';
    st.dirty = true;
  }
  window.__rp = window.__rp || {}; window.__rp.landing = { get st() { return st; }, get rg() { return rg; }, get tl() { return tl; }, Lc, apply, load, renderNow: () => { st.dirty = true; renderStage(st); } };
  return P;
}

// ================================================================ LINKAGE
// pair names from the file, in words (the sign of a clevis cheek is the side: +1 right, -1 left, as in the file's conventions)
const PAIR_WORDS = { 'arm / servo case': 'servo arm and servo case', 'clevis cheek -1 / horn blade': 'left clevis cheek and horn blade', 'clevis cheek +1 / horn blade': 'right clevis cheek and horn blade' };
const pairWords = s => PAIR_WORDS[s] || String(s).replace(' / ', ' and ');
function mountLinkage() {
  const root = $('#rp-linkage'); if (!root) return;
  const K = { D: null, side: 'R', i: 0, playing: false, tau: 0, dirty: true };
  const slider = $('#rp-k-slider', root), play = $('#rp-k-play', root), timeEl = $('#rp-k-time', root), capEl = $('#rp-k-cap', root), verdict = $('#rp-k-verdict');
  let read = null, plots = [];
  const P = addPanel(root, async () => {
    const { data } = await fetchJSON('assets/sims3d/' + manifest.linkage.file + '?v=' + VER);
    K.D = data;
    read = buildRead($('#rp-k-read', root), [['d', 'Elevon angle (trailing edge down +)'], ['th', 'Servo arm angle'], ['gear', 'Elevon degrees per servo degree'], ['hm', 'Hinge moment'],
      ['tq', 'Servo hold torque needed'], ['rf', 'Pushrod force'], ['rod', 'Pushrod length'], ['c0', 'Minimum clearance, all pairs (includes designed contacts)', 'txt'],
      ['c1', 'Minimum clearance, designed contacts left out', 'txt']],
      $('#rp-k-key', root), [['d', 'Elevon angle'], ['hm', 'Hinge moment'], ['c0', 'Clearance']]);
    root.addEventListener('click', ev => {
      const b = ev.target.closest('button[data-side]'); if (!b) return; K.side = b.dataset.side;
      b.parentElement.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); setup();
    });
    slider.addEventListener('input', () => { K.i = nearest(parseFloat(slider.value)); K.dirty = true; });
    play.addEventListener('click', () => {
      K.playing = !K.playing; play.textContent = K.playing ? 'Pause' : 'Sweep';
      if (K.playing) { let u0 = K.i / (K.D[K.side].length - 1); if (u0 >= 0.999) u0 = 0; K.tau = u0 / 2; kick(); }
    });
    new ResizeObserver(() => { const w = Math.round($('#rp-k-plots', root).clientWidth); if (K.D && Math.abs(w - (K.plotW || 0)) > 6) buildPlots(); }).observe($('#rp-k-plots', root));
    setup();
  });
  P.fail = err => { capEl.textContent = 'Could not load: ' + err.message; };
  const poses = () => K.D[K.side];
  const nearest = d => { const a = poses(); let bi = 0, bd = 1e9; for (let i = 0; i < a.length; i++) { const e = Math.abs(a[i].delta_deg - d); if (e < bd) { bd = e; bi = i; } } return bi; };
  function setup() {
    const a = poses();
    slider.min = String(a[0].delta_deg); slider.max = String(a[a.length - 1].delta_deg); slider.step = String(a[1].delta_deg - a[0].delta_deg);
    K.i = nearest(0); K.dirty = true; buildPlots();
    verdict.textContent = 'No pass line in this file. The readings below are for the chosen elevon angle.';
  }
  P.tick = dt => {
    if (K.playing) {
      const n = poses().length; K.tau += dt / 10;   // a 10 s display cycle (not data)
      if (REDUCE) {                                  // reduced motion: one pass to the far end, then stop
        const u = Math.min(1, K.tau * 2); K.i = Math.round(u * (n - 1)); K.dirty = true;
        if (u >= 1) { K.playing = false; play.textContent = 'Sweep'; }
      } else {                                       // ping-pong across the range and back
        const ph = (K.tau * 2) % 2, u = ph < 1 ? ph : 2 - ph; K.i = Math.round(u * (n - 1)); K.dirty = true;
      }
    }
    if (!K.dirty) return false; K.dirty = false; apply(); return true;
  };
  function buildPlots() {
    const host = $('#rp-k-plots', root); K.plotW = Math.round(host.clientWidth || 0); host.innerHTML = ''; plots = [];
    const a = poses(), xs = a.map(p => p.delta_deg), set = x => { K.i = nearest(x); K.dirty = true; };
    const base = { xs, xmin: xs[0], xmax: xs[xs.length - 1], onSet: set, xlabel: 'deg' };
    plots.push({ key: 'hm', p: makePlot(host, { ...base, title: 'Hinge moment, N m, against elevon angle', series: [{ ys: a.map(p => p.hinge_moment_Nm) }] }) });
    plots.push({ key: 'cl', p: makePlot(host, { ...base, title: 'Minimum clearance, mm, against elevon angle', series: [{ ys: a.map(p => p.min_clearance_mm), label: 'all pairs' }, { ys: a.map(p => p.min_clearance_excl_design_contact_mm), label: 'designed contacts left out' }] }) });
    K.dirty = true;
  }
  const NS = 'http://www.w3.org/2000/svg';
  function drawSchem(hostId, bounds, items) {
    const host = $('#' + hostId, root), [x0, x1, y0, y1] = bounds, W = 360, Hh = Math.max(60, Math.min(260, 360 * (y1 - y0) / (x1 - x0)));
    host.innerHTML = '<svg viewBox="' + x0 + ' ' + (-y1) + ' ' + (x1 - x0) + ' ' + (y1 - y0) + '" preserveAspectRatio="xMidYMid meet" width="100%" style="max-height:' + Hh + 'px" font-size="' + ((x1 - x0) / 26).toFixed(2) + '" aria-hidden="true">' + items + '</svg>';
  }
  function apply() {
    const a = poses(), p = a[K.i], g = K.D.meta.geometry, sy = K.side === 'R' ? 1 : -1, p0 = a[nearest(0)];
    slider.value = String(p.delta_deg); slider.setAttribute('aria-valuetext', nf(p.delta_deg, 1) + ' degrees, trailing edge down positive');
    timeEl.textContent = 'elevon angle = ' + nf(p.delta_deg, 1) + '°';
    read.set('d', nf(p.delta_deg, 1) + '°', '', nf(p.delta_deg, 1) + '°'); read.set('th', nf(p.servo_theta_deg, 2) + '°'); read.set('gear', nf(p.gear_ddelta_dtheta, 3) + ' deg per deg');
    read.set('hm', nf(p.hinge_moment_Nm, 4) + ' N m', '', nf(p.hinge_moment_Nm, 3) + ' N m'); read.set('tq', nf(p.servo_torque_req_Nm, 4) + ' N m');
    read.set('rf', nf(p.rod_force_N, 1) + ' N'); read.set('rod', nf(p.rod_len_mm, 2) + ' mm');
    read.set('c0', nf(p.min_clearance_mm, 3) + ' mm; designed contact: ' + pairWords(p.min_clearance_pair), '', nf(p.min_clearance_mm, 3) + ' mm');
    read.set('c1', nf(p.min_clearance_excl_design_contact_mm, 3) + ' mm; closest pair: ' + pairWords(p.min_clearance_excl_pair), '', nf(p.min_clearance_excl_design_contact_mm, 3) + ' mm');
    capEl.textContent = 'The all-pairs minimum includes the declared design contacts (the pair named above touches by design), so it can read zero or close to it. The second line leaves the declared design contacts out. Solid hulls, so both are lower bounds.';
    // geometry in CAD mm: x aft, y span (+ right), z up. Top view uses (x, y); side view (x, z); SVG y runs down, so y is negated.
    const pv = [g.SV_XS_mm, sy * g.SERVO_Y_mm, g.ROD_Z_mm], hx = g.XH_mm, hz = g.HINGE_Z_mm;
    const T = (x, y) => x + ',' + (-y);
    const all = a.flatMap(q => [q.arm_tip_mm, q.horn_hole_mm]);
    const bx = [Math.min(hx, pv[0], ...all.map(v => v[0])), Math.max(hx, pv[0], ...all.map(v => v[0]))];
    const by = [Math.min(pv[1], ...all.map(v => v[1])), Math.max(pv[1], ...all.map(v => v[1]))], bz = [Math.min(hz, ...all.map(v => v[2])), Math.max(hz, ...all.map(v => v[2]))];
    const m = 6, tipN = p0.arm_tip_mm, holeN = p0.horn_hole_mm;
    // top view
    const pr = Math.max(0.6, g.ROD_D_mm * 0.5);
    let sv = '<line x1="' + hx + '" x2="' + hx + '" y1="' + (-(by[1] + m)) + '" y2="' + (-(by[0] - m)) + '" class="rp-hinge"/>'
      + '<polyline points="' + T(pv[0], pv[1]) + ' ' + T(tipN[0], tipN[1]) + ' ' + T(holeN[0], holeN[1]) + '" class="rp-ghost" fill="none"/>'
      + '<line x1="' + pv[0] + '" y1="' + (-pv[1]) + '" x2="' + p.arm_tip_mm[0] + '" y2="' + (-p.arm_tip_mm[1]) + '" class="rp-arm"/>'
      + '<line x1="' + p.arm_tip_mm[0] + '" y1="' + (-p.arm_tip_mm[1]) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[1]) + '" class="rp-rod"/>'
      + '<circle cx="' + pv[0] + '" cy="' + (-pv[1]) + '" r="' + (pr * 2.2) + '" class="rp-pivot"/><circle cx="' + p.arm_tip_mm[0] + '" cy="' + (-p.arm_tip_mm[1]) + '" r="' + pr * 1.4 + '" class="rp-pt"/><circle cx="' + p.horn_hole_mm[0] + '" cy="' + (-p.horn_hole_mm[1]) + '" r="' + pr * 1.4 + '" class="rp-pt"/>'
      + '<text x="' + (hx + 1) + '" y="' + (-(by[1] + m) + 5) + '" class="rp-svgt">hinge line</text><text x="' + (pv[0] + 2) + '" y="' + (-pv[1] - pr * 3) + '" class="rp-svgt">servo arm</text>';
    drawSchem('rp-k-top', [bx[0] - m, bx[1] + 22, by[0] - m, by[1] + m], sv);
    // side view: sized to its content, no panel; room on the right for the "elevon" label
    const hr = g.horn_hole_rel_hinge_mm ? Math.hypot(...g.horn_hole_rel_hinge_mm) : 7, ec = hr * 5, dr = p.delta_deg * RAD;
    const ex = hx + ec * Math.cos(dr), ez = hz - ec * Math.sin(dr);
    sv = '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + (hx + ec) + '" y2="' + (-hz) + '" class="rp-ghost"/>'
      + '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + ex + '" y2="' + (-ez) + '" class="rp-elevon"/>'
      + '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[2]) + '" class="rp-horn"/>'
      + '<line x1="' + p.arm_tip_mm[0] + '" y1="' + (-p.arm_tip_mm[2]) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[2]) + '" class="rp-rod"/>'
      + '<circle cx="' + hx + '" cy="' + (-hz) + '" r="' + hr * 0.22 + '" class="rp-pivot"/><circle cx="' + p.horn_hole_mm[0] + '" cy="' + (-p.horn_hole_mm[2]) + '" r="' + hr * 0.16 + '" class="rp-pt"/>'
      + '<text x="' + (hx + 1) + '" y="' + (-hz + hr * 0.9) + '" class="rp-svgt">hinge</text><text x="' + (ex - hr * 0.4) + '" y="' + (-ez + hr * 0.9) + '" class="rp-svgt">elevon</text>';
    const sx = [Math.min(bx[0], p.arm_tip_mm[0]) - m, Math.max(hx + ec, bx[1]) + m];
    sx[1] += (sx[1] - sx[0]) * 0.2;
    drawSchem('rp-k-side', [sx[0], sx[1], Math.min(bz[0], hz - ec) - m, Math.max(bz[1], hz + ec) + m], sv);
    for (const pl of plots) {
      if (pl.key === 'hm') pl.p.set(p.delta_deg, [p.hinge_moment_Nm], nf(p.hinge_moment_Nm, 4) + ' N m');
      else pl.p.set(p.delta_deg, [p.min_clearance_mm, p.min_clearance_excl_design_contact_mm], 'all pairs ' + nf(p.min_clearance_mm, 3) + ' mm; designed contacts left out ' + nf(p.min_clearance_excl_design_contact_mm, 3) + ' mm');
    }
  }
  window.__rp = window.__rp || {}; window.__rp.linkage = { K, apply };
  return P;
}

// ================================================================ mount
export async function mountReplays() {
  if (mounted) return; mounted = true;
  try {
    const r = await fetch('assets/sims3d/manifest.json?v=' + VER); if (!r.ok) throw new Error('manifest HTTP ' + r.status);
    manifest = await r.json();
  } catch (e) { mounted = false; throw e; }
  mountFlight(); mountLanding(); mountLinkage();
}
