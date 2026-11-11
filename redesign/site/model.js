// Pure logic of the aircraft explorer (no DOM, no three.js): ES-module copy of redesign/viewer/model.js.
// Only change: subKey() maps the K09-L part-id prefixes (FIN, POD, PRP, MEC, GER ...) onto the design-system hues.
const STATUSES = ['PROPOSED', 'MODELLED', 'CHECKED', 'VERIFIED'];
const MODES = ['whole', 'inside', 'structure', 'exploded'];
// part-id prefix -> design-system subsystem key (tokens.css --sub-*); BRIEF.md lists the prefixes
const PREFIXES = ['WNG', 'FUS', 'BMS', 'TAL', 'GER', 'PSH', 'PWR', 'HRN', 'AVN'];
// K09-L prefixes (BRIEF.md) -> hue keys: fins on the booms hue, pod on the fuselage hue, mechanisms on the tail hue
const PREFIX_MAP = { WNG: 'WNG', FIN: 'BMS', BMS: 'BMS', POD: 'FUS', FUS: 'FUS', MEC: 'TAL', TAL: 'TAL', GER: 'GER', PRP: 'PSH', PSH: 'PSH', PWR: 'PWR', HRN: 'HRN', AVN: 'AVN' };

const subKey = id => PREFIX_MAP[String(id || '').split('-')[0].toUpperCase()] || 'OTHER';

// aircraft frame (x aft, y right, z up) <-> glTF (+Y up): glTF (x, y, z) = aircraft (x, z, -y)
const ac2gl = v => [v[0], v[2], -v[1]];
const gl2ac = v => [v[0], -v[2], v[1]];
const AXIS_AC = { X: [1, 0, 0], Y: [0, 1, 0], Z: [0, 0, 1] };

// ---------- formatting (design system: units with a space, thin-space thousands, unknown is an em dash) ----------
const group = s => s.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
function fmtNum(v, digits) {
  if (v === null || v === undefined || Number.isNaN(v)) return '—';
  const s = Number(v).toFixed(digits === undefined ? 0 : digits);
  const [i, f] = s.split('.');
  return group(i) + (f ? '.' + f : '');
}
const fmtMass = g => g === null || g === undefined ? '—' : (Math.abs(g) >= 10000 ? fmtNum(g / 1000, 2) + ' kg' : fmtNum(g, g < 10 ? 1 : 0) + ' g');
const fmtLen = m => m === null || m === undefined ? '—' : fmtNum(m * 1000, Math.abs(m) < 0.1 ? 1 : 0) + ' mm';

// ---------- index ----------
function index(data) {
  const parts = new Map(), edgesByPart = new Map(), claimsByPart = new Map(), edges = new Map();
  for (const p of data.parts || []) { parts.set(p.id, p); edgesByPart.set(p.id, []); claimsByPart.set(p.id, []); }
  for (const e of data.edges || []) {
    edges.set(e.id, e);
    for (const id of [e.part_a, e.part_b]) if (edgesByPart.has(id)) edgesByPart.get(id).push(e);
  }
  for (const c of data.claims || []) for (const id of c.parts || []) if (claimsByPart.has(id)) claimsByPart.get(id).push(c);
  return { data, parts, edges, edgesByPart, claimsByPart, ctypes: data.connection_types || {} };
}

// what an edge is, from its connection type: 'wire' | 'hinge' | 'bond' | 'fastened' | 'other'
function edgeKind(e, idx) {
  const ct = idx.ctypes[e.via] || {};
  if (e.wire || ct.kind === 'electrical') return 'wire';
  if (e.motion || ct.method === 'hinged') return 'hinge';
  if (ct.method === 'bonded') return 'bond';
  if (ct.method === 'fastened' || e.joint_stack) return 'fastened';
  return ct.method || 'other';   // strapped, taped, clamped, press_fit, ...
}

// Load-carrying part (Structure mode). An explicit `structural: true|false` on the part wins (CHANGE-REQUESTS #2).
// Otherwise: a flight part that is not electrical and has at least one mechanical edge that is not a hinge
// (so a control surface on its hinge, the battery, ESC, servos and motors are not structure).
function isStructural(p, idx) {
  if (typeof p.structural === 'boolean') return p.structural;
  if (p.flight === false || p.electrical) return false;
  return (idx.edgesByPart.get(p.id) || []).some(e => { const k = edgeKind(e, idx); return k !== 'wire' && k !== 'hinge'; });
}

// How a part is drawn in a mode: 'solid' | 'ghost' | 'hidden'. Wires and joint markers: see showWires/showJoints.
// Harness bundle bodies (HRN-001, HRN-002-x) are lumped-mass proxies placed for the mass/CG roll-up; the real wires
// are drawn as routed tubes, so the proxies are never drawn (they stay in the part list and the mass totals).
const isMassProxy = p => !!p.mass_proxy || /^HRN-00[12]/.test(p.id || '');
function role(mode, p, idx) {
  if (isMassProxy(p)) return 'hidden';
  if (mode === 'inside') return p.electrical ? 'solid' : 'ghost';
  if (mode === 'structure') return isStructural(p, idx) ? 'solid' : 'hidden';
  return 'solid';
}
const showWires = mode => mode === 'whole' || mode === 'inside';
const showJoints = mode => false;   // joint markers show only for the selected part (viewer.js applyLook)

// ---------- part browser ----------
function matches(p, q) {
  if (!q) return true;
  const hay = [p.id, p.name, p.material, p.vendor, p.status, p.subsystem, p.make_or_buy].join(' ').toLowerCase();
  return q.toLowerCase().split(/\s+/).filter(Boolean).every(w => hay.includes(w));
}
// [{subsystem, key, parts, mass_g}] sorted by subsystem name, parts by id; empty groups dropped
function tree(data, query) {
  const groups = new Map();
  for (const p of data.parts || []) {
    if (!matches(p, query)) continue;
    const s = p.subsystem || '(none)';
    if (!groups.has(s)) groups.set(s, { subsystem: s, key: subKey(p.id), parts: [], mass_g: 0 });
    const g = groups.get(s); g.parts.push(p); g.mass_g += (p.flight === false ? 0 : p.mass_g || 0);
  }
  const out = [...groups.values()].sort((a, b) => a.subsystem.localeCompare(b.subsystem));
  out.forEach(g => g.parts.sort((a, b) => a.id.localeCompare(b.id)));
  return out;
}

// ---------- mass and CG (declared values from interfaces.json; ground tools excluded) ----------
function massCG(data) {
  const flight = (data.parts || []).filter(p => p.flight !== false);
  let m = 0, mx = 0, my = 0, mz = 0, mcg = 0;
  const noMass = [], noCG = [], bySub = {};
  for (const p of flight) {
    if (typeof p.mass_g !== 'number') { noMass.push(p.id); continue; }
    m += p.mass_g; bySub[p.subsystem] = (bySub[p.subsystem] || 0) + p.mass_g;
    if (!Array.isArray(p.cg_xyz_m)) { noCG.push(p.id); continue; }
    mcg += p.mass_g; mx += p.mass_g * p.cg_xyz_m[0]; my += p.mass_g * p.cg_xyz_m[1]; mz += p.mass_g * p.cg_xyz_m[2];
  }
  const b = data.budget || {};
  const cg = mcg > 0 ? [mx / mcg, my / mcg, mz / mcg] : null;
  const range = Array.isArray(b.cg_x_m) ? b.cg_x_m : null;
  const inRange = cg && range ? cg[0] >= range[0] && cg[0] <= range[1] : null;
  // margin to the nearest end of the CG range (m); negative = outside
  const margin = cg && range ? Math.min(cg[0] - range[0], range[1] - cg[0]) : null;
  const subs = Object.keys(bySub).sort().map(s => ({ subsystem: s, mass_g: bySub[s],
    alloc_g: b.allocations_g ? b.allocations_g[s] ?? null : null }));
  return { total_g: m, count: flight.length, cg, limit_g: typeof b.limit_g === 'number' ? b.limit_g : null,
    cg_range: range, in_range: inRange, margin_m: margin, no_mass: noMass, no_cg: noCG, subsystems: subs };
}

// ---------- hardware (fasteners view) ----------
// A part is hardware when its name (before any ':' and without parentheses) names a screw, bolt, nut, washer, insert or spacer.
// So "Power frame: deck on 4 spacers", "Field pouch (... spare prop nuts ...)" and the spare landing inserts are not hardware.
const HW_RE = /screw|bolt|\bnuts?\b|washer|insert|spacer|nyloc|SHCS|pan head/i;
function isHardware(p) {
  if (!p) return false;
  const head = String(p.name || '').replace(/\([^)]*\)/g, '').split(':')[0];
  return HW_RE.test(head) && !/^\s*spare\b/i.test(head);
}
// type of a hardware part, from its name
function hardwareType(p) {
  const n = String(p.name || '').split(':')[0];
  if (/adapter/i.test(n) && !/screw/i.test(n)) return 'Prop adapter kit';
  if (/insert/i.test(n)) return 'Heat-set insert';
  if (/spacer/i.test(n)) return 'Spacer';
  if (/washer/i.test(n)) return 'Washer';
  if (/\bnuts?\b|nyloc/i.test(n)) return 'Nut';
  return 'Screw / bolt';
}
// pieces in one part record: "Motor screw set: 4 x M3x8" -> 4, "2 x (M3x16 ...)" -> 2, otherwise 1
const hardwarePieces = p => { const m = String(p.name || '').match(/:\s*(\d+)\s*x\s/i); return m ? +m[1] : 1; };
// summary rows [{type, material, parts, pieces, mass_g}] + totals (flight hardware only in the mass; ground hardware counted separately)
function hardwareSummary(data) {
  const hw = (data.parts || []).filter(isHardware), rows = new Map();
  let mass = 0, groundMass = 0, pieces = 0;
  for (const p of hw) {
    const t = hardwareType(p), mat = p.material || '—', k = t + '|' + mat, n = hardwarePieces(p);
    if (!rows.has(k)) rows.set(k, { type: t, material: mat, parts: 0, pieces: 0, mass_g: 0, ground: true });
    const r = rows.get(k); r.parts++; r.pieces += n; r.mass_g += p.mass_g || 0; if (p.flight !== false) r.ground = false;
    pieces += n; if (p.flight === false) groundMass += p.mass_g || 0; else mass += p.mass_g || 0;
  }
  const order = ['Screw / bolt', 'Nut', 'Washer', 'Heat-set insert', 'Spacer', 'Prop adapter kit'];
  const out = [...rows.values()].sort((a, b) => order.indexOf(a.type) - order.indexOf(b.type) || a.material.localeCompare(b.material));
  return { parts: hw, rows: out, pieces, mass_g: mass, ground_mass_g: groundMass };
}

// ---------- part panel helpers ----------
const JOINT_FIELDS = [['fastener', 'Fastener'], ['count', 'Count'], ['grade', 'Grade'], ['hole', 'Hole'], ['insert', 'Insert'],
  ['engagement_mm', 'Engagement (mm)'], ['min_engagement_mm', 'Min engagement (mm)'], ['washer_nut', 'Washer / nut'],
  ['torque', 'Torque'], ['tool', 'Tool'], ['access', 'Access'], ['install_order', 'Install order'], ['removal_order', 'Removal order']];
const WIRE_FIELDS = [['gauge_awg', 'Gauge (AWG)'], ['connector', 'Connector'], ['route_id', 'Route'], ['support_points', 'Supports'],
  ['bend_radius_mm', 'Bend radius (mm)'], ['strain_relief', 'Strain relief'], ['disconnect', 'Disconnect'], ['slack_mm', 'Slack (mm)']];
function rows(obj, fields) {
  if (!obj) return [];
  return fields.filter(([k]) => obj[k] !== undefined && obj[k] !== null && obj[k] !== '')
    .map(([k, label]) => [label, Array.isArray(obj[k]) ? obj[k].join('; ') : obj[k] === true ? 'yes' : obj[k] === false ? 'no' : String(obj[k])]);
}
// the interfaces of one part, for the panel: [{edge, other, kind, spec, rows}]
function interfacesOf(id, idx) {
  return (idx.edgesByPart.get(id) || []).map(e => {
    const ct = idx.ctypes[e.via] || {};
    const other = e.part_a === id ? e.part_b : e.part_a;
    const r = e.joint_stack ? rows(e.joint_stack, JOINT_FIELDS) : e.wire ? rows(e.wire, WIRE_FIELDS)
      : e.motion ? [['Axis', e.motion.axis], ['Range (deg)', (e.motion.range_deg || []).join(' to ')]] : [];
    if (e.joint_stack && e.joint_stack.engagement_mm < e.joint_stack.min_engagement_mm) r.unshift(['Check', 'FAIL: engagement below minimum']);
    return { edge: e, other, otherPart: idx.parts.get(other) || null, kind: edgeKind(e, idx), spec: ct.spec || e.via, rows: r };
  }).sort((a, b) => a.edge.id.localeCompare(b.edge.id));
}
const fill = (tpl, id) => (tpl || '').replace('{id}', encodeURIComponent(id));
// a claim's limit as text: "<= 5.5"
const limitText = l => !l ? '' : (l.op || '') + ' ' + (l.resolved !== undefined && l.resolved !== null ? fmtNum(l.resolved, 3).replace(/\.?0+$/, '') : l.ref || '');

// #part=WNG-003&mode=inside  ->  {part: 'WNG-003', mode: 'inside'}
function parseHash(h) {
  const out = {};
  for (const kv of String(h || '').replace(/^#/, '').split('&')) {
    const [k, v] = kv.split('=');
    if (k && v !== undefined) out[decodeURIComponent(k)] = decodeURIComponent(v);
  }
  if (out.mode && !MODES.includes(out.mode)) delete out.mode;
  return out;
}

export const api = { STATUSES, MODES, PREFIXES, subKey, ac2gl, gl2ac, AXIS_AC, fmtNum, fmtMass, fmtLen, index, edgeKind,
  isStructural, role, showWires, showJoints, matches, tree, isHardware, hardwareType, hardwarePieces, hardwareSummary, massCG, interfacesOf, fill, limitText, parseHash };
export default api;
