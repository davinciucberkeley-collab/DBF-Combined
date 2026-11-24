"""QP-1 cost totals.  Reproduce: python -I bom_qp1.py   (stdlib; reads BOM-QP1.csv beside it; prints markdown; writes nothing)
Basis: Berkeley tax 10.25 % on goods (repo basis); shipping per distinct ship_group; FAA $5; budget $2,000.
Shipping: RMRC checkout rates are not readable (page lists carriers, no dollars), so EST $15.00 per RMRC order;
Amazon $10.71 (repo basis); local pickup (Home Depot, Harbor Freight) $0.
Crash reserve = (one flight pack + one servo + one airframe set) x 1.1025 + 2 RMRC shipments.
Flags: V = vendor page read 2026-11-14; U = snippet / not read; EST = estimate.
Candidate T (scratch tilt-tri): sizing_T not available, so not priced here."""
import csv, os
TAX, FAA, BUDGET = 0.1025, 5.0, 2000.0
SHIP = {"RMRC": 15.00, "Amazon": 10.71, "Local pickup": 0.0}
WING = {"B": 60.0, "A": 45.0, "D2": 110.0}   # EST airframe set in the crash reserve (as RESTUDY)
PACK = {"B": "B06", "D2": "D03", "A": "A05"}
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BOM-QP1.csv")
rows = list(csv.DictReader(open(path, encoding="utf-8")))
for r in rows:
    r["qty"] = float(r["qty"]); r["unit"] = float(r["unit_usd"]); r["old"] = float(r["old_unit_usd"])

def lines(cfg):
    return [r for r in rows if r["config"] in ("floor", cfg)]

def total(cfg, bump=0.0):
    L = lines(cfg)
    goods = sum(r["qty"] * r["unit"] * (1 + (bump if r["flag"] in ("EST", "U") else 0)) for r in L)
    ship = sum(SHIP[g] for g in {r["ship_group"] for r in L})
    tax = goods * TAX
    spend = goods + tax + ship + FAA
    pack = next(r["unit"] for r in rows if r["id"] == PACK[cfg])
    servo = next(r["unit"] for r in rows if r["id"] == "F07")
    reserve = (pack + servo + WING[cfg]) * (1 + TAX) + 2 * SHIP["RMRC"]
    unv = sum(r["qty"] * r["unit"] for r in L if r["flag"] in ("EST", "U"))
    return dict(goods=goods, tax=tax, ship=ship, spend=spend, reserve=reserve,
                total=spend + reserve, margin=BUDGET - spend - reserve, unv=unv)

if __name__ == "__main__":
    print("| Cfg | Goods | Tax | Ship | FAA | Spend | Crash reserve | Total | Margin | EST/U goods | Margin if EST/U +30 % |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in ("B", "A", "D2"):
        t, t30 = total(c), total(c, 0.30)
        print(f"| {c} | {t['goods']:.2f} | {t['tax']:.2f} | {t['ship']:.2f} | {FAA:.2f} | {t['spend']:.2f} | "
              f"{t['reserve']:.2f} | {t['total']:.2f} | {t['margin']:+.2f} | {t['unv']:.2f} | {t30['margin']:+.2f} |")
    fg = sum(r["qty"] * r["unit"] for r in rows if r["config"] == "floor")
    print(f"\nFloor goods {fg:.2f}; with tax {fg*(1+TAX):.2f}")
    print("\nLines moved > 20 % vs RESTUDY unit price (lots normalised per set in the CSV):")
    print("| id | item | old | now | change |\n|---|---|---|---|---|")
    for r in rows:
        if r["old"] > 0 and abs(r["unit"] / r["old"] - 1) > 0.20:
            print(f"| {r['id']} | {r['item'][:60]} | {r['old']:.2f} | {r['unit']:.2f} | {100*(r['unit']/r['old']-1):+.0f} % |")
    print("\nFlag counts (lines): " + ", ".join(f"{k}={sum(1 for r in rows if r['flag']==k)}" for k in ("V", "U", "EST")))
