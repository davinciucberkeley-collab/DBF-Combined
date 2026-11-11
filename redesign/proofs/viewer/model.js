// model.js — pure logic for the proof-chain viewer: no DOM, no WebGL, so check_viewer.js can run it in Node.
// Input: the graph.json written by build_graph.py (format: ../SCHEMA.md). Edges point in the direction evidence
// flows (source -> parameter -> calculation -> claim -> requirement); "about" edges link a claim to a part.
(function (root) {
  'use strict';

  const STATUSES = ['UNVERIFIED', 'PROPOSED', 'CHECKED', 'VERIFIED'];          // worst -> best
  const TYPES = ['requirement', 'claim', 'calculation', 'parameter', 'assumption', 'source', 'test', 'part'];
  const TYPE_LABEL = { requirement: 'Requirement', claim: 'Claim', calculation: 'Calculation', parameter: 'Parameter',
    assumption: 'Assumption', source: 'Source', test: 'Test', part: 'Part' };
  // layer for the "layered" layout and for sorting chains: sources at the bottom, requirements at the top
  const LAYER = { source: 0, assumption: 1, parameter: 1, test: 2, calculation: 2, claim: 3, requirement: 4, part: 4 };

  function build(graph) {
    const nodes = graph.nodes.map(n => Object.assign({}, n));
    const byId = new Map(nodes.map(n => [n.id, n]));
    const into = new Map(), out = new Map();                    // id -> [{node, type}]
    nodes.forEach(n => { into.set(n.id, []); out.set(n.id, []); });
    const edges = [];
    for (const e of graph.edges) {
      if (!byId.has(e.source) || !byId.has(e.target)) continue;
      edges.push({ source: e.source, target: e.target, type: e.type });
      out.get(e.source).push({ id: e.target, type: e.type });
      into.get(e.target).push({ id: e.source, type: e.type });
    }
    return { meta: graph.meta || {}, nodes, edges, byId, into, out };
  }

  // Everything a node rests on (follow edges backwards), excluding part links.
  function upstream(m, id) { return walk(m, id, m.into, e => e.type !== 'about'); }
  // Everything that rests on the node (follow edges forwards to claims and requirements).
  function downstream(m, id) { return walk(m, id, m.out, e => e.type !== 'about'); }

  function walk(m, id, adj, ok) {
    const seen = new Set(), stack = [id];
    while (stack.length) {
      const cur = stack.pop();
      for (const e of adj.get(cur) || []) if (ok(e) && !seen.has(e.id)) { seen.add(e.id); stack.push(e.id); }
    }
    return seen;
  }

  // Chain set for highlighting: the node, what it rests on, what rests on it, and (for a part) its claims' chains.
  function chain(m, id) {
    const s = new Set([id]);
    if (m.byId.get(id) && m.byId.get(id).type === 'part') {
      for (const e of m.into.get(id)) { s.add(e.id); upstream(m, e.id).forEach(x => s.add(x)); downstream(m, e.id).forEach(x => s.add(x)); }
      return s;
    }
    upstream(m, id).forEach(x => s.add(x));
    downstream(m, id).forEach(x => s.add(x));
    for (const e of m.out.get(id) || []) if (e.type === 'about') s.add(e.id);
    return s;
  }

  // Paths from a node up to each requirement it supports: [[id, ..., R-id], ...] — the shortest path to each of the
  // nearest requirements (breadth-first over the evidence edges), at most 8.
  function pathsUp(m, id) {
    const parent = new Map([[id, null]]), res = [];
    let frontier = [id];
    while (frontier.length && res.length < 8) {
      const next = [];
      for (const cur of frontier) for (const e of m.out.get(cur) || []) {
        if (e.type === 'about' || parent.has(e.id)) continue;
        parent.set(e.id, cur);
        if (m.byId.get(e.id).type === 'requirement') {
          const p = [e.id];
          for (let x = cur; x !== null; x = parent.get(x)) p.unshift(x);
          if (res.length < 8) res.push(p);
        } else next.push(e.id);
      }
      frontier = next;
    }
    return res;
  }

  // Tree of what a node rests on, for the detail panel: {id, edge, arg, children[], repeat}
  function treeDown(m, id, maxDepth) {
    const seen = new Set();
    function rec(nid, depth, edge, arg) {
      const n = m.byId.get(nid);
      if (seen.has(nid)) return { id: nid, edge, arg, children: [], repeat: true };
      seen.add(nid);
      let kids = (m.into.get(nid) || []).filter(e => e.type !== 'about');
      if (n.type === 'calculation' && n.inputs) {                  // keep the function's argument order and names
        const argOf = {};
        Object.entries(n.inputs).forEach(([a, r]) => { argOf[r] = argOf[r] ? argOf[r] + ', ' + a : a; });
        kids = kids.slice().sort((a, b) => (a.type === 'uses' ? 0 : 1) - (b.type === 'uses' ? 0 : 1));
        return { id: nid, edge, arg, children: depth >= maxDepth ? [] : kids.map(e => rec(e.id, depth + 1, e.type, argOf[e.id])) };
      }
      return { id: nid, edge, arg, children: depth >= maxDepth ? [] : kids.map(e => rec(e.id, depth + 1, e.type)) };
    }
    return rec(id, 0, null, null);
  }

  // Instant search over ids, titles and (lower rank) text/equations. The lower-cased strings are cached on the model.
  function search(m, q, limit) {
    q = (q || '').trim().toLowerCase();
    if (!q) return [];
    if (!m._idx) m._idx = m.nodes.map(n => [n.id.toLowerCase(), (n.title || '').toLowerCase(), (n.text || n.equation || n.where || '').toLowerCase(), n]);
    const scored = [];
    for (const [id, t, x, n] of m._idx) {
      const s = id === q ? 0 : id.startsWith(q) ? 1 : t.startsWith(q) ? 2 : id.includes(q) ? 3 : t.includes(q) ? 4 : x.includes(q) ? 5 : -1;
      if (s >= 0) scored.push([s - (n.type === 'requirement' ? 0.5 : n.type === 'claim' ? 0.2 : 0) - Math.min(n.importance || 0, 100) * 1e-4, n]);
    }
    return scored.sort((a, b) => a[0] - b[0]).slice(0, limit || 12).map(p => p[1]);
  }

  // ---- requirement areas: the team (TEAM.md section letter) that owns most of the claims verifying it ----
  const AREAS = { A: 'Systems', B: 'Aerodynamics', C: 'Structures', D: 'Mechanical design', E: 'Propulsion and energy',
    F: 'Electrical and avionics', G: 'Manufacturing', H: 'Test and safety', I: 'Program', J: 'Support', PWR: 'Electrical and avionics' };
  const AREA_ORDER = ['Systems', 'Aerodynamics', 'Structures', 'Mechanical design', 'Propulsion and energy', 'Electrical and avionics',
    'Manufacturing', 'Test and safety', 'Program', 'Support', 'Other', 'No claims yet'];
  function claimsOfReq(m, rid) { return (m.into.get(rid) || []).filter(e => e.type === 'verifies' && m.byId.get(e.id).type === 'claim').map(e => m.byId.get(e.id)); }
  function area(m, rid) {
    const c = {};
    for (const n of claimsOfReq(m, rid)) { const k = (n.id.match(/^CL-([A-Z]+)/) || [])[1]; const a = AREAS[k] || (k && AREAS[k[0]]) || 'Other'; c[a] = (c[a] || 0) + 1; }
    const best = Object.entries(c).sort((a, b) => b[1] - a[1] || AREA_ORDER.indexOf(a[0]) - AREA_ORDER.indexOf(b[0]))[0];
    return best ? best[0] : 'No claims yet';
  }
  // One row per requirement for the list: claims, fails, worst margin, unverified count.
  function reqSummary(m, rid) {
    const cl = claimsOfReq(m, rid), margins = cl.map(n => n.margin).filter(x => typeof x === 'number');
    return { claims: cl.length, fails: cl.filter(n => n.fails).length, unverified: cl.filter(n => n.status === 'UNVERIFIED').length,
      worst: margins.length ? Math.min(...margins) : null, area: area(m, rid) };
  }

  // ---- compact proof chain for the 2-D layered view ----
  // Columns (left -> right): 0 sources · 1 parameters, assumptions, input claims · 2 calculations, tests · 3 claims · 4 requirements.
  // Only direct links are followed: requirement <- its claims <- their calculations and tests <- the calculations' inputs <- the
  // sources cited by those inputs. A claim that feeds another claim's calculation appears as an input (key "in:<id>") and can be
  // opened as its own chain. opts.inputs: true / false / undefined (= auto: hide columns 0-1 when the chain exceeds opts.max nodes).
  function compactChain(m, focus, opts) {
    opts = opts || {};
    const f = m.byId.get(focus);
    if (!f) return null;
    const T = id => m.byId.get(id).type;
    const uniq = a => [...new Set(a)];
    let claims = [], reqs = [];
    if (f.type === 'requirement') { reqs = [focus]; claims = claimsOfReq(m, focus).map(n => n.id); }
    else if (f.type === 'claim') claims = [focus];
    else if (f.type === 'calculation' || f.type === 'test') claims = m.out.get(focus).filter(e => T(e.id) === 'claim').map(e => e.id);
    else if (f.type === 'part') claims = m.into.get(focus).filter(e => e.type === 'about').map(e => e.id);
    else {                                                        // parameter / assumption / source: nearest claims downstream
      let frontier = [focus];
      const seen = new Set(frontier);
      for (let d = 0; d < 4 && !claims.length && frontier.length; d++) {
        const next = [];
        for (const x of frontier) for (const e of m.out.get(x) || []) {
          if (e.type === 'about' || seen.has(e.id)) continue;
          seen.add(e.id);
          if (T(e.id) === 'claim') claims.push(e.id); else if (T(e.id) !== 'requirement') next.push(e.id);
        }
        frontier = next;
      }
    }
    claims = uniq(claims);
    const totalClaims = claims.length, maxClaims = opts.maxClaims || 120;
    if (claims.length > maxClaims) claims = claims.slice(0, maxClaims);
    if (f.type !== 'requirement') reqs = uniq(claims.flatMap(c => m.out.get(c).filter(e => e.type === 'verifies' && T(e.id) === 'requirement').map(e => e.id)));
    const claimSet = new Set(claims);

    const nodes = new Map(), edges = [], ekeys = new Set();
    const add = (key, id, col) => { if (!nodes.has(key)) nodes.set(key, { key, id, col, ref: key !== id, hidden: 0 }); return key; };
    const link = (a, b, type) => { const k = a + '>' + b; if (!ekeys.has(k)) { ekeys.add(k); edges.push({ from: a, to: b, type }); } };
    const inputKey = id => (claimSet.has(id) ? 'in:' + id : id);
    const colOf = { source: 0, parameter: 1, assumption: 1, claim: 1, calculation: 2, test: 2, part: -1, requirement: -1 };
    reqs.forEach(r => add(r, r, 4));
    claims.forEach(c => add(c, c, 3));
    const lower = [];                                            // [fromId, toKey, type, col] candidates for columns 0-2
    for (const c of claims) {
      for (const e of m.out.get(c)) if (e.type === 'verifies' && nodes.has(e.id)) link(c, e.id, e.type);
      for (const e of m.into.get(c)) { const col = colOf[T(e.id)]; if (col >= 0) lower.push([e.id, c, e.type, col]); }
    }
    const calcs = [];
    for (const [id, to, type, col] of lower) if (col === 2) { add(id, id, 2); link(id, to, type); if (T(id) === 'calculation') calcs.push(id); }
    const inputs = lower.filter(x => x[3] < 2);
    for (const k of uniq(calcs)) for (const e of m.into.get(k)) { const col = colOf[T(e.id)]; if (col >= 0 && col < 2) inputs.push([e.id, k, e.type, col]); }
    // count what the input columns would add, then decide whether to show them
    const inNodes = new Set(), srcNodes = new Set();
    for (const [id, , , col] of inputs) (col === 0 ? srcNodes : inNodes).add(inputKey(id));
    for (const key of inNodes) { const id = key.replace(/^in:/, ''); if (key === id && T(id) !== 'claim') for (const e of m.into.get(id)) if (T(e.id) === 'source') srcNodes.add(e.id); }
    const extra = inNodes.size + srcNodes.size, max = opts.max || 160;
    const showInputs = opts.inputs === undefined ? nodes.size + extra <= max : !!opts.inputs;
    if (showInputs) {
      for (const [id, to, type, col] of inputs) { const key = add(inputKey(id), id, col); link(key, to, type); }
      for (const key of [...nodes.keys()]) {
        const nd = nodes.get(key);
        if (nd.col !== 1 || nd.ref || T(nd.id) === 'claim') continue;
        for (const e of m.into.get(nd.id)) if (T(e.id) === 'source') { add(e.id, e.id, 0); link(e.id, key, e.type); }
      }
    } else {
      for (const [, to] of inputs) if (nodes.has(to)) nodes.get(to).hidden++;
    }
    return { focus, nodes: [...nodes.values()], edges, reqs, claims, totalClaims, showInputs, hiddenInputs: showInputs ? 0 : extra };
  }

  // Positions for compactChain(): columns left -> right; claims in rank order (fails and thin margins first), every other
  // column ordered by the mean position of the nodes it feeds (barycentre), then spread so boxes never overlap.
  // dims: {w, colGap, gap, h: node => height}
  function layoutChain(m, ch, dims) {
    const W = typeof dims.w === 'function' ? dims.w : () => dims.w, CG = dims.colGap, GAP = dims.gap, H = dims.h;
    const outs = new Map(), ins = new Map();
    ch.nodes.forEach(n => { outs.set(n.key, []); ins.set(n.key, []); });
    ch.edges.forEach(e => { outs.get(e.from).push(e.to); ins.get(e.to).push(e.from); });
    const used = [...new Set(ch.nodes.map(n => n.col))].sort((a, b) => a - b);
    const xs = {};
    used.reduce((acc, c) => { xs[c] = acc; return acc + W(c) + CG; }, 0);
    const x = col => xs[col];
    const pos = new Map(), cols = {};
    ch.nodes.forEach(n => (cols[n.col] = cols[n.col] || []).push(n));
    const rank = n => { const d = m.byId.get(n.id); return [n.key === ch.focus ? 0 : 1, d.fails ? 0 : 1, typeof d.margin === 'number' ? d.margin : 9, STATUSES.indexOf(d.status), n.id]; };
    const cmp = (a, b) => { const ra = rank(a), rb = rank(b); for (let i = 0; i < ra.length; i++) if (ra[i] !== rb[i]) return ra[i] < rb[i] ? -1 : 1; return 0; };
    const place = (list, desired) => {
      const want = new Map(list.map(n => [n.key, desired(n)]));
      list.sort((a, b) => want.get(a.key) - want.get(b.key) || cmp(a, b));
      let y = -Infinity;
      const ys = list.map(n => { y = Math.max(want.get(n.key), y); const at = y; y += H(n) + GAP; return at; });
      const shift = list.length ? Math.min(0, list.reduce((s, n, i) => s + (want.get(n.key) - ys[i]), 0) / list.length) : 0;
      list.forEach((n, i) => pos.set(n.key, { x: x(n.col), y: ys[i] + shift }));
    };
    const claims = (cols[3] || []).sort(cmp);
    let y = 0;
    claims.forEach(n => { pos.set(n.key, { x: x(3), y }); y += H(n) + GAP; });
    const centre = k => pos.get(k).y + H(byKey.get(k)) / 2;
    const byKey = new Map(ch.nodes.map(n => [n.key, n]));
    const mean = keys => { const ys = keys.filter(k => pos.has(k)).map(centre); return ys.length ? ys.reduce((a, b) => a + b, 0) / ys.length : 0; };
    if (cols[4]) place(cols[4], n => { const ys = ins.get(n.key).filter(k => pos.has(k)).map(k => pos.get(k).y); return ys.length ? Math.min(...ys) : 0; });
    for (const c of [2, 1, 0]) if (cols[c]) place(cols[c], n => mean(outs.get(n.key)) - H(n) / 2);
    let minY = Infinity, maxY = -Infinity;
    for (const n of ch.nodes) { const p = pos.get(n.key); minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y + H(n)); }
    for (const p of pos.values()) p.y -= minY;
    return { pos, width: used.length ? xs[used[used.length - 1]] + W(used[used.length - 1]) : 0, height: Math.max(0, maxY - minY), columns: used, x, byKey, outs, ins };
  }

  // ---- build status: group meta.errors into re-run instructions ----
  // "DRIFT <calc>.<output>: stored a, re-runs to b. ... Re-run <script>"  -> drift, grouped by script
  // "<calc>: <script>::<fn> failed: <reason>"                              -> could not run, grouped by script
  // anything else (e.g. a link to an unknown requirement)                  -> other
  function buildIssues(meta) {
    const drift = new Map(), failed = new Map(), other = [];
    for (const e of (meta && meta.errors) || []) {
      let mm;
      if ((mm = e.match(/^DRIFT (\S+?)\.([^.:\s]+): /))) {
        const script = (e.match(/Re-run (\S+?)\.?\s*$/) || [])[1] || 'unknown script';
        if (!drift.has(script)) drift.set(script, []);
        drift.get(script).push({ id: mm[1], output: mm[2], text: e });
      } else if ((mm = e.match(/^(\S+): (\S+?)::(\S+) failed: (.*)$/))) {
        if (!failed.has(mm[2])) failed.set(mm[2], []);
        failed.get(mm[2]).push({ id: mm[1], fn: mm[3], reason: mm[4], text: e });
      } else {
        other.push({ id: (e.match(/^([A-Z][\w:.-]*):/) || [])[1], text: e });
      }
    }
    const groups = mp => [...mp.entries()].map(([script, items]) => ({ script, items })).sort((a, b) => b.items.length - a.items.length || a.script.localeCompare(b.script));
    const nDrift = [...drift.values()].reduce((s, a) => s + a.length, 0);
    const nFailed = [...failed.values()].reduce((s, a) => s + a.length, 0);
    return { drift: groups(drift), failed: groups(failed), other, nDrift, nOther: nFailed + other.length, warnings: (meta && meta.warnings) || [] };
  }

  // Filter state: {statuses:Set, types:Set, failsOnly:bool, text:string}
  function visible(n, f) {
    if (!f.types.has(n.type)) return false;
    if (!f.statuses.has(n.status)) return false;
    if (f.failsOnly && !n.fails) return false;
    return true;
  }

  function counts(m, key, type) {
    const c = {};
    for (const n of m.nodes) if (!type || n.type === type) c[n[key]] = (c[n[key]] || 0) + 1;
    return c;
  }

  // ---- formatting (mirrors proofkit.fmt so numbers read the same in CHAIN.md and the page) ----
  function fmt(v, unit) {
    let s;
    if (v === null || v === undefined) s = '—';
    else if (typeof v === 'number') s = Number.isInteger(v) && Math.abs(v) < 1e5 ? String(v) : Number(v.toPrecision(4)).toString();
    else if (Array.isArray(v)) s = 'table (' + v.length + ' rows)';
    else s = String(v);
    return unit && unit !== '-' && v !== null && v !== undefined && !Array.isArray(v) ? s + ' ' + unit : s;
  }
  const pct = x => (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(Math.round(x * 100)) + ' %';
  const opText = op => (op === '>=' ? '≥' : op === '<=' ? '≤' : op);

  function partLink(m, id) {
    const t = m.meta.part_link || '';
    return t ? t.replace('{id}', encodeURIComponent(id)) : null;
  }

  const api = { STATUSES, TYPES, TYPE_LABEL, LAYER, build, upstream, downstream, chain, pathsUp, treeDown, search,
    visible, counts, fmt, pct, opText, partLink, AREA_ORDER, area, claimsOfReq, reqSummary, compactChain, layoutChain, buildIssues };
  root.ProofModel = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
