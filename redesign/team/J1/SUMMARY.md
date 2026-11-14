# J1 outside research — K09-L comparables, failure modes, references

Status: `PROPOSED` (J1, 2026-11-09, second pass at revision A1-R2). Re-check: `python -I redesign/team/J1/research_claims.py`
then `python -I redesign/proofs/build_graph.py` (result: 0 J1 drift, 0 J1 errors; 3 J1 claims `FAIL` by design;
the build still fails on A5, B1, B2, B3 and C1 drift, which their owners re-run). CR-A1-16 / CR-A2-06 closed:
`CL-J1-TUBE-MODE-SEP` verifies `R-VIBRATION`, `CL-J1-FIN-YAW-ARM` verifies `R-DIRECTIONAL`.

## What was produced

| File | What | Status |
|---|---|---|
| `team/J1/REFERENCES.md` | comparables (9 aircraft), 12 failure modes with owner and design measure, cited reading list per role A–I | `PROPOSED` |
| `team/J1/research_claims.py` → `claims.json` | 20 claims, 7 calcs, 5 assumptions (2 superseded, kept for C1), 32 sources, 3 planned tests | 17 `PROPOSED`/`UNVERIFIED`, 3 `FAIL` |
| `team/J1/CHANGE-REQUESTS.md` | 12 requests: 6 closed by CHANGE-LOG, 6 open (B3, C4, F1, F4, I1, C1) | open |

## What changed at A1-R2 (and why the numbers moved)

| Input | R0 → R2 | Effect on J1 claims |
|---|---|---|
| Motor tubes at x −0.10 → **+0.045 m** through the core (D-04) | fin LE on the tube | fin centroid arm 0.04 → **0.14 m**; fin area ahead of CG 40 % → **0 %**; prop arm 0.21 → **0.05 m** |
| Prop 11×4.5MR → **11×5.5MR** (D-05); rpm from B4 claims, not my kT fit | hover 5 396, cruise 6 000, cap 9 350 rpm | 1P/2P hover 90 / 180 Hz, cruise 100 / 200 Hz, max 156 / 312 Hz |
| Airfoil MH 45 → **S5010** (D-02); cm0 from `P:b2.xfoil.cm0_2d_re2.3e5` | +0.0145 → −0.004 | elevons-neutral trimmable SM 2.7 % → **−0.9 %**; limit dropped (D-19 rejected CR-J1-02) |
| Cruise 15 → 16 m/s, S 0.345 → 0.368 m², hover 24 → 27 A | — | CL cruise 0.54 → **0.44**; disconnect 30 → **33.75 A** (37.4 A on E2's 29.9 A) |
| Separation limit `ASM-J1-SEP-RULE` → **`P:requirements.vibration_sep_frac`** (A2, D-14) | 0.20 | one source for the limit; assumption retired |

## Key numbers from the chain

| Claim | Value | Limit | Margin | Status | Verifies | Owner |
|---|---|---|---|---|---|---|
| `CL-J1-FIN-YAW-ARM` fin centroid aft of CG | 0.14 m (43 % c) | ≥ 0 | large | `UNVERIFIED` (CG target D-17) | `R-DIRECTIONAL` | B3 |
| `CL-J1-FIN-AREA-AHEAD` fin area ahead of CG | 0 % (1.5 % at the aft CG limit) | — | — | `UNVERIFIED` | — | B3 |
| `CL-J1-PROP-ARM` prop planes ahead of CG | 0.05 m (15 % c) | — | — | `UNVERIFIED` | — | B3 |
| `CL-J1-TUBE-F1` bare tube first mode | 183 Hz (E 100 GPa `UNVERIFIED`; 130–215 Hz for 50–140 GPa) | — | — | `UNVERIFIED` | — | C4 |
| `CL-J1-MOTOR-1P/2P-HOVER` · `-CRUISE` · `-MAX` | 90 / 180 · 100 / 200 · 156 / 312 Hz | — | — | `UNVERIFIED` (B4 rpm) | — | E1, H1 |
| `CL-J1-TUBE-MODE-SEP` | 1.7 % from hover 2P | ≥ 20 % | −91 % | `FAIL` | `R-VIBRATION` | C4, H1 |
| `CL-J1-CL-CRUISE` at 2.6 kg, 16 m/s | 0.44 | — | — | `UNVERIFIED` | — | B1 |
| `CL-J1-SM-TRIMMABLE` S5010, elevons neutral | −0.9 % | none (D-19) | — | `UNVERIFIED` | — | B2, B3 |
| `CL-J1-DISCONNECT-REQ` / `-PESS` 1.25 × 27.0 / 29.9 A | 33.75 / 37.4 A | — | — | `UNVERIFIED` | `R-DISCONNECT` | F1 |
| `CL-J1-XT60-CONT` / `-CONT-PESS` / `-BURST` | 35 / 35 / 60 A | ≥ 33.75 / 37.4 / 120 A | +4 % / −6 % / −50 % | `PROPOSED` / `FAIL` / `FAIL` | `R-DISCONNECT` | F1 |
| `CL-J1-AS150U-CONT` / `-BURST` | 70 / 140 A (reseller) | ≥ 37.4 / 120 A | +87 % / +17 % | `PROPOSED` | `R-DISCONNECT` | F1 |

## Risks the team must design out (detail: REFERENCES.md §2)

1. **Tube resonance.** The forcing sweeps 90–156 Hz (1P) and 180–312 Hz (2P) between hover and the capped maximum; with a 20 % margin no bare-tube mode in 72–374 Hz clears every steady point, and the bare tube sits at ~183 Hz, 2 % from the hover 2P. C4: the half-fin bond must put the first mode above ~375 Hz or the tap test must show it damped (`R-VIBRATION` allows either); H1: tap test and tube bend test.
2. **FW yaw.** Geometry is now sound (fin centroid 0.14 m aft, no area ahead of the CG, props only 0.05 m ahead; B3's O4b Cn_β +0.044 /rad), but Plane has no FW yaw stabilisation by default and all four student Box Kites yawed in FBWA. F4 still owes the FW yaw actuator (CR-J1-05); B3 re-runs Cn_β at R1 against `cnbeta_min` 0.03.
3. **Disconnect.** XT60 passes 1.25 × 27 A by 4 % on the Amass figure only; it fails Holybro's 30 A, E2's 29.9 A hover (−6 %) and the 120 A momentary case (−50 %). F1: AS150U, or a cited short-time XT60 rating for the ≤ 5 s / 100 A-limited case (A1's condition).
4. **Trim is all elevon.** The S5010's cm0 ≈ 0 means the 5 % static margin is carried entirely by elevon up-trim (B2 ≈ −4° at CL 0.5); the penalty is inside the trimmed CLmax 0.80, so this is accepted (D-19), but the elevon trim position in FBWA is the flight check (`elevon_trim_travel_max`).
5. **No in-class precedent** for a logged elevon quad-tailsitter round trip (EVIDENCE §0 reconfirmed); the twin, the FW-first tune and the airspeed sensor remain the three conditions.

## Open issues

1. `team/C1/claims.json` still names `ASM-J1-APC-KT` and `ASM-J1-MH45-CM0` (its `loads.py` already moved on); I keep both as superseded nodes until C1 re-runs (CR-J1-10).
2. FAA recreational page and the SunnySky page refused the fetch (403 / 429): H3 and E1 confirm from the live pages.
3. AS150U has no maker datasheet found; its 70 A is a reseller figure with one forum melt report.
4. FOAMULAR NGX 250 density not read from the sheet (binary PDF); C578 Type IV minimum 1.55 pcf used.
5. No tailsitter foot or tip-over data exists in public; C5's drop test is the only evidence path.
6. `proofs/out/*` regenerated by `build_graph.py` (J2's folder; expected, as A1 noted).
