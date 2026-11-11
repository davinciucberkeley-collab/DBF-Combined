// 3-D aircraft explorer: three.js (ES modules from jsDelivr via the import map in app.html) + the viewer rules in model.js.
// Adapted from redesign/viewer/app.js: modes (Aircraft / Inside & wiring / Structure / Exploded), part browser, part panel,
// focus, plus a cruise / hover attitude toggle and a ground-kit toggle. Data: data/viewer-data.json; geometry: assets/k09l.glb.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import M from './model.js';

const GH = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/redesign/';
const $ = s => document.querySelector(s);
const esc = s => String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const reduceMotion = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------------- state ----------------
const S = { data: null, idx: null, mode: 'whole', colour: 'realistic', explode: 0, sel: null, isolated: null, poses: {}, query: '',
  attitude: 'cruise', kit: false, fast: false, ready: false };
const G = { renderer: null, scene: null, camera: null, controls: null, root: null, parts: new Map(), wires: new Map(), joints: new Map(),
  box: new THREE.Box3(), size: 1, ground: null, key: null, dirty: true, anims: [], colours: {}, hover: null,
  hwMat: null, hwMarkers: [] };

// ---------------- colours from the design-system tokens ----------------
const isDark = () => { const t = document.documentElement.getAttribute('data-theme');
  return t ? t === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches); };
function readColours() {
  const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim() || '#888';
  const c = G.colours;
  c.sub = {}; for (const k of M.PREFIXES) c.sub[k] = new THREE.Color(v('--sub-' + k.toLowerCase()));
  c.sub.OTHER = new THREE.Color(v('--fg-3'));
  c.status = {}; for (const s of M.STATUSES.concat(['UNVERIFIED', 'FAIL'])) c.status[s] = new THREE.Color(v('--st-' + s.toLowerCase()));
  c.accent = new THREE.Color(v('--accent')); c.fg = new THREE.Color(v('--fg')); c.fg3 = new THREE.Color(v('--fg-3'));
  c.bg = new THREE.Color(v('--stage-bottom')); c.ghost = new THREE.Color(isDark() ? '#7D8CA0' : '#9AA9BC');
  c.outline = new THREE.Color(isDark() ? '#05070A' : '#1A1E24'); c.outlineOpacity = isDark() ? 0.55 : 0.32;
  c.hl = new THREE.Color(v('--highlight'));
  c.css = { sub: k => v('--sub-' + k.toLowerCase()), status: s => v('--st-' + s.toLowerCase()) };
}

// ---------------- loading ----------------
function progress(frac, text) {
  const bar = $('#load-bar'); if (!bar) return;
  bar.parentElement.classList.toggle('indeterminate', frac === null);
  if (frac !== null) bar.style.width = Math.round(frac * 100) + '%';
  if (text) $('#load-text').textContent = text;
}
const kB = n => M.fmtNum(n / 1024) + ' kB';
function loadFailed(title, html) {
  $('#load-title').textContent = title; $('#load-bar').parentElement.hidden = true;
  $('#load-text').innerHTML = html; $('#loading').classList.remove('done');
}

// ---------------- three.js setup ----------------
function initThree() {
  const canvas = $('#canvas');
  try { G.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' }); }
  catch (e) { return false; }
  const r = G.renderer;
  r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  r.outputColorSpace = THREE.SRGBColorSpace;
  r.toneMapping = THREE.AgXToneMapping; r.toneMappingExposure = 1.25;
  r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
  G.scene = new THREE.Scene();
  // image-based lighting: a soft studio room (RoomEnvironment) prefiltered once by PMREM
  const pmrem = new THREE.PMREMGenerator(r);
  G.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture; pmrem.dispose();
  G.scene.environmentIntensity = 0.9;
  G.scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa4b0, 0.25));
  // one soft key light from above front-left, the only shadow caster (contact shadow on the ground)
  G.key = new THREE.DirectionalLight(0xfff8f0, 1.5); G.key.castShadow = true;
  G.key.shadow.mapSize.set(2048, 2048); G.key.shadow.bias = -0.0002; G.key.shadow.normalBias = 0.0015;
  G.scene.add(G.key, G.key.target);
  G.camera = new THREE.PerspectiveCamera(30, 1, 0.005, 100);
  G.controls = new OrbitControls(G.camera, canvas);
  Object.assign(G.controls, { enableDamping: true, dampingFactor: 0.12, screenSpacePanning: true, zoomToCursor: true });
  G.controls.addEventListener('change', requestRender);
  new ResizeObserver(resize).observe($('#stage'));
  resize();
  requestAnimationFrame(loop);
  return true;
}
function resize() {
  const st = $('#stage'), w = st.clientWidth, h = st.clientHeight;
  if (!w || !h) return;   // the Aircraft page is hidden: keep the last size
  G.renderer.setSize(w, h, false);
  G.camera.aspect = w / h; G.camera.updateProjectionMatrix();
  requestRender();
}
function requestRender() { G.dirty = true; }
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;   // cubic in-out
function animate(dur, fn) {
  return new Promise(res => { if (reduceMotion || dur <= 0) { fn(1); requestRender(); res(); return; }
    G.anims.push({ t0: performance.now(), dur, fn, res }); });
}
function loop(now) {
  requestAnimationFrame(loop);
  if (G.anims.length) {
    G.anims = G.anims.filter(a => { const k = Math.min((now - a.t0) / a.dur, 1); a.fn(ease(k)); if (k >= 1) { a.res(); return false; } return true; });
    G.dirty = true;
  }
  if (G.controls.update()) G.dirty = true;
  if (!G.dirty) return;
  G.dirty = false;
  sizeMarkers(); placeHwMarkers();
  G.renderer.render(G.scene, G.camera);
}
const _w = new THREE.Vector3();
function sizeMarkers() {   // joint markers keep about the same size on screen at any zoom
  const cam = G.camera, r0 = G.size * 0.007;
  for (const j of G.joints.values()) if (j.marker && j.marker.visible) {
    j.marker.getWorldPosition(_w);
    const view = 2 * cam.position.distanceTo(_w) * Math.tan(THREE.MathUtils.degToRad(cam.fov / 2));
    j.marker.scale.setScalar(Math.min(view * 0.006 / r0, 1.5));
  }
}

// ---------------- fasteners view (H): hardware in the highlight colour, the rest ghosted, a screen-space ring on each ----------------
const isHw = id => M.isHardware(S.idx.parts.get(id));
function hwMaterial() {
  const hl = G.colours.hl;
  if (!G.hwMat) G.hwMat = new THREE.MeshStandardMaterial({ roughness: 0.4, metalness: 0, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
  G.hwMat.color.copy(hl); G.hwMat.emissive.copy(hl); G.hwMat.emissiveIntensity = 0.7;
  return G.hwMat;
}
function hwTexture() {   // ring + dot in the highlight colour with a light halo, so it reads on foam and on carbon
  const cv = document.createElement('canvas'); cv.width = cv.height = 64;
  const x = cv.getContext('2d'), hl = '#' + G.colours.hl.getHexString();
  x.lineWidth = 9; x.strokeStyle = 'rgba(255,255,255,0.9)'; x.beginPath(); x.arc(32, 32, 24, 0, 7); x.stroke();
  x.lineWidth = 5; x.strokeStyle = hl; x.beginPath(); x.arc(32, 32, 24, 0, 7); x.stroke();
  x.fillStyle = hl; x.beginPath(); x.arc(32, 32, 8, 0, 7); x.fill();
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; return t;
}
function buildHwMarkers() {
  if (G.hwMarkers.length || !G.root) return;
  G.root.updateMatrixWorld(true);
  const mat = new THREE.SpriteMaterial({ map: hwTexture(), depthTest: false, depthWrite: false, transparent: true, sizeAttenuation: false, toneMapped: false });
  for (const [id, e] of G.parts) {
    if (!isHw(id)) continue;
    const c = new THREE.Box3().setFromObject(e.node).getCenter(new THREE.Vector3());
    const sp = new THREE.Sprite(mat); sp.renderOrder = 25; sp.visible = false;
    sp.userData = { ref: { type: 'part', id }, local: e.node.worldToLocal(c), part: e };
    G.scene.add(sp); G.hwMarkers.push(sp);
  }
}
function placeHwMarkers() {
  if (!G.hwMarkers.length) return;
  const selId = S.sel ? S.sel.id : null;
  for (const sp of G.hwMarkers) {
    const e = sp.userData.part; sp.visible = S.fast && shown(e.node);
    if (!sp.visible) continue;
    sp.position.copy(sp.userData.local); e.node.localToWorld(sp.position);
    sp.scale.setScalar(sp.userData.ref.id === selId ? 0.034 : 0.022);
  }
}
function setFast(on) {
  if (!G.root) return;
  S.fast = on; $('#fast').setAttribute('aria-pressed', String(on));
  if (on) { buildHwMarkers(); hwMaterial(); }
  applyLook(); renderTree(true); if (!S.sel) renderPanel(); hint();
}

// ---------------- model ----------------
function buildModel(gltf) {
  G.root = gltf.scene; G.scene.add(G.root); G.root.updateMatrixWorld(true);
  { const s = new THREE.Box3().setFromObject(G.root).getSize(new THREE.Vector3()); G.sizeHint = Math.max(s.x, s.y, s.z) || 1; }
  const idx = S.idx;
  G.root.traverse(o => {
    const u = o.userData || {};
    if (u.part_id) {
      const meshes = []; o.traverse(m => { if (m.isMesh) meshes.push(m); });
      const ex = Array.isArray(u.explode_m) ? new THREE.Vector3(...M.ac2gl(u.explode_m)) : new THREE.Vector3();
      G.parts.set(u.part_id, { id: u.part_id, node: o, meshes, explode: ex, base: o.matrix.clone() });
      meshes.forEach(m => prepMesh(m, { type: 'part', id: u.part_id }));
    } else if (u.edge && u.kind === 'wire') {
      const meshes = []; o.traverse(m => { if (m.isMesh) meshes.push(m); });
      G.wires.set(u.edge, { id: u.edge, node: o, meshes });
      meshes.forEach(m => prepMesh(m, { type: 'edge', id: u.edge }));
    } else if (u.edge) {
      G.joints.set(u.edge, { id: u.edge, node: o, data: u, pos: o.getWorldPosition(new THREE.Vector3()) });  // root is at identity here
    }
  });
  for (const id of G.parts.keys()) if (!idx.parts.has(id)) {   // geometry without a data row still gets a record
    const u = G.parts.get(id).node.userData; idx.parts.set(id, { id, name: u.name, subsystem: u.subsystem, status: u.status, mass_g: u.mass_g });
    idx.edgesByPart.set(id, []); idx.claimsByPart.set(id, []);
  }
  G.ground = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShadowMaterial({ opacity: isDark() ? 0.35 : 0.16 }));
  G.ground.rotation.x = -Math.PI / 2; G.ground.receiveShadow = true; G.ground.userData.noPick = true; G.scene.add(G.ground);
  // joint markers live under the root so they follow the attitude; positions are in the root frame
  const geo = new THREE.SphereGeometry(G.size * 0.007, 16, 12);
  for (const j of G.joints.values()) {
    const e = idx.edges.get(j.id), kind = e ? M.edgeKind(e, idx) : (j.data.kind === 'revolute' ? 'hinge' : 'fastened');
    if (kind === 'wire') continue;
    j.marker = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false, transparent: true }));
    j.marker.position.copy(j.pos); j.marker.renderOrder = 20; j.kind = kind;
    j.marker.userData.ref = { type: 'edge', id: j.id };
    G.root.add(j.marker);
  }
  for (const j of G.joints.values()) if (j.data.kind === 'revolute' && j.data.part_a && G.parts.has(j.data.part_a)) {
    const ax = M.AXIS_AC[String(j.data.axis || 'Y').toUpperCase()] || [0, 1, 0];
    G.parts.get(j.data.part_a).hinge = { edge: j.id, pivot: j.pos.clone(), axis: new THREE.Vector3(...M.ac2gl(ax)).normalize(),
      limits: Array.isArray(j.data.limits) ? j.data.limits : [-30, 30] };
  }
  for (const [id, e] of G.parts) { const p = idx.parts.get(id) || { id }; e.meshes.forEach(m => realMaterial(m, lookOf(p))); }
  for (const [id, w] of G.wires) w.meshes.forEach(m => realMaterial(m, wireLook(id)));
  // crisp feature lines (Freestyle-like): 28 deg crease threshold, skipped on tiny parts
  const _s = new THREE.Sphere();
  for (const e of G.parts.values()) for (const m of e.meshes) {
    if (!m.geometry.boundingSphere) m.geometry.computeBoundingSphere();
    _s.copy(m.geometry.boundingSphere).applyMatrix4(m.matrixWorld);
    if (_s.radius > G.sizeHint * 0.012) edgesOf(m, 'line');
  }
  frameModel();
}
// bounding box, ground plane, key light and camera limits for the current attitude
function frameModel() {
  G.root.updateMatrixWorld(true);
  const b = new THREE.Box3();
  for (const e of G.parts.values()) { const p = S.idx.parts.get(e.id); if (!p || p.flight !== false) b.expandByObject(e.node); }
  G.box.copy(b.isEmpty() ? new THREE.Box3().setFromObject(G.root) : b);
  const size = G.box.getSize(new THREE.Vector3()), c = G.box.getCenter(new THREE.Vector3());
  if (!G.sized) { G.size = Math.max(size.x, size.y, size.z) || 1; G.sized = true; }
  G.camera.near = G.size / 500; G.camera.far = G.size * 50; G.camera.updateProjectionMatrix();
  G.ground.scale.set(G.size * 8, G.size * 8, 1); G.ground.position.set(c.x, G.box.min.y - G.size * 0.01, c.z);
  G.key.position.set(c.x - G.size * 0.5, c.y + G.size * 2.2, c.z + G.size * 0.7); G.key.target.position.copy(c);
  const sc = G.key.shadow.camera; Object.assign(sc, { left: -G.size * 0.9, right: G.size * 0.9, top: G.size * 0.9, bottom: -G.size * 0.9, near: G.size * 0.5, far: G.size * 5 });
  sc.updateProjectionMatrix();
}
function prepMesh(m, ref) {
  const orig = Array.isArray(m.material) ? m.material[0] : m.material;
  m.material = m.userData.flatMat = orig.clone(); m.userData.origColor = orig.color ? orig.color.clone() : new THREE.Color(0x999999);
  Object.assign(m.material, { polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });   // outlines sit on top
  m.userData.ref = ref; m.castShadow = true; m.receiveShadow = true;
}

// ---------------- realistic materials (the Blender look: foam, carbon, printed parts, electronics) ----------------
// [colour, roughness, metalness, clearcoat]
const LOOK = {
  foam:    ['#E4E8ED', 0.62, 0, 0],      // XPS, foam board: off-white satin
  skin:    ['#E2E6EC', 0.38, 0, 0.45],   // XPS under packing tape: same, with a tape sheen
  carbon:  ['#1D1F23', 0.34, 0.15, 0.6], // CF tubes, rods, strips
  printed: ['#B3B8C0', 0.55, 0, 0],      // PETG
  asa:     ['#3D4148', 0.55, 0, 0],      // ASA mounts and pads
  tpu:     ['#34373C', 0.75, 0, 0],
  rubber:  ['#26282B', 0.88, 0, 0],      // neoprene, webbing, hook-and-loop
  motor:   ['#2E3136', 0.32, 0.75, 0.3], // anodised can and bell
  prop:    ['#2F3236', 0.62, 0, 0],      // glass-filled nylon
  alu:     ['#C8CCD2', 0.3, 1, 0],
  steel:   ['#A7ACB3', 0.34, 1, 0],
  brass:   ['#C7A35E', 0.32, 1, 0],
  pcb:     ['#2F6B4A', 0.45, 0.05, 0.35],// ESC, FC, power boards
  dark:    ['#2A2D31', 0.5, 0.05, 0],    // servos, receivers, capacitors, other bought electronics
  battery: ['#2B3340', 0.45, 0, 0.5],    // LiPo wrap
  wire:    ['#B8261E', 0.42, 0, 0.2],    // power wiring and harness bundles
  signal:  ['#33363B', 0.5, 0, 0.1],
  epoxy:   ['#D8D3C7', 0.8, 0, 0],
  label:   ['#F2F3F5', 0.4, 0, 0.2],
  nylon:   ['#E6E5E0', 0.6, 0, 0],
  coro:    ['#E6E9ED', 0.66, 0, 0],
};
// look key from the part's material / name / id (viewer-data.json); null = keep the GLB colour
function lookOf(p) {
  const mat = String(p.material || '').toLowerCase(), name = String(p.name || '').toLowerCase(), id = String(p.id || '');
  const has = re => re.test(mat);
  if (/^PRP-001/.test(id) || has(/^motor/)) return 'motor';
  if (/^PRP-003/.test(id) || /\bprop\b/.test(name) && has(/nylon/)) return 'prop';
  if (/^HRN-/.test(id) || has(/copper \+ silicone|wire/)) return 'wire';
  if (has(/lipo/)) return 'battery';
  if (has(/fr4/)) return 'pcb';
  if (has(/electronics/)) return /\besc\b|flight controller|power module|power board|ubec|bus/.test(name) ? 'pcb' : 'dark';
  if (has(/servo/)) return 'dark';
  if (has(/brass/)) return 'brass';
  if (has(/alumin/) && !has(/petg/)) return 'alu';
  if (has(/steel/)) return 'steel';
  if (has(/\bcf\b|carbon/)) return 'carbon';
  if (has(/packing-tape skin|tape skin/)) return 'skin';
  if (has(/packing tape/)) return /skin/.test(name) ? 'skin' : 'label';
  if (has(/^asa/)) return 'asa';
  if (has(/tpu/)) return 'tpu';
  if (has(/neoprene|webbing|hook-and-loop|pouch|strap handle/)) return 'rubber';
  if (has(/coroplast/)) return 'coro';
  if (has(/epoxy/)) return 'epoxy';
  if (has(/vinyl/)) return 'label';
  if (has(/^nylon/)) return 'nylon';
  if (has(/foam board/)) return 'foam';
  if (has(/petg|pla|printed/)) return 'printed';
  if (has(/xps|foam/)) return 'foam';
  if (has(/silicone/)) return 'signal';
  return null;
}
function realMaterial(mesh, key) {
  const L = key && LOOK[key], src = mesh.userData.flatMat;
  const col = L ? new THREE.Color(L[0]) : mesh.userData.origColor.clone();
  const m = new THREE.MeshPhysicalMaterial({ color: col, roughness: L ? L[1] : 0.55, metalness: L ? L[2] : 0, clearcoat: L ? L[3] : 0,
    clearcoatRoughness: 0.3, side: src.side, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
  m.name = 'real ' + (key || src.name);
  mesh.userData.realMat = m; mesh.userData.realColor = col.clone();
}
// wires: power gauges red, thin signal leads dark (polarity is not modelled: one mesh per +/- pair)
function wireLook(id) {
  const e = S.idx.edges.get(id), g = e && e.wire ? +e.wire.gauge_awg : NaN;
  return !e || isNaN(g) || g <= 18 ? 'wire' : 'signal';
}
const _m = new THREE.Matrix4(), _r = new THREE.Matrix4(), _t = new THREE.Matrix4();
function placePart(e) {
  _m.makeTranslation(e.explode.x * S.explode, e.explode.y * S.explode, e.explode.z * S.explode);
  const deg = e.hinge ? S.poses[e.hinge.edge] || 0 : 0;
  if (deg) {
    const p = e.hinge.pivot;
    _m.multiply(_t.makeTranslation(p.x, p.y, p.z)).multiply(_r.makeRotationAxis(e.hinge.axis, deg * Math.PI / 180)).multiply(_t.makeTranslation(-p.x, -p.y, -p.z));
  }
  _m.multiply(e.base);
  e.node.matrix.copy(_m); e.node.matrix.decompose(e.node.position, e.node.quaternion, e.node.scale);
}
function placeAll() { for (const e of G.parts.values()) placePart(e); requestRender(); }

// ---------------- look: mode x colour x selection ----------------
function partColour(p, mesh) {
  if (S.colour === 'realistic') return mesh.userData.realColor;
  if (S.colour === 'status') return G.colours.status[p.status] || G.colours.status.PROPOSED;
  return G.colours.sub[M.subKey(p.id)];
}
function edgesOf(mesh, kind) {
  const key = kind + 'Lines';
  if (!mesh.userData[key]) {
    const geo = mesh.userData.edgeGeo || (mesh.userData.edgeGeo = new THREE.EdgesGeometry(mesh.geometry, 28));
    const mat = new THREE.LineBasicMaterial({ transparent: true, depthTest: kind !== 'sel', depthWrite: false,
      opacity: kind === 'sel' ? 0.95 : kind === 'line' ? G.colours.outlineOpacity : 0.28 });
    const l = new THREE.LineSegments(geo, mat); l.renderOrder = kind === 'sel' ? 30 : kind === 'line' ? 2 : 5; l.userData.noPick = true;
    mesh.add(l); mesh.userData[key] = l;
  }
  return mesh.userData[key];
}
function roleOf(id) {
  const p = S.idx.parts.get(id), selected = S.sel && S.sel.type === 'part' && S.sel.id === id;
  if (p && p.flight === false && !S.kit && !selected) return 'hidden';
  if (S.isolated) return id === S.isolated ? 'solid' : 'hidden';
  if (S.fast) return M.isHardware(p) || selected ? 'solid' : 'ghost';
  if (p && p.flight === false && !selected && S.mode === 'whole') return 'ghost';   // transport box x-rayed around the aircraft
  const r = M.role(S.mode, p, S.idx);
  return selected && r !== 'solid' ? 'solid' : r;
}
function applyLook() {
  if (!G.root) return;
  const c = G.colours, selId = S.sel ? S.sel.id : null, anySel = !!S.sel, real = S.colour === 'realistic';
  for (const [id, e] of G.parts) {
    const p = S.idx.parts.get(id), r = roleOf(id), isSel = selId === id;
    e.node.visible = r !== 'hidden';
    const hw = S.fast && r === 'solid' && M.isHardware(p);
    for (const m of e.meshes) {
      const ghost = r === 'ghost';
      m.userData.ghost = ghost; m.renderOrder = hw ? 10 : 0;
      if (hw) { m.material = hwMaterial(); m.castShadow = true; if (m.userData.lineLines) m.userData.lineLines.visible = false;
        if (m.userData.ghostLines) m.userData.ghostLines.visible = false;
        if (isSel || m.userData.selLines) { const l = edgesOf(m, 'sel'); l.visible = isSel; l.material.color.copy(c.accent); }
        continue; }
      const mat = m.material = real ? m.userData.realMat : m.userData.flatMat;
      if (ghost) { mat.color.copy(c.ghost); mat.opacity = S.fast ? 0.15 : 0.18; }
      else { mat.color.copy(partColour(p, m)); mat.opacity = 1; if (anySel && !isSel) mat.color.lerp(c.bg, 0.5); }
      if (mat.transparent !== ghost) { mat.transparent = ghost; mat.needsUpdate = true; }
      mat.depthWrite = !ghost; m.castShadow = !ghost;
      tint(m, id);
      if (m.userData.lineLines) { const l = m.userData.lineLines; l.visible = !ghost && !isSel; l.material.color.copy(c.outline);
        l.material.opacity = c.outlineOpacity * (anySel && !isSel ? 0.5 : 1); }
      if (ghost || m.userData.ghostLines) { const l = edgesOf(m, 'ghost'); l.visible = ghost; l.material.color.copy(c.fg3); }
      if (isSel || m.userData.selLines) { const l = edgesOf(m, 'sel'); l.visible = isSel; l.material.color.copy(c.accent); }
    }
  }
  const wiresOn = M.showWires(S.mode) && S.explode < 0.01 && !S.fast;
  for (const [id, w] of G.wires) {
    const isSel = selId === id;
    w.node.visible = isSel || (wiresOn && !S.isolated);
    for (const m of w.meshes) { m.material = real ? m.userData.realMat : m.userData.flatMat;
      m.material.color.copy(real ? m.userData.realColor : m.userData.origColor); if (anySel && !isSel) m.material.color.lerp(c.bg, 0.5);
      if (m.material.emissive) m.material.emissive.copy(c.accent).multiplyScalar(isSel ? 0.35 : 0); }
  }
  const jointsOn = M.showJoints(S.mode) && S.explode < 0.01 && !S.isolated && !S.fast;
  for (const [id, j] of G.joints) if (j.marker) {
    const ends = [j.data.part_a, j.data.part_b].filter(pid => G.parts.has(pid));   // no marker on a hidden part (ground kit, Structure)
    j.marker.visible = (jointsOn && ends.every(pid => G.parts.get(pid).node.visible)) || selId === id;
    j.marker.material.color.copy(selId === id ? c.accent : j.kind === 'hinge' ? c.fg : c.fg3);
  }
  G.ground.material.opacity = isDark() ? 0.35 : 0.16;
  renderLegend(); requestRender();
}

// selection / hover glow on one mesh
const _black = new THREE.Color(0);
function tint(m, id) {
  const mat = m.material; if (!mat.emissive || mat === G.hwMat) return;
  const sel = S.sel && S.sel.id === id, hov = G.hover === id && !sel;
  mat.emissive.copy(sel || hov ? G.colours.accent : _black).multiplyScalar(sel ? 0.16 : hov ? 0.09 : 0);
}
function setHover(id) {
  if (id === G.hover) return;
  const prev = G.hover; G.hover = id;
  for (const k of [prev, id]) if (k) { const e = G.parts.get(k) || G.wires.get(k); if (e) e.meshes.forEach(m => tint(m, k)); }
  G.renderer.domElement.style.cursor = id ? 'pointer' : '';
  requestRender();
}

// ---------------- camera ----------------
const ISO = new THREE.Vector3(-0.95, 0.85, 1.25).normalize();   // front-left, above (as hero-iso.png)
function visibleBox() {
  G.root.updateMatrixWorld(true);
  const b = new THREE.Box3();
  for (const e of G.parts.values()) if (e.node.visible) b.expandByObject(e.node);
  return b.isEmpty() ? G.box.clone() : b;
}
function fit(box, dir, dur) {
  const sph = box.getBoundingSphere(new THREE.Sphere()), r = Math.max(sph.radius, G.size * 0.12);   // a small part keeps its neighbours in view
  const cam = G.camera, ctl = G.controls;
  dir = (dir || cam.position.clone().sub(ctl.target)).clone().normalize();
  const fromT = ctl.target.clone(), fromP = cam.position.clone(), toT = sph.center.clone();
  const toP = toT.clone().add(dir.multiplyScalar(r / Math.sin(THREE.MathUtils.degToRad(cam.fov / 2)) * (cam.aspect < 1 ? 1.0 / Math.max(cam.aspect, 0.5) * 0.98 : 0.98)));
  return animate(dur === undefined ? 750 : dur, k => {
    ctl.target.lerpVectors(fromT, toT, k); cam.position.lerpVectors(fromP, toP, k);
    cam.updateProjectionMatrix(); cam.lookAt(ctl.target);
  });
}
function focusOn(ref) {
  G.root.updateMatrixWorld(true);
  const b = new THREE.Box3();
  if (ref.type === 'part' && G.parts.has(ref.id)) b.expandByObject(G.parts.get(ref.id).node);
  else if (ref.type === 'edge') {
    if (G.wires.has(ref.id)) b.expandByObject(G.wires.get(ref.id).node);
    const e = S.idx.edges.get(ref.id);
    if (e) for (const id of [e.part_a, e.part_b]) if (G.parts.has(id) && G.parts.get(id).node.visible) b.expandByObject(G.parts.get(id).node);
    if (b.isEmpty() && G.joints.has(ref.id)) b.expandByPoint(G.joints.get(ref.id).marker.getWorldPosition(new THREE.Vector3()));
  }
  if (!b.isEmpty()) fit(b);
}
function showAll() {
  S.isolated = null; select(null);
  fit(visibleBox(), ISO.clone());
}

// ---------------- attitude ----------------
function setAttitude(a, dur) {
  if (!G.root || !['cruise', 'hover'].includes(a)) return;
  S.attitude = a; pressed('#attitude', 'att', a);
  const from = G.root.rotation.z, to = a === 'hover' ? -Math.PI / 2 : 0;   // nose (-x) -> up (+y)
  return animate(dur === undefined ? 700 : dur, k => { G.root.rotation.z = from + (to - from) * k; frameModel(); })
    .then(() => fit(visibleBox(), null, 400));
}

// ---------------- picking ----------------
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
const shown = o => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
function pick(ev) {
  const rc = G.renderer.domElement.getBoundingClientRect();
  ndc.set(((ev.clientX - rc.left) / rc.width) * 2 - 1, -((ev.clientY - rc.top) / rc.height) * 2 + 1);
  ray.setFromCamera(ndc, G.camera);
  const objs = [];
  for (const e of G.parts.values()) objs.push(...e.meshes);
  for (const w of G.wires.values()) objs.push(...w.meshes);
  for (const j of G.joints.values()) if (j.marker) objs.push(j.marker);
  for (const sp of G.hwMarkers) if (sp.visible) objs.push(sp);
  ray.camera = G.camera;
  const hits = ray.intersectObjects(objs.filter(shown), false);
  const h = hits.find(x => x.object.renderOrder >= 20) || hits.find(x => !x.object.userData.ghost) || hits[0];
  return h ? { ref: h.object.userData.ref, point: h.point } : null;
}

// ---------------- modes ----------------
function pressed(sel, attr, val) { document.querySelectorAll(sel + ' button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset[attr] === val))); }
function setExplode(f) { S.explode = f; $('#explode-range').value = Math.round(f * 100); $('#explode-val').textContent = Math.round(f * 100) + ' %'; placeAll(); }
function explodeTo(target, dur) { const from = S.explode; let first = true;
  return animate(dur, k => { setExplode(from + (target - from) * k); if (first || k === 1) applyLook(); first = false; }); }
async function setMode(mode) {
  if (!M.MODES.includes(mode) || mode === S.mode) return;
  const was = S.mode; S.mode = mode; pressed('#modes', 'mode', mode);
  $('#explode').hidden = mode !== 'exploded';
  if (was === 'exploded') await explodeTo(0, 250);
  applyLook();
  if (mode === 'exploded') { await explodeTo(1, 900); fit(visibleBox(), null, 500); }
  renderTree(true); hint();
}
function setColour(c) { S.colour = c; pressed('#colours', 'colour', c); applyLook(); }
function setKit(on) { S.kit = on; $('#kit').setAttribute('aria-pressed', String(on)); applyLook(); renderTree(true); if (on) fit(visibleBox()); }

// ---------------- selection ----------------
function select(ref, opts) {
  opts = opts || {};
  if (ref && ref.type === 'part' && !S.idx.parts.has(ref.id)) ref = null;
  if (ref && ref.type === 'edge' && !S.idx.edges.has(ref.id) && !G.joints.has(ref.id) && !G.wires.has(ref.id)) ref = null;
  S.sel = ref;
  if (S.isolated && (!ref || ref.id !== S.isolated)) S.isolated = null;
  applyLook(); renderPanel(); renderTree(true);
  if (ref && opts.focus) focusOn(ref);
}

// ---------------- part browser ----------------
const subCss = k => k === 'OTHER' ? 'var(--fg-3)' : 'var(--sub-' + k.toLowerCase() + ')';
function renderTree(keepScroll) {
  const T = $('#tree'), top = T.scrollTop, selId = S.sel ? S.sel.id : null;
  const groups = S.fast ? M.tree({ parts: S.data.parts.filter(M.isHardware) }, S.query) : M.tree(S.data, S.query);
  const openState = {}; T.querySelectorAll('details[data-sub]').forEach(d => { openState[d.dataset.sub] = d.open; });
  let h = '';
  for (const g of groups) {
    const ground = g.parts.every(p => p.flight === false);
    const open = openState[g.subsystem] !== undefined ? openState[g.subsystem] : !!S.query || !ground || S.fast;
    h += '<details data-sub="' + esc(g.subsystem) + '"' + (open ? ' open' : '') + '><summary data-sub="' + g.key + '"><i class="sub" style="--sub:' + subCss(g.key) + '"></i>' +
      '<span>' + esc(g.subsystem) + (ground ? ' <small>ground</small>' : '') + '</span><span class="m">' + (S.fast ? g.parts.length + ' · ' + M.fmtMass(g.mass_g) : ground ? g.parts.length + ' parts' : M.fmtMass(g.mass_g)) + '</span></summary>';
    for (const p of g.parts) {
      const hidden = G.root && G.parts.has(p.id) && roleOf(p.id) === 'hidden';
      h += '<button class="v-row' + (p.in_model === false ? ' nogeo' : '') + (hidden ? ' dim' : '') + '" data-part="' + esc(p.id) + '"' +
        (selId === p.id ? ' aria-current="true"' : '') + ' title="' + esc(p.id + ' ' + (p.name || '') + ' · ' + (p.status || '') + ' · ' + M.fmtMass(p.mass_g)) + '">' +
        '<i class="sub" style="--sub:' + subCss(M.subKey(p.id)) + '"></i><span class="id">' + esc(p.id) + '</span><span class="nm">' + esc(p.name || '') + '</span>' +
        '<i class="st" data-status="' + esc(p.status) + '" title="' + esc(p.status) + '"></i></button>';
    }
    h += '</details>';
  }
  if (S.fast) h = '<div class="v-hwhead"><i></i><span>Fasteners and hardware</span><span class="m">' + groups.reduce((n, g) => n + g.parts.length, 0) + ' parts</span></div>' + h;
  const wires = S.fast ? [] : (S.data.edges || []).filter(e => M.edgeKind(e, S.idx) === 'wire' && M.matches({ id: e.id, name: (e.wire || {}).connector, material: e.via }, S.query));
  if (wires.length) {
    const open = openState['(wiring)'] === true;
    h += '<details data-sub="(wiring)"' + (open ? ' open' : '') + '><summary><i class="sub" style="--sub:' + subCss('HRN') + '"></i><span>wiring</span><span class="m">' + wires.length + '</span></summary>';
    for (const e of wires) h += '<button class="v-row" data-edge="' + esc(e.id) + '"' + (selId === e.id ? ' aria-current="true"' : '') + '><i></i><span class="id">' + esc(e.id) +
      '</span><span class="nm">' + esc(e.part_a + ' → ' + e.part_b) + '</span><i></i></button>';
    h += '</details>';
  }
  T.innerHTML = h || '<div class="v-empty">' + (S.query ? 'No part matches “' + esc(S.query) + '”.' : 'No parts.') + '</div>';
  if (keepScroll) T.scrollTop = top;
  const cur = T.querySelector('[aria-current="true"]');
  if (cur && !keepScroll) cur.scrollIntoView({ block: 'nearest' });
}

// ---------------- part panel ----------------
const badge = s => s ? '<span class="ds-badge" data-status="' + esc(s) + '">' + esc(s) + '</span>' : '';
const partLink = id => { const p = S.idx.parts.get(id);
  return '<button class="v-link" data-part="' + esc(id) + '" style="--sub:' + subCss(M.subKey(id)) + '"><i></i>' + esc(id) + (p && p.name ? ' ' + esc(p.name) : '') + '</button>'; };
function kv(rows) { return '<dl class="ds-kv">' + rows.map(([k, v]) => '<dt>' + esc(k) + '</dt><dd>' + v + '</dd>').join('') + '</dl>'; }
function claimHtml(c) {
  const val = c.value === null || c.value === undefined ? '—' : (typeof c.value === 'number' ? M.fmtNum(c.value, Math.abs(c.value) < 10 ? 2 : 1) : esc(c.value));
  const unit = c.unit && c.unit !== '-' ? ' ' + esc(c.unit) : '';
  return '<li class="v-claim"><div><span>' + esc(c.title || c.id) + '</span>' +
    '<div class="val">' + esc(c.id) + ' · ' + val + unit + (c.limit ? ' (limit ' + esc(M.limitText(c.limit)) + unit + ')' : '') + '</div>' +
    (c.how ? '<div class="how">Verify: ' + esc(c.how) + '</div>' : '') + '</div>' + badge(c.status) + '</li>';
}
function renderPanel() {
  const I = $('#inspector');
  if (!S.sel) { I.innerHTML = summaryHtml(); return; }
  if (S.sel.type === 'edge') { I.innerHTML = edgeHtml(S.sel.id); return; }
  const id = S.sel.id, p = S.idx.parts.get(id), k = M.subKey(id), ifs = M.interfacesOf(id, S.idx), claims = S.idx.claimsByPart.get(id) || [];
  const e = G.parts.get(id);
  const nums = [['Mass', M.fmtMass(p.mass_g) + (p.flight === false ? ' <span class="ds-meta">(ground, not flying mass)</span>' : '')], ['Material', esc(p.material || '—')],
    ['Make / buy', esc(p.make_or_buy || '—') + (typeof p.unit_cost_usd === 'number' ? ' · $' + M.fmtNum(p.unit_cost_usd, 2) : '')],
    ['Vendor / file', esc(p.vendor || '—')]];
  if (p.qty && p.qty !== 1) nums.push(['Qty', M.fmtNum(p.qty)]);
  if (p.process) nums.push(['Process', esc(p.process)]);
  nums.push(['CG x y z', Array.isArray(p.cg_xyz_m) ? p.cg_xyz_m.map(v => M.fmtNum(v, 3)).join(', ') + ' m' : '—']);
  if (p.electrical) nums.push(['Electrical', esc(p.electrical)]);
  if (!e) nums.push(['3-D model', 'no geometry']);
  const spec = p.spec ? GH + p.spec.replace(/^\.\.\//, '') : null;
  let h = '<article class="ds-part" data-sub="' + k + '" style="--sub:' + subCss(k) + '"><header><div class="id"><i class="sub"></i>' + esc(id) + ' · ' + esc(p.subsystem || '') +
    (p.csv_ref ? ' · ' + esc(p.csv_ref.replace(/^redesign\//, '')) : '') + '</div><div class="name">' + esc(p.name || id) + ' ' + badge(p.status) + '</div></header>' +
    '<section class="ds-row"><button class="ds-btn primary" data-act="focus"' + (e ? '' : ' disabled') + '>Focus</button>' +
    '<button class="ds-btn" data-act="isolate"' + (e ? '' : ' disabled') + '>' + (S.isolated === id ? 'Show all' : 'Isolate') + '</button>' +
    (spec ? '<a class="ds-btn" href="' + esc(spec) + '" target="_blank" rel="noopener">SPEC.md</a>' : '') + '</section>' +
    '<section><h3>Numbers</h3>' + kv(nums) + (p.notes ? '<p class="ds-meta" style="margin:6px 0 0">' + esc(p.notes) + '</p>' : '') + '</section>';
  h += '<section><h3>Interfaces (' + ifs.length + ')</h3>' + (ifs.length ? '<ul class="ds-iface v-iface">' + ifs.map(f => ifaceHtml(f, id)).join('') + '</ul>' : '<p class="ds-meta" style="margin:0">None declared. A part with no interface floats.</p>') + '</section>';
  h += '<section><h3>Claims about this part (' + claims.length + ')</h3>' + (claims.length ? '<ul class="ds-iface">' + claims.map(claimHtml).join('') + '</ul>' : '<p class="ds-meta" style="margin:0">No proof-chain claim names this part.</p>') + '</section></article>';
  I.innerHTML = h; I.scrollTop = 0;
}
function ifaceHtml(f, selfId) {
  const e = f.edge, hingeHere = G.parts.has(e.part_a) && G.parts.get(e.part_a).hinge && G.parts.get(e.part_a).hinge.edge === e.id;
  let pose = '';
  if (hingeHere) {
    const hg = G.parts.get(e.part_a).hinge, v = S.poses[e.id] || 0;
    pose = '<label class="v-pose"><span>Deflect</span><input type="range" data-pose="' + esc(e.id) + '" min="' + hg.limits[0] + '" max="' + hg.limits[1] + '" step="1" value="' + v + '">' +
      '<span class="ds-mono" data-pose-val="' + esc(e.id) + '">' + v + '°</span></label>';
  }
  const fail = e.joint_stack && e.joint_stack.engagement_mm < e.joint_stack.min_engagement_mm;
  return '<li><details' + (fail || pose ? ' open' : '') + '><summary><div>' + partLink(f.other) + '<span class="via">' + esc(f.spec) + ' · ' + esc(e.id) + '</span></div>' +
    (fail ? badge('FAIL') : '<span class="via">' + esc(f.kind) + '</span>') + '</summary>' +
    (f.rows.length ? kv(f.rows.map(([a, b]) => [a, esc(b)])) : '') + (e.notes ? '<p class="ds-meta" style="margin:0 0 4px">' + esc(e.notes) + '</p>' : '') + pose + '</details></li>';
}
function edgeHtml(id) {
  const e = S.idx.edges.get(id), j = G.joints.get(id), w = G.wires.get(id);
  if (!e) {
    const u = (j || w).node.userData;
    return '<article class="ds-part"><header><div class="id">' + esc(id) + '</div><div class="name">' + esc(u.kind || 'joint') + '</div></header><section>' +
      kv(Object.entries(u).map(([a, b]) => [a, esc(typeof b === 'object' ? JSON.stringify(b) : b)])) + '</section></article>';
  }
  const f = M.interfacesOf(e.part_a, S.idx).find(x => x.edge.id === id) || { rows: [], kind: M.edgeKind(e, S.idx), spec: e.via };
  return '<article class="ds-part"><header><div class="id">' + esc(id) + ' · owner ' + esc(e.owner || '—') + '</div><div class="name">' + esc(f.spec) + ' <span class="ds-meta">' + esc(f.kind) + '</span></div></header>' +
    '<section class="ds-row"><button class="ds-btn primary" data-act="focus">Focus</button></section>' +
    '<section><h3>Between</h3><ul class="ds-iface"><li>' + partLink(e.part_a) + '</li><li>' + partLink(e.part_b) + '</li></ul></section>' +
    (f.rows.length ? '<section><h3>' + (e.joint_stack ? 'Joint stack' : e.wire ? 'Wire installation' : 'Motion') + '</h3>' + kv(f.rows.map(([a, b]) => [a, esc(b)])) + '</section>' : '') +
    (e.notes ? '<section class="ds-meta">' + esc(e.notes) + '</section>' : '') + '</article>';
}
function hardwareHtml() {
  const hs = M.hardwareSummary(S.data), inGlb = hs.parts.filter(p => G.parts.has(p.id)).length;
  let h = '<div class="ds-panel v-summary"><h2>Fasteners &amp; hardware</h2><p>Every screw, nut, washer, insert and spacer in the model, drawn in orange with a ring at its centre; ' +
    'everything else is ghosted. Click a ring or a row to focus it. <span class="ds-kbd">H</span> returns to the previous view.</p>' +
    kv([['Hardware parts', M.fmtNum(hs.parts.length) + ' <span class="ds-meta">' + inGlb + ' with geometry</span>'], ['Pieces', M.fmtNum(hs.pieces)],
      ['Flight hardware', M.fmtMass(hs.mass_g)], ['Ground kit hardware', M.fmtMass(hs.ground_mass_g) + ' <span class="ds-meta">not flying mass</span>']]);
  h += '<table class="v-subtable v-hwtable"><tr><th>Type</th><th>Material</th><th>Parts</th><th>Pcs</th><th>Mass</th></tr>';
  for (const r of hs.rows) h += '<tr><td>' + esc(r.type) + (r.ground ? ' <span class="ds-meta">ground</span>' : '') + '</td><td>' + esc(r.material) + '</td><td>' + r.parts + '</td><td>' + r.pieces + '</td><td>' + M.fmtMass(r.mass_g) + '</td></tr>';
  h += '<tr class="tot"><td>Total</td><td></td><td>' + hs.parts.length + '</td><td>' + hs.pieces + '</td><td>' + M.fmtMass(hs.mass_g + hs.ground_mass_g) + '</td></tr></table>';
  h += '<p class="ds-source">Classified by part name (screw, bolt, nut, washer, insert, spacer, nyloc, SHCS, pan head); pieces read from "n x" in the name.</p></div>';
  return h;
}
function summaryHtml() {
  if (S.fast) return hardwareHtml();
  const d = S.data, mc = M.massCG(d), by = {};
  for (const p of d.parts) if (p.flight !== false) by[p.status] = (by[p.status] || 0) + 1;
  const lim = mc.limit_g, over = lim !== null && mc.total_g > lim;
  let h = '<div class="ds-panel v-summary"><h2>K09-L as designed</h2><p>Click a part for its numbers, interfaces and claims; double-click to focus. ' +
    'Modes: <b>Aircraft</b>, <b>Inside &amp; wiring</b> (skins x-rayed, electrical parts solid), <b>Structure</b> (load path only), <b>Exploded</b> (slider).</p>' +
    '<div class="ds-row">' + M.STATUSES.filter(s => by[s]).map(s => badge(s) + '<span class="ds-meta ds-mono">' + by[s] + '</span>').join(' ') + '</div>' +
    kv([['Flight parts', M.fmtNum(mc.count)], ['Declared mass', M.fmtMass(mc.total_g) + (lim !== null ? ' <span class="ds-meta">of ' + M.fmtMass(lim) + ' gate</span>' : '')],
      ['CG x', mc.cg ? M.fmtNum(mc.cg[0], 3) + ' m' + (mc.cg_range ? ' <span class="ds-meta">target ' + M.fmtNum(mc.cg_range[0], 3) + '–' + M.fmtNum(mc.cg_range[1], 3) + '</span>' : '') : '—'],
      ['Interfaces', M.fmtNum(d.edges.length)], ['Claims', M.fmtNum(d.claims.length)], ['Data built', esc(d.generated)]]);
  if (lim !== null) h += '<div class="v-meter' + (over ? ' over' : '') + '"><i style="width:' + Math.min(100, mc.total_g / lim * 100).toFixed(1) + '%"></i></div>';
  if (mc.subsystems.length) {
    h += '<table class="v-subtable"><tr><th>Subsystem</th><th>Mass</th><th>Allocation</th></tr>';
    for (const s of mc.subsystems) h += '<tr><td>' + esc(s.subsystem) + '</td><td' + (s.alloc_g !== null && s.mass_g > s.alloc_g ? ' class="over"' : '') + '>' +
      M.fmtMass(s.mass_g) + '</td><td>' + M.fmtMass(s.alloc_g) + '</td></tr>';
    h += '</table>';
  }
  h += '<div class="v-keys"><span class="ds-kbd">1</span>Aircraft<span class="ds-kbd">2</span>Inside &amp; wiring<span class="ds-kbd">3</span>Structure<span class="ds-kbd">4</span>Exploded' +
    '<span class="ds-kbd">H</span>Fasteners<span class="ds-kbd">F</span>Focus selected<span class="ds-kbd">Esc</span>Show full aircraft<span class="ds-kbd">/</span>Search</div>' +
    '<p class="ds-source">Declared masses from interfaces.json (A3-R7 roll-up in MASS-CG.md); allocations from params/mass_budget.json; geometry from blender/export_glb.py; ground tools excluded.</p></div>';
  return h;
}

// ---------------- legend, hint, counts ----------------
function renderLegend() {
  const L = $('#legend'); let items = [];
  if (S.fast) {
    const n = S.data.parts.filter(p => G.parts.has(p.id) && M.isHardware(p) && roleOf(p.id) !== 'hidden').length;
    L.innerHTML = '<span><i style="--c:var(--highlight)"></i>hardware ' + n + '</span><span><i style="--c:var(--fg-3)"></i>ghost: everything else</span><span>H to exit</span>'; return;
  }
  if (S.colour === 'realistic') { L.innerHTML = ''; return; }
  if (S.colour === 'status') {
    const by = {}; for (const p of S.data.parts) if (G.parts.has(p.id) && roleOf(p.id) !== 'hidden') by[p.status] = (by[p.status] || 0) + 1;
    items = M.STATUSES.filter(s => by[s]).map(s => [G.colours.css.status(s), s + ' ' + by[s]]);
  } else {
    const seen = new Map(); for (const p of S.data.parts) if (G.parts.has(p.id) && roleOf(p.id) !== 'hidden') { const k = M.subKey(p.id); if (!seen.has(k)) seen.set(k, new Set()); seen.get(k).add(p.subsystem); }
    items = [...seen].map(([k, s]) => [subCss(k), [...s].join(', ')]);
  }
  if (S.mode === 'inside') items.push(['var(--fg-3)', 'ghost: not electrical']);
  if (S.mode === 'structure') items.push(['var(--fg-3)', 'dots: joints']);
  L.innerHTML = items.map(([c, t]) => '<span><i style="--c:' + c + '"></i>' + esc(t) + '</span>').join('');
}
function hint() {
  $('#hint').textContent = S.fast ? 'Fasteners: click a ring or a row to focus · H to exit · drag to rotate · scroll to zoom'
    : S.mode === 'exploded' ? 'Drag the slider · drag to rotate · scroll to zoom · H fasteners' : 'Drag to rotate · right-drag to pan · scroll to zoom · click a part · double-click to focus · H fasteners';
}
function renderCounts() {
  const d = S.data, mc = M.massCG(d);
  $('#counts').textContent = M.fmtNum(mc.count) + ' flight parts · ' + M.fmtMass(mc.total_g) + ' · ' + M.fmtNum(d.edges.length) + ' interfaces';
}

// ---------------- events ----------------
function wire() {
  $('#modes').addEventListener('click', ev => { const b = ev.target.closest('button[data-mode]'); if (b) setMode(b.dataset.mode); });
  $('#attitude').addEventListener('click', ev => { const b = ev.target.closest('button[data-att]'); if (b) setAttitude(b.dataset.att); });
  $('#colours').addEventListener('click', ev => { const b = ev.target.closest('button[data-colour]'); if (b) setColour(b.dataset.colour); });
  $('#kit').addEventListener('click', () => G.root && setKit(!S.kit));
  $('#fast').addEventListener('click', () => setFast(!S.fast));
  $('#fit').addEventListener('click', () => G.root && fit(visibleBox()));
  $('#showall').addEventListener('click', () => G.root && showAll());
  $('#explode-range').addEventListener('input', ev => { setExplode(ev.target.value / 100); applyLook(); });
  $('#explode-play').addEventListener('click', async () => { await explodeTo(0, 350); await explodeTo(1, 1100); });
  $('#search').addEventListener('input', ev => { S.query = ev.target.value.trim(); renderTree(); });
  $('#search').addEventListener('keydown', ev => {
    if (ev.key === 'Enter') { const b = $('#tree [data-part]'); if (b) select({ type: 'part', id: b.dataset.part }, { focus: true }); }
    if (ev.key === 'Escape') { ev.target.value = ''; S.query = ''; renderTree(); ev.target.blur(); }
  });
  $('#explorer').addEventListener('click', ev => {
    const t = ev.target.closest('[data-part],[data-edge],[data-act]');
    if (!t || t.closest('summary') && !t.matches('.v-link')) return;
    if (t.dataset.part) { ev.preventDefault(); select({ type: 'part', id: t.dataset.part }, { focus: true }); }
    else if (t.dataset.edge) select({ type: 'edge', id: t.dataset.edge }, { focus: true });
    else if (t.dataset.act === 'focus' && S.sel) focusOn(S.sel);
    else if (t.dataset.act === 'isolate' && S.sel) { S.isolated = S.isolated === S.sel.id ? null : S.sel.id; applyLook(); renderPanel(); renderTree(true); fit(visibleBox()); }
  });
  $('#inspector').addEventListener('input', ev => {
    const id = ev.target.dataset.pose; if (!id) return;
    S.poses[id] = +ev.target.value; $('#inspector [data-pose-val="' + id + '"]').textContent = ev.target.value + '°'; placeAll();
  });
  const cv = $('#canvas'); let down = null;
  cv.addEventListener('pointerdown', ev => { down = { x: ev.clientX, y: ev.clientY }; });
  cv.addEventListener('pointerup', ev => {
    if (!down || !G.root || Math.hypot(ev.clientX - down.x, ev.clientY - down.y) > 5) { down = null; return; }
    down = null; const hit = pick(ev); select(hit ? hit.ref : null);
  });
  let hoverQ = null;
  cv.addEventListener('pointermove', ev => {
    if (!G.root || ev.buttons || ev.pointerType === 'touch') return;
    if (!hoverQ) requestAnimationFrame(() => { const ev2 = hoverQ; hoverQ = null; const h = pick(ev2);
      setHover(h && h.ref && !h.object_ghost && (G.parts.has(h.ref.id) || G.wires.has(h.ref.id)) ? h.ref.id : null); });
    hoverQ = ev;
  });
  cv.addEventListener('pointerleave', () => G.root && setHover(null));
  cv.addEventListener('dblclick', ev => { if (!G.root) return; const hit = pick(ev); if (hit) select(hit.ref, { focus: true }); else fit(visibleBox()); });
  document.addEventListener('keydown', ev => {
    if (ev.target.closest('input, textarea, select') || ev.ctrlKey || ev.metaKey || ev.altKey || !G.root) return;
    if (location.hash && location.hash !== '#aircraft') return;
    const k = ev.key;
    if (k >= '1' && k <= '4') setMode(M.MODES[+k - 1]);
    else if ((k === 'f' || k === 'F') && S.sel) focusOn(S.sel);
    else if (k === 'h' || k === 'H') setFast(!S.fast);
    else if (k === 'Home') fit(visibleBox());
    else if (k === '/') { ev.preventDefault(); $('#search').focus(); }
    else if (k === 'Escape') { if (S.isolated) { S.isolated = null; applyLook(); renderPanel(); } else if (S.sel) select(null); else showAll(); }
  });
  if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChanged);
}
function themeChanged() {
  readColours();
  if (G.hwMat) { hwMaterial(); if (G.hwMarkers.length) { const m = G.hwMarkers[0].material; m.map.dispose(); m.map = hwTexture(); m.needsUpdate = true; } }
  if (G.root) applyLook();
}

// ---------------- public ----------------
export const viewer = {
  themeChanged,
  setQuery(q) { const s = $('#search'); if (!s) return; s.value = q; S.query = q; if (S.data) renderTree(); },
  resize() { if (G.renderer) resize(); },
  state: S,
  setFasteners: on => setFast(!!on),
};

export async function start() {
  readColours(); wire(); hint();
  progress(0, 'reading part data');
  let data;
  try { const r = await fetch('data/viewer-data.json'); if (!r.ok) throw new Error('HTTP ' + r.status); data = await r.json(); }
  catch (e) { loadFailed('Part data not found', esc(e.message) + '<br>data/viewer-data.json is built by redesign/viewer/build_data.py --out site/data'); return; }
  S.data = data; S.idx = M.index(data);
  renderCounts(); renderTree(); renderPanel();
  if (!initThree()) { loadFailed('3-D is not available', 'This browser could not start WebGL. The part list and panel still work.'); return; }
  const total = (data.glb && data.glb.bytes) || 3443204;
  let gltf;
  try {
    gltf = await new Promise((res, rej) => new GLTFLoader().load('assets/k09l.glb', res,
      ev => { const got = ev.loaded || 0; progress(Math.min(got / total, 1), kB(got) + ' of ' + kB(total)); }, rej));
  } catch (e) { loadFailed('Model could not be loaded', esc((e && e.message) || e) + '<br>assets/k09l.glb'); return; }
  progress(1, 'building scene');
  buildModel(gltf);
  try { await G.renderer.compileAsync(G.scene, G.camera); } catch (e) { /* older drivers: compile on first frame */ }
  applyLook();
  G.camera.position.copy(ISO).multiplyScalar(G.size * 3); G.controls.target.copy(G.box.getCenter(new THREE.Vector3()));
  await fit(visibleBox(), ISO.clone(), 0);
  renderTree(true);
  $('#loading').classList.add('done');
  S.ready = true; window.__k09lReady = true;
}
