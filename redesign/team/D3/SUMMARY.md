# D3 Fins and motor tubes: summary

> **2026-11-13 (D-90 ... D-92, Dillon Alcouffe):** collar 22 mm, pins 12 mm pitch, mount grip 18 mm, root fillets
> 10 mm ahead of the hinge, 13 mm aft (fillets 25.0 -> 16.4 g). `CL-D3-MASS` 433.3 -> 432.0 g vs 438 g. CR-D3-35 (longer full fillet)
> withdrawn by D-92.

Revision D3-R5, 2026-11-10 (params A1-R5: D-61, D-63, D-65, D-68, D-70; C6-R5; E3 R3; F2 CR-F2-16). Answers
CR-A1-63. Subsystem files: `redesign/subsystems/fins/` (SPEC, parts.csv, interfaces.json, params.json, fusion/fins.py,
BUILD.md). Re-run: `python -I redesign/subsystems/fins/make_fins.py` → `python -I redesign/team/D3/fins_calcs.py` →
`python -I redesign/fusion/check.py` → `python -I redesign/interfaces/merge_check.py`.

## Action items (CR-A1-63 and the D-61…D-70 forwards)

| Item | Done in R5 | Value | Unit | Source | Status |
|---|---|---|---|---|---|
| Mount at D-61 (blocker) | `face_ahead_m` 0.0075, cheeks 12 → 17 mm (still reach the slit collar to the tube axis) | 7.5 / 17 | mm | `fin_detail.mount.*` | `MODELLED` |
| Prop plane x, A1 copies (carried −0.0127) | hub on the axis = face − 37.3 cos 7° | **−0.01267** | m | `CL-D3-X-PROP` | `CHECKED` |
| Plate face x, DP-MOTOR-FACE (carried 0.0244) | 0.045 − 13.15 − 7.5 mm | **0.02435** | m | `CL-D3-X-FACE` | `CHECKED` |
| Prop keep-out | `check.py` fins 0 errors, 0 keep-out errors (hull); E1 swept volume to tube 26.1 mm | 26.1 ≥ 25 | mm | `CL-E1-TIP-GAP-AT-75` | `MODELLED` |
| Block vertical edges (D-68) | four plan-form edges R 3 mm in the CAD (socket front, saddle aft) | 3 | mm | `fin_detail.block.edge_r_m` | `MODELLED` |
| Pins (D-70) | Ø 2.5 mm CF at 15 mm, epoxy injected | 1.59 | RF | `CL-C6-STRIP-PIN-RF-PROP` | `UNVERIFIED` |
| Station collar (D-70 13 mm) | **15 mm** drawn (C6-R5 CR-C6-36: 13 mm reads RF 0.9995) | 15 | mm | `CL-C6-COLLAR-RF-15MM` 1.15 | `FAIL` on C6's live re-run → CR-D3-36 |
| Strip-tail bond | BUILD step 13 inspection table: reach, full-length fill, tongue perimeters, tap, 20 N pull, recorded | — | — | CR-C4-37 | `PROPOSED` |
| E3 thermal blocks `E-FIN-85…88` | 61.6 → 56.1 °C, h 64.6 W/m² K text | 56.1 / 85 | °C | `CL-E3-ESC-PEAK` | `UNVERIFIED` |
| F2 phase tie lug | collar tail x 0.084 → 0.060, slot open along x | 0.060 | m | CR-F2-16 | `MODELLED` |
| `E-FIN-81…88` with E1 | declared; E1 acknowledges all 8, no one-sided warning | — | — | `merge_check.py` | `CHECKED` |

## Mass against 437 g (D-63) and levers

| Line | Value | Unit | Status |
|---|---|---|---|
| R5 before levers (mounts +3.8, pins +1.5, collar 15 mm +1.8, block R 3 −0.4) | 441.5 | g | `MODELLED` |
| **Taken:** fillet mix 0.55 → 0.45 g/cm³ (gate: T-D3-WEIGH cup ≤ 9.0 g / 20 cm³; strength set by paper/XPS, fillet fail-safe only) | −5.6 | g | `PROPOSED` |
| Not taken: block fill 0.55 → 0.45 (needs C4 `CL-C4-D3-BLOCK-MS` on the R 3 mm block, CR-D3-37) | (−13.8) | g | `PROPOSED` |
| Not taken: mount cheeks (withdrawn; 17 mm is set by the reach to the collar) | — | g | — |
| **Fins** `CL-D3-MASS` | **435.9 / 437** | g | `MODELLED` |

## Checks

| Check | Result | Status |
|---|---|---|
| `make_fins.py` | 42 parts, 88 edges, 0 pending, 435.9 g | `MODELLED` |
| `fins_calcs.py` | 29 claims; 3 fail on new upstream loads: `CL-D3-COLLAR-H-C6` 0.77, `CL-D3-ROOT-FILLET-RF-ALLOW` 0.81, `CL-D3-ROOT-LEFF-REQ` 0.182 > 0.150 m | `FAIL` → CR-D3-35/36 |
| `check.py` | fins ok, 0 errors, 0 warnings; 0 keep-out errors. Run FAIL from pod/avionics (D2 bay re-lay) and missing POD/AVN parts | fins `CHECKED` |
| `merge_check.py` | PASS, 0 errors, 1 warning (propulsion 462 / 462 g); no fins warnings | `CHECKED` |

## Open (with D3's proposed fix)

1. **Root fillet** (CR-D3-35): on the D-65 59.0 N side load the root is 19 % short at the C6 allowable. Fix: 15 mm
   zone forward to L_eff 0.185 m (+5 g) once C4 gives the fillet share and C2 accepts the tab shear.
2. **Collar** (CR-D3-36): C6's live run reads C1 12.67 N·m (R4 7.40) and needs 19.4 mm. 20 mm fits (+3 g). D3 redraws
   once C1/C6 confirm the value.
3. Both fixes together take fins to about 444 g, 7 g over 437. A1 decides the allocation, or C4 clears the block-fill
   lever (−13.8 g).
