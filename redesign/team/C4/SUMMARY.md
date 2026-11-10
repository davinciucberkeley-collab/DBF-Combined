# C4 — Fin and motor-tube structures (R4, 2026-11-10)

Motor tubes, half-fins, brace, station collar, strips, mounts and the through-core block of the K09-L quad tailsitter,
checked for strength, stiffness and vibration on D3's R4 fin. Full report: `BOOM-STRUCTURES.md`. Claims:
`claims.d3.json` (design) and `claims.json` (R1, shared assumptions only). Requests: `CHANGE-REQUESTS.md`.

## Verdict

**Vibration passes. One strength item fails as drawn:** the square fin tip under the D5 shoe (face MS −0.54).
Extending the D5 shoe cheeks 25 mm toward the wing fixes it (CR-C4-30). Everything else holds.

## Key numbers

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| First station mode, upper / lower | 275 / 268 | Hz | `CL-C4-D3-F1-UP`, `-F1-LO` | `UNVERIFIED` |
| Separation from 1P/2P (hover 5 416, cruise 5 894 rpm) | 0.37 (≥ 0.20) | — | `CL-C4-D3-SEP` | `UNVERIFIED` |
| Separation, worst E/G corner; with whirl | 0.29; 0.36 | — | `-SEP-WORST`, `-SEP-WHIRL` | `UNVERIFIED` |
| Mount rocking stiffness needed (bench pass ≥ 1 000) | 971 | N·m/rad | `CL-C4-D3-MOUNT-K-REQ` | `UNVERIFIED` |
| Fin face MS, D5 cheeks as drawn | −0.54 | — | `CL-C4-D3-MS-FACE` | `FAIL` |
| Fin face MS, cheeks to \|z\| 0.171 m: intact / fail-safe | +0.18 / +0.01 | — | `-MS-FACE-SHOE-INTACT`, `-MS-FACE-SHOE-FS` | `PROPOSED` |
| Collar bond MS, 12 mm (needs 10.3 mm) | +0.16 | — | `CL-C4-D3-MS-COLLAR` | `UNVERIFIED` |
| Collar torque into the tube, limit (for C6) | 6.24 | N·m | `CL-C4-D3-COLLAR-T` | `UNVERIFIED` |
| Wing-plane torsion, FE vs C1 | 7.37 / 7.37 (0.08 %) | N·m | `CL-C4-D3-SEC-T-VS-C1` | `CHECKED` |
| Brace 10 × 2 buckling MS (163 N vs 293 N) | +0.79 | — | `CL-C4-D3-MS-BRACE` | `UNVERIFIED` |
| Strip pin shear, design (pins required: bare MS −0.79) | 72.4 | N | `CL-C4-D3-STRIP-PIN-F` | `PROPOSED` |
| Strip force per face into the collar tail, design | 1 243 | N | `CL-C4-D3-STRIP-END-F` | `UNVERIFIED` |
| Foot side load (32.6 N × μ 0.7) | 22.8 | N | `CL-C4-D3-SIDE-LOAD` | `UNVERIFIED` |
| Swirl per half-fin at T_lim (B4 misbuilt) | 4.73 | N | `CL-C4-D3-SWIRL-F` | `UNVERIFIED` |
| Fins mass vs 418 g allocation | 436.4 | g | `CL-C4-D3-FINS-MASS` | `FAIL` |

## Action items this round

| Item | Result | Status |
|---|---|---|
| Re-run on D3-R4 (2 layers, 10 × 2, 12 mm collar, 16 mm as a check, D5 tip step) | done; the tip step makes the face fail (above) | `MODELLED` |
| μ 0.7 on the corner load (CR-C1-21) | 22.8 N side load | `MODELLED` |
| B4 swirl 0.57 N / 1.43 N misbuilt (CR-B4-19) | 4.73 N at T_lim; never governs | `MODELLED` |
| G3 set-down 23.2 N on the lower can (CR-C1-24) | cap MS +38.6, brace 0.61 N | `MODELLED` |
| Campbell at 5 416 / 5 894 rpm | whirl 267 Hz, separation 0.36 | `MODELLED` |
| Singular matrix / NaN (CR-C6-20) | 0 C4 calculation errors in `build_graph.py` | `CHECKED` |
| Ids `FIN-001-UR/UL/LR/LL` (CR-A4-47) | both claim files | `CHECKED` |
| Collar torque claim for C6 | `CL-C4-D3-COLLAR-T` 6.24 N·m | `MODELLED` |
| Brace section (CR-B1-18) | tape fairing, 10 × 2 unchanged (rounding: −8 % I) | `PROPOSED` |
| `T-C4-FIN-PROOF` on a test article (CR-H1-17) | 49 + 34 N, 77 N, 35 N at 1.5 × limit | `PROPOSED` |

## Requests raised

| Id | To | Short |
|---|---|---|
| CR-C4-30 | D5 | shoe cheeks down to \|z\| 0.171 m (+16 g `EST`) |
| CR-C4-29 | C1 | publish the G3 can force as a claim |
| CR-C4-31 | B1, D3 | tape fairing, no new brace section |
| CR-C4-32 | C6 | re-run joints on the R4 loads |
| CR-C4-33 | H1 | proof test article and loads |
| CR-C4-34 | A1, A3 | fins 18.4 g over |
| CR-C4-35 | D3 | SPEC to R4 claims |

## How to verify

Run `python -I redesign/team/C4/fin_structures_d3.py` (about 2 min), `python -I redesign/team/C4/fin_structures.py`,
then `python -I redesign/proofs/build_graph.py`. Hardware: `T-C4-FIN-PROOF`, `T-C4-MOUNT-STIFF`, `T-C4-TAP-D3`.
