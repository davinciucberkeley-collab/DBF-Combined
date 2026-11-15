# COST-TRADE: K09-L cost-driven redesign (I1)

Date 2026-11-14. Owner I1. Reproduce with `python -I team/I1/cost_trade.py` (reads `team/I1/BOM.csv`; writes nothing). No `params.json` edit, no gate, no git.
Label key: `EST` = estimate, `—` = not found, `UNVERIFIED` = seen only in a search snippet or an aggregator page, vendor page not read.

## 0. Result

| Case (pessimistic, all new, tax 10.25 %, $10.71 per shipment) | Spend | + $130 crash | vs $2,000 |
|---|---|---|---|
| Today, flight-ready (`bom_summary.json`) | 2,979.84 | 3,109.84 | +1,109.84 |
| Recommended set (section 3) | **1,847.99** | **1,977.99** | **-22.01** |

- The set closes only as a whole. All the risk 1-2 levers together reach $2,443 before the pack change; the big steps (one CNHL pack, defer the airspeed sensor, fin plugs, drop silica / microballoons, spares) take it under. There is no short list.
- The margin is $22. It rests on one unverified price (CNHL pack) and one mass pass (section 2.3). If the CNHL pack fails weigh-in and a Gens Ace is bought instead, the total is $2,046.35.
- Four requested searches found nothing cheaper that qualifies: servos (2.4), motors (2.5), charger (2.6), fin tube (2.7).

## 1. Cost model

Model (reproduces `bom_summary.json` flight-ready 2,979.84 to the cent): pessimistic line = qty_total x `unit_usd_pessimistic` x 1.1025; shipments = distinct (vendor, EARLY / DEC) groups of non-LOCAL lines, 25 today, x $10.71; + FAA $5 + tax-measure adder $7 + $0.07 rounding. Lines gated X10, X12, X13 are outside the flight-ready set. Line sum 2,700.02 + shipping 267.75 + 12.07 = 2,979.84.

Where the money sits: parts 2,700 (91 %), shipping 268 (9 %, 25 shipments). Five single-source parts (motors 220, packs 291, fin tube 168, servos 77, FC 77) are 833; X14 tools are 340.

Cost drivers in $ order: (1) single-source premium parts (pack, motor, tube, servo); (2) spares and second sets (5th motor, second ESC pack, 8 spare props, spare tubes, second pack); (3) tools bought new where the Jacobs page names no equivalent; (4) one $10.71 shipment per vendor.

| Line | Item | Vendor | Qty | Unit pess. $ | Ext. incl. tax $ | Status | Cost driver |
|---|---|---|---|---|---|---|---|
| B01 | Motor SunnySky X2814 V3 KV900 (4 fitted + 1 spare) | ReadyMadeRC | 5 | 39.99 | 220.44 | ship | 5 x $39.99 single US source; 20 % of price is the spare |
| B02 | ESC LANRC BLHeli_S 45 A 4-pack (4 fitted; the 4 spares are line B08) | Amazon | 1 | 30.00 | 33.08 | ship | ESC 4-pack (4 fitted) |
| B08 | ESC LANRC 45 A 4-pack, second pack = 4 spare ESCs (R-CRASH-REPAIR; agr | Amazon | 1 | 30.00 | 33.08 | ship | second 4-pack as spare ESCs |
| B03 | Prop APC 11x8E / 11x8EP (LP11080E, LP11080EP): 2 + 2 fitted, 4 + 4 spa | APC | 12 | 4.98 | 65.89 | ship | 12 props: 4 fitted + 8 spare |
| B05 | Prop adapter ring APC LPAR06E-type (centres the hub on the M6 post) | APC | 12 | 0.50 | 6.62 | ship | qty includes spares |
| B06 | M6 thin hex nut A4 stainless, 50-pack (prop-stack M6 post, 3.2 mm; D-1 | Zoro | 1 | 9.59 | 10.57 | ship | qty includes spares |
| B07 | Motor screw M3x8 SHCS ISO 4762 A2 (16 fitted + 4 spare) | Amazon | 20 | 0.10 | 2.21 | ship | qty includes spares |
| P01 | LiPo Gens Ace Redline Shorty 4S 6000 mAh 15.2 V HV 130C hard case (GEA | Discount RC Parts | 2 | 131.99 | 291.04 | ship | 2 x $131.99; HV 6.0 Ah 130C hard case is a premium SKU, second pack is the spare |
| A01 | Flight controller CoreWing F405 Wing APP V2 (FC + PDB 'stack') | RaceDayQuads | 1 | 69.49 | 76.61 | ship | FC + PDB stack; bdshot and 8 A BEC (F3) |
| A02 | GPS + compass HGLRC M100-5883 | RaceDayQuads | 1 | 20.49 | 22.59 | ship | flight electronics |
| A03 | Receiver RadioMaster RP3 V2 ELRS | RadioMaster | 1 | 19.99 | 22.04 | ship | flight electronics |
| A04 | Airspeed sensor Matek ASPD-4525 digital (MS4525DO, I2C) + pitot tube | GetFPV | 1 | 62.99 | 69.45 | ship | MS4525DO sensor + pitot; deferred (X08) |
| A05 | microSD card 16-32 GB (FC log) | Amazon | 1 | 6.00 | 6.62 | excluded (gate X13) | flight electronics |
| A06 | 2 x 150 mm U.FL / IPEX1 2.4 GHz T-antenna (dipole) for the RP3 V2 (D-7 | Amazon | 1 | 6.00 | 6.62 | ship | flight electronics |
| A07 | FC isolation set: alpha-gel 5 mm sheet (4 cubes), 1 mm foam tape, 10 m | Amazon | 1 | 10.00 | 11.03 | ship | flight electronics |
| M01 | Elevon servo Savox SH-0255MG+ (dealer SKU SH-0255MGP) 12 mm micro, 3.9 | AMain Hobbies | 2 | 34.99 | 77.15 | ship | 2 x $41.99; stall torque 3.9 kgf-cm at 6 V is the only part found that meets 3.49 |
| W01 | XPS FOAMULAR NGX F-250 2 in x 4 x 8 ft (about 6 wing cores) | Home Depot El Cerrito | 1 | 59.97 | 66.12 | local | one 4 x 8 ft XPS sheet, sold whole |
| W02 | Foam board 20x30 in, 10 single sheets, one brand (fins, pod shell, fir | Dollar Tree (store) | 10 | 1.25 | 13.78 | local | minimum retail pack / one-off stock |
| W03 | Carbon tube 22x20x1000 mm matte, US stock (one for C4's bend test, the | Aloft Hobbies | 1 | 24.00 | 26.46 | ship | spare 22 x 20 tube (test coupon) |
| W04 | Carbon tube 22x20x1000 mm matte, the wing spar WNG-002 (used at stock  | Aloft Hobbies | 1 | 24.00 | 26.46 | ship | wing spar |
| W10 | Carbon tube Rock West 35046-S filament-wound sanded 0.750 x 0.875 in,  | Rock West Composites | 1 | 151.96 | 167.54 | ship | $32.99/ft x 4 ft + $20 cut charge; 3 ft minimum; filament-wound is the only tube with published G |
| W11 | PTFE skived film 0.005 in (0.13 mm) x 12 in wide, 2 ft: release film u | eplastics (Estreet Pla | 2 | 7.27 | 16.03 | ship | minimum retail pack / one-off stock |
| D08 | CF tube 19 x 17 x 1000 mm roll-wrapped 3K (R&G), tube plugs FIN-006 x2 | lindinger.at (Austria) | 1 | 49.43 | 54.50 | ship | 19 x 17 mm tube, Austrian vendor: own shipment + duty exposure |
| W05 | PETG filament 1 kg (Ambrosia) | West3D | 1 | 20.99 | 23.14 | ship | minimum retail pack / one-off stock |
| W06 | Packing tape Scotch Heavy Duty, 6 rolls | Amazon | 1 | 19.98 | 22.03 | ship | minimum retail pack / one-off stock |
| W07 | Foam-safe glue (UHU Por / Gorilla clear) | Amazon | 1 | 12.99 | 14.32 | ship | minimum retail pack / one-off stock |
| W09 | Filament (strapping) tape Scotch 893, 3/4 in x 60 yd (TPU cap wraps, E | Staples (store) | 1 | 17.99 | 19.83 | local | minimum retail pack / one-off stock |
| G16 | Spray adhesive 3M Super 77, 13.8 oz (fin board lamination D-26; FIN-10 | Home Depot El Cerrito | 1 | 13.28 | 14.64 | local | minimum retail pack / one-off stock |
| G17 | LiPo sand bucket: play sand 50 lb (Tractor Supply) + 5 gal bucket (Hom | Tractor Supply / Home  | 1 | 13.97 | 15.40 | local | ground kit |
| G18 | Hover tether: 550 paracord 100 ft + 12 steel U-stakes 0.4 x 12 in (two | Tractor Supply / Home  | 1 | 34.67 | 38.22 | local | tether, 100 ft cord + 12 stakes |
| G14 | Handheld anemometer BTMETER BT-100 (card 1d, R-WIND-MEASURE, three RFS | eBay (BTMETER BT-100) | 1 | 35.99 | 39.68 | ship | anemometer, own eBay shipment |
| H01 | Harness parts (F2 parts.csv HRN-103..106, 108, 109): 26 AWG servo exte | Amazon / DigiKey | 1 | 41.00 | 45.20 | ship | 6 purchases in one line, all EST |
| H02 | Mechanisms hardware (D6 parts.csv): Du-Bro 2-56 rod + steel clevises $ | Amazon / hobby shop | 1 | 24.00 | 26.46 | ship | small parts, minimum retail pack |
| H03 | Charger-side XT60 pair for the AS150U charge adapter + 0.3 m 10 AWG st | Amazon | 1 | 5.00 | 5.51 | ship | small parts, minimum retail pack |
| H06 | Amass XT60H male + female, 5 sets (10 pcs) (4 fitted: one per ESC pair | GetFPV | 5 | 1.80 | 9.92 | ship | small parts, minimum retail pack |
| H07 | Board-link ribbon: male pin-header strip 1 x 40 + 10-way 28 AWG ribbon | DigiKey / Amazon | 1 | 3.00 | 3.31 | ship | small parts, minimum retail pack |
| F01 | Amass AS150U connector pair (male + female) x 5: aircraft, 2 packs, ch | Amazon | 5 | 5.00 | 27.56 | ship | minimum retail pack |
| F02 | Silicone wire 10 AWG red + black 0.3 m each (PWR-104) + 8 AWG 0.1 m ea | Amazon | 1 | 8.00 | 8.82 | ship | minimum retail pack |
| F03 | Silicone wire 16 AWG red + black + yellow, 3 m each (HRN-101); second  | Amazon | 2 | 14.00 | 30.87 | ship | minimum retail pack |
| F04 | Silicone wire 20 AWG red + black, 1 m each | Amazon | 1 | 4.00 | 4.41 | excluded (gate X12) | minimum retail pack |
| F05 | UBEC 6 V, 8 A class (Hobbywing type) | Amazon | 1 | 18.00 | 19.84 | excluded (gate X12) | minimum retail pack |
| F06 | Mini blade fuse 5 A x 3 + inline holder | Amazon | 1 | 6.00 | 6.62 | excluded (gate X12) | minimum retail pack |
| F07 | Capacitor Rubycon 35PZJ560M10X15 560 uF 35 V polymer, 3 per ESC (12 fi | DigiKey | 13 | 3.03 | 43.43 | ship | 13 caps, 22 week lead |
| F08 | FR4 1.6 mm 1 oz copper sheet 100 x 70 mm (bus board PWR-004 / PWR-105; | Amazon | 1 | 3.00 | 3.31 | ship | minimum retail pack |
| F09 | Adhesive-lined 3:1 heat-shrink assortment 2.4-9.5 mm (HRN-107; also F1 | Amazon | 1 | 9.00 | 9.92 | ship | minimum retail pack |
| C01 | M3 steel A2 kit: SHCS M3x16 x6 (D3 pinch bolts), nyloc x8, washer x12  | Amazon | 1 | 5.00 | 5.51 | ship | small parts, minimum retail pack |
| C06 | M3 nylon PA66 set: socket-head M3x18 x11, M3x16 x3 + hex nut x3, 1.0 m | Amazon | 1 | 7.00 | 7.72 | ship | small parts, minimum retail pack |
| C02 | M3 x 5.7 brass heat-set inserts x12 + M3 nylon washers / FC grommets x | Amazon | 1 | 9.00 | 9.92 | ship | small parts, minimum retail pack |
| C03 | Pultruded CF rod 2.5 mm x 1 m x 2 (one + spare): strip through-pins at | Amazon | 2 | 3.50 | 7.72 | ship | small parts, minimum retail pack |
| C04 | Loctite 243 (10 ml) + paint pen (torque witness) | Amazon | 1 | 9.00 | 9.92 | ship | small parts, minimum retail pack |
| C05 | Epoxy 30 min, 9 oz (Bob Smith Industries BSI-206 SlowCure 30 min) | AMain Hobbies | 1 | 22.99 | 25.35 | ship | 9 oz epoxy, smallest practical pack |
| C07 | Colloidal silica West System 406-2, 1.7 oz (fillet and bond thickener) | Freeport Marine | 1 | 20.67 | 22.79 | ship | small parts, minimum retail pack |
| C08 | Glass microballoons (microspheres) #22-A, 1/2 gal (WNG-006 lip beads,  | Fibreglast | 1 | 17.95 | 19.79 | ship | small parts, minimum retail pack |
| D01 | Pultruded CF strip 10 x 2 x 1000 mm x 1 (4 braces, FIN-009) | Aloft Hobbies | 1 | 10.00 | 11.03 | ship | strip |
| D02 | Pultruded CF strip 10 x 1 x 1000 mm x 3 (8 edge strips) | Aloft Hobbies | 3 | 6.00 | 19.84 | ship | minimum retail pack / one-off stock |
| D07 | Brass tube 7/32 in OD K&S x 1 (cartridge bore cutter GER-013, shop too | Amazon / hobby shop | 1 | 3.00 | 3.31 | ship | minimum retail pack |
| D04 | 10 mm hook-and-loop straps x 10 (ESC retention x4, spares) | Amazon | 1 | 8.00 | 8.82 | ship | minimum retail pack / one-off stock |
| D05 | Neoprene sheet 1/16 in 40A adhesive back 12 x 12 in | Amazon | 1 | 12.00 | 13.23 | ship | minimum retail pack |
| D06 | Pack straps 20 x 300 mm hook-and-loop rubber-backed x2 + 2 EVA shims ( | Amazon | 1 | 7.00 | 7.72 | ship | minimum retail pack |
| W08 | ASA filament 1 kg (motor mounts FIN-003, ESC pads FIN-007; D-42) | West3D | 1 | 24.99 | 27.55 | ship | minimum retail pack / one-off stock |
| T01 | Box shell: 4 x Home Depot XLBX 24 x 20 x 21 in moving boxes (cut into  | Home Depot El Cerrito | 4 | 3.48 | 15.35 | local | X07 box and field kit |
| T02 | Packaging tape Scotch 3350-RD 1.88 in x 54.6 yd, 1 roll (box panels, c | Home Depot El Cerrito | 1 | 5.51 | 6.07 | local | X07 box and field kit |
| T04 | Field pouch + 10 mm prop spanner (D-40) | Home Depot El Cerrito | 1 | 1.80 | 1.98 | local | X07 box and field kit |
| T05 | Landing mat 0.8 x 0.8 m: 3 mm birch ply (Jacobs stock) + 1.5 mm rubber | Home Depot El Cerrito | 1 | 25.00 | 27.56 | local | landing mat |
| T06 | Walmart polyethylene foam sheet 2-count, 16 x 12 x 2 in (cradle column | Walmart (store) | 1 | 15.96 | 17.60 | local | foam cradle |
| T07 | Field tote about 0.45 x 0.35 x 0.25 m (TX, landing-spares box, flight  | Home Depot El Cerrito | 1 | 8.00 | 8.82 | local | X07 box and field kit |
| H05 | Hot-wire bow/jig + airfoil template stock | Home Depot El Cerrito | 1 | 15.00 | 16.54 | local | small parts, minimum retail pack |
| R01 | Transmitter RadioMaster Pocket Crush ELRS | RaceDayQuads | 1 | 84.49 | 93.15 | ship | ELRS handset, Crush variant premium over plain Pocket |
| R02 | 18650 cells, 2-pack for the Pocket (not included) | RaceDayQuads | 1 | 24.49 | 27.00 | ship | flight electronics |
| G01 | Charger HTRC C150 150 W AC | Amazon | 1 | 56.99 | 62.83 | ship | >= 6 A LiHV AC charger; no cheaper qualified part found |
| G02 | LiPo bag x2 | RaceDayQuads | 2 | 9.99 | 22.03 | ship | 2 bags (1 per pack) |
| G03 | Ammo can (Harbor Freight 63750) | Harbor Freight | 1 | 19.99 | 22.04 | local | ground kit |
| G04 | Watt meter 150 A | Amazon | 1 | 12.99 | 14.32 | ship | ground kit |
| G05 | IR thermometer | Amazon | 1 | 8.98 | 9.90 | ship | ground kit |
| G06 | Thrust stand: 20 kg load cell + HX711 + Nano | Amazon | 1 | 17.97 | 19.81 | ship | ground kit |
| G10 | Flux + desoldering wick (fallback only: the Electronics Lab stations s | Amazon | 1 | 15.00 | 16.54 | excluded (gate X10) | ground kit |
| G11 | Hot-wire: NICE-POWER 30 V 10 A supply + Ni80 24 AWG | Amazon | 1 | 41.73 | 46.01 | ship | 30 V 10 A bench supply for the hot wire |
| G12 | Ground-test additions: 1 kgf bar cell + HX711 (torque arm) + 5 K-type  | Amazon | 1 | 17.00 | 18.74 | ship | test gear |
| G13 | 2 foil strain gauges 350 ohm (pack of 5-10) + cyanoacrylate gauge kit, | Amazon | 1 | 9.00 | 9.92 | ship | test gear |
| K01 | Adjustable torque screwdriver 0.5-6 in-lb (0.056-0.68 N m), 1/4 in hex | MariTool | 1 | 70.45 | 77.67 | ship | torque driver, 1 of 1 |
| K02 | Pocket scale 200 g x 0.01 g | Amazon | 1 | 9.99 | 11.01 | ship | X14 tool, bought new |
| K03 | Kitchen scale 5 kg x 1 g (Etekcity EK6015) | Walmart (store) | 1 | 13.99 | 15.42 | local | X14 tool, bought new |
| K04 | Digital angle gauge / inclinometer (Wixey WR300 Type 2) | Woodcraft (store) | 1 | 34.99 | 38.58 | local | angle gauge, store |
| K05 | Z-bend pliers (Hangar 9 Z-Bender) | Hillsborough Hobby | 1 | 26.99 | 29.76 | ship | single-use pliers, own shipment |
| K06 | Prop balancer BenchCraft precision balancer | Motion RC | 1 | 19.00 | 20.95 | ship | balancer, own shipment |
| K07 | Hex driver set 1.5 / 2.0 / 2.5 / 3.0 mm (RDQ edition; ball-end not con | RaceDayQuads | 1 | 11.99 | 13.22 | ship | X14 tool, bought new |
| K08 | TPU 95A filament 1.75 mm (Overture, 1 kg; 1.5 g needed for the two GER | Overture | 1 | 28.99 | 31.96 | ship | 1 kg spool for 1.5 g of TPU |
| K09 | Hobby knife blades X-Acto #11, 100-pack | Staples (store) | 1 | 28.89 | 31.85 | local | 100-pack of blades, 10 needed |
| K10 | Sandpaper 3M Pro Grade 80/150/220 assorted 6 sheets (no 120-400 assort | Home Depot El Cerrito | 1 | 11.48 | 12.66 | local | X14 tool, bought new |
| K11 | Mixing cups 8 oz graduated, 50-pack | Walmart (store) | 1 | 4.97 | 5.48 | local | X14 tool, bought new |
| K12 | Isopropyl alcohol 99 %, 32 oz | Tractor Supply | 1 | 14.99 | 16.53 | ship | X14 tool, bought new |
| K13 | Digital caliper 150 mm (Pittsburgh item 63711), also the FIN-002 OD re | Harbor Freight (store) | 1 | 22.99 | 25.35 | local | X14 tool, bought new |
| K14 | Nitrile gloves, box of 100 | Harbor Freight (store) | 1 | 7.99 | 8.81 | local | X14 tool, bought new |
| U08 | Landing-spares box, any 1 L food container (TRN-108) | team stock | 1 | - | — | unpriced | X07 box and field kit |
| U02 | Clear tape 100 mm wide (BUILD-GUIDE consumables) | - | 1 | - | — | unpriced | minimum retail pack / one-off stock |
| U05 | Servo tester, 3-channel | - | 1 | - | — | unpriced | X14 tool, bought new |
| U06 | 1 m steel rule, depth gauge, pin vise, drills 1.85 / 2.5 / 3.4 / 8 mm, | - | 1 | - | — | unpriced | X14 tool, bought new |
Unpriced (`—`, in no total): U02, U05, U06, U08. Gated X10 / X12 / X13 lines are listed but excluded from every total here.

## 2. Ranked cost reductions

Risk score (I1 judgement, not a measurement): 1 = purchasing or paperwork only; 2 = one role re-checks a number, no margin changes; 3 = a claim margin, schedule or test capability changes; 4 = a flight mass or limit changes and acceptance moves to a weigh-in; 5 = a structural claim can fail. Rank = $ saved / risk. Prices are pessimistic, tax and removed shipments included, priced by `cost_trade.py`. "Standalone" = against today's $2,979.84. P1 / P2 / P3, D1 / D2 and S5 / F1 are alternatives.

| # | Lever | $ saved (standalone) | Risk | $ / risk | Roles that re-check |
|---|---|---|---|---|---|
| 1 | J1 Jacobs pliers + hex keys replace K05, K07 | 53.69 | 1 | 53.69 | I1 + Jacobs staff (written yes), D6, D3 |
| 2 | P3 one flight pack, CNHL LiHV 6000 | 213.88 | 4 | 53.47 | E2, A3, B1, H2, A2, F1 |
| 3 | E-small: one LiPo bag 11.02, one 16 AWG reel 15.43, no H05 bow 16.54, no tote 8.82 | 51.81 | 1 | 51.81 | F2, D1, D7 |
| 4 | P1 one Gens Ace pack (alternative to P3) | 145.52 | 3 | 48.51 | E2, H2, A2 |
| 5 | P2 two CNHL packs (alternative) | 136.71 | 3 | 45.57 | E2, A3 |
| 6 | T1 lever-arm torque, no K01 | 88.38 | 2 | 44.19 | C6, D3 |
| 7 | T2 phone inclinometer, no K04 | 38.58 | 1 | 38.58 | D5, H1 |
| 8 | A1 defer airspeed sensor | 80.16 | 3 | 26.72 | F4, B4, B3, F3 |
| 9 | A2 no BTMETER anemometer | 50.39 | 2 | 25.20 | H2, H3 |
| 10 | S3 props 8 total, adapters 8 total | 24.18 | 1 | 24.18 | E1, A2 |
| 11 | K9 blades 2 x 5-pack | 23.52 | 1 | 23.52 | I1 |
| 12 | E4 no landing mat / foam cradle (T05, T06) | 45.16 | 2 | 22.58 | D7 |
| 13 | S1 no 5th motor | 44.08 | 2 | 22.04 | E1, A2 |
| 14 | X1 plain Pocket ELRS at $64.99 | 21.50 | 1 | 21.50 | F5 |
| 15 | X2 no silica / microballoons (X14) | 64.00 | 3 | 21.33 | D3, D1, C6 |
| 16 | D1 fin plug: hardwood dowel, not D08 | 57.74 | 3 | 19.25 | D3, A3, C4 |
| 17 | F1 fin tube INFINITubeV twill 36 in (not recommended) | 82.66 | 5 | 16.53 | C4, C2, D3 |
| 18 | T3 DIY prop balancer, no K06 | 31.66 | 2 | 15.83 | E1, H1 |
| 19 | T4 no TPU spool K08 | 42.67 | 3 | 14.22 | D5, C5 |
| 20 | C2 packing tape for PTFE film | 26.74 | 2 | 13.37 | D3, C2 |
| 21 | S4 no spare 22 x 20 tube (W03) | 26.46 | 2 | 13.23 | C2, C4 |
| 22 | S5 Rock West tube 36 in, no spare | 36.38 | 3 | 12.13 | C4, A2 |
| 23 | D2 plug tube from eBay US $28.56 (alternative to D1) | 23.01 | 2 | 11.51 | D3, A3 |
| 24 | S2 no second ESC 4-pack | 33.08 | 3 | 11.03 | F1, E2 |
| 25 | H1 hot wire from a pack | 21.59 | 2 | 10.79 | D1, E2, F1 |
| 26 | C1, C3, C4, C5 cart merges (each) | 10.71 | 1 | 10.71 | I1 |
| 27 | E1 SpeedyBee FC (not recommended) | 23.70 | 3 | 7.90 | F3 |
| 28 | S6 caps 9, not 13 | 13.36 | 2 | 6.68 | F1 |
| 29 | Servos, motors, charger, fin tube: no qualified saving found | 0 | - | - | - |

### 2.1 Jacobs-provided tools (J1, T1, T2, T3)

Source: Jacobs Institute "Labs and Equipment", https://jacobsinstitute.berkeley.edu/our-spaces-at-a-glance/labs-and-equipment/ (fetched 2026-11-14). Named there: "hand tools" (pliers, screwdrivers, wrenches, hammer, balance ruler, measuring tape, allen wrench), soldering irons, multi-meters, oscilloscopes and power supplies, heat guns, drill presses, laser cutters, Prusa 3D printers, "PLA filament", plywood, acrylic, "heat tube material", "carbon fiber reinforcement". A search result of 2026-11-14 also says the Jacobs Hall Material Store sells materials to Maker Pass holders "at low cost" (prices not seen: `—`). The Makers Pass page https://jacobsinstitute.berkeley.edu/makers-pass/ returned 404 on 2026-11-14, so the pass terms were not read; the pass fee is outside the budget per CLAUDE.md. "Named" is not "free to take": hand tools are shop-use, the Material Store is not free.

Not named on the page: torque driver, calipers, scales, a hex driver set (a hex key is listed), prop balancer, IR thermometer, hot-wire cutter, angle gauge, TPU filament. Those stay bought new unless a lever below removes them.

- J1: K05 Z-bend pliers (29.76 + own shipment 10.71) and K07 hex driver set (13.22) go: generic pliers and hex keys from the Jacobs hand-tool wall. Saves 53.69. Needs a written yes from Jacobs staff (the page promises no bit sizes). D6 re-checks that the Z-bend can be made with round-nose pliers; D3 that a 2.0 / 2.5 mm key reaches the cheek bolts.
- T1: C6's lever-arm torque method (a known mass on a known arm, using items already bought) replaces K01, the MariTool driver. Saves 88.38. C6 restates the tolerance (the driver reads 0.056-0.68 N m; an arm method is about +/-10 % `EST`). Torque-witness paint (C04) stays.
- T2: a phone inclinometer replaces K04 Wixey (38.58, store). A phone reads about +/-0.2 deg `EST` (no source); the cant is 10 deg (D-164). D5 / H1 confirm that is enough for the cant and pad-friction checks.
- T3: a balancer from a 6 mm rod on two razor blades or bearings (Jacobs hand tools) replaces K06 (20.95 + shipment 10.71 = 31.66). H1 / E1 re-check that imbalance is resolved to what the rpm limit needs (limit owned by B4).
- Hot-wire power supply: the Jacobs page lists "power supplies" with no rating; not relied on, see 2.9.
- Already out of the BOM: G07-G09 (Electronics Lab); G10 flux (gated X10).

### 2.2 Minimum spares (S1-S6)

The $130 crash line (`crash_cost_usd`, A2 D-160) pays for losses, so spares bought now are paid twice. A2 re-bases the crash cost for the new pack (2.3).

| Lever | Change | Saves | Effect |
|---|---|---|---|
| S1 | 4 motors, no 5th (B01 5 -> 4) | 44.08 | A motor loss draws about $44 from the reserve and waits for a 14 d `EST` delivery (stock on the listing is mixed). E1 / A2 |
| S2 | no second ESC 4-pack B08 | 33.08 | An ESC loss means a 4-pack ($33.07) from the reserve; F1 / E2 |
| S3 | props 12 -> 8, adapters 12 -> 8 | 24.18 | 4 fitted + 4 spare; E1 / A2 |
| S4 | delete W03 spare 22 x 20 tube | 26.46 | No tube for C4's bend test: C4 uses a W04 offcut or a coupon; C2 / C4 |
| S5 | W10 48 in -> 36 in | 36.38 | Loses the third 344 mm tube that A2 closure 2.4 counts as the fin-tube spare. One fin-tube loss then costs about $119 + tax with a 2-4 week backorder, which the $130 reserve covers only if nothing else is lost |
| S6 | Rubycon caps 13 -> 9 | 13.36 | 12 fitted (3 per ESC) + 1 spare today. 9 = 2 per ESC + 1 spare. F1 says whether 2 per ESC meets the ripple limit; if not, drop S6 (the set rises 13.36, margin falls to 8.65) |

DigiKey lists the Rubycon cap at a 22 week lead (I1 R7): 2026-11-14 + 22 weeks is mid-April 2027, the end of the build window. That is a schedule problem apart from cost; F1 should name a stocked 35 V polymer 560 uF equivalent.

### 2.3 One flight pack vs two, and a cheaper pack (P1, P2, P3)

Requirement (E2): >= 5.7 Ah, >= 80 A, 10 AWG-capable leads, mass <= the acceptance line (`CL-A3-PACK-ACCEPT`, which moved 526.5 -> 497.9 -> 485.6 g during the round; the Gens Ace passes it at 462 g worst case, +23.6 g).

| Pack | Ah | Mass | Lead | Price each | Source (date) | Qualifies |
|---|---|---|---|---|---|---|
| Gens Ace Redline Shorty 4S 6000 HV 130C (today) | 6.0 | 447-448 +/-10 g (E2 worst case 462 g with pigtails) | 10 AWG pigtails | 127.99 / 131.99 | https://buddyrc.com/products/gens-ace-redline-6000mah-15-2v-130c-4s1p-hard-case-hv-lipo-battery ; https://store.hobbyetc.com/parts/view/140376 ($131.99, 2 in stock, snippet) (2026-11-14) | yes (E2 PASS) |
| CNHL LiHV 4S 6000 120C hard case EC5 | 6.0 | about 479 g, tolerance not stated (E2 section 3) | 10 AWG (one snippet) | $69.99 list, $49.99 sale, "ship from US" (snippet) | https://chinahobbyline.com/products/cnhl-lihv-6000mah-15-2v-4s-120c-hv-hard-case-lipo-battery-with-ec5-plug (2026-11-14; fetch returned HTTP 429, price `UNVERIFIED`) | mass +6.6 g margin at 479 g, -3.4 g at +/-10 g `EST`; lead `UNVERIFIED` |
| Ovonic 4S 6000 50C | 6.0 | 531 g | 12 AWG | 53.99 | https://us.ovonicshop.com/products/ovonic-50c-14-8v-6000mah-4s1p-deans-lipo-battery | no (mass, lead) |
| Zeee 4S 6000 60C soft | 6.0 | 573 g | — | 75.99 | https://zeeebattery.com/products/zeee-4s-lipo-battery-6000mah-14-8v-60c-deans-plug | no |

- P3 (one CNHL, priced at the pessimistic $69.99, not the $49.99 sale) saves 213.88 against today's two Gens Ace. EST effect on the aircraft: +27 g against the Gens Ace (479 vs 452 g, E2's figures), 1 % of the 2.64-2.70 kg gate; hover power about +1.5 % (power goes as m^1.5, `EST`); pack energy is the same 6.0 Ah HV. A3 re-runs CG (pack station -0.0545 m, D-174) and `CL-A3-PACK-ACCEPT`. Acceptance must be a weigh-in on arrival; E2 sets the number. F1 re-terminates the EC5 lead to AS150U (F01).
- One pack means one flight per recharge: about 30 min at 6 A for 3.0 Ah used (`EST`; `BATT_LOW_MAH` 3,100). H2 / H3 reschedule the flight cards. Losing the only pack stops flying until the next shipment. One CNHL replacement is 77.16 with tax, inside the $130 reserve; a one-pack Gens Ace replacement is 145.52, which exceeds it (A2 re-bases, as in I1 R7).
- P1 (one Gens Ace) keeps E2's qualified part, but saves 68.36 less than P3; the set then totals $2,046.35 unless 2.7 finds another $46.
- P2 (two CNHL) saves 136.71 and keeps the second pack; alone it does not close the gap.
- E2 owns the pack qualification; I1 only prices it.

### 2.4 Cheaper servos (no saving found)

Requirement: `requirements.servo_torque_factor` 1.5 x B2's hinge moment (`CL-B2R3-HINGE-VD-FULL` 0.440 N m per servo, 25 deg, VD 27.2 m/s) through D6's linkage gives 3.49 kgf-cm (`CL-B2R3-SERVO-TORQUE-REQ`), against 3.9 kgf-cm at 6 V for the Savox SH-0255MG+ (+11 %); the servo rail stays 6 V; 12 mm pocket.

| Candidate | Torque | Price | Verdict |
|---|---|---|---|
| Savox SH-0255MG+ (today) | 3.9 kgf-cm at 6 V | 34.99 / 41.99 | passes, +11 % |
| Emax ES3054 17 g | "3.5 kg" in one snippet, voltage not given | 9.99-13.99 | +0.3 % at best, voltage unknown, 17 g and pocket not checked: no. https://www.racedayquads.com/products/emax-es3054-17g-metal-gear-digital-servo (snippet 2026-11-14; page fetch 429) |
| Hitec HS-5055MG | 22 oz-in = 1.58 kgf-cm at 6 V | 17.99-29.95 | fails by 55 % |
| Savox SH-0257MG | 2.2 kgf-cm at 6 V | 39.99 | fails, dearer |
| Miuzei 12 g metal | 2.0 kgf-cm | 9.99 | fails |
| KST X12-508 | 6.2 kgf-cm at 8.4 V | 68.99 | dearer, needs 8.4 V |
| Emax ES3352 / HV | — | 12.15-15.99 | no torque found |

The most an ES3054-class servo could save is 2 x (41.99 - 13.99) x 1.1025 = 61.74 `EST`; I do not count it. B2 / D6 would first need a 6 V stall rating >= 3.49 with margin and the pocket size.

### 2.5 Cheaper motors / props (no saving found)

X2814 class: >= 0.305 N m continuous, 4S, 11 in props.

| Candidate | Data | Price | Verdict |
|---|---|---|---|
| SunnySky X2814 V3 900 KV (today) | 11 in props recommended on 4S (Buddy RC listing) | 39.99 | baseline. https://www.readymaderc.com/products/details/sunny-sky-x-series-v3-x2814-brushless-motor-900kv (2026-11-14) |
| SunnySky X2814, Alibaba | no thrust table | 26.50-36.96, MOQ 3 | not used: import, duty, lead, no US stock |
| T-Motor AS2814 900 KV | data at 7.5 in / ~29.6 V | 42.99 (Lumenier) | dearer, data not at 4S / 11 in |
| iFlight XING 2814 | KV not seen | 38.99 | no saving, no 4S / 11 in data |
| Emax ECO II 2814 730 / 830 KV | 6S data | 54.56, sold out | no |

Prop: APC 11x8E / EP at 4.17 is already the cheap part; no cheaper prop or pairing with published data was found (`—`). The saving here is the 5th motor (S1).

### 2.6 Transmitter and charger (X1; no charger saving)

- Transmitter: plain RadioMaster Pocket ELRS $59.99 at RadioMaster, $64.99 at ReadyMadeRC, $71.49 at GetFPV / RaceDayQuads (aggregator https://www.diyfpv.com/catalog/radiomaster-pocket-radio-controller, 2026-11-14; the ELRS vs CC2500 version must be confirmed on the vendor page; `UNVERIFIED`). Today's R01 is the Crush variant at 84.49 (RDQ snippet). X1 prices it at the ReadyMadeRC $64.99 pessimistic and merges it into the motor shipment: saves 21.50. F5 re-checks the EdgeTX model file and the ELRS module output. Jumper T-Lite: no price found (`—`); RadioMaster Zorro $145.99, dearer.
- Charger: HTRC C150 $56.99 stays. SkyRC e455 is 50 W and 1-4 A (https://motionrc.com/collections/battery-chargers/products/skyrc-e455-multi-chemistry-4-cell-4s-lipo-battery-charger-sk-100170-03, search 2026-11-14): at 4S LiHV (17.4 V) 50 W gives about 2.9 A `EST`, not 6 A, so it fails the >= 6 A line. An option only if H2 accepts about an hour per recharge: saves about 34 (the e455 $25.99 is from I1 R7; page not re-read).

### 2.7 Fin tube (F1, D1, D2, S5)

C4 requires E >= 78.6 GPa and G >= 10.27 GPa at the knock-down for the current braced fin (`CL-C4-SIM-SEP-KNOCK` >= 0.20, 0.2045 with the D3 R7 cheeks). Today's tube is Rock West 35046-S, 0.750 x 0.875 in, filament-wound (G is published; roll-wrapped tubes do not publish G).

- Cheapest similar-size alternative found: Rock West INFINITubeV twill 0.750 x 0.856 x 36 in, $76.99 at 1-9 (https://www.rockwestcomposites.com/46404-l36.html, search snippet 2026-11-14; no E or G published, `—`). Section ratio against 35046-S: (0.856^4 - 0.750^4) / (0.875^4 - 0.750^4) = 0.82 `EST` (wall 0.053 vs 0.0625 in). For equal EI the modulus would need 78.6 / 0.82 = 96 GPa and G about 12.5 GPa, above any value I found for a standard-modulus twill tube (`EST`). I do not recommend F1; it is not in the set.
- Plug tube D08 (19 x 17 mm, lindinger.at, 54.50 + a shipment, duty exposure): D2 US eBay $28.56 (I1 L8, ship-from unconfirmed) saves 23.01. D1, a 3/4 in hardwood round dowel ($6.78 Builder's Choice oak, Home Depot, snippet 2026-11-14; El Cerrito stock not seen), saves 57.74. EST effect of D1: two plugs of 53 mm, about 10 g each in oak vs about 5 g for the CF tube, so about +10 g on the two fins; the bolt bearing and glue line differ from a thin-wall tube (D3 / C4).

Questions for C4 (not decided here):
1. Does a shorter tube span (cantilever bending stiffness goes as 1 / L^3, so 10 % shorter is about +37 % `EST`) or a bigger brace (10 x 3 mm gave +0.37 % at nominal for +9 g, C4.md) let a lower E / G tube pass `CL-C4-SIM-SEP-KNOCK`? C4's mount-stiffness numbers (k_est 2259 vs 1642 N m/rad needed) suggest the mount, not the tube, drives f1: say how much of the margin is tube EI and GJ.
2. What is the minimum E and G (GPa) that still gives >= 0.20 with a brace or span change? If it is under about 60 / 5 GPa, a roll-wrapped twill at about $77 becomes a candidate; if not, the tube is a fixed cost.
3. Is a delivered-tube coupon test (G12 / G13 strain gauges are in the BOM) acceptable for a cheaper tube, with the 35046-S bought only if the coupon fails?

### 2.8 Airspeed sensor (A1)

- Today A04 Matek ASPD-4525 (MS4525DO) $62.99 pessimistic; GetFPV $49.99, Holybro MS4525DO PT40 kit about $58 (spexdrone), epicfpv $73.99 (snippets 2026-11-14); one Matek listing is marked discontinued. No cheaper sensor with ArduPilot support found; SDP3x / DLVR kits: no price (`—`). The $49.99 listing would save about 14.3 `EST`; the pessimistic price stays $62.99.
- A1 buys none now and flies on the EKF wind / synthetic airspeed estimate (`ARSPD_TYPE` 0; F4 to confirm for this firmware and vehicle). Saves 80.16 (sensor 69.45 + the GetFPV shipment). Hover is unaffected. Fixed-wing tune, TECS, stall protection (B4 `AIRSPEED_MAX` 18) and B3's transition window need a speed estimate: F4 / B4 / B3 must show the synthetic one is enough. If not, the sensor is re-bought for $80.16 and the set is $58.15 over, so another lever must return.

### 2.9 Hot wire from a pack (H1)

Ni80 24 AWG is 1.61 ohm/ft = 5.3 ohm/m (https://ibspot.com/products/nichrome-80-100-24-gauge-resistance-wire-b07cj2jg6d_ca_fwd_040225_hq, 2026-11-14). A 0.6 m wire is about 3.2 ohm: on a 4S pack at 14.8-16.8 V that is 4.6-5.3 A, 70-90 W `EST` (a reviewer on the Amazon-mirror listing says 12 V 5 A cut foam). A 4S pack replaces the $41.73 bench supply (G11, 46.01 with tax) and only the wire is kept: Zoro 100 ft Remington Ni80 24 AWG at $22.15 (https://zoro.com/remington-industries-nickel-chromium-resistance-wire-nichrome-80-24-awg-100-length-00201-diameter-silver-24n80100/i/G801911496, 2026-11-14) is used as a conservative cost for the wire. Saves 21.59. D1 sets wire length and a fuse; E2 / F1 accept a pack at about 5 A for minutes (about 0.1-0.2 Ah per core `EST`); use a retiring pack, never the flight pack. A 10 A fuse is needed (F06's 5 A fuse is gated; 10 A fuse price `—`).

### 2.10 Shipping and vendors (C1-C5)

Shipping is $267.75 (25 x $10.71 pessimistic; the baseline model is $120-137).

| Merge | Saves | Condition |
|---|---|---|
| C1 XT60H singles into the RDQ cart (GetFPV out) | 10.71 | RDQ lists the part (I1 L9) |
| C3 M6 thin nut from Amazon, not Zoro | 10.71 | same price `EST`; E1 / D3 confirm the thin nut and A4 stainless |
| C4 PETG + ASA from Amazon, not West3D | 10.71 | same price `EST`; not looked up |
| C5 Amazon DEC lines into the November cart | 10.71 | later-dated lines bought early |
| C2 packing tape for PTFE film (no eplastics shipment) | 26.74 | D3 / C2 confirm release behaviour of tape on the cure |
| X1 transmitter into the ReadyMadeRC shipment | in X1 | |

After the set, 11 shipments remain (25 today). Not tried: Amazon free-shipping threshold (ORDER-PLAN.md mentions thresholds; not re-read), APC props through Amazon (no listing seen).

### 2.11 Other priced items

- X2 silica (22.79) and microballoons (19.79), both X14: bond-line fillers (FIN-105, WNG-006). Saves 64.00 including two shipments. D3 / D1 / C6 name a substitute (chopped fibre or cotton flock in the same epoxy; Jacobs lists "carbon fiber reinforcement", price `—`) and check bond-line strength.
- T4 TPU: print the two GER-007 caps in Jacobs PLA or PETG, or use the neoprene D05 already in the BOM. Saves 42.67. D5 / C5 re-check landing compliance and loads. Jacobs lists PLA only.
- K9: 2 x 5-pack #11 blades at $3.78 each (Walmart, snippet 2026-11-14) instead of the 100-pack. Saves 23.52.
- A2 anemometer: a phone wind app replaces the BTMETER (I1 R7 M4). H2 / H3 say whether the field wind limit can use a phone reading (accuracy `—`).
- E4: T05 landing mat and T06 foam cradle go. T05's plywood is Jacobs stock already. D7 confirms the box still holds the aircraft in its 1.25 x 0.55 x 0.45 m envelope.

## 3. Minimum set and re-checks

Cumulative spend, pessimistic, tax and removed shipments included (`cost_trade.py` prints the same):

| Step | Cum. spend $ | Step | Cum. spend $ |
|---|---|---|---|
| Today | 2,979.84 | A2 no anemometer | 2,610.31 |
| J1 Jacobs pliers + hex keys | 2,926.15 | S1 no 5th motor | 2,566.23 |
| T2 phone inclinometer | 2,887.57 | S4 no W03 | 2,539.77 |
| X1 Pocket ELRS $64.99 | 2,866.07 | H1 hot wire from pack | 2,518.18 |
| S3 props 8 / adapters 8 | 2,841.89 | E11 no H05 bow | 2,501.64 |
| C1, C3, C4, C5 carts | 2,799.05 | C2 tape for PTFE | 2,474.90 |
| K9 blades | 2,775.53 | T3 DIY balancer | 2,443.24 |
| E6 one bag, E2 one reel | 2,749.08 | **P3 one CNHL pack** | 2,229.36 |
| T1 lever-arm torque | 2,660.70 | A1 defer airspeed | 2,149.20 |
| T4 no TPU | 2,106.53 | S2 no 2nd ESC pack | 2,073.45 |
| S6 caps 9 | 2,060.09 | S5 tube 36 in | 2,023.71 |
| D1 dowel plugs | 1,965.97 | X2 no silica / microballoons | 1,901.97 |
| X3 no tote | 1,893.15 | E4 no mat / cradle | **1,847.99** |

**1,847.99 + 130 = 1,977.99, $22.01 under $2,000.**

What each role re-checks:

| Role | Re-check |
|---|---|
| E2 | CNHL pack: mass vs `CL-A3-PACK-ACCEPT` at listed +/- tolerance, lead gauge, EC5 to AS150U; weigh-in number; pack IR; one-pack energy (`BATT_LOW_MAH`) |
| A3 | +27 g EST at the pack, CG (pack -0.0545 m), gate margin; fin plugs +10 g EST (D1); `CL-A3-PACK-ACCEPT` |
| A2 | crash line re-base (one CNHL 77.16; tube 119+; motor 44; ESC 33); reserve and spares claims (no 5th motor, 4 spare props) |
| F4 / B4 / B3 | flying without an airspeed sensor: TECS, `AIRSPEED_MAX`, transition window; if not acceptable re-add $80.16 and drop another lever |
| C4 / D3 | plug material (D1), tube span / brace questions (2.7), 36 in tube with no spare, wood plug bearing |
| C6 / D3 | torque by lever arm and its tolerance; M3 key reach |
| D5 / C5 | TPU removed (caps in PLA / PETG / neoprene), landing compliance; phone inclinometer enough |
| E1 / H1 | no 5th motor, 8 props, DIY balancer, M6 nut source |
| F1 | cap count (S6) and ripple, ESC spare gone, pack lead re-termination, hot-wire fuse |
| H2 / H3 | one-pack cadence, no anemometer, flight cards |
| D1 | hot-wire length and fuse from a pack; no H05 bow |
| D7 | box without mat / cradle, still within 1.25 x 0.55 x 0.45 m |
| F5 | plain Pocket ELRS |
| I1 | rebuild BOM / ORDER-PLAN if accepted; Jacobs written yes (J1); re-read prices at order |

Items that could break the $22 margin, in order to check: CNHL price (read only as a snippet) and its mass pass; A1 is a deferral, not a final saving, if F4 needs the sensor; S6 cap count; the wood plug (C4 / D3). If a role rejects a lever, the cost is its standalone figure above. Rejecting P3 for a Gens Ace is the one that breaks the set.

## 4. Not done / open

- Nothing is applied to `BOM.csv`, `bom_summary.json` or `params.json`; I1 rebuilds once the team decides. The bridge would drop by 1,131.85.
- Prices from search snippets or an aggregator are `UNVERIFIED`; vendor pages returned 403 / 429 (chinahobbyline, RaceDayQuads) or 404 (Makers Pass).
- The servo, motor and charger searches found no qualified cheaper part: that means not found in a US-market search of 2026-11-14, not proof none exists.
