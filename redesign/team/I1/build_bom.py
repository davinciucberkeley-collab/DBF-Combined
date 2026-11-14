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
# R5 (2026-11-13, CDR-10 / CDR-BT-03 lever L3): shipping is counted per paid shipment instead of one flat sum.
# Rate = the old flat estimate spread over the 14 vendors it assumed (ORDER-PLAN R4 "about 14 vendors"; CDR-BT-03 L3:
# $150 / 14 = $10.71 pessimistic). A shipment = one (vendor, order wave) pair of mail-order lines; LOCAL = store pick-up,
# no shipping. Amazon is counted as paid (no free-shipping threshold read), so the estimate stays conservative.
SHIP_PER_BASE, SHIP_PER_PESS = SHIP_BASE / 14, (SHIP_BASE + SHIP_ADV) / 14
# R5: import duty + carrier brokerage on the pack parcel from Germany (CDR-BT-06: US de minimis ended 29 Aug 2025; UPS
# brokerage minimum $14, DHL quoted $17.50; duty rate on the cells "-"). Reviewer EST $20-45; not sales-taxed. Falls to 0
# if a US-stock pack is found (decision B10).
DUTY_BASE, DUTY_PESS = 20.00, 45.00
TAX_NOTE = "Berkeley 10.25 % (CDTFA 2026-10-01); Measure V (+0.5 %) leading on 2026-11-09, effective date unknown"

L = []


def line(id, group, item, vendor, pn, order, fit, spare, unit, pess=None, status="CARRY", seen="2026-11-01",
         lead=5, long=False, url="", note="", part="", taxable=True, gate=""):
    L.append(dict(gate=gate, id=id, group=group, item=item, vendor=vendor, pn=pn, order=order, fit=fit, spare=spare, unit=unit,
                  pess=unit if pess is None else pess, status=status, seen=seen, lead=lead, long=long, url=url,
                  note=note, part=part, taxable=taxable))


# R5: items the build or test documents call for whose price could not be read on any vendor page on 2026-11-13.
# They are listed in BOM.csv with price "-" and are NOT in any total; every reserve figure is quoted "plus N unpriced lines".
UNPRICED = []


def unpriced(id, group, item, vendor, order, qty, note, gate="", covers=""):
    UNPRICED.append(dict(id=id, group=group, item=item, vendor=vendor, order=order, qty=qty, note=note, gate=gate, covers=covers))


# --- propulsion (E1: subsystems/propulsion/parts.csv)
line("B01", "propulsion", "Motor SunnySky X3108S KV900", "SunnySky USA", "X3108S, KV900 variant", "EARLY", 4, 1, 24.99,
     status="CHK", seen="2026-11-09", lead=5, url="https://sunnyskyusa.com/products/sunnysky-x3108s-motors", part="PRP-001",
     note="search snippet of the vendor page: $24.99, 60 in stock; page itself 429 on fetch. Measure bolt pattern and lead length on arrival")
line("B02", "propulsion", "ESC LANRC BLHeli_S 45 A 4-pack (4 fitted; the 4 spares are line B08)", "Amazon", "ASIN B0D2HS4Y4J", "EARLY", 1, 0, 30.00,
     status="CARRY", seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0D2HS4Y4J", part="PRP-002",
     note="UNVERIFIED: Amazon 503 on 2026-11-09, search finds no US LANRC 4-pack page; no US listing found again on 2026-11-13 (CDR-BT-07). Check the live page (title, 45 A, 4-pack, price) before the order. Fallback Holybro Tekko32 F4 45A AM32 $22.50 each (backorder to Dec 2026): +$60 for 4")
line("B08", "propulsion", "ESC LANRC 45 A 4-pack, second pack = 4 spare ESCs (R-CRASH-REPAIR; agrees with propulsion parts.csv PRP-002 'buy 2 packs (4 spare)')", "Amazon", "ASIN B0D2HS4Y4J", "DEC", 0, 1, 30.00,
     status="CARRY", seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0D2HS4Y4J", part="PRP-002",
     note="R5 / D-130 (CDR-09, CDR-BT-13): was gated X01. Bought in the December order only after T-F2-DSHOT passes on the first pack (Bluejay, bdshot error <= 1 % over 0.7 m, 8 Dec); if it fails, this line becomes 5 x Tekko32 F4 45A (+$52.50 pre-tax, CDR-09 REVIEWER EST) and both packs change")
line("B03", "propulsion", "Prop APC 11x5.5MR / 11x5.5MRP (LP11055MR / MRP): 2 + 2 fitted, 8 spare (4 + 4)", "APC", "LP11055MR, LP11055MRP", "EARLY", 4, 8, 3.83,
     status="CHK", seen="2026-11-13", lead=5, url="https://www.apcprop.com/product/11x5-5mr/", part="PRP-003",
     note="vendor page fetched 2026-11-09 and re-confirmed by CDR-BT section 4 on 2026-11-13: $3.83, 0.60 oz; stock not stated on the page. R5 / D-130: spares 4 -> 8 so the BOM holds the 8 spare props R-CRASH-REPAIR names (CDR-BT-13)")
line("B04", "propulsion", "Prop APC 11x4.5MR / 11x4.5MRP (LP11045MR, LP11045MRP) for the thrust-stand A/B", "APC", "LP11045MR, LP11045MRP", "EARLY", 4, 0, 3.83,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.apcprop.com/product/11x4-5mr/", part="PRP-003",
     note="2 MR + 2 MRP (CR-E1-12); $3.83 per SRC-APC-11X45MR, checked 2026-11-09")
line("B05", "propulsion", "Prop adapter ring APC LPAR06E-type (centres the hub on the M6 post)", "APC", "LPAR06E", "EARLY", 4, 8, 0.50,
     status="EST", seen="2026-11-09", lead=5, url="https://www.apcprop.com/", part="PRP-004", note="price ESTIMATE as cost.csv")
line("B07", "propulsion", "Motor screw M3x8 SHCS ISO 4762 A2 (16 fitted + 4 spare)", "Amazon", "M3-0.5 x 8 socket head A2", "EARLY", 16, 4, 0.10,
     status="CARRY", seen="2026-11-01", lead=5, url="https://www.boltdepot.com/", part="PRP-005",
     note="per-piece price from the old design's F01; the hardware kit may already hold M3x8. R5 (lever L3): bought in the Amazon cart (a 50-100 pack), not from Bolt Depot (one fewer shipment)")
line("B09", "propulsion", "Prop APC 11x7E (LP11070E) x2 for the stand A/B against 11x5.5MR (CDR-04, CDR-AE-08; chair condition A5)", "APC", "LP11070E", "EARLY", 2, 0, 4.17,
     status="CHK", seen="2026-11-13", lead=5, url="https://www.apcprop.com/product/11x7e/", part="PRP-003",
     note="R5: vendor page fetched 2026-11-13, $4.17. Same APC cart as B03/B04. The pusher 11x7EP pair is line U01 (apcprop.com/product/11x7ep/ returned 404 on 2026-11-13: no price, not in the totals)")
# --- power
line("P01", "power", "LiPo Ovonic 4S 6500 mAh 120C hard case, EC5, 2-pack (2 flight packs, no packs 3-4, no 4S 4000)", "Ampow / OVONIC (same SKU)", "2-Pack Ovonic 14.8V 120C 4S 6500mAh Hardcase LiPo, EC5 plug, 1/8 scale RC car", "EARLY", 1, 0, 114.48, pess=131.43,
     status="EST", seen="2026-11-10", lead=14, long=True, url="https://www.ampow.com/products/2-pack-ovonic-4s-6500mah-120c-lipo-hardcase-ec5-1-8-rc-car", part="PWR-001",
     note="D-64 / CR-E2-24. NO USD price found: ampow page 429, us.ovonicshop.com has no EC5 hard-case listing. Baseline = EUR 98.69 (E2, EU page) x 1.16 = $114.48; pessimistic = EUR 113.30 (ampow el-gb page, in stock, 2026-11-10 search) x 1.16 = $131.43. Ampow ships from Germany: lead about 14 days (long). Two checks BEFORE paying: (a) 10 AWG discharge leads confirmed by the seller (12 AWG: stop, tell E2 and F1), (b) EC5 / 4S / 6500 / hard case / 2 packs in the cart. Listed 551 +/- 5 g, 135 x 46 x 49 mm. The 130C XT60 SKU (680 g, 12 AWG) is NOT bought. Fallback if unavailable: Tattu 4S 6750 25C XT90 605 g (A1 must accept the mass)")
# --- avionics (F3)
line("A01", "avionics", "Flight controller CoreWing F405 Wing APP V2 (FC + PDB 'stack')", "RaceDayQuads", "CoreWing F405 Wing V2 flight controller stack", "EARLY", 1, 0, 69.49,
     status="CHK", seen="2026-11-13", lead=5, url="https://www.racedayquads.com/products/corewing-f405-wing-v2-flight-controller-stack", part="AVN-001",
     note="WB-01 / BR-05 / D-74: place this cart FIRST in the early order and run subsystems/power/BOARD-CHECK.md the day it arrives, before D2 freezes the pod CAD; check the PDB ('PDB Board PLUS') and the 470 uF cap are in the box (the RMRC 'included' list names neither; the CoreWing manual lists both). CR-F3-06 / CR-A1-39: order V2 now (the Mini lacks bdshot). R5 (CDR-BT-22, lever L3): the ReadyMadeRC page (product 87195) returned 'Product not found' on 2026-11-13, so the line moves to the RaceDayQuads cart with A02 and R01: RDQ 'CoreWing F405 Wing V2 Flight Controller Stack' $69.49 (search snippet of the vendor page, 2026-11-13; page 429); confirm the stack holds the FC and the PDB board. Fallback SpeedyBee F405 Wing APP $47.99 (RaceDayQuads, stock unverified)")
line("A02", "avionics", "GPS + compass HGLRC M100-5883", "RaceDayQuads", "M100-5883", "EARLY", 1, 0, 20.49,
     seen="2026-10-13", lead=5, url="https://www.racedayquads.com/products/hglrc-m100-5883-gps-module-10th-gen", part="AVN-002")
line("A03", "avionics", "Receiver RadioMaster RP3 V2 ELRS", "RadioMaster", "RP3 V2 ELRS 2.4 GHz, FCC variant", "EARLY", 1, 0, 19.99,
     status="CHK", seen="2026-11-09", lead=5, url="https://www.radiomasterrc.com/products/rp3-expresslrs-2-4ghz-nano-receiver", part="AVN-003",
     note="CR-F5-06: select the FCC variant, NOT LBT (LBT caps 100 mW). Page fetched 2026-11-09: $19.99 sale, FCC and LBT both listed at $19.99 and available")
line("A04", "avionics", "Airspeed sensor RMRC digital (MS4525DO) + pitot tube", "ReadyMadeRC", "RMRC digital airspeed sensor MS4525DO + pitot", "DEC", 1, 0, 59.99,
     seen="2026-11-09", lead=10, url="https://www.readymaderc.com/", part="AVN-004",
     note="CR-F3-06: MS4525DO replaces the MS5525 line (same $59.99). Needed for the fixed-wing tune (January), not for the twin. Lever if the reserve needs help (+$66.14 incl. tax, DECISION 5.1)")
line("A05", "avionics", "microSD card 16-32 GB (FC log)", "Amazon", "SanDisk class, 16-32 GB", "EARLY", 1, 0, 6.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="AVN-007", note="CR-F3-06: team stock first. R5 / D-130 (lever L2, CDR-BT-03): held behind gate X13 (owned-or-borrowed walk, CDR-11, 19 Nov); bought only if no team member has a 16-32 GB card. Part id corrected AVN-006 -> AVN-007 (CDR-BT-21)")
line("A06", "avionics", "2 x 150 mm U.FL / IPEX1 2.4 GHz T-antenna (dipole) for the RP3 V2 (D-72)", "Amazon", "2.4 GHz 150 mm U.FL T antenna, pair", "EARLY", 1, 0, 6.00,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="AVN-003",
     note="CR-F5-11 / CR-F3-15: stock 65 mm leads do not reach the carbon-free zone. F5 estimate $6, no listing fetched. U.FL plug-in, no iron needed. Check IPEX1 vs IPEX4 on the RP3 V2")
line("A07", "avionics", "FC isolation set: alpha-gel 5 mm sheet (4 cubes), 1 mm foam tape, 10 mm hook-and-loop", "Amazon", "alpha-gel sheet + VHB-class tape", "DEC", 1, 0, 10.00,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="AVN-006",
     note="F3 AVN-006 prices $3 and CR-F3-06 says shop consumables, but nothing is owned and gel sheets sell for about $10: carried at $10 (+$7 over F3). Drop if Jacobs stock is confirmed")
# --- mechanisms (D6)
line("M01", "mechanisms", "Elevon servo Savox SH-0255MG+ (dealer SKU SH-0255MGP) 12 mm micro, 3.9 kgf-cm at 6 V (2 fitted; the spare is gated X02)", "AMain Hobbies", "SH-0255MGP", "EARLY", 2, 0, 34.99, pess=41.99,
     status="CHK", seen="2026-11-13", lead=7, url="https://amainhobbies.com/savox-sh0255mgp-digital-metal-gear-micro-servo-sav-sh-0255mgp/p1441652", part="MEC-001",
     note="CR-D6-02 / CR-A1-52: replaces the ES3005HV placeholder (42 g, does not fit the 12 mm pocket). $41.99 from D6 (SRC-D6-SH0255-PRICE). R5 (CDR-BT-22): the old AMain link p183344 is dead (404); the live AMain page p1441652 was fetched 2026-11-13: $34.99, back-ordered (baseline). Pessimistic $41.99 = Hobby Etc. https://store.hobbyetc.com/parts/view/161558 (search snippet 2026-11-13), the price four US dealers list (CDR-BT section 4). Moved to the 20 Nov order (single-source, mixed stock; lets D6 caliper the case before MEC-008 prints); buy from whichever dealer shows stock that day. D6 confirms MG+ and MGP share the case")
# --- airframe
line("W01", "airframe", "XPS FOAMULAR NGX F-250 2 in x 4 x 8 ft (about 6 wing cores)", "Home Depot El Cerrito", "F-250 2 in", "LOCAL", 1, 0, 59.97,
     seen="2026-10-01", lead=0, url="https://www.homedepot.com/", part="WNG-001", note="pick-up; check the sheet is flat and unbroken")
line("W02", "airframe", "Foam board 20x30 in, 10 single sheets, one brand (fins, pod shell, first foam-board twin)", "Dollar Tree (store)", "Readi-Board white 20 x 30 in, item 809955", "LOCAL", 10, 0, 1.25,
     status="EST", seen="2026-11-13", lead=0, url="https://www.dollartree.com/readi-board-white-foam-boards/809955", part="FIN-001",
     note="R5 / D-130 (lever L1, CDR-BT-03): replaces the $35.92 Amazon 10-pack. $1.25 per sheet from the dollartree.com listing (search snippet 2026-11-13; online it sells only by the 25-sheet case, the single-sheet shelf price is not confirmed: EST). Buy all 10 from one store on one day so the board is one brand and one batch (MF-21); weigh one sheet against fin.board areal mass before cutting")
line("W03", "airframe", "Carbon tube 22x20x1000 mm matte, US stock (one for C4's bend test, then the spare)", "Aloft Hobbies", "22 x 20 x 1000mm MW carbon tubing matte", "EARLY", 1, 0, 24.00,
     status="CHK", seen="2026-11-09", lead=5, url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish", part="WNG-002",
     note="CR-J1-07. Vendor page: $24.00, in stock, shipping at checkout; mandrel-wound, layup unstated. Weigh and bend-test on arrival")
line("W04", "airframe", "Carbon tube 22x20x1000 mm matte (spar + 2 motor tubes cut from one + 0 spare), order after the bend test", "Aloft Hobbies", "same SKU as W03", "DEC", 2, 0, 24.00, pess=28.32,
     status="CHK", seen="2026-11-09", lead=5, url="https://alofthobbies.com/products/22-x-20-x-1000mm-mw-carbon-tubing-matte-finish", part="WNG-002",
     note="baseline: Aloft $24 if the W03 bend test passes. Pessimistic and fallback: the BOM's overseas Amazon tube $28.32 (cost.csv, ~14 days: order first, 15 Dec at the latest)")
line("W05", "airframe", "PETG filament 1 kg (Ambrosia)", "West3D", "PETG 1 kg", "EARLY", 1, 0, 20.99,
     seen="2026-10-01", lead=5, url="https://west3d.com/", part="FIN-008",
     note="non-structural prints in Jacobs' free PLA. R5 (chair condition A4): moved to the 20 Nov order so T-C6-LAP-PETG and T-C6-STRIP-ANCHOR coupons print before the December order. Part id FIN-002 (a CF tube) corrected to the PETG collar FIN-008; FIN-013 / MEC-013 (8 g) print from this spool (CDR-BT-21)")
line("W06", "airframe", "Packing tape Scotch Heavy Duty, 6 rolls", "Amazon", "ASIN B000087KUA", "EARLY", 1, 0, 19.98,
     seen="2026-10-01", lead=4, url="https://www.amazon.com/dp/B000087KUA", part="WNG-003")
line("W07", "airframe", "Foam-safe glue (UHU Por / Gorilla clear)", "Amazon", "ESTIMATE vendor", "EARLY", 1, 0, 12.99,
     status="EST", seen="2026-11-01", lead=4, url="https://www.amazon.com/", part="WNG-004")
# --- R5 consumables the build, battery and test documents call for (CDR-BT-05, -19; chair A5). Prices read 2026-11-13
#     (search snippets of the vendor pages unless "page"). Store lines are LOCAL (no shipping).
line("W09", "airframe", "Filament (strapping) tape Scotch 893, 3/4 in x 60 yd (TPU cap wraps, E-GER-21/22; hinge back-up)", "Staples (store)", "Scotch 893 3/4 in", "LOCAL", 1, 0, 9.29, pess=17.99,
     status="CHK", seen="2026-11-13", lead=0, url="https://www.schoolspecialty.com/strapping-tape-040713", part="GER-007",
     note="R5 (CDR-BT-05): baseline Staples $9.29 (snippet 2026-11-13, shown out of stock); pessimistic School Specialty $17.99 (snippet 2026-11-13, URL)")
line("G16", "airframe", "Spray adhesive 3M Super 77, 13.8 oz (fin board lamination D-26; FIN-106 'shop stock', nothing owned)", "Home Depot El Cerrito", "3M 77-DSC", "LOCAL", 1, 0, 13.01, pess=13.28,
     status="CHK", seen="2026-11-13", lead=0, url="https://www.homedepot.com/p/3M-13-8-oz-Super-77-Multipurpose-Spray-Adhesive-77-DSC/316334789", part="FIN-106",
     note="R5 (CDR-BT-05): $13.01 product-page snippet, $13.28 on a category page (pessimistic), both 2026-11-13. Spray in the Jacobs spray booth (ORDER-PLAN pass table)")
line("G17", "ground", "LiPo sand bucket: play sand 50 lb (Tractor Supply) + 5 gal bucket (Home Depot 05GLHD2)", "Tractor Supply / Home Depot (store)", "play sand 50 lb; Homer bucket 05GLHD2", "LOCAL", 1, 0, 13.97,
     status="CHK", seen="2026-11-13", lead=0, url="https://homedepot.com/p/The-Home-Depot-5-Gallon-Orange-Homer-Bucket-05GLHD2/100087613", part="GND-004",
     note="R5 (CDR-BT-05, CR-H3-04): sand $8.99 (tractorsupply.com snippet 2026-11-13; the Home Depot play-sand snippet was garbled) + bucket $4.98 (Home Depot snippet 2026-11-13). H3 BATTERY-PROCEDURE: 5 m from the pilot box. Also the hover-tether ballast anchor if stakes cannot be driven")
line("G18", "groundtest", "Hover tether: 550 paracord 100 ft + 12 steel U-stakes 0.4 x 12 in (two slack lines from POD-007 to stakes 3 m apart, 1.5 m height limit)", "Tractor Supply / Home Depot (store)", "550 paracord 100 ft; Wellco SRU0412P12S", "LOCAL", 1, 0, 39.58,
     status="CHK", seen="2026-11-13", lead=0, url="https://www.homedepot.com/p/Wellco-0-4-in-x-12-in-Rebar-Stakes-U-Hook-Extra-Heavy-Duty-Garden-Stake-Steel-Stakes-Tent-Stakes-12-Pack-SRU0412P12S/326673693", part="POD-007",
     note="R5 (CDR-BT-19, CDR-30): cord $16.99 (tractorsupply.com paracord snippet 2026-11-13; 5/32 in = 4 mm, not the 3 mm the review named) + stakes 12-pack $22.59 (Home Depot snippet 2026-11-13). Reviewer EST was $10; no 2-stake pack was priced. H2 writes the tether card")
line("G14", "groundtest", "Handheld anemometer BTMETER BT-100 (card 1d, R-WIND-MEASURE, three RFS mornings by 7 Dec)", "eBay (BTMETER BT-100)", "BTMETER BT-100", "EARLY", 1, 0, 17.49,
     status="CHK", seen="2026-11-13", lead=5, url="https://www.weatherrepublic.com/collections/kestrel/products/kestrel-1000-wind-meter", part="GND-013",
     pess=89.00, note="R5 (CDR-BT-04, chair A5, CR-H3-02): BT-100 $17.49 on eBay (snippet 2026-11-13; resellers list the same unit at $64-94, search 2026-11-13). Pessimistic: Kestrel 1000 $89.00 (Weather Republic snippet 2026-11-13, URL). D-131: gated X14, H3 borrows one first (UC, team); bought by 24 Nov if not, for the three RFS mornings by 7 Dec")
# --- hardware
line("H01", "hardware", "Harness parts (F2 parts.csv HRN-103..106, 108, 109): 26 AWG servo extension 2 m $5, 28 AWG 3 colours $7, JR/Futaba connector kit $7, JST-GH housings + pigtails $12, cable ties $4, PET braid sleeve $6", "Amazon / DigiKey", "assorted, see F2 parts.csv", "EARLY", 1, 0, 41.00,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="HRN-103",
     note="F2 prices all EST UNVERIFIED; one line = six purchases. 16 AWG, 20 AWG and heat-shrink are F03, F04, F09. JST-GH from DigiKey adds shipping: use pre-crimped pigtails from Amazon if the cart allows")
line("H02", "hardware", "Mechanisms hardware (D6 parts.csv): Du-Bro 2-56 rod + steel clevises $8, 1/8 in (3.18 mm) pultruded CF rod 1 m $5, CF tube 5 x 4 x 1000 mm $8, M2 x 6 self-tapping pan-head screws (servo covers MEC-011: 4 fitted + spares, pack of 20) $3", "Amazon / hobby shop", "Du-Bro 2-56, CF rod 1/8 in, CF tube 5x4, M2 x 6 self-tapping pan head A2", "DEC", 1, 0, 24.00,
     status="EST", seen="2026-11-10", lead=5, url="https://www.amazon.com/", part="MEC-005",
     note="CR-D6-02, CR-D6-16: the 1/8 in CF rod replaces the 3/32 in music wire ($5, was $3). Hinge tape is the wing tape (W06). M2 x 6: 2 per servo cover (E-MEC-03/04, -35/36, C6 FASTENERS-CAD); buy even if the servo box has screws (length unverified)")
line("H03", "hardware", "Charger-side XT60 pair for the AS150U charge adapter + 0.3 m 10 AWG stub", "Amazon", "XT60 pair, 10 AWG silicone", "DEC", 1, 0, 5.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-002",
     note="was $15 for the whole AS150U re-termination; F01 now buys the five AS150U pairs, so only the charger-side XT60 and a short 10 AWG stub remain")
line("H06", "hardware", "Amass XT30U male + female pairs, 10-pair pack (4 fitted: one per ESC pair at the pod side exits, WB-03; rest spares)", "Amazon", "Amass XT30U (genuine Amass, 2-pin, 20 A)", "EARLY", 1, 0, 9.99,
     status="EST", seen="2026-11-11", lead=4, url="https://www.amazon.com/", part="HRN-113",
     note="D-74 / WB-03: pod-wing power disconnect, harness SPEC.md 'Pod-wing power disconnect'. Price EST (10-pair packs list about $8-12); buy genuine Amass (1.2 mOhm contact resistance, 20 A on 16 AWG per the Amass manual), not unbranded")
line("H07", "hardware", "Board-link ribbon: male pin-header strip 1 x 40 + 10-way 28 AWG ribbon 0.3 m (HRN-114, W-PMOD, case S)", "DigiKey / Amazon", "any; pitch per power BOARD-CHECK.md step 4", "EARLY", 1, 0, 3.00,
     status="EST", seen="2026-11-13", lead=4, url="https://www.amazon.com/", part="HRN-114",
     note="D-89: the CAD now draws this ribbon and its header plugs (PDB top header, FC underside header); price from subsystems/harness/parts.csv HRN-114 (EST), was in the F2 parts list but on no BOM line. Buy after BOARD-CHECK step 4 gives the pitch (1.27 mm pitch: bought IDC ribbon instead)")
# --- power (F1, CR-F1-12), itemised from team/F1/POWER.md 'Bought items'
line("F01", "power", "Amass AS150U connector pair (male + female) x 5: aircraft, 2 packs, charge lead, spare", "Amazon", "Amass AS150U", "EARLY", 5, 0, 5.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.amazon.com/", part="PWR-003", note="F1 price EST $25 for 5; open the Amass sheet. Confirm the SKU is the anti-spark AS150U, not AS150")
line("F02", "power", "Silicone wire 10 AWG red + black 0.3 m each (PWR-104) + 8 AWG 0.1 m each (bus bars)", "Amazon", "10 AWG + 8 AWG silicone", "EARLY", 1, 0, 8.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-004", note="main pigtail; vendors sell 1 m minimum")
line("F03", "power", "Silicone wire 16 AWG red + black + yellow, 3 m each (HRN-101); second reel set for re-cuts", "Amazon", "BNTECHGO 16 AWG 252/0.08 silicone, 10 ft per colour", "EARLY", 1, 1, 14.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-101", note="ESC leads, F2 cuts. R5 (chair A5, CDR-EL-16): spare 0 -> 1 reel set for re-cut leads; no US price for BNTECHGO found on 2026-11-13, so $14 EST carried")
line("F04", "power", "Silicone wire 20 AWG red + black, 1 m each", "Amazon", "20 AWG silicone", "EARLY", 1, 0, 4.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-005", note="was UBEC feed + servo bus; D-74 deletes the UBEC, so this line is held behind gate X12 with F05 / F06")
line("F05", "power", "UBEC 6 V, 8 A class (Hobbywing type)", "Amazon", "UBEC 6 V 8 A", "EARLY", 1, 0, 18.00, status="EST", seen="2026-11-09", lead=5, url="https://www.readymaderc.com/", part="PWR-005", note="F1: datasheet UNVERIFIED; 13 g in A3's roll-up. D-74: gate X12, bought only if power/BOARD-CHECK.md step 7 fails; then buy a 4S-input part (the linked UBEC-8A is listed 2-3S)")
line("F06", "power", "Mini blade fuse 5 A x 3 + inline holder", "Amazon", "ATM mini fuse + holder", "EARLY", 1, 0, 6.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="UBEC feed protection; gate X12 with F05 (D-74)")
line("F07", "power", "Capacitor 680 uF 25 V low-ESR x 5", "Amazon", "680 uF 25 V", "EARLY", 1, 0, 5.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-008", note="one per ESC + 1 spare")
line("F10", "power", "Capacitor Panasonic FR 1000 uF 35 V low-ESR (EEU-FR1V102B) x 5, ripple and rating A/B on the stand (CDR-04, CDR-EL-05)", "DigiKey", "EEU-FR1V102B", "EARLY", 5, 0, 2.33,
     status="CHK", seen="2026-11-13", lead=4, url="https://www.digikey.sg/en/products/detail/panasonic-industry/EEU-FR1V102B/3072262", part="PWR-008",
     note="R5 (chair A5): $2.33 each, USD on digikey.sg (search snippet 2026-11-13; no US page hit). Separate DigiKey shipment counted. F1 decides 25 V vs 35 V after the GT-04 ripple run")
line("F08", "power", "FR4 1.6 mm 1 oz copper sheet 100 x 70 mm (bus board PWR-004 / PWR-105; 3 boards per sheet)", "Amazon", "FR4 single-sided copper clad", "EARLY", 1, 0, 3.00, status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="PWR-105", note="F1 replaced the bare PDB with a cut FR4 bus board; was $6")
line("F09", "power", "Adhesive-lined 3:1 heat-shrink assortment 2.4-9.5 mm (HRN-107; also F1 joints)", "Amazon", "Wirefy 3:1 assortment", "EARLY", 1, 0, 9.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="PWR-003", note="joints")
# --- fasteners and bonding (C6 kit, CR-C6-11; D3's fasteners are inside it)
line("C01", "hardware", "M3 steel A2 kit: SHCS M3x16 x6 (D3 pinch bolts), nyloc x8, washer x12 (C6 kit R4; M3x8 x20 is B07)", "Amazon", "ISO 4762 / 10511 / 7089 A2", "EARLY", 1, 0, 5.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.boltdepot.com/", part="FIN-101", note="C6 kit table; piece prices about $3 plus minimum-order rounding. M3x8 x20 is B07. M3 only. R5 (lever L3): Amazon cart, not Bolt Depot")
line("C06", "hardware", "M3 nylon PA66 set: socket-head M3x18 x11, M3x16 x3 + hex nut x3, 1.0 mm washer x6 (D-89b: the power board rests on them), 10 mm spacer OD 6 / ID 3.2 x6 (power frame, GPS mast, T-C6-NYLON-TORQUE)", "Amazon", "PA66 M3 socket-head assortment + spacers", "DEC", 1, 0, 7.00,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="PWR-101",
     note="CR-C6-30 / CR-C6-26: PA66 SOCKET heads (not pan) so the 2.5 mm hex key torques them at 0.08 N m; PWR-101..103 are inside this line. C6 kit total EST $26, here $28")
line("C02", "hardware", "M3 x 5.7 brass heat-set inserts x12 + M3 nylon washers / FC grommets x8", "Amazon", "Ruthex-class RX-M3x5.7", "DEC", 1, 0, 9.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="pod FC plate (4), PDB (4), spares (4)")
line("C03", "hardware", "Pultruded CF rod 2.5 mm x 1 m x 2 (one + spare): strip through-pins at 15 mm, 48 pins (D3 FIN-012 uses the same rod)", "Amazon", "CF rod 2.5 mm x 1000 mm", "DEC", 2, 0, 3.50,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="FIN-012",
     note="CR-C6-31 / CR-C6-35 / D-70: 2 mm to 2.5 mm; if 2.5 mm cannot be bought, 2 mm at 9 mm pitch. Not double counted with D3")
line("C04", "hardware", "Loctite 243 (10 ml) + paint pen (torque witness)", "Amazon", "Loctite 243", "DEC", 1, 0, 9.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="HRN-003", note="motor screws, tip threads only")
line("C05", "hardware", "Epoxy 30 min, 9 oz (Bob Smith Industries BSI-206 SlowCure 30 min)", "AMain Hobbies", "BSI-206", "EARLY", 1, 0, 22.99,
     status="CHK", seen="2026-11-13", lead=7, url="https://amainhobbies.com/bob-smith-industries-slowcure-30-minute-epoxy-9oz-bsi206/p37086", part="FIN-105",
     note="R5 (CDR-BT-05, chair A4): re-priced from the vendor page fetched 2026-11-13, $22.99 (back-ordered that day: buy from any dealer with stock). Replaces the $14 line whose link was a West System 105/206 kit ($82.35, fiberglasssupply.com snippet 2026-11-13). C6 / D3 FIN-105 bonds and coupons; in the 20 Nov order so T-C6-LAP-PETG runs before the December order. Same AMain cart as M01. Fillers are C07 and C08")
line("C07", "hardware", "Colloidal silica West System 406-2, 1.7 oz (fillet and bond thickener)", "Freeport Marine", "West System 406-2", "EARLY", 1, 0, 20.67,
     status="CHK", seen="2026-11-13", lead=5, url="https://freeportmarine.com/products/west-system-406-2-colloidal-silica-1-7-oz-filler", part="FIN-105",
     note="R5 (CDR-BT-05): $20.67 snippet 2026-11-13 (Ace $24.99). Was inside the old $14 C05 line")
line("C08", "hardware", "Glass microballoons (microspheres) #22-A, 1/2 gal (WNG-006 lip beads, FIN-105 fillets)", "Fibreglast", "Glass Microspheres 22", "EARLY", 1, 0, 17.95,
     status="CHK", seen="2026-11-13", lead=5, url="https://fibreglast.com/product/Glass_Microspheres_22", part="WNG-006",
     note="R5 (CDR-BT-05): $17.95 snippet 2026-11-13. Phenolic microballoons (BUILD-GUIDE consumables) are not bought: glass only")
# --- fin materials (D3, CR-D3-09; the tube is W04)
line("D01", "airframe", "Pultruded CF strip 10 x 2 x 1000 mm x 1 (4 braces, FIN-009)", "Aloft Hobbies", "CF strip 10x2", "DEC", 1, 0, 10.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-009", note="D3 est. about $10 per length")
line("D02", "airframe", "Pultruded CF strip 10 x 1 x 1000 mm x 3 (8 edge strips)", "Aloft Hobbies", "CF strip 10x1", "EARLY", 3, 0, 6.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-011", note="D3 est. about $6 per length, 3 m asked in CR-D3-09. R5 (chair A4): in the 20 Nov Aloft cart with W03 so T-C6-STRIP-ANCHOR runs before the December order")
line("D03", "airframe", "CF tube 20 x 18 x 1000 mm x 1 (D3 plugs 2 x 53 mm; C2's spar plugs if the same size)", "Aloft Hobbies", "20 x 18 x 1000 CF tube", "DEC", 1, 0, 20.00,
     status="EST", seen="2026-11-09", lead=5, url="https://alofthobbies.com/", part="FIN-006", note="D3 priced a $1 share; stock is sold by the metre. Ask C2 whether its six 36 mm plugs use this tube")
line("D07", "landing", "Brass tube 7/32 in OD K&S x 1 (cartridge bore cutter GER-013, shop tool, not flying)", "Amazon / hobby shop", "K&S 7/32 in round brass tube", "DEC", 1, 0, 3.00,
     status="EST", seen="2026-11-10", lead=5, url="https://www.ksmetals.com/", part="GER-013",
     note="CR-D5-27: 7/32 in replaces 1/4 in. D5 price UNVERIFIED, no listing fetched")
line("D04", "airframe", "10 mm hook-and-loop straps x 10 (ESC retention x4, spares)", "Amazon", "ONE-WRAP class", "DEC", 1, 0, 8.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="FIN-104", note="D3 FIN-104, 4 needed")
line("D05", "landing", "Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in", "Amazon", "neoprene 40A 1/16 in", "DEC", 1, 0, 12.00,
     status="EST", seen="2026-11-09", lead=5, url="https://www.mcmaster.com/", part="GER-006", note="CR-D5-10: D5 names McMaster-Carr (separate cart and shipping); an Amazon sheet is carried. Price UNVERIFIED; 4 pads + 12 spares per sheet")
line("D06", "pod", "Pack straps 20 x 300 mm hook-and-loop rubber-backed x2 + 2 EVA shims (POD-004)", "Amazon", "battery strap", "DEC", 1, 0, 7.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="POD-004", note="D2 POD-004")
line("W08", "airframe", "ASA filament 1 kg (motor mounts FIN-003, ESC pads FIN-007; D-42)", "West3D", "ASA 1 kg", "EARLY", 1, 0, 24.99,
     status="EST", seen="2026-11-09", lead=5, url="https://west3d.com/", part="FIN-003", note="NOT in CR-A1-39: D-42 prints mounts and pads in ASA and Jacobs Hall stocks PLA only, so a spool is bought. 4 x 12.66 + 4 x 1.86 g = 58 g; a 0.5 kg spool if offered. R5 (lever L3): in the 20 Nov West3D cart with W05 (one shipment; ASA prints on the enclosed printer booked by 11 Dec)")
# --- transport (D7 parts.csv replaces the old $60 plywood-box estimate H04)
line("T01", "transport", "Coroplast 4 mm 48 x 96 in x 2 (box as separate panels: sheet 1 floor + lid + 2 end walls + lid lips, sheet 2 front + aft walls; D7 nest)", "Home Depot El Cerrito", "Coroplast CP4896S 4 mm", "LOCAL", 2, 0, 37.98,
     status="CHK", seen="2026-11-11", lead=0, url="https://www.homedepot.com/p/Coroplast-48-in-x-96-in-x-0-157-in-White-Corrugated-Plastic-Sheet-CP4896S/205351385", part="TRN-001",
     note="R5 / D-134 (CDR-24): re-priced from $15 EST to $37.98 per sheet, the CP4896S search snippet of 2026-11-11 (LINKS-CHECK); on 2026-11-13 the single-sheet page showed no price and the 10-pack WC4896-10 read $302.96 ($30.30 a sheet). Two sheets hold the 1.25 x 0.56 x 0.54 m box as separate panels (subsystems/transport/SPEC.md 'Panel nest'); a third sheet is not needed")
line("T02", "transport", "LSE double-sided tape, 1 roll (3M 300LSE class): panel corners, column bases (E-TRN-01..05)", "Home Depot El Cerrito", "3M 300LSE class", "LOCAL", 1, 0, 12.00, pess=68.34,
     status="EST", seen="2026-11-11", lead=0, url="https://www.pelicansalessupply.com/products/3m-adhesive-transfer-tape-3-4-wide-60-yd-series-9472le", part="TRN-101",
     note="D7 EST $12 baseline. R5 (CDR-24): pessimistic $68.34 = the only page price read, 3M 9472LE 3/4 in x 60 yd (LINKS-CHECK snippet 2026-11-11); a small consumer roll was not priced. Separate box panels are joined at the corners with this tape + hot-melt + the 8 corner protectors (SPEC 'Panel nest')")
line("T03", "transport", "Cam-buckle straps x2 + strap handles x3", "Home Depot El Cerrito", "25 mm tie-down, luggage handle", "LOCAL", 1, 0, 24.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-006", note="D7 TRN-006-A/B 2 x 6 + TRN-007 3 x 4")
line("T04", "transport", "Field pouch + 10 mm prop spanner (D-40) + M3x16 / nyloc / fender washers x6", "Home Depot El Cerrito", "pouch, 10 mm spanner", "LOCAL", 1, 0, 13.80, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-008", note="D7 TRN-008 8 + TRN-106 4 + TRN-102 1.80")
line("T05", "transport", "Landing mat 0.8 x 0.8 m: 3 mm birch ply (Jacobs stock) + 1.5 mm rubber sheet, cloth-tape hinge (TRN-104, CR-D7-17)", "Home Depot El Cerrito", "rubber sheet 1.5 mm + cloth tape", "LOCAL", 1, 0, 25.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-104", note="CR-D7-17 settles CR-I1-18: one rubber-on-ply mat (mu 0.7, C5). D7 estimate $25; ply is free if Jacobs stock is confirmed")
line("T06", "transport", "PE foam plank 2 in + 1 in (cradle columns, lid pillars)", "Home Depot El Cerrito", "PE foam 1.7 pcf", "LOCAL", 1, 0, 18.00, status="EST", seen="2026-11-09", lead=0, url="https://www.homedepot.com/", part="TRN-002", note="D7 TRN-002-L/R 12, TRN-004-L/R 6; XPS offcuts for the tray")
line("T07", "transport", "Field tote about 0.45 x 0.35 x 0.25 m (TX, landing-spares box, flight card, anemometer) (TRN-107)", "Home Depot El Cerrito", "tote", "LOCAL", 1, 0, 8.00, status="EST", seen="2026-11-10", lead=0, url="https://www.homedepot.com/", part="TRN-107", note="CR-D7-17")
line("H05", "hardware", "Hot-wire bow/jig + airfoil template stock", "Home Depot El Cerrito", "-", "LOCAL", 1, 0, 15.00,
     status="EST", seen="2026-11-09", lead=0, url="", part="WNG-005", note="K01 REVIEW section 2")
# --- avionics ground-side / radio
line("R01", "avionics", "Transmitter RadioMaster Pocket Crush ELRS", "RaceDayQuads", "Pocket Crush, ELRS / FCC variant", "EARLY", 1, 0, 84.49,
     status="CHK", seen="2026-11-13", lead=5, url="https://www.racedayquads.com/products/radiomaster-pocket-crush-rc-transmitter-elrs-2-4ghz-choose-your-color", part="GND-001",
     note="CR-F5-06: choose 'ELRS / FCC'. R5 (CDR-BT-07, chair A1): carried at $84.49 = RaceDayQuads (search snippet 2026-11-13; page 429); US dealers $77.99-95.99 (Pyrodrone $95.99 snippet 2026-11-13); the radiomasterrc.com $64.99 of 2026-11-09 is not used. In the RDQ cart with A01 and A02 (lever L3). F5 confirms 25-250 mW on arrival. Batteries not included")
line("R02", "avionics", "18650 cells, 2-pack for the Pocket (not included)", "RaceDayQuads", "Lumenier 18650 2-pack", "EARLY", 1, 0, 24.49,
     seen="2026-11-09", lead=5, url="https://www.getfpv.com/", part="GND-001", note="R5 (lever L3): moved to the RaceDayQuads cart with R01 (RDQ 18650 listing not read: if RDQ has none, GetFPV Lumenier 2-pack $24.49 as before, +1 shipment). K09 REVIEW section 6; the Pocket does not run on USB alone. RadioMaster says batteries cannot ship separately from a radio order: if GetFPV cannot ship them, add RadioMaster cells to the same order")
# --- ground equipment
line("G01", "ground", "Charger HTRC C150 150 W AC", "Amazon", "ASIN B0H4QLJYHY", "EARLY", 1, 0, 56.99, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/dp/B0H4QLJYHY", part="GND-002", note="E2: read the manual for max charge current and IR function on arrival")
line("G02", "ground", "LiPo bag x2", "RaceDayQuads", "LiPo safe bag", "EARLY", 2, 0, 9.99, seen="2026-11-01", lead=5, url="https://pyrodrone.com/", part="GND-003",
     note="R5 (lever L3): moved to the RaceDayQuads cart (RDQ bag listing not read; the $9.99 is the old Pyrodrone carry; if RDQ has none, Pyrodrone +1 shipment)")
line("G03", "ground", "Ammo can (Harbor Freight 63750)", "Harbor Freight", "63750", "LOCAL", 1, 0, 19.99, seen="2026-11-01", lead=0,
     url="https://www.harborfreight.com/50-caliber-metal-ammo-can-63750.html", part="GND-004")
line("G04", "ground", "Watt meter 150 A", "Amazon", "ASIN B0F13JWDFV", "EARLY", 1, 0, 12.99, seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0F13JWDFV", part="GND-005")
line("G05", "ground", "IR thermometer", "Amazon", "ASIN B0BN317X6Z", "EARLY", 1, 0, 8.98, seen="2026-11-01", lead=4, url="https://www.amazon.com/dp/B0BN317X6Z", part="GND-006")
line("G06", "ground", "Thrust stand: 20 kg load cell + HX711 + Nano", "Amazon", "kit (budget-energy-test.md)", "EARLY", 1, 0, 17.97, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/", part="GND-007", note="H1: the stand must take >= 2.5 kgf")
line("G10", "ground", "Flux + desoldering wick (fallback only: the Electronics Lab stations supply solder; flux and wick are not listed)", "Amazon", "ESTIMATE", "EARLY", 1, 0, 15.00, status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-010",
     note="2026-11-13: the soldering iron, multimeter and PD supply (old G07-G09) are Electronics Lab equipment covered by the Jacobs Maker Pass (paid outside the budget) and are no longer BOM lines. Bought only if the lab has no flux or wick (gate X10, check on the first visit)")
line("G11", "ground", "Hot-wire: NICE-POWER 30 V 10 A supply + Ni80 24 AWG", "Amazon", "ASIN B0CRSS744F + B0CP9V3DBX", "EARLY", 1, 0, 41.73, seen="2026-11-01", lead=4,
     url="https://www.amazon.com/dp/B0CRSS744F", part="GND-011",
     note="BOUGHT (2026-11-13): the Jacobs labs-and-equipment page lists no hot-wire foam cutter (checked 2026-11-13), so X11 is dissolved. EARLY order so the bow and 2-3 practice cores exist before Jacobs closes 18 Dec. The ASIN B0CRSS744F title reads 0-30 V 0-10 A 150 W (15 V 10 A / 30 V 5 A); price carried from 2026-11-01, not re-read")

line("G12", "groundtest", "Ground-test additions: 1 kgf bar cell + HX711 (torque arm) + 5 K-type thermocouple probes", "Amazon", "1 kg bar load cell + HX711; K-type bead probe x5", "EARLY", 1, 0, 17.00,
     status="EST", seen="2026-11-09", lead=4, url="https://www.amazon.com/", part="GND-012",
     note="CR-A1-39 / D-39: the only NEW ground-test purchase, <= $20. With G06 (20 kgf cell kit, $17.97) the bought rig is $34.97; everything else on H1's list is borrowed (ORDER-PLAN borrow table)")

line("G13", "groundtest", "2 foil strain gauges 350 ohm (pack of 5-10) + cyanoacrylate gauge kit, for T-C4-FIN-PROOF (paper face + strip)", "Amazon", "350 ohm foil gauge 3 x 5 mm, pack", "DEC", 1, 0, 9.00,
     status="EST", seen="2026-11-10", lead=4, url="https://www.amazon.com/", part="GND-012",
     note="CR-C4-38 / D-70: two gauges on the fin proof article; read on the HX711 from G12 as a half bridge with two 350 ohm resistors (H1 confirms the amp). Pushes the NEW ground-test purchase to $26.00, above the D-39 $20 line: A1 decision")

# --- R5 owned-or-borrowed list (CDR-BT-05 "bring or buy" tools and shop consumables, BUILD-GUIDE.md lines 41-48): every
#     line is gated X14 and bought only if the CDR-11 walk (19 Nov) finds no team member owns or lends one. Prices read
#     2026-11-13 (search snippets of the vendor pages). Items with no price read are UNPRICED lines U03-U10.
_K = dict(status="CHK", seen="2026-11-13", lead=5)
line("K01", "tools", "Preset torque screwdriver 0.1-0.6 N m (Wiha TorqueVario-S 28550 handle; bits extra) for the 0.08-0.5 N m joints", "Carbide Processors", "Wiha 28550", "EARLY", 1, 0, 111.80,
     url="https://carbideprocessors.com/torquevario-s-screwdriver-handle-0-1-0-6-nm-wiha-28550", part="FIN-101", note="R5: snippet 2026-11-13 (Transcat $152.19). Handle only, bits not included. Range 0.1-0.6 covers the PA66 0.08 N m only at its floor: borrow first", **_K)
line("K02", "tools", "Pocket scale 200 g x 0.01 g", "Amazon", "Weigh Gram 200 g x 0.01 g", "EARLY", 1, 0, 9.99,
     url="https://slickdeals.net/f/18680695-prime-weigh-gram-200g-digital-pocket-gram-scale-w-0-01g-accuracy-8-79-free-shipping", part="GND-012", note="R5: Amazon price via a deal-post snippet (Oct 2025), not the Amazon page: weak", **_K)
line("K03", "tools", "Kitchen scale 5 kg x 1 g (Etekcity EK6015)", "Walmart (store)", "EK6015", "LOCAL", 1, 0, 13.99,
     url="https://www.walmart.com/ip/Etekcity-Digital-Kitchen-Food-Stainless-Scale-11-lb-5kg-Silver/46522394", part="GND-012", note="R5: snippet 2026-11-13. Weighs packs, parts and the aircraft (T-A3-CG-BALANCE needs two)", **_K)
line("K04", "tools", "Digital angle gauge / inclinometer (Wixey WR300 Type 2)", "Woodcraft (store)", "WR300", "LOCAL", 1, 0, 34.99, pess=34.99,
     url="https://www.woodcraft.com/products/wixey-digital-angle-gauge-with-backlight-type-2-wr300", part="FIN-003", note="R5: snippet 2026-11-13 (Trick-Tools $27.99 sale). Cant 7 deg check, pad incline test (mu <= 0.40, CDR-02)", **_K)
line("K05", "tools", "Z-bend pliers (Hangar 9 Z-Bender)", "Hillsborough Hobby", "Z-Bender", "EARLY", 1, 0, 26.99,
     url="https://hillsborohobbyshop.com/products/z-bender-pliers", part="MEC-003", note="R5: snippet 2026-11-13; no Du-Bro listing found", **_K)
line("K06", "tools", "Prop balancer Du-Bro Tru-Spin DUB499", "Du-Bro", "DUB499", "EARLY", 1, 0, 51.85,
     url="https://dubro.com/products/tru-spin-prop-balancer", part="PRP-003", note="R5: snippet 2026-11-13 (page 429; Horizon also $51.85)", **_K)
line("K07", "tools", "Hex driver set 1.5 / 2.0 / 2.5 / 3.0 mm (RDQ edition; ball-end not confirmed)", "RaceDayQuads", "RDQ hex driver set", "EARLY", 1, 0, 9.99, pess=11.99,
     url="https://www.racedayquads.com/products/hex-driver-tool-set-1-5-2-0-2-5-3-0mm-rdq-edition", part="FIN-101", note="R5: $9.99 snippet, $11.99 on a second RDQ page, both 2026-11-13. Goes in the RDQ cart if bought", **_K)
line("K08", "tools", "TPU 95A filament 1.75 mm (Overture, 2 kg; 1.5 g needed for the two GER-007 caps)", "Overture", "Overture TPU 2 kg", "EARLY", 1, 0, 41.99,
     url="https://overture3d.com/collections/all/products/overture-tpu-3d-printer-filament-1-75mm-2-kg", part="GER-007", note="R5 (CR-G3-02): only the 2 kg size had a price (snippet 2026-11-13). 1.46 g is needed (G3 PRINT-LIST): ask Jacobs and the team for a TPU offcut first; a 2 kg spool for 1.5 g is the last resort", **_K)
line("K09", "tools", "Hobby knife blades X-Acto #11, 100-pack", "Staples (store)", "X-Acto X611", "LOCAL", 1, 0, 19.49, pess=28.89,
     url="https://www.staples.com/product_301846", part="FIN-001", note="R5: $19.49 snippet, $28.89 on a second Staples listing, 2026-11-13", **_K)
line("K10", "tools", "Sandpaper 3M Pro Grade 80/150/220 assorted 6 sheets (no 120-400 assortment found)", "Home Depot El Cerrito", "3M 26000PGP-6", "LOCAL", 1, 0, 11.48,
     url="https://www.homedepot.com/p/reviews/3M-Pro-Grade-Precision-9-in-x-11-in-80-150-220-Assorted-Grits-Faster-Sanding-Sheets-6-Sheets-Pack-26000PGP-6/313637698/1", part="WNG-006", note="R5: snippet 2026-11-13; 400 grit single pack $6.68 if needed", **_K)
line("K11", "tools", "Mixing cups 8 oz graduated, 50-pack", "Walmart (store)", "8 oz graduated cups", "LOCAL", 1, 0, 4.97,
     url="https://www.walmart.com/ip/seort/607476226", part="FIN-105", note="R5: snippet 2026-11-13", **_K)
line("K12", "tools", "Isopropyl alcohol 99 %, 32 oz", "Tractor Supply", "UltraCruz 99 % 32 oz", "EARLY", 1, 0, 14.99,
     url="https://www.tractorsupply.com/tsc/product/ultracruz-isopropyl-alcohol-99-32-oz-2332330", part="FIN-105", note="R5: snippet 2026-11-13, online only (counted as a shipment if bought)", **_K)

unpriced("U08", "transport", "Landing-spares box, any 1 L food container (TRN-108)", "team stock", "LOCAL", 1,
         "R5: the linked OXO box read $17.99 (LINKS-CHECK snippet) against a $3 EST; a container from home is used. Was line T08", gate="X14", covers="TRN-108")
unpriced("U01", "propulsion", "Prop APC 11x7EP (pusher) x2 for the stand A/B", "APC", "EARLY", 2,
         "apcprop.com/product/11x7ep/ returned 404 on 2026-11-13; no LP11070EP listing found. Horizon lists the 11x7 pusher LP11070P (not EP) at $4.44 (snippet): ask APC. One 11x7E (B09) is enough for a one-station stand A/B", covers="PRP-003")
unpriced("U02", "airframe", "Clear tape 100 mm wide (BUILD-GUIDE consumables)", "-", "LOCAL", 1,
         "no 4 in clear box tape listing found on 2026-11-13; nearest Shurtape 72 mm 6-pack $30.49 (Zoro snippet). W06 (48 mm) covers the skin unless D1 needs 100 mm", covers="WNG-003")
unpriced("U03", "tools", "Nitrile gloves, box of 100", "Harbor Freight (store)", "LOCAL", 1,
         "HF HARDY 5 mil item 68496: only an expired coupon price seen (2026-11-13)", gate="X14", covers="FIN-105")
unpriced("U04", "tools", "Digital calipers 150 mm", "Harbor Freight (store)", "LOCAL", 1,
         "HF Pittsburgh item 63711: only an expired member price seen (2026-11-13)", gate="X14", covers="FIN-002")
unpriced("U05", "tools", "Servo tester, 3-channel", "-", "EARLY", 1,
         "only a Fruugo (resale, currency unclear) listing found on 2026-11-13", gate="X14", covers="MEC-001")
unpriced("U06", "tools", "1 m steel rule, depth gauge, pin vise, drills 1.85 / 2.5 / 3.4 / 8 mm, 3 mm and 22 mm ball bits, luggage scale", "-", "LOCAL", 1,
         "BUILD-GUIDE 'Bring or buy'; not priced on 2026-11-13. Jacobs drill presses and bits are in-lab (Maker Pass)", gate="X14", covers="")

# --- link fixes (see LINKS-CHECK.md): product-page urls; prices and quantities untouched
LINK_FIXES = {
    'B05': ('https://gravesrc.com/apclpar06e-apc-adapter-rings-for-electric-propellers', 'Graves RC (US reseller) page for APC LPAR06E; motionrc.com listing seen sold out. Price not seen'),
    'B07': ('https://aspenfasteners.com/m3-0-5-x-8mm-din-912-iso-4762-metric-hex-socket-head-cap-screws-a2-stainless-steel', 'Bolt Depot has no M3x8 A2 page in search; Aspen Fasteners (US) lists the exact M3-0.5 x 8 mm ISO 4762 A2 screw. Price not seen'),
    'A04': ('https://www.readymaderc.com/products/details/rmrc-digital-air-speed-sensor-pixhawk-ii-2', 'RMRC kit page (sensor + pitot + tubing); confirm the board is the MS4525DO (sensor-board-only SKU 86845 names it). Price not seen'),
    'A05': ('https://www.amazon.com/dp/B08GY9NYRM', 'SanDisk Ultra 32 GB A1 microSDHC; representative product; any equivalent; link not opened; matched by search'),
    'A06': ('https://www.amazon.com/dp/B0BGN7N6PL', 'FrSky 150 mm IPEX1 dipole; sold singly, not a verified T-antenna pair; confirm IPEX1 and order 2; link not opened; matched by search'),
    'A07': ('https://www.getfpv.com/rtom-anti-vibration-moongel.html', 'NO PRODUCT PAGE FOUND for a 5 mm alpha-gel sheet; RTOM Moongel (drum damping gel) is not a confirmed match; representative product; any equivalent; link not opened; matched by search'),
    'W01': ('https://www.homedepot.com/p/Owens-Corning-FOAMULAR-NGX-F-250-2-in-x-4-ft-x-8-ft-SSE-R-10-XPS-Rigid-Foam-Board-Insulation-52DDNGX/315197962', 'Home Depot model 52DDNGX (scored square edge); price not seen; link not opened; matched by search'),
    'W05': ('https://west3d.com/products/ambrosia-petg-filament-of-the-gods-1kg-bambu-ams-friendly-cardboard-spools-premium-3d-printing-filament', 'West3D Ambrosia PETG 1 kg; search snippet shows $20.99, matches; link not opened; matched by search'),
    'W07': ('https://www.amazon.com/dp/B004GHJ9NW', 'UHU Por 50 ml; representative product; any equivalent; link not opened; matched by search'),
    'H01': ('https://www.amazon.com/dp/B0CKZCFC54', 'line = six purchases; link is the JST-GH pigtail kit only. Servo extension e.g. https://www.amazon.com/dp/B00Q683IFE; representative product; any equivalent; link not opened; matched by search'),
    'H02': ('https://www.amazon.com/dp/B0006O4G8M', 'link is the Du-Bro DUB185 2-56 rod + steel Kwik-Link only; CF rod, CF tube 5x4 and M2x6 screws not linked; representative product; any equivalent; link not opened; matched by search'),
    'H03': ('https://www.amazon.com/dp/B08LLBMT1N', 'Hobbypark XT60 pair with 10 AWG leads; representative product; any equivalent; link not opened; matched by search'),
    'F01': ('https://www.amazon.com/dp/B0BWH5D7H7', 'Amass AS150U with signal pin, one pair; need 5 pairs (check pack size); confirm AS150U not AS150; link not opened; matched by search'),
    'F02': ('https://www.amazon.com/dp/B017TGYW3S', 'BNTECHGO 10 AWG red+black 5 ft; 8 AWG bus wire not linked; representative product; any equivalent; link not opened; matched by search'),
    'F03': ('https://www.amazon.com/dp/B017TFR664', 'BNTECHGO 16 AWG red+black 10 ft; no yellow in this listing, add a yellow 16 AWG; representative product; any equivalent; link not opened; matched by search'),
    'F04': ('https://www.amazon.com/dp/B01AAX64EC', 'BNTECHGO 20 AWG red+black 10 ft each; representative product; any equivalent; link not opened; matched by search'),
    'F05': ('https://www.readymaderc.com/products/details/hobbywing-ubec-8a', 'Hobbywing UBEC-8A (5/6 V, 8 A, 2-3S); a retailer snippet marks it discontinued: check stock; alt RMRC 8A/12A UBEC'),
    'F06': ('https://www.amazon.com/dp/B07L4QFXTB', 'HUIQIAODS 2-pack inline holders with 5 A ATM fuses (listing mixes ATM/ATC wording: check); representative product; any equivalent; link not opened; matched by search'),
    'F07': ('https://www.amazon.com/pcs-Panasonic-FR-Capacitors-680uf/dp/B072SSXHW', 'Panasonic FR 680 uF 25 V 6-pack (ultra low ESR); representative product; any equivalent; link not opened; matched by search'),
    'F08': ('https://www.amazon.com/dp/B08LDXGCMJ', 'IIVVERR FR-4 single-sided 100x70x1.6 mm 5-pack; representative product; any equivalent; link not opened; matched by search'),
    'F09': ('https://www.amazon.com/dp/B089D82FLG', 'Wirefy 3:1 adhesive-lined kit 200 pcs; representative product; any equivalent; link not opened; matched by search'),
    'C01': ('https://boltdepot.com/Product-Details?product=4792', 'Bolt Depot M3 18-8 nylon-insert nut (kit also needs M3x16 screws and washers, product 4513: not linked); representative product; any equivalent; link not opened; matched by search'),
    'C06': ('https://www.amazon.com/dp/B0F5J2ZLXY', 'Happinesspark PA66 socket-head M3 assortment; spacers separate (e.g. https://www.amazon.com/dp/B074N5HD42); representative product; any equivalent; link not opened; matched by search'),
    'C02': ('https://www.amazon.com/dp/B08BCRZZS3', 'Ruthex RX-M3x5.7 inserts, 100 pcs; nylon washers not included; representative product; any equivalent; link not opened; matched by search'),
    'C03': ('https://alofthobbies.com/products/2-5mm-x-1000mm-rod', 'Aloft 2.5 mm x 1000 mm pultruded CF rod, $2.63 per search snippet (BOM $3.50), not changed; link not opened; matched by search'),
    'C04': ('https://www.amazon.com/dp/B004VODM24', 'Loctite 243 10 mL (page shown unavailable in snippet); paint pen not linked; representative product; any equivalent; link not opened; matched by search'),
    'D01': ('https://alofthobbies.com/products/2mm-x-10mm-x-1000mm', 'Aloft 2 mm x 10 mm x 1000 mm strip; search snippet shows $5.50 (BOM $10.00): not changed, page not fetched'),
    'D02': ('https://alofthobbies.com/products/1mm-x-10mm-x-1000mm', 'Aloft 1 mm x 10 mm x 1000 mm strip; price not seen; link not opened; matched by search'),
    'D03': ('https://alofthobbies.com/products/20-x-18-x-1000mm-mw-carbon-tubing', 'Aloft 20x18x1000 mm MW tube; search snippet shows $19.25 (BOM $20.00): not changed, page not fetched; link not opened; matched by search'),
    'D07': ('https://www.zoro.com/k-s-precision-metals-k-s-precision-metals-8130-022-od-x-12-l-in-round-brass-tube-691089/i/G304145442', 'K&S 8130 round brass tube 7/32 in OD x 12 in via Zoro (US); price not seen; link not opened; matched by search'),
    'D04': ('https://www.amazon.com/dp/B01LZK3UAR', 'nearest listing: 0.5 in x 8 in hook-and-loop ties, 10-pack (12.7 mm, not 10 mm); representative product; any equivalent; link not opened; matched by search'),
    'D05': ('https://www.zoro.com/zoro-select-neoprene-sheet-40a-12x12x116-black-bulk-rs-n40txt-14/i/G4865769', 'Zoro Select neoprene 40A, 12 x 12 in x 1/16 in, textured, acrylic adhesive back (BULK-RS-N40TXT-14); McMaster would not give a part number; representative product; any equivalent; link not opened; matched by search'),
    'D06': ('https://www.amazon.com/dp/B019QYCXR8', 'Apex RC 20x300 mm rubberized straps 5-pack; EVA shims not linked; representative product; any equivalent; link not opened; matched by search'),
    'W08': ('https://west3d.com/products/polymaker-polylite-asa-3d-printer-filament-1kg-1-75mm', 'West3D carries Polymaker PolyLite ASA 1 kg (no Ambrosia ASA there); search snippet shows $25.99-28.99 vs BOM $24.99: not changed; link not opened; matched by search'),
    'T03': ('https://www.homedepot.com/p/Keeper-1-in-x-6-ft-x-400-lbs-Motorcycle-Cam-Buckle-Tie-Down-2-Pack-05715/204752873', 'Keeper 05715 cam-buckle 2-pack (snippet $13.99-15.92); handles not linked; representative product; any equivalent; link not opened; matched by search'),
    'T04': ('https://www.harborfreight.com/12-in-zipper-utility-pouch-black-70998.html', 'Yukon 12 in zipper pouch (the field pouch); 10 mm spanner is a separate item, e.g. https://www.homedepot.com/p/Husky-10-mm-12-Point-Metric-Full-Polish-Combination-Wrench-HCW10MM/202916162; M3 hardware not linked; representative product; any equivalent; link not opened; matched by search'),
    'T05': ('https://www.homedepot.com/p/Rubber-Cal-Neoprene-1-16-in-x-36-in-x-12-in-Commercial-Grade-45A-Soft-Rubber-Sheet-Rolls-20-104-0062-36-012/303172042', 'Rubber-Cal neoprene 1/16 in x 12 x 36 in 45A (snippet $15.31, may be stale); thickness near 1.5 mm; representative product; any equivalent; link not opened; matched by search'),
    'T06': ('https://www.homedepot.com/p/Customizable-Polyethylene-Foam-Sheets-16L-x-12W-x-1-Thick-Padding-for-Cases-Tool-Foam-for-Packaging-Crafts-2-Pack-638PH01222D/336659215', 'NO PRODUCT PAGE FOUND for 2 in PE plank at Home Depot; 1 in PE foam sheets as nearest; representative product; any equivalent; link not opened; matched by search'),
    'T07': ('https://www.homedepot.com/p/Husky-12-Gal-Professional-Heavy-Duty-Waterproof-Stackable-Plastic-Storage-Container-with-Hinged-Lid-in-Red-248921/313861297', 'Husky 12 gal tote; check size against the 0.45 x 0.35 x 0.25 m target; representative product; any equivalent; link not opened; matched by search'),
    'H05': ('https://www.amazon.com/dp/B0FBL3342W', 'Ni80 20 ga 30 ft wire only (BOM line also needs bow/jig and template stock: NO PRODUCT PAGE FOUND for those); representative product; any equivalent; link not opened; matched by search'),
    'R02': ('https://www.getfpv.com/lumenier-nav-3000mah-1s-18650-lithium-ion-battery-2pcs.html', 'GetFPV Lumenier NAV 3000 mAh 18650 2-pack; snippet $24.49 matches; one cached page showed Out of Stock; link not opened; matched by search'),
    'G02': ('https://pyrodrone.com/products/pyrodrone-lipo-safe-pouch', 'Pyrodrone LiPo Safe Pouch; snippet $7.99 vs BOM $9.99: not changed; link not opened; matched by search'),
    'G06': ('https://www.amazon.com/dp/B07BGS58TL', 'NOYITO 20 kg load cell + HX711 combo; Arduino Nano not included; link not opened; matched by search'),
    'G10': ('https://www.amazon.com/dp/B0H94VTN26', 'KELLYSHUN flux paste + 63/37 solder wire + tip tinner; no wick, add desoldering wick; representative product; any equivalent; link not opened; matched by search'),
    'G12': ('https://www.amazon.com/dp/B0F52QCK3T', '1 kg load cell + HX711 listing; K-type probes not linked (e.g. https://www.amazon.com/dp/B0FW56V11S); link not opened; matched by search'),
    'G13': ('https://www.amazon.com/dp/B07WYD7Z4P', 'Eastar BF350-3AA 350 ohm foil gauge; CA adhesive not linked; representative product; any equivalent; link not opened; matched by search'),
}
LINK_PRICE_SEEN = ['A04', 'B05', 'B07', 'D01', 'F05']  # R5: M01, C05, T01, T02 rows dropped from LINK_FIXES (each line carries its own link); T08, T09 deleted  # price seen on the opened product page 2026-11-11 (noted, not applied)
for _l in L:
    if _l['id'] in LINK_FIXES:
        _u, _n = LINK_FIXES[_l['id']]
        _l['url'] = _u
        _l['note'] = (_l['note'] + '; ' if _l['note'] else '') + 'link: ' + _n
        if _l['id'] in LINK_PRICE_SEEN:
            _l['status'] = 'CHK'
            _l['seen'] = '2026-11-11'

# Lines that stay in this BOM (vendor, part number, price) but are bought only when their gate passes: NOT in the spend
# totals, reported in the `all-in` figures. X07 = D7 box and field kit (store pick-up, zero lead time, needed from March);
# X08 = airspeed sensor (DECISION 5.1 lever; needed for the fixed-wing tune, which can start on the synthetic airspeed).
GATE_OF = {"T01": "X07", "T02": "X07", "T03": "X07", "T04": "X07", "T05": "X07", "T06": "X07", "T07": "X07", "T08": "X07", "T09": "X07", "A04": "X08",
           # 2026-11-13: the Jacobs Maker Pass is paid outside the budget (owner). Electronics Lab iron, multimeter and PD supply
           # (old G07-G09) are covered and no longer BOM lines; only the flux/wick fallback G10 stays gated (X10). Jacobs lists no
           # hot-wire foam cutter (labs-and-equipment page, checked 2026-11-13), so G11 and H05 are BOUGHT (old gate X11 dissolved).
           "G10": "X10",
           # D-74: the power board's own servo BEC (8 A cont) replaces the UBEC; bought only if BOARD-CHECK.md step 7 fails
           "F04": "X12", "F05": "X12", "F06": "X12",
           # R5 (D-130): lever L2 microSD from team stock; X14 = the owned-or-borrowed walk of CDR-11 (19 Nov)
           "A05": "X13", **{f"K{i:02d}": "X14" for i in range(1, 13)},
           # R5 (D-131, levers to stay inside $2 000 at order): fillers and the anemometer join the owned-or-borrowed walk
           # (FIN-105 lists the fillers as 'shared shop stock'; H3 CR-H3-02 says 'add or borrow'); the 35 V caps are bought
           # only if the stand shows the 25 V cap out of rating (X15)
           "C07": "X14", "C08": "X14", "G14": "X14", "F10": "X15"}
for _l in L:
    _l["gate"] = GATE_OF.get(_l["id"], "")

# Gated purchases: NOT in the totals. Bought only when the stated test passes (D-12 pattern).
GATED = [
    dict(id="X02", item="Spare elevon servo (3rd Savox SH-0255MG+)", net=41.99, gate="as X01; D6 and CR-A1-52 ask for 3, the reserve pays for 2", why="spare, 2 fitted; single-source 12 mm servo, buy it first if the reserve allows"),
    dict(id="X03", item="Optional APC 11x5.5E x2 + 11x5.5EP x2 (CR-B4-11, rings included)", net=16.68, gate="as X01; only if the stand shows the MR/MRP pair short",
         why="alternate for the stand A/B"),
    dict(id="X04", item="Flight packs 3-4, one more Ovonic 2-pack", net=82.97, gate="D-12: reserve after the December order >= $309 + $91.47 (at sale price); and only a SKU that passes CR-I1-13",
         why="2 sorties per test day until then"),
    dict(id="X05", item="Small Parts CNC 4114 prop adapter set (2 RH + 2 LH), CR-E1-20 / D-39", net=23.95, gate="as X01; only if the motor-box adapters fail the stand (T-E1-STAND) and the page is back in stock",
         why="out of stock on 2026-11-09; E1's fallback (adapter in each motor box + Loctite 243) accepted in D-39"),
    dict(id="X06", item="Remote ID module NewBeeDrone BeeID", net=39.99, gate="only if flown outside the RFS FRIA", why="CONFIGURATION: none fitted"),
    dict(id="X07", item="D7 box and field kit (lines T01-T07: Coroplast, LSE tape, straps, handles, pouch, spanner, mat, PE foam, tote)", net=None, gate="as X01, before the first drive to the field (store pick-up, no lead time); until then a borrowed carton",
         why="deferred in R2 to hold the pessimistic reserve >= $309 (CR-I1-14); replaces the old $60 plywood estimate H04"),
    dict(id="X08", item="RMRC MS4525DO airspeed sensor + pitot (line A04)", net=None, gate="as X01; DECISION 5.1 lever, last in the order (CR-I1-03)",
         why="needed for gain scheduling in fixed-wing flight; the first fixed-wing tune can run on the synthetic airspeed estimate (F4 confirms)"),
    dict(id="X10", item="Flux + desoldering wick if the Electronics Lab has none (G10)", net=None,
         gate="first Electronics Lab visit: no flux or wick at the stations (the page says only 'solder provided'); then buy G10",
         why="2026-11-13: the Maker Pass covers the lab's soldering irons, multimeters and solder, so the old kit (G07 Pinecil, G08 PD supply, G09 multimeter) is deleted; flux and wick are not listed"),
    dict(id="X12", item="UBEC fallback (lines F04 20 AWG, F05 UBEC, F06 fuse + holder), D-74", net=None, gate="only if subsystems/power/BOARD-CHECK.md step 7 fails (servo-BEC Vx < 5.8 V at ~5.4 A); then a 4S-input 6 V UBEC (5-day lead), before the January build",
         why="the CoreWing V2 servo BEC is 8 A cont / 14 A peak (manual V2.1, ArduPilot); the 4.5 A behind the UBEC was the SpeedyBee figure"),
    dict(id="X13", item="microSD 16-32 GB (line A05), lever L2", net=None, gate="CDR-11 owned-or-borrowed walk (19 Nov): bought only if no team member has a card",
         why="R5 / D-130: CDR-BT-03 L2"),
    dict(id="X14", item="Owned-or-borrowed list (lines K01-K12: torque driver, scales, inclinometer, Z-bend pliers, prop balancer, hex drivers, TPU, blades, sandpaper, cups, IPA; U03-U06, U08 unpriced)", net=None,
         gate="CDR-11 walk (19 Nov): each item owned, borrowed (lender named) or bought; only the bought ones are ordered, early cart or store",
         why="R5 / D-130 (CDR-BT-05): BUILD-GUIDE 'Bring or buy' and shop consumables; reviewer range $60-250 EST until the walk is done"),
    dict(id="X15", item="35 V low-ESR caps x5 (line F10), CDR-EL-05", net=None,
         gate="GT-04 on the stand with the F07 25 V cap: buy only if cap-leg ripple exceeds the F07 rating (1.79 A at 100 kHz) or the can rises > 15 K",
         why="R5 / D-131: measure first with the part already bought; a DigiKey shipment for a fix the test may not need"),
    dict(id="X09", item="K-type thermocouple logger / 2-channel meter (E3 GT-04)", net=15.00, gate="only if no Electronics Lab multimeter reads the K-type probes in the lab (Jacobs does not lend equipment out; the pass is drop-in access)", why="H1 list; in-lab reading is the first choice"),
]


# ------------------------------------------------------------------ arithmetic (pure; the proof chain re-runs these)
CART = {"Amazon / DigiKey": "Amazon", "DigiKey / Amazon": "Amazon", "Amazon / hobby shop": "Amazon"}   # one Amazon cart per wave
FLIGHT_READY_GATES = ("X07", "X08")   # B4: the box and the airspeed sensor are needed to fly the mission


def _in(l, gates):
    return (not l["gate"]) or (gates == "all") or (l["gate"] in gates)


def _sum(key, orders=None, taxable_only=False, gated=False, gates=()):
    g = "all" if gated else gates
    return round(sum((l["fit"] + l["spare"]) * l[key] for l in L
                     if (orders is None or l["order"] in orders) and (l["taxable"] or not taxable_only) and _in(l, g)), 2)


def shipments(gates=()):
    """Paid shipments = distinct (cart, order wave) pairs of mail-order lines (LOCAL = store pick-up, no shipping)."""
    return sorted({(CART.get(l["vendor"], l["vendor"]), l["order"]) for l in L if l["order"] != "LOCAL" and _in(l, gates)})


def gated_net(gid):
    """Pre-tax value of one gated purchase: its own `net`, or the sum of the BOM lines that carry the gate."""
    g = next(x for x in GATED if x["id"] == gid)
    if g["net"] is not None:
        return g["net"]
    return round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["gate"] == gid), 2)


def spend_case(tax_rate, gates=()):
    """Baseline and pessimistic spend for the committed lines plus the BOM lines of `gates` ("all" = every gate)."""
    gb, gp = _sum("unit", gates=gates), _sum("pess", gates=gates)
    n = len(shipments(gates))
    sb = round(gb * (1 + tax_rate) + n * SHIP_PER_BASE + FAA_FEE + DUTY_BASE, 2)
    sp = round(gp * (1 + tax_rate) + n * SHIP_PER_PESS + FAA_FEE + DUTY_PESS + TAXMEAS_ADV + JIG_ADV, 2)
    return dict(goods_base=gb, goods_pess=gp, shipments=n, spend_base=sb, spend_pess=sp)


def money(tax_rate):
    c = spend_case(tax_rate)
    goods_b, goods_p = c["goods_base"], c["goods_pess"]
    tax_b, tax_p = round(goods_b * tax_rate, 2), round(goods_p * tax_rate, 2)
    ship_b, ship_p = round(c["shipments"] * SHIP_PER_BASE, 2), round(c["shipments"] * SHIP_PER_PESS, 2)
    spend_b = round(goods_b + tax_b + ship_b + FAA_FEE + DUTY_BASE, 2)
    spend_p = round(goods_p + tax_p + ship_p + FAA_FEE + DUTY_PESS + TAXMEAS_ADV + JIG_ADV, 2)
    early = round(_sum("unit", {"EARLY"}) * (1 + tax_rate), 2)
    fr, al = spend_case(tax_rate, FLIGHT_READY_GATES), spend_case(tax_rate, "all")
    # all-in = every BOM line incl. the gated ones (X07, X08, X10, X12, X13, X14); the X-items with their own `net`
    # (X02-X06, X09) are not BOM lines and stay out, as in R4
    return dict(spend_pess_allin=al["spend_pess"], spend_base_allin=al["spend_base"], shipments_allin=al["shipments"],
                spend_pess_flight_ready=fr["spend_pess"], spend_base_flight_ready=fr["spend_base"],
                goods_base=goods_b, goods_pess=goods_p, tax_base=tax_b, tax_pess=tax_p, ship_base=ship_b, ship_pess=ship_p,
                shipments=c["shipments"], shipments_flight_ready=fr["shipments"], duty_base=DUTY_BASE, duty_pess=DUTY_PESS,
                spend_base=spend_b, spend_pess=spend_p, early_goods_tax=early)


def bridge(tax_rate):
    """Pessimistic spend = I1-R2 published pessimistic spend ($1 687.01, params D-57) + this revision's pre-tax deltas x (1 + tax).
    The delta numbers are typed here from the designers' requests, not read from L, so money() and bridge() agree only if every
    line change was recorded."""
    r2 = 1687.01
    deltas = {
        "P01 Ovonic 120C EC5 pair, pessimistic EUR 113.30 x 1.16 = 131.43 replaces 130C XT60 list 119.88 (D-64)": 131.43 - 119.88,
        "M01 Savox SH-0255MG+ 2 x 41.99 replaces ES3005HV 2 x 19.99 (CR-D6-02)": 2 * 41.99 - 2 * 19.99,
        "A06 two U.FL T-antennas (D-72)": 6.00,
        "A07 FC isolation set 10.00 (F3 AVN-006)": 10.00,
        "F03 16 AWG 8 to 14 (HRN-101), F08 PDB 6 to FR4 3, F09 heat-shrink 6 to 9": 6.00 - 3.00 + 3.00,
        "H01 + H02 residual 36 replaced by itemised harness 41 and mechanisms hardware 24": 41.00 + 24.00 - 36.00,
        "C06 PA66 socket-head set 7.00; C03 CF rod 2.5 mm x 2 at 3.50 replaces 2 mm x 1 at 3.00": 7.00 + (7.00 - 3.00),
        "D07 brass tube 7/32 in 3.00 (CR-D5-27); D06 straps 6 to 7": 3.00 + 1.00,
        "G13 two strain gauges (CR-C4-38)": 9.00,
        "H07 board-link ribbon + headers 3.00 (HRN-114) (D-89; the H08 pitot couplers were dropped in D-89b)": 3.00,
        "2026-11-13 Maker Pass: G07 25.99 + G08 20.00 + G09 25.00 deleted (Electronics Lab, covered); G10 15.00 held behind gate X10": -(25.99 + 20.00 + 25.00 + 15.00),
        "2026-11-13: G11 41.73 + H05 15.00 BOUGHT (Jacobs lists no hot-wire gear; old gate X11 dissolved; was borrowed, delta -56.73)": 0.0,
        "T05 mat 25, T07-T09 tote, box, labels 13: gated X07, nothing in the spend": 0.0,
        "D-74: F04 4 + F05 18 + F06 6 gated X12 (UBEC fallback); H06 XT30U 10-pair 9.99 (WB-03)": -(4.00 + 18.00 + 6.00) + 9.99,
        # ---- R5 (2026-11-13, CDR-09 / CDR-10, D-130), pessimistic prices
        "R5 B08 second ESC 4-pack = 4 spare ESCs (R-CRASH-REPAIR; was gated X01)": 30.00,
        "R5 B03 spare props 4 -> 8 (R-CRASH-REPAIR) 4 x 3.83": 4 * 3.83,
        "R5 B09 APC 11x7E x2 for the stand A/B (chair A5) 2 x 4.17": 2 * 4.17,
        "R5 W02 foam board: 10 store sheets at 1.25 replace the 35.92 10-pack (L1)": 10 * 1.25 - 35.92,
        "R5 A05 microSD behind gate X13 (L2)": -6.00,
        "R5 A01 CoreWing V2 stack at RaceDayQuads 69.49 (was ReadyMadeRC 67.26, dead page)": 69.49 - 67.26,
        "R5 R01 Pocket Crush carried at 84.49 (CDR-BT-07; was 64.99)": 84.49 - 64.99,
        "R5 C05 epoxy BSI 30 min 9 oz 22.99 (was 14 for a kit); C07 silica, C08 microballoons gated X14": 22.99 - 14.00,
        "R5 F03 second 16 AWG reel set (chair A5); F10 35 V caps gated X15": 14.00,
        "R5 consumables: W09 filament tape 17.99, G16 3M 77 13.28, G17 sand + bucket 13.97, G18 tether 39.58 (G14 anemometer gated X14)": 17.99 + 13.28 + 13.97 + 39.58,
        "R5 X07 / X14 lines (T01, T02 re-priced, T08 / T09 removed, K01-K12): gated, nothing in the spend": 0.0,
    }
    # R5 untaxed changes: pack duty + brokerage (pessimistic $45) and shipping counted per shipment (15 x $10.71) instead of
    # the flat $150 (lever L3: 14 vendors -> 11 shipments)
    untaxed = {"R5 P01 duty + brokerage, pessimistic (CDR-BT-06)": DUTY_PESS,
               "R5 shipping: 11 paid shipments x 150/14 replace the flat 150": 11 * SHIP_PER_PESS - (SHIP_BASE + SHIP_ADV)}
    return round(r2 + sum(deltas.values()) * (1 + tax_rate) + sum(untaxed.values()), 2), {**deltas, **untaxed}


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

kit.assumption("ASM-I1-SHIPPING", "Shipping per paid shipment 8.57 / 10.71 USD", "R5 (lever L3): each paid shipment (one vendor cart per order wave; store pick-up free; Amazon counted as paid) costs the R4 flat $120 / $150 spread over its 14 vendors: $8.57 baseline, $10.71 pessimistic",
               basis="cards/K09/cost.csv shipping line and DECISION section 9 ($120 + $30); ORDER-PLAN R4 'about 14 vendors'; CDR-BT-03 L3 ($150 / 14); no vendor quote taken", value=round(SHIP_PER_PESS, 4), unit="USD",
               status="UNVERIFIED", cites=["SRC-K09-CARD", "SRC-TIEBREAK"])
kit.assumption("ASM-I1-ADDERS", "Pessimistic adders 27 USD", "Tax measure +7 and jig/box growth +20 USD on top of list-price lines",
               basis="DECISION section 9 (K01 REVIEW S8-S11 applied to every candidate)", value=TAXMEAS_ADV + JIG_ADV, unit="USD",
               status="UNVERIFIED", cites=["SRC-TIEBREAK"])

BOM_INPUTS = {"tax": P + "requirements.tax_rate", "budget": P + "requirements.budget_usd"}
BOM_UNITS = {"tax": "-", "budget": "USD"}


@kit.calc("CALC-I1-SPEND", title="BOM spend, baseline and pessimistic", inputs={"tax": P + "requirements.tax_rate"},
          units={"tax": "-"}, assumes=["ASM-I1-SHIPPING", "ASM-I1-ADDERS"], cites=["SRC-I1-CARRIED", "SRC-I1-APC-PRICE", "SRC-I1-OVONIC"],
          equation="spend = sum(qty x unit) x (1 + tax) + n_shipments x rate + FAA fee + pack duty (+ adders, pessimistic prices); lines in team/I1/build_bom.py LINES")
def spend(tax):
    return money(tax)


@kit.calc("CALC-I1-BRIDGE", title="Bottom-up minus R2-bridge (pessimistic spend)", inputs={"tax": P + "requirements.tax_rate", "sp": "CL-I1-SPEND-PESS"},
          units={"tax": "-", "sp": "USD"}, cites=["SRC-TIEBREAK"],
          equation="delta = spend_pess(bottom-up) - [1687.01 (R2) + sum(R3..R5 line deltas) x (1 + tax) + R5 untaxed deltas (duty, shipping)]", output="delta_usd")
def spend_bridge(tax, sp):
    return round(sp - bridge(tax)[0], 2)


@kit.calc("CALC-I1-RESERVE", title="Reserve at order, pessimistic and baseline",
          inputs={"budget": P + "requirements.budget_usd", "sp": "CL-I1-SPEND-PESS", "sb": "CL-I1-SPEND-BASE"},
          units={"budget": "USD", "sp": "USD", "sb": "USD"}, equation="reserve = budget - spend")
def reserve(budget, sp, sb):
    return {"reserve_pess": reserve_calc(budget, sp), "reserve_base": reserve_calc(budget, sb)}


@kit.calc("CALC-I1-FLIGHT-READY", title="Flight-ready spend: committed lines + X07 box and field kit + X08 airspeed sensor (B4)",
          inputs={"tax": P + "requirements.tax_rate", "budget": P + "requirements.budget_usd"},
          units={"tax": "-", "budget": "USD"}, assumes=["ASM-I1-SHIPPING", "ASM-I1-ADDERS"],
          equation="flight-ready spend = spend_case(committed + gates X07, X08); reserve = budget - spend", output="reserve_pess_flight_ready")
def flight_ready(tax, budget):
    m = money(tax)
    return {"reserve_pess_flight_ready": reserve_calc(budget, m["spend_pess_flight_ready"]),
            "reserve_base_flight_ready": reserve_calc(budget, m["spend_base_flight_ready"])}


@kit.calc("CALC-I1-ALLIN", title="All-in spend if every gated BOM line (X07, X08, X10, X12, X13, X14) were also bought",
          inputs={"tax": P + "requirements.tax_rate", "budget": P + "requirements.budget_usd"},
          units={"tax": "-", "budget": "USD"}, assumes=["ASM-I1-SHIPPING", "ASM-I1-ADDERS"],
          equation="all-in spend = spend + gated lines x (1 + tax); reserve = budget - spend", output="reserve_pess_allin")
def allin(tax, budget):
    m = money(tax)
    return {"reserve_pess_allin": reserve_calc(budget, m["spend_pess_allin"]), "reserve_base_allin": reserve_calc(budget, m["spend_base_allin"])}


@kit.calc("CALC-I1-GROUNDTEST", title="New bought ground-test purchase (line G12)", inputs={"tax": P + "requirements.tax_rate"},
          units={"tax": "-"}, cites=["SRC-I1-CARRIED"], equation="sum of BOM lines with group 'groundtest', pre-tax", output="bought_usd")
def groundtest(tax):
    g12 = sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["id"] == "G12")
    allg = sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["group"] == "groundtest")
    return {"bought_usd": round(g12, 2), "bought_with_gauges_usd": round(allg, 2)}


kit.claim("CL-I1-SPEND-BASE", "BOM spend at order, baseline", calc="CALC-I1-SPEND", output="spend_base", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Re-run build_bom.py after re-pricing each line on the day of the order; compare with the order confirmations.")
kit.claim("CL-I1-SPEND-PESS", "BOM spend at order, pessimistic", calc="CALC-I1-SPEND", output="spend_pess", unit="USD",
          limit=("<=", P + "requirements.budget_usd"), verifies=["R-BUDGET"],
          how="Same lines at list price plus the DECISION section 9 adders; CL-I1-BRIDGE-DELTA must be 0.")
kit.claim("CL-I1-BRIDGE-DELTA", "Bottom-up minus R2 bridge (USD)", calc="CALC-I1-BRIDGE", output="delta_usd", unit="USD",
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
kit.claim("CL-I1-RESERVE-PESS-FLIGHT-READY", "Pessimistic reserve, flight-ready (committed + X07 box + X08 airspeed sensor)", calc="CALC-I1-FLIGHT-READY",
          output="reserve_pess_flight_ready", unit="USD", limit=(">=", 0.0), verifies=["R-BUDGET"],
          how="Decision B4: every document quotes this beside the at-order reserve. Limit 0 = inside the $2 000 cap; the $309 crash line is CL-I1-RESERVE-PESS's limit (B3 would re-base it to about $228, not applied).")
kit.claim("CL-I1-RESERVE-BASE-FLIGHT-READY", "Baseline reserve, flight-ready (committed + X07 + X08)", calc="CALC-I1-FLIGHT-READY",
          output="reserve_base_flight_ready", unit="USD",
          how="Information: baseline prices, same lines as CL-I1-RESERVE-PESS-FLIGHT-READY.")
kit.claim("CL-I1-GROUNDTEST-BOUGHT", "New bought ground-test purchase, pre-tax (USD)", calc="CALC-I1-GROUNDTEST", output="bought_usd", unit="USD",
          limit=("<=", 20.0),
          how="D-39: at most $20 is bought new for ground test (G12 only); gauges G13 are CL-I1-GROUNDTEST-WITH-GAUGES. The 20 kgf cell kit G06 ($17.97) was already in the baseline.")

kit.claim("CL-I1-GROUNDTEST-WITH-GAUGES", "New ground-test purchases incl. the two fin-proof strain gauges G13, pre-tax (USD)", calc="CALC-I1-GROUNDTEST", output="bought_with_gauges_usd", unit="USD",
          how="G12 $17.00 (D-39 line, limit 20) + G13 $9.00 (CR-C4-38): $26.00 is $6 above the D-39 line. Information for A1, who owns the decision; the gauges are in the pessimistic spend.")
kit.test("T-I1-CONNECTOR-LEADS", "Confirm the pack connector and lead gauge before ordering", verifies=["CL-I1-SPEND-PESS"], state="planned",
         procedure="Before the pack order: ask the seller for the discharge-lead gauge (needs >= 10 AWG, F1 CL-F1-PACKLEAD-RISE) and confirm EC5 / 4S / 6500 / hard case / 2 packs in the cart (D-64). 12 AWG: stop, tell E2 and F1. Do not order the 130C XT60 SKU (680 g, 12 AWG). On arrival: measure the lead conductor with calipers, weigh both packs (accept <= 560 g each, CL-A3-PACK-ACCEPT, one line since D-95).")
kit.test("T-I1-LISTINGS", "Re-read the six listings before each order", verifies=["CL-I1-SPEND-PESS", "CL-I1-RESERVE-PESS"], state="planned",
         procedure="On 20 Nov and 15 Dec open: LANRC ASIN B0D2HS4Y4J, SunnySky X3108S, Ovonic 2-pack (connector, lead gauge, mass, price), Aloft tube, "
                   "APC 11x5.5MR/11x4.5MR; log price and stock in team/I1/listing_log.csv; re-run build_bom.py.")
kit.test("T-I1-BORROW", "Jacobs staff answer the equipment questions (Maker Pass is drop-in access, no loans)", verifies=["CL-I1-GROUNDTEST-BOUGHT"], state="planned",
         procedure="First Electronics Lab visit (before 20 Nov, with the safety training done): (a) confirm in the lab that flux and wick are at the soldering stations (else buy G10, gate X10) and that a multimeter reads K-type probes (else X09); (b) ask staff by email whether Jacobs allows hot-wire foam cutting or foam on the ShopBot (a yes would remove G11 and H05, $62.54 incl. tax); (c) confirm the Spring 2027 Maker Pass covers all four builders from 19 Jan. Jacobs does not lend equipment: the pass is in-lab access (jacobsinstitute.berkeley.edu/making-at-jacobs, checked 2026-11-13). File the reply in team/I1/borrow_confirmation.txt.")
kit.test("T-I1-ARRIVAL", "Weigh and inspect on arrival", verifies=["CL-I1-RESERVE-PESS"], state="planned",
         procedure="Weigh each pack, motor, ESC and the Aloft tube; check the pack connector is XT60; give masses to A3 and E2 (pack_log.csv).")


# ------------------------------------------------------------------ outputs
# R5 (CDR-BT-21): every part id in subsystems/*/parts.csv that a BOM line pays for. "ground" = ground gear with no parts.csv
# row (subsystems/ground/parts.csv lists GND-001 only; not in this stream's files); "test" / "tool" = not a part of the aircraft.
_PETG = ("AVN-005, FIN-004, FIN-008, FIN-010, FIN-013, GER-001, GER-002, GER-005, GER-009, GER-012, MEC-004, MEC-006, MEC-007, "
         "MEC-008, MEC-013, POD-002, POD-005, POD-006, POD-007, POD-008, POD-010, PWR-006, WNG-004, WNG-005")
COVERS = {
    "B01": "PRP-001 (4 + 1 spare); PRP-004, PRP-006, PRP-007, PRP-008 (adapter set in the motor box, E1 parts.csv)", "B02": "PRP-002", "B08": "PRP-002 (4 spares)", "B03": "PRP-003 (4 + 8 spares)", "B04": "test (PRP-003 A/B)",
    "B09": "test (PRP-003 A/B)", "B05": "PRP-004 (centring ring)", "B07": "PRP-005", "P01": "PWR-001, PWR-201", "A01": "AVN-001, PWR-003",
    "A02": "AVN-002", "A03": "AVN-003", "A04": "AVN-004, AVN-005 (pitot tube)", "A05": "AVN-007", "A06": "AVN-003 (antennas)",
    "A07": "AVN-006, PWR-106", "M01": "MEC-001, MEC-002, MEC-012 (arm and screw in the servo box)",
    "W01": "WNG-001, POD-009, POD-001 (XPS LE), TRN-002-L/R, TRN-003",
    "W02": "FIN-001, POD-001, POD-003", "W03": "WNG-002 spare (T-C4-TUBE-BEND first)", "W04": "WNG-002, FIN-002", "W05": _PETG,
    "W06": "WNG-003, MEC-010, TRN-109, WNG-020 (cover)", "W07": "WNG-001 (foam joints)", "W08": "FIN-003, FIN-007, HRN-110",
    "W09": "GER-007 (cap wraps)", "H01": "HRN-102, HRN-104, HRN-105, HRN-106, HRN-108, HRN-109", "H02": "MEC-003, MEC-005, MEC-009, MEC-011",
    "H03": "PWR-202", "H06": "HRN-113", "H07": "HRN-114", "F01": "PWR-002, PWR-202", "F02": "PWR-104", "F03": "HRN-101",
    "F04": "none (D-74 UBEC fallback)", "F05": "none (D-74 UBEC fallback)", "F06": "none (D-74 UBEC fallback)", "F07": "PWR-008",
    "F08": "PWR-105, PWR-004", "F09": "HRN-107", "F10": "test (PWR-008 A/B)", "C01": "FIN-101, FIN-102, FIN-103",
    "C06": "PWR-101, PWR-102, PWR-103, POD-011, POD-012", "C02": "PWR-107 (+ FC plate inserts)", "C03": "FIN-012", "C04": "FIN-107",
    "C05": "FIN-105, WNG-006", "C07": "FIN-105", "C08": "WNG-006, FIN-105", "D01": "FIN-009", "D02": "FIN-011", "D03": "FIN-006",
    "D07": "GER-013", "D04": "FIN-104", "D05": "GER-006, GER-004", "D06": "POD-004", "T01": "TRN-001, TRN-005, TRN-105 (offcut)", "T02": "TRN-101",
    "T03": "TRN-006-L/R, TRN-007-C/L/R", "T04": "TRN-008, TRN-106, TRN-102", "T05": "TRN-104", "T06": "TRN-002-L/R, TRN-004-L/R",
    "T07": "TRN-107", "H05": "tool (WNG-001 hot-wire bow and templates)", "R01": "GND-001", "R02": "GND-001",
    "G01": "ground", "G02": "ground", "G03": "ground", "G04": "ground", "G05": "ground", "G06": "ground (test rig)", "G10": "ground",
    "G11": "tool (WNG-001, POD-009 hot wire)", "G12": "ground (test rig)", "G13": "test (T-C4-FIN-PROOF)", "G14": "ground (R-WIND-MEASURE)",
    "G16": "FIN-106", "G17": "ground (LiPo safety)", "G18": "ground (tether, POD-007 attachment)",
    **{f"K{i:02d}": "tool" for i in range(1, 13)}, "K08": "GER-007", "K11": "FIN-105", "K12": "FIN-105",
}


def covers_check():
    """Bought part ids (make_or_buy = buy, flight or ground) that no BOM line names in COVERS: reported in bom_summary.json."""
    import re
    named = set(re.findall(r"[A-Z]{3}-\d{3}", " ".join(list(COVERS.values()) + [u["covers"] for u in UNPRICED])))
    missing = []
    for f in sorted((HERE.parents[1] / "subsystems").glob("*/parts.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r.get("make_or_buy", "").strip().lower() == "buy" and r["part_id"][:7] not in named:
                missing.append(f"{f.parent.name}:{r['part_id']}")
    return missing


def write_outputs(tax_rate=0.1025, budget=2000.0, crash=309.0, crash_b3=227.89):
    m = money(tax_rate)
    bridge_val, deltas = bridge(tax_rate)
    assert abs(bridge_val - m["spend_pess"]) < 0.015, f"bridge {bridge_val} vs bottom-up {m['spend_pess']}"
    assert set(COVERS) >= {l["id"] for l in L}, f"COVERS misses {sorted({l['id'] for l in L} - set(COVERS))}"
    rp, rb = reserve_calc(budget, m["spend_pess"]), reserve_calc(budget, m["spend_base"])
    fp, fb = reserve_calc(budget, m["spend_pess_flight_ready"]), reserve_calc(budget, m["spend_base_flight_ready"])
    cols = ["line", "group", "part_id", "covers", "item", "vendor", "part_number", "url", "order", "qty_fitted", "qty_spare", "qty_total",
            "unit_usd", "unit_usd_pessimistic", "ext_usd", "tax_usd", "ext_incl_tax_usd", "lead_time_days", "long_lead",
            "price_status", "price_seen", "note"]
    with open(HERE / "BOM.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for l in L:
            q = l["fit"] + l["spare"]
            ext = round(q * l["unit"], 2)
            tax = round(ext * tax_rate, 2) if l["taxable"] else 0.0
            w.writerow([l["id"], l["group"], l["part"], COVERS[l["id"]], l["item"], l["vendor"], l["pn"], l["url"],
                        l["order"] + (f" (GATED {l['gate']})" if l["gate"] else ""), l["fit"], l["spare"], q,
                        f"{l['unit']:.2f}", f"{l['pess']:.2f}", f"{ext:.2f}", f"{tax:.2f}", f"{ext + tax:.2f}", l["lead"],
                        "YES" if l["long"] else "", l["status"], l["seen"], l["note"]])
        for u in UNPRICED:
            w.writerow([u["id"], u["group"], "", u["covers"], u["item"], u["vendor"], "", "",
                        u["order"] + (f" (GATED {u['gate']})" if u["gate"] else "") + " (UNPRICED)",
                        u["qty"], 0, u["qty"], "-", "-", "-", "-", "-", "", "", "-", "2026-11-13", "not in any total: " + u["note"]])

        def tot(label, val):
            w.writerow(["TOTAL", "", "", "", label] + [""] * 9 + [val])
        w.writerow([])
        tot("Goods pre-tax, baseline / pessimistic", f"{m['goods_base']:.2f} / {m['goods_pess']:.2f}")
        tot("Sales tax 10.25 %, baseline / pessimistic", f"{m['tax_base']:.2f} / {m['tax_pess']:.2f}")
        tot(f"Shipping ESTIMATE: {m['shipments']} paid shipments x $8.57 / $10.71", f"{m['ship_base']:.2f} / {m['ship_pess']:.2f}")
        tot("Pack import duty + brokerage ESTIMATE (CDR-BT-06), baseline / pessimistic", f"{DUTY_BASE:.2f} / {DUTY_PESS:.2f}")
        tot("FAA registration (not taxed)", f"{FAA_FEE:.2f}")
        tot("Lines marked GATED and UNPRICED are excluded from the at-order totals", "")
        tot("Spend at order, baseline / pessimistic (pessimistic incl. adders $27)", f"{m['spend_base']:.2f} / {m['spend_pess']:.2f}")
        tot(f"Reserve AT ORDER, baseline / pessimistic (crash line ${crash:.0f}; B3 proposal ${crash_b3:.2f}, not applied)", f"{rb:.2f} / {rp:.2f}")
        tot("Reserve FLIGHT-READY (+ X07 box and field kit + X08 airspeed sensor), baseline / pessimistic", f"{fb:.2f} / {fp:.2f}")
        tot("Reserve if every gated BOM line were bought (X07, X08, X10, X12, X13, X14), baseline / pessimistic",
            f"{reserve_calc(budget, m['spend_base_allin']):.2f} / {reserve_calc(budget, m['spend_pess_allin']):.2f}")
        tot(f"Unpriced lines (price '-', in no total): {len(UNPRICED)}", ", ".join(u["id"] for u in UNPRICED))
    by = {}
    for l in L:
        if l["gate"]:
            continue
        by.setdefault(l["vendor"], 0.0)
        by[l["vendor"]] += (l["fit"] + l["spare"]) * l["unit"]
    out = dict(money=m, reserve_pess=rp, reserve_base=rb, reserve_pess_flight_ready=fp, reserve_base_flight_ready=fb,
               crash_line=dict(current_usd=crash, b3_proposed_usd=crash_b3, b3_status="PROPOSED, needs student sign-off (CDR-SUMMARY B3)",
                               margin_at_order_current=round(rp - crash, 2), margin_at_order_b3=round(rp - crash_b3, 2)),
               shipments=["%s / %s" % c for c in shipments()], unpriced=[u["id"] for u in UNPRICED],
               bridge=dict(value=bridge_val, deltas=deltas), vendors={k: round(v, 2) for k, v in by.items()},
               by_order={o: round(sum((l["fit"] + l["spare"]) * l["unit"] for l in L if l["order"] == o and not l["gate"]), 2)
                         for o in ("EARLY", "DEC", "LOCAL")},
               reserve_pess_allin=reserve_calc(budget, m["spend_pess_allin"]), reserve_base_allin=reserve_calc(budget, m["spend_base_allin"]),
               gated={g["id"]: round(gated_net(g["id"]) * (1 + tax_rate), 2) for g in GATED},
               covers_missing=covers_check())
    (HERE / "bom_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    kit.write()
    print(json.dumps(write_outputs(), indent=1))
