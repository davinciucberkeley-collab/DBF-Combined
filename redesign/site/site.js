// Concept A explorer shell: hash router (#aircraft #decision #team #subsystems #status #docs), theme toggle,
// the decision page's morphological chart and concept table (logic from redesign/config-study/web/index.html),
// the render / plot lightbox, and the 3-D explorer (viewer.js). Everything is relative: works on GitHub Pages and as an artifact.
import { DIMS, C } from './data/concepts.js?v=20261115f';
import { start as startViewer, viewer } from './viewer.js?v=20261118g';

const ROUTES = ['aircraft', 'decision', 'team', 'subsystems', 'build', 'proof', 'structures', 'sims', 'status', 'bom', 'docs'];
const TITLES = { aircraft: 'Aircraft', decision: 'Decision', team: 'Team', subsystems: 'Subsystems', build: 'Build guide', proof: 'Proof chain', structures: 'Structures', sims: 'Simulations', status: 'Status', bom: 'BOM', docs: 'Docs' };
const GH_ROOT = 'https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/';
const store = { get(k) { try { return localStorage.getItem('k09l.' + k); } catch (e) { return null; } },
  set(k, v) { try { localStorage.setItem('k09l.' + k, v); } catch (e) { /* storage blocked: fine */ } } };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

// ---------------- theme ----------------
const root = document.documentElement, themeBtn = document.getElementById('theme');
function isDark() { const t = root.getAttribute('data-theme'); return t ? t === 'dark' : !!(window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches); }
function paintTheme() { themeBtn.innerHTML = '<svg><use href="#i-' + (isDark() ? 'sun' : 'moon') + '"/></svg>'; }
{ const t = store.get('theme'); root.setAttribute('data-theme', t === 'light' ? 'light' : 'dark'); }   // dark by default (user 2026-11-17); the toggle's choice is remembered
themeBtn.addEventListener('click', () => { const next = isDark() ? 'light' : 'dark'; root.setAttribute('data-theme', next); store.set('theme', next); paintTheme(); viewer.themeChanged(); if (window.ProofEmbed) window.ProofEmbed.themeChanged(); });
if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', paintTheme);
paintTheme();


// ---------------- navigation drawer (<= 768 px) and the "On this page" rail ----------------
const menuBtn = document.getElementById('menu'), sideNav = document.getElementById('nav'), scrim = document.getElementById('scrim'), shell = document.querySelector('.shell'), rail = document.getElementById('rail');
const narrow = window.matchMedia ? matchMedia('(max-width: 768px)') : { matches: false, addEventListener() {} };
function openNav() {
  document.body.classList.add('nav-open'); menuBtn.setAttribute('aria-expanded', 'true'); scrim.hidden = false;
  const first = sideNav.querySelector('a[aria-current="page"]') || sideNav.querySelector('a'); if (first) first.focus();
}
function closeNav(refocus) {
  if (!document.body.classList.contains('nav-open')) return;
  document.body.classList.remove('nav-open'); menuBtn.setAttribute('aria-expanded', 'false'); scrim.hidden = true;
  if (refocus) menuBtn.focus();
}
menuBtn.addEventListener('click', () => document.body.classList.contains('nav-open') ? closeNav(true) : openNav());
scrim.addEventListener('click', () => closeNav(true));
sideNav.addEventListener('click', e => { if (e.target.closest('a') && narrow.matches) closeNav(false); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('nav-open')) { closeNav(true); }
  else if (e.key === 'Tab' && document.body.classList.contains('nav-open') && narrow.matches) {   // keep focus inside the open drawer
    const f = [menuBtn, ...sideNav.querySelectorAll('a')], i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); } } });
narrow.addEventListener('change', () => { if (!narrow.matches) closeNav(false); });
// the drawer is inert when closed on a phone, so Tab never lands on hidden links
function syncInert() { const off = narrow.matches && !document.body.classList.contains('nav-open'); if ('inert' in sideNav) sideNav.inert = off; }
new MutationObserver(syncInert).observe(document.body, { attributes: true, attributeFilter: ['class'] }); narrow.addEventListener('change', syncInert); syncInert();

let railFor = null, railIO = null;
const slug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 48);
function buildRail(name) {
  const view = document.getElementById(name), show = view && name !== 'aircraft' && name !== 'proof';
  if (railIO) { railIO.disconnect(); railIO = null; }
  let items = [];
  if (show) {
    view.querySelectorAll('h2, h3.ds-h2[id]').forEach(h => {
      if (h.closest('details:not([open])') || h.closest('.md .md-sec') && h.tagName !== 'H2') return;
      const sec = h.closest('section[id]'), id = (h.tagName === 'H2' && sec && sec.querySelector('h2') === h && sec.id) || h.id || (h.id = slug(h.textContent));
      const t = Array.from(h.childNodes).filter(n => !(n.classList && n.classList.contains('sh-anchor'))).map(n => n.textContent).join('').trim().replace(/\s+/g, ' '); if (!id || !t || items.some(i => i.id === id)) return;
      items.push({ id, t, el: h });
    });
  }
  shell.classList.toggle('has-rail', items.length > 1); rail.hidden = items.length < 2;
  if (items.length < 2) { rail.innerHTML = ''; return; }
  rail.innerHTML = '<h2>On this page</h2>' + items.map(i => '<a href="#' + i.id + '">' + esc(i.t) + '</a>').join('');
  if (!('IntersectionObserver' in window)) return;
  const links = new Map(items.map((i, k) => [i.el, rail.children[k + 1]]));
  railIO = new IntersectionObserver(es => es.forEach(en => { if (!en.isIntersecting) return;
    rail.querySelectorAll('a').forEach(a => a.removeAttribute('aria-current')); const a = links.get(en.target); if (a) a.setAttribute('aria-current', 'true'); }),
    { rootMargin: '-72px 0px -70% 0px' });
  items.forEach(i => railIO.observe(i.el));
}

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
  { const nav = document.getElementById('nav'), cur = nav && nav.querySelector('a[aria-current="page"]');   // narrow screens: keep the current tab in view
    if (cur && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = Math.max(0, cur.offsetLeft - nav.offsetLeft - 24); }
  document.body.dataset.route = name;
  document.title = 'Concept A · ' + TITLES[name];     // concept A is the current design (D-182)
  if (name === 'build') { watchBuildToc(); if (target) openBuildTarget(target); }
  if (target) target.scrollIntoView({ block: 'start' }); else if (current !== name) window.scrollTo(0, 0);
  current = name;
  if (name === 'proof') enterProof(); else lastOutside = name === 'aircraft' ? '#aircraft' : location.hash;
  if (name === 'build') { const h = hydrateBuild(); if (target) h.then(() => target.scrollIntoView({ block: 'start', behavior: 'instant' })); }
  if (name === 'aircraft') { viewer.resize(); if (focusPartId) focusPart(focusPartId); focusPartId = null; }
  if (name === 'decision') redrawMorph();
  if (name === 'structures') import('./fea-view.js?v=20261118f').then(m => m.mountFea());
  if (name === 'sims') import('./replay.js?v=20261124a').then(m => m.mountReplays()).catch(e => console.error('replay.js: ' + e.message));   // T-105: lazy, first visit only
  closeNav(false); buildRail(name);
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
  loadScript('proofs/model.js?v=20261112a').then(() => loadScript('proofs/app.js?v=20261118h'))
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
// One section of the guide shows at a time (user 2026-11-16: limit the long scroll). The contents list and the
// Previous / Next buttons switch sections; a link to a step (#build-a1 ...) opens its section and unfolds the step.
let buildSec = null;
function showBuildSec(id, scroll) {
  const secs = Array.from(document.querySelectorAll('#build .md-sec'));
  if (!secs.length) return;
  const k = Math.max(0, secs.findIndex(s => s.id === id));
  secs.forEach((s, j) => { s.hidden = j !== k; });
  buildSec = secs[k].id;
  document.querySelectorAll('#build .md-toc a').forEach(a => {
    if (a.getAttribute('href') === '#' + buildSec) { a.setAttribute('aria-current', 'true'); a.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
    else a.removeAttribute('aria-current');
  });
  const pg = document.getElementById('build-pager');
  if (pg) {
    const name = s => { const a = document.querySelector('#build .md-toc a[href="#' + s.id + '"]'); return a ? a.textContent : s.id; };
    const prev = secs[k - 1], next = secs[k + 1];
    pg.innerHTML = (prev ? '<button type="button" class="ds-btn" data-bsec="' + prev.id + '">&larr; ' + esc(name(prev)) + '</button>' : '<span></span>') +
      '<span class="pg-n">' + (k + 1) + ' of ' + secs.length + '</span>' +
      (next ? '<button type="button" class="ds-btn primary" data-bsec="' + next.id + '">' + esc(name(next)) + ' &rarr;</button>' : '<span></span>');
  }
  if (scroll) secs[k].scrollIntoView({ block: 'start', behavior: 'instant' });      // md-sec scroll-margin clears the top bar and the sticky contents
}
let tocWatch = false;
function watchBuildToc() {
  if (tocWatch) return;
  tocWatch = true;
  const art = document.querySelector('#build article.md');
  if (art && !document.getElementById('build-pager')) art.insertAdjacentHTML('beforeend', '<nav class="md-pager" id="build-pager" aria-label="Guide sections"></nav>');
  document.getElementById('build').addEventListener('click', e => {
    const t = e.target.closest('.md-toc a, [data-bsec]');
    if (!t) return;
    e.preventDefault();
    showBuildSec(t.dataset.bsec || t.getAttribute('href').slice(1), true);
  });
  showBuildSec(buildSec, false);
}
function openBuildTarget(el) {                               // a deep link into the guide: show its section, unfold its step
  const sec = el.closest('.md-sec'); if (sec) showBuildSec(sec.id, false);
  const st = el.closest('details.md-step'); if (st) st.open = true;
}

// ---------------- videos: load the whole file once, so the slider can seek even where the host serves no byte ranges ----------------
const vidBlobs = new Map();
document.addEventListener('play', e => {
  const v = e.target;
  if (!(v instanceof HTMLVideoElement)) return;
  const src = v.currentSrc || v.src;
  if (!src || src.startsWith('blob:')) return;
  let p = vidBlobs.get(src);
  if (!p) { p = fetch(src, { cache: 'no-store' }).then(r => r.ok ? r.blob() : Promise.reject(new Error(r.status))).then(b => URL.createObjectURL(b)); vidBlobs.set(src, p); }
  p.then(u => {
    if ((v.currentSrc || v.src) !== src) return;          // the stage buttons switched the clip meanwhile
    const at = v._seekTo != null ? v._seekTo : v.currentTime, playing = !v.paused; v._seekTo = null;
    v.addEventListener('loadedmetadata', () => { v.currentTime = at; if (playing) v.play().catch(() => {}); }, { once: true });
    v.src = u;
  }).catch(() => vidBlobs.delete(src));
}, true);
document.addEventListener('seeking', e => {                  // a seek made before the whole file is in: keep it and apply it after the swap
  const v = e.target;
  if (v instanceof HTMLVideoElement && !(v.currentSrc || v.src).startsWith('blob:')) v._seekTo = v.currentTime;
}, true);

// ---------------- decision page: morphological chart and the 43-concept table ----------------
// Chart: rows = the 11 functions (MORPH.md §1), columns = three designs (A chosen, B fallback, and a third you pick,
// K09-L by default). Clicking a row lists every option studied for that function, with its sketch and who uses it.
const FAM = { K: 'Conventional', B: 'Buy-and-modify', U: 'Unconventional' };
const SHORT = ['A', 'B', 'D2', 'K09', 'K01', 'K06', 'K19'];
const byId = {}; C.forEach(c => { byId[c[0]] = c; });
const optInfo = {}, dimOf = {}; DIMS.forEach(d => { dimOf[d.id] = d; d.opts.forEach(o => { optInfo[o[0]] = { dim: d, name: o[1], note: o[2] || '' }; }); });
const usedBy = {}; C.forEach(c => { c[2].split(' ').forEach(o => { (usedBy[o] = usedBy[o] || []).push(c[0]); }); });
const label = c => c[0] === 'K09' ? 'K09-L' : c[0];
const shortName = c => c[1].split(' (')[0].split(',')[0];
const pathOf = c => { const m = {}; c[2].split(' ').forEach(o => { if (optInfo[o]) m[optInfo[o].dim.id] = o; }); return m; };
const PA = pathOf(byId.A), PB = pathOf(byId.B);
const NOTE_TXT = { r1: 'added by audit round 1', r2: 'added by audit round 2', r3: 'added by audit round 3', '11-14': 'added by the 2026-11-14 re-study' };
let selected = byId.K09, openDim = null, openOpt = null, colTab = 'a', grid, detail, note, flow;
const sketch = code => document.getElementById('sk-' + code) ? '<svg viewBox="0 0 120 80" aria-hidden="true"><use href="#sk-' + code + '"/></svg>' : '';
function pathCell(d, col, path) {
  const code = path[d.id];
  if (!code) return '<div class="mc p' + col + '"><div class="t"><span>—</span></div></div>';
  const diff = col !== 'a' && PA[d.id] !== code, o = optInfo[code];
  return '<div class="mc p' + col + (diff ? ' diff' : '') + '" data-opt="' + code + '"' + (diff ? ' title="Differs from A (' + (PA[d.id] || '—') + ')"' : '') + '>' + sketch(code) + '<div class="t"><i>' + code + (o.note ? ' · ' + o.note : '') + '</i><span>' + esc(o.name) + '</span></div></div>';
}
function renderMorph() {
  const PC = pathOf(selected), thirdTag = selected[0] === 'K09' ? 'SUPERSEDED' : selected[3];
  let h = '<div class="mp-tabs" role="group" aria-label="Which design to show">'
    + ['a:A', 'b:B', 'c:' + label(selected)].map(s => '<button type="button" data-tab="' + s[0] + '" aria-pressed="' + (colTab === s[0]) + '">' + s.slice(2) + '</button>').join('') + '</div>';
  h += '<div class="mh"><span></span>'
    + '<div class="col pa"><span class="id">A <span class="tg">CHOSEN</span></span><small>' + esc(shortName(byId.A)) + ' · D-182</small></div>'
    + '<div class="col pb"><span class="id">B <span class="tg">FALLBACK</span></span><small>' + esc(shortName(byId.B)) + '</small></div>'
    + '<div class="col pc"><span class="id">' + label(selected) + ' <span class="tg">' + thirdTag + '</span></span><small>' + esc(shortName(selected)) + '</small></div></div>';
  DIMS.forEach(d => {
    const open = openDim === d.id;
    h += '<div class="mrow' + (open ? ' open' : '') + '" data-dim="' + d.id + '"><button class="mfn" type="button" aria-expanded="' + open + '" title="Open the ' + d.opts.length + ' options for ' + esc(d.name) + '"><b><span class="k">' + d.id + '</span>' + d.name + '</b><span class="w">' + d.what + '</span></button>'
      + pathCell(d, 'a', PA) + pathCell(d, 'b', PB) + pathCell(d, 'c', PC) + '</div>' + (open ? '<aside class="mo" id="morph-detail" aria-live="polite"></aside>' : '');
  });
  grid.innerHTML = h; grid.setAttribute('data-col', colTab);
  detail = document.getElementById('morph-detail'); renderDetail();
  renderNote(PC);
}
function renderDetail() {
  const d = openDim && dimOf[openDim];
  if (!d || !detail) return;
  const PC = pathOf(selected), third = selected[0] !== 'A' && selected[0] !== 'B';
  let h = '<div class="mo-h"><b>' + d.id + ' · ' + d.name + '</b><span>' + d.what + ' · ' + d.opts.length + ' options</span></div><div class="mo-g">';
  d.opts.forEach(o => {
    const code = o[0], inA = PA[d.id] === code, inB = PB[d.id] === code, inC = third && PC[d.id] === code, n = (usedBy[code] || []).length;
    const cls = 'ot' + (inA ? ' a' : inB ? ' b' : n ? ' x' : ' gap') + (inC ? ' pick' : '');
    h += '<button type="button" class="' + cls + '" data-opt="' + code + '" aria-pressed="' + (openOpt === code) + '">' + sketch(code)
      + '<span class="pl">' + (inA ? '<span class="tg a">A</span>' : '') + (inB ? '<span class="tg">B</span>' : '') + (inC ? '<span class="tg">' + label(selected) + '</span>' : '') + '</span>'
      + '<span class="c">' + code + (o[2] ? ' · ' + o[2] : '') + '</span><span class="n">' + esc(o[1]) + '</span><span class="u">' + (n ? 'used by ' + n : 'no concept') + '</span></button>';
  });
  h += '</div><div class="mo-use">';
  if (openOpt && optInfo[openOpt] && optInfo[openOpt].dim === d) {
    const ids = usedBy[openOpt] || [];
    h += '<b>' + openOpt + '</b>' + (ids.length ? ' is on the path of ' + ids.length + ' concept' + (ids.length > 1 ? 's' : '') + ':' + ids.map(i => '<button type="button" data-pick="' + i + '" title="Show ' + label(byId[i]) + ' in the third column">' + label(byId[i]) + '</button>').join('') : ' is on no concept’s path: an audit gap.');
  } else h += 'Click an option to see which concepts use it.';
  const notes = d.opts.filter(o => o[2]).map(o => o[2]).filter((v, i, a) => a.indexOf(v) === i);
  if (notes.length) h += '<span style="flex-basis:100%;color:var(--fg-3)">' + notes.map(k => k + ' = ' + NOTE_TXT[k]).join(' · ') + '</span>';
  detail.innerHTML = h + '</div>';
}
function renderNote(PC) {
  const out = c => '<span class="ds-badge" data-outcome="' + c[3] + '">' + c[3] + (c[4] ? ' → ' + c[4] : '') + '</span>';
  const diffs = DIMS.filter(d => PA[d.id] !== PC[d.id]);
  flow.innerHTML = '<span class="ds-badge" data-outcome="CHOSEN">CHOSEN</span><b>A</b><span>' + esc(shortName(byId.A)) + '</span><span class="arrow">→</span><span>decision D-182 (2026-11-14, J6 board)</span><span class="arrow">→</span><span>fallback B, lifeboat D2</span>'
    + '<a class="ds-link" href="#shortlist">Shortlist and trade matrix</a><a class="ds-link" href="#concepts" style="margin-left:0">All concepts</a>';
  let b = '<p><span class="ds-mono">A</span> ' + out(byId.A) + ' ' + esc(byId.A[5]) + '. ' + esc(byId.A[6]) + '</p><p><span class="ds-mono">B</span> ' + out(byId.B) + ' ' + esc(byId.B[5]) + '. ' + esc(byId.B[6]) + '</p>';
  if (selected[0] !== 'A' && selected[0] !== 'B') b += '<p><span class="ds-mono">' + label(selected) + '</span> ' + esc(selected[1]) + ' ' + out(selected) + ' ' + esc(selected[5]) + '. ' + esc(selected[6]) + '</p>';
  if (selected[0] !== 'A') b += '<p>' + label(selected) + ' differs from A in ' + diffs.length + ' of ' + DIMS.length + ' rows' + (diffs.length ? ': ' + diffs.map(d => d.id + ' ' + d.name + ' (' + (PA[d.id] || '—') + ' ' + esc(PA[d.id] ? optInfo[PA[d.id]].name : '—') + ' vs ' + (PC[d.id] || '—') + ' ' + esc(PC[d.id] ? optInfo[PC[d.id]].name : '—') + ')').join('; ') : '') + '.</p>';
  if (selected[0] === 'K09') b += '<p>Concept A shares K09-L’s path except R7 (motors in an X on carbon arms, not on the fins) and E7 (two 4S 2300 mAh packs).</p>';
  note.innerHTML = '<summary><b>Why these paths</b><span>A and B reasons' + (selected[0] !== 'A' && selected[0] !== 'B' ? ', ' + label(selected) : '') + ' · differences from A</span></summary><div class="body">' + b + '</div>';
}
function initMorph() {
  grid = document.getElementById('morph-grid'); note = document.getElementById('morph-note'); flow = document.getElementById('morph-flow');
  const chips = document.getElementById('morph-chips'), sel = document.getElementById('morph-select');
  SHORT.forEach(id => { const c = byId[id]; const b = document.createElement('button'); b.type = 'button'; b.className = 'ds-chip'; b.setAttribute('data-id', id); b.setAttribute('aria-pressed', 'false');
    b.title = shortName(c); b.innerHTML = '<span class="id">' + label(c) + '</span>'; b.addEventListener('click', () => selectConcept(id)); chips.appendChild(b); });
  sel.innerHTML = '<option value="">pick…</option>' + C.map(c => '<option value="' + c[0] + '">' + label(c) + ' · ' + esc(c[1].split(' (')[0]) + '</option>').join('');
  sel.addEventListener('change', () => selectConcept(sel.value || null));
  document.getElementById('morph-clear').addEventListener('click', () => selectConcept(null));
  grid.addEventListener('click', e => {
    const t = e.target.closest('[data-tab]'); if (t) { colTab = t.getAttribute('data-tab'); renderMorph(); return; }
    const r = e.target.closest('.mfn'); if (r) { const id = r.parentNode.getAttribute('data-dim'); openDim = openDim === id ? null : id; openOpt = null; renderMorph(); const nr = grid.querySelector('.mrow.open'); if (nr && nr.getBoundingClientRect().top < 0) nr.scrollIntoView({ block: 'nearest' }); }
  });
  grid.addEventListener('click', e => {
    const p = e.target.closest('[data-pick]'); if (p) { selectConcept(p.getAttribute('data-pick')); return; }
    const o = e.target.closest('.ot'); if (o) { openOpt = openOpt === o.getAttribute('data-opt') ? null : o.getAttribute('data-opt'); renderDetail(); }
  });
  const wrap = grid.closest('.morph-wrap');
  const fitMorph = () => { const w = wrap.clientWidth; if (w) wrap.classList.toggle('xs', w < 520); };   // phone width: one design column at a time, chosen by tabs
  if (window.ResizeObserver) new ResizeObserver(fitMorph).observe(wrap); else window.addEventListener('resize', fitMorph);
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
let redrawMorph = () => {};   // kept: the page router calls it when the decision view is shown (nothing to measure any more)
function selectConcept(id) {
  selected = id ? byId[id] : byId.K09;
  document.querySelectorAll('#morph-chips .ds-chip').forEach(b => b.setAttribute('aria-pressed', b.getAttribute('data-id') === selected[0] ? 'true' : 'false'));
  document.getElementById('morph-select').value = id || '';
  renderMorph();
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

// ---------------- section permalinks ----------------
// Every numbered section title (h2.sh-t in a section with an id) gets a "#" permalink (UI-SURVEY.md rule). The in-page contents list is
// the "On this page" rail above (T-053 / D-242 layout, 2026-11-16), so the survey's own contents list is not built (T-104).
function addPermalinks() {
  document.querySelectorAll('main > .view section.c[id] h2.sh-t').forEach(h => {
    const sec = h.closest('section.c[id]'); if (!sec || sec.querySelector('h2.sh-t') !== h || h.querySelector('.sh-anchor')) return;
    const a = document.createElement('a'); a.className = 'sh-anchor'; a.href = '#' + sec.id; a.textContent = '#';
    a.setAttribute('aria-label', 'Link to this section'); h.appendChild(a);
  });
}

// ---------------- start ----------------
addPermalinks();
initMorph();
route();
startViewer();
