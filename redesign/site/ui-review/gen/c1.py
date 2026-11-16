from data import *

CSS = r"""
:root{
  /* palette tokens, light = paper */
  --paper:#f2eee4; --sheet:#faf8f2; --ink:#1c2430; --ink-2:#4a5463; --ink-3:#7a8190;
  --rule:#c9c3b3; --rule-strong:#1c2430; --rev:#b4420f; --dim:#255f85; --ok:#2f6b4f; --warn:#8a5a00;
  /* spacing scale (px): 4 8 12 16 24 32 48 80 */
  --s1:4px;--s2:8px;--s3:12px;--s4:16px;--s5:24px;--s6:32px;--s7:48px;--s8:80px;
  --serif:"Newsreader",Georgia,serif; --mono:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
  --paper:#0c1a2b; --sheet:#0f2036; --ink:#dbe7f3; --ink-2:#9bb2c8; --ink-3:#6f879f;
  --rule:#27425e; --rule-strong:#9bb2c8; --rev:#ff9a5c; --dim:#6cc4f0; --ok:#7fd4a8; --warn:#e8bd5c;}}
:root[data-theme=dark]{
  --paper:#0c1a2b; --sheet:#0f2036; --ink:#dbe7f3; --ink-2:#9bb2c8; --ink-3:#6f879f;
  --rule:#27425e; --rule-strong:#9bb2c8; --rev:#ff9a5c; --dim:#6cc4f0; --ok:#7fd4a8; --warn:#e8bd5c;}
*{box-sizing:border-box}
html{background:var(--paper);color:var(--ink);font:400 17px/1.55 var(--serif);-webkit-text-size-adjust:100%}
body{margin:0;min-height:100vh}
a{color:inherit;text-decoration-color:var(--rev);text-underline-offset:3px}
:focus-visible{outline:2px solid var(--rev);outline-offset:2px}
.mono,.tb dd,.sheetnav,th,.n,.state,.cap,.eyebrow,.legend{font-family:var(--mono);font-feature-settings:"zero","tnum"}
.wrap{max-width:1180px;margin:0 auto;padding:0 var(--s5)}
/* title block */
.tb{display:grid;grid-template-columns:2.2fr 1fr 1fr 1fr 1fr;border:1.5px solid var(--rule-strong);margin:var(--s5) 0 0;background:var(--sheet)}
.tb>div{padding:var(--s2) var(--s3);border-left:1px solid var(--rule-strong)} .tb>div:first-child{border-left:0}
.tb dt{font:500 10px/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--ink-3);margin:0 0 var(--s1)}
.tb dd{margin:0;font-size:13px;line-height:1.35}
.tb .proj dd{font:500 19px/1.2 var(--serif)}
.sheetnav{display:flex;gap:0;border:1.5px solid var(--rule-strong);border-top:0;font-size:12px;background:var(--sheet);overflow:hidden}
.sheetnav a{flex:1;padding:var(--s2) var(--s3);text-decoration:none;border-left:1px solid var(--rule);white-space:nowrap}
.sheetnav a:first-child{border-left:0}
.sheetnav a b{color:var(--ink-3);font-weight:400;margin-right:var(--s2)}
.sheetnav a[aria-current]{background:var(--ink);color:var(--paper)} .sheetnav a[aria-current] b{color:var(--paper)}
.menu{display:none}
.theme{font:12px var(--mono);background:none;border:1px solid var(--rule-strong);color:var(--ink);padding:2px 8px;cursor:pointer}
/* sheets */
.page{padding:var(--s7) 0 var(--s8);border-bottom:1px solid var(--rule)}
.pagemark{font:11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 var(--s5);display:flex;justify-content:space-between}
h1{font:500 44px/1.05 var(--serif);letter-spacing:-.01em;margin:0 0 var(--s3)}
h2{font:500 24px/1.2 var(--serif);margin:var(--s7) 0 var(--s3);display:flex;gap:var(--s3);align-items:baseline}
h2 .n{font-size:12px;color:var(--rev)}
.lede{max-width:62ch;color:var(--ink-2);margin:0}
.eyebrow{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:0 0 var(--s2)}
/* figure */
.sheetgrid{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:var(--s6);margin-top:var(--s6)}
figure{margin:0}
.frame{position:relative;border:1px solid var(--rule-strong);background:var(--sheet);aspect-ratio:16/10;overflow:hidden}
.frame img{width:100%;height:100%;object-fit:cover;display:block;filter:saturate(.7)}
:root[data-theme=dark] .frame img{filter:saturate(.6) brightness(.85)}
.frame::before,.frame::after{content:"";position:absolute;width:14px;height:14px;border:2px solid var(--rev)}
.frame::before{top:8px;left:8px;border-right:0;border-bottom:0}.frame::after{right:8px;bottom:8px;border-left:0;border-top:0}
.hint{position:absolute;left:var(--s3);bottom:var(--s3);font:11px var(--mono);background:var(--sheet);border:1px solid var(--rule);padding:2px 8px;color:var(--ink-2)}
.modes{display:flex;gap:var(--s4);font:12px var(--mono);margin:0 0 var(--s2);flex-wrap:wrap}
.modes span{color:var(--ink-3)} .modes .on{color:var(--ink);border-bottom:2px solid var(--rev)}
.cap{font-size:12px;color:var(--ink-2);margin-top:var(--s2)}
.cap b{color:var(--ink)}
.notes{border-top:1.5px solid var(--rule-strong);font-size:14px}
.notes dl{margin:0}
.notes .row{display:flex;justify-content:space-between;gap:var(--s3);padding:var(--s2) 0;border-bottom:1px solid var(--rule)}
.notes dt{color:var(--ink-2)} .notes dd{margin:0;font:500 14px var(--mono);text-align:right}
.notes dd small{display:block;font-weight:400;color:var(--ink-3);font-size:11px}
.notes h3{font:500 11px var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:var(--s5) 0 var(--s2)}
/* tables */
table{width:100%;border-collapse:collapse;font-size:14px}
th{font-size:10.5px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;text-align:left;color:var(--ink-3);border-bottom:1.5px solid var(--rule-strong);padding:var(--s2) var(--s3) var(--s2) 0;white-space:nowrap}
td{padding:var(--s3) var(--s3) var(--s3) 0;border-bottom:1px solid var(--rule);vertical-align:top}
.num{text-align:right;font-family:var(--mono);font-size:13px;white-space:nowrap} th.num{text-align:right}
td.id{font:12px var(--mono);color:var(--ink-3);white-space:nowrap}
.bar{display:block;height:3px;background:var(--rule);margin-top:5px}.bar i{display:block;height:3px;background:var(--dim)}
.state{font-size:11.5px;white-space:nowrap} .state::before{content:"";display:inline-block;width:8px;height:8px;border:1.5px solid currentColor;margin-right:7px;vertical-align:-1px}
.s-done{color:var(--ok)} .s-done::before{background:currentColor}
.s-partial{color:var(--warn)} .s-partial::before{background:linear-gradient(90deg,currentColor 50%,transparent 50%)}
.s-todo{color:var(--ink-3)}
.s-open{color:var(--rev)} .s-open::before{background:currentColor}
.s-unverified{color:var(--warn)}.s-marginal{color:var(--warn)}
.legend{font-size:11.5px;color:var(--ink-2);border:1px solid var(--rule);padding:var(--s2) var(--s3);margin:var(--s4) 0;display:flex;gap:var(--s5);flex-wrap:wrap}
.src{font:11.5px var(--mono);color:var(--ink-3)}
/* figures row (BOM) */
.figs{display:grid;grid-template-columns:repeat(4,1fr);border-top:1.5px solid var(--rule-strong);border-bottom:1px solid var(--rule);margin:var(--s6) 0}
.figs>div{padding:var(--s4) var(--s4) var(--s4) 0;border-left:1px solid var(--rule);padding-left:var(--s4)} .figs>div:first-child{border-left:0;padding-left:0}
.figs .k{font:10.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.figs .v{font:500 34px/1.1 var(--serif);margin:var(--s1) 0}
.figs .l{font-size:12.5px;color:var(--ink-2);line-height:1.4}
.hbar{display:grid;grid-template-columns:110px 1fr 80px;align-items:center;gap:var(--s3);font-size:14px;padding:5px 0}
.hbar i{display:block;height:8px;background:repeating-linear-gradient(90deg,var(--dim) 0 3px,transparent 3px 5px)}
.hbar b{font:13px var(--mono);text-align:right;font-weight:400}
.scroll{overflow-x:auto}
footer{padding:var(--s6) 0;font:12px var(--mono);color:var(--ink-3);display:flex;justify-content:space-between;gap:var(--s4);flex-wrap:wrap}
@media (max-width:760px){
  html{font-size:16px}.wrap{padding:0 var(--s4)}
  .tb{grid-template-columns:1fr 1fr}.tb .proj{grid-column:1/-1}.tb>div{border-top:1px solid var(--rule-strong)}.tb>div:nth-child(2){border-left:0}
  .tb>div:nth-child(2),.tb>div:nth-child(3),.tb>div:nth-child(4),.tb>div:nth-child(5){border-top:1px solid var(--rule-strong)}
  .tb>div:nth-child(3){border-left:0}
  .sheetnav{display:none}
  .menu{display:block;border:1.5px solid var(--rule-strong);border-top:0;background:var(--sheet);font:13px var(--mono)}
  .menu summary{padding:var(--s3);cursor:pointer;list-style:none;display:flex;justify-content:space-between}
  .menu a{display:block;padding:var(--s3);border-top:1px solid var(--rule);text-decoration:none} .menu a b{color:var(--ink-3);margin-right:var(--s3);font-weight:400}
  h1{font-size:32px}.sheetgrid{grid-template-columns:1fr}
  .figs{grid-template-columns:1fr 1fr}.figs>div:nth-child(3){border-left:0;padding-left:0}.figs>div{border-top:1px solid var(--rule)}
  .hbar{grid-template-columns:84px 1fr 64px}
  .col-hide{display:none}
}
"""

def sheetnav(cur):
    items=["Aircraft","Decision","Team","Subsystems","Build guide","Proofs","Status","BOM","Docs"]
    a="".join('<a href="#%s"%s><b>%d</b>%s</a>'%(i.lower().replace(" ","-"),' aria-current="page"' if i==cur else "",k+1,i) for k,i in enumerate(items))
    return a

def build():
    mx=max(v for _,v in MASS)
    mass="".join('<tr><td>%s<span class="bar"><i style="width:%d%%"></i></span></td><td class="num">%s g</td></tr>'%(n,v/mx*100,("%g"%v)) for n,v in MASS)
    phases="".join('<tr><td class="id">%s</td><td><b style="font-weight:500">%s</b><br><span style="color:var(--ink-2)">%s</span></td><td class="col-hide src">%s</td><td><span class="state s-%s">%s</span></td></tr>'%(n,t,d,r,s,STATE[s]) for n,t,s,d,r in PHASES)
    iss="".join('<tr><td class="id">%s</td><td><b style="font-weight:500">%s.</b> %s<div class="src" style="margin-top:4px">%s</div></td><td class="col-hide">%s</td><td><span class="state s-%s">%s</span></td></tr>'%(n,t,d,src,o,s.lower(),s) for n,t,d,o,src,s in ISSUES)
    rows="".join('<tr><td class="id">%s</td><td>%s</td><td class="col-hide">%s</td><td class="col-hide">%s</td><td class="num">%d</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>'%(l,i,g,v,q,money(u),money(q*u),p) for l,i,g,v,q,u,p,o,c in BOM)
    gm=max(v for _,v in GROUPS)
    bars="".join('<div class="hbar"><span>%s</span><i style="width:%d%%"></i><b>%s</b></div>'%(n,v/gm*100,money(v)) for n,v in GROUPS)
    return TPL.replace("{{CSS}}",CSS).replace("{{NAV}}",sheetnav("Aircraft")).replace("{{NAV_S}}",sheetnav("Status")).replace("{{NAV_B}}",sheetnav("BOM")).replace("{{MASS}}",mass).replace("{{PHASES}}",phases).replace("{{ISSUES}}",iss).replace("{{ROWS}}",rows).replace("{{BARS}}",bars)

TPL = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Concept 1 · Drawing sheet</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<style>{{CSS}}</style></head><body>
<!--
 CONCEPT 1 "Drawing sheet" (engineering notebook / technical drawing)
 Type: Newsreader (text and headings) + IBM Plex Mono (data, labels). Mono is used only for identifiers, numbers and labels.
 Light = paper #f2eee4 / ink #1c2430 / revision orange #b4420f; dark = blueprint #0c1a2b / #dbe7f3 / #ff9a5c.
 Spacing 4 8 12 16 24 32 48 80. Radius 0 everywhere. Nav: title block + numbered sheet strip (menu button under 760 px).
-->
<div class="wrap">
 <dl class="tb">
  <div class="proj"><dt>Project</dt><dd>Concept A, scaled quad tailsitter</dd></div>
  <div><dt>Decision</dt><dd>D-182 (J6 board)</dd></div>
  <div><dt>Revision</dt><dd>D-199</dd></div>
  <div><dt>Data built</dt><dd>2026-11-16 07:46Z</dd></div>
  <div><dt>Display</dt><dd><button class="theme" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">light / dark</button></dd></div>
 </dl>
 <nav class="sheetnav" aria-label="Sheets">{{NAV}}</nav>
 <details class="menu"><summary><span>1 Aircraft</span><span>Sheets +</span></summary>{{NAV}}</details>

 <main>
 <section class="page" id="aircraft">
  <p class="pagemark"><span>Sheet 1 of 9</span><span>Aircraft, 3-D model</span></p>
  <h1>Aircraft</h1>
  <p class="lede">106 flight parts, 1,263 g declared, 141 interfaces. Select a part for its numbers, interfaces and claims; double-click to focus.</p>
  <div class="sheetgrid">
   <figure>
    <div class="modes"><span class="on">Aircraft</span><span>Inside &amp; wiring</span><span>Structure</span><span>Exploded</span><span>|</span><span class="on">Cruise</span><span>Hover</span></div>
    <div class="frame"><img src="../assets/renders/a-hero-iso.webp" alt="Placeholder for the 3-D viewer: render of concept A"><span class="hint">drag rotate / scroll zoom / click part / H fasteners</span></div>
    <figcaption class="cap"><b>Fig. 1</b> Concept A as modelled. Viewer area (placeholder: render a-hero-iso). Source: assets/concept-a.glb, built 2026-11-16.</figcaption>
   </figure>
   <aside class="notes" aria-label="Key numbers">
    <h3 style="margin-top:var(--s3)">Key numbers</h3>
    <dl>
     <div class="row"><dt>Declared mass</dt><dd>1,263 g<small>of 1,500 g gate</small></dd></div>
     <div class="row"><dt>CG x</dt><dd>0.021 m<small>target 0.004 to 0.029</small></dd></div>
     <div class="row"><dt>Claims</dt><dd>63<small>0 failing</small></dd></div>
     <div class="row"><dt>Interfaces</dt><dd>141</dd></div>
    </dl>
    <h3>Mass by subsystem</h3>
    <table><tbody>{{MASS}}</tbody></table>
   </aside>
  </div>
 </section>

 <section class="page" id="status">
  <nav class="sheetnav" aria-label="Sheets" style="margin-bottom:var(--s6);border-top:1.5px solid var(--rule-strong)">{{NAV_S}}</nav>
  <p class="pagemark"><span>Sheet 7 of 9</span><span>Status, concept A (D-182), 2026-11-15</span></p>
  <h1>Status</h1>
  <p class="lede">Five of ten phases done, one partial, four not started. Nothing bought, built or flown. Done means the round delivered and its decisions are logged in CHANGE-LOG; it does not mean verified. Claims: strict build, 0 failing.</p>
  <h2><span class="n">7.1</span>Programme</h2>
  <div class="scroll"><table><thead><tr><th>No.</th><th>Phase</th><th class="col-hide">Reference</th><th>State</th></tr></thead><tbody>{{PHASES}}</tbody></table></div>
  <h2><span class="n">7.2</span>Open issues</h2>
  <div class="legend"><span>Open: needs work</span><span>Unverified: analysed, not tested</span><span>Marginal: passes with little room</span><span>Est: estimate</span></div>
  <div class="scroll"><table><thead><tr><th>No.</th><th>Issue and source</th><th class="col-hide">Owner</th><th>State</th></tr></thead><tbody>{{ISSUES}}</tbody></table></div>
 </section>

 <section class="page" id="bom">
  <nav class="sheetnav" aria-label="Sheets" style="margin-bottom:var(--s6);border-top:1.5px solid var(--rule-strong)">{{NAV_B}}</nav>
  <p class="pagemark"><span>Sheet 8 of 9</span><span>Bill of materials, prices read 2026-11-14/15</span></p>
  <h1>Bill of materials</h1>
  <p class="lede">41 lines, all bought new, against the $2,000 limit. V = price read on the vendor page, EST = estimate. Totals add tax 10.25 %, shipping (estimate) and the FAA fee, then a crash reserve. Nothing is bought yet.</p>
  <div class="figs">
   <div><div class="k">Total, with reserve</div><div class="v">$1,779.47</div><div class="l">spend $1,452.04 + reserve $327.43</div></div>
   <div><div class="k">Margin to $2,000</div><div class="v">$220.53</div><div class="l">+$100.05 if unverified lines run 30 % over</div></div>
   <div><div class="k">Goods</div><div class="v">$1,262.50</div><div class="l">+ tax $129.41, shipping $55.13 EST, FAA $5</div></div>
   <div><div class="k">Order 1, early Dec</div><div class="v">$967.90</div><div class="l">bench kit, 2 motors (ORDER-1.csv)</div></div>
  </div>
  <h2><span class="n">8.1</span>Where the money goes, incl. tax</h2>
  <div style="max-width:640px">{{BARS}}</div>
  <h2><span class="n">8.2</span>Lines</h2>
  <div class="scroll"><table><thead><tr><th>Line</th><th>Item</th><th class="col-hide">Group</th><th class="col-hide">Vendor</th><th class="num">Qty</th><th class="num">Unit</th><th class="num">Ext</th><th class="num">Price</th></tr></thead><tbody>{{ROWS}}</tbody></table></div>
  <p class="src" style="margin-top:var(--s3)">12 of 41 lines shown. Source: qp/A/BOM-A.csv, totals from bom_a.py.</p>
 </section>
 </main>
 <footer><span>Concept A, redesign/ on GitHub</span><span>Every number on this page comes from a file in redesign/.</span></footer>
</div>
<script>if(location.hash==='#dark')document.documentElement.dataset.theme='dark'</script>
</body></html>
"""

if __name__=="__main__":
    open("concept-1.html","w",encoding="utf8").write(build())
