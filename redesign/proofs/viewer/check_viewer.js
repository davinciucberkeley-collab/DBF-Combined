// Headless check of the viewer, no browser needed:  node redesign/proofs/viewer/check_viewer.js
// 1. every built graph (out/graph.js, examples/out/graph.js) parses and is consistent;
// 2. the viewer's pure logic (model.js) finds the expected chains in the demo graph;
// 3. index.html / app.js reference only files and element ids that exist, and app.js parses.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const HERE = __dirname, M = require('./model.js');
let failures = 0;
const ok = (cond, msg) => { if (!cond) { failures++; console.error('  FAIL', msg); } };

function loadGraphJs(file) {
  const sandbox = { window: {} };
  vm.runInNewContext(fs.readFileSync(file, 'utf8'), sandbox, { filename: file });
  return sandbox.window.PROOF_GRAPH;
}

function checkGraph(file, expectClaims) {
  if (!fs.existsSync(file)) { console.log('  (not built)', path.relative(HERE, file)); return null; }
  const g = loadGraphJs(file), ids = new Set();
  ok(g && Array.isArray(g.nodes) && Array.isArray(g.edges), file + ': nodes/edges arrays');
  const json = JSON.parse(fs.readFileSync(file.replace(/graph\.js$/, 'graph.json'), 'utf8'));
  ok(JSON.stringify(json) === JSON.stringify(g), 'graph.js and graph.json hold the same data');
  for (const n of g.nodes) {
    ok(!ids.has(n.id), 'duplicate id ' + n.id); ids.add(n.id);
    ok(M.TYPES.includes(n.type), n.id + ': type ' + n.type);
    ok(M.STATUSES.includes(n.status), n.id + ': status ' + n.status);
    if (n.type === 'claim') ok(n.value !== undefined, n.id + ': claim has a value');
  }
  for (const e of g.edges) ok(ids.has(e.source) && ids.has(e.target), `edge ${e.source} -> ${e.target} has both ends`);
  if (expectClaims) {
    ok(g.meta.ok === true, 'build ok');
    ok(g.nodes.some(n => n.type === 'claim'), 'has claims');
  }
  console.log(`  ${path.relative(HERE, file)}: ${g.nodes.length} nodes, ${g.edges.length} edges, ok=${g.meta.ok}`);
  return g;
}

console.log('graphs');
checkGraph(path.join(HERE, '..', 'out', 'graph.js'), false);
const demo = checkGraph(path.join(HERE, '..', 'examples', 'out', 'graph.js'), true);

console.log('model.js on the demo graph');
if (demo) {
  const m = M.build(demo);
  const ch = M.chain(m, 'R-EX-HOVER');
  ok(ch.has('CL-EX-HOVER-TW') && ch.has('CALC-EX-HOVER-TW') && ch.has('P:propulsion.thrust_table') && ch.has('SRC-EX-X4110S'),
    'R-EX-HOVER chain reaches the thrust table source');
  ok(!ch.has('CL-EX-STALL'), 'R-EX-HOVER chain does not pull in the stall claim');
  const up = M.pathsUp(m, 'SRC-EX-X4110S').filter(p => m.byId.get(p[p.length - 1]).type === 'requirement');
  ok(up.some(p => p[p.length - 1] === 'R-EX-HOVER'), 'thrust-table source has a path up to R-EX-HOVER');
  ok(M.search(m, 'hover')[0] && M.search(m, 'hover')[0].id.includes('HOVER'), 'search "hover" finds a hover node first');
  const t = M.treeDown(m, 'CL-EX-STALL', 8);
  ok(t.children.length > 0 && t.children.some(c => c.id === 'CALC-EX-STALL'), 'tree under the stall claim starts at its calc');
  const f = { statuses: new Set(['UNVERIFIED']), types: new Set(M.TYPES), failsOnly: false };
  const unv = m.nodes.filter(n => M.visible(n, f)).map(n => n.id);
  ok(unv.includes('CL-EX-STALL') && unv.includes('ASM-EX-CLMAX') && !unv.includes('CL-EX-HOVER-TW'), 'UNVERIFIED filter');
  ok(M.chain(m, 'WNG-003').has('CL-EX-SPAR'), 'a part selects the claims about it');
  ok(M.fmt(2.40769, '-') === '2.408' && M.fmt(26, 'A') === '26 A', 'number formatting matches proofkit.fmt');
  console.log(`  ${m.nodes.length} nodes, UNVERIFIED filter shows ${unv.length}`);
}

console.log('page wiring');
const html = fs.readFileSync(path.join(HERE, 'index.html'), 'utf8'), app = fs.readFileSync(path.join(HERE, 'app.js'), 'utf8');
for (const src of [...html.matchAll(/<script src="([^"]+)"/g)].map(x => x[1])) ok(fs.existsSync(path.join(HERE, src)), 'script exists: ' + src);
for (const lib of [...app.matchAll(/'(vendor\/[^']+\.js)'/g)].map(x => x[1])) ok(fs.existsSync(path.join(HERE, lib)), 'vendored file exists: ' + lib);
for (const id of new Set([...app.matchAll(/\$\('#([\w-]+)'\)/g)].map(x => x[1]))) ok(html.includes(`id="${id}"`), 'element #' + id + ' exists in index.html');
try { new vm.Script(app, { filename: 'app.js' }); } catch (e) { ok(false, 'app.js parses: ' + e.message); }
for (const [lib, ver] of [['3d-force-graph.min.js', '1.80.1'], ['force-graph.min.js', '1.52.0']]) {
  const head = fs.readFileSync(path.join(HERE, 'vendor', lib), 'utf8').slice(0, 120);
  ok(head.includes('Version ' + ver), `vendor/${lib} is version ${ver} (as recorded in vendor/README.md)`);
}
console.log(failures ? `FAILED: ${failures} check(s)` : 'OK: viewer data and wiring check out');
process.exit(failures ? 1 : 0);
