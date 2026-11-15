"""Totals ORDER-LIST.csv. python -I order_total.py  (stdlib; reads ORDER-LIST.csv beside it)."""
import csv, os
TAX = 0.1025                      # COST.md basis
here = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(here, "ORDER-LIST.csv"), encoding="utf-8")))
g = {}
for r in rows:
    g[r["group"]] = g.get(r["group"], 0) + int(r["qty"]) * float(r["unit_usd"])
for k, v in g.items():
    print(f"{k:13s} goods {v:8.2f}  +tax {v*(1+TAX):8.2f}")
fl, bo = g["flight-stock"] * (1 + TAX), g["bench-only"] * (1 + TAX)
# shipping: T-Motor 10.71 (flight), RMRC 15.00 (one shared order: counted against bench-only because flight
# stock would otherwise ship with the main order), SparkFun 8.00 EST, Amazon 10.71 EST
ship_bench = 15.00 + 8.00 + 10.71
ship_flight = 10.71
print(f"bench-only total incl ship (RMRC+SparkFun+Amazon) {bo + ship_bench:8.2f}")
print(f"flight-stock total incl T-Motor ship                {fl + ship_flight:8.2f}")
print(f"whole kit                                            {bo + ship_bench + fl + ship_flight:8.2f}")
# board estimate: R1 pair 31.98 + stand parts, 32-60
lean = [r for r in rows if r["id"] in ("O5", "O6")]
lg = sum(float(r["unit_usd"]) * int(r["qty"]) for r in lean)
print(f"R1-only (O5+O6) goods {lg:.2f}, +tax {lg*(1+TAX):.2f}, +RMRC ship {lg*(1+TAX)+15:.2f}")
# lines the COST.md floor already carries: F11a WM150 35.31 and F11b load cell+HX711 etc 50.95
cov = (12.99 + 12.95 + 4.95 + 8.00) * (1 + TAX)
print(f"bench-only lines already inside COST floor F11a/F11b (watt meter, cell, HX711, Nano): {cov:.2f}")
print(f"bench-only net of those                                {bo + ship_bench - cov:8.2f}")
