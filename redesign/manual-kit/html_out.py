"""html_out.py - the static HTML manual (one file + img/). Standard library only.

Look and components come from redesign/design-system (tokens.css + components.css are inlined, so the page works
from disk, from GitHub Pages and on paper). One .ds-step card per step: the render on the left with numbered dots
that match the numbered actions, everything the step needs on the right, a CHECK last. Ticks, measured values and
the progress bar persist in the browser (localStorage, per manual id + revision); nothing is sent anywhere.
"""
import html
import json
import os
import re

import figures as F
import steps_lib as L

DS = os.path.join(L.REDESIGN, 'design-system')


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def fmt_min(m):
    m = int(round(m or 0))
    if m < 60:
        return '%d min' % m
    return '%d h' % (m // 60) + (' %d min' % (m % 60) if m % 60 else '')


def qty(v):
    try:
        return L.num(float(v))
    except (TypeError, ValueError):
        return esc(v)


class Text:
    """Turns step text into HTML: numbers from params (with their source as a tooltip), `values` in mono,
    part / edge ids as hover chips, glossary words underlined on first use in each step."""

    def __init__(self, m, terms):
        self.m, self.terms = m, terms

    def __call__(self, s, seen=None):
        h = esc(s)
        h = self.m.sub_params(h, lambda t, src: '<span class="ds-num" title="%s">%s</span>' % (esc(src), t))
        h = re.sub(r'`([^`]+)`', r'<span class="ds-num">\1</span>', h)

        def idrep(mt):
            i = mt.group(1)
            if i in self.m.parts:
                return '<span class="pid" tabindex="0" data-part="%s">%s</span>' % (i, i)
            if i in self.m.edges:
                return '<span class="pid edge" tabindex="0" data-edge="%s">%s</span>' % (i, i)
            return i
        h = L.ID_RE.sub(idrep, h)
        if seen is not None and self.terms:
            h = self._gloss(h, seen)
        return h

    def _gloss(self, h, seen):
        pieces = re.split(r'(<[^>]+>)', h)
        depth = 0
        for k, p in enumerate(pieces):
            if p.startswith('<'):
                depth += -1 if p.startswith('</') else (0 if p.endswith('/>') else 1)
                continue
            if depth:          # inside a chip or number: leave alone
                continue
            for t in self.terms:
                if t['term'] in seen:
                    continue
                mt = t['rx'].search(p)
                if mt:
                    seen.add(t['term'])
                    p = p[:mt.start()] + '<dfn class="gl" tabindex="0" data-term="%s">%s</dfn>' % (
                        esc(t['term']), mt.group(0)) + p[mt.end():]
                    break      # one term per text piece keeps the regex positions simple
            pieces[k] = p
        return ''.join(pieces)


ICONS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.6 2.6L16 9.5"/></symbol>
<symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8v.5"/></symbol>
<symbol id="i-warn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5l9 16H3z"/><path d="M12 10v4M12 17v.5"/></symbol>
<symbol id="i-stop" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M8 3h8l5 5v8l-5 5H8l-5-5V8z"/><path d="M12 8v5M12 16v.5"/></symbol>
<symbol id="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></symbol>
<symbol id="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></symbol>
<symbol id="i-print" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"><path d="M7 9V3h10v6M7 17H4v-7h16v7h-3"/><rect x="7" y="14" width="10" height="7"/></symbol>
<symbol id="i-reset" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12a8 8 0 1 0 2.3-5.6M4 4v4h4"/></symbol>
<symbol id="i-zoom" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></symbol>
<symbol id="i-brand" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 13h18M12 13V5M7 13l-2 6M17 13l2 6"/><circle cx="7" cy="5" r="2"/><circle cx="17" cy="5" r="2"/></symbol>
</svg>'''

CALLOUT = {'note': ('', 'i-info', 'Note'), 'caution': ('caution', 'i-warn', 'Caution'), 'stop': ('stop', 'i-stop', 'Stop'),
           'check': ('check', 'i-check', 'Check')}

PAGE_CSS = r'''
html,body{margin:0}
body{min-height:100vh}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;z-index:50;background:var(--panel);padding:8px 12px;border-radius:var(--radius-sm)}
.ds-topbar .ttl{font-weight:var(--weight-semibold);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
.ds-topbar .ttl small{font:var(--weight-regular) var(--text-xs)/1 var(--font-mono);color:var(--fg-3);margin-left:8px}
.prog{display:flex;align-items:center;gap:10px;min-width:150px;flex:0 1 320px}
.prog .bar{flex:1;height:6px;border-radius:3px;background:var(--panel-3);overflow:hidden}
.prog .bar i{display:block;height:100%;width:0;background:var(--accent);transition:width var(--dur-base) var(--ease-out)}
.prog span{font:var(--weight-medium) var(--text-xs)/1 var(--font-mono);color:var(--fg-2);white-space:nowrap}
.shell{display:grid;grid-template-columns:var(--sidebar-w) minmax(0,1fr);max-width:1560px;margin:0 auto}
.rail{position:sticky;top:var(--topbar-h);align-self:start;height:calc(100vh - var(--topbar-h));overflow:auto;padding:var(--space-5) var(--space-3) var(--space-6) var(--space-5);border-right:1px solid var(--line)}
.rail .ds-label{margin:var(--space-4) 0 var(--space-1) 8px}
.rail a{display:flex;gap:8px;align-items:baseline;padding:5px 8px;border-radius:var(--radius-sm);font-size:var(--text-sm);color:var(--fg-2);text-decoration:none;line-height:1.35}
.rail a:hover{background:var(--panel-2);color:var(--fg)}
.rail a.on{background:var(--accent-wash);color:var(--fg)}
.rail a .n{font:var(--weight-medium) var(--text-xs)/1.35 var(--font-mono);color:var(--fg-3);min-width:1.6em}
.rail a .ok{margin-left:auto;width:14px;height:14px;flex:none;color:var(--st-verified);visibility:hidden;align-self:center}
.rail a.done .ok{visibility:visible}
.rail a.done{color:var(--fg-3)}
main{padding:var(--space-6) var(--space-6) var(--space-8);display:flex;flex-direction:column;gap:var(--space-7);min-width:0}
section{scroll-margin-top:calc(var(--topbar-h) + 16px)}
.sechead{display:grid;gap:6px;padding-bottom:var(--space-3);border-bottom:1px solid var(--line);margin-bottom:var(--space-4)}
.sechead .ds-h1 small{font:var(--weight-medium) var(--text-lg)/1 var(--font-mono);color:var(--fg-3);margin-right:10px;letter-spacing:0}
.wp-meta{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:var(--text-sm);color:var(--fg-2)}
.wp-meta b{font-family:var(--font-mono);font-weight:var(--weight-medium);color:var(--fg)}
/* cover */
.cover{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:var(--space-6);align-items:center}
.cover .lead{display:grid;gap:var(--space-4)}
.cover .ds-display{font-size:2.25rem}
.cover .sub{color:var(--fg-2);font-size:var(--text-lg);line-height:1.45;margin:0;max-width:44ch}
.hero{margin:0;border:1px solid var(--line);border-radius:var(--radius-md);overflow:hidden;background:linear-gradient(180deg,var(--stage-top),var(--stage-bottom))}
.hero img{display:block;width:100%;height:auto}
.howto{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:var(--space-3)}
.howto>div{display:grid;grid-template-columns:28px 1fr;gap:10px;align-items:start;padding:12px 14px;border:1px solid var(--line);border-radius:var(--radius-md);background:var(--panel);font-size:var(--text-sm);color:var(--fg-2)}
.howto b{color:var(--fg);font-weight:var(--weight-semibold);display:block}
.howto .sw{width:22px;height:22px;border-radius:5px;margin-top:2px}
.howto .dot{width:24px;height:24px;border-radius:50%;background:var(--highlight);color:#fff;font:600 12px/24px var(--font-mono);text-align:center}
.safety{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:var(--space-3)}
.safety .ds-callout{max-width:none}
/* step card */
.ds-step.step{grid-template-columns:minmax(0,1.6fr) minmax(340px,1fr);scroll-margin-top:calc(var(--topbar-h) + 12px)}
.ds-step.step > figure{display:block;place-items:initial;min-height:0;background:var(--panel)}
.ds-step.step > figure .sticky{position:sticky;top:calc(var(--topbar-h) + 12px)}
.stage{position:relative;background:linear-gradient(180deg,var(--stage-top),var(--stage-bottom));cursor:zoom-in}
.stage img{display:block;width:100%;height:auto}
.stage svg.ovl{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.stage .mk .disc{transition:r var(--dur-fast) var(--ease-out)}
.stage .mk.on .disc{r:32px}
.stage rect.box{fill:none;stroke:var(--accent);stroke-width:4;stroke-dasharray:14 8;opacity:0;transition:opacity var(--dur-fast)}
.stage rect.box.on{opacity:1}
.stage .none{position:absolute;inset:0;display:grid;place-items:center;font-size:var(--text-sm);color:var(--fg-3);text-align:center;padding:24px}
.figbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;padding:10px 14px;border-top:1px solid var(--line)}
.figbar .fid{font:var(--weight-regular) var(--text-xs)/1 var(--font-mono);color:var(--fg-3)}
.figbar .ds-legend{margin-left:auto}
.figbar .ds-legend i.built{background:var(--line-3)}
.thumbs{display:flex;gap:10px;padding:0 14px 14px;flex-wrap:wrap}
.thumb{appearance:none;border:1px solid var(--line-2);border-radius:var(--radius-sm);background:var(--panel);padding:0;cursor:zoom-in;display:grid;grid-template-columns:96px auto;align-items:center;gap:10px;padding-right:12px;font:var(--weight-medium) var(--text-xs)/1.3 var(--font-sans);color:var(--fg-2);text-align:left;max-width:300px;overflow:hidden}
.thumb:hover{border-color:var(--accent-line);color:var(--fg)}
.thumb img{width:96px;height:60px;object-fit:cover;display:block;background:var(--stage-bottom)}
.step .body{padding:var(--space-4) var(--space-5) var(--space-5);display:flex;flex-direction:column;gap:var(--space-4);min-width:0}
.step .step-head{flex-wrap:wrap;row-gap:4px}
.step .tags{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;font:var(--weight-regular) var(--text-xs)/1 var(--font-mono);color:var(--fg-3)}
.step .goal{margin:0;color:var(--fg-2);font-size:var(--text-sm)}
.step .goal b{color:var(--fg);font-weight:var(--weight-semibold)}
.acts li{grid-template-columns:22px 1fr 24px !important;padding:4px 6px;margin:0 -6px;border-radius:var(--radius-sm);transition:background var(--dur-fast)}
.acts li.on{background:var(--highlight-wash)}
.acts li.ticked > span{color:var(--fg-3)}
.tick{display:grid;place-items:center;cursor:pointer}
.tick input,.pass input{width:18px;height:18px;margin:0;cursor:pointer}
.pid{font:var(--weight-medium) 0.86em/1 var(--font-mono);color:var(--fg);background:var(--panel-2);border-radius:var(--radius-xs);padding:2px 4px;cursor:help;white-space:nowrap;border-bottom:1px dotted var(--line-3)}
.pid:hover,.pid:focus-visible{background:var(--accent-wash)}
dfn.gl{font-style:normal;text-decoration:underline dotted var(--fg-3);text-underline-offset:3px;cursor:help}
.ds-kit h3{margin-bottom:6px}
.ds-kit li{align-items:baseline}
.ds-kit li .q{min-width:2.4em;white-space:nowrap}
.ds-kit .nm{color:var(--fg-2)}
.ds-kit .empty{color:var(--fg-3)}
details.more{border:1px solid var(--line);border-radius:var(--radius-sm)}
details.more>summary{cursor:pointer;padding:8px 12px;font:var(--weight-medium) var(--text-xs)/1.3 var(--font-sans);letter-spacing:var(--tracking-caps);text-transform:uppercase;color:var(--fg-3);list-style-position:inside}
details.more>summary:hover{color:var(--fg)}
details.more[open]>summary{border-bottom:1px solid var(--line)}
details.more .ds-table{border:0;border-radius:0;font-size:var(--text-xs)}
details.more .ds-table td,details.more .ds-table th{padding:7px 10px}
.wrong{list-style:none;margin:0;padding:8px 12px;display:grid;gap:8px;font-size:var(--text-sm)}
.wrong li{display:grid;gap:2px}.wrong li b{color:var(--fg);font-weight:var(--weight-semibold)}.wrong li span{color:var(--fg-2)}
.ds-check{grid-template-columns:20px 1fr}
.ds-check .tgt{display:block;margin-top:4px;font-family:var(--font-mono);font-size:var(--text-xs);color:var(--fg)}
.ds-check .rec{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin-top:8px}
.ds-check .rec input[type=text]{height:30px;width:min(220px,100%);padding:0 8px;border:1px solid var(--st-checked-line);border-radius:var(--radius-sm);background:var(--panel);color:var(--fg);font:var(--text-sm) var(--font-mono)}
.ds-check .pass{display:inline-flex;align-items:center;gap:6px;font-weight:var(--weight-semibold);color:var(--st-checked);cursor:pointer}
.ds-check .ds-source{display:block;margin-top:4px}
.stepfoot{display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:var(--text-xs);color:var(--fg-3)}
.stepfoot a{color:var(--fg-2)}
.step.done{border-color:var(--st-verified-line)}
.step.done .step-no{color:var(--st-verified)}
/* kits and tables */
.kitgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--space-4);padding:var(--space-4)}
.kitgrid .ds-table{font-size:var(--text-xs)}
.kitgrid .ds-table td,.kitgrid .ds-table th{padding:6px 10px}
.kitgrid .ds-table caption{font-size:var(--text-sm)}
td.tk{width:28px;text-align:center}
.miss td{color:var(--st-unverified)!important}
.gloss{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:0 var(--space-6);margin:0}
.gloss div{padding:10px 0;border-bottom:1px solid var(--line);display:grid;gap:2px}
.gloss dt{font-weight:var(--weight-semibold);color:var(--fg)}
.gloss dd{margin:0;color:var(--fg-2);font-size:var(--text-sm)}
.issues{margin:0;padding-left:1.2em;font:var(--text-xs)/1.6 var(--font-mono);color:var(--fg-2)}
.tbl-wrap{overflow-x:auto}
#tip{position:fixed;z-index:60;max-width:320px;pointer-events:none;opacity:0;transition:opacity var(--dur-fast);box-shadow:var(--shadow-pop)}
#tip.on{opacity:1}
#tip .ds-part{max-width:320px}
#tip .def{padding:10px 12px;font-size:var(--text-sm);color:var(--fg-2)}
#tip .def b{display:block;color:var(--fg);margin-bottom:2px}
dialog#lb{border:0;padding:0;width:min(96vw,1700px);max-height:96vh;background:var(--panel);border-radius:var(--radius-lg);box-shadow:var(--shadow-pop);color:var(--fg)}
dialog#lb::backdrop{background:rgba(10,12,16,.72)}
dialog#lb .stage{cursor:default}
dialog#lb .cap{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 14px;font-size:var(--text-sm)}
@media (max-width:1180px){.ds-step.step{grid-template-columns:1fr}.ds-step.step > figure{border-right:0;border-bottom:1px solid var(--line)}.ds-step.step > figure .sticky{position:static}}
@media (max-width:980px){.shell{grid-template-columns:1fr}.rail{display:none}main{padding:var(--space-5) var(--space-4) var(--space-7)}.cover{grid-template-columns:1fr}}
@media (max-width:640px){.prog{min-width:0}.prog span{display:none}.ds-topbar .ttl small{display:none}.step .body{padding:var(--space-4)}.ds-kit{grid-template-columns:1fr}}
/* print: white paper, every step whole on its page side, all details open, no chrome */
@media print{
 @page{size:A4;margin:12mm}
 .ds-topbar,.rail,.no-print,.thumbs,.tick,.stepfoot,#tip,dialog{display:none!important}
 .shell{display:block}main{padding:0;gap:16px}
 body{font-size:10.5pt}
 .ds-step.step{grid-template-columns:1fr;break-inside:avoid;page-break-inside:avoid;border-color:#999}
 .ds-step.step > figure{border-right:0;border-bottom:1px solid #999}
 .ds-step.step > figure .sticky{position:static}
 .stage{max-width:150mm;margin:0 auto}
 section.wp{break-before:page}
 .acts li::after{content:"";width:12px;height:12px;border:1px solid #333;border-radius:2px;margin-top:3px}
 .ds-check .rec input[type=text]{border:0;border-bottom:1px solid #333;border-radius:0;width:60mm}
 details.more{break-inside:avoid}
 details.more>summary{list-style:none}
 a{color:inherit}
}
'''

SCRIPT = r'''
(function(){
var D=JSON.parse(document.getElementById('data').textContent);
var KEY='dbf-manual:'+D.id+':'+D.rev, S={};
try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){S={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}
var $=function(q,r){return (r||document).querySelector(q)}, $$=function(q,r){return Array.prototype.slice.call((r||document).querySelectorAll(q))};
// ---- persisted inputs
$$('input[data-k]').forEach(function(el){
  var k=el.dataset.k;
  if(el.type==='checkbox'){el.checked=!!S[k];el.addEventListener('change',function(){if(el.checked)S[k]=1;else delete S[k];save();update()})}
  else{el.value=S[k]||'';el.addEventListener('input',function(){if(el.value)S[k]=el.value;else delete S[k];save()})}
});
function update(){
  var done=0;
  $$('article.step').forEach(function(a){
    var p=$$('input[data-pass]',a), ok=p.length&&p.every(function(x){return x.checked});
    a.classList.toggle('done',ok); if(ok)done++;
    var l=$('.rail a[href="#'+a.id+'"]'); if(l)l.classList.toggle('done',ok);
    $$('.acts li',a).forEach(function(li){var c=$('input',li);li.classList.toggle('ticked',!!(c&&c.checked))});
  });
  var n=$$('article.step').length;
  $('#prog-bar').style.width=(n?100*done/n:0)+'%';
  $('#prog-txt').textContent=done+' / '+n+' steps checked';
  $('#prog').setAttribute('aria-valuenow',done);
}
update();
$('#reset').addEventListener('click',function(){if(confirm('Clear every tick and measured value on this device?')){S={};save();$$('input[data-k]').forEach(function(el){if(el.type==='checkbox')el.checked=false;else el.value=''});update()}});
// ---- theme
$('#theme').addEventListener('click',function(){
  var dark=document.documentElement.dataset.theme==='dark'||(!document.documentElement.dataset.theme&&matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.dataset.theme=dark?'light':'dark';try{localStorage.setItem('dbf-theme',document.documentElement.dataset.theme)}catch(e){}
});
$('#print').addEventListener('click',function(){window.print()});
var opened=[];
window.addEventListener('beforeprint',function(){opened=$$('details:not([open])');opened.forEach(function(d){d.open=true})});
window.addEventListener('afterprint',function(){opened.forEach(function(d){d.open=false})});
// ---- hover: part / edge / glossary tooltips, part box in the figure
var tip=$('#tip');
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function partHTML(id){var p=D.parts[id];if(!p)return '';
  var rows=[['Mass',p.mass_g!=null?p.mass_g+' g':'—'],['Make / buy',p.mob||'—'],['Material',p.material||'—'],['Vendor / file',p.vendor||'—'],['Fitted in',p.step||'not in any step']];
  return '<div class="ds-part"><header><span class="id" data-sub="'+id.slice(0,3)+'"><i class="sub"></i>'+esc(id)+'</span><span class="name">'+esc(p.name)+'<span class="ds-badge" data-status="'+esc(p.status)+'">'+esc(p.status)+'</span></span></header><section><dl class="ds-kv">'+rows.map(function(r){return '<dt>'+r[0]+'</dt><dd>'+esc(r[1])+'</dd>'}).join('')+'</dl></section></div>'}
function edgeHTML(id){var e=D.edges[id];if(!e)return '';
  return '<div class="ds-part"><header><span class="id">'+esc(id)+'</span><span class="name">'+esc(e.a)+' &rarr; '+esc(e.b)+'</span></header><section><dl class="ds-kv">'+e.rows.map(function(r){return '<dt>'+esc(r[0])+'</dt><dd>'+esc(r[1])+'</dd>'}).join('')+'</dl></section></div>'}
function show(el){
  var h='';
  if(el.dataset.part)h=partHTML(el.dataset.part);
  else if(el.dataset.edge)h=edgeHTML(el.dataset.edge);
  else if(el.dataset.term)h='<div class="ds-panel def"><b>'+esc(el.dataset.term)+'</b>'+esc(D.terms[el.dataset.term]||'')+'</div>';
  if(!h)return; tip.innerHTML=h; tip.classList.add('on');
  var r=el.getBoundingClientRect(), w=tip.offsetWidth, hh=tip.offsetHeight;
  var x=Math.min(Math.max(8,r.left),innerWidth-w-8), y=r.bottom+8; if(y+hh>innerHeight-8)y=r.top-hh-8;
  tip.style.left=x+'px';tip.style.top=Math.max(8,y)+'px';
  var art=el.closest('article.step'); if(art&&el.dataset.part)$$('rect.box[data-id="'+el.dataset.part+'"]',art).forEach(function(b){b.classList.add('on')});
}
function hide(el){tip.classList.remove('on');$$('rect.box.on').forEach(function(b){b.classList.remove('on')})}
$$('[data-part],[data-edge],[data-term]').forEach(function(el){
  el.addEventListener('mouseenter',function(){show(el)});el.addEventListener('mouseleave',hide);
  el.addEventListener('focus',function(){show(el)});el.addEventListener('blur',hide);
});
// ---- action <-> numbered dot
$$('article.step').forEach(function(a){
  $$('.acts li',a).forEach(function(li){
    li.addEventListener('mouseenter',function(){$$('.mk[data-n="'+li.dataset.n+'"]',a).forEach(function(m){m.classList.add('on')})});
    li.addEventListener('mouseleave',function(){$$('.mk.on',a).forEach(function(m){m.classList.remove('on')})});
  });
});
// ---- lightbox
var lb=$('#lb');
function openFig(stage,cap){var c=stage.cloneNode(true);$('.body',lb).innerHTML='';$('.body',lb).appendChild(c);$('.cap span',lb).textContent=cap||'';
  if(lb.showModal)lb.showModal();else lb.setAttribute('open','')}
$$('.step .stage').forEach(function(s){s.addEventListener('click',function(){openFig(s,s.dataset.cap)})});
$$('.thumb').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById('tpl-'+b.dataset.fig);if(t)openFig(t.content.firstElementChild,b.dataset.cap)})});
$('#lb-close').addEventListener('click',function(){lb.close()});
lb.addEventListener('click',function(e){if(e.target===lb)lb.close()});
// ---- keyboard: n / p = next / previous step; rail follows the scroll
var steps=$$('article.step');
function cur(){var y=innerHeight*0.3,best=0;steps.forEach(function(s,i){if(s.getBoundingClientRect().top<y)best=i});return best}
document.addEventListener('keydown',function(e){
  if(/INPUT|TEXTAREA/.test(document.activeElement.tagName)||e.ctrlKey||e.metaKey||e.altKey)return;
  if(e.key==='n'||e.key==='p'){var i=cur()+(e.key==='n'?1:-1);i=Math.max(0,Math.min(steps.length-1,i));steps[i].scrollIntoView({behavior:'smooth',block:'start'})}
});
var links=$$('.rail a');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){links.forEach(function(l){l.classList.toggle('on',l.getAttribute('href')==='#'+en.target.id)})}})},{rootMargin:'-30% 0px -65% 0px'});
  $$('main section[id], article.step').forEach(function(s){io.observe(s)})}
})();
'''


def read_css():
    out = []
    for n in ('tokens.css', 'components.css'):
        p = os.path.join(DS, n)
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                out.append(f.read())
    return '\n'.join(out)


def callout(level, text, title=None):
    cls, icon, word = CALLOUT.get(level, CALLOUT['note'])
    return ('<div class="ds-callout %s"><svg><use href="#%s"/></svg><span><b>%s</b> %s</span></div>'
            % (cls, icon, esc(title or word), text))


def stage_html(img_rel, sc, mks, fid, cap, roles_boxes=True):
    """Image + overlay SVG (numbered dots, hidden part boxes for hover)."""
    if not sc:
        return ('<div class="stage" data-cap="%s" style="aspect-ratio:16/10"><div class="none">Figure %s not rendered yet.'
                '<br>Run build_manual.py on a machine with Blender.</div></div>' % (esc(cap), esc(fid)))
    W, H = sc['size']
    boxes = ''
    if roles_boxes:
        for s in sc.get('shown', []):
            x0, y0, x1, y1 = s['bbox_px']
            boxes += '<rect class="box" data-id="%s" x="%d" y="%d" width="%d" height="%d" rx="10"/>' % (
                esc(s['id']), x0 - 8, y0 - 8, x1 - x0 + 16, y1 - y0 + 16)
    return ('<div class="stage" data-cap="%s"><img src="%s/%s.jpg" width="%d" height="%d" alt="%s" loading="lazy" decoding="async">'
            '<svg class="ovl" viewBox="0 0 %d %d" aria-hidden="true">%s%s</svg></div>'
            % (esc(cap), img_rel, esc(fid), W, H, esc(cap), W, H, boxes, F.marker_svg(mks)))


def legend(sc):
    roles = set(sc.get('legend', [])) if sc else set()
    out = []
    if 'focus' in roles:
        out.append('<span><i class="highlight"></i>fit now</span>')
    if 'context' in roles:
        out.append('<span><i class="built"></i>already fitted</span>')
    if 'ghost' in roles:
        out.append('<span><i class="ghost"></i>see-through</span>')
    return '<div class="ds-legend">%s</div>' % ''.join(out) if out else ''


def kit_lists(m, s, T):
    k = m.kit([s])
    parts = ''.join('<li><span class="q">%sx</span><span>%s <span class="nm">%s</span></span></li>'
                    % (qty(p['qty']), T(p['id']), esc(p['name'])) for p in k['parts'])
    fas = ''.join('<li><span class="q">%dx</span><span>%s</span></li>' % (f['qty'], T(f['item'])) for f in k['fasteners'])
    tools = ''.join('<li><span class="q">·</span><span>%s</span></li>' % T(t['tool']) for t in k['tools'])
    cons = ''.join('<li><span class="q">%s</span><span>%s</span></li>'
                   % (esc(('%s %s' % (qty(c['qty']), c['unit'])).strip()), T(c['item'])) for c in k['consumables'])
    none = '<li class="empty">none</li>'
    return ('<div class="ds-kit"><div><h3>Parts</h3><ul>%s</ul></div><div><h3>Fasteners</h3><ul>%s</ul></div>'
            '<div><h3>Tools</h3><ul>%s</ul></div><div><h3>Consumables</h3><ul>%s</ul></div></div>'
            % (parts or none, fas or none, tools or none, cons or none))


def joints_table(s, T):
    if not s['joints']:
        return ''
    rows = ''
    for j in s['joints']:
        js = j['stack'] or {}
        stack = ', '.join(x for x in [('%sx %s' % (js.get('count', 1), js['fastener'])) if js.get('fastener') else '',
                                      js.get('washer_nut', ''), ('insert ' + js['insert']) if js.get('insert') and
                                      not js['insert'].lower().startswith('none') else ''] if x) or j['spec']
        eng = ('%s mm (min %s)' % (js.get('engagement_mm'), js.get('min_engagement_mm'))) if js.get('engagement_mm') else '—'
        order = ('%s / %s' % (js.get('install_order', '—'), js.get('removal_order', '—'))) if js else '—'
        rows += ('<tr><td>%s</td><td>%s → %s</td><td>%s</td><td class="num">%s</td><td>%s</td><td>%s</td><td class="num">%s</td></tr>'
                 % (T(j['edge']), T(j['a']), T(j['b']), esc(stack), esc(eng), esc(js.get('torque', '—')),
                    esc(js.get('access', '—')), esc(order)))
    return ('<details class="more"><summary>Joint stacks (%d)</summary><div class="tbl-wrap"><table class="ds-table"><thead><tr>'
            '<th>Edge</th><th>Joins</th><th>Stack</th><th class="num">Thread</th><th>Torque</th><th>Access</th>'
            '<th class="num">In / out</th></tr></thead><tbody>%s</tbody></table></div></details>' % (len(s['joints']), rows))


def wires_table(s, T):
    if not s['wires']:
        return ''
    rows = ''
    for w in s['wires']:
        x = w['wire']
        rows += ('<tr><td>%s</td><td>%s → %s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                 % (T(w['edge']), T(w['a']), T(w['b']), esc(x.get('connector', '—')),
                    esc(('%s AWG' % x['gauge_awg']) if x.get('gauge_awg') else '—'),
                    esc(('%s mm' % x['bend_radius_mm']) if x.get('bend_radius_mm') else '—'),
                    esc('; '.join(x.get('support_points', [])) or '—'), esc(x.get('strain_relief', '—')),
                    'yes' if x.get('disconnect') else 'no'))
    return ('<details class="more"><summary>Wiring (%d)</summary><div class="tbl-wrap"><table class="ds-table"><thead><tr>'
            '<th>Edge</th><th>From → to</th><th>Connector</th><th class="num">Gauge</th><th class="num">Bend r</th>'
            '<th>Supports</th><th>Strain relief</th><th>Disconnect</th></tr></thead><tbody>%s</tbody></table></div></details>'
            % (len(s['wires']), rows))


def step_card(m, s, figinfo, T, nxt):
    seen = set()
    sid = s['id']
    figs = s['figures']
    main_fig = figs[0]['id'] if figs else None
    fi = figinfo.get(main_fig, {})
    cap = 'Step %d: %s' % (s['n'], s['title'])
    cam = (figs[0]['camera'].get('preset') if figs else '') or ''
    lens = (figs[0]['camera'].get('lens', 70 if cam == 'closeup' else 50) if figs else '')
    fig = ['<figure><div class="sticky">', stage_html('img', fi.get('sc'), fi.get('markers', []), main_fig or sid, cap),
           '<div class="figbar"><span class="fid">FIG %s · %s %s mm</span>%s</div>' % (esc(sid), esc(cam), esc(lens), legend(fi.get('sc')))]
    if len(figs) > 1:
        fig.append('<div class="thumbs">')
        for k, d in enumerate(figs[1:], 1):
            di = figinfo.get(d['id'], {})
            title = (s.get('details') or [{}])[k - 1].get('title', 'Detail %d' % k)
            pic = ('<img src="img/%s.jpg" alt="" loading="lazy">' % esc(d['id'])) if di.get('sc') else '<img alt="">'
            fig.append('<button class="thumb" data-fig="%s" data-cap="%s">%s<span>%s</span></button>'
                       % (esc(d['id']), esc(title), pic, esc(title)))
            fig.append('<template id="tpl-%s">%s</template>' % (esc(d['id']), stage_html('img', di.get('sc'), di.get('markers', []), d['id'], title)))
        fig.append('</div>')
    fig.append('</div></figure>')
    t = s.get('time_min') or 0
    w = s.get('wait_min') or 0
    time_txt = fmt_min(t) + (' + %s wait' % fmt_min(w) if w else '')
    body = ['<div class="body">',
            '<div class="step-head"><span class="step-no"><small>STEP</small>%d</span><span class="step-title">%s</span>'
            '<span class="time">%s</span></div>' % (s['n'], esc(s['title']), esc(time_txt)),
            '<div class="tags"><span>%s</span><span>%s</span><span class="ds-badge" data-status="%s">%s</span></div>'
            % (esc(s['wp']), esc(sid), esc(s['status']), esc(s['status']))]
    if s.get('goal'):
        body.append('<p class="goal"><b>Goal</b> %s</p>' % T(s['goal'], seen))
    for x in s.get('safety', []):
        body.append(callout(x.get('level'), T(x.get('text', ''), seen)))
    acts = ''
    for n, a in enumerate(s['actions_n'], 1):
        acts += ('<li data-n="%d"><span>%s</span><label class="tick" title="Done"><input type="checkbox" data-k="%s:a%d" '
                 'aria-label="Action %d done"></label></li>' % (n, T(a['do'], seen), sid, n, n))
    body.append('<ol class="ds-actions acts">%s</ol>' % acts)
    body.append(kit_lists(m, s, T))
    body.append(joints_table(s, T) + wires_table(s, T))
    for k, c in enumerate(s['checks']):
        src = '<span class="ds-source"><b>Target from</b> %s</span>' % esc(c['source']) if c.get('source') else ''
        body.append('<div class="ds-check"><svg><use href="#i-check"/></svg><span><b>CHECK</b> %s'
                    '<span class="tgt">Target: %s</span>%s<span class="rec"><input type="text" data-k="%s:m%d" placeholder="%s" '
                    'aria-label="Measured value"><label class="pass"><input type="checkbox" data-pass data-k="%s:p%d"> Pass</label>'
                    '</span></span></div>' % (T(c.get('text', ''), seen), T(c.get('target', '')), src, sid, k,
                                              esc(c.get('record', 'measured')), sid, k))
    if s.get('can_go_wrong'):
        li = ''.join('<li><b>%s</b><span>%s</span></li>' % (T(g.get('problem', '')), T(g.get('fix', '')))
                     for g in s['can_go_wrong'])
        body.append('<details class="more"><summary>What can go wrong (%d)</summary><ul class="wrong">%s</ul></details>'
                    % (len(s['can_go_wrong']), li))
    miss = fi.get('missing') or []
    if miss:
        body.append('<p class="ds-meta">Action %s: its anchor is not visible in this figure.</p>' % ', '.join(map(str, miss)))
    body.append('<div class="stepfoot no-print"><span>%s</span>%s</div>' % (
        esc(s['_file']), ('<a href="#step-%s">Next: step %d &darr;</a>' % (nxt['id'], nxt['n'])) if nxt else ''))
    body.append('</div>')
    return '<article class="ds-step step" id="step-%s" data-step="%s">%s%s</article>' % (sid, sid, ''.join(fig), ''.join(body))


def kit_tables(m, w, T, key):
    k = m.kit(w['steps'])
    tk = lambda kk: '<td class="tk"><input type="checkbox" data-k="kit:%s:%s" aria-label="picked"></td>' % (key, esc(kk))
    parts = ''.join('<tr>%s<td>%s</td><td>%s</td><td class="num">%s</td><td>%s</td><td class="src">%s</td></tr>'
                    % (tk(p['id']), T(p['id']), esc(p['name']), qty(p['qty']), esc(p['make_or_buy']), esc(p['vendor']))
                    for p in k['parts'])
    fas = ''.join('<tr>%s<td>%s</td><td class="num">%d</td><td class="src">%s</td></tr>'
                  % (tk(f['item']), esc(f['item']), f['qty'], ' '.join(f['steps'])) for f in k['fasteners'])
    cons = ''.join('<tr>%s<td>%s</td><td class="num">%s</td><td class="src">%s</td></tr>'
                   % (tk(c['item']), esc(c['item']), esc(('%s %s' % (qty(c['qty']), c['unit'])).strip()), ' '.join(c['steps']))
                   for c in k['consumables'])
    tools = ''.join('<tr>%s<td>%s</td><td class="src">%s</td></tr>' % (tk(t['tool']), esc(t['tool']), ' '.join(t['steps']))
                    for t in k['tools'])
    empty = '<tr><td colspan="6" class="ds-meta">none</td></tr>'
    return ('<div class="kitgrid">'
            '<table class="ds-table"><caption>Parts</caption><thead><tr><th></th><th>Id</th><th>Name</th><th class="num">Qty</th><th>Make / buy</th><th>Vendor / file</th></tr></thead><tbody>%s</tbody></table>'
            '<table class="ds-table"><caption>Fasteners</caption><thead><tr><th></th><th>Item</th><th class="num">Qty</th><th>Steps</th></tr></thead><tbody>%s</tbody></table>'
            '<table class="ds-table"><caption>Consumables</caption><thead><tr><th></th><th>Item</th><th class="num">Qty</th><th>Steps</th></tr></thead><tbody>%s</tbody></table>'
            '<table class="ds-table"><caption>Tools</caption><thead><tr><th></th><th>Tool</th><th>Steps</th></tr></thead><tbody>%s</tbody></table>'
            '</div>' % (parts or empty, fas or empty, cons or empty, tools or empty)), k


def page(m, figinfo, terms, overview):
    T = Text(m, terms)
    meta = m.meta
    title = meta.get('title', 'Build manual')
    allk = m.kit(m.steps)
    mass = sum(float(p.get('mass_g') or 0) for p in m.parts.values() if p.get('flight', True) is not False)  # no ground tools
    n_fas = sum(f['qty'] for f in allk['fasteners'])
    # ----- data for the hover panels
    data = {'id': meta.get('id', 'manual'), 'rev': meta.get('revision', ''), 'parts': {}, 'edges': {},
            'terms': {t['term']: t['def'] for t in terms}}
    for pid, p in m.parts.items():
        row = p.get('csv', {})
        data['parts'][pid] = {'name': p.get('name', ''), 'mass_g': p.get('mass_g'), 'status': p.get('status', 'PROPOSED'),
                              'mob': p.get('make_or_buy') or row.get('make_or_buy', ''), 'material': p.get('material', ''),
                              'vendor': row.get('vendor_or_file', ''),
                              'step': ('step %d (%s)' % (next(s['n'] for s in m.steps if s['id'] == m.installed_in[pid]),
                                                         m.installed_in[pid])) if pid in m.installed_in else ''}
    for eid, e in m.edges.items():
        ct = m.ctypes.get(e.get('via'), {})
        rows = [['How', ct.get('spec', e.get('via', ''))]]
        js, wb = e.get('joint_stack'), e.get('wire')
        if js:
            rows += [['Fastener', '%sx %s %s' % (js.get('count', 1), js.get('fastener', ''), js.get('grade', ''))],
                     ['Torque', js.get('torque', '—')], ['Tool', js.get('tool', '—')], ['Access', js.get('access', '—')]]
        if wb:
            rows += [['Connector', wb.get('connector', '—')], ['Gauge', '%s AWG' % wb.get('gauge_awg', '—')],
                     ['Bend radius', '%s mm' % wb.get('bend_radius_mm', '—')]]
        if e.get('notes'):
            rows.append(['Note', e['notes']])
        rows.append(['Made in', m.installed_in.get(eid, 'not in any step')])
        data['edges'][eid] = {'a': e.get('part_a'), 'b': e.get('part_b'), 'rows': rows}
    # ----- rail
    rail = ['<nav class="rail" aria-label="Contents"><div class="ds-label">Manual</div><a href="#cover">Overview</a>'
            '<a href="#safety">Safety</a><a href="#sequence">Build sequence</a>']
    for w in m.wps:
        rail.append('<div class="ds-label">%s · %s</div>' % (esc(w['id']), esc(w.get('title', ''))))
        rail.append('<a href="#wp-%s"><span class="n">kit</span>Parts, fasteners, tools</a>' % esc(w['id']))
        for s in w['steps']:
            rail.append('<a href="#step-%s"><span class="n">%d</span><span>%s</span><svg class="ok"><use href="#i-check"/></svg></a>'
                        % (s['id'], s['n'], esc(s['title'])))
    rail.append('<div class="ds-label">Reference</div><a href="#kitting">Kitting list</a><a href="#tools">Tool list</a>'
                '<a href="#parts">Parts index</a><a href="#glossary">Glossary</a><a href="#log">Build log</a>'
                '<a href="#issues">Open items</a></nav>')
    # ----- cover
    cov = overview.get('cover')
    hero = ('<figure class="hero"><img src="img/%s" alt="%s" width="1600" height="1100"></figure>' % (esc(cov['file']), esc(cov['cap']))
            if cov else '')
    metrics = [('Steps', str(len(m.steps)), ''), ('Hands-on', fmt_min(allk['time_min']), ''),
               ('Waiting (cure)', fmt_min(allk['wait_min']), ''), ('Parts', str(len(m.parts)), ''),
               ('Fasteners', str(n_fas), 'pcs'), ('Flying mass', L.num(mass), 'g')]
    met = ''.join('<div class="ds-metric"><span class="k">%s</span><span class="v">%s<span class="ds-unit">%s</span></span></div>'
                  % (esc(k), esc(v), esc(u)) for k, v, u in metrics)
    open_n = len(m.missing_parts) + len(m.missing_edges)
    status = meta.get('status', 'PROPOSED')
    cover = ('<section id="cover"><div class="cover"><div class="lead"><span class="ds-label">Build manual · %s rev %s · %s</span>'
             '<h1 class="ds-display">%s</h1><p class="sub">%s</p><div class="ds-row"><span class="ds-badge" data-status="%s">%s</span>'
             '<span class="ds-meta">%s</span></div></div>%s</div>'
             % (esc(meta.get('id', '')), esc(meta.get('revision', '')), esc(meta.get('date', '')), esc(title),
                esc(meta.get('subtitle', '')), esc(status), esc(status),
                ('%d parts or interfaces not yet in any step: see Open items' % open_n) if open_n else
                'every part and interface is installed by a step', hero))
    cover += '<div class="ds-metrics" style="margin-top:24px">%s</div>' % met
    cover += ('<div class="howto" style="margin-top:16px">'
              '<div><span class="sw" style="background:var(--highlight)"></span><span><b>Orange = fit now</b>Parts in their own colour are already fitted; '
              'see-through parts are only there to show the inside.</span></div>'
              '<div><span class="dot">1</span><span><b>Numbers match actions</b>Each orange number in the picture is the action with the same number. '
              'Hover an action to find its number.</span></div>'
              '<div><svg class="sw" style="color:var(--st-checked)"><use href="#i-check"/></svg><span><b>Every step ends with a CHECK</b>Measure, write the value, tick Pass. '
              'Ticks stay on this device.</span></div>'
              '<div><span class="ds-kbd" style="margin-top:3px">n</span><span><b>Keys</b><span class="ds-kbd">n</span> next step, '
              '<span class="ds-kbd">p</span> previous. Hover a part id for its name, mass and vendor.</span></div></div></section>')
    # ----- safety
    saf = ''.join(callout(x.get('level'), T(x.get('text', '')), x.get('title')) for x in meta.get('safety', []))
    safety = ('<section id="safety"><div class="sechead"><h2 class="ds-h1">Safety</h2><p class="ds-body">Read once before the first '
              'session. Steps repeat the rule where it applies.</p></div><div class="safety">%s</div></section>' % (saf or
              '<p class="ds-meta">No manual-level safety rules given (manual.json "safety").</p>'))
    # ----- sequence
    seq_rows = ''
    for s in m.steps:
        seq_rows += ('<tr><td class="num">%d</td><td>%s</td><td><a class="ds-link" href="#step-%s">%s</a></td><td>%s</td>'
                     '<td class="num">%s</td><td class="num">%s</td></tr>'
                     % (s['n'], esc(s['wp']), s['id'], esc(s['title']), ' '.join(T(p['id']) for p in s['parts_n']) or
                        '<span class="ds-meta">joins earlier parts</span>', esc(fmt_min(s.get('time_min'))),
                        esc(fmt_min(s.get('wait_min'))) if s.get('wait_min') else '—'))
    exfig = ''.join('<figure class="hero" style="margin-top:16px"><img src="img/%s" alt="%s" loading="lazy"></figure>'
                    % (esc(g['file']), esc(g['cap'])) for g in overview.get('gallery', []))
    sequence = ('<section id="sequence"><div class="sechead"><h2 class="ds-h1">Build sequence</h2><p class="ds-body">%d steps in %d '
                'work packages. A step starts only when the steps it depends on have passed their CHECK.</p></div>'
                '<div class="tbl-wrap"><table class="ds-table"><thead><tr><th class="num">Step</th><th>WP</th><th>Title</th>'
                '<th>Parts fitted</th><th class="num">Hands-on</th><th class="num">Wait</th></tr></thead><tbody>%s</tbody></table></div>%s</section>'
                % (len(m.steps), len(m.wps), seq_rows, exfig))
    # ----- work packages
    wps = []
    for w in m.wps:
        tables, k = kit_tables(m, w, T, w['id'])
        cards = []
        for s in w['steps']:
            i = m.steps.index(s)
            cards.append(step_card(m, s, figinfo, T, m.steps[i + 1] if i + 1 < len(m.steps) else None))
        wps.append('<section class="wp" id="wp-%s"><div class="sechead"><h2 class="ds-h1"><small>%s</small>%s</h2>'
                   '<p class="ds-body">%s</p><div class="wp-meta"><span><b>%d</b> steps</span><span><b>%s</b> hands-on</span>'
                   '<span><b>%s</b> waiting</span><span><b>%d</b> tools</span></div></div>'
                   '<details class="more" style="margin-bottom:24px"><summary>Kit for %s: pick everything before step %d</summary>%s</details>'
                   '<div class="ds-stack" style="gap:28px">%s</div></section>'
                   % (esc(w['id']), esc(w['id']), esc(w.get('title', '')), esc(w.get('summary', '')), len(w['steps']),
                      fmt_min(k['time_min']), fmt_min(k['wait_min']), len(k['tools']), esc(w['id']),
                      w['steps'][0]['n'] if w['steps'] else 0, tables, ''.join(cards)))
    # ----- reference: kitting (all), tools, parts, glossary, log, issues
    kit_all = ''.join('<h3 class="ds-h2" style="margin:20px 0 0">%s · %s</h3>%s' % (esc(w['id']), esc(w.get('title', '')),
                      kit_tables(m, w, T, 'all-' + w['id'])[0]) for w in m.wps)
    kitting = ('<section id="kitting"><div class="sechead"><h2 class="ds-h1">Kitting list</h2><p class="ds-body">One bag or tray per '
               'work package. Fasteners are counted from the joint stacks in interfaces.json; tick as you pick. Also written as '
               '<code class="ds-inline">kitting.csv</code>.</p></div>%s</section>' % kit_all)
    trow = ''
    for t in allk['tools']:
        wpz = sorted({next(s['wp'] for s in m.steps if s['id'] == sid) for sid in t['steps']})
        trow += '<tr><td>%s</td><td>%s</td><td class="src">%s</td></tr>' % (esc(t['tool']), ' '.join(wpz),
                                                                            ' '.join('<a class="ds-link" href="#step-%s">%s</a>' % (x, x) for x in t['steps']))
    tools = ('<section id="tools"><div class="sechead"><h2 class="ds-h1">Tool list</h2><p class="ds-body">%d tools. Ground tools '
             'are never part of the flying mass. Also written as <code class="ds-inline">tools.csv</code>.</p></div>'
             '<table class="ds-table"><thead><tr><th>Tool</th><th>Work packages</th><th>Steps</th></tr></thead><tbody>%s</tbody></table></section>'
             % (len(allk['tools']), trow))
    prow = ''
    for pid in sorted(m.parts):
        p = m.parts[pid]
        row = p.get('csv', {})
        st = m.installed_in.get(pid)
        prow += ('<tr%s><td>%s</td><td>%s</td><td><span class="ds-badge" data-status="%s">%s</span></td><td>%s</td>'
                 '<td class="num">%s</td><td class="src">%s</td><td>%s</td></tr>'
                 % ('' if st else ' class="miss"', T(pid), esc(p.get('name', '')), esc(p.get('status', '')), esc(p.get('status', '')),
                    esc(p.get('make_or_buy') or row.get('make_or_buy', '')), esc(p.get('mass_g', '—')),
                    esc(row.get('vendor_or_file', '—')), ('<a class="ds-link" href="#step-%s">%s</a>' % (st, st)) if st else 'not in any step'))
    parts = ('<section id="parts"><div class="sechead"><h2 class="ds-h1">Parts index</h2><p class="ds-body">%d parts, %s g in total '
             '(declared masses, interfaces.json).</p></div><div class="tbl-wrap"><table class="ds-table"><thead><tr><th>Id</th><th>Name</th>'
             '<th>Status</th><th>Make / buy</th><th class="num">Mass g</th><th>Vendor / file</th><th>Fitted in</th></tr></thead>'
             '<tbody>%s</tbody></table></div></section>' % (len(m.parts), L.num(mass), prow))
    gl = ''.join('<div id="term-%s"><dt>%s</dt><dd>%s</dd></div>' % (esc(re.sub(r'\W+', '-', t['term'])), esc(t['term']), esc(t['def']))
                 for t in terms)
    gloss = ('<section id="glossary"><div class="sechead"><h2 class="ds-h1">Glossary</h2><p class="ds-body">For a first-time builder: '
             'the %d words this manual uses. Underlined words in the steps show these on hover.</p></div><dl class="gloss">%s</dl></section>'
             % (len(terms), gl))
    lrow = ''
    for s in m.steps:
        for k, c in enumerate(s['checks']):
            lrow += ('<tr><td class="num">%d</td><td>%s</td><td>%s</td><td class="num">%s</td><td><input type="text" data-k="%s:m%d" '
                     'aria-label="Measured" style="width:100%%;min-width:120px;border:0;border-bottom:1px solid var(--line-2);background:none;'
                     'color:var(--fg);font:inherit;font-family:var(--font-mono)"></td><td class="tk"><input type="checkbox" data-k="%s:p%d" '
                     'aria-label="Pass"></td><td style="min-width:90px"></td></tr>'
                     % (s['n'], esc(s['id']), T(c.get('text', '')), T(c.get('target', '')), s['id'], k, s['id'], k))
    log = ('<section id="log"><div class="sechead"><h2 class="ds-h1">Build log</h2><p class="ds-body">Every CHECK in one table. Fields '
           'are linked to the step cards. Print it and initial each line, or keep it on screen.</p></div><div class="tbl-wrap">'
           '<table class="ds-table"><thead><tr><th class="num">Step</th><th>Id</th><th>Check</th><th class="num">Target</th><th>Measured</th>'
           '<th>Pass</th><th>Initials, date</th></tr></thead><tbody>%s</tbody></table></div></section>' % lrow)
    iss = ''.join('<li>%s</li>' % esc(w) for w in m.warnings) or '<li>none</li>'
    issues = ('<section id="issues"><div class="sechead"><h2 class="ds-h1">Open items</h2><p class="ds-body">What the generator found '
              'incomplete (parts or interfaces no step installs, steps to split, checks that are not measurable). Missing parts stay '
              'listed here until a step installs them.</p></div><ul class="issues">%s</ul>'
              '<p class="ds-source" style="margin-top:12px"><b>Generated by</b> redesign/manual-kit/build_manual.py from %s</p></section>'
              % (iss, esc(', '.join(s + '/steps.json' for s in m.subsystems))))
    # ----- assemble
    data_json = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    head = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s</title><meta name="description" content="%s">'
            '<script>try{var t=localStorage.getItem("dbf-theme");if(t==="dark"||t==="light")document.documentElement.dataset.theme=t}catch(e){}</script>'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">'
            '<style>%s\n%s</style></head>' % (esc(title), esc(meta.get('subtitle', '')), read_css(), PAGE_CSS))
    top = ('<header class="ds-topbar"><a class="ds-brand" href="#cover"><svg class="mark"><use href="#i-brand"/></svg></a>'
           '<span class="ttl">%s<small>%s rev %s</small></span><span class="spacer"></span>'
           '<div class="prog" id="prog" role="progressbar" aria-valuemin="0" aria-valuemax="%d" aria-valuenow="0" aria-label="Steps checked">'
           '<div class="bar"><i id="prog-bar"></i></div><span id="prog-txt"></span></div>'
           '<button class="ds-iconbtn" id="print" title="Print or save as PDF" aria-label="Print"><svg><use href="#i-print"/></svg></button>'
           '<button class="ds-iconbtn" id="reset" title="Clear ticks on this device" aria-label="Clear ticks"><svg><use href="#i-reset"/></svg></button>'
           '<button class="ds-iconbtn" id="theme" title="Light / dark" aria-label="Switch theme"><svg><use href="#i-moon"/></svg></button></header>'
           % (esc(title), esc(meta.get('id', '')), esc(meta.get('revision', '')), len(m.steps)))
    lb = ('<dialog id="lb" aria-label="Figure"><div class="body"></div><div class="cap"><span></span>'
          '<button class="ds-btn" id="lb-close">Close</button></div></dialog><div id="tip" role="tooltip"></div>')
    return (head + '<body class="ds-base"><a class="skip" href="#main">Skip to the steps</a>' + ICONS + top +
            '<div class="shell">' + ''.join(rail) + '<main id="main">' + cover + safety + sequence + ''.join(wps) + kitting +
            tools + parts + gloss + log + issues + '</main></div>' + lb +
            '<script type="application/json" id="data">%s</script><script>%s</script></body></html>' % (data_json, SCRIPT))
