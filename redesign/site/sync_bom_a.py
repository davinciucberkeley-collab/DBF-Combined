"""Rebuild the Explorer BOM tab (#bom in app.html) from concept A's parts list.
Sources: redesign/qp/A/BOM-A.csv (lines), redesign/qp/A/bom_a.py (totals, caps, G7), redesign/qp/A/ORDER-1.csv (bench-kit order).
Run, then make_index.py:  python -I redesign/site/sync_bom_a.py && python -I redesign/site/make_index.py
The filter script in app.html reads data-group / data-wave on the rows and the ids bom-q, bom-g, bom-w, bom-count."""
import csv, html, importlib.util, io, os, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "..", "qp", "A")
APP = os.path.join(HERE, "app.html")
GH = "https://github.com/davinciucberkeley-collab/DBF-Combined/blob/redesign/v1/redesign/qp/A/"
esc = html.escape

spec = importlib.util.spec_from_file_location("bom_a", os.path.join(A, "bom_a.py"))
bom = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(bom)
t, t30 = bom.totals(), bom.totals(0.30)

rows = list(csv.DictReader(open(os.path.join(A, "BOM-A.csv"), encoding="utf-8")))
o1_rows = list(csv.DictReader(open(os.path.join(A, "ORDER-1.csv"), encoding="utf-8")))
o1 = {r["bom_id"] for r in o1_rows if r["order_id"] != "TOTAL"}
o1_total = next(float(r["unit_usd"]) for r in o1_rows if r["order_id"] == "TOTAL" and r["item"].startswith("ORDER 1 TOTAL, 2"))
o1_total5 = next(float(r["unit_usd"]) for r in o1_rows if r["order_id"] == "TOTAL" and r["item"].startswith("ORDER 1 TOTAL, 5"))
SERVOS = 46.27   # review/QP-4/BOARD.md line 9 / D-J6-5: M01 x 3 into Order 1, not yet in ORDER-1.csv
FLAG = {"V": ("CHECKED", "V"), "U": ("UNVERIFIED", "U"), "EST": ("UNVERIFIED", "EST")}
subs = ["propulsion", "power", "avionics", "mechanisms", "airframe", "ground_test"]
sub_cost = {s: bom.sub_cost(s) for s in subs}
top = max(sub_cost.values())

trs = []
for r in rows:
    q, u = float(r["qty"]), float(r["unit_usd"])
    wave = "ORDER1" if r["id"] in o1 else "MAIN"
    st, lab = FLAG.get(r["flag"], ("UNVERIFIED", r["flag"]))
    item = esc(r["item"])
    if len(item) > 140:
        item = item[:137].rsplit(" ", 1)[0] + "…"
    vend = esc(r["ship_group"])
    if r["source_url"].startswith("http"):
        vend = f'<a class="ds-link" href="{esc(r["source_url"], quote=True)}" target="_blank" rel="noopener">{vend}</a>'
    spare = f'<small class="pid">{int(float(r["spares"]))} spare</small>' if float(r["spares"]) else ""
    trs.append(f'<tr data-group="{r["subsystem"]}" data-wave="{wave}"><td class="id">{r["id"]}</td><td>{item}{spare}</td>'
               f'<td class="fam">{r["subsystem"].replace("_", " ")}</td><td>{vend}</td><td class="num">{q:g}</td><td class="num">${u:,.2f}</td>'
               f'<td class="num">${q*u:,.2f}</td><td><span class="ds-badge" data-status="{st}">{lab}</span></td>'
               f'<td class="fam">{"Order 1" if wave == "ORDER1" else "main"}</td><td class="num">{esc(r["date_checked"])}</td></tr>')

bars = "".join(f'<div class="bom-bar"><span>{s.replace("_", " ")}</span><i style="--v:{100*sub_cost[s]/top:.0f}%"></i><b>${sub_cost[s]:,.2f}</b></div>' for s in sorted(subs, key=lambda s: -sub_cost[s]))
gopts = "".join(f'<option value="{s}">{s.replace("_", " ")}</option>' for s in subs)

section = f'''<section class="c">
    <header><span class="secno">Concept A (D-182) · prices read 2026-11-14/15</span>
      <h1 class="ds-display">Bill of materials</h1>
      <p class="summary">${t["total"]:,.2f} including the crash reserve, against the $2,000 limit: ${t["margin"]:,.2f} margin.</p>
      <p class="use">{len(rows)} lines, all bought new, including the charger, radio, test gear and spares (nothing is owned; Jacobs Hall tools are covered by the Makers Pass). Totals add tax 10.25 %, shipping per vendor (estimate) and the FAA fee, then a crash reserve. In the Price column, V = read on the vendor page, U = unverified, EST = estimate: confirm price and stock on order day (see the <a class="ds-link" href="#status-key">status key</a>). Nothing is bought yet; Order 1 (the bench kit) goes out in early December.</p>
      <div class="ds-row"><a class="ds-btn primary" href="{GH}BOM-A.csv" target="_blank" rel="noopener">BOM-A.csv on GitHub</a><a class="ds-btn" href="{GH}ORDER-1.csv" target="_blank" rel="noopener">Order 1 (bench kit)</a><a class="ds-btn" href="{GH}bom_a.py" target="_blank" rel="noopener">bom_a.py (totals)</a></div>
    </header>
    <div class="ds-metrics">
      <div class="ds-metric"><span class="k">Total incl. crash reserve</span><span class="v">${t["total"]:,.2f}</span><span class="lim">spend ${t["spend"]:,.2f} + reserve ${t["reserve"]:,.2f}</span></div>
      <div class="ds-metric" data-status="CHECKED"><span class="k">Margin to $2,000</span><span class="v">${t["margin"]:,.2f}</span><span class="lim">+${t30["margin"]:,.2f} if unverified lines run 30 % over · G7 {"PASS" if t30["margin"] >= 100 and t["total"] <= 1800 else "FAIL"}</span></div>
      <div class="ds-metric"><span class="k">Goods</span><span class="v">${t["goods"]:,.2f}</span><span class="lim">+ tax ${t["tax"]:,.2f} + shipping ${t["ship"]:,.2f} EST + FAA $5</span></div>
      <div class="ds-metric"><span class="k">Order 1, early Dec</span><span class="v">${o1_total:,.2f}</span><span class="lim">bench kit, 2 motors (ORDER-1.csv)</span></div>
    </div>
    <p class="ds-note">Order 1 notes: 3 ES3054HV servos (${SERVOS:,.2f}) are recommended on top by the QP-4 board (D-J6-5); if all 5 motors are bought (no T-Motor stock answer by 4 Dec), Order 1 is ${o1_total5:,.2f} before servos.</p>
    <h2 class="ds-h1" id="bom-money">Where the money goes (incl. tax)</h2>
    <div class="bom-bars">{bars}</div>
    <div class="filters"><input type="search" id="bom-q" placeholder="Search item, line id, vendor" aria-label="Search BOM"><select id="bom-g" aria-label="Group"><option value="">All groups</option>{gopts}</select><select id="bom-w" aria-label="Order"><option value="">All orders</option><option value="ORDER1">Order 1 (early Dec)</option><option value="MAIN">Main order</option></select><span class="count" id="bom-count"></span></div>
    <div class="scroll wide"><table class="ds-table" id="bom-table"><thead><tr><th>Line</th><th>Item</th><th>Group</th><th>Vendor</th><th class="num">Qty</th><th class="num">Unit</th><th class="num">Ext</th><th>Price <a class="ds-link" href="#status-key" title="V, U and EST: see the status key">key</a></th><th>Order</th><th class="num">Checked</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>
    <span class="ds-source">qp/A/BOM-A.csv · ORDER-1.csv · bom_a.py (tax, shipping, crash reserve, G7: total ≤ $1,800 and ≥ $100 margin at +30 %) · regenerated by site/sync_bom_a.py. The K09-L BOM (team/I1/BOM.csv) is kept as the record.</span>
  </section>'''

s = open(APP, encoding="utf-8").read()
a = s.index('<section class="view" id="bom" hidden>')
i = s.index('<section class="c">', a)
j = s.index('</section>', s.index('<span class="ds-source">', i)) + len('</section>')
s = s[:i] + section + s[j:]
open(APP, "w", encoding="utf-8").write(s)
print(f"BOM tab: {len(rows)} lines, total ${t['total']:,.2f}, margin ${t['margin']:,.2f}, +30 % margin ${t30['margin']:,.2f}, Order 1 ${o1_total:,.2f}")
