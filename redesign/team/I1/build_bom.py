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
         lead=5, long=False, url="", note="", part="", taxable=True, gate=""):
    L.append(dict(gate=gate, id=id, group=group, item=item, vendor=vendor, pn=pn, order=order, fit=fit, spare=spare, unit=unit,
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
line("B07", "propulsion", "Motor screw M3x8 SHCS ISO 4762 A2 (16 fitted + 4 spare)", "Bolt Depot", "M3-0.5 x 8 socket head A2", "EARLY", 16, 4, 0.10,
     status="CARRY", seen="2026-11-01", lead=5, url="https://www.boltdepot.com/", part="PRP-005",
     note="per-piece price from the old design's F01; check Bolt Depot minimum order; the hardware kit may already hold M3x8")
# --- power
line("P01", "power", "LiPo Ovonic 4S 6500 mAh 130C, 2-pack (2 flight packs, no packs 3-4, no 4S 4000)", "OVONIC US", "2x 4S 6500 130C XT60 (listing title says 'XT60 to TRA plug')", "EARLY", 1, 0, 82.97, pess=119.88,
     status="CHK", seen="2026-11-09", lead=7, long=True, url="https://us.ovonicshop.com/products/2-x-ovonic-4s-6500mah-14-8v-130c-lipo-battery-with-xt60-to-tra-plug-for-1-8-1-10-scale-rc-car-truck-boat", part="PWR-001",
     note="vendor page fetched 2026-11-09: $82.97 sale (list $119.88), in stock, XT60 plug with a TRA adapter, 12 AWG leads, 680 g per pack. Earlier search snippet showed $79.25 after a $5 checkout discount. 12 AWG FAILS F1's >= 10 AWG pack-lead rule (CL-F1-PACKLEAD12-RISE 28.4 K vs 20 K) and 680 g puts the aircraft 4 g over the gate (CL-A3-GATE-MARGIN-680): DO NOT ORDER this SKU until E2 and F1 decide (CR-I1-13). Pessimistic = list")
# --- avionics (F3)
line("A01", "avionics", "Flight controller CoreWing F405 Wing APP V2", "ReadyMadeRC", "CoreWing F405 Wing APP V2", "EARLY", 1, 0, 67.26,
     seen="2026-10-13", lead=5, url="https://www.readymaderc.com/products/details/87195-corewing-f405-wing-app-v2-fixed-wing-flight-controller-unsoldered-pins", part="AVN-001",
     note="CR-F3-06 / CR-A1-39: order V2 now (the Mini lacks bdshot). ReadyMadeRC product 87195 'unsoldered pins'; the old URL returns 404 and search shows no price, so the price is carried from 2026-10-13: re-read before ordering. Fallback SpeedyBee F405 Wing APP $47.99 (-$19.27, RaceDayQuads, stock unverified)")
line("A02", "avionics", "GPS + compass HGLRC M100-5883", "RaceDayQuads", "M100-5883", "EARLY", 1, 0, 20.49,
     seen="2026-10-13", lead=5, url="https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen", part="AVN-002")
line("A03", "avionics", "Receiver RadioMaster RP3 V2 ELRS", "RadioMaster", "RP3 V2 ELRS 2.4 GHz, FCC variant", "EARLY", 1, 0, 19.99,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver", part="AVN-003",
     note="CR-F5-06: select the FCC variant, NOT LBT (LBT caps 100 mW). Page fetched 2026-11-09: $19.99 sale, FCC and LBT both listed at $19.99 and available")
line("A04", "avionics", "Airspeed sensor RMRC digital (MS4525DO) + pitot tube", "ReadyMadeRC", "RMRC digital airspeed sensor MS4525DO + pitot", "DEC", 1, 0, 59.99,
     seen="2026-11-09", lead=10, url="https://www.readymaderc.com/", part="AVN-004",
     note="CR-F3-06: MS4525DO replaces the MS5525 line (same $59.99). Needed for the fixed-wing tune (January), not for the twin. Lever if the reserve needs help (+$66.14 incl. tax, DECISION 5.1)")
line("A05", "avionics", "microSD card 16-32 GB (FC log)", "Amazon", "SanDisk class, 16-32 GB", "EARLY", 1, 0, 6.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="AVN-006", note="CR-F3-06: team stock first; nothing is owned, so carried. Gel pads from shop consumables")
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
line("H01", "hardware", "Harness and mechanism consumables, early share: 3.5 mm bullets, servo leads, JST-GH pigtails (twin and stand)", "Amazon", "assorted", "EARLY", 1, 0, 12.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-001",
     note="residual of the old $124.01 lump after the F1, C6 and D3 items moved to their own lines (F01-F09, C01-C05, D01-D06). F2 has no parts.csv yet (CR-I1-01); D6 has none either")
line("H02", "hardware", "Harness and mechanism consumables, balance: horns, pushrods, clevises, hinge tape, ties, Kapton", "Amazon", "assorted", "DEC", 1, 0, 24.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.amazon.com/", part="HRN-001", note="see H01; D6 owes the horn and pushrod list")
line("H03", "hardware", "Charger-side XT60 pair for the AS150U charge adapter + 0.3 m 10 AWG stub", "Amazon", "XT60 pair, 10 AWG silicone", "DEC", 1, 0, 5.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-002",
     note="was $15 for the whole AS150U re-termination; F01 now buys the five AS150U pairs, so only the charger-side XT60 and a short 10 AWG stub remain")
# --- power (F1, CR-F1-12), itemised from team/F1/POWER.md 'Bought items'
line("F01", "power", "Amass AS150U connector pair (male + female) x 5: aircraft, 2 packs, charge lead, spare", "Amazon", "Amass AS150U", "EARLY", 5, 0, 5.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.amazon.com/", part="PWR-003", note="F1 price EST $25 for 5; open the Amass sheet. Confirm the SKU is the anti-spark AS150U, not AS150")
line("F02", "power", "Silicone wire 8 AWG red + black, 0.5 m each", "Amazon", "8 AWG silicone", "EARLY", 1, 0, 8.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-004", note="main pigtail; vendors sell 1 m minimum")
line("F03", "power", "Silicone wire 16 AWG red + black, 2.5 m each", "Amazon", "16 AWG silicone", "EARLY", 1, 0, 8.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-004", note="ESC leads, F2 cuts")
line("F04", "power", "Silicone wire 20 AWG red + black, 1 m each", "Amazon", "20 AWG silicone", "EARLY", 1, 0, 4.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-005", note="UBEC feed, servo bus")
line("F05", "power", "UBEC 6 V, 8 A class (Hobbywing type)", "Amazon", "UBEC 6 V 8 A", "EARLY", 1, 0, 18.00, status="EST", seen="2026-11-09", lead=5, url="https://www.readymaderc.com/", part="PWR-005", note="F1: datasheet UNVERIFIED; 13 g in A3's roll-up")
line("F06", "power", "Mini blade fuse 5 A x 3 + inline holder", "Amazon", "ATM mini fuse + holder", "EARLY", 1, 0, 6.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="UBEC feed protection")
line("F07", "power", "Capacitor 680 uF 25 V low-ESR x 5", "Amazon", "680 uF 25 V", "EARLY", 1, 0, 5.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="one per ESC + 1 spare")
line("F08", "power", "Bare 4-way PDB, 2 oz copper", "Amazon", "bare PDB 2 oz", "EARLY", 1, 0, 6.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="bus")
line("F09", "power", "Heat-shrink assortment incl. 10 mm", "Amazon", "assortment", "EARLY", 1, 0, 6.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="joints")
# --- fasteners and bonding (C6 kit, CR-C6-11; D3's fasteners are inside it)
line("C01", "hardware", "M3 fasteners: SHCS A2-70 x10 (M3x10) + x8 (M3x16), nyloc x10, washer x15 (covers D3's M3x16 x6, nyloc x6, washer x12)", "Bolt Depot", "ISO 4762 / 10511 / 7089 A2", "EARLY", 1, 0, 5.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.boltdepot.com/", part="HRN-003", note="C6 kit table; piece prices about $3 plus minimum-order rounding. M3x8 x20 is B07. M3 only")
line("C02", "hardware", "M3 x 5.7 brass heat-set inserts x12 + M3 nylon washers / FC grommets x8", "Amazon", "Ruthex-class RX-M3x5.7", "DEC", 1, 0, 9.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="pod FC plate (4), PDB (4), spares (4)")
line("C03", "hardware", "Pultruded CF rod 2 mm x 1 m (strip through-pins; D3 FIN-012 uses the same rod)", "Amazon", "CF rod 2 mm", "DEC", 1, 0, 3.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="CR-C6-11; D3 FIN-012 not double counted")
line("C04", "hardware", "Loctite 243 (10 ml) + paint pen (torque witness)", "Amazon", "Loctite 243", "DEC", 1, 0, 9.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="motor screws, tip threads only")
line("C05", "hardware", "Laminating epoxy 30 min (small kit) + colloidal silica + glass microballoons", "Amazon", "30 min epoxy kit", "DEC", 1, 0, 14.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="C6 and D3 (FIN-105) both list shop stock; nothing is owned, so one kit is carried. Drop if Jacobs Hall confirms stock in writing")
# --- fin materials (D3, CR-D3-09; the tube is W04)
line("D01", "airframe", "Pultruded CF strip 10 x 3 x 1000 mm x 1 (4 braces)", "Aloft Hobbies", "CF strip 10x3", "DEC", 1, 0, 10.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-009", note="D3 est. about $10 per length")
line("D02", "airframe", "Pultruded CF strip 10 x 1 x 1000 mm x 3 (8 edge strips)", "Aloft Hobbies", "CF strip 10x1", "DEC", 3, 0, 6.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-011", note="D3 est. about $6 per length, 3 m asked in CR-D3-09")
line("D03", "airframe", "CF tube 20 x 18 x 1000 mm x 1 (D3 plugs 2 x 53 mm; C2's spar plugs if the same size)", "Aloft Hobbies", "20 x 18 x 1000 CF tube", "DEC", 1, 0, 20.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-006", note="D3 priced a $1 share; stock is sold by the metre. Ask C2 whether its six 36 mm plugs use this tube")
line("D04", "airframe", "10 mm hook-and-loop straps x 10 (ESC retention x4, spares)", "Amazon", "ONE-WRAP class", "DEC", 1, 0, 8.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="FIN-104", note="D3 FIN-104, 4 needed")
line("D05", "landing", "Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in", "Amazon", "neoprene 40A 1/16 in", "DEC", 1, 0, 12.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.mcmaster.com/", part="GER-006", note="CR-D5-10: D5 names McMaster-Carr (separate cart and shipping); an Amazon sheet is carried. Price UNVERIFIED; 4 pads + 12 spares per sheet")
line("D06", "pod", "Pack straps 20 x 300 mm hook-and-loop rubber-backed x2 + 0.5 mm silicone sheet", "Amazon", "battery strap", "DEC", 1, 0, 6.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="POD-004", note="D2 POD-004")
line("W08", "airframe", "ASA filament 1 kg (motor mounts FIN-003, ESC pads FIN-007; D-42)", "West3D", "ASA 1 kg", "DEC", 1, 0, 24.99,
     status="EST", seen="2026-11-09", lead=5, url="https://west3d.com/", part="FIN-003", note="NOT in CR-A1-39: D-42 prints mounts and pads in ASA and Jacobs Hall stocks PLA only, so a spool is bought. 4 x 12.66 + 4 x 1.86 g = 58 g; a 0.5 kg spool if offered")
# --- transport (D7 parts.csv replaces the old $60 plywood-box estimate H04)
line("T01", "transport", "Coroplast 4 mm 48 x 96 in x 2 (box base, lid)", "Home Depot El Cerrito", "Coroplast 4 mm", "LOCAL", 2, 0, 15.00,
     status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-001", note="D7 TRN-001 $30 incl. lid TRN-005; replaces H04 plywood box")
line("T02", "transport", "LSE double-sided tape, 1 roll (3M 300LSE class)", "Home Depot El Cerrito", "3M 300LSE class", "LOCAL", 1, 0, 12.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-101", note="D7")
line("T03", "transport", "Cam-buckle straps x2 + strap handles x3", "Home Depot El Cerrito", "25 mm tie-down, luggage handle", "LOCAL", 1, 0, 24.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-006", note="D7 TRN-006-A/B 2 x 6 + TRN-007 3 x 4")
line("T04", "transport", "Field pouch + 10 mm prop spanner (D-40) + M3x16 / nyloc / fender washers x6", "Home Depot El Cerrito", "pouch, 10 mm spanner", "LOCAL", 1, 0, 13.80, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-008", note="D7 TRN-008 8 + TRN-106 4 + TRN-102 1.80")
line("T05", "transport", "Ground mat 0.6 x 0.6 m EVA tile", "Home Depot El Cerrito", "EVA tile", "LOCAL", 1, 0, 10.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-104", note="D7 TRN-104. C5 wants a RUBBER landing mat (CR-C5-06): D7 and C5 reconcile; one mat carried")
line("T06", "transport", "PE foam plank 2 in + 1 in (cradle columns, lid pillars)", "Home Depot El Cerrito", "PE foam 1.7 pcf", "LOCAL", 1, 0, 18.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-002", note="D7 TRN-002-L/R 12, TRN-004-L/R 6; XPS offcuts for the tray")
line("H05", "hardware", "Hot-wire bow/jig + airfoil template stock", "Home Depot El Cerrito", "-", "LOCAL", 1, 0, 15.00,
     status="EST", seen="2026-11-09", lead=0, url="", part="WNG-005", note="K01 REVIEW section 2")
# --- avionics ground-side / radio
line("R01", "avionics", "Transmitter RadioMaster Pocket Crush ELRS", "RadioMaster", "Pocket Crush, ELRS / FCC variant", "EARLY", 1, 0, 64.99,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.radiomasterrc.com/products/pocket-crush-radio-controller", part="GND-001",
     note="CR-F5-06: choose 'ELRS / FCC' (page lists ELRS/FCC and ELRS/LBT at $64.99). The page does not state the module power: F5 confirms 25-250 mW on arrival. Fetched 2026-11-09. Batteries not included")
line("R02", "avionics", "18650 cells, 2-pack for the Pocket (not included)", "GetFPV", "Lumenier 18650 2-pack", "EARLY", 1, 0, 24.49,
     seen="2026-11-09", lead=5, url="https://www.getfpv.com/", part="GND-001", note="K09 REVIEW section 6; the Pocket does not run on USB alone. RadioMaster says batteries cannot ship separately from a radio order: if GetFPV cannot ship them, add RadioMaster cells to the same order")
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

line("G12", "groundtest", "Ground-test additions: 1 kgf bar cell + HX711 (torque arm) + 5 K-type thermocouple probes", "Amazon", "1 kg bar load cell + HX711; K-type bead probe x5", "EARLY", 1, 0, 17.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-012",
     note="CR-A1-39 / D-39: the only NEW ground-test purchase, <= $20. With G06 (20 kgf cell kit, $17.97) the bought rig is $34.97; everything else on H1's list is borrowed (ORDER-PLAN borrow table)")

# Lines that stay in this BOM (vendor, part number, price) but are bought only when their gate passes: NOT in the spend
# totals, reported in the `all-in` figures. X07 = D7 box and field kit (store pick-up, zero lead time, needed from March);
# X08 = airspeed sensor (DECISION 5.1 lever; needed for the fixed-wing tune, which can start on the synthetic airspeed).
GATE_OF = {"T01": "X07", "T02": "X07", "T03": "X07", "T04": "X07", "T05": "X07", "T06": "X07", "A04": "X08"}
for _l in L:
    _l["gate"] = GATE_OF.get(_l["id"], "")

# Gated purchases: NOT in the totals. Bought only when the stated test passes (D-12 pattern).
GATED = [
    dict(id="X01", item="2nd LANRC ESC 4-pack (4 spare ESCs)", net=30.00, gate="realised reserve after all December receipts >= $309 + this line incl. tax",
         why="was in the carried BOM (CR-E1-12 '4 + 4'); deferred to hold the pessimistic reserve >= $309 (CR-I1-02)"),
    dict(id="X02", item="Spare elevon servo (3rd ES3005HV)", net=19.99, gate="as X01", why="spare, 2 fitted"),
    dict(id="X03", item="Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included)", net=16.68, gate="as X01; only if the stand shows the MR/MRP pair short",
         why="alternate for the stand A/B"),
    dict(id="X04", item="Flight packs 3-4, one more Ovonic 2-pack", net=82.97, gate="D-12: reserve after the December order >= $309 + $91.47 (at sale price); and only a SKU that passes CR-I1-13",
         why="2 sorties per test day until then"),
    dict(id="X05", item="Small Parts CNC 4114 prop adapter set (2 RH + 2 LH), CR-E1-20 / D-39", net=23.95, gate="as X01; only if the motor-box adapters fail the stand (T-E1-STAND) and the page is back in stock",
         why="out of stock on 2026-11-09; E1's fallback (adapter in each motor box + Loctite 243) accepted in D-39"),
    dict(id="X06", item="Remote ID module NewBeeDrone BeeID", net=39.99, gate="only if flown outside the RFS FRIA", why="CONFIGURATION: none fitted"),
    dict(id="X07", item="D7 box and field kit (lines T01-T06: Coroplast, tape, straps, handles, pouch, spanner, mat, PE foam)", net=None, gate="as X01, before the first drive to the field (store pick-up, no lead time); until then a borrowed carton",
         why="deferred in R2 to hold the pessimistic reserve >= $309 (CR-I1-14); replaces the old $60 plywood estimate H04"),
    dict(id="X08", item="RMRC MS4525DO airspeed sensor + pitot (line A04)", net=None, gate="as X01; DECISION 5.1 lever, last in the order (CR-I1-03)",
         why="needed for gain scheduling in fixed-wing flight; the first fixed-wing tune can run on the synthetic airspeed estimate (F4 confirms)"),
    dict(id="X09", item="K-type thermocouple logger / 2-channel meter (E3 GT-04)", net=15.00, gate="only if Jacobs Hall cannot lend one", why="H1 borrow list"),
]


# ------------------------------------------------------------------ arithmetic (pure; the proof chain re-runs these)
def _sum(key, orders=None, taxable_only=False, gated=False):
    return round(sum((l["fit"] + l["spare"]) * l[key] for l in L
                     if (orders is None or l["order"] in orders) and (l["taxable"] or not taxable_only)
                     and (gated or not l["gate"])), 2)


def gated_net(gid):
    """Pre-tax value of one gated purchase: its own `net`, or the sum of the BOM lines that carry the gate."""
    g = next(x for x in GATED if x["id"] == gid)
    if g["net"] is not None:
        return g["net"]
    return round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["gate"] == gid), 2)


def money(tax_rate):
    goods_b, goods_p = _sum("unit"), _sum("pess")
    tax_b, tax_p = round(goods_b * tax_rate, 2), round(goods_p * tax_rate, 2)
    spend_b = round(goods_b + tax_b + SHIP_BASE + FAA_FEE, 2)
    spend_p = round(goods_p + tax_p + SHIP_BASE + FAA_FEE + SHIP_ADV + TAXMEAS_ADV + JIG_ADV, 2)
    early = round(_sum("unit", {"EARLY"}) * (1 + tax_rate), 2)
    # all-in: every BOM line including the ones held behind a gate (X07, X08), same shipping and adders
    goods_pa = _sum("pess", gated=True)
    spend_pess_all = round(goods_pa * (1 + tax_rate) + SHIP_BASE + FAA_FEE + SHIP_ADV + TAXMEAS_ADV + JIG_ADV, 2)
    spend_base_all = round(_sum("unit", gated=True) * (1 + tax_rate) + SHIP_BASE + FAA_FEE, 2)
    return dict(spend_pess_allin=spend_pess_all, spend_base_allin=spend_base_all, goods_base=goods_b, goods_pess=goods_p, tax_base=tax_b, tax_pess=tax_p, spend_base=spend_b, spend_pess=spend_p,
                early_goods_tax=early)


def bridge(tax_rate):
    """Pessimistic spend = I1-R1 pessimistic spend ($1 680.35, itself bridged to the tie-break $1 678.58 in R1) + this
    revision's pre-tax deltas x (1 + tax). The delta numbers are typed here from the designers' requests, not read from L,
    so money() and bridge() agree only if every line change was recorded."""
    r1 = 1680.35
    deltas = {
        "old $124.01 wiring/hardware lump (H01 55.00 + H02 69.01) removed": -124.01,
        "old H03 AS150U re-termination $15.00 and old H04 plywood box $60.00 removed": -75.00,
        "new H01 12.00 + H02 24.00 residual harness and mechanism consumables + H03 5.00 charger XT60 stub": 12.00 + 24.00 + 5.00,
        "F01-F09 power items (CR-F1-12): 25 + 8 + 8 + 4 + 18 + 6 + 5 + 6 + 6": 86.00,
        "C01-C05 fastener, insert, rod, Loctite, epoxy kit (CR-C6-11)": 5.00 + 9.00 + 3.00 + 9.00 + 14.00,
        "D01-D04 CF strips, CF tube 20x18, straps (CR-D3-09)": 10.00 + 3 * 6.00 + 20.00 + 8.00,
        "D05 neoprene (CR-D5-10) and D06 pack straps (D2)": 12.00 + 6.00,
        "W08 ASA spool (D-42, not in CR-A1-39)": 24.99,
        "A05 microSD (CR-F3-06)": 6.00,
        "G12 ground-test additions (CR-A1-39, <= $20)": 17.00,
        "B06 Small Parts adapter set to gated X05 (D-39)": -23.95,
        "A04 airspeed sensor held behind gate X08": -59.99,
        "T01-T06 D7 box and field kit held behind gate X07 (0 in the spend)": 0.0,
    }
    return round(r1 + sum(deltas.values()) * (1 + tax_rate), 2), deltas


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
           where="fetched 2026-11-09: $82.97 sale, list $119.88, in stock, XT60 plug with a TRA adapter, 12 AWG leads, 680 g per pack; an earlier search snippet showed $79.25; reseller rcdrone.top $142.24 sold out",
           note="12 AWG leads fail F1's >= 10 AWG rule and 680 g exceeds the mass gate by 4 g (A3): the SKU needs E2/F1 sign-off before ordering (CR-I1-13)", status="UNVERIFIED")
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


@kit.calc("CALC-I1-BRIDGE", title="Bottom-up minus R1-bridge (pessimistic spend)", inputs={"tax": P + "requirements.tax_rate", "sp": "CL-I1-SPEND-PESS"},
          units={"tax": "-", "sp": "USD"}, cites=["SRC-TIEBREAK"],
          equation="delta = spend_pess(bottom-up) - [1680.35 (R1) + sum(R2 line deltas) x (1 + tax)]", output="delta_usd")
def spend_bridge(tax, sp):
    return round(sp - bridge(tax)[0], 2)


@kit.calc("CALC-I1-RESERVE", title="Reserve at order, pessimistic and baseline",
          inputs={"budget": P + "requirements.budget_usd", "sp": "CL-I1-SPEND-PESS", "sb": "CL-I1-SPEND-BASE"},
          units={"budget": "USD", "sp": "USD", "sb": "USD"}, equation="reserve = budget - spend")
def reserve(budget, sp, sb):
    return {"reserve_pess": reserve_calc(budget, sp), "reserve_base": reserve_calc(budget, sb)}


@kit.calc("CALC-I1-ALLIN", title="All-in spend if every gated BOM line (X07, X08) were also bought",
          inputs={"tax": P + "requirements.tax_rate", "budget": P + "requirements.budget_usd"},
          units={"tax": "-", "budget": "USD"}, assumes=["ASM-I1-SHIPPING", "ASM-I1-ADDERS"],
          equation="all-in spend = spend + gated lines x (1 + tax); reserve = budget - spend", output="reserve_pess_allin")
def allin(tax, budget):
    m = money(tax)
    return {"reserve_pess_allin": reserve_calc(budget, m["spend_pess_allin"]), "reserve_base_allin": reserve_calc(budget, m["spend_base_allin"])}


@kit.calc("CALC-I1-GROUNDTEST", title="New bought ground-test purchase (line G12)", inputs={"tax": P + "requirements.tax_rate"},
          units={"tax": "-"}, cites=["SRC-I1-CARRIED"], equation="sum of BOM lines with group 'groundtest', pre-tax", output="bought_usd")
def groundtest(tax):
    return {"bought_usd": round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["group"] == "groundtest"), 2)}


kit.claim("CL-I1-SPEND-BASE", "BOM spend at order, baseline", calc="CALC-I1-SPEND", output="spend_base", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Re-run build_bom.py after re-pricing each line on the day of the order; compare with the order confirmations.")
kit.claim("CL-I1-SPEND-PESS", "BOM spend at order, pessimistic", calc="CALC-I1-SPEND", output="spend_pess", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Same lines at list price plus the DECISION section 9 adders; CL-I1-BRIDGE-DELTA must be 0.")
kit.claim("CL-I1-BRIDGE-DELTA", "Bottom-up minus R1 bridge (USD)", calc="CALC-I1-BRIDGE", output="delta_usd", unit="USD",
          limit=("<=", 0.02),
          how="Non-zero means a BOM line changed without the bridge table in build_bom.py bridge() being updated.")
kit.claim("CL-I1-RESERVE-PESS", "Pessimistic reserve at order", calc="CALC-I1-RESERVE", output="reserve_pess", unit="USD",
          limit=(">=", P + "requirements.crash_cost_usd"), verifies=["R-RESERVE", "R-BUDGET"],
          how="2 000 minus CL-I1-SPEND-PESS must be >= 309 (one class-S crash incl. tax). On the day: re-price every CARRY line.")
kit.claim("CL-I1-RESERVE-BASE", "Baseline reserve at order", calc="CALC-I1-RESERVE", output="reserve_base", unit="USD",
          limit=(">=", P + "requirements.crash_reserve_planned_usd"), verifies=["R-RESERVE"],
          how="2 000 minus CL-I1-SPEND-BASE must be >= 150 (planned reserve, P2).")

kit.claim("CL-I1-RESERVE-PESS-ALLIN", "Pessimistic reserve if the gated lines X07 and X08 were also bought", calc="CALC-I1-ALLIN", output="reserve_pess_allin", unit="USD",
          how="2 000 minus the all-in pessimistic spend. Information, not a gate: the committed order holds >= 309 by deferring X07 and X08 until their gate passes. Below 309 means every gated line cannot be bought on pessimistic numbers.")
kit.claim("CL-I1-GROUNDTEST-BOUGHT", "New bought ground-test purchase, pre-tax (USD)", calc="CALC-I1-GROUNDTEST", output="bought_usd", unit="USD",
          limit=("<=", 20.0),
          how="D-39: ground-test equipment is borrowed from Jacobs Hall first; at most $20 is bought (G12). The 20 kgf cell kit G06 ($17.97) was already in the baseline.")

kit.test("T-I1-CONNECTOR-LEADS", "Confirm the pack connector and lead gauge before ordering", verifies=["CL-I1-SPEND-PESS"], state="planned",
         procedure="Before the pack order: read the listing photos or ask the vendor for lead gauge (needs >= 10 AWG, F1 CL-F1-PACKLEAD-RISE) and connector (XT60). The 2026-11-09 listing says 12 AWG, 680 g: do not order it. On arrival: measure the lead conductor with calipers, weigh both packs.")
kit.test("T-I1-LISTINGS", "Re-read the six listings before each order", verifies=["CL-I1-SPEND-PESS", "CL-I1-RESERVE-PESS"], state="planned",
         procedure="On 20 Nov and 15 Dec open: LANRC ASIN B0D2HS4Y4J, SunnySky X3108S, Ovonic 2-pack (connector, lead gauge, mass, price), Aloft tube, "
                   "APC 11x5.5MR/11x4.5MR; log price and stock in team/I1/listing_log.csv; re-run build_bom.py.")
kit.test("T-I1-BORROW", "Jacobs Hall confirms the H1 rig loan in writing", verifies=["CL-I1-GROUNDTEST-BOUGHT"], state="planned",
         procedure="Before 20 Nov ask Jacobs Hall staff, by email, to lend the items in ORDER-PLAN.md 'Borrow list' for 25 Nov - 8 Dec (stand campaign) "
                   "and the build-end weigh-in; file the reply in team/I1/borrow_confirmation.txt. A refusal moves the item to a BOM line (price in the table).")
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
            w.writerow([l["id"], l["group"], l["part"], l["item"], l["vendor"], l["pn"], l["url"], l["order"] + (f" (GATED {l['gate']})" if l["gate"] else ""), l["fit"], l["spare"], q,
                        f"{l['unit']:.2f}", f"{l['pess']:.2f}", f"{ext:.2f}", f"{tax:.2f}", f"{ext + tax:.2f}", l["lead"],
                        "YES" if l["long"] else "", l["status"], l["seen"], l["note"]])
        w.writerow([])
        w.writerow(["TOTAL", "", "", "Goods pre-tax, baseline", "", "", "", "", "", "", "", "", "", f"{m['goods_base']:.2f}"])
        w.writerow(["TOTAL", "", "", f"Sales tax 10.25 %", "", "", "", "", "", "", "", "", "", f"{m['tax_base']:.2f}"])
        w.writerow(["TOTAL", "", "", "Shipping, all vendors (ESTIMATE)", "", "", "", "", "", "", "", "", "", f"{SHIP_BASE:.2f}"])
        w.writerow(["TOTAL", "", "", "FAA registration (not taxed)", "", "", "", "", "", "", "", "", "", f"{FAA_FEE:.2f}"])
        w.writerow(["TOTAL", "", "", "Lines marked GATED are excluded from every total below", "", "", "", "", "", "", "", "", "", ""])
        w.writerow(["TOTAL", "", "", "Spend baseline", "", "", "", "", "", "", "", "", "", f"{m['spend_base']:.2f}"])
        w.writerow(["TOTAL", "", "", "Spend pessimistic (list prices + adders 57)", "", "", "", "", "", "", "", "", "", f"{m['spend_pess']:.2f}"])
        w.writerow(["TOTAL", "", "", "Reserve baseline / pessimistic", "", "", "", "", "", "", "", "", "", f"{rb:.2f} / {rp:.2f}"])
        w.writerow(["TOTAL", "", "", "Reserve baseline / pessimistic if gated lines X07, X08 were also bought", "", "", "", "", "", "", "", "", "",
                    f"{reserve_calc(budget, m['spend_base_allin']):.2f} / {reserve_calc(budget, m['spend_pess_allin']):.2f}"])
    by = {}
    for l in L:
        if l["gate"]:
            continue
        by.setdefault(l["vendor"], 0.0)
        by[l["vendor"]] += (l["fit"] + l["spare"]) * l["unit"]
    out = dict(money=m, reserve_pess=rp, reserve_base=rb, bridge=dict(value=bridge_val, deltas=deltas), vendors={k: round(v, 2) for k, v in by.items()},
               by_order={o: round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["order"] == o and not l["gate"]), 2) for o in ("EARLY", "DEC", "LOCAL")},
               reserve_pess_allin=reserve_calc(budget, m["spend_pess_allin"]), reserve_base_allin=reserve_calc(budget, m["spend_base_allin"]),
               gated={g["id"]: round(gated_net(g["id"]) * (1 + tax_rate), 2) for g in GATED})
    (HERE / "bom_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    kit.write()
    print(json.dumps(write_outputs(), indent=1))
