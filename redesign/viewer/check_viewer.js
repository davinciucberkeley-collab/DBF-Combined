// Headless check of the aircraft viewer, no browser needed (~1 s):   node redesign/viewer/check_viewer.js
// 1. the vendored three.js bundle loads and has the add-ons the viewer uses;
// 2. every built dataset (data/*/) is consistent: .js = .json, the base64 copy = the GLB, the GLB parses with
//    three's GLTFLoader and every part with geometry is a node carrying its extras;
// 3. the viewer rules in model.js give the expected answers on the generic test aircraft;
// 4. index.html links only to files that exist, every #id that app.js uses exists, and app.js parses.
// Exit 1 on any FAIL.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const HERE = __dirname;
let failures = 0, checks = 0;
const ok = (cond, msg) => { checks++; if (!cond) { failures++; console.error('  FAIL', msg); } };

// ---------- 1. vendor bundle ----------
console.log('vendor');
globalThis.window = globalThis;          // the bundle and model.js attach to window
require(path.join(HERE, 'vendor', 'three.bundle.js'));
const THREE = globalThis.THREE, X = globalThis.THREE_ADDONS;
ok(THREE && THREE.REVISION, 'THREE loaded');
for (const k of ['GLTFLoader', 'OrbitControls', 'RoomEnvironment']) ok(typeof X[k] === 'function', 'THREE_ADDONS.' + k);
console.log('  three r' + THREE.REVISION + ', add-ons ' + Object.keys(X).filter(k => /^[A-Z]/.test(k)).join(', '));
const M = require(path.join(HERE, 'model.js'));

// ---------- 2. datasets ----------
function loadJsGlobal(file, name) {
  const sb = { window: {} }; vm.runInNewContext(fs.readFileSync(file, 'utf8'), sb, { filename: file });
  return sb.window[name];
}
const parseGlb = buf => new Promise((res, rej) =>
  new X.GLTFLoader().parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.length), '', res, rej));

async function checkDataset(dir) {
  const name = path.basename(dir), js = path.join(dir, 'viewer-data.js');
  if (!fs.existsSync(js)) return null;
  const d = loadJsGlobal(js, 'VIEWER_DATA');
  ok(d && d.schema === 'dbf-viewer/1', name + ': schema');
  ok(JSON.stringify(d) === JSON.stringify(JSON.parse(fs.readFileSync(path.join(dir, 'viewer-data.json'), 'utf8'))), name + ': viewer-data.js = viewer-data.json');
  const ids = new Set(d.parts.map(p => p.id));
  ok(ids.size === d.parts.length, name + ': part ids unique');
  for (const p of d.parts) ok(M.STATUSES.includes(p.status), name + ': ' + p.id + ' status ' + p.status);
  for (const e of d.edges) ok(ids.has(e.part_a) && ids.has(e.part_b), name + ': edge ' + e.id + ' joins known parts');
  for (const c of d.claims) for (const id of c.parts) ok(ids.has(id), name + ': claim ' + c.id + ' part ' + id);
  let nodes = 0;
  if (d.glb) {
    const glb = fs.readFileSync(path.join(dir, d.glb.file));
    ok(glb.length === d.glb.bytes && crypto.createHash('sha256').update(glb).digest('hex') === d.glb.sha256, name + ': GLB size and sha256 match viewer-data');
    const b64 = loadJsGlobal(path.join(dir, d.glb.file + '.js'), 'VIEWER_GLB_B64');
    ok(Buffer.from(b64, 'base64').equals(glb), name + ': assembly.glb.js holds the same bytes');
    const t0 = Date.now(), gltf = await parseGlb(glb), found = new Map();
    gltf.scene.traverse(o => { if (o.userData && o.userData.part_id) found.set(o.userData.part_id, o); });
    nodes = found.size;
    for (const p of d.parts) if (p.in_model) {
      const o = found.get(p.id);
      ok(!!o, name + ': ' + p.id + ' is a node in the GLB');
      if (o) {
        let meshes = 0; o.traverse(m => { if (m.isMesh) meshes++; });
        ok(meshes > 0, name + ': ' + p.id + ' has a mesh');
        ok(Array.isArray(o.userData.explode_m) && o.userData.explode_m.length === 3, name + ': ' + p.id + ' explode_m');
      }
    }
    console.log(`  ${name}: ${d.parts.length} parts, ${nodes} part nodes, ${d.edges.length} edges, ${d.claims.length} claims, GLB ${(glb.length / 1024).toFixed(0)} kB parsed in ${Date.now() - t0} ms, ${d.warnings.length} warnings`);
  } else console.log(`  ${name}: ${d.parts.length} parts, no 3-D model (viewer shows the empty state)`);
  return d;
}

// ---------- 3. model.js rules on the generic test aircraft ----------
function checkModel(d) {
  const idx = M.index(d);
  const by = mode => d.parts.filter(p => M.role(mode, p, idx) === 'solid').map(p => p.id).sort().join(' ');
  ok(by('whole').split(' ').length === d.parts.length, 'whole: every part solid');
  ok(by('inside') === 'BMS-003 BMS-004 FUS-002 FUS-003 WNG-005', 'inside: electrical parts solid, rest ghost (got ' + by('inside') + ')');
  ok(by('structure') === 'BMS-001 BMS-002 FUS-001 WNG-001 WNG-002 WNG-003', 'structure: load-carrying only (got ' + by('structure') + ')');
  ok(M.role('structure', idx.parts.get('WNG-004'), idx) === 'hidden', 'structure: aileron on its hinge is hidden');
  ok(M.isStructural(Object.assign({}, idx.parts.get('FUS-002'), { structural: true }), idx), 'explicit structural flag wins');
  ok(M.showWires('inside') && !M.showWires('structure') && !M.showWires('exploded'), 'wires shown in whole/inside only');
  const mc = M.massCG(d);
  ok(mc.total_g === 1470, 'mass roll-up 1470 g (got ' + mc.total_g + ')');
  const by_hand = i => d.parts.reduce((s, p) => s + p.mass_g * p.cg_xyz_m[i], 0) / 1470, cgx = by_hand(0);
  ok(mc.cg && [0, 1, 2].every(i => Math.abs(mc.cg[i] - by_hand(i)) < 1e-9), 'CG x, y, z = mass-weighted sum by hand');
  ok(mc.in_range === (cgx >= 0.18 && cgx <= 0.24), 'CG range verdict');
  console.log('  mass ' + M.fmtMass(mc.total_g) + ', CG x ' + mc.cg[0].toFixed(4) + ' m, target ' + JSON.stringify(mc.cg_range) + ', in range ' + mc.in_range);
  const t = M.tree(d, '');
  ok(t.map(g => g.subsystem).join() === 'ex_booms,ex_fuselage,ex_wing', 'tree groups by subsystem');
  ok(M.tree(d, 'motor').reduce((n, g) => n + g.parts.length, 0) === 2, 'search "motor" finds 2 parts');
  ok(M.tree(d, 'wng-00 foam').reduce((n, g) => n + g.parts.length, 0) === 3, 'search with two words (AND)');
  const ifs = M.interfacesOf('WNG-003', idx);
  ok(ifs.length === 3 && ifs.some(f => f.edge.id === 'E-WNG-01' && f.kind === 'fastened' && f.rows.some(r => r[0] === 'Fastener')), 'spar interfaces with joint stack');
  ok(M.interfacesOf('FUS-002', idx).some(f => f.kind === 'wire' && f.rows.some(r => r[0] === 'Connector')), 'battery wire installation rows');
  ok((idx.claimsByPart.get('WNG-003') || []).some(c => c.id === 'CL-EX-SPAR'), 'claim CL-EX-SPAR linked to WNG-003');
  ok(JSON.stringify(M.parseHash('#part=WNG-003&mode=inside')) === '{"part":"WNG-003","mode":"inside"}', 'parseHash');
  ok(M.parseHash('#mode=bogus').mode === undefined, 'parseHash drops unknown modes');
  ok(JSON.stringify(M.gl2ac(M.ac2gl([1, 2, 3]))) === '[1,2,3]', 'frame round trip');
  ok(M.fmtMass(1470) === '1 470 g' && M.fmtLen(0.0123) === '12.3 mm', 'formatting');
}

// ---------- 4. page wiring ----------
function checkPage() {
  const html = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8'), app = fs.readFileSync(path.join(HERE, 'app.js'), 'utf8');
  for (const [, ref] of html.matchAll(/(?:src|href)="([^"#:]+)"/g)) {
    if (ref === './') continue;
    ok(fs.existsSync(path.join(HERE, ref)), 'index.html links to ' + ref);
  }
  const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]));
  for (const [, id] of app.matchAll(/\$\('#([\w-]+)/g)) ok(ids.has(id), 'app.js uses #' + id + ', present in index.html');
  try { new vm.Script(app, { filename: 'app.js' }); ok(true); } catch (e) { ok(false, 'app.js parses: ' + e.message); }
  console.log('  index.html: ' + ids.size + ' ids, app.js parses');
}

(async () => {
  console.log('datasets');
  let demo = null;
  const dataDir = path.join(HERE, 'data');
  for (const ds of fs.existsSync(dataDir) ? fs.readdirSync(dataDir).sort() : []) {
    const d = await checkDataset(path.join(dataDir, ds));
    if (ds === 'examples') demo = d;
  }
  ok(!!demo, 'data/examples is built (python -I redesign/viewer/build_data.py --examples)');
  console.log('model.js');
  if (demo) checkModel(demo);
  console.log('page');
  checkPage();
  console.log(failures ? `FAIL: ${failures} of ${checks} checks` : `OK: ${checks} checks`);
  process.exit(failures ? 1 : 0);
})().catch(e => { console.error('FAIL', e); process.exit(1); });
