// Aircraft web viewer (browser side). Classic script: works from file://, a local server and GitHub Pages.
// Data:      data/<dataset>/viewer-data.js  (build_data.py: parts, interfaces, claims, mass budget)
// Geometry:  data/<dataset>/assembly.glb    (blender/export_glb.py; node names = part ids, glTF extras = part data)
// Rules (which parts a mode shows, mass/CG, search) live in model.js so check_viewer.js can test them in Node.
'use strict';
(function () {
  const M = window.ViewerModel, THREE = window.THREE, X = window.THREE_ADDONS;
  const $ = s => document.querySelector(s);
  const esc = s => String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const reduceMotion = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = { get(k) { try { return localStorage.getItem('dbf-viewer.' + k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem('dbf-viewer.' + k, v); } catch (e) { /* private mode: fine */ } } };

  // ---------------- state ----------------
  const S = { data: null, idx: null, mode: 'whole', colour: 'subsystem', explode: 0, sel: null, isolated: null,
    measuring: false, cgOn: false, view: 'persp', poses: {}, query: '' };
  // three.js objects
  const G = { renderer: null, scene: null, persp: null, ortho: null, camera: null, controls: null, root: null,
    parts: new Map(), wires: new Map(), joints: new Map(), box: new THREE.Box3(), size: 1, ground: null, key: null,
    measure: { pts: [], group: null }, cg: null, dirty: true, anims: [], colours: {} };

  // ---------------- colours from the design-system tokens ----------------
  function readColours() {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim() || '#888';
    const c = G.colours;
    c.sub = {}; for (const k of M.PREFIXES) c.sub[k] = new THREE.Color(v('--sub-' + k.toLowerCase()));
    c.sub.OTHER = new THREE.Color(v('--fg-3'));
    c.status = {}; for (const s of M.STATUSES.concat(['UNVERIFIED', 'FAIL'])) c.status[s] = new THREE.Color(v('--st-' + s.toLowerCase()));
    c.accent = new THREE.Color(v('--accent')); c.fg = new THREE.Color(v('--fg')); c.fg3 = new THREE.Color(v('--fg-3'));
    c.bg = new THREE.Color(v('--stage-bottom')); c.ghost = new THREE.Color(isDark() ? '#7D8CA0' : '#9AA9BC');
    c.css = { sub: k => v('--sub-' + k.toLowerCase()), status: s => v('--st-' + s.toLowerCase()) };
  }
  const isDark = () => { const t = document.documentElement.getAttribute('data-theme');
    return t ? t === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches); };

  // ---------------- loading ----------------
  function loadScript(src) {
    return new Promise(res => { const s = document.createElement('script'); s.src = src;
      s.onload = () => { s.remove(); res(true); }; s.onerror = () => { s.remove(); res(false); }; document.head.appendChild(s); });
  }
  async function loadData() {
    const want = new URLSearchParams(location.search).get('data');
    const tryDs = async ds => { window.VIEWER_DATA = undefined; return (await loadScript('data/' + ds + '/viewer-data.js')) ? window.VIEWER_DATA || null : null; };
    if (want && /^[\w-]+$/.test(want)) {
      const d = await tryDs(want);
      return d ? { d } : { error: 'data/' + want + '/viewer-data.js was not found. Build it with python -I redesign/viewer/build_data.py' + (want === 'examples' ? ' --examples' : '') + '.' };
    }
    const real = await tryDs('aircraft');
    if (real && real.glb) return { d: real };
    const demo = await tryDs('examples');
    if (demo) return { d: demo, note: 'Showing the generic test aircraft: ' + (real ? 'the real aircraft has no 3-D model yet' : 'data/aircraft/ is not built yet') +
      '. <a href="?data=aircraft">Open the real aircraft data</a>' };
    return { error: 'No viewer data found. Run python -I redesign/viewer/build_data.py --examples, then reload.' };
  }
  function progress(frac, text) {
    const bar = $('#load-bar'); bar.parentElement.classList.toggle('indeterminate', frac === null);
    if (frac !== null) bar.style.width = Math.round(frac * 100) + '%';
    if (text) $('#load-text').textContent = text;
  }
  const kB = n => M.fmtNum(n / 1024) + ' kB';
  // over http(s): streamed fetch with a byte count; from file:// (or if fetch fails): the base64 copy as a script
  async function fetchGlb(url, bytes) {
    if (/^https?:$/.test(location.protocol)) {
      try {
        const r = await fetch(url);
        if (!r.ok) throw new Error('HTTP ' + r.status);
        const total = bytes || +r.headers.get('content-length') || 0;  // stored size: Pages may gzip the transfer
        if (!r.body || !total) return await r.arrayBuffer();
        const reader = r.body.getReader(), chunks = []; let got = 0;
        for (;;) {
          const { done, value } = await reader.read(); if (done) break;
          chunks.push(value); got += value.length; progress(Math.min(got / total, 1), kB(got) + ' of ' + kB(total));
        }
        const buf = new Uint8Array(got); let o = 0; for (const c of chunks) { buf.set(c, o); o += c.length; }
        return buf.buffer;
      } catch (e) { console.warn('GLB fetch failed, using the script copy:', e.message); }
    }
    progress(null, 'reading ' + (bytes ? kB(bytes) : 'model'));
    window.VIEWER_GLB_B64 = undefined;
    if (!(await loadScript(url + '.js')) || !window.VIEWER_GLB_B64) throw new Error(url + '.js not found');
    const bin = atob(window.VIEWER_GLB_B64); window.VIEWER_GLB_B64 = undefined;
    const u = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
    return u.buffer;
  }
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
    r.toneMapping = THREE.NeutralToneMapping;  // keeps token colours close to their hex values
    r.shadowMap.enabled = true; r.shadowMap.type = THREE.PCFSoftShadowMap;
    G.scene = new THREE.Scene();
    const pmrem = new THREE.PMREMGenerator(r);
    G.scene.environment = pmrem.fromScene(new X.RoomEnvironment(), 0.04).texture;
    G.scene.environmentIntensity = 0.85;
    G.scene.add(new THREE.HemisphereLight(0xffffff, 0x8090a0, 0.35));
    G.key = new THREE.DirectionalLight(0xffffff, 1.6); G.key.castShadow = true;
    G.key.shadow.mapSize.set(2048, 2048); G.key.shadow.bias = -0.0004; G.key.shadow.radius = 4;
    G.scene.add(G.key, G.key.target);
    G.persp = new THREE.PerspectiveCamera(32, 1, 0.005, 100);
    G.ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, -100, 100);
    G.camera = G.persp;
    G.controls = new X.OrbitControls(G.persp, canvas);
    Object.assign(G.controls, { enableDamping: true, dampingFactor: 0.12, screenSpacePanning: true, zoomToCursor: true });
    G.controls.addEventListener('change', requestRender);
    new ResizeObserver(resize).observe($('#stage'));
    resize();
    requestAnimationFrame(loop);
    return true;
  }
  function resize() {
    const st = $('#stage'), w = st.clientWidth || 1, h = st.clientHeight || 1;
    G.renderer.setSize(w, h, false);
    G.persp.aspect = w / h; G.persp.updateProjectionMatrix();
    const hh = G.ortho.userData.half || 1;
    Object.assign(G.ortho, { left: -hh * w / h, right: hh * w / h, top: hh, bottom: -hh }); G.ortho.updateProjectionMatrix();
    requestRender();
  }
  function requestRender() { G.dirty = true; }
  const ease = t => 1 - Math.pow(1 - t, 3);
  function animate(dur, fn) {  // fn(k) with k eased 0..1; returns a promise
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
    sizeMarkers();
    G.renderer.render(G.scene, G.camera);
    placeLabels();
  }

  // joint markers keep about the same size on screen at any zoom (radius 0.6 % of the view height)
  function sizeMarkers() {
    const cam = G.camera, r0 = G.size * 0.007;
    for (const j of G.joints.values()) if (j.marker && j.marker.visible) {
      const view = cam.isPerspectiveCamera ? 2 * cam.position.distanceTo(j.pos) * Math.tan(THREE.MathUtils.degToRad(cam.fov / 2))
        : (cam.top - cam.bottom) / cam.zoom;
      j.marker.scale.setScalar(Math.min(view * 0.006 / r0, 1.5));
    }
  }

  // ---------------- model ----------------
  function buildModel(gltf) {
    G.root = gltf.scene; G.scene.add(G.root); G.root.updateMatrixWorld(true);
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
        G.joints.set(u.edge, { id: u.edge, node: o, data: u, pos: o.getWorldPosition(new THREE.Vector3()) });
      }
    });
    // parts with geometry but no data row (build_data.py warns) still get a minimal record
    for (const id of G.parts.keys()) if (!idx.parts.has(id)) {
      const u = G.parts.get(id).node.userData; idx.parts.set(id, { id, name: u.name, subsystem: u.subsystem, status: u.status, mass_g: u.mass_g });
      idx.edgesByPart.set(id, []); idx.claimsByPart.set(id, []);
    }
    G.box.setFromObject(G.root);
    const size = G.box.getSize(new THREE.Vector3()), c = G.box.getCenter(new THREE.Vector3());
    G.size = Math.max(size.x, size.y, size.z) || 1;
    G.persp.near = G.size / 500; G.persp.far = G.size * 50; G.persp.updateProjectionMatrix();
    G.ortho.near = -G.size * 20; G.ortho.far = G.size * 20;
    // shadow catcher and key light sized to the model
    G.ground = new THREE.Mesh(new THREE.PlaneGeometry(G.size * 8, G.size * 8), new THREE.ShadowMaterial({ opacity: isDark() ? 0.35 : 0.16 }));
    G.ground.rotation.x = -Math.PI / 2; G.ground.position.set(c.x, G.box.min.y - G.size * 0.01, c.z); G.ground.receiveShadow = true;
    G.ground.userData.noPick = true; G.scene.add(G.ground);
    G.key.position.set(c.x - G.size * 0.6, c.y + G.size * 1.6, c.z + G.size * 0.9); G.key.target.position.copy(c);
    const sc = G.key.shadow.camera; Object.assign(sc, { left: -G.size, right: G.size, top: G.size, bottom: -G.size, near: 0.01, far: G.size * 6 });
    sc.updateProjectionMatrix();
    // joint markers (Inside and Structure modes)
    const geo = new THREE.SphereGeometry(G.size * 0.007, 16, 12);
    for (const j of G.joints.values()) {
      const e = idx.edges.get(j.id), kind = e ? M.edgeKind(e, idx) : (j.data.kind === 'revolute' ? 'hinge' : 'fastened');
      if (kind === 'wire') continue;
      j.marker = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false, transparent: true }));
      j.marker.position.copy(j.pos); j.marker.renderOrder = 20; j.kind = kind;
      j.marker.userData.ref = { type: 'edge', id: j.id };
      G.scene.add(j.marker);
    }
    // hinge pivots: part_a turns about the joint axis (aircraft frame) through the joint position
    for (const j of G.joints.values()) if (j.data.kind === 'revolute' && j.data.part_a && G.parts.has(j.data.part_a)) {
      const ax = M.AXIS_AC[String(j.data.axis || 'Y').toUpperCase()] || [0, 1, 0];
      G.parts.get(j.data.part_a).hinge = { edge: j.id, pivot: j.pos.clone(), axis: new THREE.Vector3(...M.ac2gl(ax)).normalize(),
        limits: Array.isArray(j.data.limits) ? j.data.limits : [-30, 30] };
    }
  }
  function prepMesh(m, ref) {
    const orig = Array.isArray(m.material) ? m.material[0] : m.material;
    m.material = orig.clone(); m.userData.origColor = orig.color ? orig.color.clone() : new THREE.Color(0x999999);
    m.userData.ref = ref; m.castShadow = true; m.receiveShadow = true;
  }
  // explode offset and hinge deflection, composed on the node's own (export) transform
  const _m = new THREE.Matrix4(), _r = new THREE.Matrix4(), _t = new THREE.Matrix4();
  function placePart(e) {
    _m.makeTranslation(e.explode.x * S.explode, e.explode.y * S.explode, e.explode.z * S.explode);
    const deg = e.hinge ? S.poses[e.hinge.edge] || 0 : 0;
    if (deg) {
      const p = e.hinge.pivot;
      _m.multiply(_t.makeTranslation(p.x, p.y, p.z)).multiply(_r.makeRotationAxis(e.hinge.axis, deg * Math.PI / 180))
        .multiply(_t.makeTranslation(-p.x, -p.y, -p.z));
    }
    _m.multiply(e.base);
    e.node.matrix.copy(_m); e.node.matrix.decompose(e.node.position, e.node.quaternion, e.node.scale);
  }
  function placeAll() { for (const e of G.parts.values()) placePart(e); requestRender(); }

  // ---------------- look: mode x colour x selection ----------------
  function partColour(p, mesh) {
    if (S.colour === 'material') return mesh.userData.origColor;
    if (S.colour === 'status') return G.colours.status[p.status] || G.colours.status.PROPOSED;
    return G.colours.sub[M.subKey(p.id)];
  }
  function edgesOf(mesh, kind) {  // lazily made outline lines: 'sel' (accent, drawn on top) or 'ghost' (faint)
    const key = kind + 'Lines';
    if (!mesh.userData[key]) {
      const geo = mesh.userData.edgeGeo || (mesh.userData.edgeGeo = new THREE.EdgesGeometry(mesh.geometry, 28));
      const mat = new THREE.LineBasicMaterial({ transparent: true, depthTest: kind !== 'sel', opacity: kind === 'sel' ? 0.95 : 0.28 });
      const l = new THREE.LineSegments(geo, mat); l.renderOrder = kind === 'sel' ? 30 : 5; l.userData.noPick = true;
      mesh.add(l); mesh.userData[key] = l;
    }
    return mesh.userData[key];
  }
  function roleOf(id) {
    const p = S.idx.parts.get(id), selected = S.sel && S.sel.type === 'part' && S.sel.id === id;
    if (S.isolated) return id === S.isolated ? 'solid' : 'hidden';
    const r = M.role(S.mode, p, S.idx);
    return selected && r !== 'solid' ? 'solid' : r;   // the selected part is always shown
  }
  function applyLook() {
    if (!G.root) return;
    const c = G.colours, selId = S.sel ? S.sel.id : null, anySel = !!S.sel;
    for (const [id, e] of G.parts) {
      const p = S.idx.parts.get(id), r = roleOf(id), isSel = selId === id;
      e.node.visible = r !== 'hidden';
      for (const m of e.meshes) {
        const mat = m.material, ghost = r === 'ghost';
        m.userData.ghost = ghost;
        if (ghost) { mat.color.copy(c.ghost); mat.opacity = 0.18; }
        else { mat.color.copy(partColour(p, m)); mat.opacity = 1; if (anySel && !isSel) mat.color.lerp(c.bg, 0.5); }
        mat.transparent = ghost; mat.depthWrite = !ghost; m.castShadow = !ghost;
        if (mat.emissive) mat.emissive.copy(isSel ? c.accent : new THREE.Color(0)).multiplyScalar(isSel ? 0.12 : 0);
        mat.needsUpdate = true;
        if (ghost || m.userData.ghostLines) { const l = edgesOf(m, 'ghost'); l.visible = ghost; l.material.color.copy(c.fg3); }
        if (isSel || m.userData.selLines) { const l = edgesOf(m, 'sel'); l.visible = isSel; l.material.color.copy(c.accent); }
      }
    }
    const wiresOn = M.showWires(S.mode) && S.explode < 0.01;
    for (const [id, w] of G.wires) {
      const isSel = selId === id;
      w.node.visible = isSel || (wiresOn && !S.isolated);
      for (const m of w.meshes) { m.material.color.copy(m.userData.origColor); if (anySel && !isSel) m.material.color.lerp(c.bg, 0.5);
        if (m.material.emissive) m.material.emissive.copy(c.accent).multiplyScalar(isSel ? 0.35 : 0); }
    }
    const jointsOn = M.showJoints(S.mode) && S.explode < 0.01 && !S.isolated;
    for (const [id, j] of G.joints) if (j.marker) {
      j.marker.visible = jointsOn || selId === id;
      j.marker.material.color.copy(selId === id ? c.accent : j.kind === 'hinge' ? c.fg : c.fg3);
    }
    G.ground.material.opacity = isDark() ? 0.35 : 0.16;
    renderLegend(); requestRender();
  }

  // ---------------- camera ----------------
  const VIEWS = { persp: null, top: [0.0001, 1, 0], front: [-1, 0, 0], side: [0, 0, 1] };  // glTF directions to the camera
  const ISO = new THREE.Vector3(-1, 0.75, 1.15).normalize();   // front-left, above
  function visibleBox() {
    const b = new THREE.Box3();
    for (const e of G.parts.values()) if (e.node.visible) b.expandByObject(e.node);
    return b.isEmpty() ? G.box.clone() : b;
  }
  function fit(box, dir, dur) {
    const sph = box.getBoundingSphere(new THREE.Sphere()), r = Math.max(sph.radius, G.size * 0.04);
    const cam = G.camera, ctl = G.controls;
    dir = (dir || cam.position.clone().sub(ctl.target)).clone().normalize();
    const fromT = ctl.target.clone(), fromP = cam.position.clone(), toT = sph.center.clone();
    let toP, fromZ = cam.zoom, toZ = 1, fromH = G.ortho.userData.half || r, toH = r * 1.12;
    if (cam.isPerspectiveCamera) toP = toT.clone().add(dir.multiplyScalar(r / Math.sin(THREE.MathUtils.degToRad(cam.fov / 2)) * (cam.aspect < 1 ? 1.0 / Math.max(cam.aspect, 0.5) * 0.9 : 0.9)));
    else toP = toT.clone().add(dir.multiplyScalar(G.size * 4));
    return animate(dur === undefined ? 600 : dur, k => {
      ctl.target.lerpVectors(fromT, toT, k); cam.position.lerpVectors(fromP, toP, k);
      if (cam.isOrthographicCamera) { cam.zoom = fromZ + (toZ - fromZ) * k; G.ortho.userData.half = fromH + (toH - fromH) * k; resize(); }
      cam.updateProjectionMatrix(); cam.lookAt(ctl.target);
    });
  }
  function setView(v, dur) {
    S.view = v; pressed('#views', 'view', v);
    const ortho = v !== 'persp', cam = ortho ? G.ortho : G.persp;
    if (cam !== G.camera) { cam.position.copy(G.camera.position); G.camera = cam; G.controls.object = cam; }
    G.controls.enableRotate = !ortho;
    if (G.ground) G.ground.visible = !ortho;   // no floor shadow in plan and elevation views
    hint();
    const dir = ortho ? new THREE.Vector3(...VIEWS[v]) : ISO.clone();
    if (ortho) { G.ortho.userData.half = G.ortho.userData.half || G.size * 0.6; resize(); }
    return fit(visibleBox(), dir, dur);
  }
  function focusOn(ref) {
    const b = new THREE.Box3();
    if (ref.type === 'part' && G.parts.has(ref.id)) b.expandByObject(G.parts.get(ref.id).node);
    else if (ref.type === 'edge') {
      if (G.wires.has(ref.id)) b.expandByObject(G.wires.get(ref.id).node);
      const e = S.idx.edges.get(ref.id);
      if (e) for (const id of [e.part_a, e.part_b]) if (G.parts.has(id) && G.parts.get(id).node.visible) b.expandByObject(G.parts.get(id).node);
      if (b.isEmpty() && G.joints.has(ref.id)) b.expandByPoint(G.joints.get(ref.id).pos);
    }
    if (!b.isEmpty()) fit(b);
  }

  // ---------------- picking, measure ----------------
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
    const hits = ray.intersectObjects(objs.filter(shown), false);
    // markers are drawn on top, so they win; then the first solid surface; a ghost only if nothing else was hit
    const h = hits.find(x => x.object.renderOrder >= 20) || hits.find(x => !x.object.userData.ghost) || hits[0];
    return h ? { ref: h.object.userData.ref, point: h.point } : null;
  }
  function measureClick(hit) {
    const ms = G.measure;
    if (!ms.group) { ms.group = new THREE.Group(); G.scene.add(ms.group); }
    if (ms.pts.length >= 2) clearMeasure(true);
    if (!hit) return;
    ms.pts.push(hit.point.clone());
    const dot = new THREE.Mesh(new THREE.SphereGeometry(G.size * 0.005, 12, 10), new THREE.MeshBasicMaterial({ color: G.colours.accent, depthTest: false }));
    dot.position.copy(hit.point); dot.renderOrder = 40; ms.group.add(dot);
    if (ms.pts.length === 2) {
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(ms.pts), new THREE.LineBasicMaterial({ color: G.colours.accent, depthTest: false }));
      line.renderOrder = 40; ms.group.add(line);
      const a = M.gl2ac(ms.pts[0].toArray()), b = M.gl2ac(ms.pts[1].toArray()), d = ms.pts[0].distanceTo(ms.pts[1]);
      const lab = document.createElement('div'); lab.className = 'v-label';
      lab.innerHTML = esc(M.fmtLen(d)) + '<small>Δx ' + M.fmtNum((b[0] - a[0]) * 1000, 1) + ' · Δy ' + M.fmtNum((b[1] - a[1]) * 1000, 1) +
        ' · Δz ' + M.fmtNum((b[2] - a[2]) * 1000, 1) + ' mm</small>';
      $('#labels').appendChild(lab); ms.label = { el: lab, at: ms.pts[0].clone().add(ms.pts[1]).multiplyScalar(0.5) };
    }
    hint(); requestRender();
  }
  function clearMeasure(keepMode) {
    const ms = G.measure; ms.pts = [];
    if (ms.group) { ms.group.traverse(o => { if (o.geometry) o.geometry.dispose(); }); ms.group.clear(); }
    if (ms.label) { ms.label.el.remove(); ms.label = null; }
    if (!keepMode) setMeasuring(false);
    hint(); requestRender();
  }
  function setMeasuring(on) {
    S.measuring = on; $('#measure').setAttribute('aria-pressed', on); $('#stage').classList.toggle('measuring', on);
    if (!on && G.measure.pts.length) clearMeasure(true);
    hint();
  }
  const _v = new THREE.Vector3();
  function placeLabels() {
    const st = $('#stage'), w = st.clientWidth, h = st.clientHeight;
    const put = (lab, at) => { _v.copy(at).project(G.camera); const off = _v.z > 1;
      lab.style.display = off ? 'none' : ''; lab.style.left = ((_v.x + 1) / 2 * w) + 'px'; lab.style.top = ((1 - _v.y) / 2 * h) + 'px'; };
    if (G.measure.label) put(G.measure.label.el, G.measure.label.at);
    if (G.cg && G.cg.label && G.cg.group.visible) put(G.cg.label, G.cg.at);
  }

  // ---------------- mass / CG overlay ----------------
  function buildCG() {
    const mc = M.massCG(S.data);
    if (!G.cg) G.cg = { group: new THREE.Group() }; else { G.cg.group.clear(); if (G.cg.label) G.cg.label.remove(); }
    const g = G.cg.group; G.scene.add(g); G.cg.label = null;
    const col = G.colours, s = G.size;
    if (mc.cg_range) {   // target band: the allowed CG x range, across the model's span and height
      const [lo, hi] = mc.cg_range, b = G.box, sz = b.getSize(new THREE.Vector3());
      const geo = new THREE.BoxGeometry(hi - lo, sz.y * 1.15, sz.z * 1.05);
      const band = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: mc.in_range === false ? col.status.FAIL : col.status.CHECKED,
        transparent: true, opacity: 0.1, depthWrite: false }));
      band.position.set((lo + hi) / 2, b.min.y + sz.y / 2, (b.min.z + b.max.z) / 2); band.renderOrder = 15;
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: band.material.color, transparent: true, opacity: 0.6 }));
      band.add(edges); g.add(band);
    }
    if (mc.cg) {
      const at = new THREE.Vector3(...M.ac2gl(mc.cg));
      const ball = new THREE.Mesh(new THREE.SphereGeometry(s * 0.012, 24, 16), new THREE.MeshBasicMaterial({ color: col.fg, depthTest: false }));
      ball.position.copy(at); ball.renderOrder = 35; g.add(ball);
      const L = s * 0.06, pts = [];
      for (const d of [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) pts.push(at.clone().addScaledVector(new THREE.Vector3(...d), -L), at.clone().addScaledVector(new THREE.Vector3(...d), L));
      const cross = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: col.fg, depthTest: false }));
      cross.renderOrder = 35; g.add(cross);
      const lab = document.createElement('div'); lab.className = 'v-label cg';
      lab.innerHTML = 'CG<small>x ' + M.fmtNum(mc.cg[0], 3) + ' m</small>'; $('#labels').appendChild(lab);
      G.cg.label = lab; G.cg.at = at; lab.style.display = S.cgOn ? '' : 'none';
    }
    g.visible = S.cgOn; return mc;
  }
  function renderCGPanel() {
    const mc = M.massCG(S.data), P = $('#cgpanel');
    const lim = mc.limit_g, over = lim !== null && mc.total_g > lim;
    const verdict = mc.in_range === null ? '' : mc.in_range ? '<span class="ds-badge" data-status="CHECKED">CHECKED</span>' : '<span class="ds-badge" data-status="FAIL">FAIL</span>';
    let h = '<header>Mass and CG ' + verdict + '</header><section><dl class="ds-kv">' +
      '<dt>Mass</dt><dd>' + M.fmtMass(mc.total_g) + (lim !== null ? ' of ' + M.fmtMass(lim) : '') + '</dd>';
    if (mc.cg) h += '<dt>CG x</dt><dd>' + M.fmtNum(mc.cg[0], 3) + ' m</dd><dt>CG y, z</dt><dd>' + M.fmtNum(mc.cg[1], 3) + ', ' + M.fmtNum(mc.cg[2], 3) + ' m</dd>';
    if (mc.cg_range) h += '<dt>Target x</dt><dd>' + M.fmtNum(mc.cg_range[0], 3) + ' to ' + M.fmtNum(mc.cg_range[1], 3) + ' m</dd>' +
      '<dt>Margin</dt><dd>' + M.fmtLen(mc.margin_m) + '</dd>';
    h += '</dl>';
    if (lim !== null) h += '<div class="v-meter' + (over ? ' over' : '') + '"><i style="width:' + Math.min(100, mc.total_g / lim * 100).toFixed(1) + '%"></i></div>';
    h += '</section>';
    if (mc.subsystems.length) {
      h += '<section><table class="v-subtable"><tr><th>Subsystem</th><th>Mass</th><th>Allocation</th></tr>';
      for (const s of mc.subsystems) h += '<tr><td>' + esc(s.subsystem) + '</td><td' + (s.alloc_g !== null && s.mass_g > s.alloc_g ? ' class="over"' : '') + '>' +
        M.fmtMass(s.mass_g) + '</td><td>' + M.fmtMass(s.alloc_g) + '</td></tr>';
      h += '</table></section>';
    }
    const miss = [];
    if (mc.no_mass.length) miss.push('No mass: ' + mc.no_mass.join(', '));
    if (mc.no_cg.length) miss.push('No CG: ' + mc.no_cg.join(', '));
    if (!mc.cg_range) miss.push('No CG target (mass_budget.json cg_x_m)');
    h += '<section class="ds-meta">' + (miss.length ? esc(miss.join(' · ')) + '<br>' : '') +
      'Declared masses and CGs from interfaces.json; ground tools excluded. Source: ' + esc(S.data.sources.budget || '—') + '</section>';
    P.innerHTML = h;
  }
  function setCG(on) {
    S.cgOn = on; $('#cg').setAttribute('aria-pressed', on); $('#cgpanel').hidden = !on;
    if (on) renderCGPanel();
    if (G.cg) { G.cg.group.visible = on; if (G.cg.label) G.cg.label.style.display = on ? '' : 'none'; }
    requestRender();
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
    updateHash(); renderTree(); hint();
  }
  function setColour(c) { S.colour = c; pressed('#colours', 'colour', c); applyLook(); }

  // ---------------- selection ----------------
  function select(ref, opts) {
    opts = opts || {};
    if (ref && ref.type === 'part' && !S.idx.parts.has(ref.id)) ref = null;
    if (ref && ref.type === 'edge' && !S.idx.edges.has(ref.id) && !G.joints.has(ref.id) && !G.wires.has(ref.id)) ref = null;
    S.sel = ref;
    if (S.isolated && (!ref || ref.id !== S.isolated)) S.isolated = null;
    applyLook(); renderPanel(); renderTree(true); updateHash();
    if (ref && opts.focus) focusOn(ref);
  }
  function updateHash() {
    const h = [];
    if (S.sel) h.push((S.sel.type === 'part' ? 'part=' : 'edge=') + encodeURIComponent(S.sel.id));
    if (S.mode !== 'whole') h.push('mode=' + S.mode);
    try { history.replaceState(null, '', h.length ? '#' + h.join('&') : location.pathname + location.search); } catch (e) { /* file:// in some browsers */ }
  }

  // ---------------- part browser ----------------
  function renderTree(keepScroll) {
    const T = $('#tree'), top = T.scrollTop, groups = M.tree(S.data, S.query), selId = S.sel ? S.sel.id : null;
    const openState = {}; T.querySelectorAll('details[data-sub]').forEach(d => { openState[d.dataset.sub] = d.open; });
    let h = '';
    for (const g of groups) {
      const open = openState[g.subsystem] !== false;
      h += '<details data-sub="' + esc(g.subsystem) + '"' + (open ? ' open' : '') + '><summary data-sub="' + g.key + '"><i class="sub" style="--sub:' + subCss(g.key) + '"></i>' +
        '<span>' + esc(g.subsystem) + '</span><span class="m">' + M.fmtMass(g.mass_g) + '</span></summary>';
      for (const p of g.parts) {
        const hidden = G.root && G.parts.has(p.id) && roleOf(p.id) === 'hidden';
        h += '<button class="v-row' + (p.in_model === false ? ' nogeo' : '') + (hidden ? ' dim' : '') + '" data-part="' + esc(p.id) + '"' +
          (selId === p.id ? ' aria-current="true"' : '') + ' title="' + esc(p.id + ' ' + (p.name || '') + ' · ' + (p.status || '') + ' · ' + M.fmtMass(p.mass_g)) + '">' +
          '<i class="sub" style="--sub:' + subCss(M.subKey(p.id)) + '"></i><span class="id">' + esc(p.id) + '</span><span class="nm">' + esc(p.name || '') + '</span>' +
          '<i class="st" data-status="' + esc(p.status) + '" title="' + esc(p.status) + '"></i></button>';
      }
      h += '</details>';
    }
    // wiring: edges that are wires, so Inside & wiring has a list too
    const wires = (S.data.edges || []).filter(e => M.edgeKind(e, S.idx) === 'wire' && M.matches({ id: e.id, name: (e.wire || {}).connector, material: e.via }, S.query));
    if (wires.length) {
      const open = openState['(wiring)'] === true;
      h += '<details data-sub="(wiring)"' + (open ? ' open' : '') + '><summary><i class="sub" style="--sub:' + subCss('HRN') + '"></i><span>wiring</span><span class="m">' + wires.length + '</span></summary>';
      for (const e of wires) h += '<button class="v-row" data-edge="' + esc(e.id) + '"' + (selId === e.id ? ' aria-current="true"' : '') + '><i></i><span class="id">' + esc(e.id) +
        '</span><span class="nm">' + esc(e.part_a + ' → ' + e.part_b) + '</span><i></i></button>';
      h += '</details>';
    }
    T.innerHTML = h || '<div class="v-empty">' + (S.query ? 'No part matches “' + esc(S.query) + '”.' : 'No parts in this dataset yet.') + '</div>';
    if (keepScroll) T.scrollTop = top;
    const cur = T.querySelector('[aria-current="true"]');
    if (cur) cur.scrollIntoView({ block: 'nearest' });
  }
  const subCss = k => k === 'OTHER' ? 'var(--fg-3)' : 'var(--sub-' + k.toLowerCase() + ')';

  // ---------------- part panel ----------------
  const badge = s => s ? '<span class="ds-badge" data-status="' + esc(s) + '">' + esc(s) + '</span>' : '';
  const partLink = id => { const p = S.idx.parts.get(id);
    return '<button class="v-link" data-part="' + esc(id) + '" style="--sub:' + subCss(M.subKey(id)) + '"><i></i>' + esc(id) + (p && p.name ? ' ' + esc(p.name) : '') + '</button>'; };
  function kv(rows) { return '<dl class="ds-kv">' + rows.map(([k, v]) => '<dt>' + esc(k) + '</dt><dd>' + v + '</dd>').join('') + '</dl>'; }
  function claimHtml(c) {
    const val = c.value === null || c.value === undefined ? '—' : (typeof c.value === 'number' ? M.fmtNum(c.value, Math.abs(c.value) < 10 ? 2 : 1) : esc(c.value));
    const unit = c.unit && c.unit !== '-' ? ' ' + esc(c.unit) : '';
    return '<li class="v-claim"><div><a class="v-link" href="' + esc(M.fill(S.data.proofs_viewer, c.id)) + '" target="_blank" rel="noopener">' + esc(c.title || c.id) + '</a>' +
      '<div class="val">' + esc(c.id) + ' · ' + val + unit + (c.limit ? ' (limit ' + esc(M.limitText(c.limit)) + unit + ')' : '') + '</div>' +
      (c.how ? '<div class="how">Verify: ' + esc(c.how) + '</div>' : '') + '</div>' + badge(c.status) + '</li>';
  }
  function renderPanel() {
    const I = $('#inspector');
    if (!S.sel) { I.innerHTML = summaryHtml(); return; }
    if (S.sel.type === 'edge') { I.innerHTML = edgeHtml(S.sel.id); return; }
    const id = S.sel.id, p = S.idx.parts.get(id), k = M.subKey(id), ifs = M.interfacesOf(id, S.idx), claims = S.idx.claimsByPart.get(id) || [];
    const e = G.parts.get(id);
    const nums = [['Mass', M.fmtMass(p.mass_g)], ['Material', esc(p.material || '—')],
      ['Make / buy', esc(p.make_or_buy || '—') + (typeof p.unit_cost_usd === 'number' ? ' · $' + M.fmtNum(p.unit_cost_usd, 2) : '')],
      ['Vendor / file', esc(p.vendor || '—')]];
    if (p.qty && p.qty !== 1) nums.push(['Qty', M.fmtNum(p.qty)]);
    if (p.process) nums.push(['Process', esc(p.process)]);
    nums.push(['CG x y z', Array.isArray(p.cg_xyz_m) ? p.cg_xyz_m.map(v => M.fmtNum(v, 3)).join(', ') + ' m' : '—']);
    if (p.electrical) nums.push(['Electrical', esc(p.electrical)]);
    if (!e) nums.push(['3-D model', 'no geometry']);
    let h = '<article class="ds-part" data-sub="' + k + '" style="--sub:' + subCss(k) + '"><header><div class="id"><i class="sub"></i>' + esc(id) + ' · ' + esc(p.subsystem || '') +
      (p.csv_ref ? ' · ' + esc(p.csv_ref.replace(/^redesign\//, '')) : '') + '</div><div class="name">' + esc(p.name || id) + ' ' + badge(p.status) + '</div></header>' +
      '<section><h3>Numbers</h3>' + kv(nums) + (p.notes ? '<p class="ds-meta" style="margin:6px 0 0">' + esc(p.notes) + '</p>' : '') + '</section>';
    h += '<section><h3>Interfaces (' + ifs.length + ')</h3>' + (ifs.length ? '<ul class="ds-iface v-iface">' + ifs.map(f => ifaceHtml(f, id)).join('') + '</ul>' : '<p class="ds-meta" style="margin:0">None declared. A part with no interface floats.</p>') + '</section>';
    h += '<section><h3>Claims about this part (' + claims.length + ')</h3>' + (claims.length ? '<ul class="ds-iface">' + claims.map(claimHtml).join('') + '</ul>' : '<p class="ds-meta" style="margin:0">No proof-chain claim names this part.</p>') + '</section>';
    h += '<section class="ds-row"><button class="ds-btn primary" data-act="focus"' + (e ? '' : ' disabled') + '>Focus</button>' +
      '<button class="ds-btn" data-act="isolate"' + (e ? '' : ' disabled') + '>' + (S.isolated === id ? 'Show all' : 'Isolate') + '</button>' +
      (p.spec ? '<a class="ds-btn" href="' + esc(p.spec) + '" target="_blank" rel="noopener">Open SPEC</a>' : '<button class="ds-btn" disabled title="No SPEC.md for this subsystem yet">Open SPEC</button>') + '</section></article>';
    $('#inspector').innerHTML = h;
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
    if (!e) {  // in the model but not in interfaces.json
      const u = (j || w).node.userData;
      return '<article class="ds-part"><header><div class="id">' + esc(id) + '</div><div class="name">' + esc(u.kind || 'joint') + '</div></header><section>' +
        kv(Object.entries(u).map(([a, b]) => [a, esc(typeof b === 'object' ? JSON.stringify(b) : b)])) + '</section></article>';
    }
    const f = M.interfacesOf(e.part_a, S.idx).find(x => x.edge.id === id) || { rows: [], kind: M.edgeKind(e, S.idx), spec: e.via };
    return '<article class="ds-part"><header><div class="id">' + esc(id) + ' · owner ' + esc(e.owner || '—') + '</div><div class="name">' + esc(f.spec) + ' <span class="ds-meta">' + esc(f.kind) + '</span></div></header>' +
      '<section><h3>Between</h3><ul class="ds-iface"><li>' + partLink(e.part_a) + '</li><li>' + partLink(e.part_b) + '</li></ul></section>' +
      (f.rows.length ? '<section><h3>' + (e.joint_stack ? 'Joint stack' : e.wire ? 'Wire installation' : 'Motion') + '</h3>' + kv(f.rows.map(([a, b]) => [a, esc(b)])) + '</section>' : '') +
      (e.notes ? '<section class="ds-meta">' + esc(e.notes) + '</section>' : '') +
      '<section class="ds-row"><button class="ds-btn primary" data-act="focus">Focus</button></section></article>';
  }
  function summaryHtml() {
    const d = S.data, mc = M.massCG(d), by = {};
    for (const p of d.parts) by[p.status] = (by[p.status] || 0) + 1;
    const title = d.dataset === 'examples' ? 'Generic test aircraft' : 'Aircraft';
    return '<div class="ds-panel v-summary"><h2>' + title + '</h2><p>' + (d.dataset === 'examples' ? 'A demo of the viewer, not a design. ' : '') +
      'Click a part to see its numbers, interfaces and claims. Double-click to focus.</p>' +
      '<div class="ds-row">' + M.STATUSES.filter(s => by[s]).map(s => badge(s) + '<span class="ds-meta ds-mono">' + by[s] + '</span>').join(' ') + '</div>' +
      kv([['Parts', M.fmtNum(d.parts.length)], ['Mass', M.fmtMass(mc.total_g)], ['CG x', mc.cg ? M.fmtNum(mc.cg[0], 3) + ' m' : '—'],
        ['Interfaces', M.fmtNum(d.edges.length)], ['Claims', M.fmtNum(d.claims.length)], ['Built', esc(d.generated)]]) +
      '<div class="v-keys"><span class="ds-kbd">1</span>Whole<span class="ds-kbd">2</span>Inside &amp; wiring<span class="ds-kbd">3</span>Structure<span class="ds-kbd">4</span>Exploded' +
      '<span class="ds-kbd">M</span>Measure<span class="ds-kbd">C</span>Mass / CG<span class="ds-kbd">F</span>Focus selected<span class="ds-kbd">Esc</span>Clear</div>' +
      '<p class="ds-source">' + esc([d.sources.interfaces, d.sources.glb, d.sources.proofs].filter(Boolean).join(' · ')) + '</p></div>';
  }

  // ---------------- legend, hint, header ----------------
  function renderLegend() {
    const L = $('#legend'); let items = [];
    if (S.colour === 'status') {
      const by = {}; for (const p of S.data.parts) if (G.parts.has(p.id)) by[p.status] = (by[p.status] || 0) + 1;
      items = M.STATUSES.map(s => [G.colours.css.status(s), s + ' ' + (by[s] || 0)]);
    } else if (S.colour === 'subsystem') {
      const seen = new Map(); for (const p of S.data.parts) if (G.parts.has(p.id)) { const k = M.subKey(p.id); if (!seen.has(k)) seen.set(k, new Set()); seen.get(k).add(p.subsystem); }
      items = [...seen].map(([k, s]) => [subCss(k), [...s].join(', ')]);
    } else {
      const seen = new Map();
      for (const [id, e] of G.parts) { const hex = '#' + e.meshes[0].userData.origColor.getHexString(THREE.SRGBColorSpace), mat = (S.idx.parts.get(id) || {}).material || '';
        if (!seen.has(hex)) seen.set(hex, new Set()); seen.get(hex).add(mat.replace(/\s*\(bought\)/, '')); }
      items = [...seen].map(([hex, s]) => [hex, [...s][0] + (s.size > 1 ? ' +' + (s.size - 1) : '')]);
    }
    if (S.mode === 'inside') items.push(['var(--fg-3)', 'ghost: not electrical']);
    L.innerHTML = items.map(([c, t]) => '<span><i style="--c:' + c + '"></i>' + esc(t) + '</span>').join('');
  }
  function hint() {
    $('#hint').textContent = S.measuring ? (G.measure.pts.length === 1 ? 'Click the second point · Esc to stop' : 'Click two points on the model · Esc to stop')
      : S.view === 'persp' ? 'Drag to rotate · right-drag to pan · scroll to zoom · double-click to focus' : 'Drag to pan · scroll to zoom · 3-D to rotate again';
  }
  function renderHeader() {
    const d = S.data, mc = M.massCG(d);
    $('#dataset').textContent = d.dataset;
    $('#counts').textContent = M.fmtNum(d.parts.length) + ' parts · ' + M.fmtMass(mc.total_g) + ' · ' + M.fmtNum(d.edges.length) + ' interfaces · ' + M.fmtNum(d.claims.length) + ' claims';
    const W = $('#warnings');
    if (d.warnings && d.warnings.length) {
      W.hidden = false; W.querySelector('summary').textContent = d.warnings.length + ' data warning' + (d.warnings.length > 1 ? 's' : '');
      W.querySelector('ul').innerHTML = d.warnings.map(w => '<li>' + esc(w) + '</li>').join('');
    }
  }

  // ---------------- events ----------------
  function wire() {
    $('#modes').addEventListener('click', ev => { const b = ev.target.closest('button[data-mode]'); if (b) setMode(b.dataset.mode); });
    $('#colours').addEventListener('click', ev => { const b = ev.target.closest('button[data-colour]'); if (b) setColour(b.dataset.colour); });
    $('#views').addEventListener('click', ev => { const b = ev.target.closest('button[data-view]'); if (b && G.root) setView(b.dataset.view); });
    $('#fit').addEventListener('click', () => G.root && fit(visibleBox()));
    $('#measure').addEventListener('click', () => setMeasuring(!S.measuring));
    $('#cg').addEventListener('click', () => setCG(!S.cgOn));
    $('#explode-range').addEventListener('input', ev => { setExplode(ev.target.value / 100); applyLook(); });
    $('#explode-play').addEventListener('click', async () => { await explodeTo(0, 350); await explodeTo(1, 1100); });
    $('#search').addEventListener('input', ev => { S.query = ev.target.value.trim(); renderTree(); });
    $('#search').addEventListener('keydown', ev => {
      if (ev.key === 'Enter') { const b = $('#tree [data-part]'); if (b) select({ type: 'part', id: b.dataset.part }, { focus: true }); }
      if (ev.key === 'Escape') { ev.target.value = ''; S.query = ''; renderTree(); ev.target.blur(); }
    });
    document.addEventListener('click', ev => {
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
      down = null; const hit = pick(ev);
      if (S.measuring) measureClick(hit); else select(hit ? hit.ref : null);
    });
    cv.addEventListener('dblclick', ev => { if (!G.root || S.measuring) return; const hit = pick(ev); if (hit) select(hit.ref, { focus: true }); else fit(visibleBox()); });
    document.addEventListener('keydown', ev => {
      if (ev.target.closest('input, textarea') || ev.ctrlKey || ev.metaKey || ev.altKey) return;
      const k = ev.key;
      if (k >= '1' && k <= '4') setMode(M.MODES[+k - 1]);
      else if (k === 'm' || k === 'M') setMeasuring(!S.measuring);
      else if (k === 'c' || k === 'C') setCG(!S.cgOn);
      else if ((k === 'f' || k === 'F') && S.sel) focusOn(S.sel);
      else if (k === 'Home') fit(visibleBox());
      else if (k === '/') { ev.preventDefault(); $('#search').focus(); }
      else if (k === 'Escape') { if (S.measuring) setMeasuring(false); else if (S.isolated) { S.isolated = null; applyLook(); renderPanel(); } else select(null); }
      else return;
    });
    $('#theme').addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark'; document.documentElement.setAttribute('data-theme', next); store.set('theme', next); themeChanged();
    });
    if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', themeChanged);
    window.addEventListener('hashchange', () => { const h = M.parseHash(location.hash); if (h.mode) setMode(h.mode);
      if (h.part && (!S.sel || S.sel.id !== h.part)) select({ type: 'part', id: h.part }, { focus: true }); });
  }
  function themeChanged() { readColours(); if (G.root) { buildCG(); setCG(S.cgOn); applyLook(); } }

  // ---------------- start ----------------
  async function main() {
    const t = new URLSearchParams(location.search).get('theme') || store.get('theme');
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
    readColours(); wire(); hint();
    progress(0, 'reading data');
    const r = await loadData();
    if (r.error) { loadFailed('No data', esc(r.error)); return; }
    if (r.note) { $('#note').innerHTML = r.note; $('#note').hidden = false; }
    S.data = r.d; S.idx = M.index(S.data);
    renderHeader(); renderTree(); renderPanel();   // usable before the geometry arrives
    if (!S.data.glb) {
      loadFailed('No 3-D model yet', 'Export it, then rebuild the viewer data:<br><code class="ds-inline">B redesign/blender/export_glb.py</code><br>' +
        '<code class="ds-inline">python -I redesign/viewer/build_data.py</code><br><a class="ds-link" href="?data=examples">Open the example aircraft</a>');
      return;
    }
    if (!initThree()) { loadFailed('3-D is not available', 'This browser could not start WebGL. The part list and panel still work.'); return; }
    let buf;
    try { buf = await fetchGlb('data/' + S.data.dataset + '/' + S.data.glb.file, S.data.glb.bytes); }
    catch (e) { loadFailed('Model not found', esc(e.message) + '<br>Run <code class="ds-inline">python -I redesign/viewer/build_data.py</code>.'); return; }
    progress(1, 'building scene');
    let gltf;
    try { gltf = await new Promise((res, rej) => new X.GLTFLoader().parse(buf, '', res, rej)); }
    catch (e) { loadFailed('Model could not be read', esc(e.message || e)); return; }
    buildModel(gltf);
    try { await G.renderer.compileAsync(G.scene, G.camera); } catch (e) { /* older drivers: compile on first frame */ }
    buildCG(); applyLook();
    const h = M.parseHash(location.hash);
    if (h.mode) await setMode(h.mode);
    G.persp.position.copy(ISO).multiplyScalar(G.size * 3); G.controls.target.copy(G.box.getCenter(new THREE.Vector3()));
    await setView('persp', 0);
    renderTree(true);
    $('#loading').classList.add('done');
    if (h.part) select({ type: 'part', id: h.part }, { focus: true });
    else if (h.edge) select({ type: 'edge', id: h.edge }, { focus: true });
  }
  main();
})();
