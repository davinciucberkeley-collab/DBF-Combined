# Status — K09-L redesign, 2026-11-10

Honest state at frame revision A1-R5. Nothing is `VERIFIED`; no hardware exists. Status words follow
`design-system/README.md`: `UNVERIFIED` `PROPOSED` `MODELLED` `CHECKED` `VERIFIED`, `FAIL` for a negative margin.

## Phases

| Phase | State | What exists | What does not |
|---|---|---|---|
| Frame (A1–A5) | done, A1-R5 | `params.json`, 73 logged decisions, 59 requirements, interface graph (162 parts, 252 edges), Fusion framework, datums | Fusion backend never run in Fusion (`UNVERIFIED-IN-FUSION`) |
| Analysis (B, C1, E, F) | done | sizing, loads, S&C, props, power, energy, thermal, avionics, RC link, flight software; every number a claim | all inputs are catalogue or model values |
| Detail analysis (C2–C6) | done | wing, pod, fin, landing, joint sizing with hand + beam models | fin station not closed on the D-65 loads (collar, pins, strip anchor) |
| Design / CAD (D1–D7, E1, F1–F3) | done | 10 subsystem modules build in the stub backend; `check.py` propulsion 0 keep-out errors; parts.csv and interfaces.json for all nine flying subsystems | D5 sleeve fix (D-65) not yet in CAD; collar height pending |
| Integration (A3, A4) | done | A3-R7 roll-up 2 345 / 2 462 g, CG in range; A4-R5 interface plan | `merge_check.py` last recorded run had 1 error (CG in the old bay); not re-run after D2-R6 / A3-R7 |
| Simulation | done | 9 reports (B1–B4, C2–C5, E3): CFD, VLM, FEA, 6-DOF; fixes D-61 … D-73 | owed re-runs on the R5 keys (below); proof graph not rebuilt since 20:10 UTC |
| Build and program planning | partial | H1 ground-test plan (18 cards, 96 claims), I1 BOM and order plan, F4 param file + tuning + SITL plans, D7 box and field checklist, E2 charging and pack release, J1 references | G1–G4 process plan, print list, build steps; H2 flight-test plan and twin report; H3 flight card, compliance, battery procedure; I2 January–April schedule; F5 range test |
| Media, renders, build manual (J3, J5) | not started | `blender/` and `manual-kit/` tooling with example output only | K09-L renders, animations, build manual (overview page `index.html` done in the final pass) |
| Design review board (J6) | not started | `reviews/TOOLING-REVIEW.md` | per-discipline critique and chair sign-off |
| Physical verification (H1, H2) | not started | test cards, pass lines, log-file names | every test |

## Requirements

From [`team/A2/VERIFICATION-MATRIX.md`](team/A2/VERIFICATION-MATRIX.md) (A2-R3, graph of 2026-11-10 20:10 UTC):
59 requirements · 0 `VERIFIED` · 1 `CHECKED` (`R-CONFIG`) · 1 `PROPOSED` (`R-FC-STABLE`) · 57 `UNVERIFIED` ·
11 `FAIL`. Fifteen have no claim yet (H2 / H3 demonstrations, G and I2 plans, `R-ENVELOPE`, `R-GUST-LEAN`,
`R-NO-FLOATING`, `R-PROOF-BUILD`, `R-SPIRAL`).

| Requirement | Owner | Worst claim | Stale or real | Clears when |
|---|---|---|---|---|
| `R-MASS-GATE`, `R-PACK-MASS` | A3, E2 | `CL-A3-GATE-MARGIN-680` −66 % | stale: the 680 g pack case was retired by D-64; A3-R7 gives +138 g | proof graph rebuilt on A3-R7 |
| `R-MASS-ALLOC` | A3 | `CL-D3-MASS` 434.8 vs 418 g | stale: allocation is 437 g (D-63); A3-R7 propulsion sits on its line (1.000) | graph rebuilt |
| `R-STATIC-MARGIN` | B3 | SM 4.76 % | real as designed, fixed by D-62 (range moved; A3-R7 CG 0.0486 m inside it) | B3 re-runs `sc_analysis.py` on the D-62 bay |
| `R-PROP-CLEAR` | D3 | 21.1 mm vs 25 | real, fixed by D-61 (E1 26.1 mm) | B4 re-runs `props.py` on the 7.5 mm mount |
| `R-LANDING-IMPACT` | C5 | stroke 38.6 mm, shoe SF 0.22 | real at 1.5 m/s, fixed by D-65 (1.2 m/s, sleeve) | C5 re-runs at 1.2 m/s on D5's R5 sleeve; D5 draws it |
| `R-STRUCT-MARGIN` | C2 | pocket-corner foam 203 / 199 kPa | real, fixed by D-68 (R 3 mm, beads) | C2 re-runs the FEA on the revised pocket |
| `R-PACK-RETENTION` | C3 | aft-stop peel 408 kPa vs 50 | real, fixed by D-69 (strut, flange, brackets, drawn in D2-R6); forward-stop flange not yet modelled; crash corner R 4.5 rests on a fillet | C3 re-runs on D2-R6; `T-C3-STOP-PUSH`, `T-C3-POD-PROOF` |
| `R-VIBRATION` | C4 | `CL-J1-TUBE-MODE-SEP` 0.017, `CL-C2-WING-MODE-SEP` 0.07 | stale (J1's superseded tube claim) and open (C2's wing torsion mode 11.9–14.4 Hz vs 1P: notch filter + tap test, D-45) | J1 retires its claim; `T-C2-TAP-TEST` |
| `R-WIND` | B1 | broadside landing 4 m/s vs 5 | real: C5's 6-DOF gives 4 m/s broadside; wingtip-into-wind rule proposed (CR-A2-32d) | A2 words the rule; H3 flight card |
| `R-DISCONNECT` | F1 | J1's XT60 claims | stale: AS150U adopted (D-32), every AS150U and wire claim passes | J1 retires the XT60 claims |

Thin margins that pass today: stall +0.05 % at the forward CG (B2); transition +0.05 % vs `ARSPD_FBW_MIN`;
1.25 VH ≤ VD by 3.4 % (only with `THR_MAX` 70 %); hover pitch-trim split 1.216 vs 1.25; CG aft margin 0.8 mm for the
551 g pack (predicted); gate margin for a 590 g pack −1.8 g (`FAIL`); landing wind 5.4 vs 5.0 m/s; budget reserve $17
over the crash cost with both Jacobs loans.

## Open issues, by importance

| # | Issue | Numbers | Owner | Source |
|---|---|---|---|---|
| 1 | **Fin station collar fails on C1's D-65 torsion.** C1's second D-65 run raised the half-fin section torsion ×1.71; the drawn 13–15 mm collar reads RF 0.67–0.77. C6 asks 22 mm (CR-C6-37, +4.4 g with 0 g free); C4 must re-solve the strip, pin and collar set on the new loads (CR-C6-38). Do not print collars or drill pins until settled | 12.67 N·m vs 7.4; RF 0.77; pins est. 0.93 | C4, C6, D3, A1 | `team/C6/SUMMARY.md`, `team/C6/CHANGE-REQUESTS.md` |
| 2 | **Budget holds only with two Jacobs Hall loans.** Reserve $326 (≥ $309) assumes the soldering kit and hot-wire gear are borrowed ($157 if refused); the loan request is drafted, **not sent** (due 13 Nov, written yes by 20 Nov). Everything-bought pessimistic fails by $356: box kit, airspeed sensor, spares and packs 3–4 stay gated | $326 / $309; $1 674 spend | team, H1, I1 | `team/I1/ORDER-PLAN.md`, CR-H1-26 |
| 3 | **Mass reserve 0 g free; pack acceptance line disputed.** 214 g reserve = growth 114 + overrun 100; a 590 g pack misses the overrun by 1.8 g. A3 carries 588.2 g, A1 592.6 g: one number for `T-E2-WEIGH`. Next levers: D3 fillet filler / block fill / cheeks (−23 g), harness return (−12 g) | 2 462 / 2 600 g | A1, A3, D3, E2 | `MASS-CG.md` |
| 4 | **Stall and transition margins are inside model uncertainty.** +0.05 % at the forward CG; fails by 0.1 % at the bottom of the z range (CR-B2-20: raise `cg.z_range_m[0]` to 0.0165 m); B1 and B2 differ 9 % on CLmax; SU2 clmax not converged. Gate: `T-B2-STALL` on the twin before `ARSPD_FBW_MIN` is frozen (D-71) | 11.99 / 12.0 m/s | A1, B1, B2, B3, H2 | `team/B2/SIMULATION-REPORT.md` |
| 5 | **Cruise power disputed.** E1's PER3 chain gives 246 W vs the carried 240 W; CR-E1-51 asks 252 W (or 15 m/s cruise) and L/D 5.66. E2's endurance (12.0 / 6.4 min) moves with it | 246 vs 240 W | A1, E1, E2, B1 | `team/E1/CHANGE-REQUESTS.md` |
| 6 | **Owed re-runs on the R5 keys; proof graph stale.** B3, B4, B1, E2, E3, C1, C2, C3, C4, C5, D5, D7, F4, H1, A5 (`check.py` 0 keep-outs), A2 texts; `build_graph.py` did not finish in the last two sessions. The matrix's 11 `FAIL`s are mostly this | 729 drifting outputs at R4; count unknown at R5 | each owner | `team/A1/SUMMARY.md`, CHANGE-LOG A1-R5 |
| 7 | **CG margin thin and two station rules.** The 551 g pack at its D-59 station has 0.8 mm aft margin predicted; A1's mid-band rule gives +2.0 / +1.3 mm. The flight card needs one rule. CG height also sets the forward limit (CR-B2-20) and the spiral (3.51 s ≥ 3.3 only with roll-stabilised modes, D-66) | 0.8 mm | A1, A3, H3 | `MASS-CG.md` |
| 8 | **Landing foot and fin tip decided by test.** D5's drawn rim scales to SF 0.62 at the 59 N ultimate side load (CR-H1-22); the sleeve fix (+5 g) is not yet in CAD; `T-C4-FIN-PROOF` decides C4's +16 g cheek extension (not allocated); 200 N crash pull on a flight pod questioned (CR-H1-23) | SF 0.62; 59 N | D5, C5, C4, C3, H1 | `team/H1/SUMMARY.md` |
| 9 | **Motor-mount stiffness expected to fail its test.** C4's estimate 1 500 N·m/rad is below its own need 1 966; GT-17 pass line is the larger (CR-H1-24) | 1 500 vs 1 966 N·m/rad | C4, D3, H1 | `team/H1/SUMMARY.md` |
| 10 | **Flight software never run.** `K09L.param` is not loaded on any board; SITL is not installed; the ≥ 10 h SITL de-risking item and the "stable tailsitter build" (`R-FC-STABLE` `PROPOSED`, paper only) are open; pilot not named | 0 h of 10 | F4, F3, H2 | `subsystems/flight-software/SPEC.md` |

Also open: forward-stop flange FEA (C3), pod crash corner fillet (CR-C3-17), ESC listing unconfirmed (LANRC 503;
fallback Tekko32 +$60), Ovonic USD price and 10 AWG leads unconfirmed, `CAR-FIT.md` waits for two cars, Remote ID
needed if flown outside the RFS FRIA, FAA registration ($5), wing torsion mode vs 1P (notch + tap test).

## Unverified in Fusion, unverified by test

| Item | State | Closes with |
|---|---|---|
| `fusion_backend.py` and every subsystem module in Fusion 360 | `UNVERIFIED-IN-FUSION`: built only in the stub backend | one BuildAll run by a teammate with a licence (`HANDOFF.md` L1) |
| Masses (every line is `EST`, `CALC`, `CAD` or `DATASHEET`) | 2 345 g basic, growth 116 g | `T-A3-WEIGH-PARTS`, `T-E2-WEIGH` (pack ≤ acceptance line), `T-A1-WEIGH` |
| CG and inertia | modelled | `T-A3-CG-BALANCE` (marks 0.0466 / 0.0514 m), `T-A3-SWING` |
| Thrust, current, sag | catalogue PER3 + hand sag | `T-E1-STAND` (one station, 11×4.5MR and 11×5.5MR), `T-B4-YAW` cant sense |
| Stall, transition, CLmax | VLM + XFOIL | `T-B2-STALL` on the twin, then the first build (gate, D-71) |
| Carbon tube E, G, bond allowables | `ASM-*` | `T-C4-TUBE-BEND` by 10 Dec, `T-C6-*` coupons with the first prints |
| Fin tip, collar, strip anchor, mount stiffness | FE | `T-C4-FIN-PROOF`, `T-C6-STRIP-ANCHOR` (≥ 2 660 N frame), `T-C4-MOUNT-STIFF` |
| Pod stops, bond, brackets | FE | `T-C3-STOP-PUSH`, `T-C3-POD-PROOF` |
| Foot stroke, side load, tip-over | 6-DOF | `T-C5-FOOT-RIG`, `T-C5-AIRCRAFT-DROP`, `T-C5-TILT-BOARD` |
| ESC, motor, pack temperatures | CFD + RC network | GT-04, `T-E3-ESC-PAD-CFD`, `T-E3-MOTOR-TAU` |
| Wire and connector heating | calc | `T-F1-WIRE-HEAT`, `T-F1-CONN-HEAT` |
| RC link, compass, arm/kill, failsafes | paper | `T-F5-RANGE`, `T-F3-COMPASSMOT`, GT-12, SITL |
| Wind at the flying site | RCMC1 station only | handheld anemometer at RFS vs RCMC1 (`R-WIND-MEASURE`) |
