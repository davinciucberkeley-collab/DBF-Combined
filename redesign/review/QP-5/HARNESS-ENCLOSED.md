# Harness enclosure (D-198, 2026-11-15)

Rule (root `CLAUDE.md`, user 2026-11-15): route wires inside the arm tubes, wing-core channels, fairings or covers; list every wire left exposed with its length and the reason, and keep it to the minimum.

**Verdict.** Exposed wire fell from **9.09 to 4.27 strand-metres** (2.87 to 1.39 m of cable path, both -52 %). Gone from view: the four motor lead runs along the arms (0.27 m per motor, 12 strands), the servo leads over the skin (0.21 m each, now in foam grooves), and the FC / ESC board wiring (now under a printed bay cover). Not solved: the **hub to bay run of the motor phase leads** (0.26-0.34 m per motor, 3.6 of the 4.27 strand-metres left). No enclosure for it passed the structure or geometry checks; the reasons and a proposed next step are in section 5. Nothing was invented: every new dimension is a drawn CAD feature, and the unknown ones are marked `EST`.

Reproduce: `python -I redesign/qp/A/cad/wire_inventory.py` (this build) and `... wire_inventory.py <folder with the D-197 cad copy>` (before). Per segment, by midpoint: ARM = inside cup collar / arm bore, GROOVE = foam channel, COVER = under AVN-008, EXPOSED = the rest.

## 1. Inventory, before and after (strand centre-line lengths from the CAD wires)

| Edge | Wire | Strands x OD | Before (exposed m per strand) | After: enclosed (arm / groove / cover) | After: exposed | Note |
|---|---|---|---|---|---|---|
| E-HRN-02, -03 | phase leads UR, UL | 3 x 1.8 mm (was 2.0) | 0.445 / 0.439 | 0.271 / - / 0.008 | 0.256 | route 0.534 m |
| E-HRN-04, -05 | phase leads LR, LL | 3 x 1.8 mm | 0.527 / 0.540 | 0.271 / - / 0.006 | 0.341 | route 0.618 m |
| E-HRN-07, -08 | servo leads R, L | 3 x 1.2 mm | 0.262 each | - / 0.210 / 0.035 | 0.011 | groove 3 mm under the skin |
| E-HRN-06 | ESC signal ribbon | 6 x 1.3 mm | 0.073 | - / - / 0.073 | 0 | under cover |
| E-HRN-12 | battery tail | 2 x 3.0 mm (14 AWG) | 0.095 | - / - / 0.029 | 0.066 | out through the cover notch to the XT60 |
| E-HRN-09 | RX CRSF lead | 4 x 1.0 mm | 0.105 | - / - / 0.049 | 0.056 | RX board is outside the cover |
| E-HRN-10 | GPS lead | 6 x 1.0 mm | 0.062 | - / - / 0.035 | 0.027 | GPS board outside the cover |
| E-HRN-11 | airspeed lead | 4 x 1.0 mm | 0.059 | - / - / 0.032 | 0.027 | board outside the cover |
| E-HRN-01 | XT60 mating link | - | 0.001 | - | 0.001 | connector |
| **Total strand-m** | | | **9.085 exposed** | 3.247 arm + 1.258 groove + 1.325 cover | **4.271 exposed** | wire_inventory.json |

Strand OD 1.8 mm for 20 AWG silicone: Pimoroni listing (shop.pimoroni.com/en-us/products/dual-silicone-wire-per-metre, read 2026-11-15: OD 1.8 mm, 14.2 g per metre for two conductors). The T-Motor page (store.tmotor.com/goods-388-MN2212-V20.html, 2026-11-15) gives 20 AWG, 400 mm leads, 55 g without and 65 g with cables, but not the OD: measure on arrival.

## 2. What changed

| Item | Change | Basis |
|---|---|---|
| Motor cup CGE-003 | Old open slot (z 10.5-17.5) dropped. New: 4.8 mm lead hole through plate and sleeve wall at y +5.5 mm; lead collar OD 14 / ID 12.2, y 3.5-8.0, with a 0.8 mm end cap, holds the 4 mm bend. Sleeve bore 12.2 mm (0.1 mm epoxy gap) | `wing.py`; collar 0.39 g, hole -0.1 g: cup 4.0 -> 4.3 g |
| Motor lead exit | 3 strands leave the base ring at y +5.5, z 0 (inside the ring, 1.5 mm behind the plate face). The exit position is not on the T-Motor drawing: `EST`, measure on arrival | the old z 13.5 position was also `EST` |
| Arm bore | Bundle (tri of 3 x 1.8 mm, envelope 3.88 mm) runs inside the 10 mm bore for 0.271 m, drifting to the up side near the hub (offset 2.7 mm; bore ID 10: 2.7 + 1.94 = 4.64 < 5.0). Fill by strand area 7.6 of 78.5 mm2 = 9.7 % | `common.py` PH_* |
| Bend radius | 4 mm at the collar and at the hub exit (bundle centre; inner strand about 3 mm, 1.6 x OD). `WIRE bend_radius_mm` 6 -> 4 | CAD kink gate: no fold at 4 mm |
| Hub CGE-001 | 4.8 mm hole through each 2.0 mm socket floor so the bundle leaves the arm bore inward. Floor carries no load (arm loads go through the bond) | `wing.py` |
| Servo leads | Out of the FC between the boards, over the plate to the plate window (x 80-122, |y| 21-40), down through a slit in the skin at x 83, |y| 24, into a groove 3 mm under the upper skin (5 mm wide, 3.2 mm high), outboard along y to |y| 190, aft along the skin to the servo pocket wall. Grooves are routed shop cuts in WNG-001 | `electrical.py`, `servo_zc` |
| Bay cover AVN-008 (new) | 0.6 mm printed PETG hood, x 22.5-126.5, |y| <= 26.5, roof 45 mm over the FC and 32.5 mm over the ESC, notches open to the roof for the four phase bundles, the battery tail and the GPS / RX / airspeed leads, foam tape and two ties, removable for FC access | mass 9.6 g from the drawn volume (shell 0.6 mm, PETG 1.27) |
| Phase-lead route outside | Upper bundles now at z 29 (was 35) under the cover roof; unchanged y 62 / 88 mm, x -58.5 / -52.5 | `phase_route()` |
| Motor screw seat | 0.1 mm deeper (x -7.1 mm) so the head face is not coplanar with the plate rear face; thread engagement 3.0 -> 3.1 mm (shank 0.1 mm deeper into the base ring; base ring 3.5 mm `EST`) | boolean robustness, section 6 |

## 3. Checks

| Check | Result |
|---|---|
| Arm-bore fill / bend | 9.7 % fill, bend >= 4 mm centre line: pass |
| `arm_cup_checks.py` (re-run) | plate bending under the thrust cantilever net section 30.3 x 5 mm after the lead hole: MS +8.26 -> **+7.51**; prop strike S2 plate cantilever **+0.49 -> +0.37**; fatigue plate amplitude +6.88 -> +6.25; everything else unchanged (lowest overall: hole bearing, strike S3, +0.39) |
| `qp5_checks.py` (re-run) | unchanged (hub socket wall, bridge sleeve, spar foam): the floor hole is not in the wall or the bearing patch; the spar foam cover (6.27 / 5.62 mm) is not touched: the groove is at x 83, 17 mm aft of the spar OD, 1.2 mm of foam stays above it |
| Collision, neutral and +-20, +-21 deg | 0 part pairs deeper than 0.05 mm; wire ends not on a termination 0; wire folds 0 (97 parts, 447 bodies) |
| Collision +-22 deg | the 4 expected contacts only: balance tab x stop boss, WNG-007-R/L with WNG-008-RU/RL/LU/LL, 0.24-0.28 mm |
| Assembly | 41 steps (36 place parts, 5 are marker steps), 97 of 97 parts, 0 blocked, 0 unsupported, every electrical edge laid once after both end parts, threading steps before their partner (B0 before B1, D0 before E2) |
| `stop_check.py` | PASS |

## 4. Mass

| Item | g |
|---|---|
| Bay cover AVN-008 (new part) | +9.6 |
| Cup collars and holes, 4 cups | +1.2 |
| Harness remainder HRN-001, bottom-up (was 50.9 g, the 110 g avionics allocation less itemised parts) | 28.1 |
| of which phase-lead extensions (12 strands x (route - 0.40 m stock lead + 30 mm splice) = 2.47 m at 7.1 g/m) | 17.5 |
| of which 12 splices 1.8, ESC ribbon 0.9, RX / GPS / airspeed leads and plugs 2.7, servo ties 0.2, sleeves, ties, tape, solder 5.0 (all `EST` except the 7.1 g/m, Pimoroni) | 10.6 |
| HRN lump now vs before (the old lump had no phase-lead extensions: the 65 g motor mass carries only the 400 mm stock leads, shorter than the 0.53-0.62 m route) | -22.8 |
| **Net CAD basic mass** | **1,263.74 -> 1,259.74 g (-4.0)** |

The cover is added, not absorbed: `HRN-001` is computed from the list in `electrical.py` (`HRN_ITEMS`), not from the 106 g allocation. Predicted mass with growth and overrun: itemised 1,450 g (was 1,454), flat rule 1,455.6 g (was 1,459); target 1,460 g: room 4-10 g. CG 21.3 mm aft of the LE (was 21.1), SM 7.9 %.

## 5. What is still exposed (table for `CLAUDE.md`)

| # | Wire | Length exposed | Reason it cannot be enclosed now |
|---|---|---|---|
| 1 | Phase bundles UR, UL, hub floor hole to the cover notch (3 strands each) | 0.256 m each (+ 0.008 under the cover) | The 105 mm wide pack (y +-52.5, tray walls +-54.5, strap +-56.1) forces the run out to |y| 62 mm; the only enclosed path from the hub to the wing is the bridge tube bore (ID 10), but side holes for four bundles cut the section to 0.45 (2 holes) / 0.22 (4 holes) of its second moment: prop-strike stress 91.9 -> 205 / 423 MPa against 350 (MS +0.7 before a stress concentration, about -0.15 with Kt 2): rejected. A groove under the skin cannot cross the spar bore (ligament 6.27 / 5.62 mm, saddle ring 1.1 mm from the lower skin) without cutting it |
| 2 | Phase bundles LR, LL (lower arms), same span, climbing at the hub aft face | 0.341 m each (+ 0.006 under the cover) | as 1; the lower pair also climbs round the strut boss and over the leading edge at |y| 88 mm |
| 3 | Battery tail, XT60 female to the cover notch | 0.066 m (2 strands 14 AWG) | the XT60 pair must stay outboard of the pack end (y 55.75-71.25) for the field disconnect |
| 4 | XT60 male and female housings | 2 x 12 mm | connectors |
| 5 | Pack power leads, pack end to the XT60 male | 0.098 / 0.102 m | vendor leads (about 100 mm, nextfpv), not ours to bury |
| 6 | Pack balance lead (5 conductors) to its JST-XH plug on the pack top | 0.054 m | vendor lead |
| 7 | RX CRSF lead, outside the cover wall to the receiver | 0.056 m | the receiver and its antennas must stay outside the carbon-free zone and the cover width is set by the GPS board (y >= 27.5); widening the cover to |y| 55 would enclose items 7-9 at about +5 g `EST` |
| 8 | GPS lead | 0.027 m | GPS needs sky view and compass distance from the ESC: board outside the cover |
| 9 | Airspeed lead | 0.027 m | the MS4525 board sits at y -37.5..-52.5 near the pitot |
| 10 | Servo leads, pocket wall to the lead boot | 0.011 m each | the servo pocket must stay open for the +-20 deg arm sweep |
| 11 | RX antennas (not wire: antenna elements) | 2 x 0.050 m drawn (65 mm real) | antennas must be outside carbon and plastic shells |
| 12 | Pitot silicone tube (2 / 4 mm) | `-` | the rear connection and the run to the sensor are **not designed** in the CAD (pre-existing gap); no length claimed |
| 13 | Motor lead, base ring to the collar | 0 | inside the collar |

Total exposed in the CAD wires: 4.271 strand-metres, 1.393 m of cable path. Next step proposed (not done): a printed raceway on the hub aft face and the bridge underside to the leading edge plus foam channels at |y| 17-24 under the lower skin, and a surface-level crossing of the spar under the cover. It needs a new lower-skin hatch and a new check of the saddle ring clearance.

## 6. Blender boolean robustness (task 4)

`blender -b --factory-startup -P redesign/blender/export_glb.py -- --root redesign/qp/A/cad/model --out DIR` printed 12 `CUT NOT VERIFIED` lines, all on the left cups CGE-003-UL / -LL. Found and fixed in the CAD: the screw-hole cutters ended at x -6.4 mm, 0.6 mm past the plate rear face, where they nicked the sleeve skin (a sliver): they now end at x -7.1 mm, now 0 failures for the screw holes; the arm seat was a cylinder coincident with the sleeve bore (bore now 12.2 mm). Still printed (8 lines, UL and LL only): the two D-197 screw-head pockets and the two motor-screw-head seat cuts at y -9.5 mm. Independent point-in-solid tests of the finished UL and LL cup meshes (probe script run inside Blender) show the pockets empty and the walls and plate solid, so the delivered GLB geometry is right; the verifier's check counts samples at the sleeve skin within 20 micrometres of r 9.6 mm. UR and LR pass the same check after a retry. Not resolved: cutter ends, pocket depth, pocket shape (box instead of cylinder), cutter order and a 0.0007 deg part rotation were all tried without effect.

## 7. Measure on arrival

Motor lead OD and length (stock 400 mm), the lead exit position on the motor base, the bundle pull force through the 4 mm collar bend, bundle fill in the bore, bay cover fit round the FC screw heads, groove depth against the skin tape, pitot tube route.
