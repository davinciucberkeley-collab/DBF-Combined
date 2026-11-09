# Energy: flight pack, mission budget, charging and handling (K09-L)

Owner: E2 (battery / energy engineer). Revision E2-R2, 2026-11-09, against README revision A1-R2. Status:
`PROPOSED`. Every number below is computed by `redesign/team/E2/energy_claims.py` (claims in `team/E2/claims.json`).
To re-check, run `python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`.
The build reports no error on any E2 node (0 E2 drift; the build as a whole still fails on other roles' drift).
All 25 E2 claims are `UNVERIFIED` or `PROPOSED`: no pack has been weighed, capacity-tested or IR-tested yet.

**What changed in R2.** The cruise power is no longer E2's own drag model. It is B1's delivered claim
(`CL-B1-CRUISE-P` 306.6 W / `-P-PESS` 396.9 W, 16 m/s, gate mass), times E2's 1.05 circuit factor, and scaled to
other masses with E2's drag model. When B1 re-runs, the proof chain flags E2 and one re-run follows B1. Also new:
cruise 15 → 16 m/s (D-01), sized mass 2.482 → 2.55 kg (D-07), peak current 120 → 100 A (24.8 A per motor limiter,
D-05), and the pack-weigh log `pack_log.csv`.

**Verdict.** Keep the **Ovonic 4S 6500 mAh LiPo**, one per sortie, 2 sorties per test day (D-12). It is still the
only candidate that passes the 2.6 kg gate, 5 min of pessimistic cruise and the 100 A peak together. With B1's
delivered cruise model (APC 11×4.5MR data at 16 m/s) the pessimistic mission gives **5.1 min** of cruise (+3 %), and
**`BATT_LOW` triggers after 4.6 min (`FAILS`, −7 %)**. The 11×5.5MR adopted in D-05 is expected to close it:
scaling B1 by E1's prop ratio gives 6.5 min and 6.1 min (indicative only). B1's re-run with the 11×5.5MR at
R1 geometry decides it (CR-E2-11). The first pack is not weighed: the order arrives ~20 Nov.

## 1. Pack selection

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Chemistry, cells | LiPo, 4S (KV900 motors fix 4S) | — | `params.json#battery.cells_s` | `PROPOSED` |
| Capacity, energy | 6.5, 96.2 | Ah, Wh | `params.json#battery` | `UNVERIFIED` |
| Mass carried in the budget | 0.55 (listings 0.522–0.551; one listing 0.680); accept ≤ 0.68 | kg | `CL-E2-PACK-MASS` | `PROPOSED` (not weighed) |
| Envelope, hard case | 0.139 × 0.047 × 0.049 (alt. SKU 0.157 × 0.048 × 0.043) | m | `SRC-E2-OVONIC-LISTINGS`, `params.json#battery.size_m` | `UNVERIFIED` |
| Connectors | XT60 main, JST-XH 5-pin balance | — | `SRC-E2-OVONIC-LISTINGS` | `UNVERIFIED` |
| Peak draw (4 × 24.8 A, limiter) | 100 A = 15.3 C, < 5 s | A | `CL-E2-C-PEAK` (≤ 25 C) | `UNVERIFIED` |
| Real continuous rating needed | ≥ 25 C, IR ≤ 5 mΩ/cell (the "130C" label is not physical) | — | `ASM-E2-R-CELL` | `UNVERIFIED` |

**Trade** (`CALC-E2-PACK-TRADE`). Each candidate replaces the 0.55 kg pack in the sized mass (2.55 kg). The
pessimistic case adds the same growth up to the gate.

| Candidate | Ah | kg | Aircraft kg | Cruise base, min | Cruise pess., min | Cont. A | Result |
|---|---|---|---|---|---|---|---|
| Admiral 4S 4000 | 4.0 | 0.386 | 2.386 | 4.6 | 1.8 | 120 | fails 5 min |
| 4S 5000 hard case `EST` | 5.0 | 0.46 | 2.460 | 6.6 | 3.2 | 150 | fails 5 min pess. |
| **Ovonic 4S 6500** | **6.5** | **0.55** | **2.550** | **9.6** | **5.1** | 195 | **passes** |
| 4S 8000 hard case `EST` | 8.0 | 0.70 | 2.700 | 12.0 | 6.6 | 240 | fails 2.6 kg gate |
| Li-ion 4S2P 21700 9 Ah `EST` | 9.0 | 0.62 | 2.620 | 14.6 | 8.4 | 90 | fails gate and 100 A peak |

No pack in reach buys back the pessimistic margin: more capacity costs the gate. The lever is cruise power.

## 2. Energy budget per mission phase

The model is a Thevenin pack (Voc 4 × 3.70 V, R = 4 × 4.0 mΩ + 3 mΩ of leads), with current solved from bus
power. Hover power comes from the maker table plus the 1.06 download and the ESC loss. Climb uses momentum theory.
Cruise is B1's power × 1.05 circuit factor. The reserve is 20 % of nameplate (1.30 Ah) and is never planned into.
**Base**: sized mass 2.55 kg, new pack, calm, 25 °C. **Pessimistic**: 2.6 kg, 92 % capacity, R × 1.5 at 10 °C,
hover × 1.10 for 5 m/s wind, B1 pessimistic cruise (CD0 × 1.3, η_prop × 0.85), 20 s transitions.

| Phase | Time base / pess, s | Power base / pess, W | Current base / pess, A | Charge base / pess, mAh |
|---|---|---|---|---|
| Ground, armed checks | 180 / 180 | 6 / 6 | 0.4 / 0.4 | 20 / 20 |
| Climb 0–50 m at 2 m/s | 25 / 25 | 435 / 487 | 30.6 / 35.2 | 213 / 244 |
| Hover (mission) | 120 / 120 | 373 / 418 | 26.1 / 29.9 | 869 / 996 |
| Transition forward | 10 / 20 | 522 / 585 | 37.0 / 42.9 | 103 / 238 |
| Back-transition | 10 / 20 | 485 / 544 | 34.3 / 39.6 | 95 / 220 |
| Descent 50–0 m at 1 m/s | 50 / 50 | 373 / 418 | 26.1 / 29.9 | 362 / 415 |
| **Cruise at 16 m/s to the 20 % line** | **574 / 308** | 319 / 417 | 22.2 / 29.8 | 3 538 / 2 546 |
| Reserve (untouched) | — | — | — | 1 300 / 1 300 |

| Result | Base | Pess. | Limit | Claim | Status |
|---|---|---|---|---|---|
| Cruise after 2 min hover, min | 9.6 | 5.1 | ≥ 5 | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` (+3 % pess.) |
| Cruise before `BATT_LOW` triggers, min | — | 4.6 | ≥ 5 | `CL-E2-CRUISE-TO-LOW-PESS` | **`FAILS`** (−7 %) |
| Same two with the 11×5.5MR (E1 ratio 0.80 on B1), min | 12.0 | 6.5 / 6.1 | ≥ 5 | `CL-E2-CRUISE-MIN-PESS-55`, `CL-E2-CRUISE-TO-LOW-PESS-55` | `UNVERIFIED` (indicative) |
| Hover-only sortie to 20 %, min | 11.9 | 9.4 | ≥ 2 | `CL-E2-HOVER-ONLY-MIN-PESS` | `UNVERIFIED` |
| Hover current at the gate in wind, A | — | 29.9 | — (F1 input) | `CL-E2-HOVER-I-GATE` | `UNVERIFIED` |
| Cruise current, A | 22.2 | 29.8 | — (F1 input) | `CL-E2-CRUISE-I-PESS` | `UNVERIFIED` |

**Why the base dropped from 15.1 to 9.6 min.** B1's model puts cruise at 307 W, against E2's old 207 W: the
11×4.5MR runs near zero-thrust J at 16 m/s (η_prop 0.37). E2's own drag model, kept as a cross-check, now gives
247 W base and 405 W pessimistic, so the two models agree in the pessimistic case (405 vs 417 W) and differ by
~30 % in the base case on prop efficiency. B1's 9.6 min is lower than B1's own 12.3 min because the E2 budget also
counts the climb, descent, transitions, ground time, circuits and the sized mass.

**What closes the `FAILS`.** In order of preference: (1) B1 re-runs `CALC-B1-CRUISE` with the 11×5.5MR at 16 m/s
and c 0.32 (CR-E2-11); the indicative case passes with +22 %. (2) Packs warm (≥ 20 °C, cabin) remove the R × 1.5
cold term; F4 and H3 already carry this rule. (3) If both fail, the test card flies 4.5 min of cruise to `BATT_LOW`
on the first full mission and A2 decides on the requirement. The `FAILS` is a mission shortfall, not a safety one:
the aircraft returns with the reserve intact.

Note that B1's stored claims drift (B1 re-run at S 0.368 m² gives 311 / 405 W). E2 reads the stored values; when
B1 re-runs, E2 re-runs.

## 3. Voltage sag and thrust

The calculation is `CALC-E2-SAG`. At full throttle (24.8 A per motor at 14.8 V, the limiter), current scales as
(V/14.8)² and thrust as (V/14.8)², and the equation is solved with the pack resistance.

| Pack state | Bus V at full throttle | Thrust factor | Total A | Status |
|---|---|---|---|---|
| Full (4.20 V/cell), 25 °C | 14.9 | 1.01 | 100 | `UNVERIFIED` |
| 20 % line (3.73 V/cell), 25 °C | 13.4 | 0.82 | 81 | `UNVERIFIED` |
| 20 % line, 10 °C pack | 12.9 (0.51 V/cell sag) | **0.76** | 75 | `UNVERIFIED` |
| **Hover T/W at 2.6 kg, worst state** | — | **1.89 ≥ 1.6** (`CL-E2-TW-SAG-WORST`) | — | `UNVERIFIED` |

`params.json#propulsion.voltage_sag` carries 0.72 (D-06), from the 120 A case. With the 100 A limiter the worst
state is 0.76. The 0.72 is conservative; A1 keeps it or updates it (CR-E2-12). A warm pack (≥ 20 °C) moves the
worst-state factor from 0.76 to about 0.82. F4 sets `Q_M_BAT_VOLT_MAX` 16.8 and `Q_M_BAT_VOLT_MIN` 13.2 so that the mixer compensates.

**Pack heating** (`CALC-E2-HEAT`, adiabatic, pessimistic currents). A cold morning gives 21 W in hover and +23 K
(10 → 33 °C). A hot morning gives 14 W and +15 K (30 → **45 °C** at landing), against a 50 °C limit
(`CL-E2-PACK-T-END`, margin 10 %). E3 owns the pod heat path.

## 4. Flight-controller battery settings (for F4)

| Parameter | Value | Why | Claim |
|---|---|---|---|
| `BATT_CAPACITY` | 6500 mAh (lower it to the measured capacity) | counter base | `T-E2-CAPACITY` |
| `BATT_LOW_MAH` → QRTL | **2700** mAh remaining (2600 if B1's 11×5.5MR re-run confirms) | 1 300 mAh reserve + 1 380 mAh to back-transition, descend, 60 s return and 30 s landing hover (pessimistic) | `CL-E2-BATT-LOW-MAH` |
| `BATT_CRT_MAH` → QLAND | 1300 mAh remaining | the 20 % reserve | `CL-E2-BATT-CRT-MAH` |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 14.0 / 13.6 V (3.50 / 3.40 V/cell) | voltage backup | — |
| `BATT_FS_VOLTSRC` | 1 (sag-compensated) | a 0.5 V/cell sag in a transition must not trigger the failsafe | `CL-E2-SAG-V-WORST` |
| `BATT_ARM_VOLT` | 16.4 V (4.10 V/cell) | the mAh counter assumes a full pack at boot, so the aircraft refuses to arm on a used pack | — |

Rule: **one fully charged pack per sortie.** A part-used pack is never re-flown on the same day.

## 5. Charging and balancing

| Item | Value | Source | Status |
|---|---|---|---|
| Charger | HTRC C150, 150 W, one port | `SRC-E2-HTRC-C150` | `UNVERIFIED` |
| Charge current | 6.5 A (1C; 109 W at 16.8 V, inside 150 W) | `CALC-E2-TESTDAY` | `PROPOSED` |
| Time per pack from the 20 % line | 59 min (CC to 85 %, CV 20 min) | `CL-E2-CHARGE-MIN` | `UNVERIFIED` |
| 2 packs (D-12) / 4 packs back to back | 2.0 / 3.9 h, attended, the afternoon before a flying morning | `CL-E2-CHARGE-H-4` | `UNVERIFIED` |

- Always use balance mode, with the balance lead connected. At full charge the cell spread must be ≤ 0.02 V.
  Quarantine the pack if the spread after a 1 h rest is > 0.05 V, or if any cell is below 3.0 V.
- Charge 4.20 V/cell only on the day before flying. If the pack will not fly within 48 h, return it to storage
  (3.80–3.85 V/cell, charger STORAGE mode).
- Inspect for puffing, dents and lead damage before every charge. Log every charge: pack id, mAh in, cell voltages,
  IR if the charger shows it.

## 6. Storage, transport and damaged packs

| Situation | Rule |
|---|---|
| Storage | 3.80–3.85 V/cell, each pack in a LiPo bag, bags in the ammo can with **its rubber gasket removed** (vents, does not pressurise), room temperature, away from flammables |
| Drive to RFS | Charged packs in bags in the ammo can, in the cabin (warm packs, see §3), never left in a closed car in the sun |
| Field | Ammo can and sand bucket 5 m from the pilot box. Packs come out only to fly. IR thermometer reading at landing |
| Charging | Attended, on a non-flammable surface, extinguisher or sand at hand, never in a car (R-BATT-HANDLING). H3 names the room |
| After a crash | Unplug. If dented, puffed, hot or smelling: into the ammo can or sand outdoors, observe ≥ 30 min, never charge it again |
| Retire a pack | Capacity < 80 % of nameplate, IR > 1.5 × new, puffing > 2 mm, or any crash damage. Discharge to 0 V on a resistive load, then household hazardous-waste drop-off (H3 confirms the site) |
| Shipping | Ovonic US warehouse, ground (UN3480). 96.2 Wh < 100 Wh, so a spare pack may be carried on an airliner in cabin baggage if ever needed (`SRC-E2-FAA-PACKSAFE`) |

Mark the packs `E2-P1` and `E2-P2` on tape, plus the in-service date. One logbook line per charge and per flight.

## 7. Packs needed for a test day (D-12: 2 sorties)

| Item | Value | Claim | Status |
|---|---|---|---|
| Sortie (ground checks + full mission, base) + ground turnaround | 16.2 + 20 min | `CALC-E2-TESTDAY` | `PROPOSED` |
| Sorties the 07:00–10:00 window allows | 4 | `CL-E2-SORTIES-WINDOW` | `UNVERIFIED` |
| **Sorties planned per test day, 2 packs** | **2** | `CL-E2-SORTIES-PACKS` | `UNVERIFIED` |
| Window used by the 2 sorties | 52 of 180 min | `CL-E2-WINDOW-USED` | `UNVERIFIED` |
| Charge the afternoon before | 2.0 h attended | `CL-E2-CHARGE-H-4` | `UNVERIFIED` |
| Packs 3–4 | deferred (D-12): bought only if the post-order reserve stays ≥ $396 | CR-E2-05 | `PROPOSED` |

I2 plans every test day at 2 sorties. Use the spare 2 h of the window for ground work (CG balance, thrust checks,
re-briefs), not extra flights: a part-used pack is never re-flown. If packs 3–4 are bought later, the window allows
4 sorties and the charge afternoon becomes 3.9 h.

## 8. Pack acceptance and the first weigh (CR-A3-08)

The ~20 Nov order holds both flight packs. On arrival, before any charge:

| Step | What | Record in `team/E2/pack_log.csv` | Pass |
|---|---|---|---|
| 1 | Arrival cell voltages (storage charge expected) | `cell_v_on_arrival` | every cell 3.75–3.90 V, spread ≤ 0.02 V |
| 2 | Weigh on a 1 g scale, leads included | `mass_g` | ≤ 680 g (A3 growth bound) |
| 3 | Calipers L × W × H and lead exit | `length_mm` … `lead_exit_mm` | fits the D2 bay 160 × 52 × 53 mm |
| 4 | IR load step at 25 °C (`T-E2-IR`) | `ir_mohm_cell_25c` | ≤ 5 mΩ/cell |
| 5 | 1C capacity on the stand (`T-E2-CAPACITY`) | `capacity_mah` | ≥ 6 000 mAh |

Then re-run the script. It reads `pack_log.csv`, carries the heaviest weighed pack in `CL-E2-PACK-MASS` and marks
`T-E2-WEIGH` run. Decision on the mass: ≤ 550 g, nothing changes; 550–680 g, A3 replaces the 550 g line (the
roll-up's predicted mass already covers 680 g); > 680 g, return it and buy another 4S 6000–6500 SKU. Only then does
A1 set `checked` on `SRC-OVONIC-4S6500` (CR-E2-01b stands until the weigh).

## 9. Verification

| Test | What | Verifies |
|---|---|---|
| `T-E2-WEIGH` | 1 g scale and calipers on every pack on arrival, into `pack_log.csv` | `CL-E2-PACK-MASS` (R-PACK-MASS) |
| `T-E2-CAPACITY` | 1C discharge to 3.5 V/cell on the thrust stand with the watt meter; pass ≥ 6.0 Ah | cruise, charge time |
| `T-E2-IR` | 20 A load step at 25 °C and 10 °C; pass ≤ 5 mΩ/cell at 25 °C | sag, T/W, C-rate |
| `T-E2-MISSION-LOG` | DataFlash `BAT` against the phase table (±15 %), pack temperature at landing | budget, currents, temperature |
| Twin flights (gate 1) | Replace `ASM-E2-HOVER-MARGIN` and B1's cruise claim with the logged hover and cruise currents, then re-run | every endurance claim |
