# Route clearance: wires against structure, groove walls and each other (F2)

Every strand the CAD draws (subsystems/harness/params.json `cad.wire_strands`: the 16 AWG pairs and the servo ribbon conductor by conductor, every other run as one bundle tube of its circumscribed diameter), corners rounded to the edge bend radius, sampled every 0.5 mm against every body of every flight part (Blender BVH, ray-parity inside test) and against every strand of every other edge. The wing core is grooved in the CAD (D1: three 3.0 x 3.1 / 2.5 x 2.4 mm grooves per surface, the 4.0 x 1.6 mm servo groove and branch), so a conductor in its groove must clear the groove walls and floor; the pod side walls have their exit windows cut. Tool: `team/F2/route_clearance.py` (docstring lists the declared passages: liners, taped floor runs, the first / last 12 mm landing on a pad).

    blender -b --factory-startup -P redesign/team/F2/route_clearance.py -- [--json OUT] [--params P]

## D-74 re-run (2026-11-11, F2-R4, with the XT30U drawn)

| | before D-74 | after D-74 |
|---|---:|---:|
| wire rows / strand samples / bodies | 36 / 20 037 / 938 | 33 / 19 548 / 935 |
| penetrations, wire into a solid (now incl. the four XT30U bodies `HRN-113-*`) | 0 | **0** |
| penetrations, wire into wire | 0 | **0** |
| tight (no overlap, < 1 mm) | 266 | 264 |

What changed: `W-FUSE-IN`, `W-UBEC-IN`, `W-UBEC-OUT` and the bodies of `PWR-005` / `PWR-007` (and the fuse clip on
`PWR-006`) are gone. The four Amass XT30U are parts with bodies at the manufacturer's mated size (20.1 × 10.2 mm,
5.2 mm thick per listing): the tool now checks them (only the `HRN-001/-002` mass proxies are skipped; each
`W-PWR-<st>` is exempt inside its own plug, `OWN_LEAD`). Right plugs stacked flat on the last run to the right exit
(0.4 mm over the foot plate, 1.3 mm from the handle leg; nearest wires the right signal leads, 0.3–0.6 mm). Left
plugs stacked flat in the outboard half of the tunnel under the cradle; the right pairs moved to the inboard half
(y −0.043) and the left pairs turn to their exit aft of the cradle legs, which F1 moved 10 mm forward. The crossing
behind the aft stop has no room (strut-rib heels to the aft wall is exactly 10.2 mm). The power deck is 56 mm
(`KO-PWR-BOARD`), so `W-PMOD` runs over the deck front edge, down at x −0.0685 inboard of the airspeed board. The
servo leads are now 22 AWG + / − with a 28 AWG signal (3.6 mm flat in the 4.0 mm groove, 0.85 mm deep, branch line
0.1 mm outboard so the 3.9 mm bend clears the inboard wall at the corner). Not checked by this tool: plug bodies
against structure (bounding-box check in F2's run: no overlap).

## Result (F2-R3, before D-74)

| | before (HEAD routes) | after |
|---|---:|---:|
| penetrations, wire into a solid (incl. groove walls) | 406 | 0 |
| penetrations, wire into wire | 105 | 0 |
| max depth | 8.0 mm | - |
| tight (no overlap, < 1 mm clearance) | 102 | 266 |

Tight after: conductors in their grooves (0.05-0.35 mm to the walls, floor and tape skin: the groove sizes are D1/F2 `groove_size_mm`), runs taped side by side (pairs 0.1 mm apart, stacked layers 0.1-0.4 mm), and landings near pads. None overlaps.

Mass (A3 roll-up): harness 117.2 -> 119.8 g (+2.6 g), aircraft basic 2349.2 -> 2351.8 g; CG x 0.05023 -> 0.05023 m, z 0.01852 -> 0.01852 m. The old routes ran straight through the collar, mount, UBEC and handle; the clear routes are longer (phase leads +7 mm each, 3 x 16 AWG) and need one more tie per station.

## Before, by wire family and what was hit (all fixed: 0 after)

| wire | hits | part / other wire | n | max mm | fix |
|---|---|---|---:|---:|---|
| W-ASPD | solid | AVN-001 | 2 | 5.4 | starts inboard of the FC over the bay guide, own channel lane, corridor |
| W-ASPD | solid | PWR-107 | 1 | 1.5 | starts inboard of the FC over the bay guide, own channel lane, corridor |
| W-ASPD | solid | PWR-101 | 1 | 0.8 | starts inboard of the FC over the bay guide, own channel lane, corridor |
| W-GPS | solid | POD-007 | 1 | 2.4 | outboard of the leg into the D2 leg window, up the aft face of the mast, aft of the 45 deg pad |
| W-GPS | solid | POD-005 | 1 | 2.2 | outboard of the leg into the D2 leg window, up the aft face of the mast, aft of the 45 deg pad |
| W-GPS | solid | POD-011 | 1 | 1.1 | outboard of the leg into the D2 leg window, up the aft face of the mast, aft of the 45 deg pad |
| W-PACK | solid | PWR-006 | 1 | 0.1 | pack-owned lead aft of the cradle walls |
| W-PH-* | solid | FIN-008-* | 16 | 3.5 | collar-tail lug tie, then over the pinch bolt / nut to a tie at the pinch ear, then the motor lead exit |
| W-PH-* | solid | FIN-003-* | 12 | 4.4 | collar-tail lug tie, then over the pinch bolt / nut to a tie at the pinch ear, then the motor lead exit |
| W-PH-* | solid | FIN-102-* | 4 | 3.0 | collar-tail lug tie, then over the pinch bolt / nut to a tie at the pinch ear, then the motor lead exit |
| W-PH-* | solid | FIN-103-* | 4 | 3.0 | collar-tail lug tie, then over the pinch bolt / nut to a tie at the pinch ear, then the motor lead exit |
| W-PH-* | solid | FIN-101-* | 4 | 1.3 | collar-tail lug tie, then over the pinch bolt / nut to a tie at the pinch ear, then the motor lead exit |
| W-PMOD | wire | W-ASPD | 3 | 3.0 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | wire | W-RX | 3 | 3.0 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | PWR-107 | 1 | 1.9 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | PWR-101 | 1 | 1.1 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | PWR-102 | 1 | 0.3 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | AVN-006 | 1 | 3.2 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | AVN-001 | 1 | 2.0 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PMOD | solid | AVN-007 | 1 | 1.1 | own channel lane (3 lanes), under the FC between the gel cubes, stacked corridor (y -0.028) |
| W-PWR-* | wire | W-UBEC-IN | 10 | 5.8 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | wire | W-SIG-* | 50 | 4.5 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | PWR-006 | 6 | 2.9 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | WNG-001 | 106 | 4.0 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | WNG-003 | 8 | 1.5 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | FIN-004-* | 22 | 3.6 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | WNG-006-* | 4 | 3.4 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | wire | W-PWR-* | 21 | 6.0 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | POD-007 | 23 | 4.5 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-PWR-* | solid | PWR-005 | 6 | 8.0 | conductor by conductor: + and - in their own grooves, side by side elsewhere; groove entry 18 mm in, over the P1 mouth; leaves the groove 12 mm early, over the bead and boss, tie above the lug; pod: stacked layers (2.9-3.3 mm), crossing aft of the ribs over the foot bridge and the UBEC |
| W-RX | wire | W-ASPD | 3 | 2.9 | as W-PMOD |
| W-RX | solid | AVN-006 | 1 | 1.9 | as W-PMOD |
| W-RX | solid | PWR-107 | 1 | 0.7 | as W-PMOD |
| W-RX | solid | PWR-004 | 1 | 0.4 | as W-PMOD |
| W-SIG-* | solid | PWR-005 | 6 | 4.4 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | solid | PWR-006 | 4 | 2.2 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | solid | WNG-001 | 86 | 2.5 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | solid | WNG-003 | 8 | 0.3 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | solid | FIN-004-* | 22 | 2.1 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | solid | WNG-006-* | 4 | 1.7 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | wire | W-SRV-R | 3 | 2.1 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | wire | W-SRV-L | 1 | 0.1 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SIG-* | wire | W-SIG-* | 9 | 3.0 | own lane: pod over the UBEC forward of the pairs, left leads via the aft window edge; through the P1 straw and the fin hole in the notch on top of the pair; stacked on the pair, then forward of it |
| W-SRV-L | wire | W-SRV-R | 2 | 2.7 | ribbon conductor by conductor in the 4 mm groove 0.9 mm deep, entry after y 0.086, branch floor followed; pod: JR row re-ordered, rises over the aft stop and crosses above the signal leads |
| W-SRV-L | solid | WNG-001 | 15 | 3.1 | ribbon conductor by conductor in the 4 mm groove 0.9 mm deep, entry after y 0.086, branch floor followed; pod: JR row re-ordered, rises over the aft stop and crosses above the signal leads |
| W-SRV-L | solid | WNG-003 | 2 | 0.7 | ribbon conductor by conductor in the 4 mm groove 0.9 mm deep, entry after y 0.086, branch floor followed; pod: JR row re-ordered, rises over the aft stop and crosses above the signal leads |
| W-SRV-R | solid | WNG-001 | 15 | 3.1 | ribbon conductor by conductor in the 4 mm groove 0.9 mm deep, entry after y 0.086, branch floor followed; pod: JR row re-ordered, rises over the aft stop and crosses above the signal leads |
| W-SRV-R | solid | WNG-003 | 2 | 0.7 | ribbon conductor by conductor in the 4 mm groove 0.9 mm deep, entry after y 0.086, branch floor followed; pod: JR row re-ordered, rises over the aft stop and crosses above the signal leads |
| W-UBEC-IN | solid | POD-007 | 6 | 2.3 | over all four pairs under the cradle, inboard of cradle leg 1, crossing x 0.088 above the pairs |
| W-UBEC-IN | solid | POD-001 | 3 | 0.6 | over all four pairs under the cradle, inboard of cradle leg 1, crossing x 0.088 above the pairs |
| W-UBEC-IN | solid | PWR-005 | 1 | 2.2 | over all four pairs under the cradle, inboard of cradle leg 1, crossing x 0.088 above the pairs |

## Also changed with this fix

- HRN-001 / HRN-002-L/R are mass proxies (`"mass_proxy": true`): mass and CG stay in interfaces, parts and the roll-up; not drawn in Fusion (hidden "(mass proxy)" component), the Blender renders or the GLB (an empty with the part extras). The routed wires show the harness.
- The tape skin (WNG-003, clear BOPP packing tape) renders clear, so the taped-over grooves and the conductors in them show (blender_backend LOOKS).
- `cad.wire_strands` (harness.py `draw_strands`) is what the module draws; the wire table and every claim input are unchanged in form.
- How to verify: run the tool (0 penetrations), then `python -I redesign/team/F2/harness.py --check`.
