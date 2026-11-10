# Pod

Status: `MODELLED` (D2, revision D2-R4 on params A1-R3, 2026-11-09). Answers CR-F2-03, CR-F3-12, CR-C6-17/18/19,
CR-A4-23, CR-F1-17. CAD `fusion/pod.py`; masses and CGs from the CAD by `team/D2/pod_data.py`; claims
`team/D2/pod_claims.py`; forward-trim option `team/D2/pod_station_options.py`.

## Purpose

Hold the 4S 6500 pack at the station that balances the aircraft, keep it to ≤ 100 g in a 5 m/s nose-in crash (crush
block, C5) and in place at 12.75 g (straps, stops, C3), give one place to lift the aircraft (grip on the spar, D-23),
and carry the FC, RX, airspeed, power items, GPS and pitot with their wiring paths. Field use: hatch open, pack in
with its block and spacer, strap, plug, close. No tools.

## Bay, front to back (x, m)

| Item | x | Part |
|---|---|---|
| Nose wall 4.8 mm board · fixed XPS block A 7.0 mm | −0.115 … −0.1102 · … −0.1032 | `POD-001` |
| Forward stop 3 × 25 × 54 mm (C3), on the solid tray front piece | −0.1032 … −0.1002 | `POD-002` |
| Crush block B (cut per pack) + 1.5 mm spreader | −0.1002 … −0.071 (27.7 + 1.5 mm nominal) | `POD-008` |
| Wire channel across the bay under the pack, 10 mm (F2) | −0.0705 … −0.0605 | `POD-002` |
| Pack, nominal 550 g / 680 g | −0.071 … 0.069 / −0.067 … 0.073 | `PWR-001` |
| U-spacers 2 / 4 / 8 / 8 mm · aft stop 3 mm on the handle bridge | 0.069 … 0.077 · 0.077 … 0.080 | `POD-008` · `POD-007` |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod x range · width · height (outside) | −0.115 … 0.095 · 0.140 · 0.070 | m | `params.json#pod` | `PROPOSED` |
| Bay inside L × W × H (≥ 0.160 × 0.052 × 0.053) | 0.177 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid nominal · 680 g · aft reach · most forward with block B | −0.001 · 0.003 · 0.007 · −0.0038 | m | `CL-D2-PACK-X-*`, `-AFT-REACH`, `-PACK-X-FWD-MIN` | `CHECKED` |
| Nose extension for C5's 550 g / 503 g forward stations | 10.6 / 14.7 | mm | `CL-D2-NOSE-EXT-NOM/-LIGHT` (CR-D2-16) | `PROPOSED` |
| Block B nominal · section · forward-stop tray bond | 27.7 (≥ 24.9) · 2 849 · 180 (≥ 85) | mm · mm² · N | `CL-D2-BLOCK-B-NOM`, `-BLOCK-SECTION`, `-FWD-STOP-BOND` | `CHECKED` |
| Wire channel under the pack · crossing gap · crossing height | 3.5 (≥ 3.0) · 6.7 (≥ 6.7) · 54 (≥ 26) | mm | `CL-D2-FLOOR-CH-H`, `-CROSS-GAP`, `-CROSS-H` | `CHECKED` |
| Straps vs pack crash load · ties vs handle load | 200 vs 85 · 444 vs 76 | N | `CL-D2-STRAP-CAP`, `-TIE-CAP` | `UNVERIFIED` |
| Pitot tip · boom · socket depth · key flat | (−0.195, −0.046, 0.045) · 107 · 35 · 5.8 | m · mm · mm · mm | `CL-D2-PITOT-*`, CR-F3-12 | `PROPOSED` |
| Antenna A / B to pack (≥ 30.7) · GPS to power items (≥ 100) | 34.6 / 44 · 152 | mm | `CL-D2-ANT-A/B-CLR`, `-GPS-CLR` | `CHECKED` |
| Mast screw past the grip (PA66, ≥ 4.0) | 6.0 | mm | `CL-D2-MAST-BOLT-PAST` | `CHECKED` |
| Mass · CG | 128.0 (allocation 122) · (0.000, −0.002, 0.051) | g · m | `CL-D2-MASS` `EST` | `FAIL` (CR-D2-09) |

## Channels (y ±0.0275 … ±0.0652)

| Left (−y), x | Item | Right (+y), x | Item |
|---|---|---|---|
| −0.110 … −0.088 | pitot socket + flange; antenna B tube | −0.041 … 0.021 | FC on 4 gel cubes between end stops; 10 mm strap through the stop slots |
| −0.088 … −0.040 | airspeed between tie posts (21 mm), RX behind; antenna A tube above | 0.021 … 0.040 | JR tie bar, 3 tie slots (six in-line plugs) |
| −0.038 … −0.004 | PDB plate, 4 M3 inserts: F1's bus board and power frame | 0.044 … 0.072 | UBEC plate (F1) |
| 0.000 … 0.060 | AS150U park zone: F1's cradle `PWR-006` | 0.056 … 0.072 | side-wall exit 16 × 12 mm, z 0.027 … 0.039 (each side) |

Wiring paths: channel at x −0.0655 under the pack (guides notched 3 mm); side-wall exits for power and DShot,
aft-wall exits for servo leads; pack leads over the aft stop, inboard of the left leg; GPS cable up the right side
wall, into the right-leg window (z 0.055 … 0.065), up the leg, along the groove under the grip, up the mast bore.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-POD-01` | `WNG-001` core | shell bonded in the recess to bare foam (10 014 mm²) | C3, C6 |
| `E-POD-09` | `WNG-002` spar | handle saddles + stop bridge bonded (1 445 mm²), 1 tie per foot | C3, C2 |
| `E-POD-05` | `PWR-001` pack | field joint: 2 straps + guides + pads; block / forward stop and spacers / aft stop | C3, C5, C1 |
| `E-POD-06` | mast ↔ handle | M3x16 PA66 screw + PA66 nut, grip 10.0 mm, finger tight + ¼ turn | C6 |
| `E-POD-12` | `PWR-001` pack | thermal, insulating; heat leaves by the vents (47.1 °C at landing) | E3 |
| `E-POD-02 … -04, -07, -08, -10, -11` | internal | bonds, hatch tongue + tab, strap slots, socket flange, trim kit | C3, C6 |

Acknowledged: `E-PWR-03/-04/-05`, `E-AVN-01 … -05, -07, -10`, `E-HRN-01`.

## Mass budget

128.0 g `EST` against 122 g: CR-D2-09 asks 128 g (131 g if CR-D2-16 moves the nose 12 mm). R4 added the corner
fillets (+1.5 g, C6), UBEC plate, JR bar and a solid tray front piece (+2 g); it removed 0.2 mm from the plates (1.0 → 0.8 mm, −1.3 g),
switched the mast hardware to PA66 (−1.1 g) and cut the grip groove (−0.5 g).

## Open issues

| Issue | Owner |
|---|---|
| Pack station: B3, A3 and C5 want it 10–21 mm forward; that needs the nose +12 mm (or +15 mm and a 6 mm spacer) | A1 (CR-D2-16) |
| Mass over allocation | A1 (CR-D2-09) |
| C3 and C5 re-run on the R3/R4 bay (C3's script reads retired keys) | C3, C5 (CR-D2-10, -11) |

## How to verify

`python -I redesign/team/D2/pod_data.py --check` · `python -I redesign/fusion/check.py` · `python -I
redesign/interfaces/merge_check.py` · `python -I redesign/team/D2/pod_selfcheck.py` · built: `T-D2-WEIGH`,
`T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-C3-STOP-PUSH`.
