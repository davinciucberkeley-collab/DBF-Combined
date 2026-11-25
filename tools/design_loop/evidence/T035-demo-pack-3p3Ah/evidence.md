# Design loop evidence: pack-3p3Ah

Adapter `concept_a`, started 20261123-141617, wall 8.7 s. Category labels per CLAUDE.md (interference, kinematics, rigid-body dynamics, FEA, CFD, flight dynamics, illustrative).

## Change applied (to a copy; the committed design is untouched)

| change | old | new | unit | note |
|---|---|---|---|---|
| pack_capacity_ah | 2.8 | 3.3 | Ah | pack mass 270.0 -> 318.21 g (linear in Ah, EST); PWR-001, mass.pack_g and the itemised pack row updated; BOM price and pack size NOT updated |
| mass roll-up | 1640.98 | 1689.19 | g | CG x 22.000 -> 20.575 mm (lateral CG not updated); deltas added to mass.basic_cad_kg, mass.cg_x_mm |

Committed files unchanged after the run: **True** (sha256 prefix check of 7 files).
Baseline reproduces the committed claims graph: **True** (0 differing claim values).

## Steps

| phase | step | exit | wall s |
|---|---|---|---|
| baseline | gen_params_a | 0 | 0.24 |
| baseline | merge_check | 1 | 0.38 |
| baseline | claims_a0_base | 0 | 0.22 |
| baseline | claims_a1_flight | 0 | 0.53 |
| baseline | claims_a2_struct | 0 | 0.17 |
| baseline | claims_a3_program | 0 | 0.16 |
| baseline | build_graph --strict | 1 | 1.11 |
| variant | gen_params_a | 0 | 0.15 |
| variant | merge_check | 1 | 0.23 |
| variant | claims_a0_base | 0 | 0.16 |
| variant | claims_a1_flight | 0 | 0.4 |
| variant | claims_a2_struct | 0 | 0.16 |
| variant | claims_a3_program | 0 | 0.14 |
| variant | build_graph --strict | 1 | 0.99 |

(`build_graph --strict` exits 1 when any claim fails: that is a result, not a crash.)

## Headline metrics

| metric | category | limit | baseline |  | variant |  |
|---|---|---|---|---|---|---|
| MC-MASS-TOTAL | rigid-body (static mass properties, algebra) | <= 1500 | 1641.0 g | FAIL | 1689.2 g | FAIL |
| MC-CG-X | rigid-body (static mass properties, algebra) | 4.0 .. 28.5 | 22 mm | PASS | 20.57 mm | PASS |
| CL-A-MASS-PRED | rigid-body (static mass properties, algebra) | <= 1.47 | 1.881 kg | FAIL | 1.935 kg | FAIL |
| CL-A-CG | rigid-body (static mass properties, algebra) | >= 19.0 | 22.05 mm | PASS | 20.63 mm | PASS |
| CL-A-CG-HI | rigid-body (static mass properties, algebra) | <= 26.0 | 22.05 mm | PASS | 20.63 mm | PASS |
| CL-A-SM | flight dynamics (algebraic, EST inputs) | >= 5.0 | 7.613 % chord | PASS | 8.194 % chord | PASS |
| CL-A-TW-FRESH-PRED | flight dynamics (algebraic, EST inputs) | >= 2.0 | 2.713 - | PASS | 2.637 - | PASS |
| CL-A-TW-SAG-PRED | flight dynamics (algebraic, EST inputs) | >= 1.6 | 2.152 - | PASS | 2.092 - | PASS |
| CL-A-WINDOW-PRED | flight dynamics (algebraic, EST inputs) | >= 5.0 | 12.84 % | PASS | 11.45 % | PASS |
| CL-A-MOTOR-I | flight dynamics (algebraic, EST inputs) | <= 26.8 | 20.08 A | PASS | 20.08 A | PASS |
| CL-A-ESC-I | flight dynamics (algebraic, EST inputs) | <= 35.0 | 25.1 A | PASS | 25.1 A | PASS |
| CL-A-CRUISE-NEED | flight dynamics (algebraic, EST inputs) | <= 210.0 | 204.6 s | PASS | 204.6 s | PASS |
| CL-A-CRUISE-AVAIL | flight dynamics (algebraic, EST inputs) | >= 204.55636934924914 | 233.8 s | PASS | 313.9 s | PASS |
| CL-A-COST-TOTAL | illustrative (budget arithmetic) | <= 2000.0 | 1939.2 USD | PASS | 1939.2 USD | PASS |

## Interpretation

- REGRESSION: CL-A-MASS-ITEM PASS -> FAIL (1.447 kg -> 1.496 kg, limit <= 1.47) [rigid-body (static mass properties, algebra)]
- Margin CL-A-CUTS-REQUIRED: -8.83 -> -9.99 (409.1 g -> 457.3 g) [rigid-body (static mass properties, algebra)]
- Margin CL-A-CRUISE-AVAIL: 0.143 -> 0.535 (233.8 s -> 313.9 s) [flight dynamics (algebraic, EST inputs)]
- Margin CL-A-WINDOW-PRED: 1.57 -> 1.29 (12.84 % -> 11.45 %) [flight dynamics (algebraic, EST inputs)]
- Margin CL-A-SM: 0.523 -> 0.639 (7.613 % chord -> 8.194 % chord) [flight dynamics (algebraic, EST inputs)]
- Margin CL-A-CG-TRIM-FWD: 0.109 -> 0.026 (21.06 mm -> 19.49 mm) [rigid-body (static mass properties, algebra)]
- Failing metrics: 14 baseline -> 15 variant (of 100 judged).
- All claim values inherit the EST / UNVERIFIED status of their inputs (see params-A.json); a PASS here is a re-computation, not a flight or bench result. Stored FEA / SITL / gate results are read, not re-run.

## All changed metrics (16)

| id | category | limit | before | after | verdict |
|---|---|---|---|---|---|
| CL-A-CG | rigid-body (static mass properties, algebra) | >= 19.0 | 22.05 mm | 20.63 mm | PASS -> PASS |
| CL-A-CG-HI | rigid-body (static mass properties, algebra) | <= 26.0 | 22.05 mm | 20.63 mm | PASS -> PASS |
| CL-A-CG-TRIM-AFT | rigid-body (static mass properties, algebra) | <= 28.5 | 23.69 mm | 22.51 mm | PASS -> PASS |
| CL-A-CG-TRIM-FWD | rigid-body (static mass properties, algebra) | >= 19.0 | 21.06 mm | 19.49 mm | PASS -> PASS |
| CL-A-CRUISE-AVAIL | flight dynamics (algebraic, EST inputs) | >= 204.55636934924914 | 233.8 s | 313.9 s | PASS -> PASS |
| CL-A-CUTS-REQUIRED | rigid-body (static mass properties, algebra) | <= 41.6 | 409.1 g | 457.3 g | FAIL -> FAIL |
| CL-A-MASS-GATE-ROOM | rigid-body (static mass properties, algebra) | <= 1.47 | 1.881 kg | 1.935 kg | FAIL -> FAIL |
| CL-A-MASS-ITEM | rigid-body (static mass properties, algebra) | <= 1.47 | 1.447 kg | 1.496 kg | PASS -> FAIL |
| CL-A-MASS-PRED | rigid-body (static mass properties, algebra) | <= 1.47 | 1.881 kg | 1.935 kg | FAIL -> FAIL |
| CL-A-MASS-USER | rigid-body (static mass properties, algebra) | <= 25.0 | 1.881 kg | 1.935 kg | PASS -> PASS |
| CL-A-SM | flight dynamics (algebraic, EST inputs) | >= 5.0 | 7.613 % chord | 8.194 % chord | PASS -> PASS |
| CL-A-TW-FRESH-PRED | flight dynamics (algebraic, EST inputs) | >= 2.0 | 2.713 - | 2.637 - | PASS -> PASS |
| CL-A-TW-SAG-PRED | flight dynamics (algebraic, EST inputs) | >= 1.6 | 2.152 - | 2.092 - | PASS -> PASS |
| CL-A-WINDOW-PRED | flight dynamics (algebraic, EST inputs) | >= 5.0 | 12.84 % | 11.45 % | PASS -> PASS |
| MC-CG-X | rigid-body (static mass properties, algebra) | 4.0 .. 28.5 | 22 mm | 20.57 mm | PASS -> PASS |
| MC-MASS-TOTAL | rigid-body (static mass properties, algebra) | <= 1500 | 1641.0 g | 1689.2 g | FAIL -> FAIL |

## Reproduce

```
python -I tools/design_loop/cli.py run --set pack_capacity_ah=3.3 --name pack-3p3Ah
```
