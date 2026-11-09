# Open design decisions

The four source repositories did not agree on the design, and this consolidation **did not pick a side**. Each entry
below gives every value found, the file where it lives, and the decision the team has to make. Record the outcome
in the entry (date, who, what) and then re-run whatever is built on the losing value.

Entries marked **SAFETY** affect flight safety and should be settled before any powered test.

Values checked against the files in this repository on 2026-11-08.

## Which artifacts are built on which baseline

Three design states sit side by side in this repo. Most conflicts below come from this.

| Baseline | Key numbers | Artifacts built on it |
|---|---|---|
| **v0.4.0, 11-02 resize, CAD rev G** (DillonVTOL, 2026-11-03) | Vc 18 m/s, MTOW 7.438 kg, S 0.774 m², chord 322.3 mm, AR 7.45, hover 1132 W / 51.0 A, T/W 1.68, $1,854.55 committed | `analysis/` (incl. `results.json`, `aero/`, `cfd3d/`, `validation/`, `mass/`), `cad/`, `firmware/`, `docs/DESIGN-BASIS.md`, `docs/purchasing/C0_BOM.csv`, `docs/build/`, `docs/test/`, `review/`, the root pages `VTOL-Review.html` (issue 6), `build-manual.html`, `test-plan.html`, `flight-software.html`, `templates.html` |
| **v0.4.0 rev D** (DBF-VTOL `analysis/` as of 2026-10-25) | Vc 20 m/s, MTOW 6.552 kg, chord 284.2 mm | `Concept-Models.html` only (A0 is placed with chord 0.284176 and 6.55 kg; `concepts/build.mjs` reads the root `cad/params.txt` and `analysis/results.json`, so a rebuild moves it to rev G) |
| **v0.3.1** (2026-10-18/19) | Vc 20 m/s, MTOW 6.182 kg, S 0.573 m², chord 238.7 mm, AR 10.06, hover 832 W / 37.5 A, T/W 2.03, $1,897.92 committed | `inventory/` (the builders read the frozen copy in `inventory/v031/`), `Inventory-Overview.html`, the live Google Sheet, `fusion/` and `inventory/fusion/` (Fusion model), `concepts/variants/a1–a3`, `docs/research/electrical-architecture.md`, `hardware-schedule.md`, `tolerance-analysis.md`, `nautical-wings-props.md` |
| Not the C0 design | — | `explorations/tiltwing/` (tilt-wing, 9.5 kg paper defaults), `sim/` (notional 8-lift, 2,200 kg, 13 m span), `tools/opencae-studio/` (general CAE tool; its wing tutorial uses an S1223 half-wing) |

Sources: `analysis/results.json` and `inventory/v031/analysis/results.json` (`base.Vc`, `concepts.C0.sized.*`,
`concepts.C0.bom.total`).

**Citation drift.** Documents from DBF-VTOL cite root paths (`analysis/results.json`, `docs/DESIGN-BASIS.md`,
`docs/purchasing/C0_BOM.csv`) but quote the v0.3.1 values. In this repo those root paths hold the 11-02 values; the
v0.3.1 values are in `inventory/v031/`. Read any v0.3.1 citation against `inventory/v031/`.

---

## D1. Design baseline for the whole team

- **Values:** the three states in the table above.
- **Decision needed:** adopt the 11-02 resize as the single team baseline (then migrate `inventory/`, `fusion/`,
  `concepts/variants/`, the Google Sheet and the four DBF research notes), or reopen it. D2–D12 follow from this.
- **Status:** open.

## D2. Cruise speed: 18 or 20 m/s

| Value | Where |
|---|---|
| 18 m/s | `analysis/results.json` `base.Vc`; `firmware/vtol_c0.param` line 115 `AIRSPEED_CRUISE,18`; trade in `analysis/cruise_speed_trade.mjs` / `.json` (−22 % cruise power vs 20) |
| 20 m/s | `inventory/v031/analysis/results.json` `base.Vc`; `concepts/variants/a1/design.md` (drag at 20 m/s); `docs/research/nautical-wings-props.md` line 29 (pusher design point) |

Both sit inside requirement R11 (cruise 18–22 m/s, `docs/DESIGN-BASIS.md`). Changes RTL distances, endurance and the
parameter file. **Decision needed:** confirm 18 m/s or revert to 20 m/s.

## D3. MTOW, wing area and chord (and R2 sign-off)

| | 11-02 resize | rev D | v0.3.1 |
|---|---|---|---|
| MTOW `sized.m` | 7.438 kg | 6.552 kg | 6.182 kg |
| Wing area `sized.S` | 0.774 m² | 0.682 m² | 0.573 m² |
| Chord `sized.chord` | 322.3 mm | 284.2 mm | 238.7 mm |
| Aspect ratio | 7.45 | 8.45 | 10.06 |
| Pod length `cad/params.txt fusL` | 1.000 m | 0.850 m | 0.850 m |
| Joiner reserve factor at 4.5 g | 1.41 | 1.75 | 1.85 |

Where: `analysis/results.json`, `cad/params.txt` (11-02); `Concept-Models.html` (rev D); `inventory/v031/analysis/results.json`,
`inventory/v031/cad/params.txt` (v0.3.1). Span 2.4 m and NACA 2415 agree everywhere.
R2 sets an 8–15 kg working target; every version is below it, and the team has not signed that off
(`docs/DESIGN-BASIS.md` R2). **Decision needed:** accept the 11-02 sizing (follows D1, D2, D4) and sign off R2.

## D4. Payload and ballast (R12)

| Value | Where |
|---|---|
| No payload, no ballast; nose lengthened 0.15 m so the CG reaches 28 % MAC without ballast (revised 2026-11-01) | `docs/DESIGN-BASIS.md` R12 (line 30) and decision 6 (line 74); `docs/build/BUILD-MANUAL.md` revision note |
| 0.5 kg reserve for a future camera or sensor | `inventory/v031/docs/DESIGN-BASIS.md` R12 (line 27) |
| Fly with 0.5 kg ballast when there is no payload | DBF-VTOL rev D `docs/DESIGN-BASIS.md` (superseded, not in this repo; see DBF-VTOL `9cc31fe`) |

**Decision needed:** confirm "no payload, no ballast" or restore a payload/ballast allowance (it changes MTOW, CG and
the pod length).

## D5. Battery disconnect plug (R20): XT90S or Amass AS150U — **SAFETY**

| Value | Where |
|---|---|
| Amass AS150U, 70 A continuous / 140 A for 1 min (Amass datasheet); states the XT90-S is 40 A continuous, below the hover current | `docs/DESIGN-BASIS.md` R20 (line 38); `docs/purchasing/C0_BOM.csv` line 2; `docs/research/propulsion-margin-data.md` (connector table, lines 135–140) |
| XT90S anti-spark plug as the physical disconnect (CN01) | `inventory/v031/docs/DESIGN-BASIS.md` R20; `inventory/inventory.csv` P-04 (hardware kit); `inventory/electrical/components.json` (`XT90S_1`); `docs/research/electrical-architecture.md` lines 6, 66, 69, 81; `docs/research/hardware-schedule.md` line 50 |
| XT90S rated 50 A continuous / 90 A peak (makerstore) vs 90 A continuous (esk8 wiki) | `docs/research/electrical-architecture.md` line 41 (risk R-D) |

Currents it must carry: hover 51.0 A (53.9 A loaded) and transition 82.1 A on the 11-02 sizing
(`analysis/results.json` `sized.I_hover`, `I_hover_loaded`, `I_trans`); 37.5 A hover and 74.4 A transition on v0.3.1
(`inventory/v031/analysis/results.json`). On every rating quoted for the XT90S except the 90 A forum figure, the
transition current exceeds its continuous rating. **Decision needed:** pick the plug, buy matching battery leads
(the Ovonic packs come with EC5 leads that both BOMs re-terminate), and update the electrical architecture, inventory
and wiring blueprint to match.

## D6. Lift ESCs: LANRC or SoloGood

| Value | Where |
|---|---|
| LANRC BLHeli_S 45A 4-pack × 2, $30.00 each | `docs/purchasing/C0_BOM.csv` line 35; `docs/research/bom-savings.md` |
| SoloGood 45A 4-pack × 2, $39.99 each ("fallback LANRC 35A") | `inventory/v031/docs/purchasing/C0_BOM.csv` line 16; `inventory/inventory.csv` P-15 |

**Decision needed:** which ESC to buy; check DShot/BLHeli support against `docs/research/electrical-architecture.md` risk R-A.

## D7. Airspeed sensor: RMRC MS4525DO or Holybro MS5525DSO

| Value | Where |
|---|---|
| RMRC MS4525DO + pitot, $59.99; `ARSPD_TYPE,1`, I2C 0x28 ("no clash with the board baro at 0x76") | `docs/purchasing/C0_BOM.csv` line 9; `firmware/vtol_c0.param` line 109 |
| Holybro MS5525DSO + PT40, $59.99, ships from China; "MS5525 airspeed at 0x76" | `inventory/v031/docs/purchasing/C0_BOM.csv` line 28; `docs/research/electrical-architecture.md` line 35 |

The parameter file comment puts the board barometer at 0x76, the address the electrical note gives the MS5525.
**Decision needed:** pick the sensor; keep `ARSPD_TYPE` and the I2C wiring consistent with it.

## D8. GPS: RMRC SAM-M10Q-5883 or HGLRC M100-5883

| Value | Where |
|---|---|
| RMRC SAM-M10Q-5883, $24.99 | `docs/purchasing/C0_BOM.csv` line 5; `firmware/vtol_c0.param` line 200 comment |
| HGLRC M100-5883, $20.49 | `inventory/v031/docs/purchasing/C0_BOM.csv` line 34 |

**Decision needed:** pick one; it changes the vendor orders (ReadyMadeRC consolidation in `docs/research/bom-savings.md`).

## D9. Spare X4110S motor

| Value | Where |
|---|---|
| No spare motor (removed, held as reserve cash) | `docs/purchasing/C0_BOM.csv` (no "Spares" motor line) |
| One spare X4110S, $46.99 | `inventory/v031/docs/purchasing/C0_BOM.csv` line 41 |

C0 has no hover motor-out tolerance, so a failed lift motor grounds the aircraft until a replacement arrives.
**Decision needed:** buy the spare or keep the cash.

## D10. Committed spend and reserve

| Value | Where |
|---|---|
| $1,854.55 committed, $145.45 reserve (goods $1,598.69, tax $163.87, shipping $91.99) | `analysis/results.json` `concepts.C0.bom`; `docs/purchasing/C0_BOM.csv` lines 53–57 |
| $1,897.92 committed, $102.08 reserve (goods $1,630.77, shipping $100) | `inventory/v031/analysis/results.json`; `inventory/v031/docs/purchasing/C0_BOM.csv` lines 43–47; `inventory/inventory.json`, `Inventory-Overview.html`, the Google Sheet |

Follows D5–D9. **Decision needed:** after D5–D9, regenerate one BOM and feed it to `inventory/` and the Google Sheet.

## D11. Thermal design ambient (R21)

| Value | Where |
|---|---|
| R21: no full mission or transition flight above 25 °C measured at the field (added 2026-11-02; thermal re-run at 25 °C) | `docs/DESIGN-BASIS.md` lines 6, 39, 47, 66; `cad/sim/thermal/results.txt` |
| 35 °C "hot day" estimate, no requirement | DBF-VTOL rev D thermal analysis (superseded); no R21 in `inventory/v031/docs/DESIGN-BASIS.md` |

**Decision needed:** accept the 25 °C flight restriction (an operating limit for April flights) or design for a hotter day.

## D12. Nautical Wings prop spec sheet (before it is sent)

| Value | Where |
|---|---|
| Lift design point 6.18 kg / 4 = 1.545 kg per rotor; pusher at 20 m/s | `docs/research/nautical-wings-props.md` line 29 (v0.3.1; it cites `../DESIGN-BASIS.md`, which here says 7.438 kg) |
| On the 11-02 sizing: 7.438 kg / 4 ≈ 1.86 kg per rotor, pusher at 18 m/s | arithmetic from `analysis/results.json` |

**Decision needed:** update the design point (after D1–D3) before the spec goes to the sponsor. The message itself is
in `inventory/build_overview.mjs` (`NWA_MSG`) and on `Inventory-Overview.html` §8.

## D13. Which CAD model is the build reference

- SOLIDWORKS model, rev G, 11-02 sizing: `cad/` (drives the review, drawings DBF-DRW-001 and the build manual).
- Autodesk Fusion model, v0.3.1 geometry, with the full hardware schedule, joints and motion clearance: `fusion/`, `inventory/fusion/`, `inventory/hardware/`.
- **Decision needed:** confirm SOLIDWORKS rev G as the build reference and whether the Fusion model is migrated or frozen.
  Findings from the Fusion work that already crossed over are tracked in `docs/research/team-crosscheck.md`.

## D14. Tilt-wing status

`explorations/tiltwing/` is marked as an archived exploration (S1223 wing, 2.0 m span, 9.5 kg paper defaults). The
trade study (`analysis/tradestudy.json`) ranks C0 first. **Decision needed:** confirm it is archived, not a competing
configuration.

## D15. Canonical published links and old repositories

- GitHub Pages: DillonVTOL published at `davinciucberkeley-collab.github.io/DillonVTOL`. This repo has `index.html`
  and `.nojekyll` and can be published the same way.
- claude.ai artifacts: listed in the README under "Published versions"; several are on v0.3.1.
- **Decision needed:** which Pages URL is canonical, and whether DBF-VTOL, DillonVTOL and TiltWing are archived
  (read-only) once DBF-Combined is pushed.

---

## Self-inconsistencies inside documents

These are not team decisions, just places where one document disagrees with itself or with its neighbours.

1. **Drawing revision F vs G.** `cad/README.md` line 28 says "the title block reads rev F, 2026-11-03", while
   `cad/Drawings.cs` line 49 sets `REV = "G", DATE = "2026-11-03"`, `cad/README.md` line 46 is headed "Drawing set
   DBF-DRW-001 rev G" and `README.md` says rev G. The committed PDF was not re-read for this check.
2. **Static margin.** `README.md` quotes AVL (neutral point 38.4 % MAC, static margin 10.4 %,
   `analysis/aero/aero_results.json` `neutral_point.AVL_pod_pct_MAC`); `docs/DESIGN-BASIS.md` line 56 quotes the sizing
   value (38.2 %, 10.2 %, `neutral_point.sizing_pct_MAC`). Both are sourced; pick which one is "the" number.
3. **Nautical Wings spec.** `docs/research/nautical-wings-props.md` §3: the lift column header says "x4 + 1 spare", the
   rotation row asks for "a spare of each" direction, and the quantity row says "6 min"; the BOM holds 2 + 1 pairs
   (6 props) of JeeFly 1755. The design point cites `../DESIGN-BASIS.md` for 6.18 kg, which that file no longer says
   (see D12). The reserve after free props is "$102.08 to $186.05 (EST)" in the DBF-VTOL text (`Inventory-Overview.html`
   §8) and "$145.45 to about $229.43 (EST)" on the 11-02 BOM (DillonVTOL README, carried into `README.md`).
4. **Electrical architecture currents.** `docs/research/electrical-architecture.md` cites `analysis/results.json` for a
   74.4 A transition current; that file now says 82.1 A (the 74.4 A value is in `inventory/v031/analysis/results.json`).
5. **Alternative designs A1–A3.** `concepts/variants/a{1,2,3}/metrics.json` and `a1`, `a2` `design.md` cite `analysis/results.json` C0 at
   6.182 kg and 20 m/s; that path now holds 7.438 kg and 18 m/s (v0.3.1 copy in `inventory/v031/`).
6. **Team cross-check.** `docs/research/team-crosscheck.md` describes DBF-VTOL at `77913e9` as "built on v0.3.1". True
   for the inventory, Fusion and concepts it reviewed; DBF-VTOL's own `analysis/` later moved to rev D, and both repos are
   now merged here.
7. **Build manual revision field.** `docs/build/BUILD-MANUAL.md` line 6 keeps "Revision | B" while its dated history
   runs through drawing rev G (2026-11-03); `build-manual.html` therefore shows "DBF-MAN-001 · Rev B".
8. **Inventory sheet labels.** `inventory/build_sheet.py` lines 53, 70 and 194 write "DBF-VTOL repo" into the workbook
   and sheet seed; the repo is now DBF-Combined.
