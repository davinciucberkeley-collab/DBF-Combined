# D2 — Pod designer, summary (revision D2-R4)

Status: `MODELLED` (2026-11-09, params A1-R3). The pod passes `fusion/check.py` and `merge_check.py` with no errors
of its own. One warning remains: mass over the allocation (CR-D2-09).

## What changed at R4

| Request | Change | Claim |
|---|---|---|
| F2 CR-F2-03 | side-wall exits; 10 mm wire channel under the pack (tray split, guides notched); JR tie bar; GPS cable path in the right leg, the grip groove and the mast bore; UBEC zone 0.044 … 0.072 | `CL-D2-FLOOR-CH-H`, `-CROSS-GAP`, `-CROSS-H` |
| F3 CR-F3-12 | tie posts 21 mm apart (params); avionics plate to −0.040; PDB plate from −0.038; FC end-stop strap slots; keyed pitot bore | — |
| C6 CR-C6-17/-18/-19 | corner fillets; PA66 mast screw (grip 10.0 mm); FC secondary strap | `CL-D2-MAST-BOLT-PAST` |
| A4 CR-A4-23 | `field_joint` on `E-POD-05`; `E-POD-12` thermal edge; one `E-POD-06` stack with C6; acknowledgements | — |
| F1 CR-F1-16/-17 | park slot left to F1's frame `PWR-006`; UBEC plate added | — |
| Pack station (B3, A3, C5) | forward stop now derived from the nose; what-if script; CR-D2-16 | `CL-D2-FWD-STOP-X`, `-NOSE-EXT-NOM/-LIGHT` |

## Key numbers others build on

| Parameter | Value | Unit | Claim | Status |
|---|---|---|---|---|
| Bay inside L × W × H | 0.177 × 0.052 × 0.057 | m | `CL-D2-BAY-L/-W/-H` | `CHECKED` |
| Forward stop face · most forward pack centroid with block B | −0.1002 · −0.0038 | m | `CL-D2-FWD-STOP-X`, `-PACK-X-FWD-MIN` | `CHECKED` |
| Nose extension for C5's 550 g / 503 g stations | 10.6 / 14.7 | mm | `CL-D2-NOSE-EXT-NOM/-LIGHT` | `PROPOSED` |
| Block B nominal · forward-stop tray bond | 27.7 · 180 | mm · N | `CL-D2-BLOCK-B-NOM`, `-FWD-STOP-BOND` | `CHECKED` |
| Wire channel · crossing gap | 3.5 · 6.7 | mm | `CL-D2-FLOOR-CH-H`, `-CROSS-GAP` | `CHECKED` |
| GPS to the nearest power item | 0.152 | m | `CL-D2-GPS-CLR` | `CHECKED` |
| Pod mass (allocation 122) | 128.1 | g | `CL-D2-MASS` `EST` | `FAIL` |

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
