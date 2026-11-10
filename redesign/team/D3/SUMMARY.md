# D3 Fins and motor tubes: summary

Revision D3-R4b, 2026-11-10 (params D-48 … D-55; C6-R4; C4 claims as published). Answers the A3 mass action
(CR-A3-26, merge_check WARN mass). Subsystem files: `redesign/subsystems/fins/` (SPEC, parts.csv, interfaces.json,
params.json, fusion/fins.py, BUILD.md). Re-run: `python -I redesign/subsystems/fins/make_fins.py` →
`python -I redesign/team/D3/fins_calcs.py` → `python -I redesign/fusion/check.py` →
`python -I redesign/interfaces/merge_check.py`.

## Mass action (CR-A3-26)

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Fins mass / allocation | 434.8 / 418 (was 436.4) | g | `CL-D3-MASS` | `FAIL` → CR-D3-33 |
| Root fillets, four half-fins (C6 15 mm, zoned) | 30.6 (was 32.2) | g | `CL-D3-FILLET-MASS` | `UNVERIFIED` |
| Half-fin laminate without fillets and laps (R3: 19.32) | 19.21 | g | `CL-D3-LAMINATE-MASS` | `UNVERIFIED` |
| Forward sealing bead 6 → 4 mm (no strength credit) | −1.6 | g | `fin_detail.fin.root_fillet.leg_fwd_m` | `PROPOSED` |
| Root fillet RF, D3 / at C6 allowable (unchanged) | 2.28 / 1.14 | — | `CL-D3-ROOT-FILLET-RF`, `-ALLOW` | `UNVERIFIED` |
| Block fill, shell estimate from CAD (drawn 0.55) | 0.51–0.56 | — | 19 400 mm² × 1.2–1.35 mm + 15 % gyroid | `MODELLED` |
| Asked allocation (covers CR-C6-31 +1.5 g, CR-C6-32 +0.6 g) | 437 | g | CR-D3-33 | `PROPOSED` |

**What grew.** The laminate did not: the D-54 stepped tip leaves it 0.1 g lighter than at R3. All the growth is C6's
15 mm root fillet, which D-48 booked at +3 g. Drawn as bodies, the fillets weigh 30.6 g. The fillet can't shrink:
the RF at the C6 allowable is 1.14 and scales with the leg. The face leg can't shorten either, because the paper
(0.10 MPa) is weaker than the XPS (0.125 MPa). A one-layer tip is out because the square tip already fails as drawn
(`CL-C4-D3-MS-FACE` −0.54). The block fill was re-derived from the CAD shell and 0.55 holds. Lowering it would mean
printing the block differently, so C4 has to re-check it first.

**Decision asked of A1 (CR-D3-33).** Raise fins from 418 to 437 g. That is +19 g from the reserve; A3 says 31 g is free, so
12 g would remain. D3 gives back to the reserve whatever these levers deliver:

| Lever | Saves | Gate | Owner |
|---|---|---|---|
| Microlight fillet filler ≤ 0.45 g/cm³ | −5.6 g `EST` | T-D3-WEIGH cup | D3 (C6 adhesive spec) |
| Block 2 perimeters + 10 % gyroid (fill 0.45) | −13.8 g `EST` | `CL-C4-D3-BLOCK-MS` ≥ 0 | C4 |
| Mount cheeks 12 → 8 mm | −4 g `EST` | rocking stiffness ≥ 926 N·m/rad | C4 |

## Checks

| Check | Result | Status |
|---|---|---|
| `fins_calcs.py` | all claims written; `CL-D3-MASS` fails its limit (434.8 > 418) | `MODELLED` |
| `check.py` | fins module ok (42 parts, 435 g); 8 KO-PROP errors (tube 9.5 mm, boss 5.8, plug 8.4 mm into the convex hull) pre-date this change (CR-D3-26, A1 decision); WARN mass | `FAIL` (not from this change) |
| `merge_check.py` | PASS, 0 errors; WARN fins 435 > 418 g until A1 rules on CR-D3-33 | `CHECKED` |

## Open

1. A1: CR-D3-33 (allocation) and CR-D3-26 (prop keep-out). The keep-out errors are not part of this mass action.
2. D3 next run: adopt CR-C6-31 (pins Ø 2.5) and CR-C6-32 (collar 13 mm). Both are structural fixes, and their
   +2.1 g is inside the 437 g asked for.
3. C6: the skin bond area is now 4 934 / 4 790 mm² (bead only, no change to the RF basis). `make_fins.py` writes
   this into `E-FIN-53…56`.
