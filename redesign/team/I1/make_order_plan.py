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
    "Ampow / OVONIC (same SKU)": "**LONG LEAD (~14 d, ships from Germany); USD price not found**: baseline EUR 98.69 x 1.16, pessimistic EUR 113.30 x 1.16. Ask the seller for 10 AWG leads before paying",
    "APC": "props `CHK` $3.83; rings `EST`",
    "Amazon": "**LANRC ASIN B0D2HS4Y4J unconfirmed** (503, no US 4-pack page): open it first; fallback Tekko32 +$60; many `EST` lines, re-read each",
    "ReadyMadeRC": "**Place this cart first with the pack cart (WB-01 / D-74):** the board check (`subsystems/power/BOARD-CHECK.md`, 30 min on arrival) gates the pod CAD freeze. Page URL changed (product 87195); price carried from 2026-10-13",
    "RaceDayQuads": "",
    "RadioMaster": "select the **FCC** variant for both RP3 V2 and Pocket Crush (CR-F5-06); not LBT",
    "GetFPV": "18650 cells: RadioMaster says batteries ship only with a radio order",
    "Aloft Hobbies": "**LONG LEAD if the overseas fallback is needed** (tubes); strips and 20x18 tube `EST`",
    "Pyrodrone": "", "Pine64": "", "Bolt Depot": "minimum order may exceed the line price",
    "West3D": "ASA is not in the Jacobs free stock",
    "Savox USA / hobby dealer": "single-source 12 mm servo; US dealer with stock; price from D6, not re-read",
    "Amazon / DigiKey": "JST-GH from DigiKey: separate shipping, use pigtails if the cart allows",
    "Amazon / hobby shop": "",
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

Revision I1-R3, 2026-11-10. Status `PROPOSED`. Lines, prices and part numbers: [`BOM.csv`](BOM.csv). Money: `python -I redesign/team/I1/build_bom.py`, then
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
| Committed order, pessimistic (Ovonic at EUR 113.30 x 1.16, tubes overseas, shipping +$30, tax measure +$7, jig/box +$20) | ${m['spend_pess']:,.2f} | **${res_p:,.2f}** (margin ${res_p - 309:,.2f}) | >= $309 | `UNVERIFIED` |
| **Everything bought**, baseline (gated X07 box/field kit and X08 airspeed sensor included) | ${m['spend_base_allin']:,.2f} | ${res_ba:,.2f} | >= $150 | **FAILS by ${150 - res_ba:,.2f}** |
| **Everything bought**, pessimistic | ${m['spend_pess_allin']:,.2f} | **${res_pa:,.2f}** | >= $309 | **FAILS by ${309 - res_pa:,.2f}** (`CL-I1-RESERVE-PESS-ALLIN`) |

**What changed in R3 (CR-A1-67, D-72).** Pack re-priced for the Ovonic 120C EC5 pair (+$31.51 baseline, +$11.55 pessimistic, pre-tax); Savox SH-0255MG+ replaces the placeholder
servo (+$44.00); the $6 T-antennas, FC isolation set, F2 harness lines, D6 mechanisms hardware, 2.5 mm CF rod, PA66 socket-head set, 7/32 in brass tube and two strain gauges are
itemised; the D7 mat, tote, spares box and labels sit in the gated X07. Net of the designers' lines: pessimistic spend +$130.55 pre-tax ($143.94 incl. tax) before any lever.
**Lever 1 alone is not enough.** Borrowing the soldering kit (G07-G10, $94.80 incl. tax) leaves the pessimistic reserve at $263.87, $45.13 under the $309 crash.
Lever 2 (borrow the hot-wire gear G11 + H05, $62.54) is also applied and gives the reserve above. Both are bought if Jacobs Hall refuses (gates X10, X11): H1's written yes before 20 Nov is a hard dependency.
The committed order holds the $309 reserve only by holding blocks behind gates: X07 (D7 box and field kit, store pick-up, needed before the first drive to the field in March), X08 (airspeed sensor, DECISION 5.1 lever), X10, X11.

## Early order, ~20 Nov (electronics, packs, test hardware, power parts)

Purpose: the $40 foam-board twin, the thrust stand, charging and first power bench on real hardware (`CONFIGURATION.md` de-risking). Place it as
five or six carts. **Place the pack cart (`P01`) first: ~14 days from Germany. Place the ReadyMadeRC FC cart (`A01`) the same day:** its board check closes the WB-01 blocker before the pod CAD freeze. Re-read every listing first (`T-I1-LISTINGS`).

{e_tab}

**Early total ${early_tot:,.2f}** (goods ${e_g:,.2f} + tax ${e_g * TAX:,.2f} + shipping $75 `EST`). Before the first charge (late Nov, store): `G03` ammo can,
Harbor Freight 63750, $19.99 + $2.05 tax. The pack cart (`P01`) is released by D-64 after the two checks below; **no USD price is confirmed**, read the cart total before paying (pessimistic case $131.43).

At order, in the cart:

| Check | Value | Why |
|---|---|---|
| Pack SKU | Ovonic 4S 6500 mAh **120C hard case, EC5, 2-pack**, listed 551 +/- 5 g, 135 x 46 x 49 mm | D-64, CR-E2-24; NOT the 130C XT60 SKU (680 g) |
| Pack lead gauge | **>= 10 AWG** confirmed by the seller (the page does not print it); 12 AWG: stop, tell E2 and F1 | CR-F1-14: 12 AWG rises 28.4 K at 30.3 A against 20 K |
| Pack mass on arrival | accept <= 592.6 g each (`CL-A1-PACK-ACCEPT`) | weigh both, log in E2 `pack_log.csv` |
| RP3 V2 and Pocket Crush | FCC variant | CR-F5-06 |
| FC | CoreWing F405 Wing APP V2 (not the Mini: no bdshot); on arrival check the PDB board and the 470 uF cap are in the box, then run `subsystems/power/BOARD-CHECK.md` the same day | CR-F3-06, WB-01, D-74 |
| ESC | LANRC 4-pack: title, 45 A, 4 pieces, price | CR-I1-04 |

## Mid-December order, 15 Dec (airframe, mechanisms, fin and fastener kits)

Place the Aloft carbon cart first (tubes, strips, 20x18 tube), then the rest. Servos (Savox) have a 7-day lead `EST`: the same day.

{d_tab}

**December total ${dec_tot:,.2f}** (goods ${d_g:,.2f} + tax ${d_g * TAX:,.2f} + shipping $45 `EST`). Store pick-up in January (`LOCAL`):

{l_tab}

## Gated lines held in the BOM (not in any total above)

| Gate | Item | Cost incl. tax | Condition |
|---|---|---|---|
{gated_rows}

With the baseline reserve of ${res_b:,.2f}, X07 + X08 ($184.99) leave ${res_b - 184.99:,.2f}: both fit on baseline, not on pessimistic numbers.
The gate test is the realised reserve (2 000 minus actual spend after the December receipts), not the pessimistic forecast.

## Borrow list (not bought, not in the spend): Jacobs Hall (D-39, D-57 levers 1 and 2, D-72)

Needs a yes from Jacobs Hall staff **in writing before 20 Nov** (`T-I1-BORROW`, H1 obtains it). Two blocks fall in this list because the budget needs them:

| Lever | Lines | Cost if refused (incl. tax) | Needed for |
|---|---|---|---|
| 1: soldering kit | `G07` Pinecil, `G08` PD supply, `G09` multimeter, `G10` solder/flux/wick (gate X10) | $94.80 | harness, ESC leads, AS150U re-termination (every build week) |
| 2: hot-wire gear | `G11` 30 V 10 A supply + Ni80 wire, `H05` bow and template stock (gate X11) | $62.54 | wing core cutting (January) |

Bought for the rig: G06 ($17.97, 20 kgf cell kit, already in the baseline), G12 ($17.00) and G13 ($9.00, fin-proof strain gauges, CR-C4-38).

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
| Ovonic packs `P01` | ships from Germany (~14 days); no USD price found; 10 AWG leads unconfirmed | order first on 20 Nov; ask the seller for the lead gauge; fallback Tattu 4S 6750 XT90 (605 g, A1 must accept) |
| Savox servos `M01` | single-source 12 mm servo, price from D6 | order 15 Dec with a US dealer; the spare (X02, $46.29) first when the reserve allows |
| Jacobs Hall loan | levers 1 and 2 rest on a written yes | H1 before 20 Nov; a refusal costs $157.34 and breaks the reserve gate |
| LANRC ESC `B02` | listing unconfirmed | open the page before 20 Nov; Tekko32 fallback +$60 |
| Small Parts adapters | out of stock; now gated X05 | E1's fallback: adapter in each motor box + Loctite 243 |
| FC `A01` | power-board facts (split, link, outline) are from the manual only; page moved | order in the first cart; `BOARD-CHECK.md` on arrival before the pod CAD freeze (WB-01) |
| Shipping | $120 baseline assumes few carts; this plan has about 14 vendors | free-shipping thresholds on Amazon, Aloft, RadioMaster; re-quote in cart |
| Tax | Measure V (+0.5 %) leading on 2026-11-09; effective date unknown | +$7 kept in the pessimistic adders |
"""
    (HERE / "ORDER-PLAN.md").write_text(txt, encoding="utf-8")
    print("written", len(txt))


if __name__ == "__main__":
    main()
