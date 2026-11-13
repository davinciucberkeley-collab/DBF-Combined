// K09-L explorer shell: hash router (#aircraft #decision #team #subsystems #simulations #status #docs), theme toggle,
// the decision page's morphological chart and concept table (logic from redesign/config-study/web/index.html),
// the render / plot lightbox, and the 3-D explorer (viewer.js). Everything is relative: works on GitHub Pages and as an artifact.
import { DIMS, C } from './data/concepts.js?v=20261111d';
import { start as startViewer, viewer } from './viewer.js?v=20261112b';

const ROUTES = ['aircraft', 'decision', 'team', 'subsystems', 'simulations', 'build', 'proof', 'status', 'bom', 'docs'];
const TITLES = { aircraft: 'Aircraft', decision: 'Decision', team: 'Team', subsystems: 'Subsystems', simulations: 'Simulations', build: 'Build guide', proof: 'Proof chain', status: 'Status', bom: 'BOM', docs: 'Docs' };
const GH_ROOT = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/';
const store = { get(k) { try { return localStorage.getItem('k09l.' + k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem('k09l.' + k, v); } catch (e) { /* storage blocked: fine */ } } };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

// ---------------- theme ----------------
const root = document.documentElement, themeBtn = document.getElementById('theme');
function isDark() { const t = root.getAttribute('data-theme'); return t ? t === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches); }
function paintTheme() { themeBtn.innerHTML = '<svg><use href="#i-' + (isDark() ? 'sun' : 'moon') + '"/></svg>'; }
{ const t = store.get('theme'); if (t === 'light' || t === 'dark') root.setAttribute('data-theme', t); }
themeBtn.addEventListener('click', () => { const next = isDark() ? 'light' : 'dark'; root.setAttribute('data-theme', next); store.set('theme', next); paintTheme(); viewer.themeChanged(); if (window.ProofEmbed) window.ProofEmbed.themeChanged(); });
if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', paintTheme);
paintTheme();

// ---------------- router ----------------
let current = null, lastOutside = '#aircraft', hops = 0, focusPartId = null;
function route() {
  let name = decodeURIComponent(location.hash.replace(/^#\/?/, '')) || 'aircraft', target = null;
  // #proof, #proof-overview, #proof-<node id>: the proof chain page; #part-<id>: the 3-D explorer with that part selected
  if (/^proof(-|$)/.test(name)) { if (current !== null) hops++; name = 'proof'; }
  else if (/^part-/.test(name)) { focusPartId = name.slice(5); name = 'aircraft'; }
  else if (current !== null) hops = 0;
  if (!ROUTES.includes(name)) {
    const el = document.getElementById(name), v = el && el.closest('.view');
    if (v) { target = el; name = v.id; } else name = 'aircraft';
  }
  document.querySelectorAll('main > .view').forEach(v => { v.hidden = v.id !== name; });
  document.querySelectorAll('#nav a').forEach(a => { if (a.getAttribute('href') === '#' + name) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current'); });
  document.body.dataset.route = name;
  document.title = 'K09-L · ' + TITLES[name];
  if (target) target.scrollIntoView({ block: 'start' }); else if (current !== name) window.scrollTo(0, 0);
  current = name;
  if (name === 'proof') enterProof(); else lastOutside = name === 'aircraft' ? '#aircraft' : location.hash;
  if (name === 'build') { watchBuildToc(); const h = hydrateBuild(); if (target) h.then(() => target.scrollIntoView({ block: 'start', behavior: 'instant' })); }
  if (name === 'aircraft') { viewer.resize(); if (focusPartId) focusPart(focusPartId); focusPartId = null; }
  if (name === 'decision') redrawMorph();
}
window.addEventListener('hashchange', route);

// ---------------- proof chain, in the page (proofs/app.js in embedded mode; the 7 MB graph loads on first visit) ----------------
function loadScript(src) { return new Promise((ok, no) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = () => no(new Error(src)); document.head.appendChild(s); }); }
function enterProof() {
  if (window.ProofEmbed && window.ProofEmbed.ready) { window.ProofEmbed.render(); return; }
  if (window.PROOF_EMBED) return;                           // loading; app.js renders from the hash when the graph is in
  const home = document.getElementById('home');
  if (home) home.innerHTML = '<p class="sub">Loading the proof graph (about 7 MB, once)…</p>';
  window.PROOF_EMBED = { root: document.getElementById('proofapp'), base: 'proofs/', repo: GH_ROOT };
  loadScript('proofs/model.js?v=20261112a').then(() => loadScript('proofs/app.js?v=20261112a'))
    .catch(e => { if (home) home.innerHTML = '<p class="sub">Could not load ' + esc(e.message) + '. The standalone viewer is <a href="proofs/index.html">proofs/index.html</a>.</p>'; });
}
document.addEventListener('click', e => {
  if (e.target.closest('[data-pclose]')) { location.hash = lastOutside; }
  else if (e.target.closest('[data-pback]')) { if (hops > 0) { hops--; history.back(); } else location.hash = lastOutside; }
});
function focusPart(id, tries) {                              // the explorer loads its data after the page; wait for it
  if (viewer.selectPart && viewer.selectPart(id)) return;
  if ((tries || 0) < 60) setTimeout(() => focusPart(id, (tries || 0) + 1), 300);
}

// ---------------- build guide: highlight the section being read in the contents list ----------------
let buildReady = null;
function hydrateBuild() {                                    // images and clip posters load when the guide is first opened
  if (buildReady) return buildReady;
  const imgs = Array.from(document.querySelectorAll('#build img[data-src]'));
  document.querySelectorAll('#build video[data-poster]').forEach(v => { v.poster = v.dataset.poster; });
  buildReady = Promise.race([Promise.all(imgs.map(i => new Promise(r => { i.onload = i.onerror = r; i.src = i.dataset.src; }))), new Promise(r => setTimeout(r, 4000))]);
  return buildReady;
}
let tocWatch = false;
function watchBuildToc() {
  if (tocWatch || !('IntersectionObserver' in window)) return;
  tocWatch = true;
  const links = new Map(Array.from(document.querySelectorAll('.md-toc a')).map(a => [a.getAttribute('href').slice(1), a]));
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return;
    links.forEach(a => a.removeAttribute('aria-current'));
    const a = links.get(en.target.id); if (a) a.setAttribute('aria-current', 'true');
  }), { rootMargin: '-15% 0px -75% 0px' });
  document.querySelectorAll('.md-sec').forEach(sec => io.observe(sec));
}

// ---------------- decision page: morphological chart and the 43-concept table ----------------
const FAM = { K: 'Conventional', B: 'Buy-and-modify', U: 'Unconventional' };
const SHORT = ['K09', 'K01', 'K19', 'K06', 'B08', 'B09', 'U01'];
const byId = {}; C.forEach(c => { byId[c[0]] = c; });
const CHOSEN = byId.K09[2].split(' '), RUNNER = byId.K01[2].split(' ');
const used = {}; C.forEach(c => { c[2].split(' ').forEach(o => { used[o] = (used[o] || 0) + 1; }); });
const label = c => c[0] === 'K09' ? 'K09-L' : c[0];
let overlay, cells = {}, selected = null, grid, note;
function initMorph() {
  grid = document.getElementById('morph-grid'); note = document.getElementById('morph-note');
  let html = '';
  DIMS.forEach(d => {
    html += '<div class="row" style="--cols:' + d.opts.length + '"><div class="fn"><span class="code">' + d.id + '</span><b>' + d.name + '</b><span>' + d.what + '</span></div>';
    d.opts.forEach(o => {
      const code = o[0]; let cls = 'ds-cell', tag = 'OUT';
      if (CHOSEN.indexOf(code) >= 0) { cls += ' chosen'; tag = 'CHOSEN'; }
      else if (RUNNER.indexOf(code) >= 0) { cls += ' runner'; tag = 'RUNNER-UP'; }
      else if (!used[code]) { cls += ' empty'; tag = '—'; }
      else cls += ' rejected';
      const pic = used[code] || CHOSEN.indexOf(code) >= 0 ? '<svg aria-hidden="true"><use href="#sk-' + code + '"/></svg>' : '—';
      html += '<div class="' + cls + '" data-opt="' + code + '" title="' + code + ' · ' + esc(o[1]) + (used[code] ? ' · ' + used[code] + ' concept' + (used[code] > 1 ? 's' : '') : ' · no concept') + '"><span class="code">' + code + (o[2] ? ' <em>· ' + o[2] + '</em>' : '') + '</span><span class="tag">' + tag + '</span><div class="pic">' + pic + '</div><span class="name">' + esc(o[1]) + '</span></div>';
    });
    html += '</div>';
  });
  grid.innerHTML = html;
  const svgNS = 'http://www.w3.org/2000/svg';
  overlay = document.createElementNS(svgNS, 'svg'); overlay.setAttribute('class', 'morph-paths'); grid.appendChild(overlay);
  grid.querySelectorAll('.ds-cell').forEach(el => { cells[el.getAttribute('data-opt')] = el; });
  const centre = (el, dx) => [el.offsetLeft + el.offsetWidth / 2 + dx, el.offsetTop + el.offsetHeight / 2];
  function drawPath(codes, cls, dx) {
    const pts = [];
    codes.forEach(c => { const el = cells[c]; if (el) pts.push(centre(el, dx)); });
    if (pts.length < 2) return;
    const pl = document.createElementNS(svgNS, 'polyline');
    pl.setAttribute('class', 'p-' + cls); pl.setAttribute('points', pts.map(p => p[0] + ',' + p[1]).join(' '));
    overlay.appendChild(pl);
    pts.forEach(p => { const c = document.createElementNS(svgNS, 'circle'); c.setAttribute('class', 'c-' + cls); c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', 3.5); overlay.appendChild(c); });
  }
  redrawMorph = function () {
    if (!grid.offsetWidth) return;   // page hidden: redraw when shown
    overlay.setAttribute('width', grid.scrollWidth); overlay.setAttribute('height', grid.scrollHeight);
    while (overlay.firstChild) overlay.removeChild(overlay.firstChild);
    drawPath(CHOSEN, 'chosen', -7);
    drawPath(RUNNER, 'runner', 7);
    if (selected && selected[0] !== 'K09' && selected[0] !== 'K01') drawPath(selected[2].split(' '), 'sel', 0);
  };
  const chips = document.getElementById('morph-chips'), sel = document.getElementById('morph-select');
  SHORT.forEach(id => { const c = byId[id]; const b = document.createElement('button'); b.type = 'button'; b.className = 'ds-chip'; b.setAttribute('data-id', id); b.setAttribute('aria-pressed', 'false');
    b.innerHTML = '<span class="id">' + label(c) + '</span>' + esc(c[1].split(' (')[0].split(',')[0]); b.addEventListener('click', () => selectConcept(selected && selected[0] === id ? null : id)); chips.appendChild(b); });
  sel.innerHTML = '<option value="">pick…</option>' + C.map(c => '<option value="' + c[0] + '">' + label(c) + ' · ' + esc(c[1].split(' (')[0]) + '</option>').join('');
  sel.addEventListener('change', () => selectConcept(sel.value || null));
  document.getElementById('morph-clear').addEventListener('click', () => selectConcept(null));
  if (window.ResizeObserver) new ResizeObserver(() => redrawMorph()).observe(grid); else window.addEventListener('resize', () => redrawMorph());
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => redrawMorph());
  selectConcept(null);

  // concept table
  const tbody = document.querySelector('#ctable tbody'), q = document.getElementById('f-q'), ff = document.getElementById('f-fam'), fo = document.getElementById('f-out'), cnt = document.getElementById('f-count');
  tbody.innerHTML = C.map(c => {
    const out = c[3] + (c[4] ? ' → ' + c[4] : '');
    return '<tr data-outcome="' + c[3] + '" data-fam="' + c[0][0] + '"><td class="id"><a class="ds-link" href="#morph" data-pick="' + c[0] + '" title="Show on the chart">' + label(c) + '</a></td><td>' + esc(c[1]) + '</td><td class="fam">' + FAM[c[0][0]] + '</td><td><span class="ds-badge" data-outcome="' + c[3] + '">' + out + '</span></td><td class="num">' + c[5] + '</td><td class="reason">' + esc(c[6]) + '</td></tr>';
  }).join('');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  function filter() {
    const s = q.value.trim().toLowerCase(), f = ff.value, o = fo.value; let n = 0;
    rows.forEach((r, i) => { const c = C[i], ok = (!f || c[0][0] === f) && (!o || c[3] === o) && (!s || (c[0] + ' ' + c[1] + ' ' + c[6] + ' ' + c[2]).toLowerCase().indexOf(s) >= 0);
      r.style.display = ok ? '' : 'none'; if (ok) n++; });
    cnt.textContent = n + ' of ' + C.length;
  }
  [q, ff, fo].forEach(el => el.addEventListener('input', filter));
  tbody.addEventListener('click', e => { const a = e.target.closest('[data-pick]'); if (a) selectConcept(a.getAttribute('data-pick')); });
  filter();
}
let redrawMorph = () => {};
function selectConcept(id) {
  selected = id ? byId[id] : null;
  Object.keys(cells).forEach(k => cells[k].classList.remove('onpath'));
  document.querySelectorAll('#morph-chips .ds-chip').forEach(b => b.setAttribute('aria-pressed', selected && b.getAttribute('data-id') === selected[0] ? 'true' : 'false'));
  document.getElementById('morph-select').value = selected ? selected[0] : '';
  if (selected) {
    selected[2].split(' ').forEach(c => { if (cells[c]) cells[c].classList.add('onpath'); });
    const out = selected[3] + (selected[4] ? ' → ' + selected[4] : '');
    note.innerHTML = '<span class="ds-mono">' + label(selected) + '</span><span>' + esc(selected[1]) + '</span><span class="ds-badge" data-outcome="' + selected[3] + '">' + out + '</span><span class="ds-mono" style="font-weight:400;color:var(--fg-3)">' + selected[2] + '</span><span style="flex-basis:100%">' + esc(selected[6]) + '</span>';
  } else {
    note.innerHTML = '<span class="ds-mono">K09-L</span><span>' + esc(byId.K09[2]) + '</span><span style="color:var(--fg-3)">·</span><span class="ds-mono">K01</span><span>' + esc(byId.K01[2]) + '</span><span style="flex-basis:100%">K09-L differs from the K09 card by one cell: C4 (fins only, differential thrust) became C3 (elevons), on the skeptic’s advice. Pick a concept to see its path.</span>';
  }
  redrawMorph();
}

// ---------------- lightbox for renders and plots ----------------
const lb = document.getElementById('lightbox'), lbImg = document.getElementById('lb-img'), lbCap = document.getElementById('lb-cap');
let lbItems = [], lbAt = 0;
function openLightbox(items, at) {
  lbItems = items; lbAt = at; showLightbox();
  lb.hidden = false; document.body.classList.add('lb-open'); document.getElementById('lb-close').focus();
}
function showLightbox() {
  const a = lbItems[lbAt]; lbImg.src = a.dataset.lightbox; lbImg.alt = a.dataset.caption || ''; lbCap.textContent = (lbAt + 1) + ' / ' + lbItems.length + ' · ' + (a.dataset.caption || '');
  document.getElementById('lb-prev').hidden = document.getElementById('lb-next').hidden = lbItems.length < 2;
}
function closeLightbox() { lb.hidden = true; document.body.classList.remove('lb-open'); lbImg.removeAttribute('src'); }
document.addEventListener('click', e => {
  const a = e.target.closest('a[data-lightbox]');
  if (a) { e.preventDefault(); const group = a.closest('.gallery, .sims, .plots') || document; openLightbox(Array.from(group.querySelectorAll('a[data-lightbox]')), Array.from(group.querySelectorAll('a[data-lightbox]')).indexOf(a)); return; }
  if (e.target.closest('#lb-close') || (e.target === lb)) closeLightbox();
  else if (e.target.closest('#lb-prev')) { lbAt = (lbAt - 1 + lbItems.length) % lbItems.length; showLightbox(); }
  else if (e.target.closest('#lb-next')) { lbAt = (lbAt + 1) % lbItems.length; showLightbox(); }
  const s = e.target.closest('[data-sub3d]');
  if (s) viewer.setQuery(s.dataset.sub3d);   // the href (#aircraft) routes; the search box filters the part browser
});
document.addEventListener('keydown', e => {
  if (lb.hidden) return;
  if (e.key === 'Escape') closeLightbox();
  else if (e.key === 'ArrowLeft' && lbItems.length > 1) { lbAt = (lbAt - 1 + lbItems.length) % lbItems.length; showLightbox(); }
  else if (e.key === 'ArrowRight' && lbItems.length > 1) { lbAt = (lbAt + 1) % lbItems.length; showLightbox(); }
});

// ---------------- simulations: glossary popover, summary rows that re-scroll on a repeat click ----------------
const pop = document.createElement('div'); pop.className = 'term-pop'; pop.setAttribute('role', 'tooltip'); pop.hidden = true; document.body.appendChild(pop);
let popFor = null;
function hidePop() { pop.hidden = true; popFor = null; }
document.addEventListener('click', e => {
  const t = e.target.closest('a.term');
  if (t) {
    e.preventDefault();
    if (popFor === t) { hidePop(); return; }
    pop.innerHTML = '<b>' + esc(t.dataset.name || t.textContent) + '</b>' + esc(t.dataset.def || '');
    pop.hidden = false; popFor = t;
    const r = t.getBoundingClientRect(), w = pop.offsetWidth;
    pop.style.left = Math.max(16, Math.min(window.scrollX + r.left, window.scrollX + document.documentElement.clientWidth - w - 16)) + 'px';
    pop.style.top = (window.scrollY + r.bottom + 6) + 'px';
    return;
  }
  if (!pop.hidden && !e.target.closest('.term-pop')) hidePop();
  const row = e.target.closest('a.sum-row');
  if (row && location.hash === row.getAttribute('href')) { const el = document.querySelector(row.getAttribute('href')); if (el) el.scrollIntoView({ block: 'start' }); }
});
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !pop.hidden) hidePop(); });
window.addEventListener('hashchange', hidePop);

// ---------------- start ----------------
initMorph();
route();
startViewer();
