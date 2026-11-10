# Pod

Status: `MODELLED` (D2, revision D2-R3 on params A1-R3, 2026-11-09). Answers CR-A1-27 (D-24, D-25). Centre pod on
the wing upper surface: pack bay with a crush block ahead and spacers behind, FC and avionics side channels, hatch,
pitot socket, vents, two antenna exits, and a carry handle on the spar that also carries the aft stop and the GPS
mast. CAD `fusion/pod.py`; masses and CGs from the CAD by `team/D2/pod_data.py`; claims `team/D2/pod_claims.py`.

## Purpose

Hold the 4S 6500 pack at the station that balances the aircraft (nominal centroid x −0.001 m), keep it to ≤ 100 g
in a 5 m/s nose-in crash (crush block, C5) and in place at 12.75 g (straps, stops, C3), give one place to lift the
aircraft (on the spar, D-23), and mount the FC, RX, airspeed sensor, power items, GPS and pitot. Field use: hatch
open, pack in with its block and spacer, strap, plug, close. No tools.

## Bay, front to back (x, m)

| Item | x | Part | Status |
|---|---|---|---|
| Nose wall (foam board 4.8 mm), inside face | −0.115 … −0.1102 | `POD-001` | `MODELLED` |
| Fixed XPS nose block (block A), bonded to nose and side walls | −0.1102 … −0.1032 (7.0 mm) | `POD-001` | `MODELLED` |
| Forward stop, 3 mm PETG, 25 × 54 mm, on the tray (C3) | −0.1032 … −0.1002 | `POD-002` | `MODELLED` |
| Crush block B (XPS F-250, cut per pack) + 1.5 mm spreader | −0.1002 … −0.071 (27.7 + 1.5 mm nominal) | `POD-008` | `MODELLED` |
| Pack, nominal / 680 g | −0.071 … 0.069 / −0.067 … 0.073 | `PWR-001` | `MODELLED` |
| U-spacers (set 2 / 4 / 8 / 8 mm), nominal 8, 680 g 4 | 0.069 … 0.077 | `POD-008` | `MODELLED` |
| Aft stop, 3 mm + 2 gussets, on a bridge between the spar saddles | 0.077 … 0.080 | `POD-007` | `MODELLED` |

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod x range · width · height (outside) | −0.115 … 0.095 · 0.140 · 0.070 | m | `params.json#pod` (D-25) | `PROPOSED` |
| Bay inside L × W × H (≥ 0.160 × 0.052 × 0.053) | 0.177 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid nominal · 680 g · aft reach | −0.001 · 0.003 · 0.007 | m | `CL-D2-PACK-X-NOM/-HEAVY`, `CL-D2-AFT-REACH` (≥ C5 heavy −0.0016) | `CHECKED` |
| Most forward centroid that keeps C5's block B · spacer set vs range | −0.0038 · 22 vs 10.8 | m · mm | `CL-D2-PACK-X-FWD-MIN`, `CL-D2-SPACER-SUM` | `CHECKED` |
| Block B nominal · section · block A | 27.7 (≥ 24.9) · 2 849 · 7.0 | mm · mm² · mm | `CL-D2-BLOCK-B-NOM`, `-BLOCK-SECTION`, `-NOSE-BLOCK-L` | `CHECKED` |
| Pack centroid height · underside clearance over the spar slot | 0.048 · 0.78 | m · mm | `CL-D2-PACK-Z`, `CL-D2-OVERHANG-CLR` (2.5 mm EVA pads) | `CHECKED` |
| Recess D1 cuts: x · depth at aft end · foam left under | 0.023 … 0.065 · 6.9 · 23.5 | m · mm · mm | `CL-D2-RECESS-*` (unchanged) | `CHECKED` |
| Straps vs pack crash load · ties vs handle load | 200 vs 85 · 444 vs 76 | N | `CL-D2-STRAP-CAP`, `CL-D2-TIE-CAP` | `UNVERIFIED` (pull tests) |
| Pitot tip · boom length · socket depth · flange | (−0.195, −0.046, 0.045) · 107 · 35 · 32 × 32 | m · mm · mm · mm | `CL-D2-PITOT-*`, CR-C6-09 | `PROPOSED` |
| Antenna A / B element to pack (≥ 30.7 mm) · GPS to power items (≥ 0.10 m) | 34.6 / 44 · 0.153 | mm · m | `CL-D2-ANT-A/B-CLR`, `CL-D2-GPS-CLR` | `CHECKED` |
| GPS centre · pad | (0.076, 0, 0.178) · 45° toward the nose | m | `pod.py#layout`, CR-F3-03 | `MODELLED` |
| Mass · CG | 127.3 (allocation 122) · (0.001, −0.003, 0.052) | g · m | `CL-D2-MASS` | `UNVERIFIED` (`EST`; CR-D2-09) |

## Channels (y ±0.0275 … ±0.0652, 37.7 mm)

| Left (−y), front to back | x | Right (+y) | x |
|---|---|---|---|
| Pitot socket + flange; antenna B tube below it (z 0.0245) | −0.110 … −0.088 | free | −0.103 … −0.041 |
| Airspeed MS4525DO (foam tape + 1 tie), RX behind (tape); antenna A tube above the RX | −0.088 … −0.044 | FC on 2 gel pads between end stops | −0.041 … 0.021 |
| PDB on 4 M3 inserts (25 mm pattern `UNVERIFIED`), fuse holder | −0.042 … 0.000 | — | — |
| AS150U park (60 mm) | 0.000 … 0.060 | UBEC zone (tape) | 0.042 … 0.088 |
| Pack leads turn in, harness exit 11 × 16 mm | 0.060 … 0.090 | harness exit 11 × 16 mm | 0.088 … 0.090 |

Vents (CR-E3-03): 30 × 15 mm inlet top centre of the nose wall and nose block, 30 × 8 mm groove over the crush block,
6.9 mm over the pack, 30 × 15 mm exit in the aft wall. Pack leads exit aft over the stop (top z 0.050), turn left
inboard of the handle leg (y ±0.048) to the park.

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-POD-01` | `WNG-001` core | shell bonded in the recess to bare foam (10 014 mm²) | C3, C6 |
| `E-POD-09` | `WNG-002` spar | handle saddles + stop bridge bonded (1 445 mm²), 1 tie per foot at y ±0.036 | C3, C2 |
| `E-POD-05` | `PWR-001` pack | 2 straps + guides + pads (z, y); block / forward stop and spacers / aft stop (x) | C3, C5, C1 |
| `E-POD-06` | mast ↔ handle | M3x16 brass SHCS + brass nut + Loctite 222, grip 10.0 mm, 5.5 past | C6, F3 |
| `E-POD-10` / `-11` | trim kit ↔ aft stop / forward stop | trapped | C3, C5 |

Retired at R3: `CL-D2-BOND-STRESS` (C3's `CL-C3-BOND-R-*` own it, CR-C3-04). Open: `team/D2/CHANGE-REQUESTS.md`.
