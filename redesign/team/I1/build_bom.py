"""I1 procurement / BOM engineer: single BOM, order plan numbers and budget claims for the K09-L quad tailsitter.

Run:  python -I redesign/team/I1/build_bom.py     -> BOM.csv, bom_summary.json, claims.json beside this file
Then: python -I redesign/proofs/build_graph.py    -> confirms nothing drifted

Method. LINES is the one list of every purchased item (data, not analysis). Money is computed from it:
  goods      = sum(qty x unit price)          (qty = fitted + spare)
  tax        = 10.25 % of taxable goods       (P:requirements.tax_rate)
  shipping   = flat class-S estimate           (cards/K09/cost.csv, DECISION section 9)
  baseline   = goods + tax + shipping + FAA fee
  pessimistic= same lines at their pessimistic prices + the DECISION section 9 adders (shipping +30, tax measure +7,
               jig/box +20)
  reserve    = budget - spend
`bridge()` re-derives the pessimistic spend from the tie-break's $1 678.58 plus this BOM's line deltas, so the
two paths must agree to the cent (asserted in main).
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "proofs"))          # redesign/proofs (python -I adds no paths)
import proofkit as pk  # noqa: E402

# ------------------------------------------------------------------ the BOM
# order: EARLY = ~20 Nov 2026 order (twin, thrust stand, charging); DEC = ~15 Dec 2026 order; LOCAL = pick-up in store
# status: CHK = compared with the vendor page on 2026-11-09 (page or search snippet of the vendor page);
#         CARRY = price carried from cards/K09/cost.csv or k01-lean/cost.csv (date in `seen`), not re-checked;
#         EST = estimate, no vendor page
SHIP_BASE, SHIP_ADV, TAXMEAS_ADV, JIG_ADV, FAA_FEE = 120.00, 30.00, 7.00, 20.00, 5.00
TAX_NOTE = "Berkeley 10.25 % (CDTFA 2026-10-01); Measure V (+0.5 %) leading on 2026-11-09, effective date unknown"

L = []


def line(id, group, item, vendor, pn, order, fit, spare, unit, pess=None, status="CARRY", seen="2026-11-01",
         lead=5, long=False, url="", note="", part="", taxable=True):
    L.append(dict(id=id, group=group, item=item, vendor=vendor, pn=pn, order=order, fit=fit, spare=spare, unit=unit,
                  pess=unit if pess is None else pess, status=status, seen=seen, lead=lead, long=long, url=url,
                  note=note, part=part, taxable=taxable))


# --- propulsion (E1: subsystems/propulsion/parts.csv)
line("B01", "propulsion", "Motor SunnySky X3108S KV900", "SunnySky USA", "X3108S, KV900 variant", "EARLY", 4, 1, 24.99,
     status="CHK", seen="2026-11-09", lead=5, url="https://sunnyskyusa.com/products/sunnysky-x3108s-motors", part="PRP-001",
     note="search snippet of the vendor page: $24.99, 60 in stock; page itself 429 on fetch. Measure bolt pattern and lead length on arrival")
line("B02", "propulsion", "ESC LANRC BLHeli_S 45 A 4-pack (4 fitted, 0 spare)", "Amazon", "ASIN B0D2HS4Y4J", "EARLY", 1, 0, 30.00,
     status="CARRY", seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0D2HS4Y4J", part="PRP-002",
     note="UNVERIFIED: Amazon 503 on 2026-11-09, search finds no US LANRC 4-pack page. Check the live page (title, 45 A, 4-pack, price) before the order. Fallback Holybro Tekko32 F4 45A AM32 $22.50 each (backorder to Dec 2026): +$60 for 4")
line("B03", "propulsion", "Prop APC 11x5.5MR / 11x5.5MRP (LP11055MR / MRP): 2 + 2 fitted, 4 spare", "APC", "LP11055MR, LP11055MRP", "EARLY", 4, 4, 3.83,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.apcprop.com/product/11x5-5mr/", part="PRP-003",
     note="vendor page fetched 2026-11-09: $3.83, 0.60 oz; stock not stated on the page")
line("B04", "propulsion", "Prop APC 11x4.5MR / 11x4.5MRP (LP11045MR, LP11045MRP) for the thrust-stand A/B", "APC", "LP11045MR, LP11045MRP", "EARLY", 4, 0, 3.83,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.apcprop.com/product/11x4-5mr/", part="PRP-003",
     note="2 MR + 2 MRP (CR-E1-12); $3.83 per SRC-APC-11X45MR, checked 2026-11-09")
line("B05", "propulsion", "Prop adapter ring APC LPAR06E-type (centres the hub on the M6 post)", "APC", "LPAR06E", "EARLY", 4, 8, 0.50,
     status="EST", seen="2026-11-09", lead=5, url="https://www.apcprop.com/", part="PRP-004", note="price ESTIMATE as cost.csv")
line("B06", "propulsion", "Prop adapter set bolt-on M6x1, 2 RH + 2 LH + M3x4 screws + M6 nuts", "Small Parts CNC", "product_id 174 (set of 4)", "DEC", 1, 0, 23.95,
     status="CARRY", seen="2026-11-09", lead=14, long=True, url="https://www.smallpartscnc.com/index.php?product_id=174&route=product%2Fproduct", part="PRP-004",
     note="out of stock on 2026-11-09 (E1). Re-check on 20 Nov and 15 Dec; fallback is the adapter in each motor box plus Loctite 243 (-$23.95)")
line("B07", "propulsion", "Motor screw M3x8 SHCS ISO 4762 A2 (16 fitted + 4 spare)", "Bolt Depot", "M3-0.5 x 8 socket head A2", "EARLY", 16, 4, 0.10,
     status="CARRY", seen="2026-11-01", lead=5, url="https://www.boltdepot.com/", part="PRP-005",
     note="per-piece price from the old design's F01; check Bolt Depot minimum order; the hardware kit may already hold M3x8")
# --- power
line("P01", "power", "LiPo Ovonic 4S 6500 mAh 130C, 2-pack (2 flight packs, no packs 3-4, no 4S 4000)", "OVONIC US", "2x 4S 6500 130C XT60 (listing title says 'XT60 to TRA plug')", "EARLY", 1, 0, 79.25, pess=119.88,
     status="CHK", seen="2026-11-09", lead=7, long=True, url="https://us.ovonicshop.com/products/2-x-ovonic-4s-6500mah-14-8v-130c-lipo-battery-with-xt60-to-tra-plug-for-1-8-1-10-scale-rc-car-truck-boat", part="PWR-001",
     note="$79.25 sale, list $119.88, in stock, an automatic $5 discount at checkout (search snippet of the vendor page); pessimistic = list. CHECK that the connector is XT60 and what 'TRA plug' means; weigh each pack on arrival (T-E2-WEIGH, <= 680 g)")
# --- avionics (F3)
line("A01", "avionics", "Flight controller CoreWing F405 Wing APP V2", "ReadyMadeRC", "CoreWing F405 Wing APP V2", "EARLY", 1, 0, 67.26,
     seen="2026-10-13", lead=5, url="https://www.readymaderc.com/", part="AVN-001",
     note="F3 confirms a stable ArduPilot Plane tailsitter build exists first (firmware.ardupilot.org); else SpeedyBee F405 Wing $47.99 (RaceDayQuads, stock unverified, -$19.27) or Matek F405-WING")
line("A02", "avionics", "GPS + compass HGLRC M100-5883", "RaceDayQuads", "M100-5883", "EARLY", 1, 0, 20.49,
     seen="2026-10-13", lead=5, url="https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen", part="AVN-002")
line("A03", "avionics", "Receiver RadioMaster RP3 V2 ELRS", "RadioMaster", "RP3 V2", "EARLY", 1, 0, 19.99,
     seen="2026-10-13", lead=5, url="https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver", part="AVN-003")
line("A04", "avionics", "Airspeed sensor Holybro MS5525 + pitot", "Holybro", "MS5525 digital airspeed", "DEC", 1, 0, 59.99,
     seen="2026-11-09", lead=10, url="https://holybro.com/", part="AVN-004",
     note="needed for the fixed-wing tune, not for the twin: order in December. DECISION section 5: first lever if a pessimistic adder lands (defer, +$66)")
# --- mechanisms (D6)
line("M01", "mechanisms", "Elevon servo EMAX ES3005HV 8 kgf-cm (2 fitted, 0 spare)", "EMAX USA", "ES3005HV", "DEC", 2, 0, 19.99,
     seen="2026-11-01", lead=7, url="https://shop.emax-usa.com/products/es3005hv-high-voltage-servo", part="MEC-001",
     note="PLACEHOLDER pending D6: B2 needs >= 3.04 kgf-cm and the 12 g EMAX ES08MA II (~2 kgf-cm) is too weak. Mass and 6-8.4 V supply UNVERIFIED")
# --- airframe
line("W01", "airframe", "XPS FOAMULAR NGX F-250 2 in x 4 x 8 ft (about 6 wing cores)", "Home Depot El Cerrito", "F-250 2 in", "LOCAL", 1, 0, 59.97,
     seen="2026-10-01", lead=0, url="https://www.homedepot.com/", part="WNG-001", note="pick-up; check the sheet is flat and unbroken")
line("W02", "airframe", "Foam board 20x30 in, 10-pack (fins, first foam-board twin)", "Amazon", "ASIN B074QZMLQF", "EARLY", 1, 0, 35.92,
     seen="2026-10-01", lead=4, url="https://www.amazon.com/dp/B074QZMLQF", part="FIN-001")
line("W03", "airframe", "Carbon tube 22x20x1000 mm matte, US stock (one for C4's bend test, then the spare)", "Aloft Hobbies", "22 x 20 x 1000mm MW carbon tubing matte", "EARLY", 1, 0, 24.00,
     status="CHK", seen="2026-11-09", lead=5, url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish", part="WNG-002",
     note="CR-J1-07. Vendor page: $24.00, in stock, shipping at checkout; mandrel-wound, layup unstated. Weigh and bend-test on arrival")
line("W04", "airframe", "Carbon tube 22x20x1000 mm matte (spar + 2 motor tubes cut from one + 0 spare), order after the bend test", "Aloft Hobbies", "same SKU as W03", "DEC", 2, 0, 24.00, pess=28.32,
     status="CHK", seen="2026-11-09", lead=5, url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish", part="WNG-002",
     note="baseline: Aloft $24 if the W03 bend test passes. Pessimistic and fallback: the BOM's overseas Amazon tube $28.32 (cost.csv, ~14 days: order first, 15 Dec at the latest)")
line("W05", "airframe", "PETG filament 1 kg (Ambrosia)", "West3D", "PETG 1 kg", "DEC", 1, 0, 20.99,
     seen="2026-10-01", lead=5, url="https://west3d.com/", part="FIN-002", note="non-structural prints in Jacobs' free PLA")
line("W06", "airframe", "Packing tape Scotch Heavy Duty, 6 rolls", "Amazon", "ASIN B000087KUA", "EARLY", 1, 0, 19.98,
     seen="2026-10-01", lead=4, url="https://www.amazon.com/dp/B000087KUA", part="WNG-003")
line("W07", "airframe", "Foam-safe glue (UHU Por / Gorilla clear)", "Amazon", "ESTIMATE vendor", "EARLY", 1, 0, 12.99,
     status="EST", seen="2026-11-01", lead=4, url="https://www.amazon.com/", part="WNG-004")
# --- hardware
line("H01", "hardware", "Wiring + hardware kit, share needed for the twin and the stand (est. 55 of 124.01)", "mixed (F1/F2 itemise)", "AS150U / XT60, 12-16 AWG, bullets, screws, inserts, Velcro, epoxy, UBEC, horns, pushrods, hinge tape", "EARLY", 1, 0, 55.00,
     status="EST", seen="2026-11-01", lead=5, url="", part="HRN-001",
     note="lump floor from cost_model.py HARDWARE_MIN; split 55.00 + 69.01 is an I1 estimate. F1/F2 owe an itemised list (CR-I1-01)")
line("H02", "hardware", "Wiring + hardware kit, balance", "mixed (F1/F2 itemise)", "as H01", "DEC", 1, 0, 69.01,
     status="EST", seen="2026-11-01", lead=5, url="", part="HRN-001", note="see H01")
line("H03", "hardware", "Re-terminate packs and charge lead XT60 to AS150U (only if F1 picks AS150U)", "mixed", "AS150U pair", "DEC", 1, 0, 15.00,
     status="EST", seen="2026-11-09", lead=5, url="", part="HRN-002", note="K09 REVIEW section 6; drops to $0 if F1 keeps XT60 (params.json electrical.main_disconnect)")
line("H04", "hardware", "Transport box 1.25 x 0.55 x 0.50 m (1/4 in ply + foam cradles)", "Home Depot El Cerrito", "ply + foam", "LOCAL", 1, 0, 60.00,
     status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-001", note="K09 REVIEW section 6 ($25 + 35); D7 freezes the size")
line("H05", "hardware", "Hot-wire bow/jig + airfoil template stock", "Home Depot El Cerrito", "-", "LOCAL", 1, 0, 15.00,
     status="EST", seen="2026-11-09", lead=0, url="", part="WNG-005", note="K01 REVIEW section 2")
# --- avionics ground-side / radio
line("R01", "avionics", "Transmitter RadioMaster Pocket Crush ELRS", "RadioMaster", "Pocket Crush", "EARLY", 1, 0, 64.99,
     seen="2026-10-13", lead=5, url="https://www.radiomasterrc.com/products/pocket-crush-radio-controller", part="GND-001")
line("R02", "avionics", "18650 cells, 2-pack for the Pocket (not included)", "GetFPV", "Lumenier 18650 2-pack", "EARLY", 1, 0, 24.49,
     seen="2026-11-09", lead=5, url="https://www.getfpv.com/", part="GND-001", note="K09 REVIEW section 6; the Pocket does not run on USB alone")
# --- ground equipment
line("G01", "ground", "Charger HTRC C150 150 W AC", "Amazon", "ASIN B0H4QLJYHY", "EARLY", 1, 0, 56.99, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/dp/B0H4QLJYHY", part="GND-002", note="E2: read the manual for max charge current and IR function on arrival")
line("G02", "ground", "LiPo bag (Pyrodrone)", "Pyrodrone", "LiPo bag", "EARLY", 2, 0, 9.99, seen="2026-11-01", lead=5, url="https://pyrodrone.com/", part="GND-003")
line("G03", "ground", "Ammo can (Harbor Freight 63750)", "Harbor Freight", "63750", "LOCAL", 1, 0, 19.99, seen="2026-11-01", lead=0,
     url="https://www.harborfreight.com/50-caliber-metal-ammo-can-63750.html", part="GND-004")
line("G04", "ground", "Watt meter 150 A", "Amazon", "ASIN B0F13JWDFV", "EARLY", 1, 0, 12.99, seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0F13JWDFV", part="GND-005")
line("G05", "ground", "IR thermometer", "Amazon", "ASIN B0BN317X6Z", "EARLY", 1, 0, 8.98, seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0BN317X6Z", part="GND-006")
line("G06", "ground", "Thrust stand: 20 kg load cell + HX711 + Nano", "Amazon", "kit (budget-energy-test.md)", "EARLY", 1, 0, 17.97, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/", part="GND-007", note="H1: the stand must take >= 2.5 kgf")
line("G07", "ground", "Soldering iron Pinecil V2", "Pine64", "Pinecil V2", "EARLY", 1, 0, 25.99, seen="2026-11-01", lead=7, url="https://pine64.com/", part="GND-008")
line("G08", "ground", "USB-C PD supply for the iron", "Amazon", "ESTIMATE", "EARLY", 1, 0, 20.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-008")
line("G09", "ground", "Multimeter", "Amazon", "ESTIMATE", "EARLY", 1, 0, 25.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-009")
line("G10", "ground", "Solder, flux, wick", "Amazon", "ESTIMATE", "EARLY", 1, 0, 15.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-010")
line("G11", "ground", "Hot-wire: NICE-POWER 30 V 10 A supply + Ni80 24 AWG", "Amazon", "ASIN B0CRSS744F + B0CP9V3DBX", "DEC", 1, 0, 41.73, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/dp/B0CRSS744F", part="GND-011")

# Gated purchases: NOT in the totals. Bought only when the stated test passes (D-12 pattern).
GATED = [
    dict(id="X01", item="2nd LANRC ESC 4-pack (4 spare ESCs)", net=30.00, gate="realised reserve after all December receipts >= $309 + this line incl. tax",
         why="was in the carried BOM (CR-E1-12 '4 + 4'); deferred to hold the pessimistic reserve >= $309 (CR-I1-02)"),
    dict(id="X02", item="Spare elevon servo (3rd ES3005HV)", net=19.99, gate="as X01", why="spare, 2 fitted"),
    dict(id="X03", item="Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included)", net=16.68, gate="as X01; only if the stand shows the MR/MRP pair short",
         why="alternate for the stand A/B"),
    dict(id="X04", item="Flight packs 3-4, one more Ovonic 2-pack", net=79.25, gate="D-12: reserve after the December order >= $309 + $87.37 (at sale price)",
         why="2 sorties per test day until then"),
    dict(id="X05", item="Remote ID module NewBeeDrone BeeID", net=39.99, gate="only if flown outside the RFS FRIA", why="CONFIGURATION: none fitted"),
]


# ------------------------------------------------------------------ arithmetic (pure; the proof chain re-runs these)
def _sum(key, orders=None, taxable_only=False):
    return round(sum((l["fit"] + l["spare"]) * l[key] for l in L
                     if (orders is None or l["order"] in orders) and (l["taxable"] or not taxable_only)), 2)


def money(tax_rate):
    goods_b, goods_p = _sum("unit"), _sum("pess")
    tax_b, tax_p = round(goods_b * tax_rate, 2), round(goods_p * tax_rate, 2)
    spend_b = round(goods_b + tax_b + SHIP_BASE + FAA_FEE, 2)
    spend_p = round(goods_p + tax_p + SHIP_BASE + FAA_FEE + SHIP_ADV + TAXMEAS_ADV + JIG_ADV, 2)
    early = round(_sum("unit", {"EARLY"}) * (1 + tax_rate), 2)
    return dict(goods_base=goods_b, goods_pess=goods_p, tax_base=tax_b, tax_pess=tax_p, spend_base=spend_b, spend_pess=spend_p,
                early_goods_tax=early)


def bridge(tax_rate):
    """Pessimistic spend = tie-break $1 678.58 + this BOM's pre-tax deltas x (1 + tax). Independent of money()."""
    tb = 1678.58
    deltas = {
        "elevon servos 2 x 19.99 replace the DECISION's $30 (horns and hinge are in the hardware kit)": 2 * 19.99 - 30.00,
        "carbon tubes: 1 + 2 Aloft-or-overseas replace 3 overseas": (24.00 + 2 * 28.32) - 3 * 28.32,
        "Small Parts adapter set (CR-E1-20)": 23.95,
        "16 + 4 M3x8 screws (CR-E1-20)": 20 * 0.10,
        "second ESC pack deferred (X01)": -30.00,
        "prop and ring lines unchanged (12 x 3.83, 12 x 0.50)": 0.0,
    }
    return round(tb + sum(deltas.values()) * (1 + tax_rate), 2), deltas


def reserve_calc(budget, spend):
    return round(budget - spend, 2)


# ------------------------------------------------------------------ proof chain
kit = pk.Kit(__file__, params=["../../params/params.json"])
P = "P:"

kit.source("SRC-I1-SUNNYSKY", "SunnySky USA X3108S page", kind="web", url="https://sunnyskyusa.com/products/sunnysky-x3108s-motors",
           where="search snippet 2026-11-09: KV900 variant $24.99, 60 units; page fetch returned HTTP 429",
           note="not compared with the rendered page: stock and price to be re-read on 20 Nov", status="UNVERIFIED")
kit.source("SRC-I1-APC-PRICE", "APC 11x5.5MR page", kind="web", url="https://www.apcprop.com/product/11x5-5mr/", checked="2026-11-09",
           where="fetched 2026-11-09: $3.83, 0.60 oz; stock not stated; 11x4.5MR $3.83 per SRC-APC-11X45MR")
kit.source("SRC-I1-ALOFT", "Aloft Hobbies 22 x 20 x 1000 mm tube", kind="web",
           url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish",
           where="search 2026-11-09: $24.00, in stock, mandrel wound, shipping at checkout; page fetch 429",
           note="layup and wall stiffness not stated: C4 bend test decides whether December buys the same SKU", status="UNVERIFIED")
kit.source("SRC-I1-OVONIC", "OVONIC US 2 x 4S 6500 mAh 130C listing", kind="web",
           url="https://us.ovonicshop.com/products/2-x-ovonic-4s-6500mah-14-8v-130c-lipo-battery-with-xt60-to-tra-plug-for-1-8-1-10-scale-rc-car-truck-boat",
           where="search 2026-11-09: $79.25, list $119.88, In Stock, automatic $5 discount at checkout; reseller rcdrone.top shows $142.24 sold out",
           note="title says 'XT60 to TRA plug': confirm the XT60 connector; mass not on the page", status="UNVERIFIED")
kit.source("SRC-I1-LANRC", "LANRC 45 A ESC 4-pack (Amazon B0D2HS4Y4J)", kind="web", url="https://www.amazon.com/dp/B0D2HS4Y4J",
           where="HTTP 503 on 2026-11-09 (also E1); search finds only LANRC 45 A single units (45 A cont, 50 A / 10 s, 2-6S) at non-US shops",
           note="price, pack size and rating of this ASIN unconfirmed: check in a browser before 20 Nov", status="UNVERIFIED")
kit.source("SRC-I1-CARRIED", "Carried prices (cost.csv)", kind="web", url="redesign/config-study/cards/K09/cost.csv",
           where="all lines marked CARRY or EST in BOM.csv; dates in the `seen` column", status="UNVERIFIED")

kit.assumption("ASM-I1-SHIPPING", "Shipping 120 + 30 USD", "Class-S shipping for all vendors is $120 at baseline, +$30 in the pessimistic case",
               basis="cards/K09/cost.csv shipping line and DECISION section 9; no vendor quote taken", value=SHIP_BASE + SHIP_ADV, unit="USD",
               status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-TIEBREAK"])
kit.assumption("ASM-I1-ADDERS", "Pessimistic adders 27 USD", "Tax measure +7 and jig/box growth +20 USD on top of list-price lines",
               basis="DECISION section 9 (K01 REVIEW S8-S11 applied to every candidate)", value=TAXMEAS_ADV + JIG_ADV, unit="USD",
               status="UNVERIFIED", cites=["SRC-TIEBREAK"])

BOM_INPUTS = {"tax": P + "requirements.tax_rate", "budget": P + "requirements.budget_usd"}
BOM_UNITS = {"tax": "-", "budget": "USD"}


@kit.calc("CALC-I1-SPEND", title="BOM spend, baseline and pessimistic", inputs={"tax": P + "requirements.tax_rate"},
          units={"tax": "-"}, assumes=["ASM-I1-SHIPPING", "ASM-I1-ADDERS"], cites=["SRC-I1-CARRIED", "SRC-I1-APC-PRICE", "SRC-I1-OVONIC"],
          equation="spend = sum(qty x unit) x (1 + tax) + shipping + FAA fee (+ adders, pessimistic prices); lines in team/I1/build_bom.py LINES")
def spend(tax):
    return money(tax)


@kit.calc("CALC-I1-BRIDGE", title="Bottom-up minus tie-break bridge", inputs={"tax": P + "requirements.tax_rate", "sp": "CL-I1-SPEND-PESS"},
          units={"tax": "-", "sp": "USD"}, cites=["SRC-TIEBREAK"],
          equation="delta = spend_pess(bottom-up) - [1678.58 + sum(line deltas) x (1 + tax)]", output="delta_usd")
def spend_bridge(tax, sp):
    return round(sp - bridge(tax)[0], 2)


@kit.calc("CALC-I1-RESERVE", title="Reserve at order, pessimistic and baseline",
          inputs={"budget": P + "requirements.budget_usd", "sp": "CL-I1-SPEND-PESS", "sb": "CL-I1-SPEND-BASE"},
          units={"budget": "USD", "sp": "USD", "sb": "USD"}, equation="reserve = budget - spend")
def reserve(budget, sp, sb):
    return {"reserve_pess": reserve_calc(budget, sp), "reserve_base": reserve_calc(budget, sb)}


kit.claim("CL-I1-SPEND-BASE", "BOM spend at order, baseline", calc="CALC-I1-SPEND", output="spend_base", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Re-run build_bom.py after re-pricing each line on the day of the order; compare with the order confirmations.")
kit.claim("CL-I1-SPEND-PESS", "BOM spend at order, pessimistic", calc="CALC-I1-SPEND", output="spend_pess", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Same lines at list price plus the DECISION section 9 adders; CL-I1-BRIDGE-DELTA must be 0.")
kit.claim("CL-I1-BRIDGE-DELTA", "Bottom-up minus tie-break bridge (USD)", calc="CALC-I1-BRIDGE", output="delta_usd", unit="USD",
          limit=("<=", 0.02),
          how="Non-zero means a BOM line changed without the bridge table in build_bom.py bridge() being updated.")
kit.claim("CL-I1-RESERVE-PESS", "Pessimistic reserve at order", calc="CALC-I1-RESERVE", output="reserve_pess", unit="USD",
          limit=(">=", P + "requirements.crash_cost_usd"), verifies=["R-RESERVE", "R-BUDGET"],
          how="2 000 minus CL-I1-SPEND-PESS must be >= 309 (one class-S crash incl. tax). On the day: re-price every CARRY line.")
kit.claim("CL-I1-RESERVE-BASE", "Baseline reserve at order", calc="CALC-I1-RESERVE", output="reserve_base", unit="USD",
          limit=(">=", P + "requirements.crash_reserve_planned_usd"), verifies=["R-RESERVE"],
          how="2 000 minus CL-I1-SPEND-BASE must be >= 150 (planned reserve, P2).")

kit.test("T-I1-LISTINGS", "Re-read the six listings before each order", verifies=["CL-I1-SPEND-PESS", "CL-I1-RESERVE-PESS"], state="planned",
         procedure="On 20 Nov and 15 Dec open: LANRC ASIN B0D2HS4Y4J, SunnySky X3108S, Ovonic 2-pack (connector, price), Aloft tube, "
                   "Small Parts 4114, APC 11x5.5MR/11x4.5MR; log price and stock in team/I1/listing_log.csv; re-run build_bom.py.")
kit.test("T-I1-ARRIVAL", "Weigh and inspect on arrival", verifies=["CL-I1-RESERVE-PESS"], state="planned",
         procedure="Weigh each pack, motor, ESC and the Aloft tube; check the pack connector is XT60; give masses to A3 and E2 (pack_log.csv).")


# ------------------------------------------------------------------ outputs
def write_outputs(tax_rate=0.1025, budget=2000.0, crash=309.0):
    m = money(tax_rate)
    bridge_val, deltas = bridge(tax_rate)
    assert abs(bridge_val - m["spend_pess"]) < 0.015, f"bridge {bridge_val} vs bottom-up {m['spend_pess']}"
    rp, rb = reserve_calc(budget, m["spend_pess"]), reserve_calc(budget, m["spend_base"])
    cols = ["line", "group", "part_id", "item", "vendor", "part_number", "url", "order", "qty_fitted", "qty_spare", "qty_total",
            "unit_usd", "unit_usd_pessimistic", "ext_usd", "tax_usd", "ext_incl_tax_usd", "lead_time_days", "long_lead",
            "price_status", "price_seen", "note"]
    with open(HERE / "BOM.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for l in L:
            q = l["fit"] + l["spare"]
            ext = round(q * l["unit"], 2)
            tax = round(ext * tax_rate, 2) if l["taxable"] else 0.0
            w.writerow([l["id"], l["group"], l["part"], l["item"], l["vendor"], l["pn"], l["url"], l["order"], l["fit"], l["spare"], q,
                        f"{l['unit']:.2f}", f"{l['pess']:.2f}", f"{ext:.2f}", f"{tax:.2f}", f"{ext + tax:.2f}", l["lead"],
                        "YES" if l["long"] else "", l["status"], l["seen"], l["note"]])
        w.writerow([])
        w.writerow(["TOTAL", "", "", "Goods pre-tax, baseline", "", "", "", "", "", "", "", "", "", f"{m['goods_base']:.2f}"])
        w.writerow(["TOTAL", "", "", f"Sales tax 10.25 %", "", "", "", "", "", "", "", "", "", f"{m['tax_base']:.2f}"])
        w.writerow(["TOTAL", "", "", "Shipping, all vendors (ESTIMATE)", "", "", "", "", "", "", "", "", "", f"{SHIP_BASE:.2f}"])
        w.writerow(["TOTAL", "", "", "FAA registration (not taxed)", "", "", "", "", "", "", "", "", "", f"{FAA_FEE:.2f}"])
        w.writerow(["TOTAL", "", "", "Spend baseline", "", "", "", "", "", "", "", "", "", f"{m['spend_base']:.2f}"])
        w.writerow(["TOTAL", "", "", "Spend pessimistic (list prices + adders 57)", "", "", "", "", "", "", "", "", "", f"{m['spend_pess']:.2f}"])
        w.writerow(["TOTAL", "", "", "Reserve baseline / pessimistic", "", "", "", "", "", "", "", "", "", f"{rb:.2f} / {rp:.2f}"])
    by = {}
    for l in L:
        by.setdefault(l["vendor"], 0.0)
        by[l["vendor"]] += (l["fit"] + l["spare"]) * l["unit"]
    out = dict(money=m, reserve_pess=rp, reserve_base=rb, bridge=dict(value=bridge_val, deltas=deltas), vendors={k: round(v, 2) for k, v in by.items()},
               by_order={o: round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["order"] == o), 2) for o in ("EARLY", "DEC", "LOCAL")},
               gated={g["id"]: round(g["net"] * (1 + tax_rate), 2) for g in GATED})
    (HERE / "bom_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    kit.write()
    print(json.dumps(write_outputs(), indent=1))
