from data import *

CSS = r"""
:root{
  --bg:#ffffff; --bg-2:#f6f7f9; --ink:#14181f; --ink-2:#4b5563; --ink-3:#6b7280; --line:#e4e7ec; --line-2:#d0d5dd;
  --accent:#1f4fd8; --accent-bg:#eef2ff; --ok:#14705a; --ok-bg:#e6f5ef; --warn:#8a5a00; --warn-bg:#fdf3dc; --bad:#b42318; --bad-bg:#fdeceb;
  /* spacing 4 8 12 16 24 32 48 64 */
  --s1:4px;--s2:8px;--s3:12px;--s4:16px;--s5:24px;--s6:32px;--s7:48px;--s8:64px;
  --sans:"Public Sans",system-ui,sans-serif;--mono:"DM Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
 --bg:#0f1218;--bg-2:#151a22;--ink:#eceff4;--ink-2:#a9b2c0;--ink-3:#8791a1;--line:#242b36;--line-2:#323b49;
 --accent:#8fabff;--accent-bg:#1a2442;--ok:#6fd0b1;--ok-bg:#12292a;--warn:#e8bd5c;--warn-bg:#2b2412;--bad:#ff8a80;--bad-bg:#2e1a1a;}}
:root[data-theme=dark]{
 --bg:#0f1218;--bg-2:#151a22;--ink:#eceff4;--ink-2:#a9b2c0;--ink-3:#8791a1;--line:#242b36;--line-2:#323b49;
 --accent:#8fabff;--accent-bg:#1a2442;--ok:#6fd0b1;--ok-bg:#12292a;--warn:#e8bd5c;--warn-bg:#2b2412;--bad:#ff8a80;--bad-bg:#2e1a1a;}
*{box-sizing:border-box}
html{background:var(--bg);color:var(--ink);font:400 15px/1.6 var(--sans);-webkit-text-size-adjust:100%}
body{margin:0}
a{color:var(--accent);text-underline-offset:2px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
code,.mono{font-family:var(--mono);font-size:.9em}
.top{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;align-items:center;gap:var(--s5);padding:0 var(--s5);height:52px}
.brand{font-weight:600;font-size:15px;white-space:nowrap}.brand span{color:var(--ink-3);font-weight:400;margin-left:var(--s2)}
.top .sec{display:flex;gap:var(--s5);font-size:14px}
.top .sec a{color:var(--ink-2);text-decoration:none;height:52px;display:flex;align-items:center;border-bottom:2px solid transparent}
.top .sec a[aria-current]{color:var(--ink);border-color:var(--accent)}
.sp{flex:1}
.search{font-size:13px;color:var(--ink-3);border:1px solid var(--line-2);border-radius:6px;padding:5px 10px;min-width:190px;display:flex;justify-content:space-between}
.search kbd{font:12px var(--mono)}
.btn{font:13px var(--sans);background:none;border:1px solid var(--line-2);color:var(--ink);border-radius:6px;padding:5px 10px;cursor:pointer}
.mbtn{display:none}
.layout{display:grid;grid-template-columns:248px minmax(0,1fr) 208px;max-width:1380px;margin:0 auto}
.side{border-right:1px solid var(--line);padding:var(--s5) var(--s4);font-size:14px;position:sticky;top:52px;align-self:start;height:calc(100vh - 52px);overflow:auto}
.side h4{font:600 11px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);margin:var(--s5) 0 var(--s2) var(--s3)}
.side h4:first-child{margin-top:0}
.side a{display:block;padding:5px var(--s3);color:var(--ink-2);text-decoration:none;border-radius:6px}
.side a[aria-current]{background:var(--accent-bg);color:var(--accent);font-weight:500}
main{padding:var(--s7) var(--s7) var(--s8);min-width:0}
article{max-width:760px;margin:0 auto 96px}
.crumb{font-size:13px;color:var(--ink-3);margin:0 0 var(--s3)}
h1{font:600 34px/1.15 var(--sans);letter-spacing:-.015em;margin:0 0 var(--s3)}
h2{font:600 21px/1.3 var(--sans);margin:var(--s7) 0 var(--s3);padding-top:var(--s5);border-top:1px solid var(--line)}
h3{font:600 15px var(--sans);margin:var(--s5) 0 var(--s2)}
p{margin:0 0 var(--s4)} .lede{font-size:17px;color:var(--ink-2);line-height:1.55}
.meta{font-size:13px;color:var(--ink-3);display:flex;gap:var(--s5);flex-wrap:wrap;margin:var(--s4) 0 var(--s5)}
.rail{padding:var(--s7) var(--s4) 0 var(--s2);font-size:13px;position:sticky;top:52px;align-self:start}
.rail h4{font:600 12px var(--sans);margin:0 0 var(--s3);color:var(--ink)}
.rail a{display:block;color:var(--ink-3);text-decoration:none;padding:4px 0 4px var(--s3);border-left:1px solid var(--line)}
.rail a.on{color:var(--accent);border-color:var(--accent)}
.viewer{border:1px solid var(--line-2);border-radius:8px;overflow:hidden;background:var(--bg-2);margin:var(--s5) 0}
.vbar{display:flex;gap:var(--s2);padding:var(--s2) var(--s3);border-bottom:1px solid var(--line);font-size:13px;flex-wrap:wrap;align-items:center}
.seg{display:inline-flex;border:1px solid var(--line-2);border-radius:6px;overflow:hidden}
.seg span{padding:3px 10px;color:var(--ink-2);border-left:1px solid var(--line-2)} .seg span:first-child{border-left:0}
.seg .on{background:var(--ink);color:var(--bg)}
.vimg{aspect-ratio:16/9;background:#e9edf2}.vimg img{width:100%;height:100%;object-fit:cover;display:block}
:root[data-theme=dark] .vimg img{filter:brightness(.8)}
.vfoot{padding:var(--s2) var(--s3);font-size:12.5px;color:var(--ink-3);border-top:1px solid var(--line)}
dl.kv{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin:var(--s5) 0;border:1px solid var(--line);border-radius:8px}
dl.kv div{padding:var(--s3) var(--s4);border-left:1px solid var(--line)} dl.kv div:first-child{border-left:0}
dl.kv dt{font-size:12.5px;color:var(--ink-3)} dl.kv dd{margin:2px 0 0;font:500 22px/1.2 var(--sans);font-variant-numeric:tabular-nums} dl.kv dd small{display:block;font:400 12px var(--sans);color:var(--ink-3)}
table{width:100%;border-collapse:collapse;font-size:14px;margin:var(--s3) 0}
th{text-align:left;font-weight:600;font-size:12.5px;color:var(--ink-3);padding:var(--s2) var(--s3);border-bottom:1px solid var(--line-2);white-space:nowrap}
td{padding:var(--s3);border-bottom:1px solid var(--line);vertical-align:top}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap} th.num{text-align:right}
td.id{font:13px var(--mono);color:var(--ink-3);white-space:nowrap}
.tag{display:inline-block;font:500 12px/1.5 var(--sans);padding:0 8px;border-radius:99px;white-space:nowrap}
.t-done,.t-v{background:var(--ok-bg);color:var(--ok)}
.t-partial,.t-unverified,.t-marginal,.t-est{background:var(--warn-bg);color:var(--warn)}
.t-open{background:var(--bad-bg);color:var(--bad)}
.t-todo{background:var(--bg-2);color:var(--ink-3);box-shadow:inset 0 0 0 1px var(--line)}
.callout{border-left:3px solid var(--warn);background:var(--warn-bg);padding:var(--s3) var(--s4);border-radius:0 6px 6px 0;margin:var(--s5) 0;font-size:14px}
.callout b{display:block;margin-bottom:2px}
ol.steps{list-style:none;margin:var(--s4) 0;padding:0}
ol.steps li{display:grid;grid-template-columns:32px 1fr auto;gap:var(--s3);padding:var(--s3) 0;border-bottom:1px solid var(--line)}
ol.steps .no{font:13px var(--mono);color:var(--ink-3);padding-top:2px}
ol.steps b{font-weight:600} ol.steps p{margin:2px 0 0;color:var(--ink-2);font-size:14px}
ol.steps .ref{font:12.5px var(--mono);color:var(--ink-3);display:block;margin-top:2px}
.src{font:12.5px var(--mono);color:var(--ink-3);display:block;margin-top:4px}
.hbar{display:grid;grid-template-columns:100px 1fr 80px;gap:var(--s3);align-items:center;font-size:14px;padding:5px 0}
.hbar i{display:block;height:8px;background:var(--accent);border-radius:2px;opacity:.85}.hbar b{font-weight:500;text-align:right;font-variant-numeric:tabular-nums}
.scroll{overflow-x:auto}
.pgsep{border:0;border-top:1px dashed var(--line-2);margin:0 0 var(--s7)}
@media (max-width:1100px){.layout{grid-template-columns:232px minmax(0,1fr)}.rail{display:none}}
@media (max-width:820px){
 .top{padding:0 var(--s4);gap:var(--s3)}.top .sec,.search{display:none}.mbtn{display:block}
 .layout{display:block}.side{display:none;position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
 #menu:checked ~ .layout .side{display:block}
 main{padding:var(--s5) var(--s4) var(--s7)} h1{font-size:28px}
 dl.kv{grid-template-columns:1fr 1fr}dl.kv div:nth-child(3){border-left:0}dl.kv div:nth-child(n+3){border-top:1px solid var(--line)}
 ol.steps li{grid-template-columns:28px 1fr}ol.steps li>span:last-child{grid-column:2}
 .hbar{grid-template-columns:80px 1fr 64px}.col-hide{display:none}
}
"""

def side(cur):
    groups=[("Overview",["Aircraft"]),("The case",["Decision","Proofs","Subsystems","Team"]),("The plan",["Build guide","Status","BOM","Docs"])]
    h=""
    for g,items in groups:
        h+="<h4>%s</h4>"%g+"".join('<a href="#%s"%s>%s</a>'%(i.lower().replace(" ","-"),' aria-current="page"' if i==cur else "",i) for i in items)
    return h

def build():
    mass="".join("<tr><td>%s</td><td class=num>%s g</td></tr>"%(n,"%g"%v) for n,v in MASS)
    steps="".join('<li><span class=no>%s</span><div><b>%s</b><p>%s</p><span class=ref>%s</span></div><span><span class="tag t-%s">%s</span></span></li>'%(n,t,d,r,s,STATE[s]) for n,t,s,d,r in PHASES)
    iss="".join('<tr><td class=id>%s</td><td><b>%s.</b> %s<span class=src>%s</span></td><td class=col-hide>%s</td><td><span class="tag t-%s">%s</span></td></tr>'%(n,t,d,src,o,s.lower(),s) for n,t,d,o,src,s in ISSUES)
    rows="".join('<tr><td class=id>%s</td><td>%s</td><td class=col-hide>%s</td><td class=col-hide>%s</td><td class=num>%d</td><td class=num>%s</td><td class=num>%s</td><td><span class="tag t-%s">%s</span></td></tr>'%(l,i,g,v,q,money(u),money(q*u),p.lower(),p) for l,i,g,v,q,u,p,o,c in BOM)
    gm=max(v for _,v in GROUPS)
    bars="".join('<div class=hbar><span>%s</span><i style="width:%d%%"></i><b>%s</b></div>'%(n,v/gm*100,money(v)) for n,v in GROUPS)
    t=TPL
    for k,v in {"CSS":CSS,"SIDE_A":side("Aircraft"),"SIDE_S":side("Status"),"SIDE_B":side("BOM"),"MASS":mass,"STEPS":steps,"ISSUES":iss,"ROWS":rows,"BARS":bars}.items(): t=t.replace("{{%s}}"%k,v)
    return t

TPL = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Concept 2 · Calm docs</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>{{CSS}}</style></head><body>
<!--
 CONCEPT 2 "Calm docs": Stripe / Tailwind / PX4 documentation pattern.
 Type: Public Sans (UI and text, 15/24) + DM Mono (identifiers, line ids, sources). Scale 12.5 / 14 / 15 / 17 / 21 / 34.
 Light = white / slate #14181f / blue #1f4fd8; dark = #0f1218 / #eceff4 / #8fabff. Status colour only on tags: green, amber, red, grey.
 Spacing 4 8 12 16 24 32 48 64. Radius 6 (controls) and 8 (panels), nothing else. Nav: 3 grouped sections in a left tree, top bar with 2 sections, right "On this page" rail.
 Under 820 px: tree hides behind a Menu button, tables lock to 3 to 4 columns.
-->
<input type="checkbox" id="menu" hidden>
<header class="top"><span class="brand">Concept A<span>DBF VTOL</span></span>
 <nav class="sec" aria-label="Sections"><a href="#" aria-current="page">Explorer</a><a href="#">Archive (K09-L)</a></nav><span class="sp"></span>
 <span class="search">Search parts, claims, lines <kbd>/</kbd></span>
 <label for="menu" class="btn mbtn" role="button" tabindex="0">Menu</label>
 <button class="btn" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">Theme</button></header>

<div class="layout"><aside class="side" aria-label="Pages">{{SIDE_A}}</aside>
<main>
<article id="aircraft">
 <p class="crumb">Explorer / Overview / Aircraft</p>
 <h1>Aircraft</h1>
 <p class="lede">A 3-D model of concept A with 106 flight parts, 141 interfaces and 63 claims. Click a part for its numbers, interfaces and sources.</p>
 <div class="meta"><span>Data built 2026-11-16 07:46 UTC</span><span>Status: proposed (D-182)</span></div>
 <div class="viewer"><div class="vbar"><span class="seg"><span class="on">Aircraft</span><span>Inside &amp; wiring</span><span>Structure</span><span>Exploded</span></span><span class="seg"><span class="on">Cruise</span><span>Hover</span></span><span class="seg"><span>Realistic</span><span>Subsystem</span><span>Status</span></span></div>
 <div class="vimg"><img src="../assets/renders/a-hero-iso.webp" alt="Placeholder for the 3-D viewer: render of concept A"></div>
 <div class="vfoot">Viewer area (placeholder render). Drag to rotate, scroll to zoom, click a part, H shows fasteners.</div></div>
 <dl class="kv"><div><dt>Declared mass</dt><dd>1,263 g<small>of 1,500 g gate</small></dd></div><div><dt>CG x</dt><dd>0.021 m<small>target 0.004 to 0.029</small></dd></div><div><dt>Claims</dt><dd>63<small>0 failing</small></dd></div><div><dt>Interfaces</dt><dd>141</dd></div></dl>
 <h2>Mass by subsystem</h2>
 <table><thead><tr><th>Subsystem</th><th class=num>Mass</th></tr></thead><tbody>{{MASS}}</tbody></table>
</article>
<hr class="pgsep">
<div class="layout" style="display:block;max-width:none"><article id="status">
 <p class="crumb">Explorer / The plan / Status</p>
 <h1>Status</h1>
 <p class="lede">Five of ten phases are done, one is partial and four have not started. Nothing is bought, built or flown.</p>
 <div class="meta"><span>Concept A (D-182)</span><span>Updated 2026-11-15</span><span>Claims: strict build, 0 failing</span></div>
 <div class="callout"><b>What "done" means</b>The round delivered and its decisions are logged in CHANGE-LOG. It does not mean verified.</div>
 <h2>Programme</h2><ol class="steps">{{STEPS}}</ol>
 <h2>Open issues</h2>
 <div class="scroll"><table><thead><tr><th>#</th><th>Issue and source</th><th class=col-hide>Owner</th><th>State</th></tr></thead><tbody>{{ISSUES}}</tbody></table></div>
</article></div>
<hr class="pgsep">
<div class="layout" style="display:block;max-width:none"><article id="bom">
 <p class="crumb">Explorer / The plan / BOM</p>
 <h1>Bill of materials</h1>
 <p class="lede">41 lines, all bought new, against the $2,000 limit. V means the price was read on the vendor page; EST is an estimate. Nothing is bought yet.</p>
 <div class="meta"><span>Prices read 2026-11-14/15</span><span>Tax 10.25 %, shipping per vendor (estimate), FAA fee, then a crash reserve</span></div>
 <dl class="kv"><div><dt>Total with reserve</dt><dd>$1,779.47<small>spend $1,452.04 + reserve $327.43</small></dd></div><div><dt>Margin to $2,000</dt><dd>$220.53<small>+$100.05 if unverified lines run 30 % over</small></dd></div><div><dt>Goods</dt><dd>$1,262.50<small>+ tax, shipping, FAA</small></dd></div><div><dt>Order 1, early Dec</dt><dd>$967.90<small>bench kit, 2 motors</small></dd></div></dl>
 <h2>Where the money goes</h2>{{BARS}}
 <h2>Lines</h2>
 <div class="scroll"><table><thead><tr><th>Line</th><th>Item</th><th class=col-hide>Group</th><th class=col-hide>Vendor</th><th class=num>Qty</th><th class=num>Unit</th><th class=num>Ext</th><th>Price</th></tr></thead><tbody>{{ROWS}}</tbody></table></div>
 <p class="src">12 of 41 lines shown. Source: qp/A/BOM-A.csv, totals from bom_a.py.</p>
</article></div>
</main>
<aside class="rail" aria-label="On this page"><h4>On this page</h4><a class="on" href="#">Key numbers</a><a href="#">Mass by subsystem</a><a href="#">Programme</a><a href="#">Open issues</a><a href="#">Where the money goes</a><a href="#">Lines</a></aside>
</div>
<script>if(location.hash==='#dark')document.documentElement.dataset.theme='dark'</script>
</body></html>
"""
if __name__=="__main__": open("concept-2.html","w",encoding="utf8").write(build())
