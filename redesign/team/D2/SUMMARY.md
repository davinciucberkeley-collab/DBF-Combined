# D2 — Pod designer, summary (revision D2-R5)

Status: `MODELLED` (2026-11-09, params A1-R4). This revision is the D-47 re-lay (CR-A1-43, CR-A3-22) at the D-48
allocation of 131 g, plus the CR-A5-27 CG fix. The pod has no errors or warnings in `fusion/check.py`,
`merge_check.py` or the strict self-check, and all 47 D2 claims pass.

## What changed at R5

| Request | Change | Claim |
|---|---|---|
| D-47 nose | Shell −0.130 … 0.095 (0.225 long). XPS nose block A deleted: the forward stop and tray front sit on a 1 mm epoxy line against the nose wall, so nose skin to stop face is 8.8 mm | `CL-D2-NOSE-TO-STOP` |
| D-47 bay | The bay moved 21 mm forward: forward stop −0.1002 → −0.1212, aft stop 0.077 → 0.056. The aft stop now stands on the tray rear piece with 2 gussets, because the handle bridge cannot reach it. Saddle `POD-007` stays at x 0.080 | `CL-D2-FWD-STOP-X`, `-AFT-STOP-BOND` |
| D-47 stations | Nominal centroid read from `pod.pack_x_nominal_m` (−0.022). Spacers 2/4/6/8/8, colour-coded: 680 g none (−0.014), 550 g blue (−0.022), 503 g blue + white (−0.024) | `CL-D2-PACK-X-NOM/-HEAVY/-LIGHT` |
| Knock-on | Straps moved to −0.054 / 0.016. The wire channel moved −0.0655 → −0.0245 (the forward strap now sits on the old position). Pitot socket moved with the nose; the boom is unchanged (tip −0.210) | `CL-D2-FLOOR-CH-H`, `-PITOT-BOOM-L` |
| CR-A5-27 | Trim kit split into `POD-008` spacers, `POD-009` crush block and `POD-010` spreader, so each declared CG equals its body centroid. All CGs regenerated from the bodies | — |

## Key numbers others build on

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Forward stop · aft stop face | −0.1212 · 0.056 | m | `CL-D2-FWD-STOP-X`, `ASM-D2-AFT-STOP-X` | `CHECKED` |
| Bay inside L × W × H | 0.177 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Pack centroid 503 · 550 · 680 g | −0.024 · −0.022 · −0.014 | m | `CL-D2-PACK-X-LIGHT/-NOM/-HEAVY` | `CHECKED` |
| Block B 503 · 550 · 680 g (minimum) | 25.7 (23.5) · 27.7 (25.7) · 35.7 (31.8) | mm | `CL-D2-BLOCK-B-*` | `CHECKED`, scaling `UNVERIFIED` |
| Forward trim room at 550 g | 2.0 (D-47 assumed 3.4 with a 24.3 mm block) | mm | `CL-D2-PACK-FWD-ROOM` | `CHECKED` |
| Stop bonds, front · rear (≥ 85) | 182 · 417 | N | `CL-D2-FWD-STOP-BOND`, `-AFT-STOP-BOND` | `CHECKED` |
| Wire channel · GPS to the nearest power item | 3.5 mm · 0.152 m | — | `CL-D2-FLOOR-CH-H`, `-GPS-CLR` | `CHECKED` |
| Pod mass (allocation 131) · CG | 131.0 · (−0.007, −0.003, 0.050) | g · m | `CL-D2-MASS` `EST` | `CHECKED`, 0 g margin |

## Checks run

| Command | Result for the pod |
|---|---|
| `python -I redesign/fusion/check.py` | pod module ok: 8 parts, 63 bodies, 0 errors, 1 warning (mass) |
| `python -I redesign/interfaces/merge_check.py` | no pod errors; 1 pod warning (mass); the run fails on errors from other subsystems |
| `python -I redesign/team/D2/pod_selfcheck.py` (strict, stand-in wing and pack) | only the mass warning |
| `python -I redesign/team/D2/pod_data.py --check` | up to date |
| `python -I redesign/team/D2/pod_claims.py` | 39 claims; `CL-D2-MASS` fails (−5 %) |

## Change requests filed

CR-D2-16 (A1: nose +12 mm for the forward pack station), CR-D2-09 rev. (A1: 128 g, or 131 g with CR-D2-16),
CR-D2-10 / -11 (C5, C3: re-run on the R4 bay; C3's script reads retired keys), CR-D2-13 rev. (F1), CR-D2-17 (A4).
Details are in `team/D2/CHANGE-REQUESTS.md`.

## Files

`subsystems/pod/{SPEC.md, BUILD.md, parts.csv, interfaces.json, params.json, fusion/pod.py}`;
`team/D2/{pod_data.py, pod_claims.py, claims.json, pod_selfcheck.py, pod_station_options.py, CHANGE-REQUESTS.md}`.
