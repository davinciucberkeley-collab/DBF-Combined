"""Concept A single BOM.  Reproduce: python -I bom_a.py  (stdlib; reads BOM-T081.csv beside it; prints markdown; writes nothing)
Basis: tax 10.25 % on goods (not shipping); FAA $5; budget $2,000. Shipping per distinct ship_group, EST: RMRC $15.00,
TMotor $10.71, Amazon $10.71, Prusa $10.71 (EST, D-183), Local $0 (RMRC rates not readable, see review/QP-1/COST.md).
Status: verified = vendor page read 2026-11-14; unverified = snippet (U) or estimate (EST).
Crash reserve = one bad crash BEYOND the spares in the BOM: 1 flight pack + 1 motor + 1 servo + 1 full airframe set
(foam, spar tube, fin CFRP, half the PETG; D-183: cost cuts applied, see review/QP-2/D183.md) x 1.1025 + 3 shipments (TMotor, RMRC, Amazon).  FC and ESC-board loss are NOT in
it (a bad crash that also kills them is not covered); stated in MASS-GATE / BASELINE."""
import csv, os, math
TAX, FAA, BUDGET, BUMP = 0.1025, 5.0, 2000.0, 0.30
SHIP = {"RMRC": 15.0, "TMotor": 10.71, "Amazon": 10.71, "Prusa": 10.71, "SparkFun": 8.00, "Local": 0.0, "RDQ":10.71,"Metal":10.71,"Rockwest":10.71,"CLC":10.71,"FibGlassSupply":10.71,"USPlastic":10.71,"Zoro":10.71,"Adafruit":10.71}
rows = list(csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "BOM-T081.csv"), encoding="utf-8")))
for r in rows:
    r["qty"] = float(r["qty"]); r["u"] = float(r["unit_usd"]); r["spares"] = float(r["spares"])
U = lambda r: r["status"] == "unverified"

def goods(bump=0.0, sub=None):
    return sum(r["qty"]*r["u"]*(1+(bump if U(r) else 0)) for r in rows if sub in (None, r["subsystem"]))
def line(i): return next(r["u"] for r in rows if r["id"] == i)
def ship(): return sum(SHIP[g] for g in {r["ship_group"] for r in rows})
def reserve(bump=0.0):
    f = 1 + bump
    tubes = sum(r["qty"]*r["u"] for r in rows if r["id"] in ("R02", "R08", "R09", "R10"))   # QP-4: full carbon-tube set (16x14, 3 x 12x10, 14x12, 6x4.5); R04 removed
    airset = line("R01")*f + tubes + 0.5*line("R03")*f
    return (line("W01") + line("P01") + line("M01") + airset)*(1+TAX) + SHIP["TMotor"] + SHIP["RMRC"] + SHIP["Amazon"]
def totals(bump=0.0):
    g = goods(bump); spend = g*(1+TAX) + ship() + FAA; res = reserve(bump)
    return dict(goods=g, tax=g*TAX, ship=ship(), spend=spend, reserve=res, total=spend+res, margin=BUDGET-spend-res)
def sub_cost(s, bump=0.0): return goods(bump, s)*(1+TAX)

SUBS = [s for s in ["propulsion", "power", "avionics", "mechanisms", "airframe", "ground_test", "tools", "transport"] if any(r["subsystem"] == s for r in rows)]  # tools, transport cut by D-183
# cap = subsystem at nominal price rounded up to $5. +30 % growth does NOT fit under $2,000 (see main), so any subsystem
# crossing its cap is the early warning; the sum of caps plus the gap to $2,000 is the contingency.
CAPS = {s: math.ceil(sub_cost(s)/5)*5 for s in SUBS}
CAPS.update(shipping_faa=math.ceil((ship()+FAA)/5)*5, crash_reserve=math.ceil(reserve()/5)*5)

if __name__ == "__main__":
    t, t30 = totals(), totals(BUMP)
    unv = sum(r["qty"]*r["u"] for r in rows if U(r))
    print("| Item | $ |\n|---|---|")
    for k, v in (("Goods", t["goods"]), ("Tax 10.25 %", t["tax"]), ("Shipping (EST)", t["ship"]), ("FAA", FAA),
                 ("Spend", t["spend"]), ("Crash reserve", t["reserve"]), ("**Total**", t["total"]), ("**Margin**", t["margin"])):
        print(f"| {k} | {v:,.2f} |")
    print(f"\nUnverified goods (U + EST): {unv:.2f} ({100*unv/t['goods']:.0f} % of goods); lines {sum(U(r) for r in rows)} of {len(rows)}")
    print(f"+30 % on unverified lines: total {t30['total']:,.2f}, margin {t30['margin']:+,.2f}")
    print(f"Growth absorbed: margin / (goods x 1.1025) = {100*t['margin']/(t['goods']*1.1025):.0f} %")
    print(f"Margin >= $100 at +30 %: {'PASS' if t30['margin']>=100 else 'FAIL'}; R5 total <= $1,750 (replaced by G7): {'PASS' if t['total']<=1750 else 'FAIL'}")
    g7 = t30['margin'] >= 100 and t['total'] <= 1800   # QP-3 board G7
    print(f"G7 (+30 % margin >= $100 AND total <= $1,800): {'PASS' if g7 else 'FAIL'} (total {t['total']:,.2f}, +30 % margin {t30['margin']:+,.2f})")
    print()
    print("| Subsystem | Nominal $ (incl tax) | +30 % unverified | Cap $ | Unverified share |\n|---|---|---|---|---|")
    for s in SUBS:
        gs = goods(0, s); us = sum(r["qty"]*r["u"] for r in rows if r["subsystem"] == s and U(r))
        print(f"| {s} | {sub_cost(s):.2f} | {sub_cost(s, BUMP):.2f} | {CAPS[s]} | {100*us/gs:.0f} % |")
    print(f"| shipping + FAA | {t['ship']+FAA:.2f} | | {CAPS['shipping_faa']} | EST |")
    print(f"| crash reserve | {t['reserve']:.2f} | {reserve(BUMP):.2f} | {CAPS['crash_reserve']} | |")
    capsum = sum(CAPS.values())
    print(f"\nCaps sum {capsum}; room left to $2,000: {BUDGET-capsum:.0f}")
    print("Over cap:", [s for s in SUBS if sub_cost(s) > CAPS[s]] or "none")
    print("Spares:")
    for r in rows:
        if r["spares"]: print(f"- {r['id']} {r['item']}: {int(r['spares'])} of {int(r['qty'])}")
