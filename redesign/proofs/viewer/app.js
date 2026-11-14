// app.js — the proof-chain viewer UI. Reads the graph written by build_graph.py (out/graph.js sets window.PROOF_GRAPH,
// so the page also works from file://).
// Views: Requirements (default, plain HTML list) -> one requirement's proof chain as a 2-D layered SVG (only that chain,
// typically < 100 nodes); Overview = the whole graph on a 2-D canvas (vendored force-graph), 3-D (3d-force-graph) on request.
// Routing lives in the hash: #chain=<id>~<id>&sel=<id>, #overview, legacy #node=<id>.
// Data selection: ?data=examples | ?data=redesign | ?graph=<url of a graph.json>; default = redesign, else the demo.
(function () {
  'use strict';
  const M = window.ProofModel;
  const $ = s => document.querySelector(s);
  const esc = s => String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = {                                    // per-viewer conveniences only; the page works without them
    get(k) { try { return localStorage.getItem('proofs.' + k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem('proofs.' + k, v); } catch (e) { /* private mode or full */ } },
  };
  const REPO = '../../../';                          // viewer/ -> proofs/ -> redesign/ -> repo root
  const SOURCES = { redesign: '../out/graph.js', examples: '../examples/out/graph.js' };
  const LIBS = { '3d': 'vendor/3d-force-graph.min.js', '2d': 'vendor/force-graph.min.js' }, libLoaded = {};
  const T0 = performance.now();

  let model = null, issues = null, pal = {}, route = { view: 'reqs' }, statusOpen = false, rfilter = 'all';
  let chainZoom = null, chainCtx = null;              // chainZoom null = auto (fit width, at most 100 %)
  // overview state
  let G = null, ovMode = '2d', ovSel = null, hl = null, hoverId = null, ovBuiltFor = '';
  const ovTypes = new Set(['requirement', 'claim', 'calculation', 'source', 'test']);
  const ovStatus = { statuses: new Set(M.STATUSES), failsOnly: false };

  // ------------------------------------------------------------------ data
  function loadScript(src) {
    return new Promise(res => {
      window.PROOF_GRAPH = undefined;
      const s = document.createElement('script');
      s.src = src + '?t=' + Date.now();
      s.onload = () => { const g = window.PROOF_GRAPH || null; window.PROOF_GRAPH = undefined; res(g); };
      s.onerror = () => res(null);
      document.head.appendChild(s);
    });
  }

  async function loadData() {
    const q = new URLSearchParams(location.search);
    if (q.get('graph')) {
      try { return { g: await (await fetch(q.get('graph'))).json(), name: q.get('graph') }; }
      catch (e) { return { error: 'Could not fetch ' + q.get('graph') + ' (' + e.message + ')' }; }
    }
    const want = q.get('data');
    if (want && SOURCES[want]) {
      const g = await loadScript(SOURCES[want]);
      if (g) return { g, name: want };
    }
    const real = await loadScript(SOURCES.redesign);
    if (real && real.nodes.some(n => n.type === 'claim')) return { g: real, name: 'redesign' };
    const demo = await loadScript(SOURCES.examples);
    if (demo) return { g: demo, name: 'examples', note: (real ? 'No claims in redesign/ yet' : 'out/graph.js is not built yet') +
      ' — showing the demo aircraft from examples/. <a href="?data=redesign">real graph</a>' };
    return { error: 'No graph found. Run <code>python -I redesign/proofs/build_graph.py --examples</code>.' };
  }

  // ------------------------------------------------------------------ colours (canvas needs resolved values)
  function readPalette() {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
    pal = { st: {}, fail: v('--st-fail'), bg: v('--bg'), line: v('--line-3'), accent: v('--accent'), fg: v('--fg'), fg3: v('--fg-3'),
      sans: v('--font-sans') || 'system-ui, sans-serif' };
    M.STATUSES.forEach(s => { pal.st[s] = v('--st-' + s.toLowerCase()) || v('--st-proposed'); });
    alphaCache.clear();
  }
  const alphaCache = new Map();
  function withAlpha(hex, a) {
    const k = hex + a;
    if (alphaCache.has(k)) return alphaCache.get(k);
    const h = hex.replace('#', ''), f = h.length === 3 ? h.split('').map(c => c + c).join('') : h, i = parseInt(f, 16);
    const out = `rgba(${(i >> 16) & 255},${(i >> 8) & 255},${i & 255},${a})`;
    alphaCache.set(k, out);
    return out;
  }
  const st = n => (n.fails ? 'FAIL' : n.status);
  const pct = x => { const a = Math.abs(x) * 100, d = a < 9.95 && a > 0 ? 1 : 0; return (x > 0 ? '+' : x < 0 ? '−' : '') + a.toFixed(d) + ' %'; };
  const badge = n => `<span class="ds-badge" data-status="${st(n)}">${st(n)}</span>`;
  const mgClass = x => (x < 0 ? ' neg' : x < 0.1 ? ' thin' : '');
  // A limit of 0 has no percentage margin: build_graph.py then stores the signed distance to the limit in the claim's
  // unit and sets margin_abs. Pass the node; a bare number is still read as a fraction.
  const absTxt = n => (n.margin > 0 ? '+' : n.margin < 0 ? '−' : '') + M.fmt(Math.abs(n.margin), n.unit);
  const mgText = n => (n.margin_abs ? absTxt(n) : pct(n.margin));
  const mgCls = n => (n.margin < 0 ? ' neg' : !n.margin_abs && n.margin < 0.1 ? ' thin' : '');
  const marginBadge = x => {
    const n = typeof x === 'number' ? { margin: x } : x;
    return n && typeof n.margin === 'number' ? `<span class="mg${mgCls(n)}" title="${n.margin_abs ? 'distance to a limit of 0' : 'margin to the limit'}${n.margin < 0 ? ' — FAILS' : ''}">${esc(mgText(n))}</span>` : '';
  };
  const go = (id, label) => `<button class="nlink" data-go="${esc(id)}">${esc(label || id)}</button>`;
  const repoLink = (p, label) => /^https?:/.test(p) ? `<a href="${esc(p)}" target="_blank" rel="noopener">${esc(label || p)}</a>` : `<a href="${esc(REPO + p)}" target="_blank" rel="noopener">${esc(label || p)}</a>`;

  // ------------------------------------------------------------------ routing
  function parseHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    if (p.has('node')) return { view: 'node', node: p.get('node') };
    if (p.has('overview')) return { view: 'overview', sel: p.get('sel') };
    if (p.has('chain')) {
      const trail = p.get('chain').split('~').filter(id => model.byId.has(id));
      if (trail.length) return { view: 'chain', trail, sel: model.byId.has(p.get('sel')) ? p.get('sel') : null, inputs: p.get('inputs') };
    }
    return { view: 'reqs' };
  }
  function hashOf(r) {
    const p = new URLSearchParams();
    if (r.view === 'overview') { p.set('overview', ''); if (r.sel) p.set('sel', r.sel); }
    else if (r.view === 'chain') { p.set('chain', r.trail.join('~')); if (r.sel) p.set('sel', r.sel); if (r.inputs) p.set('inputs', r.inputs); }
    return p.toString().replace(/=$/, '').replace(/=&/, '&');
  }
  function nav(r, replace) {
    const h = hashOf(r);
    if (replace) { try { history.replaceState(null, '', h ? '#' + h : location.pathname + location.search); } catch (e) { /* file:// */ } render(); }
    else if (('#' + h) === location.hash || (!h && !location.hash)) render();
    else location.hash = h;
  }
  // Jump from any node (search, links, status panel) to the chain view of its requirement(s).
  function reqsOf(id) {
    const n = model.byId.get(id);
    if (n.type === 'requirement') return [id];
    const direct = (model.out.get(id) || []).filter(e => e.type === 'verifies' && model.byId.get(e.id).type === 'requirement').map(e => e.id);
    if (direct.length) return direct;
    let frontier = [id];                                        // breadth-first: the nearest requirement(s) downstream
    const seen = new Set(frontier);
    while (frontier.length) {
      const next = [], found = [];
      for (const x of frontier) for (const e of model.out.get(x) || []) {
        if (e.type === 'about' || seen.has(e.id)) continue;
        seen.add(e.id);
        (model.byId.get(e.id).type === 'requirement' ? found : next).push(e.id);
      }
      if (found.length) return found;
      frontier = next;
    }
    return [];
  }
  function openNode(id) {
    const n = model.byId.get(id);
    if (!n) return;
    if (n.type === 'requirement') return nav({ view: 'chain', trail: [id] });
    const reqs = reqsOf(id);
    if (reqs.length) {
      const ch = M.compactChain(model, reqs[0]);
      if (ch.nodes.some(x => x.id === id && !x.ref)) return nav({ view: 'chain', trail: [reqs[0]], sel: id });
      return nav({ view: 'chain', trail: [reqs[0], id], sel: id });
    }
    nav({ view: 'chain', trail: [id], sel: id });
  }
  function render() {
    route = parseHash();
    if (route.view === 'node') { const id = route.node; route = { view: 'reqs' }; if (model.byId.has(id)) { openNode(id); return; } }
    const v = route.view;
    $('#app').classList.toggle('wide', v === 'chain');
    document.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === (v === 'overview' ? 'overview' : 'reqs'))));
    $('#homePane').hidden = v !== 'reqs';
    $('#chainPane').hidden = v !== 'chain';
    $('#ovMain').hidden = v !== 'overview';
    $('#reqPane').hidden = v === 'overview';
    $('#ovPane').hidden = v !== 'overview';
    if (v === 'chain') {
      const sig = route.trail.join('~') + '|' + (route.inputs || '');
      if (!chainCtx || chainCtx.sig !== sig || $('#chainSvg').childElementCount === 0) renderChain(sig);
      else markChainSelection();
    }
    if (v === 'overview') showOverview();
    renderReqList();
    statusOpen ? renderStatus() : renderDetail();
  }

  // ------------------------------------------------------------------ build status line + panel
  function renderStatusLine(note) {
    const I = issues, built = esc(model.meta.generated || '');
    let h;
    if (!I.nDrift && !I.nOther) h = `<span><span class="sdot ok"></span> Every stored value re-computes from its script.</span>`;
    else {
      const parts = [];
      if (I.nDrift) parts.push(`<b>${I.nDrift}</b> stored value${I.nDrift > 1 ? 's' : ''} differ from a fresh re-run (drift)`);
      if (I.nOther) parts.push(`<b>${I.nOther}</b> other issue${I.nOther > 1 ? 's' : ''}`);
      h = `<span><span class="sdot"></span> ${parts.join(' · ')} — <button class="lnk" data-status-open>see Status</button></span>`;
    }
    if (note) h += `<span>· ${note}</span>`;
    $('#statusline').innerHTML = h + `<span class="meta" title="graph built">built ${built}</span>`;
  }
  const wbr = p => esc(p).replace(/\//g, '/<wbr>');
  const short = (s, n) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
  function renderStatus() {
    const I = issues, box = $('#detail');
    const driftItem = it => {
      const m = it.text.match(/stored (.*?), re-runs to (.*?)(?:\. Changed inputs|\. Re-run|$)/);
      return `<li>${go(it.id)}<span class="v">.${esc(it.output)}</span>${m ? ` — ${esc(short(m[1], 40))} → ${esc(short(m[2], 40))}` : ''}</li>`;
    };
    let h = `<div class="actions" style="margin-top:0"><button class="btn" data-status-close>← Back</button></div>
      <h2 class="dtitle">Build status</h2>
      <p class="text">The graph builder re-runs every calculation and compares the result with the value stored in the claims files. Built ${esc(model.meta.generated || '—')}.</p>`;
    if (!I.nDrift && !I.nOther) h += `<p class="text">Every stored value re-computes. Nothing to do.</p>`;
    if (I.nDrift) {
      h += `<h3 class="sec">Drift · ${I.nDrift} value${I.nDrift > 1 ? 's' : ''}</h3>
        <p class="text" style="margin-top:0">An input changed after the script last ran. Re-running the script stores the new value; claims that use it may change margin.</p>` +
        I.drift.map(g => `<details class="grp2"><summary><span class="s">re-run <code>${wbr(g.script)}</code></span><span class="n">${g.items.length} value${g.items.length > 1 ? 's' : ''}</span></summary>
          <ul>${g.items.slice(0, 80).map(driftItem).join('')}${g.items.length > 80 ? `<li>… ${g.items.length - 80} more</li>` : ''}</ul></details>`).join('');
    }
    if (I.failed.length) {
      h += `<h3 class="sec">Calculations that did not run · ${I.failed.reduce((s, g) => s + g.items.length, 0)}</h3>` +
        I.failed.map(g => {
          const reasons = [...new Set(g.items.map(i => i.reason))];
          return `<details class="grp2" open><summary><span class="s">fix and re-run <code>${wbr(g.script)}</code></span><span class="n">${g.items.length} calc${g.items.length > 1 ? 's' : ''}</span></summary>
            <ul>${reasons.length === 1 ? `<li>${esc(reasons[0])}</li>` : ''}${g.items.map(i => `<li>${go(i.id)} <span class="v">${esc(i.fn)}()</span>${reasons.length > 1 ? ' — ' + esc(i.reason) : ''}</li>`).join('')}</ul></details>`;
        }).join('');
    }
    if (I.other.length) {
      h += `<h3 class="sec">Other · ${I.other.length}</h3><ul style="padding-left:18px;margin:0;font-size:13px">` +
        I.other.map(o => `<li>${o.id && model.byId.has(o.id) ? go(o.id) + esc(o.text.slice(o.id.length)) : esc(o.text)}</li>`).join('') + '</ul>';
    }
    if (I.warnings.length) {
      h += `<h3 class="sec">Notes · ${I.warnings.length}</h3><details class="grp2"><summary><span class="s">warnings from the build</span><span class="n">${I.warnings.length}</span></summary><ul>` +
        I.warnings.map(w => `<li>${esc(w)}</li>`).join('') + '</ul></details>';
    }
    box.innerHTML = h;
    box.scrollTop = 0;
  }

  // ------------------------------------------------------------------ requirement list (left)
  let reqRows = null;
  function renderReqList() {
    if (!reqRows) reqRows = model.nodes.filter(n => n.type === 'requirement').map(n => ({ n, s: M.reqSummary(model, n.id) }));
    const cur = route.view === 'chain' ? route.trail[0] : null;
    const rows = reqRows.filter(r => rfilter === 'all' || (rfilter === 'fails' ? r.s.fails > 0 : r.s.claims === 0));
    const groups = new Map();
    rows.forEach(r => { if (!groups.has(r.s.area)) groups.set(r.s.area, []); groups.get(r.s.area).push(r); });
    const order = [...groups.keys()].sort((a, b) => M.AREA_ORDER.indexOf(a) - M.AREA_ORDER.indexOf(b));
    const sortRows = (a, b) => (b.s.fails > 0) - (a.s.fails > 0) || (a.s.worst === null) - (b.s.worst === null) || (a.s.worst || 0) - (b.s.worst || 0) || a.n.id.localeCompare(b.n.id);
    $('#reqList').innerHTML = order.map(area => `<section class="grp"><h3><span>${esc(area)}</span><span>${groups.get(area).length}</span></h3>` +
      groups.get(area).sort(sortRows).map(({ n, s }) => `<button class="req" data-req="${esc(n.id)}" aria-current="${n.id === cur}">
        <span class="rid">${esc(n.id)}</span>${badge(n)}<span class="rt" title="${esc(n.text || n.title)}">${esc(n.title)}</span>
        <span class="rm">${s.claims ? `${s.claims} claim${s.claims > 1 ? 's' : ''}` : 'no claims yet'}${s.fails ? ` · <span class="f">${s.fails} fail${s.fails > 1 ? 's' : ''}</span>` : ''}${s.worst !== null ? `<span class="mg${mgClass(s.worst)}" title="worst margin among its claims">${pct(s.worst)}</span>` : ''}</span>
      </button>`).join('') + '</section>').join('') || '<p class="note">No requirement matches.</p>';
  }

  // ------------------------------------------------------------------ home (centre, no requirement chosen)
  function renderHome() {
    const claims = model.nodes.filter(n => n.type === 'claim'), c = M.counts(model, 'status', 'claim');
    const fails = claims.filter(n => n.fails).sort((a, b) => (a.margin_abs ? -9 : a.margin ?? 0) - (b.margin_abs ? -9 : b.margin ?? 0));   // limit-0 fails first: their margin is a distance, not comparable
    const reqs = model.nodes.filter(n => n.type === 'requirement'), traced = reqs.filter(r => M.claimsOfReq(model, r.id).length).length;
    const order = M.STATUSES.slice().reverse();
    const failRows = fails.map(n => {
      const rq = (model.out.get(n.id) || []).filter(e => e.type === 'verifies').map(e => e.id);
      const lv = n.limit ? (n.limit.value !== undefined ? n.limit.value : n.limit.resolved) : undefined;
      return `<tr class="click" data-open="${esc(n.id)}"><td><span class="id">${esc(n.id)}</span>${esc(n.title)}</td>
        <td class="num">${esc(M.fmt(n.value, n.unit))}</td><td class="num">${n.limit ? esc(M.opText(n.limit.op) + ' ' + M.fmt(lv, n.unit)) : '—'}</td>
        <td class="num">${marginBadge(n) || '<span class="ds-badge" data-status="FAIL">FAIL</span>'}</td><td><span class="v">${esc(rq.join(', ') || '—')}</span></td></tr>`;
    }).join('');
    $('#home').innerHTML = `<h1>Requirements and their proof chains</h1>
      <p class="sub">Pick a requirement on the left to see the claims that verify it, the calculations behind each claim, and the parameters, assumptions and sources those rest on. Press <kbd>/</kbd> to search any id.</p>
      <div class="tiles">
        <div class="tile"><b>${reqs.length}</b><span>requirements · ${traced} with claims</span></div>
        <div class="tile"><b>${claims.length}</b><span>claims</span></div>
        <div class="tile fail"><b>${fails.length}</b><span>claims fail (negative margin)</span></div>
        <div class="tile"><b>${c.UNVERIFIED || 0}</b><span>claims unverified</span></div>
      </div>
      <div class="bar">${order.map(s => c[s] ? `<i data-status="${s}" style="width:${100 * c[s] / claims.length}%" title="${s} ${c[s]}"></i>` : '').join('')}</div>
      <div class="legendrow">${order.filter(s => c[s]).map(s => `<span data-status="${s}"><i></i>${s} ${c[s]}</span>`).join('')}</div>
      <h2>Failing claims (${fails.length})</h2>
      <div class="scrollx"><table class="list"><thead><tr><th>Claim</th><th class="num">Value</th><th class="num">Limit</th><th class="num">Margin</th><th>Requirement</th></tr></thead>
      <tbody>${failRows || '<tr><td colspan="5">No claim fails.</td></tr>'}</tbody></table></div>`;
  }

  // ------------------------------------------------------------------ chain view (centre): layered SVG
  const COLW = { 0: 196, 1: 210, 2: 210, 3: 250, 4: 196 };
  const DIM = { w: c => COLW[c], colGap: 32, gap: 10, pad: 16, head: 30, h: n => (n.col === 3 ? 60 : 46) };
  const COLS = { 0: 'Sources', 1: 'Parameters · assumptions · inputs', 2: 'Calculations · tests', 3: 'Claims', 4: 'Requirement' };
  const GLYPH = {                                       // shapes per diagram-style.md, drawn small and neutral
    requirement: 'M5 0L10 2.9V8.7L5 11.6L0 8.7V2.9Z', claim: 'M5 0.5A5 5 0 1 1 4.99 0.5Z', calculation: 'M5 0L10 5.5L5 11L0 5.5Z',
    parameter: 'M0.5 1H9.5V10H0.5Z', assumption: 'M3 1.5H7A4 4 0 0 1 7 9.5H3A4 4 0 0 1 3 1.5Z', source: 'M0.5 0.5H6.5L9.5 3.5V10.5H0.5ZM6.5 0.5V3.5H9.5',
    test: 'M5 0.5A5 5 0 1 1 4.99 0.5ZM5 3V8M2.5 5.5H7.5', part: 'M1 1H9V9H1Z',
  };
  const fit = (s, px, cw) => { s = String(s || ''); const n = Math.max(4, Math.floor(px / cw)); return s.length > n ? s.slice(0, n - 1) + '…' : s; };

  function renderChain(sig) {
    const trail = route.trail, focus = trail[trail.length - 1], fnode = model.byId.get(focus);
    const inputs = route.inputs === 'show' ? true : route.inputs === 'hide' ? false : undefined;
    const ch = M.compactChain(model, focus, { inputs });
    const L = M.layoutChain(model, ch, DIM);
    // breadcrumbs
    const crumbs = [`<button class="home" data-crumb="-1">All requirements</button>`];
    trail.forEach((id, i) => {
      crumbs.push('<span class="sep">›</span>');
      crumbs.push(i === trail.length - 1 ? `<span class="cur" title="${esc(model.byId.get(id).title || '')}">${esc(id)}</span>` : `<button data-crumb="${i}" title="${esc(model.byId.get(id).title || '')}">${esc(id)}</button>`);
    });
    $('#crumbs').innerHTML = crumbs.join('');
    const ib = $('#inputsBtn');
    const canToggle = ch.showInputs ? ch.nodes.some(n => n.col < 2) : ch.hiddenInputs > 0;
    ib.hidden = !canToggle;
    ib.textContent = ch.showInputs ? 'Hide inputs and sources' : `Show inputs and sources (+${ch.hiddenInputs})`;
    ib.dataset.next = ch.showInputs ? 'hide' : 'show';
    const notes = [];
    if (!ch.showInputs && ch.hiddenInputs) notes.push(`Large chain: ${ch.hiddenInputs} parameters, assumptions and sources are folded away. Click a claim and open its own chain to see them, or show them all.`);
    if (ch.totalClaims > ch.claims.length) notes.push(`Showing the first ${ch.claims.length} of ${ch.totalClaims} claims.`);
    if (fnode.type === 'requirement' && !ch.claims.length) notes.push('No claim verifies this requirement yet.');
    $('#chainNote').hidden = !notes.length;
    $('#chainNote').textContent = notes.join(' ');

    const P = DIM.pad, H0 = DIM.head;
    const pos = k => L.pos.get(k);
    const out = [];
    L.columns.forEach(c => out.push(`<text class="colh" x="${P + L.x(c)}" y="${P + 12}">${esc(COLS[c].toUpperCase())}</text>`));
    const nodeByKey = new Map(ch.nodes.map(n => [n.key, n]));
    ch.edges.forEach((e, i) => {
      const a = pos(e.from), b = pos(e.to), na = nodeByKey.get(e.from), nb = nodeByKey.get(e.to);
      const x1 = P + a.x + DIM.w(na.col), y1 = P + H0 + a.y + DIM.h(na) / 2, x2 = P + b.x, y2 = P + H0 + b.y + DIM.h(nb) / 2, dx = Math.max(24, (x2 - x1) / 2);
      const fail = na.col === 3 && model.byId.get(na.id).fails;      // a failing claim's link up to its requirement
      out.push(`<path class="e${fail ? ' fail' : ''}" data-i="${i}" d="M${x1} ${y1}C${x1 + dx} ${y1} ${x2 - dx} ${y2} ${x2} ${y2}"/>`);
    });
    for (const nd of ch.nodes) {
      const n = model.byId.get(nd.id), p = pos(nd.key), h = DIM.h(nd), W = DIM.w(nd.col), x = P + p.x, y = P + H0 + p.y, s = st(n);
      const cls = 'n' + (nd.ref ? ' ref' : '') + (nd.key === focus ? ' focus' : '');
      let inner = `<rect class="box" width="${W}" height="${h}" rx="5"/>` +
        `<path class="glyph" transform="translate(9 ${n.type === 'requirement' ? 8 : 9})" d="${GLYPH[n.type] || GLYPH.part}"/>` +
        `<text class="nid" x="25" y="17">${esc(fit(nd.id, W - 25 - 8 - s.length * 6.4 - 8, 6.6))}</text>` +
        `<text class="nst" x="${W - 8}" y="17" text-anchor="end">${s}</text>`;
      let line2 = n.title || n.id;
      if (n.type === 'parameter') line2 = M.fmt(n.value, n.unit);
      const hid = nd.hidden ? `+${nd.hidden} in` : '';
      inner += `<text class="${n.type === 'parameter' ? 'nv' : 'nt'}" x="9" y="35">${esc(fit(line2, W - 18 - (hid ? 44 : 0), n.type === 'parameter' ? 7.3 : 6.9))}</text>`;
      if (hid) inner += `<text class="nl" x="${W - 8}" y="35" text-anchor="end">${hid}</text>`;
      if (n.type === 'claim' && nd.col === 3) {
        const lv = n.limit ? (n.limit.value !== undefined ? n.limit.value : n.limit.resolved) : undefined;
        const val = M.fmt(n.value, n.unit) + (n.limit ? '  ' + M.opText(n.limit.op) + ' ' + M.fmt(lv, n.unit) : '');
        const hasM = typeof n.margin === 'number';
        inner += `<text class="nv" x="9" y="52">${esc(fit(val, W - 18 - (hasM ? 64 : 0), 7.3))}</text>`;
        if (hasM) {
          const t = mgText(n), bw = t.length * 7 + 12;
          inner += `<g class="${n.margin < 0 ? 'mg-neg' : !n.margin_abs && n.margin < 0.1 ? 'mg-thin' : ''}" transform="translate(${W - 8 - bw} 40)"><rect class="mgb" width="${bw}" height="16" rx="3"/><text class="mgt" x="${bw / 2}" y="12" text-anchor="middle">${esc(t)}</text></g>`;
        }
      }
      out.push(`<g class="${cls}" data-k="${esc(nd.key)}" data-status="${s}" transform="translate(${x} ${y})"><title>${esc(nd.id + ' — ' + (n.title || '') + (nd.ref ? ' (input; double-click to open its chain)' : ''))}</title>${inner}</g>`);
    }
    const svg = $('#chainSvg'), wN = L.width + 2 * P, hN = L.height + H0 + 2 * P;
    svg.setAttribute('viewBox', `0 0 ${wN} ${hN}`);
    svg.innerHTML = out.join('');
    chainCtx = { ch, L, wN, hN, focus, sig, adj: buildAdj(ch) };
    applyZoom();
    markChainSelection();
    const selKey = route.sel && L.pos.has(route.sel) ? route.sel : route.sel && L.pos.has('in:' + route.sel) ? 'in:' + route.sel : null;
    if (selKey && route.sel !== focus) scrollToKey(selKey); else $('#chainScroll').scrollTo(0, 0);
  }
  function buildAdj(ch) {
    const adj = new Map();
    ch.nodes.forEach(n => adj.set(n.key, { e: [], n: new Set([n.key]) }));
    ch.edges.forEach((e, i) => { adj.get(e.from).e.push(i); adj.get(e.to).e.push(i); adj.get(e.from).n.add(e.to); adj.get(e.to).n.add(e.from); });
    return adj;
  }
  function applyZoom() {
    if (!chainCtx) return;
    const box = $('#chainScroll'), auto = Math.min(1, Math.max(box.clientWidth < 640 ? 0.75 : 0.6, (box.clientWidth - 4) / chainCtx.wN));
    const z = chainZoom || auto;
    const svg = $('#chainSvg');
    svg.setAttribute('width', Math.round(chainCtx.wN * z));
    svg.setAttribute('height', Math.round(chainCtx.hN * z));
    $('#zoomLbl').textContent = Math.round(z * 100) + ' %';
    chainCtx.z = z;
  }
  function scrollToKey(key) {
    const p = chainCtx.L.pos.get(key), z = chainCtx.z, box = $('#chainScroll');
    box.scrollTo({ left: Math.max(0, (p.x + DIM.pad) * z - box.clientWidth / 2 + 105 * z), top: Math.max(0, (p.y + DIM.pad + DIM.head) * z - box.clientHeight / 3) });
  }
  function markChainSelection() {
    const svg = $('#chainSvg');
    svg.querySelectorAll('.selr').forEach(r => r.remove());
    const sel = route.sel || (chainCtx && chainCtx.focus);
    if (!sel || !chainCtx) return;
    for (const key of [sel, 'in:' + sel]) {
      const g = svg.querySelector(`g.n[data-k="${CSS.escape(key)}"]`);
      if (!g) continue;
      const nd = chainCtx.ch.nodes.find(n => n.key === key), h = DIM.h(nd);
      g.insertAdjacentHTML('beforeend', `<rect class="selr" x="-3" y="-3" width="${DIM.w(nd.col) + 6}" height="${h + 6}" rx="7"/>`);
    }
  }
  function hotChain(key) {
    const svg = $('#chainSvg');
    if (!chainCtx) return;
    svg.querySelectorAll('.on').forEach(el => el.classList.remove('on'));
    if (!key) { svg.classList.remove('hot'); return; }
    const a = chainCtx.adj.get(key);
    if (!a) return;
    svg.classList.add('hot');
    const paths = svg.querySelectorAll('path.e');
    a.e.forEach(i => paths[i] && paths[i].classList.add('on'));
    a.n.forEach(k => { const g = svg.querySelector(`g.n[data-k="${CSS.escape(k)}"]`); if (g) g.classList.add('on'); });
  }

  // ------------------------------------------------------------------ detail panel (right)
  function selectedId() {
    if (route.view === 'chain') return route.sel || route.trail[route.trail.length - 1];
    if (route.view === 'overview') return ovSel;
    return null;
  }
  function valueBlock(v, unit) {
    if (Array.isArray(v)) {
      const rows = v.map(r => `<tr>${(Array.isArray(r) ? r : [r]).map(x => `<td class="num">${esc(M.fmt(x))}</td>`).join('')}</tr>`).join('');
      const head = unit && unit.includes(',') ? `<tr>${unit.split(',').map(u => `<th>${esc(u)}</th>`).join('')}</tr>` : '';
      return `<div class="tbl"><table class="kv">${head}${rows}</table></div>`;
    }
    return `<div class="big"><b>${esc(M.fmt(v))}</b><span>${esc(unit && unit !== '-' ? unit : '')}</span></div>`;
  }
  function marginBlock(n) {
    const lim = n.limit;
    const lv = lim.value !== undefined ? lim.value : lim.resolved;
    let html = `<div class="big"><b>${esc(M.fmt(n.value))}</b><span>${esc(n.unit && n.unit !== '-' ? n.unit : '')}</span>${marginBadge(n)}</div>
      <div class="text" style="margin:0">limit ${M.opText(lim.op)} ${esc(M.fmt(lv, n.unit))}${lim.ref ? ' from ' + go(lim.ref) : ''}</div>`;
    if (typeof n.value === 'number' && typeof lv === 'number' && typeof n.margin === 'number' && !n.margin_abs && n.value >= 0 && lv >= 0) {
      const top = Math.max(n.value, lv) * 1.15 || 1, col = n.margin < 0 ? 'var(--st-fail)' : n.margin < 0.1 ? 'var(--st-unverified)' : 'var(--st-verified)';
      html += `<div class="gauge" title="value vs limit"><i style="width:${100 * n.value / top}%;background:${col}"></i><u style="left:${100 * lv / top}%"></u></div>`;
    }
    return html;
  }
  function treeHtml(t, root) {
    const n = model.byId.get(t.id);
    const val = n.value !== undefined ? ` <span class="v">${esc(M.fmt(n.value, n.unit))}</span>` : '';
    const row = `<div class="row"><span class="dot" data-status="${st(n)}" title="${st(n)}"></span>` +
      (t.arg ? `<span class="arg">${esc(t.arg)} ←</span>` : '') + go(n.id) + ` <span>${esc(n.type === 'parameter' ? '' : n.title || '')}</span>${val}` +
      (t.repeat ? ' <span class="v">(above)</span>' : '') + '</div>';
    const kids = t.children.length ? `<ul>${t.children.map(c => `<li>${treeHtml(c)}</li>`).join('')}</ul>` : '';
    return root ? kids : row + kids;
  }
  function calcBody(c, highlightOut) {
    let h = c.equation ? `<div class="eq">${esc(c.equation)}</div>` : '';
    if (c.script) h += `<dl class="meta"><dt>Function</dt><dd>${repoLink(c.script, c.script.split('/').pop())} <code>${esc(c.function)}()</code></dd></dl>`;
    h += `<table class="kv"><tr><th>Input</th><th>Value</th><th>From</th></tr>` + Object.entries(c.inputs || {}).map(([arg, ref]) => {
      const r = model.byId.get(ref) || {};
      const used = c.input_values && arg in c.input_values ? c.input_values[arg] : r.value;
      return `<tr><td><code>${esc(arg)}</code></td><td class="num">${esc(M.fmt(used, (c.units || {})[arg] || r.unit))}</td><td>${go(ref)}</td></tr>`;
    }).join('') + `</table>`;
    h += `<table class="kv" style="margin-top:8px"><tr><th>Output</th><th>Value</th><th></th></tr>` + Object.entries(c.outputs || {}).map(([k, v]) =>
      `<tr><td><code>${esc(k)}</code></td><td class="num"${k === highlightOut ? ' style="font-weight:600"' : ''}>${esc(M.fmt(v, (c.units || {})[k]))}</td><td>${k === highlightOut ? '← this claim' : ''}</td></tr>`).join('') + `</table>`;
    const srcs = (model.into.get(c.id) || []).filter(e => model.byId.get(e.id).type === 'source').map(e => model.byId.get(e.id));
    if (srcs.length) h += `<h3 class="sec">Sources</h3>` + srcs.map(sourceRow).join('');
    return h;
  }
  const sourceRow = s => `<div class="row">${go(s.id)} ${s.url ? repoLink(s.url, s.title || s.url) : esc(s.title || '')}</div>`;
  function partBtn(id) {
    const href = M.partLink(model, id), p = model.byId.get(id);
    const name = p && p.title && p.title !== id ? ' · ' + esc(p.title) : '';
    return href ? `<a class="partbtn" href="${esc(href)}" target="_blank" rel="noopener" title="Open in the aircraft viewer">${esc(id)}${name} ↗</a>` : `<span class="partbtn">${esc(id)}${name}</span>`;
  }

  function renderDetail() {
    const box = $('#detail'), id = selectedId();
    if (!id || !model.byId.has(id)) {
      const meta = model.meta, c = meta.counts || { by_type: {} };
      box.innerHTML = `<div class="empty">
        <h2 class="dtitle" style="margin-top:0">How to read a proof chain</h2>
        <p>Evidence flows left to right: <b>sources</b> → <b>parameters and assumptions</b> → <b>calculations</b> → <b>claims</b> → <b>requirement</b>. Tests sit next to the calculations; they verify claims directly.</p>
        <ol><li>Pick a requirement on the left. Its chain opens in the middle.</li>
        <li>Click a box for its equation, inputs and sources here. Double-click a claim or an input to open its own chain.</li>
        <li>A red margin badge means the claim fails its limit today.</li>
        <li>Press <kbd>/</kbd> to search any id or title. <kbd>Esc</kbd> goes back.</li></ol>
        <dl class="meta"><dt>Built</dt><dd>${esc(meta.generated || '—')}</dd>
        <dt>Nodes</dt><dd>${model.nodes.length} (${Object.entries(c.by_type).map(([k, v]) => v + ' ' + k).join(', ')})</dd>
        <dt>Build</dt><dd>${issues.nDrift || issues.nOther ? `${issues.nDrift} drift · ${issues.nOther} other — <button class="lnk" data-status-open>see Status</button>` : 'every stored value re-computes'}</dd>
        <dt>Files</dt><dd>${(meta.files || []).length} claims files</dd></dl>
      </div>`;
      return;
    }
    const n = model.byId.get(id), t = n.type;
    const inChain = route.view === 'chain' && route.trail[route.trail.length - 1] === id;
    let h = `<div class="pills"><span class="tylab">${M.TYPE_LABEL[t]}</span>${badge(n)}</div><h2 class="dtitle">${esc(n.title || n.id)}</h2><div class="did">${esc(n.id)}</div>`;
    const acts = [];
    if (!inChain && t !== 'source') acts.push(`<button class="btn primary" data-focus="${esc(id)}">Open ${t === 'requirement' ? 'its' : 'this'} chain</button>`);
    if (route.view === 'overview') acts.push(`<button class="btn" data-open="${esc(id)}">Show in requirement chain</button>`);
    if (acts.length) h += `<div class="actions">${acts.join('')}</div>`;
    if (n.text) h += `<p class="text">${esc(n.text)}</p>`;
    if (n.reasons && n.reasons.length && t !== 'requirement') h += `<div class="reasons${n.fails ? ' fail' : ''}">${n.reasons.slice(0, 6).map(r => `<div title="${esc(r)}">${esc(short(r, 180))}</div>`).join('')}${n.reasons.length > 6 ? `<div>… ${n.reasons.length - 6} more</div>` : ''}</div>`;

    if (t === 'claim') {
      h += n.limit ? marginBlock(n) : valueBlock(n.value, n.unit);
      if (n.how) h += `<h3 class="sec">How to verify</h3><p class="text">${esc(n.how)}</p>`;
      const calc = model.byId.get(n.calc);
      if (calc) h += `<h3 class="sec">Calculation ${go(calc.id)}</h3>` + calcBody(calc, n.output);
      const tests = model.into.get(n.id).filter(e => e.type === 'verifies').map(e => model.byId.get(e.id));
      if (tests.length) h += `<h3 class="sec">Tests</h3>` + tests.map(x => `<div class="row">${go(x.id)} ${esc(x.title)} — ${esc(x.state)}${x.result ? ', ' + esc(x.result) : ''}${x.measured ? ', measured ' + esc(x.measured) : ''}</div>`).join('');
      const srcs = model.into.get(n.id).filter(e => model.byId.get(e.id).type === 'source').map(e => model.byId.get(e.id));
      if (srcs.length) h += `<h3 class="sec">Sources</h3>` + srcs.map(sourceRow).join('');
      if (n.parts && n.parts.length) h += `<h3 class="sec">Parts (open in the aircraft viewer)</h3>` + n.parts.map(p => partBtn(p)).join('');
    } else if (t === 'calculation') {
      h += calcBody(n);
    } else if (t === 'parameter') {
      h += valueBlock(n.value, n.unit);
      h += `<dl class="meta"><dt>File</dt><dd>${repoLink(n.file)}</dd>` +
        (n.source ? `<dt>Source</dt><dd>${[].concat(n.source).map(s => model.byId.has(s) ? go(s) + (model.byId.get(s).url ? ' · ' + repoLink(model.byId.get(s).url, 'link') : '') : esc(s)).join('<br>')}</dd>` : '') +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
    } else if (t === 'source') {
      h += `<dl class="meta"><dt>Kind</dt><dd>${esc(n.kind)}</dd>` + (n.url ? `<dt>Link</dt><dd>${repoLink(n.url)}</dd>` : '') +
        (n.where ? `<dt>Where</dt><dd>${esc(n.where)}</dd>` : '') + `<dt>Checked</dt><dd>${esc(n.checked || 'never')}</dd>` +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
      const used = (model.out.get(n.id) || []).map(e => e.id);
      if (used.length) h += `<h3 class="sec">Cited by (${used.length})</h3>` + used.slice(0, 40).map(u => `<div class="row">${go(u)}</div>`).join('');
    } else if (t === 'assumption') {
      if (n.value !== undefined) h += valueBlock(n.value, n.unit);
      h += `<dl class="meta"><dt>Basis</dt><dd>${esc(n.basis)}</dd></dl>`;
      const srcs = model.into.get(n.id).filter(e => model.byId.get(e.id).type === 'source').map(e => model.byId.get(e.id));
      if (srcs.length) h += `<h3 class="sec">Sources</h3>` + srcs.map(sourceRow).join('');
    } else if (t === 'test') {
      h += `<dl class="meta"><dt>State</dt><dd>${esc(n.state)}</dd>` + (n.result ? `<dt>Result</dt><dd>${esc(n.result)}</dd>` : '') +
        (n.measured ? `<dt>Measured</dt><dd>${esc(n.measured)}</dd>` : '') + (n.date ? `<dt>Date</dt><dd>${esc(n.date)}</dd>` : '') +
        (n.procedure ? `<dt>Procedure</dt><dd>${esc(n.procedure)}</dd>` : '') + (n.evidence ? `<dt>Evidence</dt><dd>${repoLink(n.evidence)}</dd>` : '') +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
    } else if (t === 'requirement') {
      const s = M.reqSummary(model, n.id);
      h += `<dl class="meta"><dt>Claims</dt><dd>${s.claims}${s.fails ? ` · <b style="color:var(--st-fail)">${s.fails} fail</b>` : ''}${s.unverified ? ` · ${s.unverified} unverified` : ''}</dd>` +
        (s.worst !== null ? `<dt>Worst margin</dt><dd>${marginBadge(s.worst)}</dd>` : '') +
        (n.ref ? `<dt>Defined in</dt><dd>${repoLink(n.ref)}</dd>` : '') + `<dt>Area</dt><dd>${esc(s.area)}</dd></dl>`;
      if (n.reasons && n.reasons.length) h += `<h3 class="sec">Why ${n.status}</h3><div class="reasons${n.fails ? ' fail' : ''}">${n.reasons.slice(0, 8).map(r => `<div>${esc(r)}</div>`).join('')}${n.reasons.length > 8 ? `<div>… ${n.reasons.length - 8} more</div>` : ''}</div>`;
    } else if (t === 'part') {
      h += partBtn(n.id);
      const cl = model.into.get(n.id).filter(e => e.type === 'about').map(e => model.byId.get(e.id));
      h += `<h3 class="sec">Claims about this part</h3>` + cl.map(c => `<div class="row">${go(c.id)} ${esc(c.title)} — ${st(c)}</div>`).join('');
    }
    if (n.note && !['parameter', 'source', 'test'].includes(t)) h += `<p class="text">${esc(n.note)}</p>`;
    if (t !== 'requirement' && t !== 'part') {
      const paths = M.pathsUp(model, n.id).filter(p => model.byId.get(p[p.length - 1]).type === 'requirement');
      h += `<h3 class="sec">Up to the requirement</h3>` + (paths.length ? paths.slice(0, 5).map(p => `<div class="path">${p.map(x => go(x)).join('<span class="sep">→</span>')}</div>`).join('')
        : `<div class="text">Not linked to a requirement.</div>`);
    }
    if (['claim', 'calculation'].includes(t)) {
      const tree = M.treeDown(model, n.id, 3);
      if (tree.children.length) h += `<h3 class="sec">Rests on (3 levels)</h3><ul class="tree">${treeHtml(tree, true)}</ul>`;
    }
    if (n.defined_in) h += `<h3 class="sec">Defined in</h3><div>${repoLink(n.defined_in)}</div>`;
    box.innerHTML = h;
    box.scrollTop = 0;
  }

  // ------------------------------------------------------------------ overview (whole graph, light)
  function ensureLib(m) {                             // load only the renderer in use (the 3-D bundle is 1.4 MB)
    return libLoaded[m] || (libLoaded[m] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = LIBS[m]; s.onload = res; s.onerror = () => rej(new Error('could not load ' + LIBS[m]));
      document.head.appendChild(s);
    }));
  }
  function webglOK() {
    try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
  }
  const layoutKey = () => 'layout.' + ovMode + '.' + (model.meta.generated || '') + '.' + model.nodes.length;
  let posCache = null;
  function loadPositions() {
    if (posCache && posCache.key === layoutKey()) return posCache.map;
    posCache = { key: layoutKey(), map: new Map() };
    try { const raw = store.get(posCache.key); if (raw) Object.entries(JSON.parse(raw)).forEach(([id, p]) => posCache.map.set(id, p)); } catch (e) { /* ignore */ }
    return posCache.map;
  }
  function savePositions(nodes) {
    const map = loadPositions(), obj = {};
    nodes.forEach(d => map.set(d.id, ovMode === '3d' ? [Math.round(d.x), Math.round(d.y), Math.round(d.z)] : [Math.round(d.x), Math.round(d.y)]));
    map.forEach((p, id) => { obj[id] = p; });
    store.set(posCache.key, JSON.stringify(obj));
  }
  function ovGraphData() {
    const vis = n => ovTypes.has(n.type), cache = loadPositions();
    const nodes = model.nodes.filter(vis).map(n => ({ id: n.id, n }));
    const byId = new Map(nodes.map(d => [d.id, d])), links = [], seen = new Set();
    const addLink = (s, t, type) => { const k = s + '>' + t; if (s !== t && !seen.has(k)) { seen.add(k); links.push({ source: s, target: t, type }); } };
    for (const e of model.edges) {
      if (byId.has(e.source) && byId.has(e.target)) addLink(e.source, e.target, e.type);
      else if (byId.has(e.source) && !byId.has(e.target) && ['parameter', 'assumption'].includes(model.byId.get(e.target).type)) {
        for (const o of model.out.get(e.target)) if (byId.has(o.id) && o.type !== 'about') addLink(e.source, o.id, 'via');   // source -> (hidden parameter) -> calc
      }
    }
    let missing = 0;
    for (const d of nodes) {
      const p = cache.get(d.id);
      if (p) { d.x = p[0]; d.y = p[1]; if (ovMode === '3d') d.z = p[2] || 0; d.fx = d.x; d.fy = d.y; if (ovMode === '3d') d.fz = d.z; }
      else missing++;
    }
    if (missing && missing < nodes.length) {                // new nodes start next to their placed neighbours
      const nb = new Map();
      links.forEach(l => { [[l.source, l.target], [l.target, l.source]].forEach(([a, b]) => { if (!nb.has(a)) nb.set(a, []); nb.get(a).push(b); }); });
      for (const d of nodes) if (d.x === undefined) {
        const ps = (nb.get(d.id) || []).map(id => byId.get(id)).filter(o => o.x !== undefined);
        if (ps.length) { d.x = ps.reduce((s, o) => s + o.x, 0) / ps.length + (Math.random() - 0.5) * 20; d.y = ps.reduce((s, o) => s + o.y, 0) / ps.length + (Math.random() - 0.5) * 20; }
      }
    }
    return { nodes, links, missing };
  }
  const nodeVal = d => (d.n.type === 'requirement' ? 7 : d.n.type === 'claim' ? 1.8 : 1);
  const baseColor = n => (n.fails ? pal.fail : pal.st[n.status]);
  const nodeColor = d => (hl && !hl.has(d.id) ? withAlpha(baseColor(d.n), 0.15) : baseColor(d.n));
  const idOf = x => (typeof x === 'object' ? x.id : x);
  const linkOn = l => hl && hl.has(idOf(l.source)) && hl.has(idOf(l.target));
  const linkColor = l => (linkOn(l) ? pal.accent : withAlpha(pal.line, hl ? 0.06 : 0.35));
  const statusVisible = d => ovStatus.statuses.has(d.n.status) && (!ovStatus.failsOnly || d.n.fails);
  const linkVisible = l => statusVisible(typeof l.source === 'object' ? l.source : { n: model.byId.get(l.source) }) && statusVisible(typeof l.target === 'object' ? l.target : { n: model.byId.get(l.target) });
  const wantsLabel = d => d.id === ovSel || d.id === hoverId || d.n.type === 'requirement';
  const shortTitle = n => { const t = n.title || n.id; return t.length > 28 ? t.slice(0, 27) + '…' : t; };
  let placed = [];                                    // label boxes drawn this frame (graph units), to skip overlaps
  function drawLabel(d, ctx, scale) {
    if (!statusVisible(d)) return;
    const big = d.id === ovSel || d.id === hoverId;
    if (!big && scale < 0.35) return;
    const fs = (big ? 12.5 : 11) / scale, r = Math.sqrt(nodeVal(d)) * 3;
    ctx.font = `${d.n.type === 'requirement' || big ? 600 : 400} ${fs}px ${pal.sans}`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    const txt = big ? d.id + ' · ' + shortTitle(d.n) : shortTitle(d.n);
    const w = ctx.measureText(txt).width, box = [d.x - w / 2, d.y + r, d.x + w / 2, d.y + r + fs * 1.3];
    if (!big && placed.some(b => b[0] < box[2] && box[0] < b[2] && b[1] < box[3] && box[1] < b[3])) return;
    placed.push(box);
    ctx.lineWidth = 3 / scale; ctx.strokeStyle = pal.bg; ctx.strokeText(txt, d.x, d.y + r + 2 / scale);
    ctx.fillStyle = hl && !hl.has(d.id) ? withAlpha(pal.fg3, 0.5) : pal.fg; ctx.fillText(txt, d.x, d.y + r + 2 / scale);
  }

  async function showOverview() {
    renderChips(); renderLegend();
    const want = ovMode + '|' + [...ovTypes].sort().join(',');
    if (G && ovBuiltFor === want) { const r = $('#graph').getBoundingClientRect(); if (r.width) G.width(r.width).height(r.height); refreshOv(); return; }
    ovStart = performance.now();
    $('#ovLoading').hidden = false;
    $('#ovLoading').textContent = 'Laying out the graph…';
    try { await ensureLib(ovMode); } catch (err) { $('#ovLoading').textContent = err.message; return; }
    await new Promise(r => requestAnimationFrame(() => setTimeout(r, 0)));   // let the "laying out" note paint first
    if (route.view !== 'overview') return;
    ovStart = ovStart || performance.now();
    buildGraph();
    ovBuiltFor = want;
  }
  let ovStart = 0;
  function ovReady() {                               // first frame after the (cached or warmed-up) layout is frozen
    $('#ovLoading').hidden = true;
    if (ovStart) { window.__ovReadyMs = performance.now() - ovStart; ovStart = 0; }
  }
  function buildGraph() {
    const t0 = performance.now();
    if (G && G._destructor) G._destructor();
    G = null;
    const el = $('#graph');
    el.innerHTML = '';
    const box = el.getBoundingClientRect(), data = ovGraphData();
    const fresh = data.missing === data.nodes.length, partial = data.missing > 0 && !fresh;
    const ticks = fresh ? (ovMode === '3d' ? 60 : 90) : partial ? 40 : 0;
    const common = g => g.width(box.width).height(box.height).backgroundColor(pal.bg).nodeId('id')
      .nodeLabel(d => `<div style="font:12px ${esc(pal.sans)};padding:2px 4px"><b>${esc(d.id)}</b> ${esc(d.n.title || '')}<br>${st(d.n)}${typeof d.n.margin === 'number' ? ' · margin ' + mgText(d.n) : ''}</div>`)
      .nodeVal(nodeVal).nodeColor(nodeColor).nodeVisibility(statusVisible).linkVisibility(linkVisible).linkColor(linkColor)
      .onNodeClick(d => ovSelect(d.id)).onBackgroundClick(() => ovSelect(null))
      .d3AlphaDecay(0.06).d3VelocityDecay(0.45).warmupTicks(ticks).cooldownTicks(0)
      .onEngineStop(() => { if (!G) return; const ns = G.graphData().nodes; ns.forEach(d => { d.fx = d.x; d.fy = d.y; if (ovMode === '3d') d.fz = d.z; }); savePositions(ns); if (!G.__fitted) { G.__fitted = true; const g = G; if (ovMode === '3d') setTimeout(() => g === G && G.zoomToFit(400, 20), 60); else G.zoomToFit(0, 30); } requestAnimationFrame(ovReady); });
    if (ovMode === '3d') {
      G = common(ForceGraph3D({ controlType: 'orbit' })(el)).nodeRelSize(3).nodeResolution(6).nodeOpacity(0.95).linkOpacity(0.35).showNavInfo(false)
        .linkWidth(l => (linkOn(l) ? 1.2 : 0)).onNodeHover(d => { hoverId = d ? d.id : null; el.style.cursor = d ? 'pointer' : ''; });
      $('#hint').textContent = 'drag to rotate · right-drag to pan · scroll to zoom · click a dot';
    } else {
      G = common(ForceGraph()(el)).nodeRelSize(3).linkWidth(l => (linkOn(l) ? 1.5 : 0.6))
        .nodeCanvasObjectMode(d => (wantsLabel(d) ? 'after' : undefined)).nodeCanvasObject(drawLabel)
        .onNodeHover(d => { hoverId = d ? d.id : null; el.style.cursor = d ? 'pointer' : ''; })
        .minZoom(0.05).maxZoom(12)
        .onRenderFramePre(() => { placed = []; });
      $('#hint').textContent = 'drag to pan · scroll to zoom · click a dot';
    }
    G.d3Force('charge').strength(-28).distanceMax(400);
    G.d3Force('link').distance(l => (l.type === 'verifies' ? 30 : 18)).strength(0.6);
    G.graphData(data);
    window.__ovBuildMs = performance.now() - t0;
    if (ovSel) ovSelect(ovSel, true);
  }
  function refreshOv() {
    if (!G) return;
    G.nodeColor(nodeColor).linkColor(linkColor).nodeVisibility(statusVisible).linkVisibility(linkVisible);
    if (ovMode === '3d') G.linkWidth(l => (linkOn(l) ? 1.2 : 0)); else G.linkWidth(l => (linkOn(l) ? 1.5 : 0.6));
  }
  function ovSelect(id, keepView) {
    ovSel = id && model.byId.has(id) ? id : null;
    hl = ovSel ? M.chain(model, ovSel) : null;
    refreshOv();
    if (!statusOpen) renderDetail();
    if (ovSel && !keepView && G && ovMode === '2d') {
      const d = G.graphData().nodes.find(x => x.id === ovSel);
      if (d && d.x !== undefined) G.centerAt(d.x, d.y, 500);
    }
  }
  const TY_DEFAULT_OFF = ['parameter', 'assumption', 'part'];
  function renderChips() {
    const cs = M.counts(model, 'status'), ct = M.counts(model, 'type'), fails = model.nodes.filter(n => n.fails).length;
    $('#typeChips').innerHTML = M.TYPES.filter(t => ct[t]).map(t =>
      `<button class="chip" data-type="${t}" aria-pressed="${ovTypes.has(t)}"><span class="dot"></span>${M.TYPE_LABEL[t]}<span class="n">${ct[t]}</span></button>`).join('');
    $('#statusChips').innerHTML = M.STATUSES.slice().reverse().filter(s => cs[s]).map(s =>
      `<button class="chip" data-st="${s}" data-status="${s}" aria-pressed="${ovStatus.statuses.has(s)}"><span class="dot"></span>${s}<span class="n">${cs[s]}</span></button>`).join('') +
      `<button class="chip" data-fails="1" data-status="FAIL" aria-pressed="${ovStatus.failsOnly}" title="Only nodes that fail (negative margin)"><span class="dot"></span>Fails only<span class="n">${fails}</span></button>`;
  }
  function renderLegend() {
    $('#legend').innerHTML = M.STATUSES.slice().reverse().map(s => `<div data-status="${s}"><i></i>${s}</div>`).join('') +
      `<div data-status="FAIL"><i></i>FAIL (negative margin)</div><div style="color:var(--fg-3)">large dots = requirements</div>`;
  }
  let typeTimer = 0;
  function rebuildSoon() {                            // debounce type toggles: one layout for a burst of clicks
    clearTimeout(typeTimer);
    typeTimer = setTimeout(() => { ovBuiltFor = ''; if (route.view === 'overview') showOverview(); }, 250);
  }

  // ------------------------------------------------------------------ search
  let results = [], cursor = 0;
  function renderResults(q) {
    const box = $('#results');
    box.classList.toggle('open', !!q);
    box.innerHTML = results.length ? results.map((n, i) => `<button role="option" aria-selected="${i === cursor}" data-i="${i}">
      <span class="ty">${M.TYPE_LABEL[n.type]}</span><span class="rid">${esc(n.id)}</span><span class="rt">${esc(n.title || '')}</span></button>`).join('')
      : `<div class="none">No id or title matches “${esc(q)}”.</div>`;
  }
  function pick(n) { results = []; $('#q').value = ''; renderResults(''); $('#q').blur(); statusOpen = false; openNode(n.id); }

  // ------------------------------------------------------------------ chrome
  function applyTheme(t) {
    if (t === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t);
    $('#theme').textContent = t === 'light' ? '☀' : t === 'dark' ? '☾' : '◐';
    $('#theme').title = 'Theme: ' + t + ' (click to change)';
    readPalette();
    if (G) { G.backgroundColor(pal.bg); refreshOv(); }
  }

  function wire() {
    document.addEventListener('click', e => {
      const t = e.target;
      const so = t.closest('[data-status-open]'), sc = t.closest('[data-status-close]');
      if (so) { statusOpen = true; renderStatus(); return; }
      if (sc) { statusOpen = false; renderDetail(); return; }
      const rq = t.closest('[data-req]');
      if (rq) { statusOpen = false; chainZoom = null; nav({ view: 'chain', trail: [rq.dataset.req] }); return; }
      const cr = t.closest('[data-crumb]');
      if (cr) { const i = +cr.dataset.crumb; chainZoom = null; nav(i < 0 ? { view: 'reqs' } : { view: 'chain', trail: route.trail.slice(0, i + 1) }); return; }
      const fo = t.closest('[data-focus]');
      if (fo) { statusOpen = false; const id = fo.dataset.focus; chainZoom = null;
        if (route.view === 'chain') nav({ view: 'chain', trail: route.trail.concat(id), sel: id }); else openNode(id); return; }
      const op = t.closest('[data-open]');
      if (op) { statusOpen = false; openNode(op.dataset.open); return; }
      const g = t.closest('[data-go]');
      if (g) {
        const id = g.dataset.go;
        if (!model.byId.has(id)) return;
        if (route.view === 'chain' && chainCtx && (chainCtx.L.pos.has(id) || chainCtx.L.pos.has('in:' + id)) && !statusOpen) { nav(Object.assign({}, route, { sel: id }), true); scrollToKey(chainCtx.L.pos.has(id) ? id : 'in:' + id); }
        else if (route.view === 'overview' && !statusOpen) ovSelect(id);
        else { statusOpen = false; openNode(id); }
        return;
      }
      const rf = t.closest('[data-rfilter]');
      if (rf) { rfilter = rf.dataset.rfilter; document.querySelectorAll('[data-rfilter]').forEach(b => b.setAttribute('aria-pressed', String(b === rf))); renderReqList(); return; }
      const vw = t.closest('[data-view]');
      if (vw) { statusOpen = false; nav({ view: vw.dataset.view === 'overview' ? 'overview' : 'reqs' }); return; }
      const ty = t.closest('[data-type]');
      if (ty) { const v = ty.dataset.type; ovTypes.has(v) ? ovTypes.delete(v) : ovTypes.add(v); if (!ovTypes.size) ovTypes.add('requirement'); renderChips(); rebuildSoon(); return; }
      const sb = t.closest('[data-st]');
      if (sb) { const s = sb.dataset.st, S = ovStatus.statuses; if (S.size === M.STATUSES.length) { S.clear(); S.add(s); } else if (S.has(s)) { S.delete(s); if (!S.size) M.STATUSES.forEach(x => S.add(x)); } else S.add(s); renderChips(); refreshOv(); return; }
      const fl = t.closest('[data-fails]');
      if (fl) { ovStatus.failsOnly = !ovStatus.failsOnly; renderChips(); refreshOv(); return; }
      const md = t.closest('[data-mode]');
      if (md) {
        if (md.dataset.mode === '3d' && !webglOK()) { $('#hint').textContent = 'WebGL is not available here; staying in 2D.'; return; }
        ovMode = md.dataset.mode; document.querySelectorAll('[data-mode]').forEach(b => b.setAttribute('aria-pressed', String(b === md)));
        ovBuiltFor = ''; showOverview(); return;
      }
      const tr = t.closest('tr[data-open]');
      if (tr) { openNode(tr.dataset.open); return; }
      const r = t.closest('#results button');
      if (r) pick(results[+r.dataset.i]);
    });
    // chain: click selects, double-click opens that node's own chain, hover lights its links
    const svg = $('#chainSvg');
    svg.addEventListener('click', e => {
      const g = e.target.closest('g.n');
      if (!g) return;
      const key = g.dataset.k, id = key.replace(/^in:/, '');
      statusOpen = false;
      nav(Object.assign({}, route, { sel: id }), true);
    });
    svg.addEventListener('dblclick', e => {
      const g = e.target.closest('g.n');
      if (!g) return;
      const id = g.dataset.k.replace(/^in:/, '');
      if (id === route.trail[route.trail.length - 1]) return;
      chainZoom = null;
      nav({ view: 'chain', trail: route.trail.concat(id), sel: id });
    });
    svg.addEventListener('mouseover', e => { const g = e.target.closest('g.n'); hotChain(g ? g.dataset.k : null); });
    svg.addEventListener('mouseleave', () => hotChain(null));
    $('#inputsBtn').onclick = () => nav(Object.assign({}, route, { inputs: $('#inputsBtn').dataset.next }));
    const zoomBy = f => { chainZoom = Math.min(2, Math.max(0.25, (chainCtx ? chainCtx.z : 1) * f)); applyZoom(); };
    $('#zoomIn').onclick = () => zoomBy(1.2);
    $('#zoomOut').onclick = () => zoomBy(1 / 1.2);
    $('#zoomFit').onclick = () => { if (!chainCtx) return; const b = $('#chainScroll'); chainZoom = Math.max(0.25, Math.min(1.5, (b.clientWidth - 4) / chainCtx.wN, (b.clientHeight - 4) / chainCtx.hN)); applyZoom(); };
    $('#chainScroll').addEventListener('wheel', e => { if (!e.ctrlKey) return; e.preventDefault(); zoomBy(e.deltaY < 0 ? 1.1 : 1 / 1.1); }, { passive: false });

    const themes = ['auto', 'light', 'dark'];
    $('#theme').onclick = () => { const t = themes[(themes.indexOf(store.get('theme') || 'auto') + 1) % 3]; store.set('theme', t); applyTheme(t); };
    const q = $('#q');
    q.addEventListener('input', () => { results = M.search(model, q.value, 12); cursor = 0; renderResults(q.value.trim()); });
    q.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { cursor = Math.min(cursor + 1, results.length - 1); renderResults(q.value.trim()); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { cursor = Math.max(cursor - 1, 0); renderResults(q.value.trim()); e.preventDefault(); }
      else if (e.key === 'Enter' && results[cursor]) pick(results[cursor]);
      else if (e.key === 'Escape') { q.value = ''; results = []; renderResults(''); q.blur(); }
    });
    q.addEventListener('blur', () => setTimeout(() => { results = []; renderResults(''); }, 150));
    document.addEventListener('keydown', e => {
      if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
      else if (e.key === 'Escape' && document.activeElement !== q) {
        if (statusOpen) { statusOpen = false; renderDetail(); }
        else if (route.view === 'chain' && route.trail.length > 1) nav({ view: 'chain', trail: route.trail.slice(0, -1) });
        else if (route.view === 'chain') nav({ view: 'reqs' });
        else if (route.view === 'overview' && ovSel) ovSelect(null);
      }
    });
    new ResizeObserver(() => {
      if (route.view === 'chain' && !chainZoom) applyZoom();
      const r = $('#graph').getBoundingClientRect();
      if (G && r.width) G.width(r.width).height(r.height);
    }).observe($('main'));
    window.addEventListener('hashchange', render);
  }

  // ------------------------------------------------------------------ start
  async function start() {
    const qs = new URLSearchParams(location.search);          // ?theme=dark / ?mode=3d make shareable links
    if (['auto', 'light', 'dark'].includes(qs.get('theme'))) store.set('theme', qs.get('theme'));
    applyTheme(qs.get('theme') || store.get('theme') || 'auto');
    if (qs.get('mode') === '3d' && webglOK()) { ovMode = '3d'; document.querySelectorAll('[data-mode]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.mode === '3d'))); }
    const data = await loadData();
    if (data.error) { $('#statusline').innerHTML = `<span class="sdot"></span><span>${data.error}</span>`; return; }
    model = M.build(data.g);
    issues = M.buildIssues(model.meta);
    $('#dataset').textContent = data.name === 'examples' ? 'demo aircraft (examples/)' : data.name;
    document.title = 'Proof Chain Explorer' + (data.name === 'examples' ? ' · demo' : '');
    renderStatusLine(data.note);
    renderHome();
    wire();
    render();
    window.__firstRenderMs = performance.now() - T0;
    document.documentElement.dataset.ready = '1';
  }
  start();
})();
