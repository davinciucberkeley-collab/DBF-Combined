# Energy: flight pack, mission budget, charging and handling (K09-L)

Owner: E2 (battery / energy engineer). Date 2026-11-09. Status: `PROPOSED`. Every number below is computed by
`redesign/team/E2/energy_claims.py` (claims in `team/E2/claims.json`). To re-check, run
`python -I redesign/team/E2/energy_claims.py` and then `python -I redesign/proofs/build_graph.py`. The result was
OK with 0 drift. All 22 E2 claims are `UNVERIFIED`, because they rest on unmeasured pack resistance, listing masses
and modelled efficiencies, and none fails.

**Verdict.** Keep the **Ovonic 4S 6500 mAh LiPo**, one per sortie. It is the only candidate that passes the
2.6 kg gate, the pessimistic 5-minute cruise and the 120 A peak together. The pessimistic case gives 6.4 min of cruise
after 2 min of hover, which is half the 12 min carried in `params.json`. The worst-case thrust factor from voltage
sag is 0.72, not the 0.93 in `params.json`. T/W still clears 1.6. Two packs give **2 sorties per test day**, while
the 3 h window allows 4.

## 1. Pack selection

| Parameter | Value | Unit | Source | Status |
|---|---|---|---|---|
| Chemistry, cells | LiPo, 4S (KV900 motors fix 4S) | — | `params.json#battery.cells_s` | `PROPOSED` |
| Capacity, energy | 6.5, 96.2 | Ah, Wh | `params.json#battery` | `UNVERIFIED` |
| Mass carried in the budget | 0.55 (listings 0.522–0.551; one listing 0.680) | kg | `CL-E2-PACK-MASS`, `SRC-E2-OVONIC-LISTINGS` | `UNVERIFIED` |
| Envelope, hard case | 0.139 × 0.047 × 0.049 (alt. SKU 0.157 × 0.048 × 0.043) | m | `SRC-E2-OVONIC-LISTINGS` | `UNVERIFIED` |
| Connectors | XT60 main, JST-XH 5-pin balance | — | `SRC-E2-OVONIC-LISTINGS` | `UNVERIFIED` |
| Peak draw (4 × 30 A) | 120 A = 18.5 C, < 5 s | A | `CL-E2-C-PEAK` | `UNVERIFIED` |
| Real continuous rating needed | ≥ 25 C, IR ≤ 5 mΩ/cell (the "130C" label is not physical) | — | `ASM-E2-R-CELL` | `UNVERIFIED` |

`params.json#battery.size_m` gives a height of 0.035 m. Every 6500 hard-case listing found is **47–49 mm**
tall. The pod has to be sized to the real envelope (CR-E2-02).

**Trade** (`CALC-E2-PACK-TRADE`). Each candidate replaces the 0.55 kg pack in the sized mass. The pessimistic case
adds the same growth up to the gate.

| Candidate | Ah | kg | Aircraft kg | Cruise base, min | Cruise pess., min | Cont. A | Result |
|---|---|---|---|---|---|---|---|
| Admiral 4S 4000 (BOM fallback) | 4.0 | 0.386 | 2.318 | 7.4 | 2.3 | 120 | fails 5 min pess. |
| 4S 5000 hard case `EST` | 5.0 | 0.46 | 2.392 | 10.5 | 3.9 | 150 | fails 5 min pess. |
| **Ovonic 4S 6500** | **6.5** | **0.55** | **2.482** | **15.1** | **6.4** | 195 | **passes** |
| 4S 8000 hard case `EST` | 8.0 | 0.70 | 2.632 | 18.9 | 8.2 | 240 | fails 2.6 kg gate |
| Li-ion 4S2P 21700 9 Ah `EST` | 9.0 | 0.62 | 2.552 | 22.9 | 10.4 | 90 | fails 120 A peak; no spot welder |

The BOM's Admiral 4000 fallback **no longer meets R-MISSION** in the pessimistic case (2.3 min). If Ovonic is out
of stock, look for another 4S 6000–6500 pack of ≤ 0.55 kg, and do not fall back to the 4000.

## 2. Energy budget per mission phase

The model is a Thevenin pack (Voc 4 × 3.70 V, R = 4 × 4.0 mΩ + 3 mΩ of leads), with current solved from bus
power. Hover power comes from the maker table plus the 1.06 download and the ESC loss. Climb uses momentum theory.
Cruise uses the K09 drag build-up with the review's corrected efficiencies. The reserve is 20 % of nameplate
(1.30 Ah) and is never planned into. **Base**: sized mass 2.482 kg, new pack, calm, 25 °C. **Pessimistic**: 2.6 kg,
92 % capacity, R × 1.5 at 10 °C, hover × 1.10 for 5 m/s wind, CD0 × 1.3, η_prop 0.35, 20 s transitions.

| Phase | Time base / pess, s | Power base / pess, W | Current base / pess, A | Charge base / pess, mAh |
|---|---|---|---|---|
| Ground, armed checks | 180 / 180 | 6 / 6 | 0.4 / 0.4 | 20 / 20 |
| Climb 0–50 m at 2 m/s | 25 / 25 | 425 / 487 | 29.8 / 35.2 | 207 / 244 |
| Hover (mission) | 120 / 120 | 363 / 418 | 25.4 / 29.9 | 846 / 996 |
| Transition forward | 10 / 20 | 508 / 585 | 36.0 / 42.9 | 100 / 238 |
| Back-transition | 10 / 20 | 472 / 544 | 33.3 / 39.6 | 93 / 220 |
| Descent 50–0 m at 1 m/s | 50 / 50 | 363 / 418 | 25.4 / 29.9 | 352 / 415 |
| **Cruise at 15 m/s to the 20 % line** | **905 / 382** | 207 / 340 | 14.2 / 24.0 | 3 582 / 2 546 |
| Reserve (untouched) | — | — | — | 1 300 / 1 300 |

| Result | Base | Pess. | Limit | Claim | Status |
|---|---|---|---|---|---|
| Cruise after 2 min hover, min | 15.1 | 6.4 | ≥ 5 | `CL-E2-CRUISE-MIN-BASE`, `-PESS` | `UNVERIFIED` |
| Cruise before BATT_LOW triggers, min | — | 6.0 | ≥ 5 | `CL-E2-CRUISE-TO-LOW-PESS` | `UNVERIFIED` |
| Hover-only sortie to 20 %, min | 12.3 | 9.4 | ≥ 2 | `CL-E2-HOVER-ONLY-MIN-PESS` | `UNVERIFIED` |
| Hover current at the gate in wind, A | — | 29.9 | — (F1 input) | `CL-E2-HOVER-I-GATE` | `UNVERIFIED` |

**Cross-checks.** Momentum theory at 2.482 kg gives an ideal hover power of 169 W. Against the 357 W of motor power,
that is an overall efficiency of 0.47 (FM 0.62 × η_motor 0.80 × ESC 0.95), which is plausible for an 11 in prop
(REVIEW §3). Base cruise is 207 W against the 194 W in `params.json`. The difference comes from 2.482 vs 2.43 kg, the
+5 % circuit factor and +1 W for the servos. The pessimistic 6.4 min is lower than the 12 min in `params.json`
because the gate mass, the 92 % capacity, the cold resistance and the climb, descent and transition legs are all
counted here.

## 3. Voltage sag and thrust

The calculation is `CALC-E2-SAG`. At full throttle, current scales as (V/14.8)² and thrust as (V/14.8)², and the
equation is solved with the pack resistance.

| Pack state | Bus V at full throttle | Thrust factor | Total A | Status |
|---|---|---|---|---|
| Full (4.20 V/cell), 25 °C | 14.6 | 0.97 | 117 | `UNVERIFIED` |
| 20 % line (3.73 V/cell), 25 °C | 13.1 | 0.79 | 94 | `UNVERIFIED` |
| 20 % line, 10 °C pack | 12.6 (0.59 V/cell sag) | **0.72** | 87 | `UNVERIFIED` |
| **Hover T/W at 2.6 kg, worst state** | — | **1.76 ≥ 1.6** (`CL-E2-TW-SAG-WORST`) | — | `UNVERIFIED` |

`params.json#propulsion.voltage_sag` = 0.93 is optimistic for the end of a flight. The worst-case pack state
keeps 10 % margin on T/W 1.6. A warm pack (kept in the car cabin, ≥ 20 °C at take-off) recovers about 7 % of that
thrust. F4 should set `Q_M_BAT_VOLT_MAX` 16.8 and `Q_M_BAT_VOLT_MIN` 13.2 so that the mixer compensates.

**Pack heating** (`CALC-E2-HEAT`, adiabatic, pessimistic currents). A cold morning gives 21 W of heat in hover and
+21 K (10 → 31 °C). A hot morning gives 14 W and +14 K (30 → **44 °C** at landing), against a 50 °C limit
(`CL-E2-PACK-T-END`, margin 13 %). Pack thermal limits are not a constraint. E3 owns the pod heat path.

## 4. Flight-controller battery settings (for F4)

| Parameter | Value | Why | Claim |
|---|---|---|---|
| `BATT_CAPACITY` | 6500 mAh (lower it to the measured capacity) | counter base | `T-E2-CAPACITY` |
| `BATT_LOW_MAH` → QRTL | 2600 mAh remaining | 1 300 mAh reserve + 1 284 mAh to back-transition, descend, 60 s return and 30 s landing hover (pessimistic) | `CL-E2-BATT-LOW-MAH` |
| `BATT_CRT_MAH` → QLAND | 1300 mAh remaining | the 20 % reserve | `CL-E2-BATT-CRT-MAH` |
| `BATT_LOW_VOLT` / `BATT_CRT_VOLT` | 14.0 / 13.6 V (3.50 / 3.40 V/cell) | voltage backup | — |
| `BATT_FS_VOLTSRC` | 1 (sag-compensated) | a 0.6 V/cell sag in a transition must not trigger the failsafe | `CL-E2-SAG-V-WORST` |
| `BATT_ARM_VOLT` | 16.4 V (4.10 V/cell) | the mAh counter assumes a full pack at boot, so the aircraft refuses to arm on a used pack | — |

Rule: **one fully charged pack per sortie.** A part-used pack is never re-flown on the same day.

## 5. Charging and balancing

| Item | Value | Source | Status |
|---|---|---|---|
| Charger | HTRC C150, 150 W, one port | `SRC-E2-HTRC-C150` | `UNVERIFIED` |
| Charge current | 6.5 A (1C; 109 W at 16.8 V, inside 150 W) | `CALC-E2-TESTDAY` | `PROPOSED` |
| Time per pack from the 20 % line | 59 min (CC to 85 %, CV 20 min) | `CL-E2-CHARGE-MIN` | `UNVERIFIED` |
| 2 / 4 packs back to back | 2.0 / 3.9 h, attended, the afternoon after a test day | `CL-E2-CHARGE-H-4` | `UNVERIFIED` |

- Always use balance mode, with the balance lead connected. At full charge the cell spread must be ≤ 0.02 V. Quarantine
  the pack if the spread after a 1 h rest is > 0.05 V, or if any cell is below 3.0 V.
- Charge 4.20 V/cell only on the day before flying. If the pack will not fly within 48 h, return it to storage
  (3.80–3.85 V/cell, charger STORAGE mode).
- Inspect for puffing, dents and lead damage before every charge. Log every charge: pack id, mAh in, cell voltages,
  IR if the charger shows it.
- No parallel board and no second charger are needed while one afternoon covers 4 packs.

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

Mark every pack `E2-P1` … `E2-P4` on tape, plus the in-service date. One logbook line per charge and per flight.

## 7. Packs needed for a test day

| Item | Value | Claim | Status |
|---|---|---|---|
| Sortie (full mission, base) + ground turnaround | 21.7 + 20 min | `CALC-E2-TESTDAY` | `PROPOSED` |
| Sorties the 07:00–10:00 window allows | 4 | `CL-E2-SORTIES-WINDOW` | `UNVERIFIED` |
| Sorties with the 2 packs on order | **2** | `CL-E2-SORTIES-PACKS` | `UNVERIFIED` |
| Recommended fleet | 2 at order (the twin uses them from December), **+2 (one more 2-pack, $87.37 incl. tax) at the start of the transition campaign** | CR-E2-05 | `PROPOSED` |

Wind gives only about 5 usable mornings a week, so the morning, not the pack, is the scarce resource. With 2 packs,
half of each window goes unused. Packs 3 and 4 cost $87.37, which takes the pessimistic reserve from $321 to $234,
below one $309 crash. That is A1's call (CR-E2-05). Hover sorties early in the programme are short and crew-limited,
so 2 packs are enough until gate 6 (first transition).

## 8. Verification

| Test | What | Verifies |
|---|---|---|
| `T-E2-WEIGH` | 1 g scale and calipers on every pack on arrival | `CL-E2-PACK-MASS` (R-PACK-MASS) |
| `T-E2-CAPACITY` | 1C discharge to 3.5 V/cell on the thrust stand with the watt meter; pass ≥ 6.0 Ah | cruise, charge time |
| `T-E2-IR` | 20 A load step at 25 °C and 10 °C; pass ≤ 5 mΩ/cell at 25 °C | sag, T/W, C-rate |
| `T-E2-MISSION-LOG` | DataFlash `BAT` against the phase table (±15 %), pack temperature at landing | budget, currents, temperature |
| Twin flights (gate 1) | Replace `ASM-E2-HOVER-MARGIN` and `ASM-E2-CRUISE-AERO` with the logged hover and cruise currents, then re-run | every endurance claim |
