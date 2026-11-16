from data import *

CSS = r"""
:root{
  /* dark first: instrument panel */
  --bg:#0a0d10;--panel:#10151a;--panel-2:#151b21;--line:#222b33;--line-2:#2f3a44;--ink:#e6ebef;--ink-2:#9aa6b2;--ink-3:#6d7a87;
  --amber:#f5a524;--green:#3ddc97;--red:#ff6b5e;--cyan:#5bc0eb;
  /* spacing 2 4 8 12 16 24 */
  --s0:2px;--s1:4px;--s2:8px;--s3:12px;--s4:16px;--s5:24px;
  --sans:"IBM Plex Sans Condensed","IBM Plex Sans",system-ui,sans-serif;--mono:"JetBrains Mono",ui-monospace,monospace;
}
:root[data-theme=light]{--bg:#e9edf0;--panel:#ffffff;--panel-2:#f3f5f7;--line:#d5dbe1;--line-2:#b9c2cb;--ink:#12181e;--ink-2:#46525e;--ink-3:#66727e;--amber:#9a5b00;--green:#0d7a50;--red:#b3261e;--cyan:#0b6a96}
@media (prefers-color-scheme:light){:root:not([data-theme=dark]):not([data-theme=light]){--bg:#e9edf0;--panel:#ffffff;--panel-2:#f3f5f7;--line:#d5dbe1;--line-2:#b9c2cb;--ink:#12181e;--ink-2:#46525e;--ink-3:#66727e;--amber:#9a5b00;--green:#0d7a50;--red:#b3261e;--cyan:#0b6a96}}
*{box-sizing:border-box}
html{background:var(--bg);color:var(--ink);font:400 14px/1.45 var(--sans);-webkit-text-size-adjust:100%}
body{margin:0}
a{color:var(--cyan);text-underline-offset:2px}
:focus-visible{outline:2px solid var(--amber);outline-offset:1px}
.m{font-family:var(--mono);font-variant-numeric:tabular-nums}
.bar{display:flex;align-items:stretch;border-bottom:1px solid var(--line-2);background:var(--panel);font-size:12px;overflow:hidden}
.bar>div{padding:var(--s2) var(--s4);border-right:1px solid var(--line);white-space:nowrap}
.bar .id{font-weight:600;font-size:14px;letter-spacing:.02em}
.bar small{display:block;color:var(--ink-3);font-size:10px;letter-spacing:.1em;text-transform:uppercase}
.bar b{font:500 14px var(--mono)}
.bar .sp{flex:1;border:0}
.bar .ok{color:var(--green)}
.shell{display:grid;grid-template-columns:168px minmax(0,1fr);min-height:calc(100vh - 41px)}
.rail{border-right:1px solid var(--line-2);background:var(--panel);padding:var(--s2) 0;font-size:13px}
.rail a{display:flex;justify-content:space-between;padding:6px var(--s4);color:var(--ink-2);text-decoration:none;border-left:2px solid transparent}
.rail a kbd{font:11px var(--mono);color:var(--ink-3)}
.rail a[aria-current]{color:var(--ink);background:var(--panel-2);border-left-color:var(--amber)}
.rail h6{margin:var(--s4) var(--s4) var(--s1);font:500 10px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
.mbtn{display:none}
main{padding:var(--s4);min-width:0;display:grid;gap:var(--s5);align-content:start}
.grid{align-content:start;align-items:start;display:grid;grid-template-columns:repeat(12,1fr);gap:var(--s3)}
.pn{background:var(--panel);border:1px solid var(--line);border-radius:3px;min-width:0}
.pn>header{display:flex;justify-content:space-between;align-items:baseline;padding:6px var(--s3);border-bottom:1px solid var(--line);font:500 11px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-2)}
.pn>header span{font:11px var(--mono);letter-spacing:0;text-transform:none;color:var(--ink-3)}
.c12{grid-column:span 12}.c9{grid-column:span 9}.c8{grid-column:span 8}.c6{grid-column:span 6}.c4{grid-column:span 4}.c3{grid-column:span 3}
.ttl{display:flex;justify-content:space-between;align-items:baseline;gap:var(--s4);flex-wrap:wrap}
h1{font:600 20px/1.2 var(--sans);margin:0;letter-spacing:.01em}
.sub{color:var(--ink-2);font-size:13px;max-width:90ch}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--s3)}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:var(--s3)}
.tile .k{font:500 10px var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3)}
.tile .v{font:500 24px/1.15 var(--mono);margin:var(--s1) 0 var(--s0)}
.tile .l{font:11.5px/1.35 var(--sans);color:var(--ink-2)}
.tile.g .v{color:var(--green)}
.vw{position:relative;aspect-ratio:16/10;background:#0e1318;overflow:hidden}
.vw img{width:100%;height:100%;object-fit:cover;display:block;opacity:.92}
.vw .tl{position:absolute;top:var(--s2);left:var(--s2);display:flex;gap:var(--s1);flex-wrap:wrap}
.vw .tl span{font:11px var(--mono);background:rgba(10,13,16,.82);color:var(--ink-2);padding:2px 7px;border:1px solid var(--line-2);border-radius:2px}
.vw .tl .on{color:var(--amber);border-color:var(--amber)}
.vw .ft{position:absolute;left:var(--s2);bottom:var(--s2);font:11px var(--mono);color:#9aa6b2;background:rgba(10,13,16,.82);padding:2px 7px;border-radius:2px}
.tree{font-size:13px}.tree div{display:grid;grid-template-columns:10px 1fr auto;gap:var(--s2);align-items:center;padding:4px var(--s3);border-bottom:1px solid var(--line)}
.tree i{width:8px;height:8px;border-radius:1px;display:block}.tree b{font:12px var(--mono);font-weight:400;color:var(--ink-2)}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{font:500 10px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);text-align:left;padding:6px var(--s3);border-bottom:1px solid var(--line-2);background:var(--panel-2);white-space:nowrap;position:sticky;top:0}
td{padding:6px var(--s3);border-bottom:1px solid var(--line);vertical-align:top}
tr:hover td{background:var(--panel-2)}
.num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap} th.num{text-align:right}
td.id{font:12px var(--mono);color:var(--ink-3);white-space:nowrap}
.led{font:500 11px var(--mono);letter-spacing:.04em;text-transform:uppercase;white-space:nowrap}.led::before{content:"";display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:6px;background:currentColor}
.l-done,.l-v{color:var(--green)}.l-partial,.l-unverified,.l-marginal,.l-est{color:var(--amber)}.l-open{color:var(--red)}.l-todo{color:var(--ink-3)}.l-todo::before{background:none;box-shadow:inset 0 0 0 1.5px currentColor}
.src{font:11px var(--mono);color:var(--ink-3);display:block;margin-top:2px}
.strip{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;padding:var(--s3)}
.strip div{height:8px;background:var(--line-2)}.strip .d{background:var(--green)}.strip .p{background:var(--amber)}
.strip-l{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;padding:0 var(--s3) var(--s3);font:11px var(--mono);color:var(--ink-3)}
.hbar{display:grid;grid-template-columns:90px 1fr 70px;gap:var(--s3);align-items:center;padding:4px var(--s3);font-size:12.5px}
.hbar i{display:block;height:6px;background:var(--cyan)}.hbar b{font:500 12px var(--mono);text-align:right}
.legend{padding:var(--s2) var(--s3);font:11px var(--mono);color:var(--ink-3);display:flex;gap:var(--s4);flex-wrap:wrap;border-top:1px solid var(--line)}
.scroll{overflow-x:auto}
.theme{font:11px var(--mono);background:none;border:1px solid var(--line-2);color:var(--ink-2);padding:2px 8px;border-radius:2px;cursor:pointer;margin:6px var(--s3)}
@media (max-width:900px){.c9,.c8,.c6,.c4,.c3{grid-column:span 12}.tiles{grid-template-columns:1fr 1fr}}
@media (max-width:760px){
 .bar>div.opt{display:none}.shell{display:block}
 .rail{display:none;border-right:0;border-bottom:1px solid var(--line-2)} #menu:checked ~ .shell .rail{display:block}
 .mbtn{display:block;padding:var(--s2) var(--s4);border-bottom:1px solid var(--line-2);background:var(--panel);font:12px var(--mono)}
 main{padding:var(--s3)} .col-hide{display:none} .strip{grid-template-columns:repeat(10,1fr)}
}
"""
NAVS=[("Aircraft","F1"),("Decision","F2"),("Team","F3"),("Subsystems","F4"),("Build guide","F5"),("Proofs","F6"),("Status","F7"),("BOM","F8"),("Docs","F9")]
def rail(cur):
    return '<h6>Explorer</h6>'+"".join('<a href="#%s"%s>%s<kbd>%s</kbd></a>'%(n.lower().replace(" ","-"),' aria-current="page"' if n==cur else "",n,k) for n,k in NAVS)

def build():
    cols=["#6b7280","#4caf50","#26a69a","#26a69a","#e0a800","#a47c3c","#7a8794","#e8573f","#d6457f","#3b82f6","#e0a800"]
    names=["propulsion","power","wing","cage","fins","avionics","mechanisms","harness","assembly","wiring","landing"]
    tree="".join('<div><i style="background:%s"></i><span>%s</span><b>%s g</b></div>'%(cols[k],n,"%g"%v) for k,(n,v) in enumerate(MASS))
    strip="".join('<div class="%s"></div>'%{"done":"d","partial":"p","todo":""}[s] for n,t,s,d,r in PHASES)
    stripl="".join("<span>%s</span>"%n for n,t,s,d,r in PHASES)
    ph="".join('<tr><td class=id>%s</td><td><b style="font-weight:500">%s</b><span class=src>%s</span></td><td class=col-hide>%s</td><td class="col-hide m">%s</td><td><span class="led l-%s">%s</span></td></tr>'%(n,t,r,d,r,s,STATE[s]) for n,t,s,d,r in PHASES)
    iss="".join('<tr><td class=id>%s</td><td><b style="font-weight:500">%s</b><br>%s<span class=src>%s</span></td><td class=col-hide>%s</td><td><span class="led l-%s">%s</span></td></tr>'%(n,t,d,src,o,s.lower(),s) for n,t,d,o,src,s in ISSUES)
    rows="".join('<tr><td class=id>%s</td><td>%s</td><td class=col-hide>%s</td><td class=col-hide>%s</td><td class=num>%d</td><td class=num>%s</td><td class=num>%s</td><td><span class="led l-%s">%s</span></td><td class=col-hide>%s</td></tr>'%(l,i,g,v,q,money(u),money(q*u),p.lower(),p,o) for l,i,g,v,q,u,p,o,c in BOM)
    gm=max(v for _,v in GROUPS)
    bars="".join('<div class=hbar><span>%s</span><i style="width:%d%%"></i><b>%s</b></div>'%(n,v/gm*100,money(v)) for n,v in GROUPS)
    t=TPL
    for k,v in {"CSS":CSS,"RAIL_A":rail("Aircraft"),"RAIL_S":rail("Status"),"RAIL_B":rail("BOM"),"TREE":tree,"STRIP":strip,"STRIPL":stripl,"PH":ph,"ISS":iss,"ROWS":rows,"BARS":bars}.items(): t=t.replace("{{%s}}"%k,v)
    return t

TPL = r"""<!doctype html>
<html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Concept 3 · Mission control</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{{CSS}}</style></head><body>
<!--
 CONCEPT 3 "Mission control": dense instrument panels (Grafana, Onshape, Joby "data as of" footers).
 Type: IBM Plex Sans Condensed (labels, text) + JetBrains Mono (every number, id, source; tabular figures). Scale 10 / 11 / 12.5 / 14 / 20 / 24.
 Dark = #0a0d10 / panels #10151a / amber #f5a524 / green #3ddc97 / red #ff6b5e / cyan #5bc0eb; light = #e9edf0 / white / darker amber #9a5b00.
 Spacing 2 4 8 12 16 24. Radius 3. Nav: left rail with F-key shortcuts, status bar on top carries the live gate numbers (mass, CG, claims, build time).
 Under 760 px: rail hides behind a Pages bar, status bar keeps three readouts, tables drop owner and group columns.
-->
<input type="checkbox" id="menu" hidden>
<div class="bar"><div class="id">Concept A <small>scaled quad tailsitter, D-182</small></div>
 <div>Mass <b class="m">1,263</b> g <small>gate 1,500</small></div>
 <div class="opt">CG x <b class="m">0.021</b> m <small>0.004 to 0.029</small></div>
 <div class="opt">Claims <b class="m ok">63</b> <small>0 failing</small></div>
 <div class="opt">Built <b class="m">2026-11-16 07:46Z</b></div><div class="sp"></div>
 <div class="opt"><button class="theme" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">dark / light</button></div></div>
<label for="menu" class="mbtn" role="button" tabindex="0">Pages (9) +</label>
<div class="shell"><nav class="rail" aria-label="Pages">{{RAIL_A}}<h6>Tools</h6><a href="#">Search<kbd>/</kbd></a><a href="#">Fasteners<kbd>H</kbd></a></nav>
<main>
<section id="aircraft" class="grid">
 <div class="c12 ttl"><h1>Aircraft</h1><p class="sub">106 flight parts, 141 interfaces. Select a part for its numbers, interfaces and claims.</p></div>
 <div class="pn c3"><header>Parts <span>106</span></header><div class="tree">{{TREE}}</div></div>
 <div class="pn c6"><header>Model <span>assets/concept-a.glb, placeholder render</span></header><div class="vw"><img src="../assets/renders/a-hero-iso.webp" alt="Placeholder for the 3-D viewer: render of concept A"><div class="tl"><span class="on">Aircraft</span><span>Inside &amp; wiring</span><span>Structure</span><span>Exploded</span><span class="on">Cruise</span><span>Hover</span></div><div class="ft">drag rotate · scroll zoom · click part · H fasteners</div></div></div>
 <div class="pn c3"><header>Inspector <span>no part selected</span></header>
  <table><tbody><tr><td>Flight parts</td><td class=num>106</td></tr><tr><td>Declared mass</td><td class=num>1,263 g</td></tr><tr><td>Gate</td><td class=num>1,500 g</td></tr><tr><td>CG x</td><td class=num>0.021 m</td></tr><tr><td>Target</td><td class=num>0.004 to 0.029</td></tr><tr><td>Interfaces</td><td class=num>141</td></tr><tr><td>Claims</td><td class=num>63</td></tr></tbody></table>
  <div class="legend"><span>click a part for numbers</span></div></div>
</section>
<section id="status" class="grid">
 <div class="c12 ttl"><h1>Status</h1><p class="sub">Concept A (D-182), 2026-11-15. Five of ten phases done, one partial, four not started. Done means the round delivered and its decisions are logged; it does not mean verified.</p></div>
 <div class="pn c12"><header>Programme <span>5 done · 1 partial · 4 not started</span></header><div class="strip">{{STRIP}}</div><div class="strip-l">{{STRIPL}}</div>
  <div class="scroll"><table><thead><tr><th>No.</th><th>Phase</th><th class=col-hide>Scope</th><th class=col-hide>Ref</th><th>State</th></tr></thead><tbody>{{PH}}</tbody></table></div></div>
 <div class="pn c12"><header>Open issues <span>5 of 9 shown</span></header><div class="scroll"><table><thead><tr><th>#</th><th>Issue and source</th><th class=col-hide>Owner</th><th>State</th></tr></thead><tbody>{{ISS}}</tbody></table></div>
  <div class="legend"><span>OPEN needs work</span><span>UNVERIFIED analysed, not tested</span><span>MARGINAL little room</span><span>EST estimate</span></div></div>
</section>
<section id="bom" class="grid">
 <div class="c12 ttl"><h1>Bill of materials</h1><p class="sub">41 lines, all bought new, against the $2,000 limit. Prices read 2026-11-14/15. Nothing is bought yet.</p></div>
 <div class="tiles c12"><div class="tile"><div class="k">Total with reserve</div><div class="v">$1,779.47</div><div class="l">spend $1,452.04 + reserve $327.43</div></div><div class="tile g"><div class="k">Margin to $2,000</div><div class="v">$220.53</div><div class="l">+$100.05 if unverified lines run 30 % over</div></div><div class="tile"><div class="k">Goods</div><div class="v">$1,262.50</div><div class="l">+ tax $129.41, ship $55.13 EST, FAA $5</div></div><div class="tile"><div class="k">Order 1, early Dec</div><div class="v">$967.90</div><div class="l">bench kit, 2 motors</div></div></div>
 <div class="pn c4"><header>Spend by group <span>incl. tax</span></header>{{BARS}}</div>
 <div class="pn c8"><header>Lines <span>12 of 41, qp/A/BOM-A.csv</span></header><div class="scroll"><table><thead><tr><th>Line</th><th>Item</th><th class=col-hide>Group</th><th class=col-hide>Vendor</th><th class=num>Qty</th><th class=num>Unit</th><th class=num>Ext</th><th>Price</th><th class=col-hide>Order</th></tr></thead><tbody>{{ROWS}}</tbody></table></div></div>
</section>
</main></div>
<script>if(location.hash==='#light')document.documentElement.dataset.theme='light'</script>
</body></html>
"""
if __name__=="__main__": open("concept-3.html","w",encoding="utf8").write(build())
