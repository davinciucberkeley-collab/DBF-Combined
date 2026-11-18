// fea-view.js - Structures view: 3-D utilisation maps of the FEA models. Each map is a .fea-tool block whose element ids end in
// its suffix ('' for the hub, '-arm' for the arm): data/fea-hub.js (window.FEA_HUB, structures/fea_hub_figs.py) and
// data/fea-arm.js (window.FEA_ARM, structures/fea_arm_figs.py). Loaded on the first visit to #structures.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const TOOLS = [
  { sfx: '', src: 'data/fea-hub.js?v=20261118', key: 'FEA_HUB', cam: [-125, 110, 92], target: [8, 0, 0], frame: 'hub frame', start: 'F2' },
  { sfx: '-arm', src: 'data/fea-arm.js?v=20261118f', key: 'FEA_ARM', cam: [-195, 90, 142], target: [0, 150, 0], frame: 'arm frame: y along the arm from the hub crossing', start: 'F2' },
];
const states = {};

function loadData(t) {
  if (window[t.key]) return Promise.resolve(window[t.key]);
  return new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = t.src; s.onload = () => res(window[t.key]); s.onerror = rej;
    document.head.appendChild(s);
  });
}

function dec(b64, Type) {
  const bin = atob(b64), u8 = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
  return new Type(u8.buffer);
}

function hex(h) { return new THREE.Color(h).convertSRGBToLinear(); }

function colourise(st) {
  const D = st.data, ramp = D.ramp.map(hex), crit = hex(D.crit), nj = hex(D.nj), n = ramp.length - 1;
  st.meshes.forEach(m => {
    const u = m.userData.u[st.caseId], col = m.geometry.attributes.color;
    for (let i = 0; i < u.length; i++) {
      let c;
      if (u[i] === 65535) c = nj;
      else {
        const v = u[i] / 10000;
        if (v > 1) c = crit;
        else { const t = v * n, k = Math.min(Math.floor(t), n - 1), f = t - k; c = ramp[k].clone().lerp(ramp[k + 1], f); }
      }
      col.setXYZ(i, c.r, c.g, c.b);
    }
    col.needsUpdate = true;
  });
  const max = st.data.mats.map(m => m.cases[st.caseId].umax).filter(v => v != null);
  st.q('#fea-umax').textContent = 'Highest utilisation in this case: ' + Math.max(...max).toFixed(2) +
    (Math.max(...max) > 1 ? ' (over 1: see the note under the map)' : ' (all judged parts under 1)');
}

function bg() { return getComputedStyle(document.documentElement).getPropertyValue('--panel').trim() || '#ffffff'; }

async function mountOne(t, el) {
  const q = sel => el.querySelector(sel + t.sfx);
  const host = q('#fea-canvas'), msg = q('#fea-msg');
  if (!host) return;
  if (states[t.key]) { states[t.key].resize(); return; }
  states[t.key] = { resize() {} };
  msg.textContent = 'Loading the FEA mesh...';
  let D;
  try { D = await loadData(t); } catch (e) { msg.textContent = 'The FEA data did not load. The figures below show the same results.'; return; }
  msg.textContent = '';
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(30, 1, 1, 5000); cam.up.set(0, 0, 1);
  cam.position.set(...t.cam);
  const ctl = new OrbitControls(cam, renderer.domElement); ctl.target.set(...t.target); ctl.enableDamping = true;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 2.2));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(-1, 0.6, 1.2); scene.add(sun);
  const meshes = D.mats.map((m, i) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(dec(m.pos, Float32Array), 3));
    g.setIndex(new THREE.BufferAttribute(dec(m.idx, Uint32Array), 1));
    g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(m.n * 3), 3));
    g.computeVertexNormals();
    const mesh = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75, metalness: 0, side: THREE.DoubleSide, flatShading: false }));
    mesh.userData = { name: m.name, idx: i, u: {} };
    Object.keys(m.cases).forEach(c => { mesh.userData.u[c] = dec(m.cases[c].u, Uint16Array); });
    scene.add(mesh); return mesh;
  });
  const state = { el, q, data: D, meshes, caseId: t.start };
  states[t.key] = state;
  colourise(state);

  el.querySelectorAll('[data-fea-case' + (t.sfx ? '-arm' : '') + ']').forEach(b => b.addEventListener('click', () => {
    state.caseId = t.sfx ? b.dataset.feaCaseArm : b.dataset.feaCase;
    el.querySelectorAll('[data-fea-case' + (t.sfx ? '-arm' : '') + ']').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    q('#fea-case-note').textContent = D.cases[state.caseId];
    colourise(state); draw();
  }));
  q('#fea-case-note').textContent = D.cases[t.start];
  const parts = q('#fea-parts');
  D.mats.forEach((m, i) => {
    const l = document.createElement('label');
    l.innerHTML = '<input type="checkbox" checked> ' + m.name;
    l.querySelector('input').addEventListener('change', e => { meshes[i].visible = e.target.checked; draw(); });
    parts.appendChild(l);
  });
  const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(), out = q('#fea-read');
  renderer.domElement.addEventListener('pointermove', e => {
    const r = renderer.domElement.getBoundingClientRect();
    ptr.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ptr, cam);
    const hit = ray.intersectObjects(meshes.filter(m => m.visible))[0];
    if (!hit) { out.textContent = 'Point at the model for the value under the cursor.'; return; }
    const f = hit.face, uu = hit.object.userData.u[state.caseId];
    const vs = [f.a, f.b, f.c], p = hit.point, pos = hit.object.geometry.attributes.position;
    let best = vs[0], bd = Infinity;
    vs.forEach(v => { const d = new THREE.Vector3().fromBufferAttribute(pos, v).distanceTo(p); if (d < bd) { bd = d; best = v; } });
    const u = uu[best];
    out.textContent = hit.object.userData.name + ': ' + (u === 65535 ? 'not judged' : 'utilisation ' + (u / 10000).toFixed(2)) +
      ' at x ' + p.x.toFixed(1) + ', y ' + p.y.toFixed(1) + ', z ' + p.z.toFixed(1) + ' mm (' + t.frame + ')';
  });
  q('#fea-reset').addEventListener('click', () => { cam.position.set(...t.cam); ctl.target.set(...t.target); draw(); });

  let raf = 0;
  function draw() { if (!raf) raf = requestAnimationFrame(frame); }
  function frame() { raf = 0; const moving = ctl.update(); renderer.setClearColor(bg()); renderer.render(scene, cam); if (moving) draw(); }
  ctl.addEventListener('change', draw);
  state.resize = () => {
    const w = host.clientWidth, h = host.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h); cam.aspect = w / h; cam.zoom = Math.min(1, 1.25 * w / h); cam.updateProjectionMatrix(); draw();
  };
  new ResizeObserver(() => state.resize()).observe(host);
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
  new MutationObserver(draw).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  state.resize();
}

export async function mountFea() {
  const el = document.getElementById('structures');
  await Promise.all(TOOLS.map(t => mountOne(t, el)));
}
