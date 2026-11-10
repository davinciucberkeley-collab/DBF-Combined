"""Writes ORDER-PLAN.md from the BOM lines in build_bom.py (tables are generated; the text around them is fixed here).

Run:  python -I redesign/team/I1/make_order_plan.py   (after build_bom.py)
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))
spec = importlib.util.spec_from_file_location("build_bom", HERE / "build_bom.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)

TAX = 0.1025
SHIP = {"EARLY": 75.0, "DEC": 45.0, "LOCAL": 0.0}

FLAGS = {
    "SunnySky USA": "page 429 on 2026-11-09, price by search snippet; measure bolt pattern, hole depth and leads on arrival",
    "OVONIC US": "**HOLD:** listing is 12 AWG leads, 680 g (CR-I1-13); sale price may end, list $119.88 is the pessimistic case",
    "APC": "props `CHK` $3.83; rings `EST`",
    "Amazon": "**LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each",
    "ReadyMadeRC": "FC page URL changed (product 87195); price carried from 2026-10-13; F3 gate (stable tailsitter build) before ordering",
    "RaceDayQuads": "",
    "RadioMaster": "select the **FCC** variant for both RP3 V2 and Pocket Crush (CR-F5-06); not LBT",
    "GetFPV": "18650 cells: RadioMaster says batteries ship only with a radio order",
    "Aloft Hobbies": "**LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST`",
    "Pyrodrone": "", "Pine64": "", "Bolt Depot": "minimum order may exceed the line price",
    "West3D": "ASA is not in the Jacobs free stock",
    "EMAX USA": "placeholder until D6 picks the servo (>= 3.04 kgf cm)",
    "Home Depot El Cerrito": "store pick-up; check the XPS sheet is flat",
    "Harbor Freight": "store pick-up",
}


def table(order, gated=False):
    rows = {}
    for l in B.L:
        if l["order"] != order or bool(l["gate"]) != gated:
            continue
        rows.setdefault(l["vendor"], []).append(l)
    out = ["| Vendor | Lines | Pre-tax | Tax | With tax | Lead (days) `EST` | Flag |", "|---|---|---|---|---|---|---|"]
    tg = 0.0
    for v, ls in sorted(rows.items(), key=lambda kv: -sum((x["fit"] + x["spare"]) * x["unit"] for x in kv[1])):
        g = round(sum((x["fit"] + x["spare"]) * x["unit"] for x in ls), 2)
        tg += g
        lead = max(x["lead"] for x in ls)
        long = any(x["long"] for x in ls)
        ids = ", ".join(f"`{x['id']}`" + (f" x{x['fit'] + x['spare']}" if x["fit"] + x["spare"] > 1 else "") for x in ls)
        out.append(f"| {v} | {ids} | ${g:,.2f} | ${g * TAX:,.2f} | ${g * (1 + TAX):,.2f} | {lead}{' **LONG**' if long else ''} | {FLAGS.get(v, '')} |")
    tg = round(tg, 2)
    return "\n".join(out), tg


def main():
    m = B.money(TAX)
    e_tab, e_g = table("EARLY")
    d_tab, d_g = table("DEC")
    l_tab, l_g = table("LOCAL")
    gl_tab, gl_g = table("LOCAL", gated=True)
    gd_tab, gd_g = table("DEC", gated=True)
    res_p, res_b = 2000 - m["spend_pess"], 2000 - m["spend_base"]
    res_pa, res_ba = 2000 - m["spend_pess_allin"], 2000 - m["spend_base_allin"]
    early_tot = e_g * (1 + TAX) + SHIP["EARLY"]
    dec_tot = d_g * (1 + TAX) + SHIP["DEC"]
    loc_tot = l_g * (1 + TAX)
    gated_rows = "\n".join(f"| {g['id']} | {g['item']} | ${B.gated_net(g['id']) * (1 + TAX):,.2f} | {g['gate']} |" for g in B.GATED)
    txt = f"""# Order plan: early order (~20 Nov 2026) and mid-December order (15 Dec 2026)

Revision I1-R2, 2026-11-09. Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv). Money: `python -I redesign/team/I1/build_bom.py`, then
`python -I redesign/team/I1/make_order_plan.py` regenerates the vendor tables below. Prices are 2026 list prices before 10.25 % tax.
`CHK` = compared with the vendor page on 2026-11-09, `CARRY` = carried from `cards/K09/cost.csv`, `EST` = estimate, no vendor page.

## Totals by order

| Order | Goods | Tax 10.25 % | Shipping `EST` | Total |
|---|---|---|---|---|
| Early, ~20 Nov | ${e_g:,.2f} | ${e_g * TAX:,.2f} | $75 | **${early_tot:,.2f}** |
| December, 15 Dec | ${d_g:,.2f} | ${d_g * TAX:,.2f} | $45 | **${dec_tot:,.2f}** |
| Store pick-up (XPS, jig, ammo can) | ${l_g:,.2f} | ${l_g * TAX:,.2f} | 0 | **${loc_tot:,.2f}** |
| FAA registration (DroneZone, not taxed) | | | | **$5.00** |
| Whole BOM, baseline (excl. gated lines) | ${m['goods_base']:,.2f} | ${m['tax_base']:,.2f} | $120 | **${m['spend_base']:,.2f}** (`CL-I1-SPEND-BASE`) |
| Whole BOM, pessimistic (excl. gated lines) | ${m['goods_pess']:,.2f} | ${m['tax_pess']:,.2f} | $150 | **${m['spend_pess']:,.2f}** (`CL-I1-SPEND-PESS`; + $5 FAA + $27 adders) |

## Reserve gate (hard: $2 000, reserve >= $309 on pessimistic numbers)

| Case | Spend | Reserve | Limit | Status |
|---|---|---|---|---|
| Committed order, baseline | ${m['spend_base']:,.2f} | ${res_b:,.2f} | >= $150 planned | `CHECKED` against inputs; prices `UNVERIFIED` |
| Committed order, pessimistic (Ovonic at list, tubes overseas, shipping +$30, tax measure +$7, jig/box +$20) | ${m['spend_pess']:,.2f} | **${res_p:,.2f}** (margin ${res_p - 309:,.2f}) | >= $309 | `UNVERIFIED` |
| **Everything bought**, baseline (gated X07 box/field kit and X08 airspeed sensor included) | ${m['spend_base_allin']:,.2f} | ${res_ba:,.2f} | >= $150 | holds |
| **Everything bought**, pessimistic | ${m['spend_pess_allin']:,.2f} | **${res_pa:,.2f}** | >= $309 | **FAILS by ${309 - res_pa:,.2f}** (`CL-I1-RESERVE-PESS-ALLIN`) |

**Why two lines.** Itemising the designers' requests (F1, C6, D3, D5, D7, E3, F3, H1) adds about $190 incl. tax over the R1 BOM, because the old
$124.01 wiring/hardware lump did not cover them. The committed order holds the $309 reserve only by holding two blocks behind a gate:
X07 (D7 box and field kit, store pick-up, $118.85, needed before the first drive to the field in March, no lead time) and X08 (airspeed sensor,
$66.14, DECISION 5.1 lever, last in the lever order). Cheaper levers than X08, each needing a fact I cannot verify from here, are in `SUMMARY.md`.

## Early order, ~20 Nov (electronics, packs, test hardware, power parts)

Purpose: the $40 foam-board twin, the thrust stand, charging and first power bench on real hardware (`CONFIGURATION.md` de-risking). Place it as
five or six carts. Re-read every listing first (`T-I1-LISTINGS`).

{e_tab}

**Early total ${early_tot:,.2f}** (goods ${e_g:,.2f} + tax ${e_g * TAX:,.2f} + shipping $75 `EST`). Before the first charge (late Nov, store): `G03` ammo can,
Harbor Freight 63750, $19.99 + $2.05 tax. **Do not place the pack cart (`P01`) until CR-I1-13 is answered** (12 AWG leads, 680 g on the 2026-11-09 listing).

At order, in the cart:

| Check | Value | Why |
|---|---|---|
| Pack connector | XT60 (listing: "XT60 to TRA plug") | CR-I1-06; the AS150U pair `F01` is crimped on afterwards |
| Pack lead gauge | **>= 10 AWG** (listing says 12 AWG: fails) | CR-F1-14: 12 AWG rises 28.4 K at 30.3 A against 20 K |
| Pack mass | <= 658 g, expect 550 g (listing says 680 g: fails) | `HANDOFF` L2, `CL-A3-GATE-MARGIN-680` |
| RP3 V2 and Pocket Crush | FCC variant | CR-F5-06 |
| FC | CoreWing F405 Wing APP V2 (not the Mini: no bdshot) | CR-F3-06 |
| ESC | LANRC 4-pack: title, 45 A, 4 pieces, price | CR-I1-04 |

## Mid-December order, 15 Dec (airframe, mechanisms, fin and fastener kits)

Place the Aloft carbon cart first (tubes, strips, 20x18 tube), then the rest.

{d_tab}

**December total ${dec_tot:,.2f}** (goods ${d_g:,.2f} + tax ${d_g * TAX:,.2f} + shipping $45 `EST`). Store pick-up in January (`LOCAL`):

{l_tab}

## Gated lines held in the BOM (not in any total above)

| Gate | Item | Cost incl. tax | Condition |
|---|---|---|---|
{gated_rows}

With the baseline reserve of ${res_b:,.2f}, X07 + X08 ($184.99) leave ${res_b - 184.99:,.2f}: both fit on baseline, not on pessimistic numbers.
The gate test is the realised reserve (2 000 minus actual spend after the December receipts), not the pessimistic forecast.

## Borrow list (not bought, not in the BOM): H1's rig, Jacobs Hall (D-39)

Needs a yes from Jacobs Hall staff in writing before 20 Nov (`T-I1-BORROW`). Bought for the rig: G06 ($17.97, 20 kgf cell kit, already in the baseline) and G12 ($17.00, new, <= $20).

| Item | From H1's list ($ `EST`) | If not lent |
|---|---|---|
| 2 x 5 kg x 1 g scales | 30 | buy; +$33 incl. tax |
| Optical tachometer | 20 | use ESC rpm telemetry (F4 bdshot) |
| K-type thermocouple meter / logger | in the $30 thermal line | gated X09 $16.54 |
| 10 kg spring scale, sandbags, straps, eye bolts | 20 | luggage scale and shop weights |
| 608 bearings, M8 rod, plywood, fasteners (stand frame) | 15 | shop stock; +$17 |
| Bench supply >= 44.6 A for 14.8 V sweeps | not listed | use a flight pack with V logged at the ESC (H1 rule) |
| 100 A watt meter | 20 | `G04` ($12.99) is bought |

## Long-lead and risk flags

| Item | Why | Mitigation |
|---|---|---|
| Carbon tubes `W03`, `W04` | overseas lead ~14 days is the critical path for the build start (19 Jan) | US-stock Aloft in the early order; December Aloft cart first; Aloft or overseas by the bend-test result (CR-I1-08, 10 Dec) |
| Strips and 20x18 tube `D01`-`D03` | same Aloft cart, `EST` prices | order with the tubes; weigh the strips on arrival |
| Ovonic packs `P01` | 12 AWG leads and 680 g on the listing; sale ends | CR-I1-13: E2 and F1 name a SKU; order first once named |
| LANRC ESC `B02` | listing unconfirmed | open the page before 20 Nov; Tekko32 fallback +$60 |
| Small Parts adapters | out of stock; now gated X05 | E1's fallback: adapter in each motor box + Loctite 243 |
| FC `A01` | firmware support unconfirmed; page moved | F3 gate before ordering |
| Shipping | $120 baseline assumes few carts; this plan has about 14 vendors | free-shipping thresholds on Amazon, Aloft, RadioMaster; re-quote in cart |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |
"""
    (HERE / "ORDER-PLAN.md").write_text(txt, encoding="utf-8")
    print("written", len(txt))


if __name__ == "__main__":
    main()
