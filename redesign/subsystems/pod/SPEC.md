# Pod

Status: `MODELLED` (D2, revision D2-R7, 2026-11-11). R7: the pack datum moves 4 mm forward to −0.036 (D-77, BR-00), and
the pod takes D-74: the UBEC plate is gone, the power-board keep-outs `KO-PWR-*` are reserved and checked, the forward
strap moves ahead of them, and each side exit has room inside it for two mated XT30U. R6 (2026-11-10) re-lays the bay for D-62 (CR-A1-62, CR-A3-25),
draws the D-64 Ovonic pack, and builds C3's three FEA fixes from D-69 (CR-C3-14 to -18). It also takes CR-C6-27,
CR-E3-15, CR-F1-26 and CR-D7-23. The CAD is `fusion/pod.py`. `team/D2/pod_data.py` computes masses and CGs from the
CAD, and `team/D2/pod_claims.py` holds the claims.

## Purpose

The pod holds the 4S 6500 pack at the station that balances the aircraft. In a 5 m/s nose-in crash the crush block
(C5) keeps the pack load at or below 100 g, and the straps, stops and strut (C3) hold the pack at 12.75 g. The pod
gives one place to lift the aircraft: the grip on the spar (D-23). It carries the FC, RX, airspeed sensor, power items,
GPS and pitot, with their wiring paths. Field use needs no tools: open the hatch, put the pack in with its block,
spreader and spacer stack, strap it, plug in, close.

## Bay, front to back (x, m)

| Item | x | Part |
|---|---|---|
| Nose wall, 4.8 mm board · 1 mm microballoon epoxy line | −0.140 … −0.1352 · … −0.1342 | `POD-001` |
| Forward-stop T: 3 × 25 mm upright, past the floor edge, to a 12 × 54 × 1.2 mm flange under the floor (D-69) | −0.1342 … −0.1312 (flange to −0.1222) | `POD-002` |
| Crush block, cut per pack · 1.5 mm spreader (CAD at the D-77 datum) | −0.1312 … −0.1050 · … −0.1035 | `POD-009` · `POD-010` |
| Forward strap slot (D-74: 26 mm, ahead of `KO-PWR-*`) · wire channel (F2, 10 mm) · aft strap slot | −0.092 … −0.066 · −0.0295 … −0.0195 · −0.007 … 0.019 | `POD-004` · `POD-002` |
| Pack, 0.135 long: CAD at the −0.036 datum (D-77) · 546 · 550 · 590 g (A3 stations) | −0.1035 … 0.0315 · −0.1035 … 0.0315 · −0.1015 … 0.0335 · −0.0975 … 0.0375 | `PWR-001` |
| U-spacers 2 / 4 / 6 / 8 · aft stop 3 mm on the tray rear piece | 0.0315 … 0.0475 (CAD, 16 mm) · 0.0475 … 0.0505 | `POD-008` · `POD-002` |
| Strut: 40 × 14 × 1.5 mm pad · three 3 × 14 mm ribs, z 0.026 … 0.040 · foot bridge (D-69) | 0.0505 … 0.052 · 0.052 … 0.077 · 0.077 … 0.0902 | `POD-007` |

## Pack on the crush stack (CR-A1-62)

| Case | Block | Pack centroid | Gap to the aft stop | Spacers · play |
|---|---|---|---|---|
| A1's 24.3 mm block (D-62) | 24.3 mm | −0.0379 m | 17.9 mm | 16 mm · **1.9 mm** |
| C5's 25.7 mm block, 550 g class | 25.8 mm | −0.0364 m | 16.4 mm | 16 mm · 0.4 mm |
| Flown stations (A3 on the day) | cut to fill | as A3's station | spacer stack | 0 mm: the block takes up the play (CR-C5-14 c) |

## Key numbers

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Pod x range · width · height (outside) | −0.140 … 0.095 · 0.140 · 0.070 | m | `params.json#pod` (D-62) | `PROPOSED` |
| Forward stop face · aft stop face · nose skin to the stop | −0.1312 · **0.0475** · 8.8 mm | m | `CL-D2-FWD-STOP-X`, `ASM-D2-AFT-STOP-X`, `CL-D2-NOSE-TO-STOP` | `CHECKED` |
| Bay inside L × W × H (≥ 0.160 × 0.052 × 0.053) | 0.179 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid: datum (CAD, D-77) · no spacer · 546 · 550 · 590 g | −0.036 · −0.020 · −0.036 · −0.034 · −0.030 | m | `CL-D2-PACK-X-NOM/-NOSPACER/-LIGHT/-550/-HEAVY` | `CHECKED` |
| Spacer stack: CAD · 546 · 550 · 590 g | 16 (2 + 6 + 8) · 16 (2 + 6 + 8) · 14 (6 + 8) · 10 (2 + 8) | mm | `CL-D2-SPACER-NOM/-LIGHT/-HEAVY` | `CHECKED` |
| Crush block CAD datum · 546 · 550 · 590 g (minimum: C5's 25.8 mm, scaled by mass) | 26.2 (≥ 25.8) · 26.2 (≥ 25.6) · 28.2 (≥ 25.8) · 32.2 (≥ 27.7) | mm | `CL-D2-BLOCK-B-LIGHT/-550/-HEAVY` | `CHECKED`, scaling `UNVERIFIED` |
| Most forward centroid with C5's block · room ahead of the D-77 datum | −0.0364 · 0.4 | m · mm | `CL-D2-PACK-X-FWD-MIN`, `-PACK-FWD-ROOM` | `CHECKED` |
| Strut rib free length · rib to wing skin | 25 · 3.5 (≥ 2) | mm | `CL-D2-STRUT-RIB-L`, `-STRUT-SKIN-CLR` | `MODELLED`; C3 re-checks |
| Wall bracket bonded area per side (≥ 1 000) · stop-T flange under the floor | 1 232 · 486 | mm² | `CL-D2-BRACKET-AREA`, `-FWD-FLANGE-AREA` | `CHECKED` |
| PDB pad moment capacity vs the 1.94 N·m unplug moment · boss Ø | 2.16 (RF 1.11) · 7.2 | N·m · mm | `CL-D2-PDB-PAD-M` | `UNVERIFIED` (0.05 MPa allowable) |
| Forward stop bond (≥ 85) · straps vs pack crash · ties vs handle | 214 · 200 vs 85 · 444 vs 76 | N | `CL-D2-FWD-STOP-BOND`, `-STRAP-CAP`, `-TIE-CAP` | `UNVERIFIED` |
| Wire channel · crossing gap · crossing height | 3.5 (≥ 3.0) · 6.7 (≥ 6.7) · 54 (≥ 26) | mm | `CL-D2-FLOOR-CH-H`, `-CROSS-GAP`, `-CROSS-H` | `CHECKED` |
| Pitot tip · boom `AVN-005` · socket depth · key flat | (−0.220, −0.046, 0.045) · 107 · 35 · 5.8 | m · mm · mm · mm | `CL-D2-PITOT-*` | `PROPOSED` |
| Antenna A / B to the pack (≥ 30.7) · tube B end (≥ −0.150) · GPS to power items (≥ 100; no UBEC, D-74) | 36 / 36.5 · −0.144 · 153 | mm · m · mm | `CL-D2-ANT-A/B-CLR`, `-ANT-B-TIP-X`, `-GPS-CLR` | `CHECKED` |
| Pod bodies in `KO-PWR-BOARD` / `-PADS` (from the boss tops) / `-FWD` / `-SIDE-IN` (D-74) | 0 | – | `CL-D2-KO-PWR-HITS` | `CHECKED` |
| Board outboard edge to the side-wall inner face (case U wants 6) | 1.8 | mm | `CL-D2-KO-PWR-SIDE-OUT` | `CHECKED`, short for case U (CR-D2-31) |
| Pod bodies in the two XT30U zones · one XT30U body through a 16 × 12 exit (≥ 2) | 0 · 5.8 | – · mm | `CL-D2-XT30U-HITS`, `-XT30U-EXIT` | `CHECKED`; plug size `UNVERIFIED` |
| Thermal: pack at landing (`E-POD-12`) · FC peak (`E-AVN-10`, F3) at 44 °C ambient | 44.8 · 54.9 (68.9 hover-only) | °C | `CL-E3-PACK-END`, `CL-E3-FC-PEAK` | `MODELLED` (E3) |
| Mass · CG | **144.2** (allocation 146, D-63; UBEC plate −1.0 g) | g | `CL-D2-MASS` `EST` | `CHECKED`, 1.8 g margin |

## Channels (y ±0.0275 … ±0.0652)

| Left (−y), x | Item | Right (+y), x | Item |
|---|---|---|---|
| −0.148 … −0.113 | pitot socket + 32 mm flange on the nose wall; antenna B tube (end −0.144) | −0.041 … 0.021 | FC on 4 gel cubes between end stops; 10 mm strap through the stop slots |
| −0.088 … −0.040 | airspeed between tie posts (21 mm apart), RX behind; antenna A tube above (from z 0.076) | 0.021 … 0.040 | JR tie bar, 3 tie slots (six in-line plugs) |
| −0.038 … 0.046 | PDB plate, 4 bosses Ø 7.2 for M3 inserts, rib along each boss row: F1's bus board and power frame; `KO-PWR-BOARD` −0.066 … −0.010 above the deck (z 0.0386 … 0.0626), `KO-PWR-FWD` −0.076 … −0.066 (D-74) | 0.044 … 0.074 | right XT30U pair (two mated, stacked, z 0.026 … 0.038); the UBEC plate is gone (D-74) |
| 0.000 … 0.060 · 0.062 … 0.074 | AS150U park zone: F1's cradle `PWR-006` · left XT30U pair on the foot plate (D-74) | 0.056 … 0.072 | side-wall exit 16 × 12 mm, z 0.027 … 0.039 (each side) |
| 0.066 … 0.090 | wall bracket flange (above the exit, down to the foot behind it) | 0.066 … 0.090 | same, mirrored |

Wiring paths: the channel at x −0.0245 under the pack lands on the PDB plate (left) and the FC (right). Power and
DShot use the side-wall exits; servo leads use the aft-wall exits. The pack leads run over the aft stop (top z 0.0503)
and the strut ribs (top 0.040), inboard of the left leg. The GPS cable goes up the right leg into the grip groove and
the mast bore.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-POD-01` | `WNG-001` core | shell bonded in the recess to bare foam (10 014 mm²); floor aft end square on the recess step (D-103: fillet and bevel deleted) | C3, C6 |
| `E-POD-09` | `WNG-002` spar | handle saddles and foot bridge bonded (1 445 mm²), one tie per foot; end of the aft-stop strut path since D-69 | C3, C2 |
| `E-POD-14` | strut ↔ aft stop | pad epoxy-bedded on the stop back face (560 mm²), bearing | C3 |
| `E-POD-15` | brackets ↔ side walls | flanges epoxied to the walls (2 × 1 232 mm²) | C3 |
| `E-POD-05` | `PWR-001` pack | field joint: 2 straps, guides, pads; block and forward stop ahead, spacers and aft stop behind | C3, C5, C1 |
| `E-POD-06` | mast ↔ handle | M3x16 PA66 screw + PA66 nut, grip 10.0 mm, finger tight + ¼ turn | C6 |
| `E-POD-10` · `-11` · `-13` | spacers ↔ aft stop · block ↔ forward stop · spreader ↔ block | trapped, slid (`CT-SLIDE-STOP`) | C3, C5 |
| `E-POD-12` | `PWR-001` pack | thermal, insulating; heat leaves by the vents (44.8 °C at landing) | E3 |
| `E-POD-02` … `-04`, `-07`, `-08` | internal | bonds (stop T and its flange, 1 mm line to the nose wall), hatch tongue and tab, strap slots, socket flange | C3, C6 |

Acknowledged: `E-PWR-03/-04/-05`, `E-AVN-01` … `-05`, `-07`, `-10`, `E-HRN-01`.

## Mass budget

145.8 g `EST` against 146 g (D-63). R5a was 130.9 g. Changes from R5a:

| Change | Mass |
|---|---|
| D-69 fixes: strut 5.6 g, brackets 4.7 g, stop-T upright and flange 2.2 g | +12.4 g |
| PDB plate extension and ribs (CR-C6-27, not in D-63) | +2.5 g |
| Guides 8 → 6 mm | −1.4 g |
| D-62 nose, shell and hatch, and the re-laid tray, net | +1.4 g |

To stay inside 146 g, R6 uses these levers: bracket flange 1.5 → 1.2 mm and started at the hatch end, web 3 → 2 mm,
PDB ribs 1.6 × 4 → 1.2 × 3 mm, pad 2 → 1.5 mm, stop flange 1.6 → 1.2 mm. Together with the guides they save 4.4 g, and
they are already counted in the table. C3 voids the 0.8 mm tray floor and the lead window. The recess-step fillet
counts as D1's mass.

## Open issues

| Issue | Owner |
|---|---|
| The aft stop sits at 0.0475, not A1's 0.050, because 0.050 is the sum with the retired 0.140 pack | A1 (CR-D2-24) |
| C3's fixes are drawn on the D-62 bay: ribs 25 mm (not 14), flanges 1.2 mm, bracket 1 232 mm² per side. C3 re-runs M2 and the tied-feet case | C3 (CR-D2-25) |
| Crush limit: D-62's −0.0379 uses a 24.3 mm block; C5's 550 g class block is 25.8 mm, which gives −0.0364. The D-77 datum −0.036 keeps 0.4 mm of block margin at 550 g; no further forward move is possible without a longer nose (antenna B and D7's box gap stop that) | A1, A3, C5 (CR-D2-24, -26) |
| Case U (whole stack, D-74): `KO-PWR-SIDE` wants 6 mm outboard of the board, the 37.7 mm channel leaves 1.8 mm to the side wall. The inboard 6 mm is clear (forward strap moved). GH plugs on the outboard edge need a vertical entry, or the board turns its plugged edge inboard | F1 (CR-D2-31) |
| The XT30U zones hold the plugs only if F1/F2 route the ESC pairs there; F1's AS150U cradle legs end at 0.060 (left zone starts 0.062) | F1, F2 (CR-D2-31) |
| The pack leads cross the aft stop | F1 (CR-D2-27) |
| F2's bundles lie in the floor and channel, and on the new PDB plate (x −0.004 … 0.046) | F2 (CR-D2-27) |
| Pitot socket collar (−0.148) overlaps D7's nose pad by 5 mm until D7 fits the ½ in pad (D-62) | D7 (CR-D2-28) |
| `POD-001` mass CG vs uniform body centroid 15.1 mm (bonded multi-material part) | A5 (CR-D2-19) |

## How to verify

`python -I redesign/team/D2/pod_data.py --check` · `python -I redesign/fusion/check.py` · `python -I
redesign/interfaces/merge_check.py` · `python -I redesign/team/D2/pod_selfcheck.py` · `python -I
redesign/team/D2/pod_claims.py` · built: `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`,
`T-C3-STOP-PUSH`, `T-C3-POD-PROOF` (+200 N on the brackets), `T-C6-INSERT`, `T-A3-CG-BALANCE`.
