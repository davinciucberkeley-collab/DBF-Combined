# Pod

Status: `MODELLED` (D2, revision D2-R5a on params A1-R4a, 2026-11-10). R5 is the D-47 re-lay (CR-A1-43, CR-A3-22) and
the CR-A5-27 CG fix; R5a adds D-59 (CR-A1-54): aft stop 0.056 → 0.060, D-59 flight stations, 12 mm CAD stack. CAD `fusion/pod.py`; masses and CGs from the CAD by `team/D2/pod_data.py`; claims
`team/D2/pod_claims.py`; per-pack station table `team/D2/pod_station_options.py`.

## Purpose

Hold the 4S 6500 pack at the station that balances the aircraft, keep it to ≤ 100 g in a 5 m/s nose-in crash (crush
block, C5) and in place at 12.75 g (straps, stops, C3), give one place to lift the aircraft (grip on the spar, D-23),
and carry the FC, RX, airspeed, power items, GPS and pitot with their wiring paths. Field use: hatch open, pack in
with its block, spreader and spacer stack, strap, plug, close. No tools.

## Bay, front to back (x, m)

| Item | x | Part |
|---|---|---|
| Nose wall 4.8 mm board · 1 mm microballoon epoxy line (XPS block A deleted, D-47) | −0.130 … −0.1252 · … −0.1242 | `POD-001` |
| Forward stop 3 × 25 × 54 mm (C3), on the solid tray front piece | −0.1242 … −0.1212 | `POD-002` |
| Crush block B, cut per pack · 1.5 mm spreader | −0.1212 … −0.0935 · … −0.092 (550 g) | `POD-009` · `POD-010` |
| Forward strap · wire channel (F2, 10 mm) · aft strap | slot −0.0725 … −0.0355 · −0.0295 … −0.0195 · slot −0.0025 … 0.0345 | `POD-004` · `POD-002` |
| Pack 0.140 long: CAD at the −0.022 datum · 550 g · 680 g · 503 g (D-59) | −0.092 … 0.048 · −0.088 … 0.052 · −0.080 … 0.060 · −0.094 … 0.046 | `PWR-001` |
| U-spacers 2 / 4 / 6 / 8 / 8 · aft stop 3 mm + 2 mm root ribs on the tray rear piece | 0.048 … 0.060 (CAD, 12 mm) · 0.060 … 0.063 (tray end 0.065) | `POD-008` · `POD-002` |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod x range · width · height (outside) | −0.130 … 0.095 · 0.140 · 0.070 | m | `params.json#pod` (D-47) | `PROPOSED` |
| Nose skin to forward stop face · stop face · aft stop face | 8.8 · −0.1212 · 0.060 (D-59) | mm · m · m | `CL-D2-NOSE-TO-STOP`, `-FWD-STOP-X`, `ASM-D2-AFT-STOP-X` | `CHECKED` |
| Bay inside L × W × H (≥ 0.160 × 0.052 × 0.053) | 0.181 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid: datum (CAD) · 550 · 680 · 503 g (D-59) | −0.022 · −0.018 · −0.010 · −0.024 | m | `CL-D2-PACK-X-NOM/-550/-HEAVY/-LIGHT` | `CHECKED` |
| Spacer stack: CAD · 680 · 550 · 503 g | 12 blue + yellow · none · 8 blue · 14 blue + green | mm | `CL-D2-SPACER-NOM/-HEAVY/-LIGHT` | `CHECKED` |
| Block B 680 · 550 · 503 g (min: C5 25.7 mm at 550 g, scaled with mass) | 39.7 (≥ 31.8) · 31.7 (≥ 25.7) · 25.7 (≥ 23.5) | mm | `CL-D2-BLOCK-B-HEAVY/-550/-LIGHT` | `CHECKED` (scaling `UNVERIFIED`) |
| Forward trim room at 550 g · most forward centroid with block B | 2.0 · −0.0240 | mm · m | `CL-D2-PACK-FWD-ROOM`, `-PACK-X-FWD-MIN` | `CHECKED` |
| Block section · stop bonds front / rear (≥ 85) | 2 849 · 182 / 403 | mm² · N | `CL-D2-BLOCK-SECTION`, `-FWD-STOP-BOND`, `-AFT-STOP-BOND` | `CHECKED` |
| Wire channel under the pack · crossing gap · crossing height | 3.5 (≥ 3.0) · 6.7 (≥ 6.7) · 54 (≥ 26) | mm | `CL-D2-FLOOR-CH-H`, `-CROSS-GAP`, `-CROSS-H` | `CHECKED` |
| Straps vs pack crash load · ties vs handle load | 200 vs 85 · 444 vs 76 | N | `CL-D2-STRAP-CAP`, `-TIE-CAP` | `UNVERIFIED` |
| Pitot tip · boom (AVN-005, unchanged) · socket depth · key flat | (−0.210, −0.046, 0.045) · 107 · 35 · 5.8 | m · mm · mm · mm | `CL-D2-PITOT-*` | `PROPOSED` |
| Antenna A / B to pack (≥ 30.7) · GPS to power items (≥ 100) | 34.6 / 38 · 152 | mm | `CL-D2-ANT-A/B-CLR`, `-GPS-CLR` | `CHECKED` |
| Mass · CG | 130.9 (allocation 131, D-48) · (−0.007, −0.003, 0.050) | g · m | `CL-D2-MASS` `EST` | `CHECKED`, 0.1 g margin |

## Channels (y ±0.0275 … ±0.0652)

| Left (−y), x | Item | Right (+y), x | Item |
|---|---|---|---|
| −0.138 … −0.103 | pitot socket + 32 mm flange on the nose wall; antenna B tube (10 mm inside) | −0.041 … 0.021 | FC on 4 gel cubes between end stops; 10 mm strap through the stop slots |
| −0.088 … −0.040 | airspeed between tie posts (21 mm), RX behind; antenna A tube above | 0.021 … 0.040 | JR tie bar, 3 tie slots (six in-line plugs) |
| −0.038 … −0.004 | PDB plate, 4 M3 inserts: F1's bus board and power frame | 0.044 … 0.072 | UBEC plate (F1) |
| 0.000 … 0.060 | AS150U park zone: F1's cradle `PWR-006` | 0.056 … 0.072 | side-wall exit 16 × 12 mm, z 0.027 … 0.039 (each side) |

Wiring paths: channel at x −0.0245 under the pack (R5, was −0.0655: the forward strap now sits there), landing on
the PDB plate (left) and the FC (right); side-wall exits for power and DShot, aft-wall exits for servo leads; pack
leads over the aft stop, inboard of the left leg; GPS cable up the right leg into the grip groove and the mast bore.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-POD-01` | `WNG-001` core | shell bonded in the recess to bare foam (10 014 mm²) | C3, C6 |
| `E-POD-09` | `WNG-002` spar | handle saddles + foot bridge bonded (1 445 mm²), 1 tie per foot; handling only since R5 | C3, C2 |
| `E-POD-05` | `PWR-001` pack | field joint: 2 straps + guides + pads; block / forward stop ahead, spacers / aft stop behind | C3, C5, C1 |
| `E-POD-06` | mast ↔ handle | M3x16 PA66 screw + PA66 nut, grip 10.0 mm, finger tight + ¼ turn | C6 |
| `E-POD-10` · `-11` · `-13` | spacers ↔ aft stop · block ↔ forward stop · spreader ↔ block | trapped, slid (`CT-SLIDE-STOP`) | C3, C5 |
| `E-POD-12` | `PWR-001` pack | thermal, insulating; heat leaves by the vents (47.1 °C at landing) | E3 |
| `E-POD-02 … -04, -07, -08` | internal | bonds (incl. the 1 mm stop-to-nose-wall line), hatch tongue + tab, strap slots, socket flange | C3, C6 |

Acknowledged: `E-PWR-03/-04/-05`, `E-AVN-01 … -05, -07, -10`, `E-HRN-01`.

## Mass budget

130.9 g `EST` against 131 g (D-48). R5a (D-59): 12 mm CAD stack (+0.7 g) paid by U-spacer legs 5 → 4 mm (−0.4 g) and the shorter gussets and rear windows (−0.4 g). R5: R4 128.1 g, + nose shell and hatch 15 mm longer, + tray 21 mm longer at the
front and the aft stop (5.3 g) moved onto it from the handle, − XPS block A, − the handle's aft stop and gussets.
Levers if the weigh-in is heavy (each needs C3): a lead window in the aft stop −1.5 g; tray floor 1.0 → 0.8 mm −2.4 g.

## Open issues

| Issue | Owner |
|---|---|
| Crash path changed: block A gone, the stop is backed by the nose wall; the crush plateau now loads the nose wall | C5, C3 (CR-D2-10, -11) |
| Forward trim room 2.0 mm with C5's 25.7 mm block (D-47 quotes 3.4 mm with 24.3 mm) | A3, C5 |
| A 157 mm alternative pack SKU leaves an 18.7 mm block at most; at −0.010 its aft face is 0.0685 > 0.060 (CR-D2-22) | E2 |
| Aft stop at 0.060 leaves 2 mm of tray behind it: gussets are 2 mm root ribs; C3's 3 mm stop check (+7 %) ignores them; `T-C3-STOP-PUSH` decides | C3 (CR-D2-23) |
| Crash per pack at the D-59 stations (503 g block 25.7 mm, on the stack) | C5 (CR-D2-23) |
| `POD-001` / `POD-003` mass CG vs uniform body centroid 14.7 / 10.0 mm (bonded multi-material parts) | A5 (CR-D2-19) |

## How to verify

`python -I redesign/team/D2/pod_data.py --check` · `python -I redesign/fusion/check.py` · `python -I
redesign/interfaces/merge_check.py` · `python -I redesign/team/D2/pod_selfcheck.py` · built: `T-D2-WEIGH`,
`T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-C3-STOP-PUSH`, `T-A3-CG-BALANCE`.
