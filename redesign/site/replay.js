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

const VER = '20261124a', GLB_URL = 'assets/concept-a.opt.glb?v=20261118f', GLB_B64 = 'data/assembly.opt.glb.part1.js?v=20261118f';
const REDUCE = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const nf = (v, d = 2) => (v === null || v === undefined || Number.isNaN(v)) ? '—' : Number(v).toFixed(d);
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
    pads[c] = { part: p, x0: b.min.x, len: b.max.x - b.min.x };       // gl x = CAD x (aft): the end nearest the shoe is the smaller x
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
// spec: title, unit, xs, series[{ys, cls, label}], lines[{y, label}], bands[{x0, x1}], vlines[{x}], xlabel, onSet(x), fmt, xmin, xmax
function makePlot(host, W, spec) {
  const H = 150, ML = 44, MR = 10, MT = 8, MB = 22, pw = W - ML - MR, ph = H - MT - MB;
  const wrap = document.createElement('div'); wrap.className = 'rp-plot';
  const head = document.createElement('div'); head.className = 'rp-plot-h';
  head.innerHTML = '<span>' + esc(spec.title) + '</span><b class="rp-plot-v"></b>';
  wrap.appendChild(head);
  const svg = svgEl('svg', { width: W, height: H, viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': spec.title + ' against time' }, wrap);
  const xmin = spec.xmin, xmax = spec.xmax;
  let lo = Infinity, hi = -Infinity;
  for (const s of spec.series) for (const y of s.ys) { if (y < lo) lo = y; if (y > hi) hi = y; }
  for (const l of spec.lines || []) { lo = Math.min(lo, l.y); hi = Math.max(hi, l.y); }
  if (!(hi > lo)) { hi = lo + 1; }
  const pad = (hi - lo) * 0.06; lo -= pad; hi += pad;
  const X = x => ML + (x - xmin) / (xmax - xmin || 1) * pw, Y = y => MT + (1 - (y - lo) / (hi - lo)) * ph;
  for (const b of spec.bands || []) svgEl('rect', { x: X(b.x0), y: MT, width: Math.max(1, X(b.x1) - X(b.x0)), height: ph, class: 'rp-band' }, svg);
  for (let k = 0; k <= 3; k++) {
    const y = lo + (hi - lo) * k / 3;
    svgEl('line', { x1: ML, x2: ML + pw, y1: Y(y), y2: Y(y), class: 'rp-grid' }, svg);
    const t = svgEl('text', { x: ML - 5, y: Y(y) + 4, class: 'rp-tick', 'text-anchor': 'end' }, svg); t.textContent = (spec.fmt || (v => nf(v, Math.abs(hi - lo) < 5 ? 2 : Math.abs(hi - lo) < 50 ? 1 : 0)))(y);
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
  if (spec.series.length > 1) {   // direct labels at the right end (colour is not the only cue: each trace also has its own dash)
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
  host.appendChild(wrap);
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
  tl.set = (t, keep) => { tl.t = clamp(t, 0, tl.tmax); tl.changed = true; if (!keep) { /* user moved: keep play state */ } };
  tl.range = (tmax, step) => { tl.tmax = tmax; slider.max = String(tmax); if (step) slider.step = String(step); tl.t = 0; tl.changed = true; setPlaying(false); };
  const setPlaying = on => { tl.playing = on; play.textContent = on ? 'Pause' : 'Play'; play.setAttribute('aria-label', on ? 'Pause' : 'Play'); play.setAttribute('aria-pressed', String(on)); if (on) kick(); };
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
    tl.changed = false; slider.value = String(tl.t); label.textContent = opts.fmt(tl.t); tl.onChange(tl.t); return true;
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
const PF_LABEL = { alt_peak_abs: 'Peak altitude, m', alt_max_gain: 'Highest climb during the transition, m', 't_to_1.3Vs_s': 'Time to 1.3 × stall speed, s',
  t_cap_run_s: 'Longest run at the motor cap, s', t_ge85_s: 't_ge85_s (recorded line, s)', pitch_use_15: 'Elevon pitch use, share of ±15°', t_elevon_sat_s: 'Time with the elevons saturated, s',
  touch_in_flight: 'Fin-foot contacts while flying' };
const CG_AC = [0.02205, -0.00332, 0.00656];      // CAD-frame CG, m (cad_mass.json, T-098 basis); only offsets where the model hangs from the recorded position
const TH_PROP = () => manifest.th_to_prop;       // th1..th4 -> prop corner (a_plant.py motor order 1 FR, 2 RL, 3 FL, 4 RR in the belly-forward copter frame)

function mountFlight() {
  const root = $('#rp-flight'); if (!root) return;
  const sel = $('#rp-f-case', root), msg = $('#rp-f-msg', root), over = $('#rp-f-over', root), kbEl = $('#rp-f-kb', root);
  const F = { D: null, key: null, bytes: 0 };
  let st = null, rg = null, tl = null, plots = [], read = null;
  const showMsg = (t, err) => { msg.textContent = t || ''; msg.hidden = !t; msg.classList.toggle('rp-err', !!err); };
  const kbText = () => { const m = manifest.flight.find(c => c.id === F.key) || manifest.flight.find(c => c.default); return 'Loads <b>' + (F.bytes ? nf(F.bytes / 1024, 1) : nf(m.kb, 1)) + ' KB</b> of run data and the 3-D model (' + (modelInfo.done ? nf(modelInfo.bytes / 1024, 0) : nf(manifest.glb.kb, 0)) + ' KB, once, shared with the landing replay).'; };
  modelInfo.listeners.push(() => { kbEl.innerHTML = kbText(); });

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
    tl = timeline(root, 'f', { speed: 1, fmt: t => 't = ' + nf(t, 1) + ' s', onChange: t => apply(t) });
    P.tl = tl;
    read = buildRead($('#rp-f-read', root), [['run', 'Run'], ['mass', 'Mass'], ['t', 'Time'], ['alt', 'Altitude'], ['V', 'Airspeed V'], ['pitch', 'Pitch'], ['use', 'Elevon pitch use'], ['dl', 'Left elevon dl'], ['dr', 'Right elevon dr']]);
    sel.addEventListener('change', () => load(sel.value));
    root.addEventListener('click', ev => {
      const c = ev.target.closest('button[data-t]'); if (c) { tl.set(parseFloat(c.dataset.t)); return; }
      const dir = ev.target.closest('#rp-f-prev') ? -1 : ev.target.closest('#rp-f-next') ? 1 : 0;
      if (dir && F.D) { const ts = F.events; const t = tl.t; const nxt = dir > 0 ? ts.find(x => x > t + 0.05) : [...ts].reverse().find(x => x < t - 0.05); if (nxt !== undefined) tl.set(nxt); }
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
    const { data, bytes } = await fetchJSON('assets/sims3d/' + m.file + '?v=' + VER);
    F.D = data; F.bytes = bytes; kbEl.innerHTML = kbText(); derive(data);
    tl.range(data.t[data.t.length - 1], 0.1);
    $('#rp-f-slider', root).min = '0';
    buildEvents(); buildPF(); buildPlots();
    if (st.ok) {
      const n = data.t.length, pos = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { pos[3 * i] = data.pe[i]; pos[3 * i + 1] = data.alt[i]; pos[3 * i + 2] = -data.pn[i]; }
      st.trailGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3)); st.trailGeo.setDrawRange(0, 1); st.trailGeo.computeBoundingSphere();
      st.lastTarget = null;
    }
    read.set('run', m.label); read.set('mass', nf(data.meta.mass_kg, 3) + ' kg');
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
    F.events = F.marks.map(m => m.t).concat(F.modes.map(m => m.t)).sort((a, b) => a - b);
    const w0 = mk.t_fbwa, w1 = mk.t_cruise_end; let mx = null;
    if (w0 !== undefined && w1 !== undefined) { for (let i = 0; i < n; i++) if (D.t[i] >= w0 && D.t[i] <= w1) mx = Math.max(mx === null ? -1 : mx, D.pitch_use_15[i]); }
    F.useMax10Hz = mx;
    const pl = D.meta.pass_fail.lines.pitch_use_15; F.useLimit = pl ? parseFloat(String(pl.limit).replace(/[^0-9.]/g, '')) : 0.6;
  }
  function buildEvents() {
    const D = F.D, mk = $('#rp-f-marks', root), md = $('#rp-f-modes', root), tk = $('#rp-f-ticks', root);
    mk.innerHTML = '<span class="rp-chip-h">Events</span>' + F.marks.map(m => '<button type="button" class="rp-chip" data-t="' + m.t + '" aria-label="Jump to ' + esc(MARK_LABEL[m.k] || m.k) + ' at ' + nf(m.t, 1) + ' seconds">' + esc(MARK_LABEL[m.k] || m.k) + ' <small>' + nf(m.t, 1) + ' s</small></button>').join('');
    md.innerHTML = '<span class="rp-chip-h">Autopilot modes</span>' + F.modes.map(m => '<button type="button" class="rp-chip" data-t="' + m.t + '" aria-label="Jump to mode ' + esc(m.label) + ' at ' + nf(m.t, 1) + ' seconds">' + esc(m.label) + ' <small>' + nf(m.t, 1) + ' s</small></button>').join('');
    const tmax = D.t[D.t.length - 1];
    tk.innerHTML = F.events.map(t => '<i style="left:' + (100 * t / tmax).toFixed(2) + '%"></i>').join('');
  }
  function buildPF() {
    const D = F.D, pf = D.meta.pass_fail, host = $('#rp-f-pf', root), ps = D.meta.pitch_use_scalar;
    const rows = Object.entries(pf.lines).map(([k, l]) => '<tr><td class="first">' + esc(PF_LABEL[k] || k) + '</td><td class="val">' + esc(l.value) + '</td><td>' + esc(String(l.limit).replace('<=', '≤').replace('>=', '≥')) + '</td><td class="' + (l.pass ? 'rp-ok' : 'rp-bad') + '">' + (l.pass ? '✓ pass' : '✕ FAIL') + '</td></tr>').join('');
    const fails = Object.entries(pf.lines).filter(([, l]) => !l.pass).map(([k]) => PF_LABEL[k] || k);
    host.innerHTML = '<p class="rp-sum ' + (pf.all_pass ? 'rp-ok' : 'rp-bad') + '"><b>' + (pf.all_pass ? '✓ All recorded lines pass.' : '✕ Not all lines pass: ' + esc(fails.join('; ')) + '.') + '</b> '
      + 'Elevon pitch use, the largest share of ±15° between FBWA and the end of cruise, is <b>' + nf(ps.pitch_use_15, 2) + '</b> against ' + nf(F.useLimit, 2) + ' (recorded summary; this 10 Hz file gives ' + nf(F.useMax10Hz, 2) + ').</p>'
      + '<div class="scroll"><table class="ds-table"><thead><tr><th>Line</th><th>Value</th><th>Limit</th><th>Result</th></tr></thead><tbody>' + rows + '</tbody></table></div>'
      + '<span class="ds-source">Lines from mechanism/out/T101_results.json via the export (<code class="ds-inline">meta.pass_fail</code>).</span>';
  }
  function buildPlots() {
    const D = F.D, host = $('#rp-f-plots', root), W = Math.max(280, Math.round(host.clientWidth || 600)); F.plotW = W;
    host.innerHTML = ''; plots = [];
    const mk = D.events.marks, tmax = D.t[D.t.length - 1], vl = F.marks.map(m => ({ x: m.t })), set = x => tl.set(x);
    const base = { xs: D.t, xmin: 0, xmax: tmax, vlines: vl, onSet: set };
    plots.push({ key: 'alt', p: makePlot(host, W, { ...base, title: 'Altitude, m', series: [{ ys: D.alt }] }) });
    plots.push({ key: 'V', p: makePlot(host, W, { ...base, title: 'Airspeed V, m/s', series: [{ ys: D.V }] }) });
    plots.push({ key: 'pitch', p: makePlot(host, W, { ...base, title: 'Pitch, deg (90 = nose straight up)', series: [{ ys: D.pitch }] }) });
    const bands = mk.t_fbwa !== undefined && mk.t_cruise_end !== undefined ? [{ x0: mk.t_fbwa, x1: mk.t_cruise_end }] : [];
    plots.push({ key: 'use', p: makePlot(host, W, { ...base, title: 'Elevon pitch use, share of ±15° (shaded: FBWA to end of cruise, where the line is judged)', series: [{ ys: D.pitch_use_15 }], lines: [{ y: F.useLimit, label: nf(F.useLimit, 2) + ' limit' }], bands }) });
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
    const alt = L(D.alt), V = L(D.V), use = L(D.pitch_use_15);
    read.set('t', nf(t, 1) + ' s'); read.set('alt', nf(alt, 1) + ' m'); read.set('V', nf(V, 1) + ' m/s'); read.set('pitch', nf(pitch, 1) + '°'); read.set('use', nf(use, 2) + ' of ±15° (limit ' + nf(F.useLimit, 2) + ')', use > F.useLimit ? 'rp-bad' : '');
    read.set('dl', nf(dl, 1) + '° (trailing edge down +)'); read.set('dr', nf(dr, 1) + '° (trailing edge down +)');
    for (const pl of plots) {
      if (pl.key === 'alt') pl.p.set(t, [alt], nf(alt, 1) + ' m');
      else if (pl.key === 'V') pl.p.set(t, [V], nf(V, 1) + ' m/s');
      else if (pl.key === 'pitch') pl.p.set(t, [pitch], nf(pitch, 1) + '°');
      else pl.p.set(t, [use], nf(use, 2) + (use > F.useLimit ? ' ✕ over ' : ' ✓ within ') + nf(F.useLimit, 2));
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
    TH_PROP().forEach((c, k) => {
      const pg = manifest.props[c], ang = (F.ang[k][i] + (F.ang[k][i + 1] - F.ang[k][i]) * f) * pg.dir;
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
function buildRead(host, rows) {
  host.innerHTML = '<dl>' + rows.map(([k, l]) => '<div><dt>' + esc(l) + '</dt><dd data-k="' + k + '"></dd></div>').join('') + '</dl>';
  const m = {}; host.querySelectorAll('dd').forEach(d => { m[d.dataset.k] = d; });
  return { set(k, text, cls) { const d = m[k]; if (!d) return; if (d.textContent !== text) d.textContent = text; d.className = cls || ''; }, el: m };
}

// ================================================================ LANDING
const LAND_LABEL = ['UR', 'LR', 'UL', 'LL'];
function mountLanding() {
  const root = $('#rp-landing'); if (!root) return;
  const sel = $('#rp-l-case', root), msg = $('#rp-l-msg', root), over = $('#rp-l-over', root), kbEl = $('#rp-l-kb', root);
  const Lc = { D: null, key: null, bytes: 0 };
  let st = null, rg = null, tl = null, plots = [], read = null;
  const showMsg = (t, err) => { msg.textContent = t || ''; msg.hidden = !t; msg.classList.toggle('rp-err', !!err); };
  const kbText = () => { const m = manifest.landing.find(c => c.id === Lc.key) || manifest.landing[0]; return 'Loads <b>' + (Lc.bytes ? nf(Lc.bytes / 1024, 1) : nf(m.kb, 1)) + ' KB</b> of case data and the 3-D model (' + (modelInfo.done ? nf(modelInfo.bytes / 1024, 0) : nf(manifest.glb.kb, 0)) + ' KB, once, shared with the flight replay).'; };
  modelInfo.listeners.push(() => { kbEl.innerHTML = kbText(); });
  const Cm = new THREE.Matrix4().set(1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1), CmT = Cm.clone().transpose();   // world (x, y, z-up) -> scene (x, z, -y)

  const P = addPanel(root, async () => {
    showMsg('Loading 3-D model…');
    st = makeStage($('#rp-l-canvas', root), { gridSize: 4, gridDiv: 40 });
    if (!st.ok) showMsg('3-D is not available in this browser. The plots below still work.', true);
    else {
      makeGrid(st, 4, 40);
      const gltf = await loadModel(); rg = rig(gltf.scene.clone(true)); st.scene.add(rg.root);   // second scene: clone of the shared parsed model
      st.camera.position.set(0.95, 0.6, 1.4); st.controls.target.set(0, 0.2, 0);
    }
    tl = timeline(root, 'l', { speed: 0.1, fmt: t => 't = ' + nf(t * 1000, 0) + ' ms', onChange: t => apply(t) });
    read = buildRead($('#rp-l-read', root), [['case', 'Case'], ['mass', 'Mass'], ['t', 'Time'], ['n', 'Load factor now'], ['nmax', 'Peak load factor so far'], ['s', 'Stroke now, worst pad'], ['smax', 'Stroke, max so far'], ['tilt', 'Tilt now'], ['pads', 'Crush per pad now']]);
    sel.addEventListener('change', () => load(sel.value));
    new ResizeObserver(() => { const w = Math.round($('#rp-l-plots', root).clientWidth); if (Lc.D && Math.abs(w - (Lc.plotW || 0)) > 6) buildPlots(); }).observe($('#rp-l-plots', root));
    await load(sel.value);
  });
  P.fail = err => showMsg('Could not load: ' + err.message, true);
  P.tick = dt => { const c = tl.tick(dt); if (c && st.ok) st.dirty = true; return c; };
  P.render = () => { if (st && st.ok) renderStage(st); };

  async function load(key) {
    Lc.key = key; showMsg('Loading case data…'); if (tl) tl.setPlaying(false);
    const m = manifest.landing.find(c => c.id === key);
    const { data, bytes } = await fetchJSON('assets/sims3d/' + m.file + '?v=' + VER);
    Lc.D = data; Lc.bytes = bytes; kbEl.innerHTML = kbText();
    const n = data.t.length; Lc.maxCrush = new Float64Array(n); Lc.maxN = new Float64Array(n); let mc = 0, mn = 0;
    for (let i = 0; i < n; i++) { mc = Math.max(mc, ...data.crush_mm[i]); mn = Math.max(mn, data.load_factor_g[i]); Lc.maxCrush[i] = mc; Lc.maxN[i] = mn; }
    tl.range(data.t[n - 1], 0.005);
    read.set('case', m.label + ' (T-098: ' + m.case + ')'); read.set('mass', nf(data.meta.mass_kg, 3) + ' kg');
    buildPlots(); showMsg(st.ok ? '' : '3-D is not available in this browser. The plots below still work.', !st.ok);
    tl.changed = true; apply(0);
  }
  function buildPlots() {
    const D = Lc.D, host = $('#rp-l-plots', root), W = Math.max(280, Math.round(host.clientWidth || 600)); Lc.plotW = W;
    host.innerHTML = ''; plots = []; const lim = D.meta.limits, tmax = D.t[D.t.length - 1], set = x => tl.set(x);
    const base = { xs: D.t, xmin: 0, xmax: tmax, onSet: set, xlabel: 's' };
    plots.push({ key: 'n', p: makePlot(host, W, { ...base, title: 'Load factor, g', series: [{ ys: D.load_factor_g }], lines: [{ y: lim.load_factor_g, label: lim.load_factor_g + ' g limit' }] }) });
    const cs = [0, 1, 2, 3].map(k => D.crush_mm.map(r => r[k]));
    plots.push({ key: 'c', p: makePlot(host, W, { ...base, title: 'Pad crush, mm (four pads)', series: cs.map((ys, k) => ({ ys, label: LAND_LABEL[k] })), lines: [{ y: lim.stroke_mm, label: lim.stroke_mm + ' mm limit' }] }) });
    plots.push({ key: 't', p: makePlot(host, W, { ...base, title: 'Tilt, deg', series: [{ ys: D.tilt_deg }], lines: [{ y: lim.tilt_deg, label: lim.tilt_deg + '° limit' }] }) });
    tl.changed = true;
  }
  const okTxt = (v, lim, unit) => (v <= lim ? '✓ within ' : '✕ OVER ') + lim + ' ' + unit;
  const qa = new THREE.Quaternion(), qb = new THREE.Quaternion(), Rw = new THREE.Matrix4(), Rs = new THREE.Matrix4();
  function apply(t) {
    const D = Lc.D; if (!D) return;
    const ts = D.t, n = ts.length, dt = (ts[n - 1] - ts[0]) / (n - 1);
    const i = clamp(Math.floor(t / dt), 0, n - 2), f = clamp(t / dt - i, 0, 1), lim = D.meta.limits;
    const L = (a, k) => a[i][k] + (a[i + 1][k] - a[i][k]) * f;
    const nNow = D.load_factor_g[i] + (D.load_factor_g[i + 1] - D.load_factor_g[i]) * f, tilt = D.tilt_deg[i] + (D.tilt_deg[i + 1] - D.tilt_deg[i]) * f;
    const crush = [0, 1, 2, 3].map(k => L(D.crush_mm, k)), cmax = Math.max(...crush), cm = Lc.maxCrush[i], nm = Lc.maxN[i];
    read.set('t', nf(t * 1000, 0) + ' ms'); read.set('n', nf(nNow, 2) + ' g (limit ' + lim.load_factor_g + ')');
    read.set('nmax', nf(nm, 2) + ' g  ' + okTxt(nm, lim.load_factor_g, 'g'), nm <= lim.load_factor_g ? 'rp-ok' : 'rp-bad');
    read.set('s', nf(cmax, 1) + ' mm'); read.set('smax', nf(cm, 1) + ' mm  ' + okTxt(cm, lim.stroke_mm, 'mm'), cm <= lim.stroke_mm ? 'rp-ok' : 'rp-bad');
    read.set('tilt', nf(tilt, 2) + '°  ' + okTxt(tilt, lim.tilt_deg, '°') + ' (the limit is on the end tilt: ' + nf(D.peaks.tilt_end_deg, 2) + '°)', tilt <= lim.tilt_deg ? 'rp-ok' : 'rp-bad');
    read.set('pads', LAND_LABEL.map((l, k) => l + ' ' + nf(crush[k], 1)).join(' · ') + ' mm');
    for (const pl of plots) {
      if (pl.key === 'n') pl.p.set(t, [nNow], nf(nNow, 2) + ' g ' + (nm <= lim.load_factor_g ? '✓' : '✕') + ' peak so far ' + nf(nm, 2));
      else if (pl.key === 'c') pl.p.set(t, crush, nf(cm, 1) + ' mm max so far ' + (cm <= lim.stroke_mm ? '✓' : '✕'));
      else pl.p.set(t, [tilt], nf(tilt, 2) + '° ' + (tilt <= lim.tilt_deg ? '✓' : '✕'));
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
    over.textContent = 'grid cell 0.1 m · pads (' + LAND_LABEL.join(', ') + ') drawn shortened by their crush';
    st.dirty = true;
  }
  window.__rp = window.__rp || {}; window.__rp.landing = { get st() { return st; }, get rg() { return rg; }, get tl() { return tl; }, Lc, apply, load, renderNow: () => { st.dirty = true; renderStage(st); } };
  return P;
}

// ================================================================ LINKAGE
function mountLinkage() {
  const root = $('#rp-linkage'); if (!root) return;
  const K = { D: null, side: 'R', i: 0, playing: false, tau: 0 };
  const slider = $('#rp-k-slider', root), play = $('#rp-k-play', root), timeEl = $('#rp-k-time', root), capEl = $('#rp-k-cap', root);
  let read = null, plots = [], bytes = 0;
  const kbEl = $('#rp-k-kb', root);
  const P = addPanel(root, async () => {
    const { data, bytes: b } = await fetchJSON('assets/sims3d/' + manifest.linkage.file + '?v=' + VER);
    K.D = data; bytes = b; kbEl.innerHTML = 'Loads <b>' + nf(b / 1024, 1) + ' KB</b>; no 3-D model.';
    read = buildRead($('#rp-k-read', root), [['d', 'Elevon angle (trailing edge down +)'], ['th', 'Servo arm angle'], ['gear', 'Elevon degrees per servo degree'], ['hm', 'Hinge moment'], ['tq', 'Servo hold torque needed'], ['rf', 'Pushrod force'], ['rod', 'Pushrod length'], ['c0', 'Minimum clearance, all pairs'], ['c1', 'Minimum clearance, design contacts left out']]);
    root.addEventListener('click', ev => {
      const b = ev.target.closest('button[data-side]'); if (!b) return; K.side = b.dataset.side;
      b.parentElement.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); setup();
    });
    slider.addEventListener('input', () => { K.i = nearest(parseFloat(slider.value)); K.dirty = true; });
    play.addEventListener('click', () => { K.playing = !K.playing; play.textContent = K.playing ? 'Pause' : 'Sweep'; play.setAttribute('aria-label', K.playing ? 'Pause the sweep' : 'Sweep the elevon angle'); play.setAttribute('aria-pressed', String(K.playing)); if (K.playing) { K.tau = (K.i / (K.D[K.side].length - 1)); kick(); } });
    new ResizeObserver(() => { const w = Math.round($('#rp-k-plots', root).clientWidth); if (K.D && Math.abs(w - (K.plotW || 0)) > 6) buildPlots(); }).observe($('#rp-k-plots', root));
    setup();
  });
  P.fail = err => { capEl.textContent = 'Could not load: ' + err.message; };
  const poses = () => K.D[K.side];
  const nearest = d => { const a = poses(); let bi = 0, bd = 1e9; for (let i = 0; i < a.length; i++) { const e = Math.abs(a[i].delta_deg - d); if (e < bd) { bd = e; bi = i; } } return bi; };
  function setup() {
    const a = poses(), g = K.D.meta.geometry;
    slider.min = String(a[0].delta_deg); slider.max = String(a[a.length - 1].delta_deg); slider.step = String(a[1].delta_deg - a[0].delta_deg);
    K.i = nearest(0); K.dirty = true; buildPlots();
  }
  P.tick = dt => {
    if (K.playing) {            // ping-pong sweep, 10 s per full -stop..+stop..-stop cycle (the "10 s" is a display rate, not data)
      K.tau += dt / 10; const n = poses().length, ph = (K.tau * 2) % 2, u = ph < 1 ? ph : 2 - ph; K.i = Math.round(u * (n - 1)); K.dirty = true;
    }
    if (!K.dirty) return false; K.dirty = false; apply(); return true;
  };
  function buildPlots() {
    const host = $('#rp-k-plots', root), W = Math.max(280, Math.round(host.clientWidth || 600)); K.plotW = W; host.innerHTML = ''; plots = [];
    const a = poses(), xs = a.map(p => p.delta_deg), set = x => { K.i = nearest(x); K.dirty = true; };
    const base = { xs, xmin: xs[0], xmax: xs[xs.length - 1], onSet: set, xlabel: 'deg' };
    plots.push({ key: 'hm', p: makePlot(host, W, { ...base, title: 'Hinge moment, N m, against elevon angle', series: [{ ys: a.map(p => p.hinge_moment_Nm) }] }) });
    plots.push({ key: 'cl', p: makePlot(host, W, { ...base, title: 'Minimum clearance, mm, against elevon angle', series: [{ ys: a.map(p => p.min_clearance_mm), label: 'all pairs' }, { ys: a.map(p => p.min_clearance_excl_design_contact_mm), label: 'design contacts left out' }] }) });
    K.dirty = true;
  }
  const NS = 'http://www.w3.org/2000/svg';
  function drawSchem(hostId, project, bounds, items) {
    const host = $('#' + hostId, root), [x0, x1, y0, y1] = bounds, W = 360, Hh = Math.max(120, Math.min(260, 360 * (y1 - y0) / (x1 - x0)));
    host.innerHTML = '<svg viewBox="' + x0 + ' ' + (-y1) + ' ' + (x1 - x0) + ' ' + (y1 - y0) + '" preserveAspectRatio="xMidYMid meet" width="100%" style="max-height:' + Hh + 'px" font-size="' + ((x1 - x0) / 26).toFixed(2) + '" aria-hidden="true">' + items + '</svg>';
  }
  function apply() {
    const a = poses(), p = a[K.i], g = K.D.meta.geometry, sy = K.side === 'R' ? 1 : -1, p0 = a[nearest(0)];
    slider.value = String(p.delta_deg); timeEl.textContent = 'elevon angle = ' + nf(p.delta_deg, 1) + '°';
    read.set('d', nf(p.delta_deg, 1) + '°'); read.set('th', nf(p.servo_theta_deg, 2) + '°'); read.set('gear', nf(p.gear_ddelta_dtheta, 3));
    read.set('hm', nf(p.hinge_moment_Nm, 4) + ' N m'); read.set('tq', nf(p.servo_torque_req_Nm, 4) + ' N m'); read.set('rf', nf(p.rod_force_N, 1) + ' N'); read.set('rod', nf(p.rod_len_mm, 2) + ' mm');
    read.set('c0', nf(p.min_clearance_mm, 3) + ' mm — ' + p.min_clearance_pair); read.set('c1', nf(p.min_clearance_excl_design_contact_mm, 3) + ' mm — ' + p.min_clearance_excl_pair);
    capEl.textContent = 'The all-pairs minimum includes the declared design contacts (named in its pair: ' + p.min_clearance_pair + '), which touch by design, so it can read zero or close to it. The second line leaves the declared design contacts out. Solid hulls, so both are lower bounds.';
    // geometry in CAD mm: x aft, y span (+ right), z up. Top view uses (x, y); side view (x, z); SVG y runs down, so y is negated.
    const pv = [g.SV_XS_mm, sy * g.SERVO_Y_mm, g.ROD_Z_mm], hx = g.XH_mm, hz = g.HINGE_Z_mm;
    const T = (x, y) => x + ',' + (-y);
    const all = a.flatMap(q => [q.arm_tip_mm, q.horn_hole_mm]);
    const bx = [Math.min(hx, pv[0], ...all.map(v => v[0])), Math.max(hx, pv[0], ...all.map(v => v[0]))];
    const by = [Math.min(pv[1], ...all.map(v => v[1])), Math.max(pv[1], ...all.map(v => v[1]))], bz = [Math.min(hz, ...all.map(v => v[2])), Math.max(hz, ...all.map(v => v[2]))];
    const m = 6, tipN = p0.arm_tip_mm, holeN = p0.horn_hole_mm;
    // top view
    const w = by[1] - by[0], pr = Math.max(0.6, g.ROD_D_mm * 0.5);
    let sv = '<line x1="' + hx + '" x2="' + hx + '" y1="' + (-(by[1] + m)) + '" y2="' + (-(by[0] - m)) + '" class="rp-hinge"/>'
      + '<polyline points="' + T(pv[0], pv[1]) + ' ' + T(tipN[0], tipN[1]) + ' ' + T(holeN[0], holeN[1]) + '" class="rp-ghost" fill="none"/>'
      + '<line x1="' + pv[0] + '" y1="' + (-pv[1]) + '" x2="' + p.arm_tip_mm[0] + '" y2="' + (-p.arm_tip_mm[1]) + '" class="rp-arm"/>'
      + '<line x1="' + p.arm_tip_mm[0] + '" y1="' + (-p.arm_tip_mm[1]) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[1]) + '" class="rp-rod"/>'
      + '<circle cx="' + pv[0] + '" cy="' + (-pv[1]) + '" r="' + (pr * 2.2) + '" class="rp-pivot"/><circle cx="' + p.arm_tip_mm[0] + '" cy="' + (-p.arm_tip_mm[1]) + '" r="' + pr * 1.4 + '" class="rp-pt"/><circle cx="' + p.horn_hole_mm[0] + '" cy="' + (-p.horn_hole_mm[1]) + '" r="' + pr * 1.4 + '" class="rp-pt"/>'
      + '<text x="' + (hx + 1) + '" y="' + (-(by[1] + m) + 5) + '" class="rp-svgt">hinge line</text><text x="' + (pv[0] + 2) + '" y="' + (-pv[1] - pr * 3) + '" class="rp-svgt">servo arm</text>';
    drawSchem('rp-k-top', null, [bx[0] - m, bx[1] + 22, by[0] - m, by[1] + m], sv);
    // side view
    const hr = g.horn_hole_rel_hinge_mm ? Math.hypot(...g.horn_hole_rel_hinge_mm) : 7, ec = hr * 5, dr = p.delta_deg * RAD;
    const ex = hx + ec * Math.cos(dr), ez = hz - ec * Math.sin(dr);
    sv = '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + (hx + ec) + '" y2="' + (-hz) + '" class="rp-ghost"/>'
      + '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + ex + '" y2="' + (-ez) + '" class="rp-elevon"/>'
      + '<line x1="' + hx + '" y1="' + (-hz) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[2]) + '" class="rp-horn"/>'
      + '<line x1="' + p.arm_tip_mm[0] + '" y1="' + (-p.arm_tip_mm[2]) + '" x2="' + p.horn_hole_mm[0] + '" y2="' + (-p.horn_hole_mm[2]) + '" class="rp-rod"/>'
      + '<circle cx="' + hx + '" cy="' + (-hz) + '" r="' + hr * 0.22 + '" class="rp-pivot"/><circle cx="' + p.horn_hole_mm[0] + '" cy="' + (-p.horn_hole_mm[2]) + '" r="' + hr * 0.16 + '" class="rp-pt"/>'
      + '<text x="' + (hx + 1) + '" y="' + (-hz + hr * 0.9) + '" class="rp-svgt">hinge</text><text x="' + (ex - hr * 0.4) + '" y="' + (-ez + hr * 0.9) + '" class="rp-svgt">elevon</text>';
    const sx = [Math.min(bx[0], p.arm_tip_mm[0]) - m, Math.max(hx + ec, bx[1]) + m];
    drawSchem('rp-k-side', null, [sx[0], sx[1], Math.min(bz[0], hz - ec) - m, Math.max(bz[1], hz + ec) + m], sv);
    for (const pl of plots) {
      if (pl.key === 'hm') pl.p.set(p.delta_deg, [p.hinge_moment_Nm], nf(p.hinge_moment_Nm, 4) + ' N m');
      else pl.p.set(p.delta_deg, [p.min_clearance_mm, p.min_clearance_excl_design_contact_mm], nf(p.min_clearance_mm, 3) + ' / ' + nf(p.min_clearance_excl_design_contact_mm, 3) + ' mm');
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
