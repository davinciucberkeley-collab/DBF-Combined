# Pod

Status: `MODELLED` (D2, 2026-11-09). Centre pod on the wing upper surface: pack bay with aft trim, FC and avionics
side channels, hatch, pitot socket, and a carry handle on the spar that also carries the GPS mast. CAD
`fusion/pod.py`; masses and CGs from the CAD by `team/D2/pod_data.py`; claims `team/D2/pod_claims.py`.

## Purpose

Hold the 4S 6500 pack where it balances the aircraft (nominal station forward, trim aft only), survive a 12.75 g
crash with the pack in, give one place to lift the aircraft (on the spar, not the motors, D-23), and mount the FC,
RX, airspeed sensor, power items, GPS and pitot. Field use: open the hatch, strap the pack, plug in, close. No tools.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Pod x range · width · height (outside) | −0.105 … 0.095 · 0.140 · 0.070 | m | `params.json#pod`, width `CR-D2-01` | `PROPOSED` |
| Pack bay inside L × W × H | 0.164 × 0.052 × 0.059 (≥ 0.160 × 0.052 × 0.053) | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid at the forward stop · ahead of pod centre | −0.0302 · 25 | m · mm | `CL-D2-PACK-X-FWD`, `CL-D2-PACK-AHEAD` (D-17 asked 29, `CR-D2-02`) | `CHECKED` |
| Aft trim travel (spacers 5 / 8 / 10 mm) | 23.7 (need 18) | mm | `CL-D2-PACK-TRAVEL` | `UNVERIFIED` (need from A3) |
| Pack centroid height | 0.046 | m | `CL-D2-PACK-Z` | `CHECKED` |
| Recess D1 cuts: x · depth at aft end · foam left under | 0.023 … 0.065 · 6.9 · 23.5 | m · mm · mm | `CL-D2-RECESS-*` | `CHECKED` |
| Strap capacity vs pack crash load | 200 vs 85 | N | `CL-D2-STRAP-CAP`, `CL-C1-PACK-CRASH-LOAD` | `UNVERIFIED` (pull test) |
| Spar-tie capacity vs pod-group crash load | 444 vs 113 | N | `CL-D2-TIE-CAP`, `CL-D2-POD-CRASH-F` | `UNVERIFIED` (tie rating) |
| Handle load, 2 g lift, ultimate | 76 | N | `CL-D2-HANDLE-F-ULT` | `CHECKED` |
| Pod-to-wing bond: area · stress (L1 ult) vs allowable | 10 014 mm² · 37 vs 100 | kPa | `CL-D2-BOND-STRESS` (C3 sizes, `CR-D2-05`) | `UNVERIFIED` |
| Pitot tip · boom length · socket depth | (−0.185, −0.046, 0.045) · 107 · 35 | m · mm · mm | `CL-D2-PITOT-*`, y `CR-D2-03` | `PROPOSED` |
| GPS antenna centre | (0.080, 0, 0.169) | m | `pod.py#layout` | `MODELLED` |
| Mass · CG | 100.4 · (0.012, −0.001, 0.052) | g · m | `CL-D2-MASS` | `UNVERIFIED` (`EST`) |

## Parts

| Id | Part | Make | Mass g |
|---|---|---|---|
| `POD-001` | Shell: foam-board floor, walls, nose, aft wall, aft deck; XPS LE filler; printed nose lip | knife/laser, hot wire, FDM | 19.8 |
| `POD-002` | Tray: bay floor + guides + aft stop; FC plate (4 × M3 inserts); avionics plate (2 × M2) | FDM PETG ×3 | 23.9 |
| `POD-003` | Hatch: foam board, printed tongue, hook-and-loop tab | knife, FDM | 7.2 |
| `POD-004` | 2 pack straps 20 mm + 2 silicone pads | buy | 10.1 |
| `POD-005` | GPS mast, plugs into the grip | FDM | 5.6 |
| `POD-006` | Pitot socket, left channel, through the nose wall | FDM | 3.1 |
| `POD-007` | Carry handle: 2 spar-saddle feet, 2 legs, grip, mast socket; 2 ties; label | FDM | 26.5 |
| `POD-008` | Trim spacers 5 / 8 / 10 mm | FDM | 4.2 |

## Interfaces

| Edge | To | How | Sized by |
|---|---|---|---|
| `E-POD-01` | `WNG-001` core | shell bonded in the recess, tape skin off under the pod (10 014 mm²) | C3 |
| `E-POD-09` | `WNG-002` spar | handle feet bonded on the spar top + 1 nylon tie each round foot and spar | C3, C2 |
| `E-POD-05` | `PWR-001` pack | 2 straps (z, y); nose wall / spacers / aft stop (x); +x hover landing into the aft stop | C3, C1 |
| `E-POD-06` | mast ↔ handle | M3x16 SHCS + nyloc across the socket | D2 |
| `E-POD-02/03/04/07/08/10` | internal | bonded / tongue + tab / strap slots / bonded / bonded / trapped | D2 |
| acknowledged | `E-PWR-01…04` `E-AVN-01…05` `E-HRN-01` | FC M3 on the right plate; airspeed M2 on the left plate; RX, UBEC, PM, XT60 on the left floor; pitot in the socket | F1, F3, F2 |

Layout (looking aft): bay in the middle (y ±0.026), right channel y 0.027…0.065 = FC (x −0.040…0.020),
left channel = airspeed sensor at the front, RX, power module, UBEC, XT60 parked at x 0.030…0.060. Pack leads
leave the pack aft face over the stop wall and turn into the left channel. Harness exits: two 16 × 12 mm holes in
the aft wall at y ±0.042…0.058.

## Mass budget

| Allocation | CAD estimate | Margin | Status |
|---|---|---|---|
| 105 g (`params.json#mass.allocation_g.pod`) | 100.4 g | +4.6 g (4 %) | `UNVERIFIED` (foam board 0.20 kg/m² and PETG fill are estimates) |

## Open issues

| # | Issue | Owner |
|---|---|---|
| 1 | Width 0.10 → 0.14 m to fit the FC beside the pack (`CR-D2-01`); B1 re-runs pod drag (+0.003 m² frontal) | A1, B1 |
| 2 | Pack nominal 25 mm, not 29 mm, ahead of the pod centre; slide is 0 … +23.7 mm aft, not ±30 (`CR-D2-02`) | A1, A3 |
| 3 | Pitot tip y 0 → −0.046 m; boom OD 6 mm assumed (`CR-D2-03`) | F3, B4, A1 |
| 4 | Recess, skin-off area, open spar slot at the feet and ties laid under the spar (`CR-D2-04`) | D1 |
| 5 | FC 30.5 mm pattern and MS5525 2-hole pitch are placeholders (`CR-D2-06`) | F3 |
| 6 | Bond and retention numbers above are first cuts (`CR-D2-05`) | C3 |

## How to verify

| Check | Command or test |
|---|---|
| CAD builds, touches, registers | `python -I redesign/fusion/check.py`; until D1/F1 publish: `python -I redesign/team/D2/pod_selfcheck.py` |
| Masses and CGs match the CAD | `python -I redesign/team/D2/pod_data.py --check` |
| Claims re-run | `python -I redesign/team/D2/pod_claims.py` then `python -I redesign/proofs/build_graph.py` |
| Bench | `T-D2-WEIGH`, `T-D2-FIT`, `T-D2-STRAP-PULL`, `T-D2-HANDLE-PULL`, `T-D2-BOND-PULL` (BUILD.md) |
