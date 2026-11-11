// app.js — the proof-chain viewer UI. Reads the graph written by build_graph.py (out/graph.js sets window.PROOF_GRAPH,
// so the page also works from file://). Renders with vendored 3d-force-graph (WebGL) or force-graph (2-D canvas).
// Data selection: ?data=examples | ?data=redesign | ?graph=<url of a graph.json>; default = redesign, else the demo.
(function () {
  'use strict';
  const M = window.ProofModel;
  const $ = s => document.querySelector(s);
  const esc = s => String(s === undefined || s === null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const store = {                                    // per-viewer conveniences only; the page works without them
    get(k) { try { return localStorage.getItem('proofs.' + k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem('proofs.' + k, v); } catch (e) { /* private mode */ } },
  };
  const REPO = '../../../';                          // viewer/ -> proofs/ -> redesign/ -> repo root
  const SOURCES = { redesign: 'data/graph.js', examples: 'data/graph.js' };

  let model = null, G = null, mode = '3d', colorBy = 'status', layout = 'free', selected = null, hl = null, hoverId = null;
  let pal = {}, labelEls = new Map(), rafId = 0, dataById = new Map();
  const LIBS = { '3d': 'vendor/3d-force-graph.min.js', '2d': 'vendor/force-graph.min.js' }, libLoaded = {};
  const filter = { statuses: new Set(M.STATUSES), types: new Set(M.TYPES.filter(t => t !== 'part')), failsOnly: false };

  // ------------------------------------------------------------------ data
  function loadScript(src) {
    return new Promise(res => {
      window.PROOF_GRAPH = undefined;
      const s = document.createElement('script');
      s.src = src;
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

  // ------------------------------------------------------------------ colours (read from the CSS tokens)
  function readPalette() {
    const cs = getComputedStyle(document.documentElement), v = n => cs.getPropertyValue(n).trim();
    pal = { st: {}, ty: {}, fails: v('--fails'), bg: v('--graph-bg'), link: v('--link'), accent: v('--accent'), text: v('--text'), faint: v('--faint') };
    M.STATUSES.forEach(s => { pal.st[s] = v('--st-' + s); });
    M.TYPES.forEach(t => { pal.ty[t] = v('--ty-' + t); });
  }
  const baseColor = n => colorBy === 'status' ? (n.fails ? pal.fails : pal.st[n.status]) : pal.ty[n.type];
  function withAlpha(hex, a) {
    const h = hex.replace('#', ''), f = h.length === 3 ? h.split('').map(c => c + c).join('') : h;
    const i = parseInt(f, 16);
    return `rgba(${(i >> 16) & 255},${(i >> 8) & 255},${i & 255},${a})`;
  }
  const nodeColor = d => hl && !hl.has(d.id) ? withAlpha(baseColor(d.n), 0.14) : baseColor(d.n);
  const linkOn = l => hl && hl.has(idOf(l.source)) && hl.has(idOf(l.target));
  const linkColor = l => linkOn(l) ? pal.accent : hl ? withAlpha(pal.faint, 0.08) : pal.link;
  const idOf = x => (typeof x === 'object' ? x.id : x);
  const nodeVal = d => {
    const imp = d.n.importance || 0;
    return d.n.type === 'requirement' ? 8 + imp : d.n.type === 'claim' ? 4 + imp : d.n.type === 'part' ? 1.5 : 1 + imp * 0.5;
  };
  const isVisible = d => M.visible(d.n, filter);

  // ------------------------------------------------------------------ renderer
  function webglOK() {
    try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); } catch (e) { return false; }
  }

  function graphData() {                              // fresh objects per renderer (the layout writes x, y, z into them)
    const nodes = model.nodes.map(n => ({ id: n.id, n }));
    dataById = new Map(nodes.map(d => [d.id, d]));
    return { nodes, links: model.edges.map(e => ({ source: e.source, target: e.target, type: e.type })) };
  }
  const linkVisible = l => isVisible(dataById.get(idOf(l.source))) && isVisible(dataById.get(idOf(l.target)));

  function ensureLib(m) {                             // load only the renderer in use (the 3-D bundle is 1.4 MB)
    return libLoaded[m] || (libLoaded[m] = new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = LIBS[m]; s.onload = res; s.onerror = () => rej(new Error('could not load ' + LIBS[m]));
      document.head.appendChild(s);
    }));
  }

  async function makeGraph() {
    await ensureLib(mode);
    if (G && G._destructor) G._destructor();
    G = null;
    $('#graph').innerHTML = '';
    $('#labels').innerHTML = '';
    labelEls = new Map();
    cancelAnimationFrame(rafId);
    const el = $('#graph'), box = el.getBoundingClientRect();
    const common = g => g
      .width(box.width).height(box.height)
      .backgroundColor(pal.bg)
      .nodeId('id')
      .nodeLabel(d => `<div style="font:12px system-ui;padding:2px 4px"><b>${esc(d.id)}</b> ${esc(d.n.title || '')}<br>${esc(d.n.status)}${d.n.fails ? ' · FAILS' : ''}</div>`)
      .nodeVal(nodeVal)
      .nodeColor(nodeColor)
      .nodeVisibility(isVisible)
      .linkVisibility(linkVisible)
      .linkColor(linkColor)
      .linkDirectionalArrowLength(l => (l.type === 'about' ? 0 : 3.2))
      .linkDirectionalArrowRelPos(1)
      .linkDirectionalArrowColor(linkColor)
      .linkDirectionalParticles(l => (linkOn(l) ? 2 : 0))
      .linkDirectionalParticleWidth(2.2)
      .linkDirectionalParticleColor(() => pal.accent)
      .onNodeClick(d => select(d.id, true))
      .onNodeHover(d => { hoverId = d ? d.id : null; el.style.cursor = d ? 'pointer' : ''; })
      .onBackgroundClick(() => select(null))
      .dagMode(layout === 'layered' ? 'bu' : null)            // bottom-up: sources at the bottom, requirements on top
      .dagLevelDistance(mode === '3d' ? 45 : 60)
      .onDagError(() => { layout = 'free'; setPressed('layout', 'free'); G.dagMode(null); banner('info', 'The graph has a cycle; layered layout is off.'); })
      .graphData(graphData());

    if (mode === '3d') {
      G = common(ForceGraph3D({ controlType: 'orbit' })(el))
        .nodeOpacity(0.95).nodeResolution(16).linkOpacity(0.9).showNavInfo(false)
        .linkWidth(l => (linkOn(l) ? 1.2 : 0));
      G.d3Force('charge').strength(-90);
      labelLoop();
      $('#hint').textContent = 'drag to rotate · right-drag to pan · scroll to zoom · click a node';
    } else {
      G = common(ForceGraph()(el))
        .nodeRelSize(4)
        .linkWidth(l => (linkOn(l) ? 1.6 : 0.8))
        .nodeCanvasObjectMode(() => 'replace')
        .nodeCanvasObject(draw2D)
        .nodePointerAreaPaint((d, color, ctx) => { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(d.x, d.y, radius2D(d) + 2, 0, 2 * Math.PI); ctx.fill(); });
      G.d3Force('charge').strength(-120);
      $('#hint').textContent = 'drag to pan · scroll to zoom · click a node';
    }
    G.d3Force('link').distance(l => (l.type === 'about' ? 22 : 34));
    setTimeout(() => { if (G && !selected) G.zoomToFit(600, 40, isVisible); }, 1600);
  }

  // 2-D: one shape per node type so type stays readable while colour shows status
  const radius2D = d => Math.sqrt(nodeVal(d)) * 3;
  function draw2D(d, ctx, scale) {
    const r = radius2D(d), c = nodeColor(d), t = d.n.type;
    ctx.fillStyle = c; ctx.strokeStyle = c; ctx.lineWidth = 1.5 / scale;
    ctx.beginPath();
    if (t === 'requirement') { ctx.moveTo(d.x, d.y - r * 1.25); ctx.lineTo(d.x + r * 1.25, d.y); ctx.lineTo(d.x, d.y + r * 1.25); ctx.lineTo(d.x - r * 1.25, d.y); ctx.closePath(); ctx.fill(); }
    else if (t === 'calculation' || t === 'part') { ctx.rect(d.x - r * 0.85, d.y - r * 0.85, r * 1.7, r * 1.7); ctx.fill(); }
    else if (t === 'source') { ctx.moveTo(d.x, d.y - r * 1.1); ctx.lineTo(d.x + r, d.y + r * 0.8); ctx.lineTo(d.x - r, d.y + r * 0.8); ctx.closePath(); ctx.fill(); }
    else if (t === 'assumption') { ctx.moveTo(d.x, d.y + r * 1.1); ctx.lineTo(d.x + r, d.y - r * 0.8); ctx.lineTo(d.x - r, d.y - r * 0.8); ctx.closePath(); ctx.fill(); }
    else if (t === 'test') { ctx.arc(d.x, d.y, r * 0.8, 0, 2 * Math.PI); ctx.lineWidth = 2.2 / scale; ctx.stroke(); }
    else { ctx.arc(d.x, d.y, r, 0, 2 * Math.PI); ctx.fill(); }
    if (d.id === selected) { ctx.beginPath(); ctx.arc(d.x, d.y, r * 1.6 + 2 / scale, 0, 2 * Math.PI); ctx.strokeStyle = pal.accent; ctx.lineWidth = 2 / scale; ctx.stroke(); }
    const show = d.id === selected || d.id === hoverId || (hl ? hl.has(d.id) && (scale > 1.2 || ['requirement', 'claim'].includes(t)) :
      t === 'requirement' || (t === 'claim' && scale > 0.9) || scale > 2.2);
    if (show) {
      const fs = Math.max(11 / scale, 2);
      ctx.font = `${t === 'requirement' ? 600 : 400} ${fs}px system-ui, sans-serif`;
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      ctx.fillStyle = hl && !hl.has(d.id) ? withAlpha(pal.faint, 0.4) : pal.text;
      ctx.fillText(labelText(d.n), d.x, d.y + r * 1.3 + 1 / scale);
    }
  }
  const labelText = n => (n.type === 'claim' && n.value !== undefined ? n.title + ' = ' + M.fmt(n.value, n.unit) : n.title || n.id);

  // 3-D labels: HTML overlay projected each frame (crisp text, no extra three.js objects)
  function labelLoop() {
    const layer = $('#labels');
    const step = () => {
      if (mode !== '3d' || !G) return;
      const cam = G.camera().position, nodes = G.graphData().nodes;
      const want = nodes.filter(d => isVisible(d) && d.x !== undefined && (d.id === selected || d.id === hoverId ||
        (hl ? hl.has(d.id) && hl.size < 60 : d.n.type === 'requirement' || (d.n.type === 'claim' && nodes.length < 400))));
      const dist = want.map(d => Math.hypot(d.x - cam.x, d.y - cam.y, d.z - cam.z));
      const near = Math.min(...dist), far = Math.max(...dist);
      const keep = new Set();
      want.forEach((d, i) => {
        const p = G.graph2ScreenCoords(d.x, d.y, d.z);
        let el = labelEls.get(d.id);
        if (!el) { el = document.createElement('div'); el.className = 'lbl'; layer.appendChild(el); labelEls.set(d.id, el); }
        el.textContent = labelText(d.n);
        el.className = 'lbl' + (d.n.type === 'requirement' ? ' req' : '') + (d.id === selected ? ' sel' : '');
        el.style.left = p.x + 'px'; el.style.top = (p.y + Math.sqrt(nodeVal(d)) * 1.5) + 'px';
        el.style.opacity = far > near ? (1 - 0.6 * (dist[i] - near) / (far - near)).toFixed(2) : '1';
        el.style.zIndex = String(1000 - Math.round(dist[i]));
        keep.add(d.id);
      });
      for (const [id, el] of labelEls) if (!keep.has(id)) { el.remove(); labelEls.delete(id); }
      rafId = requestAnimationFrame(step);
    };
    rafId = requestAnimationFrame(step);
  }

  function refresh() {                                      // re-evaluate colours / visibility after a state change
    if (!G) return;
    G.nodeColor(d => nodeColor(d)).linkColor(l => linkColor(l)).linkDirectionalArrowColor(l => linkColor(l))
      .linkDirectionalParticles(l => (linkOn(l) ? 2 : 0)).nodeVisibility(d => isVisible(d))
      .linkVisibility(l => linkVisible(l));
    if (mode === '3d') G.linkWidth(l => (linkOn(l) ? 1.2 : 0));
    else G.linkWidth(l => (linkOn(l) ? 1.6 : 0.8));
    renderLegend();
  }

  // ------------------------------------------------------------------ selection
  function select(id, fly) {
    selected = id && model.byId.has(id) ? id : null;
    hl = selected ? M.chain(model, selected) : null;
    if (selected) {                                         // make sure the chosen node is not filtered away
      const n = model.byId.get(selected);
      if (!M.visible(n, filter)) { filter.statuses.add(n.status); filter.types.add(n.type); filter.failsOnly = false; renderChips(); }
    }
    try { history.replaceState(null, '', selected ? '#node=' + encodeURIComponent(selected) : location.pathname + location.search); } catch (e) { /* file:// */ }
    refresh();
    renderDetail();
    renderList();
    if (fly && selected) setTimeout(() => focusNode(selected), 30);
  }

  function focusNode(id) {
    if (!G) return;
    const d = G.graphData().nodes.find(n => n.id === id);
    if (!d || d.x === undefined) return;
    if (mode === '3d') {
      const r = Math.hypot(d.x, d.y, d.z) || 1, k = 1 + 260 / r;   // stand 260 units off the node, looking at it
      G.cameraPosition({ x: d.x * k, y: d.y * k, z: d.z * k }, d, 900);
    } else { G.centerAt(d.x, d.y, 600); G.zoom(Math.max(G.zoom(), 2.2), 600); }
  }

  // ------------------------------------------------------------------ left panel
  function renderSummary() {
    const claims = model.nodes.filter(n => n.type === 'claim'), c = M.counts(model, 'status', 'claim');
    const fails = claims.filter(n => n.fails).length;
    $('#summary').innerHTML = `<div class="bar">${M.STATUSES.slice().reverse().map(s => c[s] ? `<i title="${s} ${c[s]}" style="width:${100 * c[s] / claims.length}%;background:${pal.st[s]}"></i>` : '').join('')}</div>
      <small><b>${claims.length}</b> claims · ${M.STATUSES.slice().reverse().filter(s => c[s]).map(s => `${c[s]} ${s.toLowerCase()}`).join(' · ')}${fails ? ` · <b style="color:${pal.fails}">${fails} fail${fails > 1 ? 's' : ''}</b>` : ''}</small>`;
  }

  function chipClick(set, all, value) {           // first click solos a value; later clicks add/remove; empty = all
    if (set.size === all.length) { set.clear(); set.add(value); }
    else if (set.has(value)) { set.delete(value); if (!set.size) all.forEach(v => set.add(v)); }
    else set.add(value);
  }

  function renderChips() {
    const cs = M.counts(model, 'status'), ct = M.counts(model, 'type'), fails = model.nodes.filter(n => n.fails).length;
    $('#statusChips').innerHTML = M.STATUSES.slice().reverse().map(s =>
      `<button class="chip" data-status="${s}" aria-pressed="${filter.statuses.has(s)}"><span class="dot" style="background:${pal.st[s]}"></span>${s}<span class="n">${cs[s] || 0}</span></button>`).join('') +
      `<button class="chip" data-fails="1" aria-pressed="${filter.failsOnly ? 'true' : 'false'}" title="Only nodes with a negative margin or a failed test"><span class="dot" style="background:${pal.fails}"></span>Fails only<span class="n">${fails}</span></button>`;
    $('#typeChips').innerHTML = M.TYPES.filter(t => ct[t]).map(t =>
      `<button class="chip" data-type="${t}" aria-pressed="${filter.types.has(t)}"><span class="dot" style="background:${pal.ty[t]}"></span>${M.TYPE_LABEL[t]}<span class="n">${ct[t]}</span></button>`).join('');
  }

  function renderList() {
    const item = (n, indent) => {
      const m = n.margin !== undefined && n.margin !== null ? `<span class="m${n.margin < 0 ? ' neg' : ''}">${M.pct(n.margin)}</span>` : '<span class="m"></span>';
      return `<button class="item${n.id === selected ? ' sel' : ''}" data-go="${esc(n.id)}" style="${indent ? 'margin-left:14px' : ''}">
        <span class="dot" style="background:${n.fails ? pal.fails : pal.st[n.status]}"></span>
        <span class="t" title="${n.fails ? 'FAILS' : n.status}">${esc(n.title)}<small>${esc(n.id)}</small></span>${m}</button>`;
    };
    const shown = n => M.visible(n, filter);
    const reqs = model.nodes.filter(n => n.type === 'requirement').sort((a, b) => M.STATUSES.indexOf(a.status) - M.STATUSES.indexOf(b.status) || a.id.localeCompare(b.id));
    let html = '';
    const listed = new Set();
    for (const r of reqs) {
      const cl = model.into.get(r.id).filter(e => e.type === 'verifies').map(e => model.byId.get(e.id)).filter(shown);
      if (!shown(r) && !cl.length) continue;
      html += item(r, false) + cl.map(c => { listed.add(c.id); return item(c, true); }).join('');
    }
    const loose = model.nodes.filter(n => n.type === 'claim' && !listed.has(n.id) && shown(n) && !(model.out.get(n.id) || []).some(e => e.type === 'verifies'));
    if (loose.length) html += '<h3>Not tied to a requirement</h3>' + loose.map(c => item(c, false)).join('');
    const others = model.nodes.filter(n => !['requirement', 'claim'].includes(n.type) && shown(n));
    if (others.length && others.length < model.nodes.length) {
      html += `<h3>Other matching nodes (${others.length})</h3>` + others.slice(0, 60).map(n => item(n, false)).join('');
    }
    $('#list').innerHTML = html || '<div class="empty">Nothing matches the filters.</div>';
  }

  function renderLegend() {
    const rows = colorBy === 'status'
      ? M.STATUSES.slice().reverse().map(s => [pal.st[s], s]).concat([[pal.fails, 'FAILS (negative margin)']])
      : M.TYPES.filter(t => filter.types.has(t) && model.nodes.some(n => n.type === t)).map(t => [pal.ty[t], M.TYPE_LABEL[t]]);
    $('#legend').innerHTML = rows.map(([c, t]) => `<div><i style="background:${c}"></i>${t}</div>`).join('') +
      `<div style="margin-top:3px;color:var(--faint)">size = claims resting on it</div>`;
  }

  // ------------------------------------------------------------------ detail panel
  const go = (id, label) => `<button class="nlink" data-go="${esc(id)}">${esc(label || id)}</button>`;
  const pill = n => `<span class="pill solid" style="background:${pal.st[n.status]}">${n.status}</span>` + (n.fails ? `<span class="pill solid" style="background:${pal.fails}">FAILS</span>` : '');
  const typePill = n => `<span class="pill" style="color:${pal.ty[n.type]}">${M.TYPE_LABEL[n.type].toUpperCase()}</span>`;
  const repoLink = (p, label) => /^https?:/.test(p) ? `<a href="${esc(p)}" target="_blank" rel="noopener">${esc(label || p)}</a>` : `<a href="${esc(REPO + p)}" target="_blank" rel="noopener">${esc(label || p)}</a>`;

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
    if (!lim) return '';
    const lv = lim.value !== undefined ? lim.value : lim.resolved;
    let html = `<div class="big"><b>${esc(M.fmt(n.value))}</b><span>${esc(n.unit && n.unit !== '-' ? n.unit : '')}</span></div>
      <div class="text" style="margin:0;color:var(--muted)">limit ${M.opText(lim.op)} ${esc(M.fmt(lv, n.unit))}${lim.ref ? ' from ' + go(lim.ref) : ''}</div>`;
    if (typeof n.value === 'number' && typeof lv === 'number' && n.margin !== undefined && n.margin !== null) {
      const top = Math.max(n.value, lv) * 1.15, col = n.margin < 0 ? pal.fails : n.margin < 0.1 ? pal.st.UNVERIFIED : pal.st.VERIFIED;
      html += `<div class="gauge" title="value vs limit"><i style="width:${100 * n.value / top}%;background:${col}"></i><u style="left:${100 * lv / top}%"></u></div>
        <div style="font-size:13px;color:${col};font-weight:600">margin ${M.pct(n.margin)}</div>`;
    }
    return html;
  }

  function treeHtml(t, root) {
    const n = model.byId.get(t.id);
    const val = n.value !== undefined && n.type !== 'claim' ? ` <span class="v">${esc(M.fmt(n.value, n.unit))}</span>` : n.type === 'claim' ? ` <span class="v">${esc(M.fmt(n.value, n.unit))}</span>` : '';
    const row = `<div class="row"><span class="dot" style="background:${n.fails ? pal.fails : pal.st[n.status]}" title="${n.status}"></span>` +
      (t.arg ? `<span class="arg">${esc(t.arg)} ←</span>` : '') + go(n.id) + ` <span>${esc(n.type === 'parameter' ? '' : n.title || '')}</span>${val}` +
      (t.repeat ? ' <span class="v">(above)</span>' : '') + '</div>';
    const kids = t.children.length ? `<ul>${t.children.map(c => `<li>${treeHtml(c)}</li>`).join('')}</ul>` : '';
    return root ? kids : row + kids;
  }

  function renderDetail() {
    const box = $('#detail');
    if (!selected) {
      const meta = model.meta, c = meta.counts || { by_type: {} };
      box.innerHTML = `<div class="empty">
        <div class="pills"><span class="pill" style="color:var(--muted)">${esc(meta.dataset || '')}</span></div>
        <h2 class="dtitle">How to read this graph</h2>
        <p>Evidence flows along the arrows: <b style="color:${pal.ty.source}">sources</b> → <b style="color:${pal.ty.parameter}">parameters</b> → <b style="color:${pal.ty.calculation}">calculations</b> → <b style="color:${pal.ty.claim}">claims</b> → <b style="color:${pal.ty.requirement}">requirements</b>.</p>
        <ol><li>Click a node to see its equation, inputs, sources and the chain up to its requirement.</li>
        <li>Click a status chip to show only that status — e.g. <b>UNVERIFIED</b> lists everything still to check.</li>
        <li>Press <kbd>/</kbd> to search. <kbd>Esc</kbd> clears the selection.</li></ol>
        <dl class="meta"><dt>Built</dt><dd>${esc(meta.generated || '—')}</dd>
        <dt>Nodes</dt><dd>${model.nodes.length} (${Object.entries(c.by_type).map(([k, v]) => v + ' ' + k).join(', ')})</dd>
        <dt>Files</dt><dd>${(meta.files || []).map(f => repoLink(f)).join('<br>') || '—'}</dd>
        <dt>Build</dt><dd>${meta.ok ? 'every stored number re-computes' : `<b style="color:${pal.fails}">${(meta.errors || []).length} error(s)</b>`}</dd></dl>
        ${(meta.errors || []).length ? `<div class="reasons fail">${meta.errors.map(e => `<div>${esc(e)}</div>`).join('')}</div>` : ''}
        ${(meta.warnings || []).length ? `<h3>Warnings</h3><div class="reasons">${meta.warnings.map(e => `<div>${esc(e)}</div>`).join('')}</div>` : ''}
      </div>`;
      return;
    }
    const n = model.byId.get(selected), t = n.type;
    let h = `<div class="pills">${typePill(n)}${pill(n)}</div><h2 class="dtitle">${esc(n.title || n.id)}</h2><div class="did">${esc(n.id)}</div>`;
    if (n.text) h += `<p class="text">${esc(n.text)}</p>`;
    if (n.reasons && n.reasons.length) h += `<div class="reasons${n.fails ? ' fail' : ''}">${n.reasons.map(r => `<div>${esc(r)}</div>`).join('')}</div>`;

    if (t === 'claim') {
      h += n.limit ? marginBlock(n) : valueBlock(n.value, n.unit);
      if (n.how) h += `<h3>How to verify</h3><p class="text">${esc(n.how)}</p>`;
      const calc = model.byId.get(n.calc);
      if (calc) h += `<h3>Calculation ${go(calc.id)}</h3>` + calcBody(calc, n.output);
      const tests = model.into.get(n.id).filter(e => e.type === 'verifies').map(e => model.byId.get(e.id));
      if (tests.length) h += `<h3>Tests</h3>` + tests.map(x => `<div class="row">${go(x.id)} ${esc(x.title)} — ${esc(x.state)}${x.result ? ', ' + esc(x.result) : ''}${x.measured ? ', measured ' + esc(x.measured) : ''}</div>`).join('');
      if (n.parts && n.parts.length) h += `<h3>Parts (open in the aircraft viewer)</h3>` + n.parts.map(p => partBtn(p)).join('');
    } else if (t === 'calculation') {
      h += calcBody(n);
    } else if (t === 'parameter') {
      h += valueBlock(n.value, n.unit);
      h += `<dl class="meta"><dt>File</dt><dd>${repoLink(n.file)}</dd>` +
        (n.source ? `<dt>Source</dt><dd>${[].concat(n.source).map(s => model.byId.has(s) ? go(s) : esc(s)).join(', ')}</dd>` : '') +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
    } else if (t === 'source') {
      h += `<dl class="meta"><dt>Kind</dt><dd>${esc(n.kind)}</dd>` + (n.url ? `<dt>Link</dt><dd>${repoLink(n.url)}</dd>` : '') +
        (n.where ? `<dt>Where</dt><dd>${esc(n.where)}</dd>` : '') + `<dt>Checked</dt><dd>${esc(n.checked || 'never')}</dd>` +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
    } else if (t === 'assumption') {
      if (n.value !== undefined) h += valueBlock(n.value, n.unit);
      h += `<dl class="meta"><dt>Basis</dt><dd>${esc(n.basis)}</dd></dl>`;
    } else if (t === 'test') {
      h += `<dl class="meta"><dt>State</dt><dd>${esc(n.state)}</dd>` + (n.result ? `<dt>Result</dt><dd>${esc(n.result)}</dd>` : '') +
        (n.measured ? `<dt>Measured</dt><dd>${esc(n.measured)}</dd>` : '') + (n.date ? `<dt>Date</dt><dd>${esc(n.date)}</dd>` : '') +
        (n.procedure ? `<dt>Procedure</dt><dd>${esc(n.procedure)}</dd>` : '') + (n.evidence ? `<dt>Evidence</dt><dd>${repoLink(n.evidence)}</dd>` : '') +
        (n.note ? `<dt>Note</dt><dd>${esc(n.note)}</dd>` : '') + '</dl>';
    } else if (t === 'requirement') {
      if (n.ref) h += `<dl class="meta"><dt>Defined in</dt><dd>${repoLink(n.ref)}</dd></dl>`;
    } else if (t === 'part') {
      h += partBtn(n.id);
      const cl = model.into.get(n.id).filter(e => e.type === 'about').map(e => model.byId.get(e.id));
      h += `<h3>Claims about this part</h3>` + cl.map(c => `<div class="row">${go(c.id)} ${esc(c.title)} — ${c.fails ? 'FAILS' : c.status}</div>`).join('');
    }
    if (n.note && !['parameter', 'source', 'test'].includes(t)) h += `<p class="text" style="color:var(--muted)">${esc(n.note)}</p>`;

    // chain up to the requirement(s)
    if (t !== 'requirement' && t !== 'part') {
      const paths = M.pathsUp(model, n.id).filter(p => model.byId.get(p[p.length - 1]).type === 'requirement');
      h += `<h3>Up to the requirement</h3>` + (paths.length ? paths.map(p => `<div class="path">${p.map(id => go(id)).join('<span class="sep">→</span>')}</div>`).join('')
        : `<div class="text" style="color:var(--muted)">Not linked to a requirement.</div>`);
    }
    // chain down to the sources
    if (!['source', 'part'].includes(t)) {
      const tree = M.treeDown(model, n.id, 8);
      if (tree.children.length) h += `<h3>Rests on</h3><ul class="tree">${treeHtml(tree, true)}</ul>`;
    }
    if (n.defined_in) h += `<h3>Defined in</h3><div>${repoLink(n.defined_in)}</div>`;
    box.innerHTML = h;
    box.scrollTop = 0;
  }

  function calcBody(c, highlightOut) {
    let h = c.equation ? `<div class="eq">${esc(c.equation)}</div>` : '';
    h += `<dl class="meta"><dt>Function</dt><dd>${repoLink(c.script, c.script.split('/').pop())} <code>${esc(c.function)}()</code></dd></dl>`;
    h += `<table class="kv"><tr><th>Input</th><th>Value</th><th>From</th></tr>` + Object.entries(c.inputs || {}).map(([arg, ref]) => {
      const r = model.byId.get(ref) || {};
      const used = c.input_values && arg in c.input_values ? c.input_values[arg] : r.value;
      return `<tr><td><code>${esc(arg)}</code></td><td class="num">${esc(M.fmt(used, (c.units || {})[arg] || r.unit))}</td><td>${go(ref)}</td></tr>`;
    }).join('') + `</table>`;
    h += `<table class="kv" style="margin-top:8px"><tr><th>Output</th><th>Value</th><th></th></tr>` + Object.entries(c.outputs || {}).map(([k, v]) =>
      `<tr><td><code>${esc(k)}</code></td><td class="num"${k === highlightOut ? ' style="font-weight:600"' : ''}>${esc(M.fmt(v, (c.units || {})[k]))}</td><td>${k === highlightOut ? '← this claim' : ''}</td></tr>`).join('') + `</table>`;
    return h;
  }

  function partBtn(id) {
    const href = M.partLink(model, id), p = model.byId.get(id);
    const name = p && p.title && p.title !== id ? ' · ' + esc(p.title) : '';
    return href ? `<a class="partbtn" href="${esc(href)}" target="_blank" rel="noopener" title="Open in the aircraft viewer">${esc(id)}${name} ↗</a>` : `<span class="partbtn">${esc(id)}${name}</span>`;
  }

  // ------------------------------------------------------------------ search
  let results = [], cursor = 0;
  function renderResults() {
    const box = $('#results');
    box.classList.toggle('open', results.length > 0);
    box.innerHTML = results.map((n, i) => `<button role="option" aria-selected="${i === cursor}" data-i="${i}">
      <span class="dot" style="width:8px;height:8px;border-radius:50%;flex:none;background:${n.fails ? pal.fails : pal.st[n.status]}"></span>
      <span class="rid">${esc(n.id)}</span><span class="rt">${esc(n.title || '')}</span></button>`).join('');
  }
  function pick(n) { results = []; renderResults(); $('#q').value = ''; $('#q').blur(); select(n.id, true); }

  // ------------------------------------------------------------------ chrome
  function banner(kind, html) {                       // click to dismiss; info notes fade after 10 s
    const b = $('#banner'); b.className = 'banner ' + kind; b.innerHTML = html || '';
    b.onclick = e => { if (!e.target.closest('a')) b.innerHTML = ''; };
    b.title = 'click to dismiss';
    if (kind === 'info') setTimeout(() => { if (b.innerHTML === html) b.innerHTML = ''; }, 10000);
  }
  function setPressed(attr, value) { document.querySelectorAll(`[data-${attr}]`).forEach(b => b.setAttribute('aria-pressed', String(b.dataset[attr] === value))); }
  function applyTheme(t) {
    if (t === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t);
    $('#theme').textContent = t === 'light' ? '☀' : t === 'dark' ? '☾' : '◐';
    $('#theme').title = 'Theme: ' + t + ' (click to change)';
    readPalette();
    if (G) G.backgroundColor(pal.bg);
    if (model) { renderSummary(); renderChips(); renderList(); renderDetail(); refresh(); }
  }

  function wire() {
    document.addEventListener('click', e => {
      const goBtn = e.target.closest('[data-go]');
      if (goBtn) { select(goBtn.dataset.go, true); return; }
      const st = e.target.closest('[data-status]'), ty = e.target.closest('[data-type]'), fl = e.target.closest('[data-fails]');
      if (st) { chipClick(filter.statuses, M.STATUSES, st.dataset.status); }
      else if (ty) { chipClick(filter.types, M.TYPES, ty.dataset.type); }
      else if (fl) { filter.failsOnly = !filter.failsOnly; }
      if (st || ty || fl) { renderChips(); renderList(); refresh(); return; }
      const r = e.target.closest('#results button');
      if (r) pick(results[+r.dataset.i]);
    });
    $('#resetStatus').onclick = () => { M.STATUSES.forEach(s => filter.statuses.add(s)); filter.failsOnly = false; renderChips(); renderList(); refresh(); };
    $('#resetType').onclick = () => { M.TYPES.forEach(t => filter.types.add(t)); renderChips(); renderList(); refresh(); };
    document.querySelectorAll('[data-color]').forEach(b => b.onclick = () => { colorBy = b.dataset.color; setPressed('color', colorBy); store.set('color', colorBy); refresh(); });
    document.querySelectorAll('[data-layout]').forEach(b => b.onclick = () => {
      layout = b.dataset.layout; setPressed('layout', layout);
      G.dagMode(layout === 'layered' ? 'bu' : null); G.d3ReheatSimulation();
      setTimeout(() => G.zoomToFit(600, 40, isVisible), 1400);
    });
    document.querySelectorAll('[data-mode]').forEach(b => b.onclick = () => {
      if (b.dataset.mode === '3d' && !webglOK()) { banner('info', 'WebGL is not available here; staying in 2D.'); return; }
      mode = b.dataset.mode; setPressed('mode', mode); store.set('mode', mode);
      makeGraph().then(refresh).catch(err => banner('err', esc(err.message)));
    });
    const themes = ['auto', 'light', 'dark'];
    $('#theme').onclick = () => { const t = themes[(themes.indexOf(store.get('theme') || 'auto') + 1) % 3]; store.set('theme', t); applyTheme(t); };
    const q = $('#q');
    q.addEventListener('input', () => { results = M.search(model, q.value, 12); cursor = 0; renderResults(); });
    q.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { cursor = Math.min(cursor + 1, results.length - 1); renderResults(); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { cursor = Math.max(cursor - 1, 0); renderResults(); e.preventDefault(); }
      else if (e.key === 'Enter' && results[cursor]) pick(results[cursor]);
      else if (e.key === 'Escape') { q.value = ''; results = []; renderResults(); q.blur(); }
    });
    q.addEventListener('blur', () => setTimeout(() => { results = []; renderResults(); }, 150));
    document.addEventListener('keydown', e => {
      if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
      else if (e.key === 'Escape' && document.activeElement !== q) select(null);
    });
    new ResizeObserver(() => { const r = $('#graph').getBoundingClientRect(); if (G && r.width) G.width(r.width).height(r.height); }).observe($('main'));
    window.addEventListener('hashchange', () => { const m = location.hash.match(/node=([^&]+)/); if (m) select(decodeURIComponent(m[1]), true); });
  }

  // ------------------------------------------------------------------ start
  async function start() {
    const qs = new URLSearchParams(location.search);          // ?mode=2d / ?theme=dark make shareable links
    if (['auto', 'light', 'dark'].includes(qs.get('theme'))) store.set('theme', qs.get('theme'));
    applyTheme(qs.get('theme') || store.get('theme') || 'auto');
    const data = await loadData();
    if (data.error) { banner('err', data.error); return; }
    model = M.build(data.g);
    $('#dataset').textContent = data.name === 'examples' ? 'demo aircraft (examples/)' : data.name;
    document.title = 'Proof Chain Explorer' + (data.name === 'examples' ? ' · demo' : '');
    if (!model.meta.ok) banner('err', `<b>Build failed</b> — ${model.meta.errors.length} error(s); stored numbers may be stale. Details in the right panel.`);
    else if (data.note) banner('info', data.note);
    colorBy = store.get('color') || 'status'; setPressed('color', colorBy);
    if (qs.get('layout') === 'layered') { layout = 'layered'; setPressed('layout', layout); }
    mode = qs.get('mode') || store.get('mode') || (webglOK() && (navigator.hardwareConcurrency || 4) > 2 ? '3d' : '2d');
    if (mode === '3d' && !webglOK()) mode = '2d';
    setPressed('mode', mode);
    renderSummary(); renderChips(); renderList(); renderLegend(); renderDetail();
    wire();
    try { await makeGraph(); } catch (err) { banner('err', esc(err.message)); return; }
    const m = location.hash.match(/node=([^&]+)/);
    if (m) setTimeout(() => select(decodeURIComponent(m[1]), true), 1200);
  }
  start();
})();
