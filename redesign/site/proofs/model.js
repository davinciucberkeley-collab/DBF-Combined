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

  // Paths from a node up to each requirement it supports: [[id, ..., R-id], ...] (shortest first, max 8).
  function pathsUp(m, id) {
    const res = [], queue = [[id]];
    while (queue.length && res.length < 8) {
      const p = queue.shift(), last = p[p.length - 1];
      const nexts = (m.out.get(last) || []).filter(e => e.type !== 'about' && !p.includes(e.id));
      if (m.byId.get(last).type === 'requirement' && p.length > 1) { res.push(p); continue; }
      if (!nexts.length && p.length > 1) { res.push(p); continue; }
      nexts.forEach(e => queue.push(p.concat(e.id)));
      if (queue.length > 500) break;                               // guard against huge graphs
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

  function search(m, q, limit) {
    q = (q || '').trim().toLowerCase();
    if (!q) return [];
    const scored = [];
    for (const n of m.nodes) {
      const id = n.id.toLowerCase(), t = (n.title || '').toLowerCase(), x = (n.text || n.equation || n.where || '').toLowerCase();
      let s = id === q ? 0 : id.startsWith(q) ? 1 : t.startsWith(q) ? 2 : id.includes(q) ? 3 : t.includes(q) ? 4 : x.includes(q) ? 5 : -1;
      if (s >= 0) scored.push([s - (n.importance || 0) * 1e-3, n]);
    }
    return scored.sort((a, b) => a[0] - b[0]).slice(0, limit || 12).map(p => p[1]);
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
    visible, counts, fmt, pct, opText, partLink };
  root.ProofModel = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
