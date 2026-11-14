# D2 — Pod designer, summary (revision D2-R5a)

> **R7 (2026-11-11, D-74 / D-77):** pack datum −0.032 → −0.036 (16 mm stack, block 26.2 vs C5's 25.8 mm); stations
> 546 / 550 / 590 g at −0.036 / −0.034 / −0.030. UBEC plate removed, `KO-PWR-*` reserved and checked (0 pod bodies),
> forward strap to x −0.079, XT30U zones inside both side exits (0 bodies). Case-U outboard side clearance is 1.8 mm,
> not 6 (CR-D2-31). Pod 144.2 g. See `subsystems/pod/SPEC.md`.

Status: `MODELLED` (2026-11-10, params A1-R4a). R5 was the D-47 re-lay (CR-A1-43, CR-A3-22) at the D-48 allocation
of 131 g, plus the CR-A5-27 CG fix. R5a adds D-59 (CR-A1-54), which A1 decided after R5. The pod has no errors in
`fusion/check.py` or `merge_check.py` and no issues in the strict self-check. All 50 D2 claims pass.

## Action items this round

| Request | Result | Claim |
|---|---|---|
| CR-A3-22 / CR-A1-43 / D-47 (blockers) | Done at R5. Nose shell is −0.130 … 0.095 (0.225 long). The nose block went from 14.8 to 8.8 mm: XPS block A was deleted and a 1 mm epoxy line remains. The bay moved 21 mm forward, with the forward stop at −0.1212. The datum is read from `pod.pack_x_nominal_m` (−0.022). The spacer set is 2/4/6/8/8, colour-coded. The pitot socket moved with the nose; boom `AVN-005` is unchanged (tip −0.210). Saddle `POD-007` stays at x 0.080 | `CL-D2-FWD-STOP-X`, `-NOSE-TO-STOP`, `-PITOT-BOOM-L` |
| D-59 / CR-A1-54 (new since R5) | Aft stop 0.056 → **0.060**. The CAD pack sits at the −0.022 datum with a 12 mm stack (blue + yellow). The flight stations are the D-59 ones. The datum was not moved to −0.018 | `ASM-D2-AFT-STOP-X`, `CL-D2-PACK-X-*` |
| D-48 / CR-A5-27 | 130.9 g against 131 g. Each part's `cg_xyz_m` is regenerated from its bodies by `pod_data.py`: `POD-008` … `-010` are at 0.0 mm. `POD-001` and `POD-003` are bonded multi-material parts (CR-D2-19) | `CL-D2-MASS` |

## Key numbers others build on

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Forward stop · aft stop face · bay length | −0.1212 · 0.060 · 0.1812 | m | `CL-D2-FWD-STOP-X`, `ASM-D2-AFT-STOP-X`, `CL-D2-BAY-L` | `CHECKED` |
| Pack centroid: datum (CAD) · 550 · 503 · 680 g | −0.022 · −0.018 · −0.024 · −0.010 | m | `CL-D2-PACK-X-NOM/-550/-LIGHT/-HEAVY` | `CHECKED` |
| Spacer stack: CAD · 550 · 503 · 680 g | 12 (blue + yellow) · 8 (blue) · 14 (blue + green) · 0 | mm | `CL-D2-SPACER-NOM/-LIGHT/-HEAVY` | `CHECKED` |
| Crush block B 503 · 550 · 680 g (minimum) | 25.7 (23.5) · 31.7 (25.7) · 39.7 (31.8) | mm | `CL-D2-BLOCK-B-LIGHT/-550/-HEAVY` | `CHECKED`, scaling `UNVERIFIED` |
| Forward room at the datum · most forward centroid | 2.0 · −0.0240 | mm · m | `CL-D2-PACK-FWD-ROOM`, `-PACK-X-FWD-MIN` | `CHECKED` |
| Stop bonds, front · rear (≥ 85) | 182 · 403 | N | `CL-D2-FWD-STOP-BOND`, `-AFT-STOP-BOND` | `CHECKED` |
| Pod mass (allocation 131) · CG | 130.9 · (−0.007, −0.003, 0.050) | g · m | `CL-D2-MASS` `EST` | `CHECKED`, 0.1 g margin |

## R5a design notes

| Item | Decision |
|---|---|
| Aft stop gussets | At 0.060 the stop's back face is at 0.063, 2 mm from the tray end. The gussets shrink from 6 to 2 mm and now act only as root ribs. C3 already sizes the 3 mm stop without them (14.0 vs 15 MPa). C3 re-checks this and `T-C3-STOP-PUSH` decides (CR-D2-23) |
| Mass | The extra 4 mm spacer adds 0.7 g. U-spacer legs 5 → 4 mm save 0.4 g (bearing 0.4 MPa at 85 N), and the shorter gussets save another 0.4 g |
| Straps | Slots unchanged at −0.054 / 0.016. They cover centroids −0.0275 … −0.0105, so the 680 g pack's straps sit 0.5 mm off its quarter points (accepted) |

## Checks run (2026-11-10)

| Command | Result for the pod |
|---|---|
| `python -I redesign/fusion/check.py` | pod ok: 10 parts, 63 bodies, 131 g, 0 errors |
| `python -I redesign/interfaces/merge_check.py` | PASS (0 errors, 21 warnings, none from the pod) |
| `python -I redesign/team/D2/pod_selfcheck.py` (strict) | PASS, 0 pod issues |
| `python -I redesign/team/D2/pod_data.py --check` | up to date |
| `python -I redesign/team/D2/pod_claims.py` | 50 claims, all pass |

## Change requests

CR-D2-23 is new: C3 re-checks the aft stop, C5 re-runs the crash at each pack station, H3 takes the spacer colours,
and F2 and A5 are told `pack_aft_face_m` is now [0.048, 0.060]. Still open: CR-D2-22 (E2: 157 mm SKU does not fit),
CR-D2-10 (C5), CR-D2-11 (C3), CR-D2-13 (F1), CR-D2-19 … -21. Details are in `team/D2/CHANGE-REQUESTS.md`.

## Files

`subsystems/pod/{SPEC.md, BUILD.md, parts.csv, interfaces.json, params.json, fusion/pod.py}`;
`team/D2/{pod_data.py, pod_claims.py, claims.json, pod_selfcheck.py, pod_station_options.py, CHANGE-REQUESTS.md}`.
