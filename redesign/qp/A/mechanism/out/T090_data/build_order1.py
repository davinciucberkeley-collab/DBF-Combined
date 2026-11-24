"""T-090: rebuild ORDER-1.csv from BOM-A.csv and reconcile with bom_a.py.  Run: python -I build_order1.py  (writes ../../../ORDER-1.csv)
Category: cost accounting (not an engineering analysis)."""
import csv, os, importlib.util
A = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
spec = importlib.util.spec_from_file_location("bom_a", os.path.join(A, "bom_a.py")); B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
WHY = {
 "P01": "TP-1 (1 motor on the stand), TP-2 (4-motor limiter run); stock risk: RMRC BACKORDER (availability Nov 2026, read 2026-11-22), no spare (AM-019)",
 "P02": "TP-1 (MR + MRP on the stand), TP-2 (4 props); in stock, no spare (D-183)",
 "P04": "TP-2 needs 4 ESC channels on the stand; single-source 4-in-1; bidirectional-DShot rpm check (UNVERIFIED) is a TP-1 option",
 "W01": "TP-1 fresh-pack and 14.9 V sweeps, TP-2 voltage cap; 2 packs; order only after the CAD tray fit (TEST-PLAN-O4B T-082 note)",
 "W02": "charges / part-discharges the packs to 14.9 V resting for TP-1 and TP-2",
 "W03": "LiPo safety for the 2 packs before first charge",
 "W04": "LiPo storage before the first charge",
 "W05": "14 AWG leads, XT60, heat-shrink: stand power wiring for TP-1 and TP-2",
 "W06": "motor-stand / ESC hardware (unverified EST, local)",
 "W07": "phase-lead extensions: X2216 stock leads are only 100 mm, the 4-motor stand needs the extensions",
 "W10": "TP-2 pass line names XT90 (90 A = 1.25 x 72 A); the 72 A limiter run needs it",
 "V01": "TX to command throttle and trigger the failsafe on the FC in TP-2 (concept-neutral)",
 "V02": "RX paired with V01 for TP-2 (concept-neutral)",
 "V03": "TP-2 runs on the real H743-Wing (Lua cap, 72 A limiter, current sensor range read before the order)",
 "V04": "stock risk (Foxeer backordered); not needed by TP-1/TP-2; ships in the same RMRC group",
 "G01": "TP-1 bus current and voltage logging",
 "G02": "TP-1 thrust cell + HX711, scale, IR thermometer, caliper (Amazon lines, EST)",
 "G03": "TP-1 / TP-2 thrust stand (wood and hardware, EST)",
 "B03": "TP-1 K-type probes for the H-1 motor-base temperature (EST; the 1 kgf cell part is the yaw rig, not needed before 15 Dec)",
 "T9": "TP-1 HX711 logger to the laptop",
 "R03": "PETG for the stand motor mount prints (TP-1 base temperature is on a PETG base); Jacobs prints before 18 Dec",
}
rows = {r["id"]: r for r in B.rows}
o1 = [i for i in WHY]
out = []
for n, i in enumerate(o1, 1):
    r = rows[i]
    out.append([f"O1-{n:02d}", i, r["ship_group"], r["item"], int(r["qty"]), f"{r['u']:.2f}", r["flag"], r["status"], r["date_checked"], WHY[i], r["source_url"]])
goods = sum(float(o[4])*float(o[5]) for o in out)
groups = {o[2] for o in out}
ship = sum(B.SHIP[g] for g in groups)
tax = goods*B.TAX; o1tot = goods+tax+ship
t = B.totals(); main = t["total"]-o1tot
main_goods = t["goods"]-goods
chk_goods = abs(main_goods*(1+B.TAX) + (t["ship"]-ship) + B.FAA + t["reserve"] - main) < 1e-6
with open(os.path.join(A, "ORDER-1.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["order_id","bom_id","vendor","item","qty","unit_usd","flag","status","date_checked","why","url"])
    w.writerows(out)
    w.writerow(["TOTAL","","","Goods (qty x unit)","",f"{goods:.2f}","","","","",""])
    w.writerow(["TOTAL","","","Tax 10.25 % on goods","",f"{tax:.2f}","","","","",""])
    w.writerow(["TOTAL","","",f"Shipping EST, bom_a.py ship groups {sorted(groups)}","",f"{ship:.2f}","EST","","","RMRC / Amazon / Local are $0 in bom_a.py (RMRC rates not readable); RDQ $10.71 EST",""])
    w.writerow(["TOTAL","","","ORDER 1 TOTAL","",f"{o1tot:.2f}","EST","","","Plan, nothing bought (history in mechanism/out/T090_report.md)",""])
print(f"lines {len(out)}  goods {goods:.2f}  tax {tax:.2f}  ship {ship:.2f}  Order1 {o1tot:.2f}")
print(f"BOM total {t['total']:.2f}  remaining main order {main:.2f}  (goods {main_goods:.2f}; ship {t['ship']-ship:.2f}; FAA {B.FAA:.2f}; reserve {t['reserve']:.2f})")
print(f"Order1 + main = {o1tot+main:.2f}  reconcile {'PASS' if chk_goods and abs(o1tot+main-t['total'])<0.005 else 'FAIL'}")
unv = [o[1] for o in out if o[7]=="unverified"]; print("unverified lines in Order 1:", unv, f"{sum(float(o[4])*float(o[5]) for o in out if o[7]=='unverified'):.2f}")
not_in = [i for i in rows if i not in WHY]; print("deferred to main:", not_in)
