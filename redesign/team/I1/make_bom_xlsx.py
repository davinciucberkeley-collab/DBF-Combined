"""Build K09L-BOM.xlsx from BOM.csv: a Summary sheet (inputs, totals, reserve check, by group and order wave),
the BOM sheet with live formulas, and a Read me sheet. Run: python -I redesign/team/I1/make_bom_xlsx.py"""
import csv
import os

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

HERE = os.path.dirname(os.path.abspath(__file__))
import json  # noqa: E402
# R5: UNPRICED lines (price "-") are listed in BOM.csv but are in no total; shipping and duty come from bom_summary.json
rows = [x for x in csv.DictReader(open(os.path.join(HERE, "BOM.csv"), encoding="utf-8"))
        if x["line"] not in ("TOTAL", "") and x["unit_usd"] != "-"]
SUM = json.load(open(os.path.join(HERE, "bom_summary.json"), encoding="utf-8"))
MON = SUM["money"]

FONT = "Arial"


def f(**k):
    return Font(name=FONT, **k)


blue = f(color="0000FF")
bold = f(bold=True)
hdr = f(bold=True, color="FFFFFF")
hfill = PatternFill("solid", fgColor="1F2937")
yfill = PatternFill("solid", fgColor="FFF2CC")
money = "$#,##0.00;($#,##0.00);-"
grey = f(size=9, color="6B7280")

wb = Workbook()

# ---------------- Summary ----------------
s = wb.active
s.title = "Summary"
s["A1"] = "K09-L bill of materials: summary"
s["A1"].font = f(bold=True, size=14)
s["A2"] = ("Source: redesign/team/I1/BOM.csv (procurement engineer I1, prices seen 2026-11-01..09). "
           "Blue = input you can change; black = formula. GATED lines are excluded from every total until their gate opens.")
s["A2"].font = f(italic=True, size=9)
inputs = [
    ("Budget (hard limit)", 2000, "Team lead constraint C1"),
    ("Sales tax rate", 0.1025, "Berkeley/Alameda County rate, CDTFA, effective 2026-10-01"),
    ("Shipping + pack duty, baseline", round(MON["ship_base"] + MON["duty_base"], 2), f"ESTIMATE: {MON['shipments']} paid shipments x $8.57 + duty $20 (bom_summary.json, R5)"),
    ("FAA registration (not taxed)", 5, "FAA small-UAS registration"),
    ("Pessimistic adders", round(MON["ship_pess"] - MON["ship_base"] + MON["duty_pess"] - MON["duty_base"] + 27, 2), "shipping $10.71 vs $8.57 per shipment, duty $45 vs $20, tax measure $7, jig/box $20 (bom_summary.json, R5)"),
    ("Crash reserve needed", 309, "Configuration study: one realistic class-S crash incl. tax"),
]
s["A4"] = "Inputs"
s["A4"].font = bold
for i, (k, v, src) in enumerate(inputs):
    r = 5 + i
    s.cell(r, 1, k).font = f()
    c = s.cell(r, 2, v)
    c.font = blue
    c.fill = yfill
    c.number_format = "0.00%" if k.startswith("Sales") else money
    s.cell(r, 3, src).font = grey

n = len(rows) + 1
B = "BOM"
s["A12"] = "Totals"
s["A12"].font = bold
s["B12"] = "Baseline"
s["C12"] = "Pessimistic"
s["B12"].font = bold
s["C12"].font = bold
tot = [
    ("Goods (included lines)",
     f'=SUMIFS({B}!$O$2:$O${n},{B}!$H$2:$H${n},"Yes")',
     f'=SUMIFS({B}!$P$2:$P${n},{B}!$H$2:$H${n},"Yes")'),
    ("Sales tax", "=B13*$B$6", "=C13*$B$6"),
    ("Shipping", "=$B$7", "=$B$7"),
    ("FAA registration", "=$B$8", "=$B$8"),
    ("Pessimistic adders", "=0", "=$B$9"),
    ("Spend", "=SUM(B13:B17)", "=SUM(C13:C17)"),
    ("Reserve left of budget", "=$B$5-B18", "=$B$5-C18"),
    ("Covers one crash?", '=IF(B19>=$B$10,"YES","NO")', '=IF(C19>=$B$10,"YES","NO")'),
]
for i, (k, b, c) in enumerate(tot):
    r = 13 + i
    strong = k in ("Spend", "Reserve left of budget")
    s.cell(r, 1, k).font = f(bold=strong)
    for col, v in ((2, b), (3, c)):
        x = s.cell(r, col, v)
        x.font = f(bold=strong)
        x.number_format = money
s["A22"] = (f"Check against I1 R5 (bom_summary.json): at order spend ${MON['spend_base']:,.2f} / ${MON['spend_pess']:,.2f}, "
            f"reserve ${SUM['reserve_base']:,.2f} / ${SUM['reserve_pess']:,.2f}; flight-ready (+ X07 + X08) reserve "
            f"${SUM['reserve_base_flight_ready']:,.2f} / ${SUM['reserve_pess_flight_ready']:,.2f}.")
s["A22"].font = grey

groups = sorted(set(x["group"] for x in rows))
s["A24"] = "Included spend by group (incl. tax)"
s["A24"].font = bold
s["B24"] = "Baseline"
s["B24"].font = bold
for i, g in enumerate(groups):
    r = 25 + i
    s.cell(r, 1, g).font = f()
    x = s.cell(r, 2, f'=SUMIFS({B}!$Q$2:$Q${n},{B}!$B$2:$B${n},A{r},{B}!$H$2:$H${n},"Yes")')
    x.number_format = money
    x.font = f()
r0 = 25 + len(groups) + 1
s.cell(r0, 1, "Included spend by order wave (incl. tax)").font = bold
s.cell(r0, 2, "Baseline").font = bold
for i, o in enumerate(["EARLY", "DEC", "LOCAL"]):
    r = r0 + 1 + i
    s.cell(r, 1, o).font = f()
    x = s.cell(r, 2, f'=SUMIFS({B}!$Q$2:$Q${n},{B}!$I$2:$I${n},A{r},{B}!$H$2:$H${n},"Yes")')
    x.number_format = money
    x.font = f()
s.cell(r0 + 5, 1, "EARLY = order ~20 Nov 2026 · DEC = mid-December order · LOCAL = buy locally. See ORDER-PLAN.md.").font = grey
s.column_dimensions["A"].width = 42
s.column_dimensions["B"].width = 16
s.column_dimensions["C"].width = 16

# ---------------- BOM ----------------
w = wb.create_sheet("BOM")
cols = ["Line", "Group", "Part ID", "Item", "Vendor", "Part number", "Link", "Included in totals", "Order wave",
        "Gate", "Qty fitted", "Qty spare", "Qty total", "Unit $ (base)", "Ext $ (base)", "Ext $ (pessimistic)",
        "Ext $ incl. tax (base)", "Unit $ (pessimistic)", "Lead time (days)", "Long lead", "Price status",
        "Price seen", "Note"]
for j, c in enumerate(cols, 1):
    x = w.cell(1, j, c)
    x.font = hdr
    x.fill = hfill
    x.alignment = Alignment(wrap_text=True, vertical="center")
for i, x in enumerate(rows):
    r = i + 2
    o = x["order"]
    gated = "GATED" in o
    wave = o.split(" ")[0]
    gate = o[o.find("GATED") + 6:].strip(" )") if gated else ""
    vals = [x["line"], x["group"], x["part_id"], x["item"], x["vendor"], x["part_number"], x["url"],
            "No" if gated else "Yes", wave, gate, float(x["qty_fitted"] or 0), float(x["qty_spare"] or 0), None,
            float(x["unit_usd"] or 0), None, None, None, float(x["unit_usd_pessimistic"] or 0),
            float(x["lead_time_days"]) if x["lead_time_days"] else None, x["long_lead"], x["price_status"],
            x["price_seen"], x["note"]]
    for j, v in enumerate(vals, 1):
        w.cell(r, j, v).font = f()
    w.cell(r, 13, f"=K{r}+L{r}")
    w.cell(r, 15, f"=M{r}*N{r}")
    w.cell(r, 16, f"=M{r}*R{r}")
    w.cell(r, 17, f"=O{r}*(1+Summary!$B$6)")
    for j in (11, 12, 14, 18):
        w.cell(r, j).font = blue
    for j in (14, 15, 16, 17, 18):
        w.cell(r, j).number_format = money
    if x["url"]:
        w.cell(r, 7).hyperlink = x["url"]
        w.cell(r, 7).value = "link"
        w.cell(r, 7).font = f(color="1F5FC7", underline="single")
    if x["price_status"] == "EST":
        w.cell(r, 21).fill = yfill
widths = [6, 12, 12, 42, 18, 18, 7, 10, 9, 7, 8, 8, 8, 11, 11, 12, 13, 12, 9, 8, 9, 11, 60]
for j, wd in enumerate(widths, 1):
    w.column_dimensions[get_column_letter(j)].width = wd
w.freeze_panes = "E2"
t = Table(displayName="BOMTable", ref=f"A1:W{n}")
t.tableStyleInfo = TableStyleInfo(name="TableStyleLight9", showRowStripes=True)
w.add_table(t)
w.cell(1, 21).comment = Comment("CHK = checked on the vendor page; CARRY = from the configuration study; "
                                "EST = estimate (yellow): confirm before ordering.", "I1")

# ---------------- Read me ----------------
g = wb.create_sheet("Read me")
lines = [
    "How to use this workbook",
    "Summary: totals, reserve and the crash-budget check. Change the blue inputs (tax, shipping, budget) and everything recalculates.",
    "BOM: one row per line item. Change quantities or unit prices (blue) to update every total. 'Included in totals' = No for gated lines.",
    "Price status: CHK checked on the vendor page, CARRY from the configuration study, EST estimate (yellow): confirm price and stock on order day.",
    "Order plan, gates and vendor grouping: redesign/team/I1/ORDER-PLAN.md. Rebuild from source: python -I redesign/team/I1/make_bom_xlsx.py.",
]
for i, line in enumerate(lines):
    g.cell(i + 1, 1, line).font = bold if i == 0 else f()
g.column_dimensions["A"].width = 140

wb.calculation.fullCalcOnLoad = True  # formulas have no cached values; Excel computes them on open
out = os.path.join(HERE, "K09L-BOM.xlsx")
wb.save(out)
print("saved", out, len(rows), "lines")
