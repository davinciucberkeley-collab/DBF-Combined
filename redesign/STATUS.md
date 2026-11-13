# Status — K09-L redesign, 2026-11-13

Honest state at frame revision A1-R6 (D-95…D-100, performance, mass and CG, 2026-11-13). Nothing is `VERIFIED`; no hardware exists. Status words follow
`design-system/README.md`: `UNVERIFIED` `PROPOSED` `MODELLED` `CHECKED` `VERIFIED`, `FAIL` for a negative margin.

## Phases

| Phase | State | What exists | What does not |
|---|---|---|---|
| Frame (A1–A5) | done, A1-R5 | `params.json`, 73 logged decisions, 59 requirements, interface graph (162 parts, 252 edges), Fusion framework, datums | Fusion backend never run in Fusion (`UNVERIFIED-IN-FUSION`) |
| Analysis (B, C1, E, F) | done | sizing, loads, S&C, props, power, energy, thermal, avionics, RC link, flight software; every number a claim | all inputs are catalogue or model values |
| Detail analysis (C2–C6) | done | wing, pod, fin, landing, joint sizing with hand + beam models | fin station not closed on the D-65 loads (collar, pins, strip anchor) |
| Design / CAD (D1–D7, E1, F1–F3) | done | 10 subsystem modules build in the stub backend; `check.py` propulsion 0 keep-out errors; parts.csv and interfaces.json for all nine flying subsystems | D5 sleeve fix (D-65) not yet in CAD; collar height pending |
| Integration (A3, A4) | done | A3-R7 roll-up 2 345 / 2 462 g, CG in range; A4-R5 interface plan | `merge_check.py` last recorded run had 1 error (CG in the old bay); not re-run after D2-R6 / A3-R7 |
| Simulation | done | 9 reports (B1–B4, C2–C5, E3): CFD, VLM, FEA, 6-DOF; fixes D-61 … D-73 | proof graph rebuilt clean 2026-11-11 after D-80…D-85 (0 drift, 0 errors; 2026-11-13 after D-95…D-100: 72 claims + 7 requirements fail on margin, each explained in `PROOFS.md`); collision check passes, strict: every wire, the tape skin, every wire end seated (`collision/README.md`, D-86) |
| Build and program planning | **drafted, `PROPOSED` (2026-11-13), nothing run** | H1 ground-test plan (18 cards, 96 claims), I1 BOM and order plan (R4: Maker Pass outside the budget), F4 param file + tuning + SITL plans, D7 box and field checklist, E2 charging and pack release, J1 references; **new:** G1 process plan + table (133/133 parts.csv lines classified), G2 composites/foam sheets, G3 print list (106 pieces, 51 h, 929 g), G4 build-step sheets, H2 flight-test plan, twin report and pilot log templates, H3 flight card, compliance, battery procedure, RFS wind method, I2 schedule (computed critical path), F5 range-test procedure | No claims or proof-graph nodes for the new plans (`R-PROCESS`, `R-SCHEDULE`, `R-TWIN`, `R-LEGAL`… still `UNVERIFIED (no claim)`); no filing done (FAA registration, UC flight requests, TRUST, AMA / insurance); hot-wire workspace, enclosed printer and Jacobs trainings not arranged; `R-BUILD-HOURS` fails on the guide's times (111 vs 90 h); pessimistic reserve $283.72 vs 309 |
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
| `R-MASS-GATE`, `R-PACK-MASS` | A3, E2 | `CL-A3-GATE-MARGIN-680` −66 % | stale: the 680 g pack case was retired by D-64; gate margin now +107 g vs 100 g (harness 119.8 g, D5-R6 landing 69.9 g); 590 g pack case −33 % | done: proof graph rebuilt on A3-R7 |
| `R-MASS-ALLOC` | A3 | `CL-D3-MASS` 434.8 vs 418 g | stale: allocation is 437 g (D-63); A3-R7 propulsion sits on its line (1.000) | graph rebuilt |
| `R-STATIC-MARGIN` | B3 | SM 4.76 % | real as designed, fixed by D-62 (range moved; A3-R7 CG 0.0486 m inside it) | B3 re-runs `sc_analysis.py` on the D-62 bay |
| `R-PROP-CLEAR` | D3 | 21.1 mm vs 25 | real, fixed by D-61 (E1 26.1 mm) | B4 re-runs `props.py` on the 7.5 mm mount |
| `R-LANDING-IMPACT` | C5 | stroke 38.6 mm, shoe SF 0.22 | real at 1.5 m/s, fixed by D-65 (1.2 m/s, sleeve) | C5 re-runs at 1.2 m/s on D5's R5 sleeve; D5 draws it |
| `R-STRUCT-MARGIN` | C2 | pocket-corner foam 203 / 199 kPa | real, fixed by D-68 (R 3 mm, beads) | C2 re-runs the FEA on the revised pocket |
| `R-PACK-RETENTION` | C3 | aft-stop peel 408 kPa vs 50 | real, fixed by D-69 (strut, flange, brackets, drawn in D2-R6); forward-stop flange not yet modelled; crash corner R 4.5 rests on a fillet | C3 re-runs on D2-R6; `T-C3-STOP-PUSH`, `T-C3-POD-PROOF` |
| `R-VIBRATION` | C4 | `CL-J1-TUBE-MODE-SEP` 0.017, `CL-C2-WING-MODE-SEP` 0.07 | stale (J1's superseded tube claim) and open (C2's wing torsion mode 11.9–14.4 Hz vs 1P: notch filter + tap test, D-45) | J1 retires its claim; `T-C2-TAP-TEST` |
| `R-WIND` | B1 | broadside landing 4 m/s vs 5 | real: C5's 6-DOF gives 4 m/s broadside; wingtip-into-wind rule proposed (CR-A2-32d) | A2 words the rule; H3 flight card |
| `R-DISCONNECT` | F1 | J1's XT60 claims | stale: AS150U adopted (D-32), every AS150U and wire claim passes | J1 retires the XT60 claims |

Thin margins that pass today (after D-95…D-98, 2026-11-13): stall +2.4 % at the worst CG corner against the D-96 line 12.3 m/s, with a planned 17 m/s fallback to 13.07 m/s; transition +0.05 % against the old `ARSPD_FBW_MIN` 15.6, now 2.6 % against the integer 16; 1.25 VH ≤ VD by 3.4 % (only with `THR_MAX` 70 %); hover pitch-trim split 1.21 vs 1.25; CG aft margin 0.8 mm for the 546 g pack (predicted, set by the bay travel); pack acceptance 560.8 g, +4.8 g over the SKU maximum; A1 free mass reserve 3 g; landing wind 5.4 vs 5.0 m/s; budget reserve $17 over the crash cost with both Jacobs loans.
1.25 VH ≤ VD by 3.4 % (only with `THR_MAX` 70 %); hover pitch-trim split 1.216 vs 1.25; CG aft margin 0.8 mm for the
551 g pack (predicted); gate margin for a 590 g pack −1.8 g (`FAIL`); landing wind 5.4 vs 5.0 m/s; budget: the pessimistic reserve is now $25.28 *under* the crash cost (R4, 2026-11-13).

## Open issues, by importance

> 2026-11-13, structures & mechanical (D-90 ... D-98, Dillon Alcouffe): rows 1, 8, 9 and the "also open" line updated; fins 433.3 -> 432.0 g (D-92 root fillets 15 -> 10 mm ahead of the hinge pay for the collar, pins and mount; a deeper cut fails the forward CG limit), landing -0.14 g, net -1.4 g.

| # | Issue | Numbers | Owner | Source |
|---|---|---|---|---|
| 1 | **Fin station re-solved on the D-65 loads (D-90, 2026-11-13); strip tail decided by coupon.** Collar 15 → 22 mm (`CL-C6-COLLAR-RF` 1.13 on C1's 12.67 N·m), pins 15 → 12 mm pitch (RF 1.12). Open: strip tail anchor RF 0.71 / tail net 0.64 on 2 233 N design and the 2 MPa / 15 MPa estimates; `T-C6-LAP-PETG` and `T-C6-STRIP-ANCHOR` run on the first prints, before flight collars are printed; contingency 62 mm solid tail (+29 g) | 2 233 N; RF 0.71 / 0.64 | C6, H1 | `params/CHANGE-LOG.md` D-90 |
| 2 | **Pessimistic reserve $278.77 vs the $309 crash line (short $30.23; with D-89a lines H07, H08).** Updated 2026-11-13: the Jacobs Maker Pass is paid outside the budget and covers the Electronics Lab soldering station and meters, so the soldering-kit lines are deleted; Jacobs lists no hot-wire cutter, so the hot-wire gear ($62.54) is bought. All-in pessimistic (every gated line) improves from −$57.82 to +$20.45, inside the $2 000. Levers not applied: ShopBot foam yes (+$62.54), USD pack price, Measure V date; AMA membership ($89 per pilot) is not in the BOM | $278.77 / $309; $1 721 spend | team, I1, A1 | `team/I1/ORDER-PLAN.md` R4, CR-I1-23, `team/H3/COMPLIANCE.md` |
| 3 | **Closed (D-95, 2026-11-13).** One acceptance line: **pack ≤ 560 g at `T-E2-WEIGH`** (`CL-A3-PACK-ACCEPT` = A1 = E2 = 560.8 g; A1 had subtracted 21.4 g of R5 parts that A3 already carries). The stale roll-up was re-run (+25.7 g basic: routed harness, D-87 bars). Allocations re-based on delivered masses: 2 374 g; reserve 226 g = growth 123 + overrun 100 + **3 g free**. Levers: phase-lead extensions −13.6 g (`T-E1-MOTOR-RM`), D3 fin levers −23 g | basic 2 366, predicted 2 489 / 2 600 g; gate margin 111 g | A1, A3, E2 | `MASS-CG.md`, CHANGE-LOG D-95 |
| 4 | **Closed by design (D-96); the test gate stays.** H9: `cg.z_range_m` [0.0165, 0.025]. P7 re-derived on the integer `AIRSPEED_MIN` 16: stall ≤ 12.3 m/s. Worst corner 12.01 m/s (+2.4 %, +4.9 % CLmax); +9.6 % CLmax at the predicted mass (estimate), which covers the 9 % B1/B2 spread. Planned fallback if `T-B2-STALL` reads > 12.31 m/s: `AIRSPEED_MIN` / `AIRSPEED_CRUISE` 17, which holds to 13.07 m/s (covers the 12.85 m/s tripped case) with about 5.2 min pessimistic cruise (estimate). `T-B2-STALL` is still the gate before `AIRSPEED_MIN` is frozen | 12.01 / 12.3 m/s | A1, B2, F4, H2 | CHANGE-LOG D-96 |
| 5 | **Closed (D-97).** Carry 253 W at 16 m/s (E1 246.2 + 6 W), L/D 5.66; 15 m/s rejected (below 1.3 Vs and `AIRSPEED_MIN`). E2: 11.4 min base / 6.0 min pessimistic at 253 W (P3: ≥ 5) | 253 W | A1, E1, E2 | CHANGE-LOG D-97 |
| 6 | **Proof graph: every remaining fail explained (D-100).** 90 → 72 claims + 7 requirements (0 drift). Fixed: 8 (stall ×2, cruise power, harness mass, servo BEC, J1 ×3). Pending an owner edit: `CL-F2-I2C-LEN`, after D-99 raised the rule to 1.0 m from the bus capacitance (134.6 pF ≤ 200 pF). The rest are explained in `PROOFS.md`: fin station 27 (STATUS #1), pod FEA not re-run on D2-R6 13, vibration (test + notch) 13, rejected options 4, D-68 FEA not re-run 2, landing rules 6, flight-software protected 2, transport box 3, test pass line 1, and the GT-17 rig uncertainty after D-97 raised the cruise rpm (`CL-H1-MSTIFF-U` 10.4 % vs 10 %) | 72 claims | C3, C4, C6, D3, D7, F2 | `PROOFS.md` |
| 7 | **Closed (D-98): one rule, A1's mid-band.** Each pack flies at the spacer step that centres its basic-to-predicted CG band; after `T-A3-CG-BALANCE` the measured CG decides. 546 g and 551 g sit on the most forward whole step (−0.036): aft margin +0.8 / +1.0 mm predicted, set by the bay. Fallback: D-59 nose ballast ≤ 10 g. CG height floor now 0.0165 (D-96); spiral unchanged (top of the range) | 0.8 mm | A3, H3 | `MASS-CG.md` |
| 8 | **Landing foot passes with margin (D-101); fin tip still decided by test.** D5-R8 shoe RF 1.27 at the 59.25 N ult side load (was 1.06; H1's 0.62 was a stale scaling, CR-H1-22 closed); `T-D5-SIDE` 60 N on two R8 shoes. `T-C4-FIN-PROOF` still decides C4's cheek extension. Pod brackets proof at limit 76.2 / 51.4 N, crash force on test articles (D-102, CR-H1-23 closed) | RF 1.27 | D5, H1 | D-101, D-102 |
| 9 | **Motor-mount stiffness fixed (D-91).** Grip 12 → 18 mm: estimate 2 235 vs need 1 455 N·m/rad (×1.54); GT-17 pass 1 455; station collar and ear 6 mm lower | 2 235 vs 1 455 N·m/rad | C4, H1 | D-91 |
| 10 | **Flight software never run.** `K09L.param` is not loaded on any board; SITL is not installed; the ≥ 10 h SITL de-risking item and the "stable tailsitter build" (`R-FC-STABLE` `PROPOSED`, paper only) are open; pilot not named | 0 h of 10 | F4, F3, H2 | `subsystems/flight-software/SPEC.md` |

Also open: pod recess-step fillet deletion in CAD (D-97, decided; WNG-007 and the floor bevel go, -1.1 g), ESC listing unconfirmed (LANRC 503;
fallback Tekko32 +$60), Ovonic USD price and 10 AWG leads unconfirmed, `CAR-FIT.md` waits for two cars, Remote ID
needed if flown outside the RFS FRIA, FAA registration ($5), station-mode separation in 3-D 0.155 vs 0.20 (D-93; tube pass lines E ≥ 69.7 GPa, G ≥ 4.01 GPa; `T-C4-TAP-D3`). Closed
2026-11-13: forward-stop flange FEA (D-96), C6 dog sizing (D-94), wing modes vs 1P by forced response (D-98),
station-mode separation in the shell model (D-93; the 3-D model reads 0.155 vs 0.20, still open).

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
